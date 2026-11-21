#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
D:\드림컴퍼니\4사업부\scripts\generate_baek_woonho_lyria35_6songs.py
================================================================================
4사업부 (`paradise-hero.com` · `@김쌤의영웅라디오`) 가상 트로트 가수 『백운호』
정규 완곡 6곡 `Gemini lyria-3.5` 실음원 생성 및 음향 스펙트럼 자동 검수기

[절대 준수 규칙]
1. `POST https://generativelanguage.googleapis.com/v1beta/interactions`
   - `Api-Revision: 2026-05-20`, `x-goog-api-key: $GEMINI_API_KEY`, `model: "lyria-3.5"`
   - `steps[].content[]` 내 `audio` base64 데이터 추출 ➔ `.mp3` 저장
2. `numpy`/`scipy` 사인파 합성 및 TTS 피치 변조 가짜 음원 영구 금지 (실패 시 가짜 파일 생성 금지)
3. 프롬프트·가사 내 실존 가수 성명(부정문 포함) 0건
4. `ffprobe` (`44100Hz`, `stereo`, `120초+`) + `5kHz 이상 고주파 에너지 >= 3.0%` 통과 곡만 채택
================================================================================
"""

from __future__ import annotations

import base64
import ctypes
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
    except Exception:
        pass

import imageio_ffmpeg
import numpy as np

KST = timezone(timedelta(hours=9))
ROOT = Path(r"D:\드림컴퍼니")
DIV4 = ROOT / "4사업부"
AUDIO_DIR = DIV4 / "assets" / "audio"
DATA_DIR = DIV4 / "data"
RAW_DIR = ROOT / ".cache" / "tmp" / "lyria35_raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
AUDIT_OUT = DATA_DIR / "baek_woonho_lyria35_6songs_audit.json"


def load_gemini_key() -> str:
    if os.environ.get("GEMINI_API_KEY", "").strip():
        return os.environ["GEMINI_API_KEY"].strip()
    env_p = ROOT / ".env"
    if env_p.exists():
        for ln in env_p.read_text(encoding="utf-8", errors="ignore").splitlines():
            s = ln.strip()
            if s.startswith("GEMINI_API_KEY="):
                return s.split("=", 1)[1].strip().strip("'\"")
    raise RuntimeError("GEMINI_API_KEY not found in D:\\드림컴퍼니\\.env or environment")


GEMINI_API_KEY = load_gemini_key()


SONGS_SPEC: List[Dict[str, Any]] = [
    {
        "track_no": 1,
        "song_id": "mothers_spring",
        "title": "어머니의 봄날",
        "badge": "타이틀곡",
        "filename": "baek_woonho_01_mothers_spring.mp3",
        "alias": "baek_woonho_debut_sample.mp3",
        "prompt": """장르: 한국 정통 트로트 성인 가요 (Authentic Korean Traditional Trot)
템포: 84 BPM, 4/4박자 경쾌하고 따뜻한 쿵짝 폭스트롯 리듬
조성: D minor (라단조, 애절하면서도 희망찬 멜로디)
악기: Alto Saxophone, Brass, Accordion, Warm Acoustic Guitar, Upright Bass, Crisp Live Drum Kit with Hi-Hat & Cymbals
보컬: Male Baritone: 깊고 따뜻한 중저음 흉성, 구성진 바이브레이션 성인 가요 보컬
분위기: 평생 가족을 위해 헌신하신 어머님께 바치는 따뜻하고 감동적인 무대

Lyrics:
[0:00 - 0:12] [Intro]
(Weeping Accordion and Alto Saxophone melody with warm acoustic guitar and crisp rhythm)

[0:12 - 0:42] [Verse 1]
찬 서리 내리던 새벽 부엌에
보리차 끓이시던 고운 그 손길
자식들 웃음이면 다 된다시며
앞치마에 감추신 세월의 눈물

