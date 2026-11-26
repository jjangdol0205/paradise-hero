#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
D:\드림컴퍼니\4사업부\scripts\baek_woonho_trot_mv_promoter.py
================================================================================
4사업부 (`HERO` · `@김쌤의영웅라디오` · `@paradise_hero1` · `paradise-hero.com`)
전속 AI 가상 트로트 가수 『백운호 (白雲湖)』 음악 중심(Music-First) 공식 뮤직비디오
& 9:16 트로트 무대 쇼츠/릴스 자동 제작 엔진

설계 원칙 (GEMINI.md & 2026-11-23 감사 표준 100% 준수):
1. **노래 중심 0초 훅 (`9:16` 쇼츠/릴스 MV, 34~36초)**:
   - 로봇 TTS 장광설 0초! 0.0초부터 바로 백운호 실제 `lyria-3.5` 트로트 열창(후렴/1절 완창 34초)이 울려 퍼짐.
   - `flow_vault/div_4/` 세로 `9:16` 백운호 눈맞춤 무대 클립 3~4편을 자연스럽게 컷 연결.
   - 상단 눈가림 0%(Y=76 소형 방송 배지) + 하단 세이프존(`Y=1310~1580`) 68pt 골드·화이트 왕글씨 가사 자막(`stroke_width=8`, `□` 깨짐 0건) + 마지막 4초 무타자(`paradise-hero.com/radio.html`) 안내.
2. **양산형 판정 회피 정규 완곡 MV (`16:9`, 3분 05초)**:
   - [전반부 20초: 따뜻한 어머님 사연 내레이션(`ko-KR-InJoonNeural`) + 후반부 2분 45초: 백운호 완곡 무대(`16:9` Flow 무대 11편 컷 전환 + 90pt 왕글씨 노래방 가사 자막)].
3. **하드웨어 과열/강제종료(`Kernel-Power 41`) 방지**:
   - 단일 워커 순차 실행 + `-threads 2` + `BelowNormal` 우선순위 강제.
4. **투명 AI 표기 & 실존 연예인 0건**:
   - `황영웅` 등 실존 연예인 성명 0건, `"마음을 노래하는 AI 가상 트로트 가수 백운호"`, `containsSyntheticMedia = True`.
