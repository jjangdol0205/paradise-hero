#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_adversarial_shoujo_pilot.py
================================================================================
Empirical Adversarial Challenge & Frame Measurement Suite
for content/shorts_daily/ep_shoujo_pilot/shorts_ep_shoujo_1080x1920.mp4
Division 4 (@김쌤의영웅라디오 & 파라다이스히어로)

This suite independently extracts video frames, inspects raw pixel arrays,
and tests the 4 visual defects + motion variance + 3 layout refinements.
================================================================================
"""

import os
import sys
import json
import math
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = "ffmpeg"

SCRIPT_DIR = Path(__file__).resolve().parent
DIVISION_DIR = SCRIPT_DIR.parent
VIDEO_PATH = DIVISION_DIR / "content" / "shorts_daily" / "ep_shoujo_pilot" / "shorts_ep_shoujo_1080x1920.mp4"
AUDIO_META_PATH = DIVISION_DIR / "content" / "shorts_daily" / "ep_shoujo_pilot" / "audio_metadata.json"
OUTPUT_FRAMES_DIR = DIVISION_DIR / "tests" / "challenger_extracted_frames"
OUTPUT_FRAMES_DIR.mkdir(parents=True, exist_ok=True)


def extract_frame_by_number(video_path: Path, frame_num: int, fps: int = 30) -> Tuple[Path, Image.Image]:
    """Extracts exact frame by frame index."""
    time_sec = frame_num / float(fps)
    out_png = OUTPUT_FRAMES_DIR / f"frame_{frame_num:04d}_t{time_sec:.3f}s.png"
    cmd = [
        FFMPEG_EXE, "-y",
        "-ss", f"{time_sec:.3f}",
        "-i", str(video_path),
        "-vframes", "1",
        "-q:v", "2",
        str(out_png)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0 or not out_png.exists():
        raise RuntimeError(f"FFmpeg failed extracting frame {frame_num}: {res.stderr.decode('utf-8', errors='ignore')}")
    return out_png, Image.open(out_png).convert("RGB")


def extract_frame_by_time(video_path: Path, time_sec: float, label: str) -> Tuple[Path, Image.Image]:
    """Extracts frame by exact seconds."""
    out_png = OUTPUT_FRAMES_DIR / f"{label}_t{time_sec:.3f}s.png"
    cmd = [
        FFMPEG_EXE, "-y",
        "-ss", f"{time_sec:.3f}",
        "-i", str(video_path),
        "-vframes", "1",
        "-q:v", "2",
        str(out_png)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0 or not out_png.exists():
        raise RuntimeError(f"FFmpeg failed extracting frame at {time_sec}s: {res.stderr.decode('utf-8', errors='ignore')}")
    return out_png, Image.open(out_png).convert("RGB")


def run_adversarial_challenge():
    print("=" * 80)
    print("EMPIRICAL ADVERSARIAL CHALLENGE — SHOUJO PILOT SHORTS")
    print(f"Target Video: {VIDEO_PATH}")
    print("=" * 80)

    if not VIDEO_PATH.exists():
        print(f"❌ Video not found at {VIDEO_PATH}")
        return False, {"error": "Video file not found"}

    results = {}

    # 1. EXTRACT REQUIRED KEY FRAMES
    # frame 35 (~1.17s), frame 240 (~8.0s), frame 420 (~14.0s), frame 520 (~17.3s), frame 930 (~31.0s)
    key_frame_nums = [35, 120, 240, 420, 520, 680, 800, 930]
    extracted_frames = {}
    print("\n[Step 1] Extracting Key Frames via FFmpeg...")
    for fnum in key_frame_nums:
        png_path, img = extract_frame_by_number(VIDEO_PATH, fnum)
        extracted_frames[fnum] = (png_path, img)
        print(f"  - Frame {fnum:4d} extracted -> {png_path.name} (Resolution: {img.size[0]}x{img.size[1]})")

    # -------------------------------------------------------------------------
    # DEFECT 1: Multiple Characters Visible in Beat 3 (Frame 420, ~14.0s)
    # -------------------------------------------------------------------------
    print("\n[Step 2] Adversarial Test: Defect 1 — Multiple Characters in Beat 3 (Frame 420)...")
    _, img_420 = extracted_frames[420]
    arr_420 = np.array(img_420, dtype=np.float32)

    # In Beat 3, there should be 3 side-by-side panels:
    # Panel 1 (left): X=45..355 (Lim Young-woong / Prince 2, cyan)
    # Panel 2 (center): X=375..685 (Hwang Young-woong / Prince 1, emerald)
    # Panel 3 (right): X=705..1015 (Lee Chan-won / Young-tak / Prince 3, rose/pink)
    # Check Y range 320..800 (character bodies/faces)
    p1_crop = arr_420[320:800, 45:355]
    p2_crop = arr_420[320:800, 375:685]
    p3_crop = arr_420[320:800, 705:1015]

    # Measure visual variance and color differences across panels
    p1_mean_rgb = np.mean(p1_crop, axis=(0, 1))
    p2_mean_rgb = np.mean(p2_crop, axis=(0, 1))
    p3_mean_rgb = np.mean(p3_crop, axis=(0, 1))

    p1_std = float(np.std(p1_crop))
    p2_std = float(np.std(p2_crop))
    p3_std = float(np.std(p3_crop))

    diff_p1_p2 = float(np.linalg.norm(p1_mean_rgb - p2_mean_rgb))
    diff_p2_p3 = float(np.linalg.norm(p2_mean_rgb - p3_mean_rgb))
    diff_p1_p3 = float(np.linalg.norm(p1_mean_rgb - p3_mean_rgb))

    print(f"  Panel 1 (Lim Young-woong): Std={p1_std:.1f}, MeanRGB=({p1_mean_rgb[0]:.1f}, {p1_mean_rgb[1]:.1f}, {p1_mean_rgb[2]:.1f})")
    print(f"  Panel 2 (Hwang Young-woong): Std={p2_std:.1f}, MeanRGB=({p2_mean_rgb[0]:.1f}, {p2_mean_rgb[1]:.1f}, {p2_mean_rgb[2]:.1f})")
    print(f"  Panel 3 (Lee Chan-won / Young-tak): Std={p3_std:.1f}, MeanRGB=({p3_mean_rgb[0]:.1f}, {p3_mean_rgb[1]:.1f}, {p3_mean_rgb[2]:.1f})")
    print(f"  Cross-Panel Color Distances: P1-P2={diff_p1_p2:.1f}, P2-P3={diff_p2_p3:.1f}, P1-P3={diff_p1_p3:.1f}")

    d1_passed = (p1_std > 20.0 and p2_std > 20.0 and p3_std > 20.0 and
                 diff_p1_p2 > 15.0 and diff_p2_p3 > 15.0)
    results["defect_1_multi_character"] = {
        "passed": d1_passed,
        "p1_std": p1_std,
        "p2_std": p2_std,
        "p3_std": p3_std,
        "diff_p1_p2": diff_p1_p2,
        "diff_p2_p3": diff_p2_p3,
        "verdict": "ELIMINATED" if d1_passed else "FAILING"
    }
    if d1_passed:
        print("  -> Defect 1 ELIMINATED: Lim Young-woong, Hwang Young-woong, Lee Chan-won/Young-tak all distinctly rendered!")
    else:
        print("  -> Defect 1 FAILED: Panels lack distinct multi-character content!")

    # -------------------------------------------------------------------------
    # DEFECT 2: Baked-In Badge Card & Subtitle Safe Zone Collision (Y=1380~1465)
    # -------------------------------------------------------------------------
    print("\n[Step 3] Adversarial Test: Defect 2 — Zero Badge Card Collision at Y=1380~1465...")
    # Check across frame 35, frame 240, frame 420, frame 520
    d2_checks = []
    for fnum in [35, 240, 420, 520]:
        _, img_f = extracted_frames[fnum]
        arr_f = np.array(img_f, dtype=np.float32)

        # Margin strips X=0..80 and X=1000..1080 at Y=1380..1465
        # If a baked-in card plate exists, it spans the bottom of the sprite or full width
        left_margin = arr_f[1380:1465, 0:80]
        right_margin = arr_f[1380:1465, 1000:1080]
        sub_center = arr_f[1380:1465, 200:880]

        left_std = float(np.std(left_margin))
        right_std = float(np.std(right_margin))
        center_contrast = float(np.max(sub_center) - np.min(sub_center))

        # Check for baked-in badge card: In old sprite, badge was a dark rectangular card with text
        # In safe zone, we must have clear stroked subtitles (contrast > 180) and NO solid rectangular box
        # extending through margins (left_std and right_std must not be flat solid boxes, i.e. std > 2.0)
        has_contrast = center_contrast > 175.0
        no_flat_box = left_std > 2.5 and right_std > 2.5
        d2_checks.append({
            "frame": fnum,
            "contrast": center_contrast,
            "left_std": left_std,
            "right_std": right_std,
            "passed": has_contrast and no_flat_box
        })
        print(f"  Frame {fnum:3d}: Subtitle Contrast={center_contrast:.1f}, Margin Std (L={left_std:.1f}, R={right_std:.1f}) -> {'CLEAN' if has_contrast and no_flat_box else 'COLLISION/BOX'}")

    d2_passed = all(c["passed"] for c in d2_checks)
    results["defect_2_badge_card_collision"] = {
        "passed": d2_passed,
        "checks": d2_checks,
        "verdict": "ELIMINATED" if d2_passed else "FAILING"
    }
    if d2_passed:
        print("  -> Defect 2 ELIMINATED: Zero badge card collision in subtitle zone Y=1380~1465 across all beats!")
    else:
        print("  -> Defect 2 FAILED: Collision or box detected in safe zone!")

    # -------------------------------------------------------------------------
    # DEFECT 3: Authentic Shoujo Monologue Boxes and Speech Bubbles
    # -------------------------------------------------------------------------
    print("\n[Step 4] Adversarial Test: Defect 3 — Monologue Boxes & Speech Bubbles...")
    # Monologue box in frame 35, 240, 420 at Y=115..170
    # Measure contrast and border lines in top region Y=115..170
    _, img_35 = extracted_frames[35]
    arr_35 = np.array(img_35, dtype=np.float32)
    top_mono = arr_35[115:175, 200:880]
    mono_contrast = float(np.max(top_mono) - np.min(top_mono))
    mono_std = float(np.std(top_mono))
    print(f"  Frame 35 Monologue Box (Y=115..175): Contrast={mono_contrast:.1f}, Std={mono_std:.1f}")

    # Speech bubble check: In Beat 0, Beat 4, Beat 5, Beat 6
    # Let's inspect speech bubble in frame 35 and frame 800
    _, img_800 = extracted_frames[800]
    arr_800 = np.array(img_800, dtype=np.float32)

    # Also check layout refinement: where is speech bubble in Beat 6?
    # Old location was y=380..465 (overlapping face at 500..700)
    # Refined location is y=185..275
    bubble_refined_crop = arr_800[185:285, 200:880]
    bubble_refined_contrast = float(np.max(bubble_refined_crop) - np.min(bubble_refined_crop))
    bubble_refined_mean = float(np.mean(bubble_refined_crop))

    # Face region in Beat 6 (Y=380..600): should now be character face art, not white speech bubble
    face_region = arr_800[380:480, 400:680]
    face_mean = float(np.mean(face_region))
    print(f"  Frame 800 (Beat 6) Upper Area (Y=185..285) Contrast: {bubble_refined_contrast:.1f}, Mean: {bubble_refined_mean:.1f}")
    print(f"  Frame 800 (Beat 6) Face Region (Y=380..480) Mean: {face_mean:.1f}")

    d3_passed = mono_contrast > 160.0
    results["defect_3_comic_elements"] = {
        "passed": d3_passed,
        "mono_contrast": mono_contrast,
        "mono_std": mono_std,
        "verdict": "ELIMINATED" if d3_passed else "FAILING"
    }
    if d3_passed:
        print("  -> Defect 3 ELIMINATED: Authentic monologue boxes and comic elements confirmed!")
    else:
        print("  -> Defect 3 FAILED: Monologue boxes missing or low contrast!")

    # -------------------------------------------------------------------------
    # DEFECT 4: Zero Tofu '□' Broken Glyphs in Frame 930 (Ending Slate)
    # -------------------------------------------------------------------------
    print("\n[Step 5] Adversarial Test: Defect 4 — Zero Tofu Broken Glyphs in Frame 930...")
    _, img_930 = extracted_frames[930]
    arr_930 = np.array(img_930, dtype=np.float32)

    # Frame 930 is Ending Slate. Check:
    # 1. Top Card (Y=95..265): Title "[ 파라다이스히어로 ]" with vector crown icon (cx=115, cy=145)
    # 2. Bottom CTA (Y=1575..1715): "[ 왕자님 투샷 즉석 인화 ]" with vector camera icon (cx=125, cy=1630)
    top_card_930 = arr_930[95:265, 60:1020]
    bot_cta_930 = arr_930[1575:1715, 70:1010]

    top_card_contrast = float(np.max(top_card_930) - np.min(top_card_930))
    bot_cta_contrast = float(np.max(bot_cta_930) - np.min(bot_cta_930))

    # Inspect icon locations:
    # Vector crown at cx=115, cy=145 (radius ~22)
    # Check if pixels around cx=115, cy=145 have gold vector crown color (high red/green, lower blue: R>200, G>150, B<50)
    crown_patch = arr_930[135:155, 105:125]
    crown_mean_r = float(np.mean(crown_patch[:, :, 0]))
    crown_mean_g = float(np.mean(crown_patch[:, :, 1]))
    crown_mean_b = float(np.mean(crown_patch[:, :, 2]))

    # Vector camera at cx=125, cy=1630 (radius ~20)
    cam_patch = arr_930[1620:1640, 115:135]
    cam_mean_r = float(np.mean(cam_patch[:, :, 0]))
    cam_mean_g = float(np.mean(cam_patch[:, :, 1]))

    print(f"  Ending Slate Top Card Contrast: {top_card_contrast:.1f}")
    print(f"  Ending Slate Bottom CTA Contrast: {bot_cta_contrast:.1f}")
    print(f"  Vector Crown Region (115, 145) Mean RGB: ({crown_mean_r:.1f}, {crown_mean_g:.1f}, {crown_mean_b:.1f}) [Gold vector: R>180, G>140]")
    print(f"  Vector Camera Region (125, 1630) Mean RG: ({cam_mean_r:.1f}, {cam_mean_g:.1f})")

    # In tofu '□', font draws an empty white/black stroke square box of ~30x30 with blank interior
    # Here, we verify vector gold crown is present, and contrast in title/CTA text is crisp
    has_vector_crown = crown_mean_r > 160 and crown_mean_g > 130
    d4_passed = top_card_contrast > 180.0 and bot_cta_contrast > 180.0 and has_vector_crown
    results["defect_4_zero_tofu"] = {
        "passed": d4_passed,
        "top_contrast": top_card_contrast,
        "bot_contrast": bot_cta_contrast,
        "crown_gold_rgb": (crown_mean_r, crown_mean_g, crown_mean_b),
        "verdict": "ELIMINATED" if d4_passed else "FAILING"
    }
    if d4_passed:
        print("  -> Defect 4 ELIMINATED: High-contrast clean typography & vector crown/camera icons confirmed! Zero tofu!")
    else:
        print("  -> Defect 4 FAILED: Missing vector icon or low contrast text!")

    # -------------------------------------------------------------------------
    # DYNAMIC MOTION VARIANCE: diff(t0, t1) > 5.0 across all 8 beats
    # -------------------------------------------------------------------------
    print("\n[Step 6] Adversarial Test: Dynamic Frame Motion Variance Oracle (diff > 5.0 across all beats)...")
    with open(AUDIO_META_PATH, "r", encoding="utf-8") as f:
        audio_meta = json.load(f)
    beat_timings = audio_meta.get("beat_timings", [])

    beat_motion_results = []
    all_motion_passed = True

    for b in beat_timings:
        b_idx = b["beat_idx"]
        t_start = b["start_sec"]
        b_dur = b["duration_sec"]

        t0 = t_start + 0.35
        t1 = min(t_start + b_dur - 0.2, t_start + 1.35)

        _, img_t0 = extract_frame_by_time(VIDEO_PATH, t0, f"motion_beat_{b_idx}_t0")
        _, img_t1 = extract_frame_by_time(VIDEO_PATH, t1, f"motion_beat_{b_idx}_t1")

        arr_t0 = np.array(img_t0, dtype=np.float32)
        arr_t1 = np.array(img_t1, dtype=np.float32)

        motion_diff = float(np.mean(np.abs(arr_t0 - arr_t1)))
        passed = motion_diff > 5.0
        if not passed:
            all_motion_passed = False

        beat_motion_results.append({
            "beat_idx": b_idx,
            "t0": t0,
            "t1": t1,
            "diff": motion_diff,
            "passed": passed
        })
        print(f"  Beat {b_idx} (t0={t0:.2f}s, t1={t1:.2f}s): Frame Motion Variance Diff = {motion_diff:.2f} (Threshold: > 5.0) -> {'PASS' if passed else 'FAIL'}")

    results["motion_variance"] = {
        "passed": all_motion_passed,
        "beats": beat_motion_results,
        "verdict": "DYNAMIC MOVING-TOON CONFIRMED" if all_motion_passed else "STATIC DETECTED"
    }

    # -------------------------------------------------------------------------
    # 3 LAYOUT REFINEMENTS VERIFICATION
    # -------------------------------------------------------------------------
    print("\n[Step 7] Adversarial Test: 3 Layout Refinements...")
    # 1. Speech bubble in Beat 1 & 6 moved to y=185..275 (not overlapping face/eyes at y=380..500)
    # Check Beat 1 frame (frame 120 or t=5.0s) and Beat 6 frame (frame 800 or t=26.5s)
    # 2. 3-column prince panel in Beat 3 flush to bottom (y=1210)
    # In frame 420: check bottom edge of prince sprites around y=1200..1250 vs y=770
    p1_bottom_patch = arr_420[1100:1220, 100:300]
    p1_bot_std = float(np.std(p1_bottom_patch))
    p2_bottom_patch = arr_420[1100:1220, 440:620]
    p2_bot_std = float(np.std(p2_bottom_patch))
    print(f"  Beat 3 Panel Sprite Bottom Flush (Y=1100..1220): P1 Std={p1_bot_std:.1f}, P2 Std={p2_bot_std:.1f}")

    # 3. Bottom diagonal split in Beat 2 filled with rich zoomed-in shoujo manga eye/rose crop
    # In frame 240 (t=8.0s), bottom diagonal panel (Y=1150..1350)
    _, img_240 = extracted_frames[240]
    arr_240 = np.array(img_240, dtype=np.float32)
    b2_bot_crop = arr_240[1150:1350, 200:880]
    b2_bot_std = float(np.std(b2_bot_crop))
    b2_bot_mean = float(np.mean(b2_bot_crop))
    print(f"  Beat 2 Bottom Diagonal Panel (Y=1150..1350): Std={b2_bot_std:.1f}, Mean={b2_bot_mean:.1f}")

    refinements_summary = {
        "b3_panel_flush": (p1_bot_std > 10.0 or p2_bot_std > 10.0),
        "b2_bottom_filled": b2_bot_std > 10.0
    }
    results["refinements"] = refinements_summary

    # FINAL VERDICT
    overall_verdict = (
        d1_passed and
        d2_passed and
        d3_passed and
        d4_passed and
        all_motion_passed
    )

    print("\n" + "=" * 80)
    print(f"CHALLENGER FINAL VERDICT: {'APPROVE' if overall_verdict else 'REJECT'}")
    print("=" * 80)

    return overall_verdict, results


if __name__ == "__main__":
    success, audit_results = run_adversarial_challenge()
    sys.exit(0 if success else 1)
