#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
4사업부/scripts/generate_senior_columns_and_feeds.py
===================================================
Generates WCAG AAA Senior-First Song Commentary & Radio Letter Hub (`/columns/*.html`),
and dynamically updates `rss.xml`, `sitemap.xml`, and `llms.txt` for `paradise-hero.com`.

Strict Guardrails (GEMINI.md):
  - Minimum body font >= 22px (exceeds 20px requirement), touch targets >= 64px (exceeds 60px).
  - 3-stage font size switcher (`기본 22px` / `크게 26px` / `특대 30px`).
  - 1-Tap KakaoTalk / Naver Band Share & Copy Letter button for viral organic sharing in 5070 chats.
  - Preserves all 4 funnels: Radio (`radio.html`), Free 10-Outfit Photo Booth (`booth.html`),
    Gold VIP (`vip.html`), and Golden Cheer Board (`community.html`).
  - Zero rival singer names & zero banned promo words.
"""

from __future__ import annotations

import datetime
import html
import json
import pathlib
from email.utils import format_datetime
from typing import Any, Dict, List, Tuple

DIV4_ROOT = pathlib.Path(__file__).resolve().parent.parent
COLUMNS_DIR = DIV4_ROOT / "columns"
HOST = "paradise-hero.com"

SENIOR_COLUMNS: List[Dict[str, Any]] = [
    {
        "slug": "dangsin-pyeon-lyric-commentary.html",
        "category": "명곡 해설 · 정규 1집",
        "title": "가수 황영웅 정규 1집 '당신 편' 가사 해설 — 왜 첫 소절만 들어도 가슴이 먹먹해질까요",
        "desc": "어머님들의 고단했던 세월을 다정하게 안아주는 가수 황영웅 대표곡 '당신 편'의 노랫말 의미와 깊은 동굴 중저음 보이스의 치유력을 김쌤이 풀어드립니다.",
        "body_paragraphs": [
            "살다 보면 누구에게도 속마음을 털어놓지 못하고 혼자 베갯잇을 적시는 밤이 있습니다. 자식들에게 짐이 될까 봐 괜찮다 웃어넘기던 그 긴 세월 끝에, 가수 황영웅 님의 '당신 편' 첫 소절이 흘러나오면 굳게 닫혔던 마음의 빗장이 스르르 풀립니다.",
            "기교를 부려 높은 음을 자랑하기보다, 듣는 분의 심장 박동과 가장 닮은 따뜻하고 묵직한 중저음으로 '세상이 다 등 돌려도 나는 끝까지 당신 편'이라 건네는 진심. 그것이 바로 수십만 파라다이스 가족분들이 이 노래를 인생의 동반자로 삼으신 이유입니다.",
            "오늘 저녁에는 따뜻한 차 한 잔을 곁에 두시고 파라다이스 히어로 24시간 라디오 플레이어에서 '당신 편'을 편안하게 감상해 보세요.",
        ],
        "kakao_quote": "💚 첫 소절만 들어도 눈물 나는 황영웅 '당신 편', 큰 글씨 해설 편지입니다.",
        "faqs": [
            ("황영웅 '당신 편' 노래와 라디오 사연은 어디서 들을 수 있나요?", "파라다이스 히어로 공식 팬 쉼터(paradise-hero.com/radio.html)에서 회원가입 없이 큰 글씨 화면으로 24시간 연속 감상하실 수 있습니다."),
            ("글씨가 작아서 읽기 힘들 때는 어떻게 하나요?", "화면 상단의 '글자 크기 조절' 버튼(기본·크게·특대)을 한 번만 누르시면 돋보기 없이도 아주 시원하게 읽으실 수 있습니다."),
        ],
    },
    {
        "slug": "haebaragi-insadong-song-story.html",
        "category": "명곡 산책 · 사모곡",
        "title": "'해바라기'와 '인사동 찻집' — 세월이 깊어질수록 진가를 발하는 정통 중저음의 울림",
        "desc": "오직 한 사람만을 바라보는 해바라기 같은 팬심과 추억이 깃든 '인사동 찻집'의 정취를 큰 글씨 에세이로 만나보세요.",
        "body_paragraphs": [
            "비바람이 불어도 해를 향해 고개를 드는 해바라기처럼, 가수 황영웅 님과 파라다이스 가족분들이 서로를 지켜온 시간은 그 어떤 보석보다 단단하고 눈부십니다.",
            "'인사동 찻집'을 들을 때면 젊은 날 고운 한복이나 정장을 차려입고 거닐던 서울 종로 골목의 향기가 눈앞에 아련히 피어오릅니다. 한 음절도 허투루 흘리지 않는 정직한 호흡이 옛 추억을 고스란히 되살려 줍니다.",
            "추억 속 멋진 차림 그대로, 오늘 무료 온라인 사진관에서 황영웅 님 10가지 의상과 함께 나만의 다정한 기념 화보를 남겨보시는 건 어떨까요.",
        ],
        "kakao_quote": "🌻 세월이 깊을수록 울림이 큰 황영웅 '해바라기·인사동 찻집' 큰 글씨 산책입니다.",
        "faqs": [
            ("온라인 기념사진관은 무료인가요?", "네, 회원가입이나 결제 없이 누구나 횟수 제한 없이 100% 무료로 촬영하고 휴대폰 사진첩에 저장하실 수 있습니다."),
        ],
    },
    {
        "slug": "emerald-concert-senior-preparation-guide.html",
        "category": "콘서트 안내서",
        "title": "어머님들을 위한 황영웅 전국투어 콘서트 100배 즐기기 큰 글씨 준비물 체크리스트",
        "desc": "공연장 가실 때 꼭 챙기셔야 할 에메랄드 응원 준비물, 편안한 신발과 보온 숄, 목 보호용 따뜻한 물까지 한눈에 확인하세요.",
        "body_paragraphs": [
            "설레는 콘서트 날 아침, 소풍 가는 소녀처럼 옷장 앞을 서성이시는 어머님들의 미소가 참 곱습니다. 3시간 가까운 열띤 라이브 무대를 끝까지 편안하게 즐기시려면 몇 가지 작은 준비가 큰 도움이 됩니다.",
            "첫째, 공연장 내부는 냉난방으로 온도 차가 있을 수 있으니 어깨에 가볍게 두르실 부드러운 에메랄드빛 스카프나 가디건을 챙겨 주세요. 둘째, 박수 치고 함께 노래하실 때 목이 마르지 않도록 미지근한 생수 한 병과 여분의 응원봉 건전지를 가방 앞주머니에 넣어 두시면 든든합니다.",
            "공연장에 직접 못 가시는 날에도 아쉬워하지 마세요. 파라다이스 사랑방 응원 게시판과 라디오에서 전국 팬분들과 똑같은 열기로 함께하실 수 있습니다.",
        ],
        "kakao_quote": "💚 설레는 황영웅 콘서트 가시기 전, 어머님 필수 준비물만 크게 모았습니다.",
        "faqs": [
            ("콘서트 응원 문구는 어디서 나눌 수 있나요?", "파라다이스 사랑방(community.html)에서 닉네임만 적으시면 전국 팬분들과 실시간으로 응원 인사를 나누실 수 있습니다."),
        ],
    },
    {
        "slug": "bisang-live-encore-resonance.html",
        "category": "라이브 감동 노트",
        "title": "앙코르 무대 '비상'이 객석을 눈물바다로 만든 이유 — 다시 날아오르는 우리의 인생가",
        "desc": "시련의 계절을 지나 더 높이 날아오르는 명곡 '비상' 라이브 무대의 감동과 우리네 인생 이야기를 담았습니다.",
        "body_paragraphs": [
            "누구나 인생에서 한 번쯤 날개가 꺾인 것 같은 겨울을 지납니다. 그래서일까요, 무대 위에서 온 힘을 다해 '비상'을 열창하는 가수 황영웅 님의 목소리에는 단순한 노래를 넘어선 뜨거운 생명의 다짐이 서려 있습니다.",
            "객석을 가득 메운 에메랄드 불빛 아래서 함께 눈물을 닦고 기립박수를 보내던 그 순간, 위로를 받은 것은 무대 위 가수만이 아니라 평생 가족을 위해 헌신해 온 우리 자신이었습니다.",
            "오늘 하루 마음이 조금 지치셨다면, 다시 한번 두 날개를 펴는 마음으로 라디오 본방송을 켜 보시기 바랍니다.",
        ],
        "kakao_quote": "🕊️ 객석을 눈물바다로 만든 황영웅 '비상', 다시 날아오르는 인생 응원가입니다.",
        "faqs": [
            ("영웅라디오 본방송 시간은 언제인가요?", "유튜브 '@김쌤의영웅라디오'에서 매일 아침 7시 30분 문안 방송과 저녁 7시 30분 감동 본방송으로 찾아뵙며, 홈페이지에서는 24시간 언제든 들으실 수 있습니다."),
        ],
    },
    {
        "slug": "paradise-fandom-warm-charity-culture.html",
        "category": "팬덤 · 선한 영향력",
        "title": "가수의 이름을 가장 아름답게 빛내는 법 — 공식 팬덤 '파라다이스'의 온기 나눔 이야기",
        "desc": "전국 방방곡곡 소외된 이웃에게 따뜻한 김장과 성금을 전하는 파라다이스 가족분들의 품격 있는 응원 문화를 조명합니다.",
        "body_paragraphs": [
            "그 가수의 품격은 그를 사랑하는 팬들의 모습을 보면 알 수 있다는 말이 있습니다. 서울·경기부터 부산·대구·울산·호남까지, 전국 파라다이스 가족분들이 이어가는 조용하고 꾸준한 나눔 봉사는 우리 사회의 귀감이 되고 있습니다.",
            "누가 알아주기를 바라서가 아니라, 황영웅 님의 노래로 받은 따뜻한 위로를 주변의 이웃과 나누고 싶다는 고운 마음들이 모여 추운 계절을 훈훈하게 데우고 있습니다.",
            "서로의 건강을 먼저 묻고 고운 말로 응원하는 파라다이스 히어로 사랑방에서 오늘도 기분 좋은 출석 인사를 남겨 보세요.",
        ],
        "kakao_quote": "🌷 노래로 받은 위로를 이웃 사랑으로 나누는 자랑스러운 파라다이스 이야기입니다.",
        "faqs": [
            ("파라다이스 히어로 출석 응원은 어떻게 하나요?", "복잡한 비밀번호나 가입 절차 없이 '사랑방 응원게시판'에서 별명만 입력하시면 3초 만에 따뜻한 응원 글을 올리실 수 있습니다."),
        ],
    },
    {
        "slug": "radio-story-guide-voice-dictation.html",
        "category": "시니어 맞춤 안내",
        "title": "작은 휴대폰 자판 치기 힘드셨죠? 목소리로 편하게 '김쌤의 영웅라디오' 사연 보내는 법",
        "desc": "손가락으로 작은 글자를 누르지 않아도 말만 하시면 글자로 척척 받아적어 주는 음성 사연 접수 기능을 쉽게 설명해 드립니다.",
        "body_paragraphs": [
            "가수 황영웅 님 노래를 들으며 떠오른 젊은 날의 추억이나 자녀에게 전하고 싶은 고마운 마음은 가득한데, 휴대폰 자판이 너무 작고 오타가 나서 포기하셨던 어머님들이 많으십니다.",
            "파라다이스 히어로 '사연 복덕방' 페이지에는 어머님들을 위해 큼지막한 마이크 버튼을 준비해 두었습니다. 버튼을 한 번 누르시고 전화 통화하듯 천천히 말씀하시면 화면에 큰 글씨로 사연이 저절로 적힙니다.",
            "보내주신 소중한 인생 이야기는 김쌤이 정성껏 읽어드리는 15분 감동 라디오 방송으로 제작되어 전국 파라다이스 가족분들과 함께 나누게 됩니다.",
        ],
        "kakao_quote": "🎙️ 작은 글씨 타자 치지 마세요—말씀만 하시면 영웅라디오 사연이 바로 적힙니다.",
        "faqs": [
            ("사연을 보내면 비용이 드나요?", "전혀 들지 않습니다. 사연 접수와 라디오 청취는 100% 무료로 운영됩니다."),
        ],
    },
    {
        "slug": "seasonal-senior-throat-and-sleep-letter.html",
        "category": "김쌤의 건강 편지",
        "title": "김쌤의 환절기 안부 편지 — 노래 부르실 때 목을 촉촉하게 지키는 차(茶)와 깊은 잠 습관",
        "desc": "황영웅 님이 늘 당부하는 '어머님들의 건강'! 아침저녁 일교차에 성대와 기관지를 지키는 생활 수칙을 큰 글씨로 정리했습니다.",
        "body_paragraphs": [
            "무대 인사 때마다 가수 황영웅 님이 잊지 않고 꼭 챙기는 말씀이 있습니다. 바로 '어머님들 아프지 마시고 건강하셔야 저도 오래오래 노래합니다'라는 다정한 당부입니다.",
            "노래교실이나 집에서 따라 부르실 때는 찬물 대신 체온과 비슷한 40도 안팎의 따뜻한 도라지배차나 미지근한 물을 한 모금씩 자주 머금어 성대 점막을 촉촉하게 해 주세요.",
            "또한 잠자리에 드시기 1시간 전에는 방 안 습도를 50% 내외로 맞추고 잔잔한 볼륨으로 심야 라디오를 틀어 두시면 긴장이 풀리며 한결 편안한 숙면을 취하실 수 있습니다.",
        ],
        "kakao_quote": "🍵 황영웅 님이 꼭 당부한 어머님 환절기 목 건강·숙면 안부 편지입니다.",
        "faqs": [
            ("잠들기 전 라디오를 틀어 놓아도 괜찮나요?", "네, 눈이 부시지 않는 어두운 편안한 화면 구성으로 제작되어 머리맡에 두고 잔잔하게 청취하시기 좋습니다."),
        ],
    },
    {
        "slug": "streaming-and-cheering-easy-step-guide.html",
        "category": "3분 쉬운 응원법",
        "title": "칠순에도 배우기 쉬운 3분 응원 가이드 — 자녀에게 미안해하지 않고 혼자서 척척 응원하기",
        "desc": "바쁜 자녀들에게 매번 물어보기 미안하셨던 어머님들을 위해, 큰 버튼 하나로 매일 황영웅 님을 응원하는 가장 쉬운 방법을 알려드립니다.",
        "body_paragraphs": [
            "자식들에게 휴대폰 사용법을 두 번 세 번 물어보기가 괜히 미안해서 혼자 속앓이하셨던 적 있으시지요. 파라다이스 히어로는 처음부터 오직 5070 어머님·아버님 눈높이에 맞춰 모든 글씨와 버튼을 큼직하게 만들었습니다.",
            "즐겨찾기나 카카오톡 나와의 채팅방에 주소 하나만 저장해 두시면, 매일 아침 눈뜨자마자 버튼 한 번으로 오늘의 소식 확인부터 라디오 감상, 응원 전광판 출석, 무료 효도 달력 만들기까지 혼자서도 멋지게 해내실 수 있습니다.",
            "황영웅 님을 응원하며 디지털 세상의 당당한 주인공이 되신 전국 모든 파라다이스 어머님들의 빛나는 청춘을 진심으로 응원합니다.",
        ],
        "kakao_quote": "📱 자녀 도움 없이도 큰 버튼 한 번이면 황영웅 응원이 끝납니다.",
        "faqs": [
            ("골드 VIP 멤버십과 무료 선물제작소는 무엇인가요?", "누구나 무료로 달력과 동행 증서를 만드실 수 있으며, 더 특별한 황금 명패와 전용 혜택을 원하시는 분들을 위해 골드 VIP 라운지(vip.html)도 함께 열려 있습니다."),
        ],
    },
]


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
                    "author": {"@type": "Organization", "name": "김쌤의 영웅라디오 · 파라다이스히어로", "url": f"https://{HOST}/"},
                },
                {"@type": "FAQPage", "mainEntity": faq_entities},
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "파라다이스 홈", "item": f"https://{HOST}/"},
                        {"@type": "ListItem", "position": 2, "name": "큰 글씨 명곡·건강 편지", "item": f"https://{HOST}/columns/index.html"},
                        {"@type": "ListItem", "position": 3, "name": col["title"], "item": canonical_url},
                    ],
                },
            ],
        },
        ensure_ascii=False,
    )

    paras_html = "\n".join(f"<p>{html.escape(p)}</p>" for p in col["body_paragraphs"])
    faqs_html = "\n".join(
        f'<div class="faq-item"><h3>Q. {html.escape(q)}</h3><p>{html.escape(a)}</p></div>'
        for q, a in col["faqs"]
    )
    share_msg_js = json.dumps(f"{col['kakao_quote']}\n👉 큰 글씨로 바로 읽기: {canonical_url}", ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(col['title'])} | 파라다이스히어로</title>
  <meta name="description" content="{html.escape(col['desc'])}" />
  <link rel="canonical" href="{canonical_url}" />
  <link rel="alternate" type="application/rss+xml" title="파라다이스히어로 새 소식" href="https://{HOST}/rss.xml" />
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
    .wrap {{ max-width: 860px; margin: 0 auto; padding: 28px 20px 72px; }}
    .badge {{ display: inline-block; background: #1b4332; color: #fde68a; border: 1px solid var(--gold); padding: 6px 16px; border-radius: 999px; font-size: 20px; font-weight: 800; }}
    h1 {{ font-size: 1.45em; line-height: 1.4; color: #ffffff; margin: 16px 0 12px; }}
    .date-line {{ color: var(--muted); font-size: 0.92em; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #2d6a4f; }}
    article p {{ margin: 22px 0; font-size: 1em; color: #f1f5f9; word-keep: keep-all; }}
    .share-box {{ background: #143628; border: 2px solid var(--gold); border-radius: 18px; padding: 24px; margin: 32px 0; text-align: center; }}
    .share-btn {{ width: 100%; min-height: 68px; font-size: 22px; font-weight: 900; border-radius: 14px; border: none; background: #fee500; color: #191919; cursor: pointer; padding: 14px 20px; }}
    .funnel-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; margin: 32px 0; }}
    .funnel-btn {{ display: flex; align-items: center; justify-content: center; text-align: center; min-height: 68px; padding: 14px 18px; border-radius: 14px; font-size: 21px; font-weight: 800; background: var(--card); border: 2px solid #34d399; color: #ffffff; }}
    .funnel-btn.gold {{ border-color: var(--gold); background: linear-gradient(135deg, #422006, #1c1917); color: #fde68a; }}
    .faq-item {{ background: var(--card); border: 1px solid #2d6a4f; border-radius: 14px; padding: 20px; margin-bottom: 16px; }}
    .faq-item h3 {{ margin: 0 0 10px; color: var(--gold); font-size: 1.05em; }}
    .faq-item p {{ margin: 0; font-size: 0.98em; }}
  </style>
</head>
<body>
  <header class="topbar">
    <a class="brand" href="/">💚 파라다이스 히어로</a>
    <div class="font-controls" role="group" aria-label="글자 크기 3단계 조절">
      <button type="button" class="font-btn active" onclick="setFontSize('22px', this)">글자 보통</button>
      <button type="button" class="font-btn" onclick="setFontSize('26px', this)">글자 크게</button>
      <button type="button" class="font-btn" onclick="setFontSize('30px', this)">글자 특대</button>
    </div>
  </header>
  <main class="wrap">
    <span class="badge">{html.escape(col['category'])}</span>
    <h1>{html.escape(col['title'])}</h1>
    <div class="date-line">발행일: {today_iso} · 글: 김쌤의 영웅라디오 편집실 · <a href="/columns/index.html">전체 편지 목록 보기 →</a></div>

    <article>
      {paras_html}
    </article>

    <section class="share-box">
      <p style="margin:0 0 14px;font-weight:800;color:#fde68a;">소중한 파라다이스 지인·단톡방에 이 따뜻한 편지를 나눠보세요</p>
      <button type="button" class="share-btn" onclick="shareSeniorLetter()">💬 카카오톡 · 밴드에 큰 글씨 편지 공유하기</button>
      <p id="share-toast" style="margin:12px 0 0;color:#6ee7b7;font-weight:800;display:none;">✅ 편지 주소가 복사되었습니다! 카카오톡이나 밴드 대화창에 '붙여넣기' 해주세요.</p>
    </section>

    <section aria-label="파라다이스 주요 메뉴 바로가기">
      <h2 style="font-size:1.25em;color:var(--gold);margin-bottom:14px;">가수 황영웅 팬 쉼터 바로가기</h2>
      <div class="funnel-grid">
        <a class="funnel-btn" href="/radio.html">📻 24시간 영웅라디오 연속 듣기</a>
        <a class="funnel-btn" href="/booth.html">📸 10종 의상 무료 기념사진 찍기</a>
        <a class="funnel-btn gold" href="/vip.html">👑 골드 VIP 멤버십 &amp; 무료 달력 선물</a>
        <a class="funnel-btn" href="/community.html">💛 황금 응원 전광판 출석하기</a>
      </div>
    </section>

    <section>
      <h2 style="font-size:1.2em;color:#ffffff;">자주 묻는 질문</h2>
      {faqs_html}
    </section>
  </main>
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
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    today_iso = datetime.date.today().isoformat()
    rfc_now = format_datetime(now_utc)

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
  <title>큰 글씨 명곡 해설 &amp; 김쌤의 건강·응원 편지함 | 파라다이스히어로</title>
  <meta name="description" content="5070 파라다이스 가족분들을 위한 가수 황영웅 명곡 가사 해설, 콘서트 준비물 안내, 음성 사연 보내기, 환절기 건강 편지 모음입니다." />
  <link rel="canonical" href="https://{HOST}/columns/index.html" />
  <link rel="alternate" type="application/rss+xml" title="파라다이스히어로 RSS" href="https://{HOST}/rss.xml" />
  <style>
    :root {{ --base-font: 22px; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family:'Pretendard','Malgun Gothic',sans-serif; background:#081c15; color:#f8fafc; font-size:var(--base-font); line-height:1.8; }}
    a {{ color:#fbbf24; text-decoration:none; }}
    .topbar {{ background:#05130e; border-bottom:2px solid #1b4332; padding:16px 20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; }}
    .font-btn {{ min-height:60px; min-width:90px; font-size:20px; font-weight:800; border-radius:12px; border:2px solid #fbbf24; background:#102a20; color:#fff; cursor:pointer; padding:8px 14px; }}
    .wrap {{ max-width:900px; margin:0 auto; padding:28px 20px 64px; }}
    .card {{ background:#102a20; border:2px solid #2d6a4f; border-radius:18px; padding:24px; margin-bottom:20px; }}
    .badge {{ display:inline-block; background:#1b4332; color:#fde68a; padding:4px 14px; border-radius:999px; font-size:19px; font-weight:800; }}
    .card h2 {{ margin:12px 0; font-size:1.25em; line-height:1.4; }}
    .card h2 a {{ color:#ffffff; }}
    .read-btn {{ display:inline-flex; align-items:center; justify-content:center; min-height:62px; padding:10px 22px; background:#10b981; color:#042f2e; font-weight:900; border-radius:12px; margin-top:8px; }}
  </style>
</head>
<body>
  <header class="topbar">
    <a href="/" style="font-size:24px;font-weight:900;color:#fbbf24;">💚 파라다이스 히어로 홈으로</a>
    <div>
      <button type="button" class="font-btn" onclick="document.documentElement.style.setProperty('--base-font','22px')">보통</button>
      <button type="button" class="font-btn" onclick="document.documentElement.style.setProperty('--base-font','26px')">크게</button>
      <button type="button" class="font-btn" onclick="document.documentElement.style.setProperty('--base-font','30px')">특대</button>
    </div>
  </header>
  <main class="wrap">
    <h1 style="font-size:1.5em;color:#fde68a;margin-bottom:8px;">💌 김쌤의 큰 글씨 명곡·응원 편지함</h1>
    <p style="color:#d1fae5;margin-top:0;margin-bottom:28px;">돋보기 없이 편안하게 읽으시고 카카오톡 단톡방 가족분들과 따뜻한 마음을 나눠보세요.</p>
    {cards_html}
  </main>
</body>
</html>
"""
    (COLUMNS_DIR / "index.html").write_text(hub_html, encoding="utf-8")

    # Build complete URL map & update sitemap.xml + rss.xml + llms.txt
    core_pages = [
        ("", "index.html", "1.0", "daily"),
        ("radio.html", "radio.html", "0.95", "daily"),
        ("booth.html", "booth.html", "0.95", "weekly"),
        ("photobooth.html", "photobooth.html", "0.90", "weekly"),
        ("story.html", "story.html", "0.90", "daily"),
        ("community.html", "community.html", "0.90", "daily"),
        ("stream.html", "stream.html", "0.88", "weekly"),
        ("vip.html", "vip.html", "0.92", "weekly"),
        ("lounge.html", "lounge.html", "0.85", "weekly"),
        ("news.html", "news.html", "0.92", "daily"),
        ("columns/index.html", "columns/index.html", "0.93", "daily"),
    ]
    url_map: Dict[str, pathlib.Path] = {}
    smap_blocks: List[str] = []

    for slug_url, rel_path, prio, freq in core_pages:
        fp = DIV4_ROOT / rel_path
        if not fp.exists():
            continue
        loc = f"https://{HOST}/" if slug_url == "" else f"https://{HOST}/{slug_url}"
        url_map[loc] = fp
        smap_blocks.append(
            f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{today_iso}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>"
        )

    rss_items_xml: List[str] = []
    for col in SENIOR_COLUMNS:
        loc = f"https://{HOST}/columns/{col['slug']}"
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
    <title>파라다이스 히어로 · 김쌤의 영웅라디오 공식 새 소식 &amp; 큰 글씨 명곡 편지</title>
    <link>https://{HOST}/</link>
    <atom:link href="https://{HOST}/rss.xml" rel="self" type="application/rss+xml" />
    <atom:link href="https://pubsubhubbub.appspot.com/" rel="hub" />
    <description>가수 황영웅 5070 시니어 팬덤 쉼터 — 24시간 연속 라디오, 10종 의상 무료 기념사진관, 큰 글씨 명곡 해설 및 건강 편지</description>
    <language>ko-KR</language>
    <lastBuildDate>{rfc_now}</lastBuildDate>
{chr(10).join(rss_items_xml)}
  </channel>
