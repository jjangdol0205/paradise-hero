#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
4사업부 (UCVsUonyLFpyWHfLi0tqJzPg — @김쌤의영웅라디오)
Master YouTube Studio Overhaul Engine:
1. /editing/profile (Name, Handle, Description, 3 Links, Unified Email, Banner, Profile, Watermark) + Publish
2. Settings (Channel SEO Keywords + Upload Defaults) + Save
3. /videos/short Bulk Description Overhaul (updates all existing shorts with new funnel links)
4. /content/posts Cleanup + New Official Community Announcement Post
5. Upload New Shorts Episode 01 (shorts_ep01_1080x1920.mp4)
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

BANNER_PATH = str(KIT_DIR / "youtube_banner_2048x1152.png")
PROFILE_PATH = str(KIT_DIR / "youtube_profile_800x800.png")
WATERMARK_PATH = str(KIT_DIR / "youtube_watermark_150x150.png")
SHORTS_EP01_PATH = str(DIV4_DIR / "content" / "shorts_daily" / "ep_01" / "shorts_ep01_1080x1920.mp4")

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


def fill_input_clean(page, locator, val: str):
    locator.scroll_into_view_if_needed()
    locator.click(force=True)
    locator.fill("", force=True)
    locator.fill(val, force=True)
    page.wait_for_timeout(400)


def click_visible_done_button(page) -> bool:
    try:
        clicked = page.evaluate("""() => {
            const selectors = [
                'ytcp-profile-image-editor ytcp-button#done-button',
                'ytcp-banner-editor ytcp-button#done-button',
                'ytcp-Watermark-image-editor ytcp-button#done-button',
                'tp-yt-paper-dialog ytcp-button#done-button',
                'ytcp-dialog ytcp-button#done-button',
                'ytcp-button#done-button'
            ];
            for (const sel of selectors) {
                const btns = Array.from(document.querySelectorAll(sel));
                for (const b of btns) {
                    const r = b.getBoundingClientRect();
                    if (r.width > 0 && r.height > 0) {
                        b.click();
                        const innerBtn = b.querySelector('button');
                        if (innerBtn) innerBtn.click();
                        return true;
                    }
                }
            }
            return false;
        }""")
        if clicked:
            page.wait_for_timeout(2000)
        return clicked
    except Exception:
        return False


