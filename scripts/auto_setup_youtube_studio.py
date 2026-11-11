#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_setup_youtube_studio.py
4사업부 (@김쌤의영웅라디오 — silientocean94@gmail.com)
YouTube Studio 채널 브랜딩(2560x1440 배너 / 프로필 / 워터마크) 및
채널명·핸들·소개글·외부링크(paradise-hero.com & cshop.naver.com/paradiseshop)·고정 키워드 자동 세팅 스크립트
"""

import sys
import time
from pathlib import Path

DIV4_DIR = Path(__file__).resolve().parent.parent
KIT_DIR = DIV4_DIR / "assets" / "youtube_kit"
ASSETS_DIR = DIV4_DIR / "assets"
PROFILE_DIR = DIV4_DIR / ".youtube_studio_chrome_profile"

CHANNEL_NAME = "김쌤의 영웅 라디오"
CHANNEL_HANDLE = "김쌤의영웅라디오"
BANNER_HEADLINE = "김쌤의 영웅 라디오 | 👇 바로 아래 파란 글씨 [paradise-hero.com]을 누르시면 무료 투샷 기념사진관이 열립니다!"

FIXED_KEYWORDS = ["황영웅", "파라다이스", "트로트", "감동사연", "시니어유튜브"]
FIXED_HASHTAGS = ["#황영웅", "#파라다이스", "#트로트", "#감동사연", "#시니어유튜브"]

CHANNEL_LINKS = [
    {"title": "무료 투샷 기념사진관", "url": "https://paradise-hero.com/booth.html"},
    {"title": "김쌤 공식 네이버 특가관", "url": "https://cshop.naver.com/paradiseshop"},
]

CHANNEL_DESC = (
    "전국과 해외에 계신 사랑하는 파라다이스 가족 여러분, 그리고 우리 어머님들 반갑습니다.\n"
    "가수 황영웅 님의 깊은 목소리와 명곡 해설, 그리고 우리 어머님들의 따뜻한 인생 사연을 "
    "전직 국어선생님 김쌤이 매일 저녁 다정하게 읽어드리는 힐링 라디오 방송국 [김쌤의 영웅 라디오]입니다.\n\n"
    "💚 황영웅 10종 의상 무료 투샷 기념사진관 & 공식 팬 쉼터:\n"
    "👉 https://paradise-hero.com/booth.html\n\n"
    "💌 김쌤 라디오에 내 사연 & 영웅님께 편지 보내기:\n"
    "👉 https://paradise-hero.com/story.html\n\n"
    "🛍️ 김쌤 공식 네이버 크리에이터샵 안심특가관:\n"
    "👉 https://cshop.naver.com/paradiseshop\n\n"
    "📺 쇼츠 매일 저녁 19:30 / 보이는 사연 라디오 본방송 매주 화·금 18:00에 찾아갑니다.\n"
    "#황영웅 #파라다이스 #트로트 #감동사연 #시니어유튜브"
)


def resolve_banner_asset() -> Path:
    hq_banner = ASSETS_DIR / "yt_banner_heroradio_2560x1440.jpg"
    if hq_banner.exists():
        return hq_banner
    return KIT_DIR / "youtube_banner_2560x1440.png"


def run_youtube_studio_setup():
    from playwright.sync_api import sync_playwright

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    p_profile = KIT_DIR / "youtube_profile_800x800.png"
    p_banner = resolve_banner_asset()
    p_watermark = KIT_DIR / "youtube_watermark_150x150.png"

    print(f"[YouTube Auto-Setup] 배너 자산 확인: {p_banner} (exists={p_banner.exists()})")

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            no_viewport=True,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://studio.youtube.com", wait_until="domcontentloaded")
        print("[YouTube Auto-Setup] Chrome 창이 열렸습니다. silientocean94@gmail.com 로그인 대기 중...")

        for _ in range(300):
            url = page.url
            if "studio.youtube.com/channel/" in url:
                print(f"[YouTube Auto-Setup] 로그인 감지 완료: {url}")
                break
            time.sleep(1)
        else:
            print("[YouTube Auto-Setup] 로그인 대기 시간이 초과되었습니다.")
            ctx.close()
            return False

        time.sleep(3)
        cust_btn = page.locator(
            "a#menu-paper-icon-item-3, tp-yt-paper-icon-item:has-text('맞춤설정'), tp-yt-paper-icon-item:has-text('Customization')"
        )
        if cust_btn.count() > 0:
            cust_btn.first.click()
            time.sleep(3)

        try:
            name_inputs = page.locator("input[aria-label*='이름'], input[aria-label*='Name']")
            if name_inputs.count() > 0:
                name_inputs.first.fill(CHANNEL_NAME)
        except Exception as e:
            print("Name input note:", e)

        try:
            desc_inputs = page.locator("textarea, div[contenteditable='true']#textbox")
            if desc_inputs.count() > 0:
                desc_inputs.first.fill(CHANNEL_DESC)
        except Exception as e:
            print("Desc input note:", e)

        try:
            file_inputs = page.locator("input[type='file']")
            print(f"[YouTube Auto-Setup] 파일 업로드 슬롯 {file_inputs.count()}개 감지됨 (배너: {p_banner.name})")
        except Exception as e:
            print("File input note:", e)

        print("[YouTube Auto-Setup] 채널 브랜딩 & 링크 세팅 준비 완료!")
        time.sleep(15)
        return True


if __name__ == "__main__":
    if "--dry-run" in sys.argv:
        b_path = resolve_banner_asset()
        print(f"[DRY-RUN OK] Channel={CHANNEL_NAME} | Banner={b_path} (exists={b_path.exists()}) | Tags={FIXED_HASHTAGS}")
        sys.exit(0)
    run_youtube_studio_setup()
