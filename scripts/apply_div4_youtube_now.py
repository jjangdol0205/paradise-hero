#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
4사업부 (@김쌤의영웅라디오 — paradise-hero.com)
YouTube Studio 채널 브랜딩(배너/프로필/워터마크) 및
채널명·핸들·설명·링크 3종·이메일·채널 키워드 원클릭 자동 세팅 스크립트
"""
import argparse
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DIV4_DIR = Path(r"D:\드림컴퍼니\4사업부")
KIT_DIR = DIV4_DIR / "assets" / "youtube_kit"
PROFILE_DIR = DIV4_DIR / ".youtube_studio_chrome_profile"
CDP_PORT = 9224

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
}


def is_port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0)
        return s.connect_ex(("127.0.0.1", port)) == 0


def launch_chrome_if_needed(port: int) -> int:
    # First check if port 9224 is open
    if is_port_open(port):
        return port
    # Launch dedicated Chrome instance on port 9224 with persistent profile
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    chrome_exe = next((p for p in chrome_paths if os.path.exists(p)), "chrome.exe")
    subprocess.Popen(
        [
            chrome_exe,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={PROFILE_DIR}",
            "--no-first-run",
            "--no-default-browser-check",
            "--start-maximized",
            "https://studio.youtube.com",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(20):
        if is_port_open(port):
            break
        time.sleep(0.5)
    return port


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


def check_or_open(port: int):
    active_port = launch_chrome_if_needed(port)
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{active_port}")
        ctx = browser.contexts[0]
        yt_page = None
        for pg in ctx.pages:
            if "studio.youtube.com" in pg.url or "accounts.google.com" in pg.url or "youtube.com" in pg.url:
                yt_page = pg
                break
        if not yt_page:
            yt_page = ctx.new_page()
            yt_page.goto("https://studio.youtube.com", wait_until="domcontentloaded", timeout=30000)
            yt_page.wait_for_timeout(3000)

        yt_page.bring_to_front()
        url = yt_page.url
        logged_in = "studio.youtube.com/channel/" in url
        print(json.dumps({
            "cdp_port": active_port,
            "url": url,
            "logged_in": logged_in,
            "message": "Ready to apply settings!" if logged_in else "Waiting for Google/YouTube Studio login in Chrome window."
        }, ensure_ascii=False, indent=2))
        return logged_in


def apply_youtube_settings(port: int):
    active_port = launch_chrome_if_needed(port)
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"http://127.0.0.1:{active_port}")
        ctx = browser.contexts[0]
        yt_page = None
        for pg in ctx.pages:
            if "studio.youtube.com" in pg.url:
                yt_page = pg
                break
        if not yt_page:
            print(json.dumps({"ok": False, "error": "No studio.youtube.com tab found. Please log in first."}, ensure_ascii=False))
            return

        yt_page.bring_to_front()
        yt_page.wait_for_timeout(2000)

        # Navigate to Customization (맞춤설정)
        if "/editing" not in yt_page.url:
            cust_nav = yt_page.locator(
                "a[href*='/editing'], #menu-paper-icon-item-3, "
                "tp-yt-paper-icon-item:has-text('맞춤설정'), "
                "tp-yt-paper-icon-item:has-text('Customization')"
            ).first
            if cust_nav.count() > 0:
                cust_nav.click(force=True)
                yt_page.wait_for_timeout(4000)

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
                    list.push({ i, val: el.value });
                }
            });
            return list;
        }""")
        log.append(f"Found {len(editable_indices)} editable inputs")

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

        # Add Links up to 3
        for _ in range(3):
            add_link_btn = yt_page.locator("ytcp-button:has-text('링크 추가'), ytcp-button:has-text('Add link')").first
            if add_link_btn.count() > 0 and add_link_btn.is_visible():
                editable_now = yt_page.evaluate("""() => {
                    const list = [];
                    document.querySelectorAll('input').forEach((el, i) => {
                        if (el.id === 'query-input' || el.type === 'file') return;
                        const r = el.getBoundingClientRect();
                        if (r.width === 0 && r.height === 0) return;
                        if (!el.readOnly && !el.disabled) list.push({ i, val: el.value });
                    });
                    return list;
                }""")
                if len(editable_now) >= 8:
                    break
                add_link_btn.scroll_into_view_if_needed()
                add_link_btn.click(force=True)
                yt_page.wait_for_timeout(1000)

        editable_after = yt_page.evaluate("""() => {
            const list = [];
            document.querySelectorAll('input').forEach((el, i) => {
                if (el.id === 'query-input' || el.type === 'file') return;
                const r = el.getBoundingClientRect();
                if (r.width === 0 && r.height === 0) return;
                if (!el.readOnly && !el.disabled) list.push({ i, val: el.value });
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
        email_inputs = yt_page.locator("input[type='email'], input[aria-label*='이메일'], input[aria-label*='Email']")
        if email_inputs.count() > 0 and email_inputs.first.is_visible():
            email_inputs.first.scroll_into_view_if_needed()
            email_inputs.first.fill(CFG["contact_email"], force=True)
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

        # Settings -> Channel -> Keywords
        try:
            settings_btn = yt_page.locator("tp-yt-paper-icon-item#settings-item, tp-yt-paper-icon-item:has-text('설정')").first
            if settings_btn.count() > 0:
                settings_btn.click(force=True)
                yt_page.wait_for_timeout(2500)
                ch_tab = yt_page.locator("tp-yt-paper-item:has-text('채널'), tp-yt-paper-item:has-text('Channel')").first
                if ch_tab.count() > 0:
                    ch_tab.click(force=True)
                    yt_page.wait_for_timeout(2000)
                    kw_input = yt_page.locator("ytcp-chip-bar input#text-input, input[aria-label*='키워드'], input[placeholder*='키워드']").first
                    if kw_input.count() > 0 and kw_input.is_visible():
                        kw_input.fill(CFG["keywords"], force=True)
                        yt_page.keyboard.press("Enter")
                        yt_page.wait_for_timeout(1000)
                        log.append("Filled Channel SEO Keywords")
                    yt_page.screenshot(path=SHOT_SETTINGS)
                    save_btn = yt_page.locator("ytcp-button#save-button, ytcp-button:has-text('저장')").first
                    if save_btn.count() > 0 and save_btn.is_visible():
                        save_btn.click(force=True)
                        yt_page.wait_for_timeout(3000)
                        log.append("Saved Channel Settings")
        except Exception as e:
            log.append(f"Settings step note: {e}")

        print("RESULT:", json.dumps(log, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=CDP_PORT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.apply:
        apply_youtube_settings(args.port)
    else:
        check_or_open(args.port)
