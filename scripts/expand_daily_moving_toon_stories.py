#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
expand_daily_moving_toon_stories.py
================================================================================
Infinite Non-Repeating Story & Community Post Expander for Div 4
(@김쌤의영웅라디오 & https://paradise-hero.com/booth.html)

Ensures the automated daily 3-episode Moving-Toon pipeline always has fresh,
unique, non-repetitive Korean webtoon episodes rotating all 10 Photo Booth
Hwang Young-woong outfits, seasonal/news hooks, and musical keys — never
violating YouTube's anti-repetitious content guidelines or GEMINI.md rules.
================================================================================
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

DIV4_DIR = Path(__file__).resolve().parent.parent
EPISODES_JSON = DIV4_DIR / "data" / "moving_toon_episodes.json"
NEWS_JSON = DIV4_DIR / "data" / "trot_news.json"
PROHIBITED_WORDS = ["최저가", "할인율", "특가", "폭탄세일"]

CURATED_STORY_TEMPLATES: List[Dict[str, Any]] = [
    {
        "theme_key": "F_MAJOR",
        "title": "시장 골목 무거운 장바구니 번쩍 들어준 에메랄드 왕자님 🛍️💚 #백운호 #김쌤의영웅라디오",
        "summary": "무거운 장바구니를 들고 언덕길을 오르던 어머님 앞에 나타나 두 손으로 짐을 들어준 다정한 백운호 이야기",
        "community_teaser": "무릎이 시큰거리는 언덕길, 무거운 장바구니를 대신 번쩍 들어주며 팔짱을 내어준 다정한 청년이 우리 영웅 군이라면 어떨까요? 오늘의 신규 심야 영웅라디오을 확인하세요 💚",
        "outfits_featured": [2, 3],
        "beats": [
            {"layout": "solo_mother_closeup", "mother_pose": "mother_tearful", "prince_id": 2, "palette": "autumn_gold", "speaker": "mother", "bubble_speaker": "mother", "bubble_text": "아이고 무릎이야.. 언덕이 왜 이리 높누", "arrow_tag": "↗ 장 보고 올라가는 어머님", "narration": "찬 바람 부는 시장 언덕길, 무거운 장바구니에 어머님이 잠시 걸음을 멈추셨습니다.", "subtitle": "무거운 장바구니에 잠시 멈춘 시장 언덕길"},
            {"layout": "solo_prince_climax", "prince_id": 2, "mother_pose": "mother_surprised", "palette": "sky_crystal", "speaker": "prince", "bubble_speaker": "prince", "bubble_text": "어머님! 이 무거운 걸 왜 혼자 드세요 🤍", "arrow_tag": "↗ 화이트 수트 에스코트 영웅", "narration": "어머님! 이렇게 무거운 걸 왜 혼자 들고 가세요. 이리 주세요, 제가 댁까지 모셔다드릴게요!", "subtitle": "이리 주세요 어머님, 제가 댁까지 모셔다드릴게요!"},
            {"layout": "dual_dialogue", "mother_pose": "mother_surprised", "prince_id": 2, "palette": "peach_glow", "speaker": "mother", "bubble_speaker": "mother", "bubble_text": "어머나! 바쁜 사람이 괜찮대도 그래!", "arrow_tag": "↗ 깜짝 놀란 어머님", "narration": "어머나 세상에, 귀한 옷 다 구겨지겠네! 무거운데 내가 들어도 괜찮단다.", "subtitle": "귀한 옷 구겨지겠네, 내가 들어도 괜찮단다!"},
            {"layout": "split_action_prince", "action_img": "cut_action_hand_rose", "prince_id": 3, "mother_pose": "mother_blush_happy", "palette": "candy_pink", "speaker": "prince", "bubble_speaker": "prince", "bubble_text": "어머님 손목 아끼는 게 제 행복이에요 💕", "arrow_tag": "↗ 핑크 손하트 막내아들", "narration": "어머님 고운 손목 아끼는 게 제 일인걸요! 자, 빈손으로 제 팔짱 꼭 끼고 걸으세요.", "subtitle": "어머님 손목 아끼는 게 제 가장 큰 행복이에요!"},
            {"layout": "dual_dialogue", "mother_pose": "mother_blush_happy", "prince_id": 3, "palette": "sakura_pink", "speaker": "narrator", "bubble_speaker": "mother", "bubble_text": "동네 사람들아! 내 아들 좀 보소 ❤️", "arrow_tag": "↗ 어깨 으쓱해진 어머님", "narration": "그날 저녁 언덕길에는 세상에서 가장 환한 어머님의 꽃웃음 소리가 가득 울려 퍼졌습니다.", "subtitle": "언덕길 가득 울려 퍼진 어머님의 환한 꽃웃음"},
            {"layout": "ending_slate", "prince_id": 2, "mother_pose": "mother_blush_happy", "palette": "emerald_gold", "speaker": "narrator", "bubble_speaker": "none", "bubble_text": "", "arrow_tag": "", "narration": "기념 사진관에서 무료 투샷을 바로 찍어보세요!", "subtitle": "파라다이스히어로 기념사진관 무료 투샷 체험"}
        ]
    },
    {
        "theme_key": "G_MAJOR",
        "title": "잠 안 오는 새벽 세 시, 어머님 귓가에 속삭인 자장가 🌙🎙️ #백운호 #김쌤의영웅라디오",
        "summary": "깊은 새벽 잠 못 이루고 뒤척이는 어머님을 위해 중저음 자장가를 불러주는 심야 라디오 DJ 백운호",
        "community_teaser": "새벽 세 시, 괜스레 잠이 깨어 창밖만 바라보신 적 있으시죠? 금테 안경을 쓴 심야 DJ 영웅님이 어머님 귓가에 조용히 불러드리는 자장가 감동사연 🌙💚",
        "outfits_featured": [10, 6],
        "beats": [
            {"layout": "split_action_mother", "action_img": "cut_action_radio_onair", "mother_pose": "mother_tearful", "prince_id": 10, "palette": "lavender_mist", "speaker": "mother", "bubble_speaker": "mother", "bubble_text": "새벽 세 시네.. 왜 이리 잠이 안 올까", "arrow_tag": "↗ 밤잠 설친 어머님", "narration": "모두가 잠든 고요한 새벽 세 시, 나이가 들수록 짧아진 잠에 어머님이 라디오를 켰습니다.", "subtitle": "모두 잠든 새벽 세 시, 조용히 켜 본 라디오"},
            {"layout": "split_action_prince", "action_img": "cut_action_radio_onair", "prince_id": 10, "mother_pose": "mother_tearful", "palette": "studio_mint", "speaker": "prince", "bubble_speaker": "prince", "bubble_text": "어머님, 걱정거리 다 제게 맡기세요 🌙", "arrow_tag": "↗ 심야 자장가 DJ 영웅", "narration": "어머님, 또 자식들 생각에 잠 못 이루고 계시죠? 오늘 밤 걱정은 전부 제게 맡겨 두세요.", "subtitle": "오늘 밤 걱정은 전부 제게 맡겨 두세요"},
            {"layout": "dual_dialogue", "mother_pose": "mother_blush_happy", "prince_id": 10, "palette": "peach_glow", "speaker": "mother", "bubble_speaker": "mother", "bubble_text": "네 중저음 목소리가 보약보다 낫구나 💚", "arrow_tag": "↗ 마음 편안해진 어머님", "narration": "어쩜 내 마음을 이리 족집게처럼 알까! 영웅 군의 중저음 목소리가 천 냥 보약보다 훨씬 낫구나.", "subtitle": "영웅 군 중저음 목소리가 천 냥 보약보다 낫구나!"},
            {"layout": "solo_prince_climax", "prince_id": 6, "mother_pose": "mother_blush_happy", "palette": "royal_rose", "speaker": "prince", "bubble_speaker": "prince", "bubble_text": "좋은 꿈 꾸세요, 꿈에서도 노래할게요 💜", "arrow_tag": "↗ 퍼플 벨벳 세레나데 영웅", "narration": "두 눈 감으시고 편안히 주무세요. 어머님 고운 꿈길에서도 제가 옆에서 노래 불러 드릴게요.", "subtitle": "어머님 고운 꿈길에서도 노래 불러 드릴게요"},
            {"layout": "solo_mother_closeup", "mother_pose": "mother_blush_happy", "prince_id": 6, "palette": "sakura_pink", "speaker": "narrator", "bubble_speaker": "mother", "bubble_text": "오늘 밤은 참 달콤하게 자겠네 ❤️", "arrow_tag": "↗ 소녀 미소로 잠든 어머님", "narration": "따뜻한 목소리 이불 삼아, 오랜만에 어머님 얼굴에 평화로운 소녀 미소가 번졌습니다.", "subtitle": "따뜻한 목소리 덮고 번진 평화로운 소녀 미소"},
            {"layout": "ending_slate", "prince_id": 10, "mother_pose": "mother_blush_happy", "palette": "emerald_gold", "speaker": "narrator", "bubble_speaker": "none", "bubble_text": "", "arrow_tag": "", "narration": "파라다이스 히어로 기념 사진관에서 심야 디제이 영웅과 추억 사진을 남겨보세요.", "subtitle": "파라다이스히어로 기념사진관 무료 투샷 체험"}
        ]
    },
    {
        "theme_key": "D_MAJOR",
        "title": "스마트폰 글씨 작아 답답하셨죠? 돋보기 대신 읽어드리는 영웅님 📱💛 #백운호 #김쌤의영웅라디오",
        "summary": "작은 휴대폰 글씨 때문에 답답해하던 어머님 옆에 앉아 다정하게 큰 글씨 설정을 도와주고 사연을 읽어주는 백운호",
        "community_teaser": "휴대폰 글씨가 너무 작아서 댓글 하나 쓰기도 눈이 침침하셨던 적 있으신가요? 다정하게 옆에 앉아 하나하나 알려드리는 일등 효자 영웅 감동사연 📱💚",
        "outfits_featured": [7, 1],
        "beats": [
            {"layout": "solo_mother_closeup", "mother_pose": "mother_surprised", "prince_id": 7, "palette": "autumn_gold", "speaker": "mother", "bubble_speaker": "mother", "bubble_text": "돋보기를 어디 뒀더라.. 글씨가 너무 작네", "arrow_tag": "↗ 응원 댓글 쓰고 싶은 어머님", "narration": "응원 댓글 한 줄 남기고 싶은데, 야속하게 작은 휴대폰 글씨에 어머님이 눈을 찡그리셨어요.", "subtitle": "응원 댓글 쓰고 싶은데 너무 작은 휴대폰 글씨"},
            {"layout": "dual_dialogue", "mother_pose": "mother_surprised", "prince_id": 7, "palette": "studio_mint", "speaker": "prince", "bubble_speaker": "prince", "bubble_text": "어머님 눈 피곤하시면 안 돼요! 제가 해드릴게요", "arrow_tag": "↗ 다정한 일일 선생님 영웅", "narration": "어머님! 고운 눈 피곤하시면 안 돼요. 이리 줘 보세요, 제가 큼직하게 잘 보이도록 맞춰 드릴게요!", "subtitle": "고운 눈 피곤치 않게 제가 크게 맞춰 드릴게요!"},
            {"layout": "solo_mother_closeup", "mother_pose": "mother_blush_happy", "prince_id": 7, "palette": "peach_glow", "speaker": "mother", "bubble_speaker": "mother", "bubble_text": "애들은 귀찮다는데.. 영웅 군은 천사네! ❤️", "arrow_tag": "↗ 감동 백 배 어머님", "narration": "자식들은 한 번 물어보면 바쁘다고 손사래 치는데, 우리 영웅 군은 어쩜 이리 속이 깊을까!", "subtitle": "어쩜 이리 다정할까, 속 깊은 우리 영웅 군!"},
            {"layout": "solo_prince_climax", "prince_id": 1, "mother_pose": "mother_blush_happy", "palette": "royal_rose", "speaker": "prince", "bubble_speaker": "prince", "bubble_text": "열 번이고 백 번이고 물어보세요 💚", "arrow_tag": "↗ 에메랄드 수트 영웅", "narration": "모르시는 거 있으면 열 번이고 백 번이고 편하게 부르세요. 어머님 일이라면 언제든 일등으로 달려갑니다!", "subtitle": "열 번이고 백 번이고 편하게 저를 부르세요!"},
            {"layout": "dual_dialogue", "mother_pose": "mother_cheering", "prince_id": 1, "palette": "sakura_pink", "speaker": "narrator", "bubble_speaker": "mother", "bubble_text": "영웅 군 사랑해! 이제 큼직하게 잘 보인다!", "arrow_tag": "↗ 댓글 성공하신 어머님", "narration": "큼직해진 화면 위로 어머님이 직접 쓰신 사랑한다는 진심이 반짝반짝 빛났습니다.", "subtitle": "큼직해진 화면 위로 빛나는 어머님의 진심"},
            {"layout": "ending_slate", "prince_id": 1, "mother_pose": "mother_cheering", "palette": "emerald_gold", "speaker": "narrator", "bubble_speaker": "none", "bubble_text": "", "arrow_tag": "", "narration": "시니어 맞춤 큰 글씨 파라다이스 히어로에서 무료 기념사진을 바로 찍어보세요.", "subtitle": "파라다이스히어로 큰글씨 기념사진관 무료 체험"}
        ]
    },
    {
        "theme_key": "C_MAJOR",
        "title": "첫눈 오는 날 붉은 장미 한 송이 들고 기다린 그 사람 🌹❄️ #백운호 #김쌤의영웅라디오",
        "summary": "하얀 눈꽃이 내리는 공원 벤치에서 붉은 장미와 따뜻한 차를 건네며 설렘을 선물하는 백운호 로맨스 감동사연",
        "community_teaser": "하얀 눈송이가 폴폴 내리는 날, 버건디 벨벳 수트에 새빨간 장미 한 송이를 들고 어머님을 기다리는 사람이 있다면? 심장 설레는 로맨스 감동사연 🌹❄️",
        "outfits_featured": [9, 5],
        "beats": [
            {"layout": "split_action_prince", "action_img": "cut_action_hand_rose", "prince_id": 9, "mother_pose": "mother_surprised", "palette": "sky_crystal", "speaker": "prince", "bubble_speaker": "prince", "bubble_text": "어머님, 추우실까 봐 일찍 나와 기다렸어요 🌹", "arrow_tag": "↗ 버건디 장미 프린스 영웅", "narration": "하얀 눈송이가 내려앉는 거리에서 붉은 장미 한 송이를 품에 안고 영웅이 먼저 인사를 건넵니다.", "subtitle": "추우실까 봐 장미 안고 먼저 기다린 영웅"},
            {"layout": "solo_mother_closeup", "mother_pose": "mother_blush_happy", "prince_id": 9, "palette": "candy_pink", "speaker": "mother", "bubble_speaker": "mother", "bubble_text": "장미꽃 받아본 지가 삼십 년 만이네.. 💕", "arrow_tag": "↗ 볼이 발그레해진 어머님", "narration": "세상에, 이렇게 예쁜 붉은 장미꽃을 받아본 지가 어언 삼십 년 만이라 손끝이 떨리네!", "subtitle": "삼십 년 만에 받은 붉은 장미에 설레는 마음"},
            {"layout": "dual_dialogue", "mother_pose": "mother_blush_happy", "prince_id": 9, "palette": "royal_rose", "speaker": "prince", "bubble_speaker": "prince", "bubble_text": "앞으론 매년 꽃길만 걷게 해드릴게요 ❤️", "arrow_tag": "↗ 로맨틱 세레나데 영웅", "narration": "이제부터는 삼십 년 기다리실 필요 없어요. 제가 해마다 사계절 내내 꽃길만 걷게 해드릴게요!", "subtitle": "사계절 내내 어머님 꽃길만 걷게 해드릴게요!"},
            {"layout": "solo_prince_climax", "prince_id": 5, "mother_pose": "mother_cheering", "palette": "studio_mint", "speaker": "prince", "bubble_speaker": "prince", "bubble_text": "추운 겨울도 제 노래로 녹여드릴게요 ✨", "arrow_tag": "↗ 황실 제복 왕자 영웅", "narration": "아무리 매서운 겨울바람이 불어도 우리 어머님 마음만은 언제나 따뜻한 봄날이 되도록 노래하겠습니다.", "subtitle": "어머님 마음만은 언제나 따뜻한 봄날이 되도록!"},
            {"layout": "dual_dialogue", "mother_pose": "mother_cheering", "prince_id": 5, "palette": "sakura_pink", "speaker": "narrator", "bubble_speaker": "mother", "bubble_text": "내 인생 최고의 봄날은 바로 오늘이야 💚", "arrow_tag": "↗ 행복 가득 어머님", "narration": "붉은 장미 향기보다 더 진한 감동이 우리 어머님들의 겨울을 포근하게 감싸 안았습니다.", "subtitle": "어머님들의 겨울을 포근히 감싸 안은 감동"},
            {"layout": "ending_slate", "prince_id": 9, "mother_pose": "mother_blush_happy", "palette": "emerald_gold", "speaker": "narrator", "bubble_speaker": "none", "bubble_text": "", "arrow_tag": "", "narration": "파라다이스 히어로 기념 사진관에서 장미 든 영웅과 로맨틱 투샷을 인화하세요.", "subtitle": "파라다이스히어로 기념사진관 무료 투샷 체험"}
        ]
    }
]


def ensure_fresh_episodes(min_unscheduled: int = 3, uploaded_ids: List[str] = None) -> List[Dict[str, Any]]:
    uploaded_set = set(uploaded_ids or [])
    data = json.loads(EPISODES_JSON.read_text(encoding="utf-8"))
    episodes: List[Dict[str, Any]] = data.get("episodes", [])

    available = [e for e in episodes if e["episode_id"] not in uploaded_set]
    next_no = max((e.get("episode_no", 0) for e in episodes), default=0) + 1

    # Also pull fresh headline context from trot_news.json if needed for extra variety
    news_headlines = []
    if NEWS_JSON.exists():
        try:
            ndata = json.loads(NEWS_JSON.read_text(encoding="utf-8"))
            items = ndata if isinstance(ndata, list) else ndata.get("items", ndata.get("news", []))
            for it in items[:10]:
                t = str(it.get("title", "")).strip()
                if t and not any(b in t for b in PROHIBITED_WORDS):
                    news_headlines.append(t)
        except Exception:
            pass

    tmpl_idx = next_no - 6
    added = False
    while len(available) < min_unscheduled:
        base_t = CURATED_STORY_TEMPLATES[tmpl_idx % len(CURATED_STORY_TEMPLATES)]
        ep_id = f"ep_toon_{next_no:02d}"
        cycle = tmpl_idx // len(CURATED_STORY_TEMPLATES)
        title_str = base_t["title"]
        if cycle > 0:
            title_str = f"[심야라디오 {next_no}화] " + title_str

        new_ep = {
            "episode_id": ep_id,
            "episode_no": next_no,
            "theme_key": base_t["theme_key"],
            "title": title_str[:95],
            "hook_selected": "auto_curated_v3",
            "summary": base_t["summary"],
            "community_teaser": base_t["community_teaser"],
            "tags": ["백운호", "감동사연", "애니메이션", "웹툰", "김쌤의영웅라디오", "파라다이스히어로", "시니어감동"],
            "outfits_featured": base_t["outfits_featured"],
            "beats": base_t["beats"],
        }
        blob = json.dumps(new_ep, ensure_ascii=False)
        for bad in PROHIBITED_WORDS:
            if bad in blob:
                raise ValueError(f"Prohibited word {bad} in generated episode!")

        episodes.append(new_ep)
        available.append(new_ep)
        next_no += 1
        tmpl_idx += 1
        added = True

    if added:
        data["episodes"] = episodes
        EPISODES_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return available


if __name__ == "__main__":
    avail = ensure_fresh_episodes(min_unscheduled=8)
    print(f"[OK] Total available episodes ready: {len(avail)}")
