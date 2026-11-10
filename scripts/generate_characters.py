"""
generate_characters.py
Generates high-resolution (1080x1440, RGBA transparent PNG) Korean Romance Webtoon (순정만화)
Trot Crown Prince character sprites and selector thumbnails (160x160) for paradise-hero.com
Two-Shot Photo Booth & Daily Shorts Pipeline.

Replaces old geometric polygons ("Roblox figures") with authentic semi-realistic Korean romance
webtoon digital illustrations (raw_prince_1.png ~ raw_prince_4.png) and removes 100% of Unicode
emojis from Pillow text rendering to prevent '□' missing-glyph boxes in malgun.ttf.
"""

import os
import math
import json
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

WIDTH = 1080
HEIGHT = 1440
THUMB_SIZE = 160

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(ASSETS_DIR, "characters")
os.makedirs(OUTPUT_DIR, exist_ok=True)

ARTIFACT_DIR = r"C:\Users\jjang\.gemini\antigravity\brain\1921e31e-ab59-4720-9419-93cac770374d"
RAW_SOURCES = {
    1: os.path.join(ARTIFACT_DIR, "raw_char_1_hwang_young_woong_1794270927123.jpg"),
    2: os.path.join(ARTIFACT_DIR, "hwang_look_2_white_tuxedo_1794271917754.jpg"),
    3: os.path.join(ARTIFACT_DIR, "hwang_look_3_pink_cardigan_heart_1794271936006.jpg"),
    4: os.path.join(ARTIFACT_DIR, "hwang_look_4_all_black_suit_1794271955646.jpg"),
    5: os.path.join(ARTIFACT_DIR, "hwang_look_5_royal_uniform_1794271970920.jpg"),
    6: os.path.join(ARTIFACT_DIR, "hwang_look_6_purple_velvet_concert_1794271918941.jpg"),
    7: os.path.join(ARTIFACT_DIR, "hwang_look_7_autumn_trenchcoat_1794271937794.jpg"),
    8: os.path.join(ARTIFACT_DIR, "hwang_look_8_golden_hanbok_1794271954389.jpg"),
    9: os.path.join(ARTIFACT_DIR, "hwang_look_9_burgundy_rose_1794271971955.jpg"),
    10: os.path.join(ARTIFACT_DIR, "hwang_look_10_radio_dj_glasses_1794271991280.jpg"),
}
HERO_SOURCE = os.path.join(ARTIFACT_DIR, "hero_main_hwang_young_woong_1794271012943.jpg")

HWANG_LOOK_TITLES = [
    "감성 황태자 · 에메랄드 수트",
    "순백의 프린스 · 화이트 수트",
    "다정한 미소 · 핑크 손하트",
    "중저음 카리스마 · 올블랙",
    "파라다이스 황태자 · 황실 제복",
    "단독 콘서트 · 퍼플 벨벳",
    "가을 남자의 순정 · 트렌치코트",
    "다정한 효도왕자 · 금빛 한복",
    "당신 편 세레나데 · 붉은 장미",
    "심야 라디오 DJ · 금테 안경",
]


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


font_title = get_font(38, bold=True)
font_name = get_font(50, bold=True)
font_small = get_font(22, bold=True)


def hex_to_rgb(hex_code: str):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))


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
        (-size * 0.55, -size * 0.4)
    ]
    rotated = []
    for x, y in pts:
        rx = cx + (x * cos_a - y * sin_a)
        ry = cy + (x * sin_a + y * cos_a)
        rotated.append((rx, ry))
    draw.polygon(rotated, fill=color)


def prepare_raw_webtoon_sources():
    """Copies AI-generated webtoon illustrations into assets/ and assets/characters/."""
    hero_dst = os.path.join(ASSETS_DIR, "hero_main.png")
    if os.path.exists(HERO_SOURCE):
        im = Image.open(HERO_SOURCE).convert("RGB")
        im.save(hero_dst, "PNG", optimize=True)
        print(f"  [OK] Saved Hero Main Visual: {hero_dst} ({os.path.getsize(hero_dst)/1024:.1f} KB)")

    for idx, src_path in RAW_SOURCES.items():
        raw_dst = os.path.join(OUTPUT_DIR, f"raw_prince_{idx}.png")
        if os.path.exists(src_path):
            im = Image.open(src_path).convert("RGBA")
            im.save(raw_dst, "PNG", optimize=True)


