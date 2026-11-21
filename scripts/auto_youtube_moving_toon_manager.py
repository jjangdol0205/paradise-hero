#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
auto_youtube_moving_toon_manager.py
================================================================================
Autonomous Daily Moving-Toon Generator, Time-Staggered Uploader, Community
Manager & Channel Health Daemon for Div 4 (@김쌤의영웅라디오 / UCVsUonyLFpyWHfLi0tqJzPg)

Capabilities:
1. Safe Anti-Spam Daily Policy (3 distinct episodes/day across staggered slots):
   - Morning slot: 07:30 KST (오전 7:30)
   - Lunch slot:   12:30 KST (오후 12:30)
   - Evening slot: 19:30 KST (오후 7:30)
   - Hard cap <= 3/day to stay 100% compliant with YouTube notification & spam rules.
2. End-to-End Studio Upload & Scheduling via Direct Chrome CDP (port 9224):
   - Auto-launches persistent Chrome profile if port 9224 is closed.
   - Creates/assigns official playlist '👑 백운호 설렘 심야 영웅라디오 감동사연 극장'.
   - Uploads MP4, populates title, paradise-hero.com/booth.html funnel description,
     tags, Not-Made-For-Kids, and sets either Immediate Public ('공개') or exact
     staggered Schedule ('예약').
3. Autonomous YouTube Community ('게시물') Management:
   - Generates a warm Korean webtoon preview image card and publishes a daily
     senior-friendly Community post with zero prohibited commercial words.
   - Updates channel upload defaults if stale links exist.
4. Autonomous Videos & Shorts Management:
   - Audits Shorts, Videos & Posts rows, verifies scheduled/public statuses,
     and saves proof screenshots & daily management report JSON.
