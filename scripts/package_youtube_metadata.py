#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
package_youtube_metadata.py
@김쌤의영웅라디오 — 12~20분 보이는 사연 라디오 롱폼 메타데이터 & 고정 댓글 패키저 (2026-11-11 개조판)

핵심 규격:
1. 필수 고정 태그: #황영웅 #파라다이스 #트로트 #감동사연 #시니어유튜브
   - 절대 금지 태그(#영상툰, #애니메이션, #웹툰, '트롯 10대 왕자', 타 가수명) 원천 배제
2. 롱폼 첫 번째 고정 댓글(Pinned Comment) 자동 등록 문안:
   - 무료 화보 기념사진관 브릿지: https://paradise-hero.com/booth.html
   - 네이버 공식 안심특가관 브릿지: https://cshop.naver.com/paradiseshop + 쇼핑 커넥트 수수료 고지
3. 예약 발행 시각 고정 (publishAt):
   - 주 2~3회 화·금 18:00 KST 자동 산출
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any

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

KST = timezone(timedelta(hours=9))
FIXED_HASHTAGS = ["#황영웅", "#파라다이스", "#트로트", "#감동사연", "#시니어유튜브"]

LONGFORM_PINNED_COMMENT = """💚 우리 영웅님 라디오 매주 화·금 저녁 6시 편하게 듣기 & 무료 화보 기념사진 찍기
👉 공식 팬 쉼터 바로가기: https://paradise-hero.com/booth.html

🟢 카드 입력 없이 1초 결제! 김쌤이 엄선한 눈·관절 건강 & 효도 선물 [네이버 공식 안심 혜택관]
👉 네이버페이(Npay)로 편하게 구경하기: https://cshop.naver.com/paradiseshop

💿 황영웅 정품 음반('당신 편'·'가을, 그리움') · 차량용 효도USB · 콘서트 준비물
👉 영웅라디오 쿠팡 인플루언서 공식관: https://influencers.coupang.com/s/paradisehero
(네이버 쇼핑 커넥트 활동의 일환으로 판매 발생 시 소정의 수수료를 제공받으며, 쿠팡 파트너스 활동의 일환으로 이에 따른 일정액의 수수료를 제공받습니다.)"""


def format_timestamp(sec: float) -> str:
    """Formats seconds into MM:SS format."""
    total_sec = int(round(sec))
    mins = total_sec // 60
    secs = total_sec % 60
    return f"{mins:02d}:{secs:02d}"


def compute_next_longform_publish_at_kst(now_kst: datetime = None, target_slot_day: str = "AUTO") -> str:
    """Computes next Tuesday (weekday=1) or Friday (weekday=4) 18:00 KST ISO-8601 timestamp."""
    now_kst = now_kst or datetime.now(KST)
    norm_slot = (target_slot_day or "AUTO").strip().upper()
    allowed_weekdays = (1,) if norm_slot == "TUE" else ((4,) if norm_slot == "FRI" else (1, 4))
    for add_days in range(0, 15):
        cand_date = now_kst + timedelta(days=add_days)
        if cand_date.weekday() in allowed_weekdays:
            cand_dt = cand_date.replace(hour=18, minute=0, second=0, microsecond=0)
            if cand_dt > now_kst + timedelta(minutes=15):
                return cand_dt.isoformat()
    fallback = (now_kst + timedelta(days=3)).replace(hour=18, minute=0, second=0, microsecond=0)
    return fallback.isoformat()


def build_youtube_metadata(script_data: Dict[str, Any], video_plan: Dict[str, Any] = None, publish_at_override: str = "") -> Dict[str, Any]:
    """
    Builds the complete YouTube Longform Radio publishing metadata package.
    """
    ep_num = script_data.get("episode_number", 1)
    featured_song = script_data.get("featured_song", "당신 편")
    song_short = featured_song.split("(")[0].strip()
    slot_day = script_data.get("broadcast_slot_day", "AUTO")
    publish_at_kst = publish_at_override.strip() if publish_at_override else compute_next_longform_publish_at_kst(target_slot_day=slot_day)

    if ep_num >= 6 and script_data.get("episode_title"):
        base_title = script_data["episode_title"].strip()
        if "황영웅" not in base_title:
            base_title = f"{base_title} (황영웅 [{song_short}])"
        suffix = " #황영웅 #파라다이스"
        max_base = 98 - len(suffix)
        if len(base_title) > max_base:
            base_title = base_title[:max_base - 1].rstrip() + "…"
        title = f"{base_title}{suffix}"
    else:
        title = (
            f"[심야라디오 {ep_num}화] \"어머니, 이제 제가 당신 편이 되어드릴게요\" "
            f"황영웅 [{song_short}] 사연 3편 & 주요 소식 #황영웅 #파라다이스"
        )

    chapter_icons = ["🌸", "🎙️", "🎵", "💌", "💚", "🌙"]
    timestamps = []

    if video_plan and "chapters" in video_plan:
        for i, ch in enumerate(video_plan["chapters"]):
            ts_str = format_timestamp(ch["timeline_start_sec"])
            icon = chapter_icons[i % len(chapter_icons)]
            timestamps.append({
                "chapter_index": ch["chapter_index"],
                "timestamp": ts_str,
                "label": f"{ts_str} {icon} {ch['title']}",
            })
    else:
        std_times = [
            ("00:00", "🌸 오프닝 — 파라다이스 어머님들, 저녁 진지 드셨습니까?"),
            ("02:00", "🎙️ 영웅 이야기 & 첫 번째 소식 — 모진 비바람을 견뎌낸 깊은 목소리"),
            ("05:45", "🎵 명곡 해설 & 두 번째 사연 — [당신 편] 가사 속 눈물의 약속"),
            ("09:30", "💌 파라다이스 우체통 — 대구 이순자 어머님의 사연 전문 낭독"),
            ("13:15", "💚 영웅 응원석 & 두 번째 소식 — 세 번째 사연과 파라다이스 나눔 소식"),
            ("15:00", "🌙 클로징 — 무료 화보 기념사진관 & 공식 사랑방 사연 안내"),
        ]
        for idx, (t, lbl) in enumerate(std_times, 1):
            timestamps.append({
                "chapter_index": idx,
                "timestamp": t,
                "label": f"{t} {lbl}",
            })

    timestamp_block = "\n".join([ts["label"] for ts in timestamps])
    hashtags_line = " ".join(FIXED_HASHTAGS)

    description = f"""파라다이스 가족 여러분, 그리고 사랑하는 우리 어머님들, 김쌤의 영웅 라디오에 오신 것을 진심으로 환영합니다.
📅 정규 본방송 편성: 매주 화요일 · 금요일 저녁 6시 (화요 심야 사연 드라마 & 금요 명곡 해부학·친절 특집)
오늘 밤 방송에서는 공식 사랑방(story.html)에 도착한 어머님들의 감동 사연 3편과 황영웅 뉴스룸(news.html) 주요 소식 2건을 따뜻한 진공관 라디오 부스에서 정성껏 읽어드립니다.

💚 [무료 화보 기념사진관 & 공식 팬 쉼터 바로가기]
👉 https://paradise-hero.com/booth.html

💌 [김쌤 라디오 사연 신청 & 어머님 편지 접수]
👉 https://paradise-hero.com/story.html

📰 [가수 황영웅 전용 큰글씨 뉴스룸]
👉 https://paradise-hero.com/news.html

🟢 [카드 입력 없이 1초 결제! 김쌤 공식 네이버 크리에이터샵 안심 혜택관]
👉 https://cshop.naver.com/paradiseshop

💿 [황영웅 정품 음반 · 차량용 효도USB · 콘서트 준비물 — 쿠팡 인플루언서 공식관]
👉 https://influencers.coupang.com/s/paradisehero
(네이버 쇼핑 커넥트 활동의 일환으로 판매 발생 시 소정의 수수료를 제공받으며, 쿠팡 파트너스 활동의 일환으로 이에 따른 일정액의 수수료를 제공받습니다.)

━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️ [영상 타임스탬프 (누르면 바로 해당 코너로 이동합니다)]
{timestamp_block}
━━━━━━━━━━━━━━━━━━━━━━━━━━

🎧 [황영웅 가수의 공식 음원을 응원해 주세요]
황영웅 가수의 모든 노래는 멜론, 지니, 벅스, 유튜브 뮤직의 공식 스트리밍을 이용해 주실 때 가수에게 가장 큰 힘과 날개가 됩니다.

※ 본 영상에 수록된 배경음악은 드림컴퍼니 자체 제작 서정적 어쿠스틱/피아노 로열티 프리 음원이며, 황영웅 가수의 모든 음원 권리를 100% 존중합니다.
※ 공식 고객지원 및 제휴 문의: beable9489@gmail.com

{hashtags_line}
"""

    tags = FIXED_HASHTAGS.copy()

    hl_line1 = script_data.get("thumbnail_headline_line1") or "어머니,"
    hl_line2 = script_data.get("thumbnail_headline_line2") or "이젠 울지 마세요"
    sub_hl = script_data.get("thumbnail_subline") or "보이는 사연 라디오 3편 & 반가운 소식 2건"
    prog_fmt = script_data.get("program_format", "TUE_STORY_DRAMA")
    if ep_num >= 6:
        badge_txt = f"[화요 심야 사연극 {ep_num}화]" if slot_day == "TUE" else f"[금요 명곡·친절특집 {ep_num}화]"
    else:
        badge_txt = f"[김쌤의 영웅 라디오 {ep_num}화]"

    thumbnail_spec = {
        "aspect_ratio": "16:9 (1920x1080)",
        "layout_formula": "좌측 55% 가수 황영웅 감성 화보 클로즈업 + 우측 45% 진공관 부스 3단 왕글씨",
        "program_format": prog_fmt,
        "top_amber_badge": badge_txt,
        "headline_line1": hl_line1,
        "headline_line2": hl_line2,
        "main_headline": f"{hl_line1} {hl_line2}".strip(),
        "headline_color": "#F1C40F (황금빛 골드)",
        "sub_headline": sub_hl,
        "sub_headline_color": "#FFFFFF (순백색)",
        "generation_art_prompt": (
            "YouTube 16:9 thumbnail, warm vacuum-tube radio studio split composition. "
            "Left 55%: Emotional warm portrait of Korean trot gentleman in emerald velvet suit by vintage tube microphone. "
            "Right 45%: Deep mahogany and navy background with glowing amber vacuum tubes and clean space for giant Korean typography --ar 16:9"
        ),
    }

    metadata = {
        "channel_name": "@김쌤의영웅라디오",
        "episode_number": ep_num,
        "broadcast_slot_day": slot_day,
        "program_format": prog_fmt,
        "title": title,
        "title_length_chars": len(title),
        "description": description,
        "pinned_comment": LONGFORM_PINNED_COMMENT,
        "pinned_comment_booth_url": "https://paradise-hero.com/booth.html",
        "pinned_comment_creator_shop_url": "https://cshop.naver.com/paradiseshop",
        "pinned_comment_coupang_influencer_url": "https://influencers.coupang.com/s/paradisehero",
        "publish_schedule_policy": "화·금 18:00 KST",
        "publishAt": publish_at_kst,
        "target_funnel_url": "https://paradise-hero.com/booth.html",
        "story_funnel_url": "https://paradise-hero.com/story.html",
        "news_funnel_url": "https://paradise-hero.com/news.html",
        "creator_shop_url": "https://cshop.naver.com/paradiseshop",
        "coupang_influencer_url": "https://influencers.coupang.com/s/paradisehero",
        "official_domain": "https://paradise-hero.com",
        "contact_email": "beable9489@gmail.com",
        "tags": tags,
        "tags_count": len(tags),
        "timestamps": timestamps,
        "thumbnail_specification": thumbnail_spec,
    }

    return metadata


def render_sample_thumbnail(meta: Dict[str, Any], output_path: str):
    """Renders 1920x1080 YouTube Longform thumbnail matching senior design formula with per-episode dynamic copy & palette."""
    if Image is None or ImageDraw is None:
        return

    font_path = r"C:\Windows\Fonts\malgunbd.ttf"
    def _font(sz: int):
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, sz)
            except Exception:
                pass
        return ImageFont.load_default()

    width, height = 1920, 1080
    thumb = Image.new("RGB", (width, height), color=(18, 14, 12))
    draw = ImageDraw.Draw(thumb)

    thumb_spec = meta["thumbnail_specification"]
    prog_fmt = thumb_spec.get("program_format", "TUE_STORY_DRAMA")
    if prog_fmt == "FRI_LYRIC_ANATOMY":
        left_bg, left_poly, badge_bg = (38, 16, 22), (62, 26, 36), (168, 42, 68)
    elif prog_fmt == "FRI_CONCERT_GUIDE":
        left_bg, left_poly, badge_bg = (16, 28, 48), (28, 48, 78), (32, 108, 168)
    else:
        left_bg, left_poly, badge_bg = (14, 38, 28), (24, 58, 42), (185, 82, 24)

    draw.rectangle([(0, 0), (1050, 1080)], fill=left_bg)
    draw.polygon([(0, 0), (620, 0), (960, 1080), (280, 1080)], fill=left_poly)

    ep_num = int(meta.get("episode_number", 1))
    assets_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
    portrait_candidates = [
        os.path.join(assets_root, "characters", "sprite_hwang_young_woong.png"),
        os.path.join(assets_root, "hero_main.png"),
    ]
    chosen_portrait = portrait_candidates[(ep_num - 1) % len(portrait_candidates)] if ep_num >= 6 else portrait_candidates[0]
    if not os.path.exists(chosen_portrait):
        chosen_portrait = portrait_candidates[0]
    if os.path.exists(chosen_portrait):
        try:
            sp = Image.open(chosen_portrait).convert("RGBA")
            if chosen_portrait.endswith("hero_main.png"):
                # Center-crop/scale hero_main into the left 1050x1080 stage cleanly
                sp = sp.resize((1050, 1080), Image.Resampling.LANCZOS)
                thumb.paste(sp, (0, 0))
                overlay = Image.new("RGBA", (1050, 1080), (10, 22, 16, 55))
                thumb.paste(Image.alpha_composite(thumb.crop((0, 0, 1050, 1080)).convert("RGBA"), overlay).convert("RGB"), (0, 0))
            else:
                sp = sp.resize((760, 1010), Image.Resampling.LANCZOS)
                thumb.paste(sp, (140, 50), sp)
        except Exception:
            pass

    draw = ImageDraw.Draw(thumb)
    draw.rectangle([(1050, 0), (1920, 1080)], fill=(20, 15, 14))
    draw.line([(1050, 0), (1050, 1080)], fill=(241, 196, 15), width=5)

    draw.rounded_rectangle([(1110, 95), (1855, 188)], radius=18, fill=badge_bg)
    draw.text((1145, 117), thumb_spec["top_amber_badge"], font=_font(40), fill=(255, 255, 255))

    hl1 = thumb_spec.get("headline_line1", "어머니,")
    hl2 = thumb_spec.get("headline_line2", "이젠 울지 마세요")
    hl_font_sz = 62 if max(len(hl1), len(hl2)) >= 11 else 72
    draw.rounded_rectangle([(1110, 225), (1855, 535)], radius=22, fill=(28, 20, 18), outline=(241, 196, 15), width=4)
    draw.text((1142, 272), hl1[:13], font=_font(hl_font_sz), fill=(241, 196, 15))
    draw.text((1142, 392), hl2[:13], font=_font(hl_font_sz), fill=(255, 255, 255) if ep_num >= 6 else (241, 196, 15))

    sub_txt = thumb_spec.get("sub_headline", "보이는 사연 라디오 3편 & 반가운 소식 2건")
    if "|" in sub_txt:
        s_part1, s_part2 = [x.strip() for x in sub_txt.split("|", 1)]
    elif ep_num == 1:
        s_part1, s_part2 = "보이는 사연 라디오 3편", "& 황영웅 반가운 소식 2건"
    else:
        s_part1, s_part2 = sub_txt[:17], "화·금 저녁 6시 정규 본방송"

    draw.rounded_rectangle([(1110, 575), (1855, 745)], radius=18, fill=(245, 242, 235))
    draw.text((1142, 602), s_part1[:18], font=_font(42), fill=(15, 15, 15))
    draw.text((1142, 668), s_part2[:19], font=_font(40), fill=(165, 24, 24))

    draw.rounded_rectangle([(1110, 795), (1855, 965)], radius=18, fill=(14, 52, 36), outline=(46, 204, 113), width=3)
    draw.text((1145, 822), "무료 화보 기념사진관 & 안심 혜택관", font=_font(35), fill=(255, 232, 110))
    draw.text((1145, 882), "paradise-hero.com", font=_font(38), fill=(255, 255, 255))

    draw.rectangle([(15, 15), (1905, 1065)], outline=(241, 196, 15), width=4)
    thumb.save(output_path, "PNG")
    print(f"[+] Saved 1080p high-CTR YouTube thumbnail to: {output_path} ({os.path.getsize(output_path)} bytes)")


