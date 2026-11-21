#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
4사업부 (UCVsUonyLFpyWHfLi0tqJzPg — @김쌤의영웅라디오)
Step 1: /editing/profile (프로필·배너·워터마크·채널명·핸들·설명·링크 3종·이메일) + 채널 키워드 & 업로드 기본 설정 완벽 적용
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
SHOT_BEFORE_PUB = str(KIT_DIR / "yt_div4_before_publish.png")
SHOT_AFTER_PUB = str(KIT_DIR / "yt_div4_after_publish.png")
SHOT_SETTINGS = str(KIT_DIR / "yt_div4_settings_saved.png")

CFG = {
    "channel_name": "김쌤의 영웅라디오",
    "handle_candidates": ["김쌤의영웅라디오", "KimTeacherHeroRadio", "paradise_hero_radio"],
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
        "김쌤의영웅라디오, 파라다이스히어로, 트로트, 트로트왕자, 트로트뉴스, 영웅시대, 파라다이스, 시니어라디오,"
    ),
    "default_upload_desc": (
        "\n\n━━━━━━━━━━━━━━━━━━━━━━\n"
        "👑 [왕자님과 나의 2샷 사진관 — 회원가입 시 1회 무료 촬영!]\n"
        "👉 https://paradise-hero.com/booth.html\n\n"
        "💌 [김쌤의 영웅라디오 사연 복덕방 — 1등 사연 방송 편성]\n"
        "👉 https://paradise-hero.com/story.html\n\n"
        "📰 [실시간 트로트 가수 뉴스룸 — 큰 글씨 보기]\n"
        "👉 https://paradise-hero.com/news.html\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "#백운호 #임영웅 #이찬원 #영탁 #정동원 #김호중 #장민호 #박서진 #손태진 #안성훈 #김쌤의영웅라디오 #김쌤의영웅라디오히어로 #트로트 #김쌤의영웅라디오"
    ),
}


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


