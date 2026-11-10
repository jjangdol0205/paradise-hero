#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_daily_radio_master.py
@김쌤의영웅라디오 Master End-to-End Daily Pipeline Orchestrator

Executes the full production pipeline in sequence:
1. Script Generation (generate_radio_script.py)
2. Narration & Audio Synthesis (synthesize_radio_audio.py)
3. Video Assembly Planning & Visuals (render_radio_video.py)
4. YouTube Metadata & Upload Kit Packaging (package_youtube_metadata.py)
"""

import os
import sys
import subprocess
import argparse

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def run_pipeline(episode_num: int, sample_audio: bool = False):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    content_dir = os.path.abspath(os.path.join(base_dir, "..", "content", f"episode_{episode_num:02d}"))
    os.makedirs(content_dir, exist_ok=True)

    print("==================================================================")
    print(f"[*] Starting @김쌤의영웅라디오 Master Production Pipeline for Episode {episode_num}")
    print(f"[*] Output directory: {content_dir}")
    print("==================================================================\n")

    python_exe = sys.executable

    # Step 1: Script Generation
    print(">>> [Step 1/4] Generating 6-Chapter Radio Script...")
    script_gen = os.path.join(base_dir, "generate_radio_script.py")
    cmd1 = [python_exe, script_gen, "--episode", str(episode_num), "--output-dir", content_dir]
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

    # Step 3: Video Assembly Planning
    print(">>> [Step 3/4] Generating 16:9 Video Assembly Plan & 1080p Storyboard...")
    video_render = os.path.join(base_dir, "render_radio_video.py")
    cmd3 = [python_exe, video_render, "--script-file", script_json, "--narration-file", narration_json, "--output-dir", content_dir]
    res3 = subprocess.run(cmd3, capture_output=True, text=True, encoding="utf-8")
    print(res3.stdout)
    if res3.returncode != 0:
        print(f"[ERROR] Video assembly planning failed:\n{res3.stderr}")
        return False

    video_plan_json = os.path.join(content_dir, "video_assembly_plan.json")

    # Step 4: YouTube Metadata Packaging
    print(">>> [Step 4/4] Packaging High-CTR YouTube Metadata & Thumbnail...")
    pkg_meta = os.path.join(base_dir, "package_youtube_metadata.py")
    cmd4 = [python_exe, pkg_meta, "--script-file", script_json, "--video-plan", video_plan_json, "--output-dir", content_dir]
    res4 = subprocess.run(cmd4, capture_output=True, text=True, encoding="utf-8")
    print(res4.stdout)
    if res4.returncode != 0:
        print(f"[ERROR] Metadata packaging failed:\n{res4.stderr}")
        return False

    print("==================================================================")
    print(f"[SUCCESS] All 4 pipeline stages completed successfully for Episode {episode_num}!")
    print(f"Artifacts located at: {content_dir}")
    print("==================================================================")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="@김쌤의영웅라디오 Master Daily Pipeline Runner")
    parser.add_argument("--episode", type=int, default=1, help="Episode number (default: 1)")
    parser.add_argument("--full-audio", action="store_true", default=False, help="Synthesize all audio segments rather than sample")
    args = parser.parse_args()

    success = run_pipeline(args.episode, sample_audio=not args.full_audio)
    sys.exit(0 if success else 1)
