#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
package_youtube_metadata.py
@김쌤의영웅라디오 YouTube Metadata, SEO & Conversion Kit Packager

Specifications:
- High-CTR Title: Emotional hook for 5070 senior mothers with emojis
- Chapter Timestamps: 6-chapter timing marks matching timeline
- SEO Description: Single-gate story funnel (https://paradise-hero.com/story.html),
  VIP community perks callout, support email (beable9489@gmail.com)
- Pinned Comment: Algorithmic safe kit (0 direct URLs, directs to description box)
- High-Converting Tags & Thumbnail Generation Prompt + 1080p visual thumbnail
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


def format_timestamp(sec: float) -> str:
    """Formats seconds into MM:SS format."""
    total_sec = int(round(sec))
    mins = total_sec // 60
    secs = total_sec % 60
    return f"{mins:02d}:{secs:02d}"


def build_youtube_metadata(script_data: Dict[str, Any], video_plan: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Builds the complete YouTube publishing metadata package.
    """
    ep_num = script_data.get("episode_number", 1)
    featured_song = script_data.get("featured_song", "당신 편")

    # High-CTR Title adhering to senior appeal
    title = f"[제{ep_num}화] \"어머니, 이제 제가 당신의 편이 되어드릴게요\" 🌸 황영웅 [{featured_song}]에 얽힌 눈물의 사연과 김쌤의 감동 해설"

    # Chapter Timestamps
    # If video plan is provided, use actual plan start times, otherwise standard timestamps
    chapter_icons = ["🌸", "🎙️", "🎵", "💌", "💚", "🌙"]
    timestamps = []

    if video_plan and "chapters" in video_plan:
        for i, ch in enumerate(video_plan["chapters"]):
            ts_str = format_timestamp(ch["timeline_start_sec"])
            icon = chapter_icons[i % len(chapter_icons)]
            short_title = ch["title"].split("—")[0].strip() if "—" in ch["title"] else ch["title"]
            timestamps.append({
                "chapter_index": ch["chapter_index"],
                "timestamp": ts_str,
                "label": f"{ts_str} {icon} {ch['title']}"
            })
    else:
        # Standard fallback timestamps
        std_times = [
            ("00:00", "🌸 오프닝 — 파라다이스 어머님들, 저녁 진지 드셨습니까?"),
            ("02:00", "🎙️ 영웅 이야기 — 모진 비바람을 견뎌낸 그 깊은 목소리의 비밀"),
            ("05:45", "🎵 명곡 해설 — '내가 그대 편이 되겠소', [당신 편] 가사 속 눈물의 약속"),
            ("09:30", "💌 파라다이스 우체통 — 대구 이순자 어머님의 눈물겨운 사연 낭독"),
            ("13:00", "💚 영웅 응원석 — 파라다이스 가족들이 함께 만드는 황금빛 기적"),
            ("14:15", "🌙 클로징 — 편안한 밤 되세요 & 공식 사랑방 사연 안내")
        ]
        for idx, (t, lbl) in enumerate(std_times, 1):
            timestamps.append({
                "chapter_index": idx,
                "timestamp": t,
                "label": f"{t} {lbl}"
            })

    timestamp_block = "\n".join([ts["label"] for ts in timestamps])

    # Single-gate funnel and description
    description = f"""파라다이스 가족 여러분, 그리고 사랑하는 우리 어머님들, 김쌤의 영웅 라디오에 오신 것을 진심으로 환영합니다.
오늘 밤, 영웅님의 따뜻한 목소리와 함께 고단했던 하루의 피로를 모두 씻어내시길 바랍니다.

김쌤의 영웅 라디오 사연 신청 및 황금빛 VIP 혜택은 공식 커뮤니티 https://paradise-hero.com 에서 확인하세요.

💌 [김쌤 라디오 사연 신청 & 파라다이스 사랑방 바로가기]
👉 https://paradise-hero.com/story.html
(어머님의 소중한 삶의 이야기와 영웅님을 향한 편지는 오직 위 공식 사랑방에서만 정성껏 접수받습니다)

🌟 [황영웅 노래 1-클릭 연속 듣기 & 황금빛 응원 전광판]
👉 https://paradise-hero.com

━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️ [영상 타임스탬프 (누르면 바로 해당 코너로 이동합니다)]
{timestamp_block}
━━━━━━━━━━━━━━━━━━━━━━━━━━

🎧 [황영웅 가수의 공식 음원을 소비해 주세요]
황영웅 가수의 모든 노래는 멜론, 지니, 벅스, 유튜브 뮤직의 공식 스트리밍을 이용해 주실 때 가수에게 가장 큰 힘과 날개가 됩니다.

※ 본 영상에 수록된 배경음악은 드림컴퍼니 자체 제작 서정적 어쿠스틱/피아노 로열티 프리 음원이며, 황영웅 가수의 모든 음원 권리를 100% 존중합니다.
※ 공식 고객지원 및 제휴 문의: beable9489@gmail.com
"""

    # Pinned comment kit: STRICT ZERO RAW URL to maintain YouTube algorithm standing
    pinned_comment = """🌸 [김쌤의 다정한 안내 말씀] 🌸
사랑하는 파라다이스 어머님들, 오늘도 영웅님 노래와 함께 따뜻하고 평안한 시간 보내셨는지요.

가슴속에 품어두셨던 애틋한 사연이나 영웅님께 전하고 싶은 편지가 있으시다면,
영상 바로 아래 [더보기]를 누르셔서 공식 사랑방(paradise-hero.com) 사연 우체통에 편안히 남겨주세요.
김쌤이 하나하나 소중히 읽고 다음 방송에서 따뜻하게 소개해 드리겠습니다.

오늘 밤도 근심 걱정 모두 내려놓으시고, 영웅님 노래 들으시며 달콤한 단잠 이루시길 기도합니다. 
항상 건강하시고, 늘 행복하세요. 건행! 💚"""

    # High-ranking SEO tags
    tags = [
        "황영웅",
        "파라다이스",
        "김쌤의영웅라디오",
        "황영웅당신편",
        "당신편",
        "황영웅노래",
        "황영웅사연",
        "황영웅콘서트",
        "황영웅팬클럽",
        "황영웅비하인드",
        "트로트라디오",
        "시니어힐링라디오",
        "황영웅감동사연",
        "꽃구경",
        "붓",
        "파라다이스히어로",
        "paradise-hero"
    ]

    # Thumbnail formula & prompt
    thumbnail_spec = {
        "aspect_ratio": "16:9 (1280x720 / 1920x1080)",
        "layout_formula": "좌측 55% 아티스트 감성 표정 클로즈업 + 우측 45% 딥네이비/골드 3단 극대형 볼드 텍스트",
        "top_amber_badge": f"[김쌤의 영웅 라디오 {ep_num}화]",
        "main_headline": "어머니, 이젠 울지 마세요",
        "headline_color": "#F1C40F (황금빛 골드)",
        "sub_headline": f"황영웅 [{featured_song}]에 얽힌 눈물의 사연",
        "sub_headline_color": "#FFFFFF (순백색)",
        "generation_art_prompt": (
            "YouTube 16:9 thumbnail, dramatic split composition. "
            "Left 55%: Emotional and warm close-up portrait of handsome Korean trot singer Hwang Young-woong singing passionately on stage, "
            "warm golden spotlight illumination, tearful yet hopeful expression. "
            "Right 45%: Rich deep royal navy background with warm amber glow, clean negative space for giant typography. "
            "High CTR aesthetic, ultra-sharp detail, cinematic lighting, 8k resolution --ar 16:9"
        )
    }

    metadata = {
        "channel_name": "@김쌤의영웅라디오",
        "episode_number": ep_num,
        "title": title,
        "title_length_chars": len(title),
        "description": description,
        "pinned_comment": pinned_comment,
        "pinned_comment_has_raw_url": ("http://" in pinned_comment or "https://" in pinned_comment),
        "target_funnel_url": "https://paradise-hero.com/story.html",
        "official_domain": "https://paradise-hero.com",
        "contact_email": "beable9489@gmail.com",
        "tags": tags,
        "tags_count": len(tags),
        "timestamps": timestamps,
        "thumbnail_specification": thumbnail_spec
    }

    return metadata


def render_sample_thumbnail(meta: Dict[str, Any], output_path: str):
    """
    Renders an authentic 1920x1080 YouTube thumbnail matching the high-CTR senior design formula.
    """
    if Image is None or ImageDraw is None:
        print("[WARN] Pillow (PIL) not available, skipping thumbnail image rendering.")
        return

    width, height = 1920, 1080
    thumb = Image.new("RGB", (width, height), color=(10, 18, 32))
    draw = ImageDraw.Draw(thumb)

    # Left 55% Stage / Artist artistic zone (Deep charcoal/emerald gradient)
    draw.rectangle([(0, 0), (1050, 1080)], fill=(12, 36, 26))
    # Soft golden spotlight beam simulation
    draw.polygon([(0, 0), (600, 0), (950, 1080), (300, 1080)], fill=(25, 55, 38))
    draw.ellipse([(200, 200), (850, 850)], fill=(35, 75, 50))

    # Artist illustration silhouette representation
    draw.rectangle([(150, 450), (900, 950)], fill=(20, 45, 32), outline=(241, 196, 15), width=3)
    draw.text((220, 520), "가수 황영웅", fill=(245, 230, 200))
    draw.text((220, 580), "정규 1집 [당신 편] 감성 보컬", fill=(200, 220, 210))
    draw.text((220, 650), "♪ \"세상이 다 등을 돌려도 내 그대 편이 되겠소\"", fill=(241, 196, 15))

    # Right 45% High-CTR Typography zone (Deep navy with gold accents)
    draw.rectangle([(1050, 0), (1920, 1080)], fill=(8, 15, 28))
    draw.line([(1050, 0), (1050, 1080)], fill=(241, 196, 15), width=4)

    # Top amber badge
    thumb_spec = meta["thumbnail_specification"]
    draw.rectangle([(1120, 120), (1700, 200)], fill=(230, 126, 34))
    draw.text((1150, 145), thumb_spec["top_amber_badge"], fill=(255, 255, 255))

    # Main Headline (Large Gold)
    draw.rectangle([(1120, 260), (1850, 480)], fill=(18, 28, 48), outline=(241, 196, 15), width=4)
    draw.text((1150, 310), "어머니,", fill=(241, 196, 15))
    draw.text((1150, 380), "이젠 울지 마세요", fill=(241, 196, 15))

    # Sub Headline (White Box)
    draw.rectangle([(1120, 540), (1850, 700)], fill=(240, 240, 240))
    draw.text((1150, 580), "황영웅 [당신 편]에 얽힌", fill=(10, 10, 10))
    draw.text((1150, 630), "눈물의 사연과 김쌤의 해설", fill=(180, 20, 20))

    # Bottom CTA strip
    draw.rectangle([(1120, 780), (1850, 940)], fill=(12, 45, 30), outline=(46, 204, 113), width=3)
    draw.text((1150, 810), "💌 사연 신청 & 파라다이스 사랑방", fill=(46, 204, 113))
    draw.text((1150, 860), "👉 https://paradise-hero.com", fill=(255, 255, 255))

    # Outer border
    draw.rectangle([(15, 15), (1905, 1065)], outline=(241, 196, 15), width=4)

    thumb.save(output_path, "PNG")
    print(f"[+] Saved 1080p high-CTR YouTube thumbnail to: {output_path} ({os.path.getsize(output_path)} bytes)")


def main():
    parser = argparse.ArgumentParser(description="@김쌤의영웅라디오 YouTube Metadata Packager")
    parser.add_argument("--script-file", type=str, default="", help="Path to script_epXX.json")
    parser.add_argument("--video-plan", type=str, default="", help="Path to video_assembly_plan.json")
    parser.add_argument("--output-dir", type=str, default="", help="Target directory for metadata artifacts")
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

    os.makedirs(base_dir, exist_ok=True)

    with open(script_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    video_plan = None
    if args.video_plan and os.path.exists(args.video_plan):
        with open(args.video_plan, "r", encoding="utf-8") as f:
            video_plan = json.load(f)
    else:
        # Check if video_assembly_plan.json exists in base_dir
        plan_cand = os.path.join(base_dir, "video_assembly_plan.json")
        if os.path.exists(plan_cand):
            with open(plan_cand, "r", encoding="utf-8") as f:
                video_plan = json.load(f)

    print(f"[*] Packaging YouTube metadata for Episode {script_data.get('episode_number', 1)}...")
    meta = build_youtube_metadata(script_data, video_plan)

    meta_json_path = os.path.join(base_dir, "youtube_metadata.json")
    with open(meta_json_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved metadata JSON to: {meta_json_path}")

    # Also render sample 1080p thumbnail
    thumb_path = os.path.join(base_dir, "thumbnail_ep01_1080p.png")
    render_sample_thumbnail(meta, thumb_path)

    # Save copy-paste ready text file
    meta_txt_path = os.path.join(base_dir, "youtube_upload_kit.txt")
    with open(meta_txt_path, "w", encoding="utf-8") as f:
        f.write("=== YOUTUBE VIDEO TITLE ===\n")
        f.write(meta["title"] + "\n\n")
        f.write("=== YOUTUBE DESCRIPTION ===\n")
        f.write(meta["description"] + "\n\n")
        f.write("=== PINNED COMMENT (Zero External URLs for Algorithm Safety) ===\n")
        f.write(meta["pinned_comment"] + "\n\n")
        f.write("=== TAGS ===\n")
        f.write(", ".join(meta["tags"]) + "\n")
    print(f"[+] Saved upload kit text to: {meta_txt_path}")

    print("[SUCCESS] YouTube metadata and thumbnail package complete.")


if __name__ == "__main__":
    main()
