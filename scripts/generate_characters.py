"""
generate_characters.py
Generates high-resolution (1080x1440, RGBA transparent PNG) illustrated virtual trot singer
Baek Woon-ho (백운호) 6-outfit stage character sprites (hero_style_01.png ~ hero_style_06.png)
and selector thumbnails (thumb_hero_style_01.png ~ thumb_hero_style_06.png, 160x160)
for paradise-hero.com Two-Shot Photo Booth & Gift Studio.

Zero real celebrity names or Unicode emojis are used in PIL text to prevent '□' missing-glyph boxes.
"""

import os
import math
import json
import shutil
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1080
HEIGHT = 1440
THUMB_SIZE = 160

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(ASSETS_DIR, "characters")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Map each of the 6 Baek Woon-ho stage outfits to its clean illustrated base source
RAW_PRINCE_INDEX_MAP = [1, 2, 4, 7, 8, 10]

BAEK_STYLE_BANNER_TITLES = [
    "1. 에메랄드 정장",
    "2. 화이트 콘서트 턱시도",
    "3. 클래식 네이비 수트",
    "4. 따뜻한 가을 코트",
    "5. 전통 한복 자락",
    "6. 라디오 DJ 스튜디오룩",
]


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


font_title = get_font(36, bold=True)
font_name = get_font(48, bold=True)
font_small = get_font(21, bold=True)


def hex_to_rgb(hex_code: str):
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))


