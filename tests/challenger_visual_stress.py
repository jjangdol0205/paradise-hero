#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
challenger_visual_stress.py
Adversarial Stress Test Suite for Photo Booth Visual Compositing Pipeline.
Stress tests master frame compositing with:
- Multiple aspect ratios (1:1 square, 16:9 landscape, 9:16 portrait, extreme panoramas, high-res 4032x3024)
- Color modes (RGBA, RGB, Grayscale L, Palette P)
- Extreme transformations (scale 0.1 to 4.0, translation +/- 500, rotation -180 to +180, flip)
- Output metrics: exactly 1080x1440, RGB mode, non-blank validation, and ColorStddev analysis.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageStat

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from tests.visual_pipeline import (
    apply_transform,
    composite_frame,
    WIDTH,
    HEIGHT,
    FRAMES_DIR,
    FRAME_FILES
)

OUT_DIR = os.path.join(BASE_DIR, "tests", "visual_output", "stress")
os.makedirs(OUT_DIR, exist_ok=True)

test_results = []

def create_gradient_test_image(w, h, mode="RGBA"):
    """Creates a synthetic gradient image of given dimensions and mode with details."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Gradient
    for y in range(h):
        r = int(255 * (y / max(1, h)))
        g = int(180 * (1 - y / max(1, h)))
        b = int(220 * (0.5 + 0.5 * (y / max(1, h))))
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))
    # Geometric shapes
    draw.ellipse([(w*0.2, h*0.2), (w*0.8, h*0.8)], fill=(40, 100, 200, 255))
    draw.rectangle([(w*0.3, h*0.4), (w*0.7, h*0.6)], fill=(255, 215, 0, 255))

    if mode == "RGB":
        return img.convert("RGB")
    elif mode == "L":
        return img.convert("L")
    elif mode == "P":
        return img.convert("P")
    return img

def run_stress_case(case_name, input_img, frame_name, scale, translate, rotation, flip_h):
    frame_path = os.path.join(FRAMES_DIR, frame_name)
    assert os.path.exists(frame_path), f"Frame missing: {frame_path}"

    # Ensure input image has alpha for clean compositing
    if input_img.mode != "RGBA":
        user_rgba = input_img.convert("RGBA")
    else:
        user_rgba = input_img

    user_tf = apply_transform(user_rgba, scale=scale, translate=translate, rotation=rotation, flip_h=flip_h)
    composite = composite_frame(user_tf, frame_path)

    # Validation
    is_exact_res = (composite.size == (WIDTH, HEIGHT))
    is_rgb = (composite.mode == "RGB")
    stat = ImageStat.Stat(composite)
    avg_std = sum(stat.stddev[:3]) / 3.0

    # Save artifact
    out_file = os.path.join(OUT_DIR, f"{case_name}.jpg")
    composite.save(out_file, "JPEG", quality=95)
    size_kb = os.path.getsize(out_file) / 1024.0

    result = {
        "case": case_name,
        "frame": frame_name,
        "resolution": composite.size,
        "mode": composite.mode,
        "color_stddev": round(avg_std, 2),
        "size_kb": round(size_kb, 1),
        "exact_res_pass": is_exact_res,
        "mode_pass": is_rgb,
        "stddev_pass": avg_std > 70.0
    }
    test_results.append(result)
    return result

def main():
    print("===============================================================")
    print("Running Challenger Photo Booth Visual Compositing Stress Tests")
    print("===============================================================\n")

    cases = [
        # (name, width, height, mode, frame, scale, translate, rot, flip)
        ("1_square_1000x1000", 1000, 1000, "RGBA", "frame_flower_path.png", 1.0, (0, 0), 0, False),
        ("2_landscape_1920x1080", 1920, 1080, "RGBA", "frame_golden_milestone.png", 0.9, (0, 0), 0, True),
        ("3_portrait_1080x1920", 1080, 1920, "RGBA", "frame_paradise_4cut.png", 1.0, (0, 0), 0, False),
        ("4_highres_4032x3024", 4032, 3024, "RGB", "frame_radio_studio.png", 0.35, (0, 0), 0, False),
        ("5_extreme_wide_3000x600", 3000, 600, "RGBA", "frame_flower_path.png", 1.2, (0, 0), 15, True),
        ("6_extreme_tall_600x3000", 600, 3000, "RGBA", "frame_golden_milestone.png", 0.8, (0, 0), -20, False),
        ("7_small_100x100", 100, 100, "RGBA", "frame_paradise_4cut.png", 4.0, (50, -50), 45, True),
        ("8_grayscale_1080x1440", 1080, 1440, "L", "frame_radio_studio.png", 1.0, (0, 0), 0, False),
        ("9_palette_800x1200", 800, 1200, "P", "frame_flower_path.png", 1.1, (-30, 40), 90, True),
        ("10_extreme_rotation_180", 1080, 1440, "RGBA", "frame_golden_milestone.png", 1.0, (0, 0), 180, False),
        ("11_extreme_scale_down_01", 1080, 1440, "RGBA", "frame_paradise_4cut.png", 0.1, (0, 0), 0, False),
        ("12_large_offset_outside", 1080, 1440, "RGBA", "frame_radio_studio.png", 1.0, (600, -800), 0, False),
    ]

    for name, w, h, mode, frame, sc, tr, rot, fl in cases:
        img = create_gradient_test_image(w, h, mode=mode)
        res = run_stress_case(name, img, frame, sc, tr, rot, fl)
        status = "[PASS]" if (res["exact_res_pass"] and res["mode_pass"]) else "[FAIL]"
        print(f"{status} {res['case']} ({frame}) -> Res: {res['resolution']}, Mode: {res['mode']}, Size: {res['size_kb']}KB, ColorStddev: {res['color_stddev']}")

    # Check ColorStddev distribution
    stddev_fails = [r for r in test_results if not r["stddev_pass"]]
    print(f"\nTotal cases tested: {len(test_results)}")
    print(f"Passed 1080x1440 exact res & RGB mode: {sum(1 for r in test_results if r['exact_res_pass'] and r['mode_pass'])} / {len(test_results)}")
    print(f"ColorStddev > 70.0: {sum(1 for r in test_results if r['stddev_pass'])} / {len(test_results)}")

    if stddev_fails:
        print("\nCases where ColorStddev <= 70.0:")
        for sf in stddev_fails:
            print(f"  - {sf['case']} ({sf['frame']}): ColorStddev = {sf['color_stddev']}")

if __name__ == "__main__":
    main()