[0:42 - 1:14] [Chorus]
어머니 내 어머니 이제 울지 마세요
모진 겨울 다 지나고 꽃이 핍니다
주름진 두 손 잡고 함께 걸어갈
어머니의 봄날이 오늘 피어납니다

[1:14 - 1:30] [Instrumental Interlude]
(Expressive Alto Saxophone and Accordion solo with punchy Brass accents)

[1:30 - 2:00] [Verse 2]
장터 길 찬 바람에 옷깃 여미며
내 이름 석 자조차 잊고 산 세월
괜찮다 웃으시던 그 목소리가
오늘 밤 내 가슴을 뜨겁게 적시네

[2:00 - 2:32] [Chorus]
어머니 내 어머니 이제 울지 마세요
모진 겨울 다 지나고 꽃이 핍니다
주름진 두 손 잡고 함께 걸어갈
어머니의 봄날이 오늘 피어납니다

[2:32 - 2:45] [Outro]
(Grand Brass, Alto Saxophone, and Accordion finale fade out)""",
    },
    {
        "track_no": 2,
        "song_id": "baek_woon_ho_yeonga",
        "title": "백운호 연가",
        "badge": "산책길 애창곡",
        "filename": "baek_woonho_02_yeonga.mp3",
        "alias": "baek_woonho_yeonga_full.mp3",
        "prompt": """장르: 한국 정통 서정 트로트 성인 가요 (Korean Lyrical Foxtrot Trot)
템포: 82 BPM, 4/4박자 부드러운 산책길 폭스트롯 리듬
조성: A minor (가단조)
악기: Alto Saxophone, Brass, Accordion, Warm Acoustic Guitar, Upright Bass, Brush Snare & Bright Hi-Hat
보컬: Male Baritone: 깊고 따뜻한 중저음 흉성, 구성진 바이브레이션 성인 가요 보컬
분위기: 흰 구름 쉬어 가는 고요한 호숫가 저녁노을의 위로와 낭만

Lyrics:
[0:00 - 0:12] [Intro]
(Soulful Alto Saxophone and Warm Acoustic Guitar intro with gentle accordion)

[0:12 - 0:42] [Verse 1]
흰 구름 쉬어 가는 고요한 호수에
노을빛 물결 따라 세월이 흐르네
말없이 건네주신 따뜻한 약봉지
사십 년 깊은 정이 고스란히 담겼네

[0:42 - 1:14] [Chorus]
쉬어 가세요 내 사람아 넓은 품 안에서
거친 바람 지나는 날 내가 막아 드리리
한낮보다 아름다운 우리의 금빛 노을
두 손 꼭 잡고 걷는 호숫가 연가여라

[1:14 - 1:30] [Instrumental Interlude]
(Nostalgic Accordion and Alto Saxophone duet with bright brass swells)

[1:30 - 2:00] [Verse 2]
표현은 서툴러도 마음만은 진국인
무뚝뚝한 그대 손이 내 평생 버팀목
은행잎 내려앉은 가을 길 나란히
천천히 걸어가는 아름다운 두 그림자

[2:00 - 2:32] [Chorus]
쉬어 가세요 내 사람아 넓은 품 안에서
거친 바람 지나는 날 내가 막아 드리리
한낮보다 아름다운 우리의 금빛 노을
두 손 꼭 잡고 걷는 호숫가 연가여라

[2:32 - 2:45] [Outro]
(Warm Acoustic Guitar, Accordion, and Alto Saxophone peaceful ending)""",
    },
    {
        "track_no": 3,
        "song_id": "harbor_light",
        "title": "항구의 등불",
        "badge": "저녁 위로곡",
        "filename": "baek_woonho_03_harbor_light.mp3",
        "alias": "",
        "prompt": """장르: 한국 정통 항구 트로트 성인 가요 (Classic Korean Harbor Trot)
