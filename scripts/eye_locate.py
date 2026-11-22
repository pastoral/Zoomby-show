#!/usr/bin/env python3
"""Find the cartoon eyes (white ovals with a dark pupil) in a Zoomby shot image, for eye animation.

Usage: python eye_locate.py IMG [--box x0,y0,x1,y1] [--all]
  --box  search only inside this box (percent of the image), e.g. the main character's head area
  --all  list every eye pair found (cast too), largest first; default prints the largest pair only

Prints JSON: {"pairs": [{"eyes": [{"cx","cy","rx","ry"} x2], "skin": "#rrggbb", "ink": "#rrggbb"}]}
All coordinates are percent of the image width (x, rx) and height (y, ry), so they also fit the
1080x1920 plate made by bg_process.py when the image is already 9:16. Use the processed plate as IMG.
"""
import argparse, json
import numpy as np
from PIL import Image
from scipy import ndimage


def hexc(c):
    return "#%02X%02X%02X" % tuple(int(v) for v in c)


def find(path, box=None):
    im = Image.open(path).convert("RGB")
    W0, H0 = im.size
    s = 1080 / W0
    im = im.resize((1080, round(H0 * s)))
    a = np.asarray(im).astype(np.int16)
    H, W = a.shape[:2]
    white = (a.min(2) > 205) & ((a.max(2) - a.min(2)) < 30)
    if box:
        x0, y0, x1, y1 = box
        m = np.zeros_like(white)
        m[int(y0 / 100 * H):int(y1 / 100 * H), int(x0 / 100 * W):int(x1 / 100 * W)] = True
        white &= m
    lab, n = ndimage.label(white)
    eyes = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        if sl is None:
            continue
        ys, xs = sl
        h, w = ys.stop - ys.start, xs.stop - xs.start
        if w < 8 or h < 9 or w > W * 0.3:
            continue
        comp = lab[sl] == i
        area = comp.sum()
        fill = area / (np.pi / 4 * w * h)
        if not (0.35 < fill < 1.05) or not (0.45 < h / w < 2.4):
            continue
        # pupil: dark pixels inside the eye's bounding ellipse (filled holes)
        yy, xx = np.mgrid[0:h, 0:w]
        filled = ((xx - (w - 1) / 2) / (w / 2)) ** 2 + ((yy - (h - 1) / 2) / (h / 2)) ** 2 <= 1.0  # bbox ellipse (the pupil may touch the rim)
        dark = (a[sl].max(2) < 90) & filled
        if dark.sum() < max(2, 0.02 * filled.sum()):
            continue
        eyes.append(dict(cx=(xs.start + xs.stop) / 2, cy=(ys.start + ys.stop) / 2, rx=w / 2, ry=h / 2, area=filled.sum()))
    pairs = []
    for i in range(len(eyes)):
        for j in range(i + 1, len(eyes)):
            e1, e2 = sorted((eyes[i], eyes[j]), key=lambda e: e["cx"])
            dx, dy = e2["cx"] - e1["cx"], abs(e2["cy"] - e1["cy"])
            r = (e1["rx"] + e2["rx"]) / 2
            if 0.7 < e1["area"] / e2["area"] < 1.43 and dy < r * 0.8 and 1.6 * r < dx < 5.5 * r:
                pairs.append((e1, e2))
    pairs.sort(key=lambda p: -(p[0]["area"] + p[1]["area"]))
    out = []
    used = set()
    for e1, e2 in pairs:
        if id(e1) in used or id(e2) in used:
            continue
        used |= {id(e1), id(e2)}
        # skin: median colour of a ring under/around the eyes (not white, not dark)
        cx, cy, r = (e1["cx"] + e2["cx"]) / 2, (e1["cy"] + e2["cy"]) / 2, (e1["ry"] + e2["ry"]) / 2
        y0, y1 = int(min(H - 1, cy + r * 1.3)), int(min(H, cy + r * 2.2))
        x0, x1 = int(max(0, e1["cx"] - e1["rx"])), int(min(W, e2["cx"] + e2["rx"]))
        patch = a[y0:y1, x0:x1].reshape(-1, 3)
        ok = patch[(patch.min(1) < 200) & (patch.max(1) > 60)]
        skin = np.median(ok, 0) if len(ok) else np.array([150, 100, 70])
        out.append({"eyes": [{"cx": round(e["cx"] / W * 100, 2), "cy": round(e["cy"] / H * 100, 2),
                              "rx": round(e["rx"] / W * 100, 2), "ry": round(e["ry"] / H * 100, 2)} for e in (e1, e2)],
                    "skin": hexc(skin), "ink": "#1E1410"})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("img")
    ap.add_argument("--box")
    ap.add_argument("--all", action="store_true")
    A = ap.parse_args()
    box = [float(v) for v in A.box.split(",")] if A.box else None
    pairs = find(A.img, box)
    print(json.dumps({"pairs": pairs if A.all else pairs[:1]}, indent=1))


if __name__ == "__main__":
    main()
