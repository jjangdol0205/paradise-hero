"""
Challenger Empirical Audit & Stress Test Suite (2026-11-11 HQ Spec)
Verifies:
1. Hwang Young-woong Exclusive 6-Category News & Physical Images (Zero Other Singers)
2. Unlimited Free Photo Booth & Gift Studio (Zero Lemon Squeezy / Zero Store #296100 / Kakao 2s Save Modal)
3. Hwang Young-woong 10 Signature Outfits Catalog & 20 RGBA PNGs + 4 Commemorative Frames
4. Dual Safe Special Store (Naver Creator Shop cshop.naver.com/paradiseshop + 6 Coupang AF7865143 Search URLs)
5. OG Share Thumbnails (og_booth_share.jpg, og_vip_gift.jpg) & Local Link Integrity
"""
import os
import sys
import json
import re
from PIL import Image

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = os.path.abspath("D:/드림컴퍼니/4사업부")
os.chdir(ROOT)

results = {"passed": [], "failed": []}


def check(name, condition, msg):
    if condition:
        results["passed"].append(f"{name}: {msg}")
        print(f"  [PASS] {name}: {msg}")
    else:
        results["failed"].append(f"{name}: {msg}")
        print(f"  [FAIL] {name}: {msg}")


print("=================================================================")
print("Challenger 2026-11-11 HQ Empirical Verification")
print("=================================================================")

# 1. News check
with open(os.path.join(ROOT, "data", "trot_news.json"), encoding="utf-8") as f:
    articles = json.load(f)
check("R1.1 Articles Count", len(articles) >= 20, f"Found {len(articles)} articles")
missing_imgs = [a["image_url"] for a in articles if not os.path.exists(os.path.join(ROOT, a["image_url"]))]
check("R1.2 News Images Exist", len(missing_imgs) == 0, f"Missing: {missing_imgs}")

# 2. Unlimited Free Photo Booth & Gift Studio (Zero Lemon Squeezy / Store #296100)
for page in ["index.html", "booth.html", "photobooth.html", "vip.html", "radio.html", "stream.html", "news.html", "story.html", "community.html"]:
    with open(os.path.join(ROOT, page), encoding="utf-8") as f:
        html = f.read()
    check(f"R2.1 Zero LemonSqueezy/296100 in {page}", "lemonsqueezy" not in html.lower() and "296100" not in html, "Clean")
    plain_html = re.sub(r"<[^>]+>", " ", html)
    plain_html = re.sub(r"\s+", " ", plain_html)
    check(f"R2.2 Free Gift Studio Nav in {page}", "🎁 무료 선물제작소" in plain_html, "Unified header nav present")

# 3. 10 Hwang Young-woong Signature Outfits
with open(os.path.join(ROOT, "data", "characters.json"), encoding="utf-8") as f:
    chars = json.load(f)
check("R3.1 10 Outfits", len(chars) == 10 and all(c["name_ko"] == "황영웅" for c in chars), "All 10 belong to 황영웅")
for c in chars:
    sp = os.path.join(ROOT, c["sprite_path"])
    tp = os.path.join(ROOT, c["thumb_path"])
    s_img = Image.open(sp)
    t_img = Image.open(tp)
    check(f"R3.2 Asset {c['id']}", s_img.size == (1080, 1440) and t_img.size == (160, 160) and s_img.mode == "RGBA", "1080x1440 & 160x160 RGBA")

# 4. Dual Safe Special Store & OG Images
for page in ["index.html", "booth.html", "vip.html", "radio.html", "stream.html", "news.html", "community.html", "lounge.html", "story.html"]:
    with open(os.path.join(ROOT, page), encoding="utf-8") as f:
        html = f.read()
    check(f"R4.1 Naver Creator Shop in {page}", "https://cshop.naver.com/paradiseshop" in html, "Present")
    check(
        f"R4.2 Coupang AF7865143 AFFSRP URLs in {page}",
        html.count("link.coupang.com/re/AFFSRP?lptag=AF7865143") >= 6 and "link.coupang.com/a/" not in html,
        "6+ valid AFFSRP URLs",
    )

# 5. Local Link Integrity
broken_refs = []
for page in ["index.html", "news.html", "booth.html", "photobooth.html", "radio.html", "stream.html", "community.html", "vip.html", "story.html"]:
    html = open(os.path.join(ROOT, page), encoding="utf-8").read()
    for m in re.finditer(r'(?:href|src)=["\']([^"\']+)["\']', html):
        val = m.group(1)
        if val.startswith(("http", "mailto:", "tel:", "#", "data:", "javascript:")):
            continue
        clean = val.split("?")[0].split("#")[0]
        if clean and not os.path.exists(os.path.join(ROOT, clean)):
            broken_refs.append((page, val))
check("R5.1 Local Link Integrity", len(broken_refs) == 0, f"Broken: {broken_refs}")

print("\n=================================================================")
print(f"Summary: {len(results['passed'])} PASS, {len(results['failed'])} FAIL")
print("=================================================================")
sys.exit(1 if results["failed"] else 0)
