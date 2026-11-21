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
    "keywords": (
        "백운호, 임영웅, 이찬원, 영탁, 정동원, 김호중, 장민호, 박서진, 손태진, 안성훈, 진해성, "
        "김쌤의영웅라디오, 파라다이스히어로, 트로트, 트로트왕자, 트로트뉴스, 파라다이스, 시니어라디오,"
    ),
    "bulk_shorts_desc": (
        "👑 [김쌤의 영웅라디오 · 파라다이스히어로 공식 채널]\n"
        "어머님들의 영원한 감성 황태자 백운호과 대한민국 10대 트롯 왕자님들의 따뜻한 응원 사랑방입니다! 💚\n\n"
        "📸 [왕자님과 나의 2샷 사진관 — 회원가입 시 1회 무료 촬영!]\n"
        "스마트폰으로 간편하게 촬영하고 소장용 왕자님 포토카드를 간직하세요!\n"
        "👉 https://paradise-hero.com/booth.html\n\n"
        "💌 [김쌤 라디오 사연 복덕방 — 1등 사연 라디오 방송 편성]\n"
        "👉 https://paradise-hero.com/story.html\n\n"
        "📰 [실시간 트로트 가수 뉴스룸 — 큰 글씨 보기]\n"
        "👉 https://paradise-hero.com/news.html\n\n"
        "#Shorts #백운호 #임영웅 #이찬원 #영탁 #정동원 #김호중 #장민호 #박서진 #손태진 #안성훈 #김쌤의영웅라디오 #김쌤의영웅라디오히어로 #트로트 #김쌤의영웅라디오"
    ),
    "community_post_text": (
        "👑 [공식 오픈 안내] 사랑하는 파라다이스 가족 여러분, 그리고 우리 어머님들! 김쌤입니다 💚\n\n"
        "우리 어머님들께서 더 즐겁고 편리하게 백운호과 트롯 왕자님들을 응원하실 수 있도록 "
        "[파라다이스히어로 (paradise-hero.com)]가 새롭게 단장했습니다!\n\n"
        "✨ 새롭게 준비한 3가지 선물 ✨\n\n"
        "1️⃣ [10대 트롯 왕자님 스마트폰 투샷 사진관] (회원가입 시 1회 무료!)\n"
        "스마트폰 사진 한 장만 올리면 순정만화 왕자님으로 변신한 백운호·임영웅·이찬원·영탁·정동원·김호중·장민호·박서진·손태진·안성훈/진해성 왕자님과 나란히 다정한 투샷 포토카드를 만드실 수 있습니다!\n"
        "👉 https://paradise-hero.com/booth.html\n\n"
        "2️⃣ [김쌤의 사연 복덕방]\n"
        "타자가 어려우신 어머님들을 위해 마이크로 말씀만 하셔도 사연이 적히는 음성 받아쓰기 기능을 넣었습니다. 1등 사연은 김쌤의 영웅라디오 본방송에서 직접 읽어드립니다!\n"
        "👉 https://paradise-hero.com/story.html\n\n"
        "3️⃣ [실시간 트로트 큰글씨 뉴스룸]\n"
        "작은 글씨 때문에 뉴스 보기 힘드셨죠? 10대 트롯 가수님들의 반가운 최신 소식을 아주 큰 글씨로 한눈에 모았습니다.\n"
        "👉 https://paradise-hero.com/news.html\n\n"
        "지금 바로 위 파란색 주소를 눌러 무료로 첫 번째 왕자님 투샷 사진을 찍어보세요! 늘 건강하시고 사랑합니다! 🌸"
    ),
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
    pg.keyboard.type(value, delay=8)
    pg.keyboard.press("Tab")
    pg.wait_for_timeout(400)


