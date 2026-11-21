#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DIV4_DIR = Path(r"D:\드림컴퍼니\4사업부")
KIT_DIR = DIV4_DIR / "assets" / "youtube_kit"
CHANNEL_ID = "UCVsUonyLFpyWHfLi0tqJzPg"

BANNER_PATH = str(KIT_DIR / "youtube_banner_2048x1152.png")
PROFILE_PATH = str(KIT_DIR / "youtube_profile_800x800.png")
WATERMARK_PATH = str(KIT_DIR / "youtube_watermark_150x150.png")

CFG = {
    "channel_name": "김쌤의 영웅라디오",
    "handle": "김쌤의영웅라디오",
    "description": (
        "전국과 해외에 계신 사랑하는 파라다이스 가족 여러분, 그리고 우리 어머님들 반갑습니다.\n"
        "감성 황태자 백운호과 대한민국 10대 트롯 왕자님들의 감동 스토리, 명곡 해설, "
        "그리고 어머님들의 구구절절한 인생 사연을 전직 국어선생님 김쌤이 매일 다정하게 읽어드리는 "
        "[김쌤의 영웅라디오]입니다.\n\n"
        "👑 10대 트롯 왕자님과 스마트폰 투샷 사진관 (회원가입 시 1회 무료 촬영!):\n"
        "👉 https://paradise-hero.com/booth.html\n\n"
        "💌 김쌤 라디오 사연 복덕방 (1등 사연 라디오 방송 편성):\n"
        "👉 https://paradise-hero.com/story.html\n\n"
        "📰 실시간 트로트 가수 소식 & 공식 팬덤 사랑방:\n"
        "👉 https://paradise-hero.com/news.html\n\n"
        "📩 비즈니스 및 제휴 문의: beable9489@gmail.com"
    ),
    "contact_email": "beable9489@gmail.com",
    "links": [
        {"title": "왕자님 투샷 사진관(1회무료)", "url": "https://paradise-hero.com/booth.html"},
        {"title": "김쌤 라디오 사연 복덕방", "url": "https://paradise-hero.com/story.html"},
        {"title": "파라다이스히어로 트로트뉴스", "url": "https://paradise-hero.com/news.html"},
    ],
}


def click_done_in_dialog(pg):
    pg.wait_for_timeout(2000)
    done_btn = pg.locator("tp-yt-paper-dialog ytcp-button#done-button, ytcp-dialog ytcp-button#done-button, ytcp-button#done-button").last
    if done_btn.count() > 0:
        done_btn.click(force=True)
        pg.wait_for_timeout(2000)


def set_lit_input(pg, locator, value: str):
    locator.scroll_into_view_if_needed()
    locator.click(force=True)
    pg.keyboard.press("Control+A")
    pg.keyboard.press("Backspace")
    pg.keyboard.type(value, delay=10)
    pg.keyboard.press("Tab")
    pg.wait_for_timeout(500)