def phase1_profile_and_settings(pg, log):
    print("--- [Phase 1] Profile & Settings ---", flush=True)
    pg.goto(
        f"https://studio.youtube.com/channel/{CHANNEL_ID}/editing/profile",
        wait_until="networkidle",
        timeout=45000,
    )
    pg.wait_for_timeout(3000)

    # 1. Channel Name
    name_inp = pg.locator("input[placeholder='채널 이름 입력']").first
    if name_inp.count() > 0:
        fill_input_clean(pg, name_inp, CFG["channel_name"])
        log.append(f"Set Channel Name -> {CFG['channel_name']}")

    # 2. Handle
    handle_inp = pg.locator("input[placeholder='핸들 설정']").first
    if handle_inp.count() > 0:
        fill_input_clean(pg, handle_inp, CFG["handle"])
        pg.wait_for_timeout(1500)
        log.append(f"Set Handle -> @{CFG['handle']}")

    # 3. Description
    desc_box = pg.locator("div#textbox[contenteditable='true']").first
    if desc_box.count() > 0:
        desc_box.scroll_into_view_if_needed()
        desc_box.click(force=True)
        desc_box.fill(CFG["description"], force=True)
        pg.wait_for_timeout(600)
        log.append("Set Channel Description")

    # 4. External Links (Ensure 3 rows exist)
    for _ in range(3):
        title_inps = pg.locator("input[placeholder='제목 입력']")
        if title_inps.count() >= 3:
            break
        add_btn = pg.locator("ytcp-button:has-text('링크 추가'), button:has-text('링크 추가')").first
        if add_btn.count() > 0:
            add_btn.scroll_into_view_if_needed()
            add_btn.click(force=True)
            pg.wait_for_timeout(800)

    title_inps = pg.locator("input[placeholder='제목 입력']")
    url_inps = pg.locator("input[placeholder='URL 입력']")
    t_cnt = title_inps.count()
    for i, link in enumerate(CFG["links"]):
        if i < t_cnt:
            fill_input_clean(pg, title_inps.nth(i), link["title"])
            fill_input_clean(pg, url_inps.nth(i), link["url"])
            log.append(f"Set Link {i+1}: {link['title']} -> {link['url']}")

    # 5. Contact Email
    email_inp = pg.locator("input[placeholder='이메일 주소']").first
    if email_inp.count() > 0:
        fill_input_clean(pg, email_inp, CFG["contact_email"])
        log.append(f"Set Contact Email -> {CFG['contact_email']}")

    # 6. Enable all file inputs and upload Banner, Profile, Watermark
    pg.evaluate("""() => {
        document.querySelectorAll("input[type='file']").forEach(el => {
            el.disabled = false;
            el.removeAttribute('disabled');
        });
    }""")
    file_inps = pg.locator("input[type='file']#file-selector")
    f_cnt = file_inps.count()
    if f_cnt >= 1 and os.path.exists(BANNER_PATH):
        try:
            file_inps.nth(0).set_input_files(BANNER_PATH)
            pg.wait_for_timeout(2500)
            click_visible_done_button(pg)
            log.append("Uploaded Banner (2048x1152)")
        except Exception as e:
            log.append(f"Banner upload note: {e}")

    if f_cnt >= 2 and os.path.exists(PROFILE_PATH):
        try:
            file_inps.nth(1).set_input_files(PROFILE_PATH)
            pg.wait_for_timeout(2500)
            click_visible_done_button(pg)
            log.append("Uploaded Profile (800x800)")
        except Exception as e:
            log.append(f"Profile upload note: {e}")

    if f_cnt >= 3 and os.path.exists(WATERMARK_PATH):
        try:
            file_inps.nth(2).set_input_files(WATERMARK_PATH)
            pg.wait_for_timeout(2500)
            click_visible_done_button(pg)
            log.append("Uploaded Watermark (150x150)")
        except Exception as e:
            log.append(f"Watermark upload note: {e}")

    pg.wait_for_timeout(1500)
    pg.screenshot(path=str(KIT_DIR / "yt_phase1_before_publish.png"))

    # Click Publish (게시)
    pub_btn = pg.locator("ytcp-button#publish-button").first
    if pub_btn.count() > 0:
        pub_btn.scroll_into_view_if_needed()
        pub_btn.click(force=True)
        pg.evaluate("""() => {
            const b = document.querySelector('ytcp-button#publish-button');
            if (b) {
                b.click();
                const ib = b.querySelector('button');
                if (ib) ib.click();
            }
        }""")
        pg.wait_for_timeout(5000)
        log.append("Published Channel Profile & Branding")

    pg.screenshot(path=str(KIT_DIR / "yt_phase1_after_publish.png"))

    # 7. Settings -> Channel Keywords & Upload Defaults
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
                    kw_input.fill(CFG["keywords"], force=True)
                    pg.keyboard.press("Enter")
                    pg.wait_for_timeout(1000)
                    log.append("Filled Channel SEO Keywords")

            up_tab = pg.locator("tp-yt-paper-item:has-text('업로드 기본 설정')").first
            if up_tab.count() > 0:
                up_tab.click(force=True)
                pg.wait_for_timeout(2000)
                up_desc = pg.locator("ytcp-mention-textbox[label='설명'] div#textbox, div#textbox[aria-label*='설명']").first
                if up_desc.count() > 0 and up_desc.is_visible():
                    up_desc.fill(CFG["bulk_shorts_desc"], force=True)
                    pg.wait_for_timeout(800)
                    log.append("Set Upload Default Description")

            save_btn = pg.locator("ytcp-button#save-button, ytcp-button:has-text('저장')").first
            if save_btn.count() > 0 and save_btn.is_visible():
                save_btn.click(force=True)
                pg.wait_for_timeout(3500)
                log.append("Saved Settings & Upload Defaults")
    except Exception as e:
        log.append(f"Settings note: {e}")


def phase2_overhaul_existing_shorts(pg, log):
    print("--- [Phase 2] Bulk Overhaul Existing Shorts ---", flush=True)
    pg.goto(
        f"https://studio.youtube.com/channel/{CHANNEL_ID}/videos/short",
        wait_until="networkidle",
        timeout=45000,
    )
    pg.wait_for_timeout(4000)

    # Select all checkbox in header
    select_all = pg.locator("ytcp-checkbox-lit#selection-checkbox").first
    if select_all.count() > 0:
        select_all.click(force=True)
        pg.wait_for_timeout(1500)
        log.append("Selected all Shorts on page")

        # Click '수정' (Edit) dropdown in bulk action bar
        edit_btn = pg.locator("ytcp-button#edit-button, ytcp-button:has-text('수정')").first
        if edit_btn.count() > 0 and edit_btn.is_visible():
            edit_btn.click(force=True)
            pg.wait_for_timeout(1200)
            desc_item = pg.locator("tp-yt-paper-item:has-text('설명')").first
            if desc_item.count() > 0:
                desc_item.click(force=True)
                pg.wait_for_timeout(1500)

                # Select '모두 바꾸기' (Replace all) if dropdown exists, or fill textbox
                replace_Trigger = pg.locator("ytcp-text-dropdown-trigger:has-text('추가'), ytcp-select#edit-type-select").first
                if replace_Trigger.count() > 0 and replace_Trigger.is_visible():
                    replace_Trigger.click(force=True)
                    pg.wait_for_timeout(800)
                    rep_all = pg.locator("tp-yt-paper-item:has-text('모두 바꾸기')").first
                    if rep_all.count() > 0 and rep_all.is_visible():
                        rep_all.click(force=True)
                        pg.wait_for_timeout(800)

                bulk_box = pg.locator("ytcp-bulk-edit-description textarea, div#textbox[contenteditable='true'], textarea").first
                if bulk_box.count() > 0 and bulk_box.is_visible():
                    bulk_box.fill(CFG["bulk_shorts_desc"], force=True)
                    pg.wait_for_timeout(1000)
                    log.append("Filled Bulk Description for all Shorts")

                    # Click '동영상 수정' (Update videos)
                    apply_btn = pg.locator("ytcp-button#submit-button, ytcp-button:has-text('동영상 수정')").first
                    if apply_btn.count() > 0 and apply_btn.is_visible():
                        apply_btn.click(force=True)
                        pg.wait_for_timeout(1500)
                        confirm_chk = pg.locator("ytcp-checkbox-lit#confirm-checkbox, tp-yt-paper-dialog ytcp-checkbox-lit").first
                        if confirm_chk.count() > 0 and confirm_chk.is_visible():
                            confirm_chk.click(force=True)
                            pg.wait_for_timeout(600)
                        confirm_btn = pg.locator("tp-yt-paper-dialog ytcp-button#confirm-button, ytcp-button:has-text('동영상 수정')").last
                        if confirm_btn.count() > 0 and confirm_btn.is_visible():
                            confirm_btn.click(force=True)
                            pg.wait_for_timeout(8000)
                            log.append("Submitted Bulk Description Update for Existing Shorts")
    pg.screenshot(path=str(KIT_DIR / "yt_phase2_shorts_bulk.png"))