def main():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9224")
        ctx = browser.contexts[0]
        yt_page = None
        for pg in ctx.pages:
            if "studio.youtube.com" in pg.url:
                yt_page = pg
                break
        if not yt_page:
            yt_page = ctx.new_page()

        yt_page.bring_to_front()
        yt_page.goto(
            f"https://studio.youtube.com/channel/{CHANNEL_ID}/editing/profile",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        yt_page.wait_for_timeout(5000)

        log = []

        if click_visible_done_button(yt_page):
            log.append("Closed open image crop modal")
        else:
            yt_page.keyboard.press("Escape")
            yt_page.wait_for_timeout(800)

        all_inputs = yt_page.locator("input")
        editable_indices = yt_page.evaluate("""() => {
            const list = [];
            document.querySelectorAll('input').forEach((el, i) => {
                if (el.id === 'query-input' || el.type === 'file') return;
                const r = el.getBoundingClientRect();
                if (r.width === 0 && r.height === 0) return;
                if (!el.readOnly && !el.disabled) {
                    list.push({ i, val: el.value, placeholder: el.placeholder || '', aria: el.getAttribute('aria-label') || '' });
                }
            });
            return list;
        }""")
        log.append(f"Found {len(editable_indices)} editable inputs: {editable_indices}")

        def set_input_by_global_idx(idx: int, val: str):
            el = all_inputs.nth(idx)
            el.scroll_into_view_if_needed()
            el.fill(val, force=True)
            yt_page.evaluate("""([index, value]) => {
                const el = document.querySelectorAll('input')[index];
                if (el) {
                    el.focus();
                    el.value = value;
                    el.dispatchEvent(new Event('input', { bubbles: true, composed: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true, composed: true }));
                    el.blur();
                }
            }""", [idx, val])
            yt_page.wait_for_timeout(500)

        if len(editable_indices) >= 2:
            set_input_by_global_idx(editable_indices[0]["i"], CFG["channel_name"])
            log.append(f"Set Channel Name -> {CFG['channel_name']}")

            for h_cand in CFG["handle_candidates"]:
                set_input_by_global_idx(editable_indices[1]["i"], h_cand)
                yt_page.wait_for_timeout(2200)
                body_t = yt_page.locator("body").inner_text()
                if "이미 사용 중" not in body_t and "사용할 수 없" not in body_t:
                    log.append(f"Set Handle -> @{h_cand}")
                    break

        desc_box = yt_page.locator("div#textbox[contenteditable='true']").first
        if desc_box.count() > 0:
            desc_box.scroll_into_view_if_needed()
            desc_box.fill(CFG["description"], force=True)
            yt_page.wait_for_timeout(800)
            log.append("Set Channel Description")

        # Ensure 3 link slots exist
        for _ in range(3):
            editable_now = yt_page.evaluate("""() => {
                const list = [];
                document.querySelectorAll('input').forEach((el, i) => {
                    if (el.id === 'query-input' || el.type === 'file') return;
                    const r = el.getBoundingClientRect();
                    if (r.width === 0 && r.height === 0) return;
                    if (!el.readOnly && !el.disabled) list.push({ i, val: el.value, type: el.type || '' });
                });
                return list;
            }""")
            # Count link inputs (excluding name, handle, and email)
            non_email = [x for x in editable_now if x["type"] != "email" and "이메일" not in (x.get("val") or "")]
            if len(non_email) >= 8:
                break
            add_link_btn = yt_page.locator("ytcp-button:has-text('링크 추가'), ytcp-button:has-text('Add link')").first
            if add_link_btn.count() > 0 and add_link_btn.is_visible():
                add_link_btn.scroll_into_view_if_needed()
                add_link_btn.click(force=True)
                yt_page.wait_for_timeout(1000)

        editable_after = yt_page.evaluate("""() => {
            const list = [];
            document.querySelectorAll('input').forEach((el, i) => {
                if (el.id === 'query-input' || el.type === 'file') return;
                const r = el.getBoundingClientRect();
                if (r.width === 0 && r.height === 0) return;
                if (!el.readOnly && !el.disabled) list.push({ i, val: el.value, placeholder: el.placeholder || '' });
            });
            return list;
        }""")

        for link_idx, link_item in enumerate(CFG["links"]):
            base_pos = 2 + link_idx * 2
            if len(editable_after) >= base_pos + 2:
                set_input_by_global_idx(editable_after[base_pos]["i"], link_item["title"])
                set_input_by_global_idx(editable_after[base_pos + 1]["i"], link_item["url"])
                log.append(f"Set Link {link_idx + 1} -> {link_item['title']} ({link_item['url']})")

        # Email input if visible
        if len(editable_after) >= 9:
            set_input_by_global_idx(editable_after[-1]["i"], CFG["contact_email"])
            log.append(f"Set Contact Email -> {CFG['contact_email']}")

        # Upload Banner, Profile Picture, and Watermark
        file_inputs = yt_page.locator("input[type='file']#file-selector, input[type='file']")
        f_count = file_inputs.count()
        log.append(f"Found {f_count} file inputs")

        if f_count >= 1 and os.path.exists(BANNER_PATH):
            try:
                file_inputs.nth(0).set_input_files(BANNER_PATH)
                yt_page.wait_for_timeout(2500)
                click_visible_done_button(yt_page)
                log.append("Uploaded Banner (2048x1152)")
            except Exception as e:
                log.append(f"Banner upload err: {e}")

        if f_count >= 2 and os.path.exists(PROFILE_PATH):
            try:
                file_inputs.nth(1).set_input_files(PROFILE_PATH)
                yt_page.wait_for_timeout(2500)
                click_visible_done_button(yt_page)
                log.append("Uploaded Profile Picture (800x800)")
            except Exception as e:
                log.append(f"Profile upload err: {e}")

        if f_count >= 3 and os.path.exists(WATERMARK_PATH):
            try:
                file_inputs.nth(2).set_input_files(WATERMARK_PATH)
                yt_page.wait_for_timeout(2500)
                click_visible_done_button(yt_page)
                log.append("Uploaded Video Watermark (150x150)")
            except Exception as e:
                log.append(f"Watermark upload err: {e}")

        yt_page.screenshot(path=SHOT_BEFORE_PUB)

        pub_btn = yt_page.locator("ytcp-button#publish-button").first
        if pub_btn.count() > 0:
            pub_btn.scroll_into_view_if_needed()
            yt_page.wait_for_timeout(1000)
            pub_btn.click(force=True)
            yt_page.evaluate("""() => {
                const b = document.querySelector('ytcp-button#publish-button');
                if (b) {
                    b.click();
                    const ib = b.querySelector('button');
                    if (ib) ib.click();
                }
            }""")
            yt_page.wait_for_timeout(5000)
            log.append("Clicked Publish (게시)")

        yt_page.screenshot(path=SHOT_AFTER_PUB)

        # Settings -> Channel (Keywords) & Upload Defaults (업로드 기본 설정)
        try:
            settings_btn = yt_page.locator("tp-yt-paper-icon-item#settings-item, tp-yt-paper-icon-item:has-text('설정')").first
            if settings_btn.count() > 0:
                settings_btn.click(force=True)
                yt_page.wait_for_timeout(2500)
                ch_tab = yt_page.locator("tp-yt-paper-item:has-text('채널')").first
                if ch_tab.count() > 0:
                    ch_tab.click(force=True)
                    yt_page.wait_for_timeout(2000)
                    kw_input = yt_page.locator("ytcp-chip-bar input#text-input, input[aria-label*='키워드'], input[placeholder*='키워드']").first
                    if kw_input.count() > 0 and kw_input.is_visible():
                        kw_input.fill(CFG["keywords"], force=True)
                        yt_page.keyboard.press("Enter")
                        yt_page.wait_for_timeout(1000)
                        log.append("Filled Channel SEO Keywords")

                up_tab = yt_page.locator("tp-yt-paper-item:has-text('업로드 기본 설정')").first
                if up_tab.count() > 0:
                    up_tab.click(force=True)
                    yt_page.wait_for_timeout(2000)
                    up_desc = yt_page.locator("ytcp-mention-textbox[label='설명'] div#textbox, div#textbox[aria-label*='설명']").first
                    if up_desc.count() > 0 and up_desc.is_visible():
                        up_desc.fill(CFG["default_upload_desc"], force=True)
                        yt_page.wait_for_timeout(800)
                        log.append("Set Default Upload Description Funnel")

                yt_page.screenshot(path=SHOT_SETTINGS)
                save_btn = yt_page.locator("ytcp-button#save-button, ytcp-button:has-text('저장')").first
                if save_btn.count() > 0 and save_btn.is_visible():
                    save_btn.click(force=True)
                    yt_page.wait_for_timeout(3000)
                    log.append("Saved Channel Settings & Upload Defaults")
        except Exception as e:
            log.append(f"Settings step note: {e}")

        print("RESULT:", json.dumps(log, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