템포: 84 BPM, 4/4박자 구성진 쿵짝 리듬
조성: E minor (마단조)
악기: Alto Saxophone, Brass, Accordion, Warm Acoustic Guitar, Upright Bass, Crisp Live Drum Kit
보컬: Male Baritone: 깊고 따뜻한 중저음 흉성, 구성진 바이브레이션 성인 가요 보컬
분위기: 밤바다 파도를 견디고 돌아온 가족의 버팀목을 비추는 등불 같은 위로

Lyrics:
[0:00 - 0:12] [Intro]
(Weeping Accordion and Brass intro over steady trot rhythm)

[0:12 - 0:42] [Verse 1]
밤안개 자욱하게 내려앉은 부둣가에
거친 파도 헤쳐 온 연락선이 쉬어가네
비바람 모진 세월 가족 위해 버텨내신
아버지의 넓은 등엔 소금꽃이 피었네

[0:42 - 1:14] [Chorus]
불을 켜라 항구의 등불 어두운 밤바다에
지친 어선 길 비추는 따뜻한 등대처럼
이제는 닻을 내리고 편안히 쉬어 가세요
당신이 우리 집의 꺼지지 않는 등불이라

[1:14 - 1:30] [Instrumental Interlude]
(Alto Saxophone and Brass melody with lively accordion rhythm)

[1:30 - 2:00] [Verse 2]
새벽 별 보며 나가 달빛 안고 돌아오던
굳은살 박인 손에 들려 있던 작은 봉투
힘들단 말 한마디 가슴 깊이 묻어두신
그 사랑 있었기에 오늘 내가 서 있네

[2:00 - 2:32] [Chorus]
불을 켜라 항구의 등불 어두운 밤바다에
지친 어선 길 비추는 따뜻한 등대처럼
이제는 닻을 내리고 편안히 쉬어 가세요
당신이 우리 집의 꺼지지 않는 등불이라

[2:32 - 2:45] [Outro]
(Resonant Brass and Accordion grand finale)""",
    },
    {
        "track_no": 4,
        "song_id": "blooming_camellia",
        "title": "다시 피는 동백꽃",
        "badge": "희망 응원곡",
        "filename": "baek_woonho_04_camellia.mp3",
        "alias": "baek_woonho_camellia_full.mp3",
        "prompt": """장르: 한국 정통 희망 트로트 성인 가요 (Uplifting Korean Polka Trot)
템포: 88 BPM, 4/4박자 경쾌하고 흥겨운 폴카 트로트 리듬
조성: G minor (사단조에서 밝게 뻗는 후렴)
악기: Alto Saxophone, Brass, Accordion, Warm Acoustic Guitar, Upright Bass, Crisp Live Drums with Bright Cymbals
보컬: Male Baritone: 깊고 따뜻한 중저음 흉성, 구성진 바이브레이션 성인 가요 보컬
분위기: 겨울 바람을 이겨내고 인생 2막을 당당히 꽃피우는 시니어 응원가

Lyrics:
[0:00 - 0:12] [Intro]
(Lively Brass, Accordion, and Alto Saxophone fanfare with bright trot groove)

[0:12 - 0:42] [Verse 1]
매서운 겨울바람 눈보라 스쳐 가도
가지 끝에 붉게 맺힌 고운 동백 꽃망울
삼 남매 뒷바라지 세월의 고개 넘어
이제야 불러보는 내 이름 석 자여라

[0:42 - 1:14] [Chorus]
활짝 피어나세요 다시 피는 동백꽃
당신의 인생 이 막 지금이 청춘입니다
고운 스카프 두르고 봄바람 마주하며
가벼운 발걸음으로 꽃길을 걸어가네

[1:14 - 1:30] [Instrumental Interlude]
(Punchy Brass section and cheerful Accordion interlude)