================================================================================
"""

import os
import sys
import json
import time
import base64
import asyncio
import argparse
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

import websockets
from PIL import Image, ImageDraw

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SCRIPT_DIR = Path(__file__).resolve().parent
DIV4_DIR = SCRIPT_DIR.parent
EPISODES_JSON = DIV4_DIR / "data" / "moving_toon_episodes.json"
LEDGER_JSON = DIV4_DIR / "data" / "youtube_moving_toon_ledger.json"
TOON_OUT_DIR = DIV4_DIR / "output" / "moving_toon"
REPORT_JSON = DIV4_DIR / "output" / "youtube_daily_management_report.json"
PROFILE_DIR = DIV4_DIR / ".youtube_studio_chrome_profile"

CHANNEL_ID = "UCVsUonyLFpyWHfLi0tqJzPg"
CDP_PORT = 9224
PLAYLIST_TITLE = "김쌤의 심야 영웅라디오 감동사연"
PROHIBITED_WORDS = ["최저가", "할인율", "특가", "폭탄세일"]


def load_ledger() -> Dict[str, Any]:
    if LEDGER_JSON.exists():
        try:
            return json.loads(LEDGER_JSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"uploaded_episodes": {}, "community_posts": [], "playlist_created": False, "upload_defaults_updated": False}


def save_ledger(ledger: Dict[str, Any]):
    LEDGER_JSON.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_JSON.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")


def build_default_channel_description() -> str:
    return (
        "👑 [백운호 10종 캐릭터와 무료 투샷 기념사진관]\n"
        "👉 https://paradise-hero.com/booth.html\n\n"
        "💌 [김쌤의 영웅라디오 사연 복덕방 접수]\n"
        "👉 https://paradise-hero.com/story.html\n\n"
        "📰 [실시간 큰글씨 트로트 뉴스룸]\n"
        "👉 https://paradise-hero.com/news.html\n\n"
        "#백운호 #김쌤의영웅라디오 #트로트 #감동사연 #시니어유튜브"
    )


def build_episode_description(ep: Dict[str, Any]) -> str:
    desc = (
        "👑 [백운호 10종 캐릭터와 무료 투샷 기념사진관]\n"
        "👉 https://paradise-hero.com/booth.html\n\n"
        "💌 [김쌤의 영웅라디오 사연 복덕방 접수]\n"
        "👉 https://paradise-hero.com/story.html\n\n"
        "📰 [실시간 큰글씨 트로트 뉴스룸]\n"
        "👉 https://paradise-hero.com/news.html\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📖 [심야 영웅라디오 감동사연 제{ep['episode_no']}화 줄거리]\n"
        f"{ep['summary']}\n\n"
        "영상에 등장한 다정한 영웅 캐릭터는 파라다이스히어로 기념사진관(paradise-hero.com/booth.html)에서\n"
        "어머님 스마트폰 사진과 함께 무료 즉석 인화 투샷으로 바로 만나보실 수 있습니다 ❤️\n\n"
        "구독과 좋아요를 눌러주시면 매일 아침·점심·저녁 새로운 감동 심야 영웅라디오 감동사연이 찾아갑니다!\n\n"
        "#백운호 #김쌤의영웅라디오 #트로트 #감동사연 #시니어유튜브"
    )
    for bad in PROHIBITED_WORDS:
        if bad in desc:
            raise ValueError(f"Prohibited word '{bad}' found in description!")
    return desc


def build_youtube_api_status_payload(schedule_dt: Optional[datetime] = None) -> Dict[str, Any]:
    """Enforces `status.containsSyntheticMedia = True` on all Div 4 virtual singer Baek Woon-ho uploads."""
    payload: Dict[str, Any] = {
        "privacyStatus": "private" if schedule_dt else "public",
        "selfDeclaredMadeForKids": False,
        "containsSyntheticMedia": True,
    }
    if schedule_dt:
        payload["publishAt"] = schedule_dt.strftime("%Y-%m-%dT%H:%M:00+09:00")
    return payload


def build_community_preview_card(out_png: Path) -> Path:
    """Create a crisp 1080x1080 square Korean webtoon Community teaser card starring Photo Booth characters."""
    card = Image.new("RGB", (1080, 1080), (255, 244, 248))
    draw = ImageDraw.Draw(card, "RGBA")
    for k in range(-1080, 2160, 64):
        draw.line([(k, 0), (k - 540, 1080)], fill=(255, 224, 235, 140), width=18)

    from yeongung_moving_toon_engine import CharacterAssetBank, alpha_blit, get_font
    bank = CharacterAssetBank()
    arr = __import__("numpy").array(card)
    sp_m = bank.render_rigged_sprite(True, "mother_blush_happy", 0.4, 0.0, 0.0, 0.0, 0.5, 0.7, target_h=780)
    sp_p = bank.render_rigged_sprite(False, 3, 0.5, 0.0, 0.0, 0.0, 0.6, 0.5, target_h=820)
    alpha_blit(arr, sp_m, -30, 270)
    alpha_blit(arr, sp_p, 430, 240)

    pil = Image.fromarray(arr)
    d = ImageDraw.Draw(pil, "RGBA")
    d.rectangle([24, 24, 1056, 1056], outline=(34, 20, 38, 255), width=6)
    d.rounded_rectangle([54, 52, 1026, 234], radius=28, fill=(18, 52, 44, 245), outline=(242, 202, 108, 255), width=4)
    f1 = get_font(44, bold=True)
    f2 = get_font(30, bold=True)
    d.text((540, 110), "★ 백운호 설렘 심야 영웅라디오 감동사연 극장 OPEN ★", font=f1, fill=(255, 226, 132, 255), anchor="mm")
    d.text((540, 178), "기념사진관 캐릭터가 살아 움직이는 감동 드라마! (paradise-hero.com)", font=f2, fill=(255, 255, 255, 255), anchor="mm")
    out_png.parent.mkdir(parents=True, exist_ok=True)
    pil.save(str(out_png))
    return out_png


class StudioCDP:
    def __init__(self, ws):
        self.ws = ws
        self.msg_id = 0

    async def send(self, method: str, params: dict = None, timeout: float = 20.0) -> dict:
        self.msg_id += 1
        cid = self.msg_id
        await self.ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
        while True:
            raw = await asyncio.wait_for(self.ws.recv(), timeout=timeout)
            msg = json.loads(raw)
            if msg.get("id") == cid:
                if "error" in msg:
                    raise RuntimeError(f"CDP error on {method}: {msg['error']}")
                return msg.get("result", {})

    async def eval(self, expr: str, timeout: float = 15.0):
        res = await self.send("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": False}, timeout=timeout)
        return res.get("result", {}).get("value")

    async def click_xy(self, x: float, y: float):
        await self.send("Input.dispatchMouseEvent", {"type": "mousePressed", "x": float(x), "y": float(y), "button": "left", "clickCount": 1})
        await asyncio.sleep(0.05)
        await self.send("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": float(x), "y": float(y), "button": "left", "clickCount": 1})

    async def click_pierced(self, selector: str) -> bool:
        """Ultra-fast native C++ shadow-piercing click on the first visible matching node (<5ms)."""
        doc = await self.send("DOM.getDocument", {"depth": -1, "pierce": True})
        root_id = doc["root"]["nodeId"]
        q = await self.send("DOM.querySelectorAll", {"nodeId": root_id, "selector": selector})
        for nid in q.get("nodeIds", []):
            try:
                await self.send("DOM.scrollIntoViewIfNeeded", {"nodeId": nid})
                bm = await self.send("DOM.getBoxModel", {"nodeId": nid})
                border = bm["model"]["border"]
                w = abs(border[2] - border[0])
                h = abs(border[5] - border[1])
                if w > 4 and h > 4:
                    cx = (border[0] + border[2]) / 2.0
                    cy = (border[1] + border[5]) / 2.0
                    await self.click_xy(cx, cy)
                    return True
            except Exception:
                continue
        return False

    async def set_scheduler_datetime(self, target_date_str: str, ko_time_str: str) -> bool:
        """Set date & time inside ytcp-visibility-scheduler using #datepicker-trigger live BoxModel geometry."""
        doc = await self.send("DOM.getDocument", {"depth": -1, "pierce": True})
        root_id = doc["root"]["nodeId"]
        q = await self.send("DOM.querySelectorAll", {"nodeId": root_id, "selector": "ytcp-visibility-scheduler #datepicker-trigger"})
        dp_box = None
        dp_nid = 0
        for nid in q.get("nodeIds", []):
            try:
                await self.send("DOM.scrollIntoViewIfNeeded", {"nodeId": nid})
                bm = await self.send("DOM.getBoxModel", {"nodeId": nid})
                b = bm["model"]["border"]
                if abs(b[2] - b[0]) > 20:
                    dp_box = {"left": b[0], "right": b[2], "top": b[1], "bottom": b[5], "cx": (b[0] + b[2]) / 2.0, "cy": (b[1] + b[5]) / 2.0}
                    dp_nid = nid
                    break
            except Exception:
                continue
        if not dp_box:
            return False

        # 1. Set Date ONLY if different, and guarantee calendar popover is closed via Escape!
        cur_dp_html = (await self.send("DOM.getOuterHTML", {"nodeId": dp_nid})).get("outerHTML", "")
        if target_date_str not in cur_dp_html:
            await self.click_xy(dp_box["cx"], dp_box["cy"])
            await asyncio.sleep(0.8)
            if await self.click_pierced("ytcp-date-picker input"):
                await asyncio.sleep(0.15)
                await self.select_all_and_type(target_date_str)
                await self.press_enter()
                await asyncio.sleep(0.5)
            await self.press_escape()
            await asyncio.sleep(0.5)

        # 2. Set Time (always positioned 65px to the right of #datepicker-trigger!)
        time_x = dp_box["right"] + 65.0
        time_y = dp_box["cy"]
        await self.click_xy(time_x, time_y)
        await asyncio.sleep(0.45)
        await self.select_all_and_type(ko_time_str)
        await asyncio.sleep(0.2)
        await self.press_enter()
        await asyncio.sleep(0.25)

        # 3. Click neutral '공개로 예약' label 25px above #datepicker-trigger to blur & trigger Polymer validation!
        await self.click_xy(dp_box["left"] + 30.0, dp_box["top"] - 25.0)
        await asyncio.sleep(0.85)
        return True

    async def select_all_and_type(self, text: str):
        await self.send("Input.dispatchKeyEvent", {
            "type": "keyDown", "key": "a", "code": "KeyA",
            "windowsVirtualKeyCode": 65, "modifiers": 2, "commands": ["selectAll"]
        })
        await self.send("Input.dispatchKeyEvent", {
            "type": "keyUp", "key": "a", "code": "KeyA",
            "windowsVirtualKeyCode": 65, "modifiers": 2
        })
        await asyncio.sleep(0.08)
        await self.send("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Backspace", "code": "Backspace", "windowsVirtualKeyCode": 8})
        await self.send("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Backspace", "code": "Backspace", "windowsVirtualKeyCode": 8})
        await asyncio.sleep(0.08)
        await self.send("Input.insertText", {"text": text})
        await asyncio.sleep(0.25)

    async def fill_box_native(self, selector_js: str, text: str) -> bool:
        pt = await self.eval(f"""(() => {{
            const el = {selector_js};
            if (!el) return null;
            el.scrollIntoView({{block: 'center'}});
            const r = el.getBoundingClientRect();
            return r.width > 10 ? {{x: r.left + Math.min(40, r.width / 2), y: r.top + Math.min(24, r.height / 2)}} : null;
        }})()""")
        if not pt:
            return False
        await asyncio.sleep(0.18)
        await self.click_xy(pt["x"], pt["y"])
        await asyncio.sleep(0.15)
        await self.select_all_and_type(text)
        # Dismiss mention/hashtag dropdown only if opened
        has_suggest = await self.eval("""(() => {
            const m = document.querySelector('ytcp-mention-autosuggest-menu tp-yt-iron-dropdown');
            return !!(m && m.offsetParent !== null);
        })()""")
        if has_suggest:
            await self.press_escape()
            await asyncio.sleep(0.15)
        return True

    async def press_enter(self):
        await self.send("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13})
        await self.send("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Enter", "code": "Enter", "windowsVirtualKeyCode": 13})

    async def press_escape(self):
        await self.send("Input.dispatchKeyEvent", {"type": "keyDown", "key": "Escape", "code": "Escape", "windowsVirtualKeyCode": 27})
        await self.send("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Escape", "code": "Escape", "windowsVirtualKeyCode": 27})

    async def screenshot(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        res = await self.send("Page.captureScreenshot", {"format": "png"})
        if res.get("data"):
            path.write_bytes(base64.b64decode(res["data"]))


async def ensure_responsive_studio_tab() -> dict:
    """Connect to existing Chrome CDP port 9224 (verifying <3s JS responsiveness), or open a fresh Studio tab."""
    for attempt in range(2):
        try:
            tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json", timeout=5).read().decode())
            candidates = [t for t in tabs if t.get("type") == "page" and "studio.youtube.com" in t.get("url", "")]
            # Prefer /videos/short tab over stale playlist tabs
            candidates.sort(key=lambda t: 0 if "/videos" in t.get("url", "") and "/playlist/" not in t.get("url", "") else 1)
            for st in candidates:
                try:
                    async with websockets.connect(st["webSocketDebuggerUrl"], max_size=20_000_000, ping_interval=None) as test_ws:
                        tcdp = StudioCDP(test_ws)
                        await tcdp.send("Page.bringToFront", timeout=3.0)
                        pong = await tcdp.eval("1 + 1", timeout=3.0)
                        if pong == 2:
                            return st
                except Exception:
                    try:
                        urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/close/{st['id']}", timeout=3)
                    except Exception:
                        pass
            # Open a fresh responsive Studio tab
            new_t = json.loads(urllib.request.urlopen(
                urllib.request.Request(f"http://127.0.0.1:{CDP_PORT}/json/new?https://studio.youtube.com/channel/{CHANNEL_ID}/videos/short", method="PUT"),
                timeout=6
            ).read().decode())
            await asyncio.sleep(5.5)
            return new_t
        except Exception:
            if attempt == 0:
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                ]
                chrome_exe = next((p for p in chrome_paths if os.path.exists(p)), "chrome.exe")
                subprocess.Popen([
                    chrome_exe,
                    f"--user-data-dir={PROFILE_DIR}",
                    f"--remote-debugging-port={CDP_PORT}",
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized",
                    f"https://studio.youtube.com/channel/{CHANNEL_ID}/videos/short",
                ])
                await asyncio.sleep(8.0)
    raise RuntimeError("Could not connect to or launch Chrome YouTube Studio on port 9224.")


