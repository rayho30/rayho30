#!/usr/bin/env python3
"""
Cleans up a source photo before ASCII conversion:
  1. (optional) cut the background out with rembg, if it's installed
  2. even out lighting with CLAHE (adaptive histogram equalization)
  3. composite onto a white canvas so background falls at the light end
     of the character ramp instead of printing as mid-gray noise

Usage:
    python tools/clean_photo.py my-photo.jpg
    # writes assets/photo-ready.png
"""
import sys
import os
import cv2
import numpy as np
from PIL import Image

OUT_PATH = "assets/photo-ready.png"


def remove_background(img_bgr):
    """Try rembg if available; otherwise return the image unchanged with a
    warning so the pipeline still works end-to-end."""
    try:
        from rembg import remove
        ok, buf = cv2.imencode(".png", img_bgr)
        result = remove(buf.tobytes())
        arr = np.frombuffer(result, dtype=np.uint8)
        rgba = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
        return rgba
    except ImportError:
        print("[clean_photo] rembg not installed - skipping background removal. "
              "Install with `pip install rembg` for cleaner cutouts.", file=sys.stderr)
        h, w = img_bgr.shape[:2]
        bgra = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2BGRA)
        bgra[:, :, 3] = 255
        return bgra


def apply_clahe(img_bgr):
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l2 = clahe.apply(l)
    lab2 = cv2.merge((l2, a, b))
    return cv2.cvtColor(lab2, cv2.COLOR_LAB2BGR)


def composite_on_white(rgba):
    h, w = rgba.shape[:2]
    if rgba.shape[2] == 4:
        alpha = rgba[:, :, 3:4].astype(np.float32) / 255.0
        rgb = rgba[:, :, :3].astype(np.float32)
        white = np.full_like(rgb, 255.0)
        out = rgb * alpha + white * (1 - alpha)
        return out.astype(np.uint8)
    return rgba[:, :, :3]


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/clean_photo.py <path-to-photo>", file=sys.stderr)
        sys.exit(1)

    src_path = sys.argv[1]
    img_bgr = cv2.imread(src_path)
    if img_bgr is None:
        print(f"[clean_photo] could not read {src_path}", file=sys.stderr)
        sys.exit(1)

    img_bgr = apply_clahe(img_bgr)
    rgba = remove_background(img_bgr)
    composited = composite_on_white(rgba)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    Image.fromarray(cv2.cvtColor(composited, cv2.COLOR_BGR2RGB)).save(OUT_PATH)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