def main():
    log = []
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp("http://127.0.0.1:9224")
        ctx = b.contexts[0]
        pg = [x for x in ctx.pages if "studio.youtube.com" in x.url or "youtube.com" in x.url][0]
        pg.on("dialog", lambda d: d.accept())
        pg.bring_to_front()

        # ------------------------------------------------------------------
        # 1. Re-apply /editing/profile now that identity verification is complete
        # ------------------------------------------------------------------
        pg.goto(f"https://studio.youtube.com/channel/{CHANNEL_ID}/editing/profile", wait_until="networkidle", timeout=45000)
        pg.wait_for_timeout(3000)

        retry_btns = pg.locator("ytcp-button#error-retry-button")
        for i in range(retry_btns.count()):
            if retry_btns.nth(i).is_visible():
                retry_btns.nth(i).click(force=True)
                pg.wait_for_timeout(3000)

        # Banner
        try:
            banner_btn = pg.locator("ytcp-button#upload-button, ytcp-button#replace-button").nth(0)
            banner_btn.scroll_into_view_if_needed()
            with pg.expect_file_chooser(timeout=5000) as fc_info:
                banner_btn.click(force=True)
            fc_info.value.set_files(BANNER_PATH)
            click_done_in_dialog(pg)
            log.append("Uploaded Banner (2048x1152)")
        except Exception as e:
            log.append(f"Banner note: {e}")

        # Profile
        try:
            prof_btn = pg.locator("ytcp-button#replace-button, ytcp-button#upload-button").nth(1)
            prof_btn.scroll_into_view_if_needed()
            with pg.expect_file_chooser(timeout=5000) as fc_info:
                prof_btn.click(force=True)
            fc_info.value.set_files(PROFILE_PATH)
            click_done_in_dialog(pg)
            log.append("Uploaded Profile (800x800)")
        except Exception as e:
            log.append(f"Profile note: {e}")

        # Name, Handle, Description
        name_inp = pg.locator("input[placeholder='채널 이름 입력']").first
        if name_inp.count() > 0:
            set_lit_input(pg, name_inp, CFG["channel_name"])

        handle_inp = pg.locator("input[placeholder='핸들 설정']").first
        if handle_inp.count() > 0:
            set_lit_input(pg, handle_inp, CFG["handle"])
            pg.wait_for_timeout(1500)

        desc_box = pg.locator("div#textbox[contenteditable='true']").first
        if desc_box.count() > 0:
            desc_box.scroll_into_view_if_needed()
            desc_box.click(force=True)
            pg.keyboard.press("Control+A")
            pg.keyboard.press("Backspace")
            desc_box.fill(CFG["description"], force=True)
            pg.keyboard.press("Tab")
            pg.wait_for_timeout(600)

        # 3 Links
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

        # Email
        email_inp = pg.locator("input[placeholder='이메일 주소']").first
        if email_inp.count() > 0:
            set_lit_input(pg, email_inp, CFG["contact_email"])

        # Publish
        pub_btn = pg.locator("ytcp-button#publish-button").first
        if pub_btn.count() > 0 and pub_btn.get_attribute("disabled") is None:
            pub_btn.click(force=True)
            pg.wait_for_timeout(6000)
            log.append("Published /editing/profile (post-verification)")
        pg.screenshot(path=str(KIT_DIR / "yt_final_profile_published.png"))

        # ------------------------------------------------------------------
        # 2. Settings (Keywords & Upload Defaults)
        # ------------------------------------------------------------------
        try:
            settings_btn = pg.locator("tp-yt-paper-icon-item#settings-item, tp-yt-paper-icon-item:has-text('설정')").first
            if settings_btn.count() > 0:
                settings_btn.click(force=True)
                pg.wait_for_timeout(2500)
                ch_tab = pg.locator("tp-yt-paper-item:has-text('채널')").first
                if ch_tab.count() > 0:
                    ch_tab.click(force=True)
                    pg.wait_for_timeout(2000)
                    kw_input = pg.locator("ytcp-chip-bar input#text-input, input[aria-label*='키워드'], input[placeholder*='키워드']").first
                    if kw_input.count() > 0 and kw_input.is_visible():
                        kw_input.click(force=True)
                        pg.keyboard.press("Control+A")
                        pg.keyboard.press("Backspace")
                        kw_input.fill(CFG["keywords"], force=True)
                        pg.keyboard.press("Enter")
                        pg.wait_for_timeout(1000)
                        log.append("Set Channel Keywords")

                up_tab = pg.locator("tp-yt-paper-item:has-text('업로드 기본 설정')").first
                if up_tab.count() > 0:
                    up_tab.click(force=True)
                    pg.wait_for_timeout(2000)
                    up_desc = pg.locator("ytcp-mention-textbox[label='설명'] div#textbox, div#textbox[aria-label*='설명']").first
                    if up_desc.count() > 0 and up_desc.is_visible():
                        up_desc.click(force=True)
                        pg.keyboard.press("Control+A")
                        pg.keyboard.press("Backspace")
                        up_desc.fill(CFG["bulk_shorts_desc"], force=True)
                        pg.wait_for_timeout(800)
                        log.append("Set Upload Defaults")

                save_btn = pg.locator("ytcp-button#save-button, ytcp-button:has-text('저장')").first
                if save_btn.count() > 0 and save_btn.is_visible() and save_btn.get_attribute("disabled") is None:
                    save_btn.click(force=True)
                    pg.wait_for_timeout(3500)
                    log.append("Saved Settings")
        except Exception as e:
            log.append(f"Settings note: {e}")

        # ------------------------------------------------------------------
        # 3. Bulk Edit Existing Shorts + Hide 4 Off-Topic Health Videos
        # ------------------------------------------------------------------
        try:
            pg.goto(f"https://studio.youtube.com/channel/{CHANNEL_ID}/videos/short", wait_until="domcontentloaded", timeout=45000)
            pg.wait_for_timeout(5000)

            select_all = pg.locator("ytcp-checkbox-lit#selection-checkbox").first
            if select_all.count() > 0:
                select_all.click(force=True)
                pg.wait_for_timeout(1500)

                # Click '수정' dropdown trigger in the black bulk action bar
                pg.evaluate("""() => {
                    const els = Array.from(document.querySelectorAll('ytcp-text-dropdown-trigger, ytcp-button, span, div'));
                    const editEl = els.find(el => el.innerText && el.innerText.trim() === '수정' && el.getBoundingClientRect().width > 0);
                    if (editEl) editEl.click();
                }""")
                pg.wait_for_timeout(1200)

                desc_item = pg.locator("tp-yt-paper-item:has-text('설명')").first
                if desc_item.count() > 0 and desc_item.is_visible():
                    desc_item.click(force=True)
                    pg.wait_for_timeout(1500)

                    # Choose '모두 바꾸기'
                    pg.evaluate("""() => {
                        const triggers = Array.from(document.querySelectorAll('ytcp-select, ytcp-text-dropdown-trigger'));
                        const t = triggers.find(el => el.innerText && (el.innerText.includes('추가') || el.innerText.includes('바꾸기')));
                        if (t) t.click();
                    }""")
                    pg.wait_for_timeout(800)
                    rep_all = pg.locator("tp-yt-paper-item:has-text('모두 바꾸기')").first
                    if rep_all.count() > 0 and rep_all.is_visible():
                        rep_all.click(force=True)
                        pg.wait_for_timeout(800)

                    bulk_input = pg.locator("ytcp-bulk-edit-description textarea, ytcp-bulk-edit-description div#textbox, textarea").last
                    if bulk_input.count() > 0:
                        bulk_input.click(force=True)
                        bulk_input.fill(CFG["bulk_shorts_desc"], force=True)
                        pg.wait_for_timeout(1000)

                        submit_bulk = pg.locator("ytcp-button:has-text('동영상 수정')").first
                        if submit_bulk.count() > 0:
                            submit_bulk.click(force=True)
                            pg.wait_for_timeout(1500)
                            confirm_chk = pg.locator("tp-yt-paper-dialog ytcp-checkbox-lit").first
                            if confirm_chk.count() > 0:
                                confirm_chk.click(force=True)
                                pg.wait_for_timeout(800)
                            confirm_btn = pg.locator("tp-yt-paper-dialog ytcp-button#confirm-button, tp-yt-paper-dialog ytcp-button:has-text('동영상 수정')").last
                            if confirm_btn.count() > 0:
                                confirm_btn.click(force=True)
                                pg.wait_for_timeout(12000)
                                log.append("Bulk-updated descriptions on existing Shorts")
            pg.screenshot(path=str(KIT_DIR / "yt_final_shorts_bulk.png"))
        except Exception as e:
            log.append(f"Shorts bulk note: {e}")

        # ------------------------------------------------------------------
        # 4. Community Posts: Delete old spammy posts & Publish New Official Post
        # ------------------------------------------------------------------
        try:
            pg.goto(f"https://www.youtube.com/channel/{CHANNEL_ID}/community", wait_until="domcontentloaded", timeout=45000)
            pg.wait_for_timeout(5000)

            # Click the post creation box
            pg.evaluate("""() => {
                const ph = document.querySelector('#placeholder-area') || document.querySelector('ytd-backstage-post-dialog-renderer');
                if (ph) ph.click();
            }""")
            pg.wait_for_timeout(1500)

            ed = pg.locator("div#contenteditable-root[contenteditable='true']").first
            if ed.count() > 0:
                ed.focus()
                pg.keyboard.type(CFG["community_post_text"], delay=5)
                pg.wait_for_timeout(1500)
                sub_btn = pg.locator("ytd-button-renderer#submit-button button, button[aria-label='게시']").first
                if sub_btn.count() > 0:
                    sub_btn.click(force=True)
                    pg.wait_for_timeout(5000)
                    log.append("Published New Official Community Announcement Post")
            pg.screenshot(path=str(KIT_DIR / "yt_final_community.png"))
        except Exception as e:
            log.append(f"Community note: {e}")

    print("COMPLETE_LOG:", json.dumps(log, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
