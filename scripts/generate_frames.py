"""
generate_frames.py
Generates 4 high-resolution (1080x1440, 3:4 portrait) commemorative transparent PNG frames
and corresponding thumbnails (160x213) for paradise-hero.com Companion Photo Booth.

Frames:
1. frame_flower_path.png: "영웅님과 함께하는 다정한 꽃길"
2. frame_golden_milestone.png: "정규 1집 [당신 편] 63만 장 돌파 기념 골드 엠블럼"
3. frame_paradise_4cut.png: "파라다이스 인생 네컷 클래식"
4. frame_radio_studio.png: "김쌤의 영웅 라디오 특별 초대석"
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1080
HEIGHT = 1440
THUMB_W = 160
THUMB_H = 213

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "assets", "frames")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Font loading helper
def get_font(size: int, bold: bool = False):
    font_paths = [
        "C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/batang.ttc",
        "C:/Windows/Fonts/gulim.ttc",
        "C:/Windows/Fonts/arial.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

font_title = get_font(44, bold=True)
font_subtitle = get_font(28, bold=True)
font_badge = get_font(24, bold=True)
font_small = get_font(20, bold=False)
font_watermark = get_font(22, bold=True)


def draw_flower_vine(draw, x, y, size, color):
    """Draws a decorative floral/leaf motif."""
    # Petals
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        px = x + int(math.cos(rad) * size)
        py = y + int(math.sin(rad) * size)
        draw.ellipse([(px - size // 2, py - size // 2), (px + size // 2, py + size // 2)], fill=color)
    # Center pistil
    draw.ellipse([(x - size // 3, y - size // 3), (x + size // 3, y + size // 3)], fill=(212, 175, 55, 230))


def draw_stars(draw, points, color):
    """Draws 4-point golden sparkle stars."""
    for (cx, cy, r) in points:
        # Cross sparkle
        draw.polygon([(cx, cy - r), (cx + r // 4, cy - r // 4), (cx + r, cy), (cx + r // 4, cy + r // 4),
                      (cx, cy + r), (cx - r // 4, cy + r // 4), (cx - r, cy), (cx - r // 4, cy - r // 4)],
                     fill=color)


# ==============================================================================
# Frame 1: "영웅님과 함께하는 다정한 꽃길 (Flower Path Companion)"
# ==============================================================================
def create_frame_flower_path():
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Elegant emerald & gold outer border
    emerald = (27, 77, 62, 245)      # #1B4D3E
    gold = (212, 175, 55, 255)        # #D4AF37
    gold_soft = (235, 205, 115, 200)

    # Top & bottom thick headers
    draw.rectangle([(0, 0), (WIDTH, 90)], fill=(27, 77, 62, 230))
    draw.rectangle([(0, HEIGHT - 130), (WIDTH, HEIGHT)], fill=(27, 77, 62, 230))

    # Inner ornate border lines
    draw.rectangle([(30, 110), (WIDTH - 30, HEIGHT - 150)], outline=gold, width=4)
    draw.rectangle([(42, 122), (WIDTH - 42, HEIGHT - 162)], outline=(27, 77, 62, 180), width=2)
    draw.rectangle([(50, 130), (WIDTH - 50, HEIGHT - 170)], outline=gold_soft, width=1)

    # Corner floral ornaments
    corners = [(70, 150), (WIDTH - 70, 150), (70, HEIGHT - 190), (WIDTH - 70, HEIGHT - 190)]
    for cx, cy in corners:
        draw_flower_vine(draw, cx, cy, 14, (39, 174, 96, 210))
        draw_stars(draw, [(cx, cy, 18)], gold)

    # Gold sparkles along the sides
    sparkles = [
        (46, 350, 10), (46, 600, 12), (46, 850, 10), (46, 1100, 12),
        (WIDTH - 46, 350, 10), (WIDTH - 46, 600, 12), (WIDTH - 46, 850, 10), (WIDTH - 46, 1100, 12)
    ]
    draw_stars(draw, sparkles, gold)

    # Top header text
    header_title = "영웅님과 함께 걷는 다정한 꽃길"
    draw.text((WIDTH // 2, 45), header_title, font=font_subtitle, fill=(255, 255, 255, 255), anchor="mm")

    # Bottom commemorative banner
    banner_main = "언제나 당신 편, 영원히 함께해요"
    draw.text((WIDTH // 2, HEIGHT - 85), banner_main, font=font_title, fill=gold, anchor="mm")

    banner_sub = "파라다이스 공식 포토부스 | paradise-hero.com"
    draw.text((WIDTH // 2, HEIGHT - 35), banner_sub, font=font_small, fill=(240, 240, 240, 220), anchor="mm")

    # Gentle companion badge silhouette / motif on bottom right
    # (Stylized heart & companion emblem)
    badge_x, badge_y = WIDTH - 160, HEIGHT - 230
    draw.ellipse([(badge_x - 55, badge_y - 55), (badge_x + 55, badge_y + 55)], fill=(27, 77, 62, 220), outline=gold, width=3)
    draw.text((badge_x, badge_y - 12), "당신 편", font=font_badge, fill=gold, anchor="mm")
    draw.text((badge_x, badge_y + 16), "황영웅", font=font_small, fill=(255, 255, 255, 230), anchor="mm")

    return img


# ==============================================================================
# Frame 2: "정규 1집 [당신 편] 63만 장 기념 골드 엠블럼 (630K Golden Milestone)"
# ==============================================================================
def create_frame_golden_milestone():
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    gold = (212, 175, 55, 255)
    gold_dark = (166, 124, 0, 255)
    gold_light = (255, 223, 100, 255)
    royal_black = (20, 18, 15, 240)

    # Outer ornate double gold border
    draw.rectangle([(15, 15), (WIDTH - 15, HEIGHT - 15)], outline=gold, width=8)
    draw.rectangle([(28, 28), (WIDTH - 28, HEIGHT - 28)], outline=gold_dark, width=2)
    draw.rectangle([(40, 40), (WIDTH - 40, HEIGHT - 40)], outline=gold_light, width=3)

    # Top royal crown banner
    draw.rectangle([(70, 30), (WIDTH - 70, 150)], fill=royal_black, outline=gold, width=4)
    draw.text((WIDTH // 2, 70), "FIRST ALBUM [당신 편] 초동 63만 장 돌파 기념", font=font_subtitle, fill=gold_light, anchor="mm")
    draw.text((WIDTH // 2, 115), "대한민국 가요계의 역사, 황영웅과 파라다이스 가족", font=font_small, fill=(255, 255, 255, 220), anchor="mm")

    # Bottom golden plaque
    draw.rectangle([(70, HEIGHT - 170), (WIDTH - 70, HEIGHT - 35)], fill=royal_black, outline=gold, width=4)
    draw.text((WIDTH // 2, HEIGHT - 125), "골든 레코드 공식 헌정 엠블럼", font=font_title, fill=gold, anchor="mm")
    draw.text((WIDTH // 2, HEIGHT - 70), "GOLDEN MILESTONE 630,000+ COPIES | paradise-hero.com", font=font_badge, fill=gold_light, anchor="mm")

    # Golden vinyl record motif on bottom left corner
    vl_x, vl_y = 170, HEIGHT - 240
    # Outer vinyl ring
    draw.ellipse([(vl_x - 80, vl_y - 80), (vl_x + 80, vl_y + 80)], fill=(25, 25, 25, 235), outline=gold, width=4)
    # Grooves
    for r in [65, 52, 40]:
        draw.ellipse([(vl_x - r, vl_y - r), (vl_x + r, vl_y + r)], outline=(80, 75, 60, 200), width=1)
    # Center gold label
    draw.ellipse([(vl_x - 26, vl_y - 26), (vl_x + 26, vl_y + 26)], fill=gold, outline=gold_dark, width=2)
    draw.ellipse([(vl_x - 6, vl_y - 6), (vl_x + 6, vl_y + 6)], fill=(20, 20, 20, 255))
    draw.text((vl_x, vl_y - 38), "63만", font=font_small, fill=gold, anchor="mm")

    # Corner filigree
    for cx, cy in [(60, 60), (WIDTH - 60, 60), (60, HEIGHT - 60), (WIDTH - 60, HEIGHT - 60)]:
        draw_stars(draw, [(cx, cy, 22)], gold_light)

    return img


# ==============================================================================
# Frame 3: "파라다이스 인생 네컷 클래식 (Paradise 4-Cut Classic Photobooth)"
# ==============================================================================
def create_frame_paradise_4cut():
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    emerald_strip = (14, 40, 32, 250)  # #0E2820 deep photobooth emerald
    gold = (212, 175, 55, 255)
    gold_soft = (245, 227, 200, 230)

    # Classic photobooth border padding
    # Top bar: 130px, Bottom bar: 180px, Left/Right: 40px
    draw.rectangle([(0, 0), (WIDTH, 120)], fill=emerald_strip)
    draw.rectangle([(0, HEIGHT - 170), (WIDTH, HEIGHT)], fill=emerald_strip)
    draw.rectangle([(0, 0), (45, HEIGHT)], fill=emerald_strip)
    draw.rectangle([(WIDTH - 45, 0), (WIDTH, HEIGHT)], fill=emerald_strip)

    # Thin gold inner line framing the user's photo cut
    draw.rectangle([(45, 120), (WIDTH - 45, HEIGHT - 170)], outline=gold, width=4)

    # Top header
    draw.text((WIDTH // 2, 50), "PARADISE PHOTOBOOTH", font=font_title, fill=gold, anchor="mm")
    draw.text((WIDTH // 2, 92), "황영웅과 함께 찍는 우리들의 인생 네컷 순간", font=font_subtitle, fill=gold_soft, anchor="mm")

    # Photobooth camera roll punch holes (film strip motif on left and right)
    for y in range(160, HEIGHT - 200, 90):
        # Left holes
        draw.rounded_rectangle([(12, y), (32, y + 45)], radius=6, fill=(240, 240, 240, 60), outline=gold, width=1)
        # Right holes
        draw.rounded_rectangle([(WIDTH - 32, y), (WIDTH - 12, y + 45)], radius=6, fill=(240, 240, 240, 60), outline=gold, width=1)

    # Bottom serial stamp and commemorative date
    draw.text((WIDTH // 2, HEIGHT - 120), "2026 PARADISE PHOTOBOOTH #01", font=font_title, fill=gold, anchor="mm")
    draw.text((WIDTH // 2, HEIGHT - 65), "영원히 변치 않는 감동과 동행 | paradise-hero.com", font=font_subtitle, fill=gold_soft, anchor="mm")

    # Corner seals
    draw_stars(draw, [(25, 25, 14), (WIDTH - 25, 25, 14), (25, HEIGHT - 25, 14), (WIDTH - 25, HEIGHT - 25, 14)], gold)

    return img


# ==============================================================================
# Frame 4: "김쌤의 영웅 라디오 특별 초대석 (Radio Guest Studio Frame)"
# ==============================================================================
def create_frame_radio_studio():
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    studio_wood = (44, 26, 20, 245)     # Warm mahogany retro radio color
    studio_accent = (232, 155, 83, 255) # Warm sunset amber
    neon_red = (220, 38, 38, 255)       # ON AIR neon red
    cream_text = (245, 227, 200, 240)

    # Studio border
    draw.rectangle([(0, 0), (WIDTH, 130)], fill=studio_wood)
    draw.rectangle([(0, HEIGHT - 180), (WIDTH, HEIGHT)], fill=studio_wood)
    draw.rectangle([(0, 0), (40, HEIGHT)], fill=studio_wood)
    draw.rectangle([(WIDTH - 40, 0), (WIDTH, HEIGHT)], fill=studio_wood)

    # Amber line frame
    draw.rectangle([(40, 130), (WIDTH - 40, HEIGHT - 180)], outline=studio_accent, width=4)

    # Top Left: Glowing "ON AIR" box
    draw.rounded_rectangle([(70, 35), (230, 95)], radius=8, fill=neon_red, outline=(255, 255, 255), width=2)
    draw.text((150, 65), "● ON AIR", font=font_subtitle, fill=(255, 255, 255), anchor="mm")

    # Top Center/Right: Title
    draw.text((WIDTH // 2 + 60, 52), "유튜브 @김쌤의영웅라디오", font=font_subtitle, fill=studio_accent, anchor="mm")
    draw.text((WIDTH // 2 + 60, 92), "오늘 하루 특별 명예 DJ 초대석", font=font_title, fill=cream_text, anchor="mm")

    # Bottom Desk Area: Vintage Microphone motif on bottom right
    mic_x, mic_y = WIDTH - 150, HEIGHT - 240
    # Mic grill
    draw.rounded_rectangle([(mic_x - 30, mic_y - 60), (mic_x + 30, mic_y + 10)], radius=15, fill=(180, 180, 185, 240), outline=studio_accent, width=3)
    # Horizontal grill lines
    for gy in range(mic_y - 45, mic_y, 10):
        draw.line([(mic_x - 25, gy), (mic_x + 25, gy)], fill=(80, 80, 80), width=2)
    # Mic stem & round base
    draw.rectangle([(mic_x - 6, mic_y + 10), (mic_x + 6, mic_y + 50)], fill=(90, 90, 95))
    draw.ellipse([(mic_x - 35, mic_y + 40), (mic_x + 35, mic_y + 65)], fill=studio_accent)

    # Bottom Banner Text
    draw.text((WIDTH // 2 - 40, HEIGHT - 130), "어머님, 오늘은 당신이 라디오의 주인공입니다", font=font_title, fill=studio_accent, anchor="mm")
    draw.text((WIDTH // 2 - 40, HEIGHT - 70), "매일 저녁 7시 본방사수 | 유튜브 @김쌤의영웅라디오 & paradise-hero.com", font=font_subtitle, fill=cream_text, anchor="mm")

    return img


def generate_all_frames():
    frames = [
        ("frame_flower_path.png", "thumb_flower_path.png", create_frame_flower_path),
        ("frame_golden_milestone.png", "thumb_golden_milestone.png", create_frame_golden_milestone),
        ("frame_paradise_4cut.png", "thumb_paradise_4cut.png", create_frame_paradise_4cut),
        ("frame_radio_studio.png", "thumb_radio_studio.png", create_frame_radio_studio)
    ]

    for frame_name, thumb_name, creator_func in frames:
        frame_path = os.path.join(OUTPUT_DIR, frame_name)
        thumb_path = os.path.join(OUTPUT_DIR, thumb_name)

        print(f"Generating 1080x1440 master frame: {frame_name}...")
        img = creator_func()
        img.save(frame_path, "PNG", optimize=True)
        size_kb = os.path.getsize(frame_path) / 1024
        print(f"  [OK] Saved {frame_path} ({size_kb:.1f} KB)")

        # Create thumbnail with soft background for thumbnail tray
        print(f"Generating thumbnail: {thumb_name}...")
        thumb_bg = Image.new("RGBA", (WIDTH, HEIGHT), (245, 245, 240, 255))
        thumb_composite = Image.alpha_composite(thumb_bg, img)
        thumb_img = thumb_composite.resize((THUMB_W, THUMB_H), Image.Resampling.LANCZOS)
        thumb_img.save(thumb_path, "PNG")
        thumb_kb = os.path.getsize(thumb_path) / 1024
        print(f"  [OK] Saved {thumb_path} ({thumb_kb:.1f} KB)")

    print(f"\n[SUCCESS] All 4 commemorative frames & thumbnails generated in: {OUTPUT_DIR}")


if __name__ == "__main__":
    generate_all_frames()
