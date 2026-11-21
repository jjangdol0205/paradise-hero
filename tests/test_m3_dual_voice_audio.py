#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_m3_dual_voice_audio.py
================================================================================
Milestone 3 Dual-Voice Shoujo Drama Dubbing Verification Suite
Tests & Validates:
1. Dual-Voice Roles & Speaker Assignment (Narrator SunHi vs Prince InJoon)
2. Master WAV Output Existence in 4사업부/output/ and synchronization
3. WAV Specs & Stereo Geometry (2ch stereo, 16-bit PCM, 44100Hz)
4. Peak Limiter Compliance (peak <= -0.50 dBFS, peak amplitude <= 0.944)
5. Zero Clipping Integrity (0 clipped samples >= 32767)
6. 100% Full Subtitle Reading guarantee (seg_dur >= tts_dur + 0.22s, margin >= 0.22s)
7. Procedural SFX Coverage (hook_chime, cut_whoosh, metric_ping, outro_drop)
8. Zero Commercial Forbidden Words Audit across all script & metadata files
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
OUTPUT_DIR = DIVISION_DIR / "output"
PILOT_DIR = DIVISION_DIR / "content" / "shorts_daily" / "ep_shoujo_pilot"

OUT_WAV = OUTPUT_DIR / "audio_ep_shoujo.wav"
OUT_META = OUTPUT_DIR / "audio_metadata.json"
PILOT_WAV = PILOT_DIR / "audio_ep_shoujo.wav"
PILOT_META = PILOT_DIR / "audio_metadata.json"
SCRIPT_PATH = PILOT_DIR / "script_ep_shoujo.json"

BANNED_WORDS = ["최" + "저가", "할" + "인율", "특" + "가", "폭" + "탄세일"]


def test_dual_voice_speaker_assignment():
    print("\n--- [TEST 1] Dual-Voice Speaker & Voice Configuration ---")
    assert SCRIPT_PATH.exists(), f"Missing script file: {SCRIPT_PATH}"
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        script = json.load(f)

    voice_configs = script.get("voice_configs", {})
    assert "narrator" in voice_configs, "Missing narrator in voice_configs"
    assert "prince" in voice_configs, "Missing prince in voice_configs"

    narrator_voice = voice_configs["narrator"]["voice"]
    prince_voice = voice_configs["prince"]["voice"]
    assert narrator_voice == "ko-KR-SunHiNeural", f"Expected SunHi for narrator, got {narrator_voice}"
    assert prince_voice == "ko-KR-InJoonNeural", f"Expected InJoon for prince, got {prince_voice}"

    beats = script.get("beats", [])
    assert len(beats) == 8, f"Expected 8 beats, found {len(beats)}"

    expected_speakers = {
        0: ("narrator", "ko-KR-SunHiNeural"),
        1: ("narrator", "ko-KR-SunHiNeural"),
        2: ("prince", "ko-KR-InJoonNeural"),
        3: ("narrator", "ko-KR-SunHiNeural"),
        4: ("prince", "ko-KR-InJoonNeural"),
        5: ("prince", "ko-KR-InJoonNeural"),
        6: ("narrator", "ko-KR-SunHiNeural"),
        7: ("narrator", "ko-KR-SunHiNeural")
    }

    for b in beats:
        b_idx = b["beat_idx"]
        exp_spk, exp_vc = expected_speakers[b_idx]
        actual_spk = b.get("speaker")
        actual_vc = b.get("voice")
        assert actual_spk == exp_spk, f"Beat {b_idx}: expected speaker {exp_spk}, got {actual_spk}"
        assert actual_vc == exp_vc, f"Beat {b_idx}: expected voice {exp_vc}, got {actual_vc}"
        print(f"  Beat {b_idx}: Speaker='{actual_spk}' Voice='{actual_vc}' | Narration: '{b['narration'][:25]}...'")

    print("✅ TEST 1 PASSED: Dual-voice assignments (Narrator vs Prince) strictly verified across 8 beats.")


