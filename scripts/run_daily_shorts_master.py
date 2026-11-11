#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_daily_shorts_master.py
================================================================================
@김쌤의영웅라디오 — 시니어 맞춤 쇼츠 & 네이버 클립 일일 마스터 오케스트레이터 (2026-11-11 개조판)

핵심 규격:
1. 해시태그 고정: #황영웅 #파라다이스 #트로트 #감동사연 #시니어유튜브
   - 절대 금지 태그(#영상툰, #애니메이션, #웹툰, '트롯 10대 왕자', 타 가수명) 원천 차단
2. 제목 공식 (50자 이내):
   [눈물주의/심야라디오/감동실화/단독소식] "직접 인용구" #황영웅 #파라다이스
3. 쇼츠 관련 동영상(Related Video) 브릿지:
   - 채널 최신 롱폼 라디오 영상(기본값 lGkMncY4u1o)으로 자동 연결
4. 예약 발행 시각 고정 (publishAt):
   - 매일 19:30 KST (한국 5070 시니어 저녁 골든타임)
5. 네이버 클립(Clip) 동시 배포 패키지:
   - 클린 MP4(shorts_epXX_naver_clip_clean.mp4) + 네이버 공식 크리에이터샵(https://cshop.naver.com/paradiseshop) 연동
================================================================================
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = Path(__file__).resolve().parent
DIVISION_DIR = SCRIPT_DIR.parent

KST = timezone(timedelta(hours=9))
FIXED_HASHTAGS = ["#황영웅", "#파라다이스", "#트로트", "#감동사연", "#시니어유튜브"]
DEFAULT_RELATED_LONGFORM_VIDEO_ID = "lGkMncY4u1o"


def compute_next_shorts_publish_at_kst(now_kst: datetime = None) -> str:
    """Computes next daily 19:30 KST ISO-8601 publishAt timestamp."""
    now_kst = now_kst or datetime.now(KST)
    target = now_kst.replace(hour=19, minute=30, second=0, microsecond=0)
    if target <= now_kst + timedelta(minutes=15):
        target += timedelta(days=1)
    return target.isoformat()


def package_multiplatform_metadata(
    episode: int,
    script_data: Dict[str, Any],
    audio_meta: Dict[str, Any],
    video_meta: Dict[str, Any],
    ep_dir: Path,
    related_video_id: str = DEFAULT_RELATED_LONGFORM_VIDEO_ID,
) -> Dict[str, Any]:
    """
    Packages YouTube Shorts, Naver Clip, and Instagram Reels metadata packets.
    """
    beats = script_data.get("beats", [])
    selected_variant = script_data.get("selected_variant", "A_VS_CONTRAST")
    total_dur = video_meta.get("duration_sec", audio_meta.get("total_duration_sec", 35.0))
    publish_at_kst = compute_next_shorts_publish_at_kst()

    chapters = []
    accum = 0.0
    beat_durs = audio_meta.get("beat_durations_sec", [b.get("target_duration_sec", 3.8) for b in beats])
    for idx, beat in enumerate(beats):
        m = int(accum // 60)
        s = int(accum % 60)
        chapters.append({
            "timestamp": f"{m:02d}:{s:02d}",
            "title": beat.get("subtitle_l1", f"장면 {idx + 1}"),
        })
        accum += beat_durs[idx] if idx < len(beat_durs) else beat.get("target_duration_sec", 3.8)

    yt_title = script_data.get("youtube_title") or script_data.get("title") or '[심야라디오] "엄마 이제 제가 당신 편이오" #황영웅 #파라다이스'
    yt_title = yt_title[:50]

    hashtags_line = " ".join(FIXED_HASHTAGS)
    yt_description = (
        f"📻 김쌤의 심야 영웅라디오 제{episode:02d}화\n"
        f"가수 황영웅 님의 깊은 목소리와 파라다이스 어머님들의 따뜻한 인생 사연을 전해드립니다.\n\n"
        f"💚 [황영웅 무료 화보 투샷 사진관 & 공식 팬 쉼터]\n"
        f"👉 https://paradise-hero.com/booth.html\n\n"
        f"💌 [김쌤 라디오에 내 사연 보내기]\n"
        f"👉 https://paradise-hero.com/story.html\n\n"
        f"🎬 [15분 풀버전 보이는 사연 라디오 본방송 듣기]\n"
        f"👉 https://www.youtube.com/watch?v={related_video_id}\n\n"
        f"타임스탬프:\n"
        + "\n".join([f"{ch['timestamp']} {ch['title']}" for ch in chapters])
        + f"\n\n{hashtags_line}"
    )

    yt_tags = FIXED_HASHTAGS.copy()

    ig_caption = (
        f"📻 [김쌤의 심야 영웅라디오] 어머님들의 마음을 따뜻하게 안아주는 가수 황영웅 이야기 💚\n\n"
        f"지금 프로필 링크(paradise-hero.com)에서 영웅님 10종 의상 무료 화보 기념사진도 편하게 찍어보세요!\n\n"
        f"@kimteacher_heroradio\n"
        f"{hashtags_line}"
    )

    naver_clip_caption = (
        f"{yt_title}\n"
        f"김쌤이 어머님들 눈·관절 건강과 콘서트 응원 필수품만 엄선한 공식 크리에이터샵도 함께 만나보세요 💚\n"
        f"👉 https://cshop.naver.com/paradiseshop\n"
        f"(네이버 쇼핑 커넥트 활동의 일환으로 판매 발생 시 소정의 수수료를 제공받습니다.)\n"
        f"{hashtags_line}"
    )

    metadata = {
        "episode": episode,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "selected_variant": selected_variant,
        "duration_sec": total_dur,
        "schedule_policy": {
            "shorts_daily_kst": "19:30 KST",
            "longform_tue_fri_kst": "18:00 KST",
            "publishAt": publish_at_kst,
        },
        "youtube_shorts": {
            "title": yt_title,
            "title_length": len(yt_title),
            "description": yt_description,
            "tags": yt_tags,
            "category_id": "24",
            "privacy_status": "private",
            "publishAt": publish_at_kst,
            "madeForKids": False,
            "related_video_id": related_video_id,
            "related_video_url": f"https://www.youtube.com/watch?v={related_video_id}",
            "chapters": chapters,
        },
        "naver_clip": {
            "clean_video_file": video_meta.get("naver_clip_clean_file", ""),
            "title": yt_title,
            "caption": naver_clip_caption,
            "creator_shop_url": "https://cshop.naver.com/paradiseshop",
            "shopping_connect_disclosure": "네이버 쇼핑 커넥트 활동의 일환으로 판매 발생 시 소정의 수수료를 제공받습니다.",
            "hashtags": FIXED_HASHTAGS,
        },
        "instagram_reels": {
            "caption": ig_caption,
            "account_tag": "@kimteacher_heroradio",
            "domain_callout": "paradise-hero.com",
            "cover_timestamp_sec": 2.0,
        },
        "audio_specs": {
            "sample_rate": audio_meta.get("sample_rate", 44100),
            "speech_rate": audio_meta.get("speech_rate", "+0%"),
            "peak_dbfs": audio_meta.get("peak_dbfs", -1.30),
            "clipped_samples": audio_meta.get("clipped_samples", 0),
            "max_internal_silence_sec": audio_meta.get("max_internal_silence_sec", 0.02),
            "full_narration_completion_compliant": audio_meta.get("full_narration_completion_compliant", True),
        },
        "video_specs": {
            "resolution": video_meta.get("resolution", "1080x1920"),
            "aspect_ratio": "9:16",
            "fps": video_meta.get("fps", 30),
            "file_size_kb": video_meta.get("file_size_kb", 0.0),
            "naver_clip_size_kb": video_meta.get("naver_clip_size_kb", 0.0),
            "top_plaque_text": video_meta.get("top_plaque_text", "📻 김쌤의 심야 영웅라디오"),
            "subtitle_center_y": video_meta.get("subtitle_center_y", 1005),
            "subtitle_font_pt": video_meta.get("subtitle_font_pt", 108),
            "subtitle_stroke_px": video_meta.get("subtitle_stroke_px", 12),
            "speech_bubbles_present": False,
        },
    }

    json_path = ep_dir / f"metadata_ep{episode:02d}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    md_path = ep_dir / f"metadata_ep{episode:02d}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# 데일리 시니어 쇼츠 & 네이버 클립 제{episode:02d}화 배포 패키지\n\n")
        f.write(f"- **에피소드**: 제{episode:02d}화 ({selected_variant})\n")
        f.write(f"- **예약 발행(`publishAt`)**: `{publish_at_kst}` (매일 19:30 KST 고정)\n")
        f.write(f"- **관련 롱폼 연결(`Related Video`)**: `{related_video_id}`\n")
        f.write(f"- **영상 규격**: 1080x1920 (9:16), {total_dur:.1f}초 (기준 30~42초), 30fps\n")
        f.write(f"- **자막 규격**: 중앙 Y=960~1050, 108pt 볼드 + 12px 외곽선 + 반투명 바\n\n")
        f.write("## 1. YouTube Shorts\n\n")
        f.write(f"**제목 ({len(yt_title)}자)**: `{yt_title}`\n\n")
        f.write(f"**고정 태그**: `{', '.join(yt_tags)}`\n\n")
        f.write(f"**설명문**:\n```\n{yt_description}\n```\n\n")
        f.write("## 2. Naver Clip (클린 MP4 + 쇼핑 커넥트)\n\n")
        f.write(f"- **클린 영상 파일**: `{video_meta.get('naver_clip_clean_file', '')}`\n")
        f.write(f"- **크리에이터샵**: `https://cshop.naver.com/paradiseshop`\n\n")
        f.write("## 3. Instagram Reels\n\n")
        f.write(f"**캡션**:\n```\n{ig_caption}\n```\n")

    print(f"📦 Metadata packaging complete: {json_path} & {md_path}")
    return metadata


def run_daily_shorts_master(
    episode: int = 1,
    offline: bool = False,
    variant_override: str = None,
    related_video_id: str = DEFAULT_RELATED_LONGFORM_VIDEO_ID,
) -> Dict[str, Any]:
    """Orchestrates end-to-end 6070 Senior Shorts & Naver Clip production pipeline."""
    ep_dir = DIVISION_DIR / "content" / "shorts_daily" / f"ep_{episode:02d}"
    ep_dir.mkdir(parents=True, exist_ok=True)

    print("================================================================================")
    print(f"🚀 [김쌤의 심야 영웅라디오] 6070 Senior Shorts & Naver Clip Pipeline — Episode {episode:02d}")
    print("================================================================================")

    # 1. Script Generation
    print("\n[Step 1/4] Generating Hwang Young-woong Solo Story/News Script...")
    script_py = SCRIPT_DIR / "generate_shorts_script.py"
    cmd_script = [sys.executable, str(script_py), "--episode", str(episode), "--out-dir", str(ep_dir)]
    if variant_override:
        cmd_script.extend(["--variant", variant_override])
    subprocess.run(cmd_script, check=True)

    script_path = ep_dir / f"script_ep{episode:02d}.json"
    with open(script_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    # 2. Audio Synthesis & Mastering
    print("\n[Step 2/4] Synthesizing Natural-Rate TTS (seg_dur >= tts_dur + 0.22s) & Point SFX...")
    audio_py = SCRIPT_DIR / "synthesize_shorts_audio.py"
    audio_path = ep_dir / f"audio_ep{episode:02d}.wav"
    cmd_audio = [sys.executable, str(audio_py), "--script", str(script_path), "--out", str(audio_path)]
    if offline:
        cmd_audio.append("--offline")
    subprocess.run(cmd_audio, check=True)

    with open(ep_dir / "audio_metadata.json", "r", encoding="utf-8") as f:
        audio_meta = json.load(f)

    # 3. Video Rendering (YouTube Shorts + Naver Clip Clean MP4)
    print("\n[Step 3/4] Rendering 1080x1920 Senior Video + Naver Clip Clean MP4...")
    video_py = SCRIPT_DIR / "render_shorts_video.py"
    video_path = ep_dir / f"shorts_ep{episode:02d}_1080x1920.mp4"
    naver_clip_path = ep_dir / f"shorts_ep{episode:02d}_naver_clip_clean.mp4"
    cmd_video = [
        sys.executable,
        str(video_py),
        "--script", str(script_path),
        "--audio", str(audio_path),
        "--out", str(video_path),
        "--naver-clip-out", str(naver_clip_path),
    ]
    subprocess.run(cmd_video, check=True)

    video_meta_file = ep_dir / "video_metadata.json"
    if video_meta_file.exists():
        video_meta = json.loads(video_meta_file.read_text(encoding="utf-8"))
    else:
        video_meta = {
            "video_file": str(video_path),
            "naver_clip_clean_file": str(naver_clip_path),
            "resolution": "1080x1920",
            "aspect_ratio": "9:16",
            "fps": 30,
            "duration_sec": audio_meta.get("total_duration_sec", 35.0),
            "file_size_kb": round(video_path.stat().st_size / 1024.0, 1),
            "naver_clip_size_kb": round(naver_clip_path.stat().st_size / 1024.0, 1),
        }

    # 4. Packaging
    print("\n[Step 4/4] Packaging YouTube Shorts (19:30 KST) & Naver Clip Metadata...")
    metadata = package_multiplatform_metadata(
        episode, script_data, audio_meta, video_meta, ep_dir, related_video_id=related_video_id
    )

    print("\n================================================================================")
    print(f"🎉 Episode {episode:02d} Senior Shorts + Naver Clip Production COMPLETE!")
    print(f"   - Title:       {metadata['youtube_shorts']['title']} ({metadata['youtube_shorts']['title_length']} chars)")
    print(f"   - PublishAt:   {metadata['youtube_shorts']['publishAt']} (Related: {related_video_id})")
    print(f"   - Audio:       {audio_path} ({audio_meta['total_duration_sec']}s, peak {audio_meta['peak_dbfs']} dBFS)")
    print(f"   - YT Shorts:   {video_path} ({video_meta['file_size_kb']} KB)")
    print(f"   - Naver Clip:  {naver_clip_path} ({video_meta['naver_clip_size_kb']} KB)")
    print("================================================================================")
    return metadata


def main():
    parser = argparse.ArgumentParser(description="Master Daily 6070 Senior Shorts & Naver Clip Orchestrator")
    parser.add_argument("--episode", type=int, default=1, help="Episode number (default: 1)")
    parser.add_argument("--offline", action="store_true", help="Force deterministic offline synthesis")
    parser.add_argument("--variant", type=str, default=None, help="Override script variant")
    parser.add_argument("--related-video-id", type=str, default=DEFAULT_RELATED_LONGFORM_VIDEO_ID, help="Latest Longform Video ID")
    args = parser.parse_args()

    run_daily_shorts_master(
        episode=args.episode,
        offline=args.offline,
        variant_override=args.variant,
        related_video_id=args.related_video_id,
    )


if __name__ == "__main__":
    main()
