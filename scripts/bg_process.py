#!/usr/bin/env python3
"""Zoomby background pipeline: reframe/upscale -> (cleanup) -> grade -> manifest.

Usage:
  python bg_process.py IN.png OUT_DIR [--name scene03] [--fit crop|extend] [--focus 0.5,0.4]
                       [--mask MASK.png] [--blur 2] [--no-grade] [--w 1080 --h 1920]

  --fit crop    (default) scale to cover 9:16 and crop around --focus (x,y in 0..1)
  --fit extend  keep the whole image; fill the missing area with a blurred, darkened
                stretch of the image itself (use when cropping would cut the gag)
  --mask        white = area to remove (text, watermark, extra person); filled by inpainting
                (OpenCV if installed, else a blur-based fill)
Writes <OUT_DIR>/<name>.jpg and appends to <OUT_DIR>/manifest.json.
Target look (references/style.md): mean luma 32-46 %, saturation ~0.45, warm, light overall soften.
No depth layers: the camera move plus the character layer give separation.
"""
import argparse, json, os, sys, time
import numpy as np
from PIL import Image, ImageFilter, ImageOps

LUMA_RANGE = (0.32, 0.46)
SAT_TARGET = 0.45


def stats(im):
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255
    luma = (a * [0.2126, 0.7152, 0.0722]).sum(2)
    mx, mn = a.max(2), a.min(2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    return {"mean_luma": round(float(luma.mean()), 3), "contrast": round(float(luma.std()), 3), "saturation": round(float(sat.mean()), 3)}


def reframe(im, W, H, fit, focus):
    im = ImageOps.exif_transpose(im).convert("RGB")
    sw, sh = im.size
    if fit == "extend":
        # whole image fits inside; background = same image cover-scaled, blurred, darkened
        s = min(W / sw, H / sh)
        fg = im.resize((max(1, round(sw * s)), max(1, round(sh * s))), Image.LANCZOS)
        cs = max(W / sw, H / sh)
        bg = im.resize((round(sw * cs), round(sh * cs)), Image.LANCZOS)
        l, t = (bg.width - W) // 2, (bg.height - H) // 2
        bg = bg.crop((l, t, l + W, t + H)).filter(ImageFilter.GaussianBlur(40))
        bg = Image.eval(bg, lambda v: int(v * 0.7))
        bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
        return bg
    s = max(W / sw, H / sh)
    nw, nh = round(sw * s), round(sh * s)
    big = im.resize((nw, nh), Image.LANCZOS)
    fx, fy = focus
    l = int(min(max(fx * nw - W / 2, 0), nw - W))
    t = int(min(max(fy * nh - H / 2, 0), nh - H))
    out = big.crop((l, t, l + W, t + H))
    if s > 1.2:  # restore some crispness after a big upscale
        out = out.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    return out


def grade(im, warmth=1.06):
    a = np.asarray(im).astype(np.float32) / 255
    W3 = np.array([0.2126, 0.7152, 0.0722], np.float32)
    # 1) look: warm cinematic tint + gentle S-curve + vignette
    a[..., 0] *= warmth
    a[..., 2] /= warmth
    a = np.clip(a, 0, 1)
    a = a + 0.08 * (a - 0.5) * (1 - np.abs(2 * a - 1))
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    a *= (1 - 0.18 * np.clip(r - 0.55, 0, 1))[..., None]
    a = np.clip(a, 0, 1)
    # 2) saturation toward the target (measured on the current image)
    for _ in range(3):
        gray = (a * W3).sum(2, keepdims=True)
        mx, mn = a.max(2), a.min(2)
        sat = float(np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0).mean())
        k = float(np.clip(SAT_TARGET / max(sat, 1e-3), 0.85, 1.5))
        if abs(k - 1) < 0.02:
            break
        a = np.clip(gray + (a - gray) * k, 0, 1)
    # 3) brightness last, so the band holds: iterate gamma until the mean luma is inside it
    for _ in range(6):
        luma = float((a * W3).sum(2).mean())
        target = min(max(luma, LUMA_RANGE[0] + 0.01), LUMA_RANGE[1] - 0.01)
        if abs(target - luma) < 0.004 or not (0 < luma < 1):
            break
        a = np.clip(a, 1e-6, 1) ** (np.log(target) / np.log(luma))
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def cleanup(im, mask_path):
    mask = Image.open(mask_path).convert("L").resize(im.size)
    try:
        import cv2
        a = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
        m = (np.asarray(mask) > 127).astype(np.uint8) * 255
        m = cv2.dilate(m, np.ones((7, 7), np.uint8))
        res = cv2.inpaint(a, m, 9, cv2.INPAINT_TELEA)
        return Image.fromarray(cv2.cvtColor(res, cv2.COLOR_BGR2RGB)), "opencv-telea"
    except ImportError:
        m = mask.point(lambda v: 255 if v > 127 else 0).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(6))
        filled = im.filter(ImageFilter.GaussianBlur(28))
        return Image.composite(filled, im, m), "blur-fill (install opencv-python-headless for real inpainting)"




def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out_dir")
    ap.add_argument("--name"); ap.add_argument("--fit", default="crop", choices=["crop", "extend"])
    ap.add_argument("--focus", default="0.5,0.45"); ap.add_argument("--mask")
    ap.add_argument("--blur", type=float, default=2)
    ap.add_argument("--no-grade", action="store_true"); ap.add_argument("--warmth", type=float, default=1.06)
    ap.add_argument("--w", type=int, default=1080); ap.add_argument("--h", type=int, default=1920)
    a = ap.parse_args()

    os.makedirs(a.out_dir, exist_ok=True)
    name = a.name or os.path.splitext(os.path.basename(a.src))[0]
    src = Image.open(a.src)
    log = {"name": name, "source": os.path.abspath(a.src), "source_size": list(src.size), "time": time.strftime("%Y-%m-%d %H:%M:%S"), "steps": []}
    log["before"] = stats(src)

    im = reframe(src, a.w, a.h, a.fit, tuple(float(v) for v in a.focus.split(",")))
    log["steps"].append({"reframe": a.fit, "focus": a.focus, "size": [a.w, a.h]})
    if a.mask:
        im, how = cleanup(im, a.mask)
        log["steps"].append({"cleanup": how, "mask": os.path.abspath(a.mask)})
    if not a.no_grade:
        im = grade(im, a.warmth)
        log["steps"].append({"grade": {"luma_range": LUMA_RANGE, "sat_target": SAT_TARGET, "warmth": a.warmth}})
    if a.blur > 0:
        im = im.filter(ImageFilter.GaussianBlur(a.blur * 0.5))
        log["steps"].append({"soften": a.blur * 0.5})

    out = os.path.join(a.out_dir, f"{name}.jpg")
    im.save(out, quality=92)
    log["output"] = os.path.basename(out)
    log["after"] = stats(im)

    mpath = os.path.join(a.out_dir, "manifest.json")
    man = json.load(open(mpath, encoding="utf8")) if os.path.exists(mpath) else []
    man = [m for m in man if m.get("name") != name] + [log]
    json.dump(man, open(mpath, "w", encoding="utf8"), indent=1)
    print(json.dumps({"output": out, "before": log["before"], "after": log["after"], "notes": [s for s in log["steps"]]}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
