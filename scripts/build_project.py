#!/usr/bin/env python3
"""Build a Zoomby HyperFrames project (index.html) from zoomby.project.json.

Usage:  python build_project.py PROJECT.json OUT_DIR

Asset paths in the JSON are relative to the VIDEO FOLDER (paths.root, default: the folder above the
JSON, i.e. <video>/ when the JSON lives in <video>/06_project/), e.g. "03_character/rig/tux_body.png",
"04_backgrounds/scene01.jpg", "05_vo/vo.wav". Files outside OUT_DIR are copied into OUT_DIR/media/
(same sub-path) so the HyperFrames project is self-contained. Paths that already exist inside OUT_DIR
are used as they are (older projects).
Schema: ../templates/zoomby.project.example.json. Style defaults: ../references/style.md.
Then:  cd OUT_DIR && npx hyperframes check && npx hyperframes snapshot --at ... && npx hyperframes render -o out.mp4
"""
import html, json, math, os, re, shutil, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zoomby_motion as ZM
import zoomby_puppet as ZP
import zoomby_fx as ZF

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULTS = {
    "badge": {"show": True, "color": "#8A3FE9", "x_pct": 14, "y_pct": 13, "diameter_pct_w": 12},
    "caption": {"words_per_chunk": 2, "min_chunk_s": 0.18, "center_y_pct": 64, "cap_height_pct_h": 3.2,
                "fill": "#FFFFFF", "stroke": "#000000", "stroke_px": 6, "pop_from_scale": 0.9, "pop_frames": 1,
                "max_join_chars": 7, "hold_after_s": 0.25},
    "camera": {"drift_pct": 6, "punch_in_pct": 20, "whip_frames": 3, "whip_blur_px": 40, "pan_pct": 5},
    "character": {"bob_px": 10, "bob_s": 0.28, "mouth_s": 0.09, "lip": "minimal",
                  "talk_default": "speaking"},  # lips move only on shots marked "speaking": true ("always" = old behaviour)
}


def merge(a, b):
    out = json.loads(json.dumps(a))
    for k, v in (b or {}).items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def esc(s):
    return html.escape(str(s), quote=True)


def shade(hexc, f):
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    if f >= 0:
        r, g, b = (round(c + (255 - c) * f) for c in (r, g, b))
    else:
        r, g, b = (round(c * (1 + f)) for c in (r, g, b))
    return f"#{r:02X}{g:02X}{b:02X}"


def chunk_words(words, cfg, fps):
    """Group word timings into 1-2 word caption chunks (Zoomby: 1-2 words, new chunk every 0.2-0.5 s)."""
    ws = [dict(w, w=str(w["w"]).strip()) for w in words if str(w["w"]).strip()]
    chunks, i = [], 0
    while i < len(ws):
        c = [ws[i]]
        a = ws[i]
        if cfg["words_per_chunk"] >= 2 and i + 1 < len(ws):
            b = ws[i + 1]
            ends_sentence = re.search(r"[.?!,:;]$", a["w"]) is not None
            is_num = re.search(r"\d", a["w"] + b["w"]) is not None
            short = len(a["w"]) + len(b["w"]) <= cfg["max_join_chars"] + 4 and min(len(a["w"]), len(b["w"])) <= cfg["max_join_chars"]
            fast = (b["e"] - a["s"]) < 0.55 and (a["e"] - a["s"]) < cfg["min_chunk_s"] * 2
            if short and fast and not ends_sentence and not is_num:
                c.append(b)
        chunks.append(c)
        i += len(c)
    out = []
    for j, c in enumerate(chunks):
        s = c[0]["s"]
        nxt = chunks[j + 1][0]["s"] if j + 1 < len(chunks) else None
        e = c[-1]["e"] + cfg["hold_after_s"]
        if nxt is not None and nxt - c[-1]["e"] < 0.6:
            e = nxt
        e = max(e, s + max(cfg["min_chunk_s"], 2 / fps))
        if nxt is not None:
            e = min(e, nxt)
        text = " ".join(w["w"] for w in c).upper()
        text = re.sub(r"[.,;:]+$", "", text)  # Zoomby drops trailing periods/commas; keeps ? and !
        out.append({"text": text, "s": round(s, 3), "e": round(e, 3)})
    return out



