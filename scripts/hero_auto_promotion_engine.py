#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hero_auto_promotion_engine.py — 4사업부(파라다이스히어로 · 영웅라디오) 비영상 글로벌 홍보 자동화 엔진
=============================================================================================
1. DA88 Telegra.ph 시니어 트롯 팬덤 & 황영웅 [당신 편] 명곡 해설 칼럼 자동 발행 (paradise-hero.com 백링크)
2. IndexNow (Bing / Yandex / Naver 제휴) 실시간 9개 핵심 URL 색인 핑
3. Google WebSub / PubSubHubbub 피드 핑
"""

import datetime
import json
import pathlib
import sys
import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DIV4_ROOT = pathlib.Path(__file__).resolve().parent.parent
HOST = "paradise-hero.com"
KEY = "c75f10bb24814e518712613d9646bca3"


def publish_telegraph_hero_article(today_str: str) -> str:
    try:
        with httpx.Client(timeout=20.0) as client:
            acc = client.post(
                "https://api.telegra.ph/createAccount",
                data={
                    "short_name": "ParadiseHero",
                    "author_name": "김쌤의 영웅라디오 · 파라다이스히어로",
                    "author_url": "https://paradise-hero.com/",
                },
            ).json()
            token = acc.get("result", {}).get("access_token")
            if not token:
                return ""

            title = f"[김쌤의 영웅라디오 {today_str}] 가수 황영웅 정규 1집 '당신 편' 명곡 해설 & 10종 의상 무료 화보 기념사진관 안내"
            content_nodes = [
                {
                    "tag": "h3",
                    "children": ["1. '어머니, 제가 끝까지 당신의 편이 되어드릴게요' — 황영웅 [당신 편] 해설"],
                },
                {
                    "tag": "p",
                    "children": [
                        "전국과 해외에 계신 파라다이스 가족 여러분, 김쌤의 영웅라디오입니다. 가수 황영웅 님의 깊은 중저음 보이스가 빛나는 대표곡 [당신 편]과 24시간 무인 연속 재생 라디오 플레이어는 공식 팬덤 사랑방 ",
                        {"tag": "a", "attrs": {"href": "https://paradise-hero.com/radio.html"}, "children": ["paradise-hero.com/radio.html"]},
                        " 에서 큰 글씨(20px 이상)로 편안하게 감상하실 수 있습니다.",
                    ],
                },
                {
                    "tag": "h3",
                    "children": ["2. 무제한 무료 개방! 가수 황영웅 10대 시그니처 의상 투샷 기념사진관"],
                },
                {
                    "tag": "p",
                    "children": [
                        "에메랄드 벨벳 콘서트 수트, 순백 프린스 턱시도, 심야 라디오 DJ 안경룩 등 가수 황영웅 님의 10대 시그니처 의상 캐릭터와 함께 스마트폰으로 나만의 소장용 투샷 화보 포토카드를 횟수 제한 없이 무료로 촬영해보세요: ",
                        {"tag": "a", "attrs": {"href": "https://paradise-hero.com/booth.html"}, "children": ["https://paradise-hero.com/booth.html"]},
                    ],
                },
                {
                    "tag": "blockquote",
                    "children": ["공식 팬 쉼터 바로가기: https://paradise-hero.com"],
                },
            ]
            page = client.post(
                "https://api.telegra.ph/createPage",
                data={
                    "access_token": token,
                    "title": title,
                    "author_name": "김쌤의 영웅라디오",
                    "author_url": "https://paradise-hero.com/",
                    "content": json.dumps(content_nodes, ensure_ascii=False),
                    "return_content": "false",
                },
            ).json()
            return page.get("result", {}).get("url", "")
    except Exception as e:
        print(f"  ⚠️ Telegra.ph 발행 오류: {e}")
        return ""


def ping_indexnow() -> dict:
    urls = [
        f"https://{HOST}/",
        f"https://{HOST}/story.html",
        f"https://{HOST}/booth.html",
        f"https://{HOST}/photobooth.html",
        f"https://{HOST}/radio.html",
        f"https://{HOST}/community.html",
        f"https://{HOST}/stream.html",
        f"https://{HOST}/vip.html",
        f"https://{HOST}/news.html",
    ]
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": f"https://{HOST}/{KEY}.txt",
        "urlList": urls,
    }
    results = {}
    with httpx.Client(timeout=15.0) as client:
        for name, ep in [
            ("indexnow_api", "https://api.indexnow.org/indexnow"),
            ("bing_indexnow", "https://www.bing.com/indexnow"),
            ("yandex_indexnow", "https://yandex.com/indexnow"),
        ]:
            try:
                r = client.post(ep, json=payload)
                results[name] = r.status_code
            except Exception as e:
                results[name] = str(e)
    return results


def main() -> int:
    today_str = datetime.date.today().isoformat()
    print(f"🚀 [4사업부 파라다이스히어로 · 영웅라디오] 비영상 홍보 자동화 가동 ({today_str})")
    tg_url = publish_telegraph_hero_article(today_str)
    print(f"  ✅ DA88 Telegra.ph 아티클 발행: {tg_url}")
    idx_res = ping_indexnow()
    print(f"  ✅ IndexNow 색인 핑 결과: {idx_res}")

    log_path = DIV4_ROOT / "data" / "hero_promotion_status.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        json.dumps(
            {
                "last_run": datetime.datetime.now().isoformat(),
                "telegraph_url": tg_url,
                "indexnow": idx_res,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