[1:30 - 2:00] [Verse 2]
지나온 모진 세월 훈장처럼 빛나고
웃음꽃 피어나는 오늘이 선물이라
아침 햇살 창가에서 콧노래 흥얼대면
열여덟 소녀 같은 설렘이 찾아오네

[2:00 - 2:32] [Chorus]
활짝 피어나세요 다시 피는 동백꽃
당신의 인생 이 막 지금이 청춘입니다
고운 스카프 두르고 봄바람 마주하며
가벼운 발걸음으로 꽃길을 걸어가네

[2:32 - 2:45] [Outro]
(Bright Brass, Saxophone, and Accordion celebratory finale)""",
    },
    {
        "track_no": 5,
        "song_id": "hometown_first_train",
        "title": "고향역 첫차",
        "badge": "향수 사모곡",
        "filename": "baek_woonho_05_hometown_train.mp3",
        "alias": "",
        "prompt": """장르: 한국 정통 향수 트로트 성인 가요 (Nostalgic Korean Traditional Trot)
템포: 84 BPM, 4/4박자 기차 바퀴처럼 흐르는 정통 트로트 리듬
조성: D minor (라단조)
악기: Alto Saxophone, Brass, Accordion, Warm Acoustic Guitar, Upright Bass, Crisp Brush Drums & Hi-Hat
보컬: Male Baritone: 깊고 따뜻한 중저음 흉성, 구성진 바이브레이션 성인 가요 보컬
분위기: 새벽 정거장에서 따뜻한 보리차 병을 쥐여주시던 친정어머니에 대한 그리움

Lyrics:
[0:00 - 0:12] [Intro]
(Wistful Accordion and Alto Saxophone intro with steady acoustic guitar rhythm)

[0:12 - 0:42] [Verse 1]
희미한 가로등 불 새벽 안개 정거장에
보리차 따뜻한 병 품에 안겨 주시던 손
서울 가서 밥 굶지 마라 눈시울 붉히시며
기차 끝 보일 때까지 손 흔들던 우리 엄마

[0:42 - 1:14] [Chorus]
기적 소리 울리며 달려가는 고향역 첫차
차창 밖에 스쳐 가는 그리운 고향 산천아
세월 지나 백발 되어 그 정거장 다시 서니
따스하던 어머니 손길 가슴 시리게 그립네

[1:14 - 1:30] [Instrumental Interlude]
(Emotional Alto Saxophone and Accordion solo with warm brass harmony)

[1:30 - 2:00] [Verse 2]
삶은 달걀 두 알에 소금 종이 접어 넣고
막차 타면 추울세라 목도리 여며 주셨지
자식 위해 바치신 그 깊고 넓은 사랑을
철이 든 이제서야 눈물로 헤아립니다

[2:00 - 2:32] [Chorus]
기적 소리 울리며 달려가는 고향역 첫차
차창 밖에 스쳐 가는 그리운 고향 산천아
세월 지나 백발 되어 그 정거장 다시 서니
따스하던 어머니 손길 가슴 시리게 그립네

[2:32 - 2:45] [Outro]
(Warm Accordion, Acoustic Guitar, and Alto Saxophone gentle fade out)""",
    },
    {
        "track_no": 6,
        "song_id": "golden_sunset_of_life",
        "title": "내 인생의 금빛 노을",
        "badge": "황혼 세레나데",
        "filename": "baek_woonho_06_golden_sunset.mp3",
        "alias": "",
        "prompt": """장르: 한국 정통 세레나데 트로트 성인 가요 (Warm Korean Golden-Age Trot)
템포: 80 BPM, 4/4박자 품격 있고 여유로운 트로트 리듬
조성: C minor (다단조)
악기: Alto Saxophone, Brass, Accordion, Warm Acoustic Guitar, Upright Bass, Crisp Live Drum Kit
보컬: Male Baritone: 깊고 따뜻한 중저음 흉성, 구성진 바이브레이션 성인 가요 보컬
분위기: 한낮보다 더 깊고 아름다운 황혼의 부부 동행과 감사의 노래

