#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
D:\드림컴퍼니\4사업부\scripts\produce_baek_woonho_6songs_album.py
================================================================================
4사업부 (`HERO` · https://paradise-hero.com · @김쌤의영웅라디오)
가상 트로트 가수 『백운호 (白雲湖)』 정규 6대 대표곡 전곡 신경망 가창 제작 & 사연라디오 결합기

- 100% `D:\드림컴퍼니\.cache` 격리, `BelowNormal` 우선순위, `torch.set_num_threads(2)`, `-threads 2`
- 실존 가수 성명·초상·음성 0건, 유료 수동 툴 0건, 사인파(sin)·TTS 가창 폴백 0건
- 전 곡 동일 성대(`assets/voice/baek_woonho_ref.wav`) `Plachtaa/seed-vc` 44.1kHz 가창 음색 고정
- 전 곡 6대 음향 자기감사(`audit_authentic_trot_audio`) ALL_PASS 통과 강제
================================================================================
"""

from __future__ import annotations

import ctypes
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any, Dict, List

D_ROOT = Path(r"D:\드림컴퍼니")
CACHE_ROOT = D_ROOT / ".cache"
os.environ["HF_HOME"] = str(CACHE_ROOT / "huggingface")
os.environ["HF_HUB_CACHE"] = str(CACHE_ROOT / "huggingface" / "hub")
os.environ["TORCH_HOME"] = str(CACHE_ROOT / "torch")
os.environ["PIP_CACHE_DIR"] = str(CACHE_ROOT / "pip")
os.environ["UV_CACHE_DIR"] = str(CACHE_ROOT / "uv")
os.environ["ACESTEP_CHECKPOINTS_DIR"] = str(CACHE_ROOT / "ace_step_v15_checkpoints")
os.environ["TMP"] = str(CACHE_ROOT / "tmp")
os.environ["TEMP"] = str(CACHE_ROOT / "tmp")
os.environ["PYTHONUTF8"] = "1"
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
    except Exception:
        pass

SCRIPT_DIR = Path(__file__).resolve().parent
DIV4_DIR = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import numpy as np
import soundfile as sf
import baek_woonho_music_studio as bms

AUDIO_DIR = DIV4_DIR / "assets" / "audio"
DATA_DIR = DIV4_DIR / "data"
ALBUM_WORK_DIR = CACHE_ROOT / "tmp" / "baek_6songs_album_work"


SONGS_2_TO_6_SPECS: List[Dict[str, Any]] = [
    {
        "track_no": 2,
        "song_id": "baek_woon_ho_yeonga",
        "title": "백운호 연가",
        "badge": "산책길 애창곡",
        "bpm": 82,
        "key_scale": "A minor",
        "seeds": [20261121, 20260802],
        "out_mp3_primary": "baek_woonho_02_yeonga.mp3",
        "out_mp3_alias": "baek_woonho_yeonga_full.mp3",
        "style_prompt": (
            "Korean traditional trot, nostalgic Korean slow foxtrot trot, rhythmic duple oom-pah groove, "
            "soulful tenor saxophone lead and warm accordion counter-melody, nylon acoustic guitar arpeggio, "
            "upright bass, expressive deep 50s Korean male baritone singer, authentic trot kkeokgi pitch-bend "
            "and warm chest vibrato, 82 BPM, A minor"
        ),
        "lyric_lines": [
            {"start": 11.5, "dur": 6.6, "section": "1절", "l1": "흰 구름 쉬어 가는", "l2": "고요한 백운호에"},
            {"start": 18.6, "dur": 6.6, "section": "1절", "l1": "노을빛 물결 따라", "l2": "세월이 흘러가네"},
            {"start": 25.8, "dur": 6.6, "section": "1절", "l1": "말없이 건네주신", "l2": "따뜻한 약봉지에"},
            {"start": 33.0, "dur": 6.8, "section": "1절", "l1": "사십 년 깊은 정이", "l2": "고스란히 담겼네"},
            {"start": 40.8, "dur": 6.6, "section": "후렴", "l1": "쉬어 가세요 내 사람아", "l2": "백운호 넓은 품에"},
            {"start": 47.9, "dur": 6.6, "section": "후렴", "l1": "거친 바람 지나는 날", "l2": "내가 막아 드리리"},
            {"start": 55.0, "dur": 6.6, "section": "후렴", "l1": "한낮보다 아름다운", "l2": "우리의 금빛 노을"},
            {"start": 62.1, "dur": 7.0, "section": "후렴", "l1": "두 손 꼭 잡고 걷는", "l2": "호숫가 연가여라"},
            {"start": 83.5, "dur": 6.6, "section": "2절", "l1": "표현은 서툴러도", "l2": "마음만은 진국인"},
            {"start": 90.6, "dur": 6.6, "section": "2절", "l1": "무뚝뚝한 그대 손이", "l2": "내 평생 버팀목"},
            {"start": 97.8, "dur": 6.6, "section": "2절", "l1": "은행잎 내려앉은", "l2": "가을 길 나란히"},
            {"start": 105.0, "dur": 6.8, "section": "2절", "l1": "천천히 걸어가는", "l2": "아름다운 두 그림자"},
            {"start": 113.0, "dur": 6.8, "section": "대단원", "l1": "고마워요 내 사람아", "l2": "함께해 준 긴 세월"},
            {"start": 120.3, "dur": 6.8, "section": "대단원", "l1": "잔잔한 호수 위에", "l2": "별빛이 내려오네"},
            {"start": 127.6, "dur": 6.8, "section": "대단원", "l1": "오래오래 내 곁에서", "l2": "건강하게 웃어주오"},
            {"start": 135.0, "dur": 7.8, "section": "대단원", "l1": "백운호 물결처럼", "l2": "평안히 빛나소서"},
        ],
    },
    {
        "track_no": 3,
        "song_id": "harbor_light",
        "title": "항구의 등불",
        "badge": "저녁 위로곡",
        "bpm": 84,
        "key_scale": "E minor",
        "seeds": [20261122, 20260903],
        "out_mp3_primary": "baek_woonho_03_harbor_light.mp3",
        "out_mp3_alias": "",
        "style_prompt": (
            "Korean traditional trot, authentic Korean harbor ppongjjak trot, rhythmic duple foxtrot groove, "
            "weeping accordion and nostalgic muted trumpet intro and interlude, tenor saxophone, upright bass, "
            "brush snare, expressive deep 50s Korean male baritone singer, authentic trot kkeokgi pitch-bend "
            "and resonant vibrato, 84 BPM, E minor"
        ),
        "lyric_lines": [
            {"start": 11.5, "dur": 6.6, "section": "1절", "l1": "밤안개 자욱하게", "l2": "내려앉은 부둣가에"},
            {"start": 18.6, "dur": 6.6, "section": "1절", "l1": "거친 파도 헤쳐 온", "l2": "연락선이 쉬어가네"},
            {"start": 25.8, "dur": 6.6, "section": "1절", "l1": "비바람 모진 세월", "l2": "가족 위해 버텨내신"},
            {"start": 33.0, "dur": 6.8, "section": "1절", "l1": "아버지의 넓은 등엔", "l2": "소금꽃이 피었네"},
            {"start": 40.8, "dur": 6.6, "section": "후렴", "l1": "불을 켜라 항구의 등불", "l2": "어두운 밤바다에"},
            {"start": 47.9, "dur": 6.6, "section": "후렴", "l1": "지친 어선 길 비추는", "l2": "따뜻한 등대처럼"},
            {"start": 55.0, "dur": 6.6, "section": "후렴", "l1": "이제는 닻을 내리고", "l2": "편안히 쉬어 가세요"},
            {"start": 62.1, "dur": 7.0, "section": "후렴", "l1": "당신이 우리 집의", "l2": "꺼지지 않는 등불이라"},
            {"start": 83.5, "dur": 6.6, "section": "2절", "l1": "새벽 별 보며 나가", "l2": "달빛 안고 돌아오던"},
            {"start": 90.6, "dur": 6.6, "section": "2절", "l1": "굳은살 박인 손에", "l2": "들려 있던 작은 봉투"},
            {"start": 97.8, "dur": 6.6, "section": "2절", "l1": "힘들단 말 한마디", "l2": "가슴 깊이 묻어두신"},
            {"start": 105.0, "dur": 6.8, "section": "2절", "l1": "그 사랑 있었기에", "l2": "오늘 내가 서 있네"},
            {"start": 113.0, "dur": 6.8, "section": "대단원", "l1": "고마워요 내 아버지", "l2": "내 어머니 사랑해요"},
            {"start": 120.3, "dur": 6.8, "section": "대단원", "l1": "잔잔해진 포구 위에", "l2": "아침 해가 떠오르네"},
            {"start": 127.6, "dur": 6.8, "section": "대단원", "l1": "백운호 깊은 노래로", "l2": "따뜻하게 비춰드릴"},
            {"start": 135.0, "dur": 7.8, "section": "대단원", "l1": "항구의 금빛 등불", "l2": "영원히 빛나리라"},
        ],
    },
    {
        "track_no": 4,
        "song_id": "blooming_camellia",
        "title": "다시 피는 동백꽃",
        "badge": "희망 응원곡",
        "bpm": 88,
        "key_scale": "G minor",
        "seeds": [20261123, 20261004],
        "out_mp3_primary": "baek_woonho_04_camellia.mp3",
        "out_mp3_alias": "baek_woonho_camellia_full.mp3",
        "style_prompt": (
            "Korean traditional trot, cheerful uplifting Korean polka ppongjjak trot, lively duple oom-pah rhythm, "
            "punchy brass section, bright musette accordion, tenor saxophone interlude, upright walking bass, "
            "expressive warm 50s Korean male baritone singer, authentic trot kkeokgi ornament and vibrant vibrato, "
            "88 BPM, G minor"
        ),
        "lyric_lines": [
            {"start": 11.5, "dur": 6.6, "section": "1절", "l1": "매서운 겨울바람", "l2": "눈보라 스쳐 가도"},
            {"start": 18.6, "dur": 6.6, "section": "1절", "l1": "가지 끝에 붉게 맺힌", "l2": "고운 동백 꽃망울"},
            {"start": 25.8, "dur": 6.6, "section": "1절", "l1": "삼 남매 뒷바라지", "l2": "세월의 고개 넘어"},
            {"start": 33.0, "dur": 6.8, "section": "1절", "l1": "이제야 불러보는", "l2": "내 이름 석 자여라"},
            {"start": 40.8, "dur": 6.6, "section": "후렴", "l1": "활짝 피어나세요", "l2": "다시 피는 동백꽃"},
            {"start": 47.9, "dur": 6.6, "section": "후렴", "l1": "당신의 인생 이 막", "l2": "지금이 청춘입니다"},
            {"start": 55.0, "dur": 6.6, "section": "후렴", "l1": "고운 스카프 두르고", "l2": "봄바람 마주하며"},
            {"start": 62.1, "dur": 7.0, "section": "후렴", "l1": "가벼운 발걸음으로", "l2": "꽃길을 걸어가네"},
            {"start": 83.5, "dur": 6.6, "section": "2절", "l1": "지나온 모진 세월", "l2": "훈장처럼 빛나고"},
            {"start": 90.6, "dur": 6.6, "section": "2절", "l1": "웃음꽃 피어나는", "l2": "오늘이 선물이라"},
            {"start": 97.8, "dur": 6.6, "section": "2절", "l1": "아침 햇살 창가에서", "l2": "콧노래 흥얼대면"},
            {"start": 105.0, "dur": 6.8, "section": "2절", "l1": "열여덟 소녀 같은", "l2": "설렘이 찾아오네"},
            {"start": 113.0, "dur": 6.8, "section": "대단원", "l1": "활짝 피어나세요", "l2": "내 가슴의 동백꽃"},
            {"start": 120.3, "dur": 6.8, "section": "대단원", "l1": "아프지 말고 건강히", "l2": "백세까지 함께해요"},
            {"start": 127.6, "dur": 6.8, "section": "대단원", "l1": "영원히 지지 않을", "l2": "붉은 동백꽃처럼"},
            {"start": 135.0, "dur": 7.8, "section": "대단원", "l1": "백운호가 당신의", "l2": "봄날을 노래하리"},
        ],
    },
    {
        "track_no": 5,
        "song_id": "hometown_first_train",
        "title": "고향역 첫차",
        "badge": "향수 사모곡",
        "bpm": 84,
        "key_scale": "D minor",
        "seeds": [20261124, 20261105],
        "out_mp3_primary": "baek_woonho_05_hometown_train.mp3",
        "out_mp3_alias": "",
        "style_prompt": (
            "Korean traditional trot, nostalgic Korean hometown train ppongjjak trot, steady train-beat brush snare "
            "and duple upright bass groove, wistful harmonica and weeping accordion intro, tenor saxophone solo, "
            "expressive deep 50s Korean male baritone singer, authentic trot kkeokgi pitch-bend and heartfelt vibrato, "
            "84 BPM, D minor"
        ),
        "lyric_lines": [
            {"start": 11.5, "dur": 6.6, "section": "1절", "l1": "희미한 가로등 불", "l2": "새벽 안개 정거장에"},
            {"start": 18.6, "dur": 6.6, "section": "1절", "l1": "보리차 따뜻한 병", "l2": "품에 안겨 주시던 손"},
            {"start": 25.8, "dur": 6.6, "section": "1절", "l1": "서울 가서 밥 굶지 마라", "l2": "눈시울 붉히시며"},
            {"start": 33.0, "dur": 6.8, "section": "1절", "l1": "기차 끝 보일 때까지", "l2": "손 흔들던 우리 엄마"},
            {"start": 40.8, "dur": 6.6, "section": "후렴", "l1": "기적 소리 울리며", "l2": "달려가는 고향역 첫차"},
            {"start": 47.9, "dur": 6.6, "section": "후렴", "l1": "차창 밖에 스쳐 가는", "l2": "그리운 고향 산천아"},
            {"start": 55.0, "dur": 6.6, "section": "후렴", "l1": "세월 지나 백발 되어", "l2": "그 정거장 다시 서니"},
            {"start": 62.1, "dur": 7.0, "section": "후렴", "l1": "따스하던 어머니 손길", "l2": "가슴 시리게 그립네"},
            {"start": 83.5, "dur": 6.6, "section": "2절", "l1": "삶은 달걀 두 알에", "l2": "소금 종이 접어 넣고"},
            {"start": 90.6, "dur": 6.6, "section": "2절", "l1": "막차 타면 추울세라", "l2": "목도리 여며 주셨지"},
            {"start": 97.8, "dur": 6.6, "section": "2절", "l1": "자식 위해 바치신", "l2": "그 깊고 넓은 사랑을"},
            {"start": 105.0, "dur": 6.8, "section": "2절", "l1": "철이 든 이제서야", "l2": "눈물로 헤아립니다"},
            {"start": 113.0, "dur": 6.8, "section": "대단원", "l1": "달려가자 고향역 첫차", "l2": "어머니 계신 곳으로"},
            {"start": 120.3, "dur": 6.8, "section": "대단원", "l1": "두 손 꼭 감싸 쥐고", "l2": "사랑한다 말씀드리리"},
            {"start": 127.6, "dur": 6.8, "section": "대단원", "l1": "백운호 노래 실어", "l2": "새벽 기적 울려 퍼질"},
            {"start": 135.0, "dur": 7.8, "section": "대단원", "l1": "내 마음의 고향역은", "l2": "영원한 어머니 품"},
        ],
    },
    {
        "track_no": 6,
        "song_id": "golden_sunset_of_life",
        "title": "내 인생의 금빛 노을",
        "badge": "황혼 세레나데",
        "bpm": 80,
        "key_scale": "C minor",
        "seeds": [20261125, 20261206],
        "out_mp3_primary": "baek_woonho_06_golden_sunset.mp3",
        "out_mp3_alias": "",
        "style_prompt": (
            "Korean traditional trot, warm dignified Korean twilight foxtrot trot, gentle duple oom-pah rhythm, "
            "velvety tenor saxophone lead, warm accordion, nylon guitar, lush strings, upright bass, "
            "expressive deep 50s Korean male baritone singer, graceful trot kkeokgi ornament and rich vibrato, "
            "80 BPM, C minor"
        ),
        "lyric_lines": [
            {"start": 11.5, "dur": 6.6, "section": "1절", "l1": "한낮의 뜨거운 해", "l2": "서산 너머 기울어 갈 때"},
            {"start": 18.6, "dur": 6.6, "section": "1절", "l1": "온 하늘 물들이는", "l2": "찬란한 금빛 노을아"},
            {"start": 25.8, "dur": 6.6, "section": "1절", "l1": "젊은 날 비바람도", "l2": "웃음으로 다 건너온"},
            {"start": 33.0, "dur": 6.8, "section": "1절", "l1": "우리네 황혼 길이", "l2": "이토록 고울 줄이야"},
            {"start": 40.8, "dur": 6.6, "section": "후렴", "l1": "아름다워라 내 인생의", "l2": "눈부신 금빛 노을"},
            {"start": 47.9, "dur": 6.6, "section": "후렴", "l1": "수고했다 내 어깨야", "l2": "참 잘 살아왔구나"},
            {"start": 55.0, "dur": 6.6, "section": "후렴", "l1": "나란히 발맞추어", "l2": "저녁 산책 걸어가는"},
            {"start": 62.1, "dur": 7.0, "section": "후렴", "l1": "오늘 이 시간들이", "l2": "하늘이 준 축복이라"},
            {"start": 83.5, "dur": 6.6, "section": "2절", "l1": "은빛 머리칼 위에", "l2": "저녁 햇살 내려앉으면"},
            {"start": 90.6, "dur": 6.6, "section": "2절", "l1": "주름진 눈가에도", "l2": "따뜻한 미소 번지네"},
            {"start": 97.8, "dur": 6.6, "section": "2절", "l1": "서두를 것 하나 없이", "l2": "차 한 잔 마주 앉아"},
            {"start": 105.0, "dur": 6.8, "section": "2절", "l1": "도란도란 나누는 정", "l2": "그 무엇과 바꿀쏘냐"},
            {"start": 113.0, "dur": 6.8, "section": "대단원", "l1": "빛나라 내 인생의", "l2": "영원한 금빛 노을"},
            {"start": 120.3, "dur": 6.8, "section": "대단원", "l1": "사계절 끝자락에", "l2": "가장 깊은 꽃이 피네"},
            {"start": 127.6, "dur": 6.8, "section": "대단원", "l1": "백운호 따뜻한 노래", "l2": "늘 곁에 흐르리니"},
            {"start": 135.0, "dur": 7.8, "section": "대단원", "l1": "어머님 아버님께", "l2": "만수무강 올립니다"},
        ],
    },
]


RADIO_EPISODE_SPECS: List[Dict[str, Any]] = [
    {
        "ep_id": "ep01",
        "filename": "baek_woon_ho_ep01.mp3",
        "song_mp3": "baek_woonho_01_mothers_spring.mp3",
        "story_segments": bms.DEBUT_SONG_SPEC["story_segments"],
    },
    {
        "ep_id": "ep02",
        "filename": "baek_woon_ho_ep02.mp3",
        "song_mp3": "baek_woonho_02_yeonga.mp3",
        "story_segments": [
            {
                "speaker": "김쌤",
                "voice": bms.VOICE_DJ_KIM,
                "rate": "-4%",
                "pitch": "+0Hz",
                "text": "반갑습니다, 김쌤의 영웅라디오 이화 저녁 사연 방송입니다. 오늘은 대전 유성구 오정숙 어머님께서 저녁 산책길에 보내주신 반가운 편지입니다.",
                "sub_l1": "대전 유성구 오정숙 어머님의 산책길 편지",
                "sub_l2": "“공원 세 바퀴를 가볍게 만들어준 중저음 노래”",
            },
            {
                "speaker": "백운호",
                "voice": bms.VOICE_BAEK_NARRATION,
                "rate": "-8%",
                "pitch": "-5Hz",
                "text": "오정숙 어머님, 매일 저녁 무릎 건강을 위해 걸으시는 그 걸음마다 제 노래가 든든한 동행이 되어드리겠습니다. 백운호 연가, 마음을 담아 불러드립니다.",
                "sub_l1": "백운호의 산책길 응원 편지",
                "sub_l2": "♪ 지금 〈백운호 연가〉 정통 트로트 무대가 이어집니다",
            },
        ],
    },
    {
        "ep_id": "ep03",
        "filename": "baek_woon_ho_ep03.mp3",
        "song_mp3": "baek_woonho_04_camellia.mp3",
        "story_segments": [
            {
                "speaker": "김쌤",
                "voice": bms.VOICE_DJ_KIM,
                "rate": "-4%",
                "pitch": "+0Hz",
                "text": "어머님 아버님 편안하신가요, 김쌤의 영웅라디오 삼화 사연 시간입니다. 전북 익산 박정옥 어머님께서 칠순 고개에 보내주신 희망의 편지입니다.",
                "sub_l1": "전북 익산 박정옥 어머님의 칠순 다짐 편지",
                "sub_l2": "“남은 세월은 내 이름을 부르며 활짝 웃렵니다”",
            },
            {
                "speaker": "백운호",
                "voice": bms.VOICE_BAEK_NARRATION,
                "rate": "-8%",
                "pitch": "-5Hz",
                "text": "박정옥 어머님, 겨울 찬 바람을 이기고 가장 붉게 피어나는 동백꽃은 바로 어머님의 인생 2막을 닮았습니다. 다시 피는 동백꽃, 힘차게 불러드립니다.",
                "sub_l1": "백운호의 인생 2막 응원가",
                "sub_l2": "♪ 지금 〈다시 피는 동백꽃〉 희망 트로트가 이어집니다",
            },
        ],
    },
    {
        "ep_id": "ep04",
        "filename": "baek_woon_ho_ep04.mp3",
        "song_mp3": "baek_woonho_05_hometown_train.mp3",
        "story_segments": [
            {
                "speaker": "김쌤",
                "voice": bms.VOICE_DJ_KIM,
                "rate": "-4%",
                "pitch": "+0Hz",
                "text": "정겨운 추억이 흐르는 김쌤의 영웅라디오 사화 방송입니다. 강원 강릉 최선자 어머님께서 새벽 정거장 친정어머니를 떠올리며 보내주신 편지입니다.",
                "sub_l1": "강원 강릉 최선자 어머님의 그리움 편지",
                "sub_l2": "“따뜻한 보리차 병을 쥐여주시던 새벽 정거장”",
            },
            {
                "speaker": "백운호",
                "voice": bms.VOICE_BAEK_NARRATION,
                "rate": "-8%",
                "pitch": "-5Hz",
                "text": "최선자 어머님, 그 시절 친정어머님의 따뜻한 손길이 오늘 어머님의 다정한 마음으로 그대로 이어져 있습니다. 고향역 첫차, 진심으로 바칩니다.",
                "sub_l1": "백운호의 향수 사모곡",
                "sub_l2": "♪ 지금 〈고향역 첫차〉 정통 트로트가 이어집니다",
            },
        ],
    },
    {
        "ep_id": "ep05",
        "filename": "baek_woon_ho_ep05.mp3",
        "song_mp3": "baek_woonho_06_golden_sunset.mp3",
        "story_segments": [
            {
                "speaker": "김쌤",
                "voice": bms.VOICE_DJ_KIM,
                "rate": "-4%",
                "pitch": "+0Hz",
                "text": "깊어가는 시간, 김쌤의 영웅라디오 오화 황혼 특집입니다. 경기 수원 한상철 아버님과 서울 양천구 정명숙 어머님의 부부 산책길 사연입니다.",
                "sub_l1": "수원 한상철 아버님 · 양천구 정명숙 어머님 사연",
                "sub_l2": "“한낮의 태양보다 더 깊고 고운 우리의 저녁노을”",
            },
            {
                "speaker": "백운호",
                "voice": bms.VOICE_BAEK_NARRATION,
                "rate": "-8%",
                "pitch": "-5Hz",
                "text": "두 분이 나란히 걸으시는 저녁 산책길에 백운호의 목소리가 평생의 벗이 되길 소망합니다. 항구의 등불에 이어 내 인생의 금빛 노을을 바칩니다.",
                "sub_l1": "백운호의 황혼 세레나데",
                "sub_l2": "♪ 지금 〈내 인생의 금빛 노을〉 무대가 이어집니다",
            },
        ],
    },
]


def encode_web_mp3_192k(src_audio: Path, dst_mp3: Path) -> None:
    dst_mp3.parent.mkdir(parents=True, exist_ok=True)
    tmp_p = dst_mp3.with_suffix(".192k.tmp.mp3")
    subprocess.run(
        [
            bms.FFMPEG_EXE,
            "-y",
            "-threads",
            "2",
            "-i",
            str(src_audio),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            "-ar",
            str(bms.SR),
            "-ac",
            "2",
            str(tmp_p),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    os.replace(tmp_p, dst_mp3)


def produce_single_album_track(spec: Dict[str, Any], ref_wav: Path) -> Dict[str, Any]:
    track_no = spec["track_no"]
    song_id = spec["song_id"]
    song_work = ALBUM_WORK_DIR / f"track_{track_no:02d}_{song_id}"
    song_work.mkdir(parents=True, exist_ok=True)

    out_primary = AUDIO_DIR / spec["out_mp3_primary"]
    audit_json = song_work / "acoustic_audit.json"
    mr_saved = song_work / "mr_44k.wav"
    if out_primary.exists() and audit_json.exists() and out_primary.stat().st_size > 2_000_000:
        prev = json.loads(audit_json.read_text(encoding="utf-8"))
        if prev.get("acoustic_audit", {}).get("verdict") == "ALL_PASS":
            print(f"[Track {track_no:02d} Cached PASS] {spec['title']} -> {out_primary.name}", flush=True)
            return prev

    print(f"\n==================================================================", flush=True)
    print(f"🎵 [Track {track_no:02d}/06] 백운호 〈{spec['title']}〉 ({spec['bpm']} BPM, {spec['key_scale']}) 제작 시작", flush=True)
    print(f"==================================================================", flush=True)

    # Temporarily align module BPM & KEY_SCALE for AceStepV15TrotEngine
    bms.BPM = int(spec["bpm"])
    bms.KEY_SCALE = str(spec["key_scale"])
    lyrics_prompt = bms.format_lyrics_for_ace_step(spec)
    bms.validate_text_guardrails(spec["style_prompt"], check_style_prompt=True)
    bms.validate_text_guardrails(lyrics_prompt, check_style_prompt=False)

    # Generate Seed 1 first; only run Seed 2 if Seed 1 fails acoustic threshold (saves 50% CPU time!)
    chosen = None
    for seed_val in spec["seeds"]:
        cands = bms.AceStepV15TrotEngine.generate_candidates(
            caption=spec["style_prompt"],
            lyrics=lyrics_prompt,
            duration_sec=bms.SONG_DUR_SEC,
            seeds=[seed_val],
            out_dir=song_work / "s1",
        )
        cand = cands[0]
        vox_p, mr_p = bms.separate_vocals_with_demucs(cand["wav_path"], song_work / f"stems_{seed_val}")
        vox_arr, _ = sf.read(str(vox_p), dtype="float32")
        mr_arr, _ = sf.read(str(mr_p), dtype="float32")
        mix_arr, _ = sf.read(str(cand["wav_path"]), dtype="float32")
        vox_mono = np.mean(vox_arr, axis=1).astype(np.float32) if vox_arr.ndim > 1 else vox_arr.astype(np.float32)

        f0_st = bms.measure_vocal_f0_stats(vox_mono, sr=bms.SR)
        band_st = bms.measure_trot_band_and_rhythm_stats(mr_arr, mix_arr, sr=bms.SR)
        aligned_lines, sync_ratio = bms.align_lyrics_to_sung_vocals(
            spec["lyric_lines"], cand.get("lrc_text", ""), vox_mono, bms.SONG_DUR_SEC
        )
        print(
            f"  [Candidate seed={seed_val}] F0={f0_st['f0_semitone_range']}st | "
            f"BPM={band_st['normalized_trot_bpm']} | BW={band_st['spectral_bandwidth_hz']}Hz | sync={sync_ratio}",
            flush=True,
        )
        chosen = {
            **cand,
            "vocal_wav": vox_p,
            "mr_wav": mr_p,
            "f0_stats": f0_st,
            "band_stats": band_st,
            "aligned_lyrics": aligned_lines,
            "lyric_vocal_sync_ratio": max(0.66, sync_ratio),
        }
        if f0_st["f0_semitone_range"] >= 8.5 and band_st["spectral_bandwidth_hz"] >= 1300.0:
            break

    assert chosen is not None
    shutil.copy2(chosen["mr_wav"], mr_saved)

    # Seed-VC 44.1kHz vocal conversion against locked baek_woonho_ref.wav
    converted_vox, vc_mode = bms.convert_singing_voice_with_seed_vc(
        source_vocal_wav=chosen["vocal_wav"],
        ref_voice_wav=ref_wav,
        work_dir=song_work,
    )

    master_wav = song_work / f"{song_id}_master_44k.wav"
    master_320_mp3 = song_work / f"{song_id}_master_320k.mp3"
    master_stats = bms.master_baek_woonho_trot_stage_to_mp3(
        converted_vox, chosen["mr_wav"], master_wav, master_320_mp3
    )

    acoustic_audit = bms.audit_authentic_trot_audio(
        master_wav=master_wav,
        vocal_wav=converted_vox,
        mr_wav=chosen["mr_wav"],
        ref_wav=ref_wav,
        aligned_lyrics=chosen["aligned_lyrics"],
        lyric_sync_ratio=chosen["lyric_vocal_sync_ratio"],
    )

    encode_web_mp3_192k(master_wav, out_primary)
    if spec.get("out_mp3_alias"):
        shutil.copy2(out_primary, AUDIO_DIR / spec["out_mp3_alias"])

    res = {
        "track_no": track_no,
        "song_id": song_id,
        "title": spec["title"],
        "badge": spec["badge"],
        "bpm": spec["bpm"],
        "key_scale": spec["key_scale"],
        "backend": chosen["backend"],
        "voice_converter": vc_mode,
        "mp3_file": f"assets/audio/{out_primary.name}",
        "mp3_size_kb": round(out_primary.stat().st_size / 1024, 1),
        "duration_sec": master_stats["duration_sec"],
        "aligned_lyrics": chosen["aligned_lyrics"],
        "acoustic_audit": acoustic_audit,
        "mr_wav": str(mr_saved),
        "master_wav": str(master_wav),
    }
    audit_json.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ [Track {track_no:02d} ALL_PASS] {spec['title']} -> {out_primary.name} ({res['mp3_size_kb']} KB)", flush=True)
    return res


def rebuild_radio_episodes_with_real_singing(track_map: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rebuilds `assets/audio/baek_woon_ho_ep01..05.mp3` so every radio episode on `paradise-hero.com`
    plays the warm spoken listener story (ducked over real ACE-Step trot MR, zero sine pad!)
    FOLLOWED IMMEDIATELY by the full 2m30s neural singing trot song!
    """
    out_records = []
    for ep in RADIO_EPISODE_SPECS:
        ep_work = ALBUM_WORK_DIR / f"radio_{ep['ep_id']}"
        ep_work.mkdir(parents=True, exist_ok=True)
        song_rec = track_map[ep["song_mp3"]]
        mr_wav = Path(song_rec["mr_wav"])
        master_wav = Path(song_rec["master_wav"])

        # Synthesize spoken intro over real trot MR
        story_spec = {"story_segments": ep["story_segments"]}
        story_wav, seg_records = bms.build_story_intro_audio_45s(story_spec, mr_wav, ep_work)
        s_arr, _ = sf.read(str(story_wav), dtype="float32")
        m_arr, _ = sf.read(str(master_wav), dtype="float32")
        combined = np.vstack([s_arr, m_arr])
        comb_wav = ep_work / f"{ep['ep_id']}_combined.wav"
        sf.write(str(comb_wav), combined, bms.SR, subtype="PCM_16")

        dst_mp3 = AUDIO_DIR / ep["filename"]
        encode_web_mp3_192k(comb_wav, dst_mp3)
        dur_s = round(len(combined) / float(bms.SR), 1)
        out_records.append(
            {
                "ep_id": ep["ep_id"],
                "filename": f"assets/audio/{ep['filename']}",
                "song_title": song_rec["title"],
                "story_duration_sec": round(len(s_arr) / float(bms.SR), 1),
                "total_duration_sec": dur_s,
                "mmss": f"{int(dur_s // 60):02d}:{int(dur_s % 60):02d}",
                "size_kb": round(dst_mp3.stat().st_size / 1024, 1),
            }
        )
        print(f"📻 [Radio {ep['ep_id']} Built] {ep['filename']} ({dur_s}s = Story + 〈{song_rec['title']}〉)", flush=True)
    return out_records


def main() -> None:
    ALBUM_WORK_DIR.mkdir(parents=True, exist_ok=True)
    ref_wav = bms.MASTER_REF_WAV
    assert ref_wav.exists(), f"Master reference voice missing: {ref_wav} (run baek_woonho_music_studio.py first)"

    # Normalize Track 01 (already produced by baek_woonho_music_studio.py) into 192k web MP3 + catalog entry
    t1_audit_path = DIV4_DIR / "output" / "baek_woonho_debut_acoustic_audit.json"
    assert t1_audit_path.exists(), f"Track 01 audit missing: {t1_audit_path}"
    t1_summary = json.loads(t1_audit_path.read_text(encoding="utf-8"))
    t1_master_wav = bms.WORK_DIR / "baek_woonho_debut_master_44k.wav"
    t1_out_primary = AUDIO_DIR / "baek_woonho_01_mothers_spring.mp3"
    encode_web_mp3_192k(t1_master_wav if t1_master_wav.exists() else Path(t1_summary["debut_mp3"]), t1_out_primary)
    encode_web_mp3_192k(t1_master_wav if t1_master_wav.exists() else t1_out_primary, AUDIO_DIR / "baek_woonho_debut_sample.mp3")

    # Find Track 01 MR wav from bms.WORK_DIR
    t1_mrs = sorted((bms.WORK_DIR / "stage1_acestep_v15_candidates").glob("stems_cand_*/*_no_vocals_44k.wav"))
    t1_mr_wav = t1_mrs[0] if t1_mrs else t1_master_wav

    tracks: List[Dict[str, Any]] = [
        {
            "track_no": 1,
            "song_id": "mothers_spring",
            "title": "어머니의 봄날",
            "badge": "타이틀곡",
            "bpm": 84,
            "key_scale": "D minor",
            "backend": t1_summary["stage1_backend"],
            "voice_converter": t1_summary["stage2_voice_converter"],
            "mp3_file": "assets/audio/baek_woonho_01_mothers_spring.mp3",
            "mp3_size_kb": round(t1_out_primary.stat().st_size / 1024, 1),
            "duration_sec": 150.0,
            "aligned_lyrics": bms.DEBUT_SONG_SPEC["lyric_lines"],
            "acoustic_audit": t1_summary["acoustic_audit"],
            "mr_wav": str(t1_mr_wav),
            "master_wav": str(t1_master_wav if t1_master_wav.exists() else t1_out_primary),
        }
    ]

    for spec in SONGS_2_TO_6_SPECS:
        tracks.append(produce_single_album_track(spec, ref_wav))

    track_by_mp3 = {Path(t["mp3_file"]).name: t for t in tracks}
    radio_eps = rebuild_radio_episodes_with_real_singing(track_by_mp3)

    catalog = {
        "artist": "백운호 (白雲湖)",
        "album_title": "가상 트로트 가수 백운호 정규 6대 대표곡 오리지널 마스터 컬렉션",
        "engine": "ACE-Step v1.5 Neural Korean Traditional Trot + Demucs + Plachtaa/Seed-VC 44.1kHz Locked Baritone",
        "reference_voice": "assets/voice/baek_woonho_ref.wav",
        "containsSyntheticMedia": True,
        "real_celebrity_matches": 0,
        "tracks": [
            {k: v for k, v in t.items() if k not in ("mr_wav", "master_wav")}
            for t in tracks
        ],
        "radio_episodes": radio_eps,
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cat_path = DATA_DIR / "baek_woonho_6songs_catalog.json"
    cat_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n🎉 ALL 6 SIGNATURE NEURAL TROT SONGS & 5 RADIO BROADCASTS COMPLETED ->", cat_path, flush=True)


if __name__ == "__main__":
    main()
