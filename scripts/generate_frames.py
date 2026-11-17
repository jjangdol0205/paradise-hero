"""
generate_frames.py
Generates 4 high-resolution (1080x1440, 3:4 portrait) commemorative transparent PNG frames
and corresponding thumbnails (160x213) for paradise-hero.com Two-Shot Photo Booth
with Original Virtual Trot Singer Baek Woon-ho (백운호).

Frames:
1. frame_flower_path.png: "어머니의 봄날 다정한 꽃길 액자"
2. frame_golden_milestone.png: "백운호 오리지널 명곡 골드 기념 액자"
3. frame_paradise_4cut.png: "김쌤의영웅라디오 가족 사랑방 네컷 액자"
4. frame_radio_studio.png: "김쌤의영웅라디오 특별 초대석 스튜디오 액자"
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


def get_font(size: int, bold: bool = False):
    font_paths = [
        "C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/batang.ttc",
        "C:/Windows/Fonts/gulim.ttc",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


font_title = get_font(42, bold=True)
font_subtitle = get_font(27, bold=True)
font_badge = get_font(23, bold=True)
font_small = get_font(20, bold=False)


def draw_flower_vine(draw, x, y, size, color):
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        px = x + int(math.cos(rad) * size)
        py = y + int(math.sin(rad) * size)
        draw.ellipse([(px - size // 2, py - size // 2), (px + size // 2, py + size // 2)], fill=color)
    draw.ellipse([(x - size // 3, y - size // 3), (x + size // 3, y + size // 3)], fill=(212, 175, 55, 230))


def draw_stars(draw, points, color):
    for (cx, cy, r) in points:
        draw.polygon(
            [
                (cx, cy - r),
                (cx + r // 4, cy - r // 4),
                (cx + r, cy),
                (cx + r // 4, cy + r // 4),
                (cx, cy + r),
                (cx - r // 4, cy + r // 4),
                (cx - r, cy),
                (cx - r // 4, cy - r // 4),
            ],
            fill=color,
        )


def create_frame_flower_path():
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    gold = (212, 175, 55, 255)
    gold_soft = (235, 205, 115, 200)

    draw.rectangle([(0, 0), (WIDTH, 90)], fill=(27, 77, 62, 230))
    draw.rectangle([(0, HEIGHT - 130), (WIDTH, HEIGHT)], fill=(27, 77, 62, 230))

    draw.rectangle([(30, 110), (WIDTH - 30, HEIGHT - 150)], outline=gold, width=4)
    draw.rectangle([(42, 122), (WIDTH - 42, HEIGHT - 162)], outline=(27, 77, 62, 180), width=2)
    draw.rectangle([(50, 130), (WIDTH - 50, HEIGHT - 170)], outline=gold_soft, width=1)

    corners = [(70, 150), (WIDTH - 70, 150), (70, HEIGHT - 190), (WIDTH - 70, HEIGHT - 190)]
    for cx, cy in corners:
        draw_flower_vine(draw, cx, cy, 14, (39, 174, 96, 210))
        draw_stars(draw, [(cx, cy, 18)], gold)

    sparkles = [
        (46, 350, 10),
        (46, 600, 12),
        (46, 850, 10),
        (46, 1100, 12),
        (WIDTH - 46, 350, 10),
        (WIDTH - 46, 600, 12),
        (WIDTH - 46, 850, 10),
        (WIDTH - 46, 1100, 12),
    ]
    draw_stars(draw, sparkles, gold)

    draw.text((WIDTH // 2, 45), "가상 트로트 가수 백운호와 함께 걷는 다정한 꽃길", font=font_subtitle, fill=(255, 255, 255, 255), anchor="mm")
    draw.text((WIDTH // 2, HEIGHT - 85), "어머니의 봄날처럼 늘 건강하고 행복하세요", font=font_title, fill=gold, anchor="mm")
    draw.text((WIDTH // 2, HEIGHT - 35), "김쌤의영웅라디오 가족 사랑방 포토부스 | paradise-hero.com", font=font_small, fill=(240, 240, 240, 220), anchor="mm")

    badge_x, badge_y = WIDTH - 160, HEIGHT - 230
    draw.ellipse([(badge_x - 58, badge_y - 58), (badge_x + 58, badge_y + 58)], fill=(27, 77, 62, 220), outline=gold, width=3)
    draw.text((badge_x, badge_y - 12), "봄날꽃길", font=font_badge, fill=gold, anchor="mm")
    draw.text((badge_x, badge_y + 18), "백운호", font=font_small, fill=(255, 255, 255, 230), anchor="mm")

    return img


def create_frame_golden_milestone():
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    gold = (212, 175, 55, 255)
    gold_dark = (166, 124, 0, 255)
    gold_light = (255, 223, 100, 255)
    royal_black = (20, 18, 15, 240)

    draw.rectangle([(15, 15), (WIDTH - 15, HEIGHT - 15)], outline=gold, width=8)
    draw.rectangle([(28, 28), (WIDTH - 28, HEIGHT - 28)], outline=gold_dark, width=2)
    draw.rectangle([(40, 40), (WIDTH - 40, HEIGHT - 40)], outline=gold_light, width=3)

    draw.rectangle([(70, 30), (WIDTH - 70, 150)], fill=royal_black, outline=gold, width=4)
    draw.text((WIDTH // 2, 70), "백운호 오리지널 타이틀곡 [어머니의 봄날] 기념", font=font_subtitle, fill=gold_light, anchor="mm")
    draw.text((WIDTH // 2, 115), "가족을 위해 바치신 세월, 당신이 우리 인생의 진짜 영웅입니다", font=font_small, fill=(255, 255, 255, 220), anchor="mm")

    draw.rectangle([(70, HEIGHT - 170), (WIDTH - 70, HEIGHT - 35)], fill=royal_black, outline=gold, width=4)
    draw.text((WIDTH // 2, HEIGHT - 125), "인생 영웅 골든 레코드 헌정 액자", font=font_title, fill=gold, anchor="mm")
    draw.text((WIDTH // 2, HEIGHT - 70), "BAEK WOON-HO ORIGINAL TROT | paradise-hero.com", font=font_badge, fill=gold_light, anchor="mm")

    vl_x, vl_y = 170, HEIGHT - 240
    draw.ellipse([(vl_x - 80, vl_y - 80), (vl_x + 80, vl_y + 80)], fill=(25, 25, 25, 235), outline=gold, width=4)
    for r in [65, 52, 40]:
        draw.ellipse([(vl_x - r, vl_y - r), (vl_x + r, vl_y + r)], outline=(80, 75, 60, 200), width=1)
    draw.ellipse([(vl_x - 26, vl_y - 26), (vl_x + 26, vl_y + 26)], fill=gold, outline=gold_dark, width=2)
    draw.ellipse([(vl_x - 6, vl_y - 6), (vl_x + 6, vl_y + 6)], fill=(20, 20, 20, 255))
    draw.text((vl_x, vl_y - 38), "백운호", font=font_small, fill=gold, anchor="mm")

    for cx, cy in [(60, 60), (WIDTH - 60, 60), (60, HEIGHT - 60), (WIDTH - 60, HEIGHT - 60)]:
        draw_stars(draw, [(cx, cy, 22)], gold_light)

    return img


def create_frame_paradise_4cut():
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    emerald_strip = (14, 40, 32, 250)
    gold = (212, 175, 55, 255)
    gold_soft = (245, 227, 200, 230)

    draw.rectangle([(0, 0), (WIDTH, 120)], fill=emerald_strip)
    draw.rectangle([(0, HEIGHT - 170), (WIDTH, HEIGHT)], fill=emerald_strip)
    draw.rectangle([(0, 0), (45, HEIGHT)], fill=emerald_strip)
    draw.rectangle([(WIDTH - 45, 0), (WIDTH, HEIGHT)], fill=emerald_strip)

    draw.rectangle([(45, 120), (WIDTH - 45, HEIGHT - 170)], outline=gold, width=4)

    draw.text((WIDTH // 2, 50), "HERO RADIO PHOTOBOOTH", font=font_title, fill=gold, anchor="mm")
    draw.text((WIDTH // 2, 92), "백운호와 함께 남기는 따뜻한 가족 사랑방 기념 네컷", font=font_subtitle, fill=gold_soft, anchor="mm")

    for y in range(160, HEIGHT - 200, 90):
        draw.rounded_rectangle([(12, y), (32, y + 45)], radius=6, fill=(240, 240, 240, 60), outline=gold, width=1)
        draw.rounded_rectangle([(WIDTH - 32, y), (WIDTH - 12, y + 45)], radius=6, fill=(240, 240, 240, 60), outline=gold, width=1)

    draw.text((WIDTH // 2, HEIGHT - 120), "내 인생의 금빛 노을 기념 사진", font=font_title, fill=gold, anchor="mm")
    draw.text((WIDTH // 2, HEIGHT - 65), "유튜브 @김쌤의영웅라디오 가족 사랑방 | paradise-hero.com", font=font_subtitle, fill=gold_soft, anchor="mm")

    draw_stars(draw, [(25, 25, 14), (WIDTH - 25, 25, 14), (25, HEIGHT - 25, 14), (WIDTH - 25, HEIGHT - 25, 14)], gold)

    return img


def create_frame_radio_studio():
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    studio_wood = (44, 26, 20, 245)
    studio_accent = (232, 155, 83, 255)
    neon_red = (220, 38, 38, 255)
    cream_text = (245, 227, 200, 240)

    draw.rectangle([(0, 0), (WIDTH, 130)], fill=studio_wood)
    draw.rectangle([(0, HEIGHT - 180), (WIDTH, HEIGHT)], fill=studio_wood)
    draw.rectangle([(0, 0), (40, HEIGHT)], fill=studio_wood)
    draw.rectangle([(WIDTH - 40, 0), (WIDTH, HEIGHT)], fill=studio_wood)

    draw.rectangle([(40, 130), (WIDTH - 40, HEIGHT - 180)], outline=studio_accent, width=4)

    draw.rounded_rectangle([(70, 35), (230, 95)], radius=8, fill=neon_red, outline=(255, 255, 255), width=2)
    draw.text((150, 65), "ON AIR", font=font_subtitle, fill=(255, 255, 255), anchor="mm")

    draw.text((WIDTH // 2 + 60, 52), "유튜브 @김쌤의영웅라디오", font=font_subtitle, fill=studio_accent, anchor="mm")
    draw.text((WIDTH // 2 + 60, 92), "오늘 하루 특별 명예 DJ 초대석", font=font_title, fill=cream_text, anchor="mm")

    mic_x, mic_y = WIDTH - 150, HEIGHT - 240
    draw.rounded_rectangle([(mic_x - 30, mic_y - 60), (mic_x + 30, mic_y + 10)], radius=15, fill=(180, 180, 185, 240), outline=studio_accent, width=3)
    for gy in range(mic_y - 45, mic_y, 10):
        draw.line([(mic_x - 25, gy), (mic_x + 25, gy)], fill=(80, 80, 80), width=2)
    draw.rectangle([(mic_x - 6, mic_y + 10), (mic_x + 6, mic_y + 50)], fill=(90, 90, 95))
    draw.ellipse([(mic_x - 35, mic_y + 40), (mic_x + 35, mic_y + 65)], fill=studio_accent)

    draw.text((WIDTH // 2 - 40, HEIGHT - 130), "어머님·아버님, 당신이 라디오의 주인공입니다", font=font_title, fill=studio_accent, anchor="mm")
    draw.text((WIDTH // 2 - 40, HEIGHT - 70), "화·금 저녁 6시 정규방송 | @김쌤의영웅라디오 & paradise-hero.com", font=font_subtitle, fill=cream_text, anchor="mm")

    return img


def generate_all_frames():
    frames = [
        ("frame_flower_path.png", "thumb_flower_path.png", create_frame_flower_path),
        ("frame_golden_milestone.png", "thumb_golden_milestone.png", create_frame_golden_milestone),
        ("frame_paradise_4cut.png", "thumb_paradise_4cut.png", create_frame_paradise_4cut),
        ("frame_radio_studio.png", "thumb_radio_studio.png", create_frame_radio_studio),
    ]

    for frame_name, thumb_name, creator_func in frames:
        frame_path = os.path.join(OUTPUT_DIR, frame_name)
        thumb_path = os.path.join(OUTPUT_DIR, thumb_name)

        img = creator_func()
        img.save(frame_path, "PNG", optimize=True)

        thumb_bg = Image.new("RGBA", (WIDTH, HEIGHT), (245, 245, 240, 255))
        thumb_composite = Image.alpha_composite(thumb_bg, img)
        thumb_img = thumb_composite.resize((THUMB_W, THUMB_H), Image.Resampling.LANCZOS)
        thumb_img.save(thumb_path, "PNG")
        print(f"  [OK] Saved {frame_name} & {thumb_name}")

    print(f"\n[SUCCESS] All 4 Baek Woon-ho commemorative frames & thumbnails generated in: {OUTPUT_DIR}")


if __name__ == "__main__":
    generate_all_frames()
