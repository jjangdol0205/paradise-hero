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
PROFILE_PATH = str(KIT_DIR / "youtube_profile_800x800.png")
WATERMARK_PATH = str(KIT_DIR / "youtube_watermark_150x150.png")

DESCRIPTION = (
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
)

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
            await cdp.send("DOM.enable")
            await cdp.send("Runtime.enable")
            await asyncio.sleep(1.0)

            # ---------------------------------------------------------
            # 1. On Shorts tab: Select All -> 수정 -> 설명 -> 첫 부분에 삽입 -> 동영상 업데이트
            # ---------------------------------------------------------
            clicked_cb = await cdp.click_element_box("document.querySelector('ytcp-checkbox-lit#selection-checkbox')")
            await asyncio.sleep(1.5)
            log.append(f"Clicked Select All on Shorts: {clicked_cb}")

            # Also click '전체 선택' if visible so all 199 shorts are selected
            await cdp.click_element_box("Array.from(document.querySelectorAll('span, a, ytcp-button')).find(el => (el.innerText || '').trim() === '전체 선택')")
            await asyncio.sleep(1.0)

            # Click '수정' dropdown trigger
            clicked_edit = await cdp.click_element_box("Array.from(document.querySelectorAll('ytcp-text-dropdown-trigger, ytcp-button')).find(el => (el.innerText || '').trim() === '수정')")
            await asyncio.sleep(1.2)
            log.append(f"Clicked Edit dropdown: {clicked_edit}")

            # Click '설명' menu item
            clicked_desc_menu = await cdp.click_element_box("Array.from(document.querySelectorAll('tp-yt-paper-item')).find(el => (el.innerText || '').trim() === '설명')")
            await asyncio.sleep(1.8)
            log.append(f"Clicked Description item: {clicked_desc_menu}")

            # Focus the text box inside ytcp-bulk-edit-description by real mouse click
            clicked_bulk_input = await cdp.click_element_box("document.querySelector('ytcp-bulk-edit-description textarea') || document.querySelector('ytcp-bulk-edit-description #textbox') || document.querySelector('ytcp-bulk-edit-description ytcp-form-textarea')")
            await asyncio.sleep(0.8)
            log.append(f"Clicked bulk text area: {clicked_bulk_input}")

            if clicked_bulk_input:
                await cdp.send("Input.insertText", {"text": PREPEND_FUNNEL_TEXT})
                await asyncio.sleep(1.2)
                clicked_upd = await cdp.click_element_box("Array.from(document.querySelectorAll('ytcp-button')).find(b => (b.innerText || '').includes('동영상 업데이트'))")
                log.append(f"Clicked 동영상 업데이트 button: {clicked_upd}")
                await asyncio.sleep(1.8)

                # Click confirm checkbox in dialog
                clicked_conf_chk = await cdp.click_element_box("document.querySelector('tp-yt-paper-dialog ytcp-checkbox-lit#confirm-checkbox') || document.querySelector('tp-yt-paper-dialog ytcp-checkbox-lit')")
                await asyncio.sleep(1.0)
                clicked_conf_btn = await cdp.click_element_box("document.querySelector('tp-yt-paper-dialog ytcp-button#confirm-button')")
                log.append(f"Confirmed Bulk Update dialog: chk={clicked_conf_chk}, btn={clicked_conf_btn}")
                await asyncio.sleep(14.0)
            await cdp.screenshot(str(KIT_DIR / "spa_step1_shorts_bulk.png"))

            # ---------------------------------------------------------
            # 2. Click '게시물' (Posts) tab in Content to delete old May 2026 Coupang posts
            # ---------------------------------------------------------
            clicked_posts_tab = await cdp.click_element_box("Array.from(document.querySelectorAll('tp-yt-paper-tab')).find(t => (t.innerText || '').trim() === '게시물')")
            await asyncio.sleep(4.0)
            log.append(f"Clicked Posts tab: {clicked_posts_tab}")

            # Hover and delete old Coupang posts
            deleted_posts = 0
            for _ in range(7):
                # Find a row that has '쿠팡' or '특가'
                row_box = await cdp.eval("""(() => {
                    const rows = Array.from(document.querySelectorAll('ytcp-post-row'));
                    for (const r of rows) {
                        const txt = r.innerText || '';
                        if (txt.includes('쿠팡') || txt.includes('특가') || txt.includes('2026. 5.')) {
                            r.scrollIntoView({ block: 'center' });
                            const rect = r.getBoundingClientRect();
                            return { x: rect.left + 300, y: rect.top + rect.height / 2 };
                        }
                    }
                    return null;
                })()""")
                if not row_box:
                    break
                # Move mouse over the row so action icons appear
                await cdp.send("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": row_box["x"], "y": row_box["y"]})
                await asyncio.sleep(0.6)
                clicked_opt = await cdp.click_element_box("""(() => {
                    const rows = Array.from(document.querySelectorAll('ytcp-post-row'));
                    for (const r of rows) {
                        const txt = r.innerText || '';
                        if (txt.includes('쿠팡') || txt.includes('특가') || txt.includes('2026. 5.')) {
                            return r.querySelector('ytcp-icon-button[aria-label*="옵션"], ytcp-icon-button#menu-button, ytcp-icon-button:last-of-type');
                        }
                    }
                    return null;
                })()""")
                if not clicked_opt:
                    break
                await asyncio.sleep(0.8)
                clicked_del = await cdp.click_element_box("Array.from(document.querySelectorAll('tp-yt-paper-item')).find(i => (i.innerText || '').includes('삭제'))")
                if clicked_del:
                    await asyncio.sleep(0.8)
                    await cdp.click_element_box("document.querySelector('tp-yt-paper-dialog ytcp-button#confirm-button') || Array.from(document.querySelectorAll('tp-yt-paper-dialog ytcp-button')).find(b => (b.innerText || '').includes('삭제'))")
                    await asyncio.sleep(2.5)
                    deleted_posts += 1
            log.append(f"Deleted {deleted_posts} old Coupang posts in Studio")
            await cdp.screenshot(str(KIT_DIR / "spa_step2_posts_cleaned.png"))

            # ---------------------------------------------------------
            # 3. Click '맞춤설정' on left sidebar (SPA navigation!)
            # ---------------------------------------------------------
            clicked_cust = await cdp.click_element_box("Array.from(document.querySelectorAll('tp-yt-paper-icon-item')).find(el => (el.innerText || '').includes('맞춤설정'))")
            await asyncio.sleep(4.5)
            log.append(f"Clicked Customization sidebar: {clicked_cust}")

            # Click retry if visible
            await cdp.click_element_box("document.querySelector('ytcp-button#error-retry-button')")
            await asyncio.sleep(2.5)

            # Upload Banner, Profile, Watermark via DOM.setFileInputFiles
            doc = await cdp.send("DOM.getDocument", {"depth": -1, "pierce": True})
            root_id = doc["root"]["nodeId"]
            q_res = await cdp.send("DOM.querySelectorAll", {"nodeId": root_id, "selector": "input[type='file']"})
            node_ids = q_res.get("nodeIds", [])
            for idx, fpath in [(0, BANNER_PATH), (1, PROFILE_PATH), (2, WATERMARK_PATH)]:
                if idx < len(node_ids) and os.path.exists(fpath):
                    await cdp.send("DOM.setFileInputFiles", {"nodeId": node_ids[idx], "files": [fpath]})
                    await asyncio.sleep(2.5)
                    await cdp.click_element_box("Array.from(document.querySelectorAll('ytcp-button#done-button')).find(b => b.getBoundingClientRect().width > 0)")
                    await asyncio.sleep(2.0)

            # Set Email cleanly via real mouse click + Ctrl+A + Backspace + insertText
            clicked_email = await cdp.click_element_box("document.querySelector(\"input[placeholder='이메일 주소']\")")
            if clicked_email:
                await cdp.eval("document.querySelector(\"input[placeholder='이메일 주소']\").select()")
                await cdp.send("Input.insertText", {"text": "beable9489@gmail.com"})
                await asyncio.sleep(0.5)

            # Set Description if visible
            clicked_desc = await cdp.click_element_box("document.querySelector(\"div#textbox[contenteditable='true']\")")
            if clicked_desc:
                await cdp.eval("document.execCommand('selectAll', false, null)")
                await cdp.send("Input.insertText", {"text": DESCRIPTION})
                await asyncio.sleep(0.8)

            # Add 3 links
            for _ in range(3):
                cnt = await cdp.eval("document.querySelectorAll(\"input[placeholder='제목 입력']\").length")
                if cnt and cnt >= 3:
                    break
                await cdp.click_element_box("Array.from(document.querySelectorAll('ytcp-button')).find(b => (b.innerText || '').includes('링크 추가'))")
                await asyncio.sleep(0.8)

            links_data = [
                ("왕자님 투샷 사진관(1회무료)", "https://paradise-hero.com/booth.html"),
                ("김쌤 라디오 사연 복덕방", "https://paradise-hero.com/story.html"),
                ("파라다이스히어로 트로트뉴스", "https://paradise-hero.com/news.html"),
            ]
            for i, (lt, lu) in enumerate(links_data):
                ok_t = await cdp.click_element_box(f"document.querySelectorAll(\"input[placeholder='제목 입력']\")[{i}]")
                if ok_t:
                    await cdp.eval(f"document.querySelectorAll(\"input[placeholder='제목 입력']\")[{i}].select()")
                    await cdp.send("Input.insertText", {"text": lt})
                    await asyncio.sleep(0.3)
                ok_u = await cdp.click_element_box(f"document.querySelectorAll(\"input[placeholder='URL 입력']\")[{i}]")
                if ok_u:
                    await cdp.eval(f"document.querySelectorAll(\"input[placeholder='URL 입력']\")[{i}].select()")
                    await cdp.send("Input.insertText", {"text": lu})
                    await asyncio.sleep(0.3)

            await asyncio.sleep(1.5)
            pub_clicked = await cdp.click_element_box("document.querySelector('ytcp-button#publish-button:not([disabled])')")
            await asyncio.sleep(5.0)
            log.append(f"Clicked Publish on Customization: {pub_clicked}")
            await cdp.screenshot(str(KIT_DIR / "spa_step3_profile_done.png"))

    print("SPA_COMPLETE_LOG:", json.dumps(log, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(run())
