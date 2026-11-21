#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_m2_audio.py
================================================================================
Milestone 2 Audio Verification Suite
Tests & Validates:
1. Master WAV Geometry (2ch stereo, 16-bit PCM, 44100Hz)
2. Peak Limiter Compliance (peak <= -0.50 dBFS, peak amplitude <= 0.944)
3. Anti-Clipping Integrity (strictly 0 clipped samples >= 32767)
4. Zero-Silence Standard (max internal dead air / pause <= 0.12s)
5. 100% Full Reading Sync (seg_dur >= tts_dur + 0.22s for all 8 beats)
6. 4-Point Procedural SFX Coverage (hook_chime, cut_whoosh, metric_ping, outro_drop)
7. GEMINI.md Zero Prohibited Commercial Words Audit
================================================================================
"""

import sys
import math
import wave
import json
from pathlib import Path
import numpy as np

# Ensure UTF-8 console output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = Path(__file__).resolve().parent
DIVISION_DIR = SCRIPT_DIR.parent
PILOT_DIR = DIVISION_DIR / "content" / "shorts_daily" / "ep_shoujo_pilot"
WAV_PATH = PILOT_DIR / "audio_ep_shoujo.wav"
META_PATH = PILOT_DIR / "audio_metadata.json"
SCRIPT_PATH = PILOT_DIR / "script_ep_shoujo.json"

BANNED_WORDS = ["최저가", "할인율", "특가", "폭탄세일"]


def test_1_wav_geometry():
    print("\n--- [TEST 1] WAV Audio Specs & Geometry ---")
    assert WAV_PATH.exists(), f"Missing audio file: {WAV_PATH}"

    with wave.open(str(WAV_PATH), "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw_bytes = wf.readframes(n_frames)

    assert n_channels == 2, f"Expected stereo audio (2 channels), got {n_channels}"
    assert sampwidth == 2, f"Expected 16-bit audio (sampwidth=2), got {sampwidth}"
    assert framerate == 44100, f"Expected 44100Hz sample rate, got {framerate}"

    audio_pcm = np.frombuffer(raw_bytes, dtype=np.int16).reshape(-1, 2)
    dur = len(audio_pcm) / float(framerate)
    print(f"  Stereo 16-bit 44.1kHz PCM: {dur:.3f}s ({len(audio_pcm):,} frames)")
    print("✅ TEST 1 PASSED: Audio geometry is 100% compliant.")
    return audio_pcm, dur


def test_2_limiter_and_clipping(audio_pcm: np.ndarray):
    print("\n--- [TEST 2] Peak Limiter & Zero-Clipping Audit ---")
    # Anti-clipping check: sample values >= 32767
    clipped_left = int(np.sum(np.abs(audio_pcm[:, 0]) >= 32767))
    clipped_right = int(np.sum(np.abs(audio_pcm[:, 1]) >= 32767))
    total_clipped = clipped_left + clipped_right
    print(f"  Clipped samples: Left={clipped_left}, Right={clipped_right} (Total: {total_clipped})")
    assert total_clipped == 0, f"Detected {total_clipped} clipped samples!"

    # Peak amplitude check: <= -0.5 dBFS (linear <= 0.94406)
    audio_float = audio_pcm.astype(np.float64) / 32768.0
    peak_val = float(np.max(np.abs(audio_float)))
    peak_dbfs = 20.0 * math.log10(max(peak_val, 1e-9))
    print(f"  Peak Linear Amplitude: {peak_val:.4f} (Max ceiling: 0.9440)")
    print(f"  Peak dBFS: {peak_dbfs:.2f} dBFS (Mandatory ceiling: <= -0.50 dBFS)")

    assert peak_dbfs <= -0.50, f"Peak level {peak_dbfs:.2f} dBFS exceeds -0.50 dBFS ceiling!"
    assert peak_val <= 0.9441, f"Peak linear amplitude {peak_val:.4f} exceeds 0.94406!"
    print("✅ TEST 2 PASSED: Soft limiter <= -0.5 dBFS & strictly 0 clipped samples verified.")
    return audio_float


def test_3_silence_and_dead_air(audio_float: np.ndarray):
    print("\n--- [TEST 3] Dead Air / Internal Silence Duration ---")
    mono_abs = np.mean(np.abs(audio_float), axis=1)
    thresh = 0.012
    silent_run = 0
    max_silent_run = 0
    for val in mono_abs:
        if val <= thresh:
            silent_run += 1
            if silent_run > max_silent_run:
                max_silent_run = silent_run
        else:
            silent_run = 0

    max_silence_sec = max_silent_run / 44100.0
    print(f"  Max internal dead air / pause: {max_silence_sec:.4f}s (Threshold: <= 0.12s)")
    assert max_silence_sec <= 0.1200, f"Internal silence {max_silence_sec:.4f}s exceeds <= 0.12s standard!"
    print("✅ TEST 3 PASSED: Zero-silence & announcer breathing pause verified.")


def test_4_full_reading_and_beat_sync(audio_dur: float):
    print("\n--- [TEST 4] 100% Full Subtitle Reading & Timing Guarantees ---")
    assert META_PATH.exists(), f"Missing metadata file: {META_PATH}"

    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    meta_total = meta.get("total_duration_sec", 0.0)
    assert abs(meta_total - audio_dur) < 0.05, f"Metadata duration {meta_total}s != WAV duration {audio_dur}s"

    timings = meta.get("beat_timings", [])
    assert len(timings) == 8, f"Expected 8 beats, found {len(timings)}"

    running_time = 0.0
    for t in timings:
        b_idx = t["beat_idx"]
        s_sec = t["start_sec"]
        e_sec = t["end_sec"]
        d_sec = t["duration_sec"]
        tts_dur = t["tts_dur_sec"]
        margin = t["margin_sec"]

        # Continuity check
        assert abs(s_sec - running_time) < 0.02, f"Beat {b_idx} start {s_sec}s discontinuous with previous end {running_time}s"
        assert abs(e_sec - (s_sec + d_sec)) < 0.02, f"Beat {b_idx} end != start + duration"

        # 100% Full reading rule check: seg_dur >= tts_dur + 0.22s
        print(f"  Beat {b_idx}: TTS={tts_dur:.2f}s, Seg={d_sec:.2f}s, Margin=+{margin:.2f}s")
        assert d_sec >= tts_dur + 0.219, (
            f"Beat {b_idx} violation: duration {d_sec:.2f}s < tts_dur ({tts_dur:.2f}s) + 0.22s"
        )
        assert margin >= 0.219, f"Beat {b_idx} breathing margin {margin:.2f}s < 0.22s"
        running_time = e_sec

    print("✅ TEST 4 PASSED: All 8 beats satisfy seg_dur >= tts_dur + 0.22s (zero syllables truncated).")


def test_5_procedural_4point_sfx():
    print("\n--- [TEST 5] Procedural 4-Point SFX Coverage ---")
    with open(META_PATH, "r", encoding="utf-8") as f:
        meta = json.load(f)

    sfx_list = meta.get("sfx_timestamps", [])
    sfx_types = {item["sfx_type"] for item in sfx_list}
    expected_sfx = {"hook_chime", "cut_whoosh", "metric_ping", "outro_drop"}

    print(f"  Present SFX types: {sorted(list(sfx_types))}")
    missing = expected_sfx - sfx_types
    assert not missing, f"Missing required SFX types: {missing}"

    # Verify specific placements
    b0_sfx = [m for m in sfx_list if m["beat_idx"] == 0]
    assert any(m["sfx_type"] == "hook_chime" for m in b0_sfx), "Beat 0 missing hook_chime"

    b7_sfx = [m for m in sfx_list if m["beat_idx"] == 7]
    assert any(m["sfx_type"] == "outro_drop" for m in b7_sfx), "Beat 7 missing outro_drop"

    print("✅ TEST 5 PASSED: 4-Point procedural SFX suite verified across key beats.")


def test_6_prohibited_words():
    print("\n--- [TEST 6] GEMINI.md Zero Prohibited Commercial Words Audit ---")
    check_files = [
        PILOT_DIR / "script_ep_shoujo.json",
        PILOT_DIR / "audio_metadata.json",
        DIVISION_DIR / "scripts" / "synthesize_shoujo_pilot_audio.py"
    ]

    for fp in check_files:
        if not fp.exists():
            continue
        text = fp.read_text(encoding="utf-8", errors="replace")
        for banned in BANNED_WORDS:
            assert banned not in text, f"Prohibited word '{banned}' found in {fp.name}"
        print(f"  [PASS] {fp.name}: Clean (0 prohibited words)")

    print("✅ TEST 6 PASSED: Zero prohibited commercial words.")


def main():
    print("================================================================================")
    print("🛡️ VALIDATION SUITE: MILESTONE 2 SHOUJO MANGA PILOT AUDIO")
    print("================================================================================")

    audio_pcm, dur = test_1_wav_geometry()
    audio_float = test_2_limiter_and_clipping(audio_pcm)
    test_3_silence_and_dead_air(audio_float)
    test_4_full_reading_and_beat_sync(dur)
    test_5_procedural_4point_sfx()
    test_6_prohibited_words()

    print("\n================================================================================")
    print("🎉 ALL M2 AUDIO VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("================================================================================")


if __name__ == "__main__":
    main()
