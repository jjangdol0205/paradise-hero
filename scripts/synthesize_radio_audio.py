#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
synthesize_radio_audio.py
@김쌤의영웅라디오 Edge-TTS Audio Narration & BGM Ducking Synthesis Engine

Voices:
- DJ 김쌤: ko-KR-InJoonNeural (rate="-4%", pitch="-2Hz")
- Fan Letter / 어머니: ko-KR-SunHiNeural (rate="-3%", pitch="-1Hz")
Audio Standard:
- Auto-Ducking: -22 dBFS during speech / -14 dBFS during pauses
- Master Loudness Target: -16 LUFS (±1.0 LUFS), True Peak -1.0 dBTP
- Sample Rate: 48,000 Hz, 16-bit
"""

import os
import sys
import json
import asyncio
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
    import edge_tts
except ImportError:
    edge_tts = None

VOICE_CONFIG = {
    "dj_kim": {
        "voice": "ko-KR-InJoonNeural",
        "rate": "-4%",
        "pitch": "-2Hz",
        "description": "DJ 김쌤 (따뜻하고 온화한 남성 중저음 진행자)"
    },
    "fan_letter_writer": {
        "voice": "ko-KR-SunHiNeural",
        "rate": "-3%",
        "pitch": "-1Hz",
        "description": "사연자 이순자 어머니 (따뜻하고 애절한 시니어 여성 낭독자)"
    }
}

DUCKING_SPEC = {
    "speech_active_bgm_db": -22.0,
    "speech_pause_bgm_db": -14.0,
    "duck_fade_in_ms": 300,
    "duck_fade_out_ms": 450,
    "master_integrated_lufs": -16.0,
    "true_peak_limit_db": -1.0,
    "sample_rate_hz": 48000
}


def build_narration_manifest(script_data: Dict[str, Any], audio_rel_dir: str = "audio") -> Dict[str, Any]:
    """
    Builds the complete narration prompts manifest and audio assembly plan from script data.
    """
    segments_manifest = []
    current_time_sec = 0.0

    chapters = script_data.get("chapters", [])
    for ch in chapters:
        ch_idx = ch["chapter_index"]
        ch_id = ch["chapter_id"]
        ch_title = ch["title"]
        bgm_mood = ch.get("bgm_mood", "warm_acoustic_guitar")

        # Musical intro bridge before speech starts in chapter
        intro_bridge_sec = 2.5 if ch_idx == 1 else 3.5
        current_time_sec += intro_bridge_sec

        for seg in ch["segments"]:
            speaker_key = seg["speaker"]
            v_conf = VOICE_CONFIG.get(speaker_key, VOICE_CONFIG["dj_kim"])
            duration_est = seg.get("estimated_duration_sec", 15.0)

            seg_start = round(current_time_sec, 2)
            seg_end = round(current_time_sec + duration_est, 2)

            audio_filename = f"{seg['segment_id']}_{speaker_key}.mp3"
            audio_path = os.path.join(audio_rel_dir, audio_filename).replace("\\", "/")

            manifest_entry = {
                "segment_id": seg["segment_id"],
                "chapter_index": ch_idx,
                "chapter_id": ch_id,
                "chapter_title": ch_title,
                "speaker": speaker_key,
                "speaker_title": seg.get("speaker_title", "진행자"),
                "voice_id": v_conf["voice"],
                "rate": v_conf["rate"],
                "pitch": v_conf["pitch"],
                "text": seg["text"],
                "pacing_pause_sec": seg.get("pacing_pause_sec", 1.0),
                "estimated_duration_sec": duration_est,
                "timeline_start_sec": seg_start,
                "timeline_end_sec": seg_end,
                "audio_rel_path": audio_path,
                "bgm_mood": bgm_mood,
                "ducking_profile": {
                    "bgm_gain_db": DUCKING_SPEC["speech_active_bgm_db"],
                    "post_pause_gain_db": DUCKING_SPEC["speech_pause_bgm_db"],
                    "fade_in_ms": DUCKING_SPEC["duck_fade_in_ms"],
                    "fade_out_ms": DUCKING_SPEC["duck_fade_out_ms"]
                }
            }
            segments_manifest.append(manifest_entry)
            current_time_sec = seg_end + seg.get("pacing_pause_sec", 1.0)

        # Musical outro bridge after chapter speech ends
        current_time_sec += 4.0

    total_broadcast_sec = round(current_time_sec, 2)

    manifest = {
        "channel_name": script_data.get("channel_name", "@김쌤의영웅라디오"),
        "episode_number": script_data.get("episode_number", 1),
        "episode_title": script_data.get("episode_title", ""),
        "total_segments": len(segments_manifest),
        "total_broadcast_duration_sec": total_broadcast_sec,
        "target_pacing_window_min": "12~18 min (720s ~ 1080s)",
        "voice_specifications": VOICE_CONFIG,
        "ducking_specifications": DUCKING_SPEC,
        "ffmpeg_ducking_recipe": (
            "ffmpeg -i narration_master.wav -i bgm_bed.wav "
            "-filter_complex \"[1:a]volume=-14dB[bgm_base];"
            "[0:a]asplit=2[narr_main][narr_sc];"
            "[bgm_base][narr_sc]sidechaincompress=threshold=0.03:ratio=8:attack=300:release=450[ducked_bgm];"
            "[ducked_bgm][narr_main]amix=inputs=2:duration=longest:dropout_transition=2[mixed];"
            "[mixed]loudnorm=I=-16:TP=-1.0:LRA=11[out]\" -map \"[out]\" mastered_broadcast_audio.wav"
        ),
        "segments": segments_manifest
    }

    return manifest


async def synthesize_segment(segment: Dict[str, Any], output_filepath: str):
    """
    Synthesizes a single narration segment using edge-tts.
    """
    if edge_tts is None:
        raise RuntimeError("edge_tts module is not installed.")

    communicate = edge_tts.Communicate(
        text=segment["text"],
        voice=segment["voice_id"],
        rate=segment["rate"],
        pitch=segment["pitch"]
    )
    await communicate.save(output_filepath)


async def synthesize_all_or_sample(manifest: Dict[str, Any], base_dir: str, sample_only: bool = False, max_sample_count: int = 4):
    """
    Synthesizes real audio files for segments in the manifest.
    If sample_only is True, synthesizes the first few segments covering both DJ and fan letter voices.
    """
    audio_dir = os.path.join(base_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    segments = manifest["segments"]
    if sample_only:
        # Select representative segments (e.g. DJ Kim intro, DJ Kim song intro, SunHi fan letter, DJ Kim closing)
        selected_segments = []
        # Ch 1 DJ Kim
        for s in segments:
            if s["speaker"] == "dj_kim" and s["chapter_index"] == 1:
                selected_segments.append(s)
                break
        # Ch 3 DJ Kim
        for s in segments:
            if s["speaker"] == "dj_kim" and s["chapter_index"] == 3:
                selected_segments.append(s)
                break
        # Ch 4 Fan letter (SunHi)
        for s in segments:
            if s["speaker"] == "fan_letter_writer":
                selected_segments.append(s)
                break
        # Ch 6 Closing
        for s in segments:
            if s["speaker"] == "dj_kim" and s["chapter_index"] == 6:
                selected_segments.append(s)
                break
    else:
        selected_segments = segments

    print(f"[*] Starting Edge-TTS synthesis for {len(selected_segments)} segments...")
    sem = asyncio.Semaphore(4)

    async def _worker(seg: Dict[str, Any]) -> int:
        out_filename = os.path.basename(seg["audio_rel_path"])
        out_path = os.path.join(audio_dir, out_filename)
        if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            print(f"    - [CACHED] {out_filename} ({os.path.getsize(out_path)} bytes)")
            return 1
        async with sem:
            for attempt in range(3):
                try:
                    print(f"    - Synthesizing [{seg['speaker']} / {seg['voice_id']}] {seg['segment_id']} -> {out_filename}")
                    await synthesize_segment(seg, out_path)
                    file_size = os.path.getsize(out_path)
                    print(f"      [OK] Saved {out_filename} ({file_size} bytes)")
                    return 1
                except Exception as e:
                    if attempt == 2:
                        print(f"      [WARN] TTS Synthesis failed for {seg['segment_id']}: {e}")
                    else:
                        await asyncio.sleep(1.0)
            return 0

    results = await asyncio.gather(*[_worker(s) for s in selected_segments])
    success_count = sum(results)
    print(f"[+] Edge-TTS synthesis finished: {success_count}/{len(selected_segments)} files generated in {audio_dir}")


def main():
    parser = argparse.ArgumentParser(description="@김쌤의영웅라디오 Audio Synthesis Engine")
    parser.add_argument("--script-file", type=str, default="", help="Path to script_epXX.json")
    parser.add_argument("--output-dir", type=str, default="", help="Target directory for narration prompts and audio")
    parser.add_argument("--synthesize-audio", action="store_true", default=True, help="Actually run Edge-TTS synthesis")
    parser.add_argument("--sample-only", action="store_true", default=False, help="Synthesize representative sample segments only")
    args = parser.parse_args()

    # Determine script file path
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

    print(f"[*] Building narration manifest for {script_data.get('episode_title', 'Radio Episode')}...")
    manifest = build_narration_manifest(script_data)

    manifest_path = os.path.join(base_dir, "narration_prompts.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved narration prompts manifest to: {manifest_path}")

    if args.synthesize_audio:
        try:
            # We synthesize sample or key segments to verify audio synthesis locally
            asyncio.run(synthesize_all_or_sample(manifest, base_dir, sample_only=args.sample_only))
        except Exception as e:
            print(f"[WARN] Audio synthesis encountered an issue: {e}")

    print("[SUCCESS] Audio synthesis planning and manifest generation complete.")


if __name__ == "__main__":
    main()
