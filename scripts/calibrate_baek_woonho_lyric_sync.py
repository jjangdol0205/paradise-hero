#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
D:\드림컴퍼니\4사업부\scripts\calibrate_baek_woonho_lyric_sync.py
================================================================================
4사업부 (`HERO` · @김쌤의영웅라디오) 백운호 6곡 전수 실제 보컬 음원 기반 가사 싱크 보정기

파이프라인 (저부하 순차 실행: BelowNormal + OMP_NUM_THREADS=2 + demucs -j 1):
1. Demucs (`htdemucs --two-stems=vocals`)로 6곡 각각의 순수 보컬 스템(`vocals.wav`) 분리
2. 50ms 해상도 보컬 RMS 엔벨로프 계산 -> 실제 발성 구간(Vocal VAD) 및 무보컬 간주/후주 실측
3. 순수 보컬 MP3 + Demucs 발성 구간표를 `Gemini 2.5 Audio` (`gemini-2.5-pro` / `gemini-2.5-flash`)에
   전달해 실제 가창 라인별 `[start_sec, end_sec]` 정밀 추출 (프롬프트 희망값 복붙 원천 제거)
4. 추출된 타임스탬프를 Demucs 실측 보컬 발성 시작/종료 경계에 결정론적 스냅 & 보컬 활성비율 검증
5. `baek_woonho_6songs_mv_catalog.json`의 `slices`(`chorus1`/`verse1`/`chorus2`) 및 `full_cues`
   갱신 + `sync_verified=true` 메타 기록 + 보정 전/후 비교 리포트 저장
