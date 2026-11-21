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
BANNER_PATH = str(KIT_DIR / "youtube_banner_2048x1152.png")
WATERMARK_PATH = str(KIT_DIR / "youtube_watermark_150x150.png")

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

    async def click_visible(self, selector_or_fn: str):
        box = await self.eval(f"""(() => {{
            const els = Array.from(document.querySelectorAll({json.dumps(selector_or_fn)}));
            const el = els.find(e => e.getBoundingClientRect().width > 0 && e.getBoundingClientRect().height > 0);
            if (!el) return null;
            el.scrollIntoView({{ block: 'center' }});
            const r = el.getBoundingClientRect();
            return {{ x: r.left + r.width / 2, y: r.top + r.height / 2 }};
        }})()""")
        if box:
            await asyncio.sleep(0.25)
            await self.click_xy(box["x"], box["y"])
            return True
        return False

    async def click_visible_text(self, selector: str, text_sub: str):
        box = await self.eval(f"""(() => {{
            const els = Array.from(document.querySelectorAll({json.dumps(selector)}));
            const el = els.find(e => (e.innerText || '').includes({json.dumps(text_sub)}) && e.getBoundingClientRect().width > 0 && e.getBoundingClientRect().height > 0);
            if (!el) return null;
            el.scrollIntoView({{ block: 'center' }});
            const r = el.getBoundingClientRect();
            return {{ x: r.left + r.width / 2, y: r.top + r.height / 2 }};
        }})()""")
        if box:
            await asyncio.sleep(0.25)
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
            await cdp.send("DOM.enable")
            await cdp.send("Runtime.enable")
            await asyncio.sleep(0.5)

            # ---------------------------------------------------------
            # 1. Pin our new Official Community Post on '게시물' tab
            # ---------------------------------------------------------
            await cdp.click_visible_text("tp-yt-paper-icon-item", "콘텐츠")
            await asyncio.sleep(3.0)
            await cdp.click_visible_text("tp-yt-paper-tab", "게시물")
            await asyncio.sleep(3.5)

            # Hover over Row 0 and click '커뮤니티에 고정'
            r0 = await cdp.eval("""(() => {
                const row = document.querySelector('ytcp-post-row');
                if (!row) return null;
                const r = row.getBoundingClientRect();
                return { x: r.left + 250, y: r.top + r.height / 2 };
            })()""")
            if r0:
                await cdp.send("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": r0["x"], "y": r0["y"]})
                await asyncio.sleep(0.8)
                pinned = await cdp.click_visible("button[aria-label='커뮤니티에 고정'], ytcp-icon-button[aria-label='커뮤니티에 고정']")
                await asyncio.sleep(1.5)
                # Confirm pin if dialog appears
                await cdp.click_visible("tp-yt-paper-dialog ytcp-button#confirm-button")
                await asyncio.sleep(2.0)
                log.append(f"Pinned new Official Community Post: {pinned}")
            await cdp.screenshot(str(KIT_DIR / "final1_post_pinned.png"))

            # ---------------------------------------------------------
            # 2. Bulk Update All 199 Shorts Descriptions on 'Shorts' tab
            # ---------------------------------------------------------
            await cdp.click_visible_text("tp-yt-paper-tab", "Shorts")
            await asyncio.sleep(4.0)

            sel_ok = await cdp.click_visible("ytcp-checkbox-lit#selection-checkbox")
            await asyncio.sleep(1.5)
            sel_all_ok = await cdp.click_visible_text("span, a, ytcp-button", "전체 선택")
            await asyncio.sleep(1.0)
            edit_ok = await cdp.click_visible_text("ytcp-text-dropdown-trigger, ytcp-button", "수정")
            await asyncio.sleep(1.0)
            desc_ok = await cdp.click_visible_text("tp-yt-paper-item", "설명")
            await asyncio.sleep(1.8)
            log.append(f"Shorts bulk bar: sel={sel_ok}, selAll={sel_all_ok}, edit={edit_ok}, desc={desc_ok}")

            # Click at (450, 470) to focus the '텍스트 추가' box
            await cdp.click_xy(450, 470)
            await asyncio.sleep(0.6)
            await cdp.send("Input.insertText", {"text": PREPEND_FUNNEL_TEXT})
            await asyncio.sleep(1.2)

            upd_ok = await cdp.click_visible_text("ytcp-button", "동영상 업데이트")
            await asyncio.sleep(1.8)
            chk_ok = await cdp.click_visible("tp-yt-paper-dialog ytcp-checkbox-lit")
            await asyncio.sleep(1.0)
            conf_ok = await cdp.click_visible("tp-yt-paper-dialog ytcp-button#confirm-button")
            log.append(f"Shorts Bulk Update submitted: upd={upd_ok}, chk={chk_ok}, conf={conf_ok}")
            await asyncio.sleep(14.0)
            await cdp.screenshot(str(KIT_DIR / "final2_shorts_bulk_done.png"))

            # ---------------------------------------------------------
            # 3. Go to '맞춤설정' -> Fill '핸들 설정', Upload Banner & Watermark, Add 3 Links, Publish!
            # ---------------------------------------------------------
            await cdp.click_visible_text("tp-yt-paper-icon-item", "맞춤설정")
            await asyncio.sleep(4.5)

            # Scroll up to top first
            await cdp.eval("""(() => {
                document.querySelectorAll('*').forEach(el => {
                    if (el.scrollTop > 0) el.scrollTop = 0;
                });
            })()""")
            await asyncio.sleep(1.0)

            # Fill '핸들 설정' so Publish button is enabled!
            h_ok = await cdp.click_visible("input[placeholder='핸들 설정']")
            if h_ok:
                await cdp.eval("document.querySelector(\"input[placeholder='핸들 설정']\").select()")
                await cdp.send("Input.insertText", {"text": "김쌤의영웅라디오"})
                await asyncio.sleep(2.5)
                log.append("Filled Handle -> 김쌤의영웅라디오")

            # Upload Banner & Watermark via DOM.setFileInputFiles
            doc = await cdp.send("DOM.getDocument", {"depth": -1, "pierce": True})
            root_id = doc["root"]["nodeId"]
            q_res = await cdp.send("DOM.querySelectorAll", {"nodeId": root_id, "selector": "input[type='file']"})
            node_ids = q_res.get("nodeIds", [])
            for idx, fpath in [(0, BANNER_PATH), (2, WATERMARK_PATH)]:
                if idx < len(node_ids) and os.path.exists(fpath):
                    await cdp.send("DOM.setFileInputFiles", {"nodeId": node_ids[idx], "files": [fpath]})
                    await asyncio.sleep(2.5)
                    await cdp.click_visible("ytcp-button#done-button")
                    await asyncio.sleep(2.0)

            # Fill Email
            e_ok = await cdp.click_visible("input[placeholder='이메일 주소']")
            if e_ok:
                await cdp.eval("document.querySelector(\"input[placeholder='이메일 주소']\").select()")
                await cdp.send("Input.insertText", {"text": "beable9489@gmail.com"})
                await asyncio.sleep(0.6)

            # Add 3 Links
            for _ in range(3):
                cnt = await cdp.eval("document.querySelectorAll(\"input[placeholder='제목 입력']\").length")
                if cnt and cnt >= 3:
                    break
                await cdp.click_visible_text("ytcp-button", "링크 추가")
                await asyncio.sleep(0.8)

            links_data = [
                ("왕자님 투샷 사진관(1회무료)", "https://paradise-hero.com/booth.html"),
                ("김쌤 라디오 사연 복덕방", "https://paradise-hero.com/story.html"),
                ("파라다이스히어로 트로트뉴스", "https://paradise-hero.com/news.html"),
            ]
            for i, (lt, lu) in enumerate(links_data):
                box_t = await cdp.eval(f"""(() => {{
                    const el = document.querySelectorAll("input[placeholder='제목 입력']")[{i}];
                    if (!el) return null;
                    el.scrollIntoView({{ block: 'center' }});
                    const r = el.getBoundingClientRect();
                    return {{ x: r.left + r.width / 2, y: r.top + r.height / 2 }};
                }})()""")
                if box_t:
                    await cdp.click_xy(box_t["x"], box_t["y"])
                    await asyncio.sleep(0.2)
                    await cdp.eval(f"document.querySelectorAll(\"input[placeholder='제목 입력']\")[{i}].select()")
                    await cdp.send("Input.insertText", {"text": lt})
                    await asyncio.sleep(0.3)

                box_u = await cdp.eval(f"""(() => {{
                    const el = document.querySelectorAll("input[placeholder='URL 입력']")[{i}];
                    if (!el) return null;
                    el.scrollIntoView({{ block: 'center' }});
                    const r = el.getBoundingClientRect();
                    return {{ x: r.left + r.width / 2, y: r.top + r.height / 2 }};
                }})()""")
                if box_u:
                    await cdp.click_xy(box_u["x"], box_u["y"])
                    await asyncio.sleep(0.2)
                    await cdp.eval(f"document.querySelectorAll(\"input[placeholder='URL 입력']\")[{i}].select()")
                    await cdp.send("Input.insertText", {"text": lu})
                    await asyncio.sleep(0.3)

            await asyncio.sleep(1.5)
            pub_ok = await cdp.click_visible("ytcp-button#publish-button:not([disabled])")
            await asyncio.sleep(5.0)
            log.append(f"Published Profile & Links: {pub_ok}")
            await cdp.screenshot(str(KIT_DIR / "final3_profile_published.png"))

    print("FINAL_THREE_LOG:", json.dumps(log, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(run())
