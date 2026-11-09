"""
generate_payment_qr.py
Lemon Squeezy Store #296100 Checkout QR Code Generator
paradise-hero.com Division 4

Generates scannable high-contrast QR code for senior users:
- Item: 3,000 KRW (~$2.20 USD) Photo Booth Recharge Pass
- Lemon Squeezy Checkout URL:
  https://kidsfitglobal.lemonsqueezy.com/buy/bad98d00-7175-41f6-9d58-eeb2471d0da4?store=296100
- Output: assets/payments/qr_photobooth_3000.png
"""

import os
import sys
import qrcode

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(ROOT_DIR, "assets", "payments")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "qr_photobooth_3000.png")

PAYMENT_CHECKOUT_URL = (
    "https://kidsfitglobal.lemonsqueezy.com/buy/bad98d00-7175-41f6-9d58-eeb2471d0da4?store=296100"
)


def generate_qr():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    qr = qrcode.QRCode(
        version=None,  # Automatic sizing
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction for senior camera scanning
        box_size=12,
        border=4,
    )
    qr.add_data(PAYMENT_CHECKOUT_URL)
    qr.make(fit=True)

    # High-contrast deep brand emerald on pure white background
    img = qr.make_image(fill_color="#1B4D3E", back_color="#FFFFFF")
    img.save(OUTPUT_PATH)

    file_size = os.path.getsize(OUTPUT_PATH)
    print(f"[OK] Generated payment QR code: {OUTPUT_PATH} ({file_size} bytes)")
    print(f"     Target URL: {PAYMENT_CHECKOUT_URL}")
    return OUTPUT_PATH


if __name__ == "__main__":
    generated = generate_qr()
    if not os.path.exists(generated):
        sys.exit(1)
    sys.exit(0)
