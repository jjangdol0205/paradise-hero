#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_radio_video.py
@김쌤의영웅라디오 16:9 1080p Long-Form Video Assembly & Master MP4 Renderer

Specifications:
- Resolution: 1920x1080 (16:9 Landscape)
- Senior Subtitle Spec: 52~56pt font (default 54pt), #FFFFFF & #FFE600 with 8px dark outline, Y=845~925
- 100% Full Subtitle Reading & Natural Voice Pacing (Common Directive #3)
- Warm Acoustic/Piano BGM Bed with Auto-Ducking (-20 dBFS during speech, -13 dBFS during bridges)
- Produces both:
  1) visuals/ch1~ch6_scene_1080p.png (6 chapter background cards)
  2) episode_XX_master.mp4 (Full 16:9 1080p Long-Form Radio Broadcast MP4)
"""

import os
import re
import sys
import math
import wave
import json
import time
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple
import numpy as np

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = None
    ImageDraw = None
    ImageFont = None

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = "ffmpeg"

SAMPLE_RATE = 44100

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\malgunbd.ttf",
    r"C:\Windows\Fonts\malgun.ttf",
    r"C:\Windows\Fonts\gulim.ttc",
    r"D:\드림컴퍼니\3사업부\src\fonts\Pretendard-Black.otf"
]


def get_font(size: int) -> ImageFont.FreeTypeFont:
    for fp in FONT_CANDIDATES:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()


VIDEO_SPECS = {
    "width": 1920,
    "height": 1080,
    "aspect_ratio": "16:9",
    "framerate": 30,
    "video_codec": "libx264",
    "video_profile": "high",
    "crf": 22,
    "preset": "ultrafast",
    "audio_codec": "aac",
    "audio_bitrate": "192k",
    "audio_samplerate": SAMPLE_RATE,
    "ken_burns": {
        "cycle_duration_sec": 30.0,
        "zoom_start": 1.00,
        "zoom_end": 1.05,
        "ffmpeg_zoompan_filter": "zoompan=z='min(zoom+0.00008,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=900:s=1920x1080:fps=30"
    },
    "subtitles": {
        "font_family": "Malgun Gothic Bold / NanumSquareRoundEB",
        "font_size_pt": 54,
        "font_size_range": "52~56pt",
        "text_color": "#FFFFFF",
        "highlight_color": "#FFE600",
        "outline_color": "#1A1A1A",
        "outline_width_px": 8,
        "vertical_align_y": 910,
        "safe_margin_bottom_px": 170,
        "max_lines_per_cue": 2,
        "max_chars_per_line": 25
    }
}

SCENE_PROMPTS = [
    {
        "chapter_index": 1,
        "chapter_id": "ch1_opening",
        "title": "오프닝 — 파라다이스 어머님들, 저녁 진지 드셨습니까?",
        "art_prompt": (
            "Cinematic 16:9 wide shot, cozy retro Korean radio studio at late autumn twilight. "
            "Warm golden sunset streaming through large wooden window pane, vintage broadcast tube microphone on mahogany desk, "
            "steaming porcelain teacup emitting gentle vapor, glowing amber dials of analog radio. "
            "Soft depth of field, warm cozy nostalgic atmosphere, 8k resolution, cinematic lighting --ar 16:9"
        ),
        "visual_elements": ["원목 스튜디오", "노을빛 창가", "진공관 마이크", "따뜻한 도자기 찻잔"],
        "color_palette": ["#2C1A14", "#E89B53", "#F5E3C8", "#4A6B5B"]
    },
    {
        "chapter_index": 2,
        "chapter_id": "ch2_hero_story",
        "title": "영웅 이야기 — 모진 비바람을 견뎌낸 그 깊은 목소리의 비밀",
        "art_prompt": (
            "Cinematic 16:9 landscape, majestic concert hall stage silhouette. "
            "Solo singer silhouette holding a retro acoustic guitar in center spotlight, beams of soft emerald and gold lights cutting through subtle atmospheric haze. "
            "Far background showing ocean of glowing emerald green cheering lights from loving audience. "
            "Profound emotional resonance, inspiring and solemn aura, ultra high quality, 35mm lens --ar 16:9"
        ),
        "visual_elements": ["콘서트 무대 실루엣", "에메랄드/골드 조명", "어쿠스틱 기타", "객석 응원 불빛"],
        "color_palette": ["#0E2A1E", "#27AE60", "#F1C40F", "#1A1A1A"]
    },
    {
        "chapter_index": 3,
        "chapter_id": "ch3_song_commentary",
        "title": "명곡 해설 — '내가 그대 편이 되겠소', [당신 편] 가사 속 눈물의 약속",
        "art_prompt": (
            "Cinematic 16:9 close-up view, vintage turntable vinyl record spinning slowly on dark oak table. "
            "A single golden maple leaf resting beside the vinyl sleeve with elegant Korean calligraphy title '당신 편'. "
            "Soft warm ambient desk lamp, gentle analog audio wave reflections in background, peaceful poetic melancholia --ar 16:9"
        ),
        "visual_elements": ["회전하는 LP 턴테이블", "단풍잎 한 잎", "감성 캘리그라피 [당신 편]", "은은한 스탠드 조명"],
        "color_palette": ["#1F1610", "#D35400", "#F39C12", "#E5DCC5"]
    },
    {
        "chapter_index": 4,
        "chapter_id": "ch4_fan_letter",
        "title": "파라다이스 사연 우체통 — 대구 이순자 어머님의 눈물겨운 사연 낭독",
        "art_prompt": (
            "Cinematic 16:9 still life, heartfelt handwritten letter on traditional Korean Hanji paper lying on wooden desk. "
            "Reading glasses folded neatly next to the letter, single flickering candle in brass holder casting dancing warm shadows. "
            "Quiet rainy autumn window in soft background, deeply touching, tender, tearful yet healing mood --ar 16:9"
        ),
        "visual_elements": ["정성스런 한지 손편지", "돋보기안경", "은은한 촛불", "비 내리는 밤 창가"],
        "color_palette": ["#1A1412", "#C0392B", "#F39C12", "#BDC3C7"]
    },
    {
        "chapter_index": 5,
        "chapter_id": "ch5_fandom_cheer",
        "title": "영웅 응원석 — 파라다이스 가족들이 함께 만드는 황금빛 기적",
        "art_prompt": (
            "Cinematic 16:9 panoramic view, thousands of glowing emerald-green and gold cheering light sticks waving in unison under a clear starry night sky. "
            "Dawn horizon breaking with hopeful golden sunlight over distant mountain ridge, sense of profound unity, triumphant solidarity and benevolence --ar 16:9"
        ),
        "visual_elements": ["에메랄드빛 응원봉 물결", "별빛 밤하늘", "새벽 여명과 황금빛 능선", "선한 연대의 온기"],
        "color_palette": ["#0B3B24", "#2ECC71", "#F1C40F", "#34495E"]
    },
    {
        "chapter_index": 6,
        "chapter_id": "ch6_closing_cta",
        "title": "클로징 — 편안한 밤 되세요 & 공식 사랑방 사연 안내",
        "art_prompt": (
            "Cinematic 16:9 wide landscape, serene night sky filled with gentle glowing stars and warm crescent moon over a peaceful sleeping countryside town. "
            "A warm yellow light softly glowing from a single rooftop window, quiet lullaby atmosphere, peaceful rest and healing sleep --ar 16:9"
        ),
        "visual_elements": ["초승달과 별빛 밤하늘", "고요한 마을의 따뜻한 창문 불빛", "평화로운 자장가 무드", "공식 로고 오버레이"],
        "color_palette": ["#0A192F", "#1B2A4A", "#F7D070", "#E0E6ED"]
    }
]


def split_korean_text_into_cues(text: str, max_chars_per_line: int = 24) -> List[Tuple[str, str]]:
    """
    Splits a multi-sentence Korean radio narration segment into clean 2-line subtitle cues
    so that each cue fits comfortably at 54pt senior-friendly font size and 100% of the text is shown.
    """
    raw_sentences = re.split(r"(?<=[.?!])\s+", text.strip())
    cues: List[Tuple[str, str]] = []

    for sent in raw_sentences:
        sent = sent.strip()
        if not sent:
            continue
        words = sent.split()
        lines: List[str] = []
        cur = ""
        for w in words:
            cand = f"{cur} {w}".strip() if cur else w
            if len(cand) <= max_chars_per_line:
                cur = cand
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)

        # Group lines into pairs (l1, l2)
        for k in range(0, len(lines), 2):
            l1 = lines[k]
            l2 = lines[k + 1] if (k + 1) < len(lines) else ""
            cues.append((l1, l2))

    if not cues:
        cues.append((text[:max_chars_per_line], text[max_chars_per_line:max_chars_per_line * 2]))
    return cues


def build_video_assembly_plan(script_data: Dict[str, Any], narration_data: Dict[str, Any] = None) -> Dict[str, Any]:
    chapters = script_data.get("chapters", [])
    chapters_plan = []
    cumulative_time = 0.0

    for i, ch in enumerate(chapters):
        ch_idx = ch["chapter_index"]
        scene_info = SCENE_PROMPTS[i] if i < len(SCENE_PROMPTS) else SCENE_PROMPTS[-1]
        ch_duration = ch.get("total_estimated_sec", 150.0) + 12.0
        start_time = round(cumulative_time, 2)
        end_time = round(cumulative_time + ch_duration, 2)

        subtitle_cues = []
        for seg in ch["segments"]:
            cue = {
                "segment_id": seg["segment_id"],
                "speaker": seg["speaker"],
                "speaker_display": "🎙️ [DJ 김쌤]" if seg["speaker"] == "dj_kim" else "💌 [사연 낭독]",
                "text": seg["text"],
                "estimated_duration_sec": seg.get("estimated_duration_sec", 15.0),
                "style": {
                    "font_size_pt": VIDEO_SPECS["subtitles"]["font_size_pt"],
                    "color": VIDEO_SPECS["subtitles"]["text_color"],
                    "outline_color": VIDEO_SPECS["subtitles"]["outline_color"],
                    "outline_width": VIDEO_SPECS["subtitles"]["outline_width_px"],
                    "y_position": VIDEO_SPECS["subtitles"]["vertical_align_y"]
                }
            }
            subtitle_cues.append(cue)

        chapter_plan_entry = {
            "chapter_index": ch_idx,
            "chapter_id": ch["chapter_id"],
            "title": ch["title"],
            "timeline_start_sec": start_time,
            "timeline_end_sec": end_time,
            "duration_sec": round(ch_duration, 2),
            "visual_asset_file": f"visuals/ch{ch_idx}_scene_1080p.png",
            "art_prompt": scene_info["art_prompt"],
            "visual_elements": scene_info["visual_elements"],
            "color_palette": scene_info["color_palette"],
            "ken_burns_motion": {
                "duration_sec": round(ch_duration, 2),
                "zoom_ratio": "1.00x -> 1.05x",
                "pan_direction": "slow center-bottom to center-top drift",
                "ffmpeg_filter": VIDEO_SPECS["ken_burns"]["ffmpeg_zoompan_filter"]
            },
            "subtitles_count": len(subtitle_cues),
            "subtitles": subtitle_cues
        }
        chapters_plan.append(chapter_plan_entry)
        cumulative_time = end_time

    total_duration = round(cumulative_time, 2)
    return {
        "channel_name": script_data.get("channel_name", "@김쌤의영웅라디오"),
        "episode_number": script_data.get("episode_number", 1),
        "episode_title": script_data.get("episode_title", ""),
        "total_chapters": len(chapters_plan),
        "total_video_duration_sec": total_duration,
        "aspect_ratio": VIDEO_SPECS["aspect_ratio"],
        "resolution": f"{VIDEO_SPECS['width']}x{VIDEO_SPECS['height']}",
        "video_specifications": VIDEO_SPECS,
        "chapters": chapters_plan
    }


def create_studio_chapter_base(
    ch_idx: int,
    ch_title: str,
    visual_elements: List[str],
    sprite_path: Path
) -> Image.Image:
    """
    Renders a rich 1920x1080 Senior Broadcast Studio background canvas for a chapter.
    """
    palettes = [
        ((38, 22, 16), (232, 155, 83), (255, 236, 209)),   # Ch1: Warm twilight radio studio
        ((12, 42, 30), (46, 204, 113), (255, 225, 105)),   # Ch2: Emerald stage spotlight
        ((32, 20, 14), (230, 126, 34), (245, 230, 205)),   # Ch3: Vintage LP turntable
        ((28, 18, 22), (231, 76, 60), (255, 218, 121)),    # Ch4: Hanji fan letter & candle
        ((10, 48, 34), (39, 174, 96), (255, 230, 80)),     # Ch5: Fandom emerald wave
        ((10, 24, 46), (84, 153, 199), (255, 230, 128))    # Ch6: Serene starry night
    ]
    bg_rgb, accent_rgb, title_rgb = palettes[(ch_idx - 1) % len(palettes)]

    W, H = 1920, 1080
    y = np.linspace(0, 1, H)[:, None]
    x = np.linspace(0, 1, W)[None, :]
    dx = (x - 0.62) * 1.1
    dy = (y - 0.42) * 1.3
    spot = np.clip(1.0 - np.sqrt(dx ** 2 + dy ** 2), 0.0, 1.0) ** 1.6

    r = np.clip(10 + bg_rgb[0] * (1.0 - y * 0.45) + spot * accent_rgb[0] * 0.32, 0, 255)
    g = np.clip(12 + bg_rgb[1] * (1.0 - y * 0.45) + spot * accent_rgb[1] * 0.32, 0, 255)
    b = np.clip(18 + bg_rgb[2] * (1.0 - y * 0.45) + spot * accent_rgb[2] * 0.32, 0, 255)
    arr = np.stack([r, g, b], axis=-1).astype(np.uint8)
    canvas = Image.fromarray(arr, "RGB").convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    # Golden bokeh particles
    rng = np.random.default_rng(1000 + ch_idx * 77)
    for _ in range(28):
        bx = int(rng.uniform(80, W - 80))
        by = int(rng.uniform(60, H - 280))
        br = int(rng.uniform(14, 64))
        alpha = int(rng.uniform(20, 65))
        draw.ellipse(
            [bx - br, by - br, bx + br, by + br],
            fill=(min(255, accent_rgb[0] + 40), min(255, accent_rgb[1] + 40), min(255, accent_rgb[2] + 40), alpha)
        )

    # Outer gold studio frame
    draw.rounded_rectangle([28, 24, W - 28, H - 24], radius=24, outline=(212, 175, 55, 220), width=4)

    # Left Portrait Card (Hwang Young-woong Prince Portrait)
    portrait_box = [64, 64, 520, 760]
    draw.rounded_rectangle(portrait_box, radius=26, fill=(14, 24, 22, 230), outline=(212, 175, 55, 255), width=4)
    if sprite_path and sprite_path.exists():
        try:
            sp = Image.open(sprite_path).convert("RGBA")
            sp_resized = sp.resize((440, 586), Image.Resampling.LANCZOS)
            canvas.alpha_composite(sp_resized, (72, 80))
        except Exception:
            pass

    f_badge = get_font(26)
    f_ch = get_font(30)
    f_title = get_font(40)
    f_meta = get_font(28)

    # Portrait caption
    draw.rounded_rectangle([84, 675, 500, 742], radius=14, fill=(22, 58, 44, 245), outline=(255, 215, 0, 220), width=2)
    draw.text((112, 692), "👑 감성 황태자 황영웅 — [당신 편]", font=f_badge, fill=(255, 240, 150, 255))

    # Right Studio Header Panel
    draw.rounded_rectangle([556, 64, 1856, 205], radius=22, fill=(16, 22, 34, 225), outline=accent_rgb + (240,), width=3)
    draw.rounded_rectangle([580, 86, 835, 134], radius=12, fill=accent_rgb + (255,))
    draw.text((602, 94), f"CHAPTER 0{ch_idx}", font=f_badge, fill=(15, 15, 15, 255))
    draw.text((855, 92), "@김쌤의영웅라디오  |  공식 사랑방: paradise-hero.com", font=f_badge, fill=(255, 230, 120, 255))
    draw.text((582, 146), ch_title, font=f_title, fill=title_rgb + (255,))

    # Right Studio Main Storyboard Card
    draw.rounded_rectangle([556, 228, 1856, 760], radius=24, fill=(14, 18, 28, 215), outline=(90, 105, 130, 190), width=2)
    draw.text((595, 260), "🎵 오늘의 힐링 라디오 사연 & 명곡 해설", font=f_ch, fill=(255, 220, 110, 255))
    draw.text((595, 315), "• 사연 주인공: 대구 달서구 이순자 어머니의 눈물과 위로의 편지", font=f_meta, fill=(235, 240, 245, 255))
    draw.text((595, 362), "• 주제곡 해설: 황영웅 정규 1집 타이틀곡 [당신 편] ('내가 그대 편이 되겠소')", font=f_meta, fill=(235, 240, 245, 255))
    draw.text((595, 409), f"• 스튜디오 무드: {', '.join(visual_elements)}", font=f_meta, fill=(180, 235, 200, 255))

    return canvas


def generate_sample_scene_cards(plan: Dict[str, Any], output_dir: str):
    if Image is None or ImageDraw is None:
        return
    visuals_dir = os.path.join(output_dir, "visuals")
    os.makedirs(visuals_dir, exist_ok=True)
    sprite_path = Path(output_dir).resolve().parent.parent / "assets" / "characters" / "sprite_hwang_young_woong.png"

    for ch in plan["chapters"]:
        idx = ch["chapter_index"]
        base_img = create_studio_chapter_base(idx, ch["title"], ch["visual_elements"], sprite_path)
        draw = ImageDraw.Draw(base_img)
        f_sub = get_font(48)
        draw.rounded_rectangle([64, 795, 1856, 1025], radius=24, fill=(8, 12, 20, 235), outline=(212, 175, 55, 255), width=4)
        sample_sub = f"어머님, 오늘 하루도 참 고생 많으셨습니다 — Chapter 0{idx}"
        bbox = draw.textbbox((0, 0), sample_sub, font=f_sub)
        tw = bbox[2] - bbox[0]
        draw.text(((1920 - tw) // 2, 885), sample_sub, font=f_sub, fill=(255, 230, 0, 255), stroke_width=8, stroke_fill=(0, 0, 0, 255))

        card_filename = f"ch{idx}_scene_1080p.png"
        card_path = os.path.join(visuals_dir, card_filename)
        base_img.convert("RGB").save(card_path, "PNG")
        print(f"    - Rendered 1080p chapter card: {card_filename} ({os.path.getsize(card_path)} bytes)")


def render_cue_slide(
    chapter_base: Image.Image,
    speaker_label: str,
    speaker_is_fan: bool,
    cue_l1: str,
    cue_l2: str,
    is_closing_chapter: bool
) -> Image.Image:
    """
    Renders a single 1920x1080 broadcast frame with speaker indicator and 54pt senior-friendly subtitles.
    """
    frame = chapter_base.copy()
    draw = ImageDraw.Draw(frame)

    f_speaker = get_font(34)
    f_quote = get_font(36)
    f_sub1 = get_font(52)
    f_sub2 = get_font(54)

    # Speaker active badge inside right studio box (Y=485..565)
    sp_bg = (145, 45, 55, 245) if speaker_is_fan else (22, 85, 62, 245)
    draw.rounded_rectangle([595, 480, 1280, 552], radius=18, fill=sp_bg, outline=(255, 230, 120, 255), width=3)
    draw.text((622, 497), speaker_label, font=f_speaker, fill=(255, 255, 255, 255))

    # Warm lyric/cta highlight banner inside studio card (Y=585..725)
    if is_closing_chapter:
        draw.rounded_rectangle([595, 580, 1815, 725], radius=18, fill=(25, 42, 68, 240), outline=(255, 215, 0, 255), width=3)
        draw.text((630, 602), "👑 파라다이스히어로 공식 사랑방: https://paradise-hero.com", font=f_quote, fill=(255, 235, 100, 255))
        draw.text((630, 658), "📸 사연 접수 및 왕자님 2샷 포토부스 1회 무료 체험 진행 중!", font=f_speaker, fill=(255, 255, 255, 255))
    else:
        draw.rounded_rectangle([595, 580, 1815, 725], radius=18, fill=(22, 28, 40, 230), outline=(120, 140, 165, 200), width=2)
        draw.text((630, 605), "“세상 모든 사람이 등을 돌려도, 나 하나만큼은 끝까지 당신 편이 되어드리겠습니다.”", font=f_speaker, fill=(255, 235, 165, 255))
        draw.text((630, 662), "— 황영웅 [당신 편] 명곡 해설 & 파라다이스 사연 우체통", font=get_font(28), fill=(200, 220, 210, 255))

    # Bottom Senior Subtitle Safe Box (Y=795..1025)
    draw.rounded_rectangle([64, 795, 1856, 1025], radius=24, fill=(8, 12, 20, 238), outline=(212, 175, 55, 255), width=4)

    if cue_l1 and cue_l2:
        bbox1 = draw.textbbox((0, 0), cue_l1, font=f_sub1)
        tw1 = bbox1[2] - bbox1[0]
        draw.text(
            ((1920 - tw1) // 2, 832),
            cue_l1,
            font=f_sub1,
            fill=(255, 255, 255, 255),
            stroke_width=8,
            stroke_fill=(0, 0, 0, 255)
        )
        bbox2 = draw.textbbox((0, 0), cue_l2, font=f_sub2)
        tw2 = bbox2[2] - bbox2[0]
        draw.text(
            ((1920 - tw2) // 2, 918),
            cue_l2,
            font=f_sub2,
            fill=(255, 230, 0, 255),
            stroke_width=8,
            stroke_fill=(0, 0, 0, 255)
        )
    elif cue_l1:
        bbox1 = draw.textbbox((0, 0), cue_l1, font=f_sub2)
        tw1 = bbox1[2] - bbox1[0]
        draw.text(
            ((1920 - tw1) // 2, 875),
            cue_l1,
            font=f_sub2,
            fill=(255, 230, 0, 255),
            stroke_width=8,
            stroke_fill=(0, 0, 0, 255)
        )

    return frame.convert("RGB")


def assemble_master_radio_mp4(script_data: Dict[str, Any], plan: Dict[str, Any], base_dir: str) -> str:
    """
    Synthesizes the full broadcast audio track (with warm acoustic BGM ducking) and encodes
    episode_XX_master.mp4 (1920x1080 16:9 H.264 + AAC) with 100% full subtitle reading.
    """
    t0 = time.time()
    ep_num = script_data.get("episode_number", 1)
    audio_dir = Path(base_dir) / "audio"
    slides_dir = Path(base_dir) / "_slides_work"
    slides_dir.mkdir(parents=True, exist_ok=True)
    sprite_path = Path(base_dir).resolve().parent.parent / "assets" / "characters" / "sprite_hwang_young_woong.png"

    # Pre-build chapter base canvases
    chapter_bases: Dict[int, Image.Image] = {}
    for ch_plan in plan["chapters"]:
        c_idx = ch_plan["chapter_index"]
        chapter_bases[c_idx] = create_studio_chapter_base(
            c_idx, ch_plan["title"], ch_plan["visual_elements"], sprite_path
        )

    voice_parts: List[np.ndarray] = []
    slide_entries: List[Tuple[Path, float]] = []
    slide_counter = 0

    for ch in script_data.get("chapters", []):
        c_idx = ch["chapter_index"]
        ch_base = chapter_bases[c_idx]
        is_closing = (c_idx == 6)

        # 1.2s chapter opening bridge
        bridge_sec = 1.2
        bridge_samples = int(bridge_sec * SAMPLE_RATE)
        voice_parts.append(np.zeros(bridge_samples, dtype=np.float32))

        slide_counter += 1
        ch_intro_png = slides_dir / f"slide_{slide_counter:04d}.png"
        intro_img = render_cue_slide(
            ch_base,
            "📻 @김쌤의영웅라디오 — 챕터 오프닝",
            False,
            f"제{c_idx}장. {ch['title'][:24]}",
            "황영웅 [당신 편] 특집 라디오 방송",
            is_closing
        )
        intro_img.save(ch_intro_png, "PNG")
        slide_entries.append((ch_intro_png, bridge_sec))

        for seg in ch["segments"]:
            seg_id = seg["segment_id"]
            speaker = seg["speaker"]
            is_fan = (speaker == "fan_letter_writer")
            speaker_label = "💌 사연 낭독: 대구 이순자 어머니" if is_fan else "🎙️ 진행: DJ 김쌤 (영웅라디오)"
            mp3_path = audio_dir / f"{seg_id}_{speaker}.mp3"
            wav_tmp = slides_dir / f"{seg_id}.wav"

            if mp3_path.exists() and mp3_path.stat().st_size > 500:
                subprocess.run(
                    [FFMPEG_EXE, "-y", "-i", str(mp3_path), "-ac", "1", "-ar", str(SAMPLE_RATE), "-c:a", "pcm_s16le", str(wav_tmp)],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
                )
                with wave.open(str(wav_tmp), "rb") as wf:
                    pcm_i16 = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
                seg_audio = pcm_i16.astype(np.float32) / 32768.0
                if wav_tmp.exists():
                    wav_tmp.unlink()
            else:
                dur_fallback = float(seg.get("estimated_duration_sec", 12.0))
                seg_audio = np.zeros(int(dur_fallback * SAMPLE_RATE), dtype=np.float32)

            # Add 0.45s natural breathing pause after segment
            pause_sec = 0.45
            pause_samples = int(pause_sec * SAMPLE_RATE)
            seg_full_audio = np.concatenate([seg_audio, np.zeros(pause_samples, dtype=np.float32)])
            seg_total_dur = len(seg_full_audio) / float(SAMPLE_RATE)
            voice_parts.append(seg_full_audio)

            # Split text into sentence-level 2-line cues timed proportionally to character length
            cues = split_korean_text_into_cues(seg["text"], max_chars_per_line=24)
            total_chars = max(1, sum(len(c[0]) + len(c[1]) for c in cues))

            accum_dur = 0.0
            for idx_c, (l1, l2) in enumerate(cues):
                c_chars = max(1, len(l1) + len(l2))
                if idx_c < len(cues) - 1:
                    c_dur = round(seg_total_dur * (c_chars / float(total_chars)), 3)
                    c_dur = max(1.5, c_dur)
                    accum_dur += c_dur
                else:
                    c_dur = max(1.0, round(seg_total_dur - accum_dur, 3))

                slide_counter += 1
                cue_png = slides_dir / f"slide_{slide_counter:04d}.png"
                cue_img = render_cue_slide(ch_base, speaker_label, is_fan, l1, l2, is_closing)
                cue_img.save(cue_png, "PNG")
                slide_entries.append((cue_png, c_dur))

    # Concatenate full voice track
    voice_track = np.concatenate(voice_parts)
    total_samples = len(voice_track)
    total_duration = total_samples / float(SAMPLE_RATE)
    t = np.linspace(0, total_duration, total_samples, endpoint=False)

    # Synthesize warm acoustic/piano BGM bed (G Major -> Em7 -> Cmaj7 -> D7 gentle progression)
    chords = [
        (196.00, 246.94, 293.66),  # G3, B3, D4
        (164.81, 196.00, 246.94),  # E3, G3, B3
        (130.81, 164.81, 246.94),  # C3, E3, B3
        (146.83, 185.00, 220.00),  # D3, F#3, A3
    ]
    cycle_sec = 16.0
    phase_in_cycle = (t % cycle_sec) / cycle_sec
    bgm = np.zeros(total_samples, dtype=np.float32)
    for c_i, (f1, f2, f3) in enumerate(chords):
        mask = ((phase_in_cycle >= c_i * 0.25) & (phase_in_cycle < (c_i + 1) * 0.25)).astype(np.float32)
        tone = (
            0.45 * np.sin(2 * np.pi * f1 * t) +
            0.35 * np.sin(2 * np.pi * f2 * t) +
            0.20 * np.sin(2 * np.pi * f3 * t)
        ).astype(np.float32)
        bgm += tone * mask

    # Smooth envelope & sidechain ducking
    duck_win = int(SAMPLE_RATE * 0.12)
    v_env = np.convolve(np.abs(voice_track), np.ones(duck_win, dtype=np.float32) / duck_win, mode="same")
    bgm_gain = np.clip(0.14 - v_env * 0.28, 0.045, 0.14)

    mix_mono = voice_track * 1.05 + bgm * bgm_gain
    peak = max(float(np.max(np.abs(mix_mono))), 1e-6)
    if peak > 0.891:  # -1.0 dBTP limiter
        mix_mono *= (0.891 / peak)

    stereo_pcm = np.vstack([mix_mono, mix_mono]).T
    pcm_out = np.clip(stereo_pcm * 32767.0, -32768, 32767).astype(np.int16)

    master_wav = Path(base_dir) / f"episode_{ep_num:02d}_master_audio.wav"
    with wave.open(str(master_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm_out.tobytes())

    # Write FFmpeg concat demuxer manifest
    concat_txt = slides_dir / "slides_concat.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for png_path, dur in slide_entries:
            safe_p = str(png_path.resolve()).replace("\\", "/")
            f.write(f"file '{safe_p}'\n")
            f.write(f"duration {dur:.3f}\n")
        # Repeat last file per FFmpeg concat demuxer spec
        last_p = str(slide_entries[-1][0].resolve()).replace("\\", "/")
        f.write(f"file '{last_p}'\n")

    master_mp4 = Path(base_dir) / f"episode_{ep_num:02d}_master.mp4"
    ffmpeg_cmd = [
        FFMPEG_EXE, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_txt),
        "-i", str(master_wav),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "stillimage",
        "-crf", "23",
        "-r", "15",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(master_mp4)
    ]
    print(f"[*] Encoding 16:9 1080p Master Radio Broadcast MP4 ({len(slide_entries)} subtitle slides, {total_duration:.1f}s)...")
    res = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="ignore")
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg master radio encode failed:\n{res.stderr[-500:]}")

    # Clean up temporary slide PNGs to save disk space
    shutil.rmtree(slides_dir, ignore_errors=True)
    if master_wav.exists():
        master_wav.unlink()

    size_mb = master_mp4.stat().st_size / (1024 * 1024)
    print(f"[+] Master Radio MP4 rendered in {time.time() - t0:.1f}s: {master_mp4} ({size_mb:.2f} MB, {total_duration:.1f}s)")
    return str(master_mp4)


def main():
    parser = argparse.ArgumentParser(description="@김쌤의영웅라디오 Video Assembly Engine")
    parser.add_argument("--script-file", type=str, default="", help="Path to script_epXX.json")
    parser.add_argument("--narration-file", type=str, default="", help="Path to narration_prompts.json")
    parser.add_argument("--output-dir", type=str, default="", help="Directory to save video assembly plan")
    parser.add_argument("--render-visuals", action="store_true", default=True, help="Render 1080p visual storyboard cards")
    parser.add_argument("--render-mp4", action="store_true", default=True, help="Render full 1080p episode_XX_master.mp4")
    args = parser.parse_args()

    if not args.script_file:
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "content", "episode_01", "script_ep01.json"))
    else:
        script_path = os.path.abspath(args.script_file)

    if not os.path.exists(script_path):
        print(f"[ERROR] Script file not found: {script_path}")
        sys.exit(1)

    if not args.output_dir:
        base_dir = os.path.dirname(script_path)
    else:
        base_dir = os.path.abspath(args.output_dir)

    with open(script_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    narration_data = None
    if args.narration_file and os.path.exists(args.narration_file):
        with open(args.narration_file, "r", encoding="utf-8") as f:
            narration_data = json.load(f)

    print(f"[*] Building 16:9 video assembly plan for {script_data.get('episode_title', 'Radio Episode')}...")
    plan = build_video_assembly_plan(script_data, narration_data)

    plan_path = os.path.join(base_dir, "video_assembly_plan.json")
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved video assembly plan to: {plan_path}")

    if args.render_visuals:
        generate_sample_scene_cards(plan, base_dir)

    if args.render_mp4:
        assemble_master_radio_mp4(script_data, plan, base_dir)

    print("[SUCCESS] Video assembly plan, visual assets, and master MP4 generation complete.")


if __name__ == "__main__":
    main()