def puppet_inner(ch, cid, PUP):
    """inline SVG for a code-drawn puppet character (see zoomby_puppet.py / references/puppet.md)"""
    spec = PUP["characters"][ch["puppet"]]
    names, emos = ZP.needed(ch)
    hold = None
    if ch.get("hold"):
        hold = dict(PUP.get("props", {}).get(ch["hold"], {"name": ch["hold"]}))
    carry = None
    if ch.get("carry"):
        carry = ZP.rider(PUP["characters"][ch["carry"]], f"{cid}-r", ch.get("outfit"), ch.get("carry_emotion", "laugh"))
    outfit = ch.get("outfit") or next(iter(spec["outfits"]))
    return ZP.puppet_svg(spec, f"{cid}-p", outfit, names, emos, speaking=bool(ch.get("talk")), hold=hold, carry=carry)


MEDIA_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".wav", ".mp3", ".m4a", ".aac", ".ogg", ".mp4", ".mov", ".webm")


def localize(P, proj_path, out_dir):
    """Rewrite every media path so it resolves inside out_dir (copy from the video folder when needed)."""
    root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(proj_path)),
                                         (P.get("paths") or {}).get("root", "..")))
    out_abs = os.path.abspath(out_dir)

    def fix(v):
        if not (isinstance(v, str) and v.lower().endswith(MEDIA_EXT)) or re.match(r"^[a-z]+:", v):
            return v
        if os.path.exists(os.path.join(out_abs, v)):
            return v
        src = os.path.join(root, v)
        if not os.path.exists(src):
            print(f"warning: missing media {v}", file=sys.stderr)
            return v
        rel = "media/" + os.path.relpath(src, root).replace("\\", "/")
        dst = os.path.join(out_abs, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
            shutil.copy2(src, dst)
        return rel

    def walk(o):
        if isinstance(o, dict):
            return {k: (o[k] if k in ("words", "storyboard_initial", "storyboard_final", "assets", "topic_options") else walk(o[k])) for k in o}
        if isinstance(o, list):
            return [walk(x) for x in o]
        return fix(o)
    return walk(P)


def main():
    proj_path, out_dir = sys.argv[1], sys.argv[2]
    P = json.load(open(proj_path, encoding="utf8"))
    os.makedirs(out_dir, exist_ok=True)
    P = localize(P, proj_path, out_dir)
    root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(proj_path)), (P.get("paths") or {}).get("root", "..")))
    PUP = {}  # code-drawn puppets (character_route "code"): {"characters": {...}, "props": {...}}
    if P.get("puppet_spec"):
        PUP = json.load(open(os.path.join(root, P["puppet_spec"]), encoding="utf8"))
    cfg = merge(DEFAULTS, P.get("params", {}))
    W, H, fps = P.get("width", 1080), P.get("height", 1920), P.get("fps", 25)
    words = P.get("words", [])
    shots_all = [sh for sc in P["scenes"] for sh in sc["shots"]]
    D = P.get("duration") or round(max([sh["end"] for sh in shots_all] + [words[-1]["e"] + 0.6 if words else 0]), 3)

    os.makedirs(os.path.join(out_dir, "fonts"), exist_ok=True)
    font_src = os.path.join(HERE, "..", "templates", "fonts", "Montserrat.ttf")
    shutil.copyfile(font_src, os.path.join(out_dir, "fonts", "Montserrat.ttf"))

    body, tl = [], []
    f1 = 1 / fps
    cam = cfg["camera"]
    tl.append(f"// {len(shots_all)} shots, duration {D}s")

    # ---------------- shots (background plate + characters + bubbles/symbols) ----------------
    n = 0
    for si, sc in enumerate(P["scenes"]):
        for sh in sc["shots"]:
            n += 1
            sid = f"s{n:02d}"
            st, du = round(sh["start"], 3), round(sh["end"] - sh["start"], 3)
            parts = [f'<img id="{sid}-bg" class="bg" src="{esc(sh["bg"])}" alt="" />']
            if sh.get("eyes"):  # premium route: animated cartoon eyes over the still's own eyes
                eh, ej = ZF.eyes(sh["eyes"], sid, st, du, W, H)
                parts.append(eh); tl.extend(ej)
            for ci, ch in enumerate(sh.get("characters", [])):
                cid = f"{sid}-c{ci}"
                ch = dict(ch)
                if cfg["character"].get("lip") == "none":
                    ch["talk"] = False
                elif cfg["character"].get("talk_default", "speaking") == "speaking":
                    ch.setdefault("talk", bool(sh.get("speaking", False)))
                ch = ZM.resolve_rig(ch, P)          # rig + emotion -> body/head/mouth paths and automatic acting
                puppet = ch.get("puppet")
                if puppet:
                    spec = PUP["characters"][puppet]
                    ch.setdefault("neck", [50, 34])
                    hpx = H * ch.get("h", 60) / 100
                    wpx = hpx * ZP.ASPECT
                else:
                    iw, ih = Image.open(os.path.join(out_dir, ch["src"])).size
                    hpx = H * ch.get("h", 55) / 100
                    wpx = hpx * iw / ih
                left = W * ch.get("x", 50) / 100 - wpx / 2
                top = H * ch.get("y", 62) / 100 - hpx / 2
                flip = "scale(-1,1)" if ch.get("flip") else "none"
                # Layering: #cid (position + bob) > #cid-fx (keyframed moves) > #cid-idle (sway/breath) > flip > body + head + hands
                imgs = (f'<div id="{cid}-fx" class="layer" style="transform-origin:50% 100%">'
                        f'<div id="{cid}-idle" class="layer" style="transform-origin:50% 100%">'
                        f'<div class="layer" style="transform:{flip}">{puppet_inner(ch, cid, PUP) if puppet else ZM.char_inner_html(ch, cid)}</div></div></div>')
                parts.append(f'<div id="{cid}" class="char" style="left:{left:.0f}px;top:{top:.0f}px;width:{wpx:.0f}px;height:{hpx:.0f}px">{imgs}</div>')
                tl.extend(ZM.acting_js(ch, cid, st, du, W, H, words))
                emo_html, emo_js = ZM.emotion_symbol(ch, cid, left, top, wpx, hpx, st, du)
                if emo_html:
                    parts.append(emo_html); tl.extend(emo_js)
                if ch.get("bob", False):  # old constant head-bob; the idle sway replaces it by default
                    reps = max(1, int(du / cfg["character"]["bob_s"]) - 1)
                    tl.append(f'tl.fromTo("#{cid}",{{y:0}},{{y:-{cfg["character"]["bob_px"]},duration:{cfg["character"]["bob_s"]},ease:"sine.inOut",yoyo:true,repeat:{reps}}},{st});')
                if puppet:
                    tl.extend(ZP.puppet_js(ch, f"{cid}-p", spec, st, du, words))
                else:
                    tl.extend(ZM.lips_js(ch, cid, st, du, words, cfg, f1))
            for pi, pr in enumerate(sh.get("props", [])):   # free-standing code-drawn props
                prid = f"{sid}-pr{pi}"
                spec_p = dict(PUP.get("props", {}).get(pr["prop"], {"name": pr["prop"]}))
                name = spec_p.pop("name")
                at = round(st + pr.get("at", 0), 3)
                sz = W * pr.get("w", 22) / 100
                parts.append(f'<div id="{prid}" class="char" style="left:{W * pr.get("x", 50) / 100 - sz / 2:.0f}px;top:{H * pr.get("y", 60) / 100 - sz / 2:.0f}px;width:{sz:.0f}px;height:{sz:.0f}px">'
                             f'<svg viewBox="-130 -130 260 260" width="100%" height="100%" style="overflow:visible"><g transform="rotate({pr.get("rot", 0)})">{ZP.prop_svg(name, **spec_p)}</g></svg></div>')
                tl.append(f'tl.fromTo("#{prid}",{{scale:0,opacity:0}},{{scale:1,opacity:1,duration:0.25,ease:"back.out(2.4)",immediateRender:false}},{at});')
                tl.append(f'tl.set("#{prid}",{{scale:0,opacity:0}},{st});')
            def bfit(key, text):  # long bubble words shrink to fit the oval (about 7 caps at full size)
                n = len(str(text))
                return f' style="font-size:{H * 0.032 / 0.72 * 0.85 * 5.6 / n:.0f}px"' if key == "bubble" and n > 7 else ""
            for key in ("bubble", "symbol"):
                b = sh.get(key)
                if not b:
                    continue
                bid = f"{sid}-{key}"
                at = round(st + b.get("at", 0.2), 3)
                cls = "bubble" if key == "bubble" else "symbol"
                parts.append(f'<div id="{bid}" class="{cls}-pos" style="left:{b.get("x", 70)}%;top:{b.get("y", 20)}%"><div id="{bid}-in" class="{cls}"{' data-layout-allow-occlusion' if key == 'symbol' else ''}{bfit(key, b["text"])}>{esc(b["text"])}</div></div>')
                tl.append(f'tl.fromTo("#{bid}-in",{{scale:0,opacity:0}},{{scale:1,opacity:1,duration:0.24,ease:"back.out(2.4)"}},{at});')
                if key == "symbol":
                    tl.append(f'tl.fromTo("#{bid}",{{y:0}},{{y:-14,duration:0.4,ease:"sine.inOut",yoyo:true,repeat:{max(1, int((du - b.get("at", 0.2)) / 0.4) - 1)}}},{at});')
            chart_html = ""
            if sh.get("chart"):
                chart_html, cjs = ZM.chart(sh["chart"], sid, st, du, W, H)
                tl.extend(cjs)
            if sh.get("fx"):
                fx_html, fx_js = ZF.fx(sh["fx"], sid, st, du, W, H)
                chart_html += fx_html; tl.extend(fx_js)
            body.append(
                f'<div id="{sid}" class="clip shot" data-start="{st}" data-duration="{du}" data-track-index="1">'
                f'<div id="{sid}-whip" class="layer"><div id="{sid}-punch" class="layer"><div id="{sid}-cam" class="cam">'
                + "".join(parts) + "</div></div>" + chart_html + "</div></div>")
            # camera move on the single background plate (no depth layers)
            mv = sh.get("camera", "push")
            dp = sh.get("drift", cam["drift_pct"]) / 100
            px = W * cam["pan_pct"] / 100
            if mv == "push":
                tl.append(f'tl.fromTo("#{sid}-cam",{{scale:1}},{{scale:{1 + dp:.3f},duration:{du},ease:"sine.inOut"}},{st});')
            elif mv == "pull":
                tl.append(f'tl.fromTo("#{sid}-cam",{{scale:{1 + dp:.3f}}},{{scale:1,duration:{du},ease:"sine.inOut"}},{st});')
            elif mv in ("pan-left", "pan-right"):
                a, b2 = (px, -px) if mv == "pan-left" else (-px, px)
                tl.append(f'tl.fromTo("#{sid}-cam",{{x:{a:.0f},scale:1.08}},{{x:{b2:.0f},scale:1.08,duration:{du},ease:"sine.inOut"}},{st});')
            if sh.get("punch"):
                pc = sh["punch"]
                tl.append(f'tl.set("#{sid}-punch",{{scale:{1 + pc.get("pct", cam["punch_in_pct"]) / 100:.3f}}},{st + pc.get("at", du / 2):.3f});')
            if sh.get("enter") == "zoom":  # zoom/radial-blur whip (premium route)
                tl.append(f'tl.fromTo("#{sid}-whip",{{scale:1.38,filter:"blur(22px)"}},{{scale:1,filter:"blur(0px)",duration:0.22,ease:"power3.out"}},{st});')
            if sh.get("enter") == "whip":
                tl.append(f'tl.fromTo("#{sid}-whip",{{x:{-W * 0.18:.0f},filter:"blur({cam["whip_blur_px"]}px)"}},{{x:0,filter:"blur(0px)",duration:{cam["whip_frames"] * f1:.3f},ease:"power2.out"}},{st});')

    # ---------------- countdown badge ----------------
    bd = cfg["badge"]
    if bd["show"]:
        for si, sc in enumerate(P["scenes"]):
            if sc.get("badge") is None:
                continue
            st = round(min(s["start"] for s in sc["shots"]), 3)
            du = round(max(s["end"] for s in sc["shots"]) - st, 3)
            bc = sc.get("badge_color")  # per-scene colour (e.g. it follows the shirt); default params.badge.color
            bstyle = (f' style="background: radial-gradient(circle at 32% 28%, {shade(bc, 0.75)} 0%, {shade(bc, 0.15)} 22%, {bc} 55%, {shade(bc, -0.45)} 100%)"'
                      if bc else "")
            body.append(f'<div id="badge{si}" class="clip badge-pos" data-start="{st}" data-duration="{du}" data-track-index="3">'
                        f'<div class="badge"{bstyle}><span>{esc(sc["badge"])}</span></div></div>')

    # ---------------- captions ----------------
    cc = cfg["caption"]
    for k, c in enumerate(chunk_words(words, cc, fps)):
        if c["s"] >= D:
            continue
        c["e"] = min(c["e"], D)
        cid = f"cap{k:03d}"
        body.append(f'<div id="{cid}" class="clip cap-pos" data-start="{c["s"]}" data-duration="{round(c["e"] - c["s"], 3)}" data-track-index="4">'
                    f'<div id="{cid}-t" class="cap">{esc(c["text"])}</div></div>')
        tl.append(f'tl.fromTo("#{cid}-t",{{scale:{cc["pop_from_scale"]},opacity:0.85}},{{scale:1,opacity:1,duration:{cc["pop_frames"] * f1:.3f},ease:"none"}},{c["s"]});')

    # ---------------- audio ----------------
    db = lambda d: round(10 ** (d / 20), 3)
    vo = P["vo"]
    body.append(f'<audio id="vo" src="{esc(vo["src"])}" data-start="0" data-duration="{D}" data-volume="{vo.get("volume", 1)}"></audio>')
    if P.get("music"):
        m = P["music"]
        body.append(f'<audio id="music" src="{esc(m["src"])}" data-start="0" data-duration="{D}" data-volume="{db(m.get("db", -18))}"></audio>')
    for k, s in enumerate(P.get("sfx", [])):
        body.append(f'<audio id="sfx{k:02d}" src="{esc(s["src"])}" data-start="{s["t"]}" data-duration="{s.get("dur", 1)}" data-volume="{db(s.get("db", -8))}"></audio>')

    # ---------------- page ----------------
    bdia = W * bd["diameter_pct_w"] / 100
    cap_px = H * cc["cap_height_pct_h"] / 100 / 0.72  # font-size from cap height (Montserrat caps ~0.72 em)
    sp = cc["stroke_px"]
    shadow = ",".join(f"{x}px {y}px 0 {cc['stroke']}" for x, y in [(sp, 0), (-sp, 0), (0, sp), (0, -sp), (sp * .7, sp * .7), (-sp * .7, sp * .7), (sp * .7, -sp * .7), (-sp * .7, -sp * .7)])
    css = f"""
@font-face {{ font-family: "Montserrat"; src: url("fonts/Montserrat.ttf") format("truetype"); font-weight: 100 900; }}
html,body {{ margin:0; background:#000; }}
#root {{ position:relative; width:100%; height:100%; overflow:hidden; background:#000; font-family:"Montserrat", sans-serif; }}
.clip {{ position:absolute; inset:0; }}
.layer {{ position:absolute; inset:0; }}
.cam {{ position:absolute; inset:0; overflow:hidden; }}
.bg {{ position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }}
.char {{ position:absolute; }}
.char-img {{ position:absolute; inset:0; width:100%; height:100%; object-fit:contain; }}
.char-open {{ opacity:0; }}
.badge-pos {{ pointer-events:none; }}
.badge {{ position:absolute; left:{W * bd['x_pct'] / 100 - bdia / 2:.0f}px; top:{H * bd['y_pct'] / 100 - bdia / 2:.0f}px; width:{bdia:.0f}px; height:{bdia:.0f}px; border-radius:50%;
  background: radial-gradient(circle at 32% 28%, {shade(bd['color'], 0.75)} 0%, {shade(bd['color'], 0.15)} 22%, {bd['color']} 55%, {shade(bd['color'], -0.45)} 100%);
  box-shadow: 0 6px 14px rgba(0,0,0,.45), inset 0 -6px 10px rgba(0,0,0,.25), 0 0 0 3px rgba(255,255,255,.35);
  display:flex; align-items:center; justify-content:center; }}
.badge span {{ font-weight:900; font-size:{bdia * 0.55:.0f}px; color:#fff; line-height:1;
  text-shadow: 3px 0 0 #000,-3px 0 0 #000,0 3px 0 #000,0 -3px 0 #000,2px 2px 0 #000,-2px 2px 0 #000,2px -2px 0 #000,-2px -2px 0 #000; }}
.cap-pos {{ display:flex; align-items:center; justify-content:center; pointer-events:none; }}
.cap {{ position:absolute; left:6%; right:6%; top:{cc['center_y_pct']}%; margin-top:-{cap_px * 0.6:.0f}px; text-align:center;
  font-weight:900; font-size:{cap_px:.0f}px; line-height:1.05; letter-spacing:-0.01em; color:{cc['fill']};
  text-shadow:{shadow}, 0 {sp}px {sp * 2}px rgba(0,0,0,.55); }}
{ZM.CSS.format(emo_px=round(cap_px * 1.1), pad=10)}
{ZF.CSS.format(px=round(cap_px * 1.6))}
.bubble-pos, .symbol-pos {{ position:absolute; width:0; height:0; z-index:5; }}
.bubble {{ position:absolute; left:-{W * 0.17:.0f}px; top:-{H * 0.045:.0f}px; width:{W * 0.34:.0f}px; padding:{H * 0.012:.0f}px 0;
  background:#fff; border:6px solid #000; border-radius:50%; text-align:center; font-weight:900; font-size:{cap_px * 0.85:.0f}px; color:#000; }}
.symbol {{ position:absolute; left:-{W * 0.3:.0f}px; top:-{W * 0.06:.0f}px; width:{W * 0.6:.0f}px; text-align:center; white-space:nowrap; font-weight:900; font-size:{cap_px * 1.3:.0f}px; color:#fff;
  text-shadow:{shadow}; }}
"""
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width={W}, height={H}" />
<title>{esc(P.get('title', 'Zoomby video'))}</title>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>{css}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-fps="{fps}" data-duration="{D}">
{chr(10).join(body)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tl)}
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
    open(os.path.join(out_dir, "index.html"), "w", encoding="utf8").write(page)
    print(json.dumps({"index": os.path.join(out_dir, "index.html"), "duration": D, "fps": fps,
                      "shots": len(shots_all), "captions": len(chunk_words(words, cc, fps)),
                      "tweens": len(tl) - 1}, indent=1))


if __name__ == "__main__":
    main()
