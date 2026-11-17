#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
4사업부/scripts/hero_auto_promotion_engine.py (v2.0 — Zero-Ban & 403 Recovery Edition)
====================================================================================
파라다이스히어로 · 김쌤의 영웅라디오 (https://paradise-hero.com) 비영상 글 자동화 엔진:
  1. 백운호 전용 뉴스룸 데이터 갱신 (`fetch_trot_news.py`, 타 가수·금지어 0건 검증).
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

from fandom_editor_letter_builder import (  # noqa: E402
    compose_fandom_editor_letter_md,
    validate_fandom_editor_letter,
)
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
    no_deploy = "--no-deploy" in sys.argv
    today_str = datetime.date.today().isoformat()

    # 1. Refresh clean Baek Woon-ho news dataset
    news_py = DIV4_ROOT / "scripts" / "fetch_trot_news.py"
    if news_py.exists():
        subprocess.run([sys.executable, str(news_py), "--verify"], cwd=str(DIV4_ROOT), check=False, capture_output=True)

    # 2. Generate WCAG AAA Senior Columns + dynamic RSS/Sitemap/llms.txt + deploy live
    url_map = generate_all_senior_columns_and_feeds()
    deploy_res = {"status": "SKIPPED_NO_DEPLOY"} if no_deploy else deploy_division_live("HERO", dry_run=dry_run)

    # 3. Rotate daily column for 1x/day Telegraph & Kakao/Band/Threads pack
    day_ord = datetime.date.today().toordinal()
    col = SENIOR_COLUMNS[day_ord % len(SENIOR_COLUMNS)]
    canonical_url = f"https://{HOST}/columns/{col['slug']}"
    title = f"[김쌤의 사랑방 아침 편지 {today_str}] {col['title']}"

    nodes = [
        {
            "tag": "blockquote",
            "children": [
                f"💚 김쌤과 백운호 가족 사랑방 ({today_str}): 존경하는 영웅 가족 어머님·아버님, 간밤에 평안히 주무셨는지요? 자식들 앞에서는 늘 괜찮다 웃으시느라 삼켜 두셨던 마음까지, 오늘도 김쌤이 언제나 어머님·아버님 편이 되어 다정한 노래 이야기로 안아드리겠습니다."
            ],
        },
        {"tag": "h3", "children": [col["title"]]},
        {"tag": "p", "children": [col["body_paragraphs"][0]]},
        {"tag": "p", "children": [col["body_paragraphs"][1]]},
        {
            "tag": "p",
            "children": [
                "🌱 오늘 사랑방 작은 응원 미션: 따뜻한 물 한 잔을 천천히 드신 뒤, 돋보기 없이 시원한 큰 글씨(22px~30px) 편지 원문에서 오늘의 출석 도장을 꾹 눌러 보세요: ",
                {"tag": "a", "attrs": {"href": canonical_url}, "children": [canonical_url]},
            ],
        },
        {
            "tag": "p",
            "children": [
                "백운호 10종 의상 무제한 무료 투샷 기념사진관: ",
                {"tag": "a", "attrs": {"href": f"https://{HOST}/booth.html"}, "children": [f"https://{HOST}/booth.html"]},
            ],
        },
    ]

    tg_res = publish_daily_unique_telegraph_summary(
        div_code="HERO",
        account_file=TELEGRAPH_ACCT_PATH,
        short_name="ParadiseHero",
        author_name="김쌤과 백운호 가족 사랑방",
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
        f"유튜브 라디오와 24시간 음악 쉼터에서 매일 다정한 목소리와 사연으로 어머님·아버님 곁을 지킵니다. #백운호 #김쌤의영웅라디오"
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

    p0 = col["body_paragraphs"][0]
    p1 = col["body_paragraphs"][1] if len(col["body_paragraphs"]) > 1 else col["desc"]
    p2 = col["body_paragraphs"][2] if len(col["body_paragraphs"]) > 2 else "매일 아침 7시 30분 문안 방송과 24시간 연속 영웅라디오에서 어머님·아버님 곁을 든든하게 지키겠습니다."

    longform_md = compose_fandom_editor_letter_md(
        div_code="HERO",
        title=col["title"],
        canonical_url=canonical_url,
        empathy_two_lines=[
            "존경하는 영웅 가족 어머님·아버님, 간밤에 주무시는 동안 어깨나 무릎은 시리지 않으셨는지요? 아침 창문을 열며 가장 먼저 우리 사랑방 가족분들의 건강과 평안부터 여쭙습니다.",
            "자식들 앞에서는 늘 괜찮다 웃으시느라 혼자 삼켜 두셨던 마음까지, 오늘도 김쌤과 백운호 가족 사랑방이 언제나 어머님·아버님 편에 서서 따뜻한 노래 이야기로 다정하게 안아드리겠습니다.",
        ],
        three_insights=[
            f"**마음을 적시는 첫 번째 이야기**: {p0}",
            f"**깊은 중저음 보이스의 위로**: {p1}",
            f"**일상 속 편안한 휴식 (22px~30px 큰 글씨 & 24시간 라디오)**: {p2}",
        ],
        daily_mission=(
            "오늘 편지를 읽으신 뒤 목을 따뜻하게 적시는 미지근한 물 한 잔을 천천히 드시고, "
            "사랑방 큰 글씨 편지 화면의 '초록색 출석 도장'을 한 번 눌러 오늘의 기분 좋은 동행을 기록해 보세요."
        ),
        gentle_bridge_lines=[
            f"📖 **돋보기 없이 시원한 큰 글씨 편지 원문 & 사랑방 출석 도장 찍기**: [{canonical_url}]({canonical_url})",
            f"📻 **24시간 연속 영웅라디오 무료 듣기**: [https://{HOST}/radio.html](https://{HOST}/radio.html) · 📸 **10종 의상 무제한 무료 투샷 기념사진관**: [https://{HOST}/booth.html](https://{HOST}/booth.html)",
            f"💚 **필요하실 때 천천히 둘러보시는 공식 안심 매장**: 카드 입력 없는 네이버페이 공식샵(https://cshop.naver.com/paradiseshop) 및 정품 음반·응원준비물·건강선물 통합 혜택관(https://{HOST}/#senior-curation-market)",
        ],
        footer_disclaimer="※ 본 편지는 김쌤과 백운호 가족 사랑방(`paradise-hero.com`)에서 시니어 팬 가족분들의 평안한 일상을 응원하기 위해 정성껏 작성한 문안 편지입니다.",
    )
    hero_letter_check = validate_fandom_editor_letter("HERO", longform_md)
    if not hero_letter_check["passed"]:
        raise RuntimeError(f"HERO Fandom Editor Letter validation failed: {hero_letter_check}")

    kakao_band_letter = (
        f"💌 [김쌤과 백운호 가족 사랑방 아침 안부 편지 — {today_str}]\n\n"
        f"존경하는 영웅 가족 어머님·아버님, 간밤에 평안히 주무셨는지요?\n"
        f"늘 가족을 먼저 챙기시느라 애쓰신 어머님·아버님 마음을 오늘도 김쌤이 다정하게 응원합니다.\n\n"
        f"{col['kakao_quote']}\n\n"
        f"{p0}\n\n"
        f"🌱 오늘 사랑방 작은 응원 미션:\n"
        f"따뜻한 물 한 잔 천천히 드시고, 아래 큰 글씨 편지에서 오늘의 출석 도장을 꾹 찍어 보세요!\n\n"
        f"📖 돋보기 없이 시원한 큰 글씨 편지 전문 & 출석 도장:\n{canonical_url}?utm_source=kakao_band\n\n"
        f"📸 백운호 10종 의상 무료 투샷 기념사진 찍기:\nhttps://{HOST}/booth.html?utm_source=kakao_band\n\n"
        f"🟢 필요하실 때 카드번호 입력 없이 편한 네이버페이 공식샵:\nhttps://cshop.naver.com/paradiseshop\n\n"
        f"🚀 정품 음반·에메랄드 응원준비물·건강선물 쿠팡 공식관:\nhttps://influencers.coupang.com/s/paradisehero\n"
    )

    naver_fancafe_greeting = longform_md

    yt_pinned_and_community = (
        f"=== [@김쌤의영웅라디오 유튜브 고정 댓글 & 커뮤니티 큰 글씨 공지 · {today_str}] ===\n\n"
        f"💚 {col['kakao_quote']}\n\n"
        f"1️⃣ 돋보기 없이 시원하게 읽는 큰 글씨 사연·건강 편지 전문:\n"
        f"👉 {canonical_url}?utm_source=youtube_pinned\n\n"
        f"2️⃣ 백운호 10종 의상 무제한 무료 투샷 사진관 & 효도 달력 제작소:\n"
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
        tags=["백운호", "김쌤의영웅라디오"],
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
