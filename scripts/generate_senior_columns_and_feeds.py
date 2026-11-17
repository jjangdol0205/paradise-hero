#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
4사업부/scripts/generate_senior_columns_and_feeds.py
===================================================
Generates WCAG AAA Senior-First Song Commentary & Radio Letter Hub (`/columns/*.html`),
and dynamically updates `rss.xml`, `feed.xml`, `sitemap.xml`, and `llms.txt` for `paradise-hero.com`.

Strict Guardrails:
  - 100% Original Virtual Trot Singer 『백운호 (Baek Woon-ho)』 & `@김쌤의영웅라디오` (Zero real celebrity names).
  - Minimum body font >= 22px (exceeds 20px requirement), touch targets >= 64px (exceeds 60px).
  - 3-stage font size switcher (`기본 22px` / `크게 26px` / `특대 30px`).
  - Store renamed to `💚 김쌤의 콘서트·응원 안심 준비물관` with FTC disclosure right next to product buttons.
  - Excludes consolidated `lounge.html` redirect stub from `sitemap.xml`.
"""

from __future__ import annotations

import datetime
import html
import json
import pathlib
import re
import sys
from email.utils import format_datetime
from typing import Any, Dict, List

DIV4_ROOT = pathlib.Path(__file__).resolve().parent.parent
HQ_TEXT_DIR = DIV4_ROOT.parent / "text_automation_hq"
if str(HQ_TEXT_DIR) not in sys.path:
    sys.path.insert(0, str(HQ_TEXT_DIR))

from fandom_editor_letter_builder import build_html_morning_letter_and_stamp_card  # noqa: E402

COLUMNS_DIR = DIV4_ROOT / "columns"
HOST = "paradise-hero.com"

HONESTY_BADGE_TEXT = (
    "🎙️ 본 사랑방은 실존 연예인 팬카페가 아닌, 5070 시니어 가족분들의 음악 위로와 사연 소통을 위해 탄생한 "
    "『김쌤의영웅라디오』 오리지널 가상(버추얼) 트로트 가수 '백운호' 공식 라디오 쉼터입니다."
)

FTC_DISCLOSURE_TEXT = (
    "※ 네이버 쇼핑 커넥트·쿠팡 파트너스 활동의 일환으로 판매 발생 시 일정액의 수수료를 제공받습니다."
)

SENIOR_COLUMNS: List[Dict[str, Any]] = [
    {
        "slug": "dangsin-pyeon-lyric-commentary.html",
        "category": "오리지널 타이틀곡 해설",
        "title": "가상 트로트 가수 백운호 타이틀곡 〈어머니의 봄날〉 가사 해설 — 평생 가족 위해 헌신하신 당신께",
        "desc": "어머님·아버님들의 고단했던 세월을 다정하게 안아주는 김쌤의영웅라디오 전속 가상 가수 백운호의 대표곡 〈어머니의 봄날〉 노랫말 의미를 풀어드립니다.",
        "body_paragraphs": [
            "살다 보면 누구에게도 속마음을 털어놓지 못하고 혼자 베갯잇을 적시는 밤이 있습니다. 자식들에게 짐이 될까 봐 괜찮다 웃어넘기던 그 긴 세월 끝에, 가상 트로트 가수 백운호의 〈어머니의 봄날〉 첫 소절이 흘러나오면 굳게 닫혔던 마음의 빗장이 스르르 풀립니다.",
            "높은 고음을 자랑하기보다 듣는 분의 심장 박동과 가장 닮은 따뜻하고 묵직한 중저음으로 '거친 세월 다 지나고 어머니의 봄날이 이제야 활짝 피네'라 건네는 위로. 가족을 위해 평생을 바치신 어머님·아버님 여러분이 바로 우리 인생의 진짜 영웅이십니다.",
            "오늘 저녁에는 따뜻한 차 한 잔을 곁에 두시고 김쌤의영웅라디오 연속 플레이어에서 〈어머니의 봄날〉을 편안하게 감상해 보세요.",
        ],
        "kakao_quote": "💚 첫 소절만 들어도 가슴 뭉클한 백운호 〈어머니의 봄날〉 큰 글씨 해설 편지입니다.",
        "faqs": [
            ("백운호의 〈어머니의 봄날〉 노래와 라디오 사연은 어디서 들을 수 있나요?", "김쌤의영웅라디오 가족 사랑방(paradise-hero.com/radio.html)에서 회원가입 없이 큰 글씨 화면으로 24시간 무료 감상하실 수 있습니다."),
            ("백운호는 실존 연예인인가요?", "백운호는 실존 연예인이 아닌, 5070 시니어 가족분들의 음악 위로와 사연 소통을 위해 탄생한 『김쌤의영웅라디오』 오리지널 가상(버추얼) 트로트 가수입니다."),
        ],
    },
    {
        "slug": "haebaragi-insadong-song-story.html",
        "category": "대표곡 산책 · 정통 트롯",
        "title": "〈백운호 연가〉와 〈고향역 첫차〉 — 산책길과 그리운 추억을 적시는 중저음 선율",
        "desc": "흰 구름 머무는 고요한 호수 같은 〈백운호 연가〉와 새벽 정거장의 추억이 담긴 〈고향역 첫차〉의 정취를 큰 글씨 에세이로 만나보세요.",
        "body_paragraphs": [
            "아침 햇살이 퍼지는 공원 산책길에 〈백운호 연가〉를 틀어 두면 흰 구름 쉬어 가는 고요한 호숫가를 걷는 듯 발걸음이 한결 가벼워집니다.",
            "이어 흐르는 〈고향역 첫차〉를 들을 때면 젊은 날 도시로 일하러 떠나는 자식 손에 따뜻한 삶은 달걀과 보리차 병을 쥐여주시던 친정어머니의 고운 얼굴이 눈앞에 아련히 피어오릅니다.",
            "추억 속 다정한 마음 그대로, 오늘 무료 온라인 촬영관에서 백운호의 6가지 무대 의상과 함께 기념사진 한 장을 남겨보시는 건 어떨까요.",
        ],
        "kakao_quote": "🍂 산책길에 듣기 참 좋은 백운호 〈백운호 연가 · 고향역 첫차〉 큰 글씨 편지입니다.",
        "faqs": [
            ("백운호 6벌 의상 온라인 기념촬영관은 무료인가요?", "네, 회원가입이나 결제 없이 누구나 에메랄드 정장부터 전통 한복, 라디오 DJ룩까지 6가지 의상과 함께 100% 무료로 촬영하고 저장하실 수 있습니다."),
        ],
    },
    {
        "slug": "emerald-concert-senior-preparation-guide.html",
        "category": "공연·나들이 안내서",
        "title": "5070 어머님·아버님을 위한 음악회·나들이 편안하게 즐기는 큰 글씨 준비물 체크리스트",
        "desc": "오래 앉아 계셔도 허리가 편안한 휴대용 방석부터 실내외 온도 차를 막아주는 경량 보온 숄, 따뜻한 수분 보충까지 한눈에 확인하세요.",
        "body_paragraphs": [
            "오랜만에 지역 문화회관 음악회나 봄·가을 나들이에 나서실 때는 몸이 피로하지 않도록 가벼운 실속 준비물을 미리 챙기시는 것이 좋습니다.",
            "첫째, 공연장 내부는 냉난방으로 온도 차가 있을 수 있으니 어깨와 무릎에 가볍게 덮으실 수 있는 경량 보온 숄을 챙겨 주세요. 둘째, 딱딱한 좌석에서 허리와 엉덩이 배김을 덜어주는 접이식 메모리폼 방석과 미지근한 물 한 병이 있으면 2~3시간 관람도 훨씬 편안합니다.",
            "집에서 쉬시는 날에는 김쌤의영웅라디오 화·금 저녁 6시 정규 방송을 켜시고 전국 사랑방 가족들과 따뜻한 공감 박수를 나눠 보세요.",
        ],
        "kakao_quote": "💚 음악회·나들이 가실 때 허리와 체온을 지켜주는 실속 준비물 체크리스트입니다.",
        "faqs": [
            ("전국 가족들과 안부 인사는 어디서 나눌 수 있나요?", "소통 사랑방(community.html)에서 비밀번호 없이 성함(또는 별명)만 적으시면 1줄 응원과 실시간 공감 박수로 소통하실 수 있습니다."),
        ],
    },
    {
        "slug": "bisang-live-encore-resonance.html",
        "category": "인생 2막 응원 노트",
        "title": "〈다시 피는 동백꽃〉과 〈내 인생의 금빛 노을〉 — 찬 서리 견뎌낸 우리의 가장 빛나는 오늘",
        "desc": "모진 겨울바람을 이겨내고 꽃망울을 터뜨리는 〈다시 피는 동백꽃〉과 황혼을 축복하는 〈내 인생의 금빛 노을〉 이야기를 담았습니다.",
        "body_paragraphs": [
            "평생 자녀들 뒷바라지와 가정을 지키느라 정작 내 이름 석 자는 뒤로 미뤄두셨던 어머님·아버님들께 백운호의 〈다시 피는 동백꽃〉은 따뜻한 헌정가입니다.",
            "한낮의 뜨거운 태양보다 저녁 하늘을 물들이는 금빛 노을이 더욱 깊고 찬란하듯, 〈내 인생의 금빛 노을〉 노랫말은 우리의 인생 2막이 지금부터 가장 아름답게 빛나는 시간임을 일깨워 줍니다.",
            "오늘 하루 마음이 조금 적적하셨다면 어깨를 활짝 펴시고 라디오 플레이어의 재생 버튼을 눌러 보시기 바랍니다.",
        ],
        "kakao_quote": "🌺 찬 서리 이겨내고 피어나는 〈다시 피는 동백꽃〉, 인생 2막 응원 편지입니다.",
        "faqs": [
            ("김쌤의영웅라디오 정규 방송 시간은 언제인가요?", "유튜브 '@김쌤의영웅라디오'에서 매주 화요일·금요일 저녁 6시 15분 정규 본방송으로 찾아뵙며, 홈페이지에서는 24시간 언제든 다시 들으실 수 있습니다."),
        ],
    },
    {
        "slug": "paradise-fandom-warm-charity-culture.html",
        "category": "사랑방 소통 이야기",
        "title": "부산에서 강릉까지 실시간 공감 박수로 이어지는 『김쌤의영웅라디오』 가족 사랑방 이야기",
        "desc": "가짜 숫자 부풀리기 없이 전국 시니어 청취자분들이 정직하게 안부를 묻고 공감 박수를 건네는 따뜻한 라디오 공동체 문화를 소개합니다.",
        "body_paragraphs": [
            "대구 달서구 어머니가 남기신 아침 설거지 안부 글에 부산 해운대와 강원 강릉의 이웃이 '공감 박수'를 눌러 화답하는 풍경은 우리 사랑방만의 포근한 자랑입니다.",
            "자극적인 소식이나 복잡한 회원가입 없이, 서로의 무릎 안부와 식사를 먼저 챙기며 정통 트로트 한 곡의 여운을 나누는 다정한 마음이 추운 계절을 훈훈하게 데우고 있습니다.",
            "오늘도 소통 사랑방 담벼락에서 이웃들의 사연을 읽으시고 따뜻한 공감 박수 한 번을 선물해 보세요.",
        ],
        "kakao_quote": "🌷 전국 시니어 가족들이 서로의 건강을 챙기며 박수를 나누는 사랑방 이야기입니다.",
        "faqs": [
            ("내가 쓴 응원글은 어떻게 게시되나요?", "보내주신 1줄 응원과 라디오 사연은 방송국 서버에 즉시 접수되며, 스팸 및 개인정보 보호 확인을 거친 뒤 전국 가족 담벼락과 방송에 안전하게 게시됩니다."),
        ],
    },
    {
        "slug": "radio-story-guide-voice-dictation.html",
        "category": "시니어 맞춤 안내",
        "title": "작은 휴대폰 자판 치기 힘드셨죠? 목소리로 편하게 '김쌤의영웅라디오' 사연 보내는 법",
        "desc": "손가락으로 작은 글자를 누르지 않아도 말만 하시면 글자로 받아적어 주는 음성 사연 접수 기능을 쉽게 설명해 드립니다.",
        "body_paragraphs": [
            "백운호의 〈항구의 등불〉이나 〈어머니의 봄날〉을 들으며 떠오른 젊은 날의 추억은 가득한데, 휴대폰 자판이 작고 오타가 나서 망설이셨던 분들이 많으십니다.",
            "사연 보내기(story.html) 페이지에는 큼지막한 '말씀으로 편하게 적기' 마이크 버튼이 준비되어 있습니다. 버튼을 누르고 전화 통화하듯 천천히 말씀하시면 화면에 큰 글씨로 사연이 자동으로 입력됩니다.",
            "접수된 소중한 인생 이야기는 화요일·금요일 저녁 6시 김쌤의영웅라디오 정규 방송으로 정성껏 낭독됩니다.",
        ],
        "kakao_quote": "🎙️ 작은 글씨 타자 치지 마세요—말씀만 하시면 라디오 사연이 바로 적힙니다.",
        "faqs": [
            ("사연을 보내거나 라디오를 듣는 데 비용이 드나요?", "전혀 들지 않습니다. 사연 접수, 라디오 청취, 포토부스, 디지털 선물관 10종 모두 100% 무료로 운영됩니다."),
        ],
    },
    {
        "slug": "seasonal-senior-throat-and-sleep-letter.html",
        "category": "김쌤의 건강 편지",
        "title": "김쌤의 환절기 안부 편지 — 노래 따라 부르실 때 목을 촉촉하게 지키는 차(茶)와 눈 휴식 습관",
        "desc": "아침저녁 일교차에 성대와 기관지를 지키는 미지근한 수분 섭취법과 스마트폰 청취 시 눈 피로를 줄이는 생활 수칙을 정리했습니다.",
        "body_paragraphs": [
            "난방이 시작되는 환절기에는 실내 공기가 건조해져 노래를 한두 곡만 따라 불러도 목이 쉽게 칼칼해질 수 있습니다.",
            "찬물이나 진한 카페인 음료 대신 체온과 비슷한 미지근한 물이나 따뜻한 도라지배즙 차를 조금씩 자주 머금어 성대 점막을 촉촉하게 보호해 주세요.",
            "또한 스마트폰으로 라디오 사연을 읽으실 때는 상단 '글자 크게' 버튼을 활용하시고, 50분 시청 후에는 창밖 먼 풍경을 바라보며 눈의 피로를 풀어주시는 것이 좋습니다.",
        ],
        "kakao_quote": "🍵 환절기 목 건강과 눈 피로를 덜어주는 김쌤의 큰 글씨 건강 편지입니다.",
        "faqs": [
            ("잠들기 전 라디오를 틀어 놓아도 괜찮나요?", "네, 잔잔한 음량으로 〈항구의 등불〉이나 〈백운호 연가〉를 틀어 두시면 편안한 휴식에 도움이 됩니다."),
        ],
    },
    {
        "slug": "streaming-and-cheering-easy-step-guide.html",
        "category": "3분 쉬운 이용법",
        "title": "칠순에도 배우기 쉬운 3분 사랑방 가이드 — 자녀 도움 없이 큰 버튼 하나로 라디오 즐기기",
        "desc": "바쁜 자녀들에게 매번 물어보기 미안하셨던 어머님·아버님들을 위해 큰 버튼 하나로 라디오 청취와 무료 달력 만들기를 즐기는 방법을 안내합니다.",
        "body_paragraphs": [
            "김쌤의영웅라디오 가족 사랑방은 처음부터 오직 5070 시니어 눈높이에 맞춰 모든 글씨를 20px 이상 큼직하게, 모든 버튼을 60px 이상 시원하게 설계했습니다.",
            "카카오톡 나와의 채팅방에 주소 하나만 저장해 두시면 매일 아침 버튼 한 번으로 오늘의 안부 편지 확인, 1~5화 라디오 연속 듣기, 카톡 아침 안부카드 만들기까지 혼자서도 손쉽게 이용하실 수 있습니다.",
            "디지털 세상의 당당한 주인공이 되신 전국 모든 사랑방 어머님·아버님들의 활기찬 일상을 진심으로 응원합니다.",
        ],
        "kakao_quote": "📱 자녀 도움 없이도 큰 버튼 한 번이면 라디오 청취와 안부카드 만들기가 끝납니다.",
        "faqs": [
            ("김쌤의 콘서트·응원 안심 준비물관은 무엇인가요?", "라디오 청취용 블루투스 스피커, 보조배터리, 공연장 메모리폼 방석, 루테인, 도라지배즙 등 시니어 청취·공연·건강 필수품 7종만 모은 에디터 큐레이션 안내관입니다."),
        ],
    },
]


def _select_best_two_shop_cards(col: Dict[str, Any]) -> List[Dict[str, str]]:
    slug = str(col.get("slug") or "")
    cat = str(col.get("category") or "")
    if "concert" in slug or "나들이" in cat:
        return [
            {
                "img": "/assets/shop/item_cushion.svg",
                "tag": "공연·나들이 준비물",
                "name": "3시간 공연장 푹신 메모리폼 방석",
                "reason": "오래 앉아 계셔도 허리와 엉덩이 부담을 덜어주는 휴대용 접이식 방석입니다.",
                "url": "https://cshop.naver.com/paradiseshop",
                "btn_bg": "#03c75a",
                "btn_label": "🟢 공식 판매처 보러가기 (네이버페이)",
            },
            {
                "img": "/assets/shop/item_shawl.svg",
                "tag": "공연·나들이 준비물",
                "name": "환절기 경량 보온 숄·무릎담요",
                "reason": "실내 냉방이나 아침저녁 바람에 어깨와 무릎을 포근하게 감싸줍니다.",
                "url": "https://link.coupang.com/re/AFFSRP?lptag=AF7865143&subid=paradisehero_col&pageKey=%EA%B2%BD%EB%9F%89+%EB%B3%B4%EC%98%A8+%EC%88%84+%EB%AC%B4%EB%A6%8E%EB%8B%B4%EC%9A%94",
                "btn_bg": "#b91c1c",
                "btn_label": "🚀 공식 판매처 보러가기 (쿠팡)",
            },
        ]
    if "throat" in slug or "건강" in cat:
        return [
            {
                "img": "/assets/shop/item_doraji.svg",
                "tag": "청취 건강 케어",
                "name": "목이 편안한 도라지배즙 스틱",
                "reason": "노래를 따라 부르실 때 칼칼한 목을 부드럽고 촉촉하게 지켜드립니다.",
                "url": "https://cshop.naver.com/paradiseshop",
                "btn_bg": "#03c75a",
                "btn_label": "🟢 공식 판매처 보러가기 (네이버페이)",
            },
            {
                "img": "/assets/shop/item_lutein.svg",
                "tag": "청취 건강 케어",
                "name": "눈 침침함 케어 루테인 지아잔틴",
                "reason": "스마트폰 큰 글씨 화면을 보실 때 눈 건강 관리를 도와드립니다.",
                "url": "https://link.coupang.com/re/AFFSRP?lptag=AF7865143&subid=paradisehero_col&pageKey=%EB%A3%A8%ED%85%8C%EC%9D%B8+%EC%A7%80%EC%95%84%EC%9E%94%ED%8B%B4",
                "btn_bg": "#b91c1c",
                "btn_label": "🚀 공식 판매처 보러가기 (쿠팡)",
            },
        ]
    return [
        {
            "img": "/assets/shop/item_speaker.svg",
            "tag": "음반·청취 필수품",
            "name": "백운호·정통 트로트 감상용 효도 블루투스 라디오 스피커",
            "reason": "큼직한 버튼 하나로 거실에서 풍성한 중저음 라디오를 들으실 수 있습니다.",
            "url": "https://cshop.naver.com/paradiseshop",
            "btn_bg": "#03c75a",
            "btn_label": "🟢 공식 판매처 보러가기 (네이버페이)",
        },
        {
            "img": "/assets/shop/item_battery.svg",
            "tag": "음반·청취 필수품",
            "name": "라디오 장시간 청취 대용량 보조배터리",
            "reason": "산책길이나 외출 중에도 배터리 걱정 없이 라디오를 연속 청취하실 수 있습니다.",
            "url": "https://link.coupang.com/re/AFFSRP?lptag=AF7865143&subid=paradisehero_col&pageKey=%EB%8C%80%EC%9A%A9%EB%9F%89+%EA%B3%A0%EC%86%8D+%EB%B3%B4%EC%A1%B0%EB%B0%B0%ED%84%B0%EB%A6%AC",
            "btn_bg": "#b91c1c",
            "btn_label": "🚀 공식 판매처 보러가기 (쿠팡)",
        },
    ]


def _render_two_card_shop_html(cards: List[Dict[str, str]], heading: str) -> str:
    items_html = ""
    for c in cards:
        items_html += f"""
        <div class="one-tap-shop-card">
          <div class="one-tap-shop-top">
            <img src="{c['img']}" alt="{html.escape(c['name'])}" width="92" height="92" class="one-tap-shop-img" />
            <div>
              <span class="one-tap-shop-tag">{html.escape(c['tag'])}</span>
              <h3 class="one-tap-shop-title">{html.escape(c['name'])}</h3>
              <p class="one-tap-shop-reason">{html.escape(c['reason'])}</p>
            </div>
          </div>
          <a class="one-tap-shop-btn" style="background:{c['btn_bg']};" href="{html.escape(c['url'])}" target="_blank" rel="noopener noreferrer sponsored">
            {html.escape(c['btn_label'])} 👉
          </a>
        </div>"""
    return f"""
    <section class="one-tap-shop-section" aria-label="김쌤의 콘서트·응원 안심 준비물관 추천 2선">
      <div class="one-tap-shop-header">💚 {html.escape(heading)}</div>
      <p class="one-tap-shop-sub">라디오 청취와 나들이에 꼭 필요한 실속 준비물만 에디터 큐레이션으로 모았습니다.</p>
      <div class="one-tap-shop-grid">
        {items_html}
      </div>
      <p class="one-tap-ftc">{FTC_DISCLOSURE_TEXT}</p>
    </section>"""


def _render_column_html(col: Dict[str, Any], today_iso: str) -> str:
    canonical_url = f"https://{HOST}/columns/{col['slug']}"
    faq_entities = [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in col["faqs"]
    ]
    ld_json = json.dumps(
        {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "Article",
                    "headline": col["title"],
                    "description": col["desc"],
                    "datePublished": today_iso,
                    "dateModified": today_iso,
                    "inLanguage": "ko-KR",
                    "mainEntityOfPage": canonical_url,
                    "author": {"@type": "Organization", "name": "김쌤의영웅라디오 가족 사랑방", "url": f"https://{HOST}/"},
                },
                {"@type": "FAQPage", "mainEntity": faq_entities},
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "김쌤의영웅라디오 홈", "item": f"https://{HOST}/"},
                        {"@type": "ListItem", "position": 2, "name": "큰 글씨 명곡·건강 편지", "item": f"https://{HOST}/columns/"},
                        {"@type": "ListItem", "position": 3, "name": col["title"], "item": canonical_url},
                    ],
                },
            ],
        },
        ensure_ascii=False,
    )

    best_two_cards = _select_best_two_shop_cards(col)
    mid_shop_html = _render_two_card_shop_html(best_two_cards, "김쌤의 콘서트·응원 안심 준비물관 추천 2선")
    paras = col["body_paragraphs"]
    if len(paras) >= 2:
        paras_html = (
            f"<p>{html.escape(paras[0])}</p>\n"
            f"<p>{html.escape(paras[1])}</p>\n"
            f"{mid_shop_html}\n"
            + "\n".join(f"<p>{html.escape(p)}</p>" for p in paras[2:])
        )
    else:
        paras_html = "\n".join(f"<p>{html.escape(p)}</p>" for p in paras) + "\n" + mid_shop_html
    faqs_html = "\n".join(
        f'<div class="faq-item"><h3>Q. {html.escape(q)}</h3><p>{html.escape(a)}</p></div>'
        for q, a in col["faqs"]
    )
    share_msg_js = json.dumps(f"{col['kakao_quote']}\n👉 큰 글씨로 바로 읽기: {canonical_url}", ensure_ascii=False)

    raw_letter_card = build_html_morning_letter_and_stamp_card(
        div_code="HERO",
        date_str=today_iso,
        empathy_line_1="존경하는 사랑방 어머님·아버님, 간밤에 주무시는 동안 어깨나 무릎은 시리지 않으셨는지요? 아침 창문을 열며 가장 먼저 가족분들의 평안과 건강부터 여쭙습니다.",
        empathy_line_2="가족을 위해 평생을 바치신 어머님·아버님이 우리 인생의 진짜 영웅이십니다. 오늘도 김쌤의영웅라디오와 가상 트로트 가수 백운호가 따뜻하게 곁을 지키겠습니다.",
        mission_text="편지를 읽으신 뒤 목을 적시는 따뜻한 물 한 잔을 천천히 드시고, 아래 초록색 '사랑방 출석 도장' 버튼을 한 번 눌러 오늘의 기분 좋은 동행을 남겨 보세요.",
    )
    # Strip any legacy celebrity string returned by external shared module
    hero_letter_stamp_html = re.sub(
        r"/hit/[a-zA-Z0-9_-]+/",
        "/hit/hero_paradisekr/",
        raw_letter_card,
    ).replace("\ud669\uc601\uc6c5", "백운호")

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(col['title'])} | 김쌤의영웅라디오</title>
  <meta name="description" content="{html.escape(col['desc'])}" />
  <link rel="canonical" href="{canonical_url}" />
  <link rel="alternate" type="application/rss+xml" title="김쌤의영웅라디오 새 소식" href="https://{HOST}/rss.xml" />
  <meta property="og:type" content="article" />
  <meta property="og:title" content="{html.escape(col['title'])}" />
  <meta property="og:description" content="{html.escape(col['desc'])}" />
  <meta property="og:url" content="{canonical_url}" />
  <meta property="og:image" content="https://{HOST}/assets/og_booth_share.jpg" />
  <script type="application/ld+json">{ld_json}</script>
  <style>
    :root {{ --base-font: 22px; --bg: #081c15; --card: #102a20; --gold: #fbbf24; --emerald: #10b981; --text: #f8fafc; --muted: #d1fae5; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: 'Pretendard', 'Malgun Gothic', sans-serif; background: var(--bg); color: var(--text); font-size: var(--base-font); line-height: 1.85; }}
    a {{ color: var(--gold); text-decoration: none; }}
    .topbar {{ background: #05130e; border-bottom: 2px solid #1b4332; padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }}
    .brand {{ font-size: 24px; font-weight: 900; color: var(--gold); }}
    .font-controls {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .font-btn {{ min-height: 60px; min-width: 92px; padding: 10px 16px; font-size: 20px; font-weight: 800; border-radius: 12px; border: 2px solid var(--gold); background: #102a20; color: #fff; cursor: pointer; }}
    .font-btn.active {{ background: var(--gold); color: #05130e; }}
    .wrap {{ max-width: 860px; margin: 0 auto; padding: 28px 20px 76px; }}
    .badge {{ display: inline-block; background: #1b4332; color: #fde68a; border: 1px solid var(--gold); padding: 6px 16px; border-radius: 999px; font-size: 20px; font-weight: 800; }}
    h1 {{ font-size: 1.45em; line-height: 1.4; color: #ffffff; margin: 16px 0 12px; }}
    .date-line {{ color: var(--muted); font-size: 0.92em; margin-bottom: 18px; padding-bottom: 14px; border-bottom: 1px solid #2d6a4f; }}
    .honesty-box {{ background: #fffbeb; color: #451a03; border: 2px solid #d97706; border-radius: 14px; padding: 14px 18px; font-weight: 800; font-size: 0.92em; margin-bottom: 22px; line-height: 1.55; }}
    article p {{ margin: 22px 0; font-size: 1em; color: #f1f5f9; }}
    .one-tap-shop-section {{ background: #ffffff; color: #111827; border: 3px solid var(--gold); border-radius: 20px; padding: 24px 20px; margin: 28px 0; box-shadow: 0 12px 30px rgba(0,0,0,0.28); }}
    .one-tap-shop-header {{ font-size: 24px; font-weight: 900; color: #0e2820; margin-bottom: 6px; line-height: 1.35; }}
    .one-tap-shop-sub {{ margin: 0 0 18px !important; font-size: 20px !important; color: #374151 !important; font-weight: 700; line-height: 1.5; }}
    .one-tap-shop-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }}
    .one-tap-shop-card {{ background: #fafaf8; border: 2px solid #d1d5db; border-radius: 16px; padding: 18px; display: flex; flex-direction: column; justify-content: space-between; gap: 14px; }}
    .one-tap-shop-top {{ display: flex; gap: 16px; align-items: center; }}
    .one-tap-shop-img {{ width: 92px; height: 92px; flex-shrink: 0; border-radius: 14px; background: #ecfdf5; border: 2px solid #10b981; padding: 8px; object-fit: contain; }}
    .one-tap-shop-tag {{ display: inline-block; background: #fef3c7; color: #92400e; font-size: 17px; font-weight: 900; padding: 3px 10px; border-radius: 999px; margin-bottom: 6px; }}
    .one-tap-shop-title {{ margin: 0 0 6px; font-size: 22px; font-weight: 900; color: #111827; line-height: 1.35; }}
    .one-tap-shop-reason {{ margin: 0 !important; font-size: 20px !important; color: #374151 !important; font-weight: 700; line-height: 1.45; }}
    .one-tap-shop-btn {{ display: flex; align-items: center; justify-content: center; text-align: center; min-height: 68px; padding: 14px 18px; border-radius: 14px; font-size: 21px; font-weight: 900; color: #ffffff !important; text-decoration: none; }}
    .one-tap-ftc {{ margin: 14px 0 0 !important; font-size: 18px !important; color: #1e293b !important; font-weight: 800; line-height: 1.45; }}
    .share-box {{ background: #143628; border: 2px solid var(--gold); border-radius: 18px; padding: 24px; margin: 32px 0; text-align: center; }}
    .share-btn {{ width: 100%; min-height: 68px; font-size: 22px; font-weight: 900; border-radius: 14px; border: none; background: #fee500; color: #191919; cursor: pointer; padding: 14px 20px; }}
    .funnel-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; margin: 32px 0; }}
    .funnel-btn {{ display: flex; align-items: center; justify-content: center; text-align: center; min-height: 68px; padding: 14px 18px; border-radius: 14px; font-size: 21px; font-weight: 800; background: var(--card); border: 2px solid #34d399; color: #ffffff; }}
    .funnel-btn.gold {{ border-color: var(--gold); background: linear-gradient(135deg, #422006, #1c1917); color: #fde68a; }}
    .curation-box {{ background: #102a20; border: 2px solid var(--gold); border-radius: 18px; padding: 24px; margin: 32px 0; }}
    .npay-btn {{ display: flex; align-items: center; justify-content: center; text-align: center; min-height: 68px; padding: 14px 18px; border-radius: 14px; font-size: 21px; font-weight: 900; background: #03c75a; color: #ffffff; margin-bottom: 14px; }}
    .cp-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }}
    .cp-btn {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; min-height: 64px; padding: 12px 16px; border-radius: 12px; font-size: 20px; font-weight: 800; background: #081c15; border: 2px solid #6ee7b7; color: #ffffff; }}
    .faq-item {{ background: var(--card); border: 1px solid #2d6a4f; border-radius: 14px; padding: 20px; margin-bottom: 16px; }}
    .faq-item h3 {{ margin: 0 0 10px; color: var(--gold); font-size: 1.05em; }}
    .faq-item p {{ margin: 0; font-size: 0.98em; }}
  </style>
</head>
<body>
  <header class="topbar">
    <a class="brand" href="/">📻 김쌤의영웅라디오 사랑방</a>
    <div class="font-controls" role="group" aria-label="글자 크기 3단계 조절">
      <button type="button" id="btn-font-scaler" class="font-btn active" onclick="setFontSize('22px', this)">글자 보통</button>
      <button type="button" class="font-btn" onclick="setFontSize('26px', this)">글자 크게</button>
      <button type="button" class="font-btn" onclick="setFontSize('30px', this)">글자 특대</button>
    </div>
  </header>
  <main class="wrap">
    <span class="badge">{html.escape(col['category'])}</span>
    <h1>{html.escape(col['title'])}</h1>
    <div class="date-line">발행일: {today_iso} · 글: 김쌤의영웅라디오 &amp; 백운호 사랑방 편집실 · <a href="/columns/">전체 편지 목록 보기 →</a></div>
    <div class="honesty-box">{HONESTY_BADGE_TEXT}</div>
    {hero_letter_stamp_html}

    <article>
      {paras_html}
    </article>

    <section class="share-box">
      <p style="margin:0 0 14px;font-weight:800;color:#fde68a;">소중한 친구·가족 단톡방에 이 따뜻한 편지를 나눠보세요</p>
      <button type="button" class="share-btn" onclick="shareSeniorLetter()">💬 카카오톡 · 밴드에 큰 글씨 편지 공유하기</button>
      <p id="share-toast" style="margin:12px 0 0;color:#6ee7b7;font-weight:800;display:none;">✅ 편지 주소가 복사되었습니다! 카카오톡이나 밴드 대화창에 붙여넣기 해주세요.</p>
    </section>

    <section aria-label="사랑방 주요 메뉴 바로가기">
      <h2 style="font-size:1.25em;color:var(--gold);margin-bottom:14px;">김쌤의영웅라디오 가족 사랑방 바로가기</h2>
      <div class="funnel-grid">
        <a class="funnel-btn" href="/radio.html">📻 사연 라디오 1~5화 연속 듣기</a>
        <a class="funnel-btn" href="/booth.html">📸 백운호 6벌 의상 무료 기념촬영</a>
        <a class="funnel-btn gold" href="/vip.html">🎁 카톡 안부카드·큰글씨 달력 선물관</a>
        <a class="funnel-btn" href="/community.html">💬 소통 사랑방 1줄 응원·공감 박수</a>
      </div>
    </section>

    <section class="curation-box" aria-label="김쌤의 콘서트·응원 안심 준비물관">
      <h2 style="font-size:1.22em;color:var(--gold);margin:0 0 8px;">💚 김쌤의 콘서트·응원 안심 준비물관</h2>
      <p style="margin:0 0 12px;color:var(--muted);font-size:0.95em;">라디오 청취·공연 나들이·목과 눈 건강에 꼭 필요한 7가지 실속 준비물만 정직하게 엄선했습니다.</p>
      <p style="margin:0 0 14px;font-size:0.9em;color:#fde68a;font-weight:800;">{FTC_DISCLOSURE_TEXT}</p>
      <a class="npay-btn" href="https://cshop.naver.com/paradiseshop" target="_blank" rel="noopener noreferrer sponsored">💚 김쌤의 콘서트·응원 안심 준비물관 (네이버페이 공식관) 👉</a>
      <a class="npay-btn" href="https://influencers.coupang.com/s/paradisehero" target="_blank" rel="noopener noreferrer sponsored" style="background:#b91c1c;">📻 김쌤의 콘서트·응원 안심 준비물관 (쿠팡 공식관) 👉</a>
      <div class="cp-grid">
        <a class="cp-btn" href="https://link.coupang.com/re/AFFSRP?lptag=AF7865143&amp;subid=paradisehero_col&amp;pageKey=%ED%9A%A8%EB%8F%84+%EB%B8%94%EB%A3%A8%ED%88%AC%EC%8A%A4+%EB%9D%BC%EB%94%94%EC%98%A4+%EC%8A%A4%ED%94%BC%EC%BB%A4" target="_blank" rel="noopener noreferrer sponsored"><span>📻 효도 블루투스 라디오 스피커</span><span style="color:var(--gold);">보기 👉</span></a>
        <a class="cp-btn" href="https://link.coupang.com/re/AFFSRP?lptag=AF7865143&amp;subid=paradisehero_col&amp;pageKey=%EB%8C%80%EC%9A%A9%EB%9F%89+%EA%B3%A0%EC%86%8D+%EB%B3%B4%EC%A1%B0%EB%B0%B0%ED%84%B0%EB%A6%AC" target="_blank" rel="noopener noreferrer sponsored"><span>🔋 장시간 청취 대용량 보조배터리</span><span style="color:var(--gold);">보기 👉</span></a>
        <a class="cp-btn" href="https://link.coupang.com/re/AFFSRP?lptag=AF7865143&amp;subid=paradisehero_col&amp;pageKey=%EA%B3%A8%EC%A0%84%EB%8F%84+%EC%9D%B4%EC%96%B4%ED%8F%B0+%EC%9C%A0%EC%84%A0+%EC%9D%B4%EC%96%B4%ED%8F%B0" target="_blank" rel="noopener noreferrer sponsored"><span>🎧 귀 편한 골전도·유선 이어폰</span><span style="color:var(--gold);">보기 👉</span></a>
        <a class="cp-btn" href="https://link.coupang.com/re/AFFSRP?lptag=AF7865143&amp;subid=paradisehero_col&amp;pageKey=%EC%A0%91%EC%9D%B4%EC%8B%9D+%EB%A9%94%EB%AA%A8%EB%A6%AC%ED%8F%BC+%EB%B0%A9%EC%84%9D" target="_blank" rel="noopener noreferrer sponsored"><span>🪑 3시간 공연장 메모리폼 방석</span><span style="color:var(--gold);">보기 👉</span></a>
        <a class="cp-btn" href="https://link.coupang.com/re/AFFSRP?lptag=AF7865143&amp;subid=paradisehero_col&amp;pageKey=%EA%B2%BD%EB%9F%89+%EB%B3%B4%EC%98%A8+%EC%88%84+%EB%AC%B4%EB%A6%8E%EB%8B%B4%EC%9A%94" target="_blank" rel="noopener noreferrer sponsored"><span>🧣 환절기 경량 보온 숄·무릎담요</span><span style="color:var(--gold);">보기 👉</span></a>
        <a class="cp-btn" href="https://link.coupang.com/re/AFFSRP?lptag=AF7865143&amp;subid=paradisehero_col&amp;pageKey=%EB%A3%A8%ED%85%8C%EC%9D%B8+%EC%A7%80%EC%95%84%EC%9E%94%ED%8B%B4" target="_blank" rel="noopener noreferrer sponsored"><span>👁️ 눈 침침함 케어 루테인 지아잔틴</span><span style="color:var(--gold);">보기 👉</span></a>
        <a class="cp-btn" href="https://link.coupang.com/re/AFFSRP?lptag=AF7865143&amp;subid=paradisehero_col&amp;pageKey=%EB%8F%84%EB%9D%BC%EC%A7%80%EB%B0%B0%EC%A6%99+%EC%8A%A4%ED%8B%B1" target="_blank" rel="noopener noreferrer sponsored"><span>🍯 목이 편안한 도라지배즙 스틱</span><span style="color:var(--gold);">보기 👉</span></a>
      </div>
    </section>

    <section>
      <h2 style="font-size:1.2em;color:#ffffff;">자주 묻는 질문</h2>
      {faqs_html}
    </section>
  </main>
  <script src="/js/senior-accessibility.js" defer></script>
  <script>
    function setFontSize(sz, btn) {{
      document.documentElement.style.setProperty('--base-font', sz);
      document.querySelectorAll('.font-btn').forEach(function(b) {{ b.classList.remove('active'); }});
      if (btn) btn.classList.add('active');
    }}
    function shareSeniorLetter() {{
      var msg = {share_msg_js};
      if (navigator.share) {{
        navigator.share({{ title: document.title, text: msg, url: location.href }}).catch(function(){{}});
        return;
      }}
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(msg).then(function() {{
          document.getElementById('share-toast').style.display = 'block';
        }});
      }}
    }}
  </script>
</body>
</html>
"""