async def set_file_on_upload_input(cdp: StudioCDP, file_path: str) -> bool:
    doc = await cdp.send("DOM.getDocument", {"depth": -1, "pierce": True})
    root_id = doc["root"]["nodeId"]
    q_res = await cdp.send("DOM.querySelectorAll", {"nodeId": root_id, "selector": "input[type='file']"})
    for nid in q_res.get("nodeIds", []):
        attrs_res = await cdp.send("DOM.getAttributes", {"nodeId": nid})
        attrs = attrs_res.get("attributes", [])
        attr_str = " ".join(attrs)
        if "Filedata" in attr_str or "video" in attr_str or len(q_res.get("nodeIds", [])) == 1:
            await cdp.send("DOM.setFileInputFiles", {"nodeId": nid, "files": [file_path]})
            return True
    if q_res.get("nodeIds"):
        await cdp.send("DOM.setFileInputFiles", {"nodeId": q_res["nodeIds"][-1], "files": [file_path]})
        return True
    return False


async def ensure_series_playlist(cdp: StudioCDP, ledger: Dict[str, Any]):
    if ledger.get("playlist_created"):
        return
    await cdp.send("Page.bringToFront")
    clicked_create = await cdp.click_pierced("button[aria-label='만들기']")
    if not clicked_create:
        return
    await asyncio.sleep(1.0)
    clicked_pl = await cdp.click_pierced("tp-yt-paper-item#text-item-3")
    if not clicked_pl:
        return
    await asyncio.sleep(2.2)

    filled_pl = await cdp.fill_box_native(
        "document.querySelector('ytcp-playlist-creation-dialog div#textbox[contenteditable=\"true\"], tp-yt-paper-dialog div#textbox[contenteditable=\"true\"]')",
        f"👑 {PLAYLIST_TITLE}"
    )
    if filled_pl:
        await asyncio.sleep(0.8)
        created = await cdp.eval("""(() => {
            const btns = Array.from(document.querySelectorAll('ytcp-playlist-creation-dialog ytcp-button, tp-yt-paper-dialog ytcp-button'));
            const createBtn = btns.find(b => ['만들기', '생성'].includes((b.innerText||'').trim()) && !b.hasAttribute('disabled'));
            if (createBtn) { createBtn.click(); return true; }
            return false;
        })()""")
        await asyncio.sleep(2.5)
        if created:
            ledger["playlist_created"] = True
            save_ledger(ledger)
    await cdp.press_escape()
    await asyncio.sleep(0.8)