def phase3_overhaul_community_posts(pg, log):
    print("--- [Phase 3] Community Posts Cleanup & Official Announcement ---", flush=True)
    # 1. Go to YouTube channel Community tab to publish new official announcement post
    pg.goto(f"https://www.youtube.com/channel/{CHANNEL_ID}/community", wait_until="domcontentloaded", timeout=45000)
    pg.wait_for_timeout(4000)

    post_box = pg.locator("div#contenteditable-root[contenteditable='true']").first
    if post_box.count() > 0:
        post_box.scroll_into_view_if_needed()
        post_box.click(force=True)
        pg.wait_for_timeout(800)
        post_box.fill(CFG["community_post_text"], force=True)
        pg.wait_for_timeout(1500)

        submit_post = pg.locator("ytd-button-renderer#submit-button button, button[aria-label='게시'], button:has-text('게시')").first
        if submit_post.count() > 0:
            submit_post.click(force=True)
            pg.wait_for_timeout(4000)
            log.append("Published New Official Community Announcement Post")
    pg.screenshot(path=str(KIT_DIR / "yt_phase3_community.png"))


def phase4_upload_new_shorts_ep01(pg, log):
    print("--- [Phase 4] Upload Mastered Shorts Episode 01 ---", flush=True)
    if not os.path.exists(SHORTS_EP01_PATH):
        log.append("SHORTS_EP01_PATH not found, skipping")
        return

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
                pg.wait_for_timeout(6000)

                # Set title
                title_box = pg.locator("ytcp-social-suggestions-textbox#title-textarea div#textbox").first
                if title_box.count() > 0:
                    title_box.click(force=True)
                    title_box.fill("[김쌤의 영웅라디오] 백운호과 트롯 10대 왕자들의 기적 같은 우정! #Shorts", force=True)
                    pg.wait_for_timeout(800)

                # Set description
                desc_box = pg.locator("ytcp-social-suggestions-textbox#description-textarea div#textbox").first
                if desc_box.count() > 0:
                    desc_box.click(force=True)
                    desc_box.fill(CFG["bulk_shorts_desc"], force=True)
                    pg.wait_for_timeout(800)

                # Set NOT made for kids
                not_kids = pg.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
                if not_kids.count() > 0:
                    not_kids.scroll_into_view_if_needed()
                    not_kids.click(force=True)
                    pg.wait_for_timeout(800)

                # Click Next 3 times
                for _ in range(3):
                    next_btn = pg.locator("ytcp-button#next-button").first
                    if next_btn.count() > 0 and next_btn.is_visible():
                        next_btn.click(force=True)
                        pg.wait_for_timeout(1800)

                # Select Public (공개)
                pub_radio = pg.locator("tp-yt-paper-radio-button[name='PUBLIC']").first
                if pub_radio.count() > 0:
                    pub_radio.click(force=True)
                    pg.wait_for_timeout(1000)

                done_btn = pg.locator("ytcp-button#done-button").first
                if done_btn.count() > 0:
                    done_btn.click(force=True)
                    pg.wait_for_timeout(6000)
                    log.append("Uploaded & Published Shorts Episode 01 (1080x1920)")
    pg.screenshot(path=str(KIT_DIR / "yt_phase4_upload_ep01.png"))


def main():
    log = []
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp("http://127.0.0.1:9224")
        ctx = b.contexts[0]
        pg = [x for x in ctx.pages if "studio.youtube.com" in x.url or "youtube.com" in x.url][0]
        pg.bring_to_front()

        phase1_profile_and_settings(pg, log)
        phase2_overhaul_existing_shorts(pg, log)
        phase3_overhaul_community_posts(pg, log)
        phase4_upload_new_shorts_ep01(pg, log)

    print("FINAL_OVERHAUL_LOG:", json.dumps(log, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
