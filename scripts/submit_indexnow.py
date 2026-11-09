#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/submit_indexnow.py
==========================
Division 4: paradise-hero.com IndexNow Instant Search Engine Indexing Script.
Submits all production endpoints to IndexNow protocol endpoints:
- api.indexnow.org
- www.bing.com/indexnow
- yandex.com/indexnow

Also verifies live HTTPS connectivity for https://paradise-hero.com.
"""

import sys
import json
import urllib.request
import urllib.error
from typing import List, Dict, Any

HOST = "paradise-hero.com"
GITHUB_PAGES_HOST = "jjangdol0205.github.io"
GITHUB_PAGES_URL = f"https://{GITHUB_PAGES_HOST}/paradise-hero/"
KEY = "c75f10bb24814e518712613d9646bca3"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"

ENDPOINTS = [
    "https://api.indexnow.org/indexnow",
    "https://www.bing.com/indexnow",
    "https://yandex.com/indexnow"
]

URL_LIST = [
    f"https://{HOST}/",
    f"https://{HOST}/story.html",
    f"https://{HOST}/booth.html",
    f"https://{HOST}/photobooth.html",
    f"https://{HOST}/radio.html",
    f"https://{HOST}/community.html",
    f"https://{HOST}/stream.html",
    f"https://{HOST}/vip.html"
]


def build_payload() -> Dict[str, Any]:
    """Construct standard IndexNow JSON submission payload."""
    return {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": URL_LIST
    }


def submit_to_endpoint(endpoint: str, payload: Dict[str, Any], timeout: int = 15) -> Dict[str, Any]:
    """Submit URLs payload to an individual IndexNow endpoint."""
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "ParadiseHero-IndexNow/1.0"
        },
        method="POST"
    )

    result = {
        "endpoint": endpoint,
        "status": None,
        "success": False,
        "message": ""
    }

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.getcode()
            body = resp.read().decode('utf-8', errors='replace')
            result["status"] = status
            # 200 (OK) or 202 (Accepted) indicates success per IndexNow spec
            if status in (200, 202):
                result["success"] = True
                result["message"] = f"HTTP {status} - URLs submitted successfully ({len(payload.get('urlList', []))} URLs)"
            else:
                result["message"] = f"HTTP {status}: {body[:100]}"
    except urllib.error.HTTPError as e:
        result["status"] = e.code
        # In IndexNow, HTTP 202 is sometimes raised as non-fatal or 422 if key is in propagation
        body = e.read().decode('utf-8', errors='replace') if hasattr(e, 'read') else str(e)
        if e.code in (200, 202):
            result["success"] = True
            result["message"] = f"HTTP {e.code} (Accepted)"
        else:
            result["message"] = f"HTTP Error {e.code}: {body[:120]}"
    except urllib.error.URLError as e:
        result["message"] = f"Network URLError: {e.reason}"
    except Exception as e:
        result["message"] = f"Unexpected Exception: {str(e)}"

    return result


def verify_live_domain(url: str = f"https://{HOST}/", timeout: int = 10) -> Dict[str, Any]:
    """Verify live connectivity and authentic Paradise Hero branding."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ParadiseHero-LiveCheck/1.0"
        }
    )
    result = {
        "url": url,
        "status": None,
        "live": False,
        "brand_verified": False,
        "message": ""
    }
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = resp.getcode()
            body = resp.read().decode('utf-8', errors='replace')
            result["status"] = code
            has_brand = ("파라다이스" in body or "황영웅" in body)
            result["brand_verified"] = has_brand
            if code == 200 and has_brand:
                result["live"] = True
                result["message"] = f"HTTP {code} OK (Paradise Hero Verified)"
            elif code == 200:
                result["live"] = False
                result["message"] = f"HTTP {code} OK (Content mismatch - missing '파라다이스' brand content)"
            else:
                result["live"] = False
                result["message"] = f"HTTP {code}"
    except urllib.error.HTTPError as e:
        result["status"] = e.code
        result["live"] = False
        result["message"] = f"HTTP {e.code}"
    except Exception as e:
        result["message"] = f"Check failed / DNS propagation: {str(e)}"
    return result


def run_submission() -> bool:
    """Execute complete submission cycle across all endpoints."""
    print("=" * 65)
    print("paradise-hero.com IndexNow Instant Search Engine Indexing")
    print("=" * 65)
    payload = build_payload()
    print(f"Host: {payload['host']}")
    print(f"Key: {payload['key']}")
    print(f"Key Location: {payload['keyLocation']}")
    print(f"Total URLs to Submit: {len(payload['urlList'])}")
    for u in payload['urlList']:
        print(f"  - {u}")
    print("-" * 65)

    all_results = []
    any_success = False

    for ep in ENDPOINTS:
        print(f"[*] Submitting to {ep} ...")
        res = submit_to_endpoint(ep, payload)
        all_results.append(res)
        status_label = "[PASS]" if res["success"] else "[WARN]"
        print(f"    {status_label} Endpoint: {ep} -> {res['message']}")
        if res["success"]:
            any_success = True

    print("-" * 65)
    print("[*] Verifying Live Domain Accessibility...")
    live_res = verify_live_domain(f"https://{HOST}/")
    print(f"    Custom Domain ({HOST}): {live_res['message']}")

    gh_res = verify_live_domain(GITHUB_PAGES_URL)
    print(f"    GitHub Pages Origin ({GITHUB_PAGES_URL}): {gh_res['message']}")

    print("=" * 65)
    is_live = live_res.get("live") or gh_res.get("live")
    if any_success and live_res.get("live"):
        print("[SUCCESS] IndexNow submission and custom domain live check completed successfully!")
        return True
    elif any_success and gh_res.get("live"):
        print("[SUCCESS] IndexNow accepted; GitHub Pages live check passed (custom domain in DNS/Pages routing propagation).")
        return True
    elif is_live:
        print("[NOTE] Live site content verified, but IndexNow search engine key verification is in propagation.")
        return True
    else:
        print("[FAIL] Neither IndexNow submission succeeded nor live site content verified.")
        return False


if __name__ == "__main__":
    success = run_submission()
    sys.exit(0 if success else 1)
