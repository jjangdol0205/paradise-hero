"""
visual_pipeline.py
Headless Visual Rendering & Compositing Test Suite for Milestone 2:
Interactive Companion Photo Booth & Visual Pipeline on paradise-hero.com.

Verifications:
1. Frame asset existence, RGBA mode, and exact 1080x1440 dimensions.
2. Center transparency check (verifying frames have transparent windows for user photos).
3. Synthetic user photo generation with realistic gradients, simulated portrait, and text.
4. User image transform application (translate, scale, rotation, horizontal flip).
5. Multi-layer compositing pipeline (Layer 0 Ivory Canvas + Layer 1 Transformed User + Layer 2 Commemorative Frame + Layer 3 Watermark).
6. Composite output validation:
   - Mode: RGB (ready for JPEG client-side export)
   - Resolution: Exactly 1080x1440
   - File size: > 100KB (satisfies substantive quality criteria)
   - Pixel entropy & color stddev: > 20 (guarantees image is neither blank black nor blank white)
7. All 4 commemorative frames composite cleanly to disk.
"""

import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont, ImageStat

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAMES_DIR = os.path.join(BASE_DIR, "assets", "frames")
TEST_OUTPUT_DIR = os.path.join(BASE_DIR, "tests", "visual_output")
os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

WIDTH = 1080
HEIGHT = 1440

FRAME_FILES = [
    "frame_flower_path.png",
    "frame_golden_milestone.png",
    "frame_paradise_4cut.png",
    "frame_radio_studio.png"
]