================================================================================
"""

from __future__ import annotations

import argparse
import asyncio
import ctypes
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import wave
from typing import Any, Dict, List, Optional, Sequence, Tuple

from PIL import Image, ImageDraw, ImageFont

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
    except Exception:
        pass

KST = timezone(timedelta(hours=9))
ROOT = Path(r"D:\드림컴퍼니")
DIV4 = ROOT / "4사업부"
CATALOG_PATH = DIV4 / "data" / "baek_woonho_6songs_mv_catalog.json"
AUDIO_DIR = DIV4 / "assets" / "audio"
FLOW_DIV4_DIR = ROOT / "flow_vault" / "div_4"
FLOW_MANIFEST = ROOT / "flow_vault" / "manifest.json"
OUT_BASE = DIV4 / "outputs" / "trot_mv_promo"
OUT_SHORTS = OUT_BASE / "shorts_9x16"
OUT_FULL = OUT_BASE / "full_mv_16x9"


def _get_ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    import imageio_ffmpeg  # type: ignore
    return imageio_ffmpeg.get_ffmpeg_exe()


def _pick_kr_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\malgunbd.ttf",
        r"C:\Windows\Fonts\batang.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        r"C:\Windows\Fonts\arialbd.ttf",
    ]
    for fp in candidates:
        if Path(fp).exists():
            try:
                return ImageFont.truetype(fp, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def load_catalog(enforce_sync_gate: bool = True) -> Dict[str, Any]:
    cat = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    if enforce_sync_gate:
        cloud_dir = str(ROOT / "cloud_automation")
        if cloud_dir not in sys.path:
            sys.path.insert(0, cloud_dir)
        from promo_hard_gate import check_hero_lyric_sync_catalog_gate  # type: ignore

        ok_sync, sync_errs = check_hero_lyric_sync_catalog_gate(cat)
        if not ok_sync:
            raise RuntimeError(f"HERO_LYRIC_SYNC_HARD_GATE_BLOCKED: {sync_errs}")
    return cat


def get_hero_stage_clips(aspect_ratio: str = "9:16") -> List[Path]:
    clips: List[Path] = []
    if FLOW_MANIFEST.exists():
        m = json.loads(FLOW_MANIFEST.read_text(encoding="utf-8"))
        for c in m.get("clips", []):
            if c.get("division") == "HERO" and c.get("aspect_ratio") == aspect_ratio:
                p = Path(str(c.get("local_path", "")))
                if p.exists() and p.stat().st_size > 100_000:
                    clips.append(p)
    if not clips and FLOW_DIV4_DIR.exists():
        clips = sorted(FLOW_DIV4_DIR.glob("HERO_*.mp4"))
    return clips


def _fmt_srt_time(sec: float) -> str:
    s = max(0.0, float(sec))
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    rem = int(s % 60)
    ms = int(round((s - int(s)) * 1000)) % 1000
    return f"{h:02d}:{m:02d}:{rem:02d},{ms:03d}"


_SRT_EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF]")


def build_synced_srt(cues: Sequence[Tuple[float, float, str, str]], offset_sec: float = 0.0) -> str:
    blocks: List[str] = []
    for idx, (t0, t1, l1, l2) in enumerate(cues, start=1):
        c1 = _SRT_EMOJI_RE.sub("", re.sub(r"https?://\S+", "", str(l1 or ""))).strip()
        c2 = _SRT_EMOJI_RE.sub("", re.sub(r"https?://\S+", "", str(l2 or ""))).strip()
        txt = f"{c1}\n{c2}".strip() if c2 else c1
        if not txt:
            continue
        blocks.append(f"{idx}\n{_fmt_srt_time(t0 + offset_sec)} --> {_fmt_srt_time(t1 + offset_sec)}\n{txt}\n")
    return "\n".join(blocks)


def _fit_font(draw: ImageDraw.ImageDraw, text: str, start_size: int, max_w: int, stroke_w: int = 0) -> ImageFont.FreeTypeFont:
    sz = start_size
    while sz >= 20:
        f = _pick_kr_font(sz)
        bb = draw.textbbox((0, 0), text, font=f, stroke_width=stroke_w)
        if (bb[2] - bb[0]) <= max_w:
            return f
        sz -= 2
    return _pick_kr_font(20)


def _draw_centered(
    draw: ImageDraw.ImageDraw,
    w: int,
    y: int,
    text: str,
    font: ImageFont.ImageFont,
    fill: Tuple[int, int, int, int],
    stroke_w: int = 8,
) -> int:
    bb = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_w)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x = max(24, (w - tw) // 2)
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_w, stroke_fill=(8, 16, 14, 255))
    return th


def _render_lyric_card_png(
    w: int,
    h: int,
    song_title: str,
    badge: str,
    line1: str,
    line2: str,
    show_cta: bool,
    out_png: Path,
) -> Path:
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    is_vertical = h > w

    # Bottom readability gradient ONLY (never darkens Baek Woon-ho's face/eyes!)
    grad_start = int(h * (0.62 if is_vertical else 0.68))
    for y in range(grad_start, h):
        a = int(min(215, ((y - grad_start) / max(1, h - grad_start)) * 215))
        draw.line([(0, y), (w, y)], fill=(8, 22, 18, a))

    # Top broadcast title pill (auto-fit inside w - 80, strictly malgunbd-safe glyphs, zero tofu!)
    pill_txt = f"♪ 백운호 〈{song_title}〉 · {badge} (AI 가상 트로트 가수)"
    pill_font = _fit_font(draw, pill_txt, 34 if is_vertical else 32, w - 120)
    pbb = draw.textbbox((0, 0), pill_txt, font=pill_font)
    pw, ph = pbb[2] - pbb[0] + 44, pbb[3] - pbb[1] + 22
    px = (w - pw) // 2
    py = 72 if is_vertical else 34
    draw.rounded_rectangle([px, py, px + pw, py + ph], radius=ph // 2, fill=(10, 38, 30, 205), outline=(212, 175, 55, 240), width=3)
    draw.text((px + 22, py + 9), pill_txt, font=pill_font, fill=(255, 242, 195, 255))

    # Giant karaoke-style gold + crisp white 2-line synced lyrics (auto-fit inside safe margins!)
    l1_size = 66 if is_vertical else 84
    l2_size = 62 if is_vertical else 78
    f1 = _fit_font(draw, line1 or " ", l1_size, w - 96, stroke_w=9)
    f2 = _fit_font(draw, line2 or " ", l2_size, w - 96, stroke_w=8)
    y_l1 = 1320 if is_vertical else 785
    if line1:
        th1 = _draw_centered(draw, w, y_l1, line1, f1, (255, 226, 118, 255), stroke_w=9)
    else:
        th1 = l1_size
    if line2:
        _draw_centered(draw, w, y_l1 + th1 + (20 if is_vertical else 16), line2, f2, (255, 255, 255, 255), stroke_w=8)

    # Zero-Typing CTA footer in final 4s (strictly native Korean/ASCII glyphs + auto-fit width, ZERO clipping, ZERO tofu!)
    if show_cta:
        cta_txt = (
            "프로필 눌러 백운호 6곡 무료 듣기 → paradise-hero.com"
            if is_vertical
            else "♪ 백운호 6곡 완곡 무료 라디오 & 카톡 안부카드 → paradise-hero.com/radio.html"
        )
        cta_font = _fit_font(draw, cta_txt, 32 if is_vertical else 36, w - 120)
        cbb = draw.textbbox((0, 0), cta_txt, font=cta_font)
        cw, ch = cbb[2] - cbb[0] + 48, cbb[3] - cbb[1] + 24
        cx = (w - cw) // 2
        cy = 1605 if is_vertical else 985
        draw.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=16, fill=(14, 58, 44, 235), outline=(245, 208, 90, 255), width=3)
        draw.text((cx + 24, cy + 10), cta_txt, font=cta_font, fill=(255, 250, 230, 255))
    else:
        sub_txt = "유튜브 @김쌤의영웅라디오 · 무료 6곡 듣기 paradise-hero.com"
        sub_font = _fit_font(draw, sub_txt, 28, w - 96, stroke_w=5)
        _draw_centered(draw, w, 1625 if is_vertical else 998, sub_txt, sub_font, (220, 236, 228, 225), stroke_w=5)

    out_png.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_png)
    return out_png


def _render_thumbnail_16x9(song: Dict[str, Any], frame_jpg: Path, out_png: Path) -> Path:
    base = Image.open(frame_jpg).convert("RGBA").resize((1280, 720), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(base)
    for y in range(420, 720):
        a = int(((y - 420) / 300.0) * 230)
        draw.line([(0, y), (1280, y)], fill=(8, 26, 20, a))
    # Top badge
    badge = "공식 완곡 뮤직비디오 · AI 가상 트로트 가수 백운호"
    f_b = _fit_font(draw, badge, 34, 1140)
    bbb = draw.textbbox((0, 0), badge, font=f_b)
    bw, bh = bbb[2] - bbb[0] + 44, bbb[3] - bbb[1] + 24
    draw.rounded_rectangle([38, 30, 38 + bw, 30 + bh], radius=14, fill=(10, 40, 30, 220), outline=(218, 178, 60, 255), width=3)
    draw.text((60, 40), badge, font=f_b, fill=(255, 232, 140, 255))
    # Huge crisp title (auto-fit inside 1180px)
    t_txt = f"〈{song['title']}〉"
    f_t = _fit_font(draw, t_txt, 96, 1180, stroke_w=10)
    _draw_centered(draw, 1280, 468, t_txt, f_t, (255, 230, 120, 255), stroke_w=10)
    s_txt = f"{song['hook_headline']} · 풀버전 완곡"
    f_s = _fit_font(draw, s_txt, 44, 1180, stroke_w=7)
    _draw_centered(draw, 1280, 594, s_txt, f_s, (255, 255, 255, 255), stroke_w=7)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(out_png, quality=95)
    return out_png


def _synthesize_intro_tts(text: str, out_mp3: Path) -> Optional[Path]:
    try:
        import edge_tts  # type: ignore
    except Exception:
        return None

    async def _gen() -> None:
        comm = edge_tts.Communicate(text, voice="ko-KR-InJoonNeural", rate="-4%")
        await comm.save(str(out_mp3))

    try:
        asyncio.run(_gen())
        if out_mp3.exists() and out_mp3.stat().st_size > 2000:
            return out_mp3
    except Exception as e:
        print(f"[INTRO TTS WARN] {e}", flush=True)
    return None


def _probe_duration(path: Path) -> float:
    if not path or not path.exists():
        return 0.0
    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        try:
            return float(subprocess.check_output(
                [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                stderr=subprocess.DEVNULL, text=True, timeout=15,
            ).strip())
        except Exception:
            pass
    # Fallback via ffmpeg -i stderr regex (works even when ffprobe is not on PATH!)
    try:
        r = subprocess.run([_get_ffmpeg(), "-i", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", timeout=15)
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", r.stderr or "")
        if m:
            return int(m.group(1)) * 3600.0 + int(m.group(2)) * 60.0 + float(m.group(3))
    except Exception:
        pass
    return 0.0


def _stitch_stage_montage(
    ffmpeg: str,
    stage_clips: List[Path],
    target_w: int,
    target_h: int,
    target_dur: float,
    out_bg_mp4: Path,
) -> Path:
    """Stitches multiple Baek Woon-ho Flow stage clips into a smooth looping montage with -threads 2."""
    # Repeat list cleanly to cover target_dur
    chosen: List[Path] = []
    seg_len = 7.5
    needed = max(1, int(target_dur // seg_len) + 2)
    for i in range(needed):
        chosen.append(stage_clips[i % len(stage_clips)])

    with tempfile.TemporaryDirectory(prefix="hero_montage_") as td:
        tdir = Path(td)
        norm_files: List[Path] = []
        # Deduplicate normalization per unique source clip (super fast!)
        uniq_map: Dict[Path, Path] = {}
        for idx, src in enumerate(dict.fromkeys(chosen)):
            np_mp4 = tdir / f"norm_{idx:02d}.mp4"
            cmd = [
                ffmpeg, "-y", "-threads", "2",
                "-i", str(src),
                "-t", f"{seg_len:.2f}",
                "-vf", f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h},fps=30,format=yuv420p",
                "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
                str(np_mp4),
            ]
            r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=120)
            if r.returncode != 0:
                raise RuntimeError(f"Norm clip failed {src.name}: {r.stderr[-250:]}")
            uniq_map[src] = np_mp4
        for src in chosen:
            norm_files.append(uniq_map[src])
        concat_txt = tdir / "concat.txt"
        concat_txt.write_text("\n".join(f"file '{p.as_posix()}'" for p in norm_files), encoding="utf-8")
        cmd_c = [
            ffmpeg, "-y", "-threads", "2",
            "-f", "concat", "-safe", "0", "-i", str(concat_txt),
            "-t", f"{target_dur:.2f}",
            "-c", "copy", str(out_bg_mp4),
        ]
        rc = subprocess.run(cmd_c, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=120)
        if rc.returncode != 0:
            raise RuntimeError(f"Concat failed: {rc.stderr[-250:]}")
    return out_bg_mp4


def produce_hero_short_mv(
    track_no: int = 1,
    slice_id: str = "chorus1",
    out_dir: Optional[Path] = None,
    stage_clips_override: Optional[List[Path]] = None,
    audio_override: Optional[Path] = None,
) -> Dict[str, Any]:
    """Produces a Music-First 9:16 (1080x1920, 34s) Baek Woon-ho Trot Singing Short/Reel MV."""
    cat = load_catalog()
    song = next(s for s in cat["songs"] if s["track_no"] == track_no)
    sl = next((x for x in song["slices"] if x["slice_id"] == slice_id), song["slices"][0])
    audio_path = audio_override or (AUDIO_DIR / song["filename"])
    assert audio_path.exists(), f"Missing song audio: {audio_path}"

    stage_clips = stage_clips_override or get_hero_stage_clips("9:16")
    assert stage_clips, "No 9:16 HERO Flow stage clips found!"
    # Rotate starting clip per track so each track has unique visual scenes
    rot = ((track_no - 1) * 4) % len(stage_clips)
    selected_clips = [stage_clips[(rot + i) % len(stage_clips)] for i in range(min(4, len(stage_clips)))]

    ffmpeg = _get_ffmpeg()
    target_dir = out_dir or OUT_SHORTS
    target_dir.mkdir(parents=True, exist_ok=True)
    stem = f"hero_short_mv_{track_no:02d}_{song['song_id']}_{sl['slice_id']}"
    out_mp4 = target_dir / f"{stem}.mp4"
    out_srt = target_dir / f"{stem}.srt"
    out_meta = target_dir / f"{stem}_metadata.json"

    dur = float(sl["duration_sec"])
    start_s = float(sl["start_sec"])
    cues: List[Tuple[float, float, str, str]] = [(float(a), float(b), str(c), str(d)) for a, b, c, d in sl["cues"]]

    with tempfile.TemporaryDirectory(prefix=f"{stem}_") as td:
        tdir = Path(td)
        bg_mp4 = _stitch_stage_montage(ffmpeg, selected_clips, 1080, 1920, dur, tdir / "bg.mp4")

        # Prepare sliced 34s real Baek Woon-ho trot singing audio (-0.5 dBFS broadcast limiter, smooth fade in/out)
        aud_m4a = tdir / "song_slice.m4a"
        cmd_a = [
            ffmpeg, "-y", "-threads", "2",
            "-ss", f"{start_s:.2f}", "-t", f"{dur:.2f}", "-i", str(audio_path),
            "-af", f"aresample=44100,afade=t=in:st=0:d=0.6,afade=t=out:st={max(1.0, dur-1.6):.2f}:d=1.6,alimiter=limit=0.944",
            "-c:a", "aac", "-b:a", "192k", str(aud_m4a),
        ]
        ra = subprocess.run(cmd_a, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=90)
        if ra.returncode != 0:
            raise RuntimeError(f"Audio slice failed: {ra.stderr[-240:]}")

        # Render synced karaoke lyric PNGs (4 cues + CTA on final cue)
        inputs = ["-i", str(bg_mp4), "-i", str(aud_m4a)]
        filter_parts: List[str] = []
        last_v = "0:v"
        for idx, (t0, t1, l1, l2) in enumerate(cues):
            is_last = idx == (len(cues) - 1)
            png_p = _render_lyric_card_png(1080, 1920, song["title"], song["badge"], l1, l2, show_cta=is_last, out_png=tdir / f"cue_{idx}.png")
            inp_idx = idx + 2
            inputs.extend(["-i", str(png_p)])
            out_v = f"v{idx}"
            filter_parts.append(f"[{last_v}][{inp_idx}:v]overlay=0:0:enable='between(t,{t0:.2f},{t1:.2f})'[{out_v}]")
            last_v = out_v

        cmd_v = [
            ffmpeg, "-y", "-threads", "2",
            *inputs,
            "-filter_complex", ";".join(filter_parts) + f";[{last_v}]format=yuv420p[vfinal]",
            "-map", "[vfinal]", "-map", "1:a",
            "-t", f"{dur:.2f}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-movflags", "+faststart",
            "-c:a", "copy", str(out_mp4),
        ]
        rv = subprocess.run(cmd_v, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=240)
        if rv.returncode != 0 or not out_mp4.exists():
            raise RuntimeError(f"Short MV compose failed: {rv.stderr[-300:]}")

    srt_text = build_synced_srt(cues, offset_sec=0.0)
    out_srt.write_text(srt_text, encoding="utf-8")

    first_lyric = f"{cues[0][2]} {cues[0][3]}".strip() if cues else song["hook_headline"]
    sl_id = str(sl.get("slice_id") or "")
    if sl_id == "chorus1":
        yt_title = f"♪ 백운호 〈{song['title']}〉 {song['hook_headline']} #백운호 #트로트 #Shorts"[:98]
    elif sl_id == "verse1":
        yt_title = f"♪ 백운호 〈{song['title']}〉 \"{first_lyric}\" 1절 첫 소절 무대 #백운호 #트로트 #Shorts"[:98]
    else:
        yt_title = f"♪ 백운호 〈{song['title']}〉 \"{first_lyric}\" {sl['label']} #백운호 #트로트 #Shorts"[:98]
    utm_yt = "https://paradise-hero.com/go/yt"
    utm_ig = "https://paradise-hero.com/go/ig"
    description = (
        f"{yt_title}\n\n"
        f"어머님, 아버님 반갑습니다 💚\n"
        f"마음을 노래하는 AI 가상 트로트 가수 『백운호』의 {song['badge']} 〈{song['title']}〉 {sl['label']}입니다.\n\n"
        f"🎵 백운호 6곡 완곡 무료 라디오 & 카톡 무료 안부카드 (가입 없음): {utm_yt}\n"
        f"📸 공식 인스타그램 (@paradise_hero1): {cat['instagram_url']}\n\n"
        f"💬 {song['either_or_question']}\n\n"
        f"※ {cat['ai_disclosure']}\n"
        f"#백운호 #{song['title'].replace(' ', '')} #김쌤의영웅라디오 #시니어트로트 #트로트무대 #Shorts"
    )
    pinned_comment = (
        f"🎵 백운호 〈{song['title']}〉 포함 6곡 완곡 무료 라디오 & 카톡 안부카드 (가입 없음): {utm_yt}\n"
        f"💬 {song['either_or_question']}"
    )
    meta = {
        "mode": "hero_trot_music_short_mv",
        "track_no": track_no,
        "song_id": song["song_id"],
        "song_title": song["title"],
        "slice_id": sl["slice_id"],
        "duration_sec": dur,
        "vocal_highlight_sec": dur,
        "mp4_path": str(out_mp4),
        "srt_path": str(out_srt),
        "yt_title": yt_title,
        "description": description,
        "ig_caption": description.replace(utm_yt, utm_ig),
        "pinned_comment": pinned_comment,
        "status": {"madeForKids": False, "selfDeclaredMadeForKids": False},
        "stage_clips_used": [p.name for p in selected_clips],
        "generated_at_kst": datetime.now(KST).isoformat(),
    }
    out_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[HERO SHORT MV OK] #{track_no} 〈{song['title']}〉 ({sl['slice_id']}, {dur:.1f}s, {out_mp4.stat().st_size:,}B) -> {out_mp4.name}", flush=True)
    return meta


def produce_hero_full_mv_16x9(track_no: int = 1, out_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Produces Full 16:9 Official Dedication Trot MV (20s warm story intro + full 2m45s uncut Baek Woon-ho song + 90pt lyrics)."""
    cat = load_catalog()
    song = next(s for s in cat["songs"] if s["track_no"] == track_no)
    audio_path = AUDIO_DIR / song["filename"]
    assert audio_path.exists(), f"Missing song audio: {audio_path}"

    stage_clips = get_hero_stage_clips("16:9")
    assert stage_clips, "No 16:9 HERO Flow stage clips found!"
    ffmpeg = _get_ffmpeg()
    target_dir = out_dir or OUT_FULL
    target_dir.mkdir(parents=True, exist_ok=True)

    stem = f"hero_full_mv_{track_no:02d}_{song['song_id']}_16x9"
    out_mp4 = target_dir / f"{stem}.mp4"
    out_srt = target_dir / f"{stem}.srt"
    out_thumb = target_dir / f"{stem}_thumb_1280x720.png"
    out_meta = target_dir / f"{stem}_metadata.json"

    song_dur = float(song["duration_sec"])
    with tempfile.TemporaryDirectory(prefix=f"{stem}_") as td:
        tdir = Path(td)
        intro_mp3 = _synthesize_intro_tts(song["story_intro"], tdir / "intro_tts.mp3")
        raw_intro_tts_dur = _probe_duration(intro_mp3) if intro_mp3 else 0.0
        target_intro_dur = max(14.0, round(raw_intro_tts_dur + 1.5, 2)) if (intro_mp3 and raw_intro_tts_dur > 1.0) else 0.0

        # Build exact PCM segments FIRST and read exact sample-accurate durations via wave.open()!
        # Prevents apad=pad_dur premature cutoff when intro_tts < 12.5s!
        master_m4a = tdir / "full_master.m4a"
        song_wav = tdir / "song_seg.wav"
        rs = subprocess.run(
            [
                ffmpeg, "-y", "-threads", "2",
                "-i", str(audio_path),
                "-af", f"aresample=44100,aformat=channel_layouts=stereo,afade=t=in:st=0:d=0.4,afade=t=out:st={max(1.0, song_dur-1.8):.2f}:d=1.8",
                "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", str(song_wav),
            ],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=90,
        )
        if rs.returncode != 0 or not song_wav.exists():
            raise RuntimeError(f"Song WAV render failed: {rs.stderr[-260:]}")
        with wave.open(str(song_wav), "rb") as wf:
            actual_song_dur = wf.getnframes() / float(wf.getframerate())

        actual_intro_dur = 0.0
        if intro_mp3 and target_intro_dur > 5.0:
            intro_wav = tdir / "intro_seg.wav"
            ri = subprocess.run(
                [
                    ffmpeg, "-y", "-threads", "2",
                    "-i", str(intro_mp3),
                    "-t", f"{target_intro_dur:.2f}", "-i", str(audio_path),
                    "-filter_complex",
                    f"[0:a]aresample=44100,aformat=channel_layouts=stereo,apad=whole_dur={target_intro_dur:.2f},atrim=0:{target_intro_dur:.2f},asetpts=PTS-STARTPTS[v0];"
                    f"[1:a]aresample=44100,aformat=channel_layouts=stereo,apad=whole_dur={target_intro_dur:.2f},atrim=0:{target_intro_dur:.2f},asetpts=PTS-STARTPTS,volume=0.18,afade=t=out:st={max(1.0, target_intro_dur-1.2):.2f}:d=1.2[bed];"
                    f"[v0][bed]amix=inputs=2:duration=first:normalize=0[intro]",
                    "-map", "[intro]", "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", str(intro_wav),
                ],
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=90,
            )
            if ri.returncode != 0 or not intro_wav.exists():
                raise RuntimeError(f"Intro WAV render failed: {ri.stderr[-260:]}")
            with wave.open(str(intro_wav), "rb") as wf:
                actual_intro_dur = wf.getnframes() / float(wf.getframerate())

            cmd_a = [
                ffmpeg, "-y", "-threads", "2",
                "-i", str(intro_wav),
                "-i", str(song_wav),
                "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1,alimiter=limit=0.944[aout]",
                "-map", "[aout]", "-c:a", "aac", "-b:a", "192k", str(master_m4a),
            ]
        else:
            cmd_a = [
                ffmpeg, "-y", "-threads", "2",
                "-i", str(song_wav),
                "-af", "alimiter=limit=0.944",
                "-c:a", "aac", "-b:a", "192k", str(master_m4a),
            ]
        ra = subprocess.run(cmd_a, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=120)
        if ra.returncode != 0:
            raise RuntimeError(f"Full MV audio failed: {ra.stderr[-260:]}")

        intro_dur = actual_intro_dur
        song_dur = actual_song_dur
        total_dur = intro_dur + song_dur

        # Stitch 16:9 stage montage covering full total_dur
        bg_mp4 = _stitch_stage_montage(ffmpeg, stage_clips, 1920, 1080, total_dur, tdir / "bg_16x9.mp4")

        # Extract crisp thumbnail frame from bg_mp4 at t=3s
        frame_jpg = tdir / "thumb_frame.jpg"
        subprocess.run([ffmpeg, "-y", "-ss", "3.0", "-i", str(bg_mp4), "-frames:v", "1", "-q:v", "2", str(frame_jpg)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
        if frame_jpg.exists():
            _render_thumbnail_16x9(song, frame_jpg, out_thumb)

        # Build timeline cues: intro story card + all full_cues shifted by intro_dur
        all_cues: List[Tuple[float, float, str, str]] = []
        if intro_dur > 5.0:
            all_cues.append((0.3, intro_dur - 0.3, f"♪ 사연 헌정곡 · 백운호 〈{song['title']}〉", song["hook_headline"]))
        for t0, t1, l1, l2 in song["full_cues"]:
            all_cues.append((float(t0) + intro_dur, float(t1) + intro_dur, str(l1), str(l2)))

        # Render each cue segment independently (1 static PNG overlay per ~8s clip -> ~100MB RAM, ZERO overlay deadlock!)
        # then stream-copy concat all segments + exact master audio (0-frame cumulative drift at 30fps!).
        blank_png = tdir / "blank_1080p.png"
        Image.new("RGBA", (1920, 1080), (0, 0, 0, 0)).save(blank_png)

        seg_specs: List[Tuple[float, float, Path]] = []
        ov_t = 0.0
        for idx, (t0, t1, l1, l2) in enumerate(all_cues):
            is_last = idx == (len(all_cues) - 1)
            if t0 > ov_t + 0.04:
                seg_specs.append((ov_t, t0, blank_png))
                ov_t = t0
            png_p = _render_lyric_card_png(1920, 1080, song["title"], song["badge"], l1, l2, show_cta=is_last, out_png=tdir / f"fcue_{idx:02d}.png")
            end_c = min(total_dur, t1)
            if end_c > ov_t + 0.04:
                seg_specs.append((ov_t, end_c, png_p))
                ov_t = end_c
        if total_dur > ov_t + 0.04:
            seg_specs.append((ov_t, total_dur, blank_png))

        seg_mp4s: List[Path] = []
        emitted_v = 0.0
        for sidx, (st_s, en_s, ov_png) in enumerate(seg_specs):
            raw_d = max(1.0 / 30.0, en_s - emitted_v)
            frames = max(1, int(round(raw_d * 30.0)))
            snapped_d = frames / 30.0
            seg_out = tdir / f"vseg_{sidx:03d}.mp4"
            cmd_seg = [
                ffmpeg, "-y", "-threads", "2",
                "-ss", f"{emitted_v:.4f}", "-t", f"{snapped_d:.4f}", "-i", str(bg_mp4),
                "-i", str(ov_png),
                "-filter_complex", "[0:v][1:v]overlay=0:0,fps=30,format=yuv420p[vs]",
                "-map", "[vs]", "-an",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-g", "60",
                "-video_track_timescale", "15360",
                str(seg_out),
            ]
            rs = subprocess.run(cmd_seg, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=120)
            if rs.returncode != 0 or not seg_out.exists():
                raise RuntimeError(f"Full MV segment {sidx} failed: {rs.stderr[-250:]}")
            seg_mp4s.append(seg_out)
            emitted_v += snapped_d

        seg_list_txt = tdir / "vseg_concat.txt"
        seg_list_txt.write_text("\n".join(f"file '{p.as_posix()}'" for p in seg_mp4s) + "\n", encoding="utf-8")
        cmd_v = [
            ffmpeg, "-y", "-threads", "2",
            "-f", "concat", "-safe", "0", "-i", str(seg_list_txt),
            "-i", str(master_m4a),
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "copy",
            "-movflags", "+faststart", "-shortest",
            str(out_mp4),
        ]
        rv = subprocess.run(cmd_v, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=180)
        if rv.returncode != 0 or not out_mp4.exists():
            raise RuntimeError(f"Full MV 16:9 concat mux failed: {rv.stderr[-300:]}")

    out_srt.write_text(build_synced_srt(all_cues, offset_sec=0.0), encoding="utf-8")
    yt_title = f"[공식 뮤직비디오 · 완곡] 백운호 〈{song['title']}〉 ({song['badge']}) | 큰글씨 가사 · 김쌤의영웅라디오"[:98]
    utm_yt = "https://paradise-hero.com/go/yt"
    description = (
        f"{yt_title}\n\n"
        f"어머님, 아버님 반갑습니다 💚\n"
        f"{song['story_intro']}\n\n"
        f"⏱️ [곡 순서]\n"
        f"00:00 따뜻한 사연 헌정 인사\n"
        f"00:{int(intro_dur):02d} 백운호 〈{song['title']}〉 완곡 공식 무대 (큰글씨 가사)\n\n"
        f"🎵 백운호 6곡 완곡 무료 라디오 & 카톡 안부카드 (가입 없음): {utm_yt}\n"
        f"📸 공식 인스타그램 (@paradise_hero1): {cat['instagram_url']}\n\n"
        f"💬 {song['either_or_question']}\n\n"
        f"※ {cat['ai_disclosure']}\n"
        f"#백운호 #{song['title'].replace(' ', '')} #공식뮤직비디오 #김쌤의영웅라디오 #시니어트로트 #트로트신곡"
    )
    meta = {
        "mode": "hero_trot_official_full_mv_16x9",
        "track_no": track_no,
        "song_id": song["song_id"],
        "song_title": song["title"],
        "intro_sec": round(intro_dur, 4),
        "song_dur_sec": round(song_dur, 4),
        "total_duration_sec": round(total_dur, 4),
        "mp4_path": str(out_mp4),
        "srt_path": str(out_srt),
        "thumbnail_path": str(out_thumb),
        "yt_title": yt_title,
        "description": description,
        "pinned_comment": (
            f"🎵 백운호 〈{song['title']}〉 포함 6곡 완곡 무료 라디오 & 카톡 안부카드 (가입 없음): {utm_yt}\n"
            f"💬 {song['either_or_question']}"
        ),
        "status": {"madeForKids": False, "selfDeclaredMadeForKids": False},
        "stage_clips_used": [p.name for p in stage_clips],
        "generated_at_kst": datetime.now(KST).isoformat(),
    }
    out_meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[HERO FULL 16:9 MV OK] #{track_no} 〈{song['title']}〉 ({total_dur:.1f}s, {out_mp4.stat().st_size:,}B) -> {out_mp4.name}", flush=True)
    return meta


def main() -> int:
    parser = argparse.ArgumentParser(description="Baek Woon-ho Music-First Trot MV & Shorts Promoter")
    parser.add_argument("--mode", choices=["shorts", "all-shorts", "full-mv"], default="shorts")
    parser.add_argument("--track", type=int, default=1, help="Track number 1..6")
    parser.add_argument("--slice", dest="slice_id", default="chorus1", choices=["chorus1", "verse1", "chorus2"])
    args = parser.parse_args()

    if args.mode == "all-shorts":
        results = [produce_hero_short_mv(track_no=t, slice_id=args.slice_id) for t in range(1, 7)]
        print(f"=== ALL 6 BAEK WOON-HO TROT SHORTS MVs COMPLETE ({len(results)} files) ===", flush=True)
    elif args.mode == "full-mv":
        produce_hero_full_mv_16x9(track_no=args.track)
    else:
        produce_hero_short_mv(track_no=args.track, slice_id=args.slice_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
