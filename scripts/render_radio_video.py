#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_radio_video.py
@김쌤의영웅라디오 16:9 1080p Long-Form Video Assembly & Storyboard Engine

Specifications:
- Resolution: 1920x1080 (16:9 Landscape), 30fps
- Ken Burns Motion: 30s cycle slow zoom (1.00x -> 1.05x) and subtle pan
- Senior Subtitle Spec: 52~56pt font (default 54pt), #FFFFFF with 8px dark charcoal (#1A1A1A) outline, Y=910
- Chapter Title Cards: 6 chapters with custom scene prompts and generated 1080p graphics
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any

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

VIDEO_SPECS = {
    "width": 1920,
    "height": 1080,
    "aspect_ratio": "16:9",
    "framerate": 30,
    "video_codec": "libx264",
    "video_profile": "high",
    "crf": 18,
    "preset": "fast",
    "audio_codec": "aac",
    "audio_bitrate": "320k",
    "audio_samplerate": 48000,
    "ken_burns": {
        "cycle_duration_sec": 30.0,
        "zoom_start": 1.00,
        "zoom_end": 1.05,
        "ffmpeg_zoompan_filter": "zoompan=z='min(zoom+0.00008,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=900:s=1920x1080:fps=30"
    },
    "subtitles": {
        "font_family": "NanumSquareRoundEB / Malgun Gothic / AppleSDGothicNeo",
        "font_size_pt": 54,
        "font_size_range": "52~56pt",
        "text_color": "#FFFFFF",
        "outline_color": "#1A1A1A",
        "outline_width_px": 8,
        "vertical_align_y": 910,
        "safe_margin_bottom_px": 170,
        "max_lines_per_cue": 2,
        "max_chars_per_line": 26
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


def build_video_assembly_plan(script_data: Dict[str, Any], narration_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Constructs the master 16:9 video assembly plan linking scripts, audio, Ken Burns motion,
    chapter scene prompts, and senior-friendly subtitle timing.
    """
    chapters = script_data.get("chapters", [])
    chapters_plan = []

    cumulative_time = 0.0

    for i, ch in enumerate(chapters):
        ch_idx = ch["chapter_index"]
        scene_info = SCENE_PROMPTS[i] if i < len(SCENE_PROMPTS) else SCENE_PROMPTS[-1]

        # Calculate chapter duration from segments
        ch_duration = ch.get("total_estimated_sec", 150.0) + 12.0  # include intro/outro bridges

        start_time = round(cumulative_time, 2)
        end_time = round(cumulative_time + ch_duration, 2)

        # Build subtitle cues for segments
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

    plan = {
        "channel_name": script_data.get("channel_name", "@김쌤의영웅라디오"),
        "episode_number": script_data.get("episode_number", 1),
        "episode_title": script_data.get("episode_title", ""),
        "total_chapters": len(chapters_plan),
        "total_video_duration_sec": total_duration,
        "aspect_ratio": VIDEO_SPECS["aspect_ratio"],
        "resolution": f"{VIDEO_SPECS['width']}x{VIDEO_SPECS['height']}",
        "video_specifications": VIDEO_SPECS,
        "ffmpeg_render_command": (
            "ffmpeg -loop 1 -framerate 30 -t {duration} -i {background_image} "
            "-i {master_audio} -filter_complex "
            "\"[0:v]scale=1920:1080,zoompan=z='min(zoom+0.00008,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=900:s=1920x1080:fps=30[bg];"
            "[bg]drawtext=text='{subtitle_text}':fontcolor=white:fontsize=54:bordercolor=black:borderw=8:x=(w-text_w)/2:y=910[v]\" "
            "-map \"[v]\" -map 1:a -c:v libx264 -preset fast -crf 18 -c:a aac -b:a 320k -shortest output_1080p.mp4"
        ),
        "chapters": chapters_plan
    }

    return plan


def generate_sample_scene_cards(plan: Dict[str, Any], output_dir: str):
    """
    Renders 1920x1080 high-contrast visual title cards for all 6 chapters using PIL.
    """
    if Image is None or ImageDraw is None:
        print("[WARN] Pillow (PIL) not available, skipping title card image rendering.")
        return

    visuals_dir = os.path.join(output_dir, "visuals")
    os.makedirs(visuals_dir, exist_ok=True)

    # Color themes for chapters
    palette = [
        ((35, 20, 15), (232, 155, 83), (245, 227, 200)),  # Warm twilight
        ((14, 42, 30), (39, 174, 96), (241, 196, 15)),    # Emerald stage
        ((31, 22, 16), (211, 84, 0), (229, 220, 197)),    # Vintage LP
        ((26, 20, 18), (192, 57, 43), (243, 156, 18)),    # Candle letter
        ((11, 59, 36), (46, 204, 113), (241, 196, 15)),   # Fandom wave
        ((10, 25, 47), (27, 42, 74), (247, 208, 112))     # Serene night
    ]

    for i, ch in enumerate(plan["chapters"]):
        idx = ch["chapter_index"]
        bg_col, accent_col, text_col = palette[(idx - 1) % len(palette)]

        img = Image.new("RGB", (1920, 1080), color=bg_col)
        draw = ImageDraw.Draw(img)

        # Draw decorative background elements
        # Outer border
        draw.rectangle([(30, 30), (1890, 1050)], outline=accent_col, width=4)
        draw.rectangle([(40, 40), (1880, 1040)], outline=(80, 80, 80), width=1)

        # Channel watermark badge top left
        draw.rectangle([(70, 70), (450, 130)], fill=(20, 20, 20, 200), outline=accent_col, width=2)
        draw.text((90, 85), "@김쌤의영웅라디오", fill=(255, 255, 255))

        # Chapter Badge
        badge_text = f"CHAPTER 0{idx}"
        draw.rectangle([(70, 200), (320, 260)], fill=accent_col)
        draw.text((90, 218), badge_text, fill=(10, 10, 10))

        # Title & Subtitle
        draw.text((70, 290), ch["title"], fill=text_col)

        # Art prompt summary in middle
        draw.rectangle([(70, 420), (1850, 780)], fill=(15, 15, 20), outline=(60, 60, 70), width=2)
        draw.text((100, 450), f"[시네마틱 16:9 비주얼 콘셉트 프롬프트]", fill=accent_col)

        prompt_lines = [ch["art_prompt"][k:k+110] for k in range(0, min(len(ch["art_prompt"]), 330), 110)]
        y_pos = 500
        for pline in prompt_lines:
            draw.text((100, y_pos), pline, fill=(200, 200, 200))
            y_pos += 35

        draw.text((100, 680), f"주요 연출 요소: {', '.join(ch['visual_elements'])}", fill=(180, 220, 190))
        draw.text((100, 720), f"모션: {ch['ken_burns_motion']['zoom_ratio']} ({ch['ken_burns_motion']['pan_direction']})", fill=(240, 200, 120))

        # Senior Subtitle Safe Area Preview at bottom (Y=900~960)
        draw.rectangle([(200, 880), (1720, 980)], fill=(0, 0, 0, 180), outline=(100, 100, 100), width=2)
        sample_sub = f"▶ 54pt 고가독성 노안 방지 자막 안심 구역 (Y=910) — 황영웅 [당신 편] Chapter {idx}"
        draw.text((240, 915), sample_sub, fill=(255, 255, 255))

        # Save output image
        card_filename = f"ch{idx}_scene_1080p.png"
        card_path = os.path.join(visuals_dir, card_filename)
        img.save(card_path, "PNG")
        print(f"    - Rendered 1080p chapter card: {card_filename} ({os.path.getsize(card_path)} bytes)")

    print(f"[+] All {len(plan['chapters'])} chapter visual title cards generated in: {visuals_dir}")


def main():
    parser = argparse.ArgumentParser(description="@김쌤의영웅라디오 Video Assembly Engine")
    parser.add_argument("--script-file", type=str, default="", help="Path to script_epXX.json")
    parser.add_argument("--narration-file", type=str, default="", help="Path to narration_prompts.json")
    parser.add_argument("--output-dir", type=str, default="", help="Directory to save video assembly plan")
    parser.add_argument("--render-visuals", action="store_true", default=True, help="Render 1080p visual storyboard cards")
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

    print("[SUCCESS] Video assembly plan and visual assets generation complete.")


if __name__ == "__main__":
    main()
