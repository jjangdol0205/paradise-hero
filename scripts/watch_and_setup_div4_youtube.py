#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
4사업부 (@김쌤의영웅라디오 — paradise-hero.com)
상주형 YouTube Studio & Instagram 브라우저 런처 + 로그인 감지 시 즉시 자동 세팅 데몬
"""
import json
import os
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


def main():
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        print("[Div4 YouTube Daemon] Launching visible Chrome window on port 9224...", flush=True)
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            channel="chrome",
            headless=False,
            args=[
                f"--remote-debugging-port={CDP_PORT}",
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--no-first-run",
                "--no-default-browser-check",
            ],
            no_viewport=True,
        )
        yt_page = ctx.pages[0] if ctx.pages else ctx.new_page()
        yt_page.goto("https://studio.youtube.com", wait_until="domcontentloaded", timeout=60000)
        yt_page.bring_to_front()
        print(f"[Div4 YouTube Daemon] Chrome window opened! Current URL: {yt_page.url}", flush=True)

        # Keep the browser alive indefinitely so user can log in and we can run apply_div4_youtube_now.py
        while True:
            time.sleep(2)


if __name__ == "__main__":
    main()
