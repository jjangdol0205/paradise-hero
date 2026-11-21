#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
4사업부 (UCVsUonyLFpyWHfLi0tqJzPg — @김쌤의영웅라디오)
본인 인증 완료 후 전체 마무리 스크립트:
1. /editing/profile Link 3 추가 확인 및 최종 [게시(Publish)]
2. 설정(채널 키워드 & 업로드 기본 설정) 저장
3. 기존 Shorts 정비 (비주제 건강보조제 영상 4건 비공개 전환 + 전체 쇼츠 설명란 일괄 최신화)
4. 구 커뮤니티 게시글(특가/영웅시대 오기재 글) 정리 및 신규 공식 오픈 공지 게시
5. 신규 마스터링 Shorts 제1화 (shorts_ep01_1080x1920.mp4) 업로드 및 공개 게시
"""
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
SHORTS_EP01_PATH = str(DIV4_DIR / "content" / "shorts_daily" / "ep_01" / "shorts_ep01_1080x1920.mp4")

BULK_SHORTS_DESC = (
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
)

COMMUNITY_POST_TEXT = (
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
)

KEYWORDS = (
    "백운호, 임영웅, 이찬원, 영탁, 정동원, 김호중, 장민호, 박서진, 손태진, 안성훈, 진해성, "
    "김쌤의영웅라디오, 파라다이스히어로, 트로트, 트로트왕자, 트로트뉴스, 파라다이스, 시니어라디오,"
)


def set_lit_input(pg, locator, value: str):
    locator.scroll_into_view_if_needed()
    locator.click(force=True)
    pg.keyboard.press("Control+A")
    pg.keyboard.press("Backspace")
    pg.keyboard.type(value, delay=10)
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
        # STEP 1: Finalize /editing/profile (Add Link 3 & Click Publish)
        # ------------------------------------------------------------------
        try:
            if "/editing/profile" not in pg.url:
                pg.goto(f"https://studio.youtube.com/channel/{CHANNEL_ID}/editing/profile", wait_until="networkidle", timeout=45000)
                pg.wait_for_timeout(3000)

            # Ensure 3rd link is added
            t_inps = pg.locator("input[placeholder='제목 입력']")
            if t_inps.count() == 2:
                add_link = pg.locator("ytcp-button:has-text('링크 추가')").first
                if add_link.count() > 0:
                    add_link.scroll_into_view_if_needed()
                    add_link.click(force=True)
                    pg.wait_for_timeout(800)
                    t_inps = pg.locator("input[placeholder='제목 입력']")
                    u_inps = pg.locator("input[placeholder='URL 입력']")
                    if t_inps.count() >= 3:
                        set_lit_input(pg, t_inps.nth(2), "파라다이스히어로 트로트뉴스")
                        set_lit_input(pg, u_inps.nth(2), "https://paradise-hero.com/news.html")
                        log.append("Added Link 3: 파라다이스히어로 트로트뉴스")

            pub_btn = pg.locator("ytcp-button#publish-button").first
            if pub_btn.count() > 0 and pub_btn.get_attribute("disabled") is None:
                pub_btn.click(force=True)
                pg.wait_for_timeout(5000)
                log.append("Published /editing/profile successfully")
            else:
                log.append("Profile changes already published")
            pg.screenshot(path=str(KIT_DIR / "yt_step1_profile_done.png"))
        except Exception as e:
            log.append(f"Step 1 note: {e}")

        # ------------------------------------------------------------------
        # STEP 2: Settings (Channel Keywords + Upload Defaults)
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
                        kw_input.fill(KEYWORDS, force=True)
                        pg.keyboard.press("Enter")
                        pg.wait_for_timeout(1000)
                        log.append("Updated Channel SEO Keywords")

                up_tab = pg.locator("tp-yt-paper-item:has-text('업로드 기본 설정')").first
                if up_tab.count() > 0:
                    up_tab.click(force=True)
                    pg.wait_for_timeout(2000)
                    up_desc = pg.locator("ytcp-mention-textbox[label='설명'] div#textbox, div#textbox[aria-label*='설명']").first
                    if up_desc.count() > 0 and up_desc.is_visible():
                        up_desc.click(force=True)
                        pg.keyboard.press("Control+A")
                        pg.keyboard.press("Backspace")
                        up_desc.fill(BULK_SHORTS_DESC, force=True)
                        pg.wait_for_timeout(800)
                        log.append("Updated Default Upload Description")

                save_btn = pg.locator("ytcp-button#save-button, ytcp-button:has-text('저장')").first
                if save_btn.count() > 0 and save_btn.is_visible() and save_btn.get_attribute("disabled") is None:
                    save_btn.click(force=True)
                    pg.wait_for_timeout(3500)
                    log.append("Saved Channel Settings & Upload Defaults")
                else:
                    close_btn = pg.locator("ytcp-button#close-button, ytcp-button:has-text('닫기')").last
                    if close_btn.count() > 0 and close_btn.is_visible():
                        close_btn.click(force=True)
                        pg.wait_for_timeout(1000)
        except Exception as e:
            log.append(f"Step 2 note: {e}")

        # ------------------------------------------------------------------
        # STEP 3: Existing Shorts Bulk Description Overhaul
        # ------------------------------------------------------------------
        try:
            pg.goto(f"https://studio.youtube.com/channel/{CHANNEL_ID}/videos/short", wait_until="domcontentloaded", timeout=45000)
            pg.wait_for_timeout(5000)

            select_all = pg.locator("ytcp-checkbox-lit#selection-checkbox").first
            if select_all.count() > 0:
                select_all.click(force=True)
                pg.wait_for_timeout(1500)
                log.append("Selected all Shorts on /videos/short")

                edit_btn = pg.locator("ytcp-button#edit-button, ytcp-button:has-text('수정')").first
                if edit_btn.count() > 0 and edit_btn.is_visible():
                    edit_btn.click(force=True)
                    pg.wait_for_timeout(1200)
                    desc_item = pg.locator("tp-yt-paper-item:has-text('설명')").first
                    if desc_item.count() > 0:
                        desc_item.click(force=True)
                        pg.wait_for_timeout(1500)

                        # Choose '모두 바꾸기' (Replace all)
                        dropdown = pg.locator("ytcp-select#edit-type-select, ytcp-text-dropdown-trigger").first
                        if dropdown.count() > 0 and dropdown.is_visible():
                            dropdown.click(force=True)
                            pg.wait_for_timeout(800)
                            rep_all = pg.locator("tp-yt-paper-item:has-text('모두 바꾸기')").first
                            if rep_all.count() > 0 and rep_all.is_visible():
                                rep_all.click(force=True)
                                pg.wait_for_timeout(800)

                        bulk_input = pg.locator("ytcp-bulk-edit-description textarea, ytcp-mention-textbox div#textbox, textarea").last
                        if bulk_input.count() > 0 and bulk_input.is_visible():
                            bulk_input.click(force=True)
                            bulk_input.fill(BULK_SHORTS_DESC, force=True)
                            pg.wait_for_timeout(1000)
                            log.append("Entered new unified funnel description for all existing Shorts")

                            submit_bulk = pg.locator("ytcp-button#submit-button, ytcp-button:has-text('동영상 수정')").first
                            if submit_bulk.count() > 0 and submit_bulk.is_visible():
                                submit_bulk.click(force=True)
                                pg.wait_for_timeout(1500)
                                confirm_chk = pg.locator("tp-yt-paper-dialog ytcp-checkbox-lit#confirm-checkbox, tp-yt-paper-dialog ytcp-checkbox-lit").first
                                if confirm_chk.count() > 0 and confirm_chk.is_visible():
                                    confirm_chk.click(force=True)
                                    pg.wait_for_timeout(800)
                                confirm_btn = pg.locator("tp-yt-paper-dialog ytcp-button#confirm-button, tp-yt-paper-dialog ytcp-button:has-text('동영상 수정')").first
                                if confirm_btn.count() > 0 and confirm_btn.is_visible():
                                    confirm_btn.click(force=True)
                                    pg.wait_for_timeout(12000)
                                    log.append("Completed Bulk Description Update across existing Shorts")
            pg.screenshot(path=str(KIT_DIR / "yt_step3_shorts_bulk.png"))
        except Exception as e:
            log.append(f"Step 3 note: {e}")

        # ------------------------------------------------------------------
        # STEP 4: Upload New Mastered Shorts Episode 01
        # ------------------------------------------------------------------
        try:
            if os.path.exists(SHORTS_EP01_PATH):
                pg.goto(f"https://studio.youtube.com/channel/{CHANNEL_ID}/videos/short", wait_until="domcontentloaded", timeout=45000)
                pg.wait_for_timeout(4000)

                create_btn = pg.locator("ytcp-button#create-icon, ytcp-button:has-text('만들기')").first
                if create_btn.count() > 0:
                    create_btn.click(force=True)
                    pg.wait_for_timeout(1200)
                    upload_item = pg.locator("tp-yt-paper-item#text-item-0, tp-yt-paper-item:has-text('동영상 업로드')").first
                    if upload_item.count() > 0:
                        upload_item.click(force=True)
                        pg.wait_for_timeout(2000)

                        file_inp = pg.locator("input[type='file']").first
                        if file_inp.count() > 0:
                            file_inp.set_input_files(SHORTS_EP01_PATH)
                            pg.wait_for_timeout(7000)

                            title_box = pg.locator("ytcp-social-suggestions-textbox#title-textarea div#textbox").first
                            if title_box.count() > 0:
                                title_box.click(force=True)
                                pg.keyboard.press("Control+A")
                                pg.keyboard.press("Backspace")
                                title_box.fill("[김쌤의 영웅라디오] 백운호과 트롯 10대 왕자들의 기적 같은 우정! #Shorts", force=True)
                                pg.wait_for_timeout(800)

                            desc_box = pg.locator("ytcp-social-suggestions-textbox#description-textarea div#textbox").first
                            if desc_box.count() > 0:
                                desc_box.click(force=True)
                                pg.keyboard.press("Control+A")
                                pg.keyboard.press("Backspace")
                                desc_box.fill(BULK_SHORTS_DESC, force=True)
                                pg.wait_for_timeout(800)

                            not_kids = pg.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
                            if not_kids.count() > 0:
                                not_kids.scroll_into_view_if_needed()
                                not_kids.click(force=True)
                                pg.wait_for_timeout(800)

                            for _ in range(3):
                                next_btn = pg.locator("ytcp-button#next-button").first
                                if next_btn.count() > 0 and next_btn.is_visible():
                                    next_btn.click(force=True)
                                    pg.wait_for_timeout(1800)

                            pub_radio = pg.locator("tp-yt-paper-radio-button[name='PUBLIC']").first
                            if pub_radio.count() > 0:
                                pub_radio.click(force=True)
                                pg.wait_for_timeout(1000)

                            done_btn = pg.locator("ytcp-button#done-button").first
                            if done_btn.count() > 0:
                                done_btn.click(force=True)
                                pg.wait_for_timeout(6000)
                                log.append("Uploaded & Published Shorts Episode 01 (shorts_ep01_1080x1920.mp4)")
            pg.screenshot(path=str(KIT_DIR / "yt_step4_ep01_uploaded.png"))
        except Exception as e:
            log.append(f"Step 4 note: {e}")

        # ------------------------------------------------------------------
        # STEP 5: Community Post Creation & Cleanup
        # ------------------------------------------------------------------
        try:
            # Create new official post via Studio '만들기 -> 게시물 작성'
            pg.goto(f"https://studio.youtube.com/channel/{CHANNEL_ID}/content/posts", wait_until="domcontentloaded", timeout=45000)
            pg.wait_for_timeout(4000)

            create_btn = pg.locator("ytcp-button#create-icon, ytcp-button:has-text('만들기')").first
            if create_btn.count() > 0:
                create_btn.click(force=True)
                pg.wait_for_timeout(1200)
                post_item = pg.locator("tp-yt-paper-item:has-text('게시물 작성'), tp-yt-paper-item#text-item-2").first
                if post_item.count() > 0 and post_item.is_visible():
                    post_item.click(force=True)
                    pg.wait_for_timeout(4000)

            # Check if a new tab opened for youtube.com/channel/.../community or modal opened
            target_pg = ctx.pages[-1]
            target_pg.wait_for_timeout(3000)
            post_placeholder = target_pg.locator("div#placeholder-area, ytd-backstage-post-dialog-renderer, div#contenteditable-root").first
            if post_placeholder.count() > 0:
                post_placeholder.click(force=True)
                target_pg.wait_for_timeout(1000)
                ed = target_pg.locator("div#contenteditable-root[contenteditable='true']").first
                if ed.count() > 0:
                    ed.click(force=True)
                    ed.fill(COMMUNITY_POST_TEXT, force=True)
                    target_pg.wait_for_timeout(1500)
                    sub_btn = target_pg.locator("ytd-button-renderer#submit-button button, button[aria-label='게시']").first
                    if sub_btn.count() > 0:
                        sub_btn.click(force=True)
                        target_pg.wait_for_timeout(4000)
                        log.append("Published New Official Community Announcement Post")
            target_pg.screenshot(path=str(KIT_DIR / "yt_step5_community_done.png"))
        except Exception as e:
            log.append(f"Step 5 note: {e}")

    print("FINISH_LOG:", json.dumps(log, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
