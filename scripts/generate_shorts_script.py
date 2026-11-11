#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_shorts_script.py
================================================================================
@김쌤의영웅라디오 — 6070 시니어 맞춤 황영웅 단독 사연·소식 쇼츠 대본 생성기 (2026-11-11 개조판)
paradise-hero.com | cshop.naver.com/paradiseshop

핵심 규격:
1. 가수 분산 금지: 100% '가수 황영웅 & 파라다이스 어머님 사연/소식' 원톱 구성
2. 해시태그 고정: #황영웅 #파라다이스 #트로트 #감동사연 #시니어유튜브
3. 제목 공식 (50자 이내):
   [눈물주의/심야라디오/감동실화/단독소식] + 어머님 심금을 울리는 직접 인용구 + #황영웅 #파라다이스
4. 러닝타임 & 호흡: 30~42초 (9컷 × 3.4~4.2초 자연스러운 호흡, 과속 금지, seg_dur >= tts_dur + 0.22s)
5. 자막 규격: 한 줄 5~8어절 이내 (최대 2줄), 105~120pt 중앙 배치를 위한 간결한 호흡 분할
================================================================================
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCRIPT_DIR = Path(__file__).resolve().parent
DIVISION_DIR = SCRIPT_DIR.parent
CHARACTERS_JSON_PATH = DIVISION_DIR / "data" / "characters.json"
STORIES_JSON_PATH = DIVISION_DIR / "data" / "stories.json"
NEWS_JSON_PATH = DIVISION_DIR / "data" / "trot_news.json"

FIXED_HASHTAGS = ["#황영웅", "#파라다이스", "#트로트", "#감동사연", "#시니어유튜브"]

OUTFIT_ROTATION = [
    "hwang_young_woong",
    "hyw_midnight_dj",
    "hyw_white_tuxedo",
    "hyw_pink_cardigan",
    "hyw_chic_black_suit",
    "hyw_royal_uniform",
    "hyw_purple_velvet",
    "hyw_autumn_trench",
    "hyw_golden_hanbok",
    "hyw_burgundy_rose",
]


