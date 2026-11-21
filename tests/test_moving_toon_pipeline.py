#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_moving_toon_pipeline.py
================================================================================
End-to-End Automated Test Suite for Div 4 Korean Moving-Toon (#영상툰) Engine,
Photo Booth Character Identity, Anti-Spam Staggered Scheduling & Guardrails.
================================================================================
"""

import os
import sys
import json
import unittest
from pathlib import Path
from datetime import datetime

DIV4_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DIV4_DIR / "scripts"))

from yeongung_moving_toon_engine import sanitize_canvas_text, wrap_subtitle_lines, PROHIBITED_WORDS
from auto_youtube_moving_toon_manager import compute_staggered_slots_from_now, build_episode_description
from expand_daily_moving_toon_stories import ensure_fresh_episodes


class TestMovingToonPipeline(unittest.TestCase):
    def test_all_10_photo_booth_characters_and_costar_assets_exist(self):
        for i in range(1, 11):
            p = DIV4_DIR / "assets" / "characters" / f"raw_prince_{i}.png"
            self.assertTrue(p.exists(), f"Missing Photo Booth character: {p}")
        for m in ["mother_tearful", "mother_blush_happy", "mother_surprised", "mother_cheering"]:
            p = DIV4_DIR / "assets" / "moving_toon" / f"{m}.png"
            self.assertTrue(p.exists(), f"Missing Mother co-star sprite: {p}")
        for c in ["cut_action_hand_rose", "cut_action_coat_umbrella", "cut_action_radio_onair", "cut_action_hanbok_bouquet"]:
            p = DIV4_DIR / "assets" / "moving_toon" / f"{c}.png"
            self.assertTrue(p.exists(), f"Missing Webtoon action panel: {p}")

    def test_episodes_bank_covers_all_10_outfits_and_zero_prohibited_words(self):
        data = json.loads((DIV4_DIR / "data" / "moving_toon_episodes.json").read_text(encoding="utf-8"))
        eps = data["episodes"]
        self.assertGreaterEqual(len(eps), 5)
        blob = json.dumps(data, ensure_ascii=False)
        for bad in PROHIBITED_WORDS:
            self.assertNotIn(bad, blob, f"Prohibited word '{bad}' detected!")
        featured = set()
        for ep in eps[:5]:
            featured.update(ep.get("outfits_featured", []))
            desc = build_episode_description(ep)
            self.assertIn("https://paradise-hero.com/booth.html", desc)
            for bad in PROHIBITED_WORDS:
                self.assertNotIn(bad, desc)
        self.assertEqual(featured, set(range(1, 11)), "First 5 episodes must showcase all 10 Photo Booth outfits!")

    def test_sanitize_canvas_text_zero_tofu(self):
        s = sanitize_canvas_text("외로울 땐 기대세요 ❤️👑🌹✨")
        self.assertTrue(all(ord(ch) <= 0xFFFF for ch in s))
        self.assertIn("♥", s)

    def test_wrap_subtitle_preserves_exact_word_order(self):
        orig = "거울 속 흰머리를 보며 한숨이 나오던 날"
        lines = wrap_subtitle_lines(orig, max_chars=19)
        self.assertEqual(" ".join(lines), orig)

    def test_anti_spam_staggered_slots_max_3_per_day(self):
        now = datetime(2026, 11, 11, 4, 30)
        slots = compute_staggered_slots_from_now(now, count=5, first_immediate=True)
        self.assertEqual(len(slots), 5)
        self.assertIsNone(slots[0])
        # Count uploads per calendar day
        counts = {}
        for s in slots:
            d = now.date() if s is None else s.date()
            counts[d] = counts.get(d, 0) + 1
        for d, cnt in counts.items():
            self.assertLessEqual(cnt, 3, f"Exceeded 3 uploads/day anti-spam cap on {d}: {cnt}")


if __name__ == "__main__":
    unittest.main()
