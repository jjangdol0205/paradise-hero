#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path
import websockets

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DIV4_DIR = Path(r"D:\드림컴퍼니\4사업부")
KIT_DIR = DIV4_DIR / "assets" / "youtube_kit"

PREPEND_FUNNEL_TEXT = (
    "👑 [왕자님과 나의 2샷 사진관 — 회원가입 시 1회 무료 촬영!]\n"
    "👉 https://paradise-hero.com/booth.html\n"
    "💌 [김쌤 라디오 사연 복덕방]: https://paradise-hero.com/story.html\n"
    "📰 [트로트 큰글씨 뉴스룸]: https://paradise-hero.com/news.html\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
)


class CDPPage:
    def __init__(self, ws):
        self.ws = ws
        self.msg_id = 0

    async def send(self, method: str, params: dict = None):
        self.msg_id += 1
        cur_id = self.msg_id
        payload = {"id": cur_id, "method": method, "params": params or {}}
        await self.ws.send(json.dumps(payload))
        while True:
            raw = await asyncio.wait_for(self.ws.recv(), timeout=15.0)
            msg = json.loads(raw)
            if msg.get("id") == cur_id:
                return msg.get("result", {})

    async def eval(self, expr: str):
        res = await self.send("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})
        return res.get("result", {}).get("value")

    async def click_xy(self, x: float, y: float):
        await self.send("Input.dispatchMouseEvent", {"type": "mousePressed", "x": x, "y": y, "button": "left", "clickCount": 1})
        await asyncio.sleep(0.05)
        await self.send("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": x, "y": y, "button": "left", "clickCount": 1})

    async def click_element_box(self, js_find_expr: str):
        box = await self.eval(f"""(() => {{
            const el = {js_find_expr};
            if (!el) return null;
            el.scrollIntoView({{ block: 'center' }});
            const r = el.getBoundingClientRect();
            if (r.width === 0 || r.height === 0) return null;
            return {{ x: r.left + r.width / 2, y: r.top + r.height / 2 }};
        }})()""")
        if box:
            await asyncio.sleep(0.2)
            await self.click_xy(box["x"], box["y"])
            return True
        return False

    async def screenshot(self, path: str):
        res = await self.send("Page.captureScreenshot", {"format": "png"})
        data = res.get("data")
        if data:
            Path(path).write_bytes(base64.b64decode(data))


