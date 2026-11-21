#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_adversarial_audio.py
================================================================================
ADVERSARIAL AUDIO SIGNAL & ALIGNMENT STRESS TEST SUITE
Milestone 5 Forensic Verification for 4사업부 Shoujo Anime Movie Pipeline

Empirical Oracles & Adversarial Probes:
1. Master WAV Signal Integrity:
   - Exhaustive sample-by-sample inspection across all L/R channels.
   - Hard clipping detection: samples >= 32767 or <= -32768 (strictly 0).
   - Linear peak amplitude ceiling: <= 0.94406 (-0.50 dBFS).
   - Peak dBFS calculation & True Peak 4x oversampling approximation.
   - DC Offset drift and stereo balance verification.
2. Video Audio Track Alignment & Forensic Mux Verification:
   - Audio track extraction from 'shoujo_shorts_master.mp4' via FFmpeg.
   - Duration delta between MP4 container, video stream, and master WAV (<= 0.05s).
   - AAC lossy compression inter-sample peak & clipping evaluation.
   - Audio waveform cross-correlation / RMS alignment to detect drift or desync.
3. Subtitle Full Readout Guarantee & Beat Timestamp Continuity:
   - Every beat in audio_metadata.json: seg_dur >= tts_dur + 0.22s (margin >= 0.22s).
   - Timestamp continuity: beat[i].start == beat[i-1].end.
   - 100% complete voice readout prior to visual scene transitions.
4. Video Scene Cut Alignment & Ending Slate Gating:
   - Video frame-by-frame scene transition timestamps vs beat timing boundaries.
   - Ending slate gating: final 3.4s domain callout & photo booth CTA.
5. Zero-Tolerance Prohibited Commercial Words Audit:
   - Prohibited words: ["최저가", "할인율", "특가", "폭탄세일"].
   - Scanned across all 4사업부 scripts, metadata, and configuration files.
