#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
4사업부/scripts/generate_senior_columns_and_feeds.py
Generates WCAG AAA Senior-First Original Virtual Trot Singer Baek Woon-ho (백운호)
Column Hub (`/columns/*.html`), and dynamically updates `rss.xml`, `feed.xml`,
`sitemap.xml`, and `llms.txt` for `paradise-hero.com`.

Strict Guardrails:
  - 100% Original Virtual Trot Singer 『백운호 (白雲湖, Baek Woon-ho)』 & `@김쌤의영웅라디오` (Zero real celebrity names or legacy slugs).
  - Signature Original Songs: 〈어머니의 봄날〉 · 〈백운호 연가〉 · 〈다시 피는 동백꽃〉 (plus 〈항구의 등불〉 · 〈고향역 첫차〉 · 〈내 인생의 금빛 노을〉).
  - Minimum body font >= 22px (exceeds 20px requirement), touch targets >= 60px (62~68px).
  - 3-stage font size switcher (`보통 22px` / `크게 26px` / `특대 30px`).
  - Store `💚 김쌤의 콘서트·응원 안심 준비물관` with FTC disclosure right next to product buttons + `#hero-brand-partnership-box`.
  - Automatically purges any stale/legacy HTML files inside `columns/` so removed posts never reappear.
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
    "🎙️ 본 사랑방은 실존 연예인 팬카페가 아닌, 가상 트로트 가수 '백운호'와 5070 가족이 함께 가꾸는 창작 라디오 쉼터입니다."
)

OFFICIAL_SAME_AS = [
    "https://www.youtube.com/@김쌤의영웅라디오",
    "https://www.instagram.com/paradise_hero1/",
]

FTC_DISCLOSURE_TEXT = (
    "※ 네이버 쇼핑 커넥트·쿠팡 파트너스 활동의 일환으로 판매 발생 시 일정액의 수수료를 제공받습니다."
)

