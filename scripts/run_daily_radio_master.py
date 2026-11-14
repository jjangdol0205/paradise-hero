#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_daily_radio_master.py
@김쌤의영웅라디오 — 주 2~3회(화·금 18:00 KST) 12~20분 가로형(1920x1080) 보이는 사연 라디오 마스터 파이프라인

실행 순서:
1. 대본 생성 (generate_radio_script.py — story.html 사연 3편 + news.html 소식 2건 통합)
2. 음성 합성 (synthesize_radio_audio.py — DJ 김쌤 & 사연 어머님 Edge-TTS + BGM 덕킹)
3. 가로형 1920x1080 진공관 라디오 부스 + 우측 72pt+ 왕글씨 자막 렌더링 (render_radio_video.py)
4. 유튜브 메타데이터·예약시간(화·금 18:00 KST)·고정댓글(booth.html + cshop.naver.com/paradiseshop) 패키징 (package_youtube_metadata.py)
"""

import os
import sys
import json
import subprocess
import argparse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def run_pipeline(
    episode_num: int,
    sample_audio: bool = False,
    skip_mp4: bool = False,
    no_tts: bool = False,
    slot_day: str = "AUTO",
    publish_at: str = "",
):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    content_dir = os.path.abspath(os.path.join(base_dir, "..", "content", f"episode_{episode_num:02d}"))
    os.makedirs(content_dir, exist_ok=True)

    print("==================================================================")
    print(f"[*] Starting @김쌤의영웅라디오 1920x1080 Visible Story Radio Pipeline (Episode {episode_num} / Slot {slot_day})")
    print(f"[*] Schedule Policy: 매주 화·금 18:00 KST 정규 편성 | Output: {content_dir}")
    print("==================================================================\n")

    python_exe = sys.executable

    # Step 1: Script Generation (3 Stories + 2 News)
    print(">>> [Step 1/4] Generating 12~20min Radio Script (3 Stories + 2 News)...")
    script_gen = os.path.join(base_dir, "generate_radio_script.py")
    cmd1 = [python_exe, script_gen, "--episode", str(episode_num), "--slot-day", slot_day, "--output-dir", content_dir]
    res1 = subprocess.run(cmd1, capture_output=True, text=True, encoding="utf-8")
    print(res1.stdout)
    if res1.returncode != 0:
        print(f"[ERROR] Script generation failed:\n{res1.stderr}")
        return False

    script_json = os.path.join(content_dir, f"script_ep{episode_num:02d}.json")

    # Step 2: Audio Synthesis
    print(">>> [Step 2/4] Synthesizing Audio Narration & BGM Ducking Plan...")
    audio_synth = os.path.join(base_dir, "synthesize_radio_audio.py")
    cmd2 = [python_exe, audio_synth, "--script-file", script_json, "--output-dir", content_dir]
    if sample_audio:
        cmd2.append("--sample-only")
    res2 = subprocess.run(cmd2, capture_output=True, text=True, encoding="utf-8")
    print(res2.stdout)
    if res2.returncode != 0:
        print(f"[ERROR] Audio synthesis failed:\n{res2.stderr}")
        return False

    narration_json = os.path.join(content_dir, "narration_prompts.json")

    # Step 3: Video Assembly & Vacuum-Tube Booth 72pt+ Right Subtitle Render
    print(">>> [Step 3/4] Rendering 1920x1080 Vacuum-Tube Booth & Right 72pt+ Story Subtitles...")
    video_render = os.path.join(base_dir, "render_radio_video.py")
    cmd3 = [python_exe, video_render, "--script-file", script_json, "--narration-file", narration_json, "--output-dir", content_dir]
    if skip_mp4:
        cmd3.append("--skip-mp4")
    res3 = subprocess.run(cmd3, capture_output=True, text=True, encoding="utf-8")
    print(res3.stdout)
    if res3.returncode != 0:
        print(f"[ERROR] Video assembly failed:\n{res3.stderr}")
        return False

    video_plan_json = os.path.join(content_dir, "video_assembly_plan.json")

    # Step 4: YouTube Metadata, Tue/Fri 18:00 KST Schedule & Pinned Comment Packaging
    print(">>> [Step 4/4] Packaging Metadata, Tue/Fri 18:00 KST Schedule & Pinned Comment...")
    pkg_meta = os.path.join(base_dir, "package_youtube_metadata.py")
    cmd4 = [python_exe, pkg_meta, "--script-file", script_json, "--video-plan", video_plan_json, "--output-dir", content_dir]
    if publish_at:
        cmd4.extend(["--publish-at", publish_at])
    res4 = subprocess.run(cmd4, capture_output=True, text=True, encoding="utf-8")
    print(res4.stdout)
    if res4.returncode != 0:
        print(f"[ERROR] Metadata packaging failed:\n{res4.stderr}")
        return False

    meta_json_path = os.path.join(content_dir, "youtube_metadata.json")
    if os.path.exists(meta_json_path):
        with open(meta_json_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        print(f"[+] Scheduled publishAt : {meta.get('publishAt')}")
        print(f"[+] Fixed Hashtags      : {', '.join(meta.get('tags', []))}")
        print(f"[+] Pinned Booth Link   : {meta.get('pinned_comment_booth_url')}")
        print(f"[+] Pinned C-Shop Link  : {meta.get('pinned_comment_creator_shop_url')}")
        print(f"[+] Pinned Coupang Link : {meta.get('pinned_comment_coupang_influencer_url')}")

    print("==================================================================")
    print(f"[SUCCESS] All 4 Longform Radio stages completed for Episode {episode_num}!")
    print(f"Artifacts located at: {content_dir}")
    print("==================================================================")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="@김쌤의영웅라디오 Master Longform Radio Runner")
    parser.add_argument("--episode", type=int, default=1, help="Episode number (default: 1)")
    parser.add_argument("--slot-day", type=str, default="AUTO", choices=["AUTO", "TUE", "FRI"], help="Broadcast slot day (TUE/FRI/AUTO)")
    parser.add_argument("--publish-at", type=str, default="", help="Explicit ISO-8601 publishAt timestamp")
    parser.add_argument("--full-audio", action="store_true", default=False, help="Synthesize all audio segments rather than sample")
    parser.add_argument("--skip-mp4", action="store_true", default=False, help="Generate script, plan, 1080p cards & metadata without MP4 encode")
    args = parser.parse_args()

    success = run_pipeline(
        args.episode,
        sample_audio=not args.full_audio,
        skip_mp4=args.skip_mp4,
        slot_day=args.slot_day,
        publish_at=args.publish_at,
    )
    sys.exit(0 if success else 1)