def test_master_audio_files_and_geometry():
    print("\n--- [TEST 2] Master WAV File Existence & Audio Geometry ---")
    assert OUT_WAV.exists(), f"Missing master WAV file: {OUT_WAV}"
    assert OUT_META.exists(), f"Missing master metadata file: {OUT_META}"
    assert PILOT_WAV.exists(), f"Missing synchronized pilot WAV file: {PILOT_WAV}"
    assert PILOT_META.exists(), f"Missing synchronized pilot metadata file: {PILOT_META}"

    with wave.open(str(OUT_WAV), "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw_bytes = wf.readframes(n_frames)

    assert n_channels == 2, f"Expected stereo audio (2ch), got {n_channels}"
    assert sampwidth == 2, f"Expected 16-bit audio (2 bytes), got {sampwidth}"
    assert framerate == 44100, f"Expected 44100Hz sample rate, got {framerate}"

    audio_pcm = np.frombuffer(raw_bytes, dtype=np.int16).reshape(-1, 2)
    dur = len(audio_pcm) / float(framerate)
    print(f"  Stereo 16-bit 44.1kHz PCM: {dur:.3f}s ({len(audio_pcm):,} frames)")
    print("✅ TEST 2 PASSED: Audio geometry and dual export paths verified.")
    return audio_pcm, dur


def test_peak_limiter_and_zero_clipping(audio_pcm: np.ndarray):
    print("\n--- [TEST 3] Peak Limiter & Zero-Clipping Integrity ---")
    clipped_left = int(np.sum(np.abs(audio_pcm[:, 0]) >= 32767))
    clipped_right = int(np.sum(np.abs(audio_pcm[:, 1]) >= 32767))
    total_clipped = clipped_left + clipped_right
    print(f"  Clipped samples: Left={clipped_left}, Right={clipped_right} (Total: {total_clipped})")
    assert total_clipped == 0, f"Detected {total_clipped} clipped samples!"

    audio_float = audio_pcm.astype(np.float64) / 32768.0
    peak_val = float(np.max(np.abs(audio_float)))
    peak_dbfs = 20.0 * math.log10(max(peak_val, 1e-9))
    print(f"  Peak Linear Amplitude: {peak_val:.4f} (Max ceiling: 0.9440)")
    print(f"  Peak dBFS: {peak_dbfs:.2f} dBFS (Mandatory ceiling: <= -0.50 dBFS)")

    assert peak_dbfs <= -0.50, f"Peak level {peak_dbfs:.2f} dBFS exceeds -0.50 dBFS ceiling!"
    assert peak_val <= 0.9441, f"Peak linear amplitude {peak_val:.4f} exceeds 0.94406!"
    print("✅ TEST 3 PASSED: Limiter <= -0.50 dBFS & exactly 0 clipped samples verified.")
    return audio_float


def test_full_reading_and_beat_timings(audio_dur: float):
    print("\n--- [TEST 4] 100% Full Subtitle Reading & Beat Timings ---")
    with open(OUT_META, "r", encoding="utf-8") as f:
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
        spk = t.get("speaker")
        vc = t.get("voice")

        assert abs(s_sec - running_time) < 0.02, f"Discontinuity at beat {b_idx}"
        assert abs(e_sec - (s_sec + d_sec)) < 0.02, f"Duration mismatch at beat {b_idx}"
        assert d_sec >= tts_dur + 0.219, f"Beat {b_idx} margin too small"
        assert margin >= 0.219, f"Beat {b_idx} breathing margin too small"

        print(f"  Beat {b_idx} [{spk} - {vc}]: TTS={tts_dur:.2f}s, Seg={d_sec:.2f}s, Margin=+{margin:.2f}s ✅")
        running_time = e_sec

    print("✅ TEST 4 PASSED: 100% full reading guaranteed across all 8 beats.")


def test_sfx_and_banned_words():
    print("\n--- [TEST 5] SFX Coverage & Zero Prohibited Words Audit ---")
    with open(OUT_META, "r", encoding="utf-8") as f:
        meta = json.load(f)

    sfx_list = meta.get("sfx_timestamps", [])
    sfx_types = {item["sfx_type"] for item in sfx_list}
    expected_sfx = {"hook_chime", "cut_whoosh", "metric_ping", "outro_drop"}
    assert expected_sfx.issubset(sfx_types), f"Missing SFX: {expected_sfx - sfx_types}"
    print(f"  SFX types confirmed: {sorted(list(sfx_types))}")

    check_files = [
        SCRIPT_PATH,
        OUT_META,
        PILOT_META,
        DIVISION_DIR / "scripts" / "synthesize_shoujo_drama_audio.py"
    ]
    for fp in check_files:
        assert fp.exists(), f"File missing: {fp}"
        text = fp.read_text(encoding="utf-8", errors="replace")
        for banned in BANNED_WORDS:
            assert banned not in text, f"Prohibited word '{banned}' found in {fp.name}"
        print(f"  [PASS] {fp.name}: 0 prohibited commercial words")

    print("✅ TEST 5 PASSED: SFX suite complete & zero prohibited words verified.")


def main():
    print("=" * 80)
    print("🎭 TEST SUITE: MILESTONE 3 DUAL-VOICE DRAMA DUBBING AUDIO")
    print("=" * 80)

    test_dual_voice_speaker_assignment()
    audio_pcm, dur = test_master_audio_files_and_geometry()
    audio_float = test_peak_limiter_and_zero_clipping(audio_pcm)
    test_full_reading_and_beat_timings(dur)
    test_sfx_and_banned_words()

    print("\n" + "=" * 80)
    print("🎉 ALL MILESTONE 3 DUAL-VOICE AUDIO TESTS PASSED PERFECTLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()