def draw_sparkle_star(draw, cx, cy, r, color, points=4):
    pts = []
    total_pts = points * 2
    for i in range(total_pts):
        angle = i * (math.pi / points) - (math.pi / 2)
        radius = r if (i % 2 == 0) else max(2, int(r * 0.22))
        px = cx + radius * math.cos(angle)
        py = cy + radius * math.sin(angle)
        pts.append((px, py))
    draw.polygon(pts, fill=color)
    core_r = max(1, r // 4)
    draw.ellipse([(cx - core_r, cy - core_r), (cx + core_r, cy + core_r)], fill=(255, 255, 255, 240))


def draw_floating_petal(draw, cx, cy, size, angle_deg, color):
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    pts = [
        (0, -size),
        (size * 0.55, -size * 0.4),
        (size * 0.65, size * 0.4),
        (0, size * 0.9),
        (-size * 0.65, size * 0.4),
        (-size * 0.55, -size * 0.4),
    ]
    rotated = []
    for x, y in pts:
        rx = cx + (x * cos_a - y * sin_a)
        ry = cy + (x * sin_a + y * cos_a)
        rotated.append((rx, ry))
    draw.polygon(rotated, fill=color)


def extract_foreground_rgba(raw_img: Image.Image) -> Image.Image:
    """
    Flood-fills / keys out the outer pure white background (#FFFFFF) from the character
    illustration while preserving white suit details inside the character silhouette.
    """
    rgba = raw_img.convert("RGBA")
    w, h = rgba.size
    pixels = rgba.load()

    visited = bytearray(w * h)
    bg_mask = bytearray(w * h)
    queue = []

    def is_bg_white(r, g, b):
        return r >= 240 and g >= 240 and b >= 240 and abs(r - g) <= 10 and abs(g - b) <= 10

    for x in range(w):
        for y in (0, h - 1):
            idx = y * w + x
            r, g, b, _ = pixels[x, y]
            if is_bg_white(r, g, b):
                visited[idx] = 1
                bg_mask[idx] = 1
                queue.append((x, y))

    for y in range(h):
        for x in (0, w - 1):
            idx = y * w + x
            if not visited[idx]:
                r, g, b, _ = pixels[x, y]
                if is_bg_white(r, g, b):
                    visited[idx] = 1
                    bg_mask[idx] = 1
                    queue.append((x, y))

    head = 0
    while head < len(queue):
        cx, cy = queue[head]
        head += 1
        for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
            if 0 <= nx < w and 0 <= ny < h:
                nidx = ny * w + nx
                if not visited[nidx]:
                    visited[nidx] = 1
                    r, g, b, _ = pixels[nx, ny]
                    if is_bg_white(r, g, b):
                        bg_mask[nidx] = 1
                        queue.append((nx, ny))

    for y in range(h):
        row_offset = y * w
        for x in range(w):
            idx = row_offset + x
            if bg_mask[idx]:
                pixels[x, y] = (255, 255, 255, 0)
            else:
                adj_bg = 0
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and bg_mask[ny * w + nx]:
                        adj_bg += 1
                if adj_bg > 0:
                    r, g, b, _ = pixels[x, y]
                    pixels[x, y] = (r, g, b, max(80, 255 - adj_bg * 45))

    return rgba


_CUTOUT_CACHE = {}


def get_prince_cutout(prince_idx: int) -> Image.Image:
    if prince_idx in _CUTOUT_CACHE:
        return _CUTOUT_CACHE[prince_idx].copy()
    raw_path = os.path.join(OUTPUT_DIR, f"raw_prince_{prince_idx}.png")
    raw_img = Image.open(raw_path).convert("RGBA")
    cutout = extract_foreground_rgba(raw_img)
    _CUTOUT_CACHE[prince_idx] = cutout
    return cutout.copy()


def generate_character_sprite(char_info: dict, index_zero_based: int = 0) -> Image.Image:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    theme_rgb = hex_to_rgb(char_info["theme_color"])
    accent_rgb = hex_to_rgb(char_info["accent_color"])
    gold_rgb = (212, 175, 55, 255)
    soft_gold = (245, 225, 140, 235)

    HEAD_X = 740
    HEAD_Y = 440
    BODY_CX = 740

    for r in range(380, 80, -25):
        alpha = int(28 * (1.0 - (r / 380.0)))
        draw.ellipse(
            [(HEAD_X - r, HEAD_Y + 120 - r), (HEAD_X + r, HEAD_Y + 120 + r)],
            fill=(theme_rgb[0], theme_rgb[1], theme_rgb[2], alpha),
        )

    prince_idx = RAW_PRINCE_INDEX_MAP[index_zero_based % len(RAW_PRINCE_INDEX_MAP)]
    cutout = get_prince_cutout(prince_idx)

    target_w = 720
    target_h = int(cutout.height * (target_w / cutout.width))
    if target_h < 1020:
        target_h = 1020
        target_w = int(cutout.width * (target_h / cutout.height))

    cutout_resized = cutout.resize((target_w, target_h), Image.Resampling.LANCZOS)
    paste_x = WIDTH - target_w + 30
    paste_y = HEIGHT - target_h - 110
    img.alpha_composite(cutout_resized, dest=(max(340, paste_x), max(120, paste_y)))

    sparkle_coords = [
        (520, 210, 16),
        (620, 150, 22),
        (910, 170, 24),
        (1010, 280, 18),
        (480, 480, 18),
        (1015, 560, 22),
        (510, 820, 16),
        (1020, 880, 20),
    ]
    for sx, sy, sr in sparkle_coords:
        draw_sparkle_star(draw, sx, sy, sr, soft_gold, 4 if sr < 22 else 8)

    petal_coords = [
        (500, 310, 16, 25),
        (950, 350, 18, -40),
        (1010, 710, 20, 15),
        (960, 990, 18, 45),
    ]
    petal_tint = (accent_rgb[0], accent_rgb[1], accent_rgb[2], 210)
    for px, py, ps, pa in petal_coords:
        draw_floating_petal(draw, px, py, ps, pa, petal_tint)

    banner_y = HEIGHT - 205
    banner_box = [(BODY_CX - 275, banner_y), (BODY_CX + 275, banner_y + 128)]

    draw.rounded_rectangle(banner_box, radius=18, fill=(14, 40, 32, 238), outline=gold_rgb, width=4)
    draw.rounded_rectangle(
        [(banner_box[0][0] + 6, banner_box[0][1] + 6), (banner_box[1][0] - 6, banner_box[1][1] - 6)],
        radius=14,
        outline=(soft_gold[0], soft_gold[1], soft_gold[2], 180),
        width=2,
    )

    clean_title = BAEK_STYLE_BANNER_TITLES[index_zero_based % len(BAEK_STYLE_BANNER_TITLES)]
    name_text = "가상 트로트 가수 백운호"
    sub_text = "김쌤의영웅라디오 가족 사랑방 기념사진"

    draw.text((BODY_CX, banner_y + 26), clean_title, font=font_title, fill=soft_gold, anchor="mm")
    draw.text((BODY_CX, banner_y + 68), name_text, font=font_name, fill=(255, 255, 255, 255), anchor="mm")
    draw.text((BODY_CX, banner_y + 105), sub_text, font=font_small, fill=(215, 235, 225, 235), anchor="mm")

    return img


def generate_character_thumbnail(char_info: dict, index_zero_based: int = 0) -> Image.Image:
    thumb = Image.new("RGBA", (THUMB_SIZE, THUMB_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(thumb)

    theme_rgb = hex_to_rgb(char_info["theme_color"])
    gold_rgb = (212, 175, 55, 255)

    margin = 4
    draw.ellipse(
        [(margin, margin), (THUMB_SIZE - margin, THUMB_SIZE - margin)],
        fill=(250, 250, 248, 255),
        outline=gold_rgb,
        width=4,
    )
    draw.ellipse(
        [(margin + 4, margin + 4), (THUMB_SIZE - margin - 4, THUMB_SIZE - margin - 4)],
        outline=(theme_rgb[0], theme_rgb[1], theme_rgb[2], 190),
        width=2,
    )

    prince_idx = RAW_PRINCE_INDEX_MAP[index_zero_based % len(RAW_PRINCE_INDEX_MAP)]
    cutout = get_prince_cutout(prince_idx)
    cw, ch = cutout.size
    crop_size = int(min(cw, ch) * 0.62)
    cx = cw // 2
    cy = int(ch * 0.30)
    crop_box = (
        max(0, cx - crop_size // 2),
        max(0, cy - crop_size // 2),
        min(cw, cx + crop_size // 2),
        min(ch, cy + crop_size // 2),
    )
    head_crop = cutout.crop(crop_box)

    avatar_size = THUMB_SIZE - 20
    head_resized = head_crop.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)

    mask = Image.new("L", (avatar_size, avatar_size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse([(0, 0), (avatar_size, avatar_size)], fill=255)

    thumb.paste(head_resized, (10, 10), mask)
    draw.ellipse([(margin, margin), (THUMB_SIZE - margin, THUMB_SIZE - margin)], outline=gold_rgb, width=3)

    return thumb


def generate_all_characters():
    json_path = os.path.join(BASE_DIR, "data", "characters.json")
    with open(json_path, "r", encoding="utf-8") as f:
        characters = json.load(f)

    print("=================================================================")
    print("Generating Virtual Trot Singer Baek Woon-ho 6-Outfit Assets (RGBA)")
    print(f"Output Directory: {OUTPUT_DIR}")
    print("=================================================================\n")

    for idx, char in enumerate(characters):
        char_id = char["id"]  # hero_style_01 ~ hero_style_06
        sprite_filename = f"{char_id}.png"
        thumb_filename = f"thumb_{char_id}.png"
        sprite_path = os.path.join(OUTPUT_DIR, sprite_filename)
        thumb_path = os.path.join(OUTPUT_DIR, thumb_filename)

        sprite_img = generate_character_sprite(char, idx)
        sprite_img.save(sprite_path, "PNG", optimize=True)

        thumb_img = generate_character_thumbnail(char, idx)
        thumb_img.save(thumb_path, "PNG", optimize=True)

        if idx < 4:
            num_idx = idx + 1
            shutil.copyfile(sprite_path, os.path.join(OUTPUT_DIR, f"sprite_{num_idx}.png"))
            shutil.copyfile(thumb_path, os.path.join(OUTPUT_DIR, f"thumb_{num_idx}.png"))

        print(
            f"  [{idx+1}/{len(characters)}] Saved {sprite_filename} ({os.path.getsize(sprite_path)/1024:.1f} KB) "
            f"& {thumb_filename} ({os.path.getsize(thumb_path)/1024:.1f} KB)"
        )

    print("\n[SUCCESS] All Baek Woon-ho 6-outfit character sprites & thumbnails generated!")


if __name__ == "__main__":
    generate_all_characters()
