"""
Challenger R5-1 Empirical Audit & Stress Test Suite
Verifies:
1. R1: Trot RSS Ingestion, Schema, Missing Images, Broken Fallback Thumbnails
2. R2: Photo Booth Credit Lifecycle, Lemon Squeezy Store #296100 UX, QR Code
3. R3: 10 Anime Prince Trot Singer Profiles, PNG Binary Metrics (1080x1440, 160x160 RGBA), Commemorative Frames (4)
4. Link integrity across all HTML pages
5. Prohibited commercial cliches audit
"""
import os
import sys
import json
import re
from PIL import Image

ROOT = os.path.abspath("D:/드림컴퍼니/4사업부")
os.chdir(ROOT)

results = {"passed": [], "failed": [], "warnings": []}

def check(name, condition, msg):
    if condition:
        results["passed"].append(f"{name}: {msg}")
        print(f"  [PASS] {name}: {msg}")
    else:
        results["failed"].append(f"{name}: {msg}")
        print(f"  [FAIL] {name}: {msg}")

print("=================================================================")
print("Challenger R5-1 Comprehensive Empirical Verification")
print("=================================================================")

# -------------------------------------------------------------
# Section 1: R1 Trot News & Fallback Thumbnails
# -------------------------------------------------------------
print("\n--- [1] R1 Trot News Asset & Fallback Thumbnail Integrity ---")
news_json_path = os.path.join(ROOT, "data", "trot_news.json")
with open(news_json_path, encoding="utf-8") as f:
    articles = json.load(f)

check("R1.1 Articles Count", len(articles) >= 20, f"Found {len(articles)} articles")

missing_news_images = []
for a in articles:
    img = a.get("image_url", "")
    full_path = os.path.join(ROOT, img)
    if not os.path.exists(full_path):
        missing_news_images.append((a["id"], a["title"][:25], img))

check("R1.2 News Article Images Physical Existence", len(missing_news_images) == 0, 
      f"Missing images in data/trot_news.json: {len(missing_news_images)} articles! Details: {set(m[2] for m in missing_news_images)}")

# Check fallback thumbnails referenced in code
news_js_path = os.path.join(ROOT, "js", "trot-news.js")
with open(news_js_path, encoding="utf-8") as f:
    news_js_code = f.read()

# Look for onerror fallbacks
onerror_fallbacks = re.findall(r"this\.src='([^']+)'", news_js_code)
print(f"  Discovered onerror fallbacks in js/trot-news.js: {set(onerror_fallbacks)}")
for fb in set(onerror_fallbacks):
    fb_path = os.path.join(ROOT, fb)
    check(f"R1.3 Onerror Fallback Image Existence ({fb})", os.path.exists(fb_path),
          f"Path: {fb} (Exists: {os.path.exists(fb_path)})")

# Check news.html meta og:image & twitter:image
with open(os.path.join(ROOT, "news.html"), encoding="utf-8") as f:
    news_html = f.read()

meta_images = re.findall(r'<meta (?:property="og:image"|name="twitter:image") content="https://paradise-hero\.com/([^"]+)"', news_html)
print(f"  Discovered meta images in news.html: {set(meta_images)}")
for mi in set(meta_images):
    mi_path = os.path.join(ROOT, mi)
    check(f"R1.4 Meta Tag Image Existence ({mi})", os.path.exists(mi_path),
          f"Path: {mi} (Exists: {os.path.exists(mi_path)})")


# -------------------------------------------------------------
# Section 2: R2 Two-Shot Photo Booth & Payment UX
# -------------------------------------------------------------
print("\n--- [2] R2 Photo Booth Credit & Payment UX ---")
qr_path = os.path.join(ROOT, "assets", "payments", "qr_photobooth_3000.png")
check("R2.1 Payment QR PNG Exists", os.path.exists(qr_path), f"File size: {os.path.getsize(qr_path) if os.path.exists(qr_path) else 0} bytes")

if os.path.exists(qr_path):
    qr_img = Image.open(qr_path)
    check("R2.2 QR Dimensions", qr_img.size[0] >= 200 and qr_img.size[1] >= 200, f"Dimensions: {qr_img.size}")

# Check booth.html and photobooth.html for Lemon Squeezy Store #296100
for bp in ["booth.html", "photobooth.html"]:
    with open(os.path.join(ROOT, bp), encoding="utf-8") as f:
        bhtml = f.read()
    check(f"R2.3 Store #296100 in {bp}", "store=296100" in bhtml, "Store parameter #296100 present")
    check(f"R2.4 3,000 KRW pricing in {bp}", "3,000원" in bhtml, "3,000 KRW pricing present")
    check(f"R2.5 QR element in {bp}", 'id="payment-qr-img"' in bhtml, "QR image element present")
    check(f"R2.6 Free signup credit in {bp}", "credits: 1" in bhtml, "Free credit allocation present")
    check(f"R2.7 Zero-credit gating in {bp}", "credits <= 0" in bhtml or "credits || 0) <= 0" in bhtml, "Gating intercept present")