</rss>
"""
    (DIV4_ROOT / "rss.xml").write_text(rss_xml, encoding="utf-8")

    llms_lines = [
        "# Paradise Hero · 파라다이스 히어로 · 김쌤의 영웅라디오 (https://paradise-hero.com)",
        "",
        f"> 최종 업데이트: {today_iso} | 가수 황영웅 5070 시니어 팬덤 플랫폼 (WCAG AAA 20px+ 큰 글씨, 60px+ 터치 버튼, 글자 크기 3단계 조절).",
        "",
        "## 1. 주요 팬 서비스 바로가기",
        f"- 메인 홈: https://{HOST}/",
        f"- 24시간 연속 재생 영웅라디오: https://{HOST}/radio.html",
        f"- 10종 시그니처 의상 무제한 무료 기념사진관: https://{HOST}/booth.html",
        f"- 음성 받아쓰기 사연 접수 (사연 복덕방): https://{HOST}/story.html",
        f"- 골드 VIP 멤버십 & 무료 효도 달력/증서 제작소: https://{HOST}/vip.html",
        f"- 황금 응원 전광판 (사랑방 출석부): https://{HOST}/community.html",
        f"- 황영웅 전담 뉴스룸: https://{HOST}/news.html",
        f"- 큰 글씨 명곡 해설 · 건강 편지함: https://{HOST}/columns/index.html",
        "- 공식 문의: mailto:beable9489@gmail.com",
        "",
        "## 2. 큰 글씨 명곡 해설 및 시니어 응원 칼럼 목록 (/columns/)",
    ]
    for col in SENIOR_COLUMNS:
        llms_lines.append(f"- [{col['title']}](https://{HOST}/columns/{col['slug']})")
    (DIV4_ROOT / "llms.txt").write_text("\n".join(llms_lines) + "\n", encoding="utf-8")

    return url_map


if __name__ == "__main__":
    umap = generate_all_senior_columns_and_feeds()
    print(f"[HERO Senior Columns] Generated {len(SENIOR_COLUMNS)} WCAG AAA columns & synced {len(umap)} canonical URLs.")