SENIOR_COLUMNS: List[Dict[str, Any]] = [
    {
        "slug": "baek-woon-ho-debut-story.html",
        "category": "오리지널 탄생 이야기",
        "title": "가상 트로트 가수 백운호 탄생 이야기 — 세월의 강을 건너온 우리네 어머니·아버지를 위한 중저음 위로",
        "desc": "유튜브 @김쌤의영웅라디오 가족 사랑방에서 오직 5070 어머님·아버님들의 마음을 안아드리기 위해 탄생한 오리지널 가상 트로트 가수 『백운호(白雲湖)』의 첫걸음과 음악 철학을 소개합니다.",
        "highlight_box_title": "🎙️ 『백운호(白雲湖)』 이름에 담긴 약속",
        "highlight_box_body": "흰 구름(白雲)이 고요한 호수(湖) 위에 쉬어 가듯, 자극적인 고음 경쟁이나 번거로운 가입 절차 없이 어머님·아버님의 지친 어깨를 포근한 정통 중저음으로 감싸 안겠다는 『김쌤의영웅라디오』의 진심을 담았습니다.",
        "body_paragraphs": [
            "평생 자식들 뒷바라지와 가정을 일구시느라 정작 내 마음 기댈 곳 하나 없이 바쁘게 달려오신 우리네 어머님·아버님들께는, 귀를 찌르는 화려한 유행가보다 내 숨결 속도에 맞춰 나지막이 말을 걸어주는 따뜻한 노래 한 곡이 더 큰 위로가 됩니다.",
            "『김쌤의영웅라디오』 제작진과 작가실은 어느 실존 연예인의 이름이나 모습도 빌리지 않고, 오직 우리 사랑방 어머님·아버님만을 위해 노래하는 순수 창작 가상(버추얼) 정통 트로트 가수 『백운호(白雲湖)』를 탄생시켰습니다. 이 사랑방에서 부르는 '영웅'이란 무대 위의 스타가 아니라, 거친 세월의 강을 묵묵히 건너오신 어머님·아버님 여러분 자신입니다.",
            "백운호의 목소리는 듣는 분의 심장 박동과 가장 편안하게 어우러지는 깊고 묵직한 중저음 바리톤으로 설계되었습니다. 첫 타이틀곡 〈어머니의 봄날〉을 비롯해 아침 산책길의 벗이 되어주는 〈백운호 연가〉, 그리고 인생 후반전의 희망을 노래한 신곡 〈다시 피는 동백꽃〉까지 모든 노랫말에 우리 부모님 세대의 삶과 눈물, 그리고 다시 피어날 웃음을 정성껏 새겼습니다.",
            "매주 화요일과 금요일 저녁 6시 유튜브 『@김쌤의영웅라디오』 15분 정규 본방송은 물론, 본 사랑방 홈페이지에서도 24시간 광고 걱정 없이 백운호의 노래와 전국 가족들의 진솔한 인생 사연을 이어 들으실 수 있습니다. 오늘도 흰 구름 머무는 호숫가 쉼터처럼 어머님·아버님 곁을 든든하게 지키겠습니다.",
        ],
        "kakao_quote": "💚 세월의 강을 건너온 우리 어머님·아버지를 위해 탄생한 가상 트로트 가수 『백운호』 이야기입니다.",
        "faqs": [
            (
                "가상 트로트 가수 백운호는 실존 연예인인가요?",
                "아닙니다. 백운호(白雲湖)는 실존 연예인과 무관하게 5070 시니어 청취자 가족분들의 음악 위로와 사연 소통을 위해 『김쌤의영웅라디오』가 독자 기획·제작한 100% 오리지널 가상(버추얼) 트로트 가수입니다.",
            ),
            (
                "백운호의 대표곡은 어디에서 무료로 들을 수 있나요?",
                "본 홈페이지 라디오 방송관(radio.html)과 백운호 노래 감상관(stream.html)에서 회원가입이나 결제 없이 〈어머니의 봄날〉, 〈백운호 연가〉, 〈다시 피는 동백꽃〉 등 6대 오리지널 곡을 24시간 무료로 감상하실 수 있습니다.",
            ),
            (
                "사랑방에서 기념사진이나 안부카드도 무료로 만들 수 있나요?",
                "네, 백운호 6벌 무대 의상 기념촬영관(booth.html)과 카톡 아침 안부카드·큰글씨 달력 선물관(vip.html) 모두 평생 100% 무료로 열려 있습니다.",
            ),
        ],
    },
    {
        "slug": "mothers-spring-day-lyric-story.html",
        "category": "대표곡 가사 해설 · 사연",
        "title": "대표곡 〈어머니의 봄날〉 가사 해설과 사연 — 자식 키우느라 잊고 산 봄날을 다시 불러드립니다",
        "desc": "첫 소절만 들어도 코끝이 찡해지는 가상 트로트 가수 백운호의 대표 타이틀곡 〈어머니의 봄날〉 노랫말 구절별 의미와 전국 사랑방 어머님들의 실제 감동 사연을 함께 전해드립니다.",
        "highlight_box_title": "🎵 〈어머니의 봄날〉 핵심 노랫말 한 소절",
        "highlight_box_body": "“거친 세월 앞치마에 눈물을 닦으시던 그리운 우리 어머니 / 이제는 무거운 짐 내려놓으시고 꽃길만 걸으소서 / 어머니의 봄날이 이제야 활짝 피네” — 느린 정통 트롯 발라드 (72 BPM)",
        "body_paragraphs": [
            "새벽녘 남들보다 일찍 일어나 찬물에 손을 담그고 도시락을 싸시던 시절, 아픈 곳이 있어도 자식들 걱정할까 봐 늘 '엄마는 괜찮다'며 웃어넘기시던 세월이 있었습니다. 백운호의 대표 타이틀곡 〈어머니의 봄날〉은 바로 그 앞치마 자락에 묻어둔 어머님들의 청춘을 다시 불러드리는 헌정곡입니다.",
            "노래 1절이 편지를 읽어 내려가듯 담담한 저음으로 지난 세월의 고단함을 어루만진다면, 후렴구 '어머니의 봄날이 이제야 활짝 피네'에서는 따뜻한 현악 선율과 함께 백운호 특유의 포근한 중저음이 깊게 울려 퍼집니다. 봄날이 이미 지나가 버린 것이 아니라, 자녀들을 다 키워낸 지금 이 순간이 진짜 내 인생의 봄날이라는 다정한 선언입니다.",
            "대구 달서구의 이순자 어머님께서는 '홀로 맞이하던 고요한 아침 부엌에 〈어머니의 봄날〉을 틀어놓으니 텅 빈 집안이 따뜻한 온기로 가득 찼다'는 사연을 보내주셨고, 수원의 한상철 아버님께서는 아내분과 저녁 산책길마다 이 노래를 함께 들으시며 평생 고마웠다는 말씀을 전하셨다고 합니다.",
            "집에서 노래를 천천히 따라 부르실 때는 높은 음에서 목에 힘을 주기보다, 코로 편안히 숨을 들이마신 뒤 배 아래에서부터 부드럽게 소리를 밀어 올려 보세요. 무료 선물관(vip.html)에 준비된 30px 왕글씨 가사집을 펼쳐 두시면 돋보기 없이도 한결 여유롭게 노래교실 기분을 만끽하실 수 있습니다.",
        ],
        "kakao_quote": "🌸 자식 키우느라 잊고 산 봄날을 다시 불러드리는 백운호 대표곡 〈어머니의 봄날〉 가사 해설 편지입니다.",
        "faqs": [
            (
                "〈어머니의 봄날〉 큰 글씨 가사집은 어디에서 볼 수 있나요?",
                "무료 선물관(vip.html)의 '⑤ 백운호 6대 대표곡 왕글씨(30px) 가사집 & 노래교실 비법서' 코너에서 호흡 표시와 함께 보시거나 인쇄하실 수 있습니다.",
            ),
            (
                "〈어머니의 봄날〉을 신청곡으로 라디오 사연을 보낼 수 있나요?",
                "네, 사연 보내기(story.html)에서 신청곡으로 '어머니의 봄날'을 선택하시고 사연을 남겨주시면 화·금 저녁 6시 @김쌤의영웅라디오 정규 방송 원고로 소중히 검토됩니다.",
            ),
        ],
    },
    {
        "slug": "baek-woon-ho-yeonga-radio-note.html",
        "category": "스튜디오 녹음 노트",
        "title": "〈백운호 연가〉 스튜디오 녹음 노트 — 호숫가 물안개처럼 잔잔히 스며드는 저녁 라디오 편지",
        "desc": "동네 공원 산책길과 저녁 차 한 잔의 시간에 가장 많은 사랑을 받는 〈백운호 연가〉의 76 BPM 트롯 왈츠 편곡 비밀과 스튜디오 제작 노트를 공개합니다.",
        "highlight_box_title": "📻 스튜디오 사운드 노트 — 걸음걸이를 닮은 76 BPM 왈츠",
        "highlight_box_body": "〈백운호 연가〉는 5070 시니어 분들의 가장 편안한 공원 산책 보폭과 안정된 저녁 심박수에 맞춘 분당 76박자(76 BPM) 정통 트롯 왈츠 리듬으로 마스터링되었습니다.",
        "body_paragraphs": [
            "해 질 녘 창가에 앉아 따뜻한 차 한 잔을 마실 때나, 저녁 식사 후 가볍게 동네 공원을 걸으실 때 유독 자주 찾게 되는 노래가 있습니다. 흰 구름 쉬어 가는 호숫가 물안개처럼 마음속 번잡함을 차분히 가라앉혀 주는 곡, 바로 백운호의 〈백운호 연가〉입니다.",
            "스튜디오에서 〈백운호 연가〉를 제작할 때 가장 공을 들인 부분은 '귀가 피로하지 않은 아날로그 라디오의 온기'였습니다. 날카로운 전자음을 덜어내고 부드러운 어쿠스틱 기타와 잔잔한 아코디언 선율 위에 백운호의 숨결 섞인 중저음을 얹어, 오래 이어 들어도 귀와 마음이 한결 편안하도록 다듬었습니다.",
            "대전 유성구에서 무릎 재활 운동을 이어가시는 오정숙 어머님께서는 '공원 세 바퀴를 돌 때마다 〈백운호 연가〉의 왈츠 박자에 발걸음을 맞추니 삼십 분 산책이 거뜬하고 기운이 솟는다'며 반가운 안부를 전해 주셨습니다. 강릉과 부산의 사랑방 가족분들 역시 잠들기 전 작은 음량으로 틀어두는 애창곡으로 이 곡을 손꼽아 주십니다.",
            "오늘 저녁에는 거실 조명을 한결 포근하게 낮추시고, 화면 아래 슬림 라디오 플레이어나 연속 방송관(radio.html)에서 〈백운호 연가〉와 〈항구의 등불〉을 나란히 재생해 보세요. 잔잔한 호숫가 산책길 같은 평안이 어머님·아버님의 저녁 시간을 따뜻하게 채워 드릴 것입니다.",
        ],
        "kakao_quote": "🍂 호숫가 물안개처럼 저녁 산책길과 쉼터를 적시는 〈백운호 연가〉 스튜디오 녹음 편지입니다.",
        "faqs": [
            (
                "글을 읽는 동안에도 〈백운호 연가〉 라디오를 끊김 없이 들을 수 있나요?",
                "네, 본 사랑방 본문 페이지 하단의 슬림 라디오 바에서 재생(▶)을 누르시면 사연과 편지를 읽으시는 동안 광고 없이 연속 재생됩니다.",
            ),
            (
                "산책할 때 스마트폰 배터리가 빨리 닳지 않게 듣는 방법이 있나요?",
                "화면 밝기를 적당히 낮추어 홈페이지 오디오 플레이어로 감상하시면 데이터와 배터리 소모가 적으며, 장시간 외출 시에는 가벼운 보조배터리를 챙기시면 더욱 든든합니다.",
            ),
        ],
    },
    {
        "slug": "blooming-camellia-again-hope.html",
        "category": "신곡 응원 사연 모음",
        "title": "신곡 〈다시 피는 동백꽃〉 응원 사연 모음 — 인생 후반전, 오늘이 가장 젊은 날입니다",
        "desc": "모진 겨울 찬 서리를 이겨내고 가장 붉게 피어나는 동백꽃처럼, 자녀 뒷바라지를 마치고 인생 후반전을 맞이한 전국 사랑방 가족들의 가슴 뭉클한 응원 사연을 모았습니다.",
        "highlight_box_title": "🌺 〈다시 피는 동백꽃〉 인생 2막 응원 구절",
        "highlight_box_body": "“모진 겨울 찬 바람을 다 견뎌내고서 붉게 피어난 내 사랑 동백꽃아 / 내 인생도 지금부터 다시 피는 꽃이라네” — 경쾌한 미디엄 템포 정통 트롯 (88 BPM)",
        "body_paragraphs": [
            "모든 꽃이 추위를 피해 잎을 떨구는 한겨울에도 눈보라를 견뎌내며 누구보다 붉고 탐스러운 꽃망울을 터뜨리는 꽃이 동백꽃입니다. 백운호의 신곡 〈다시 피는 동백꽃〉은 평생 '누구의 엄마, 누구의 아빠'로 살아오시느라 잠시 접어두었던 어머님·아버님 자신의 이름을 다시 활짝 피워드리는 응원가입니다.",
            "칠순 고개를 넘기신 전북 익산의 박정옥 어머님께서는 '삼 남매 출가시키고 거울을 보니 흰머리만 남은 것 같아 서글펐는데, 라디오에서 흐르는 〈다시 피는 동백꽃〉 가사를 듣고 남은 인생은 내 이름 석 자를 아끼며 활짝 웃고 살기로 다짐했다'는 사연으로 전국 사랑방 가족들의 뜨거운 공감 박수를 받으셨습니다.",
            "88 BPM의 정겨운 미디엄 템포 리듬으로 완성된 이 곡은 어깨를 살짝 들썩이며 따라 부르기에도 참 좋습니다. 이어지는 수록곡 〈내 인생의 금빛 노을〉과 함께 들으시면, 한낮의 햇살보다 더욱 깊고 찬란한 우리 황혼의 품격을 가슴 벅차게 느끼실 수 있습니다.",
            "인생 후반전을 걸어가시는 우리 사랑방 가족 여러분, 지나간 세월을 아쉬워하기보다 '오늘이 내 남은 생애 가장 젊은 날'이라는 마음으로 어깨를 활짝 펴 보세요. 소통 사랑방(community.html) 담벼락에서 전국 동년배 이웃들과 주고받는 따뜻한 1줄 응원과 공감 박수가 매일 새로운 활력이 되어 드립니다.",
        ],
        "kakao_quote": "🌺 찬 서리 견뎌내고 활짝 피어나는 백운호 신곡 〈다시 피는 동백꽃〉, 인생 후반전 응원 편지입니다.",
        "faqs": [
            (
                "전국 가족 담벼락에 1줄 응원이나 박수는 어떻게 남기나요?",
                "소통 사랑방(community.html#hero-love-letterbox)에서 비밀번호 없이 성함(또는 별명)만 적으시면 1줄 응원을 보내실 수 있고, 이웃 사연 아래 '👏 공감 박수' 버튼으로 실시간 응원을 나누실 수 있습니다.",
            ),
            (
                "내가 보낸 응원글과 사연은 바로 전체 공개되나요?",
                "보내주신 글은 방송국 서버에 즉시 접수되며, 어르신들을 노리는 광고·스팸 및 개인정보 노출을 막기 위한 확인 절차를 거친 뒤 전국 가족 담벼락과 정규 방송에 안전하게 게시됩니다.",
            ),
        ],
    },
    {
        "slug": "senior-radio-concert-wellness-guide.html",
        "category": "본방송 활용법 · 청취 건강",
        "title": "화·금 저녁 6시 김쌤의영웅라디오 15분 본방송 100% 즐기는 법 & 눈·목 편안한 청취 건강 수칙",
        "desc": "매주 화요일·금요일 저녁 6시 유튜브 @김쌤의영웅라디오 15분 정규 방송을 자녀 도움 없이 큰 글씨로 편하게 즐기시는 방법과 스마트폰 청취 시 눈·목 건강 수칙을 안내해 드립니다.",
        "highlight_box_title": "📅 기억하기 쉬운 『김쌤의영웅라디오』 주간 약속",
        "highlight_box_body": "• 정규 본방송: 매주 화요일 · 금요일 저녁 6시 (유튜브 @김쌤의영웅라디오 15분 힐링 라디오)\n• 사랑방 다시듣기: paradise-hero.com 에서 연중무휴 24시간 무료 연속 청취 & 음성 받아쓰기 사연 접수",
        "body_paragraphs": [
            "매주 화요일과 금요일 저녁 6시가 되면 유튜브 『@김쌤의영웅라디오』에서는 한 주 동안 전국 어머님·아버님들께서 보내주신 귀한 인생 사연과 가상 트로트 가수 백운호의 〈어머니의 봄날〉·〈백운호 연가〉·〈다시 피는 동백꽃〉을 엮은 15분 정규 라디오 본방송이 문을 엽니다.",
            "자녀들에게 매번 물어보지 않으셔도 혼자서 편하게 이용하실 수 있도록 모든 기능을 큼직하게 준비했습니다. 첫째, 글씨가 작게 느껴지실 때는 화면 오른쪽 위 '글자 크게' 버튼을 눌러 22px부터 30px 특대 글씨까지 3단계로 키워 보세요. 둘째, 작은 휴대폰 자판 치기가 번거로우실 때는 사연 보내기(story.html)의 황금색 '말씀으로 편하게 적기' 마이크 버튼을 누르고 천천히 말씀만 하시면 사연이 저절로 글자로 적힙니다.",
            "좋은 노래와 사연을 오래오래 건강하게 즐기시려면 눈과 목을 지키는 작은 생활 습관도 꼭 함께 챙겨 주세요. 스마트폰 화면은 눈에서 30cm 이상 거리를 두시고, 50분 정도 라디오나 사연을 보신 뒤에는 10분간 창밖 먼 산이나 하늘을 바라보며 눈의 피로를 풀어주시는 것이 좋습니다. 이어폰 음량은 최대 크기의 60% 이하로 맞추시거나 거실 블루투스 라디오 스피커를 활용하시면 귀가 한결 편안합니다.",
            "또한 실내 난방이나 환절기 건조한 공기로 목이 칼칼할 때 백운호의 노래를 따라 부르시려면, 진한 커피 대신 체온과 비슷한 미지근한 물이나 따뜻한 도라지배즙 차로 성대 점막을 촉촉하게 적셔 주세요. 지역 음악회나 나들이에 나서실 때는 가벼운 메모리폼 방석과 경량 보온 숄 하나만 챙기셔도 허리와 체온을 든든하게 보호하실 수 있습니다.",
        ],
        "kakao_quote": "📻 화·금 저녁 6시 김쌤의영웅라디오 100% 즐기는 법과 눈·목 편안한 청취 건강 수칙입니다.",
        "faqs": [
            (
                "화·금 저녁 6시 본방송 소식을 잊지 않고 받아볼 수 있나요?",
                "메인 홈(index.html#hero-passwordless-club-card)의 '비밀번호 없는 3초 무료 우편함'에 이메일 주소만 적어두시면 새 방송과 큰 글씨 건강 편지를 정직하게 보내드리며 언제든 1클릭 수신거부가 가능합니다.",
            ),
            (
                "카카오톡 안에서 열었더니 음성 받아쓰기 마이크가 안 켜질 때는 어떻게 하나요?",
                "카카오톡 내부 임시 창에서는 휴대폰 보안 정책상 마이크가 제한될 수 있어, 안내창의 '크롬(Chrome)으로 열기' 또는 'Safari로 열기'를 누르시면 음성 받아쓰기가 시원하게 작동합니다.",
            ),
        ],
    },
]


