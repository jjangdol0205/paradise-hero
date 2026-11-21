#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit & End-to-End Verification Suite for Div 4 Baek Woon-ho v2 Neural Trot Music Studio
(`baek_woonho_music_studio.py` + Authentic Trot Self-Audit + `status.containsSyntheticMedia = True`)
"""

import json
from pathlib import Path
import sys

import soundfile as sf

DIV4_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = DIV4_DIR / "scripts"
HQ_SHORTS_DIR = DIV4_DIR.parent / "shorts_automation_hq"

for p in (SCRIPTS_DIR, HQ_SHORTS_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import baek_woonho_music_studio as bms
import package_youtube_metadata as pym
import auto_youtube_moving_toon_manager as aym


def test_d_drive_cache_isolation_and_models_cloned() -> None:
    for env_key in (
        "HF_HOME",
        "HF_HUB_CACHE",
        "TORCH_HOME",
        "PIP_CACHE_DIR",
        "UV_CACHE_DIR",
        "ACESTEP_CHECKPOINTS_DIR",
        "TMP",
        "TEMP",
    ):
        val = bms.os.environ.get(env_key, "")
        assert val.upper().startswith("D:\\"), f"{env_key} must point to D:\\, got {val}"
    assert (DIV4_DIR / "models_src" / "ACE-Step-1.5").exists()
    assert (DIV4_DIR / "models_src" / "seed-vc" / "inference.py").exists()
    assert bms.VENV_PYTHON.exists()


def test_zero_fake_tts_sine_synth_and_authentic_84bpm_trot_prompt() -> None:
    src_text = Path(bms.__file__).read_text(encoding="utf-8")
    assert "_synth_local" not in src_text, "Speech-TTS + sine-wave fallback must be 100% removed"
    assert "np.sin(" not in src_text, "Sine-wave tone synthesis must be 0 occurrences"
    assert "ballad" not in src_text.lower(), "Generic 'ballad' keyword must be 0 occurrences"
    assert bms.BPM == 84
    assert bms.KEY_SCALE == "D minor"
    assert bms.VOCAL_LANGUAGE == "ko"
    assert "ppongjjak" in bms.ACE_STEP_TROT_STYLE_PROMPT
    assert "accordion" in bms.ACE_STEP_TROT_STYLE_PROMPT
    assert "tenor saxophone" in bms.ACE_STEP_TROT_STYLE_PROMPT
    assert "kkeokgi" in bms.ACE_STEP_TROT_STYLE_PROMPT


def test_contains_synthetic_media_enforced_across_all_div4_youtubers() -> None:
    meta = pym.build_youtube_metadata({
        "episode_number": 10,
        "episode_title": "백운호 사연 라디오 테스트",
        "featured_song": "어머니의 봄날",
        "broadcast_slot_day": "FRI",
    })
    assert meta.get("containsSyntheticMedia") is True
    assert meta.get("status", {}).get("containsSyntheticMedia") is True

    api_body = pym.build_youtube_api_insert_body(meta)
    assert api_body["status"]["containsSyntheticMedia"] is True
    assert api_body["status"]["selfDeclaredMadeForKids"] is False

    toon_status = aym.build_youtube_api_status_payload()
    assert toon_status["containsSyntheticMedia"] is True
    assert toon_status["selfDeclaredMadeForKids"] is False


def test_zero_real_celebrity_or_paid_tool_in_studio_and_metadata() -> None:
    src_text = Path(bms.__file__).read_text(encoding="utf-8")
    bms.validate_text_guardrails(src_text)
    bms.validate_text_guardrails(bms.ACE_STEP_TROT_STYLE_PROMPT, check_style_prompt=True)
    bms.validate_text_guardrails(json.dumps(bms.DEBUT_SONG_SPEC, ensure_ascii=False))


def test_debut_outputs_and_singing_ref_when_present() -> None:
    if bms.MASTER_REF_WAV.exists():
        ref_arr, ref_sr = sf.read(str(bms.MASTER_REF_WAV), dtype="float32")
        assert ref_sr == 44100
        if ref_arr.ndim > 1:
            ref_arr = ref_arr.mean(axis=1)
        f0_ref = bms.measure_vocal_f0_stats(ref_arr, sr=44100)
        assert f0_ref["f0_semitone_range"] >= 8.0, f"Reference vocal must be real singing (>=8st), got {f0_ref}"

    if bms.DEFAULT_DEBUT_MP3.exists() and bms.DEFAULT_DEBUT_MP4.exists() and bms.DEFAULT_STILL_PNG.exists():
        res = bms.verify_media_outputs(bms.DEFAULT_DEBUT_MP3, bms.DEFAULT_DEBUT_MP4, bms.DEFAULT_STILL_PNG)
        assert res["mp4_resolution"] == "1920x1080"
        assert 185.0 <= res["mp4_duration_sec"] <= 215.0
        assert res["mp3_rms"] > 0.04
        assert res["containsSyntheticMedia"] is True
        assert res["real_celebrity_matches"] == 0