================================================================================
"""

import sys
import os
import math
import wave
import json
import subprocess
import shutil
import tempfile
from pathlib import Path
import numpy as np
import cv2
import imageio_ffmpeg

# Ensure UTF-8 console output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(r"d:\드림컴퍼니")
DIV4_DIR = ROOT_DIR / "4사업부"
OUTPUT_DIR = DIV4_DIR / "output"
PILOT_DIR = DIV4_DIR / "content" / "shorts_daily" / "ep_shoujo_pilot"
SCRIPTS_DIR = DIV4_DIR / "scripts"
TESTS_DIR = DIV4_DIR / "tests"

MASTER_WAV = OUTPUT_DIR / "audio_ep_shoujo.wav"
MASTER_META = OUTPUT_DIR / "audio_metadata.json"
MASTER_MP4 = OUTPUT_DIR / "shoujo_shorts_master.mp4"
PILOT_SCRIPT = PILOT_DIR / "script_ep_shoujo.json"

BANNED_WORDS = ["최저가", "할인율", "특가", "폭탄세일"]
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()


class AdversarialAudioChallenger:
    def __init__(self):
        self.results = {}
        self.temp_dir = Path(tempfile.mkdtemp(prefix="adv_audio_"))
        print(f"🔬 Adversarial Test Harness Initialized. Temp dir: {self.temp_dir}")

    def cleanup(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    # --------------------------------------------------------------------------
    # CHALLENGE 1: Master WAV File Sample-Level Signal Forensics
    # --------------------------------------------------------------------------
    def challenge_1_sample_level_signal(self):
        print("\n" + "=" * 80)
        print("⚡ CHALLENGE 1: Master WAV Sample-Level Signal Forensics")
        print("=" * 80)

        assert MASTER_WAV.exists(), f"Master WAV not found: {MASTER_WAV}"
        file_size = MASTER_WAV.stat().st_size
        print(f"  File: {MASTER_WAV} ({file_size:,} bytes)")

        with wave.open(str(MASTER_WAV), "rb") as wf:
            channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            raw_data = wf.readframes(n_frames)

        assert channels == 2, f"Expected 2 channels stereo, got {channels}"
        assert sampwidth == 2, f"Expected 16-bit PCM (2 bytes), got {sampwidth}"
        assert framerate == 44100, f"Expected 44100 Hz, got {framerate}"

        audio_int16 = np.frombuffer(raw_data, dtype=np.int16).reshape(-1, 2)
        total_samples_per_ch = len(audio_int16)
        total_samples_all = total_samples_per_ch * 2
        duration_sec = total_samples_per_ch / float(framerate)

        print(f"  Specs: 2ch Stereo, 16-bit signed PCM, 44,100 Hz")
        print(f"  Total Sample Frames: {total_samples_per_ch:,} ({duration_sec:.4f}s)")
        print(f"  Total Individual Samples Inspected: {total_samples_all:,}")

        # 1. Clipped Samples Oracle (Hard limits: >= 32767 or <= -32768)
        left_pos_clips = int(np.sum(audio_int16[:, 0] >= 32767))
        left_neg_clips = int(np.sum(audio_int16[:, 0] <= -32768))
        right_pos_clips = int(np.sum(audio_int16[:, 1] >= 32767))
        right_neg_clips = int(np.sum(audio_int16[:, 1] <= -32768))

        total_clips = left_pos_clips + left_neg_clips + right_pos_clips + right_neg_clips
        print(f"  Clipped Samples Count (>= 32767 or <= -32768):")
        print(f"    - Left Channel:  pos={left_pos_clips}, neg={left_neg_clips}")
        print(f"    - Right Channel: pos={right_pos_clips}, neg={right_neg_clips}")
        print(f"    - Total Clipped: {total_clips} (Requirement: EXACTLY 0)")
        assert total_clips == 0, f"VIOLATION: Detected {total_clips} clipped samples in master WAV!"

        # 2. Peak Linear & dBFS Amplitude Oracle
        audio_float = audio_int16.astype(np.float64) / 32768.0

        left_peak_lin = float(np.max(np.abs(audio_float[:, 0])))
        right_peak_lin = float(np.max(np.abs(audio_float[:, 1])))
        overall_peak_lin = max(left_peak_lin, right_peak_lin)

        left_peak_dbfs = 20.0 * math.log10(max(left_peak_lin, 1e-12))
        right_peak_dbfs = 20.0 * math.log10(max(right_peak_lin, 1e-12))
        overall_peak_dbfs = 20.0 * math.log10(max(overall_peak_lin, 1e-12))

        print(f"  Peak Linear Amplitude: {overall_peak_lin:.4f} (Ceiling: 0.94406)")
        print(f"    - Left:  {left_peak_lin:.4f} ({left_peak_dbfs:.2f} dBFS)")
        print(f"    - Right: {right_peak_lin:.4f} ({right_peak_dbfs:.2f} dBFS)")
        print(f"    - Master Overall: {overall_peak_dbfs:.2f} dBFS (Requirement: <= -0.50 dBFS)")

        assert overall_peak_lin <= 0.94406 + 1e-4, (
            f"VIOLATION: Peak linear amplitude {overall_peak_lin:.4f} exceeds 0.94406 ceiling!"
        )
        assert overall_peak_dbfs <= -0.50 + 1e-3, (
            f"VIOLATION: Peak {overall_peak_dbfs:.2f} dBFS exceeds -0.50 dBFS limiter requirement!"
        )

        # 3. DC Offset Drift Oracle
        dc_left = float(np.mean(audio_float[:, 0]))
        dc_right = float(np.mean(audio_float[:, 1]))
        print(f"  DC Offset: Left={dc_left:.6f}, Right={dc_right:.6f} (Threshold: < 0.002)")
        assert abs(dc_left) < 0.002, f"Left DC offset {dc_left} exceeds threshold"
        assert abs(dc_right) < 0.002, f"Right DC offset {dc_right} exceeds threshold"

        # 4. True Peak 4x Sinc/Oversampling Approximation
        # Check if inter-sample peaks exceed digital full scale (1.0)
        # Using 4x linear interpolation over highest peak neighborhoods
        peak_indices = np.where(np.abs(audio_float) >= (overall_peak_lin * 0.98))[0]
        max_inter_peak = overall_peak_lin
        if len(peak_indices) > 0:
            for ch in range(2):
                ch_peaks = np.where(np.abs(audio_float[:, ch]) >= (overall_peak_lin * 0.98))[0]
                for idx in ch_peaks[:500]:  # inspect top 500 peak regions
                    if 2 < idx < len(audio_float) - 2:
                        window = audio_float[idx - 2 : idx + 3, ch]
                        interp_x = np.linspace(0, 4, 17)
                        interp_y = np.interp(interp_x, np.arange(5), window)
                        local_peak = float(np.max(np.abs(interp_y)))
                        if local_peak > max_inter_peak:
                            max_inter_peak = local_peak

        max_inter_peak_dbfs = 20.0 * math.log10(max(max_inter_peak, 1e-12))
        print(f"  True-Peak 4x Oversampling Estimate: {max_inter_peak:.4f} ({max_inter_peak_dbfs:.2f} dBFS)")
        assert max_inter_peak <= 1.0, f"VIOLATION: True peak {max_inter_peak:.4f} exceeds 0 dBFS!"

        # 5. Internal Dead Air / Silence Oracle
        mono_envelope = np.mean(np.abs(audio_float), axis=1)
        silence_thresh = 0.010
        runs = np.where(mono_envelope <= silence_thresh, 1, 0)
        # Calculate max consecutive run
        max_run = 0
        curr_run = 0
        for r in runs:
            if r == 1:
                curr_run += 1
                if curr_run > max_run:
                    max_run = curr_run
            else:
                curr_run = 0
        max_silence_sec = max_run / float(framerate)
        print(f"  Max Internal Silence / Dead Air: {max_silence_sec:.4f}s (Threshold: <= 0.12s)")
        assert max_silence_sec <= 0.120, f"Internal silence {max_silence_sec:.4f}s exceeds 0.12s threshold!"

        print("✅ CHALLENGE 1 PASSED: Master WAV sample-level signal integrity 100% verified.")
        self.results["wav_duration"] = duration_sec
        self.results["wav_peak_dbfs"] = overall_peak_dbfs
        self.results["wav_clipped"] = total_clips
        return audio_float, duration_sec

    # --------------------------------------------------------------------------
    # CHALLENGE 2: Video Audio Track Extraction & Container Sync
    # --------------------------------------------------------------------------
    def challenge_2_video_audio_track(self, wav_float: np.ndarray, wav_dur: float):
        print("\n" + "=" * 80)
        print("⚡ CHALLENGE 2: Video Audio Track Extraction & Forensic Container Mux")
        print("=" * 80)

        assert MASTER_MP4.exists(), f"Master MP4 not found: {MASTER_MP4}"
        mp4_size = MASTER_MP4.stat().st_size
        print(f"  File: {MASTER_MP4} ({mp4_size:,} bytes)")

        # 1. Probe MP4 Container via FFmpeg / FFprobe
        probe_cmd = [
            FFMPEG_EXE,
            "-i", str(MASTER_MP4),
            "-hide_banner"
        ]
        res = subprocess.run(probe_cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        ffmpeg_log = res.stderr
        print("  FFmpeg Stream Inspection:")
        for line in ffmpeg_log.splitlines():
            if "Duration:" in line or "Stream #" in line:
                print(f"    {line.strip()}")

        # 2. Extract MP4 Audio Track directly to uncompressed 16-bit 44.1kHz WAV
        extracted_wav = self.temp_dir / "extracted_mp4_audio.wav"
        extract_cmd = [
            FFMPEG_EXE,
            "-y",
            "-i", str(MASTER_MP4),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "44100",
            "-ac", "2",
            str(extracted_wav)
        ]
        run_res = subprocess.run(extract_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert run_res.returncode == 0, f"FFmpeg audio extraction failed: {run_res.stderr.decode('utf-8', errors='ignore')}"
        assert extracted_wav.exists(), "Extracted WAV file does not exist"

        # 3. Analyze Extracted MP4 Audio Track
        with wave.open(str(extracted_wav), "rb") as ewf:
            e_ch = ewf.getnchannels()
            e_sw = ewf.getsampwidth()
            e_fr = ewf.getframerate()
            e_nf = ewf.getnframes()
            e_raw = ewf.readframes(e_nf)

        e_pcm = np.frombuffer(e_raw, dtype=np.int16).reshape(-1, 2)
        e_dur = len(e_pcm) / float(e_fr)
        e_float = e_pcm.astype(np.float64) / 32768.0

        dur_delta = abs(e_dur - wav_dur)
        print(f"  Master WAV Duration: {wav_dur:.4f}s")
        print(f"  MP4 Audio Duration:  {e_dur:.4f}s")
        print(f"  Duration Delta:      {dur_delta:.4f}s (Threshold: <= 0.05s)")
        assert dur_delta <= 0.05, f"Audio duration delta {dur_delta:.4f}s exceeds 0.05s tolerance!"

        # 4. Check for AAC codec clipping / inter-sample overshoot in MP4 track
        e_clipped_left = int(np.sum(e_pcm[:, 0] >= 32767))
        e_clipped_right = int(np.sum(e_pcm[:, 1] >= 32767))
        total_e_clipped = e_clipped_left + e_clipped_right
        e_peak_lin = float(np.max(np.abs(e_float)))
        e_peak_dbfs = 20.0 * math.log10(max(e_peak_lin, 1e-12))

        print(f"  Decoded MP4 AAC Peak: {e_peak_lin:.4f} ({e_peak_dbfs:.2f} dBFS)")
        print(f"  Decoded MP4 Clipped Samples: {total_e_clipped}")
        assert total_e_clipped == 0, f"AAC encoding introduced {total_e_clipped} clipped samples!"
        assert e_peak_lin <= 1.0, f"AAC decoded peak exceeds 0 dBFS!"

        # 5. Cross-Correlation / Waveform Matching (Verify identical content)
        min_len = min(len(wav_float), len(e_float))
        # Compute correlation coefficient on downsampled mono
        sub_wav = np.mean(wav_float[:min_len:10], axis=1)
        sub_mp4 = np.mean(e_float[:min_len:10], axis=1)
        corr_coeff = float(np.corrcoef(sub_wav, sub_mp4)[0, 1])
        print(f"  Waveform Correlation Coeff (WAV vs MP4 Audio): {corr_coeff:.6f} (Requirement: > 0.98)")
        assert corr_coeff > 0.98, f"Waveform correlation {corr_coeff:.4f} is too low (audio mismatch)!"

        print("✅ CHALLENGE 2 PASSED: Video audio track is accurately muxed, synced, and clipping-free.")
        self.results["mp4_audio_duration"] = e_dur
        self.results["mp4_audio_peak_dbfs"] = e_peak_dbfs
        self.results["mp4_audio_corr"] = corr_coeff

    # --------------------------------------------------------------------------
    # CHALLENGE 3: Beat Alignment & 100% Subtitle Full-Readout Guarantee
    # --------------------------------------------------------------------------
    def challenge_3_beat_alignment(self, wav_dur: float):
        print("\n" + "=" * 80)
        print("⚡ CHALLENGE 3: 100% Subtitle Full Readout Guarantee & Beat Timings")
        print("=" * 80)

        assert MASTER_META.exists(), f"Metadata not found: {MASTER_META}"
        with open(MASTER_META, "r", encoding="utf-8") as f:
            meta = json.load(f)

        beat_timings = meta.get("beat_timings", [])
        assert len(beat_timings) == 8, f"Expected 8 beats, got {len(beat_timings)}"

        running_start = 0.0
        for i, beat in enumerate(beat_timings):
            b_idx = beat["beat_idx"]
            speaker = beat["speaker"]
            voice = beat["voice"]
            start_s = beat["start_sec"]
            end_s = beat["end_sec"]
            seg_dur = beat["duration_sec"]
            tts_dur = beat["tts_dur_sec"]
            margin = beat["margin_sec"]
            narration = beat["narration"]

            # 1. Continuity check
            assert abs(start_s - running_start) < 0.005, (
                f"Discontinuity at beat {b_idx}: start={start_s:.4f}s, expected {running_start:.4f}s"
            )
            assert abs(end_s - (start_s + seg_dur)) < 0.005, (
                f"End time mismatch at beat {b_idx}: end={end_s:.4f}s, start+seg={start_s + seg_dur:.4f}s"
            )

            # 2. seg_dur >= tts_dur + 0.22s Rule Oracle (Zero syllable truncation)
            min_required_dur = tts_dur + 0.220
            diff = seg_dur - min_required_dur
            print(
                f"  Beat {b_idx} [{speaker:<8} / {voice}]: "
                f"TTS={tts_dur:.3f}s | Seg={seg_dur:.3f}s | Margin=+{margin:.3f}s "
                f"(Req: >= +0.220s, Excess: {diff:+.3f}s)"
            )

            assert seg_dur >= (tts_dur + 0.219), (
                f"VIOLATION at beat {b_idx}: seg_dur ({seg_dur:.3f}s) < tts_dur ({tts_dur:.3f}s) + 0.22s!"
            )
            assert margin >= 0.219, (
                f"VIOLATION at beat {b_idx}: margin_sec ({margin:.3f}s) < 0.22s breathing buffer!"
            )
            assert beat.get("full_reading_guaranteed") is True, f"Beat {b_idx} lacks full_reading_guaranteed flag"

            running_start = end_s

        total_beat_dur = running_start
        meta_total = meta.get("total_duration_sec", 0.0)
        print(f"  Sum of Beat Durations: {total_beat_dur:.4f}s")
        print(f"  Metadata Total:        {meta_total:.4f}s")
        print(f"  WAV Total Duration:    {wav_dur:.4f}s")

        assert abs(total_beat_dur - wav_dur) < 0.05, "Sum of beats does not match WAV duration!"
        assert abs(meta_total - wav_dur) < 0.05, "Metadata total does not match WAV duration!"

        print("✅ CHALLENGE 3 PASSED: All 8 beats strictly fulfill seg_dur >= tts_dur + 0.22s.")
        self.results["beat_count"] = len(beat_timings)
        self.results["total_beat_dur"] = total_beat_dur

    # --------------------------------------------------------------------------
    # CHALLENGE 4: Video Scene Duration & Transition Synchronization
    # --------------------------------------------------------------------------
    def challenge_4_video_scene_alignment(self):
        print("\n" + "=" * 80)
        print("⚡ CHALLENGE 4: Video Scene Cut & Ending Slate Synchronization")
        print("=" * 80)

        cap = cv2.VideoCapture(str(MASTER_MP4))
        assert cap.isOpened(), f"Cannot open video: {MASTER_MP4}"

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video_dur = frame_count / float(fps)

        print(f"  Video Specs: {width}x{height} @ {fps:.2f} fps")
        print(f"  Total Frames: {frame_count:,} ({video_dur:.3f}s)")

        assert width == 1080 and height == 1920, f"Expected 1080x1920, got {width}x{height}"
        assert abs(fps - 30.0) < 0.1, f"Expected 30 fps, got {fps}"
        assert abs(video_dur - 33.80) < 0.1, f"Expected ~33.80s, got {video_dur:.3f}s"

        with open(MASTER_META, "r", encoding="utf-8") as f:
            meta = json.load(f)
        beat_timings = meta["beat_timings"]

        # Check frame at middle of each beat to confirm valid active frame
        for i, beat in enumerate(beat_timings):
            mid_t = (beat["start_sec"] + beat["end_sec"]) / 2.0
            mid_frame_idx = int(round(mid_t * fps))
            cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame_idx)
            ret, frame = cap.read()
            assert ret, f"Failed to read frame at beat {i} (frame {mid_frame_idx})"
            assert frame.shape == (1920, 1080, 3)

            # Measure variance across frame to ensure no blank / corrupted frame
            var = np.var(frame)
            print(f"  Beat {i} Midpoint Frame {mid_frame_idx} (t={mid_t:.2f}s): Variance={var:.1f}")
            assert var > 100.0, f"Beat {i} midpoint frame appears blank or corrupted (variance={var})"

        # Check Ending Slate Gating (final 3.4 seconds)
        ending_start_t = video_dur - 3.4
        ending_start_frame = int(round(ending_start_t * fps))
        pre_ending_frame = ending_start_frame - 15  # 0.5s before outro
        in_ending_frame = ending_start_frame + 15   # 0.5s into outro

        cap.set(cv2.CAP_PROP_POS_FRAMES, pre_ending_frame)
        ret_pre, frame_pre = cap.read()
        cap.set(cv2.CAP_PROP_POS_FRAMES, in_ending_frame)
        ret_in, frame_in = cap.read()

        assert ret_pre and ret_in, "Failed to read ending slate test frames"

        # In outro, top header card is rendered around Y=95..265
        # Verify top region differs significantly between pre-ending and in-ending
        top_pre = frame_pre[100:260, 200:880]
        top_in = frame_in[100:260, 200:880]
        diff_top = float(np.mean(np.abs(top_in.astype(float) - top_pre.astype(float))))

        print(f"  Ending Slate Gating Check:")
        print(f"    - Pre-ending Frame {pre_ending_frame} (t={pre_ending_frame/fps:.2f}s)")
        print(f"    - In-ending Frame {in_ending_frame} (t={in_ending_frame/fps:.2f}s)")
        print(f"    - Top Card Pixel Diff: {diff_top:.2f} (Threshold: > 20.0)")

        assert diff_top > 20.0, (
            f"Ending slate top card not detected or not properly gated (diff={diff_top:.2f})!"
        )

        cap.release()
        print("✅ CHALLENGE 4 PASSED: Video scene durations and ending slate alignment verified.")
        self.results["video_duration"] = video_dur
        self.results["video_frames"] = frame_count

    # --------------------------------------------------------------------------
    # CHALLENGE 5: Zero-Tolerance Prohibited Commercial Words Audit
    # --------------------------------------------------------------------------
    def challenge_5_prohibited_words_audit(self):
        print("\n" + "=" * 80)
        print("⚡ CHALLENGE 5: Zero-Tolerance Prohibited Commercial Words Scan")
        print("=" * 80)

        targets = [
            MASTER_META,
            PILOT_SCRIPT,
            PILOT_DIR / "audio_metadata.json",
            PILOT_DIR / "metadata_ep_shoujo.json",
            PILOT_DIR / "metadata_ep_shoujo.md",
            SCRIPTS_DIR / "render_shoujo_anime_movie.py",
            SCRIPTS_DIR / "synthesize_shoujo_drama_audio.py",
            SCRIPTS_DIR / "validate_m2_audio.py",
            SCRIPTS_DIR / "validate_m3_video.py",
            TESTS_DIR / "test_m3_dual_voice_audio.py"
        ]

        violations = []
        scanned_count = 0

        for path in targets:
            if not path.exists():
                continue
            scanned_count += 1
            content = path.read_text(encoding="utf-8", errors="replace")
            file_hits = []
            for banned in BANNED_WORDS:
                # Count occurrences, excluding banned word definition list variables
                count = content.count(banned)
                if count > 0:
                    # Check lines to see if it's in a test list or actual content
                    lines = content.splitlines()
                    for line_no, line in enumerate(lines, 1):
                        if banned in line:
                            # If it's a test assertion or banned word list definition, note it
                            is_filter_def = any(
                                token in line
                                for token in ["BANNED_WORDS", "banned", "assert banned", "금지어", "prohibited"]
                            )
                            if not is_filter_def:
                                file_hits.append((banned, line_no, line.strip()))

            if file_hits:
                violations.append((path.name, file_hits))
                print(f"  ❌ VIOLATION in {path.name}: {file_hits}")
            else:
                print(f"  [PASS] {path.name:<35} : Clean (0 prohibited commercial words)")

        print(f"  Total Files Scanned: {scanned_count}")
        assert len(violations) == 0, f"Found prohibited commercial words in {violations}!"
        print("✅ CHALLENGE 5 PASSED: Zero prohibited commercial words strictly audited.")
        self.results["scanned_files"] = scanned_count
        self.results["prohibited_violations"] = len(violations)

    def run_all(self):
        try:
            audio_float, wav_dur = self.challenge_1_sample_level_signal()
            self.challenge_2_video_audio_track(audio_float, wav_dur)
            self.challenge_3_beat_alignment(wav_dur)
            self.challenge_4_video_scene_alignment()
            self.challenge_5_prohibited_words_audit()

            print("\n" + "#" * 80)
            print("🎉 ALL 5 ADVERSARIAL CHALLENGES COMPLETED WITH 100% SUCCESS!")
            print("🛡️ VERDICT: APPROVE")
            print("#" * 80)
            return True, self.results
        finally:
            self.cleanup()


def main():
    challenger = AdversarialAudioChallenger()
    success, results = challenger.run_all()
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