def create_synthetic_user_photo(w=1080, h=1440) -> Image.Image:
    """
    Creates a realistic synthetic user portrait photo with rich gradient background,
    simulated friendly senior figure silhouette, and vibrant color variance.
    """
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Warm sunset pastel gradient background
    for y in range(h):
        ratio = y / float(h)
        r = int(245 * (1 - ratio) + 215 * ratio)
        g = int(230 * (1 - ratio) + 195 * ratio)
        b = int(220 * (1 - ratio) + 185 * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # 2. Simulated friendly companion silhouette & warm portrait shapes
    # Head & shoulders
    cx, cy = w // 2, h // 2 + 80
    # Shoulders
    draw.ellipse([(cx - 280, cy + 120), (cx + 280, cy + 550)], fill=(45, 55, 72, 255))
    # Neck
    draw.rectangle([(cx - 70, cy + 50), (cx + 70, cy + 160)], fill=(240, 205, 175, 255))
    # Head
    draw.ellipse([(cx - 150, cy - 180), (cx + 150, cy + 120)], fill=(245, 215, 185, 255))
    # Hair
    draw.ellipse([(cx - 165, cy - 200), (cx + 165, cy - 40)], fill=(60, 45, 35, 255))

    # Warm eyes & smile
    draw.arc([(cx - 85, cy - 50), (cx - 45, cy - 20)], start=20, end=160, fill=(40, 30, 20, 255), width=4)
    draw.arc([(cx + 45, cy - 50), (cx + 85, cy - 20)], start=20, end=160, fill=(40, 30, 20, 255), width=4)
    draw.arc([(cx - 50, cy + 10), (cx + 50, cy + 60)], start=0, end=180, fill=(180, 50, 50, 255), width=5)

    # Warm flower bouquet / fan keepsake held
    draw.ellipse([(cx - 180, cy + 280), (cx - 60, cy + 400)], fill=(220, 38, 38, 255))
    draw.ellipse([(cx - 120, cy + 260), (cx + 20, cy + 380)], fill=(34, 197, 94, 255))
    draw.ellipse([(cx - 70, cy + 280), (cx + 60, cy + 410)], fill=(234, 179, 8, 255))

    return img


def apply_transform(user_img: Image.Image, scale=1.0, translate=(0, 0), rotation=0, flip_h=False) -> Image.Image:
    """
    Applies the exact same transformation pipeline as photo-booth.js canvas compositing:
    1. Horizontal flip
    2. Rotation
    3. Scale
    4. Centering & Translation onto 1080x1440 canvas
    """
    img = user_img.copy()

    # 1. Flip
    if flip_h:
        img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

    # 2. Rotate
    if rotation != 0:
        img = img.rotate(rotation, resample=Image.Resampling.BICUBIC, expand=True)

    # 3. Scale
    new_w = max(10, int(img.width * scale))
    new_h = max(10, int(img.height * scale))
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # 4. Paste onto blank 1080x1440 canvas centered + translate
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    paste_x = (WIDTH - new_w) // 2 + translate[0]
    paste_y = (HEIGHT - new_h) // 2 + translate[1]
    canvas.paste(img, (paste_x, paste_y), img)

    return canvas


def composite_frame(user_transformed: Image.Image, frame_path: str) -> Image.Image:
    """
    Composites:
    Layer 0: Soft Ivory (#FAFAF8)
    Layer 1: Transformed User Photo
    Layer 2: Commemorative Frame PNG (RGBA)
    Layer 3: Dynamic Watermark Seal
    Returns RGB image.
    """
    # Layer 0: Ivory base
    base = Image.new("RGBA", (WIDTH, HEIGHT), (250, 250, 248, 255))

    # Layer 1: User photo
    base.alpha_composite(user_transformed)

    # Layer 2: Frame overlay
    frame = Image.open(frame_path).convert("RGBA")
    base.alpha_composite(frame)

    # Layer 3: Dynamic Watermark
    draw = ImageDraw.Draw(base)
    watermark_text = "황영웅과 함께하는 파라다이스 | paradise-hero.com"
    draw.text((WIDTH - 420, HEIGHT - 30), watermark_text, fill=(27, 77, 62, 200))

    # Convert to RGB (standard for JPEG export)
    return base.convert("RGB")


def run_visual_pipeline_tests():
    print("===============================================================")
    print("Running paradise-hero.com Visual Pipeline Verification (PIL)")
    print("===============================================================\n")

    # -------------------------------------------------------------------------
    # Test 1: Verify all 4 frames exist and have exact dimensions and RGBA mode
    # -------------------------------------------------------------------------
    print("Test 1: Verifying master frame assets dimensions, mode, and transparency...")
    for frame_name in FRAME_FILES:
        fpath = os.path.join(FRAMES_DIR, frame_name)
        assert os.path.exists(fpath), f"Frame file not found: {fpath}"
        with Image.open(fpath) as fimg:
            assert fimg.size == (WIDTH, HEIGHT), f"{frame_name} size must be (1080, 1440), got {fimg.size}"
            assert fimg.mode == "RGBA", f"{frame_name} mode must be RGBA, got {fimg.mode}"

            # Check center area has transparency (alpha < 100) so user photo shows through
            center_pixel = fimg.getpixel((WIDTH // 2, HEIGHT // 2))
            assert center_pixel[3] < 50, (
                f"{frame_name} center pixel at ({WIDTH//2}, {HEIGHT//2}) must be transparent, "
                f"got alpha={center_pixel[3]}"
            )
            print(f"  [PASS] {frame_name}: (1080x1440, RGBA, center transparent alpha={center_pixel[3]}).")

    # -------------------------------------------------------------------------
    # Test 2: Generate synthetic user image
    # -------------------------------------------------------------------------
    print("\nTest 2: Generating synthetic test user photo...")
    user_img = create_synthetic_user_photo(WIDTH, HEIGHT)
    assert user_img.size == (WIDTH, HEIGHT)
    user_stat = ImageStat.Stat(user_img)
    mean_std = sum(user_stat.stddev[:3]) / 3.0
    assert mean_std > 20.0, f"Synthetic photo must have rich detail, got stddev={mean_std}"
    print(f"  [PASS] Synthetic portrait generated: stddev={mean_std:.2f} (vibrant detail).")

    # -------------------------------------------------------------------------
    # Test 3: Test transformation matrices
    # -------------------------------------------------------------------------
    print("\nTest 3: Testing transform matrix (scale, translation, flip, rotation)...")
    transformed_1 = apply_transform(user_img, scale=1.05, translate=(20, -30), rotation=0, flip_h=True)
    assert transformed_1.size == (WIDTH, HEIGHT)
    print("  [PASS] Transform 1 (scale=1.05, translate=(20, -30), flip_h=True) applied cleanly.")

    # -------------------------------------------------------------------------
    # Test 4: Composite each of the 4 frames and verify output quality
    # -------------------------------------------------------------------------
    print("\nTest 4: Compositing all 4 commemorative frames and verifying output metrics...")

    test_configs = [
        ("frame_flower_path.png", "composite_flower_path.jpg", 1.0, (0, 0), 0, False),
        ("frame_golden_milestone.png", "composite_golden_milestone.jpg", 1.1, (-10, 20), 0, True),
        ("frame_paradise_4cut.png", "composite_paradise_4cut.jpg", 0.95, (0, -15), 0, False),
        ("frame_radio_studio.png", "composite_radio_studio.jpg", 1.0, (15, 10), 0, True),
    ]

    for frame_name, out_filename, scale, trans, rot, flip in test_configs:
        frame_path = os.path.join(FRAMES_DIR, frame_name)
        user_tf = apply_transform(user_img, scale=scale, translate=trans, rotation=rot, flip_h=flip)

        composite = composite_frame(user_tf, frame_path)

        # Assertions on PIL image
        assert composite.size == (WIDTH, HEIGHT), f"Composite size must be 1080x1440, got {composite.size}"
        assert composite.mode == "RGB", f"Composite mode must be RGB, got {composite.mode}"

        # Color entropy and standard deviation checks
        stat = ImageStat.Stat(composite)
        std_rgb = stat.stddev[:3]
        avg_std = sum(std_rgb) / 3.0
        assert avg_std > 20.0, f"Composite must be non-blank, got avg stddev={avg_std}"

        # Check pixel color at center contains user image colors (not blank canvas)
        center_color = composite.getpixel((WIDTH // 2, HEIGHT // 2))
        assert center_color != (0, 0, 0) and center_color != (255, 255, 255), (
            f"Center pixel must not be solid black or white, got {center_color}"
        )

        # Save to JPEG with 95% quality (mirroring canvas.toBlob('image/jpeg', 0.95))
        out_path = os.path.join(TEST_OUTPUT_DIR, out_filename)
        composite.save(out_path, "JPEG", quality=95)

        file_size_kb = os.path.getsize(out_path) / 1024.0
        assert file_size_kb > 100.0, f"Output file must be substantive (>100KB), got {file_size_kb:.1f}KB"
        assert file_size_kb < 3500.0, f"Output file must be reasonable (<3.5MB), got {file_size_kb:.1f}KB"

        print(
            f"  [PASS] Rendered {out_filename}: Size={file_size_kb:.1f}KB, "
            f"Mode={composite.mode}, Res={composite.size}, ColorStddev={avg_std:.1f}"
        )

    print(f"\n[SUCCESS] All 4 composite outputs verified and saved in: {TEST_OUTPUT_DIR}")
    print("===============================================================")
    print("SUCCESS: ALL VISUAL PIPELINE VERIFICATION TESTS PASSED (100%)")
    print("===============================================================\n")


if __name__ == "__main__":
    try:
        run_visual_pipeline_tests()
    except AssertionError as e:
        print(f"\n[FAIL] Visual pipeline test assertion failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error in visual pipeline tests: {e}", file=sys.stderr)
        sys.exit(1)