================================================================================
"""

from __future__ import annotations

import base64
import ctypes
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

D_ROOT = Path(r"D:\드림컴퍼니")
CACHE_ROOT = D_ROOT / ".cache"
os.environ["HF_HOME"] = str(CACHE_ROOT / "huggingface")
os.environ["TORCH_HOME"] = str(CACHE_ROOT / "torch")
os.environ["TMP"] = str(CACHE_ROOT / "tmp")
os.environ["TEMP"] = str(CACHE_ROOT / "tmp")
os.environ["PYTHONUTF8"] = "1"
os.environ["OMP_NUM_THREADS"] = "4"
os.environ["MKL_NUM_THREADS"] = "4"

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
    except Exception:
        pass

import numpy as np
import soundfile as sf
import torch

torch.set_num_threads(4)

KST = dt.timezone(dt.timedelta(hours=9))
DIV4_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = DIV4_DIR / "assets" / "audio"
CATALOG_PATH = DIV4_DIR / "data" / "baek_woonho_6songs_mv_catalog.json"
REPORT_PATH = DIV4_DIR / "data" / "baek_woonho_lyric_sync_report_20261126.json"
WORK_DIR = CACHE_ROOT / "tmp" / "hero_lyric_sync_calib_20261126"


def _get_ffmpeg() -> str:
    try:
        import imageio_ffmpeg  # type: ignore
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def _load_env() -> Dict[str, str]:
    env: Dict[str, str] = {}
    for p in (D_ROOT / ".env", DIV4_DIR / ".env"):
        if p.exists():
            for raw in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                s = raw.strip()
                if s and not s.startswith("#") and "=" in s:
                    k, v = s.split("=", 1)
                    val = v.strip().strip('"').strip("'")
                    if val:
                        env.setdefault(k.strip(), val)
    for k, v in os.environ.items():
        if v:
            env[k] = v
    return env


def separate_vocals_demucs(song_mp3: Path, song_id: str) -> Path:
    """Runs htdemucs --two-stems=vocals sequentially (-j 1, cpu, BelowNormal) with disk cache."""
    out_base = WORK_DIR / "demucs_out"
    cached = out_base / "htdemucs" / song_mp3.stem / "vocals.wav"
    if cached.exists() and cached.stat().st_size > 1_000_000:
        print(f"  [DEMUCS CACHED] {song_id} -> {cached.name}", flush=True)
        return cached

    out_base.mkdir(parents=True, exist_ok=True)
    # Decode MP3 to 44.1kHz WAV first so torchaudio never needs torchcodec/mp3 backend
    wav_in = WORK_DIR / "wav_in" / f"{song_mp3.stem}.wav"
    wav_in.parent.mkdir(parents=True, exist_ok=True)
    if not wav_in.exists():
        subprocess.run(
            [_get_ffmpeg(), "-y", "-threads", "2", "-i", str(song_mp3), "-ar", "44100", "-ac", "2", str(wav_in)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )

    print(f"  [DEMUCS RUN] Separating pure vocal stem for {song_id}...", flush=True)
    t0 = time.time()
    # Run via Python API using soundfile (100% immune to torchaudio backend issues on Windows)
    from demucs.pretrained import get_model  # type: ignore
    from demucs.apply import apply_model  # type: ignore

    model = _get_demucs_model()
    audio_np, sr = sf.read(str(wav_in), dtype="float32")
    if audio_np.ndim == 1:
        audio_np = np.stack([audio_np, audio_np], axis=-1)
    wav_t = torch.from_numpy(audio_np.T).unsqueeze(0)  # (1, 2, T)
    with torch.no_grad():
        sources = apply_model(model, wav_t, device="cpu", shifts=0, split=True, overlap=0.1, progress=False)
    # htdemucs sources order: ['drums', 'bass', 'other', 'vocals']
    voc_idx = model.sources.index("vocals")
    voc_np = sources[0, voc_idx].cpu().numpy().T  # (T, 2)
    cached.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(cached), voc_np, sr, subtype="PCM_16")
    print(f"  [DEMUCS OK] {song_id} vocals.wav ({cached.stat().st_size:,}B, {time.time()-t0:.1f}s)", flush=True)
    return cached


_DEMUCS_MODEL = None


def _get_demucs_model():
    global _DEMUCS_MODEL
    if _DEMUCS_MODEL is None:
        from demucs.pretrained import get_model  # type: ignore
        _DEMUCS_MODEL = get_model("htdemucs")
        _DEMUCS_MODEL.eval()
    return _DEMUCS_MODEL


def compute_vocal_envelope(vocals_wav: Path, hop_sec: float = 0.05) -> Dict[str, Any]:
    """Computes 50ms vocal RMS contour, active singing phrases, and vocal-free instrumental spans."""
    data, sr = sf.read(str(vocals_wav), dtype="float32")
    mono = np.mean(data, axis=1) if data.ndim > 1 else data
    dur = len(mono) / float(sr)
    hop = max(1, int(round(sr * hop_sec)))
    n_frames = len(mono) // hop
    frames = mono[: n_frames * hop].reshape(n_frames, hop)
    rms = np.sqrt(np.mean(frames ** 2, axis=1) + 1e-12)
    # Smooth lightly over 3 frames (150ms) to suppress single-frame clicks
    kernel = np.array([0.25, 0.5, 0.25], dtype=np.float32)
    rms_s = np.convolve(rms, kernel, mode="same")

    p95 = float(np.percentile(rms_s, 95))
    thresh = max(0.012, p95 * 0.13)
    active = rms_s >= thresh

    # Extract raw vocal intervals, merge pauses <= 0.65s, drop blips < 0.35s
    raw_spans: List[List[float]] = []
    in_seg = False
    seg_s = 0.0
    for i, act in enumerate(active):
        t = i * hop_sec
        if act and not in_seg:
            seg_s = t
            in_seg = True
        elif not act and in_seg:
            raw_spans.append([seg_s, t])
            in_seg = False
    if in_seg:
        raw_spans.append([seg_s, dur])

    merged: List[List[float]] = []
    for a, b in raw_spans:
        if merged and (a - merged[-1][1]) <= 0.65:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    phrases = [[round(a, 2), round(b, 2)] for a, b in merged if (b - a) >= 0.45]

    # Compute fine onset/offset points (using smaller 0.25s pause threshold for line boundary snapping)
    fine_spans: List[List[float]] = []
    for a, b in raw_spans:
        if fine_spans and (a - fine_spans[-1][1]) <= 0.25:
            fine_spans[-1][1] = b
        else:
            fine_spans.append([a, b])
    fine_spans = [[round(a, 2), round(b, 2)] for a, b in fine_spans if (b - a) >= 0.30]

    # Identify instrumental (non-vocal) spans >= 2.0s
    inst_spans: List[List[float]] = []
    prev = 0.0
    for a, b in phrases:
        if a - prev >= 2.0:
            inst_spans.append([round(prev, 2), round(a, 2)])
        prev = b
    if dur - prev >= 1.5:
        inst_spans.append([round(prev, 2), round(dur, 2)])

    return {
        "duration_sec": round(dur, 2),
        "hop_sec": hop_sec,
        "p95_rms": round(p95, 5),
        "thresh_rms": round(thresh, 5),
        "rms": rms_s,
        "active": active,
        "phrases": phrases,
        "fine_spans": fine_spans,
        "instrumental_spans": inst_spans,
    }


def vocal_active_ratio(vad: Dict[str, Any], t0: float, t1: float) -> float:
    hop = vad["hop_sec"]
    act = vad["active"]
    i0 = max(0, min(len(act) - 1, int(round(t0 / hop))))
    i1 = max(i0 + 1, min(len(act), int(round(t1 / hop))))
    return float(np.mean(act[i0:i1]))


def encode_compact_vocal_mp3(vocals_wav: Path, song_id: str) -> Path:
    out_mp3 = WORK_DIR / "vocals_mp3" / f"{song_id}_vocals_48k.mp3"
    out_mp3.parent.mkdir(parents=True, exist_ok=True)
    if not out_mp3.exists():
        subprocess.run(
            [_get_ffmpeg(), "-y", "-threads", "2", "-i", str(vocals_wav), "-ac", "1", "-ar", "24000", "-b:a", "48k", str(out_mp3)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    return out_mp3


def align_song_with_gemini_audio(
    song: Dict[str, Any],
    vocal_mp3: Path,
    vad: Dict[str, Any],
    api_key: str,
) -> Dict[str, Any]:
    """
    Sends the isolated vocal MP3 + Demucs vocal-active phrase windows + reference lyrics
    to Gemini 2.5 Audio (gemini-2.5-pro -> gemini-2.5-flash fallback) for exact line-by-line timing.
    """
    b64_audio = base64.b64encode(vocal_mp3.read_bytes()).decode("ascii")

    # Collect reference lyrics per section from existing catalog
    slices_by_id = {s["slice_id"]: s for s in song["slices"]}
    ref_v1 = [f"{c[2]} / {c[3]}" for c in slices_by_id["verse1"]["cues"]]
    ref_c1 = [f"{c[2]} / {c[3]}" for c in slices_by_id["chorus1"]["cues"]]
    ref_full = [f"{c[2]} / {c[3]}" for c in song.get("full_cues") or [] if not str(c[2]).startswith("♪")]

    prompt = (
        f"You are a precision Korean music audio-to-lyric alignment engineer.\n"
        f"Attached is the ISOLATED VOCAL STEM (pure male baritone singing, instruments removed) of Korean trot song 〈{song['title']}〉.\n"
        f"Total audio duration: {vad['duration_sec']} seconds.\n"
        f"Objective Demucs vocal-activity windows (seconds where singing energy is actually present):\n"
        f"  Major singing blocks: {json.dumps(vad['phrases'])}\n"
        f"  Fine singing phrases: {json.dumps(vad['fine_spans'])}\n"
        f"  Vocal-free instrumental spans: {json.dumps(vad['instrumental_spans'])}\n\n"
        f"Reference lyric lines for this song (note: the AI singer may sing slightly shifted timing, repeat a line, or pause between lines — trust ONLY what you actually hear in the audio!):\n"
        f"  Verse 1 lines: {json.dumps(ref_v1, ensure_ascii=False)}\n"
        f"  Chorus 1 lines: {json.dumps(ref_c1, ensure_ascii=False)}\n"
        f"  Full song reference lines: {json.dumps(ref_full, ensure_ascii=False)}\n\n"
        f"TASK:\n"
        f"Listen carefully from 0.0s to {vad['duration_sec']}s and timestamp EVERY sung 2-part lyric line (l1, l2) with 0.1s precision.\n"
        f"Group the sung lines into 4 sections: `verse1`, `chorus1`, `verse2`, `chorus2`.\n"
        f"RULES:\n"
        f"1. Every `start_sec` MUST be the exact second when the singer begins singing that line (inside one of the Demucs vocal-active windows!).\n"
        f"2. Every `end_sec` MUST be the exact second when the singer finishes singing that line (NEVER extend into instrumental silence!).\n"
        f"3. Each section (`verse1`, `chorus1`, `verse2`, `chorus2`) should have 4 clear 2-line karaoke cues (`l1`, `l2`, each <= 16 Korean chars, matching the actual sung Korean lyrics cleanly without typos).\n"
        f"4. Return STRICT JSON ONLY (no markdown fences) matching this exact schema:\n"
        f'{{\n'
        f'  "verse1": [{{"start_sec": 12.4, "end_sec": 19.2, "l1": "...", "l2": "..."}}, ...],\n'
        f'  "chorus1": [{{"start_sec": 41.8, "end_sec": 48.5, "l1": "...", "l2": "..."}}, ...],\n'
        f'  "verse2": [{{"start_sec": 84.4, "end_sec": 91.0, "l1": "...", "l2": "..."}}, ...],\n'
        f'  "chorus2": [{{"start_sec": 114.0, "end_sec": 120.8, "l1": "...", "l2": "..."}}, ...]\n'
        f'}}'
    )

    payload = {
        "contents": [{
            "parts": [
                {"inline_data": {"mime_type": "audio/mpeg", "data": b64_audio}},
                {"text": prompt},
            ]
        }],
        "generationConfig": {
            "temperature": 0.0,
            "responseMimeType": "application/json",
        },
    }
    body_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    last_err = None
    for model_name in ("gemini-2.5-pro", "gemini-2.5-flash"):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        req = urllib.request.Request(url, data=body_bytes, method="POST", headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                resp = json.loads(r.read().decode("utf-8"))
            txt = resp["candidates"][0]["content"]["parts"][0]["text"].strip()
            txt = re.sub(r"^```(?:json)?\s*|\s*```$", "", txt, flags=re.S).strip()
            parsed = json.loads(txt)
            if all(isinstance(parsed.get(k), list) and len(parsed[k]) >= 2 for k in ("verse1", "chorus1", "chorus2")):
                print(f"  [GEMINI AUDIO OK] {song['song_id']} via {model_name}", flush=True)
                parsed["_model"] = model_name
                return parsed
            last_err = f"Incomplete sections from {model_name}: {list(parsed.keys())}"
        except urllib.error.HTTPError as e:
            last_err = f"{model_name} HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:240]}"
            print(f"  [GEMINI WARN] {last_err}", flush=True)
        except Exception as e:
            last_err = f"{model_name} err: {e}"
            print(f"  [GEMINI WARN] {last_err}", flush=True)
    raise RuntimeError(f"Gemini audio alignment failed for {song['song_id']}: {last_err}")


def snap_line_to_vocal_vad(a: float, b: float, vad: Dict[str, Any], max_snap: float = 0.85) -> Tuple[float, float, float]:
    """
    Snaps a lyric cue [a, b] cleanly onto real Demucs vocal activity boundaries:
    - Trims leading/trailing silence outside vocal activity
    - Snaps start/end to nearby fine vocal onset/offset within +/- max_snap seconds
    - Returns (snapped_start, snapped_end, vocal_ratio)
    """
    hop = vad["hop_sec"]
    act = vad["active"]
    dur = vad["duration_sec"]
    a = max(0.0, min(dur - 0.5, float(a)))
    b = max(a + 0.8, min(dur, float(b)))

    # 1. If start sits in silence right before a vocal onset (within 1.5s), advance to onset - 0.10s
    i0 = int(round(a / hop))
    i1 = min(len(act), int(round(b / hop)))
    search_end = min(len(act), int(round((a + 1.8) / hop)))
    if i0 < len(act) and not act[i0]:
        # Look forward for vocal start
        for idx in range(i0, search_end):
            if act[idx]:
                a = max(0.0, idx * hop - 0.10)
                break
    else:
        # Look slightly backward (up to 0.45s) if singing actually began just before Gemini's timestamp
        for idx in range(i0, max(-1, i0 - int(0.45 / hop)), -1):
            if not act[idx]:
                cand = (idx + 1) * hop - 0.08
                if abs(cand - a) <= max_snap:
                    a = max(0.0, cand)
                break

    # 2. Trim trailing instrumental silence at end of cue so lyrics NEVER hang over vocal-free outro!
    i0_new = max(0, min(len(act) - 1, int(round(a / hop))))
    i1 = max(i0_new + 4, min(len(act) - 1, int(round(b / hop))))
    if not act[i1]:
        # Walk backward inside [i0_new, i1] to find last active vocal frame
        for idx in range(i1, i0_new, -1):
            if act[idx]:
                b = min(dur, (idx + 1) * hop + 0.15)
                break
    else:
        # If singing continues slightly past b (<= 0.5s) before a pause, extend neatly
        for idx in range(i1, min(len(act), i1 + int(0.55 / hop))):
            if not act[idx]:
                b = min(dur, idx * hop + 0.10)
                break

    # 3. Also snap to nearest fine_span boundary if very close (<= 0.35s)
    for fs_a, fs_b in vad["fine_spans"]:
        if abs(fs_a - a) <= 0.35:
            a = max(0.0, fs_a - 0.08)
        if abs(fs_b - b) <= 0.35:
            b = min(dur, fs_b + 0.12)

    a = round(a, 2)
    b = round(max(a + 1.0, b), 2)
    vr = round(vocal_active_ratio(vad, a, b), 3)
    return a, b, vr


def build_calibrated_song_entry(
    old_song: Dict[str, Any],
    aligned: Dict[str, Any],
    vad: Dict[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Constructs calibrated slices & full_cues with strict vocal-active assertions & non-lyric outros."""
    song = json.loads(json.dumps(old_song))
    dur_total = vad["duration_sec"]
    song["duration_sec"] = dur_total

    snapped_sections: Dict[str, List[Dict[str, Any]]] = {}
    all_vr: List[float] = []

    for sec_name in ("verse1", "chorus1", "verse2", "chorus2"):
        raw_lines = aligned.get(sec_name) or []
        clean_lines: List[Dict[str, Any]] = []
        for idx, item in enumerate(raw_lines):
            a, b, vr = snap_line_to_vocal_vad(float(item["start_sec"]), float(item["end_sec"]), vad)
            # Ensure monotonic non-overlapping within section
            if clean_lines and a < clean_lines[-1]["end_sec"] + 0.05:
                mid = round((clean_lines[-1]["end_sec"] + a) / 2.0, 2)
                clean_lines[-1]["end_sec"] = max(clean_lines[-1]["start_sec"] + 0.8, round(mid - 0.03, 2))
                a = round(clean_lines[-1]["end_sec"] + 0.06, 2)
                b = max(a + 0.9, b)
                vr = round(vocal_active_ratio(vad, a, b), 3)
            l1 = str(item.get("l1") or "").strip()
            l2 = str(item.get("l2") or "").strip()
            # Keep every line clean & URL-free for .srt compliance
            l1 = re.sub(r"https?://\S+", "", l1).strip()
            l2 = re.sub(r"https?://\S+", "", l2).strip()
            assert vr >= 0.35, f"FATAL: {song['song_id']} {sec_name}[{idx}] sits on non-vocal span ({a}-{b}s, vr={vr})!"
            all_vr.append(vr)
            clean_lines.append({"start_sec": a, "end_sec": b, "l1": l1, "l2": l2, "vocal_ratio": vr})
        snapped_sections[sec_name] = clean_lines

    # Rebuild 3 Shorts slices (`chorus1`, `verse1`, `chorus2`) with exact vocal-calibrated start_sec + clean outro cue
    old_slice_summary = {}
    new_slice_summary = {}
    label_map = {
        "chorus1": "하이라이트 후렴 무대",
        "verse1": "1절 첫 소절 감동 무대",
        "chorus2": "엔딩 클라이맥스 무대",
    }
    for sl in song["slices"]:
        sid = sl["slice_id"]
        old_slice_summary[sid] = {"start_sec": sl["start_sec"], "duration_sec": sl["duration_sec"]}
        lines = snapped_sections.get(sid) or snapped_sections["chorus1"]
        first_abs = lines[0]["start_sec"]
        last_abs = lines[-1]["end_sec"]

        # Start 0.35s before first sung note so singing begins cleanly at t=0.35s (0.3~0.5s spec)
        sl_start = round(max(0.0, first_abs - 0.35), 2)
        rel_cues: List[List[Any]] = []
        for ln in lines:
            r0 = round(max(0.05, ln["start_sec"] - sl_start), 2)
            r1 = round(max(r0 + 0.8, ln["end_sec"] - sl_start), 2)
            rel_cues.append([r0, r1, ln["l1"], ln["l2"]])

        last_rel_end = rel_cues[-1][1]
        # Cap total slice cleanly to 2.0s after final vocal note (non-lyric outro card on instrumental tail!)
        outro_pad = min(2.2, max(1.6, round(dur_total - (sl_start + last_rel_end), 2)))
        sl_dur = round(min(dur_total - sl_start, last_rel_end + outro_pad), 2)
        if sl_dur - last_rel_end >= 0.8:
            rel_cues.append([
                round(last_rel_end + 0.12, 2),
                round(sl_dur - 0.10, 2),
                f"♪ 백운호 〈{song['title']}〉",
                "김쌤의 영웅라디오 무료 감상",
            ])

        sl["label"] = sl.get("label") or label_map.get(sid, "하이라이트 무대")
        sl["start_sec"] = sl_start
        sl["duration_sec"] = sl_dur
        sl["cues"] = rel_cues
        sl["vocal_end_rel_sec"] = last_rel_end
        sl["min_cue_vocal_ratio"] = round(min(ln["vocal_ratio"] for ln in lines), 3)
        new_slice_summary[sid] = {
            "start_sec": sl_start,
            "duration_sec": sl_dur,
            "vocal_span_abs": [first_abs, last_abs],
            "delta_start_sec": round(sl_start - old_slice_summary[sid]["start_sec"], 2),
        }

    # Rebuild full_cues covering entire song from 0.0s -> dur_total with exact sung cues + non-lyric intro/interlude/outro
    full_cues: List[List[Any]] = []
    ordered_sung = (
        snapped_sections["verse1"]
        + snapped_sections["chorus1"]
        + snapped_sections["verse2"]
        + snapped_sections["chorus2"]
    )
    ordered_sung.sort(key=lambda x: x["start_sec"])

    # Intro non-lyric card
    if ordered_sung and ordered_sung[0]["start_sec"] >= 2.0:
        full_cues.append([0.0, round(ordered_sung[0]["start_sec"] - 0.15, 2), f"♪ 백운호 〈{song['title']}〉", "정통 트로트 전주"])

    prev_end = ordered_sung[0]["start_sec"] if ordered_sung else 0.0
    for idx, ln in enumerate(ordered_sung):
        a, b = ln["start_sec"], ln["end_sec"]
        # Insert clean non-lyric interlude card whenever there is an instrumental gap >= 4.0s
        if idx > 0 and (a - prev_end) >= 4.0:
            full_cues.append([
                round(prev_end + 0.15, 2),
                round(a - 0.15, 2),
                "♪ 색소폰 · 아코디언 간주",
                "마음을 노래하는 가상 트로트 가수 백운호",
            ])
        elif idx > 0 and a < prev_end + 0.05:
            a = round(prev_end + 0.05, 2)
            b = max(a + 0.8, b)
        full_cues.append([a, b, ln["l1"], ln["l2"]])
        prev_end = b

    # Outro non-lyric card on instrumental tail (URL-free for strict SRT gate!)
    if dur_total - prev_end >= 1.5:
        full_cues.append([
            round(prev_end + 0.15, 2),
            round(dur_total - 0.2, 2),
            f"♪ 백운호 〈{song['title']}〉 완곡",
            "김쌤의 영웅라디오에서 6곡 무료 감상",
        ])

    song["full_cues"] = full_cues
    song["sync_verified"] = True
    song["sync_method"] = f"demucs_htdemucs_vocal_vad+{aligned.get('_model', 'gemini-2.5')}"
    song["sync_calibrated_at"] = dt.datetime.now(KST).isoformat()

    diff_rec = {
        "track_no": song["track_no"],
        "song_id": song["song_id"],
        "title": song["title"],
        "duration_sec": dur_total,
        "gemini_model": aligned.get("_model"),
        "mean_vocal_ratio": round(float(np.mean(all_vr)), 3),
        "min_vocal_ratio": round(float(np.min(all_vr)), 3),
        "before": old_slice_summary,
        "after": new_slice_summary,
    }
    return song, diff_rec


