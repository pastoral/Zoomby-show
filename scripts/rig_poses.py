#!/usr/bin/env python3
"""Build character rigs: body layer + interchangeable head layers (one per emotion) on a shared canvas.

Usage:
  python rig_poses.py CHAR_DIR [--outfits chains,tux,purple] [--views front] [--head-scale 0.62] [--side-scale 0.775]

CHAR_DIR layout (CHAR_DIR = <video>/03_character; rigs.json paths come out relative to the video folder):
  CHAR_DIR/body/<outfit>_<view>.png     transparent body cut-outs (from the character sheet; the real head stays, the cartoon head covers it)
  CHAR_DIR/heads/head_<emotion>.png      transparent cartoon heads: neutral (required), happy, laugh, smug, sad, angry,
                                     surprised, scared, confused, love, shock, profile (side view) ... any you have
  CHAR_DIR/heads/head_neutral_half.png optional: same head with the mouth slightly open (speaking shots)
  CHAR_DIR/heads/head_neutral_open.png   optional: wider open mouth (used only with lip "full")
  CHAR_DIR/hands/hand_<gesture>.png      optional: cartoon hands (wave, point, thumbs, fist) used by the "hands" key

Writes CHAR_DIR/rig/<outfit>[_side]_body.png, CHAR_DIR/rig/<outfit>[_side]_<emotion>.png and CHAR_DIR/rig/rigs.json:
  {"tux": {"body": "03_character/rig/tux_body.png", "neck": [x%, y%], "heads": {"neutral": ..., "sad": ...},
           "mouth_half": ..., "mouth_open": ...}, "tux_side": {...}}
Paste rigs.json into zoomby.project.json -> "rigs". A character then only needs {"rig": "tux", "emotion": "sad"}.
"""
import argparse, glob, json, os
import numpy as np
from PIL import Image

BH = 1400


def load_body(path):
    b = Image.open(path).convert("RGBA")
    s = BH / b.height
    return b.resize((round(b.width * s), BH), Image.LANCZOS)


def build(char_dir, name, body_path, head_paths, hscale):
    b = load_body(body_path)
    a = np.asarray(b.getchannel("A"))
    xs = np.where(a[int(BH * 0.05)] > 128)[0]
    hx = int(xs.mean()) if len(xs) else b.width // 2
    neck = int(BH * 0.135)
    H = {}
    for key, p in head_paths.items():
        h = Image.open(p).convert("RGBA")
        hw = round(b.width * hscale)
        H[key] = h.resize((hw, round(h.height * hw / h.width)), Image.LANCZOS)
    top = min(neck - h.height + int(h.height * 0.08) for h in H.values())
    off = -top if top < 0 else 0
    hwmax = max(h.width for h in H.values())
    left = min(0, hx - hwmax // 2)
    right = max(b.width, hx + hwmax // 2)
    Wc, Hc = right - left, BH + off
    out = os.path.join(char_dir, "rig")
    os.makedirs(out, exist_ok=True)
    c = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0)); c.alpha_composite(b, (-left, off))
    body_out = os.path.join(out, f"{name}_body.png"); c.save(body_out)
    rel = lambda p: os.path.relpath(p, os.path.dirname(char_dir.rstrip("/\\")) or ".").replace("\\", "/")
    rig = {"body": rel(body_out), "neck": [round((hx - left) / Wc * 100, 1), round((off + neck) / Hc * 100, 1)], "heads": {}, "size": [Wc, Hc]}
    for key, h in H.items():
        c = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0))
        c.alpha_composite(h, (hx - h.width // 2 - left, off + neck - h.height + int(h.height * 0.08)))
        p = os.path.join(out, f"{name}_{key}.png"); c.save(p)
        if key in ("neutral_half", "neutral_open"):
            rig["mouth_" + key.split("_")[1]] = rel(p)
        else:
            rig["heads"][key] = rel(p)
    return rig


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("char_dir")
    ap.add_argument("--outfits", default="")
    ap.add_argument("--views", default="front,side_r")
    ap.add_argument("--head-scale", type=float, default=0.62)
    ap.add_argument("--side-scale", type=float, default=0.775)
    A = ap.parse_args()
    heads = {os.path.basename(p)[5:-4]: p for p in glob.glob(os.path.join(A.char_dir, "heads", "head_*.png"))}
    if "neutral" not in heads:
        raise SystemExit("need char/heads/head_neutral.png")
    outfits = [o for o in A.outfits.split(",") if o] or sorted({os.path.basename(p).rsplit("_", 1)[0].replace("_side", "")
                                                               for p in glob.glob(os.path.join(A.char_dir, "body", "*_front.png"))})
    rigs = {}
    for o in outfits:
        for v in A.views.split(","):
            bp = os.path.join(A.char_dir, "body", f"{o}_{v}.png")
            if not os.path.exists(bp):
                continue
            side = v != "front"
            if side:
                hp = {k: p for k, p in heads.items() if k.startswith("profile")} or {"profile": heads["neutral"]}
                hp = {("neutral" if k == "profile" else k.replace("profile_", "")): p for k, p in hp.items()}
            else:
                hp = {k: p for k, p in heads.items() if not k.startswith("profile")}
            name = f"{o}_side" if side else o
            rigs[name] = build(A.char_dir, name, bp, hp, A.side_scale if side else A.head_scale)
            print(name, "heads:", ", ".join(sorted(rigs[name]["heads"])), "| neck", rigs[name]["neck"])
    json.dump(rigs, open(os.path.join(A.char_dir, "rig", "rigs.json"), "w"), indent=1)
    print("wrote", os.path.join(A.char_dir, "rig", "rigs.json"))


if __name__ == "__main__":
    main()