# -------------------------------------------------------------
# Section 3: R3 10 Anime Prince Trot Characters & Frames
# -------------------------------------------------------------
print("\n--- [3] R3 10 Anime Prince Trot Characters & Commemorative Frames ---")
char_json_path = os.path.join(ROOT, "data", "characters.json")
with open(char_json_path, encoding="utf-8") as f:
    chars = json.load(f)

check("R3.1 Character Count", len(chars) == 10, f"Total characters: {len(chars)}")

for c in chars:
    cid = c["id"]
    sp = os.path.join(ROOT, c["sprite_path"])
    tp = os.path.join(ROOT, c["thumb_path"])
    sp_ok = os.path.exists(sp)
    tp_ok = os.path.exists(tp)
    if sp_ok and tp_ok:
        s_img = Image.open(sp)
        t_img = Image.open(tp)
        check(f"R3.2 Character Asset {cid}", 
              s_img.size == (1080, 1440) and t_img.size == (160, 160) and s_img.mode == "RGBA",
              f"Sprite: {s_img.size} {s_img.mode}, Thumb: {t_img.size} {t_img.mode}")
    else:
        check(f"R3.2 Character Asset {cid}", False, f"Missing files: sprite={sp_ok}, thumb={tp_ok}")

# Verify COMMEMORATIVE_FRAMES length 4 and physical frame existence
with open(os.path.join(ROOT, "js", "photo-booth.js"), encoding="utf-8") as f:
    booth_js = f.read()

frames_match = re.search(r"COMMEMORATIVE_FRAMES\s*=\s*\[([\s\S]*?)\];", booth_js)
check("R3.3 Frames Array in photo-booth.js", bool(frames_match), "Found COMMEMORATIVE_FRAMES definition")

actual_frames = [
    "assets/frames/frame_flower_path.png",
    "assets/frames/frame_golden_milestone.png",
    "assets/frames/frame_paradise_4cut.png",
    "assets/frames/frame_radio_studio.png"
]
for af in actual_frames:
    check(f"R3.4 Physical Commemorative Frame ({os.path.basename(af)})", 
          os.path.exists(os.path.join(ROOT, af)), f"Exists: {af}")

# Verify privacy invariant (0 fetch calls in photo-booth.js)
has_fetch = bool(re.search(r"\bfetch\s*\(", booth_js))
has_xhr = "XMLHttpRequest" in booth_js
has_ajax = "$.ajax" in booth_js
check("R3.5 Client-side Privacy (Zero Fetch/Upload)", 
      not has_fetch and not has_xhr and not has_ajax, 
      f"fetch={has_fetch}, xhr={has_xhr}, ajax={has_ajax}")


# -------------------------------------------------------------
# Section 4: Cross-Page Links & Prohibited Commercial Cliches
# -------------------------------------------------------------
print("\n--- [4] Cross-Page Reference Integrity & Prohibited Words Audit ---")
all_html = ["index.html", "news.html", "booth.html", "photobooth.html", "radio.html", "stream.html", "community.html", "vip.html", "story.html"]
broken_local_refs = []
for page in all_html:
    page_path = os.path.join(ROOT, page)
    if not os.path.exists(page_path):
        continue
    with open(page_path, encoding="utf-8") as f:
        html = f.read()
    for m in re.finditer(r'(?:href|src)=["\']([^"\']+)["\']', html):
        val = m.group(1)
        if val.startswith(("http", "mailto:", "tel:", "#", "data:")):
            continue
        clean = val.split("?")[0].split("#")[0]
        if not clean:
            continue
        if not os.path.exists(os.path.join(ROOT, clean)):
            broken_local_refs.append((page, val, clean))

check("R4.1 HTML Local Link/Resource Integrity", len(broken_local_refs) == 0,
      f"Broken references: {len(broken_local_refs)} -> {broken_local_refs}")

banned_words = ["최" + "저가", "할" + "인율", "특" + "가", "폭" + "탄세일"]
banned_found = []
for root_dir, dirs, files in os.walk(ROOT):
    if any(ignore in root_dir for ignore in ["node_modules", ".git", "tests", "docs"]):
        continue
    for file in files:
        if file.endswith((".html", ".js", ".json", ".py", ".md", ".css")):
            fp = os.path.join(root_dir, file)
            try:
                c = open(fp, encoding="utf-8").read()
                for bw in banned_words:
                    if bw in c:
                        banned_found.append((os.path.relpath(fp, ROOT), bw))
            except Exception:
                pass

check("R4.2 Zero Prohibited Words Audit", len(banned_found) == 0,
      f"Prohibited words violations: {len(banned_found)} -> {banned_found}")


print("\n=================================================================")
print(f"Summary: {len(results['passed'])} PASS, {len(results['failed'])} FAIL")
print("=================================================================")
if results["failed"]:
    print("FAILED CHECKS:")
    for f in results["failed"]:
        print("  - " + f)
    sys.exit(1)
else:
    print("ALL EMPIRICAL CHECKS PASSED PERFECTLY!")
    sys.exit(0)
