#!/usr/bin/env python3
"""Render the code-drawn character sheet (SVG puppets) for approval.

Usage: python puppet_sheet.py <video>/03_character/puppet.json [--out <video>/03_character/sheet]

Builds a small HyperFrames composition (1920x1080, one page per second):
  page 1..n  every outfit of the main character in the key poses
  next       emotion heads grid (all 16 emotions)
  last       hands, props and the supporting cast
then snapshots each page to OUT/puppet_sheet_<n>.png (needs node + npx hyperframes).
"""
import argparse, json, os, shutil, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zoomby_puppet as ZP

W, H = 1920, 1080
KEY_POSES = ["front", "side_r", "walk", "run", "celebrate", "wave", "point", "shush", "sip", "hold_up", "piggyback", "jump"]


def cell(svg, label, w, h):
    return (f'<div class="cell" style="width:{w}px;height:{h}px"><div class="fig">{svg}</div>'
            f'<div class="lab">{label}</div></div>')


def head_svg(spec, pid, emo):
    s = ZP.puppet_svg(spec, pid, next(iter(spec["outfits"])), ["front"], [emo])
    return s.replace(f'viewBox="{ZP.VIEWBOX}"', 'viewBox="40 -10 320 360"').replace("overflow:visible", "overflow:hidden")