def main():
    log = []
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp("http://127.0.0.1:9224")
        ctx = b.contexts[0]
        pg = [x for x in ctx.pages if "studio.youtube.com" in x.url or "youtube.com" in x.url][0]
        pg.on("dialog", lambda d: d.accept())
        pg.bring_to_front()

        # First discard any stuck changes if discard button is enabled
        discard = pg.locator("ytcp-button#discard-changes-button")
        if discard.count() > 0 and discard.first.is_visible():
            try:
                discard.first.click(force=True)
                pg.wait_for_timeout(1500)
            except Exception:
                pass

        pg.goto(f"https://studio.youtube.com/channel/{CHANNEL_ID}/editing/profile", wait_until="networkidle", timeout=45000)
        pg.wait_for_timeout(3000)

        # Click retry button if any section failed to load
        retry_btns = pg.locator("ytcp-button#error-retry-button")
        for i in range(retry_btns.count()):
            if retry_btns.nth(i).is_visible():
                retry_btns.nth(i).click(force=True)
                pg.wait_for_timeout(3000)
                log.append("Clicked retry button to load full profile form")

        # 1. Upload Banner Image via file chooser
        try:
            banner_btn = pg.locator("ytcp-button#upload-button, ytcp-button#replace-button").nth(0)
            banner_btn.scroll_into_view_if_needed()
            with pg.expect_file_chooser(timeout=5000) as fc_info:
                banner_btn.click(force=True)
            fc_info.value.set_files(BANNER_PATH)
            click_done_in_dialog(pg)
            log.append("Uploaded Banner (2048x1152) via file chooser")
        except Exception as e:
            log.append(f"Banner note: {e}")

        # 2. Upload Profile Picture via file chooser
        try:
            prof_btn = pg.locator("ytcp-button#replace-button, ytcp-button#upload-button").nth(1)
            prof_btn.scroll_into_view_if_needed()
            with pg.expect_file_chooser(timeout=5000) as fc_info:
                prof_btn.click(force=True)
            fc_info.value.set_files(PROFILE_PATH)
            click_done_in_dialog(pg)
            log.append("Uploaded Profile Picture (800x800) via file chooser")
        except Exception as e:
            log.append(f"Profile note: {e}")

        # 3. Upload Watermark via file chooser
        try:
            wm_btn = pg.locator("ytcp-button#upload-button, ytcp-button#replace-button").last
            wm_btn.scroll_into_view_if_needed()
            with pg.expect_file_chooser(timeout=5000) as fc_info:
                wm_btn.click(force=True)
            fc_info.value.set_files(WATERMARK_PATH)
            click_done_in_dialog(pg)
            # Also select '전체 동영상' (Entire video) radio if visible
            entire_vid = pg.locator("tp-yt-paper-radio-button:has-text('전체 동영상')").first
            if entire_vid.count() > 0 and entire_vid.is_visible():
                entire_vid.click(force=True)
            log.append("Uploaded Watermark (150x150) via file chooser")
        except Exception as e:
            log.append(f"Watermark note: {e}")

        # 4. Channel Name
        name_inp = pg.locator("input[placeholder='채널 이름 입력']").first
        if name_inp.count() > 0:
            set_lit_input(pg, name_inp, CFG["channel_name"])
            log.append(f"Set Channel Name -> {CFG['channel_name']}")

        # 5. Handle
        handle_inp = pg.locator("input[placeholder='핸들 설정']").first
        if handle_inp.count() > 0:
            set_lit_input(pg, handle_inp, CFG["handle"])
            pg.wait_for_timeout(2000)
            log.append(f"Set Handle -> @{CFG['handle']}")

        # 6. Description
        desc_box = pg.locator("div#textbox[contenteditable='true']").first
        if desc_box.count() > 0:
            desc_box.scroll_into_view_if_needed()
            desc_box.click(force=True)
            pg.keyboard.press("Control+A")
            pg.keyboard.press("Backspace")
            desc_box.fill(CFG["description"], force=True)
            pg.keyboard.press("Tab")
            pg.wait_for_timeout(800)
            log.append("Set Channel Description")

        # 7. External Links (Ensure 3 rows exist)
        for _ in range(3):
            if pg.locator("input[placeholder='제목 입력']").count() >= 3:
                break
            add_link = pg.locator("ytcp-button:has-text('링크 추가')").first
            if add_link.count() > 0:
                add_link.scroll_into_view_if_needed()
                add_link.click(force=True)
                pg.wait_for_timeout(800)

        t_inps = pg.locator("input[placeholder='제목 입력']")
        u_inps = pg.locator("input[placeholder='URL 입력']")
        for i, lk in enumerate(CFG["links"]):
            if i < t_inps.count():
                set_lit_input(pg, t_inps.nth(i), lk["title"])
                set_lit_input(pg, u_inps.nth(i), lk["url"])
                log.append(f"Set Link {i+1}: {lk['title']} -> {lk['url']}")

        # 8. Contact Email
        email_inp = pg.locator("input[placeholder='이메일 주소']").first
        if email_inp.count() > 0:
            set_lit_input(pg, email_inp, CFG["contact_email"])
            log.append(f"Set Contact Email -> {CFG['contact_email']}")

        pg.wait_for_timeout(1500)
        pg.screenshot(path=str(KIT_DIR / "yt_phase1_ready.png"))

        # 9. Click Publish (게시)
        pub_btn = pg.locator("ytcp-button#publish-button").first
        is_disabled = pub_btn.get_attribute("disabled")
        log.append(f"Publish button disabled attr: {is_disabled}")
        pub_btn.click(force=True)
        pg.wait_for_timeout(5000)
        pg.screenshot(path=str(KIT_DIR / "yt_phase1_published.png"))
        log.append("Clicked Publish (게시)")

    print("PHASE1_LOG:", json.dumps(log, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
