"""
generate_payment_qr.py
김쌤 공식 네이버 크리에이터샵(cshop.naver.com/paradiseshop) & 무료 기념사진관 안내 QR 생성기
paradise-hero.com Division 4
"""

import os
import sys
import qrcode

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT_DIR, "assets", "payments")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "qr_photobooth_3000.png")

CREATOR_SHOP_URL = "https://cshop.naver.com/paradiseshop"


def generate_qr():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4,
    )
    qr.add_data(CREATOR_SHOP_URL)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1B4D3E", back_color="#FFFFFF")
    img.save(OUTPUT_PATH)

    file_size = os.path.getsize(OUTPUT_PATH)
    print(f"[OK] Generated Naver Creator Shop QR code: {OUTPUT_PATH} ({file_size} bytes)")
    print(f"     Target URL: {CREATOR_SHOP_URL}")
    return OUTPUT_PATH


if __name__ == "__main__":
    generated = generate_qr()
    if not os.path.exists(generated):
        sys.exit(1)
    sys.exit(0)
