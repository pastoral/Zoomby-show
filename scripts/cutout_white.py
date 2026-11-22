#!/usr/bin/env python3
"""Cut flat cartoon art (heads, hands, props) off a plain white background.

Flood-fills the white that touches the image edge, so white eyes, teeth and highlights inside the
black outline stay opaque (an AI background remover often eats them).

Usage: python cutout_white.py IN.png OUT.png [--crop-like REF.png] [--thresh 225]
  --crop-like  crop to the same box as another cut-out of the same drawing (keeps a head and its
               edited mouth variants pixel-aligned); default crops to the art's own bounding box.
"""
import argparse
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage


def cut(path, thresh=225):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    white = (a.min(2) > thresh) & ((a.max(2) - a.min(2)) < 25)
    lab, _ = ndimage.label(white)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    bg = (ndimage.binary_dilation(bg, iterations=1) & (a.min(2) > 170)) | bg
    alpha = np.where(bg, 0, 255).astype(np.uint8)
    out = im.copy()
    out.putalpha(Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(1.2)))
    return out, Image.fromarray(alpha).getbbox()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--crop-like"); ap.add_argument("--thresh", type=int, default=225)
    A = ap.parse_args()
    img, bb = cut(A.src, A.thresh)
    if A.crop_like:
        _, bb = cut(A.crop_like, A.thresh)
    img.crop(bb).save(A.out)
    print(A.out, img.crop(bb).size)
