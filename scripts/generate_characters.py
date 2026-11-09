"""
generate_characters.py
Generates 10 high-resolution (1080x1440, RGBA transparent PNG) Anime Prince Trot Singer
character sprites and 10 selector thumbnails (160x160) for paradise-hero.com
Two-Shot Photo Booth & Daily Shorts Pipeline.

Character Roster (10 Shoujo-Manga Princes):
1. hwang_young_woong (황영웅) - 감성 황태자
2. lim_young_woong (임영웅) - 별빛 황제 왕자
3. lee_chan_won (이찬원) - 찬또 브레인 왕자
4. young_tak (영탁) - 청량 에너지 왕자
5. jeong_dong_won (정동원) - 음악 신동 소년왕자
6. kim_ho_joong (김호중) - 트바로티 고결 왕자
7. jang_min_ho (장민호) - 로맨틱 신사 왕자
8. park_seo_jin (박서진) - 열정의 장구 왕자
9. son_tae_jin (손태진) - 크로스오버 클래식 왕자
10. ahn_sung_hoon_jin_hae_seong (안성훈 / 진해성) - 정통 감성 마스터 왕자

Aesthetic Mandate:
- Nostalgic 80s/90s shoujo-manga prince aesthetic:
  * Ornate royal military/prince regalia with gold bullion epaulettes and aiguillettes
  * Sparkling starry eyes with layered celestial reflections and delicate winged lashes
  * Voluminous flowing anime hair with dimensional highlights and shadow strands
  * Shimmering aura, floating rose petals, sparkle stars, and signature props
- Avoid portrait rights infringement via 100% original transformative manga illustration.
"""

import os
import math
import json
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1080
HEIGHT = 1440
THUMB_SIZE = 160

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "assets", "characters")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# Font Loader
# -----------------------------------------------------------------------------
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

font_title = get_font(42, bold=True)
font_name = get_font(52, bold=True)
font_catchphrase = get_font(26, bold=False)
font_badge = get_font(24, bold=True)
font_small = get_font(20, bold=False)


# -----------------------------------------------------------------------------
# Color Utilities
# -----------------------------------------------------------------------------
def hex_to_rgb(hex_code: str):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def hex_to_rgba(hex_code: str, alpha: int = 255):
    rgb = hex_to_rgb(hex_code)
    return (rgb[0], rgb[1], rgb[2], alpha)

def lighten(color, factor=0.3):
    return tuple(min(255, int(c + (255 - c) * factor)) for c in color[:3])

def darken(color, factor=0.3):
    return tuple(max(0, int(c * (1 - factor))) for c in color[:3])


