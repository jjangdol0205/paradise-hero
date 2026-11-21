#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
validate_m1_artifacts.py
================================================================================
Verification Script for Milestone 1 Artifacts:
1. D:\드림컴퍼니\4사업부\docs\SHOUJO_MANGA_SHORTS_GUIDE.md
2. D:\드림컴퍼니\4사업부\content\shorts_daily\ep_shoujo_pilot\script_ep_shoujo.json

Checks:
- JSON validity and schema completeness
- 8 beats (0 to 7) with all required fields
- Ending slate duration (2.5s ~ 3.8s) and CTA domain callouts
- Zero occurrences of banned sales words in script
- Section completeness and keyword verification in Directing Guide
================================================================================
"""

import os
import sys
import json
from pathlib import Path

# Ensure UTF-8 on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DIVISION_DIR = Path(__file__).resolve().parent.parent
GUIDE_PATH = DIVISION_DIR / "docs" / "SHOUJO_MANGA_SHORTS_GUIDE.md"
SCRIPT_PATH = DIVISION_DIR / "content" / "shorts_daily" / "ep_shoujo_pilot" / "script_ep_shoujo.json"
CHARACTERS_PATH = DIVISION_DIR / "data" / "characters.json"

BANNED_WORDS = ["최저가", "할인율", "특가", "폭탄세일"]


def test_script_json():
    print(">>> 1. Testing script_ep_shoujo.json...")
    assert SCRIPT_PATH.exists(), f"Missing script file: {SCRIPT_PATH}"
    
    with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert data.get("episode") == "ep_shoujo_pilot", "Episode ID mismatch"
    assert "사모곡과 황태자의 기적" in data.get("title", ""), "Title missing expected story concept"
    assert data.get("domain") == "paradise-hero.com", "Domain mismatch"
    assert data.get("channel") == "@김쌤의영웅라디오", "Channel mismatch"
    
    beats = data.get("beats", [])
    assert len(beats) == 8, f"Expected exactly 8 beats, got {len(beats)}"
    
    # Load character catalog
    with open(CHARACTERS_PATH, "r", encoding="utf-8") as f:
        chars = {c["id"]: c for c in json.load(f)}
        
    required_fields = [
        "beat_id", "subtitle_line_1", "subtitle_line_2",
        "target_duration_sec", "sfx_trigger", "character_id",
        "panel_layout", "camera_move", "vfx_elements"
    ]
    
    total_dur = 0.0
    for idx, beat in enumerate(beats):
        assert beat.get("beat_id") == idx, f"Beat {idx} beat_id mismatch"
        for field in required_fields:
            assert field in beat, f"Beat {idx} missing required field: {field}"
            
        assert beat["character_id"] in chars, f"Beat {idx} has unknown character: {beat['character_id']}"
        assert isinstance(beat["vfx_elements"], list) and len(beat["vfx_elements"]) > 0, f"Beat {idx} vfx_elements invalid"
        
        dur = float(beat["target_duration_sec"])
        assert 1.5 <= dur <= 5.0, f"Beat {idx} duration out of bounds: {dur}"
        total_dur += dur
        
        # Audio compatibility fields
        assert "narration" in beat, f"Beat {idx} missing narration"
        assert "subtitle_l1" in beat and "subtitle_l2" in beat, f"Beat {idx} missing subtitle_l1/l2"
        assert "sfx" in beat, f"Beat {idx} missing sfx"
        
    print(f"    - All 8 beats validated successfully. Total duration: {total_dur:.1f}s")
    assert 15.0 <= total_dur <= 60.0, f"Total duration out of Shorts bounds: {total_dur}"
    
    # Beat 7 ending slate check
    beat_7 = beats[7]
    dur_7 = float(beat_7["target_duration_sec"])
    assert 2.5 <= dur_7 <= 3.8, f"Beat 7 duration {dur_7}s not within 2.5s~3.8s range"
    assert beat_7.get("is_cta") is True, "Beat 7 must have is_cta = true"
    assert "paradise-hero.com" in data.get("domain", ""), "Domain paradise-hero.com missing"
    assert "무료" in beat_7["subtitle_line_2"] or "무료" in beat_7["narration"], "Beat 7 must include free photo booth CTA"
    print("    - Beat 7 ending slate verified (2.5s~3.8s, CTA, domain).")

    # Banned words check on script
    script_text = SCRIPT_PATH.read_text(encoding="utf-8")
    for banned in BANNED_WORDS:
        assert banned not in script_text, f"Prohibited word '{banned}' found in script_ep_shoujo.json"
    print("    - Zero prohibited commercial words in script_ep_shoujo.json.")
    print("✅ script_ep_shoujo.json PASSED all tests!\n")


def test_directing_guide_markdown():
    print(">>> 2. Testing SHOUJO_MANGA_SHORTS_GUIDE.md...")
    assert GUIDE_PATH.exists(), f"Missing guide file: {GUIDE_PATH}"
    content = GUIDE_PATH.read_text(encoding="utf-8")
    
    required_keywords = [
        "벤치마킹", "5070", "모성애", "소녀 감성",
        "컷 분할", "2-Panel Slanted", "3-Panel Sequential", "Full Page Splash",
        "켄 번스", "Ken Burns", "패럴랙스", "Parallax",
        "방사형 집중선", "Speedlines", "장미 꽃잎", "스파클", "스크린톤",
        "크리스탈 훅", "우쉬", "메트릭 핑", "서브베이스 드롭", "아나운서 호흡",
        "1080x1920", "세이프존", "seg_dur >= tts_dur + 0.22s", "paradise-hero.com",
        "-0.5 dBFS"
    ]
    
    for kw in required_keywords:
        assert kw in content, f"Directing guide missing keyword/concept: '{kw}'"
        print(f"    - Found concept: {kw}")
        
    print(f"    - Guide length: {len(content)} characters, {len(content.splitlines())} lines.")
    print("✅ SHOUJO_MANGA_SHORTS_GUIDE.md PASSED all tests!\n")


if __name__ == "__main__":
    try:
        test_script_json()
        test_directing_guide_markdown()
        print("################################################################################")
        print("🎉 ALL M1 ARTIFACT INTEGRITY & DIRECTING GUIDE TESTS PASSED (100% SUCCESS)!")
        print("################################################################################")
    except AssertionError as e:
        print(f"❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"💥 UNEXPECTED ERROR: {e}")
        sys.exit(1)