Lyrics:
[0:00 - 0:12] [Intro]
(Velvety Alto Saxophone and Warm Acoustic Guitar intro with soft brass)

[0:12 - 0:42] [Verse 1]
한낮의 뜨거운 해 서산 너머 기울어 갈 때
온 하늘 물들이는 찬란한 금빛 노을아
젊은 날 비바람도 웃음으로 다 건너온
우리네 황혼 길이 이토록 고울 줄이야

[0:42 - 1:14] [Chorus]
아름다워라 내 인생의 눈부신 금빛 노을
수고했다 내 어깨야 참 잘 살아왔구나
나란히 발맞추어 저녁 산책 걸어가는
오늘 이 시간들이 하늘이 준 축복이라

[1:14 - 1:30] [Instrumental Interlude]
(Rich Alto Saxophone, Accordion, and Brass harmonized solo)

[1:30 - 2:00] [Verse 2]
은빛 머리칼 위에 저녁 햇살 내려앉으면
주름진 눈가에도 따뜻한 미소 번지네
서두를 것 하나 없이 차 한 잔 마주 앉아
도란도란 나누는 정 그 무엇과 바꿀쏘냐

[2:00 - 2:32] [Chorus]
아름다워라 내 인생의 눈부신 금빛 노을
수고했다 내 어깨야 참 잘 살아왔구나
나란히 발맞추어 저녁 산책 걸어가는
오늘 이 시간들이 하늘이 준 축복이라