# -----------------------------------------------------------------------------
# Procedural Drawing Primitives
# -----------------------------------------------------------------------------
def draw_sparkle_star(draw, cx, cy, r, color, points=4):
    """Draws a shimmering anime 4-point or 8-point sparkle star."""
    pts = []
    total_pts = points * 2
    for i in range(total_pts):
        angle = i * (math.pi / points) - (math.pi / 2)
        radius = r if (i % 2 == 0) else max(2, int(r * 0.22))
        px = cx + radius * math.cos(angle)
        py = cy + radius * math.sin(angle)
        pts.append((px, py))
    draw.polygon(pts, fill=color)
    # Center gleam
    core_r = max(1, r // 4)
    draw.ellipse([(cx - core_r, cy - core_r), (cx + core_r, cy + core_r)], fill=(255, 255, 255, 240))


def draw_floating_petal(draw, cx, cy, size, angle_deg, color):
    """Draws a delicate falling shoujo-manga rose petal."""
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
    # Petal crease highlight
    top_x = cx + (0 * cos_a - (-size * 0.8) * sin_a)
    top_y = cy + (0 * sin_a + (-size * 0.8) * cos_a)
    bot_x = cx + (0 * cos_a - (size * 0.5) * sin_a)
    bot_y = cy + (0 * sin_a + (size * 0.5) * cos_a)
    draw.line([(top_x, top_y), (bot_x, bot_y)], fill=(255, 255, 255, 120), width=1)


def draw_shoujo_eye(draw, cx, cy, w, h, eye_color, look_left=True):
    """Draws a classic nostalgic shoujo-manga eye with multi-layer starry reflections."""
    white = (255, 255, 255, 255)
    skin_shadow = (235, 225, 220, 255)
    
    # Eye Sclera (White base with upper shadow)
    sclera_box = [(cx - w, cy - h), (cx + w, cy + h)]
    draw.ellipse(sclera_box, fill=white)
    # Upper shadow inside eyeball
    draw.chord([(cx - w, cy - h), (cx + w, cy + h // 3)], start=180, end=360, fill=skin_shadow)

    # Iris
    iris_w = int(w * 0.75)
    iris_h = int(h * 0.95)
    iris_cx = cx - (w * 0.15 if look_left else -w * 0.15)
    iris_cy = cy + 2
    iris_box = [(iris_cx - iris_w, iris_cy - iris_h), (iris_cx + iris_w, iris_cy + iris_h)]
    
    dark_eye = darken(eye_color, 0.45)
    mid_eye = eye_color
    light_eye = lighten(eye_color, 0.45)

    draw.ellipse(iris_box, fill=mid_eye)
    # Upper dark gradient of iris
    draw.chord([(iris_cx - iris_w, iris_cy - iris_h), (iris_cx + iris_w, iris_cy)], start=180, end=360, fill=dark_eye)
    
    # Pupil
    pupil_w = int(iris_w * 0.45)
    pupil_h = int(iris_h * 0.55)
    draw.ellipse([(iris_cx - pupil_w, iris_cy - pupil_h), (iris_cx + pupil_w, iris_cy + pupil_h)], fill=(20, 20, 25, 255))

    # Lower iris starry reflection crescent
    draw.chord([(iris_cx - int(iris_w * 0.8), iris_cy), (iris_cx + int(iris_w * 0.8), iris_cy + int(iris_h * 0.9))],
               start=0, end=180, fill=light_eye)

    # Shoujo Multi-Sparkle Highlights
    # Big sparkling highlight
    draw.ellipse([(iris_cx - iris_w // 2 - 2, iris_cy - iris_h // 2 - 2),
                  (iris_cx - iris_w // 2 + 10, iris_cy - iris_h // 2 + 10)], fill=white)
    # Small secondary highlight
    draw.ellipse([(iris_cx + iris_w // 4, iris_cy + iris_h // 3),
                  (iris_cx + iris_w // 4 + 6, iris_cy + iris_h // 3 + 6)], fill=white)
    # Tiny sparkle star inside eye
    draw_sparkle_star(draw, iris_cx + 4, iris_cy - 4, 5, (255, 255, 255, 230), points=4)

    # Winged Upper Eyelash line (Thick, elegant shoujo wing)
    eyelash_color = (35, 25, 25, 255)
    lash_pts = [
        (cx - w - 8, cy - h // 3),
        (cx - w * 0.5, cy - h - 3),
        (cx + w * 0.3, cy - h - 5),
        (cx + w + 6, cy - h - 2),
        (cx + w + 16, cy - h - 8),  # Wing tip
        (cx + w + 8, cy - h + 2),
        (cx + w * 0.2, cy - h),
        (cx - w * 0.4, cy - h + 2),
        (cx - w - 6, cy - h // 3 + 3)
    ]
    draw.polygon(lash_pts, fill=eyelash_color)
    
    # Double eyelid crease line
    crease_y = cy - h - 10
    draw.arc([(cx - w * 0.8, crease_y - 6), (cx + w * 0.8, crease_y + 6)], start=200, end=340, fill=(160, 120, 110, 200), width=2)

    # Lower gentle lash line
    draw.arc([(cx - w * 0.7, cy + h - 6), (cx + w * 0.7, cy + h + 6)], start=20, end=160, fill=(90, 60, 60, 180), width=2)


def draw_epaulette(draw, cx, cy, width, height, theme_color, gold_color):
    """Draws an ornate royal shoulder epaulette with gold bullion fringe."""
    # Base rounded pad
    pad_box = [(cx - width // 2, cy - height // 2), (cx + width // 2, cy + height // 2)]
    draw.rounded_rectangle(pad_box, radius=12, fill=theme_color, outline=gold_color, width=4)
    
    # Inner gold embroidery strip
    inner_box = [(cx - width // 2 + 8, cy - height // 2 + 6), (cx + width // 2 - 8, cy + height // 2 - 6)]
    draw.rounded_rectangle(inner_box, radius=8, outline=gold_color, width=2)

    # Gold button on collar side
    draw.ellipse([(cx - width // 2 + 10, cy - 8), (cx - width // 2 + 26, cy + 8)], fill=gold_color)
    draw.ellipse([(cx - width // 2 + 13, cy - 5), (cx - width // 2 + 23, cy + 5)], fill=(255, 235, 140, 255))

    # Dangling gold bullion fringe
    fringe_count = 14
    spacing = (width - 16) / fringe_count
    fringe_len = 55
    start_x = cx - width // 2 + 8
    bot_y = cy + height // 2

    for i in range(fringe_count):
        fx = int(start_x + i * spacing)
        # Gold cord
        draw.line([(fx, bot_y), (fx + (i - 7) * 2, bot_y + fringe_len)], fill=gold_color, width=3)
        # Gold droplet bead at tip
        tip_x = fx + (i - 7) * 2
        tip_y = bot_y + fringe_len
        draw.ellipse([(tip_x - 3, tip_y - 3), (tip_x + 3, tip_y + 3)], fill=(255, 225, 100, 255))


def draw_aiguillette_cords(draw, start_pt, mid_pt, end_pt, gold_color, width=4):
    """Draws curved decorative gold aiguillette ropes looping across uniform."""
    pts = []
    # Quadratic Bezier
    for t in range(0, 101, 2):
        u = t / 100.0
        x = (1 - u)**2 * start_pt[0] + 2 * (1 - u) * u * mid_pt[0] + u**2 * end_pt[0]
        y = (1 - u)**2 * start_pt[1] + 2 * (1 - u) * u * mid_pt[1] + u**2 * end_pt[1]
        pts.append((int(x), int(y)))
    draw.line(pts, fill=gold_color, width=width)
    # Highlight thread
    pts_hi = [(p[0], p[1] - 1) for p in pts]
    draw.line(pts_hi, fill=(255, 240, 160, 200), width=1)


# -----------------------------------------------------------------------------
# Signature Visual Props & Emblems
# -----------------------------------------------------------------------------
def draw_signature_prop(draw, char_id, cx, cy, gold_color):
    """Draws signature emblems, microphones, instruments, and brooches."""
    if char_id == "hwang_young_woong":
        # Emerald Guardian Brooch & Golden Mic
        # 1. Brooch
        draw.ellipse([(cx - 30, cy - 30), (cx + 30, cy + 30)], fill=gold_color)
        draw.polygon([(cx, cy - 25), (cx + 22, cy), (cx, cy + 25), (cx - 22, cy)], fill=(27, 105, 78, 255))
        draw_sparkle_star(draw, cx, cy, 14, (120, 235, 180, 255), 4)
        # 2. Golden Mic in hand/crest
        mic_x = cx + 80
        mic_y = cy + 40
        draw.ellipse([(mic_x - 18, mic_y - 30), (mic_x + 18, mic_y)], fill=gold_color)
        draw.rectangle([(mic_x - 8, mic_y), (mic_x + 8, mic_y + 55)], fill=(60, 60, 65, 255))
        draw.rectangle([(mic_x - 12, mic_y + 55), (mic_x + 12, mic_y + 68)], fill=gold_color)

    elif char_id == "lim_young_woong":
        # Starburst Halo Crest & Sky Blue Silk Emblem
        for r in range(40, 75, 12):
            draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], outline=(186, 230, 253, 160), width=2)
        draw_sparkle_star(draw, cx, cy, 38, gold_color, 8)
        draw_sparkle_star(draw, cx, cy, 18, (255, 255, 255, 255), 4)

    elif char_id == "lee_chan_won":
        # Antique Gold Spectacles & Royal Lily Crest
        # Spectacles
        glass_r = 18
        draw.ellipse([(cx - 38 - glass_r, cy - glass_r), (cx - 38 + glass_r, cy + glass_r)], outline=gold_color, width=3)
        draw.ellipse([(cx + 38 - glass_r, cy - glass_r), (cx + 38 + glass_r, cy + glass_r)], outline=gold_color, width=3)
        draw.line([(cx - 38 + glass_r, cy), (cx + 38 - glass_r, cy)], fill=gold_color, width=3)
        # Lily petals
        draw_floating_petal(draw, cx, cy + 45, 26, 0, (255, 245, 245, 240))
        draw_floating_petal(draw, cx - 18, cy + 48, 22, -35, (255, 235, 238, 220))
        draw_floating_petal(draw, cx + 18, cy + 48, 22, 35, (255, 235, 238, 220))

    elif char_id == "young_tak":
        # Energy Lightning Scepter / Badge & Thumbs Up Crest
        pts = [(cx - 10, cy - 45), (cx + 25, cy - 45), (cx - 5, cy), (cx + 20, cy), (cx - 20, cy + 50), (cx - 5, cy + 8), (cx - 25, cy + 8)]
        draw.polygon(pts, fill=(250, 204, 21, 255))
        draw_sparkle_star(draw, cx + 12, cy - 25, 20, (255, 255, 255, 255), 4)

    elif char_id == "jeong_dong_won":
        # Golden Saxophone & Musical Treble Crest
        sax_x, sax_y = cx, cy
        draw.ellipse([(sax_x - 14, sax_y + 15), (sax_x + 14, sax_y + 45)], fill=gold_color)
        draw.line([(sax_x - 6, sax_y - 35), (sax_x - 6, sax_y + 25)], fill=gold_color, width=8)
        draw.line([(sax_x - 6, sax_y - 35), (sax_x + 18, sax_y - 45)], fill=gold_color, width=6)
        draw_sparkle_star(draw, sax_x + 22, sax_y - 45, 14, (255, 255, 255, 255), 4)

    elif char_id == "kim_ho_joong":
        # Opera Velvet Crest & Royal Heraldic Shield
        shield_pts = [(cx, cy - 40), (cx + 36, cy - 30), (cx + 32, cy + 15), (cx, cy + 48), (cx - 32, cy + 15), (cx - 36, cy - 30)]
        draw.polygon(shield_pts, fill=(107, 33, 168, 255), outline=gold_color)
        draw.polygon([(p[0], p[1]) for p in shield_pts], outline=gold_color)
        draw_sparkle_star(draw, cx, cy + 4, 18, gold_color, 4)

    elif char_id == "jang_min_ho":
        # Champagne Gold Tuxedo Brooch & Diamond Crest
        pts = [(cx, cy - 40), (cx + 32, cy), (cx, cy + 40), (cx - 32, cy)]
        draw.polygon(pts, fill=gold_color)
        draw.polygon([(cx, cy - 26), (cx + 20, cy), (cx, cy + 26), (cx - 20, cy)], fill=(254, 243, 199, 255))
        draw_sparkle_star(draw, cx, cy, 18, (255, 255, 255, 255), 4)

    elif char_id == "park_seo_jin":
        # Golden Janggu Drumsticks & North Star (닻별)
        # 1. North star
        draw_sparkle_star(draw, cx, cy - 10, 36, gold_color, 8)
        draw_sparkle_star(draw, cx, cy - 10, 16, (255, 255, 255, 255), 4)
        # 2. Crossed drumsticks
        draw.line([(cx - 35, cy + 35), (cx + 35, cy - 15)], fill=gold_color, width=5)
        draw.line([(cx + 35, cy + 35), (cx - 35, cy - 15)], fill=gold_color, width=5)

    elif char_id == "son_tae_jin":
        # Burgundy Wine Rose & Grand Piano Keys Crest
        # Rose
        draw_floating_petal(draw, cx, cy, 26, 15, (159, 18, 57, 255))
        draw_floating_petal(draw, cx - 12, cy - 10, 20, -45, (190, 18, 60, 240))
        draw_floating_petal(draw, cx + 12, cy + 8, 22, 65, (225, 29, 72, 240))
        # Piano key arc
        key_y = cy + 42
        for k in range(-3, 4):
            kx = cx + k * 12
            draw.rectangle([(kx - 5, key_y), (kx + 5, key_y + 24)], fill=(255, 255, 255, 240), outline=(50, 20, 30, 255))

    elif char_id == "ahn_sung_hoon_jin_hae_seong":
        # Traditional Mother-of-Pearl Knot (자개 매듭) & Vintage Broadcast Mic
        draw.ellipse([(cx - 28, cy - 28), (cx + 28, cy + 28)], fill=(13, 148, 136, 255), outline=gold_color, width=3)
        draw.ellipse([(cx - 18, cy - 18), (cx + 18, cy + 18)], fill=(204, 251, 241, 240))
        # Traditional knot cross
        draw.line([(cx - 32, cy), (cx + 32, cy)], fill=gold_color, width=4)
        draw.line([(cx, cy - 32), (cx, cy + 32)], fill=gold_color, width=4)
        draw_sparkle_star(draw, cx, cy, 14, (255, 255, 255, 255), 4)


# -----------------------------------------------------------------------------
# Master 1080x1440 Sprite Generator
# -----------------------------------------------------------------------------
def generate_character_sprite(char_info: dict) -> Image.Image:
    """
    Renders an original nostalgic shoujo-manga prince sprite at 1080x1440
    with RGBA transparency.
    """
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    char_id = char_info["id"]
    theme_hex = char_info["theme_color"]
    accent_hex = char_info["accent_color"]
    
    theme_rgb = hex_to_rgb(theme_hex)
    accent_rgb = hex_to_rgb(accent_hex)
    gold_rgb = (212, 175, 55, 255)
    soft_gold = (245, 225, 140, 220)

    # Figure Center of Mass (Optimized for side-by-side two-shot: Right Half)
    HEAD_X = 720
    HEAD_Y = 460
    SHOULDER_Y = 640
    BODY_CX = 730

    # 1. Background Celestial Aura & Magic Atmosphere
    # Radial aura glow
    for r in range(480, 80, -25):
        alpha = int(35 * (1.0 - (r / 480.0)))
        draw.ellipse([(HEAD_X - r, HEAD_Y + 100 - r), (HEAD_X + r, HEAD_Y + 100 + r)],
                     fill=(theme_rgb[0], theme_rgb[1], theme_rgb[2], alpha))

    # Floating Sparkles & Stars
    sparkle_coords = [
        (480, 240, 16), (580, 160, 24), (880, 180, 28), (980, 280, 20),
        (420, 480, 22), (990, 560, 26), (460, 780, 18), (1020, 860, 22),
        (510, 1020, 24), (960, 1140, 20), (740, 180, 32)
    ]
    for sx, sy, sr in sparkle_coords:
        draw_sparkle_star(draw, sx, sy, sr, soft_gold, 4 if sr < 24 else 8)

    # Cascading Rose Petals
    petal_coords = [
        (440, 320, 18, 25), (920, 360, 22, -40), (490, 620, 20, 75),
        (1000, 720, 24, 15), (430, 940, 22, -60), (950, 990, 20, 45),
        (620, 210, 16, -15), (860, 240, 18, 30)
    ]
    petal_tint = (accent_rgb[0], accent_rgb[1], accent_rgb[2], 220)
    for px, py, ps, pa in petal_coords:
        draw_floating_petal(draw, px, py, ps, pa, petal_tint)

    # 2. Billowing Royal Velvet Cape (Back layer)
    cape_dark = darken(theme_rgb, 0.45)
    cape_pts = [
        (BODY_CX - 280, SHOULDER_Y + 20),
        (BODY_CX + 280, SHOULDER_Y + 20),
        (WIDTH - 40, HEIGHT - 80),
        (WIDTH - 120, HEIGHT - 40),
        (BODY_CX + 150, HEIGHT - 100),
        (BODY_CX, HEIGHT - 50),
        (BODY_CX - 220, HEIGHT - 80),
        (BODY_CX - 360, HEIGHT - 120),
        (BODY_CX - 320, SHOULDER_Y + 80)
    ]
    draw.polygon(cape_pts, fill=cape_dark)
    # Cape silk inner lining folds
    draw.polygon([(BODY_CX - 320, SHOULDER_Y + 80), (BODY_CX - 200, SHOULDER_Y + 120),
                  (BODY_CX - 180, HEIGHT - 140), (BODY_CX - 360, HEIGHT - 120)],
                 fill=(accent_rgb[0], accent_rgb[1], accent_rgb[2], 200))

    # 3. Back Hair Volume
    hair_base = (35, 25, 25, 255)
    if char_id in ["lim_young_woong", "young_tak"]:
        hair_base = (20, 25, 35, 255)
    elif char_id in ["lee_chan_won", "jang_min_ho"]:
        hair_base = (70, 45, 25, 255)
    elif char_id == "son_tae_jin":
        hair_base = (55, 20, 25, 255)

    draw.ellipse([(HEAD_X - 165, HEAD_Y - 170), (HEAD_X + 165, HEAD_Y + 140)], fill=hair_base)
    # Flowing side hair curls
    draw.polygon([(HEAD_X - 160, HEAD_Y), (HEAD_X - 220, HEAD_Y + 160),
                  (HEAD_X - 140, HEAD_Y + 220), (HEAD_X - 100, HEAD_Y + 120)], fill=hair_base)
    draw.polygon([(HEAD_X + 160, HEAD_Y), (HEAD_X + 220, HEAD_Y + 160),
                  (HEAD_X + 140, HEAD_Y + 220), (HEAD_X + 100, HEAD_Y + 120)], fill=hair_base)

    # 4. Neck & Face Anatomy (Shoujo Manga Delicate Proportions)
    skin_tone = (255, 240, 230, 255)
    skin_shadow = (240, 215, 200, 255)
    blush_color = (255, 175, 180, 130)

    # Neck
    neck_pts = [
        (HEAD_X - 55, HEAD_Y + 80),
        (HEAD_X + 55, HEAD_Y + 80),
        (HEAD_X + 68, SHOULDER_Y),
        (HEAD_X - 68, SHOULDER_Y)
    ]
    draw.polygon(neck_pts, fill=skin_shadow)
    draw.polygon([(HEAD_X - 45, HEAD_Y + 80), (HEAD_X + 45, HEAD_Y + 80),
                  (HEAD_X + 55, SHOULDER_Y), (HEAD_X - 55, SHOULDER_Y)], fill=skin_tone)

    # Face Oval / Jawline
    jaw_pts = [
        (HEAD_X - 135, HEAD_Y - 40),
        (HEAD_X - 130, HEAD_Y + 40),
        (HEAD_X - 85, HEAD_Y + 125),
        (HEAD_X, HEAD_Y + 175),  # Chin
        (HEAD_X + 85, HEAD_Y + 125),
        (HEAD_X + 130, HEAD_Y + 40),
        (HEAD_X + 135, HEAD_Y - 40)
    ]
    draw.polygon(jaw_pts, fill=skin_tone)

    # Cheeks Watercolor Blush
    draw.ellipse([(HEAD_X - 125, HEAD_Y + 45), (HEAD_X - 55, HEAD_Y + 95)], fill=blush_color)
    draw.ellipse([(HEAD_X + 55, HEAD_Y + 45), (HEAD_X + 125, HEAD_Y + 95)], fill=blush_color)

    # Nose (Delicate anime profile line)
    draw.line([(HEAD_X - 2, HEAD_Y + 30), (HEAD_X + 6, HEAD_Y + 65)], fill=(210, 170, 155, 240), width=3)
    draw.line([(HEAD_X + 6, HEAD_Y + 65), (HEAD_X + 1, HEAD_Y + 70)], fill=(210, 170, 155, 240), width=3)

    # Warm, Charming Manga Lips
    lip_color = (235, 115, 125, 230)
    draw.arc([(HEAD_X - 35, HEAD_Y + 95), (HEAD_X + 35, HEAD_Y + 125)], start=15, end=165, fill=lip_color, width=4)
    # Upper lip center notch
    draw.arc([(HEAD_X - 15, HEAD_Y + 98), (HEAD_X + 15, HEAD_Y + 108)], start=200, end=340, fill=(210, 95, 105, 200), width=2)
    # Lower lip specular gleam
    draw.ellipse([(HEAD_X - 8, HEAD_Y + 115), (HEAD_X + 8, HEAD_Y + 121)], fill=(255, 240, 240, 240))

    # Eyebrows
    brow_color = darken(hair_base, 0.2)
    draw.line([(HEAD_X - 105, HEAD_Y - 35), (HEAD_X - 35, HEAD_Y - 42)], fill=brow_color, width=4)
    draw.line([(HEAD_X + 35, HEAD_Y - 42), (HEAD_X + 105, HEAD_Y - 35)], fill=brow_color, width=4)

    # Shoujo Eyes (Left & Right)
    draw_shoujo_eye(draw, HEAD_X - 62, HEAD_Y + 5, 34, 24, theme_rgb, look_left=True)
    draw_shoujo_eye(draw, HEAD_X + 62, HEAD_Y + 5, 34, 24, theme_rgb, look_left=True)

    # 5. Voluminous Flowing Front Bangs & Angel Ring Gleam
    hair_highlight = lighten(hair_base, 0.45)
    # Bang strands covering forehead
    bangs = [
        [(HEAD_X - 145, HEAD_Y - 140), (HEAD_X - 90, HEAD_Y - 30), (HEAD_X - 130, HEAD_Y + 20)],
        [(HEAD_X - 110, HEAD_Y - 150), (HEAD_X - 40, HEAD_Y - 15), (HEAD_X - 80, HEAD_Y + 30)],
        [(HEAD_X - 50, HEAD_Y - 160), (HEAD_X + 10, HEAD_Y - 20), (HEAD_X - 20, HEAD_Y + 35)],
        [(HEAD_X + 10, HEAD_Y - 160), (HEAD_X + 60, HEAD_Y - 15), (HEAD_X + 40, HEAD_Y + 30)],
        [(HEAD_X + 60, HEAD_Y - 150), (HEAD_X + 120, HEAD_Y - 30), (HEAD_X + 90, HEAD_Y + 20)],
        [(HEAD_X + 100, HEAD_Y - 130), (HEAD_X + 150, HEAD_Y - 10), (HEAD_X + 130, HEAD_Y + 50)]
    ]
    for b in bangs:
        draw.polygon(b, fill=hair_base)
        # Highlight strand
        draw.line([b[0], b[1]], fill=hair_highlight, width=3)

    # Angel Ring (Glossy hair gleam band)
    draw.arc([(HEAD_X - 140, HEAD_Y - 130), (HEAD_X + 140, HEAD_Y - 60)], start=200, end=340, fill=(255, 255, 255, 140), width=5)

    # 6. Royal High Standing Collar & Silk Cravat / Tie
    collar_y = SHOULDER_Y - 25
    draw.polygon([(HEAD_X - 70, collar_y), (HEAD_X + 70, collar_y),
                  (HEAD_X + 60, collar_y + 60), (HEAD_X - 60, collar_y + 60)],
                 fill=(255, 255, 255, 255), outline=gold_rgb, width=3)

    # Cravat / Silk Tie
    cravat_color = hex_to_rgb(accent_hex)
    draw.polygon([(HEAD_X - 25, collar_y + 35), (HEAD_X + 25, collar_y + 35),
                  (HEAD_X + 35, collar_y + 115), (HEAD_X, collar_y + 140), (HEAD_X - 35, collar_y + 115)],
                 fill=cravat_color, outline=gold_rgb, width=2)
    # Tie Brooch Gem
    draw.ellipse([(HEAD_X - 12, collar_y + 45), (HEAD_X + 12, collar_y + 69)], fill=gold_rgb)
    draw.ellipse([(HEAD_X - 7, collar_y + 50), (HEAD_X + 7, collar_y + 64)], fill=theme_rgb)

    # 7. Royal Prince Regalia Uniform (Chest & Torso)
    suit_color = theme_rgb
    suit_shadow = darken(theme_rgb, 0.25)
    
    torso_pts = [
        (BODY_CX - 240, SHOULDER_Y + 15),
        (BODY_CX + 240, SHOULDER_Y + 15),
        (BODY_CX + 210, HEIGHT - 100),
        (BODY_CX - 210, HEIGHT - 100)
    ]
    draw.polygon(torso_pts, fill=suit_color)

    # Diagonal Royal Order Sash across chest
    sash_color = (accent_rgb[0], accent_rgb[1], accent_rgb[2], 240)
    sash_pts = [
        (BODY_CX + 190, SHOULDER_Y + 25),
        (BODY_CX + 240, SHOULDER_Y + 30),
        (BODY_CX - 150, HEIGHT - 120),
        (BODY_CX - 210, HEIGHT - 120)
    ]
    draw.polygon(sash_pts, fill=sash_color)
    draw.line([(BODY_CX + 190, SHOULDER_Y + 25), (BODY_CX - 150, HEIGHT - 120)], fill=gold_rgb, width=4)
    draw.line([(BODY_CX + 240, SHOULDER_Y + 30), (BODY_CX - 210, HEIGHT - 120)], fill=gold_rgb, width=4)

    # Royal Golden Epaulettes on both shoulders
    draw_epaulette(draw, BODY_CX - 200, SHOULDER_Y + 25, 120, 48, suit_shadow, gold_rgb)
    draw_epaulette(draw, BODY_CX + 200, SHOULDER_Y + 25, 120, 48, suit_shadow, gold_rgb)

    # Braided Gold Aiguillette Ropes looping to breast buttons
    draw_aiguillette_cords(draw, (BODY_CX + 170, SHOULDER_Y + 45), (BODY_CX + 80, SHOULDER_Y + 160), (BODY_CX - 10, SHOULDER_Y + 130), gold_rgb, 4)
    draw_aiguillette_cords(draw, (BODY_CX + 190, SHOULDER_Y + 55), (BODY_CX + 110, SHOULDER_Y + 210), (BODY_CX - 10, SHOULDER_Y + 180), gold_rgb, 4)

    # Double-Breasted Golden Heraldic Buttons
    for btn_y in range(SHOULDER_Y + 110, HEIGHT - 220, 65):
        # Left button
        draw.ellipse([(BODY_CX - 55, btn_y - 12), (BODY_CX - 31, btn_y + 12)], fill=gold_rgb)
        draw.ellipse([(BODY_CX - 51, btn_y - 8), (BODY_CX - 35, btn_y + 8)], fill=soft_gold)
        # Right button
        draw.ellipse([(BODY_CX + 31, btn_y - 12), (BODY_CX + 55, btn_y + 12)], fill=gold_rgb)
        draw.ellipse([(BODY_CX + 35, btn_y - 8), (BODY_CX + 51, btn_y + 8)], fill=soft_gold)

    # 8. Signature Visual Emblem & Prop
    draw_signature_prop(draw, char_id, BODY_CX - 100, SHOULDER_Y + 160, gold_rgb)

    # 9. Deluxe Collectible Bottom Plaque / Name Banner
    banner_y = HEIGHT - 200
    banner_box = [(BODY_CX - 280, banner_y), (BODY_CX + 280, banner_y + 130)]
    
    # Frosted glass banner backdrop
    draw.rounded_rectangle(banner_box, radius=18, fill=(15, 23, 42, 235), outline=gold_rgb, width=4)
    draw.rounded_rectangle([(banner_box[0][0] + 6, banner_box[0][1] + 6),
                            (banner_box[1][0] - 6, banner_box[1][1] - 6)],
                           radius=14, outline=(soft_gold[0], soft_gold[1], soft_gold[2], 180), width=2)

    # Prince Title & Name Text
    title_text = f"{char_info['badge_emoji']} {char_info['title']}"
    name_text = char_info["name_ko"]
    sub_text = "황영웅과 함께하는 파라다이스 투샷"

    draw.text((BODY_CX, banner_y + 24), title_text, font=font_title, fill=soft_gold, anchor="mm")
    draw.text((BODY_CX, banner_y + 68), name_text, font=font_name, fill=(255, 255, 255, 255), anchor="mm")
    draw.text((BODY_CX, banner_y + 104), sub_text, font=font_small, fill=(200, 215, 230, 230), anchor="mm")

    return img


# -----------------------------------------------------------------------------
# Selector Thumbnail Generator (160x160)
# -----------------------------------------------------------------------------
def generate_character_thumbnail(sprite_img: Image.Image, char_info: dict) -> Image.Image:
    """
    Produces a crisp, high-visibility 160x160 circular/avatar thumbnail
    highlighting the prince's face, starry eyes, and royal regalia.
    """
    thumb = Image.new("RGBA", (THUMB_SIZE, THUMB_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(thumb)

    theme_rgb = hex_to_rgb(char_info["theme_color"])
    gold_rgb = (212, 175, 55, 255)

    # 1. Subtle luxury circular base
    margin = 4
    draw.ellipse([(margin, margin), (THUMB_SIZE - margin, THUMB_SIZE - margin)],
                 fill=(248, 250, 252, 255), outline=gold_rgb, width=4)
    # Inner theme ring
    draw.ellipse([(margin + 4, margin + 4), (THUMB_SIZE - margin - 4, THUMB_SIZE - margin - 4)],
                 outline=(theme_rgb[0], theme_rgb[1], theme_rgb[2], 180), width=2)

    # 2. Crop head & bust from master sprite
    # Master face center is at X=720, Y=460. Crop box 500x500
    crop_cx = 720
    crop_cy = 475
    crop_w = 480
    crop_h = 480
    crop_box = (crop_cx - crop_w // 2, crop_cy - crop_h // 2,
                crop_cx + crop_w // 2, crop_cy + crop_h // 2)

    head_crop = sprite_img.crop(crop_box)
    
    # Target avatar size
    avatar_size = THUMB_SIZE - 20
    head_resized = head_crop.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)

    # Circular mask for avatar
    mask = Image.new("L", (avatar_size, avatar_size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse([(0, 0), (avatar_size, avatar_size)], fill=255)

    # Paste onto thumbnail
    thumb.paste(head_resized, (10, 10), mask)

    # 3. Outer golden crest ring
    draw.ellipse([(margin, margin), (THUMB_SIZE - margin, THUMB_SIZE - margin)], outline=gold_rgb, width=3)
    
    # 4. Tiny sparkle at upper right
    draw_sparkle_star(draw, THUMB_SIZE - 22, 22, 9, (255, 255, 255, 255), 4)

    return thumb


# -----------------------------------------------------------------------------
# Main Generation Flow
# -----------------------------------------------------------------------------
def generate_all_characters():
    json_path = os.path.join(BASE_DIR, "data", "characters.json")
    with open(json_path, "r", encoding="utf-8") as f:
        characters = json.load(f)

    print("=================================================================")
    print("Generating 10 Shoujo-Manga Prince Trot Singer Character Assets")
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"Total Characters: {len(characters)}")
    print("=================================================================\n")

    for idx, char in enumerate(characters, 1):
        char_id = char["id"]
        sprite_filename = f"sprite_{char_id}.png"
        thumb_filename = f"thumb_{char_id}.png"
        sprite_path = os.path.join(OUTPUT_DIR, sprite_filename)
        thumb_path = os.path.join(OUTPUT_DIR, thumb_filename)

        print(f"[{idx}/10] Rendering Prince: {char['name_ko']} ({char['title']}) [{char_id}]...")
        
        # 1. Generate 1080x1440 Sprite
        sprite_img = generate_character_sprite(char)
        sprite_img.save(sprite_path, "PNG", optimize=True)
        sprite_kb = os.path.getsize(sprite_path) / 1024
        print(f"  -> Saved Master Sprite: {sprite_filename} ({WIDTH}x{HEIGHT}, {sprite_kb:.1f} KB)")

        # 2. Generate 160x160 Selector Thumbnail
        thumb_img = generate_character_thumbnail(sprite_img, char)
        thumb_img.save(thumb_path, "PNG", optimize=True)
        thumb_kb = os.path.getsize(thumb_path) / 1024
        print(f"  -> Saved Selector Thumb: {thumb_filename} ({THUMB_SIZE}x{THUMB_SIZE}, {thumb_kb:.1f} KB)")

    print(f"\n[SUCCESS] Successfully generated all {len(characters) * 2} assets in {OUTPUT_DIR}")


if __name__ == "__main__":
    generate_all_characters()