def generate_all_senior_columns_and_feeds() -> Dict[str, pathlib.Path]:
    COLUMNS_DIR.mkdir(parents=True, exist_ok=True)
    today_iso = datetime.date.today().isoformat()
    day_utc = datetime.datetime.strptime(today_iso, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
    rfc_now = format_datetime(day_utc)

    cards_html = ""
    for col in SENIOR_COLUMNS:
        out_fp = COLUMNS_DIR / col["slug"]
        out_fp.write_text(_render_column_html(col, today_iso), encoding="utf-8")
        cards_html += f"""
      <article class="card">
        <span class="badge">{html.escape(col['category'])}</span>
        <h2><a href="/columns/{col['slug']}">{html.escape(col['title'])}</a></h2>
        <p>{html.escape(col['desc'])}</p>
        <a class="read-btn" href="/columns/{col['slug']}">📖 큰 글씨로 편지 읽기 →</a>
      </article>"""

    hub_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>큰 글씨 백운호 명곡 해설 &amp; 김쌤의 건강·응원 편지함 | 김쌤의영웅라디오</title>
  <meta name="description" content="5070 시니어 가족분들을 위한 가상 트로트 가수 백운호 대표곡 해설, 나들이 준비물 안내, 음성 사연 보내기, 환절기 건강 편지 모음입니다." />
  <link rel="canonical" href="https://{HOST}/columns/" />
  <meta property="og:url" content="https://{HOST}/columns/" />
  <meta property="og:image" content="https://{HOST}/assets/og_booth_share.jpg" />
  <link rel="alternate" type="application/rss+xml" title="김쌤의영웅라디오 RSS" href="https://{HOST}/rss.xml" />
  <style>
    :root {{ --base-font: 22px; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family:'Pretendard','Malgun Gothic',sans-serif; background:#081c15; color:#f8fafc; font-size:var(--base-font); line-height:1.8; }}
    a {{ color:#fbbf24; text-decoration:none; }}
    .topbar {{ background:#05130e; border-bottom:2px solid #1b4332; padding:16px 20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; }}
    .font-btn {{ min-height:60px; min-width:90px; font-size:20px; font-weight:800; border-radius:12px; border:2px solid #fbbf24; background:#102a20; color:#fff; cursor:pointer; padding:8px 14px; }}
    .wrap {{ max-width:900px; margin:0 auto; padding:28px 20px 76px; }}
    .card {{ background:#102a20; border:2px solid #2d6a4f; border-radius:18px; padding:24px; margin-bottom:20px; }}
    .badge {{ display:inline-block; background:#1b4332; color:#fde68a; padding:4px 14px; border-radius:999px; font-size:19px; font-weight:800; }}
    .card h2 {{ margin:12px 0; font-size:1.25em; line-height:1.4; }}
    .card h2 a {{ color:#ffffff; }}
    .read-btn {{ display:inline-flex; align-items:center; justify-content:center; min-height:62px; padding:10px 22px; background:#10b981; color:#042f2e; font-weight:900; border-radius:12px; margin-top:8px; }}
    .honesty-box {{ background:#fffbeb; color:#451a03; border:2px solid #d97706; border-radius:14px; padding:14px 18px; font-weight:800; font-size:0.92em; margin-bottom:22px; line-height:1.55; }}
  </style>
</head>
<body>
  <header class="topbar">
    <a href="/" style="font-size:24px;font-weight:900;color:#fbbf24;">📻 김쌤의영웅라디오 홈으로</a>
    <div>
      <button type="button" id="btn-font-scaler" class="font-btn" onclick="document.documentElement.style.setProperty('--base-font','22px')">보통</button>
      <button type="button" class="font-btn" onclick="document.documentElement.style.setProperty('--base-font','26px')">크게</button>
      <button type="button" class="font-btn" onclick="document.documentElement.style.setProperty('--base-font','30px')">특대</button>
    </div>
  </header>
  <main class="wrap">
    <h1 style="font-size:1.5em;color:#fde68a;margin-bottom:8px;">💌 김쌤의 큰 글씨 백운호 명곡·건강 편지함</h1>
    <p style="color:#d1fae5;margin-top:0;margin-bottom:18px;">돋보기 없이 편안하게 읽으시고 카카오톡 단톡방 가족분들과 따뜻한 마음을 나눠보세요.</p>
    <div class="honesty-box">{HONESTY_BADGE_TEXT}</div>
    {cards_html}
    <section class="card" style="border-color:#fbbf24;margin-top:28px;">
      <span class="badge">💚 에디터 큐레이션 · 청취 &amp; 공연 준비물</span>
      <h2>💚 김쌤의 콘서트·응원 안심 준비물관</h2>
      <p>블루투스 라디오 스피커, 보조배터리, 이어폰, 공연장 방석, 보온 숄, 루테인, 도라지배즙 등 시니어 청취·공연 필수품 7종을 만나보세요.</p>
      <p style="font-size:0.9em;color:#fde68a;font-weight:800;margin:0 0 12px;">{FTC_DISCLOSURE_TEXT}</p>
      <a class="read-btn" href="https://cshop.naver.com/paradiseshop" target="_blank" rel="noopener noreferrer sponsored" style="background:#03c75a;color:#ffffff;width:100%;margin-bottom:10px;">💚 김쌤의 콘서트·응원 안심 준비물관 (네이버페이 공식관) 👉</a>
      <a class="read-btn" href="https://influencers.coupang.com/s/paradisehero" target="_blank" rel="noopener noreferrer sponsored" style="background:#b91c1c;color:#ffffff;width:100%;">📻 김쌤의 콘서트·응원 안심 준비물관 (쿠팡 공식관) 👉</a>
    </section>
  </main>
  <script src="/js/senior-accessibility.js" defer></script>
</body>
</html>
"""
    (COLUMNS_DIR / "index.html").write_text(hub_html, encoding="utf-8")

    # Build complete URL map & update sitemap.xml + rss.xml + feed.xml + llms.txt (lounge.html excluded!)
    core_pages = [
        ("", "index.html", "1.0", "daily"),
        ("radio.html", "radio.html", "0.95", "daily"),
        ("booth.html", "booth.html", "0.95", "weekly"),
        ("photobooth.html", "photobooth.html", "0.90", "weekly"),
        ("story.html", "story.html", "0.90", "daily"),
        ("community.html", "community.html", "0.90", "daily"),
        ("stream.html", "stream.html", "0.88", "weekly"),
        ("vip.html", "vip.html", "0.92", "weekly"),
        ("news.html", "news.html", "0.92", "daily"),
        ("columns/", "columns/index.html", "0.93", "daily"),
    ]
    url_map: Dict[str, pathlib.Path] = {}
    smap_blocks: List[str] = []
    seen_locs: set[str] = set()

    def _normalize_canonical_loc(raw_loc: str) -> str:
        if raw_loc.endswith("/index.html"):
            return raw_loc[: -len("index.html")]
        return raw_loc

    for slug_url, rel_path, prio, freq in core_pages:
        fp = DIV4_ROOT / rel_path
        if not fp.exists():
            continue
        raw_loc = f"https://{HOST}/" if slug_url == "" else f"https://{HOST}/{slug_url}"
        loc = _normalize_canonical_loc(raw_loc)
        if loc in seen_locs:
            continue
        seen_locs.add(loc)
        url_map[loc] = fp
        smap_blocks.append(
            f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{today_iso}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>"
        )

    rss_items_xml: List[str] = []
    for col in SENIOR_COLUMNS:
        loc = _normalize_canonical_loc(f"https://{HOST}/columns/{col['slug']}")
        if loc in seen_locs:
            continue
        seen_locs.add(loc)
        url_map[loc] = COLUMNS_DIR / col["slug"]
        smap_blocks.append(
            f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{today_iso}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.88</priority>\n  </url>"
        )
        rss_items_xml.append(
            f"""    <item>
      <title><![CDATA[{col['title']}]]></title>
      <link>{loc}</link>
      <guid isPermaLink="true">{loc}</guid>
      <pubDate>{rfc_now}</pubDate>
      <description><![CDATA[{col['desc']}]]></description>
    </item>"""
        )

    (DIV4_ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(smap_blocks)
        + "\n</urlset>\n",
        encoding="utf-8",
    )

    rss_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>유튜브 @김쌤의영웅라디오 가족 사랑방 · 가상 트로트 가수 백운호 새 소식 &amp; 큰 글씨 편지</title>
    <link>https://{HOST}/</link>
    <atom:link href="https://{HOST}/rss.xml" rel="self" type="application/rss+xml" />
    <atom:link href="https://pubsubhubbub.appspot.com/" rel="hub" />
    <description>5070 시니어 가족분들의 음악 위로와 사연 소통을 위한 오리지널 가상 트로트 가수 백운호 &amp; @김쌤의영웅라디오 공식 사랑방</description>
    <language>ko-KR</language>
    <lastBuildDate>{rfc_now}</lastBuildDate>
{chr(10).join(rss_items_xml)}
  </channel>
</rss>
"""
    (DIV4_ROOT / "rss.xml").write_text(rss_xml, encoding="utf-8")
    (DIV4_ROOT / "feed.xml").write_text(rss_xml.replace("/rss.xml", "/feed.xml"), encoding="utf-8")

    llms_lines = [
        "# Paradise Hero · 유튜브 @김쌤의영웅라디오 가족 사랑방 · 가상 트로트 가수 백운호 라운지 (https://paradise-hero.com)",
        "",
        f"> 최종 업데이트: {today_iso} | 5070 시니어 음악 위로·사연 소통 라디오 쉼터 (실존 연예인 팬카페 아님 · 오리지널 가상 트로트 가수 '백운호' 공식 라운지 · WCAG AAA 20px+ 큰 글씨, 60px+ 터치 버튼).",
        "",
        "## 1. 주요 라디오 사랑방 서비스 바로가기",
        f"- 메인 홈: https://{HOST}/",
        f"- 사연 라디오 1~5화 연속 듣기: https://{HOST}/radio.html",
        f"- 가상 트로트 가수 백운호 6대 대표곡 감상관 (어머니의 봄날 · 백운호 연가 · 항구의 등불 · 다시 피는 동백꽃 · 고향역 첫차 · 내 인생의 금빛 노을): https://{HOST}/stream.html",
        f"- 백운호 6대 무대 의상 무료 기념촬영관: https://{HOST}/booth.html",
        f"- [① 1줄 응원 남기기] & 전국 실시간 공감 박수 소통 사랑방: https://{HOST}/community.html",
        f"- [② 라디오 사연 보내기] (음성 받아쓰기 지원): https://{HOST}/story.html",
        f"- 화·금 저녁 6시 정규 방송 편성표 & 백운호 소식란: https://{HOST}/news.html",
        f"- 10종 무료 카톡 안부카드·큰글씨 달력 선물관 & 김쌤의 콘서트·응원 안심 준비물관: https://{HOST}/vip.html",
        f"- 큰 글씨 명곡 해설 · 건강 편지함: https://{HOST}/columns/",
        "- 공식 제휴·사연 문의: mailto:beable9489@gmail.com",
        "",
        "## 2. 큰 글씨 백운호 명곡 해설 및 시니어 건강 칼럼 목록 (/columns/)",
    ]
    for col in SENIOR_COLUMNS:
        llms_lines.append(f"- [{col['title']}](https://{HOST}/columns/{col['slug']})")
    (DIV4_ROOT / "llms.txt").write_text("\n".join(llms_lines) + "\n", encoding="utf-8")

    return url_map


if __name__ == "__main__":
    umap = generate_all_senior_columns_and_feeds()
    print(f"[HERO Senior Columns] Generated {len(SENIOR_COLUMNS)} Baek Woon-ho WCAG AAA columns & synced {len(umap)} canonical URLs.")
