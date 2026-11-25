#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
D:\드림컴퍼니\4사업부\scripts\build_hero_ep1_radio_master.py
================================================================================
4사업부 (HERO · https://paradise-hero.com · @김쌤의영웅라디오)
정규 1화 [연속극장 1부] 어머님 감동 사연 2편 & 백운호 대표곡 3곡 완곡 방송 마스터 빌더

핵심 안전 가드레일 (Hard Asserts):
1. 3곡 고유 음원 MD5 해시 강제 검증:
   - 1곡 〈어머니의 봄날〉  -> assets/audio/baek_woonho_01_mothers_spring.mp3
   - 2곡 〈백운호 연가〉    -> assets/audio/baek_woonho_02_yeonga.mp3
   - 3곡 〈다시 피는 동백꽃〉 -> assets/audio/baek_woonho_04_camellia.mp3
   세 파일의 MD5 해시 3종이 모두 상이하고 파형 상관계수가 중복 기준 미만임을 코드로 Assert.
2. 렌더링 완료 MP4 사후 음향 역검증:
   최종 MP4 내부 1곡·2곡·3곡 타임스탬프 구간을 디코딩해 각각 1·2·3번 원본 MP3와
   최고 상관계수(> 0.80)로 정확히 1:1 매칭됨을 Assert (동일 곡 중복 삽입 원천 차단).
3. 공식 용어 사전(data/hq_glossary.json) 기반 SRT·자막 100% 정규화 (배군노·박공기·님님·황영웅 0건).
4. 저부하 순차 실행 (BelowNormal 우선순위, -threads 2, 단일 워커).
================================================================================
"""

from __future__ import annotations

import asyncio
import ctypes
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import wave
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

os.environ["PYTHONUTF8"] = "1"
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        # BelowNormal priority class to prevent overheating / Kernel-Power 41
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
    except Exception:
        pass

import edge_tts
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
DIV4_DIR = Path(__file__).resolve().parent.parent
HQ_ROOT = DIV4_DIR.parent
AUDIO_DIR = DIV4_DIR / "assets" / "audio"
WATERCOLOR_DIR = DIV4_DIR / "assets" / "watercolor_drama"
MV_CATALOG_PATH = DIV4_DIR / "data" / "baek_woonho_6songs_mv_catalog.json"
GLOSSARY_PATH = HQ_ROOT / "data" / "hq_glossary.json"
OUT_DIR = DIV4_DIR / "outputs" / "ep1_flagship_20min"
WORK_DIR = HQ_ROOT / ".cache" / "tmp" / "hero_ep1_3songs_rebuild_work"
MR_BED_WAV = HQ_ROOT / ".cache" / "tmp" / "baek_music_studio_work" / "stage1_raw_mr.wav"

SR = 48000
VIDEO_W, VIDEO_H = 1920, 1080

VOICE_DJ = ("ko-KR-InJoonNeural", "-4%", "-2Hz")
VOICE_LETTER = ("ko-KR-SunHiNeural", "-4%", "-1Hz")

# Strictly pinned 3 distinct master MP3 files for Radio Ep.1
EP1_TRACK_SPECS: List[Dict[str, Any]] = [
    {
        "slot": 1,
        "song_id": "mothers_spring",
        "title": "어머니의 봄날",
        "mp3_filename": "baek_woonho_01_mothers_spring.mp3",
        "bg_image": "ep1_ch3_baek_watercolor_stage_burgundy.png",
        "chapter_badge": "ON AIR · 김쌤의 영웅라디오 | 3부 · 백운호 〈어머니의 봄날〉 완곡",
        "pill_label": "♪ 백운호 제1대표곡 · 〈어머니의 봄날〉",
    },
    {
        "slot": 2,
        "song_id": "baek_woon_ho_yeonga",
        "title": "백운호 연가",
        "mp3_filename": "baek_woonho_02_yeonga.mp3",
        "bg_image": "ep1_ch5_baek_woon_lake_sunset_watercolor.png",
        "chapter_badge": "ON AIR · 김쌤의 영웅라디오 | 5부 · 백운호 〈백운호 연가〉 완곡",
        "pill_label": "♪ 백운호 제2대표곡 · 〈백운호 연가〉",
    },
    {
        "slot": 3,
        "song_id": "blooming_camellia",
        "title": "다시 피는 동백꽃",
        "mp3_filename": "baek_woonho_04_camellia.mp3",
        "bg_image": "ep1_ch6_winter_camellia_bloom_watercolor.png",
        "chapter_badge": "ON AIR · 김쌤의 영웅라디오 | 7부 · 백운호 〈다시 피는 동백꽃〉 완곡",
        "pill_label": "♪ 백운호 제3대표곡 · 〈다시 피는 동백꽃〉",
    },
]

FORBIDDEN_TERMS = [
    "황영웅",
    "배군노",
    "배군호",
    "배군의",
    "박공기",
    "왕공",
    "님님",
    "beable9489@gmail.com",
    "lemonsqueezy",
]

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\malgunbd.ttf",
    r"D:\드림컴퍼니\3사업부\src\fonts\Pretendard-Black.otf",
    r"C:\Windows\Fonts\malgun.ttf",
]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for fp in FONT_CANDIDATES:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()


def md5_file(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def decode_mono_8k(path: Path, ss: float = 0.0, dur: Optional[float] = None) -> np.ndarray:
    cmd = [FFMPEG_EXE, "-v", "error", "-threads", "2"]
    if ss > 0:
        cmd += ["-ss", f"{ss:.2f}"]
    cmd += ["-i", str(path)]
    if dur is not None:
        cmd += ["-t", f"{dur:.2f}"]
    cmd += ["-ac", "1", "-ar", "8000", "-f", "f32le", "pipe:1"]
    raw = subprocess.run(cmd, stdout=subprocess.PIPE, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def envelope_corr(a: np.ndarray, b: np.ndarray, step: int = 400) -> float:
    n = min(len(a), len(b)) // step
    if n < 20:
        return 0.0
    ea = np.sqrt(np.mean(a[: n * step].reshape(n, step) ** 2, axis=1) + 1e-12)
    eb = np.sqrt(np.mean(b[: n * step].reshape(n, step) ** 2, axis=1) + 1e-12)
    ea = (ea - ea.mean()) / (ea.std() + 1e-9)
    eb = (eb - eb.mean()) / (eb.std() + 1e-9)
    return float(np.mean(ea * eb))


def best_shift_envelope_corr(long_sig: np.ndarray, needle_sig: np.ndarray, step: int = 400) -> float:
    na = len(long_sig) // step
    nb = len(needle_sig) // step
    if na < nb or nb < 20:
        return envelope_corr(long_sig, needle_sig, step=step)
    ea = np.sqrt(np.mean(long_sig[: na * step].reshape(na, step) ** 2, axis=1) + 1e-12)
    eb = np.sqrt(np.mean(needle_sig[: nb * step].reshape(nb, step) ** 2, axis=1) + 1e-12)
    eb = (eb - eb.mean()) / (eb.std() + 1e-9)
    best = -1.0
    for shift in range(0, na - nb + 1, 2):
        w = ea[shift : shift + nb]
        w = (w - w.mean()) / (w.std() + 1e-9)
        c = float(np.mean(w * eb))
        if c > best:
            best = c
    return best


def assert_three_distinct_song_mp3s() -> Dict[int, Dict[str, Any]]:
    """HARD ASSERT: All 3 Ep.1 tracks must exist, be >2MB, >140s, have 3 distinct MD5s & low cross-corr."""
    verified: Dict[int, Dict[str, Any]] = {}
    md5_set = set()
    chorus_sigs: Dict[int, np.ndarray] = {}

    for spec in EP1_TRACK_SPECS:
        p = AUDIO_DIR / spec["mp3_filename"]
        assert p.exists(), f"FATAL: Missing song MP3 for slot {spec['slot']} ({spec['title']}): {p}"
        sz = p.stat().st_size
        assert sz > 2_000_000, f"FATAL: Song MP3 too small ({sz}B): {p}"
        h = md5_file(p)
        assert h not in md5_set, f"FATAL: Duplicate MD5 hash detected across Ep.1 songs! slot={spec['slot']} file={p.name} md5={h}"
        md5_set.add(h)

        sig = decode_mono_8k(p)
        dur = len(sig) / 8000.0
        rms = float(np.sqrt(np.mean(sig ** 2)))
        assert dur >= 140.0, f"FATAL: Song too short ({dur:.1f}s): {p.name}"
        assert rms >= 0.04, f"FATAL: Song appears silent (rms={rms:.4f}): {p.name}"
        chorus_sigs[spec["slot"]] = sig[40 * 8000 : 80 * 8000]
        verified[spec["slot"]] = {
            **spec,
            "path": p,
            "md5": h,
            "size_bytes": sz,
            "duration_sec": round(dur, 2),
            "rms": round(rms, 4),
        }

    assert len(md5_set) == 3, f"FATAL: Expected 3 unique song MD5 hashes, got {len(md5_set)}"
    for i in (1, 2, 3):
        for j in (1, 2, 3):
            if i < j:
                cc = best_shift_envelope_corr(chorus_sigs[i], chorus_sigs[j][: 25 * 8000])
                assert cc < 0.78, f"FATAL: Songs {i} and {j} have suspiciously identical waveform envelope (corr={cc:.3f})!"
                print(f"  [AUDIO DISTINCT CHECK OK] Track {i} vs Track {j} cross-corr={cc:.3f} (< 0.78)", flush=True)

    print("[ASSERT PASS] 3 strictly distinct Ep.1 master MP3s verified by MD5 & waveform:", flush=True)
    for slot, info in verified.items():
        print(f"  - Slot {slot} 〈{info['title']}〉: {info['mp3_filename']} | MD5={info['md5']} | {info['duration_sec']}s", flush=True)
    return verified


def load_glossary_normalizer() -> List[Tuple[str, str]]:
    pairs: List[Tuple[str, str]] = [
        ("님님", "님"),
        ("배군노", "백운호"),
        ("배군호", "백운호"),
        ("배군의", "백운호의"),
        ("박공기", "약봉지"),
        ("왕공", "완곡"),
    ]
    if GLOSSARY_PATH.exists():
        g = json.loads(GLOSSARY_PATH.read_text(encoding="utf-8"))
        for cat in (g.get("categories") or {}).values():
            if not isinstance(cat, list):
                continue
            for item in cat:
                canon = str(item.get("canonical") or "").strip()
                if canon in ("백운호", "김쌤의영웅라디오", "paradise-hero"):
                    for al in item.get("aliases") or []:
                        a = str(al).strip()
                        if a and a != canon and a not in ("4사업부", "paradise-hero.com", "김쌤의 영웅 라디오", "김쌤의 영웅라디오", "영웅라디오", "영웅 라디오"):
                            pairs.append((a, canon))
    return pairs


def sanitize_text(text: str, norm_pairs: List[Tuple[str, str]]) -> str:
    out = text
    for bad, good in norm_pairs:
        out = out.replace(bad, good)
    out = re.sub(r"님+", "님", out)
    low = out.lower()
    for fterm in FORBIDDEN_TERMS:
        assert fterm.lower() not in low, f"FATAL: Forbidden term '{fterm}' detected in Ep.1 script/SRT: {out}"
    return out


def wrap_two_lines(text: str, max_chars: int = 21) -> Tuple[str, str]:
    words = text.strip().split()
    lines: List[str] = []
    cur = ""
    for w in words:
        cand = f"{cur} {w}".strip() if cur else w
        if len(cand) <= max_chars:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) <= 1:
        return (lines[0] if lines else text[:max_chars], "")
    if len(lines) == 2:
        return (lines[0], lines[1])
    # Re-balance cleanly into 2 lines
    mid = len(text) // 2
    sp = text.rfind(" ", 0, mid + 4)
    if sp > 4:
        return (text[:sp].strip(), text[sp:].strip())
    return (lines[0], " ".join(lines[1:]))


def split_speech_into_subtitle_chunks(text: str, max_chars: int = 40) -> List[str]:
    sents = [s.strip() for s in re.split(r"(?<=[.?!])\s+", text.strip()) if s.strip()]
    chunks: List[str] = []
    for s in sents:
        if len(s) <= max_chars:
            chunks.append(s)
        else:
            # Split at natural comma if possible
            parts = [p.strip() for p in re.split(r"(?<=,)\s+", s) if p.strip()]
            buf = ""
            for p in parts:
                cand = f"{buf} {p}".strip() if buf else p
                if len(cand) <= max_chars:
                    buf = cand
                else:
                    if buf:
                        chunks.append(buf)
                    buf = p
            if buf:
                chunks.append(buf)
    return chunks or [text]


# Complete curated Radio Ep.1 spoken chapters (Story 1 + Story 2 + Health Break + Ep.2 Cliffhanger Closing)
SPOKEN_BLOCKS: Dict[str, Dict[str, Any]] = {
    "ch1_opening": {
        "chapter_label": "1부 오프닝 · 따뜻한 저녁 라디오 인사",
        "chapter_badge": "ON AIR · 김쌤의 영웅라디오 | 1부 · 따뜻한 저녁 오프닝",
        "bg_image": "ep1_ch1_radio_booth_watercolor.png",
        "segments": [
            ("dj", "DJ 김쌤", "안녕하세요, 든든한 우리 영웅 가족 여러분. 저녁 진지는 따뜻하게 챙겨 드셨는지요."),
            ("dj", "DJ 김쌤", "하루 동안 바쁘게 움직이던 발걸음을 멈추고 숨을 고르는 시간, 김쌤의 영웅라디오 정규 1화 본방송 문을 활짝 엽니다."),
            ("dj", "DJ 김쌤", "오늘도 저희 스튜디오 나무 책상 위에는 대구와 충남 공주, 전국 어머님 아버님들께서 보내주신 사연 편지들이 쌓여 있습니다."),
            ("dj", "DJ 김쌤", "오늘 1화 특집에서는 가슴 뭉클한 인생 사연 두 편과, 사랑방 전속 가상 트로트 가수 백운호의 대표곡 세 곡 완곡을 끊김 없이 준비했습니다."),
            ("dj", "DJ 김쌤", "거실 조명을 은은하게 맞추시고 따뜻한 보리차나 대추차 한 잔 곁에 두신 채 편안히 귀 기울여 주세요."),
        ],
    },
    "ch2_story1": {
        "chapter_label": "2부 [사연 1편] 텅 빈 새벽 부엌, 어머니의 봄날 (연속극장 1부)",
        "chapter_badge": "ON AIR · 김쌤의 영웅라디오 | 2부 · [사연 1편] 대구 이순자 어머님",
        "bg_image": "ep1_ch2_mother_dawn_kitchen_watercolor.png",
        "bg_image_second_half": "ep1_ch2_mother_apron_spring_blossoms_watercolor.png",
        "segments": [
            ("dj", "DJ 김쌤", "첫 번째 사연은 대구 달서구에 사시는 칠십이 세 이순자 어머님께서 보내주신 봄날의 편지입니다."),
            ("dj", "DJ 김쌤", "늦둥이 막내딸까지 시집을 보내고 난 뒤, 유독 텅 빈 새벽 부엌이 낯설고 시리셨다고 적어 주셨습니다."),
            ("letter", "사연 1편 · 대구 이순자 어머님(72세)", "김쌤 안녕하세요. 삼 남매 도시락 싸느라 젊은 시절부터 새벽 다섯 시면 불을 켜던 부엌에 오늘 아침에도 습관처럼 서 있었습니다."),
            ("letter", "사연 1편 · 대구 이순자 어머님(72세)", "이제는 마실 사람도 저 혼자뿐인데 무심코 예전 큰 주전자에 물을 가득 채워 보리차를 끓이고 있더군요."),
            ("letter", "사연 1편 · 대구 이순자 어머님(72세)", "보리차가 끓어오르는 소리를 듣는데 찬장 속 밥공기 다섯 개가 눈에 들어와 한참을 서 있었습니다."),
            ("letter", "사연 1편 · 대구 이순자 어머님(72세)", "식탁에 앉아 물기 묻은 꽃무늬 앞치마를 천천히 개는데, 오십 년 세월 누구의 아내와 엄마로만 살다 잊어버린 내 이름 석 자가 떠올랐습니다."),
            ("letter", "사연 1편 · 대구 이순자 어머님(72세)", "창밖 봄꽃을 바라보며 순자야, 칠십 평생 자식들 키워내느라 참 애썼다 하고 혼자 중얼거리니 마음속 응어리가 따뜻하게 녹아내렸습니다."),
            ("letter", "사연 1편 · 대구 이순자 어머님(72세)", "그날 부엌 서랍에 조용히 접어둔 편지를 보며 이제는 이순자라는 내 이름으로 밝게 살아보렵니다. 전국 어머님들께 따뜻한 노래 한 곡 부탁드립니다."),
            ("dj", "DJ 김쌤", "이순자 어머님, 편지 마지막 줄을 읽는데 제 마음도 참 먹먹해집니다. 오늘 저녁 전국 가족 모두가 어머님의 고운 이름 이순자 세 글자를 존경 담아 불러드립니다."),
            ("dj", "DJ 김쌤", "앞치마에 남몰래 눈물을 닦으시던 이 땅의 모든 어머님께 바칩니다. 백운호의 첫 번째 대표곡, 어머니의 봄날 완곡을 큰글씨 가사와 함께 청해 듣겠습니다."),
        ],
    },
    "ch4_story2": {
        "chapter_label": "4부 [사연 2편] 아버님이 남긴 약봉지와 황혼 편지",
        "chapter_badge": "ON AIR · 김쌤의 영웅라디오 | 4부 · [사연 2편] 공주 박순덕 어머님",
        "bg_image": "ep1_ch4_father_medicine_letter_watercolor.png",
        "bg_image_second_half": "ep1_ch4_twilight_couple_gingko_walk_watercolor.png",
        "segments": [
            ("dj", "DJ 김쌤", "백운호의 깊은 중저음으로 들으신 어머니의 봄날, 가사 한 소절마다 우리 어머님들의 세월이 고스란히 스며 있습니다."),
            ("dj", "DJ 김쌤", "이어서 두 번째 사연은 충남 공주에서 일흔 살 박순덕 어머님께서 칠십사 세 남편 김태호 아버님 이야기를 보내주신 황혼의 편지입니다."),
            ("letter", "사연 2편 · 충남 공주 박순덕 어머님(70세)", "김쌤, 제 남편은 사십오 년을 함께 살면서 사랑한다 고맙다 살가운 말 한마디 할 줄 모르는 무뚝뚝한 충청도 남자입니다."),
            ("letter", "사연 2편 · 충남 공주 박순덕 어머님(70세)", "지난주 오른쪽 무릎이 시큰거려 병원에서 약을 지어 왔더니, 남편은 아직도 걸레질을 하느냐며 퉁명스럽게 말하고 안방으로 들어가 버리더군요."),
            ("letter", "사연 2편 · 충남 공주 박순덕 어머님(70세)", "서운한 마음에 새벽 세 시 물을 마시러 나왔는데 부엌 식탁에 작은 불이 켜져 있었습니다."),
            ("letter", "사연 2편 · 충남 공주 박순덕 어머님(70세)", "남편이 낡은 돋보기안경을 걸친 채 제 약봉지 서른 개에 검은 매직으로 아침 식후, 저녁 식후를 큼직하게 적고 있었습니다."),
            ("letter", "사연 2편 · 충남 공주 박순덕 어머님(70세)", "다음 날 아침 보온병 밑 메모지엔 순덕아, 그동안 무거운 장바구니 혼자 들게 해서 미안하다, 이제 천천히 같이 걷자 적혀 있었습니다."),
            ("letter", "사연 2편 · 충남 공주 박순덕 어머님(70세)", "사십오 년 묵은 서운함이 눈 녹듯 사라졌습니다. 어제저녁엔 남편이 제 속도에 맞춰 은행나무 길을 함께 걸어주었답니다. 백운호 연가를 신청합니다."),
            ("dj", "DJ 김쌤", "새벽 세 시 돋보기 너머로 약봉지에 글씨를 적어 내려간 아버님의 투박한 손길이야말로 세상에서 가장 깊은 사랑 고백입니다."),
            ("dj", "DJ 김쌤", "서로의 지팡이가 되어 살아가시는 전국 모든 부부께 바칩니다. 백운호의 두 번째 대표곡, 백운호 연가 완곡을 함께 듣겠습니다."),
        ],
    },
    "ch6_health": {
        "chapter_label": "6부 김쌤의 시니어 관절·보온 건강 쉼표",
        "chapter_badge": "ON AIR · 김쌤의 영웅라디오 | 6부 · 김쌤의 건강·안부 쉼표",
        "bg_image": "health_posture_neck_shoulder_stretch.png",
        "segment_bgs": [
            "health_posture_neck_shoulder_stretch.png",
            "health_posture_seated_knee_extension.png",
            "health_posture_ankle_pumps.png",
            "health_posture_chair_heel_raises.png",
            "ep1_ch6_winter_camellia_bloom_watercolor.png",
        ],
        "segments": [
            ("dj", "DJ 김쌤 · 건강 쉼표", "백운호 연가의 잔잔한 호숫가 선율까지 편안히 들으셨습니다. 마지막 세 번째 곡 전에 일 분 건강 쉼표를 가져보겠습니다. 얇은 스카프로 목 체온을 지키시고 고개를 좌우로 천천히 늘려 보세요."),
            ("dj", "DJ 김쌤 · 건강 쉼표", "두 번째로 의자에 허리를 펴고 앉아 다리를 수평으로 들어 무릎을 다섯 초간 폈다 내려보세요. 양쪽 열 번씩만 해주셔도 무릎 주변 근육이 탄탄해집니다."),
            ("dj", "DJ 김쌤 · 건강 쉼표", "세 번째로 발끝을 몸 쪽으로 당겼다 펴는 발목 펌프 동작을 열 번씩 해보세요. 저녁 라디오 들으시며 발목만 풀어주셔도 밤에 다리 쥐 나는 것을 막아줍니다."),
            ("dj", "DJ 김쌤 · 건강 쉼표", "아침 식사 후엔 식탁 의자 등받이를 잡고 발뒤꿈치를 스무 번 천천히 들어 올려 보세요. 십 년 뒤에도 두 발로 전국 꽃길 어디든 당당히 걸으실 수 있습니다."),
            ("dj", "DJ 김쌤", "자, 겨울 눈보라를 이겨내고 가장 붉게 피어나는 여러분의 인생 이 막을 응원합니다. 백운호의 세 번째 대표곡, 다시 피는 동백꽃 완곡을 힘차게 띄워드립니다."),
        ],
    },
    "ch8_closing": {
        "chapter_label": "8부 다음 화 2부 연속 사연 예고 & 따뜻한 저녁 클로징",
        "chapter_badge": "ON AIR · 김쌤의 영웅라디오 | 8부 · 다음 화 예고 & 저녁 클로징",
        "bg_image": "ep1_ch1_radio_booth_watercolor.png",
        "bg_image_second_half": "ep1_ch4_twilight_couple_gingko_walk_watercolor.png",
        "segments": [
            ("dj", "DJ 김쌤 · 클로징", "어머니의 봄날부터 백운호 연가, 그리고 가슴 벅찬 다시 피는 동백꽃까지 백운호의 대표곡 세 곡 완곡을 모두 함께하셨습니다."),
            ("dj", "DJ 김쌤 · 다음 화 예고", "다음 화 이부 연속 사연에서는 오늘 일부에서 부엌 서랍에 접어둔 어머니의 편지를 십 년 만에 열어본 큰아들의 눈물겨운 답장과 백운호 신곡 무대가 이어집니다."),
            ("dj", "DJ 김쌤 · 사랑방 안내", "백운호 여섯 곡 무료 연속듣기와 카톡 아침 안부카드, 나들이 안심 준비물관은 영상 아래 설명란과 고정댓글 첫 번째 파란 링크에서 비밀번호 없이 바로 만나실 수 있습니다."),
            ("dj", "DJ 김쌤 · 클로징", "주무시기 전 미지근한 물 한 모금으로 목을 적시는 것 잊지 마세요. 가족을 위해 평생을 바치신 어머님 아버님, 당신이 우리 인생의 진짜 영웅입니다. 지금까지 김쌤이었습니다. 편안한 밤 되세요."),
        ],
    },
}


def load_cover_bg(img_name: str, cache: Dict[str, Image.Image]) -> Image.Image:
    if img_name in cache:
        return cache[img_name]
    p = WATERCOLOR_DIR / img_name
    assert p.exists(), f"Missing watercolor asset: {p}"
    im = Image.open(p).convert("RGB")
    iw, ih = im.size
    if ih > iw:
        # Vertical posture illustration -> warm blurred full-bleed backdrop + centered crisp gold-framed card
        bg = im.resize((VIDEO_W, VIDEO_H), Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(radius=28))
        dark = Image.new("RGBA", (VIDEO_W, VIDEO_H), (12, 10, 8, 120))
        comp = Image.alpha_composite(bg.convert("RGBA"), dark)
        target_h = 840
        target_w = int(iw * (target_h / float(ih)))
        fg = im.resize((target_w, target_h), Image.Resampling.LANCZOS).convert("RGBA")
        x0 = (VIDEO_W - target_w) // 2
        y0 = 40
        comp.paste(fg, (x0, y0))
        d = ImageDraw.Draw(comp)
        d.rounded_rectangle([x0 - 4, y0 - 4, x0 + target_w + 4, y0 + target_h + 4], radius=18, outline=(235, 200, 100, 235), width=4)
        out = comp.convert("RGB")
    else:
        # 16:9 cover crop/scale
        scale = max(VIDEO_W / iw, VIDEO_H / ih)
        nw, nh = int(round(iw * scale)), int(round(ih * scale))
        resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
        left = (nw - VIDEO_W) // 2
        top = (nh - VIDEO_H) // 2
        out = resized.crop((left, top, left + VIDEO_W, top + VIDEO_H))
    cache[img_name] = out
    return out


def render_cue_png(
    bg_img: Image.Image,
    chapter_badge: str,
    speaker_pill: str,
    line1: str,
    line2: str,
    out_png: Path,
    is_song: bool = False,
) -> None:
    canvas = bg_img.convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    f_badge = load_font(30)
    f_pill = load_font(30)
    f_sub = load_font(78 if is_song else 66)

    # Top-left ON AIR gold-bordered pill
    bx0, by0 = 48, 34
    bb = draw.textbbox((0, 0), chapter_badge, font=f_badge)
    bw = (bb[2] - bb[0]) + 56
    bh = (bb[3] - bb[1]) + 28
    draw.rounded_rectangle([bx0, by0, bx0 + bw, by0 + bh], radius=bh // 2, fill=(14, 24, 20, 212), outline=(235, 202, 102, 240), width=3)
    draw.text((bx0 + 28, by0 + 11), chapter_badge, font=f_badge, fill=(255, 246, 214, 255))

    # Bottom senior large subtitle card
    box_x0, box_x1 = 96, VIDEO_W - 96
    box_y0, box_y1 = 746, 986
    draw.rounded_rectangle([box_x0, box_y0, box_x1, box_y1], radius=26, fill=(10, 12, 16, 214), outline=(235, 202, 102, 235), width=3)

    # Centered speaker / song pill overlapping top border of subtitle card
    pb = draw.textbbox((0, 0), speaker_pill, font=f_pill)
    pw = (pb[2] - pb[0]) + 56
    ph = (pb[3] - pb[1]) + 22
    px0 = (VIDEO_W - pw) // 2
    py0 = box_y0 - ph // 2 - 4
    pill_fill = (20, 62, 42, 238) if is_song else (58, 34, 22, 238)
    draw.rounded_rectangle([px0, py0, px0 + pw, py0 + ph], radius=ph // 2, fill=pill_fill, outline=(242, 210, 114, 245), width=3)
    draw.text((px0 + 28, py0 + 8), speaker_pill, font=f_pill, fill=(255, 244, 205, 255))

    def draw_centered(txt: str, cy: int, fill_rgba: Tuple[int, int, int, int]) -> None:
        if not txt.strip():
            return
        tb = draw.textbbox((0, 0), txt, font=f_sub)
        tw = tb[2] - tb[0]
        th = tb[3] - tb[1]
        tx = (VIDEO_W - tw) // 2
        ty = cy - th // 2
        draw.text((tx, ty), txt, font=f_sub, fill=fill_rgba, stroke_width=6, stroke_fill=(6, 8, 12, 255))

    if line2.strip():
        draw_centered(line1, box_y0 + 86, (255, 255, 255, 255))
        draw_centered(line2, box_y0 + 174, (255, 234, 92, 255))
    else:
        draw_centered(line1, (box_y0 + box_y1) // 2 + 6, (255, 245, 168, 255))

    canvas.convert("RGB").save(out_png, format="PNG", optimize=True)


async def synth_tts_mp3(text: str, role: str, out_mp3: Path) -> None:
    if out_mp3.exists() and out_mp3.stat().st_size > 2000:
        return
    voice, rate, pitch = VOICE_DJ if role == "dj" else VOICE_LETTER
    for attempt in range(3):
        try:
            comm = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
            await comm.save(str(out_mp3))
            if out_mp3.exists() and out_mp3.stat().st_size > 1000:
                return
        except Exception as e:
            if attempt == 2:
                raise RuntimeError(f"Edge-TTS failed for {out_mp3.name}: {e}")
            await asyncio.sleep(1.5)


def mp3_to_48k_stereo_wav(src: Path, dst_wav: Path, target_lufs: Optional[float] = None) -> float:
    af = []
    if target_lufs is not None:
        af.append(f"loudnorm=I={target_lufs}:TP=-1.0:LRA=11")
    cmd = [FFMPEG_EXE, "-y", "-threads", "2", "-i", str(src)]
    if af:
        cmd += ["-af", ",".join(af)]
    cmd += ["-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(dst_wav)]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with wave.open(str(dst_wav), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate())


def mix_speech_over_mr_bed(voice_wav: Path, out_wav: Path, dur_sec: float) -> None:
    """Mixes voice over gently ducked real ACE-Step trot acoustic MR bed (-23dB, lowpass 3.5kHz). ZERO sine waves."""
    if not MR_BED_WAV.exists():
        # Clean voice-only fallback if MR missing
        subprocess.run(
            [FFMPEG_EXE, "-y", "-threads", "2", "-i", str(voice_wav), "-af", "loudnorm=I=-15:TP=-1.0:LRA=9", "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(out_wav)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return
    fade_out_st = max(0.5, dur_sec - 1.2)
    cmd = [
        FFMPEG_EXE, "-y", "-threads", "2",
        "-i", str(voice_wav),
        "-stream_loop", "-1", "-i", str(MR_BED_WAV),
        "-filter_complex",
        f"[1:a]atrim=0:{dur_sec:.3f},asetpts=PTS-STARTPTS,lowpass=f=3200,volume=-23dB,"
        f"afade=t=in:st=0:d=0.9,afade=t=out:st={fade_out_st:.3f}:d=1.1[bed];"
        f"[0:a]loudnorm=I=-15.5:TP=-1.5:LRA=9[vc];"
        f"[vc][bed]amix=inputs=2:duration=first:dropout_transition=2,alimiter=limit=0.95[outa]",
        "-map", "[outa]", "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(out_wav),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def make_silence_wav(dur_sec: float, dst_wav: Path) -> None:
    n_frames = int(round(dur_sec * SR))
    with wave.open(str(dst_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(b"\x00" * (n_frames * 4))


def fmt_srt_ts(sec: float) -> str:
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int(round((sec - int(sec)) * 1000))
    if ms >= 1000:
        s += 1
        ms -= 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def fmt_mmss(sec: float) -> str:
    m = int(sec // 60)
    s = int(round(sec % 60))
    if s >= 60:
        m += 1
        s -= 60
    return f"{m:02d}:{s:02d}"


def post_render_verify_mp4_songs(mp4_path: Path, song_spans: List[Dict[str, Any]], tracks: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
    """POST-RENDER HARD ASSERT: Decode finished MP4 at each song span and prove 1:1 match with its own MP3."""
    print("\n[POST-RENDER AUDIO AUDIT] Decoding final MP4 to verify 3 distinct tracks...", flush=True)
    full_sig = decode_mono_8k(mp4_path)
    needles = {
        slot: decode_mono_8k(tracks[slot]["path"], ss=42.0, dur=20.0)
        for slot in (1, 2, 3)
    }
    matrix: Dict[str, Dict[str, float]] = {}
    for sp in song_spans:
        slot = sp["slot"]
        t0 = max(0.0, sp["start_sec"] + 35.0)
        t1 = min(len(full_sig) / 8000.0, sp["start_sec"] + 75.0)
        seg = full_sig[int(t0 * 8000) : int(t1 * 8000)]
        scores = {}
        for cand_slot in (1, 2, 3):
            scores[f"track_{cand_slot}"] = round(best_shift_envelope_corr(seg, needles[cand_slot]), 4)
        matrix[f"span_slot_{slot}_{sp['title']}"] = scores
        own_score = scores[f"track_{slot}"]
        other_max = max(v for k, v in scores.items() if k != f"track_{slot}")
        print(f"  Slot {slot} 〈{sp['title']}〉 @{fmt_mmss(sp['start_sec'])} -> {scores}", flush=True)
        assert own_score >= 0.80, f"FATAL: Rendered MP4 Slot {slot} failed self-correlation ({own_score} < 0.80)!"
        assert own_score > other_max + 0.25, f"FATAL: Rendered MP4 Slot {slot} confused with another song ({own_score} vs {other_max})!"
    print("[POST-RENDER AUDIO AUDIT ALL PASS] All 3 songs inside final MP4 are 100% distinct and accurately placed!", flush=True)
    return matrix


async def build_ep1_master() -> Dict[str, Any]:
    t_start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    cues_dir = WORK_DIR / "cue_pngs"
    tts_dir = WORK_DIR / "tts"
    audio_parts_dir = WORK_DIR / "audio_parts"
    for d in (cues_dir, tts_dir, audio_parts_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 1. Hard Pre-Render Assert on 3 distinct MP3s
    tracks = assert_three_distinct_song_mp3s()
    mv_cat = json.loads(MV_CATALOG_PATH.read_text(encoding="utf-8"))
    mv_by_id = {s["song_id"]: s for s in mv_cat["songs"]}
    norm_pairs = load_glossary_normalizer()

    # 2. Synthesize all spoken TTS segments sequentially/gently
    print("\n[STEP 2] Synthesizing DJ 김쌤 & 사연자 Edge-TTS narration...", flush=True)
    spoken_wavs: Dict[str, List[Tuple[str, str, str, Path, float]]] = {}
    for blk_key, blk in SPOKEN_BLOCKS.items():
        items = []
        for idx, (role, speaker_pill, raw_text) in enumerate(blk["segments"], start=1):
            clean_txt = sanitize_text(raw_text, norm_pairs)
            seg_mp3 = tts_dir / f"{blk_key}_{idx:02d}_{role}.mp3"
            seg_wav = tts_dir / f"{blk_key}_{idx:02d}_{role}.wav"
            await synth_tts_mp3(clean_txt, role, seg_mp3)
            dur = mp3_to_48k_stereo_wav(seg_mp3, seg_wav)
            items.append((role, speaker_pill, clean_txt, seg_wav, dur))
        spoken_wavs[blk_key] = items
        print(f"  [TTS OK] {blk_key}: {len(items)} segments ({sum(x[4] for x in items):.1f}s)", flush=True)

    # 3. Assemble timeline (audio parts + visual cues + SRT cues + exact chapter timestamps)
    print("\n[STEP 3] Building exact synced audio parts, 1080p cue cards & SRT...", flush=True)
    bg_cache: Dict[str, Image.Image] = {}
    audio_concat_wavs: List[Path] = []
    video_cues: List[Tuple[Path, float]] = []
    srt_entries: List[Tuple[float, float, str]] = []
    chapter_timestamps: List[Dict[str, Any]] = []
    song_spans: List[Dict[str, Any]] = []

    cursor_sec = 0.0
    cue_seq = 0

    def add_spoken_block(blk_key: str) -> None:
        nonlocal cursor_sec, cue_seq
        blk = SPOKEN_BLOCKS[blk_key]
        chapter_timestamps.append({
            "sec": round(cursor_sec, 2),
            "mmss": fmt_mmss(cursor_sec),
            "label": blk["chapter_label"],
        })
        items = spoken_wavs[blk_key]
        seg_concat_lines: List[str] = []
        pause_045 = audio_parts_dir / "pause_045s.wav"
        if not pause_045.exists():
            make_silence_wav(0.45, pause_045)

        blk_start = cursor_sec
        blk_total_dur = 0.0
        half_idx = max(1, len(items) // 2)

        for idx, (role, speaker_pill, clean_txt, seg_wav, seg_dur) in enumerate(items):
            if "segment_bgs" in blk and idx < len(blk["segment_bgs"]):
                bg_name = blk["segment_bgs"][idx]
            elif "bg_image_second_half" in blk and idx >= half_idx:
                bg_name = blk["bg_image_second_half"]
            else:
                bg_name = blk["bg_image"]
            bg_img = load_cover_bg(bg_name, bg_cache)

            # Append voice wav + 0.45s breath pause
            seg_concat_lines.append(f"file '{seg_wav.as_posix()}'")
            seg_concat_lines.append(f"file '{pause_045.as_posix()}'")
            slot_dur = seg_dur + 0.45

            chunks = split_speech_into_subtitle_chunks(clean_txt, max_chars=38)
            total_chars = max(1, sum(len(c) for c in chunks))
            sub_t = cursor_sec
            for ci, ch_txt in enumerate(chunks):
                frac = len(ch_txt) / float(total_chars)
                cdur = slot_dur * frac if ci < len(chunks) - 1 else (cursor_sec + slot_dur - sub_t)
                cdur = max(0.35, cdur)
                l1, l2 = wrap_two_lines(ch_txt, max_chars=20)
                cue_seq += 1
                png_path = cues_dir / f"cue_{cue_seq:04d}.png"
                render_cue_png(bg_img, blk["chapter_badge"], speaker_pill, l1, l2, png_path, is_song=False)
                video_cues.append((png_path, cdur))
                srt_entries.append((sub_t + 0.05, sub_t + max(0.25, cdur - 0.08), ch_txt))
                sub_t += cdur

            cursor_sec += slot_dur
            blk_total_dur += slot_dur

        # Concatenate block voice wavs and gently mix over real trot MR bed
        blk_list = audio_parts_dir / f"{blk_key}_list.txt"
        blk_list.write_text("\n".join(seg_concat_lines) + "\n", encoding="utf-8")
        blk_voice_wav = audio_parts_dir / f"{blk_key}_voice.wav"
        subprocess.run(
            [FFMPEG_EXE, "-y", "-threads", "2", "-f", "concat", "-safe", "0", "-i", str(blk_list), "-c", "copy", str(blk_voice_wav)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        blk_mixed_wav = audio_parts_dir / f"{blk_key}_mixed.wav"
        mix_speech_over_mr_bed(blk_voice_wav, blk_mixed_wav, blk_total_dur)
        audio_concat_wavs.append(blk_mixed_wav)
        print(f"  [BLOCK OK] {blk_key} @{fmt_mmss(blk_start)} ({blk_total_dur:.2f}s)", flush=True)

    def add_song_block(slot: int) -> None:
        nonlocal cursor_sec, cue_seq
        info = tracks[slot]
        mv_song = mv_by_id[info["song_id"]]
        song_wav = audio_parts_dir / f"song_{slot:02d}_{info['song_id']}.wav"
        actual_dur = mp3_to_48k_stereo_wav(info["path"], song_wav, target_lufs=-14.0)

        # Add clean 1.0s post-song silence breathing room
        pad_wav = audio_parts_dir / "pause_100s.wav"
        if not pad_wav.exists():
            make_silence_wav(1.0, pad_wav)

        start_s = cursor_sec
        chapter_timestamps.append({
            "sec": round(start_s, 2),
            "mmss": fmt_mmss(start_s),
            "label": f"{'3부' if slot==1 else ('5부' if slot==2 else '7부')} [대표곡 {slot}곡] 백운호 〈{info['title']}〉 완곡",
        })
        song_spans.append({
            "slot": slot,
            "song_id": info["song_id"],
            "title": info["title"],
            "mp3_filename": info["mp3_filename"],
            "md5": info["md5"],
            "start_sec": round(start_s, 2),
            "end_sec": round(start_s + actual_dur, 2),
            "duration_sec": round(actual_dur, 2),
        })

        bg_img = load_cover_bg(info["bg_image"], bg_cache)
        cues = mv_song["full_cues"]
        t_local = 0.0
        for ci, (c0, c1, l1_raw, l2_raw) in enumerate(cues):
            l1 = sanitize_text(str(l1_raw), norm_pairs)
            l2 = sanitize_text(str(l2_raw), norm_pairs)
            # Ensure exact seamless coverage from 0.0 to actual_dur + 1.0s pad
            if ci == len(cues) - 1:
                cue_end = actual_dur + 1.0
            else:
                next_start = float(cues[ci + 1][0])
                cue_end = min(actual_dur, max(float(c1), next_start))
            cdur = max(0.5, cue_end - t_local)
            cue_seq += 1
            png_path = cues_dir / f"cue_{cue_seq:04d}.png"
            render_cue_png(bg_img, info["chapter_badge"], info["pill_label"], l1, l2, png_path, is_song=True)
            video_cues.append((png_path, cdur))
            srt_text = f"♪ {l1}\n{l2}".strip() if not l1.startswith("♪") else f"{l1}\n{l2}".strip()
            srt_entries.append((start_s + t_local + 0.05, start_s + t_local + cdur - 0.08, srt_text))
            t_local += cdur

        audio_concat_wavs.append(song_wav)
        audio_concat_wavs.append(pad_wav)
        cursor_sec += actual_dur + 1.0
        print(f"  [SONG {slot} OK] 〈{info['title']}〉 @{fmt_mmss(start_s)} ({actual_dur:.2f}s | MD5={info['md5']})", flush=True)

    # Exact Broadcast Sequence: Opening -> Story1 -> Song1 -> Story2 -> Song2 -> Health -> Song3 -> Closing
    add_spoken_block("ch1_opening")
    add_spoken_block("ch2_story1")
    add_song_block(1)
    add_spoken_block("ch4_story2")
    add_song_block(2)
    add_spoken_block("ch6_health")
    add_song_block(3)
    add_spoken_block("ch8_closing")

    # 4. Concatenate Master WAV
    master_audio_list = WORK_DIR / "master_audio_concat.txt"
    master_audio_list.write_text("\n".join(f"file '{p.as_posix()}'" for p in audio_concat_wavs) + "\n", encoding="utf-8")
    master_wav = WORK_DIR / "ep1_master_48k.wav"
    subprocess.run(
        [FFMPEG_EXE, "-y", "-threads", "2", "-f", "concat", "-safe", "0", "-i", str(master_audio_list), "-c", "copy", str(master_wav)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    with wave.open(str(master_wav), "rb") as wf:
        master_audio_dur = wf.getnframes() / float(wf.getframerate())

    # 5. Write FFmpeg video concat file matching exact cue durations
    vid_concat_lines: List[str] = []
    for p, d in video_cues:
        vid_concat_lines.append(f"file '{p.as_posix()}'")
        vid_concat_lines.append(f"duration {d:.4f}")
    if video_cues:
        vid_concat_lines.append(f"file '{video_cues[-1][0].as_posix()}'")
    vid_list_path = WORK_DIR / "master_video_concat.txt"
    vid_list_path.write_text("\n".join(vid_concat_lines) + "\n", encoding="utf-8")

    # 6. Encode 1920x1080 MP4 in single low-CPU pass (-threads 2, BelowNormal)
    out_mp4 = OUT_DIR / "hero_ep1_3songs_verified_master.mp4"
    print(f"\n[STEP 4] Encoding final 1080p MP4 ({master_audio_dur:.1f}s = {fmt_mmss(master_audio_dur)}, {len(video_cues)} synced cues)...", flush=True)
    cmd_enc = [
        FFMPEG_EXE, "-y", "-threads", "2",
        "-f", "concat", "-safe", "0", "-i", str(vid_list_path),
        "-i", str(master_wav),
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-crf", "22",
        "-r", "24", "-g", "48", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", str(SR),
        "-movflags", "+faststart", "-shortest",
        str(out_mp4),
    ]
    rv = subprocess.run(cmd_enc, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    if rv.returncode != 0 or not out_mp4.exists():
        raise RuntimeError(f"FFmpeg encode failed: {rv.stderr[-500:]}")

    # 7. Write sanitized official .srt
    out_srt = OUT_DIR / "hero_ep1_3songs_verified_master.srt"
    srt_blocks = []
    for idx, (t0, t1, txt) in enumerate(srt_entries, start=1):
        clean_srt = sanitize_text(txt, norm_pairs)
        srt_blocks.append(f"{idx}\n{fmt_srt_ts(t0)} --> {fmt_srt_ts(t1)}\n{clean_srt}\n")
    out_srt.write_text("\n".join(srt_blocks), encoding="utf-8")

    # 8. Post-Render Acoustic Proof Assert directly on final MP4
    audit_matrix = post_render_verify_mp4_songs(out_mp4, song_spans, tracks)

    # 9. Extract 4 visual verification frames (Story 1, Song 1, Song 2, Song 3)
    kf_dir = OUT_DIR / "keyframes_verify_v2"
    kf_dir.mkdir(parents=True, exist_ok=True)
    kf_paths = []
    kf_targets = [
        ("kf1_story1.jpg", chapter_timestamps[1]["sec"] + 20.0),
        ("kf2_song1_mothers_spring.jpg", song_spans[0]["start_sec"] + 45.0),
        ("kf3_song2_yeonga.jpg", song_spans[1]["start_sec"] + 45.0),
        ("kf4_song3_camellia.jpg", song_spans[2]["start_sec"] + 45.0),
    ]
    for kname, ksec in kf_targets:
        kp = kf_dir / kname
        subprocess.run(
            [FFMPEG_EXE, "-y", "-threads", "2", "-ss", f"{ksec:.1f}", "-i", str(out_mp4), "-frames:v", "1", "-q:v", "3", str(kp)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        kf_paths.append(str(kp))

    # 10. Build clean YouTube metadata JSON with exact chapter timestamps & /go/yt links
    mmss_total = fmt_mmss(master_audio_dur)
    chap_lines = "\n".join(f"{c['mmss']} {c['label']}" for c in chapter_timestamps)
    yt_title = "[1화·연속극장 1부] 어머님 감동 사연 2편 & 백운호 대표곡 3곡 완곡 연속 듣기 | 어머니의 봄날 · 백운호 연가 · 다시 피는 동백꽃"[:99]
    yt_desc = (
        f"{yt_title} ({mmss_total} 완곡)\n\n"
        f"어머님, 아버님 반갑습니다 💚\n"
        f"마음을 노래하는 AI 가상 트로트 가수 『백운호 (白雲湖)』의 중저음 명곡 3곡 완곡(〈어머니의 봄날〉 · 〈백운호 연가〉 · 〈다시 피는 동백꽃〉)과 어머님들의 가슴 뭉클한 사연 2편이 흐르는 [김쌤의 영웅라디오] 정규 1화 본방송입니다.\n\n"
        f"🔥 [다음 화 예고 · 2부 연속 사연] 오늘 1부에서 부엌에 접어둔 어머니의 편지, 그 편지를 10년 만에 열어본 큰아들의 답장과 백운호 신곡 무대가 화·금 저녁 6시 2부에서 이어집니다!\n\n"
        f"⏱️ [1화 방송 순서 · 터치하시면 바로 이동합니다]\n"
        f"{chap_lines}\n\n"
        f"🎵 백운호 6곡 완곡 무료 라디오 & 연속 사연 사랑방 (가입 없음): https://paradise-hero.com/go/yt\n"
        f"💐 매일 아침 카톡 무료 안부카드 만들기: https://paradise-hero.com/vip.html\n"
        f"📸 공식 인스타그램 (@paradise_hero1): https://www.instagram.com/paradise_hero1/\n"
        f"💚 어머님 상황별 안심 준비물관 (네이버페이 공식관): https://cshop.naver.com/paradiseshop\n"
        f"🚀 어머님 나들이·청취 준비물 쿠팡 공식관: https://influencers.coupang.com/s/paradisehero\n"
        f"💌 사연 제보 및 브랜드 협찬 문의: radio@paradise-hero.com\n\n"
        f"💬 오늘 들으신 〈어머니의 봄날〉, 〈백운호 연가〉, 〈다시 피는 동백꽃〉 세 곡 중 어머님 가슴에 가장 오래 남은 곡은 몇 번째 곡이셨나요? 댓글로 한 줄 남겨주세요.\n\n"
        f"※ 본 방송의 가수 『백운호』는 마음을 노래하는 AI 가상(버추얼) 트로트 가수입니다.\n"
        f"(네이버 쇼핑커넥트 및 쿠팡 파트너스 활동의 일환으로 이에 따른 일정액의 수수료를 제공받습니다.)\n"
        f"#백운호 #어머니의봄날 #백운호연가 #다시피는동백꽃 #김쌤의영웅라디오"
    )
    pinned_comment = (
        f"💚 든든한 우리 영웅 가족 여러분! 오늘 [1화] 사연 2편과 백운호 대표곡 3곡 완곡(어머니의 봄날 · 백운호 연가 · 다시 피는 동백꽃) 중 가장 가슴에 와닿았던 곡을 댓글 사랑방에 남겨주세요!\n"
        f"🎵 백운호 6곡 무료 연속듣기 & 큰글씨 사랑방 (가입 없음) 👉 https://paradise-hero.com/go/yt\n"
        f"💐 매일 아침 카톡 무료 안부카드 만들기 👉 https://paradise-hero.com/vip.html\n"
        f"💚 김쌤의 나들이·응원 안심 준비물관 👉 https://cshop.naver.com/paradiseshop"
    )

    meta_out = {
        "episode_number": 1,
        "version": "v2_3songs_md5_verified_20261126",
        "title": yt_title,
        "description": yt_desc,
        "pinned_comment": pinned_comment,
        "tags": ["백운호", "어머니의봄날", "백운호연가", "다시피는동백꽃", "김쌤의영웅라디오", "시니어트로트"],
        "categoryId": "24",
        "defaultLanguage": "ko",
        "defaultAudioLanguage": "ko",
        "mp4_path": str(out_mp4),
        "srt_path": str(out_srt),
        "thumbnail_path": str(OUT_DIR / "hero_ep1_flagship_thumb_1280x720.png"),
        "duration_sec": round(master_audio_dur, 2),
        "duration_mmss": mmss_total,
        "mp4_size_mb": round(out_mp4.stat().st_size / (1024 * 1024), 2),
        "srt_cue_count": len(srt_entries),
        "chapter_timestamps": chapter_timestamps,
        "song_spans": song_spans,
        "post_render_audio_audit": audit_matrix,
        "keyframes": kf_paths,
        "elapsed_sec": round(time.time() - t_start, 1),
    }
    (OUT_DIR / "youtube_metadata_v2_verified.json").write_text(
        json.dumps(meta_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"\n🎉 [EP1 3-SONG VERIFIED MASTER COMPLETE] {out_mp4.name} "
        f"({meta_out['mp4_size_mb']} MB, {mmss_total}, {len(srt_entries)} SRT cues, elapsed={meta_out['elapsed_sec']}s)",
        flush=True,
    )
    return meta_out


if __name__ == "__main__":
    asyncio.run(build_ep1_master())