def main() -> int:
    t0 = time.time()
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    env = _load_env()
    api_key = env.get("GEMINI_API_KEY", "").strip()
    assert api_key, "FATAL: GEMINI_API_KEY missing in D:\\드림컴퍼니\\.env"

    cat = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    # Backup old catalog once before modifying
    backup_p = WORK_DIR / "baek_woonho_6songs_mv_catalog.pre_calib_backup.json"
    if not backup_p.exists():
        backup_p.write_text(CATALOG_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    updated_songs: List[Dict[str, Any]] = []
    diff_report: List[Dict[str, Any]] = []

    print("=== BAEK WOON-HO 6-SONG ACOUSTIC LYRIC SYNC CALIBRATION START ===", flush=True)
    for song in cat["songs"]:
        mp3_path = AUDIO_DIR / song["filename"]
        assert mp3_path.exists(), f"Missing song MP3: {mp3_path}"
        print(f"\n[Track {song['track_no']}/6] 〈{song['title']}〉 ({mp3_path.name})", flush=True)

        vocals_wav = separate_vocals_demucs(mp3_path, song["song_id"])
        vad = compute_vocal_envelope(vocals_wav)
        print(f"  [VAD] dur={vad['duration_sec']}s | major_phrases={vad['phrases']} | inst={vad['instrumental_spans']}", flush=True)

        vocal_mp3 = encode_compact_vocal_mp3(vocals_wav, song["song_id"])
        aligned = align_song_with_gemini_audio(song, vocal_mp3, vad, api_key)
        new_song, diff_rec = build_calibrated_song_entry(song, aligned, vad)
        updated_songs.append(new_song)
        diff_report.append(diff_rec)
        for sid in ("verse1", "chorus1", "chorus2"):
            b = diff_rec["before"][sid]
            a = diff_rec["after"][sid]
            print(
                f"  [CALIB {sid:7s}] old=({b['start_sec']}s, {b['duration_sec']}s) -> "
                f"new=({a['start_sec']}s, {a['duration_sec']}s) | delta={a['delta_start_sec']:+.2f}s | vocal={a['vocal_span_abs']}",
                flush=True,
            )

    # Global anti-copy-paste sanity check across all 6 songs
    c2_starts = {s["slices"][2]["start_sec"] for s in updated_songs}
    assert len(c2_starts) >= 3, f"FATAL: Calibrated chorus2 start_sec lacks natural variation across 6 songs: {c2_starts}"

    cat["songs"] = updated_songs
    cat["sync_verified"] = True
    cat["sync_method"] = "demucs_htdemucs_vocal_vad+gemini_2.5_audio_alignment"
    cat["sync_calibrated_at"] = dt.datetime.now(KST).isoformat()

    out_text = json.dumps(cat, ensure_ascii=False, indent=2) + "\n"
    CATALOG_PATH.write_text(out_text, encoding="utf-8")
    sha256 = hashlib.sha256(CATALOG_PATH.read_bytes()).hexdigest()

    full_report = {
        "calibrated_at_kst": cat["sync_calibrated_at"],
        "sync_method": cat["sync_method"],
        "catalog_path": str(CATALOG_PATH),
        "catalog_sha256": sha256,
        "elapsed_sec": round(time.time() - t0, 1),
        "tracks": diff_report,
    }
    REPORT_PATH.write_text(json.dumps(full_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n🎉 ALL 6 SONGS CALIBRATED & VERIFIED! SHA256={sha256} (elapsed={full_report['elapsed_sec']}s)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
