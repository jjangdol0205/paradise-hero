#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import sys
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9224")
    ctx = b.contexts[0]
    pg = [x for x in ctx.pages if "studio.youtube.com" in x.url][0]
    pg.goto("https://studio.youtube.com/channel/UCVsUonyLFpyWHfLi0tqJzPg/editing/profile", wait_until="networkidle", timeout=30000)
    pg.wait_for_timeout(3000)

    # Click retry button if visible
    retry_btn = pg.locator("ytcp-button#error-retry-button")
    if retry_btn.count() > 0 and retry_btn.first.is_visible():
        retry_btn.first.click(force=True)
        pg.wait_for_timeout(3000)

    # Scroll top
    pg.evaluate("""() => {
        document.querySelectorAll('*').forEach(el => {
            if (el.scrollTop > 0) el.scrollTop = 0;
        });
    }""")
    pg.wait_for_timeout(1000)
    pg.screenshot(path=r"D:\드림컴퍼니\4사업부\assets\youtube_kit\yt_div4_top.png")

    # Find all inputs including shadow DOM
    shadow_inputs = pg.evaluate("""() => {
        const results = [];
        function walk(root, path='') {
            const els = root.querySelectorAll ? root.querySelectorAll('*') : [];
            els.forEach((el, i) => {
                if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.getAttribute('contenteditable') === 'true') {
                    results.push({
                        tag: el.tagName,
                        id: el.id,
                        type: el.type || '',
                        placeholder: el.placeholder || '',
                        aria: el.getAttribute('aria-label') || '',
                        val: el.value !== undefined ? el.value : el.innerText.slice(0, 50),
                        disabled: !!el.disabled,
                        readOnly: !!el.readOnly,
                        path: path + '/' + el.tagName + (el.id ? '#' + el.id : '')
                    });
                }
                if (el.shadowRoot) {
                    walk(el.shadowRoot, path + '/' + el.tagName + '#shadow');
                }
            });
        }
        walk(document);
        return results;
    }""")
    print(json.dumps(shadow_inputs, ensure_ascii=False, indent=2))
