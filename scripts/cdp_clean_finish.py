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
CHANNEL_ID = "UCVsUonyLFpyWHfLi0tqJzPg"
BANNER_PATH = str(KIT_DIR / "youtube_banner_2048x1152.png")

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

    async def clear_and_type(self, selector: str, text: str):
        ok = await self.eval(f"""(() => {{
            const el = document.querySelector("{selector}");
            if (!el) return false;
            el.scrollIntoView({{ block: 'center' }});
            el.focus();
            el.click();
            if (el.value !== undefined) {{
                el.value = '';
                el.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
            }} else {{
                el.innerText = '';
                el.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
            }}
            return true;
        }})()""")
        if ok:
            await asyncio.sleep(0.2)
            await self.send("Input.insertText", {"text": text})
            await asyncio.sleep(0.3)
            await self.eval(f"""(() => {{
                const el = document.querySelector("{selector}");
                if (el) {{
                    el.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                    el.dispatchEvent(new Event('change', {{ bubbles: true, composed: true }}));
                    el.blur();
                }}
            }})()""")
            await asyncio.sleep(0.3)
        return ok

    async def screenshot(self, path: str):
        res = await self.send("Page.captureScreenshot", {"format": "png"})
        data = res.get("data")
        if data:
            Path(path).write_bytes(base64.b64decode(data))