async def run():
    with urllib.request.urlopen("http://127.0.0.1:9224/json", timeout=3) as r:
        tabs = json.loads(r.read().decode())

    studio_tab = next((t for t in tabs if t.get("type") == "page" and "studio.youtube.com" in t.get("url", "")), None)
    log = []

    if studio_tab:
        urllib.request.urlopen(f"http://127.0.0.1:9224/json/activate/{studio_tab['id']}", timeout=3)
        async with websockets.connect(studio_tab["webSocketDebuggerUrl"], max_size=50_000_000) as ws:
            cdp = CDPPage(ws)
            await cdp.send("Page.enable")
            await cdp.send("Runtime.enable")
            await asyncio.sleep(0.5)

            # ---------------------------------------------------------
            # 1. Inspect & Fix Top of /editing/profile
            # ---------------------------------------------------------
            await cdp.eval("""(() => {
                document.querySelectorAll('*').forEach(el => {
                    if (el.scrollTop > 0) el.scrollTop = 0;
                });
            })()""")
            await asyncio.sleep(1.0)
            await cdp.screenshot(str(KIT_DIR / "xy_profile_top.png"))

            profile_vals = await cdp.eval("""(() => {
                return Array.from(document.querySelectorAll('input')).map(i => ({
                    placeholder: i.placeholder,
                    val: i.value,
                    invalid: i.hasAttribute('invalid') || (i.closest('ytcp-form-input-container') && i.closest('ytcp-form-input-container').hasAttribute('invalid'))
                }));
            })()""")
            log.append(f"Profile inputs state: {profile_vals}")

            # Click '콘텐츠' on left sidebar -> 'Shorts'
            await cdp.click_element_box("Array.from(document.querySelectorAll('tp-yt-paper-icon-item')).find(el => (el.innerText || '').includes('콘텐츠'))")
            await asyncio.sleep(3.5)
            await cdp.click_element_box("Array.from(document.querySelectorAll('tp-yt-paper-tab')).find(t => (t.innerText || '').includes('Shorts'))")
            await asyncio.sleep(4.0)

            # Select all Shorts -> 전체 선택 -> 수정 -> 설명
            await cdp.click_element_box("document.querySelector('ytcp-checkbox-lit#selection-checkbox')")
            await asyncio.sleep(1.2)
            await cdp.click_element_box("Array.from(document.querySelectorAll('span, a, ytcp-button')).find(el => (el.innerText || '').trim() === '전체 선택')")
            await asyncio.sleep(1.0)
            await cdp.click_element_box("Array.from(document.querySelectorAll('ytcp-text-dropdown-trigger, ytcp-button')).find(el => (el.innerText || '').trim() === '수정')")
            await asyncio.sleep(1.0)
            await cdp.click_element_box("Array.from(document.querySelectorAll('tp-yt-paper-item')).find(el => (el.innerText || '').trim() === '설명')")
            await asyncio.sleep(1.8)

            # Click directly at (450, 470) where the '텍스트 추가' box is located!
            await cdp.click_xy(450, 470)
            await asyncio.sleep(0.5)
            await cdp.send("Input.insertText", {"text": PREPEND_FUNNEL_TEXT})
            await asyncio.sleep(1.2)
            await cdp.screenshot(str(KIT_DIR / "xy_shorts_text_typed.png"))

            # Click '동영상 업데이트' at (948, 308) or via element box
            clicked_upd = await cdp.click_element_box("Array.from(document.querySelectorAll('ytcp-button')).find(b => (b.innerText || '').includes('동영상 업데이트'))")
            await asyncio.sleep(1.8)
            await cdp.screenshot(str(KIT_DIR / "xy_shorts_confirm_modal.png"))

            # Click confirm checkbox and confirm button in dialog
            await cdp.click_element_box("document.querySelector('tp-yt-paper-dialog ytcp-checkbox-lit#confirm-checkbox') || document.querySelector('tp-yt-paper-dialog ytcp-checkbox-lit')")
            await asyncio.sleep(1.0)
            await cdp.click_element_box("document.querySelector('tp-yt-paper-dialog ytcp-button#confirm-button')")
            log.append(f"Triggered Bulk Update on all 199 Shorts: {clicked_upd}")
            await asyncio.sleep(12.0)
            await cdp.screenshot(str(KIT_DIR / "xy_shorts_bulk_completed.png"))

            # ---------------------------------------------------------
            # 2. Go to '게시물' (Posts) tab and inspect actions on rows
            # ---------------------------------------------------------
            await cdp.click_element_box("Array.from(document.querySelectorAll('tp-yt-paper-tab')).find(t => (t.innerText || '').trim() === '게시물')")
            await asyncio.sleep(4.0)

            # Hover over row 0 (our new post) and click Pin icon if available, and inspect buttons in row 1
            row_info = await cdp.eval("""(() => {
                const rows = Array.from(document.querySelectorAll('ytcp-post-row'));
                return rows.slice(0, 4).map(r => {
                    const btns = Array.from(r.querySelectorAll('ytcp-icon-button, button')).map(b => ({
                        id: b.id,
                        aria: b.getAttribute('aria-label') || '',
                        title: b.getAttribute('title') || ''
                    }));
                    return { text: (r.innerText || '').slice(0, 60), btns };
                });
            })()""")
            log.append(f"Posts rows info: {row_info}")

    print("XY_FINISH_LOG:", json.dumps(log, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(run())
