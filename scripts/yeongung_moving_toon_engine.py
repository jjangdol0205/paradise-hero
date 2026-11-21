#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
yeongung_moving_toon_engine.py
================================================================================
Authentic Korean Moving-Toon (#영상툰 #애니메이션 #웹툰) Production Engine (v2 Ultra-Fast)
for Div 4 (@김쌤의영웅라디오 & https://paradise-hero.com/booth.html)
================================================================================
"""

import os
import re
import sys
import math
import json
import wave
import time
import asyncio
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import edge_tts
try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = "ffmpeg"

SCRIPT_DIR = Path(__file__).resolve().parent
DIV4_DIR = SCRIPT_DIR.parent
CHAR_DIR = DIV4_DIR / "assets" / "characters"
TOON_ASSETS_DIR = DIV4_DIR / "assets" / "moving_toon"
EPISODES_JSON = DIV4_DIR / "data" / "moving_toon_episodes.json"
OUT_BASE_DIR = DIV4_DIR / "output" / "moving_toon"

WIDTH, HEIGHT = 1080, 1920
FPS = 30
SAMPLE_RATE = 44100

PROHIBITED_WORDS = ["최저가", "할인율", "특가", "폭탄세일"]

VOICE_MAP = {
    "prince":   {"voice": "ko-KR-InJoonNeural",             "rate": "-2%", "pitch": "-2Hz"},
    "mother":   {"voice": "ko-KR-SunHiNeural",              "rate": "-1%", "pitch": "-1Hz"},
    "narrator": {"voice": "ko-KR-HyunsuMultilingualNeural", "rate": "+2%", "pitch": "+0Hz"},
}

PRINCE_RIGS = {
    1:  {"leye": (375, 281), "reye": (468, 274), "mouth": (425, 392), "neck": (440, 470), "hand": (340, 620), "base_open": True,  "glasses": False},
    2:  {"leye": (566, 300), "reye": (660, 297), "mouth": (617, 405), "neck": (612, 485), "hand": (595, 810), "base_open": False, "glasses": False},
    3:  {"leye": (566, 300), "reye": (660, 297), "mouth": (617, 405), "neck": (612, 485), "hand": (580, 620), "base_open": False, "glasses": False},
    4:  {"leye": (566, 299), "reye": (661, 298), "mouth": (617, 408), "neck": (612, 488), "hand": (535, 650), "base_open": True,  "glasses": False},
    5:  {"leye": (566, 300), "reye": (660, 297), "mouth": (617, 405), "neck": (612, 485), "hand": (605, 760), "base_open": False, "glasses": False},
    6:  {"leye": (508, 253), "reye": (602, 253), "mouth": (555, 356), "neck": (555, 445), "hand": (685, 660), "base_open": True,  "glasses": False},
    7:  {"leye": (508, 253), "reye": (602, 253), "mouth": (555, 356), "neck": (555, 445), "hand": (650, 910), "base_open": True,  "glasses": False},
    8:  {"leye": (508, 253), "reye": (602, 253), "mouth": (555, 354), "neck": (555, 445), "hand": (650, 860), "base_open": False, "glasses": False},
    9:  {"leye": (508, 253), "reye": (602, 253), "mouth": (555, 356), "neck": (555, 445), "hand": (675, 680), "base_open": True,  "glasses": False},
    10: {"leye": (508, 253), "reye": (602, 253), "mouth": (555, 356), "neck": (555, 445), "hand": (720, 660), "base_open": True,  "glasses": True},
}

MOTHER_RIGS = {
    "mother_tearful":     {"leye": (358, 290), "reye": (468, 279), "mouth": (428, 397), "neck": (435, 470), "hand": (445, 760), "base_open": False, "glasses": False},
    "mother_blush_happy": {"leye": (376, 330), "reye": (518, 322), "mouth": (453, 466), "neck": (455, 550), "hand": (455, 580), "base_open": True,  "glasses": False},
    "mother_surprised":   {"leye": (368, 286), "reye": (477, 276), "mouth": (433, 396), "neck": (435, 472), "hand": (445, 680), "base_open": True,  "glasses": False},
    "mother_cheering":    {"leye": (360, 290), "reye": (474, 280), "mouth": (427, 401), "neck": (435, 475), "hand": (235, 630), "base_open": True,  "glasses": False},
}

PALETTES = {
    "rainy_amber":   {"top": (228, 236, 248), "bot": (252, 238, 224), "stripe": (215, 226, 242), "fx": "rain"},
    "studio_mint":   {"top": (228, 248, 242), "bot": (248, 252, 245), "stripe": (210, 240, 232), "fx": "sparkle"},
    "peach_glow":    {"top": (255, 236, 232), "bot": (255, 249, 240), "stripe": (255, 224, 220), "fx": "hearts"},
    "sakura_pink":   {"top": (255, 228, 238), "bot": (255, 246, 250), "stripe": (255, 214, 228), "fx": "petals"},
    "royal_rose":    {"top": (252, 226, 240), "bot": (244, 234, 255), "stripe": (246, 212, 232), "fx": "hearts"},
    "lavender_mist": {"top": (236, 232, 252), "bot": (250, 244, 252), "stripe": (226, 220, 246), "fx": "sparkle"},
    "candy_pink":    {"top": (255, 224, 235), "bot": (255, 248, 242), "stripe": (255, 208, 224), "fx": "hearts"},
    "autumn_gold":   {"top": (255, 240, 218), "bot": (255, 250, 238), "stripe": (248, 228, 198), "fx": "petals"},
    "sky_crystal":   {"top": (224, 242, 255), "bot": (246, 252, 255), "stripe": (208, 234, 252), "fx": "sparkle"},
    "emerald_gold":  {"top": (18, 52, 44),    "bot": (10, 28, 24),    "stripe": (26, 68, 56),    "fx": "sparkle"},
}

MUSIC_KEYS = {
    "F_MAJOR": [349.23, 440.00, 523.25, 659.25, 587.33, 523.25, 440.00, 392.00],
    "G_MAJOR": [392.00, 493.88, 587.33, 739.99, 659.25, 587.33, 493.88, 440.00],
    "D_MAJOR": [293.66, 369.99, 440.00, 587.33, 554.37, 493.88, 440.00, 369.99],
    "C_MAJOR": [261.63, 329.63, 392.00, 523.25, 493.88, 440.00, 392.00, 329.63],
    "A_MAJOR": [329.63, 440.00, 554.37, 659.25, 587.33, 554.37, 493.88, 440.00],
}


def sanitize_canvas_text(text: str) -> str:
    """Replace astral Unicode emojis with crisp BMP glyphs supported by Malgun Gothic Bold (zero tofu boxes!)."""
    if not text:
        return ""
    repl = {
        "❤️": "♥", "❤": "♥", "💕": "♥", "💖": "♥", "💚": "♥", "💜": "♥", "💛": "♥", "🤍": "♡",
        "👑": "★", "✨": "★", "🌹": "♥", "💐": "♥", "☔": "♪", "🌙": "♪", "🎙️": "♪", "📞": "♪",
        "👍": "!", "🛍️": "", "📱": "", "❄️": "*", "\ufe0f": "",
    }
    out = text
    for k, v in repl.items():
        out = out.replace(k, v)
    # Strip any remaining non-BMP (> U+FFFF) codepoints so tofu '□' is 100% impossible
    out = "".join(ch for ch in out if ord(ch) <= 0xFFFF)
    return re.sub(r"\s{2,}", " ", out).strip()


def check_zero_prohibited_words(ep: Dict[str, Any]):
    blob = json.dumps(ep, ensure_ascii=False)
    for bad in PROHIBITED_WORDS:
        if bad in blob:
            raise ValueError(f"Prohibited commercial word '{bad}' detected in {ep.get('episode_id')}!")


def get_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf",
        r"C:\Windows\Fonts\NanumGothicBold.ttf",
        r"C:\Windows\Fonts\gulim.ttc",
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


async def synth_tts_segment(text: str, role: str, mp3_path: Path, wav_path: Path) -> np.ndarray:
    cfg = VOICE_MAP.get(role, VOICE_MAP["narrator"])
    sig_path = wav_path.with_suffix(".sig")
    sig_val = f"{cfg['voice']}|{cfg['rate']}|{cfg['pitch']}|{text}"
    if not (wav_path.exists() and sig_path.exists() and sig_path.read_text(encoding="utf-8") == sig_val):
        comm = edge_tts.Communicate(text=text, voice=cfg["voice"], rate=cfg["rate"], pitch=cfg["pitch"])
        await comm.save(str(mp3_path))
        subprocess.run(
            [FFMPEG_EXE, "-y", "-i", str(mp3_path), "-ac", "1", "-ar", str(SAMPLE_RATE), "-f", "wav", str(wav_path)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )
        sig_path.write_text(sig_val, encoding="utf-8")
    with wave.open(str(wav_path), "rb") as wf:
        raw = wf.readframes(wf.getnframes())
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    nz = np.where(np.abs(samples) > 0.007)[0]
    if len(nz) > 100:
        s0 = max(0, int(nz[0]) - int(0.04 * SAMPLE_RATE))
        s1 = min(len(samples), int(nz[-1]) + int(0.07 * SAMPLE_RATE))
        samples = samples[s0:s1]
    peak = np.max(np.abs(samples)) if len(samples) else 1.0
    if peak > 0.02:
        samples = samples * (0.82 / peak)
    return samples


def compute_30fps_lipsync(voice_buf: np.ndarray, total_frames: int) -> List[float]:
    spf = SAMPLE_RATE / FPS
    env = []
    for f in range(total_frames):
        i0 = int(f * spf)
        i1 = min(len(voice_buf), int((f + 1) * spf))
        if i0 >= len(voice_buf) or i1 <= i0:
            env.append(0.0)
        else:
            rms = float(np.sqrt(np.mean(voice_buf[i0:i1] ** 2)))
            val = np.clip((rms - 0.015) / 0.19, 0.0, 1.0)
            env.append(float(val ** 0.75))
    sm = []
    for i in range(len(env)):
        sm.append(round(env[max(0, i - 1)] * 0.22 + env[i] * 0.56 + env[min(len(env) - 1, i + 1)] * 0.22, 4))
    return sm


def make_sfx_bubble_pop(sr=SAMPLE_RATE) -> np.ndarray:
    dur = 0.14
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    phase = 2 * np.pi * np.cumsum(np.linspace(520, 1080, len(t))) / sr
    return (np.sin(phase) * np.exp(-t * 24.0) * 0.24).astype(np.float32)


def make_sfx_whoosh(sr=SAMPLE_RATE) -> np.ndarray:
    dur = 0.22
    n = int(sr * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    noise = np.random.default_rng(42).normal(0, 1, n).astype(np.float32)
    kernel = np.hanning(38)
    kernel /= kernel.sum()
    filt = np.convolve(noise, kernel, mode="same")
    return (filt * (np.sin(np.pi * t / dur) ** 1.6) * 0.22).astype(np.float32)


def make_sfx_sparkle(sr=SAMPLE_RATE) -> np.ndarray:
    dur = 0.48
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    sig = (
        0.16 * np.sin(2 * np.pi * 1567.98 * t) * np.exp(-t * 7.5)
        + 0.13 * np.sin(2 * np.pi * 2093.00 * t) * np.exp(-np.maximum(0, t - 0.05) * 8.0)
        + 0.11 * np.sin(2 * np.pi * 2637.02 * t) * np.exp(-np.maximum(0, t - 0.10) * 8.5)
    )
    return sig.astype(np.float32)


def make_sfx_outro_drop(sr=SAMPLE_RATE) -> np.ndarray:
    dur = 0.95
    t = np.linspace(0, dur, int(sr * dur), endpoint=False)
    phase = 2 * np.pi * np.cumsum(np.linspace(72, 34, len(t))) / sr
    return (np.sin(phase) * np.exp(-t * 3.4) * 0.28 + np.sin(2 * np.pi * 1046.5 * t) * np.exp(-t * 5.0) * 0.12).astype(np.float32)


def make_warm_webtoon_bgm(total_samples: int, theme_key: str, ep_no: int) -> np.ndarray:
    notes = MUSIC_KEYS.get(theme_key, MUSIC_KEYS["F_MAJOR"])
    note_dur = 0.46 + (ep_no % 3) * 0.04
    bgm = np.zeros(total_samples, dtype=np.float32)
    step_n = int(note_dur * SAMPLE_RATE)
    idx, pos = 0, 0
    while pos < total_samples:
        f0 = notes[idx % len(notes)]
        length = min(total_samples - pos, int(step_n * 1.6))
        t = np.arange(length, dtype=np.float32) / SAMPLE_RATE
        tone = (
            0.62 * np.sin(2 * np.pi * f0 * t)
            + 0.24 * np.sin(2 * np.pi * (f0 * 2.0) * t) * np.exp(-t * 4.5)
            + 0.14 * np.sin(2 * np.pi * (f0 * 0.5) * t)
        ) * np.exp(-t * 2.6)
        bgm[pos:pos + length] += (tone * np.minimum(1.0, t / 0.015) * 0.26).astype(np.float32)
        pos += step_n
        idx += 1
    return bgm


async def build_episode_audio(ep: Dict[str, Any], work_dir: Path) -> Tuple[Path, Dict[str, Any]]:
    work_dir.mkdir(parents=True, exist_ok=True)
    beats_meta = []
    voice_segments = []

    for b_idx, beat in enumerate(ep["beats"]):
        mp3_p = work_dir / f"tts_{b_idx:02d}.mp3"
        wav_p = work_dir / f"tts_{b_idx:02d}.wav"
        v_samples = await synth_tts_segment(beat["narration"], beat["speaker"], mp3_p, wav_p)
        tts_dur = len(v_samples) / SAMPLE_RATE

        # GEMINI.md Section 4: STRICT seg_dur >= tts_dur + 0.30s on ALL beats (zero truncation!)
        min_dur = 3.35 if beat["layout"] == "ending_slate" else 3.20
        seg_dur = max(tts_dur + 0.30, min_dur)
        seg_frames = math.ceil(seg_dur * FPS)
        seg_dur = seg_frames / FPS
        seg_samples = int(round(seg_dur * SAMPLE_RATE))

        lead_samples = int(0.10 * SAMPLE_RATE)
        padded_voice = np.zeros(seg_samples, dtype=np.float32)
        end_s = min(seg_samples, lead_samples + len(v_samples))
        padded_voice[lead_samples:end_s] = v_samples[:end_s - lead_samples]

        lipsync_env = compute_30fps_lipsync(padded_voice, seg_frames)
        voice_segments.append(padded_voice)
        beats_meta.append({
            "beat_index": b_idx,
            "tts_dur": round(tts_dur, 3),
            "seg_dur": round(seg_dur, 3),
            "frames": seg_frames,
            "lipsync": lipsync_env,
        })

    voice_track = np.concatenate(voice_segments)
    total_samples = len(voice_track)
    bgm_track = make_warm_webtoon_bgm(total_samples, ep.get("theme_key", "F_MAJOR"), ep.get("episode_no", 1))

    win = int(0.08 * SAMPLE_RATE)
    v_abs = np.convolve(np.abs(voice_track), np.ones(win, dtype=np.float32) / win, mode="same")
    duck_gain = np.where(v_abs > 0.02, 0.22, 0.52).astype(np.float32)
    duck_gain = np.convolve(duck_gain, np.ones(int(0.12 * SAMPLE_RATE), dtype=np.float32) / int(0.12 * SAMPLE_RATE), mode="same")
    mix = voice_track * 0.92 + bgm_track * duck_gain

    sfx_pop = make_sfx_bubble_pop()
    sfx_whoosh = make_sfx_whoosh()
    sfx_sparkle = make_sfx_sparkle()
    sfx_outro = make_sfx_outro_drop()

    cur_s = 0
    for b_idx, bm in enumerate(beats_meta):
        if b_idx == 0:
            L = min(len(sfx_sparkle), total_samples - cur_s)
            mix[cur_s:cur_s + L] += sfx_sparkle[:L]
        elif ep["beats"][b_idx]["layout"] == "ending_slate":
            L = min(len(sfx_outro), total_samples - cur_s)
            mix[cur_s:cur_s + L] += sfx_outro[:L]
        else:
            L = min(len(sfx_whoosh), total_samples - cur_s)
            mix[cur_s:cur_s + L] += sfx_whoosh[:L] * 0.75
            pop_pos = cur_s + int(0.14 * SAMPLE_RATE)
            if pop_pos < total_samples:
                Lp = min(len(sfx_pop), total_samples - pop_pos)
                mix[pop_pos:pop_pos + Lp] += sfx_pop[:Lp]
        if b_idx == len(beats_meta) - 2:
            sp_pos = cur_s + int(0.25 * SAMPLE_RATE)
            if sp_pos < total_samples:
                Ls = min(len(sfx_sparkle), total_samples - sp_pos)
                mix[sp_pos:sp_pos + Ls] += sfx_sparkle[:Ls] * 0.85
        cur_s += int(round(bm["seg_dur"] * SAMPLE_RATE))

    mix = np.tanh(mix * 1.08) * 0.91
    peak = float(np.max(np.abs(mix))) if len(mix) else 0.0
    if peak > 0.938:
        mix = mix * (0.935 / peak)
    peak_db = 20.0 * math.log10(max(float(np.max(np.abs(mix))), 1e-6))

    stereo = np.column_stack([mix, mix])
    pcm16 = np.clip(stereo * 32767.0, -32766, 32766).astype(np.int16)
    wav_out = work_dir / f"{ep['episode_id']}_master.wav"
    with wave.open(str(wav_out), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm16.tobytes())

    meta = {
        "episode_id": ep["episode_id"],
        "total_dur": round(total_samples / SAMPLE_RATE, 3),
        "total_frames": sum(b["frames"] for b in beats_meta),
        "peak_dbfs": round(peak_db, 2),
        "beats": beats_meta,
    }
    return wav_out, meta


class CharacterAssetBank:
    def __init__(self):
        self.princes: Dict[int, np.ndarray] = {}
        self.mothers: Dict[str, np.ndarray] = {}
        self.actions: Dict[str, np.ndarray] = {}
        self._face_state_cache: Dict[Tuple, np.ndarray] = {}
        self._coord_grid_cache: Dict[Tuple[int, int], Tuple[np.ndarray, np.ndarray]] = {}

        for i in range(1, 11):
            self.princes[i] = self._load_rgba_clean(CHAR_DIR / f"raw_prince_{i}.png")
        for nm in MOTHER_RIGS.keys():
            self.mothers[nm] = self._load_rgba_clean(TOON_ASSETS_DIR / f"{nm}.png")
        for act in ["cut_action_hand_rose", "cut_action_coat_umbrella", "cut_action_radio_onair", "cut_action_hanbok_bouquet"]:
            p = TOON_ASSETS_DIR / f"{act}.png"
            if p.exists():
                self.actions[act] = np.array(Image.open(p).convert("RGB"))

        self.p_open_rgb = self.princes[4][:, :, :3]
        self.p_closed_rgb = self.princes[8][:, :, :3]
        self.m_open_rgb = self.mothers["mother_surprised"][:, :, :3]
        self.m_closed_rgb = self.mothers["mother_tearful"][:, :, :3]

    @staticmethod
    def _load_rgba_clean(path: Path) -> np.ndarray:
        rgb = np.array(Image.open(path).convert("RGB"))
        h, w = rgb.shape[:2]
        gray = rgb.mean(axis=2)
        bg_cand = (gray >= 244).astype(np.uint8) * 255
        mask = np.zeros((h + 2, w + 2), np.uint8)
        flood = bg_cand.copy()
        for sx, sy in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (0, h // 2), (w - 1, h // 2)]:
            if flood[sy, sx] == 255:
                cv2.floodFill(flood, mask, (sx, sy), 128)
        is_bg = (flood == 128).astype(np.float32)
        alpha = np.clip((1.0 - cv2.GaussianBlur(is_bg, (5, 5), 0.9) - 0.15) / 0.85, 0.0, 1.0)
        return np.dstack([rgb, (alpha * 255).astype(np.uint8)])

    @staticmethod
    def _blend_mouth(rgba: np.ndarray, dst_mouth: Tuple[int, int], dst_edist: float,
                     src_rgb: np.ndarray, src_mouth: Tuple[int, int], src_edist: float,
                     weight: float, rx: int = 52, ry: int = 25) -> np.ndarray:
        if weight <= 0.02:
            return rgba
        scale = dst_edist / float(src_edist)
        sw, sh = int(rx * 2 / scale), int(ry * 2 / scale)
        sx0, sy0 = src_mouth[0] - sw // 2, src_mouth[1] - sh // 2
        patch = src_rgb[max(0, sy0):sy0 + sh, max(0, sx0):sx0 + sw].copy()
        dw, dh = rx * 2, ry * 2
        patch_rs = cv2.resize(patch, (dw, dh), interpolation=cv2.INTER_LINEAR).astype(np.float32)
        dx0, dy0 = dst_mouth[0] - rx, dst_mouth[1] - ry
        dst_roi = rgba[dy0:dy0 + dh, dx0:dx0 + dw, :3].astype(np.float32)
        yy, xx = np.mgrid[0:dh, 0:dw].astype(np.float32)
        ell = ((xx - rx) / (rx * 0.88)) ** 2 + ((yy - ry) / (ry * 0.85)) ** 2
        ring = (ell > 0.55) & (ell < 1.05)
        if ring.any():
            gain = np.clip((dst_roi[ring].mean(axis=0) + 1.0) / (patch_rs[ring].mean(axis=0) + 1.0), 0.85, 1.15)
            patch_rs = np.clip(patch_rs * gain, 0, 255)
        mask = (np.clip(1.0 - ell, 0.0, 1.0) ** 1.35 * weight)[..., None]
        out = rgba.copy()
        out[dy0:dy0 + dh, dx0:dx0 + dw, :3] = np.clip(patch_rs * mask + dst_roi * (1.0 - mask), 0, 255).astype(np.uint8)
        return out

    def _get_baked_face_state(self, is_mother: bool, key: Any, mouth_bin: int, blink_bin: int, blush_bin: int, target_h: int) -> np.ndarray:
        # Quantize target_h to 12px steps or exact height; cache hits > 97% of frames!
        ck = (is_mother, key, mouth_bin, blink_bin, blush_bin, target_h)
        if ck in self._face_state_cache:
            return self._face_state_cache[ck]

        mouth_open = mouth_bin / 4.0  # 0.0, 0.25, 0.50, 0.75, 1.0
        blink = [0.0, 0.52, 0.96][blink_bin]
        blush = 0.65 if blush_bin else 0.0

        base = self.mothers[key] if is_mother else self.princes[int(key)]
        rig = MOTHER_RIGS[key] if is_mother else PRINCE_RIGS[int(key)]
        work = base.copy()
        edist = math.hypot(rig["reye"][0] - rig["leye"][0], rig["reye"][1] - rig["leye"][1])

        if not is_mother:
            if rig["base_open"]:
                cw = float(np.clip((0.36 - mouth_open) / 0.30, 0.0, 1.0))
                work = self._blend_mouth(work, rig["mouth"], edist, self.p_closed_rgb, (555, 354), 94.0, cw, rx=52, ry=25)
            else:
                ow = float(np.clip((mouth_open - 0.14) / 0.42, 0.0, 1.0))
                work = self._blend_mouth(work, rig["mouth"], edist, self.p_open_rgb, (617, 408), 95.0, ow, rx=52, ry=26)
        else:
            if rig["base_open"]:
                cw = float(np.clip((0.36 - mouth_open) / 0.30, 0.0, 1.0))
                work = self._blend_mouth(work, rig["mouth"], edist, self.m_closed_rgb, (428, 397), 110.5, cw, rx=48, ry=24)
            else:
                ow = float(np.clip((mouth_open - 0.14) / 0.42, 0.0, 1.0))
                work = self._blend_mouth(work, rig["mouth"], edist, self.m_open_rgb, (433, 396), 109.5, ow, rx=48, ry=24)

        if blink > 0.14 or blush > 0.05:
            pil_f = Image.fromarray(work)
            df = ImageDraw.Draw(pil_f, "RGBA")
            if blink > 0.14:
                for ex, ey in [rig["leye"], rig["reye"]]:
                    rx_e = int(edist * (0.19 if rig["glasses"] else 0.23))
                    ry_e = int(edist * 0.11)
                    sy_s = min(work.shape[0] - 1, ey + int(edist * 0.24))
                    sx_s = int(np.clip(ex, 4, work.shape[1] - 5))
                    skin_med = np.median(work[sy_s - 3:sy_s + 3, sx_s - 4:sx_s + 4, :3].reshape(-1, 3), axis=0)
                    skin_rgb = tuple(int(c) for c in skin_med)
                    lid_drop = min(1.0, (blink - 0.10) / 0.75)
                    cur_bot = ey - ry_e + int((ry_e * 2 + 2) * lid_drop)
                    df.ellipse([ex - rx_e, ey - ry_e - 1, ex + rx_e, cur_bot], fill=skin_rgb + (int(248 * lid_drop),))
                    if blink > 0.55:
                        lash_y = cur_bot - 3
                        df.arc([ex - rx_e, lash_y - 6, ex + rx_e, lash_y + 5], start=12, end=168, fill=(32, 20, 20, 245), width=3)
            if blush > 0.05:
                for bx in [rig["leye"][0] - 12, rig["reye"][0] + 12]:
                    by = rig["leye"][1] + int(edist * 0.42)
                    for k in (-9, 0, 9):
                        df.line([(bx + k - 4, by + 6), (bx + k + 4, by - 6)], fill=(238, 108, 128, int(165 * blush)), width=2)
            work = np.array(pil_f)

        h0, w0 = work.shape[:2]
        sc = target_h / float(h0)
        tw = max(32, int(round(w0 * sc)))
        work_s = cv2.resize(work, (tw, target_h), interpolation=cv2.INTER_AREA if sc < 1.0 else cv2.INTER_LINEAR)
        if len(self._face_state_cache) > 220:
            self._face_state_cache.clear()
        self._face_state_cache[ck] = work_s
        return work_s

    def render_rigged_sprite(
        self, is_mother: bool, key: Any, mouth_open: float, blink: float,
        head_deg: float, breath: float, hand_lift: float, blush: float,
        target_h: int, flip_x: bool = False
    ) -> np.ndarray:
        rig = MOTHER_RIGS[key] if is_mother else PRINCE_RIGS[int(key)]
        mouth_bin = int(round(np.clip(mouth_open, 0.0, 1.0) * 4.0))
        blink_bin = 2 if blink > 0.65 else (1 if blink > 0.20 else 0)
        blush_bin = 1 if blush > 0.30 else 0

        work_s = self._get_baked_face_state(is_mother, key, mouth_bin, blink_bin, blush_bin, target_h)
        th, tw = work_s.shape[:2]
        sc = th / 1200.0

        gw, gh = 96, 128
        gx_grid = np.linspace(0, tw - 1, gw, dtype=np.float32)
        gy_grid = np.linspace(0, th - 1, gh, dtype=np.float32)
        xx, yy = np.meshgrid(gx_grid, gy_grid)
        dx_tot = np.zeros_like(xx)
        dy_tot = np.zeros_like(yy)

        # Continuous sub-frame jaw articulation on top of viseme!
        mx, my = rig["mouth"][0] * sc, rig["mouth"][1] * sc
        vowel_drop = max(0.0, mouth_open - 0.20) * 14.0 * sc
        lip_g = np.exp(-(((xx - mx) ** 2) / (2 * (42.0 * sc) ** 2) + ((yy - (my + 10.0 * sc)) ** 2) / (2 * (17.0 * sc) ** 2)))
        jaw_g = np.exp(-(((xx - mx) ** 2) / (2 * (60.0 * sc) ** 2) + ((yy - (my + 32.0 * sc)) ** 2) / (2 * (48.0 * sc) ** 2)))
        dy_tot -= vowel_drop * lip_g
        dy_tot -= (vowel_drop * 0.58) * jaw_g

        nx, ny = rig["neck"][0] * sc, rig["neck"][1] * sc
        head_w = 1.0 / (1.0 + np.exp((yy - ny) / (28.0 * sc)))
        rad = math.radians(head_deg)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        dx_r = (xx - nx) * (cos_a - 1.0) - (yy - ny) * sin_a
        dy_r = (xx - nx) * sin_a + (yy - ny) * (cos_a - 1.0)
        dx_tot -= dx_r * head_w
        dy_tot -= (dy_r + abs(head_deg) * 0.9 * sc) * head_w

        body_w = 1.0 - head_w
        torso_lift = breath * 5.2 * sc * np.exp(-((yy - (ny + 210.0 * sc)) ** 2) / (2 * (210.0 * sc) ** 2))
        dy_tot += torso_lift * body_w

        hx, hy = rig["hand"][0] * sc, rig["hand"][1] * sc
        hand_g = np.exp(-(((xx - hx) ** 2) / (2 * (125.0 * sc) ** 2) + ((yy - hy) ** 2) / (2 * (145.0 * sc) ** 2)))
        dy_tot += hand_lift * 12.5 * sc * hand_g
        dx_tot -= hand_lift * 4.5 * sc * hand_g

        dx_full = cv2.resize(dx_tot, (tw, th), interpolation=cv2.INTER_LINEAR)
        dy_full = cv2.resize(dy_tot, (tw, th), interpolation=cv2.INTER_LINEAR)

        gkey = (tw, th)
        if gkey not in self._coord_grid_cache:
            bx = np.broadcast_to(np.arange(tw, dtype=np.float32)[None, :], (th, tw)).copy()
            by = np.broadcast_to(np.arange(th, dtype=np.float32)[:, None], (th, tw)).copy()
            self._coord_grid_cache[gkey] = (bx, by)
        base_x, base_y = self._coord_grid_cache[gkey]

        warped = cv2.remap(work_s, base_x + dx_full, base_y + dy_full, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        if flip_x:
            warped = cv2.flip(warped, 1)
        return warped


_BG_CACHE: Dict[Tuple[int, int, str], np.ndarray] = {}


def get_base_panel_bg(w: int, h: int, pal_name: str) -> np.ndarray:
    pal = PALETTES.get(pal_name, PALETTES["sakura_pink"])
    cache_key = (w, h, pal_name)
    if cache_key not in _BG_CACHE:
        yy = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
        top = np.array(pal["top"], dtype=np.float32)
        bot = np.array(pal["bot"], dtype=np.float32)
        grad = np.clip(top * (1.0 - yy) + bot * yy, 0, 255)
        bg0 = np.broadcast_to(grad[:, None, :], (h, w, 3)).astype(np.uint8).copy()
        pil0 = Image.fromarray(bg0)
        d0 = ImageDraw.Draw(pil0, "RGBA")
        scol = pal["stripe"] + (90,)
        for k in range(-h, w + h, 56):
            d0.line([(k, 0), (k - h // 2, h // 2)], fill=scol, width=14)
        _BG_CACHE[cache_key] = np.array(pil0)
    return _BG_CACHE[cache_key].copy()


def draw_fx_particles(draw: ImageDraw.ImageDraw, x0: int, y0: int, w: int, h: int, pal_name: str, t: float):
    fx = PALETTES.get(pal_name, PALETTES["sakura_pink"])["fx"]
    for i in range(12):
        seed = (i * 137 + 29)
        bx = x0 + int((seed * 73 + t * (18 if i % 2 == 0 else -14)) % w)
        by = y0 + int((seed * 113 + t * (48 if fx != "rain" else 280)) % h)
        if fx == "rain":
            draw.line([(bx, by), (bx - 8, by + 44)], fill=(255, 255, 255, 145), width=2)
        elif fx == "hearts":
            rr = int((10 + (i % 3) * 4) * (1.0 + 0.15 * math.sin(t * 4.5 + i)))
            hc = (255, 125, 162, 150)
            draw.ellipse([bx - rr, by - rr, bx, by], fill=hc)
            draw.ellipse([bx, by - rr, bx + rr, by], fill=hc)
            draw.polygon([(bx - rr, by - rr // 3), (bx + rr, by - rr // 3), (bx, by + rr)], fill=hc)
        elif fx == "petals":
            pw, ph = 12 + (i % 3) * 4, 7 + (i % 2) * 3
            draw.ellipse([bx - pw, by - ph, bx + pw, by + ph], fill=(255, 182, 205, 165))
        else:
            rad = 18 + (i % 4) * 12
            draw.ellipse([bx - rad, by - rad, bx + rad, by + rad], fill=(255, 255, 255, 65))
            if i % 3 == 0:
                draw.line([(bx - 13, by), (bx + 13, by)], fill=(255, 255, 255, 205), width=2)
                draw.line([(bx, by - 13), (bx, by + 13)], fill=(255, 255, 255, 205), width=2)


def alpha_blit(canvas: np.ndarray, sprite_rgba: np.ndarray, x: int, y: int):
    ch, cw = canvas.shape[:2]
    sh, sw = sprite_rgba.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(cw, x + sw), min(ch, y + sh)
    if x1 <= x0 or y1 <= y0:
        return
    sx0, sy0 = x0 - x, y0 - y
    sub_s = sprite_rgba[sy0:sy0 + (y1 - y0), sx0:sx0 + (x1 - x0)]
    a = sub_s[:, :, 3:4].astype(np.float32) / 255.0
    dst = canvas[y0:y1, x0:x1].astype(np.float32)
    canvas[y0:y1, x0:x1] = np.clip(sub_s[:, :, :3].astype(np.float32) * a + dst * (1.0 - a), 0, 255).astype(np.uint8)


def draw_oval_speech_bubble(
    draw: ImageDraw.ImageDraw, text: str, cx: int, cy: int, tail_target: Tuple[int, int],
    pop_progress: float, font_b: ImageFont.FreeTypeFont
):
    clean = sanitize_canvas_text(text)
    if not clean or pop_progress <= 0.02:
        return
    sc = (0.55 + 0.51 * (pop_progress / 0.7)) if pop_progress < 0.7 else (1.06 - 0.06 * ((pop_progress - 0.7) / 0.3))
    bbox = draw.textbbox((0, 0), clean, font=font_b)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    rx = min(int((tw // 2 + 54) * sc), 465)
    ry = int((th // 2 + 38) * sc)

    tx, ty = tail_target
    ang = math.atan2(ty - cy, tx - cx)
    base1 = (cx + int(math.cos(ang - 0.25) * rx * 0.55), cy + int(math.sin(ang - 0.25) * ry * 0.75))
    base2 = (cx + int(math.cos(ang + 0.25) * rx * 0.55), cy + int(math.sin(ang + 0.25) * ry * 0.75))
    tip = (cx + int(math.cos(ang) * (rx * 0.72 + 28)), cy + int(math.sin(ang) * (ry + 34)))

    ink = (34, 22, 42, 255)
    draw.ellipse([cx - rx + 4, cy - ry + 6, cx + rx + 4, cy + ry + 6], fill=(30, 20, 35, 38))
    draw.polygon([base1, base2, tip], fill=(255, 255, 255, 255), outline=ink, width=4)
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(255, 255, 255, 255), outline=ink, width=4)
    draw.polygon([
        (cx + int(math.cos(ang - 0.22) * (rx * 0.52)), cy + int(math.sin(ang - 0.22) * (ry * 0.70))),
        (cx + int(math.cos(ang + 0.22) * (rx * 0.52)), cy + int(math.sin(ang + 0.22) * (ry * 0.70))),
        (cx + int(math.cos(ang) * (rx * 0.68 + 14)), cy + int(math.sin(ang) * (ry + 18))),
    ], fill=(255, 255, 255, 255))
    if pop_progress > 0.25:
        draw.text((cx, cy - 3), clean, font=font_b, fill=(28, 18, 34, 255), anchor="mm")


def wrap_subtitle_lines(text: str, max_chars: int = 19) -> List[str]:
    clean = sanitize_canvas_text(text)
    if len(clean) <= max_chars:
        return [clean]
    words = clean.split(" ")
    l1, l2, cur = [], [], 0
    for w in words:
        if not l2 and (cur + len(w) <= max_chars or not l1):
            l1.append(w)
            cur += len(w) + 1
        else:
            l2.append(w)
    return [" ".join(l1), " ".join(l2)] if l2 else [" ".join(l1)]


def compute_natural_blink(global_t: float, offset: float = 0.0) -> float:
    cycle = (global_t + offset) % 3.15
    return math.sin(math.pi * (cycle / 0.18)) if cycle < 0.18 else 0.0


def render_episode_video(ep: Dict[str, Any], wav_path: Path, meta: Dict[str, Any], bank: CharacterAssetBank, out_mp4: Path):
    font_bubble = get_font(38, bold=True)
    font_tag = get_font(29, bold=True)
    font_sub = get_font(44, bold=True)
    font_end_h1 = get_font(48, bold=True)
    font_end_h2 = get_font(35, bold=True)
    font_end_url = get_font(41, bold=True)

    cmd = [
        FFMPEG_EXE, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}", "-pix_fmt", "rgb24", "-r", str(FPS), "-i", "-",
        "-i", str(wav_path),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-shortest",
        str(out_mp4)
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    global_f = 0
    for b_idx, beat in enumerate(ep["beats"]):
        bm = meta["beats"][b_idx]
        n_frames = bm["frames"]
        lipsync_arr = bm["lipsync"]
        layout = beat["layout"]
        speaker = beat["speaker"]
        pal_name = beat.get("palette", "sakura_pink")

        for lf in range(n_frames):
            global_t = global_f / FPS
            local_t = lf / FPS
            voice_open = lipsync_arr[lf]

            canvas = np.full((HEIGHT, WIDTH, 3), (252, 249, 246), dtype=np.uint8)

            breath_p = math.sin(global_t * 2.4)
            breath_m = math.sin(global_t * 2.6 + 1.2)
            blink_p = compute_natural_blink(global_t, offset=0.4)
            blink_m = compute_natural_blink(global_t, offset=1.7)

            p_mouth = voice_open if speaker == "prince" else 0.0
            m_mouth = voice_open if speaker == "mother" else (voice_open * 0.25 if speaker == "narrator" and "mother" in layout else 0.0)

            p_head = math.sin(global_t * 5.2) * 1.9 * (0.35 + p_mouth)
            m_head = math.sin(global_t * 4.8 + 0.8) * 1.8 * (0.35 + m_mouth)
            p_hand = 0.5 + 0.5 * math.sin(global_t * 3.2) * (0.4 + 0.6 * p_mouth)
            m_hand = 0.5 + 0.5 * math.sin(global_t * 3.0 + 0.9) * (0.4 + 0.6 * m_mouth)

            if layout == "ending_slate":
                canvas[:, :, :] = get_base_panel_bg(WIDTH, HEIGHT, "emerald_gold")
                featured_p = int(beat.get("prince_id", 1))
                trio = [1, featured_p if featured_p not in (1, 3) else 8, 3]
                xs = [-65, 235, 540]
                for ti, pid in enumerate(trio):
                    sp = bank.render_rigged_sprite(
                        False, pid, mouth_open=0.35 if ti == 1 else 0.0,
                        blink=compute_natural_blink(global_t, ti * 0.9),
                        head_deg=math.sin(global_t * 2.5 + ti) * 1.4,
                        breath=math.sin(global_t * 2.3 + ti), hand_lift=0.5, blush=0.0,
                        target_h=880
                    )
                    alpha_blit(canvas, sp, xs[ti], 470)

                pil_c = Image.fromarray(canvas)
                dc = ImageDraw.Draw(pil_c, "RGBA")
                draw_fx_particles(dc, 0, 0, WIDTH, HEIGHT, "emerald_gold", global_t)
                dc.rounded_rectangle([54, 88, 1026, 360], radius=32, fill=(14, 40, 34, 240), outline=(242, 202, 108, 255), width=4)
                dc.text((540, 158), "★ 파라다이스히어로 기념 사진관 ★", font=font_end_h1, fill=(255, 224, 130, 255), anchor="mm")
                dc.text((540, 235), "영상 속 백운호 10종 캐릭터와 추억 투샷 무료 인화!", font=font_end_h2, fill=(255, 255, 255, 255), anchor="mm")
                dc.rounded_rectangle([150, 278, 930, 340], radius=22, fill=(242, 202, 108, 255))
                dc.text((540, 309), "검색창에  paradise-hero.com", font=font_end_url, fill=(18, 32, 28, 255), anchor="mm")

                dc.rounded_rectangle([74, 1525, 1006, 1695], radius=30, fill=(255, 248, 230, 248), outline=(242, 202, 108, 255), width=4)
                dc.text((540, 1582), "구독 · 좋아요 누르시면 매일 새 영상툰이 찾아옵니다 ♥", font=font_end_h2, fill=(28, 20, 24, 255), anchor="mm")
                dc.text((540, 1644), "@김쌤의영웅라디오  |  paradise-hero.com", font=font_end_h2, fill=(16, 98, 76, 255), anchor="mm")
                canvas = np.array(pil_c)

            elif layout in ("split_action_mother", "split_action_prince"):
                pw, ph_top, ph_bot = 1012, 640, 1182
                act_img = bank.actions.get(beat.get("action_img", "cut_action_radio_onair"))
                if act_img is not None:
                    ah, aw = act_img.shape[:2]
                    zoom = 1.03 + 0.06 * (local_t / max(bm["seg_dur"], 1.0))
                    cw_c = int(aw / zoom)
                    ch_c = int(cw_c * ph_top / pw)
                    if ch_c > ah:
                        ch_c = ah
                        cw_c = int(ch_c * pw / ph_top)
                    x0, y0 = (aw - cw_c) // 2, (ah - ch_c) // 2
                    top_crop = cv2.resize(act_img[y0:y0 + ch_c, x0:x0 + cw_c], (pw, ph_top), interpolation=cv2.INTER_LINEAR)
                else:
                    top_crop = get_base_panel_bg(pw, ph_top, pal_name)
                canvas[34:34 + ph_top, 34:34 + pw] = top_crop

                reveal = min(1.0, local_t / 0.18)
                slide_dy = int((1.0 - reveal) * 48)
                bot_panel = get_base_panel_bg(pw, ph_bot, pal_name)

                if layout == "split_action_mother":
                    sp = bank.render_rigged_sprite(
                        True, beat["mother_pose"], m_mouth, blink_m, m_head, breath_m, m_hand,
                        blush=0.7 if "blush" in beat["mother_pose"] else 0.15, target_h=1050
                    )
                    alpha_blit(bot_panel, sp, (pw - sp.shape[1]) // 2 + 25, 145 + slide_dy)
                    tail_xy = (560, 1080)
                else:
                    sp = bank.render_rigged_sprite(
                        False, beat["prince_id"], p_mouth, blink_p, p_head, breath_p, p_hand,
                        blush=0.45, target_h=1060
                    )
                    alpha_blit(bot_panel, sp, (pw - sp.shape[1]) // 2 - 20, 135 + slide_dy)
                    tail_xy = (555, 1060)

                canvas[704:704 + ph_bot, 34:34 + pw] = bot_panel

                # SINGLE PIL conversion per frame!
                pil_c = Image.fromarray(canvas)
                dc = ImageDraw.Draw(pil_c, "RGBA")
                draw_fx_particles(dc, 34, 704, pw, ph_bot, pal_name, global_t)
                dc.rectangle([34, 34, 1046, 674], outline=(28, 20, 34, 255), width=5)
                dc.rectangle([34, 704, 1046, 1886], outline=(28, 20, 34, 255), width=5)

                pop_p = min(1.0, max(0.0, (local_t - 0.10) / 0.24))
                draw_oval_speech_bubble(dc, beat["bubble_text"], 540, 815, tail_xy, pop_p, font_bubble)
                if beat.get("arrow_tag"):
                    dc.text((84, 965), sanitize_canvas_text(beat["arrow_tag"]), font=font_tag, fill=(52, 34, 62, 245), stroke_width=4, stroke_fill=(255, 255, 255, 240))
                if beat.get("subtitle"):
                    lines = wrap_subtitle_lines(beat["subtitle"], max_chars=19)
                    sub_fill = (255, 245, 168, 255) if speaker == "prince" else (255, 255, 255, 255)
                    base_y = 1420 if len(lines) == 1 else 1392
                    for li, ln in enumerate(lines):
                        dc.text((540, base_y + li * 54), ln, font=font_sub, fill=sub_fill, stroke_width=9, stroke_fill=(18, 12, 24, 255), anchor="mm")
                canvas = np.array(pil_c)

            elif layout == "dual_dialogue":
                pw, ph = 1012, 1852
                panel = get_base_panel_bg(pw, ph, pal_name)
                sp_m = bank.render_rigged_sprite(
                    True, beat["mother_pose"], m_mouth, blink_m, m_head, breath_m, m_hand,
                    blush=0.75 if "blush" in beat["mother_pose"] else 0.25, target_h=1120, flip_x=False
                )
                pid = int(beat["prince_id"])
                sp_p = bank.render_rigged_sprite(
                    False, pid, p_mouth, blink_p, p_head, breath_p, p_hand,
                    blush=0.45, target_h=1180, flip_x=(pid == 1)
                )
                alpha_blit(panel, sp_m, -95, 590)
                px_dual = 235 if pid in (2, 3, 4, 5) else (355 if pid == 1 else 285)
                alpha_blit(panel, sp_p, px_dual, 515)
                canvas[34:34 + ph, 34:34 + pw] = panel

                pil_c = Image.fromarray(canvas)
                dc = ImageDraw.Draw(pil_c, "RGBA")
                draw_fx_particles(dc, 34, 34, pw, 520, pal_name, global_t)
                dc.rectangle([34, 34, 1046, 1886], outline=(28, 20, 34, 255), width=5)

                pop_p = min(1.0, max(0.0, (local_t - 0.08) / 0.24))
                b_spk = beat.get("bubble_speaker", speaker)
                tail_xy = (310, 760) if b_spk == "mother" else (740, 690)
                bx_c = 450 if b_spk == "mother" else 575
                draw_oval_speech_bubble(dc, beat["bubble_text"], bx_c, 285, tail_xy, pop_p, font_bubble)
                if beat.get("arrow_tag"):
                    tx = 75 if b_spk == "mother" else 620
                    dc.text((tx, 505), sanitize_canvas_text(beat["arrow_tag"]), font=font_tag, fill=(52, 34, 62, 245), stroke_width=4, stroke_fill=(255, 255, 255, 240))
                if beat.get("subtitle"):
                    lines = wrap_subtitle_lines(beat["subtitle"], max_chars=19)
                    sub_fill = (255, 245, 168, 255) if speaker == "prince" else (255, 255, 255, 255)
                    base_y = 1420 if len(lines) == 1 else 1392
                    for li, ln in enumerate(lines):
                        dc.text((540, base_y + li * 54), ln, font=font_sub, fill=sub_fill, stroke_width=9, stroke_fill=(18, 12, 24, 255), anchor="mm")
                canvas = np.array(pil_c)

            else:
                pw, ph = 1012, 1852
                panel = get_base_panel_bg(pw, ph, pal_name)
                # Quantize zoom_h to 4 steps across the beat so face cache hits 98% of frames while still breathing/zooming!
                step_z = int(4 * local_t / max(bm["seg_dur"], 1.0))
                zoom_h = 1360 + step_z * 12
                if layout == "solo_mother_closeup":
                    sp = bank.render_rigged_sprite(
                        True, beat["mother_pose"], m_mouth, blink_m, m_head, breath_m, m_hand,
                        blush=0.8 if "blush" in beat["mother_pose"] else 0.2, target_h=zoom_h
                    )
                    alpha_blit(panel, sp, (pw - sp.shape[1]) // 2 + 15, 455 - step_z * 4)
                    tail_xy = (530, 660)
                else:
                    sp = bank.render_rigged_sprite(
                        False, beat["prince_id"], p_mouth, blink_p, p_head, breath_p, p_hand,
                        blush=0.65, target_h=zoom_h
                    )
                    alpha_blit(panel, sp, (pw - sp.shape[1]) // 2 - 35, 430 - step_z * 4)
                    tail_xy = (545, 640)

                canvas[34:34 + ph, 34:34 + pw] = panel
                pil_c = Image.fromarray(canvas)
                dc = ImageDraw.Draw(pil_c, "RGBA")
                draw_fx_particles(dc, 34, 34, pw, ph, pal_name, global_t)
                dc.rectangle([34, 34, 1046, 1886], outline=(28, 20, 34, 255), width=5)

                pop_p = min(1.0, max(0.0, (local_t - 0.08) / 0.24))
                draw_oval_speech_bubble(dc, beat["bubble_text"], 540, 255, tail_xy, pop_p, font_bubble)
                if beat.get("arrow_tag"):
                    dc.text((86, 455), sanitize_canvas_text(beat["arrow_tag"]), font=font_tag, fill=(52, 34, 62, 245), stroke_width=4, stroke_fill=(255, 255, 255, 240))
                if beat.get("subtitle"):
                    lines = wrap_subtitle_lines(beat["subtitle"], max_chars=19)
                    sub_fill = (255, 245, 168, 255) if speaker == "prince" else (255, 255, 255, 255)
                    base_y = 1420 if len(lines) == 1 else 1392
                    for li, ln in enumerate(lines):
                        dc.text((540, base_y + li * 54), ln, font=font_sub, fill=sub_fill, stroke_width=9, stroke_fill=(18, 12, 24, 255), anchor="mm")
                canvas = np.array(pil_c)

            proc.stdin.write(canvas.tobytes())
            global_f += 1

    proc.stdin.close()
    proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg encode failed for {ep['episode_id']} with code {proc.returncode}")


async def produce_episodes(episode_ids: List[str] = None) -> List[Dict[str, Any]]:
    data = json.loads(EPISODES_JSON.read_text(encoding="utf-8"))
    episodes = data["episodes"]
    if episode_ids:
        episodes = [e for e in episodes if e["episode_id"] in episode_ids]

    OUT_BASE_DIR.mkdir(parents=True, exist_ok=True)
    bank = CharacterAssetBank()
    results = []

    for ep in episodes:
        t0 = time.time()
        check_zero_prohibited_words(ep)
        ep_dir = OUT_BASE_DIR / ep["episode_id"]
        ep_dir.mkdir(parents=True, exist_ok=True)

        wav_path, meta = await build_episode_audio(ep, ep_dir)
        mp4_path = OUT_BASE_DIR / f"{ep['episode_id']}.mp4"
        render_episode_video(ep, wav_path, meta, bank, mp4_path)

        meta["mp4_path"] = str(mp4_path)
        meta["title"] = ep["title"]
        meta["render_sec"] = round(time.time() - t0, 2)
        (ep_dir / "render_report.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[OK] {ep['episode_id']} rendered in {meta['render_sec']}s -> {mp4_path} ({meta['total_dur']}s, peak {meta['peak_dbfs']} dBFS)", flush=True)
        results.append(meta)

    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", nargs="*", default=None, help="Episode IDs to render (default: all)")
    args = parser.parse_args()
    asyncio.run(produce_episodes(args.episodes))


if __name__ == "__main__":
    main()
