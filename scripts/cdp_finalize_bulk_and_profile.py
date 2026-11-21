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

PREPEND_FUNNEL_TEXT = (
    "👑 [왕자님과 나의 2샷 사진관 — 회원가입 시 1회 무료 촬영!]\n"
    "👉 https://paradise-hero.com/booth.html\n"
    "💌 [김쌤 라디오 사연 복덕방]: https://paradise-hero.com/story.html\n"
    "📰 [트로트 큰글씨 뉴스룸]: https://paradise-hero.com/news.html\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
)

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
    # 1. Clean old 5-month-old spammy posts on comm_tab
    # ---------------------------------------------------------
    if comm_tab:
        async with websockets.connect(comm_tab["webSocketDebuggerUrl"], max_size=50_000_000) as ws:
            cdp = CDPPage(ws)
            await cdp.send("Page.enable")
            await cdp.send("Runtime.enable")
            await cdp.send("Page.bringToFront")
            await asyncio.sleep(1.5)

            deleted_cnt = 0
            for _ in range(8):
                opened_menu = await cdp.eval("""(() => {
                    const posts = Array.from(document.querySelectorAll('ytd-backstage-post-thread-renderer'));
                    for (const p of posts) {
                        const txt = p.innerText || '';
                        // Keep our new official post, delete old Coupang/특가 posts
                        if (!txt.includes('[공식 오픈 안내]') && (txt.includes('쿠팡') || txt.includes('특가') || txt.includes('영웅시대') || txt.includes('개월 전'))) {
                            const btn = p.querySelector('#action-menu button, ytd-menu-renderer button');
                            if (btn) {
                                btn.scrollIntoView({ block: 'center' });
                                btn.click();
                                return true;
                            }
                        }
                    }
                    return false;
                })()""")
                if not opened_menu:
                    break
                await asyncio.sleep(0.8)
                clicked_del = await cdp.eval("""(() => {
                    const items = Array.from(document.querySelectorAll('ytd-menu-navigation-item-renderer, ytd-menu-service-item-renderer, tp-yt-paper-item'));
                    const delItem = items.find(i => (i.innerText || '').includes('삭제'));
                    if (delItem) {
                        delItem.click();
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
            log.append(f"Deleted {deleted_cnt} old community posts on YouTube channel page")
            await cdp.screenshot(str(KIT_DIR / "cdp_comm_cleaned_final.png"))

    # ---------------------------------------------------------
    # 2. Studio Tab: Complete Bulk Edit on Shorts, then Publish Profile
    # ---------------------------------------------------------
    if studio_tab:
        async with websockets.connect(studio_tab["webSocketDebuggerUrl"], max_size=50_000_000) as ws:
            cdp = CDPPage(ws)
            await cdp.send("Page.enable")
            await cdp.send("DOM.enable")
            await cdp.send("Runtime.enable")
            await cdp.send("Page.bringToFront")
            await asyncio.sleep(1.5)

            # Inspect current input inside ytcp-bulk-edit-description (including shadow DOM)
            focused_box = await cdp.eval("""(() => {
                function findEditable(root) {
                    const els = root.querySelectorAll ? root.querySelectorAll('*') : [];
                    for (const el of els) {
                        if ((el.tagName === 'TEXTAREA' || el.tagName === 'INPUT' || el.getAttribute('contenteditable') === 'true') &&
                            el.id !== 'query-input' && el.getBoundingClientRect().width > 100) {
                            el.focus();
                            el.click();
                            return el.tagName + '#' + (el.id || el.placeholder || 'box');
                        }
                        if (el.shadowRoot) {
                            const res = findEditable(el.shadowRoot);
                            if (res) return res;
                        }
                    }
                    return null;
                }
                const bulkRoot = document.querySelector('ytcp-bulk-edit-description') || document;
                return findEditable(bulkRoot);
            })()""")
            log.append(f"Bulk edit focused element: {focused_box}")

            if focused_box:
                await cdp.send("Input.insertText", {"text": PREPEND_FUNNEL_TEXT})
                await asyncio.sleep(1.2)
                clicked_upd = await cdp.eval("""(() => {
                    const btns = Array.from(document.querySelectorAll('ytcp-button, button'));
                    const upd = btns.find(b => (b.innerText || '').includes('동영상 업데이트') && b.getBoundingClientRect().width > 0);
                    if (upd) {
                        upd.click();
                        const ib = upd.querySelector('button');
                        if (ib) ib.click();
                        return true;
                    }
                    return false;
                })()""")
                log.append(f"Clicked 동영상 업데이트: {clicked_upd}")
                await asyncio.sleep(1.5)

                # Confirm dialog
                await cdp.eval("""(() => {
                    const chk = document.querySelector('tp-yt-paper-dialog ytcp-checkbox-lit#confirm-checkbox') ||
                                document.querySelector('tp-yt-paper-dialog ytcp-checkbox-lit');
                    if (chk) {
                        chk.click();
                        const div = chk.querySelector('#checkbox');
                        if (div) div.click();
                    }
                })()""")
                await asyncio.sleep(1.0)
                confirmed_upd = await cdp.eval("""(() => {
                    const dlg = document.querySelector('tp-yt-paper-dialog');
                    if (!dlg) return false;
                    const btns = Array.from(dlg.querySelectorAll('ytcp-button, button'));
                    const conf = btns.find(b => (b.innerText || '').includes('동영상 업데이트') || b.id === 'confirm-button');
                    if (conf) {
                        conf.click();
                        const ib = conf.querySelector('button');
                        if (ib) ib.click();
                        return true;
                    }
                    return false;
                })()""")
                log.append(f"Confirmed Bulk Update dialog: {confirmed_upd}")
                await asyncio.sleep(12.0)
            await cdp.screenshot(str(KIT_DIR / "cdp_shorts_updated_final.png"))

            # If cancel button is still there, close bulk bar so navigation isn't blocked
            await cdp.eval("""(() => {
                const btns = Array.from(document.querySelectorAll('ytcp-button'));
                const cancel = btns.find(b => (b.innerText || '').trim() === '취소' && b.getBoundingClientRect().width > 0);
                if (cancel) cancel.click();
            })()""")
            await asyncio.sleep(1.0)

            # Now navigate to /editing/profile
            await cdp.eval(f"window.onbeforeunload = null; window.location.href = 'https://studio.youtube.com/channel/{CHANNEL_ID}/editing/profile';")
            await asyncio.sleep(6.0)

            await cdp.eval("""(() => {
                const retry = document.querySelector('ytcp-button#error-retry-button');
                if (retry && retry.getBoundingClientRect().width > 0) retry.click();
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
                log.append("Uploaded Banner (2048x1152) on /editing/profile")

            # Add 3 links
            for _ in range(3):
                cnt = await cdp.eval("document.querySelectorAll(\"input[placeholder='제목 입력']\").length")
                if cnt and cnt >= 3:
                    break
                await cdp.eval("""(() => {
                    const btns = Array.from(document.querySelectorAll('ytcp-button'));
                    const add = btns.find(b => (b.innerText || '').includes('링크 추가'));
                    if (add) add.click();
                })()""")
                await asyncio.sleep(0.8)

            # Fill Description, Email, and 3 Links using native Input.insertText per field
            fields_to_fill = [
                ("input[placeholder='채널 이름 입력']", "김쌤의 영웅라디오"),
                ("input[placeholder='핸들 설정']", "김쌤의영웅라디오"),
                ("div#textbox[contenteditable='true']", DESCRIPTION),
                ("input[placeholder='이메일 주소']", "beable9489@gmail.com"),
            ]
            for sel, val in fields_to_fill:
                ok = await cdp.eval(f"""(() => {{
                    const el = document.querySelector("{sel}");
                    if (el) {{
                        el.scrollIntoView({{ block: 'center' }});
                        el.focus();
                        el.click();
                        if (el.value !== undefined) el.value = '';
                        else el.innerText = '';
                        return true;
                    }}
                    return false;
                }})()""")
                if ok:
                    await cdp.send("Input.insertText", {"text": val})
                    await asyncio.sleep(0.5)

            links_data = [
                ("왕자님 투샷 사진관(1회무료)", "https://paradise-hero.com/booth.html"),
                ("김쌤 라디오 사연 복덕방", "https://paradise-hero.com/story.html"),
                ("파라다이스히어로 트로트뉴스", "https://paradise-hero.com/news.html"),
            ]
            for i, (lt, lu) in enumerate(links_data):
                ok_t = await cdp.eval(f"""(() => {{
                    const el = document.querySelectorAll("input[placeholder='제목 입력']")[{i}];
                    if (el) {{ el.focus(); el.click(); el.value = ''; return true; }}
                    return false;
                }})()""")
                if ok_t:
                    await cdp.send("Input.insertText", {"text": lt})
                    await asyncio.sleep(0.3)
                ok_u = await cdp.eval(f"""(() => {{
                    const el = document.querySelectorAll("input[placeholder='URL 입력']")[{i}];
                    if (el) {{ el.focus(); el.click(); el.value = ''; return true; }}
                    return false;
                }})()""")
                if ok_u:
                    await cdp.send("Input.insertText", {"text": lu})
                    await asyncio.sleep(0.3)

            await asyncio.sleep(1.5)
            pub_ok = await cdp.eval("""(() => {
                const pub = document.querySelector('ytcp-button#publish-button');
                if (pub && !pub.hasAttribute('disabled')) {
                    pub.click();
                    const ib = pub.querySelector('button');
                    if (ib) ib.click();
                    return true;
                }
                return false;
            })()""")
            await asyncio.sleep(5.0)
            log.append(f"Final Profile Publish clicked: {pub_ok}")
            await cdp.screenshot(str(KIT_DIR / "cdp_profile_final_done.png"))

    print("FINALIZE_RESULT:", json.dumps(log, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(run())