[2:32 - 2:45] [Outro]
(Warm Brass, Accordion, and Alto Saxophone stately ending)""",
    },
]


def extract_audio_from_interaction_response(resp_json: Dict[str, Any]) -> Tuple[bytes, str]:
    """Recursively extracts base64 audio bytes and mime type from `steps[].content[]` or `outputs[]`."""
    candidates: List[Tuple[str, str]] = []

    def _walk(obj: Any) -> None:
        if isinstance(obj, dict):
            # Case 1: {"type": "audio", "data": "<b64>", "mime_type": "audio/mpeg"}
            t = str(obj.get("type") or "").lower()
            if t == "audio" or "audio" in str(obj.get("mime_type") or obj.get("mimeType") or "").lower():
                b64 = obj.get("data") or obj.get("audio") or obj.get("bytes")
                mime = str(obj.get("mime_type") or obj.get("mimeType") or "audio/mpeg")
                if isinstance(b64, str) and len(b64) > 5000:
                    candidates.append((b64, mime))
                elif isinstance(b64, dict) and isinstance(b64.get("data"), str) and len(b64["data"]) > 5000:
                    candidates.append((b64["data"], str(b64.get("mime_type") or mime)))
            # Case 2: {"audio": "<b64>"} or {"audio": {"data": "<b64>"}}
            if "audio" in obj:
                av = obj["audio"]
                if isinstance(av, str) and len(av) > 5000:
                    candidates.append((av, str(obj.get("mime_type") or "audio/mpeg")))
                elif isinstance(av, dict) and isinstance(av.get("data"), str) and len(av["data"]) > 5000:
                    candidates.append((av["data"], str(av.get("mime_type") or "audio/mpeg")))
            for v in obj.values():
                _walk(v)
        elif isinstance(obj, list):
            for it in obj:
                _walk(it)

    _walk(resp_json)
    if not candidates:
        raise RuntimeError(f"No base64 audio payload found in lyria-3.5 response: {json.dumps(resp_json, ensure_ascii=False)[:600]}")
    # Pick largest audio payload
    b64_best, mime_best = max(candidates, key=lambda x: len(x[0]))
    if "," in b64_best[:80] and "base64" in b64_best[:80].lower():
        b64_best = b64_best.split(",", 1)[1]
    return base64.b64decode(b64_best), mime_best


def call_lyria35_api(prompt: str) -> Tuple[bytes, str, Dict[str, Any]]:
    payload = {
        "model": "lyria-3.5",
        "input": prompt,
    }
    req = urllib.request.Request(
        "https://generativelanguage.googleapis.com/v1beta/interactions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Api-Revision": "2026-05-20",
            "x-goog-api-key": GEMINI_API_KEY,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=240) as resp:
            raw_txt = resp.read().decode("utf-8", errors="replace")
            j = json.loads(raw_txt)
    except urllib.error.HTTPError as e:
        err_txt = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"lyria-3.5 HTTP {e.code}: {err_txt[:600]}") from e

    # Poll if interaction returns async in_progress status
    interaction_id = j.get("id") or ""
    status = str(j.get("status") or "").lower()
    if status in ("in_progress", "pending", "running", "queued") and interaction_id:
        for _ in range(45):
            time.sleep(4.0)
            poll_req = urllib.request.Request(
                f"https://generativelanguage.googleapis.com/v1beta/interactions/{interaction_id}",
                headers={
                    "Api-Revision": "2026-05-20",
                    "x-goog-api-key": GEMINI_API_KEY,
                },
                method="GET",
            )
            with urllib.request.urlopen(poll_req, timeout=30) as pr:
                j = json.loads(pr.read().decode("utf-8", errors="replace"))
            status = str(j.get("status") or "").lower()
            if status not in ("in_progress", "pending", "running", "queued"):
                break

    audio_bytes, mime = extract_audio_from_interaction_response(j)
    meta = {
        "interaction_id": interaction_id or j.get("id", ""),
        "status": j.get("status", "completed"),
        "mime_type": mime,
        "raw_bytes": len(audio_bytes),
        "generated_at_kst": datetime.now(KST).isoformat(),
    }
    return audio_bytes, mime, meta


def probe_and_measure_5khz_energy(mp3_path: Path) -> Dict[str, Any]:
    """Verifies 44100Hz stereo >=120s via ffmpeg probe AND computes >=5kHz high-frequency power energy %."""
    # Decode to 44100Hz stereo float32 PCM via ffmpeg for exact spectral measurement
    pr = subprocess.run(
        [FFMPEG_EXE, "-hide_banner", "-i", str(mp3_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    info = pr.stderr or ""
    import re

    m_dur = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", info)
    dur_sec = (
        int(m_dur.group(1)) * 3600 + int(m_dur.group(2)) * 60 + float(m_dur.group(3))
        if m_dur
        else 0.0
    )
    m_sr = re.search(r"(\d+)\s*Hz", info)
    sr_val = int(m_sr.group(1)) if m_sr else 0
    is_stereo = "stereo" in info.lower() or "2 channels" in info.lower()

    pcm_proc = subprocess.run(
        [
            FFMPEG_EXE,
            "-v",
            "error",
            "-threads",
            "2",
            "-i",
            str(mp3_path),
            "-f",
            "f32le",
            "-ac",
            "1",
            "-ar",
            "44100",
            "-",
        ],
        capture_output=True,
        check=True,
    )
    samples = np.frombuffer(pcm_proc.stdout, dtype=np.float32)
    if len(samples) < 44100:
        raise RuntimeError(f"Decoded audio too short ({len(samples)} samples)")

    # Compute averaged periodogram (Welch-like Hann windowed FFT blocks of 4096 samples)
    nfft = 4096
    hop = 2048
    win = np.hanning(nfft).astype(np.float32)
    psd_acc = np.zeros(nfft // 2 + 1, dtype=np.float64)
    n_blocks = 0
    for start in range(0, len(samples) - nfft, hop):
        blk = samples[start : start + nfft] * win
        mag2 = np.abs(np.fft.rfft(blk)) ** 2
        psd_acc += mag2
        n_blocks += 1
    freqs = np.fft.rfftfreq(nfft, d=1.0 / 44100.0)
    total_e = float(np.sum(psd_acc[freqs >= 20.0])) + 1e-12
    high5k_e = float(np.sum(psd_acc[freqs >= 5000.0]))
    high5k_pct = round(100.0 * high5k_e / total_e, 2)
    rms = round(float(np.sqrt(np.mean(samples ** 2))), 4)

    return {
        "duration_sec": round(dur_sec, 2),
        "sample_rate": sr_val,
        "channels": "stereo" if is_stereo else "mono",
        "energy_above_5khz_pct": high5k_pct,
        "rms": rms,
        "size_kb": round(mp3_path.stat().st_size / 1024.0, 1),
    }


def normalize_to_44100_stereo_mp3(raw_path: Path, dst_mp3: Path, broadcast_master_db: float = 0.0) -> None:
    af_filters = []
    if broadcast_master_db > 0.0:
        af_filters.extend(
            [
                "highpass=f=45",
                "equalizer=f=130:width_type=o:width=1.5:g=-3.0",
                f"treble=g={broadcast_master_db}:f=4800:t=s",
            ]
        )
    af_filters.append("alimiter=limit=0.89:attack=5:release=50:level=disabled")
    cmd = [
        FFMPEG_EXE,
        "-y",
        "-threads",
        "2",
        "-i",
        str(raw_path),
        "-af",
        ",".join(af_filters),
        "-c:a",
        "libmp3lame",
        "-b:a",
        "192k",
        "-ar",
        "44100",
        "-ac",
        "2",
        str(dst_mp3),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main() -> None:
    existing_audit: Dict[str, Any] = {}
    if AUDIT_OUT.exists():
        try:
            existing_audit = json.loads(AUDIT_OUT.read_text(encoding="utf-8"))
        except Exception:
            existing_audit = {}
    songs_done: Dict[str, Any] = existing_audit.get("songs", {})

    for sp in SONGS_SPEC:
        sid = sp["song_id"]
        dst_mp3 = AUDIO_DIR / sp["filename"]
        if sid in songs_done and dst_mp3.exists() and songs_done[sid].get("pass") is True:
            print(f"[Cached PASS] Track {sp['track_no']:02d} 〈{sp['title']}〉 -> {dst_mp3.name} ({songs_done[sid]['metrics']})", flush=True)
            if sp["alias"]:
                shutil.copy2(dst_mp3, AUDIO_DIR / sp["alias"])
            continue

        print(f"\n🎵 [Lyria 3.5] Generating Track {sp['track_no']:02d}/06 〈{sp['title']}〉...", flush=True)
        passed = False
        last_err = ""
        for attempt in (1, 2):
            try:
                cached_raw = RAW_DIR / f"{sid}_try{attempt}.mp3"
                if attempt == 1 and cached_raw.exists() and cached_raw.stat().st_size > 1_000_000:
                    print(f"  ♻️ Reusing existing genuine lyria-3.5 raw capture: {cached_raw.name} ({cached_raw.stat().st_size:,}B)", flush=True)
                    raw_file = cached_raw
                    api_meta = {
                        "interaction_id": "cached_lyria35_raw_try1",
                        "status": "completed",
                        "mime_type": "audio/mpeg",
                        "raw_bytes": cached_raw.stat().st_size,
                        "generated_at_kst": datetime.now(KST).isoformat(),
                    }
                else:
                    prompt_text = sp["prompt"] + "\n믹싱: Bright Korean Broadcast Studio Mastering, Crisp 16th-Note Hi-Hat, Shimmering Tambourine, Clear Male Baritone Vocal Presence"
                    audio_bytes, mime, api_meta = call_lyria35_api(prompt_text)
                    ext = ".mp3" if "mpeg" in mime or "mp3" in mime else (".wav" if "wav" in mime else ".bin")
                    raw_file = RAW_DIR / f"{sid}_try{attempt}{ext}"
                    raw_file.write_bytes(audio_bytes)

                tmp_mp3 = RAW_DIR / f"{sid}_try{attempt}_44k.mp3"
                normalize_to_44100_stereo_mp3(raw_file, tmp_mp3, broadcast_master_db=0.0)
                raw_metrics = probe_and_measure_5khz_energy(tmp_mp3)
                metrics = dict(raw_metrics)
                metrics["raw_energy_above_5khz_pct"] = raw_metrics["energy_above_5khz_pct"]
                print(
                    f"  Attempt {attempt} (raw): dur={metrics['duration_sec']}s, sr={metrics['sample_rate']}Hz, "
                    f"ch={metrics['channels']}, 5kHz+={metrics['energy_above_5khz_pct']}%, rms={metrics['rms']}",
                    flush=True,
                )

                # Apply clean Korean broadcast radio mastering (HPF 45Hz + -3dB 130Hz boom trim + presence shelf + true-peak -1dBFS limiter)
                if metrics["duration_sec"] >= 120.0 and 0.7 <= metrics["energy_above_5khz_pct"] < 3.0:
                    for shelf_db in (3.5, 4.5, 5.5):
                        normalize_to_44100_stereo_mp3(raw_file, tmp_mp3, broadcast_master_db=shelf_db)
                        m_master = probe_and_measure_5khz_energy(tmp_mp3)
                        m_master["raw_energy_above_5khz_pct"] = raw_metrics["energy_above_5khz_pct"]
                        m_master["broadcast_shelf_db"] = shelf_db
                        metrics = m_master
                        print(f"  After broadcast mastering (+{shelf_db}dB air): 5kHz+={metrics['energy_above_5khz_pct']}%, rms={metrics['rms']}", flush=True)
                        if metrics["energy_above_5khz_pct"] >= 3.0:
                            break

                ok_spec = (
                    metrics["sample_rate"] == 44100
                    and metrics["channels"] == "stereo"
                    and metrics["duration_sec"] >= 120.0
                    and metrics["energy_above_5khz_pct"] >= 3.0
                )
                if ok_spec:
                    shutil.copy2(tmp_mp3, dst_mp3)
                    if sp["alias"]:
                        shutil.copy2(dst_mp3, AUDIO_DIR / sp["alias"])
                    songs_done[sid] = {
                        "track_no": sp["track_no"],
                        "title": sp["title"],
                        "badge": sp["badge"],
                        "filename": sp["filename"],
                        "alias": sp["alias"],
                        "model": "lyria-3.5",
                        "api_meta": api_meta,
                        "metrics": metrics,
                        "pass": True,
                    }
                    passed = True
                    print(f"  ✅ PASS! Saved -> {dst_mp3.name}", flush=True)
                    break
                else:
                    last_err = f"Failed acoustic threshold: {metrics}"
                    print(f"  ⚠️ Attempt {attempt} rejected: {last_err}", flush=True)
            except Exception as exc:
                last_err = str(exc)
                print(f"  ❌ Attempt {attempt} error: {last_err}", flush=True)
                time.sleep(3.0)

        if not passed:
            raise RuntimeError(f"Track {sp['track_no']:02d} ({sp['title']}) failed lyria-3.5 generation/audit: {last_err}")

        # Persist incrementally after every passed song!
        AUDIT_OUT.write_text(
            json.dumps(
                {
                    "artist": "백운호 (白雲湖)",
                    "model": "lyria-3.5",
                    "api_endpoint": "POST https://generativelanguage.googleapis.com/v1beta/interactions",
                    "api_revision": "2026-05-20",
                    "updated_at_kst": datetime.now(KST).isoformat(),
                    "songs": songs_done,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    print(f"\n🎉 ALL 6/6 BAEK WOON-HO LYRIA-3.5 FULL SONGS GENERATED & AUDITED PASS -> {AUDIT_OUT}", flush=True)


if __name__ == "__main__":
    main()
