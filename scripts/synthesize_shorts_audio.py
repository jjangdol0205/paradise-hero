#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
synthesize_shorts_audio.py
================================================================================
Milestone 4 (F10): 1.2x Zero-Silence TTS & Point SFX Mastering Engine
@김쌤의영웅라디오 & 파라다이스히어로 (paradise-hero.com)

Specifications:
- 1.2x speed TTS (+18%~+20%) using edge-tts (ko-KR-InJoonNeural)
- Zero-silence tight mastering: dead air / pauses strictly <= 0.05s
- Point SFX procedural synthesis:
    1) 0.0s Hook Impact Chime (crystalline bell + low impact)
    2) ~2.0s Cut Whoosh (aerodynamic sweep at micro-cuts)
    3) Achievement Ping (1760Hz/2637Hz high-tech emotional chime)
    4) Ending Sub-Bass Drop (65Hz -> 28Hz cinematic drop)
- Peak soft limiter at -0.5 dBFS (peak amplitude <= 0.940, 0 clipped samples)
- Deterministic offline / cached audio fallback for CI/tests without internet
================================================================================
"""

import os
import sys
import math
import wave
import json
import asyncio
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple
import numpy as np

# Ensure UTF-8 on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import edge_tts
except ImportError:
    edge_tts = None

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = "ffmpeg"

SCRIPT_DIR = Path(__file__).resolve().parent
DIVISION_DIR = SCRIPT_DIR.parent
SAMPLE_RATE = 44100


def run_ffmpeg(args: list[str]) -> subprocess.CompletedProcess:
    """Executes FFmpeg command cleanly."""
    cmd = [FFMPEG_EXE, "-y"] + args
    res = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg command failed: {res.stderr[-400:]}")
    return res


def synthesize_synthetic_voice_beat(text: str, duration_sec: float) -> np.ndarray:
    """
    Synthesizes deterministic synthetic voice audio mimicking Korean speech cadence
    for offline / CI environments when edge-tts is unavailable or offline flag is set.
    Uses multi-formant harmonic pulse train (F0 ~ 138Hz with vowel formants).
    """
    total_samples = int(duration_sec * SAMPLE_RATE)
    t = np.linspace(0, duration_sec, total_samples, endpoint=False)
    
    # Syllabic pulse rate ~ 4.5 syllables per second
    syllable_freq = 4.5
    syllable_envelope = 0.5 + 0.5 * np.sin(2 * np.pi * syllable_freq * t - np.pi / 2)
    syllable_envelope = np.clip(syllable_envelope ** 2, 0.05, 1.0)
    
    # Fundamental pitch with subtle micro-intonation curve
    f0 = 138.0 + 8.0 * np.sin(2 * np.pi * 1.2 * t)
    phase = 2 * np.pi * np.cumsum(f0) / SAMPLE_RATE
    
    # Formant resonances: F1 (500Hz), F2 (1500Hz), F3 (2500Hz)
    voice = (
        0.50 * np.sin(phase) +
        0.30 * np.sin(2 * phase) +
        0.20 * np.sin(3 * phase) +
        0.15 * np.sin(4 * phase) +
        0.10 * np.sin(5 * phase)
    )
    voice = voice * syllable_envelope
    
    # Add gentle pink-noise breathiness
    rng = np.random.default_rng(len(text) + int(duration_sec * 100))
    noise = rng.normal(0, 0.04, total_samples)
    voice = voice + noise
    
    # Smooth start and end (15ms fade)
    fade_len = int(0.015 * SAMPLE_RATE)
    if total_samples > fade_len * 2:
        fade_in = np.linspace(0, 1, fade_len)
        fade_out = np.linspace(1, 0, fade_len)
        voice[:fade_len] *= fade_in
        voice[-fade_len:] *= fade_out
        
    return (voice * 0.70).astype(np.float32)


def tighten_pcm_silence(samples: np.ndarray, sr: int = SAMPLE_RATE, thresh: float = 0.014, max_pause_sec: float = 0.045) -> np.ndarray:
    """
    Enforces Shorts V3 Zero-Silence standard:
    - Strips leading/trailing silence (maintaining <= 20ms pad).
    - Compresses all internal pauses longer than max_pause_sec (0.045s <= 0.05s)
      so dead air never exceeds 0.05s.
    """
    if len(samples) == 0:
        return samples

    norm = np.abs(samples.astype(np.float32)) / 32768.0
    win = max(1, int(sr * 0.015))
    env = np.convolve(norm, np.ones(win) / win, mode="same")

    active_idx = np.where(env > thresh)[0]
    if len(active_idx) == 0:
        # Audio is completely silent, return trimmed short buffer
        return samples[:int(sr * 0.05)]

    pad = int(sr * 0.015)
    start = max(0, int(active_idx[0]) - pad)
    end = min(len(samples), int(active_idx[-1]) + pad)
    trimmed = samples[start:end]
    env_t = env[start:end]

    max_silent_samples = int(sr * max_pause_sec)
    buf = []
    silent_run = 0
    for s_val, e_val in zip(trimmed, env_t):
        if e_val <= thresh:
            silent_run += 1
            if silent_run <= max_silent_samples:
                buf.append(s_val)
        else:
            silent_run = 0
            buf.append(s_val)

    return np.array(buf, dtype=np.int16)


async def synthesize_beat_tts(
    text: str,
    target_duration: float,
    voice: str,
    rate: str,
    cache_wav: Path,
    offline: bool = False
) -> np.ndarray:
    """
    Synthesizes single beat voice audio using Edge-TTS (+20% speed) or synthetic fallback.
    Caches audio to cache_wav for deterministic re-runs.
    """
    if cache_wav.exists() and cache_wav.stat().st_size > 500:
        with wave.open(str(cache_wav), "rb") as wf:
            raw_pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        return tighten_pcm_silence(raw_pcm, SAMPLE_RATE)

    # Attempt Edge-TTS if not forced offline
    pcm_int16 = None
    if not offline and edge_tts is not None:
        try:
            tmp_mp3 = cache_wav.with_suffix(".tmp.mp3")
            tmp_wav = cache_wav.with_suffix(".tmp.wav")
            comm = edge_tts.Communicate(text=text, voice=voice, rate=rate)
            await asyncio.wait_for(comm.save(str(tmp_mp3)), timeout=10.0)
            
            # Convert to standard 16-bit 44.1kHz PCM mono WAV
            run_ffmpeg([
                "-i", str(tmp_mp3),
                "-ac", "1",
                "-ar", str(SAMPLE_RATE),
                "-c:a", "pcm_s16le",
                str(tmp_wav)
            ])
            with wave.open(str(tmp_wav), "rb") as wf:
                raw_pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
            pcm_int16 = raw_pcm
            
            # Clean up temp files
            if tmp_mp3.exists():
                tmp_mp3.unlink()
            if tmp_wav.exists():
                tmp_wav.unlink()
        except Exception as e:
            print(f"   [Notice] Edge-TTS live call fallback triggered: {e}")
            pcm_int16 = None

    if pcm_int16 is None:
        # Fallback to deterministic synthetic voice
        synth_float = synthesize_synthetic_voice_beat(text, target_duration)
        pcm_int16 = (synth_float * 32767.0).astype(np.int16)

    tight_pcm = tighten_pcm_silence(pcm_int16, SAMPLE_RATE)

    # Time-stretch or pad to match target_duration (e.g. 1.8~2.2s for body, 2.8~3.2s for CTA)
    target_samples = int(target_duration * SAMPLE_RATE)
    cur_dur = len(tight_pcm) / float(SAMPLE_RATE)
    if cur_dur > target_duration * 1.05 and cur_dur > 0.5:
        # Accelerate with atempo
        ratio = cur_dur / float(target_duration)
        tmp_unscaled = cache_wav.with_suffix(".unscaled.wav")
        tmp_scaled = cache_wav.with_suffix(".scaled.wav")
        with wave.open(str(tmp_unscaled), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(tight_pcm.tobytes())
        try:
            # atempo supports up to 2.0 per filter instance
            filter_str = f"atempo={ratio:.4f}" if ratio <= 2.0 else f"atempo=2.0,atempo={ratio/2.0:.4f}"
            run_ffmpeg(["-i", str(tmp_unscaled), "-filter:a", filter_str, str(tmp_scaled)])
            with wave.open(str(tmp_scaled), "rb") as wf:
                tight_pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        except Exception:
            pass
        finally:
            if tmp_unscaled.exists():
                tmp_unscaled.unlink()
            if tmp_scaled.exists():
                tmp_scaled.unlink()

    # If slightly shorter than target_duration, pad to target_samples (with zero-silence bridge)
    if len(tight_pcm) < target_samples:
        pad_tail = np.zeros(target_samples - len(tight_pcm), dtype=np.int16)
        tight_pcm = np.concatenate([tight_pcm, pad_tail])
    elif len(tight_pcm) > target_samples + int(0.10 * SAMPLE_RATE):
        tight_pcm = tight_pcm[:target_samples]

    # Cache tightly mastered beat audio
    cache_wav.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(cache_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(tight_pcm.tobytes())

    return tight_pcm


# ==============================================================================
# Procedural Point SFX Synthesis
# ==============================================================================
def generate_sfx_hook_chime(sr: int = SAMPLE_RATE) -> np.ndarray:
    """0.0s Hook Impact Chime: Crystalline dual chime + sub impact thump."""
    dur = 0.85
    total = int(dur * sr)
    t = np.linspace(0, dur, total, endpoint=False)
    
    # Sub impact thump (90Hz -> 42Hz)
    sub_env = np.exp(-14.0 * t)
    sub = 0.40 * np.sin(2 * np.pi * (42.0 + 48.0 * np.exp(-18.0 * t)) * t) * sub_env
    
    # Crystalline high chime (1318.5Hz E6 + 2093Hz C7 + 2637Hz E7)
    chime_env = np.exp(-5.5 * t)
    chime = (
        0.28 * np.sin(2 * np.pi * 1318.5 * t) +
        0.22 * np.sin(2 * np.pi * 2093.0 * t) +
        0.15 * np.sin(2 * np.pi * 2637.0 * t)
    ) * chime_env
    
    return sub + chime


def generate_sfx_cut_whoosh(sr: int = SAMPLE_RATE) -> np.ndarray:
    """~2.0s Cut Whoosh: Aerodynamic swoosh transition on micro-cuts."""
    dur = 0.24
    total = int(dur * sr)
    t = np.linspace(0, dur, total, endpoint=False)
    
    # Gaussian envelope peaking at center
    env = np.exp(-((t - 0.12) / 0.045) ** 2)
    
    # Frequency chirp 350Hz -> 1400Hz -> 450Hz
    freq = 350.0 + 1050.0 * np.sin(np.pi * t / dur)
    phase = 2 * np.pi * np.cumsum(freq) / sr
    sweep = 0.25 * np.sin(phase) * env
    
    # Shaped noise component
    rng = np.random.default_rng(2026)
    noise = rng.normal(0, 0.12, total) * env
    # Simple lowpass moving average
    noise = np.convolve(noise, np.ones(12) / 12.0, mode="same")
    
    return sweep + noise


def generate_sfx_metric_ping(sr: int = SAMPLE_RATE) -> np.ndarray:
    """Achievement / Resonance Ping: High-tech bell chime (1760Hz + 2637Hz)."""
    dur = 0.55
    total = int(dur * sr)
    t = np.linspace(0, dur, total, endpoint=False)
    
    env = np.exp(-8.0 * t)
    ping = (
        0.30 * np.sin(2 * np.pi * 1760.0 * t) +
        0.22 * np.sin(2 * np.pi * 2637.0 * t) +
        0.10 * np.sin(2 * np.pi * 3520.0 * t)
    ) * env
    return ping


def generate_sfx_outro_drop(sr: int = SAMPLE_RATE) -> np.ndarray:
    """Ending Sub-Bass Drop: Cinematic 68Hz -> 28Hz drop with warm sub-boom."""
    dur = 1.30
    total = int(dur * sr)
    t = np.linspace(0, dur, total, endpoint=False)
    
    # Exponential frequency glide
    freq = 68.0 * np.exp(-1.8 * t) + 26.0
    phase = 2 * np.pi * np.cumsum(freq) / sr
    env = np.exp(-2.2 * t)
    drop = 0.45 * np.sin(phase) * env
    
    # Gentle sparkle shimmer on top
    shimmer_env = np.exp(-7.0 * t)
    shimmer = 0.08 * np.sin(2 * np.pi * 1568.0 * t) * shimmer_env
    
    return drop + shimmer


# ==============================================================================
# Master Audio Synthesis & Limiter
# ==============================================================================
async def synthesize_shorts_audio(
    script_path: Path,
    out_wav: Path,
    offline: bool = False
) -> Dict[str, Any]:
    """
    Synthesizes and masters full episode audio:
    - 1.2x speech narration with zero-silence tight trimming
    - Point SFX injection at exact beat transition timestamps
    - Background emotional pulse at -20 dBFS with voice sidechain ducking
    - Soft limiter at -0.5 dBFS with strictly 0 clipped samples
    """
    with open(script_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    beats = script_data.get("beats", [])
    if not beats:
        raise ValueError("Script contains 0 beats!")

    voice = script_data.get("voice", "ko-KR-InJoonNeural")
    rate = script_data.get("speech_rate", "+20%")
    work_dir = out_wav.parent / "_audio_work"
    work_dir.mkdir(parents=True, exist_ok=True)

    # 1. Synthesize individual tight beat audios
    beat_pcm_list: List[np.ndarray] = []
    beat_durations: List[float] = []
    beat_cut_times: List[float] = []
    current_time = 0.0

    print("🎵 Synthesizing Shorts narration beats (+20% rate, zero-silence)...")
    for idx, beat in enumerate(beats):
        cache_wav = work_dir / f"beat_{idx:02d}.wav"
        pcm = await synthesize_beat_tts(
            text=beat["narration"],
            target_duration=beat.get("target_duration_sec", 2.0),
            voice=voice,
            rate=rate,
            cache_wav=cache_wav,
            offline=offline
        )
        beat_pcm_list.append(pcm)
        dur = len(pcm) / float(SAMPLE_RATE)
        beat_durations.append(round(dur, 3))
        current_time += dur
        beat_cut_times.append(round(current_time, 3))
        print(f"   - Beat {idx:02d} [{beat['character_id']}]: {dur:.2f}s | SFX: {beat.get('sfx')}")

    # 2. Assemble voice track with micro-crossfade bridging (<= 0.035s, strictly <= 0.05s dead air)
    bridge_len = int(SAMPLE_RATE * 0.025)
    voice_mono_parts = []
    for idx, pcm in enumerate(beat_pcm_list):
        voice_mono_parts.append(pcm.astype(np.float64) / 32768.0)
        if idx < len(beat_pcm_list) - 1:
            # Subtle smooth pad (25ms <= 50ms)
            voice_mono_parts.append(np.zeros(bridge_len, dtype=np.float64))

    voice_full = np.concatenate(voice_mono_parts)
    total_samples = len(voice_full)
    total_duration = total_samples / float(SAMPLE_RATE)
    t = np.linspace(0, total_duration, total_samples, endpoint=False)

    # 3. Synthesize subtle background emotional bed (D Major chords: D, A, Bm, G)
    chords = [
        (146.83, 185.00, 220.00), # D3, F#3, A3
        (110.00, 164.81, 220.00), # A2, E3, A3
        (123.47, 146.83, 220.00), # B2, D3, A3
        (98.00, 146.83, 196.00)   # G2, D3, G3
    ]
    bgm_left = np.zeros(total_samples, dtype=np.float64)
    bgm_right = np.zeros(total_samples, dtype=np.float64)
    sec_per_chord = total_duration / len(chords)

    for c_idx, (f1, f2, f3) in enumerate(chords):
        s_t = c_idx * sec_per_chord
        e_t = (c_idx + 1) * sec_per_chord
        chord_env = np.clip((t - s_t) / 0.35, 0, 1) * np.clip((e_t - t) / 0.35, 0, 1)
        pad = (
            0.45 * np.sin(2 * np.pi * f1 * t) +
            0.35 * np.sin(2 * np.pi * f2 * t) +
            0.20 * np.sin(2 * np.pi * f3 * t)
        )
        bgm_left += 0.12 * pad * chord_env
        bgm_right += 0.12 * pad * chord_env

    # 4. Inject Point SFX at beat starting timestamps
    sfx_left = np.zeros(total_samples, dtype=np.float64)
    sfx_right = np.zeros(total_samples, dtype=np.float64)
    sfx_markers = []

    # Calculate actual start times for each beat
    beat_starts = [0.0]
    accum = 0.0
    for dur in beat_durations[:-1]:
        accum += dur + (bridge_len / float(SAMPLE_RATE))
        beat_starts.append(round(accum, 3))

    for idx, (b_start, beat) in enumerate(zip(beat_starts, beats)):
        sfx_tag = beat.get("sfx", "cut_whoosh")
        idx_0 = int(b_start * SAMPLE_RATE)
        sfx_markers.append({
            "beat_idx": idx,
            "time_sec": b_start,
            "sfx_type": sfx_tag
        })

        sfx_arr = None
        if sfx_tag == "hook_chime" or idx == 0:
            sfx_arr = generate_sfx_hook_chime(SAMPLE_RATE)
        elif sfx_tag == "cut_whoosh":
            sfx_arr = generate_sfx_cut_whoosh(SAMPLE_RATE)
        elif sfx_tag == "metric_ping":
            sfx_arr = generate_sfx_metric_ping(SAMPLE_RATE)
        elif sfx_tag == "outro_drop" or beat.get("is_cta"):
            sfx_arr = generate_sfx_outro_drop(SAMPLE_RATE)

        if sfx_arr is not None:
            w_len = min(len(sfx_arr), total_samples - idx_0)
            if w_len > 0:
                sfx_left[idx_0:idx_0 + w_len] += sfx_arr[:w_len]
                sfx_right[idx_0:idx_0 + w_len] += sfx_arr[:w_len]

    # 5. Sidechain ducking of background music under voice
    duck_win = int(SAMPLE_RATE * 0.10)
    v_env = np.convolve(np.abs(voice_full), np.ones(duck_win) / duck_win, mode="same")
    duck_gain = np.clip(0.60 - v_env * 1.40, 0.18, 0.60)

    # Combine channels: Voice (1.10x) + Ducked BGM + SFX
    mix_left = voice_full * 1.10 + bgm_left * duck_gain + sfx_left * 0.90
    mix_right = voice_full * 1.10 + bgm_right * duck_gain + sfx_right * 0.90

    # 6. Anti-Clipping Soft Limiter (Ceiling strictly at -0.5 dBFS = 0.94406)
    target_ceiling = 0.940
    peak_raw = max(float(np.max(np.abs(mix_left))), float(np.max(np.abs(mix_right))), 1e-6)
    if peak_raw > target_ceiling:
        scale = target_ceiling / peak_raw
        mix_left *= scale
        mix_right *= scale

    # 7. Quality & Compliance Verification
    final_peak = max(float(np.max(np.abs(mix_left))), float(np.max(np.abs(mix_right))))
    peak_dbfs = 20.0 * math.log10(max(final_peak, 1e-9))
    clipped_count = int(np.sum(np.abs(mix_left) >= 0.999) + np.sum(np.abs(mix_right) >= 0.999))

    # Verify zero-silence constraint across whole track
    mix_abs = 0.5 * (np.abs(mix_left) + np.abs(mix_right))
    thresh = 0.012
    silent_samples = 0
    max_silent_run_samples = 0
    for val in mix_abs:
        if val <= thresh:
            silent_samples += 1
            if silent_samples > max_silent_run_samples:
                max_silent_run_samples = silent_samples
        else:
            silent_samples = 0
    max_internal_silence_sec = round(max_silent_run_samples / float(SAMPLE_RATE), 4)

    # 8. Export 16-bit stereo PCM WAV
    stereo = np.vstack([mix_left, mix_right]).T
    pcm_int16_out = np.clip(stereo * 32767.0, -32768, 32767).astype(np.int16)

    out_wav.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm_int16_out.tobytes())

    # Write audio mastering metadata
    meta = {
        "audio_file": str(out_wav.name),
        "sample_rate": SAMPLE_RATE,
        "channels": 2,
        "total_duration_sec": round(total_duration, 3),
        "beat_count": len(beats),
        "beat_durations_sec": beat_durations,
        "beat_start_times_sec": beat_starts,
        "peak_amplitude": round(final_peak, 4),
        "peak_dbfs": round(peak_dbfs, 2),
        "clipped_samples": clipped_count,
        "max_internal_silence_sec": max_internal_silence_sec,
        "zero_silence_compliant": bool(max_internal_silence_sec <= 0.05),
        "limiter_compliant": bool(peak_dbfs <= -0.5),
        "sfx_markers": sfx_markers
    }

    meta_file = out_wav.parent / "audio_metadata.json"
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"✅ Audio mastering complete: {out_wav}")
    print(f"   - Duration: {total_duration:.2f}s | Beats: {len(beats)}")
    print(f"   - Peak dBFS: {peak_dbfs:.2f} dBFS (Ceiling: -0.5 dBFS) | Clipped: {clipped_count}")
    print(f"   - Max dead air: {max_internal_silence_sec:.4f}s (Standard: <= 0.05s)")
    print(f"   - SFX Markers: {len(sfx_markers)} events injected")
    return meta


def main():
    parser = argparse.ArgumentParser(description="Milestone 4: 1.2x Zero-Silence TTS & Point SFX Mastering")
    parser.add_argument("--script", type=str, required=True, help="Path to script JSON")
    parser.add_argument("--out", type=str, required=True, help="Path to output WAV")
    parser.add_argument("--offline", action="store_true", help="Force deterministic offline synthesis")
    args = parser.parse_args()

    script_path = Path(args.script)
    out_wav = Path(args.out)
    asyncio.run(synthesize_shorts_audio(script_path, out_wav, args.offline))


if __name__ == "__main__":
    main()