def main():
    parser = argparse.ArgumentParser(description="@김쌤의영웅라디오 YouTube Metadata Packager")
    parser.add_argument("--script-file", type=str, default="", help="Path to script_epXX.json")
    parser.add_argument("--video-plan", type=str, default="", help="Path to video_assembly_plan.json")
    parser.add_argument("--publish-at", type=str, default="", help="Explicit ISO-8601 publishAt timestamp (e.g. 2026-11-17T18:00:00+09:00)")
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
        plan_cand = os.path.join(base_dir, "video_assembly_plan.json")
        if os.path.exists(plan_cand):
            with open(plan_cand, "r", encoding="utf-8") as f:
                video_plan = json.load(f)

    ep_num = script_data.get("episode_number", 1)
    print(f"[*] Packaging YouTube Longform metadata for Episode {ep_num}...")
    meta = build_youtube_metadata(script_data, video_plan, publish_at_override=args.publish_at)

    meta_json_path = os.path.join(base_dir, "youtube_metadata.json")
    with open(meta_json_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved metadata JSON to: {meta_json_path}")

    thumb_path = os.path.join(base_dir, f"thumbnail_ep{ep_num:02d}_1080p.png")
    render_sample_thumbnail(meta, thumb_path)
    if ep_num != 1:
        # Also maintain compatibility if ep01 path is checked
        pass

    meta_txt_path = os.path.join(base_dir, "youtube_upload_kit.txt")
    with open(meta_txt_path, "w", encoding="utf-8") as f:
        f.write("=== YOUTUBE LONGFORM TITLE ===\n")
        f.write(meta["title"] + "\n\n")
        f.write("=== SCHEDULED PUBLISH AT (Tue/Fri 18:00 KST) ===\n")
        f.write(meta["publishAt"] + "\n\n")
        f.write("=== YOUTUBE DESCRIPTION ===\n")
        f.write(meta["description"] + "\n\n")
        f.write("=== PINNED COMMENT (Auto-Register First Comment) ===\n")
        f.write(meta["pinned_comment"] + "\n\n")
        f.write("=== FIXED TAGS ===\n")
        f.write(", ".join(meta["tags"]) + "\n")
    print(f"[+] Saved upload kit text to: {meta_txt_path}")
    print("[SUCCESS] YouTube metadata, pinned comment & conversion kit packaging complete.")


if __name__ == "__main__":
    main()