def _select_best_two_shop_cards(col: Dict[str, Any]) -> List[Dict[str, str]]:
    slug = str(col.get("slug") or "")
    if "wellness" in slug:
        return [
            {
                "img": "/assets/shop/item_doraji.svg",
                "tag": "청취 건강 케어",
                "name": "목이 편안한 도라지배즙 스틱",
                "reason": "백운호 애창곡을 따라 부르실 때 칼칼한 목을 부드럽고 촉촉하게 지켜드립니다.",
                "url": "https://cshop.naver.com/paradiseshop",
                "btn_bg": "#03c75a",
                "btn_label": "🟢 공식 판매처 보러가기 (네이버페이)",
            },
            {
                "img": "/assets/shop/item_lutein.svg",
                "tag": "청취 건강 케어",
                "name": "눈 침침함 케어 루테인 지아잔틴",
                "reason": "스마트폰 큰 글씨 화면으로 사연과 가사를 보실 때 눈 건강 관리를 도와드립니다.",
                "url": "https://link.coupang.com/re/AFFSRP?lptag=AF7865143&subid=paradisehero_col&pageKey=%EB%A3%A8%ED%85%8C%EC%9D%B8+%EC%A7%80%EC%95%84%EC%9E%94%ED%8B%B4",
                "btn_bg": "#b91c1c",
                "btn_label": "🚀 공식 판매처 보러가기 (쿠팡)",
            },
        ]
    if "camellia" in slug:
        return [
            {
                "img": "/assets/shop/item_cushion.svg",
                "tag": "공연·나들이 준비물",
                "name": "3시간 공연장 푹신 메모리폼 방석",
                "reason": "음악회나 나들이 좌석에 오래 앉아 계셔도 허리와 엉덩이 부담을 덜어주는 접이식 방석입니다.",
                "url": "https://cshop.naver.com/paradiseshop",
                "btn_bg": "#03c75a",
                "btn_label": "🟢 공식 판매처 보러가기 (네이버페이)",
            },
            {
                "img": "/assets/shop/item_shawl.svg",
                "tag": "공연·나들이 준비물",
                "name": "환절기 경량 보온 숄·무릎담요",
                "reason": "실내외 온도 차이나 산책길 바람에 어깨와 무릎을 포근하게 감싸줍니다.",
                "url": "https://link.coupang.com/re/AFFSRP?lptag=AF7865143&subid=paradisehero_col&pageKey=%EA%B2%BD%EB%9F%89+%EB%B3%B4%EC%98%A8+%EC%88%84+%EB%AC%B4%EB%A6%8E%EB%8B%B4%EC%9A%94",
                "btn_bg": "#b91c1c",
                "btn_label": "🚀 공식 판매처 보러가기 (쿠팡)",
            },
        ]
    return [
        {
            "img": "/assets/shop/item_speaker.svg",
            "tag": "음반·청취 필수품",
            "name": "백운호·정통 트로트 감상용 효도 블루투스 라디오 스피커",
            "reason": "큼직한 버튼 하나로 거실과 부엌에서 풍성한 중저음 라디오를 편안하게 들으실 수 있습니다.",
            "url": "https://cshop.naver.com/paradiseshop",
            "btn_bg": "#03c75a",
            "btn_label": "🟢 공식 판매처 보러가기 (네이버페이)",
        },
        {
            "img": "/assets/shop/item_battery.svg",
            "tag": "음반·청취 필수품",
            "name": "라디오 장시간 청취 대용량 보조배터리",
            "reason": "공원 산책길이나 외출 중에도 배터리 걱정 없이 라디오 사연을 연속 청취하실 수 있습니다.",
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


def _render_related_columns_html(current_slug: str) -> str:
    links_html = ""
    for item in SENIOR_COLUMNS:
        if item["slug"] == current_slug:
            continue
        links_html += (
            f'<a class="related-col-link" href="/columns/{item["slug"]}">'
            f'<span class="related-col-cat">{html.escape(item["category"])}</span>'
            f'<span class="related-col-title">{html.escape(item["title"])}</span>'
            f'</a>\n'
        )
    return f"""
    <section class="related-box" aria-label="백운호 사랑방 다른 큰 글씨 편지 읽기">
      <h2 style="font-size:1.22em;color:var(--gold);margin:0 0 14px;">📖 이어 읽기 좋은 백운호 사랑방 큰 글씨 편지</h2>
      <div class="related-col-list">
        {links_html}
      </div>
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
                    "sameAs": OFFICIAL_SAME_AS,
                    "author": {
                        "@type": "Organization",
                        "name": "김쌤의영웅라디오 가족 사랑방",
                        "url": f"https://{HOST}/",
                        "sameAs": OFFICIAL_SAME_AS,
                    },
                    "publisher": {
                        "@type": "Organization",
                        "name": "유튜브 @김쌤의영웅라디오 가족 사랑방 · 가상 트로트 가수 백운호 라운지",
                        "url": f"https://{HOST}/",
                        "sameAs": OFFICIAL_SAME_AS,
                    },
                },
                {"@type": "FAQPage", "mainEntity": faq_entities},
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "김쌤의영웅라디오 홈", "item": f"https://{HOST}/"},
                        {"@type": "ListItem", "position": 2, "name": "백운호 큰 글씨 명곡·건강 편지함", "item": f"https://{HOST}/columns/"},
                        {"@type": "ListItem", "position": 3, "name": col["title"], "item": canonical_url},
                    ],
                },
            ],
        },
        ensure_ascii=False,
    )

    best_two_cards = _select_best_two_shop_cards(col)
    mid_shop_html = _render_two_card_shop_html(best_two_cards, "김쌤의 콘서트·응원 안심 준비물관 추천 2선")
    highlight_html = ""
    if col.get("highlight_box_title") and col.get("highlight_box_body"):
        hb_lines = "<br />".join(html.escape(line) for line in str(col["highlight_box_body"]).split("\n"))
        highlight_html = f"""
      <div class="lyric-note-box">
        <div class="lyric-note-title">{html.escape(str(col['highlight_box_title']))}</div>
        <p class="lyric-note-body">{hb_lines}</p>
      </div>"""

    paras = col["body_paragraphs"]
    if len(paras) >= 2:
        paras_html = (
            f"<p>{html.escape(paras[0])}</p>\n"
            f"{highlight_html}\n"
            f"<p>{html.escape(paras[1])}</p>\n"
            f"{mid_shop_html}\n"
            + "\n".join(f"<p>{html.escape(p)}</p>" for p in paras[2:])
        )
    else:
        paras_html = highlight_html + "\n" + "\n".join(f"<p>{html.escape(p)}</p>" for p in paras) + "\n" + mid_shop_html

    faqs_html = "\n".join(
        f'<div class="faq-item"><h3>Q. {html.escape(q)}</h3><p>{html.escape(a)}</p></div>'
        for q, a in col["faqs"]
    )
    related_html = _render_related_columns_html(col["slug"])
    share_msg_js = json.dumps(f"{col['kakao_quote']}\n👉 큰 글씨로 바로 읽기: {canonical_url}", ensure_ascii=False)

    raw_letter_card = build_html_morning_letter_and_stamp_card(
        div_code="HERO",
        date_str=today_iso,
        empathy_line_1="존경하는 사랑방 어머님·아버님, 간밤에 주무시는 동안 어깨나 무릎은 시리지 않으셨는지요? 아침 창문을 열며 가장 먼저 가족분들의 평안과 건강부터 여쭙습니다.",
        empathy_line_2="가족을 위해 평생을 바치신 어머님·아버님이 우리 인생의 진짜 영웅이십니다. 오늘도 김쌤의영웅라디오와 가상 트로트 가수 백운호가 따뜻하게 곁을 지키겠습니다.",
        mission_text="편지를 읽으신 뒤 목을 적시는 따뜻한 물 한 잔을 천천히 드시고, 아래 초록색 '사랑방 출석 도장' 버튼을 한 번 눌러 오늘의 기분 좋은 동행을 남겨 보세요.",
    )
    hero_letter_stamp_html = re.sub(
        r"fetch\('https://[^']+/hit/[^;]+;",
        "if (window.hitHeroBeacon) { window.hitHeroBeacon(beaconPrefix); }",
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
    .brand {{ font-size: 24px; font-weight: 900; color: var(--gold); min-height: 60px; display: inline-flex; align-items: center; }}
    .font-controls {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    .font-btn {{ min-height: 60px; min-width: 92px; padding: 10px 16px; font-size: 20px; font-weight: 800; border-radius: 12px; border: 2px solid var(--gold); background: #102a20; color: #fff; cursor: pointer; }}
    .font-btn.active {{ background: var(--gold); color: #05130e; }}
    .wrap {{ max-width: 860px; margin: 0 auto; padding: 28px 20px 76px; }}
    .badge {{ display: inline-block; background: #1b4332; color: #fde68a; border: 1px solid var(--gold); padding: 6px 16px; border-radius: 999px; font-size: 20px; font-weight: 800; }}
    h1 {{ font-size: 1.45em; line-height: 1.4; color: #ffffff; margin: 16px 0 12px; }}
    .date-line {{ color: var(--muted); font-size: 0.92em; margin-bottom: 18px; padding-bottom: 14px; border-bottom: 1px solid #2d6a4f; }}
    .honesty-box {{ background: #fffdf5; color: #451a03; border: 1.5px solid #d97706; border-radius: 999px; padding: 8px 18px; font-weight: 700; font-size: 17px; margin-bottom: 18px; line-height: 1.45; text-align: center; }}
    .col-footer {{ background: #05130e; border-top: 3px solid var(--gold); padding: 32px 20px 64px; margin-top: 36px; text-align: center; }}
    .col-footer-inner {{ max-width: 860px; margin: 0 auto; }}
    .col-sns-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; margin: 18px 0; }}
    .col-sns-pill {{ display: inline-flex; align-items: center; justify-content: center; gap: 8px; min-height: 64px; padding: 12px 20px; border-radius: 999px; font-size: 20px; font-weight: 900; color: #ffffff !important; border: 2px solid #fde68a; text-decoration: none; }}
    .col-sns-yt {{ background: linear-gradient(135deg, #991b1b, #dc2626); }}
    .col-sns-ig {{ background: linear-gradient(135deg, #831843, #be185d 55%, #d97706); }}
    .col-footer-nav {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin: 16px 0; }}
    .col-footer-nav a {{ display: inline-flex; align-items: center; justify-content: center; min-height: 60px; padding: 10px 18px; border-radius: 999px; border: 1.5px solid var(--gold); background: #102a20; color: var(--gold); font-size: 18px; font-weight: 800; }}
    .lyric-note-box {{ background: #143628; border-left: 6px solid var(--gold); border-radius: 14px; padding: 18px 20px; margin: 22px 0; }}
    .lyric-note-title {{ font-size: 1.04em; font-weight: 900; color: #fde68a; margin-bottom: 8px; }}
    .lyric-note-body {{ margin: 0 !important; color: #ecfdf5 !important; font-weight: 700; line-height: 1.7; }}
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
    .related-box {{ background: var(--card); border: 2px solid #2d6a4f; border-radius: 18px; padding: 22px; margin: 28px 0; }}
    .related-col-list {{ display: grid; gap: 12px; }}
    .related-col-link {{ display: flex; flex-direction: column; justify-content: center; gap: 4px; min-height: 66px; padding: 14px 16px; border-radius: 14px; background: #081c15; border: 1.5px solid #34d399; color: #ffffff; }}
    .related-col-cat {{ font-size: 17px; font-weight: 800; color: #fde68a; }}
    .related-col-title {{ font-size: 20px; font-weight: 800; color: #ffffff; line-height: 1.4; }}
    .curation-box {{ background: #102a20; border: 2px solid var(--gold); border-radius: 18px; padding: 24px; margin: 32px 0; }}
    .npay-btn {{ display: flex; align-items: center; justify-content: center; text-align: center; min-height: 68px; padding: 14px 18px; border-radius: 14px; font-size: 21px; font-weight: 900; background: #03c75a; color: #ffffff; margin-bottom: 14px; }}
    .cp-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }}
    .cp-btn {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; min-height: 64px; padding: 12px 16px; border-radius: 12px; font-size: 20px; font-weight: 800; background: #081c15; border: 2px solid #6ee7b7; color: #ffffff; }}
    .faq-item {{ background: var(--card); border: 1px solid #2d6a4f; border-radius: 14px; padding: 20px; margin-bottom: 16px; }}
    .faq-item h3 {{ margin: 0 0 10px; color: var(--gold); font-size: 1.05em; }}
    .faq-item p {{ margin: 0; font-size: 0.98em; }}
    .partner-box {{ background: #102a20; border: 2px solid #34d399; border-radius: 18px; padding: 22px; margin-top: 28px; }}
    .partner-btn {{ display: inline-flex; align-items: center; justify-content: center; width: 100%; min-height: 64px; padding: 12px 18px; border-radius: 14px; border: 2px solid var(--gold); background: #081c15; color: #fde68a; font-size: 20px; font-weight: 800; margin-top: 10px; }}
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

    {related_html}

    <section aria-label="사랑방 주요 메뉴 바로가기">
      <h2 style="font-size:1.25em;color:var(--gold);margin-bottom:14px;">김쌤의영웅라디오 가족 사랑방 바로가기</h2>
      <div class="funnel-grid">
        <a class="funnel-btn" href="/radio.html">📻 사연 라디오 1~5화 연속 듣기</a>
        <a class="funnel-btn" href="/stream.html">🎵 백운호 6대 대표곡 감상관</a>
        <a class="funnel-btn" href="/booth.html">📸 백운호 6벌 의상 무료 기념촬영</a>
        <a class="funnel-btn gold" href="/vip.html">🎁 카톡 안부카드·큰글씨 달력 선물관</a>
        <a class="funnel-btn" href="/community.html">💬 소통 사랑방 1줄 응원·공감 박수</a>
        <a class="funnel-btn" href="/story.html">💌 라디오 사연 보내기 (음성 지원)</a>
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

    <section id="hero-brand-partnership-box" class="partner-box" aria-label="공식 브랜드 협찬 및 제휴 문의">
      <h2 style="font-size:1.15em;color:var(--gold);margin:0 0 8px;">🤝 공식 브랜드 협찬 · 라디오 캠페인 제휴 창구</h2>
      <p style="margin:0;color:var(--muted);font-size:0.95em;">5070 시니어 청취자분들께 유익한 음향·공연·청취 건강 브랜드 협찬 및 사연 캠페인 문의는 공식 이메일 창구로 연락해 주세요.</p>
      <a class="partner-btn" href="mailto:beable9489@gmail.com">📧 공식 제휴·사연 문의: beable9489@gmail.com</a>
    </section>
  </main>
  <footer class="col-footer" role="contentinfo">
    <div class="col-footer-inner">
      <p style="margin:0 0 8px;font-size:21px;font-weight:900;color:var(--gold);">📻 유튜브 @김쌤의영웅라디오 가족 사랑방 · 가상 트로트 가수 백운호 라운지</p>
      <p style="margin:0 0 14px;font-size:18px;color:var(--muted);">공식 유튜브와 인스타그램에서도 매일 따뜻한 트로트와 인생 사연을 만나보세요.</p>
      <div class="col-sns-grid" aria-label="공식 SNS 바로가기">
        <a class="col-sns-pill col-sns-yt" href="https://www.youtube.com/@김쌤의영웅라디오" target="_blank" rel="noopener noreferrer">📺 공식 유튜브 @김쌤의영웅라디오 👉</a>
        <a class="col-sns-pill col-sns-ig" href="https://www.instagram.com/paradise_hero1/" target="_blank" rel="noopener noreferrer">📸 공식 인스타그램 @paradise_hero1 👉</a>
      </div>
      <nav class="col-footer-nav" aria-label="하단 바로가기">
        <a href="/">🏠 홈</a>
        <a href="/radio.html">📻 방송듣기</a>
        <a href="/stream.html">🎵 백운호곡</a>
        <a href="/community.html">💬 사랑방</a>
        <a href="/story.html">💌 사연접수</a>
        <a href="/booth.html">📸 기념촬영관</a>
        <a href="/vip.html">🎁 무료선물관</a>
        <a href="/columns/">📖 편지함목록</a>
      </nav>
      <p style="margin:14px 0 0;font-size:16px;color:#9ca3af;">© 2026 김쌤의영웅라디오 가족 사랑방 (paradise-hero.com) · Dream Company 4사업부</p>
    </div>
  </footer>
  <script src="/js/hq_member_crm_client.js" defer></script>
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

    allowed_files = {col["slug"] for col in SENIOR_COLUMNS} | {"index.html"}
    for existing_fp in COLUMNS_DIR.glob("*.html"):
        if existing_fp.name not in allowed_files:
            existing_fp.unlink()

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

    hub_ld_json = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "가상 트로트 가수 백운호 탄생 이야기 · 명곡 해설 & 청취 건강 편지함 | 김쌤의영웅라디오",
            "description": "5070 시니어 가족분들을 위한 오리지널 가상 트로트 가수 백운호(白雲湖) 탄생 이야기와 대표곡 〈어머니의 봄날〉·〈백운호 연가〉·〈다시 피는 동백꽃〉 해설 및 청취 건강 편지 모음입니다.",
            "url": f"https://{HOST}/columns/",
            "inLanguage": "ko-KR",
            "sameAs": OFFICIAL_SAME_AS,
            "publisher": {
                "@type": "Organization",
                "name": "유튜브 @김쌤의영웅라디오 가족 사랑방 · 가상 트로트 가수 백운호 라운지",
                "url": f"https://{HOST}/",
                "sameAs": OFFICIAL_SAME_AS,
            },
        },
        ensure_ascii=False,
    )

    hub_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>가상 트로트 가수 백운호 탄생 이야기 · 명곡 해설 &amp; 청취 건강 편지함 | 김쌤의영웅라디오</title>
  <meta name="description" content="5070 시니어 가족분들을 위한 오리지널 가상 트로트 가수 백운호(白雲湖) 탄생 이야기와 대표곡 〈어머니의 봄날〉·〈백운호 연가〉·〈다시 피는 동백꽃〉 해설 및 청취 건강 편지 모음입니다." />
  <link rel="canonical" href="https://{HOST}/columns/" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="가상 트로트 가수 백운호 탄생 이야기 · 명곡 해설 &amp; 청취 건강 편지함 | 김쌤의영웅라디오" />
  <meta property="og:description" content="5070 시니어 가족분들을 위한 오리지널 가상 트로트 가수 백운호(白雲湖) 탄생 이야기와 대표곡 〈어머니의 봄날〉·〈백운호 연가〉·〈다시 피는 동백꽃〉 해설 및 청취 건강 편지 모음입니다." />
  <meta property="og:url" content="https://{HOST}/columns/" />
  <meta property="og:image" content="https://{HOST}/assets/og_booth_share.jpg" />
  <link rel="alternate" type="application/rss+xml" title="김쌤의영웅라디오 RSS" href="https://{HOST}/rss.xml" />
  <script type="application/ld+json">{hub_ld_json}</script>
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
    .honesty-box {{ background:#fffdf5; color:#451a03; border:1.5px solid #d97706; border-radius:999px; padding:8px 18px; font-weight:700; font-size:17px; margin-bottom:18px; line-height:1.45; text-align:center; }}
    .nav-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:12px; margin-top:20px; }}
    .nav-btn {{ display:flex; align-items:center; justify-content:center; min-height:62px; padding:12px 16px; border-radius:12px; border:2px solid #34d399; background:#081c15; color:#ffffff; font-weight:800; text-align:center; }}
    .hub-footer {{ background:#05130e; border-top:3px solid #fbbf24; padding:32px 20px 64px; margin-top:36px; text-align:center; }}
    .hub-sns-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:12px; max-width:860px; margin:16px auto; }}
    .hub-sns-pill {{ display:inline-flex; align-items:center; justify-content:center; gap:8px; min-height:64px; padding:12px 20px; border-radius:999px; font-size:20px; font-weight:900; color:#ffffff !important; border:2px solid #fde68a; text-decoration:none; }}
  </style>
</head>
<body>
  <header class="topbar">
    <a href="/" style="font-size:24px;font-weight:900;color:#fbbf24;min-height:60px;display:inline-flex;align-items:center;">📻 김쌤의영웅라디오 홈으로</a>
    <div style="display:flex;gap:8px;flex-wrap:wrap;">
      <button type="button" id="btn-font-scaler" class="font-btn" onclick="document.documentElement.style.setProperty('--base-font','22px')">보통</button>
      <button type="button" class="font-btn" onclick="document.documentElement.style.setProperty('--base-font','26px')">크게</button>
      <button type="button" class="font-btn" onclick="document.documentElement.style.setProperty('--base-font','30px')">특대</button>
    </div>
  </header>
  <main class="wrap">
    <h1 style="font-size:1.5em;color:#fde68a;margin-bottom:8px;">💌 가상 트로트 가수 『백운호』 탄생 이야기 · 대표곡 해설 편지함</h1>
    <p style="color:#d1fae5;margin-top:0;margin-bottom:18px;">〈어머니의 봄날〉 · 〈백운호 연가〉 · 〈다시 피는 동백꽃〉 이야기와 청취 건강 수칙을 돋보기 없이 큰 글씨로 만나보세요.</p>
    <div class="honesty-box">{HONESTY_BADGE_TEXT}</div>
    {cards_html}
    <section class="card" aria-label="사랑방 주요 바로가기">
      <span class="badge">📻 김쌤의영웅라디오 가족 사랑방</span>
      <h2>노래 감상과 사연 소통도 큰 버튼으로 편하게 즐기세요</h2>
      <div class="nav-grid">
        <a class="nav-btn" href="/radio.html">📻 1~5화 사연 라디오 듣기</a>
        <a class="nav-btn" href="/stream.html">🎵 백운호 6대 대표곡 감상</a>
        <a class="nav-btn" href="/community.html">💬 1줄 응원 &amp; 공감 박수</a>
        <a class="nav-btn" href="/story.html">💌 라디오 사연 보내기</a>
        <a class="nav-btn" href="/booth.html">📸 백운호 6벌 의상 촬영관</a>
        <a class="nav-btn" href="/vip.html">🎁 무료 안부카드 선물관</a>
      </div>
    </section>
    <section class="card" style="border-color:#fbbf24;margin-top:28px;">
      <span class="badge">💚 에디터 큐레이션 · 청취 &amp; 공연 준비물</span>
      <h2>💚 김쌤의 콘서트·응원 안심 준비물관</h2>
      <p>블루투스 라디오 스피커, 보조배터리, 이어폰, 공연장 방석, 보온 숄, 루테인, 도라지배즙 등 시니어 청취·공연 필수품 7종을 만나보세요.</p>
      <p style="font-size:0.9em;color:#fde68a;font-weight:800;margin:0 0 12px;">{FTC_DISCLOSURE_TEXT}</p>
      <a class="read-btn" href="https://cshop.naver.com/paradiseshop" target="_blank" rel="noopener noreferrer sponsored" style="background:#03c75a;color:#ffffff;width:100%;margin-bottom:10px;">💚 김쌤의 콘서트·응원 안심 준비물관 (네이버페이 공식관) 👉</a>
      <a class="read-btn" href="https://influencers.coupang.com/s/paradisehero" target="_blank" rel="noopener noreferrer sponsored" style="background:#b91c1c;color:#ffffff;width:100%;">📻 김쌤의 콘서트·응원 안심 준비물관 (쿠팡 공식관) 👉</a>
    </section>
    <section id="hero-brand-partnership-box" class="card" style="border-color:#34d399;">
      <span class="badge">🤝 공식 브랜드 협찬 · 제휴 문의</span>
      <h2>유튜브 @김쌤의영웅라디오 &amp; 시니어 브랜드 제휴 안내</h2>
      <p>음향·공연·청취 건강 브랜드 협찬 및 라디오 사연 캠페인 문의: <a href="mailto:beable9489@gmail.com" style="font-weight:900;text-decoration:underline;">beable9489@gmail.com</a></p>
    </section>
  </main>
  <footer class="hub-footer" role="contentinfo">
    <p style="margin:0 0 8px;font-size:21px;font-weight:900;color:#fbbf24;">📻 유튜브 @김쌤의영웅라디오 가족 사랑방 · 가상 트로트 가수 백운호 라운지</p>
    <div class="hub-sns-grid" aria-label="공식 SNS 바로가기">
      <a class="hub-sns-pill" style="background:linear-gradient(135deg,#991b1b,#dc2626);" href="https://www.youtube.com/@김쌤의영웅라디오" target="_blank" rel="noopener noreferrer">📺 공식 유튜브 @김쌤의영웅라디오 👉</a>
      <a class="hub-sns-pill" style="background:linear-gradient(135deg,#831843,#be185d 55%,#d97706);" href="https://www.instagram.com/paradise_hero1/" target="_blank" rel="noopener noreferrer">📸 공식 인스타그램 @paradise_hero1 👉</a>
    </div>
    <p style="margin:12px 0 0;font-size:16px;color:#9ca3af;">© 2026 김쌤의영웅라디오 가족 사랑방 (paradise-hero.com) · Dream Company 4사업부</p>
  </footer>
  <script src="/js/hq_member_crm_client.js" defer></script>
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
            f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{today_iso}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.90</priority>\n  </url>"
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
        f"> 최종 업데이트: {today_iso} | 5070 시니어 음악 위로·사연 소통 라디오 쉼터 (실존 연예인 팬카페 아님 · 오리지널 가상 트로트 가수 '백운호(白雲湖)' 공식 라운지 · WCAG AAA 20px+ 큰 글씨, 60px+ 터치 버튼).",
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
        f"- 백운호 탄생 이야기 · 명곡 해설 · 청취 건강 편지함: https://{HOST}/columns/",
        "- 공식 유튜브 (@김쌤의영웅라디오): https://www.youtube.com/@김쌤의영웅라디오",
        "- 공식 인스타그램 (@paradise_hero1): https://www.instagram.com/paradise_hero1/",
        "- 공식 제휴·사연 문의: mailto:beable9489@gmail.com",
        "",
        "## 2. 오리지널 가상 트로트 가수 『백운호(白雲湖)』 큰 글씨 칼럼 목록 (/columns/)",
    ]
    for col in SENIOR_COLUMNS:
        llms_lines.append(f"- [{col['title']}](https://{HOST}/columns/{col['slug']})")
    (DIV4_ROOT / "llms.txt").write_text("\n".join(llms_lines) + "\n", encoding="utf-8")

    return url_map


if __name__ == "__main__":
    umap = generate_all_senior_columns_and_feeds()
    print(f"[HERO Senior Columns] Generated {len(SENIOR_COLUMNS)} pure Baek Woon-ho WCAG AAA columns & synced {len(umap)} canonical URLs.")
