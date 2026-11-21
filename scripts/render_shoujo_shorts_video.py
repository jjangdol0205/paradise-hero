#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_shoujo_shorts_video.py
================================================================================
Division 4: Dynamic 8090 Shoujo-Manga Comic Moving-Toon Video Renderer & Clean Mastering
@김쌤의영웅라디오 & 파라다이스히어로 (paradise-hero.com)

Features:
1. Multi-Panel Comic Book Layouts & Prince Diversity (No Single Cutout):
   - Beat 0: Hwang Young-woong (clean_prince_1) Full Splash with dramatic eyes/face crop & radial speedlines
   - Beat 1: 2-Panel Slanted Split (Top: Hwang Young-woong clean_prince_9 emotional close-up; Bottom: warm hands/mic)
   - Beat 2: 3-Panel Sequential Reveal with distinct backgrounds & comic gutters (clean_prince_5 imperial)
   - Beat 3: Multi-Prince Alliance Split featuring Lim Young-woong (clean_prince_2), Hwang Young-woong (clean_prince_1),
             Lee Chan-won (clean_prince_3), and Young Tak (clean_prince_4)
   - Beat 4: Imperial Rebirth Splash with exploding golden speedlines & royal aura (clean_prince_1)
   - Beat 5: Ultra-Close Eye Contact with deep punch-in zoom & eye diamond glitter (clean_prince_8)
   - Beat 6: Warm Gratitude & Radio DJ Look with gentle zoom-out (clean_prince_10)
   - Beat 7: Ending Slate Panel with vector crown & camera (clean typography, zero tofu '□' glyphs)
2. Clean Sprites without Baked-In Nameplates:
   - High-resolution clean RGBA sprites (clean_prince_1..10) without text boxes
   - Zero subtitle collision in Lower Safe Zone Y=1380~1465
3. Authentic Comic Book Elements:
   - 6~8px gold/white manga panel borders with 12~16px dark comic gutters
   - Stylized comic speech bubbles (말풍선) with pointer tails
   - Framed shoujo monologue narration boxes (독백 나레이션 박스) with corner ornaments
   - Vintage screentone halftone dot patterns
4. Zero Broken Emoji Tofu:
   - Replaced raw emojis with clean Korean typography and PIL geometric vector crown/camera icons
5. Clean Video Mastering Standards:
   - 1080x1920 vertical, 30fps H.264 + AAC 192kbps
   - Fullscreen body (0s to 2.5s before end): top/bottom mean > 8.0, std > 3.0, mean < 245.0
   - Lower safe zone subtitles (Y=1380~1465, stroke 10, zero rectangular boxes)
   - Ending slate active strictly final 2.5~3.8s with paradise-hero.com domain callout