def extract_foreground_rgba(raw_img: Image.Image) -> Image.Image:
    """
    Flood-fills / keys out the outer pure white background (#FFFFFF) from the webtoon
    character illustration while preserving white suit details inside the character silhouette.
    """
    rgba = raw_img.convert("RGBA")
    w, h = rgba.size
    pixels = rgba.load()

    # BFS flood-fill from borders for near-white background pixels
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

    # Apply smooth edge feathering on the boundary of bg_mask
    for y in range(h):
        row_offset = y * w
        for x in range(w):
            idx = row_offset + x
            if bg_mask[idx]:
                pixels[x, y] = (255, 255, 255, 0)
            else:
                # Check if adjacent to background for soft anti-aliased edge
                adj_bg = 0
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and bg_mask[ny * w + nx]:
                        adj_bg += 1
                if adj_bg > 0:
                    r, g, b, a = pixels[x, y]
                    pixels[x, y] = (r, g, b, max(80, 255 - adj_bg * 45))

    return rgba


# Cache extracted RGBA cutout images for the 4 raw princes
_CUTOUT_CACHE = {}


def get_prince_cutout(prince_idx: int) -> Image.Image:
    if prince_idx in _CUTOUT_CACHE:
        return _CUTOUT_CACHE[prince_idx].copy()
    raw_path = os.path.join(OUTPUT_DIR, f"raw_prince_{prince_idx}.png")
    if not os.path.exists(raw_path) and prince_idx in RAW_SOURCES and os.path.exists(RAW_SOURCES[prince_idx]):
        raw_img = Image.open(RAW_SOURCES[prince_idx]).convert("RGBA")
    else:
        raw_img = Image.open(raw_path).convert("RGBA")
    cutout = extract_foreground_rgba(raw_img)
    _CUTOUT_CACHE[prince_idx] = cutout
    return cutout.copy()


def generate_character_sprite(char_info: dict, index_zero_based: int = 0) -> Image.Image:
    """
    Renders a 1080x1440 RGBA Two-Shot partner sprite using our Korean romance webtoon
    illustrations positioned on the right half so the senior fan's photo appears clearly
    on the left half. Zero emojis are used in PIL text to guarantee zero '□' boxes.
    """
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    theme_rgb = hex_to_rgb(char_info["theme_color"])
    accent_rgb = hex_to_rgb(char_info["accent_color"])
    gold_rgb = (212, 175, 55, 255)
    soft_gold = (245, 225, 140, 235)

    HEAD_X = 740
    HEAD_Y = 440
    BODY_CX = 740

    # 1. Soft Romantic Aura Glow on Right Half Only (keeping left side transparent for user's face)
    for r in range(380, 80, -25):
        alpha = int(28 * (1.0 - (r / 380.0)))
        draw.ellipse(
            [(HEAD_X - r, HEAD_Y + 120 - r), (HEAD_X + r, HEAD_Y + 120 + r)],
            fill=(theme_rgb[0], theme_rgb[1], theme_rgb[2], alpha),
        )

    # 2. Composite Webtoon Prince Cutout on Right Side (Two-Shot Partner Position — 1:1 Singer Likeness)
    prince_idx = index_zero_based + 1
    cutout = get_prince_cutout(prince_idx)

    target_w = 720
    target_h = int(cutout.height * (target_w / cutout.width))
    if target_h < 1020:
        target_h = 1020
        target_w = int(cutout.width * (target_h / cutout.height))

    cutout_resized = cutout.resize((target_w, target_h), Image.Resampling.LANCZOS)
    paste_x = WIDTH - target_w + 30  # Positioned cleanly on right half (~x=390..1080)
    paste_y = HEIGHT - target_h - 110
    img.alpha_composite(cutout_resized, dest=(max(340, paste_x), max(120, paste_y)))

    # 3. Delicate Shoujo Sparkles & Floating Petals around the Prince
    sparkle_coords = [
        (520, 210, 16), (620, 150, 22), (910, 170, 24), (1010, 280, 18),
        (480, 480, 18), (1015, 560, 22), (510, 820, 16), (1020, 880, 20),
    ]
    for sx, sy, sr in sparkle_coords:
        draw_sparkle_star(draw, sx, sy, sr, soft_gold, 4 if sr < 22 else 8)

    petal_coords = [
        (500, 310, 16, 25), (950, 350, 18, -40),
        (1010, 710, 20, 15), (960, 990, 18, 45),
    ]
    petal_tint = (accent_rgb[0], accent_rgb[1], accent_rgb[2], 210)
    for px, py, ps, pa in petal_coords:
        draw_floating_petal(draw, px, py, ps, pa, petal_tint)

    # 4. Emoji-Free Korean Nameplate Banner at Bottom Right (ZERO '□' glyph boxes!)
    banner_y = HEIGHT - 205
    banner_box = [(BODY_CX - 270, banner_y), (BODY_CX + 270, banner_y + 126)]

    draw.rounded_rectangle(banner_box, radius=18, fill=(14, 40, 32, 238), outline=gold_rgb, width=4)
    draw.rounded_rectangle(
        [(banner_box[0][0] + 6, banner_box[0][1] + 6), (banner_box[1][0] - 6, banner_box[1][1] - 6)],
        radius=14,
        outline=(soft_gold[0], soft_gold[1], soft_gold[2], 180),
        width=2,
    )

    # Strictly pure Korean text (no Unicode emojis that break malgun.ttf)
    clean_title = HWANG_LOOK_TITLES[index_zero_based % len(HWANG_LOOK_TITLES)]
    name_text = "황영웅"
    sub_text = "언제나 당신 편 파라다이스 기념사진"

    draw.text((BODY_CX, banner_y + 26), clean_title, font=font_title, fill=soft_gold, anchor="mm")
    draw.text((BODY_CX, banner_y + 68), name_text, font=font_name, fill=(255, 255, 255, 255), anchor="mm")
    draw.text((BODY_CX, banner_y + 104), sub_text, font=font_small, fill=(215, 235, 225, 235), anchor="mm")

    return img


