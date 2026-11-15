#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
4사업부/scripts/hero_auto_promotion_engine.py (v2.0 — Zero-Ban & 403 Recovery Edition)
====================================================================================
파라다이스히어로 · 김쌤의 영웅라디오 (https://paradise-hero.com) 비영상 글 자동화 엔진:
  1. 황영웅 전용 뉴스룸 데이터 갱신 (`fetch_trot_news.py`, 타 가수·금지어 0건 검증).
  2. 시니어 WCAG AAA 큰 글씨(22px~30px) 명곡 해설·건강 편지(`/columns/*.html`) 및 `rss.xml`/`sitemap.xml`/`llms.txt` 갱신.
  3. 영구 단일 계정(`data/hero_telegraph_account.json`) 재사용 + 일 1회 고유 Telegra.ph 칼럼 발행 (매시간 일회용 계정 생성 스팸 제거!).
  4. SHA-256 변경분 전용 IndexNow + HTTP 403 자동 48시간 쿨다운 보호 (`indexnow_delta_gate.py`).
  5. 카카오톡 단톡방 / 네이버 밴드 공유용 큰 글씨 편지 킷 + Threads 2단 스레드 자동 생성 (`outbox/YYYY-MM-DD/HERO/`).
"""

from __future__ import annotations

import datetime
import json
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DIV4_ROOT = pathlib.Path(__file__).resolve().parent.parent
HQ_TEXT_DIR = DIV4_ROOT.parent / "text_automation_hq"
if str(HQ_TEXT_DIR) not in sys.path:
    sys.path.insert(0, str(HQ_TEXT_DIR))

from indexnow_delta_gate import (  # noqa: E402
    ping_websub_if_feed_changed,
    publish_daily_unique_telegraph_summary,
    submit_delta_indexnow,
)
from live_web_deployer import deploy_division_live  # noqa: E402
from official_api_syndicator import dispatch_zero_ban_text_bundle  # noqa: E402
from generate_senior_columns_and_feeds import (  # noqa: E402
    SENIOR_COLUMNS,
    generate_all_senior_columns_and_feeds,
)

HOST = "paradise-hero.com"
KEY = "7d41a93e60b24f8c851924de3c90a628"
TELEGRAPH_ACCT_PATH = DIV4_ROOT / "data" / "hero_telegraph_account.json"
STATUS_LOG_PATH = DIV4_ROOT / "data" / "hero_promotion_status.json"


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    today_str = datetime.date.today().isoformat()

    # 1. Refresh clean Hwang Young-woong news dataset
    news_py = DIV4_ROOT / "scripts" / "fetch_trot_news.py"
    if news_py.exists():
        subprocess.run([sys.executable, str(news_py), "--verify"], cwd=str(DIV4_ROOT), check=False, capture_output=True)

    # 2. Generate WCAG AAA Senior Columns + dynamic RSS/Sitemap/llms.txt + deploy live
    url_map = generate_all_senior_columns_and_feeds()
    deploy_res = deploy_division_live("HERO", dry_run=dry_run)

    # 3. Rotate daily column for 1x/day Telegraph & Kakao/Band/Threads pack
    day_ord = datetime.date.today().toordinal()
    col = SENIOR_COLUMNS[day_ord % len(SENIOR_COLUMNS)]
    canonical_url = f"https://{HOST}/columns/{col['slug']}"
    title = f"[김쌤의 영웅라디오 {today_str}] {col['title']}"

    nodes = [
        {"tag": "h3", "children": [col["title"]]},
        {"tag": "p", "children": [col["body_paragraphs"][0]]},
        {"tag": "p", "children": [col["body_paragraphs"][1]]},
        {
            "tag": "p",
            "children": [
                "돋보기 없이 시원한 큰 글씨(22px~30px) 편지 전문 읽기 & 24시간 영웅라디오 무료 감상: ",
                {"tag": "a", "attrs": {"href": canonical_url}, "children": [canonical_url]},
            ],
        },
        {
            "tag": "p",
            "children": [
                "카드번호 입력 없는 네이버페이 1초 결제 공식 안심셀렉트샵: ",
                {"tag": "a", "attrs": {"href": "https://cshop.naver.com/paradiseshop"}, "children": ["https://cshop.naver.com/paradiseshop"]},
            ],
        },
        {
            "tag": "p",
            "children": [
                "황영웅 님 10종 의상 무제한 무료 투샷 사진관 바로가기: ",
                {"tag": "a", "attrs": {"href": f"https://{HOST}/booth.html"}, "children": [f"https://{HOST}/booth.html"]},
            ],
        },
    ]

    tg_res = publish_daily_unique_telegraph_summary(
        div_code="HERO",
        account_file=TELEGRAPH_ACCT_PATH,
        short_name="ParadiseHero",
        author_name="김쌤의 영웅라디오 · 파라다이스히어로",
        author_url=f"https://{HOST}/",
        title=title,
        content_nodes=nodes,
        canonical_url=canonical_url,
        dry_run=dry_run,
    )

    prev_status = {}
    if STATUS_LOG_PATH.exists():
        try:
            prev_status = json.loads(STATUS_LOG_PATH.read_text(encoding="utf-8"))
        except Exception:
            prev_status = {}
    tg_url = tg_res.get("url") or prev_status.get("telegraph_url", "")

    main_hook = (
        f"{col['kakao_quote']}\n\n"
        f"유튜브 라디오와 24시간 음악 쉼터에서 매일 다정한 목소리와 사연으로 어머님·아버님 곁을 지킵니다. #황영웅 #파라다이스"
    )[:275]

    reply_link = (
        f"💚 돋보기 없이 시원한 큰 글씨 편지 전문 & 원터치 공식 쇼핑·무료 사진관 바로가기:\n"
        f"{canonical_url}?utm_source=social_thread&utm_medium=organic"
    )

    kakao_groupchat_3line = (
        f"{col['kakao_quote']}\n"
        f"👉 큰 글씨 편지 & 24시간 영웅라디오: {canonical_url}?utm_source=kakao_3line\n"
        f"🟢 카드 입력 없는 네이버페이 1초 공식샵: https://cshop.naver.com/paradiseshop\n"
        f"🚀 내일 도착 쿠팡 응원준비물·음반 공식관: https://influencers.coupang.com/s/paradisehero\n"
    )

    kakao_band_letter = (
        f"💌 [김쌤의 영웅라디오 다정한 안부 편지 — {today_str}]\n\n"
        f"존경하는 파라다이스 어머님·아버님, 오늘 하루도 평안하셨는지요?\n"
        f"{col['kakao_quote']}\n\n"
        f"{col['body_paragraphs'][0]}\n\n"
        f"📖 돋보기 없이 시원한 큰 글씨로 편지 끝까지 읽기:\n{canonical_url}?utm_source=kakao_band\n\n"
        f"📸 황영웅 님 10종 의상 무료 투샷 기념사진 찍기:\nhttps://{HOST}/booth.html?utm_source=kakao_band\n\n"
        f"🟢 복잡한 카드번호 입력 없이 1초 결제! 김쌤 네이버페이 안심셀렉트샵:\nhttps://cshop.naver.com/paradiseshop\n\n"
        f"🚀 내일 문앞 도착! 정품 음반·에메랄드 응원준비물·건강선물 쿠팡 공식관:\nhttps://influencers.coupang.com/s/paradisehero\n"
    )

    naver_fancafe_greeting = (
        f"# [큰 글씨 안부 편지] {col['title']}\n\n"
        f"반갑습니다 파라다이스 가족 여러분! 언제나 어머님·아버님 편에 서서 따뜻한 노래 이야기를 전해드리는 김쌤입니다.\n\n"
        + "\n\n".join(col["body_paragraphs"])
        + "\n\n---\n"
        + f"- 📻 **24시간 연속 영웅라디오 & 큰 글씨 원문 보기**: {canonical_url}?utm_source=fancafe\n"
        + f"- 📸 **무료 10종 의상 투샷 기념사진관**: https://{HOST}/booth.html?utm_source=fancafe\n"
        + "- 🟢 **김쌤 네이버페이 원터치 안심셀렉트샵**: https://cshop.naver.com/paradiseshop\n"
        + f"- 🛍️ **YES24 차트반영 정품음반 · 건강효도선물 · 주말 나들이 통합 혜택관**: https://{HOST}/#senior-curation-market\n"
    )

    longform_md = (
        f"# {col['title']}\n\n"
        + "\n\n".join(col["body_paragraphs"])
        + f"\n\n### 💚 어머님·아버님을 위한 큰 글씨 바로가기\n"
        + f"- 📖 [돋보기 없이 시원한 큰 글씨 원문 & 24시간 라디오]({canonical_url})\n"
        + f"- 📸 [10종 의상 무제한 무료 투샷 기념사진관](https://{HOST}/booth.html)\n"
        + "- 🟢 [카드 입력 없는 네이버페이 1초 결제 공식샵](https://cshop.naver.com/paradiseshop)\n"
        + f"- 🛍️ [정품 음반 · 콘서트 응원준비물 · 관절/목 건강 원터치 혜택관](https://{HOST}/#senior-curation-market)\n"
    )

    yt_pinned_and_community = (
        f"=== [@김쌤의영웅라디오 유튜브 고정 댓글 & 커뮤니티 큰 글씨 공지 · {today_str}] ===\n\n"
        f"💚 {col['kakao_quote']}\n\n"
        f"1️⃣ 돋보기 없이 시원하게 읽는 큰 글씨 사연·건강 편지 전문:\n"
        f"👉 {canonical_url}?utm_source=youtube_pinned\n\n"
        f"2️⃣ 황영웅 님 10종 의상 무제한 무료 투샷 사진관 & 효도 달력 제작소:\n"
        f"👉 https://{HOST}/booth.html?utm_source=youtube_pinned\n\n"
        f"3️⃣ 카드번호 입력 없는 1초 결제! 김쌤 네이버페이 공식 안심셀렉트샵:\n"
        f"👉 https://cshop.naver.com/paradiseshop\n\n"
        f"4️⃣ 내일 바로 도착! 정품 음반·콘서트 응원준비물·건강선물 쿠팡 공식관:\n"
        f"👉 https://influencers.coupang.com/s/paradisehero\n\n"
        f"5️⃣ YES24 차트반영 정품음반 · iHerb 건강직구 · 주말 나들이 티켓 통합 혜택관:\n"
        f"👉 https://{HOST}/#senior-curation-market\n"
    )

    syn_res = dispatch_zero_ban_text_bundle(
        div_code="HERO",
        canonical_domain=HOST,
        canonical_url=canonical_url,
        title=col["title"],
        summary=col["desc"],
        main_social_hook=main_hook,
        reply_social_link=reply_link,
        longform_markdown=longform_md,
        tags=["황영웅", "파라다이스"],
        platform_extras={
            "kakao_groupchat_3line_share.txt": kakao_groupchat_3line,
            "kakao_naver_band_senior_letter.md": kakao_band_letter,
            "naver_fancafe_warm_greeting.md": naver_fancafe_greeting,
            "youtube_pinned_comment_and_community_post.txt": yt_pinned_and_community,
        },
        div_env_path=DIV4_ROOT / ".env",
        dry_run=dry_run,
    )

    idx_res = submit_delta_indexnow(
        div_code="HERO",
        host=HOST,
        key=KEY,
        url_to_filepath=url_map,
        dry_run=dry_run,
    )
    ws_res = (
        {"status": "DRY_RUN"}
        if dry_run
        else ping_websub_if_feed_changed("HERO", f"https://{HOST}/rss.xml", DIV4_ROOT / "rss.xml")
    )

    STATUS_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATUS_LOG_PATH.write_text(
        json.dumps(
            {
                "last_run": datetime.datetime.now().isoformat(),
                "telegraph_url": tg_url,
                "latest_column_url": canonical_url,
                "indexnow": idx_res,
                "websub": ws_res,
                "syndication_status": syn_res.get("status"),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"[HERO Zero-Ban v2] Deploy={deploy_res.get('status')} | Columns={len(SENIOR_COLUMNS)} | Telegraph={tg_url or 'daily-cap'} | "
        f"IndexNow={idx_res.get('status')}({idx_res.get('submitted_count', 0)}/{len(url_map)}) | "
        f"WebSub={ws_res.get('status')} | Syndication={syn_res.get('status')}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
