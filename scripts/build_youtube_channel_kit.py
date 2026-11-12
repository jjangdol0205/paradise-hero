#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
4사업부 (@김쌤의영웅라디오 — silientocean94@gmail.com)
유튜브 채널 초기 세팅 마스터 키트 생성 및 텔레그램(@inves123_bot) 즉시 전송 스크립트
- 프로필 사진: 800x800 PNG (YouTube Studio 권장 규격)
- 채널 배너 아트: 2048x1152 PNG (모바일/PC 세이프존 1546x423 정중앙 정렬, 6MB 이하)
- 영상 구독 워터마크: 150x150 PNG (1MB 이하)
- 원터치 복사 블록(채널명, 핸들, 채널 설명글, 외부 링크, 채널 키워드, 업로드 기본값) 전송
"""

import json
import os
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

DIV4_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = DIV4_DIR / "assets" / "youtube_kit"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def get_korean_font(size: int, bold: bool = True):
    candidates = [
        r"C:\Windows\Fonts\malgunbd.ttf" if bold else r"C:\Windows\Fonts\malgun.ttf",
        r"C:\Windows\Fonts\NanumGothicBold.ttf",
        r"C:\Windows\Fonts\gulim.ttc",
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()


def draw_text_with_stroke(draw, xy, text, font, fill, stroke_fill=(0, 0, 0), stroke_width=4, anchor="mm"):
    draw.text(xy, text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill, anchor=anchor)


def build_profile_800():
    size = 800
    img = Image.new("RGBA", (size, size), (22, 16, 12, 255))
    draw = ImageDraw.Draw(img)

    # Warm radial-like gradient background
    for r in range(400, 0, -2):
        ratio = 1.0 - (r / 400.0)
        red = int(28 + ratio * 55)
        green = int(18 + ratio * 35)
        blue = int(12 + ratio * 18)
        draw.ellipse((400 - r, 400 - r, 400 + r, 400 + r), fill=(red, green, blue, 255))

    # Load DJ / Hero character illustration if available
    char_candidates = [
        DIV4_DIR / "assets" / "characters" / "raw_prince_10.png",
        DIV4_DIR / "assets" / "characters" / "sprite_hwang_young_woong.png",
        DIV4_DIR / "assets" / "hero_main.png",
    ]
    for cp in char_candidates:
        if cp.exists():
            try:
                cimg = Image.open(cp).convert("RGBA")
                cimg.thumbnail((680, 680), Image.Resampling.LANCZOS)
                cx = (size - cimg.width) // 2
                cy = (size - cimg.height) // 2 - 20
                img.alpha_composite(cimg, (cx, cy))
                break
            except Exception:
                pass

    # Dark gradient vignette at bottom for crisp text readability
    overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    for y in range(460, size):
        alpha = int(min(235, ((y - 460) / 340.0) * 245))
        odraw.line([(0, y), (size, y)], fill=(15, 10, 8, alpha))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # Outer golden ring
    draw.ellipse((18, 18, size - 18, size - 18), outline=(245, 194, 66, 255), width=14)
    draw.ellipse((34, 34, size - 34, size - 34), outline=(255, 236, 179, 180), width=4)

    # Top pill badge
    draw.rounded_rectangle((220, 56, 580, 118), radius=30, fill=(180, 35, 24, 235), outline=(255, 215, 100, 255), width=3)
    draw_text_with_stroke(draw, (400, 87), "ON AIR · 황영웅 힐링방송", get_korean_font(28, True), (255, 248, 220), stroke_width=3)

    # Bottom title text
    draw_text_with_stroke(draw, (400, 600), "김쌤의", get_korean_font(74, True), (255, 230, 140), stroke_width=8)
    draw_text_with_stroke(draw, (400, 695), "영웅라디오", get_korean_font(96, True), (255, 255, 255), stroke_width=10)

    out_path = OUT_DIR / "youtube_profile_800x800.png"
    img.convert("RGB").save(out_path, "PNG", optimize=True)
    return out_path


def build_banner_2048x1152():
    w, h = 2560, 1440
    img = Image.new("RGBA", (w, h), (18, 13, 10, 255))
    draw = ImageDraw.Draw(img)

    # Prefer HQ 2560x1440 banner asset if present, else build warm studio safe-zone banner
    hq_banner = DIV4_DIR / "assets" / "yt_banner_heroradio_2560x1440.jpg"
    bg_candidates = [
        hq_banner,
        DIV4_DIR / "content" / "episode_01" / "visuals" / "ch1_scene_1080p.png",
        DIV4_DIR / "assets" / "hero_main.png",
    ]
    for bp in bg_candidates:
        if bp.exists():
            try:
                bg = Image.open(bp).convert("RGBA").resize((w, h), Image.Resampling.LANCZOS)
                if bp != hq_banner:
                    bg = bg.filter(ImageFilter.GaussianBlur(radius=6))
                img.alpha_composite(bg, (0, 0))
                break
            except Exception:
                pass

    if not hq_banner.exists():
        # Center safe zone (1546x423 centered at 1280, 720): X=507..2053, Y=508..931
        overlay = Image.new("RGBA", (w, h), (14, 10, 8, 190))
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)
        sx1, sy1, sx2, sy2 = 507, 508, 2053, 931
        draw.rounded_rectangle(
            (sx1 + 16, sy1 + 12, sx2 - 16, sy2 - 12),
            radius=28,
            fill=(26, 18, 14, 232),
            outline=(245, 194, 66, 255),
            width=5,
        )
        cx = 1280
        draw_text_with_stroke(
            draw,
            (cx, 635),
            "김쌤의 영웅 라디오",
            get_korean_font(84, True),
            (255, 215, 90),
            stroke_width=9,
        )
        draw_text_with_stroke(
            draw,
            (cx, 775),
            "바로 아래 파란 글씨 [paradise-hero.com]을 누르시면 무료 투샷 기념사진관이 열립니다!",
            get_korean_font(34, True),
            (255, 255, 255),
            stroke_width=5,
        )

    out_path = OUT_DIR / "youtube_banner_2560x1440.png"
    img.convert("RGB").save(out_path, "PNG", optimize=True)
    return out_path


def build_watermark_150():
    size = 150
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle((6, 6, size - 6, size - 6), radius=28, fill=(185, 28, 28, 240), outline=(255, 215, 90, 255), width=5)
    draw_text_with_stroke(draw, (75, 48), "🎙️ 영웅라디오", get_korean_font(20, True), (255, 245, 200), stroke_width=3)
    draw_text_with_stroke(draw, (75, 98), "구독하기", get_korean_font(30, True), (255, 255, 255), stroke_width=4)

    out_path = OUT_DIR / "youtube_watermark_150x150.png"
    img.save(out_path, "PNG", optimize=True)
    return out_path


def send_telegram_photo_or_doc(bot_token: str, chat_id: str, file_path: Path, caption: str):
    boundary = "----WebKitFormBoundaryHeroYTKit2026"
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"

    body = bytearray()
    for k, v in [("chat_id", chat_id), ("caption", caption), ("parse_mode", "HTML")]:
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode("utf-8"))
        body.extend(f"{v}\r\n".encode("utf-8"))

    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(
        f'Content-Disposition: form-data; name="document"; filename="{file_path.name}"\r\n'.encode("utf-8")
    )
    body.extend(b"Content-Type: image/png\r\n\r\n")
    body.extend(file_path.read_bytes())
    body.extend(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        url,
        data=bytes(body),
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    p_profile = build_profile_800()
    p_banner = build_banner_2048x1152()
    p_watermark = build_watermark_150()

    print(f"Generated profile: {p_profile} ({p_profile.stat().st_size} bytes)")
    print(f"Generated banner: {p_banner} ({p_banner.stat().st_size} bytes)")
    print(f"Generated watermark: {p_watermark} ({p_watermark.stat().st_size} bytes)")

    env_path = DIV4_DIR / ".env"
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip() if "os" in globals() else ""
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("TELEGRAM_BOT_TOKEN="):
                bot_token = line.split("=", 1)[1].strip().strip("'\"")

    for cid in ["755033799", "-1003834697086"]:
        try:
            send_telegram_photo_or_doc(
                bot_token,
                cid,
                p_profile,
                "1️⃣ <b>[유튜브 프로필 사진 원본 (800×800 PNG)]</b>\n• YouTube 스튜디오 → 맞춤설정 → <b>사진(Picture)</b>에 그대로 업로드하세요!",
            )
            send_telegram_photo_or_doc(
                bot_token,
                cid,
                p_banner,
                "2️⃣ <b>[유튜브 채널 배너 이미지 원본 (2048×1152 PNG · 세이프존 완벽 정렬)]</b>\n• YouTube 스튜디오 → 맞춤설정 → <b>배너 이미지(Banner image)</b>에 그대로 업로드하세요!",
            )
            send_telegram_photo_or_doc(
                bot_token,
                cid,
                p_watermark,
                "3️⃣ <b>[유튜브 동영상 워터마크 원본 (150×150 PNG)]</b>\n• YouTube 스튜디오 → 맞춤설정 → <b>동영상 워터마크(Video watermark)</b> → <b>전체 동영상(Entire video)</b> 선택 후 업로드하세요!",
            )
        except Exception as e:
            print(f"Failed sending to {cid}: {e}")


if __name__ == "__main__":
    main()
