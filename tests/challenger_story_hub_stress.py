#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
challenger_story_hub_stress.py
Empirical Challenger Stress Harness for Story Hub Ranking Engine and Radio Scripting Bridge.
Tests edge cases, spam patterns, boundary values, malformed inputs, and integration failure modes.
"""

import os
import sys
import json
import tempfile
import traceback
from datetime import datetime, timezone, timedelta

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from scripts.select_top_story import (
    validate_story,
    compute_resonance_score,
    assign_tier,
    segment_story_for_radio,
    select_top_story,
    build_radio_payload,
    PROHIBITED_COMMERCIAL_WORDS,
    SPAM_BLACK_WORDS
)
from scripts.generate_radio_script import (
    build_episode_script_from_story,
    AI_BLACKLIST
)

failures = []
passes = []

def run_test(name, fn):
    print(f"[*] Testing: {name} ... ", end="")
    try:
        fn()
        passes.append(name)
        print("[PASS]")
    except AssertionError as ae:
        failures.append((name, f"AssertionError: {ae}"))
        print(f"[FAIL] AssertionError: {ae}")
    except Exception as e:
        failures.append((name, f"Exception: {type(e).__name__}: {e}"))
        print(f"[FAIL] Exception: {type(e).__name__}: {e}")
        traceback.print_exc()

# -----------------------------------------------------------------------------
# Test Suite 1: Ingestion Filter Boundaries & Edge Cases
# -----------------------------------------------------------------------------
def test_short_story_boundary():
    # 29 characters -> must fail (aligned with 30-char threshold)
    s_29 = {
        "story_title": "제목",
        "story_content": "가" * 29,
        "cheer_count": 10
    }
    is_valid, reason = validate_story(s_29)
    assert not is_valid, "Story with 29 chars should be quarantined"
    assert "too short" in reason

    # 30 characters with diverse words -> must pass
    sample_text = "영웅님의 노래를 매일 아침 감사히 듣고 있습니다 사랑해요"[:30]
    assert len(sample_text.strip()) == 30
    s_30 = {
        "story_title": "어머님의 편지",
        "story_content": sample_text,
        "cheer_count": 10
    }
    is_valid, reason = validate_story(s_30)
    assert is_valid, f"Valid 30-char story should pass validation, got reason: {reason}"

def test_long_story_boundary():
    # 3000 chars -> should pass if valid (ensure diverse vocabulary ratio >= 0.35)
    sentences = [
        f"사연문단{i} 우리 가수{i} 황영웅님의 감미로운 목소리{i} 따스한 온기{i} 고단한 삶에 찬란한 봄날{i} 위로와 용기{i} 사랑{i} 감사합니다."
        for i in range(60)
    ]
    content_3000 = " ".join(sentences)[:3000]
    s_3000 = {
        "story_title": "긴 사연",
        "story_content": content_3000,
        "cheer_count": 50
    }
    is_valid, reason = validate_story(s_3000)
    assert is_valid, f"3000-char story should pass validation, got: {reason}"

    # 3001 chars -> must fail
    content_3001 = content_3000 + "더"
    s_3001 = {
        "story_title": "초과 사연",
        "story_content": content_3001,
        "cheer_count": 50
    }
    is_valid, reason = validate_story(s_3001)
    assert not is_valid, "3001-char story must be quarantined"
    assert "too long" in reason

def test_missing_or_null_fields():
    # Empty dictionary
    is_valid, reason = validate_story({})
    assert not is_valid, "Empty dict story must fail validation"

    # None values
    s_none = {
        "story_title": None,
        "story_content": None,
        "song_title": None,
        "cheer_count": None
    }
    is_valid, reason = validate_story(s_none)
    assert not is_valid, "None values must be handled safely"

    # Score computation with None values
    score, breakdown = compute_resonance_score(s_none)
    assert isinstance(score, float)
    assert 0.0 <= score <= 100.0

def test_negative_and_extreme_cheer():
    valid_text = "우리 영웅님의 따뜻한 노래를 들으며 매일 아침 눈물과 감동으로 하루를 시작합니다 감사해요 힘을 내어 살아갑니다 사랑합니다"
    # Negative cheer
    s_neg = {
        "story_title": "음수 응원",
        "story_content": valid_text,
        "cheer_count": -9999
    }
    score_neg, bd_neg = compute_resonance_score(s_neg)
    assert bd_neg["cheer_score"] == 0.0, f"Negative cheer must yield 0.0 cheer score, got {bd_neg['cheer_score']}"

    # Huge cheer (10 billion)
    s_huge = {
        "story_title": "초거대 응원",
        "story_content": valid_text,
        "cheer_count": 10_000_000_000
    }
    score_huge, bd_huge = compute_resonance_score(s_huge)
    assert bd_huge["cheer_score"] <= 35.0, f"Cheer score must be capped at 35.0, got {bd_huge['cheer_score']}"
    assert score_huge <= 100.0, f"Total score must be <= 100.0, got {score_huge}"

def test_character_repetition_quarantine():
    s_rep = {
        "story_title": "반복 문자",
        "story_content": "우리 영웅님 노래 정말 최고입니다 ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ 너무너무 좋습니다 힘이 납니다 감사합니다",
        "cheer_count": 5
    }
    is_valid, reason = validate_story(s_rep)
    assert not is_valid, "Excessive character repetition must be quarantined"
    assert "repetition" in reason

def test_low_vocabulary_diversity_spam():
    # 35 words all repeating identical words
    content = " ".join(["영웅님", "사랑합니다", "최고"] * 12) + " 영웅님 사랑합니다"
    s_low_div = {
        "story_title": "단어 도배",
        "story_content": content,
        "cheer_count": 5
    }
    is_valid, reason = validate_story(s_low_div)
    assert not is_valid, "Low vocabulary diversity must be quarantined"
    assert "vocabulary diversity" in reason

def test_banned_commercial_words():
    for word in PROHIBITED_COMMERCIAL_WORDS:
        s = {
            "story_title": f"공지 {word}",
            "story_content": f"우리 영웅님 앨범 {word} 정보 공유합니다 꼭 확인하시고 많이 응원해 주세요 사랑합니다",
            "cheer_count": 10
        }
        is_valid, reason = validate_story(s)
        assert not is_valid, f"Prohibited word '{word}' must be quarantined"
        assert "commercial buzzword" in reason

def test_spam_black_words():
    for word in SPAM_BLACK_WORDS:
        s = {
            "story_title": f"사연 {word}",
            "story_content": f"우리 영웅님 노래 듣고 힘내세요 여기서 {word} 관련 안내도 드립니다 문의 바랍니다 파라다이스",
            "cheer_count": 10
        }
        is_valid, reason = validate_story(s)
        assert not is_valid, f"Spam word '{word}' must be quarantined"
        assert "Spam keyword" in reason

def test_url_detection():
    url_samples = [
        "https://evil-site.com/phishing",
        "http://free-gift.kr",
        "www.naver-scam.com",
        "t.me/telegram_channel",
        "open.kakao.com/o/abcd123"
    ]
    for url in url_samples:
        s = {
            "story_title": "링크 포함 사연",
            "story_content": f"우리 영웅님 응원방 입장 링크입니다 {url} 어서오셔서 함께 응원합시다 감사합니다",
            "cheer_count": 10
        }
        is_valid, reason = validate_story(s)
        assert not is_valid, f"URL pattern '{url}' must be quarantined"
        assert "External link" in reason

def test_created_at_decay_and_malformed_dates():
    valid_text = "우리 영웅님의 따뜻한 노래를 들으며 매일 아침 눈물과 감동으로 하루를 시작합니다 감사해요 힘을 내어 살아갑니다 사랑합니다"
    now = datetime.now(timezone.utc)

    # 10 days ago -> decay penalty = 1.2 * 10 = 12.0
    s_10d = {
        "story_title": "10일전",
        "story_content": valid_text,
        "song_title": "당신 편",
        "cheer_count": 100,
        "created_at": (now - timedelta(days=10)).isoformat()
    }
    score_10d, bd_10d = compute_resonance_score(s_10d, now)
    assert bd_10d["decay_penalty"] == 12.0, f"Expected 12.0 decay penalty, got {bd_10d['decay_penalty']}"

    # 100 days ago -> capped at 25.0
    s_100d = {
        "story_title": "100일전",
        "story_content": valid_text,
        "song_title": "당신 편",
        "cheer_count": 100,
        "created_at": (now - timedelta(days=100)).isoformat()
    }
    score_100d, bd_100d = compute_resonance_score(s_100d, now)
    assert bd_100d["decay_penalty"] == 25.0, f"Decay penalty must cap at 25.0, got {bd_100d['decay_penalty']}"

    # Future date (created_at in future) -> max(0, negative delta) -> decay_penalty = 0.0
    s_future = {
        "story_title": "미래 사연",
        "story_content": valid_text,
        "created_at": (now + timedelta(days=10)).isoformat()
    }
    score_fut, bd_fut = compute_resonance_score(s_future, now)
    assert bd_fut["decay_penalty"] == 0.0, f"Future date decay penalty must be 0.0, got {bd_fut['decay_penalty']}"

    # Malformed date strings -> should not crash, decay_penalty = 0.0
    for bad_date in ["invalid-date", "2026/11/09", "None", 12345]:
        s_bad = {
            "story_title": "오류 날짜",
            "story_content": valid_text,
            "created_at": bad_date
        }
        score_bad, bd_bad = compute_resonance_score(s_bad, now)
        assert bd_bad["decay_penalty"] == 0.0, f"Malformed date should yield 0.0 decay, got {bd_bad['decay_penalty']}"

def test_select_top_story_empty_and_all_quarantined():
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".json") as f:
        json.dump([], f)
        empty_file = f.name

    try:
        top_story, valid_list = select_top_story(empty_file)
        assert top_story is None, "Empty story file should return None top_story"
        assert len(valid_list) == 0, "Empty story file should return empty valid_list"
    finally:
        os.remove(empty_file)

    # All quarantined file
    spam_stories = [
        {"story_id": "sp1", "story_title": "카지노", "story_content": "카지노 대출 조건만남", "cheer_count": 100},
        {"story_id": "sp2", "story_title": "짧음", "story_content": "너무 짧아", "cheer_count": 500}
    ]
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".json") as f:
        json.dump(spam_stories, f)
        spam_file = f.name

    try:
        top_story, valid_list = select_top_story(spam_file)
        assert top_story is None, "All-quarantined file should return None top_story"
        assert len(valid_list) == 0, "All-quarantined file should return empty valid_list"
    finally:
        os.remove(spam_file)

# -----------------------------------------------------------------------------
# Test Suite 2: Radio Segmentation and Payload Generation
# -----------------------------------------------------------------------------
def test_segmentation_with_no_punctuation():
    # 500 characters with zero punctuation marks
    text = "영웅님의 목소리를 들을 때마다 가슴속 깊은 곳에서 눈물이 솟구치고 힘겨웠던 지난 세월의 모든 아픔과 상처들이 봄눈 녹듯이 사르르 씻겨 내려가는 듯한 따스하고 벅찬 위로를 받습니다 홀로 남겨진 외로움 속에서 버텨오던 날들에 영웅님은 한 줄기 눈부신 햇살이었고 이제는 제 삶의 든든한 버팀목이 되어주셨습니다 언제나 건강하시고 오래도록 고운 노래 들려주시기를 간절히 기도하며 전국 각지의 파라다이스 가족들과 함께 끝까지 두 손 꼭 잡고 동행하겠습니다 늘 감사합니다 사랑합니다"
    s = {"story_content": text}
    segments = segment_story_for_radio(s)
    assert len(segments) >= 1, "Should produce at least 1 segment"
    for seg in segments:
        assert len(seg["text"]) <= 200, f"Segment text length ({len(seg['text'])}) exceeds reasonable chunk limit"
        assert "pacing_pause_sec" in seg
        assert "emotion" in seg

def test_radio_script_generation_with_edge_payloads():
    # Minimal payload
    top_story = {
        "story_id": "edge_01",
        "sender_name": "김영희 어머니",
        "sender_location": "부산 해운대구",
        "song_title": "당신 편",
        "story_title": "가슴에 묻어둔 편지",
        "story_content": "영웅님 노래를 들으며 매일 아침 눈물과 치유를 경험합니다. 우리 어머님들 힘내세요.",
        "cheer_count": 88,
        "resonance_score": 78.5
    }
    payload = build_radio_payload(top_story, episode_number=2)
    script_data = build_episode_script_from_story(2, payload)

    assert script_data["episode_number"] == 2
    assert script_data["total_chapters"] == 6
    assert script_data["total_segments"] > 20
    assert script_data["total_characters"] > 1500
    assert script_data["total_estimated_duration_sec"] >= 720, f"Duration {script_data['total_estimated_duration_sec']} should meet 12-min minimum"

# -----------------------------------------------------------------------------
# Test Suite 3: AI Blacklist Injection in User Stories
# -----------------------------------------------------------------------------
def test_ai_blacklist_word_in_user_story():
    """
    Test that fan letters containing phrases in AI_BLACKLIST do NOT raise ValueError.
    Exemption of fan_letter_writer from AI_BLACKLIST guarantees unhindered script generation.
    """
    for bad_phrase in ["함께 성장해요", "놀라운 경험", "바쁜 현대사회"]:
        top_story_with_ai = {
            "story_id": "ai_test_01",
            "sender_name": "박순자 어머니",
            "sender_location": "서울 강동구",
            "song_title": "당신 편",
            "story_title": "눈물의 사연",
            "story_content": f"영웅님의 노래를 듣는 것은 정말 {bad_phrase} 였습니다. 눈물과 감동으로 매일 치유받고 있습니다. 영웅님 건강하세요.",
            "cheer_count": 95,
            "resonance_score": 82.0
        }
        payload = build_radio_payload(top_story_with_ai, episode_number=2)
        script_data = build_episode_script_from_story(2, payload)
        assert script_data["episode_number"] == 2
        assert script_data["total_chapters"] == 6
        assert script_data["total_estimated_duration_sec"] >= 720, "Script must satisfy 12-min minimum broadcast length"

def run_all():
    print("==================================================================")
    print("Running Challenger Story Hub Adversarial Stress Test Suite")
    print("==================================================================\n")

    run_test("1. Short story boundary (<30 chars quarantined, 30 chars valid)", test_short_story_boundary)
    run_test("2. Long story boundary (3000 chars valid, 3001 chars quarantined)", test_long_story_boundary)
    run_test("3. Missing and null fields handling", test_missing_or_null_fields)
    run_test("4. Negative and huge cheer counts (log clamping)", test_negative_and_extreme_cheer)
    run_test("5. Excessive character repetition quarantine", test_character_repetition_quarantine)
    run_test("6. Low vocabulary diversity spam quarantine", test_low_vocabulary_diversity_spam)
    run_test("7. Prohibited commercial words quarantine", test_banned_commercial_words)
    run_test("8. Prohibited spam keywords quarantine", test_spam_black_words)
    run_test("9. URL and external link regex quarantine", test_url_detection)
    run_test("10. Created_at date decay and malformed dates", test_created_at_decay_and_malformed_dates)
    run_test("11. Empty story list and all-quarantined stories handling", test_select_top_story_empty_and_all_quarantined)
    run_test("12. Radio segmentation with zero punctuation", test_segmentation_with_no_punctuation)
    run_test("13. Radio script generation from dynamic story payload", test_radio_script_generation_with_edge_payloads)
    run_test("14. Adversarial AI Blacklist injection in user story", test_ai_blacklist_word_in_user_story)

    print("\n==================================================================")
    print(f"Summary: {len(passes)} PASSED, {len(failures)} FAILED")
    print("==================================================================")
    if failures:
        for name, err in failures:
            print(f"- {name}: {err}")
        sys.exit(1)
    else:
        print("[SUCCESS] All adversarial story hub stress tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    run_all()