async def run():
    with urllib.request.urlopen("http://127.0.0.1:9224/json", timeout=3) as r:
        tabs = json.loads(r.read().decode())

    studio_tab = next((t for t in tabs if t.get("type") == "page" and "studio.youtube.com" in t.get("url", "")), None)
    comm_tab = next((t for t in tabs if t.get("type") == "page" and "youtube.com/channel/" in t.get("url", "")), None)

    log = []

    # ---------------------------------------------------------
    # 1. Studio Tab: Clean /editing/profile & Publish, then Bulk Edit Shorts
    # ---------------------------------------------------------
    if studio_tab:
        urllib.request.urlopen(f"http://127.0.0.1:9224/json/activate/{studio_tab['id']}", timeout=3)
        async with websockets.connect(studio_tab["webSocketDebuggerUrl"], max_size=50_000_000) as ws:
            cdp = CDPPage(ws)
            await cdp.send("Page.enable")
            await cdp.send("DOM.enable")
            await cdp.send("Runtime.enable")
            await asyncio.sleep(1.0)

            # Discard any dirty state on /editing/profile first
            await cdp.eval("""(() => {
                const disc = document.querySelector('ytcp-button#discard-changes-button');
                if (disc && !disc.hasAttribute('disabled')) {
                    disc.click();
                    const ib = disc.querySelector('button');
                    if (ib) ib.click();
                }
            })()""")
            await asyncio.sleep(1.5)

            # Reload /editing/profile cleanly
            await cdp.eval(f"window.onbeforeunload = null; window.location.href = 'https://studio.youtube.com/channel/{CHANNEL_ID}/editing/profile';")
            await asyncio.sleep(5.0)

            # Click retry if needed
            await cdp.eval("""(() => {
                const retry = document.querySelector('ytcp-button#error-retry-button');
                if (retry && retry.getBoundingClientRect().width > 0) {
                    retry.click();
                    const ib = retry.querySelector('button');
                    if (ib) ib.click();
                }
            })()""")
            await asyncio.sleep(3.0)

            # Upload Banner via DOM.setFileInputFiles
            doc = await cdp.send("DOM.getDocument", {"depth": -1, "pierce": True})
            root_id = doc["root"]["nodeId"]
            q_res = await cdp.send("DOM.querySelectorAll", {"nodeId": root_id, "selector": "input[type='file']"})
            node_ids = q_res.get("nodeIds", [])
            if len(node_ids) >= 1 and os.path.exists(BANNER_PATH):
                await cdp.send("DOM.setFileInputFiles", {"nodeId": node_ids[0], "files": [BANNER_PATH]})
                await asyncio.sleep(2.5)
                await cdp.eval("""(() => {
                    const btns = Array.from(document.querySelectorAll('ytcp-button#done-button'));
                    for (const b of btns) {
                        if (b.getBoundingClientRect().width > 0) {
                            b.click();
                            const ib = b.querySelector('button');
                            if (ib) ib.click();
                        }
                    }
                })()""")
                await asyncio.sleep(2.0)
                log.append("Uploaded Banner (2048x1152)")

            # Fill Name, Handle, Description, Email cleanly
            r_name = await cdp.clear_and_type("input[placeholder='채널 이름 입력']", "김쌤의 영웅라디오")
            r_handle = await cdp.clear_and_type("input[placeholder='핸들 설정']", "김쌤의영웅라디오")
            await asyncio.sleep(1.5)
            r_desc = await cdp.clear_and_type("div#textbox[contenteditable='true']", DESCRIPTION)
            r_email = await cdp.clear_and_type("input[placeholder='이메일 주소']", "beable9489@gmail.com")
            log.append(f"Filled profile fields: name={r_name}, handle={r_handle}, desc={r_desc}, email={r_email}")

            # Check Publish button state and click
            pub_state = await cdp.eval("""(() => {
                const pub = document.querySelector('ytcp-button#publish-button');
                if (!pub) return 'not_found';
                const disabled = pub.hasAttribute('disabled');
                if (!disabled) {
                    pub.click();
                    const ib = pub.querySelector('button');
                    if (ib) ib.click();
                    return 'clicked';
                }
                return 'disabled';
            })()""")
            await asyncio.sleep(5.0)
            log.append(f"Profile Publish state: {pub_state}")
            await cdp.screenshot(str(KIT_DIR / "cdp_clean_profile.png"))

            # Now navigate to /videos/short via sidebar click
            await cdp.eval("""(() => {
                const nav = document.querySelector("a#menu-paper-icon-item-1") ||
                            Array.from(document.querySelectorAll("tp-yt-paper-icon-item")).find(el => (el.innerText || '').includes('콘텐츠'));
                if (nav) nav.click();
            })()""")
            await asyncio.sleep(3.5)
            await cdp.eval("""(() => {
                const tabs = Array.from(document.querySelectorAll("tp-yt-paper-tab"));
                const st = tabs.find(t => (t.innerText || '').includes('Shorts'));
                if (st) st.click();
            })()""")
            await asyncio.sleep(4.0)

            # Select all Shorts
            await cdp.eval("""(() => {
                const cb = document.querySelector('ytcp-checkbox-lit#selection-checkbox');
                if (cb) {
                    cb.click();
                    const d = cb.querySelector('#checkbox');
                    if (d) d.click();
                }
            })()""")
            await asyncio.sleep(1.5)

            # Click '수정' -> '설명'
            await cdp.eval("""(() => {
                const triggers = Array.from(document.querySelectorAll('ytcp-text-dropdown-trigger, ytcp-button'));
                const editBtn = triggers.find(el => (el.innerText || '').trim() === '수정');
                if (editBtn) editBtn.click();
            })()""")
            await asyncio.sleep(1.0)
            await cdp.eval("""(() => {
                const items = Array.from(document.querySelectorAll('tp-yt-paper-item'));
                const descItem = items.find(el => (el.innerText || '').trim() === '설명');
                if (descItem) descItem.click();
            })()""")
            await asyncio.sleep(1.5)

            # Focus the textarea inside ytcp-bulk-edit-description
            focused_bulk = await cdp.eval("""(() => {
                const bulk = document.querySelector('ytcp-bulk-edit-description');
                if (!bulk) return false;
                const ta = bulk.querySelector('textarea') || bulk.querySelector("div#textbox[contenteditable='true']") || bulk.querySelector('input');
                if (ta) {
                    ta.focus();
                    ta.click();
                    return true;
                }
                return false;
            })()""")
            if focused_bulk:
                await cdp.send("Input.insertText", {"text": PREPEND_FUNNEL_TEXT})
                await asyncio.sleep(1.0)
                await cdp.eval("""(() => {
                    const btns = Array.from(document.querySelectorAll('ytcp-button'));
                    const upd = btns.find(b => (b.innerText || '').includes('동영상 업데이트'));
                    if (upd) {
                        upd.click();
                        const ib = upd.querySelector('button');
                        if (ib) ib.click();
                    }
                })()""")
                await asyncio.sleep(1.5)
                await cdp.eval("""(() => {
                    const chk = document.querySelector('tp-yt-paper-dialog ytcp-checkbox-lit#confirm-checkbox') ||
                                document.querySelector('tp-yt-paper-dialog ytcp-checkbox-lit');
                    if (chk) {
                        chk.click();
                        const d = chk.querySelector('#checkbox');
                        if (d) d.click();
                    }
                })()""")
                await asyncio.sleep(1.0)
                await cdp.eval("""(() => {
                    const conf = document.querySelector('tp-yt-paper-dialog ytcp-button#confirm-button');
                    if (conf) {
                        conf.click();
                        const ib = conf.querySelector('button');
                        if (ib) ib.click();
                    }
                })()""")
                await asyncio.sleep(10.0)
                log.append("Bulk updated existing Shorts descriptions with funnel links")
            await cdp.screenshot(str(KIT_DIR / "cdp_clean_shorts_bulk.png"))

    # ---------------------------------------------------------
    # 2. Community Tab: Delete old 5-month-old spammy Coupang posts
    # ---------------------------------------------------------
    if comm_tab:
        urllib.request.urlopen(f"http://127.0.0.1:9224/json/activate/{comm_tab['id']}", timeout=3)
        async with websockets.connect(comm_tab["webSocketDebuggerUrl"], max_size=50_000_000) as ws:
            cdp = CDPPage(ws)
            await cdp.send("Page.enable")
            await cdp.send("Runtime.enable")
            await asyncio.sleep(1.5)

            deleted_cnt = 0
            for _ in range(8):
                opened = await cdp.eval("""(() => {
                    const posts = Array.from(document.querySelectorAll('ytd-backstage-post-thread-renderer'));
                    for (const p of posts) {
                        const txt = p.innerText || '';
                        if (!txt.includes('[공식 오픈 안내]') && (txt.includes('쿠팡') || txt.includes('특가') || txt.includes('영웅시대') || txt.includes('개월 전'))) {
                            const btn = p.querySelector('#action-menu button, ytd-menu-renderer button, yt-icon-button#button button');
                            if (btn) {
                                btn.scrollIntoView({ block: 'center' });
                                btn.click();
                                return true;
                            }
                        }
                    }
                    return false;
                })()""")
                if not opened:
                    break
                await asyncio.sleep(0.8)
                clicked_del = await cdp.eval("""(() => {
                    const items = Array.from(document.querySelectorAll('ytd-menu-navigation-item-renderer, ytd-menu-service-item-renderer, tp-yt-paper-item'));
                    const delItem = items.find(i => (i.innerText || '').includes('삭제'));
                    if (delItem) {
                        delItem.click();
                        const a = delItem.querySelector('a, tp-yt-paper-item');
                        if (a) a.click();
                        return true;
                    }
                    return false;
                })()""")
                if clicked_del:
                    await asyncio.sleep(0.8)
                    await cdp.eval("""(() => {
                        const conf = document.querySelector('yt-confirm-dialog-renderer #confirm-button button') ||
                                     Array.from(document.querySelectorAll('yt-button-renderer button, button')).find(b => (b.innerText || '').trim() === '삭제');
                        if (conf) conf.click();
                    })()""")
                    await asyncio.sleep(2.0)
                    deleted_cnt += 1
            log.append(f"Deleted {deleted_cnt} old community posts")
            await cdp.screenshot(str(KIT_DIR / "cdp_clean_community.png"))

    print("CLEAN_FINISH_LOG:", json.dumps(log, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(run())
