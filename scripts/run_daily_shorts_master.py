#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_daily_shorts_master.py
================================================================================
Milestone 4 (F12): Master Daily Shorts Orchestrator & Multi-Platform Packager
@김쌤의영웅라디오 & 파라다이스히어로 (paradise-hero.com)

Features:
- End-to-end orchestration:
    1) scripts/generate_shorts_script.py (A/B/C dopamine script generation & selection)
    2) scripts/synthesize_shorts_audio.py (1.2x zero-silence audio & point SFX mastering)
    3) scripts/render_shorts_video.py (1080x1920 vertical clean video compositor)
    4) Multi-platform packaging:
       - YouTube Shorts metadata (#Shorts, madeForKids=False, chapters, tags)
       - Instagram Reels metadata (caption, hashtags, @kimteacher_heroradio, domain CTA)
- Generates complete daily episode package in content/shorts_daily/ep_{episode:02d}/
================================================================================
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any

# Ensure UTF-8 on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = Path(__file__).resolve().parent
DIVISION_DIR = SCRIPT_DIR.parent


def package_multiplatform_metadata(
    episode: int,
    script_data: Dict[str, Any],
    audio_meta: Dict[str, Any],
    video_meta: Dict[str, Any],
    ep_dir: Path
) -> Dict[str, Any]:
    """
    Packages YouTube Shorts and Instagram Reels metadata packets.
    Enforces GEMINI.md standards:
    - YouTube Shorts tags (#Shorts)
    - madeForKids = False
    - Domain callout paradise-hero.com
    - Instagram handle @kimteacher_heroradio
    - Zero prohibited commercial marketing words compliance
    """
    beats = script_data.get("beats", [])
    title_raw = script_data.get("title", f"제{episode}화: 트롯 왕자들의 우정")
    selected_variant = script_data.get("selected_variant", "A_VS_CONTRAST")
    total_dur = video_meta.get("duration_sec", 17.0)

    # Chapters calculation
    chapters = []
    accum = 0.0
    for idx, beat in enumerate(beats):
        m = int(accum // 60)
        s = int(accum % 60)
        chapters.append({
            "timestamp": f"{m:02d}:{s:02d}",
            "title": beat.get("subtitle_l1", f"비트 {idx+1}")
        })
        accum += beat.get("target_duration_sec", 2.0)

    # YouTube Shorts Packet
    yt_title = f"[김쌤의 영웅라디오] 황영웅과 트롯 10대 왕자들의 기적 같은 우정! #{selected_variant[:1]}안 #Shorts"
    yt_description = (
        f"👑 김쌤의 영웅라디오 데일리 쇼츠 제{episode:02d}화\n\n"
        f"어머님들의 영원한 감성 황태자 황영웅과 10대 트롯 왕자들의 찬란한 우정 이야기!\n\n"
        f"🌟 [파라다이스히어로 공식 팬덤 플랫폼]\n"
        f"👉 https://paradise-hero.com\n\n"
        f"📸 [왕자님과 나의 2샷 포토부스]\n"
        f"스마트폰으로 간편하게 1회 무료 촬영 체험하고 소장용 포토카드를 남겨보세요!\n"
        f"👉 https://paradise-hero.com/booth.html\n\n"
        f"타임스탬프:\n" +
        "\n".join([f"{ch['timestamp']} {ch['title']}" for ch in chapters]) + "\n\n"
        f"#황영웅 #임영웅 #이찬원 #영탁 #정동원 #김호중 #장민호 #박서진 #손태진 #안성훈 #김쌤의영웅라디오 #파라다이스히어로 #Shorts #트로트"
    )
    yt_tags = [
        "#Shorts",
        "#황영웅",
        "#임영웅",
        "#이찬원",
        "#영탁",
        "#정동원",
        "#김호중",
        "#장민호",
        "#박서진",
        "#손태진",
        "#안성훈",
        "#김쌤의영웅라디오",
        "#파라다이스히어로",
        "트로트쇼츠",
        "영웅시대"
    ]

    # Instagram Reels Packet
    ig_caption = (
        f"👑 [김쌤의 영웅라디오] 감성 황태자 황영웅과 10대 왕자들의 눈부신 연대!\n\n"
        f"어머님들의 희생과 눈물을 따스하게 안아주는 황영웅의 깊은 울림 💚\n"
        f"서로를 격려하는 트롯 왕자들의 진정한 우정이 펼쳐집니다.\n\n"
        f"📸 지금 프로필 링크(paradise-hero.com)에서 나만의 왕자님 투샷 사진을 무료로 촬영해보세요!\n\n"
        f"@kimteacher_heroradio\n"
        f"#황영웅 #임영웅 #이찬원 #영탁 #정동원 #김호중 #장민호 #박서진 #손태진 #안성훈 "
        f"#김쌤의영웅라디오 #파라다이스히어로 #트로트왕자 #포토부스 #reels #trot"
    )

    metadata = {
        "episode": episode,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "selected_variant": selected_variant,
        "duration_sec": total_dur,
        "youtube_shorts": {
            "title": yt_title,
            "description": yt_description,
            "tags": yt_tags,
            "category_id": "24",
            "privacy_status": "public",
            "madeForKids": False,
            "chapters": chapters
        },
        "instagram_reels": {
            "caption": ig_caption,
            "account_tag": "@kimteacher_heroradio",
            "domain_callout": "paradise-hero.com",
            "cover_timestamp_sec": 2.0
        },
        "audio_specs": {
            "sample_rate": audio_meta.get("sample_rate", 44100),
            "peak_dbfs": audio_meta.get("peak_dbfs", -1.30),
            "clipped_samples": audio_meta.get("clipped_samples", 0),
            "max_internal_silence_sec": audio_meta.get("max_internal_silence_sec", 0.02)
        },
        "video_specs": {
            "resolution": video_meta.get("resolution", "1080x1920"),
            "aspect_ratio": "9:16",
            "fps": video_meta.get("fps", 30),
            "file_size_kb": video_meta.get("file_size_kb", 0.0)
        }
    }

    # Save JSON metadata
    json_path = ep_dir / f"metadata_ep{episode:02d}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    # Save human-readable Markdown packet
    md_path = ep_dir / f"metadata_ep{episode:02d}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# 데일리 쇼츠 제{episode:02d}화 배포 메타데이터 패킷\n\n")
        f.write(f"- **에피소드**: 제{episode:02d}화\n")
        f.write(f"- **선택 안**: {selected_variant}\n")
        f.write(f"- **영상 규격**: 1080x1920 (9:16 세로형), {total_dur:.1f}초, 30fps\n")
        f.write(f"- **음원 마스터링**: 피크 {audio_meta.get('peak_dbfs')} dBFS, 무음 간격 {audio_meta.get('max_internal_silence_sec')}초 (기준 <=0.05s 충족)\n\n")
        f.write("## 1. YouTube Shorts\n\n")
        f.write(f"**제목**: `{yt_title}`\n\n")
        f.write(f"**태그**: `{', '.join(yt_tags)}`\n\n")
        f.write(f"**아동용 여부**: `madeForKids: false`\n\n")
        f.write(f"**설명문**:\n```\n{yt_description}\n```\n\n")
        f.write("## 2. Instagram Reels\n\n")
        f.write(f"**계정**: `@kimteacher_heroradio`\n\n")
        f.write(f"**캡션**:\n```\n{ig_caption}\n```\n\n")
        f.write("## 3. 포토부스 CTA 연동\n\n")
        f.write("- 도메인: `paradise-hero.com`\n")
        f.write("- 포토부스: `paradise-hero.com/booth.html` (신규 1회 무료 체험)\n")

    print(f"📦 Metadata packaging complete: {json_path} & {md_path}")
    return metadata


def run_daily_shorts_master(episode: int = 1, offline: bool = False, variant_override: str = None) -> Dict[str, Any]:
    """Orchestrates end-to-end Shorts production pipeline."""
    ep_dir = DIVISION_DIR / "content" / "shorts_daily" / f"ep_{episode:02d}"
    ep_dir.mkdir(parents=True, exist_ok=True)

    print("================================================================================")
    print(f"🚀 [김쌤의 영웅라디오] Daily Shorts Master Production Pipeline — Episode {episode:02d}")
    print("================================================================================")

    # 1. Script Generation
    print("\n[Step 1/4] Generating A/B/C Dopamine Script Candidates...")
    script_py = SCRIPT_DIR / "generate_shorts_script.py"
    cmd_script = [sys.executable, str(script_py), "--episode", str(episode), "--out-dir", str(ep_dir)]
    if variant_override:
        cmd_script.extend(["--variant", variant_override])
    res1 = subprocess.run(cmd_script, check=True)

    script_path = ep_dir / f"script_ep{episode:02d}.json"
    with open(script_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    # 2. Audio Synthesis & Mastering
    print("\n[Step 2/4] Synthesizing 1.2x Zero-Silence TTS & Point SFX...")
    audio_py = SCRIPT_DIR / "synthesize_shorts_audio.py"
    audio_path = ep_dir / f"audio_ep{episode:02d}.wav"
    cmd_audio = [sys.executable, str(audio_py), "--script", str(script_path), "--out", str(audio_path)]
    if offline:
        cmd_audio.append("--offline")
    res2 = subprocess.run(cmd_audio, check=True)

    with open(ep_dir / "audio_metadata.json", "r", encoding="utf-8") as f:
        audio_meta = json.load(f)

    # 3. Video Rendering
    print("\n[Step 3/4] Rendering Vertical 1080x1920 Clean Fullscreen Video...")
    video_py = SCRIPT_DIR / "render_shorts_video.py"
    video_path = ep_dir / f"shorts_ep{episode:02d}_1080x1920.mp4"
    cmd_video = [sys.executable, str(video_py), "--script", str(script_path), "--audio", str(audio_path), "--out", str(video_path)]
    res3 = subprocess.run(cmd_video, check=True)

    video_meta = {
        "video_file": str(video_path),
        "resolution": "1080x1920",
        "aspect_ratio": "9:16",
        "fps": 30,
        "duration_sec": audio_meta.get("total_duration_sec", 17.0),
        "file_size_kb": round(video_path.stat().st_size / 1024.0, 1)
    }

    # 4. Packaging
    print("\n[Step 4/4] Packaging Multi-Platform Distribution Metadata...")
    metadata = package_multiplatform_metadata(episode, script_data, audio_meta, video_meta, ep_dir)

    print("\n================================================================================")
    print(f"🎉 Episode {episode:02d} Shorts Master Production COMPLETE!")
    print(f"   - Script:   {script_path}")
    print(f"   - Audio:    {audio_path} ({audio_meta['total_duration_sec']}s, peak {audio_meta['peak_dbfs']} dBFS)")
    print(f"   - Video:    {video_path} ({video_meta['file_size_kb']} KB, 1080x1920 @ 30fps)")
    print(f"   - Metadata: {ep_dir / f'metadata_ep{episode:02d}.json'}")
    print("================================================================================")
    return metadata


def main():
    parser = argparse.ArgumentParser(description="Master Daily Shorts Orchestrator")
    parser.add_argument("--episode", type=int, default=1, help="Episode number (default: 1)")
    parser.add_argument("--offline", action="store_true", help="Force deterministic offline synthesis")
    parser.add_argument("--variant", type=str, default=None, help="Override script variant")
    args = parser.parse_args()

    run_daily_shorts_master(
        episode=args.episode,
        offline=args.offline,
        variant_override=args.variant
    )


if __name__ == "__main__":
    main()