def page(title, cells, cols, cw, ch):
    return (f'<div class="page"><div class="title">{title}</div>'
            f'<div class="grid" style="grid-template-columns:repeat({cols},{cw}px)">{"".join(cells)}</div></div>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--out")
    A = ap.parse_args()
    D = json.load(open(A.spec, encoding="utf8"))
    out = A.out or os.path.join(os.path.dirname(os.path.abspath(A.spec)), "sheet")
    os.makedirs(out, exist_ok=True)
    chars = D["characters"]
    main_id = D.get("main") or next(iter(chars))
    M = chars[main_id]
    rider_id = next((k for k in chars if k not in (main_id,) and "barca" in chars[k].get("outfits", {})), None)
    props = D.get("props", {})
    pages = []
    n = 0
    for o in M["outfits"]:
        cells = []
        for pz in KEY_POSES:
            n += 1
            hold = None
            if pz == "hold_up":
                hold = dict(props.get("pig", {"name": "football"}))
            if pz == "sip":
                hold = dict(props.get("can_blue", {"name": "can"}))
            carry = None
            if pz == "piggyback" and rider_id:
                carry = ZP.rider(chars[rider_id], f"r{n}", o)
            emo = {"celebrate": "happy", "hold_up": "laugh", "sip": "proud", "shush": "smug", "run": "happy", "jump": "happy",
                   "piggyback": "laugh", "wave": "happy"}.get(pz, "neutral")
            svg = ZP.puppet_svg(M, f"p{n}", o, [pz], [emo], hold=hold, carry=carry)
            cells.append(cell(svg, f"{o}_{pz}", 300, 470))
        pages.append(page(f"{main_id} · outfit <b>{o}</b> · poses", cells, 6, 300, 470))
    cells = []
    for e in ZP.EMOTIONS:
        if e in ("talk", "shock"):
            continue
        n += 1
        cells.append(cell(head_svg(M, f"h{n}", e), e, 220, 250))
    n += 1
    cells.append(cell(head_svg(M, f"h{n}", "neutral").replace('class="mc"', 'class="mc" opacity="0"').replace('class="mh" opacity="0"', 'class="mh"')
                      if False else ZP.puppet_svg(M, f"h{n}", next(iter(M["outfits"])), ["front"], ["neutral"], speaking=True)
                      .replace(f'viewBox="{ZP.VIEWBOX}"', 'viewBox="40 -10 320 360"').replace("overflow:visible", "overflow:hidden").replace('class="mc"', 'class="mc" opacity="0"').replace('class="mh" opacity="0"', 'class="mh"'),
                      "speaking (half-open)", 220, 250))
    pages.append(page(f"{main_id} · emotions (mouth closed unless laugh / surprised)", cells, 7, 220, 250))
    cells = []
    for k in ZP.HANDS:
        if k == "hold":
            continue
        svg = (f'<svg viewBox="-60 -100 120 110" width="100%" height="100%"><g transform="rotate(180)">{ZP.HANDS[k]().replace("SKIN", M["skin"])}</g></svg>')
        cells.append(cell(svg, f"hand {k}", 150, 170))
    for pid_, pr in props.items():
        pr = dict(pr); name = pr.pop("name")
        svg = f'<svg viewBox="-130 -120 260 240" width="100%" height="100%">{ZP.prop_svg(name, **pr)}</svg>'
        cells.append(cell(svg, f"prop {pid_}", 150, 170))
    for cid_, sp in chars.items():
        if cid_ == main_id:
            continue
        n += 1
        o = next(iter(sp["outfits"]))
        emo = "sad" if cid_ == "defender" else "happy"
        pz = "slump" if cid_ == "defender" else "front"
        cells.append(cell(ZP.puppet_svg(sp, f"c{n}", o, [pz], [emo]), f"cast {cid_}", 220, 360))
    pages.append(page("hands · props · supporting cast", cells, 9, 160, 170))

    clips = "".join(f'<div id="pg{i}" class="clip" data-start="{i}" data-duration="1" data-track-index="0">{p}</div>' for i, p in enumerate(pages))
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width={W}, height={H}" />
<title>Puppet sheet</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
html,body {{ margin:0; background:#fff; }}
#root {{ position:relative; width:100%; height:100%; overflow:hidden; background:#FFFFFF; font-family: Arial, sans-serif; }}
.clip {{ position:absolute; inset:0; }}
.page {{ position:absolute; inset:0; padding:24px 30px; box-sizing:border-box; background:#FFFFFF; }}
.title {{ font-size:30px; color:#333; margin-bottom:14px; }}
.grid {{ display:grid; gap:10px 16px; }}
.cell {{ position:relative; }}
.fig {{ position:absolute; left:0; right:0; top:0; bottom:26px; }}
.lab {{ position:absolute; left:0; right:0; bottom:0; text-align:center; font-size:17px; color:#555; }}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-fps="25" data-duration="{len(pages)}">
{clips}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
tl.set("#root", {{opacity:1}}, 0);
window.__timelines["main"] = tl;
</script>
</body></html>
"""
    import hashlib, tempfile
    # build in a short temp path: the CLI's snapshot paths inside a deep video folder exceed Windows MAX_PATH
    proj = os.path.join(tempfile.gettempdir(), "zb_sheet_" + hashlib.md5(os.path.abspath(out).encode()).hexdigest()[:8])
    shutil.rmtree(proj, ignore_errors=True)
    os.makedirs(proj, exist_ok=True)
    open(os.path.join(proj, "index.html"), "w", encoding="utf8").write(html)
    at = ",".join(f"{i + 0.5}" for i in range(len(pages)))
    r = subprocess.run(f'npx hyperframes snapshot --at {at}', cwd=proj, shell=True, capture_output=True, text=True, encoding="utf8", errors="replace")
    print(r.stdout[-1500:], r.stderr[-1500:])
    import time
    found = []
    for _ in range(20):  # the CLI may finish writing the PNGs just after it exits
        found = [os.path.join(dp, f) for dp, _, fs in os.walk(proj) for f in fs if f.endswith(".png") and "-at-" in f]
        if len({f.rsplit("-at-", 1)[1] for f in found}) >= len(pages):
            break
        time.sleep(1)
    found.sort(key=os.path.getmtime)
    shots = []
    for i in range(len(pages)):
        tag = f"-at-{i + 0.5}s.png"
        m = [f for f in found if f.endswith(tag)]
        if m:
            shots.append(m[-1])
    res = []
    for i, f in enumerate(shots):
        dst = os.path.join(out, f"puppet_sheet_{i + 1}.png")
        shutil.copyfile(f, dst); res.append(dst)
    print(json.dumps({"pages": res}, indent=1))


if __name__ == "__main__":
    main()
