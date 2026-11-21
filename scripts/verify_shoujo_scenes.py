r"""
Verification script for Milestone 2: 8 Shoujo Anime Scene Keyframes
Checks:
- All 8 scene files exist in d:\드림컴퍼니\4사업부\assets\shoujo_scenes\
- Exact dimensions: 1080x1920
- Color mode: 3-channel RGB
- File size > 1MB
- Non-trivial variance (authentic illustration with rich color distribution)
- Zero corruption or incomplete data
"""
import os
import sys
import numpy as np
from PIL import Image

TARGET_DIR = r"d:\드림컴퍼니\4사업부\assets\shoujo_scenes"
EXPECTED_FILES = [f"scene_{i:02d}.png" for i in range(1, 9)]

def verify_all_scenes():
    print(f"=== Verifying 8 Shoujo Anime Keyframes in {TARGET_DIR} ===")
    assert os.path.isdir(TARGET_DIR), f"Target directory does not exist: {TARGET_DIR}"

    results = []
    all_passed = True

    for fname in EXPECTED_FILES:
        fpath = os.path.join(TARGET_DIR, fname)
        if not os.path.exists(fpath):
            print(f"[FAIL] Missing file: {fname}")
            all_passed = False
            continue

        fsize = os.path.getsize(fpath)
        if fsize < 1_000_000:
            print(f"[FAIL] {fname} size suspiciously small: {fsize} bytes")
            all_passed = False
            continue

        try:
            with Image.open(fpath) as img:
                width, height = img.size
                mode = img.mode
                
                # Check dimensions
                dim_ok = (width == 1080 and height == 1920)
                # Check mode
                mode_ok = (mode == "RGB")
                
                # Check variance & channels
                arr = np.array(img)
                channels_ok = (arr.ndim == 3 and arr.shape[2] == 3)
                std_r = np.std(arr[:, :, 0])
                std_g = np.std(arr[:, :, 1])
                std_b = np.std(arr[:, :, 2])
                variance_ok = (std_r > 20 and std_g > 20 and std_b > 20)
                
                status = dim_ok and mode_ok and channels_ok and variance_ok
                if not status:
                    all_passed = False

                results.append({
                    "file": fname,
                    "dim": f"{width}x{height}",
                    "mode": mode,
                    "size_mb": round(fsize / (1024 * 1024), 2),
                    "std_rgb": (round(std_r, 1), round(std_g, 1), round(std_b, 1)),
                    "passed": status
                })
        except Exception as e:
            print(f"[FAIL] Exception loading {fname}: {e}")
            all_passed = False

    for r in results:
        status_tag = "[PASS]" if r["passed"] else "[FAIL]"
        print(f"{status_tag} {r['file']}: {r['dim']} | Mode: {r['mode']} | Size: {r['size_mb']} MB | RGB std: {r['std_rgb']}")

    if all_passed and len(results) == 8:
        print("\n>>> ALL 8 SHOUJO ANIME SCENES VERIFIED SUCCESSFULLY! <<<")
        return 0
    else:
        print("\n>>> VERIFICATION FAILED! <<<")
        return 1

if __name__ == "__main__":
    sys.exit(verify_all_scenes())