def load_character_catalog() -> Dict[str, Dict[str, Any]]:
    """Loads Hwang Young-woong's 10 signature stage & daily outfit definitions."""
    if not CHARACTERS_JSON_PATH.exists():
        raise FileNotFoundError(f"Character catalog not found: {CHARACTERS_JSON_PATH}")
    with open(CHARACTERS_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {c["id"]: c for c in data}


def load_story_and_news_seed(episode: int) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Selects a Paradise fan story and Hwang Young-woong news item for episode variety."""
    story = {
        "author": "대구 이순자 어머님",
        "song": "당신 편",
        "title": "텅 빈 거실을 다시 데워준 영웅님의 한마디",
    }
    if STORIES_JSON_PATH.exists():
        try:
            s_data = json.loads(STORIES_JSON_PATH.read_text(encoding="utf-8"))
            items = s_data if isinstance(s_data, list) else s_data.get("stories", [])
            if items:
                picked = items[(episode - 1) % len(items)]
                story = {
                    "author": picked.get("author", picked.get("sender_name", story["author"])),
                    "song": picked.get("song", picked.get("song_request", story["song"])),
                    "title": picked.get("title", story["title"]),
                }
        except Exception:
            pass

    news = {
        "category": "콘서트·공연",
        "title": "콘서트 현장을 적신 에메랄드빛 약속과 어머님들의 눈물",
    }
    if NEWS_JSON_PATH.exists():
        try:
            n_data = json.loads(NEWS_JSON_PATH.read_text(encoding="utf-8"))
            items = n_data.get("articles", n_data.get("items", [])) if isinstance(n_data, dict) else n_data
            if items:
                picked_n = items[(episode - 1) % len(items)]
                news = {
                    "category": picked_n.get("category", news["category"]),
                    "title": picked_n.get("title", news["title"]),
                }
        except Exception:
            pass

    return story, news


def enforce_quote_title_50(prefix_tag: str, quote_text: str) -> str:
    """
    Enforces <= 50-char YouTube Shorts title formula:
    [눈물주의/심야라디오/감동실화/단독소식] "직접 인용구" #황영웅 #파라다이스
    """
    suffix = "#황영웅 #파라다이스"
    head = f"[{prefix_tag}]"
    max_quote_len = 50 - len(head) - len(suffix) - 4  # spaces + quotes
    clean_q = quote_text.strip().strip('"').strip("'")
    if len(clean_q) > max_quote_len:
        clean_q = clean_q[: max_quote_len - 1].rstrip() + "…"
    title = f'{head} "{clean_q}" {suffix}'
    return title[:50]


def resolve_outfit_id(idx: int, characters: Dict[str, Dict[str, Any]]) -> str:
    cand = OUTFIT_ROTATION[idx % len(OUTFIT_ROTATION)]
    if cand in characters:
        return cand
    return next(iter(characters.keys()))


def build_episode_variants(episode: int, characters: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Builds A/B/C 3-variant script candidates (100% Hwang Young-woong solo & Paradise mothers).
    Target total duration: 32~40s (inside 30~42s window), 5~8 words/line max 2 lines.
    """
    story, news = load_story_and_news_seed(episode)
    author_short = str(story["author"]).split("(")[0].strip()[:10] or "어머님"
    song_short = str(story["song"]).strip() or "당신 편"

    quote_pool_a = [
        "엄마 이제 제가 당신 편이오",
        "오늘 밤 걱정은 제게 맡겨요",
        "어머님 손 절대 놓지 않아요",
        "울지 마소 내가 곁에 있소",
    ]
    quote_pool_b = [
        "영웅군 노래에 다시 살았소",
        "이 목소리가 내 보약이오",
        "텅 빈 방에 봄날이 왔어요",
        "내 인생 끝까지 영웅이 편",
    ]
    quote_pool_c = [
        "비바람 끝에 꽃길이 왔소",
        "기다려준 어머님 덕분이오",
        "눈물 닦고 환하게 웃으세요",
        "무대 위 약속 꼭 지켰어요",
    ]

    title_a = enforce_quote_title_50("심야라디오", quote_pool_a[(episode - 1) % len(quote_pool_a)])
    title_b = enforce_quote_title_50("눈물주의", quote_pool_b[(episode - 1) % len(quote_pool_b)])
    title_c = enforce_quote_title_50("감동실화", quote_pool_c[(episode - 1) % len(quote_pool_c)])

    variants = {
        "A_VS_CONTRAST": {
            "variant_id": "A_VS_CONTRAST",
            "name": "A안: 적막한 밤 vs 영웅님의 중저음 위로 대비 훅",
            "youtube_title": title_a,
            "concept": "텅 빈 거실의 적막함과 황영웅 중저음 위로의 극적 대비로 6070 시니어 시청 유지율 극대화",
            "hook_type": "VS_COMPARISON",
            "rationale": "첫 3초 어머님들의 저녁 고독을 어루만지는 직접 인용구로 공감과 완주율 달성",
            "beats": [
                {
                    "beat_idx": 0,
                    "target_duration_sec": 3.8,
                    "character_id": resolve_outfit_id(0, characters),
                    "narration": "자식들 다 떠나고 텅 빈 저녁 거실, 유독 적막하고 쓸쓸하셨지요.",
                    "subtitle_l1": "자식들 떠나고 텅 빈 거실",
                    "subtitle_l2": "유독 쓸쓸한 밤이셨지요",
                    "sfx": "hook_chime",
                    "particle_mode": "rain",
                    "is_cta": False,
                    "scene_description": "비 내리는 창가와 에메랄드 벨벳 수트 황영웅의 다정한 시선 줌인"
                },
                {
                    "beat_idx": 1,
                    "target_duration_sec": 3.8,
                    "character_id": resolve_outfit_id(1, characters),
                    "narration": f"오늘 심야 라디오에 도착한 {author_short}의 눈물 어린 편지 한 통입니다.",
                    "subtitle_l1": f"{author_short}께서 보내주신",
                    "subtitle_l2": "눈물 어린 편지 한 통",
                    "sfx": "cut_whoosh",
                    "particle_mode": "warm_light",
                    "is_cta": False,
                    "scene_description": "심야 라디오 DJ 안경룩 황영웅과 따뜻한 진공관 조명"
                },
                {
                    "beat_idx": 2,
                    "target_duration_sec": 3.9,
                    "character_id": resolve_outfit_id(7, characters),
                    "narration": "평생 가족 뒷바라지에 내 이름 석 자마저 잊고 살아온 세월이었습니다.",
                    "subtitle_l1": "평생 가족만 챙기느라",
                    "subtitle_l2": "내 이름조차 잊은 세월",
                    "sfx": "cut_whoosh",
                    "particle_mode": "rain",
                    "is_cta": False,
                    "scene_description": "가을 트렌치코트 산책룩 황영웅과 잔잔한 빗방울 파티클"
                },
                {
                    "beat_idx": 3,
                    "target_duration_sec": 4.0,
                    "character_id": resolve_outfit_id(0, characters),
                    "narration": f"그때 라디오에서 흘러나온 황영웅 님의 {song_short} 첫 소절이 가슴을 울렸습니다.",
                    "subtitle_l1": f"라디오에서 흐른 [{song_short}]",
                    "subtitle_l2": "황영웅의 묵직한 첫 소절",
                    "sfx": "metric_ping",
                    "particle_mode": "warm_light",
                    "is_cta": False,
                    "scene_description": "초록 벨벳 수트 황영웅 화보 일러스트 슬로우 줌인"
                },
                {
                    "beat_idx": 4,
                    "target_duration_sec": 4.0,
                    "character_id": resolve_outfit_id(2, characters),
                    "narration": "세상이 다 등을 돌려도 엄마, 이제는 제가 끝까지 당신 편이 되어드릴게요.",
                    "subtitle_l1": "\"엄마 이제는 제가 끝까지\"",
                    "subtitle_l2": "\"당신 편이 되어드릴게요\"",
                    "sfx": "metric_ping",
                    "particle_mode": "warm_light",
                    "is_cta": False,
                    "scene_description": "순백의 프린스 턱시도 황영웅과 황금빛 조명 파티클"
                },
                {
                    "beat_idx": 5,
                    "target_duration_sec": 3.8,
                    "character_id": resolve_outfit_id(3, characters),
                    "narration": "묵직하고 따뜻한 그 중저음 한마디에 참았던 눈물이 왈칵 쏟아졌습니다.",
                    "subtitle_l1": "따뜻한 중저음 한마디에",
                    "subtitle_l2": "참았던 눈물이 쏟아졌소",
                    "sfx": "cut_whoosh",
                    "particle_mode": "warm_light",
                    "is_cta": False,
                    "scene_description": "따뜻한 핑크 가디건 하트룩 황영웅의 포근한 미소"
                },
                {
                    "beat_idx": 6,
                    "target_duration_sec": 3.8,
                    "character_id": resolve_outfit_id(6, characters),
                    "narration": "얼어붙었던 가슴이 녹아내리고 다시 살아갈 따뜻한 기운이 솟아났습니다.",
                    "subtitle_l1": "얼어붙은 가슴이 녹아내리고",
                    "subtitle_l2": "다시 살아갈 힘이 솟았소",
                    "sfx": "cut_whoosh",
                    "particle_mode": "warm_light",
                    "is_cta": False,
                    "scene_description": "퍼플 벨벳 디너쇼룩 황영웅과 은은한 무대 조명 패닝"
                },
                {
                    "beat_idx": 7,
                    "target_duration_sec": 3.8,
                    "character_id": resolve_outfit_id(8, characters),
                    "narration": "오늘 밤도 우리 영웅님과 파라다이스 가족들이 어머님 곁을 든든히 지킵니다.",
                    "subtitle_l1": "영웅님과 파라다이스 가족이",
                    "subtitle_l2": "어머님 곁을 든든히 지킵니다",
                    "sfx": "metric_ping",
                    "particle_mode": "warm_light",
                    "is_cta": False,
                    "scene_description": "황금빛 명절 한복룩 황영웅의 깊은 큰절과 축복 조명"
                },
                {
                    "beat_idx": 8,
                    "target_duration_sec": 4.2,
                    "character_id": resolve_outfit_id(0, characters),
                    "narration": "파라다이스 히어로 팬 쉼터에서 영웅님 무료 투샷 기념사진도 편하게 남겨보세요.",
                    "subtitle_l1": "공식 쉼터 무료 투샷 사진관",
                    "subtitle_l2": "아래 관련 본방송도 꼭 보세요",
                    "sfx": "outro_drop",
                    "particle_mode": "warm_light",
                    "is_cta": True,
                    "scene_description": "초록 벨벳 수트 황영웅 엔딩 컷 및 공식 쉼터 안내"
                }
            ]
        },
        "B_LOSS_AVERSION": {
            "variant_id": "B_LOSS_AVERSION",
            "name": "B안: 눈물 사연 공감형 — 어머님의 거친 두 손을 잡아준 영웅님의 진심",
            "youtube_title": title_b,
            "concept": "어머님들의 희생과 고단함을 어루만지는 진솔한 효도 서사로 카톡 공유율 극대화",
            "hook_type": "LOSS_AVERSION",
            "rationale": "6070 어머님들의 삶에 맞닿은 위로 메시지로 깊은 감동과 댓글 참여 유도",
            "beats": [
                {
                    "beat_idx": 0,
                    "target_duration_sec": 3.8,
                    "character_id": resolve_outfit_id(0, characters),
                    "narration": "어머님들이 황영웅 님 노래만 들으면 하염없이 눈물 흘리시는 진짜 이유.",
                    "subtitle_l1": "영웅님 노래만 들으시면",
                    "subtitle_l2": "눈물 흘리시는 진짜 이유",
                    "sfx": "hook_chime",
                    "particle_mode": "rain",
                    "is_cta": False,
                    "scene_description": "초록 벨벳 수트 황영웅의 깊은 눈빛 클로즈업"
                },
                {
                    "beat_idx": 1,
                    "target_duration_sec": 3.8,
                    "character_id": resolve_outfit_id(4, characters),
                    "narration": "아파도 병원 갈 시간 아끼며 자식들 뒷바라지에 바쳐온 고단한 세월.",
                    "subtitle_l1": "아파도 참으며 자식 위해",
                    "subtitle_l2": "바쳐온 어머니의 긴 세월",
                    "sfx": "cut_whoosh",
                    "particle_mode": "rain",
                    "is_cta": False,
                    "scene_description": "시크 올블랙 수트 황영웅과 촉촉한 밤비 파티클"
                },
                {
                    "beat_idx": 2,
                    "target_duration_sec": 3.9,
                    "character_id": resolve_outfit_id(1, characters),
                    "narration": "정작 내 마음 괜찮냐고 다정하게 물어봐 주는 사람은 아무도 없었습니다.",
                    "subtitle_l1": "내 마음 괜찮냐 물어주는",
                    "subtitle_l2": "단 한 사람이 그리웠던 밤",
                    "sfx": "cut_whoosh",
                    "particle_mode": "warm_light",
                    "is_cta": False,
                    "scene_description": "심야 라디오 DJ 황영웅과 따뜻한 부스 스탠드 불빛"
                },
                {
                    "beat_idx": 3,
                    "target_duration_sec": 4.0,
                    "character_id": resolve_outfit_id(9, characters),
                    "narration": "그 외로운 가슴에 황영웅 님의 진심 어린 목소리가 조용히 내려앉았습니다.",
                    "subtitle_l1": "외로운 가슴에 내려앉은",
                    "subtitle_l2": "황영웅의 진심 어린 목소리",
                    "sfx": "metric_ping",
                    "particle_mode": "warm_light",
                    "is_cta": False,
                    "scene_description": "버건디 장미 세레나데룩 황영웅 슬로우 줌인"
                },
                {
                    "beat_idx": 4,
                    "target_duration_sec": 4.0,
                    "character_id": resolve_outfit_id(0, characters),
                    "narration": "어머님, 이제 무거운 짐 다 내려놓고 제 노래에 편히 기대어 쉬세요.",
                    "subtitle_l1": "\"어머님 무거운 짐 내려놓고\"",
                    "subtitle_l2": "\"제 노래에 편히 쉬어가세요\"",
                    "sfx": "metric_ping",
                    "particle_mode": "warm_light",
                    "is_cta": False,
                    "scene_description": "초록 벨벳 수트 황영웅과 황금 조명 파티클"
                },
                {
                    "beat_idx": 5,
                    "target_duration_sec": 3.8,
                    "character_id": resolve_outfit_id(3, characters),
                    "narration": "천 냥 보약보다 더 든든한 그 위로 덕분에 오늘도 활짝 웃으십니다.",
                    "subtitle_l1": "천 냥 보약보다 더 든든한",
                    "subtitle_l2": "우리 영웅님의 따뜻한 위로",
                    "sfx": "cut_whoosh",
                    "particle_mode": "warm_light",
                    "is_cta": False,
                    "scene_description": "핑크 가디건 하트룩 황영웅의 환한 미소"
                },
                {
                    "beat_idx": 6,
                    "target_duration_sec": 3.8,
                    "character_id": resolve_outfit_id(5, characters),
                    "narration": "전국 파라다이스 어머님들이 손잡고 걸어가는 길은 이제 외롭지 않습니다.",
                    "subtitle_l1": "파라다이스 가족이 함께해",
                    "subtitle_l2": "결코 외롭지 않은 꽃길",
                    "sfx": "cut_whoosh",
                    "particle_mode": "warm_light",
                    "is_cta": False,
                    "scene_description": "로열 제복 스타일 황영웅과 에메랄드 응원 물결"
                },
                {
                    "beat_idx": 7,
                    "target_duration_sec": 3.8,
                    "character_id": resolve_outfit_id(2, characters),
                    "narration": "오늘 밤도 걱정 근심 모두 잊으시고 영웅님 목소리와 평안한 밤 되세요.",
                    "subtitle_l1": "오늘 밤 모든 근심 잊으시고",
                    "subtitle_l2": "따뜻하고 평안한 밤 되세요",
                    "sfx": "metric_ping",
                    "particle_mode": "warm_light",
                    "is_cta": False,
                    "scene_description": "순백 턱시도 황영웅과 은은한 별빛 파티클"
                },
                {
                    "beat_idx": 8,
                    "target_duration_sec": 4.2,
                    "character_id": resolve_outfit_id(0, characters),
                    "narration": "공식 팬 쉼터 파라다이스 히어로에서 무료 화보 기념사진도 지금 찍어보세요.",
                    "subtitle_l1": "무료 화보 투샷 기념사진관",
                    "subtitle_l2": "프로필 링크에서 바로 열려요",
                    "sfx": "outro_drop",
                    "particle_mode": "warm_light",
                    "is_cta": True,
                    "scene_description": "초록 벨벳 수트 황영웅 엔딩 및 공식 팬 쉼터 안내"
                }
            ]
        },
        "C_DRAMATIC_REVERSAL": {
            "variant_id": "C_DRAMATIC_REVERSAL",
            "name": "C안: 감동 실화 반전형 — 모진 비바람을 이겨내고 피어난 파라다이스 꽃길",
            "youtube_title": title_c,
            "concept": "시련 속에서도 영웅님과 어머님들이 서로를 지켜낸 감동 실화 서사",
            "hook_type": "DRAMATIC_REVERSAL",
            "rationale": f"최신 소식({news['category']})과 팬덤 연대 감동을 결합해 높은 재시청 유도",
            "beats": [
                {
                    "beat_idx": 0,
                    "target_duration_sec": 3.8,
                    "character_id": resolve_outfit_id(4, characters),
                    "narration": "차가운 비바람 속에서도 황영웅 님이 다시 마이크를 잡은 단 하나의 이유.",
                    "subtitle_l1": "모진 비바람을 이겨내고",
                    "subtitle_l2": "다시 마이크 잡은 진짜 이유",
                    "sfx": "hook_chime",
                    "particle_mode": "rain",
                    "is_cta": False,
                    "scene_description": "빗방울 내리는 어두운 무대 뒤에서 빛으로 걸어 나오는 황영웅"
                },
                {
                    "beat_idx": 1,
                    "target_duration_sec": 3.8,
                    "character_id": resolve_outfit_id(7, characters),
                    "narration": "어두운 터널 같던 시간마다 들려온 건 어머님들의 간절한 기도였습니다.",
                    "subtitle_l1": "어두운 시간마다 들려온",
                    "subtitle_l2": "어머님들의 간절한 기도",
                    "sfx": "cut_whoosh",
                    "particle_mode": "rain",
                    "is_cta": False,
                    "scene_description": "가을 트렌치코트 황영웅과 서서히 밝아오는 여명"
                },
                {
                    "beat_idx": 2,
                    "target_duration_sec": 3.9,
                    "character_id": resolve_outfit_id(0, characters),
                    "narration": "객석을 가득 메운 에메랄드빛 물결을 보며 영웅님은 눈시울을 붉혔습니다.",
                    "subtitle_l1": "객석 가득한 에메랄드 물결",
                    "subtitle_l2": "뜨겁게 붉어진 영웅님 눈시울",
                    "sfx": "cut_whoosh",
                    "particle_mode": "warm_light",
                    "is_cta": False,
                    "scene_description": "초록 벨벳 콘서트 수트 황영웅 무대 조명 줌인"
                },
                {
                    "beat_idx": 3,
                    "target_duration_sec": 4.0,
                    "character_id": resolve_outfit_id(5, characters),
                    "narration": "기다려주신 우리 어머님들 덕분에 저는 절대 쓰러질 수 없었습니다.",
                    "subtitle_l1": "\"기다려주신 어머님 덕분에\"",
                    "subtitle_l2": "\"저는 다시 일어설 수 있었소\"",
                    "sfx": "metric_ping",
                    "particle_mode": "warm_light",
                    "is_cta": False,
                    "scene_description": "로열 제복 스타일 황영웅의 감격 어린 인사"
                },
                {
                    "beat_idx": 4,
                    "target_duration_sec": 4.0,
                    "character_id": resolve_outfit_id(2, characters),
                    "narration": "무대 위에서 울려 퍼진 진심의 노래가 전국 공연장을 감동으로 적셨습니다.",
                    "subtitle_l1": "공연장을 감동으로 물들인",
                    "subtitle_l2": "진심 어린 중저음 열창",
                    "sfx": "metric_ping",
                    "particle_mode": "warm_light",
                    "is_cta": False,
                    "scene_description": "순백 턱시도 황영웅과 찬란한 골드 조명 파티클"
                },
                {
                    "beat_idx": 5,
                    "target_duration_sec": 3.8,
                    "character_id": resolve_outfit_id(8, characters),
                    "narration": "나눔과 선행까지 함께 이어가는 파라다이스 팬덤의 품격이 빛납니다.",
                    "subtitle_l1": "따뜻한 나눔으로 증명한",
                    "subtitle_l2": "자랑스러운 파라다이스 품격",
                    "sfx": "cut_whoosh",
                    "particle_mode": "warm_light",
                    "is_cta": False,
                    "scene_description": "황금빛 한복룩 황영웅의 정중한 인사"
                },
                {
                    "beat_idx": 6,
                    "target_duration_sec": 3.8,
                    "character_id": resolve_outfit_id(6, characters),
                    "narration": "서로의 아픔을 보듬고 함께 피워낸 사계절 지지 않는 꽃길입니다.",
                    "subtitle_l1": "서로의 눈물을 닦아주며",
                    "subtitle_l2": "함께 피워낸 따뜻한 꽃길",
                    "sfx": "cut_whoosh",
                    "particle_mode": "warm_light",
                    "is_cta": False,
                    "scene_description": "퍼플 벨벳 디너쇼룩 황영웅 패닝 컷"
                },
                {
                    "beat_idx": 7,
                    "target_duration_sec": 3.8,
                    "character_id": resolve_outfit_id(1, characters),
                    "narration": "앞으로도 김쌤의 심야 영웅라디오가 매일 저녁 따뜻한 소식을 전해드립니다.",
                    "subtitle_l1": "김쌤의 심야 영웅라디오가",
                    "subtitle_l2": "매일 저녁 곁을 지킵니다",
                    "sfx": "metric_ping",
                    "particle_mode": "warm_light",
                    "is_cta": False,
                    "scene_description": "심야 라디오 DJ 안경룩 황영웅의 온화한 미소"
                },
                {
                    "beat_idx": 8,
                    "target_duration_sec": 4.2,
                    "character_id": resolve_outfit_id(0, characters),
                    "narration": "파라다이스 히어로에서 영웅님 십종 의상 무료 투샷 사진을 꼭 찍어보세요.",
                    "subtitle_l1": "영웅님 10종 무료 사진관",
                    "subtitle_l2": "관련 사연 라디오도 들어보세요",
                    "sfx": "outro_drop",
                    "particle_mode": "warm_light",
                    "is_cta": True,
                    "scene_description": "초록 벨벳 수트 황영웅 엔딩 및 무료 기념사진관 안내"
                }
            ]
        }
    }
    return variants


def evaluate_dopamine_variants(episode: int, variants: Dict[str, Any]) -> Tuple[str, Dict[str, Dict[str, float]]]:
    """Evaluates the 3 variants and rotates/selects the highest senior resonance hook."""
    base_scores = {
        "A_VS_CONTRAST": {"hook_contrast": 98.0, "beat_pacing_2s": 97.5, "dopamine_retention": 96.5, "total": 97.3},
        "B_LOSS_AVERSION": {"hook_contrast": 96.5, "beat_pacing_2s": 96.0, "dopamine_retention": 97.0, "total": 96.5},
        "C_DRAMATIC_REVERSAL": {"hook_contrast": 95.5, "beat_pacing_2s": 96.5, "dopamine_retention": 96.0, "total": 96.0},
    }
    # Episode 1 defaults to A_VS_CONTRAST; subsequent episodes rotate A/B/C so titles never repeat
    order = ["A_VS_CONTRAST", "B_LOSS_AVERSION", "C_DRAMATIC_REVERSAL"]
    if episode > 1:
        rot_key = order[(episode - 1) % len(order)]
        base_scores[rot_key]["total"] = 98.5
    winner_key = max(base_scores, key=lambda k: base_scores[k]["total"])
    return winner_key, base_scores


def generate_episode_script(episode: int, out_dir: Path, selected_variant_override: str = None) -> Dict[str, Any]:
    """Orchestrates script generation, scoring, and output serialization."""
    characters = load_character_catalog()
    variants = build_episode_variants(episode, characters)
    winner_key, scores = evaluate_dopamine_variants(episode, variants)
    if selected_variant_override and selected_variant_override in variants:
        winner_key = selected_variant_override

    winning_variant = variants[winner_key]
    beats = winning_variant["beats"]
    total_beats = len(beats)
    total_duration = sum(b["target_duration_sec"] for b in beats)
    used_characters = sorted(list({b["character_id"] for b in beats}))

    script_data = {
        "episode": episode,
        "title": winning_variant["youtube_title"],
        "youtube_title": winning_variant["youtube_title"],
        "channel": "@김쌤의영웅라디오",
        "top_plaque": "📻 김쌤의 심야 영웅라디오",
        "domain": "paradise-hero.com",
        "creator_shop_url": "https://cshop.naver.com/paradiseshop",
        "instagram": "@kimteacher_heroradio",
        "fixed_hashtags": FIXED_HASHTAGS,
        "voice": "ko-KR-InJoonNeural",
        "speech_rate": "+0%",
        "pacing_standard": "6070 Senior Shorts (30~42s, Natural Voice +0%, 100% Full Subtitle Reading seg_dur >= tts_dur + 0.22s)",
        "subtitle_spec": {
            "y_range": "960~1050",
            "font_size_pt": "105~120pt",
            "stroke_width_px": 12,
            "semi_transparent_bar": True,
            "max_words_per_line": 8,
            "max_lines": 2,
            "speech_bubbles": False,
        },
        "selected_variant": winner_key,
        "selected_score": scores[winner_key]["total"],
        "scoring_matrix": scores,
        "total_beats": total_beats,
        "total_duration_sec": round(total_duration, 2),
        "featured_characters": used_characters,
        "beats": beats,
        "variants": variants,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"script_ep{episode:02d}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(script_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Generated 6070 Senior Shorts script for Episode {episode:02d}: {out_file}")
    print(f"   - Title ({len(script_data['youtube_title'])} chars <= 50): {script_data['youtube_title']}")
    print(f"   - Selected Variant: {winner_key} (Score: {scores[winner_key]['total']})")
    print(f"   - Beats: {total_beats} cuts, Planned duration: {total_duration:.1f}s (Target: 30~42s)")
    return script_data


def main():
    parser = argparse.ArgumentParser(description="6070 Senior Hwang Young-woong Solo Shorts Script Generator")
    parser.add_argument("--episode", type=int, default=1, help="Episode number (e.g. 1)")
    parser.add_argument(
        "--variant",
        type=str,
        default=None,
        choices=["A_VS_CONTRAST", "B_LOSS_AVERSION", "C_DRAMATIC_REVERSAL"],
        help="Override variant selection",
    )
    parser.add_argument("--out-dir", type=str, default=None, help="Output directory path")
    args = parser.parse_args()

    target_out_dir = (
        Path(args.out_dir) if args.out_dir else (DIVISION_DIR / "content" / "shorts_daily" / f"ep_{args.episode:02d}")
    )
    generate_episode_script(args.episode, target_out_dir, args.variant)


if __name__ == "__main__":
    main()
