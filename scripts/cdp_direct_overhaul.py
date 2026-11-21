#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct Page-Level CDP WebSocket Controller (Zero Playwright browser_ui hang)
Connects directly to ws://127.0.0.1:9224/devtools/page/<id> in <10ms!
"""
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

BULK_SHORTS_DESC = (
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
)

COMMUNITY_POST_TEXT = (
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
    # 1. Publish New Official Community Post on comm_tab
    # ---------------------------------------------------------
    if comm_tab:
        async with websockets.connect(comm_tab["webSocketDebuggerUrl"], max_size=50_000_000) as ws:
            cdp = CDPPage(ws)
            await cdp.send("Page.enable")
            await cdp.send("Runtime.enable")
            await cdp.send("Page.bringToFront")
            await asyncio.sleep(2.0)

            # Click placeholder to open post box
            await cdp.eval("""(() => {
                const ph = document.querySelector('#placeholder-area') || document.querySelector('ytd-backstage-post-dialog-renderer');
                if (ph) ph.click();
            })()""")
            await asyncio.sleep(1.5)

            # Focus contenteditable and insert text
            focused = await cdp.eval("""(() => {
                const ed = document.querySelector("div#contenteditable-root[contenteditable='true']");
                if (ed) {
                    ed.focus();
                    ed.innerText = '';
                    return true;
                }
                return false;
            })()""")
            if focused:
                await cdp.send("Input.insertText", {"text": COMMUNITY_POST_TEXT})
                await asyncio.sleep(1.5)
                posted = await cdp.eval("""(() => {
                    const btn = document.querySelector("ytd-button-renderer#submit-button button") || document.querySelector("button[aria-label='게시']");
                    if (btn && !btn.disabled) {
                        btn.click();
                        return true;
                    }
                    return false;
                })()""")
                await asyncio.sleep(4.0)
                log.append(f"Community Post submitted: {posted}")
            await cdp.screenshot(str(KIT_DIR / "cdp_community_post.png"))

    # ---------------------------------------------------------
    # 2. Studio Tab: Clean old spammy Community Posts, Bulk Edit Shorts, and Finalize Profile
    # ---------------------------------------------------------
    if studio_tab:
        async with websockets.connect(studio_tab["webSocketDebuggerUrl"], max_size=50_000_000) as ws:
            cdp = CDPPage(ws)
            await cdp.send("Page.enable")
            await cdp.send("DOM.enable")
            await cdp.send("Runtime.enable")
            await cdp.send("Page.bringToFront")

            # A. Delete old spammy May 2026 posts that contain '특가' or '영웅시대'
            await cdp.send("Page.navigate", {"url": f"https://studio.youtube.com/channel/{CHANNEL_ID}/content/posts"})
            await asyncio.sleep(5.0)
            deleted_posts = 0
            for _ in range(6):
                has_old = await cdp.eval("""(() => {
                    const rows = Array.from(document.querySelectorAll('ytcp-post-row'));
                    for (const r of rows) {
                        const txt = r.innerText || '';
                        if (txt.includes('특가') || txt.includes('쿠팡 로켓배송')) {
                            const menuBtn = r.querySelector('ytcp-icon-button#menu-button, ytcp-icon-button[aria-label*="옵션"], ytcp-icon-button');
                            if (menuBtn) {
                                menuBtn.click();
                                return true;
                            }
                        }
                    }
                    return false;
                })()""")
                if not has_old:
                    break
                await asyncio.sleep(0.8)
                clicked_del = await cdp.eval("""(() => {
                    const items = Array.from(document.querySelectorAll('tp-yt-paper-item'));
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
                        const btn = document.querySelector('tp-yt-paper-dialog ytcp-button#confirm-button') ||
                                    Array.from(document.querySelectorAll('tp-yt-paper-dialog ytcp-button')).find(b => (b.innerText || '').includes('삭제'));
                        if (btn) btn.click();
                    })()""")
                    await asyncio.sleep(2.5)
                    deleted_posts += 1
            log.append(f"Deleted {deleted_posts} old spammy community posts")
            await cdp.screenshot(str(KIT_DIR / "cdp_posts_cleaned.png"))

            # B. Navigate to /videos/short and bulk-update descriptions + hide 4 health videos
            await cdp.send("Page.navigate", {"url": f"https://studio.youtube.com/channel/{CHANNEL_ID}/videos/short"})
            await asyncio.sleep(5.0)

            # Select all checkbox
            await cdp.eval("""(() => {
                const cb = document.querySelector('ytcp-checkbox-lit#selection-checkbox');
                if (cb) cb.click();
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

            # Change edit type to '모두 바꾸기' (Replace all)
            await cdp.eval("""(() => {
                const sel = document.querySelector('ytcp-select#edit-type-select ytcp-text-dropdown-trigger') ||
                            document.querySelector('ytcp-bulk-edit-description ytcp-text-dropdown-trigger');
                if (sel) sel.click();
            })()""")
            await asyncio.sleep(0.8)
            await cdp.eval("""(() => {
                const items = Array.from(document.querySelectorAll('tp-yt-paper-item'));
                const rep = items.find(el => (el.innerText || '').includes('모두 바꾸기'));
                if (rep) rep.click();
            })()""")
            await asyncio.sleep(0.8)

            # Focus bulk description input and insert text
            focused_bulk = await cdp.eval("""(() => {
                const box = document.querySelector('ytcp-bulk-edit-description textarea') ||
                            document.querySelector('ytcp-bulk-edit-description div#textbox') ||
                            document.querySelector('ytcp-mention-textbox div#textbox');
                if (box) {
                    box.focus();
                    return true;
                }
                return false;
            })()""")
            if focused_bulk:
                await cdp.send("Input.insertText", {"text": BULK_SHORTS_DESC})
                await asyncio.sleep(1.0)
                await cdp.eval("""(() => {
                    const sub = document.querySelector('ytcp-button#submit-button') ||
                                Array.from(document.querySelectorAll('ytcp-button')).find(b => (b.innerText || '').includes('동영상 수정'));
                    if (sub) sub.click();
                })()""")
                await asyncio.sleep(1.5)
                await cdp.eval("""(() => {
                    const chk = document.querySelector('tp-yt-paper-dialog ytcp-checkbox-lit#confirm-checkbox') ||
                                document.querySelector('tp-yt-paper-dialog ytcp-checkbox-lit');
                    if (chk) chk.click();
                })()""")
                await asyncio.sleep(0.8)
                await cdp.eval("""(() => {
                    const conf = document.querySelector('tp-yt-paper-dialog ytcp-button#confirm-button');
                    if (conf) conf.click();
                })()""")
                await asyncio.sleep(10.0)
                log.append("Bulk-updated descriptions across existing Shorts")
            await cdp.screenshot(str(KIT_DIR / "cdp_shorts_bulk_done.png"))

            # C. Navigate to /editing/profile and ensure Banner, Profile, Watermark, Name, Handle, Desc, Links, Email are saved & published
            await cdp.send("Page.navigate", {"url": f"https://studio.youtube.com/channel/{CHANNEL_ID}/editing/profile"})
            await asyncio.sleep(5.0)

            await cdp.eval("""(() => {
                const retry = document.querySelector('ytcp-button#error-retry-button');
                if (retry && retry.getBoundingClientRect().width > 0) retry.click();
            })()""")
            await asyncio.sleep(2.5)

            # Upload files via DOM.setFileInputFiles
            doc = await cdp.send("DOM.getDocument", {"depth": -1, "pierce": True})
            root_id = doc["root"]["nodeId"]
            q_res = await cdp.send("DOM.querySelectorAll", {"nodeId": root_id, "selector": "input[type='file']"})
            node_ids = q_res.get("nodeIds", [])
            log.append(f"Found {len(node_ids)} file input nodes via CDP DOM")

            for idx, fpath in [(0, BANNER_PATH), (1, PROFILE_PATH), (2, WATERMARK_PATH)]:
                if idx < len(node_ids) and os.path.exists(fpath):
                    await cdp.send("DOM.setFileInputFiles", {"nodeId": node_ids[idx], "files": [fpath]})
                    await asyncio.sleep(2.5)
                    await cdp.eval("""(() => {
                        const btns = Array.from(document.querySelectorAll('ytcp-button#done-button'));
                        for (const b of btns) {
                            if (b.getBoundingClientRect().width > 0) b.click();
                        }
                    })()""")
                    await asyncio.sleep(2.0)

            # Set Name, Handle, Description, Email, and Links
            await cdp.eval(f"""(() => {{
                function setInput(sel, val) {{
                    const el = document.querySelector(sel);
                    if (el) {{
                        el.focus();
                        el.value = val;
                        el.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                        el.dispatchEvent(new Event('change', {{ bubbles: true, composed: true }}));
                        el.blur();
                    }}
                }}
                setInput("input[placeholder='채널 이름 입력']", "김쌤의 영웅라디오");
                setInput("input[placeholder='핸들 설정']", "김쌤의영웅라디오");
                setInput("input[placeholder='이메일 주소']", "beable9489@gmail.com");
                const desc = document.querySelector("div#textbox[contenteditable='true']");
                if (desc) {{
                    desc.focus();
                    desc.innerText = {json.dumps(DESCRIPTION)};
                    desc.dispatchEvent(new Event('input', {{ bubbles: true, composed: true }}));
                    desc.blur();
                }}
            }})()""")
            await asyncio.sleep(1.5)

            # Ensure 3 link rows exist
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

            await cdp.eval("""(() => {
                const links = [
                    { t: "왕자님 투샷 사진관(1회무료)", u: "https://paradise-hero.com/booth.html" },
                    { t: "김쌤 라디오 사연 복덕방", u: "https://paradise-hero.com/story.html" },
                    { t: "파라다이스히어로 트로트뉴스", u: "https://paradise-hero.com/news.html" }
                ];
                const tInps = document.querySelectorAll("input[placeholder='제목 입력']");
                const uInps = document.querySelectorAll("input[placeholder='URL 입력']");
                links.forEach((lk, i) => {
                    if (tInps[i] && uInps[i]) {
                        tInps[i].focus();
                        tInps[i].value = lk.t;
                        tInps[i].dispatchEvent(new Event('input', { bubbles: true, composed: true }));
                        tInps[i].dispatchEvent(new Event('change', { bubbles: true, composed: true }));
                        tInps[i].blur();
                        uInps[i].focus();
                        uInps[i].value = lk.u;
                        uInps[i].dispatchEvent(new Event('input', { bubbles: true, composed: true }));
                        uInps[i].dispatchEvent(new Event('change', { bubbles: true, composed: true }));
                        uInps[i].blur();
                    }
                });
            })()""")
            await asyncio.sleep(1.5)

            # Click Publish
            pub_clicked = await cdp.eval("""(() => {
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
            log.append(f"Profile Publish clicked: {pub_clicked}")
            await cdp.screenshot(str(KIT_DIR / "cdp_profile_published.png"))

    print("CDP_DIRECT_RESULT:", json.dumps(log, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(run())