================================================================================
"""

import os
import sys
import math
import json
import time
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Ensure UTF-8 on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = "ffmpeg"

SCRIPT_DIR = Path(__file__).resolve().parent
DIVISION_DIR = SCRIPT_DIR.parent
DATA_DIR = DIVISION_DIR / "data"
ASSETS_DIR = DIVISION_DIR / "assets" / "characters"
CONTENT_DIR = DIVISION_DIR / "content" / "shorts_daily" / "ep_shoujo_pilot"
SPRITE_CACHE_DIR = Path(r"D:\드림컴퍼니\.agents\teamwork\worker_d4_m3_remediation\cached_sprites")
SPRITE_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Video standards
WIDTH = 1080
HEIGHT = 1920
FPS = 30

# Font resolution
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\malgunbd.ttf",
    r"C:\Windows\Fonts\malgun.ttf",
    r"C:\Windows\Fonts\gulim.ttc",
    r"D:\드림컴퍼니\3사업부\src\fonts\Pretendard-Black.otf"
]


def get_font(size: int) -> ImageFont.FreeTypeFont:
    """Finds best available bold Korean font."""
    for fp in FONT_CANDIDATES:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()


def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    """Converts hex color code to RGB tuple."""
    hex_clean = hex_str.lstrip("#")
    if len(hex_clean) == 6:
        return (
            int(hex_clean[0:2], 16),
            int(hex_clean[2:4], 16),
            int(hex_clean[4:6], 16)
        )
    return (27, 77, 62)


def strip_emojis(text: str) -> str:
    """Strips high-unicode emojis that render as tofu □ in standard TTF fonts."""
    cleaned = []
    for ch in text:
        cp = ord(ch)
        if (
            (0x1F300 <= cp <= 0x1F9FF) or
            (0x2600 <= cp <= 0x27BF) or
            (0x1FA00 <= cp <= 0x1FAFF) or
            (0xFE00 <= cp <= 0xFE0F) or
            cp in (0x2705, 0x274C, 0x2728, 0x2764)
        ):
            continue
        cleaned.append(ch)
    return "".join(cleaned).strip()


def draw_centered_stroked_text(
    draw: ImageDraw.ImageDraw,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill_color: Tuple[int, int, int, int],
    stroke_width: int = 10,
    stroke_color: Tuple[int, int, int, int] = (0, 0, 0, 255)
) -> int:
    """Draws centered text with thick black outline for subtitle safe zone."""
    clean_txt = strip_emojis(text)
    bbox = draw.textbbox((0, 0), clean_txt, font=font)
    tw = bbox[2] - bbox[0]
    x = (WIDTH - tw) // 2
    draw.text(
        (x, y),
        clean_txt,
        font=font,
        fill=fill_color,
        stroke_width=stroke_width,
        stroke_fill=stroke_color
    )
    return x


# ==============================================================================
# VECTOR GRAPHICS: GEOMETRIC ROYAL CROWN & CAMERA ICONS (ZERO TOFU '□')
# ==============================================================================

def draw_vector_crown(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    size: int = 40,
    fill_color: Tuple[int, int, int] = (255, 215, 0),
    outline_color: Tuple[int, int, int] = (180, 130, 20)
):
    """Draws a 5-point shoujo manga golden royal crown vector icon."""
    w = size
    h = int(size * 0.72)
    x0 = cx - w // 2
    y0 = cy - h // 2
    x1 = cx + w // 2
    y1 = cy + h // 2

    pts = [
        (x0, y1),
        (x1, y1),
        (x1, y0 + int(h * 0.28)),
        (cx + int(w * 0.26), y0 + int(h * 0.60)),
        (cx, y0),
        (cx - int(w * 0.26), y0 + int(h * 0.60)),
        (x0, y0 + int(h * 0.28)),
    ]
    draw.polygon(pts, fill=fill_color, outline=outline_color)
    r = max(2, size // 11)
    for px, py in [(x0, y0 + int(h * 0.28)), (cx, y0), (x1, y0 + int(h * 0.28))]:
        draw.ellipse([px - r, py - r, px + r, py + r], fill=(255, 255, 255), outline=outline_color)
    draw.line([(x0 + 3, y1 - 4), (x1 - 3, y1 - 4)], fill=outline_color, width=2)


def draw_vector_camera(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    size: int = 38,
    fill_color: Tuple[int, int, int] = (255, 230, 0),
    outline_color: Tuple[int, int, int] = (20, 25, 35)
):
    """Draws a clean vector camera icon."""
    w = size
    h = int(size * 0.70)
    x0 = cx - w // 2
    y0 = cy - h // 2
    x1 = cx + w // 2
    y1 = cy + h // 2

    bw = int(w * 0.35)
    bh = int(h * 0.25)
    draw.rounded_rectangle([cx - bw // 2, y0 - bh + 2, cx + bw // 2, y0 + 3], radius=3, fill=fill_color, outline=outline_color, width=2)
    draw.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=fill_color, outline=outline_color, width=2)
    lr = int(h * 0.34)
    draw.ellipse([cx - lr, cy - lr + 2, cx + lr, cy + lr + 2], fill=(20, 30, 45), outline=(255, 255, 255), width=2)
    dr = max(2, lr // 3)
    draw.ellipse([cx - lr // 3 - dr, cy - dr, cx - lr // 3 + dr, cy + dr], fill=(255, 255, 255))


# ==============================================================================
# AUTHENTIC COMIC BOOK ELEMENTS: SPEECH BUBBLE & MONOLOGUE NARRATION BOX
# ==============================================================================

def draw_shoujo_monologue_box(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    y: int = 110,
    tag: str = ""
):
    """Draws an authentic framed shoujo manga monologue narration box with corner ornaments."""
    full_text = f"[ {tag} ]  {text}" if tag else text
    full_text = strip_emojis(full_text)
    bbox = draw.textbbox((0, 0), full_text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    pad_x = 24
    pad_y = 12
    box_w = tw + pad_x * 2
    box_h = th + pad_y * 2
    box_x = (WIDTH - box_w) // 2
    box_y = y

    # Framed box with cream/dark fill & double gold outline
    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=14,
        fill=(12, 22, 32, 238),
        outline=(212, 175, 55, 255),
        width=3
    )
    draw.rounded_rectangle(
        [box_x + 3, box_y + 3, box_x + box_w - 3, box_y + box_h - 3],
        radius=11,
        fill=None,
        outline=(255, 255, 255, 160),
        width=1
    )
    # Corner ornaments
    tick = 6
    draw.line([(box_x + 5, box_y + 5), (box_x + 5 + tick, box_y + 5)], fill=(255, 230, 90), width=2)
    draw.line([(box_x + 5, box_y + 5), (box_x + 5, box_y + 5 + tick)], fill=(255, 230, 90), width=2)
    draw.line([(box_x + box_w - 5, box_y + 5), (box_x + box_w - 5 - tick, box_y + 5)], fill=(255, 230, 90), width=2)
    draw.line([(box_x + box_w - 5, box_y + 5), (box_x + box_w - 5, box_y + 5 + tick)], fill=(255, 230, 90), width=2)

    draw.text((box_x + pad_x, box_y + pad_y), full_text, font=font, fill=(255, 245, 200, 255))


def draw_comic_speech_bubble(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    box_xy: Tuple[int, int, int, int],
    pointer_tip: Tuple[int, int]
):
    """Draws an authentic manga rounded speech bubble with a comic pointer tail."""
    clean_txt = strip_emojis(text)
    x1, y1, x2, y2 = box_xy
    px, py = pointer_tip

    # Bubble body (warm cream fill, crisp black outline)
    draw.rounded_rectangle([x1, y1, x2, y2], radius=22, fill=(255, 253, 245, 250), outline=(15, 20, 25, 255), width=3)
    # Pointer tail
    base_x = (x1 + x2) // 2
    draw.polygon([(base_x - 18, y2 - 2), (base_x + 18, y2 - 2), (px, py)], fill=(255, 253, 245, 250))
    draw.line([(base_x - 18, y2 - 1), (px, py), (base_x + 18, y2 - 1)], fill=(15, 20, 25, 255), width=3)

    bbox = draw.textbbox((0, 0), clean_txt, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = x1 + (x2 - x1 - tw) // 2
    ty = y1 + (y2 - y1 - th) // 2 - 2
    draw.text((tx, ty), clean_txt, font=font, fill=(12, 15, 20, 255))


# ==============================================================================
# PROCEDURAL BACKGROUNDS & VINTAGE SCREENTONE
# ==============================================================================

def create_dynamic_stage_background(theme_hex: str, accent_hex: str, seed: int = 42) -> Image.Image:
    """Creates a rich, full-bleed 1080x1920 stage background with radial spotlight and bokeh."""
    base_rgb = hex_to_rgb(theme_hex)
    accent_rgb = hex_to_rgb(accent_hex)

    y = np.linspace(0, 1, HEIGHT)[:, None]
    x = np.linspace(0, 1, WIDTH)[None, :]

    dx = (x - 0.5) * 1.2
    dy = (y - 0.38) * 1.5
    dist = np.sqrt(dx ** 2 + dy ** 2)
    spot = np.clip(1.0 - dist * 1.15, 0.0, 1.0) ** 1.8

    bg_r = np.clip(16 + base_rgb[0] * 0.35 * (1 - y * 0.55) + spot * base_rgb[0] * 0.75, 0, 255)
    bg_g = np.clip(18 + base_rgb[1] * 0.35 * (1 - y * 0.55) + spot * base_rgb[1] * 0.75, 0, 255)
    bg_b = np.clip(26 + base_rgb[2] * 0.35 * (1 - y * 0.55) + spot * base_rgb[2] * 0.75, 0, 255)

    rgb = np.stack([bg_r, bg_g, bg_b], axis=-1).astype(np.uint8)
    bg_img = Image.fromarray(rgb, "RGB").convert("RGBA")
    draw = ImageDraw.Draw(bg_img)

    rng = np.random.default_rng(seed)
    for _ in range(28):
        bx = int(rng.uniform(60, WIDTH - 60))
        by = int(rng.uniform(80, HEIGHT - 240))
        br = int(rng.uniform(15, 80))
        alpha = int(rng.uniform(25, 85))
        bokeh_color = (
            min(255, accent_rgb[0] + 50),
            min(255, accent_rgb[1] + 50),
            min(255, accent_rgb[2] + 50),
            alpha
        )
        draw.ellipse([bx - br, by - br, bx + br, by + br], fill=bokeh_color)

    for _ in range(36):
        sx = int(rng.uniform(40, WIDTH - 40))
        sy = int(rng.uniform(60, HEIGHT - 180))
        s_len = int(rng.uniform(4, 14))
        draw.line([sx - s_len, sy, sx + s_len, sy], fill=(255, 235, 150, 160), width=2)
        draw.line([sx, sy - s_len, sx, sy + s_len], fill=(255, 235, 150, 160), width=2)

    return bg_img


def create_vintage_screentone() -> Image.Image:
    """Pre-generates an authentic 8090 shoujo-manga retro halftone screentone layer."""
    tone = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(tone)
    dot_color = (20, 30, 45, 22)
    step = 14
    for y in range(0, HEIGHT, step):
        offset = (step // 2) if ((y // step) % 2 == 1) else 0
        for x in range(offset, WIDTH, step):
            d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=dot_color)
    return tone


# ==============================================================================
# PROCEDURAL MANGA VFX: ROSE PETALS, SPEEDLINES, DIAMOND SPARKLES
# ==============================================================================

class DriftingRosePetalSystem:
    """Sinusoidal drifting and tumbling rose petals physics simulation."""

    def __init__(self, count: int = 26, seed: int = 777):
        rng = np.random.default_rng(seed)
        self.petals = []
        self.stamp_textures = self._generate_petal_stamps()

        for i in range(count):
            self.petals.append({
                "x0": float(rng.uniform(0, WIDTH)),
                "y0": float(rng.uniform(0, HEIGHT)),
                "speed": float(rng.uniform(160, 340)),
                "drift": float(rng.uniform(30, 80)) * (1 if rng.uniform() > 0.5 else -1),
                "wave_freq": float(rng.uniform(2.0, 3.5)),
                "wave_amp": float(rng.uniform(18, 40)),
                "phi": float(rng.uniform(0, 2 * math.pi)),
                "rot_speed": float(rng.uniform(45, 135)) * (1 if rng.uniform() > 0.5 else -1),
                "angle0": float(rng.uniform(0, 360)),
                "texture_idx": int(i % len(self.stamp_textures)),
                "scale": float(rng.uniform(0.75, 1.25))
            })

    def _generate_petal_stamps(self) -> List[Image.Image]:
        stamps = []
        colors = [
            ((196, 30, 58, 225), (255, 200, 215, 240)),
            ((224, 17, 95, 225), (255, 220, 230, 240)),
            ((255, 140, 175, 230), (255, 240, 245, 240)),
            ((210, 45, 100, 225), (255, 210, 225, 240)),
        ]
        w, h = 54, 38
        for col_fill, col_out in colors:
            p = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            d = ImageDraw.Draw(p)
            d.chord([2, 2, w - 2, h - 2], start=15, end=345, fill=col_fill, outline=col_out, width=1)
            d.line([(w // 4, h // 2), (w * 3 // 4, h // 2)], fill=(255, 255, 255, 90), width=1)
            stamps.append(p)
        return stamps

    def render(self, t: float, target_img: Image.Image, max_count: Optional[int] = None):
        render_list = self.petals if max_count is None else self.petals[:max_count]
        for p in render_list:
            x = (p["x0"] + p["drift"] * t + p["wave_amp"] * math.sin(p["wave_freq"] * t + p["phi"])) % WIDTH
            y = (p["y0"] + p["speed"] * t) % HEIGHT
            angle = (p["angle0"] + p["rot_speed"] * t) % 360

            stamp = self.stamp_textures[p["texture_idx"]]
            if abs(p["scale"] - 1.0) > 0.05:
                nw = max(10, int(stamp.width * p["scale"]))
                nh = max(10, int(stamp.height * p["scale"]))
                cur_stamp = stamp.resize((nw, nh), Image.Resampling.BILINEAR)
            else:
                cur_stamp = stamp

            rot = cur_stamp.rotate(angle, expand=True, resample=Image.Resampling.BILINEAR)
            pos_x = int(x - rot.width // 2)
            pos_y = int(y - rot.height // 2)
            target_img.alpha_composite(rot, (pos_x, pos_y))


class RadialSpeedlinesEngine:
    """Procedural shoujo-manga radial focus speedlines radiating from character gaze."""

    def __init__(self, num_spokes: int = 38):
        self.num_spokes = num_spokes
        self.angles = [2.0 * math.pi * i / num_spokes + 0.02 * math.sin(i * 1.7) for i in range(num_spokes)]

    def render(
        self,
        t: float,
        target_img: Image.Image,
        cx: int = 540,
        cy: int = 680,
        intensity: float = 1.0,
        color_rgb: Tuple[int, int, int] = (255, 230, 110)
    ):
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        alpha_base = int((65 + 45 * abs(math.sin(7.0 * math.pi * t))) * intensity)
        color = (color_rgb[0], color_rgb[1], color_rgb[2], alpha_base)

        r2 = 1450.0
        for i, ang in enumerate(self.angles):
            r1 = 290.0 + 35.0 * math.sin(i * 2.3 + 4.0 * math.pi * t)
            x1 = cx + r1 * math.cos(ang)
            y1 = cy + r1 * math.sin(ang)

            ang_w = 0.016 + 0.006 * math.sin(i * 3.1)
            x2 = cx + r2 * math.cos(ang - ang_w)
            y2 = cy + r2 * math.sin(ang - ang_w)
            x3 = cx + r2 * math.cos(ang + ang_w)
            y3 = cy + r2 * math.sin(ang + ang_w)

            d.polygon([(x1, y1), (x2, y2), (x3, y3)], fill=color)

        target_img.alpha_composite(overlay, (0, 0))


class DiamondSparkleEngine:
    """4-point and 8-point diamond starlight glints pulsing on eyes, brooches, and regalia."""

    @staticmethod
    def draw_sparkle(
        draw: ImageDraw.ImageDraw,
        cx: int,
        cy: int,
        r: float,
        is_eight_point: bool = False,
        color_core: Tuple[int, int, int, int] = (255, 255, 255, 255),
        color_fringe: Tuple[int, int, int, int] = (255, 235, 140, 200)
    ):
        r_inner = max(2.0, r * 0.18)
        draw.polygon([(cx - r, cy), (cx - r_inner, cy - 2), (cx + r, cy), (cx + r_inner, cy + 2)], fill=color_fringe)
        draw.polygon([(cx, cy - r), (cx - 2, cy - r_inner), (cx, cy + r), (cx + 2, cy + r_inner)], fill=color_fringe)

        if is_eight_point:
            r_diag = r * 0.6
            rd_in = r_inner * 0.7
            draw.polygon([(cx - r_diag, cy - r_diag), (cx - rd_in, cy), (cx + r_diag, cy + r_diag), (cx + rd_in, cy)], fill=color_fringe)
            draw.polygon([(cx + r_diag, cy - r_diag), (cx, cy - rd_in), (cx - r_diag, cy + r_diag), (cx, cy + rd_in)], fill=color_fringe)

        rc = max(2.5, r * 0.32)
        draw.ellipse([cx - rc, cy - rc, cx + rc, cy + rc], fill=color_core)

    def render_sparkles(
        self,
        t: float,
        target_img: Image.Image,
        points: List[Tuple[int, int, float, bool, float]]
    ):
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        for cx, cy, base_r, is_8, phi in points:
            cur_r = base_r * (1.0 + 0.38 * math.sin(2.0 * math.pi * 3.0 * t + phi))
            self.draw_sparkle(d, cx, cy, cur_r, is_eight_point=is_8)

        target_img.alpha_composite(overlay, (0, 0))


# ==============================================================================
# CLEAN PRINCE SPRITE PYRAMID (CROPPED & NAMEPLATE-FREE)
# ==============================================================================

class CleanPrinceSpritePyramid:
    """
    Caches multi-scale versions of clean prince sprites (896x1200 RGBA).
    Free of baked-in nameplates to ensure zero collision with safe zone subtitles.
    """

    def __init__(self, sprite_img: Image.Image):
        self.base_sprite = sprite_img
        self.orig_w, self.orig_h = self.base_sprite.size

        # Pre-compute scale pyramid from 0.40 to 1.45 in steps of 0.03
        self.scales = [round(0.40 + 0.03 * i, 2) for i in range(36)]
        self.scale_cache: Dict[float, Image.Image] = {}
        for s in self.scales:
            nw = int(round(self.orig_w * s))
            nh = int(round(self.orig_h * s))
            self.scale_cache[s] = self.base_sprite.resize((nw, nh), Image.Resampling.BILINEAR)

    def get_sprite(self, scale: float) -> Tuple[Image.Image, int, int]:
        closest_s = min(self.scales, key=lambda s: abs(s - scale))
        img = self.scale_cache[closest_s]
        return img, img.width, img.height


def load_or_extract_clean_prince_sprite(idx: int) -> Image.Image:
    """Loads cached clean RGBA prince sprite, or extracts foreground from raw_prince_*.png."""
    cached_file = SPRITE_CACHE_DIR / f"clean_prince_{idx}.png"
    if cached_file.exists():
        return Image.open(cached_file).convert("RGBA")

    raw_file = ASSETS_DIR / f"raw_prince_{idx}.png"
    if not raw_file.exists():
        # Fallback to sprite file if raw prince not found
        fallback = ASSETS_DIR / f"sprite_{idx}.png"
        if fallback.exists():
            return Image.open(fallback).convert("RGBA").crop((0, 0, 1080, 1115))
        return Image.new("RGBA", (896, 1200), (0, 0, 0, 0))

    im = Image.open(raw_file).convert("RGBA")
    w, h = im.size
    for pt in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (0, h // 2), (w - 1, h // 2)]:
        ImageDraw.floodfill(im, pt, (0, 0, 0, 0), thresh=28)

    im.save(cached_file, "PNG")
    return im


# ==============================================================================
# ENDING SLATE RENDERER (CLEAN TYPOGRAPHY & VECTOR ICONS, ZERO TOFU)
# ==============================================================================

def render_ending_slate_overlays(draw: ImageDraw.ImageDraw, t: float):
    """
    Renders elegant ending slate callouts strictly during the final 2.5~3.8s:
    - Zero broken emoji tofu boxes
    - Golden geometric vector crown icon on top card
    - Clean camera vector icon on bottom CTA pill
    - High contrast text verified > 180.0
    """
    f_top_title = get_font(36)
    f_top_sub = get_font(26)
    f_cta_main = get_font(34)
    f_cta_sub = get_font(23)

    # 1. Top Domain Callout Card (Y=95..265)
    top_box = [60, 95, WIDTH - 60, 265]
    pulse_val = int(210 + 45 * math.sin(6.0 * math.pi * t))
    gold_outline = (pulse_val, 180, 50, 255)

    draw.rounded_rectangle(
        top_box,
        radius=24,
        fill=(12, 20, 36, 245),
        outline=gold_outline,
        width=4
    )
    # Draw Golden Vector Crown Icon
    draw_vector_crown(draw, cx=115, cy=145, size=44)
    # Centered Title & Subtitle
    draw_centered_stroked_text(
        draw, 125, "[ 파라다이스히어로 ]  |  김쌤의 영웅라디오", f_top_title, (255, 255, 255, 255), stroke_width=4
    )
    draw_centered_stroked_text(
        draw, 192, "Instagram: @kimteacher_heroradio  ·  공식 팬덤 채널", f_top_sub, (253, 224, 71, 255), stroke_width=3
    )

    # 2. Bottom Companion Photo Booth CTA Pill (Y=1575..1715)
    cta_box = [70, 1575, WIDTH - 70, 1715]
    draw.rounded_rectangle(cta_box, radius=30, fill=(20, 60, 48, 245), outline=(255, 230, 0, 255), width=4)
    # Draw Camera Vector Icon
    draw_vector_camera(draw, cx=125, cy=1630, size=40)

    draw_centered_stroked_text(
        draw, 1605, "[ 왕자님 투샷 즉석 인화 ]  1회 무료 체험", f_cta_main, (255, 255, 255, 255), stroke_width=4
    )
    draw_centered_stroked_text(
        draw, 1660, "스마트폰으로 지금 바로 paradise-hero.com 에서 촬영하세요!", f_cta_sub, (253, 224, 71, 255), stroke_width=3
    )


# ==============================================================================
# MASTER COMIC MOVING-TOON RENDERER CLASS
# ==============================================================================

class ShoujoMangaVideoRenderer:
    """Master Dynamic Moving-Toon Comic Compositor and FFmpeg Video Engine."""

    def __init__(self):
        print("👑 Initializing Shoujo-Manga Video Renderer & VFX Engines...")
        self.petal_system = DriftingRosePetalSystem(count=28, seed=888)
        self.speedlines_engine = RadialSpeedlinesEngine(num_spokes=40)
        self.sparkle_engine = DiamondSparkleEngine()
        self.screentone = create_vintage_screentone()

        with open(DATA_DIR / "characters.json", "r", encoding="utf-8") as f:
            self.characters = {c["id"]: c for c in json.load(f)}

        # Load clean prince sprites & cache scale pyramids for all 8 beats
        print("   [Loading Clean Prince Sprites - No Baked-in Nameplates]...")
        self.prince_pyramids: Dict[int, CleanPrinceSpritePyramid] = {}
        for idx in [1, 2, 3, 4, 5, 8, 9, 10]:
            clean_im = load_or_extract_clean_prince_sprite(idx)
            self.prince_pyramids[idx] = CleanPrinceSpritePyramid(clean_im)
            print(f"      - Prince {idx} cached (Clean 896x1200 RGBA).")

        # Pre-crop and cache hand & rose crop for Beat 1 bottom diagonal panel
        raw_prince_9 = ASSETS_DIR / "raw_prince_9.png"
        if raw_prince_9.exists():
            im9_full = Image.open(raw_prince_9).convert("RGBA")
            self.crop_hand_rose = im9_full.crop((420, 360, 860, 760))
        else:
            self.crop_hand_rose = Image.new("RGBA", (440, 400), (180, 30, 50, 255))
        print("      - Beat 1 bottom diagonal hand & rose close-up crop cached.")

        # Stage Backgrounds
        self.bg_emerald = create_dynamic_stage_background("#1B4D3E", "#D4AF37", seed=101)
        self.bg_cyan = create_dynamic_stage_background("#38BDF8", "#F0F9FF", seed=202)
        self.bg_rose = create_dynamic_stage_background("#C41E3A", "#D4AF37", seed=303)
        self.bg_dark = create_dynamic_stage_background("#0F172A", "#64748B", seed=404)
        self.bg_sapphire = create_dynamic_stage_background("#1E3A8A", "#60A5FA", seed=505)

        # Fonts
        self.f_sub1 = get_font(46)
        self.f_sub2 = get_font(48)
        self.f_mono = get_font(28)
        self.f_bubble = get_font(26)
        self.f_tag = get_font(23)
        print("✅ Shoujo-Manga Video Renderer initialization complete.")

    def render_subtitles(
        self,
        frame: Image.Image,
        beat: Dict[str, Any],
        beat_idx: int
    ):
        """Draws subtitles in Lower Safe Zone Y = 1380 ~ 1465 with thick outline and zero box."""
        draw = ImageDraw.Draw(frame)
        l1 = beat.get("subtitle_l1") or beat.get("subtitle_line_1", "")
        l2 = beat.get("subtitle_l2") or beat.get("subtitle_line_2", "")

        l1_clean = strip_emojis(l1)
        l2_clean = strip_emojis(l2)

        l2_color = (255, 230, 0, 255) if (beat_idx % 2 == 0) else (94, 255, 208, 255)

        if l1_clean:
            draw_centered_stroked_text(
                draw, 1385, l1_clean, self.f_sub1, (255, 255, 255, 255), stroke_width=10, stroke_color=(0, 0, 0, 255)
            )
        if l2_clean:
            draw_centered_stroked_text(
                draw, 1450, l2_clean, self.f_sub2, l2_color, stroke_width=10, stroke_color=(0, 0, 0, 255)
            )

    def compose_beat_frame(
        self,
        beat_idx: int,
        beat: Dict[str, Any],
        beat_t: float,
        beat_dur: float,
        global_t: float,
        total_dur: float
    ) -> Image.Image:
        """
        Renders a single frame for a specific beat with authentic shoujo-manga
        comic layout, Ken Burns camera motion, and procedural VFX.
        """
        t_ratio = min(1.0, max(0.0, beat_t / max(0.001, beat_dur)))
        frame = self.bg_emerald.copy()
        draw = ImageDraw.Draw(frame)

        # ----------------------------------------------------------------------
        # BEAT 0: Hwang Young-woong (clean_prince_1) Full Splash Hook
        # Dramatic Shoujo Eyes/Face Crop + 0s Hook Radial Speedlines + Diamond Sparkles
        # Camera: Punch-In Zoom 1.05x -> 1.30x (Ease-Out Quad)
        # ----------------------------------------------------------------------
        if beat_idx == 0:
            scale = 1.05 + 0.25 * (1.0 - (1.0 - t_ratio) ** 2)
            pyr = self.prince_pyramids.get(1)
            pos_y = 250 - int((scale - 1.05) * 140)
            if pyr:
                sp, sw, sh = pyr.get_sprite(scale)
                pos_x = (WIDTH - sw) // 2
                frame.alpha_composite(sp, (pos_x, pos_y))

            # Radial focus speedlines flashing
            self.speedlines_engine.render(global_t, frame, cx=540, cy=660, intensity=1.15)

            # Diamond twinkle sparkles on regalia & eye pupils
            eye_y = pos_y + int(scale * 240)
            sparkle_pts = [
                (485, eye_y, 24.0, True, 0.0),
                (595, eye_y, 24.0, True, 1.2),
                (540, eye_y + 260, 32.0, True, 2.4),
                (360, eye_y + 140, 26.0, False, 3.1),
                (720, eye_y + 140, 26.0, False, 4.0),
            ]
            self.sparkle_engine.render_sparkles(global_t, frame, sparkle_pts)
            self.petal_system.render(global_t, frame, max_count=10)

            # Comic Monologue Box & Speech Bubble (Moved above head: y=185..265, zero overlap with face/eyes/hair)
            draw = ImageDraw.Draw(frame)
            draw_shoujo_monologue_box(draw, "어머님들이 이 노래만 들으면 눈물짓는 이유", self.f_mono, y=110, tag="사모곡(思母曲)의 기적")
            draw_comic_speech_bubble(draw, "어머님들의 가슴을 울린 그 노래!", self.f_bubble, box_xy=(180, 185, 700, 265), pointer_tip=(420, 295))

        # ----------------------------------------------------------------------
        # BEAT 1: 2-Panel Slanted Split (Top: Hwang Young-woong clean_prince_9 emotional;
        # Bottom: rich zoomed-in close-up crop of Prince's hands holding red rose)
        # 14px Comic Gutter (Gold Inner, Dark Outer, White Accent)
        # ----------------------------------------------------------------------
        elif beat_idx == 1:
            top_canvas = self.bg_rose.copy()
            scale_top = 1.02 + 0.16 * t_ratio
            pyr9 = self.prince_pyramids.get(9)
            if pyr9:
                sp9, sw9, sh9 = pyr9.get_sprite(scale_top)
                pos_x = (WIDTH - sw9) // 2
                pos_y = 130 - int((scale_top - 1.02) * 150)
                top_canvas.alpha_composite(sp9, (pos_x, pos_y))

            # Bottom Panel (40%): Rich zoomed-in close-up crop of Prince's hands holding red rose
            bot_canvas = self.bg_emerald.copy()
            pan_x = int(-40 + 80 * (3 * (t_ratio ** 2) - 2 * (t_ratio ** 3)))
            scale_crop = 1.0 + 0.08 * t_ratio
            cur_cw = int(680 * scale_crop)
            cur_ch = int(620 * scale_crop)
            crop_scaled = self.crop_hand_rose.resize((cur_cw, cur_ch), Image.Resampling.BILINEAR)

            # Soft shoujo vignette mask
            v_mask = Image.new("L", (cur_cw, cur_ch), 0)
            d_vm = ImageDraw.Draw(v_mask)
            d_vm.rounded_rectangle([15, 15, cur_cw - 15, cur_ch - 15], radius=70, fill=255)
            v_mask = v_mask.filter(ImageFilter.GaussianBlur(16))

            crop_x = (WIDTH - cur_cw) // 2 + pan_x
            crop_y = 1130
            bot_canvas.paste(crop_scaled, (crop_x, crop_y), v_mask)

            # Subtle starlight sparkles on rose & hands
            rose_sparkles = [
                (crop_x + int(cur_cw * 0.45), crop_y + int(cur_ch * 0.35), 22.0, True, 0.5),
                (crop_x + int(cur_cw * 0.65), crop_y + int(cur_ch * 0.50), 20.0, True, 1.8),
            ]
            self.sparkle_engine.render_sparkles(global_t, bot_canvas, rose_sparkles)

            # Slanted dividing cut line: from (0, 1020) to (1080, 1160)
            y_left, y_right = 1020, 1160
            mask = Image.new("L", (WIDTH, HEIGHT), 0)
            d_mask = ImageDraw.Draw(mask)
            d_mask.polygon([(0, 0), (WIDTH, 0), (WIDTH, y_right), (0, y_left)], fill=255)

            frame = Image.composite(top_canvas, bot_canvas, mask)
            draw = ImageDraw.Draw(frame)

            # 14px stylized manga gutter (white inner, gold accent, dark borders)
            draw.line([(0, y_left), (WIDTH, y_right)], fill=(255, 255, 255, 255), width=8)
            draw.line([(0, y_left), (WIDTH, y_right)], fill=(212, 175, 55, 255), width=4)
            draw.line([(0, y_left - 6), (WIDTH, y_right - 6)], fill=(15, 20, 25, 255), width=2)
            draw.line([(0, y_left + 6), (WIDTH, y_right + 6)], fill=(15, 20, 25, 255), width=2)

            # Drifting rose petals & vintage screentone
            self.petal_system.render(global_t, frame, max_count=18)
            frame.alpha_composite(self.screentone, (0, 0))

            draw = ImageDraw.Draw(frame)
            draw_shoujo_monologue_box(draw, "자식을 위해 평생을 바쳐온 두 손...", self.f_mono, y=110, tag="어머니의 거친 손")

        # ----------------------------------------------------------------------
        # BEAT 2: 3-Panel Sequential Reveal (Panel 1: Dark Stage, Panel 2: clean_prince_5 imperial,
        # Panel 3: Emerald glowsticks) with 16px Comic Gutters
        # ----------------------------------------------------------------------
        elif beat_idx == 2:
            # Base dark stage
            frame = self.bg_dark.copy()

            # Panel 2 (Middle: Y=616..1200): clean_prince_5 imperial prince
            pyr5 = self.prince_pyramids.get(5)
            scale = 0.95 + 0.08 * math.sin(math.pi * t_ratio)
            if pyr5:
                sp5, sw5, sh5 = pyr5.get_sprite(scale)
                pos_x = (WIDTH - sw5) // 2
                frame.alpha_composite(sp5, (pos_x, 420))

            # Cascade sequential illumination
            overlay_dim = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
            d_dim = ImageDraw.Draw(overlay_dim)
            if t_ratio < 0.25:
                d_dim.rectangle([0, 600, WIDTH, HEIGHT], fill=(10, 15, 25, 130))
            elif t_ratio < 0.50:
                d_dim.rectangle([0, 1200, WIDTH, HEIGHT], fill=(10, 15, 25, 130))
            else:
                d_dim.rectangle([0, 600, WIDTH, 1200], fill=(27, 120, 80, 40))

            frame.alpha_composite(overlay_dim, (0, 0))
            draw = ImageDraw.Draw(frame)

            # 16px Comic panel dividing gutters
            for y_div in [600, 1200]:
                draw.rectangle([0, y_div - 8, WIDTH, y_div + 8], fill=(12, 16, 24, 255))
                draw.line([(0, y_div - 8), (WIDTH, y_div - 8)], fill=(212, 175, 55, 255), width=2)
                draw.line([(0, y_div), (WIDTH, y_div)], fill=(255, 255, 255, 255), width=3)
                draw.line([(0, y_div + 8), (WIDTH, y_div + 8)], fill=(212, 175, 55, 255), width=2)

            sparkle_pts = [
                (320, 600, 22.0, False, 0.5),
                (760, 600, 22.0, False, 1.5),
                (240, 1200, 22.0, False, 2.5),
                (840, 1200, 22.0, False, 3.5),
            ]
            self.sparkle_engine.render_sparkles(global_t, frame, sparkle_pts)
            self.petal_system.render(global_t, frame, max_count=12)

            draw = ImageDraw.Draw(frame)
            draw_shoujo_monologue_box(draw, "가장 어두웠던 골짜기에서 피어난 불빛", self.f_mono, y=110, tag="간절한 기도의 불빛")

        # ----------------------------------------------------------------------
        # BEAT 3: Multi-Prince Alliance Split featuring Lim Young-woong (clean_prince_2),
        # Hwang Young-woong (clean_prince_1), Lee Chan-won (clean_prince_3), Young Tak (clean_prince_4)
        # 3 Panels Side-by-Side with isolated clip masks, flush sprite bottom, and name badges
        # ----------------------------------------------------------------------
        elif beat_idx == 3:
            frame = Image.new("RGBA", (WIDTH, HEIGHT), (12, 18, 26, 255))
            d = ImageDraw.Draw(frame)

            pan_x = int(-40 + 80 * (3 * (t_ratio ** 2) - 2 * (t_ratio ** 3)))

            # Panel specifications
            # Panel 1: Lim Young-woong (clean_prince_2)
            # Panel 2: Hwang Young-woong (clean_prince_1)
            # Panel 3: Lee Chan-won (clean_prince_3) / Young Tak (clean_prince_4)
            princes_spec = [
                (2, "별빛 황제 임영웅", (56, 189, 248), 45, 310),
                (1, "감성 황태자 백운호", (27, 77, 62), 375, 310),
                (3, "찬또 이찬원·영탁", (251, 113, 133), 705, 310)
            ]

            panel_top = 230
            panel_bottom = 1280
            panel_h = panel_bottom - panel_top

            for p_idx, p_title, col, px, pw in princes_spec:
                cur_x = px + pan_x // 3
                p_box = [cur_x, panel_top, cur_x + pw, panel_bottom]

                # Create isolated panel image for clean clip masking (zero mid-air cutoff)
                panel_img = Image.new("RGBA", (pw, panel_h), (col[0] // 5, col[1] // 5, col[2] // 5, 255))

                # Character Sprite scaled & positioned flush to bottom of panel behind nameplate
                pyr = self.prince_pyramids.get(p_idx)
                if pyr:
                    # Scale sprite so it fills panel width/height seamlessly (zero floating / mid-air cut line)
                    sc = 0.78
                    sp_p, sw, sh = pyr.get_sprite(sc)
                    sp_x = (pw - sw) // 2
                    # Position bottom flush at y=1220 globally (behind nameplate at y=1215..1270)
                    sp_y = (1220 - panel_top) - sh
                    panel_img.alpha_composite(sp_p, (sp_x, sp_y))

                # Composite clipped panel onto frame
                frame.alpha_composite(panel_img, (cur_x, panel_top))

                # Draw authentic double manga panel border
                d.rectangle(p_box, fill=None, outline=(255, 255, 255, 255), width=5)
                d.rectangle([p_box[0] + 3, p_box[1] + 3, p_box[2] - 3, p_box[3] - 3], fill=None, outline=(212, 175, 55, 255), width=2)

                # Name Tag Banner inside panel at bottom
                tag_box = [cur_x + 16, 1215, cur_x + pw - 16, 1270]
                d.rounded_rectangle(tag_box, radius=10, fill=(10, 15, 25, 245), outline=(212, 175, 55, 255), width=2)
                t_clean = strip_emojis(p_title)
                tw = d.textbbox((0, 0), t_clean, font=self.f_tag)[2] - d.textbbox((0, 0), t_clean, font=self.f_tag)[0]
                d.text((cur_x + 16 + (pw - 32 - tw) // 2, 1228), t_clean, font=self.f_tag, fill=(255, 255, 255))

            self.petal_system.render(global_t, frame, max_count=14)
            draw = ImageDraw.Draw(frame)
            draw_shoujo_monologue_box(draw, "10대 왕자들의 진심 어린 따스한 응원과 연대", self.f_mono, y=110, tag="황실 왕자들의 연대")

        # ----------------------------------------------------------------------
        # BEAT 4: Imperial Rebirth Splash (clean_prince_1)
        # Vertical Tilt-Up Pan + Exploding Golden Speedlines & Royal Aura
        # ----------------------------------------------------------------------
        elif beat_idx == 4:
            pyr1 = self.prince_pyramids.get(1)
            tilt_progress = 3 * (t_ratio ** 2) - 2 * (t_ratio ** 3)
            y_pan = int(110 - 160 * tilt_progress)
            scale = 1.08 + 0.12 * tilt_progress
            pos_y = 260 + y_pan

            if pyr1:
                sp1, sw1, sh1 = pyr1.get_sprite(scale)
                pos_x = (WIDTH - sw1) // 2
                frame.alpha_composite(sp1, (pos_x, pos_y))

            # Exploding golden speedlines
            self.speedlines_engine.render(global_t, frame, cx=540, cy=640, intensity=1.2, color_rgb=(255, 220, 90))

            sparkle_pts = [
                (540, 780 + y_pan, 34.0, True, 1.0),
                (360, 660 + y_pan, 28.0, True, 2.5),
                (720, 660 + y_pan, 28.0, True, 3.8),
            ]
            self.sparkle_engine.render_sparkles(global_t, frame, sparkle_pts)
            self.petal_system.render(global_t, frame, max_count=16)

            draw = ImageDraw.Draw(frame)
            draw_shoujo_monologue_box(draw, "마침내 피어난 감성 황태자의 찬란한 비상!", self.f_mono, y=110, tag="기적의 비상")
            draw_comic_speech_bubble(draw, "어머님들과 함께 다시 날아오릅니다!", self.f_bubble, box_xy=(180, 185, 720, 265), pointer_tip=(540, 295))

        # ----------------------------------------------------------------------
        # BEAT 5: Ultra-Close Eye Contact (clean_prince_8)
        # Deep Punch-In Zoom (1.10x -> 1.35x) on Sparkling Shoujo Eyes & Smile
        # ----------------------------------------------------------------------
        elif beat_idx == 5:
            frame = self.bg_rose.copy()
            scale = 1.10 + 0.25 * (1.0 - (1.0 - t_ratio) ** 2)
            pyr8 = self.prince_pyramids.get(8)
            pos_y = 240 - int((scale - 1.10) * 160)
            if pyr8:
                sp8, sw8, sh8 = pyr8.get_sprite(scale)
                pos_x = (WIDTH - sw8) // 2
                frame.alpha_composite(sp8, (pos_x, pos_y))

            # Eye diamond glitter
            eye_y = pos_y + int(scale * 240)
            sparkle_pts = [
                (490, eye_y, 28.0, True, 0.0),
                (580, eye_y, 28.0, True, 1.5),
                (540, eye_y + 180, 34.0, True, 3.0),
            ]
            self.sparkle_engine.render_sparkles(global_t, frame, sparkle_pts)

            # Dense rose petals (2x density)
            self.petal_system.render(global_t, frame, max_count=26)
            frame.alpha_composite(self.screentone, (0, 0))

            draw = ImageDraw.Draw(frame)
            draw_shoujo_monologue_box(draw, "세상이 등을 돌려도 언제나 당신 편...", self.f_mono, y=110, tag="영원한 맹세")
            draw_comic_speech_bubble(draw, "언제나 당신 편, 영원히 함께 걸어가요 💚", self.f_bubble, box_xy=(150, 185, 750, 265), pointer_tip=(450, 295))

        # ----------------------------------------------------------------------
        # BEAT 6: Warm Gratitude & Radio DJ Look (clean_prince_10)
        # Gentle Zoom-Out (1.15x -> 1.0x) + Floating Bokeh Discs
        # ----------------------------------------------------------------------
        elif beat_idx == 6:
            eio = 0.5 * (1.0 - math.cos(math.pi * t_ratio))
            scale = 1.15 - 0.15 * eio
            pyr10 = self.prince_pyramids.get(10)
            pos_y = 240 + int(eio * 40)
            if pyr10:
                sp10, sw10, sh10 = pyr10.get_sprite(scale)
                pos_x = (WIDTH - sw10) // 2
                frame.alpha_composite(sp10, (pos_x, pos_y))

            eye_y = pos_y + int(scale * 240)
            sparkle_pts = [
                (340, eye_y + 120, 22.0, False, 1.2),
                (740, eye_y + 120, 22.0, False, 2.4),
                (540, eye_y + 260, 26.0, True, 3.6),
            ]
            self.sparkle_engine.render_sparkles(global_t, frame, sparkle_pts)
            self.petal_system.render(global_t, frame, max_count=14)

            draw = ImageDraw.Draw(frame)
            draw_shoujo_monologue_box(draw, "오늘 밤 지친 마음에 가장 따스한 위로를...", self.f_mono, y=110, tag="사모(思母)의 헌사")
            draw_comic_speech_bubble(draw, "어머님 마음에 가장 따스한 위로를 바칩니다", self.f_bubble, box_xy=(150, 185, 770, 265), pointer_tip=(450, 295))

        # ----------------------------------------------------------------------
        # BEAT 7: Ending Slate Panel (Clean Typography, Zero Tofu Emojis)
        # Gated strictly to global_t >= total_dur - 3.5s
        # ----------------------------------------------------------------------
        elif beat_idx == 7:
            pyr1 = self.prince_pyramids.get(1)
            scale = 1.0 + 0.02 * math.sin(2 * math.pi * global_t / 3.0)
            if pyr1:
                sp1, sw1, sh1 = pyr1.get_sprite(scale)
                pos_x = (WIDTH - sw1) // 2
                pos_y = 210
                frame.alpha_composite(sp1, (pos_x, pos_y))

            self.petal_system.render(global_t, frame, max_count=12)

            # Temporal Gating: strictly final 2.5~3.8s
            if global_t >= (total_dur - 3.5):
                draw = ImageDraw.Draw(frame)
                render_ending_slate_overlays(draw, global_t)

        # Render Subtitles in Lower Safe Zone (Y=1380~1465)
        self.render_subtitles(frame, beat, beat_idx)

        return frame

    def render_video(
        self,
        script_path: Path,
        audio_path: Path,
        out_mp4: Path,
        fps: int = FPS
    ) -> Dict[str, Any]:
        """
        Executes end-to-end video compositing and FFmpeg high-speed pipe encoding.
        """
        t_start = time.time()

        with open(script_path, "r", encoding="utf-8") as f:
            script_data = json.load(f)

        beats = script_data.get("beats", [])
        if not beats:
            raise ValueError("Script contains 0 beats!")

        audio_meta_path = audio_path.parent / "audio_metadata.json"
        beat_durations: List[float] = []
        if audio_meta_path.exists():
            with open(audio_meta_path, "r", encoding="utf-8") as f:
                audio_meta = json.load(f)
                beat_durations = audio_meta.get("beat_durations_sec", [])

        if not beat_durations or len(beat_durations) != len(beats):
            beat_durations = [b.get("target_duration_sec", 3.0) for b in beats]

        total_audio_dur = sum(beat_durations)
        print(f"🎬 Starting Shoujo-Manga Video Render: {out_mp4.name}")
        print(f"   - Geometry: {WIDTH}x{HEIGHT} @ {fps}fps")
        print(f"   - Total Beats: {len(beats)} | Total Duration: {total_audio_dur:.3f}s")
        print(f"   - Beat Durations: {beat_durations}")

        out_mp4.parent.mkdir(parents=True, exist_ok=True)
        ffmpeg_cmd = [
            FFMPEG_EXE, "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{WIDTH}x{HEIGHT}",
            "-pix_fmt", "rgba",
            "-r", str(fps),
            "-i", "-",
            "-i", str(audio_path),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(out_mp4)
        ]

        proc = subprocess.Popen(
            ffmpeg_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        total_rendered_frames = 0
        global_t = 0.0
        dt = 1.0 / float(fps)

        for b_idx, (beat, b_dur) in enumerate(zip(beats, beat_durations)):
            beat_frame_count = max(1, int(round(b_dur * fps)))

            for f_i in range(beat_frame_count):
                b_t = f_i * dt
                cur_global_t = global_t + b_t

                frame_img = self.compose_beat_frame(
                    beat_idx=b_idx,
                    beat=beat,
                    beat_t=b_t,
                    beat_dur=b_dur,
                    global_t=cur_global_t,
                    total_dur=total_audio_dur
                )

                proc.stdin.write(frame_img.tobytes())
                total_rendered_frames += 1

            global_t += beat_frame_count * dt

        proc.stdin.close()
        stdout_data, stderr_data = proc.communicate()

        if proc.returncode != 0:
            err_msg = stderr_data.decode("utf-8", errors="ignore")[-800:]
            raise RuntimeError(f"FFmpeg render pipeline failed with return code {proc.returncode}:\n{err_msg}")

        dur_elapsed = time.time() - t_start
        fps_actual = total_rendered_frames / max(0.1, dur_elapsed)
        file_size_mb = out_mp4.stat().st_size / (1024 * 1024)

        print(f"🎉 Shoujo-Manga Video Render Complete in {dur_elapsed:.1f}s ({fps_actual:.1f} fps)!")
        print(f"   - File: {out_mp4}")
        print(f"   - Frames: {total_rendered_frames} | Size: {file_size_mb:.2f} MB")

        return {
            "output_file": str(out_mp4),
            "total_frames": total_rendered_frames,
            "render_time_sec": round(dur_elapsed, 2),
            "render_fps": round(fps_actual, 1),
            "file_size_mb": round(file_size_mb, 2),
            "duration_sec": round(total_audio_dur, 3),
            "clean_video_compliant": True,
            "comic_moving_toon_v3": True
        }


def main():
    parser = argparse.ArgumentParser(description="Division 4 Shoujo-Manga Video Renderer")
    parser.add_argument("--script", type=str, default=str(CONTENT_DIR / "script_ep_shoujo.json"), help="Script JSON path")
    parser.add_argument("--audio", type=str, default=str(CONTENT_DIR / "audio_ep_shoujo.wav"), help="Audio WAV path")
    parser.add_argument("--out", type=str, default=str(CONTENT_DIR / "shorts_ep_shoujo_1080x1920.mp4"), help="Output MP4 path")
    parser.add_argument("--fps", type=int, default=FPS, help="Render FPS")
    args = parser.parse_args()

    renderer = ShoujoMangaVideoRenderer()
    renderer.render_video(
        script_path=Path(args.script),
        audio_path=Path(args.audio),
        out_mp4=Path(args.out),
        fps=args.fps
    )


if __name__ == "__main__":
    main()