def generate_character_thumbnail( char_info: dict, index_zero_based: int = 0) -> Image.Image:
    """
    Produces a 160x160 RGBA circular portrait thumbnail directly from the high-res
    webtoon prince illustration face & upper bust.
    """
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

    prince_idx = index_zero_based + 1
    cutout = get_prince_cutout(prince_idx)
    cw, ch = cutout.size
    # Crop upper face & bust region centered on the singer's real-life likeness face
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
    prepare_raw_webtoon_sources()

    json_path = os.path.join(BASE_DIR, "data", "characters.json")
    with open(json_path, "r", encoding="utf-8") as f:
        characters = json.load(f)

    print("=================================================================")
    print("Generating Korean Romance Webtoon Prince Character Assets (RGBA)")
    print(f"Output Directory: {OUTPUT_DIR}")
    print("=================================================================\n")

    for idx, char in enumerate(characters):
        char_id = char["id"]
        sprite_filename = f"sprite_{char_id}.png"
        thumb_filename = f"thumb_{char_id}.png"
        sprite_path = os.path.join(OUTPUT_DIR, sprite_filename)
        thumb_path = os.path.join(OUTPUT_DIR, thumb_filename)

        sprite_img = generate_character_sprite(char, idx)
        sprite_img.save(sprite_path, "PNG", optimize=True)

        thumb_img = generate_character_thumbnail(char, idx)
        thumb_img.save(thumb_path, "PNG", optimize=True)

        # Also save numbered aliases sprite_1.png ~ sprite_4.png & thumb_1.png ~ thumb_4.png
        if idx < 4:
            num_idx = idx + 1
            shutil.copyfile(sprite_path, os.path.join(OUTPUT_DIR, f"sprite_{num_idx}.png"))
            shutil.copyfile(thumb_path, os.path.join(OUTPUT_DIR, f"thumb_{num_idx}.png"))

        print(f"  [{idx+1}/10] Saved {sprite_filename} ({os.path.getsize(sprite_path)/1024:.1f} KB) & {thumb_filename} ({os.path.getsize(thumb_path)/1024:.1f} KB)")

    print("\n[SUCCESS] All Korean Romance Webtoon character sprites & thumbnails generated with 0 emoji boxes!")


if __name__ == "__main__":
    generate_all_characters()
