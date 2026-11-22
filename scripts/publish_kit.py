#!/usr/bin/env python3
"""Thumbnails for a finished Zoomby video + embed the vertical one as the MP4's cover image.

Usage:
  python publish_kit.py <video_folder> --plate 04_backgrounds/plates/8c.jpg --line1 "HE WON" --line2 "A PIG?!"
         --sub "8 WEIRD RONALDINHO FACTS" [--badge 1] [--crop-y 120] [--video 07_render/<slug>.mp4] [--no-embed]

Writes into <video_folder>/07_render/:
  thumbnail_vertical_1080x1920.jpg   Shorts / TikTok / Reels cover (also embedded in the MP4 as attached_pic)
  thumbnail_1280x720.jpg             YouTube custom thumbnail (16:9: text left, framed shot right)
Text style = the captions: Montserrat 900, white line 1, yellow #FFD60A line 2, thick black outline + soft shadow.
Use a CLEAN plate (04_backgrounds/plates/*.jpg, no captions or badge burned in), ideally the funniest face/prop shot.
publish.md itself is written by Claude from references/publish.md.
"""
import argparse, os, shutil, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "templates", "fonts", "Montserrat.ttf")
YEL, BLK, WHT = (255, 214, 10), (0, 0, 0), (255, 255, 255)


def font(px):
    f = ImageFont.truetype(FONT, px)
    try:
        f.set_variation_by_axes([900])
    except Exception:
        pass
    return f


def fit_px(text, px, max_w):
    while px > 20 and font(px).getlength(text) > max_w:
        px -= 4
    return px


def stroke_text(img, xy, text, px, fill, anchor="mm", rot=0):
    f = font(px)
    sw = max(4, px // 9)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xy[0] + sw * 0.6, xy[1] + sw * 1.2), text, font=f, fill=(0, 0, 0, 170), anchor=anchor,
                            stroke_width=sw, stroke_fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(sw * 0.8))
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).text(xy, text, font=f, fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=BLK)
    if rot:
        sh = sh.rotate(rot, center=xy, resample=Image.BICUBIC)
        lay = lay.rotate(rot, center=xy, resample=Image.BICUBIC)
    img.alpha_composite(sh)
    img.alpha_composite(lay)


def badge(img, cx, cy, r, num):
    d = ImageDraw.Draw(img)
    d.ellipse((cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6), fill=(0, 0, 0, 200))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=YEL + (255,))
    d.ellipse((cx - r * 0.55, cy - r * 0.75, cx + r * 0.1, cy - r * 0.2), fill=(255, 245, 190, 160))
    stroke_text(img, (cx, cy + 2), str(num), int(r * 1.15), WHT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--plate", required=True)
    ap.add_argument("--line1", required=True)
    ap.add_argument("--line2", required=True)
    ap.add_argument("--sub", default="")
    ap.add_argument("--badge", default=None)
    ap.add_argument("--crop-y", type=int, default=120, help="top of the 1080x1000 window used for the 16:9 photo panel")
    ap.add_argument("--text-y", type=float, default=0.64, help="vertical cover: centre of line 1 as a fraction of the height")
    ap.add_argument("--video")
    ap.add_argument("--no-embed", action="store_true")
    A = ap.parse_args()
    out = os.path.join(A.folder, "07_render")
    base = Image.open(os.path.join(A.folder, A.plate)).convert("RGB").resize((1080, 1920))
    base = ImageEnhance.Contrast(ImageEnhance.Color(base).enhance(1.12)).enhance(1.06)

    # vertical 1080x1920
    v = base.copy().convert("RGBA")
    y1 = int(1920 * A.text_y)
    grad = Image.new("L", (1, 1920))
    for y in range(1920):
        grad.putpixel((0, y), int(max(0.0, min(1.0, (y - (y1 - 200)) / 500)) * 170))
    v.alpha_composite(Image.merge("RGBA", (Image.new("L", v.size, 0),) * 3 + (grad.resize(v.size),)))
    p1, p2 = fit_px(A.line1, 190, 980), fit_px(A.line2, 230, 980)
    stroke_text(v, (540, y1), A.line1, p1, WHT, rot=-4)
    stroke_text(v, (540, y1 + int(p2 * 0.85)), A.line2, p2, YEL, rot=-4)
    if A.sub:
        stroke_text(v, (540, y1 + int(p2 * 0.85) + int(p2 * 0.75)), A.sub, fit_px(A.sub, 62, 1000), WHT)
    if A.badge:
        badge(v, 150, 250, 95, A.badge)
    vp = os.path.join(out, "thumbnail_vertical_1080x1920.jpg")
    v.convert("RGB").save(vp, quality=92)

    # landscape 1280x720
    L = Image.new("RGBA", (1280, 720), (0, 0, 0, 255))
    cy = max(0, min(920, A.crop_y))
    panel = base.crop((0, cy, 1080, cy + 1000)).resize((720, 667))
    bg = ImageEnhance.Brightness(base.resize((1280, 2276)).crop((0, 300, 1280, 1020)).filter(ImageFilter.GaussianBlur(22))).enhance(0.55)
    L.paste(bg.convert("RGBA"), (0, 0))
    L.paste(panel.convert("RGBA"), (560, 53))
    ImageDraw.Draw(L).rectangle((556, 49, 1284, 724), outline=(0, 0, 0, 255), width=8)
    stroke_text(L, (285, 250), A.line1, fit_px(A.line1, 118, 500), WHT, rot=-4)
    stroke_text(L, (285, 395), A.line2, fit_px(A.line2, 142, 500), YEL, rot=-4)
    if A.sub:
        words = A.sub.split()
        half = (len(words) + 1) // 2
        l1, l2 = " ".join(words[:half]), " ".join(words[half:])
        px = min(fit_px(l1, 44, 500), fit_px(l2, 44, 500) if l2 else 44)
        stroke_text(L, (285, 560), l1, px, WHT)
        if l2:
            stroke_text(L, (285, 615), l2, px, WHT)
    if A.badge:
        badge(L, 80, 80, 52, A.badge)
    L.convert("RGB").save(os.path.join(out, "thumbnail_1280x720.jpg"), quality=92)

    if not A.no_embed and A.video:
        vid = os.path.join(A.folder, A.video)
        tmp = vid[:-4] + "_cover.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", vp, "-map", "0:v:0", "-map", "0:a?", "-map", "1",
                        "-c", "copy", "-c:v:1", "mjpeg", "-disposition:v:1", "attached_pic", tmp], check=True)
        shutil.move(tmp, vid)
    print("thumbnails written to", out)


if __name__ == "__main__":
    main()