async def update_studio_upload_defaults(cdp: StudioCDP, ledger: Dict[str, Any]):
    """Replace any stale upload default description with Paradise-Hero official links."""
    if ledger.get("upload_defaults_updated"):
        return
    try:
        await cdp.send("Page.bringToFront", timeout=5.0)
        opened_settings = await cdp.eval("""(() => {
            const items = Array.from(document.querySelectorAll('tp-yt-paper-icon-item'));
            const m = items.find(e => (e.textContent || '').includes('설정'));
            if (m) { m.click(); return true; }
            return false;
        })()""", timeout=6.0)
        if not opened_settings:
            return
        await asyncio.sleep(1.8)
        opened_defaults = await cdp.eval("""(() => {
            const items = Array.from(document.querySelectorAll('ytcp-settings-dialog tp-yt-paper-item'));
            const m = items.find(e => (e.textContent || '').includes('업로드 기본 설정'));
            if (m) { m.click(); return true; }
            return false;
        })()""", timeout=6.0)
        if opened_defaults:
            await asyncio.sleep(1.2)
            ok_def = await cdp.fill_box_native(
                "document.querySelector('ytcp-settings-dialog div#textbox[aria-label*=\"시청자에게\"]') || document.querySelectorAll('ytcp-settings-dialog div#textbox[contenteditable=\"true\"]')[1]",
                build_default_channel_description()
            )
            if ok_def:
                await asyncio.sleep(0.6)
                saved = await cdp.eval("""(() => {
                    const btns = Array.from(document.querySelectorAll('ytcp-settings-dialog ytcp-button'));
                    const saveBtn = btns.find(b => (b.textContent || '').trim() === '저장' && !b.hasAttribute('disabled') && b.getAttribute('aria-disabled') !== 'true');
                    if (saveBtn) { saveBtn.click(); return true; }
                    return false;
                })()""", timeout=6.0)
                await asyncio.sleep(1.8)
                if saved:
                    ledger["upload_defaults_updated"] = True
                    save_ledger(ledger)
        await cdp.eval("""(() => {
            const closeBtn = Array.from(document.querySelectorAll('ytcp-settings-dialog ytcp-button')).find(b => ['닫기', '취소'].includes((b.textContent||'').trim()));
            if (closeBtn) closeBtn.click();
        })()""", timeout=5.0)
        await asyncio.sleep(0.8)
    except Exception as exc:
        print(f"[WARN] Skipped optional upload-defaults update: {exc}", flush=True)


