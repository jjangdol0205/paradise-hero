#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
select_top_story.py
Automated Multi-Factor Ranking & Story Selection Engine for Division 4 (paradise-hero.com)
Connects Senior Fan Stories to @김쌤의영웅라디오 YouTube Production Pipeline.

Equation:
    S = W_cheer * C_norm + W_emotion * E_norm + W_length * L_norm + W_song * K_song - P_decay
    Where:
      - W_cheer = 35.0, C_norm = min(1.0, ln(1 + cheer_count) / ln(1 + 200))
      - W_emotion = 30.0, E_norm based on emotional lexicons
      - W_length = 20.0, piecewise length curve (optimal 400~1200 chars)
      - W_song = 15.0, Hwang Young-woong repertoire match
      - P_decay = min(25.0, 1.2 * delta_days)
"""

import os
import sys
import json
import math
import re
import argparse
from datetime import datetime, timezone

# -----------------------------------------------------------------------------
# Configuration & Lexicons
# -----------------------------------------------------------------------------
HWANG_YOUNG_WOONG_REPERTOIRE = {
    "당신 편", "꽃구경", "당신꽃", "인사동 찻집", "함께해요",
    "황금빛 인생", "복덩이", "비나리", "비상"
}

# Ingestion Filter: Prohibited Commercial & Spam Words
PROHIBITED_COMMERCIAL_WORDS = [
    "최" + "저가", "할" + "인율", "특" + "가", "폭" + "탄세일"
]

SPAM_BLACK_WORDS = [
    "카지노", "바카라", "토토", "코인", "비트코인", "대출", "조건만남", "수익보장"
]

# Emotional Lexicons (Weighted by Category)
EMOTION_LEXICON_TEARS_HEALING = [
    "눈물", "울컥", "가슴", "치유", "위로", "품", "따뜻", "상처", "버팀목", "희망", "감사", "은혜", "기운"
]
EMOTION_LEXICON_FAMILY_SACRIFICE = [
    "남편", "자식", "딸", "아들", "어머니", "엄마", "청춘", "세월", "병간호", "홀로", "새벽", "고생"
]
EMOTION_LEXICON_DEVOTION = [
    "영웅", "영웅님", "파라다이스", "노래", "목소리", "콘서트", "중저음", "당신 편", "꽃구경", "비상"
]

URL_REGEX = re.compile(r"(https?://|www\.|t\.me/|open\.kakao\.com)", re.IGNORECASE)


def validate_story(story):
    """
    Layer 1: Ingestion Filter (Instant Quarantine check).
    Returns (is_valid: bool, reason: str).
    """
    content = story.get("story_content", "") or ""
    title = story.get("story_title", "") or ""
    full_text = f"{title} {content}"

    # 1. Commercial Buzzword Blacklist
    for word in PROHIBITED_COMMERCIAL_WORDS:
        if word in full_text:
            return False, f"Prohibited commercial buzzword detected: '{word}'"

    # 2. General Spam Blacklist
    for word in SPAM_BLACK_WORDS:
        if word in full_text:
            return False, f"Spam keyword detected: '{word}'"

    # 3. External Link Detection
    if URL_REGEX.search(full_text):
        return False, "External link or unauthorized URL detected"

    # 4. Length Bounds (60 to 3000 chars)
    char_len = len(content.strip())
    if char_len < 60:
        return False, f"Story content too short: {char_len} chars (min 60 required)"
    if char_len > 3000:
        return False, f"Story content too long: {char_len} chars (max 3000 allowed)"

    # 5. Character Repetition Ratio & Spam Patterns
    if re.search(r"(.)\1{6,}", content):
        return False, "Excessive character repetition detected"

    words = re.findall(r"\w+", content)
    if words:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.35 and len(words) > 30:
            return False, f"Low vocabulary diversity: unique word ratio {unique_ratio:.2f} < 0.35"

    return True, "Valid"


def compute_resonance_score(story, current_time=None):
    """
    Layer 2: Multi-Factor Resonance Scoring.
    Returns (score: float, breakdown: dict).
    """
    if current_time is None:
        current_time = datetime.now(timezone.utc)

    cheer_count = max(0, int(story.get("cheer_count", 0)))
    content = story.get("story_content", "") or ""
    song_title = (story.get("song_title", "") or "").strip()
    created_at_str = story.get("created_at")

    # 1. Cheer Resonance (Weight: 35.0)
    # Logarithmic scaling: min(1.0, ln(1 + cheer_count) / ln(1 + 200))
    c_norm = min(1.0, math.log(1 + cheer_count) / math.log(1 + 200))
    cheer_score = round(35.0 * c_norm, 2)

    # 2. Emotional Keyword Density (Weight: 30.0)
    score_sum = 0.0
    for kw in EMOTION_LEXICON_TEARS_HEALING:
        score_sum += content.count(kw) * 1.5
    for kw in EMOTION_LEXICON_FAMILY_SACRIFICE:
        score_sum += content.count(kw) * 1.5
    for kw in EMOTION_LEXICON_DEVOTION:
        score_sum += content.count(kw) * 1.0

    # Estimate sentence count
    sentence_markers = len(re.findall(r"[.!?\n]+", content))
    sentence_count = max(1, sentence_markers)
    e_norm = min(1.0, score_sum / (sentence_count * 1.8))
    emotion_score = round(30.0 * e_norm, 2)

    # 3. Narrative Length Curve (Weight: 20.0)
    L = len(content.strip())
    if L < 150:
        l_norm = 0.3
    elif 150 <= L < 400:
        l_norm = 0.3 + 0.7 * ((L - 150) / 250.0)
    elif 400 <= L <= 1200:
        l_norm = 1.0
    elif 1200 < L <= 2000:
        l_norm = 1.0 - 0.2 * ((L - 1200) / 800.0)
    else:
        l_norm = 0.6
    length_score = round(20.0 * l_norm, 2)

    # 4. Repertoire Song Match (Weight: 15.0)
    matched_song = False
    for standard_song in HWANG_YOUNG_WOONG_REPERTOIRE:
        if standard_song in song_title:
            matched_song = True
            break
    k_song = 1.0 if matched_song else 0.4
    song_score = round(15.0 * k_song, 2)

    # 5. Time Decay Penalty (1.2 pts per day elapsed, capped at 25.0)
    decay_penalty = 0.0
    if created_at_str:
        try:
            created_dt = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            delta_days = max(0.0, (current_time - created_dt).total_seconds() / 86400.0)
            decay_penalty = min(25.0, round(1.2 * delta_days, 2))
        except Exception:
            decay_penalty = 0.0

    total_score = max(0.0, min(100.0, cheer_score + emotion_score + length_score + song_score - decay_penalty))
    total_score = round(total_score, 1)

    breakdown = {
        "cheer_score": cheer_score,
        "emotion_score": emotion_score,
        "length_score": length_score,
        "song_score": song_score,
        "decay_penalty": decay_penalty
    }
    return total_score, breakdown


def assign_tier(score):
    """
    Layer 3: Automated Tiering.
    """
    if score >= 75.0:
        return "top_spotlight"
    elif score >= 50.0:
        return "heartfelt_resonant"
    else:
        return "community_feed"


def segment_story_for_radio(story):
    """
    Splits story text into spoken radio segments of ~120-180 characters.
    Returns list of dicts: [{"segment_index": int, "text": str, "pacing_pause_sec": float, "emotion": str}]
    """
    content = story.get("story_content", "").strip()

    # Split on Korean sentence boundaries
    raw_sentences = re.split(r"(?<=[.!?])\s+", content)
    chunks = []
    current_chunk = ""

    for s in raw_sentences:
        s = s.strip()
        if not s:
            continue
        if len(current_chunk) + len(s) + 1 <= 170:
            current_chunk = f"{current_chunk} {s}".strip() if current_chunk else s
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = s

    if current_chunk:
        chunks.append(current_chunk)

    if not chunks:
        chunks = [content]

    # Assign sequential emotional tones matching senior fan narration
    emotion_flow = [
        "grieving_loss",
        "despair_to_light",
        "tears_of_healing",
        "renewed_life",
        "heartfelt_gratitude"
    ]

    segments = []
    for idx, chunk in enumerate(chunks):
        emotion = emotion_flow[min(idx, len(emotion_flow) - 1)]
        pause = 2.0 if idx == len(chunks) - 1 else 1.3
        segments.append({
            "segment_index": idx + 1,
            "text": chunk,
            "pacing_pause_sec": pause,
            "emotion": emotion
        })

    return segments


def select_top_story(stories_path, min_score=50.0, auto_pick=True, update_json=False):
    """
    Processes all stories, computes scores, filters spam, and returns the top story.
    """
    if not os.path.exists(stories_path):
        raise FileNotFoundError(f"Stories file not found: {stories_path}")

    with open(stories_path, "r", encoding="utf-8") as f:
        stories = json.load(f)

    valid_stories = []
    current_time = datetime.now(timezone.utc)

    for story in stories:
        is_valid, reason = validate_story(story)
        if not is_valid:
            story["status"] = "quarantined"
            story["quarantine_reason"] = reason
            story["resonance_score"] = 0.0
            story["tier"] = "quarantined"
            continue

        score, breakdown = compute_resonance_score(story, current_time)
        story["resonance_score"] = score
        story["score_breakdown"] = breakdown
        story["tier"] = assign_tier(score)

        if story.get("status") not in ("selected_for_radio", "broadcast_completed"):
            story["status"] = "ranked"

        valid_stories.append(story)

    # Sort primarily by:
    # 1. status == 'selected_for_radio' first
    # 2. resonance_score descending
    # 3. cheer_count descending
    valid_stories.sort(
        key=lambda s: (
            1 if s.get("status") == "selected_for_radio" else 0,
            s.get("resonance_score", 0),
            s.get("cheer_count", 0)
        ),
        reverse=True
    )

    if update_json:
        with open(stories_path, "w", encoding="utf-8") as f:
            json.dump(stories, f, ensure_ascii=False, indent=2)

    if not valid_stories:
        return None, []

    top_story = valid_stories[0]
    return top_story, valid_stories


def build_radio_payload(top_story, episode_number=2):
    """
    Constructs the formatted JSON payload expected by generate_radio_script.py.
    """
    spoken_segments = segment_story_for_radio(top_story)

    payload = {
        "story_id": top_story.get("story_id"),
        "episode_number": episode_number,
        "sender_name": top_story.get("sender_name"),
        "sender_location": top_story.get("sender_location", ""),
        "song_title": top_story.get("song_title"),
        "story_title": top_story.get("story_title"),
        "story_content": top_story.get("story_content"),
        "cheer_count": top_story.get("cheer_count", 0),
        "resonance_score": top_story.get("resonance_score", 0.0),
        "spoken_segments": spoken_segments
    }
    return payload


def main():
    parser = argparse.ArgumentParser(description="Automated Top Story Selection Engine for Division 4")
    parser.add_argument("--stories-file", type=str, default="", help="Path to data/stories.json")
    parser.add_argument("--output", type=str, default="", help="Output path for selected story payload JSON")
    parser.add_argument("--min-score", type=float, default=50.0, help="Minimum resonance score threshold")
    parser.add_argument("--episode", type=int, default=2, help="Episode number to associate with selection")
    parser.add_argument("--auto-pick", action="store_true", default=True, help="Auto pick top ranked story")
    parser.add_argument("--update-json", action="store_true", default=False, help="Update data/stories.json with calculated scores")
    args = parser.parse_args()

    # Determine default path if omitted
    if not args.stories_file:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
        stories_file = os.path.join(base_dir, "stories.json")
    else:
        stories_file = os.path.abspath(args.stories_file)

    top_story, all_valid = select_top_story(
        stories_file,
        min_score=args.min_score,
        auto_pick=args.auto_pick,
        update_json=args.update_json
    )

    if not top_story:
        print("[!] No eligible stories found passing minimum criteria.", file=sys.stderr)
        sys.exit(1)

    payload = build_radio_payload(top_story, episode_number=args.episode)

    if args.output:
        out_path = os.path.abspath(args.output)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"[+] Top story selected: '{top_story.get('story_title')}' (Score: {top_story.get('resonance_score')}) -> Saved to {out_path}")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