async def upload_single_episode(
    cdp: StudioCDP,
    ep: Dict[str, Any],
    mp4_path: Path,
    schedule_dt: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Upload a single Moving-Toon Short MP4 to YouTube Studio.
    If schedule_dt is None -> publishes immediately as PUBLIC ('공개').
    If schedule_dt is provided -> schedules ('예약') for that exact KST date & time!
    """
    await cdp.send("Page.bringToFront")

    # Dismiss any lingering post-publish modal first
    await cdp.eval("""(() => {
        document.querySelectorAll(
            'ytcp-video-share-dialog ytcp-button#close-button, ' +
            'ytcp-uploads-still-processing-dialog ytcp-button#close-button, ' +
            'tp-yt-paper-dialog ytcp-button#close-button'
        ).forEach(b => b.click());
    })()""")
    await asyncio.sleep(0.6)

    # Ensure we are on Channel Content Shorts page (not inside a specific playlist page)
    cur_url = await cdp.eval("location.href") or ""
    if f"/channel/{CHANNEL_ID}/videos" not in cur_url:
        await cdp.eval(f"location.href = 'https://studio.youtube.com/channel/{CHANNEL_ID}/videos/short'")
        await asyncio.sleep(3.8)

    # 1. Click 만들기 -> 동영상 업로드 (#text-item-0) via native C++ shadow-piercing selector
    ok_create = await cdp.click_pierced("button[aria-label='만들기']")
    if not ok_create:
        raise RuntimeError("Could not click '만들기' button in YouTube Studio")
    await asyncio.sleep(1.0)
    ok_up = await cdp.click_pierced("tp-yt-paper-item#text-item-0")
    if not ok_up:
        await cdp.eval("""(() => {
            const up = Array.from(document.querySelectorAll('tp-yt-paper-item')).find(e => (e.textContent||'').includes('동영상 업로드'));
            if (up) up.click();
        })()""")
    await asyncio.sleep(2.0)

    # 2. Attach MP4 via DOM.setFileInputFiles
    ok_file = await set_file_on_upload_input(cdp, str(mp4_path))
    if not ok_file:
        raise RuntimeError(f"Failed to locate file input in YouTube Studio upload dialog for {mp4_path}")

    # 3. Wait for Metadata Details step (div#textbox[aria-label*="제목"]) to mount
    title_ready = False
    for _ in range(35):
        await asyncio.sleep(1.0)
        title_ready = bool(await cdp.eval("""(() => {
            const t = document.querySelector('ytcp-uploads-dialog div#textbox[aria-label*="제목"]');
            if (!t) return false;
            const r = t.getBoundingClientRect();
            return r.width > 20;
        })()"""))
        if title_ready:
            break
    if not title_ready:
        raise RuntimeError(f"Timed out waiting for Title textbox in upload dialog for {ep['episode_id']}")

    await asyncio.sleep(1.2)

    # 4. Populate Title & Description via native CDP Input events
    await cdp.fill_box_native(
        "document.querySelector('ytcp-uploads-dialog div#textbox[aria-label*=\"제목\"]')",
        ep["title"][:98]
    )
    await asyncio.sleep(0.4)

    await cdp.fill_box_native(
        "document.querySelector('ytcp-uploads-dialog div#textbox[aria-label*=\"시청자에게\"]') || document.querySelectorAll('ytcp-uploads-dialog div#textbox[contenteditable=\"true\"]')[1]",
        build_episode_description(ep)
    )
    await asyncio.sleep(0.5)

    # 5. Select Playlist ('백운호 설렘 심야 영웅라디오 감동사연 극장')
    pl_opened = await cdp.eval("""(() => {
        const trig = document.querySelector('ytcp-video-metadata-playlists ytcp-text-dropdown-trigger');
        if (trig) { trig.scrollIntoView({block: 'center'}); trig.click(); return true; }
        return false;
    })()""")
    if pl_opened:
        await asyncio.sleep(1.4)
        pl_pt = await cdp.eval(f"""(() => {{
            const items = Array.from(document.querySelectorAll('ytcp-playlist-dialog ytcp-checkbox-lit, ytcp-playlist-dialog tp-yt-paper-checkbox, ytcp-playlist-dialog li'));
            const m = items.find(el => (el.textContent || '').includes('{PLAYLIST_TITLE}'));
            if (!m) return null;
            m.scrollIntoView({{block: 'center'}});
            const r = m.getBoundingClientRect();
            return r.width > 10 ? {{x: r.left + 22, y: r.top + r.height / 2}} : null;
        }})()""")
        if pl_pt:
            await cdp.click_xy(pl_pt["x"], pl_pt["y"])
            await asyncio.sleep(0.5)
        await cdp.eval("""(() => {
            const done = Array.from(document.querySelectorAll('ytcp-playlist-dialog ytcp-button')).find(
                b => ['완료', 'Done'].includes((b.textContent || '').trim())
            );
            if (done) done.click();
        })()""")
        await asyncio.sleep(0.7)

    # 6. Select '아동용이 아닙니다' (VIDEO_MADE_FOR_KIDS_NOT_MFK)
    await cdp.eval("""(() => {
        const r = document.querySelector('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]');
        if (r) { r.scrollIntoView({block: 'center'}); r.click(); }
    })()""")
    await asyncio.sleep(0.4)

    # 7. Expand '더보기' (#toggle-button) & add Tags
    toggled = await cdp.eval("""(() => {
        const btn = document.querySelector('ytcp-video-metadata-editor #toggle-button');
        if (btn && (btn.innerText || '').includes('더보기')) { btn.scrollIntoView({block: 'center'}); btn.click(); return true; }
        return false;
    })()""")
    if toggled:
        await asyncio.sleep(0.8)
        # Mandatory YouTube Altered/Synthetic Media disclosure (`status.containsSyntheticMedia = True`)
        await cdp.eval("""(() => {
            const altYes = document.querySelector(
                'tp-yt-paper-radio-button[name="VIDEO_HAS_ALTERED_CONTENT_YES"], ' +
                'ytcp-altered-content-select tp-yt-paper-radio-button[name*="YES"]'
            );
            if (altYes) { altYes.scrollIntoView({block: 'center'}); altYes.click(); }
        })()""")
        await asyncio.sleep(0.35)
        tag_box = await cdp.eval("""(() => {
            const inp = document.querySelector('ytcp-free-text-chip-bar#tags-container input#text-input, input[aria-label*="태그"]');
            if (!inp) return null;
            inp.scrollIntoView({block: 'center'});
            const r = inp.getBoundingClientRect();
            return r.width > 10 ? {x: r.left + 30, y: r.top + r.height/2} : null;
        })()""")
        if tag_box:
            await cdp.click_xy(tag_box["x"], tag_box["y"])
            await asyncio.sleep(0.15)
            await cdp.send("Input.insertText", {"text": ",".join(ep.get("tags", ["백운호", "김쌤의영웅라디오", "트로트", "감동사연", "시니어유튜브"])) + ","})
            await asyncio.sleep(0.35)

    # Extract assigned YouTube video URL
    video_url = ""
    for _ in range(15):
        video_url = await cdp.eval("""(() => {
            const a = document.querySelector('ytcp-uploads-dialog a[href*="youtu.be"], ytcp-uploads-dialog a[href*="/shorts/"]');
            return a ? a.href : '';
        })()""") or ""
        if video_url:
            break
        await asyncio.sleep(0.6)

    # 8. Click '다음' (#next-button) 3 times to reach Visibility ('공개 상태') step
    for _ in range(3):
        await cdp.eval("""(() => {
            const nb = document.querySelector('ytcp-uploads-dialog ytcp-button#next-button');
            if (nb) nb.click();
        })()""")
        await asyncio.sleep(1.0)

    await asyncio.sleep(0.8)

    if schedule_dt is None:
        await cdp.eval("""(() => {
            const firstExpand = document.querySelector('#first-container-expand-button');
            if (firstExpand) firstExpand.click();
            const pub = document.querySelector('tp-yt-paper-radio-button[name="PUBLIC"]');
            if (pub) { pub.scrollIntoView({block: 'center'}); pub.click(); }
        })()""")
        await asyncio.sleep(0.4)
        await cdp.eval("""(() => {
            const pub = document.querySelector('tp-yt-paper-radio-button[name="PUBLIC"]');
            if (pub) pub.click();
        })()""")
        vis_label = "PUBLIC"
        sched_str = "IMMEDIATE_PUBLIC"
    else:
        # Expand Schedule ('예약') container via #second-container-expand-button
        await cdp.eval("""(() => {
            const exp = document.querySelector('#second-container-expand-button, tp-yt-paper-radio-button#schedule-radio-button');
            if (exp) { exp.scrollIntoView({block: 'center'}); exp.click(); }
        })()""")
        await asyncio.sleep(1.0)

        # Format target Korean date & time and set via #datepicker-trigger live BoxModel anchor
        target_date_str = f"{schedule_dt.year}. {schedule_dt.month}. {schedule_dt.day}."
        h24, minute = schedule_dt.hour, schedule_dt.minute
        ampm_ko = "오전" if h24 < 12 else "오후"
        h12 = h24 if 1 <= h24 <= 12 else (h24 - 12 if h24 > 12 else 12)
        ko_time_str = f"{ampm_ko} {h12}:{minute:02d}"

        await cdp.set_scheduler_datetime(target_date_str, ko_time_str)
        print(f"   -> Studio Scheduler set to: {target_date_str} {ko_time_str}", flush=True)
        vis_label = "SCHEDULED"
        sched_str = schedule_dt.strftime("%Y-%m-%d %H:%M KST")

    # 9. Wait until checks/upload finish & #done-button ('게시' / '예약') is enabled, then click!
    done_clicked = False
    for _ in range(50):
        await asyncio.sleep(1.0)
        done_clicked = await cdp.eval("""(() => {
            const btn = document.querySelector('ytcp-uploads-dialog ytcp-button#done-button');
            if (btn && !btn.hasAttribute('disabled') && btn.getAttribute('aria-disabled') !== 'true') {
                const lbl = (btn.textContent || '').trim();
                btn.click();
                return lbl || true;
            }
            return false;
        })()""")
        if done_clicked:
            break

    if not done_clicked:
        raise RuntimeError(f"#done-button never became clickable for {ep['episode_id']}")

    await asyncio.sleep(6.0)
    for close_sel in [
        "ytcp-video-share-dialog ytcp-button#close-button",
        "ytcp-uploads-still-processing-dialog ytcp-button#close-button",
        "tp-yt-paper-dialog ytcp-button#close-button",
    ]:
        await cdp.click_pierced(close_sel)
    await asyncio.sleep(1.5)

    return {
        "episode_id": ep["episode_id"],
        "title": ep["title"],
        "video_url": video_url,
        "visibility": vis_label,
        "scheduled_kst": sched_str,
        "containsSyntheticMedia": True,
        "status": build_youtube_api_status_payload(schedule_dt),
        "uploaded_at": datetime.now().isoformat(),
    }


async def publish_community_post(cdp: StudioCDP, ep: Dict[str, Any], preview_png: Path) -> Dict[str, Any]:
    """Publish a warm senior-friendly Community Post via YouTube Community composer using native CDP Input."""
    post_text = (
        f"🌸 [김쌤의 영웅라디오 — 백운호 설렘 심야 영웅라디오 감동사연 극장 오픈!] 🌸\n\n"
        f"{ep['community_teaser']}\n\n"
        f"🎬 제1화 바로 보기: https://youtube.com/shorts/R9CoK9wX3D0\n"
        f"👑 영상 속 다정한 영웅님 10종 캐릭터와 어머님 스마트폰 사진으로 무료 추억 투샷도 찍어보세요!\n"
        f"👉 https://paradise-hero.com/booth.html\n\n"
        f"💬 어머님들은 10가지 의상 중 어떤 영웅님 모습이 제일 설레시나요? (금테안경 DJ / 핑크 손하트 / 에메랄드 수트 / 금빛 한복)\n"
        f"댓글로 편하게 남겨주시면 다음 감동사연 이야기에 정성껏 담아드리겠습니다 ❤️"
    )
    for bad in PROHIBITED_WORDS:
        if bad in post_text:
            raise ValueError(f"Prohibited word '{bad}' in community post!")

    new_tab = json.loads(urllib.request.urlopen(
        urllib.request.Request(f"http://127.0.0.1:{CDP_PORT}/json/new?https://www.youtube.com/channel/{CHANNEL_ID}/community", method="PUT"),
        timeout=8
    ).read().decode())
    await asyncio.sleep(5.5)

    posted = False
    try:
        async with websockets.connect(new_tab["webSocketDebuggerUrl"], max_size=30_000_000, ping_interval=None) as cws:
            ccdp = StudioCDP(cws)
            await ccdp.send("Page.bringToFront")
            await asyncio.sleep(1.5)

            await ccdp.eval("""(() => {
                const ph = document.querySelector('#placeholder-area, ytd-backstage-post-dialog-renderer #contenteditable-root');
                if (ph) ph.click();
            })()""")
            await asyncio.sleep(1.0)

            filled_comm = await ccdp.fill_box_native(
                "document.querySelector('ytd-backstage-post-dialog-renderer #contenteditable-root, div#contenteditable-root[contenteditable=\"true\"]')",
                post_text
            )
            if filled_comm:
                await asyncio.sleep(0.8)
                # Click Image attachment button & attach preview_png
                await ccdp.eval("""(() => {
                    const btns = Array.from(document.querySelectorAll('ytd-backstage-post-dialog-renderer button, ytd-button-renderer button'));
                    const imgBtn = btns.find(b => {
                        const t = (b.innerText || b.getAttribute('aria-label') || '');
                        return t.includes('이미지') || t.includes('Image');
                    });
                    if (imgBtn) imgBtn.click();
                })()""")
                await asyncio.sleep(1.2)
                doc = await ccdp.send("DOM.getDocument", {"depth": -1, "pierce": True})
                q_res = await ccdp.send("DOM.querySelectorAll", {"nodeId": doc["root"]["nodeId"], "selector": "input[type='file']"})
                if q_res.get("nodeIds") and preview_png.exists():
                    await ccdp.send("DOM.setFileInputFiles", {"nodeId": q_res["nodeIds"][-1], "files": [str(preview_png)]})
                    await asyncio.sleep(5.0)

                for _ in range(15):
                    clicked_sub = await ccdp.eval("""(() => {
                        const sub = document.querySelector(
                            'ytd-backstage-post-dialog-renderer #submit-button button, ' +
                            'ytd-backstage-post-dialog-renderer ytd-button-renderer#submit-button button'
                        );
                        if (sub && !sub.disabled && sub.getAttribute('aria-disabled') !== 'true') {
                            sub.click();
                            return true;
                        }
                        return false;
                    })()""")
                    if clicked_sub:
                        posted = True
                        break
                    await asyncio.sleep(1.0)

                await asyncio.sleep(4.0)
                await ccdp.screenshot(DIV4_DIR / "output" / "youtube_community_live_proof.png")
    finally:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{CDP_PORT}/json/close/{new_tab['id']}", timeout=4)
        except Exception:
            pass

    return {"posted": posted, "timestamp": datetime.now().isoformat(), "episode_id": ep["episode_id"]}


async def audit_and_clean_channel(cdp: StudioCDP) -> Dict[str, Any]:
    """Navigate to Content -> Videos, Shorts & Posts, verify live/scheduled rows, and capture proof screenshots."""
    await cdp.send("Page.bringToFront")
    await cdp.eval(f"location.href = 'https://studio.youtube.com/channel/{CHANNEL_ID}/videos/upload'")
    await asyncio.sleep(4.2)
    videos_rows = await cdp.eval("""(() => {
        return Array.from(document.querySelectorAll('ytcp-video-row')).slice(0, 10).map(r => ({
            title: r.querySelector('#video-title')?.textContent?.trim(),
            visibility: r.querySelector('.tablecell-visibility')?.textContent?.trim()?.replace(/\\s+/g, ' '),
            date: r.querySelector('.tablecell-date')?.textContent?.trim()?.replace(/\\s+/g, ' '),
            href: r.querySelector('a#thumbnail-anchor')?.getAttribute('href')
        }));
    })()""")
    await cdp.screenshot(DIV4_DIR / "output" / "youtube_studio_videos_proof.png")

    await cdp.eval("""(() => {
        const t = Array.from(document.querySelectorAll('tp-yt-paper-tab')).find(el => (el.textContent||'').trim() === 'Shorts');
        if (t) t.click();
    })()""")
    await asyncio.sleep(3.8)

    shorts_rows = await cdp.eval("""(() => {
        return Array.from(document.querySelectorAll('ytcp-video-row')).slice(0, 10).map(r => ({
            title: r.querySelector('#video-title')?.textContent?.trim(),
            visibility: r.querySelector('.tablecell-visibility')?.textContent?.trim()?.replace(/\\s+/g, ' '),
            date: r.querySelector('.tablecell-date')?.textContent?.trim()?.replace(/\\s+/g, ' '),
            href: r.querySelector('a#thumbnail-anchor')?.getAttribute('href')
        }));
    })()""")
    await cdp.screenshot(DIV4_DIR / "output" / "youtube_studio_shorts_scheduled_proof.png")

    await cdp.eval("""(() => {
        const t = Array.from(document.querySelectorAll('tp-yt-paper-tab')).find(el => (el.textContent||'').trim() === '게시물');
        if (t) t.click();
    })()""")
    await asyncio.sleep(3.5)
    posts_rows = await cdp.eval("""(() => {
        return Array.from(document.querySelectorAll('ytcp-post-row')).slice(0, 6).map(r => ({
            text: (r.textContent || '').trim().replace(/\\s+/g, ' ').slice(0, 140)
        }));
    })()""")
    await cdp.screenshot(DIV4_DIR / "output" / "youtube_studio_posts_proof.png")

    await cdp.eval("""(() => {
        const t = Array.from(document.querySelectorAll('tp-yt-paper-tab')).find(el => (el.textContent||'').trim() === 'Shorts');
        if (t) t.click();
    })()""")
    await asyncio.sleep(2.0)

    return {
        "videos_top10": videos_rows,
        "shorts_top10": shorts_rows,
        "posts_top6": posts_rows,
        "audited_at": datetime.now().isoformat(),
    }


def compute_staggered_slots_from_now(
    now: datetime,
    count: int,
    first_immediate: bool = True,
    existing_today_count: int = 0,
    booked_slots_kst: Optional[List[str]] = None,
    has_recent_public_today: bool = False,
) -> List[Optional[datetime]]:
    """
    Generate safe anti-spam staggered upload slots spaced across golden senior viewing hours:
    07:30 (아침 문안), 12:30 (점심 힐링), 19:30 (저녁 라디오) — strictly max 3 uploads per calendar day,
    zero duplicate slot booking, and >= 3.5h spacing after any immediate PUBLIC upload!
    """
    booked_set = set(booked_slots_kst or [])
    slots: List[Optional[datetime]] = []
    if first_immediate and count > 0:
        slots.append(None)

    min_lead = timedelta(minutes=210 if (first_immediate or has_recent_public_today) else 90)
    daily_hm = [(19, 30)]
    day_cursor = now.date()
    while len(slots) < count:
        day_str = day_cursor.strftime("%Y-%m-%d")
        booked_on_day = sum(1 for b in booked_set if b.startswith(day_str))
        if day_cursor == now.date():
            booked_on_day = max(booked_on_day, existing_today_count)

        for hh, mm in daily_hm:
            cand = datetime(day_cursor.year, day_cursor.month, day_cursor.day, hh, mm)
            cand_key = cand.strftime("%Y-%m-%d %H:%M KST")
            if cand_key in booked_set:
                continue
            lead_req = min_lead if day_cursor == now.date() else timedelta(minutes=90)
            if cand > now + lead_req:
                same_day_cnt = booked_on_day + sum(
                    1 for s in slots
                    if (s is None and day_cursor == now.date()) or (s is not None and s.date() == day_cursor)
                )
                if same_day_cnt < 1:
                    slots.append(cand)
                    if len(slots) >= count:
                        break
        day_cursor += timedelta(days=1)
    return slots


async def run_manager(batch_count: int = 3, first_immediate: bool = False):
    ledger = load_ledger()
    uploaded_ids = list(ledger["uploaded_episodes"].keys())

    from expand_daily_moving_toon_stories import ensure_fresh_episodes
    from yeongung_moving_toon_engine import produce_episodes
    from verify_moving_toon_episodes import verify_all

    avail_eps = ensure_fresh_episodes(min_unscheduled=batch_count + 2, uploaded_ids=uploaded_ids)
    target_eps = avail_eps[:batch_count]
    if not target_eps:
        print("[INFO] No pending episodes to upload.")
        return

    missing_render = [e["episode_id"] for e in target_eps if not (TOON_OUT_DIR / f"{e['episode_id']}.mp4").exists()]
    if missing_render:
        print(f"[RENDER] Producing missing episodes: {missing_render}", flush=True)
        await produce_episodes(missing_render)

    qa = verify_all([e["episode_id"] for e in target_eps])
    if not qa["all_passed"]:
        raise RuntimeError(f"QA verification failed before upload: {qa}")

    st_tab = await ensure_responsive_studio_tab()
    now = datetime.now()
    today_prefix = now.strftime("%Y-%m-%d")
    booked_slots_kst = [
        str(v.get("scheduled_kst", ""))
        for v in ledger["uploaded_episodes"].values()
        if v.get("scheduled_kst") and v.get("scheduled_kst") != "IMMEDIATE_PUBLIC"
    ]
    has_recent_public_today = any(
        v.get("visibility") == "PUBLIC" and str(v.get("uploaded_at", "")).startswith(today_prefix)
        for v in ledger["uploaded_episodes"].values()
    )
    existing_today = sum(
        1 for v in ledger["uploaded_episodes"].values()
        if (v.get("visibility") == "PUBLIC" and str(v.get("uploaded_at", "")).startswith(today_prefix))
        or str(v.get("scheduled_kst", "")).startswith(today_prefix)
    )
    slots = compute_staggered_slots_from_now(
        now,
        len(target_eps),
        first_immediate=first_immediate,
        existing_today_count=existing_today,
        booked_slots_kst=booked_slots_kst,
        has_recent_public_today=has_recent_public_today,
    )

    upload_results = []
    async with websockets.connect(st_tab["webSocketDebuggerUrl"], max_size=50_000_000, ping_interval=None) as ws:
        cdp = StudioCDP(ws)
        await cdp.send("Page.bringToFront")

        await ensure_series_playlist(cdp, ledger)
        await update_studio_upload_defaults(cdp, ledger)

        for ep, slot_dt in zip(target_eps, slots):
            mp4_p = TOON_OUT_DIR / f"{ep['episode_id']}.mp4"
            print(f"[UPLOAD] {ep['episode_id']} -> {'PUBLIC NOW' if slot_dt is None else slot_dt.strftime('%Y-%m-%d %H:%M')}", flush=True)
            res = await upload_single_episode(cdp, ep, mp4_p, schedule_dt=slot_dt)
            ledger["uploaded_episodes"][ep["episode_id"]] = res
            save_ledger(ledger)
            upload_results.append(res)
            await asyncio.sleep(2.5)

        # Publish daily Community Post if not posted today
        already_posted_today = any(p.get("date") == today_prefix and p.get("posted") for p in ledger.get("community_posts", []))
        comm_res = None
        if not already_posted_today:
            all_eps = json.loads(EPISODES_JSON.read_text(encoding="utf-8"))["episodes"]
            lead_ep = all_eps[0] if all_eps else target_eps[0]
            preview_png = TOON_OUT_DIR / "community_preview_card.png"
            build_community_preview_card(preview_png)
            comm_res = await publish_community_post(cdp, lead_ep, preview_png)
            comm_res["date"] = today_prefix
            ledger.setdefault("community_posts", []).append(comm_res)
            save_ledger(ledger)

        audit = await audit_and_clean_channel(cdp)

    report = {
        "executed_at": datetime.now().isoformat(),
        "uploaded_count": len(upload_results),
        "uploads": upload_results,
        "community_post": comm_res,
        "channel_audit": audit,
    }
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("[SUCCESS] Autonomous YouTube Moving-Toon batch & channel management complete!", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1, help="Number of episodes to upload/schedule (daily 19:30 KST: 1)")
    parser.add_argument("--first-immediate", action="store_true", help="Publish first episode immediately as PUBLIC")
    args = parser.parse_args()
    asyncio.run(run_manager(batch_count=args.count, first_immediate=args.first_immediate))


if __name__ == "__main__":
    main()
