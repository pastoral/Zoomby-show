"""Premium-route effects for build_project.py: animated cartoon eyes on still shots + foreground FX.

All GSAP lines are seek-safe (tl.set at the shot start + fromTo with immediateRender:false).

Shot keys (see ../references/premium.md):
  "eyes": {"pair": <one pair from eye_locate.py>, "looks": [{"at": 0.4, "dir": "l"|"r"|"c"|"up"|"down"}],
           "blink": true, "wide": [{"at": 1.2, "scale": 1.18}]}
  "fx":   [{"type": "flash", "at": 0.6}, {"type": "camera_flashes", "at": 0, "dur": 2, "n": 6},
           {"type": "shake", "at": 1.1, "dur": 0.25, "amt": 18}, {"type": "money_rain", "at": 0.4, "dur": 1.6, "dir": "down"|"up"},
           {"type": "zz", "at": 0.3, "x": 70, "y": 25}, {"type": "hearts", "at": 0.3, "x": 50, "y": 30},
           {"type": "question", "at": 0.3, "x": 70, "y": 25}, {"type": "ball_to_lens", "at": 0.2, "dur": 0.7},
           {"type": "number", "at": 0.2, "to": 23, "label": "GOALS", "sub": "IN ONE GAME, AGE 13", "x": 50, "y": 24}]
"""
import math, random

IR = "immediateRender:false"


def eyes(spec, sid, st, du, W, H):
    """SVG eye layer drawn over the shot's own cartoon eyes (inside the camera layer, so it moves with the plate)."""
    pair = spec["pair"]
    ink = pair.get("ink", "#1E1410")
    skin = pair.get("skin", "#9C6744")
    g, js = [], []
    eid = f"{sid}-eyes"
    for k, e in enumerate(pair["eyes"]):
        cx, cy = e["cx"] * W / 100, e["cy"] * H / 100
        rx, ry = e["rx"] * W / 100 * 1.12, e["ry"] * H / 100 * 1.14
        sw = max(2.0, min(rx, ry) * 0.16)
        pr = min(rx, ry) * 0.42
        g.append(f'<g id="{eid}-e{k}" style="transform-origin:{cx:.1f}px {cy:.1f}px">'
                 f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#FFFFFF" stroke="{ink}" stroke-width="{sw:.1f}"/>'
                 f'<circle class="pupil" cx="{cx:.1f}" cy="{cy:.1f}" r="{pr:.1f}" fill="{ink}"/>'
                 f'<g class="lid" opacity="0"><ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx + sw:.1f}" ry="{ry + sw:.1f}" fill="{skin}"/>'
                 f'<path d="M{cx - rx:.1f},{cy:.1f} Q{cx:.1f},{cy + ry * 0.55:.1f} {cx + rx:.1f},{cy:.1f}" fill="none" stroke="{ink}" stroke-width="{sw * 1.2:.1f}" stroke-linecap="round"/></g></g>')
    html = f'<svg id="{eid}" class="fxsvg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{"".join(g)}</svg>'
    rxp = pair["eyes"][0]["rx"] * W / 100
    ryp = pair["eyes"][0]["ry"] * H / 100
    off = {"c": (0, 0), "l": (-0.5 * rxp, 0), "r": (0.5 * rxp, 0), "up": (0, -0.45 * ryp), "down": (0, 0.4 * ryp),
           "ul": (-0.45 * rxp, -0.35 * ryp), "ur": (0.45 * rxp, -0.35 * ryp)}
    js.append(f'tl.set("#{eid} .pupil",{{x:0,y:0}},{st});tl.set("#{eid} .lid",{{opacity:0}},{st});tl.set("#{eid} g[id]",{{scale:1}},{st});')
    prev = (0, 0)
    for lk in spec.get("looks", []):
        o = off.get(lk.get("dir", "c"), (0, 0))
        t = st + lk["at"]
        js.append(f'tl.fromTo("#{eid} .pupil",{{x:{prev[0]:.1f},y:{prev[1]:.1f}}},{{x:{o[0]:.1f},y:{o[1]:.1f},duration:0.07,ease:"power2.out",{IR}}},{t:.3f});')
        prev = o
    if spec.get("blink", True):
        t = st + 0.7
        while t < st + du - 0.2:
            if not any(abs(t - (st + lk["at"])) < 0.15 for lk in spec.get("looks", [])):
                js.append(f'tl.set("#{eid} .lid",{{opacity:1}},{t:.3f});tl.set("#{eid} .lid",{{opacity:0}},{t + 0.09:.3f});')
            t += 2.3
    for wd in spec.get("wide", []):
        js.append(f'tl.fromTo("#{eid} g[id]",{{scale:1}},{{scale:{wd.get("scale", 1.18)},duration:0.12,ease:"back.out(3)",{IR}}},{st + wd["at"]:.3f});')
    return html, js


def _note(x, y, rot, s):
    return (f'<g transform="translate({x:.0f} {y:.0f}) rotate({rot:.0f}) scale({s:.2f})">'
            f'<rect x="-60" y="-28" width="120" height="56" rx="5" fill="#8FD18A" stroke="#2F6B34" stroke-width="4"/>'
            f'<rect x="-48" y="-18" width="96" height="36" rx="3" fill="none" stroke="#2F6B34" stroke-width="2.5"/>'
            f'<circle cx="0" cy="0" r="12" fill="#C8EBC2" stroke="#2F6B34" stroke-width="2.5"/></g>')


def fx(items, sid, st, du, W, H):
    """foreground FX above the camera layer; returns (html, js)"""
    html, js = [], []
    rnd = random.Random(hash(sid) & 0xFFFF)
    for n, f in enumerate(items or []):
        typ, at = f["type"], st + f.get("at", 0)
        fid = f"{sid}-fx{n}"
        d = f.get("dur", 0.6)
        if typ == "flash":
            html.append(f'<div id="{fid}" class="fxfull" style="background:#FFF;opacity:0"></div>')
            js.append(f'tl.set("#{fid}",{{opacity:0}},{st});tl.fromTo("#{fid}",{{opacity:0.9}},{{opacity:0,duration:{f.get("dur", 0.18)},ease:"power2.out",{IR}}},{at:.3f});')
        elif typ == "camera_flashes":
            k = f.get("n", 6)
            for i in range(k):
                x, y = rnd.uniform(5, 95), rnd.uniform(18, 60)
                sz = rnd.uniform(0.18, 0.32) * W
                t = at + i * d / k + rnd.uniform(0, d / k * 0.6)
                html.append(f'<div id="{fid}-{i}" class="fxabs" style="left:{x}%;top:{y}%;width:{sz:.0f}px;height:{sz:.0f}px;margin:-{sz / 2:.0f}px 0 0 -{sz / 2:.0f}px;'
                            f'background:radial-gradient(circle,rgba(255,255,255,1) 0%,rgba(255,255,255,.75) 18%,rgba(200,220,255,.25) 45%,rgba(255,255,255,0) 70%);opacity:0"></div>')
                js.append(f'tl.set("#{fid}-{i}",{{opacity:0}},{st});tl.fromTo("#{fid}-{i}",{{opacity:1,scale:0.6}},{{opacity:0,scale:1.15,duration:0.16,ease:"power1.out",{IR}}},{t:.3f});')
        elif typ == "shake":
            amt = f.get("amt", 18)
            reps = max(2, int(f.get("dur", 0.25) / 0.04))
            js.append(f'tl.fromTo("#{sid}-punch",{{x:{-amt},y:{amt * 0.6:.0f}}},{{x:{amt},y:{-amt * 0.6:.0f},duration:0.04,ease:"none",yoyo:true,repeat:{reps},{IR}}},{at:.3f});')
            js.append(f'tl.set("#{sid}-punch",{{x:0,y:0}},{at + 0.04 * (reps + 1) + 0.01:.3f});')
        elif typ == "money_rain":
            k = f.get("n", 16)
            up = f.get("dir", "down") == "up"
            notes = []
            for i in range(k):
                x = rnd.uniform(0.05, 0.95) * W
                notes.append((i, x, rnd.uniform(-40, 40), rnd.uniform(0.9, 1.6), rnd.uniform(0, d * 0.5)))
            for i, x, rot, s, delay in notes:
                y0, y1 = (H * 1.1, -H * 0.15) if up else (-H * 0.1, H * 1.1)
                html.append(f'<svg id="{fid}-{i}" class="fxsvg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" style="opacity:0">{_note(x, 0, rot, s)}</svg>')
                js.append(f'tl.set("#{fid}-{i}",{{opacity:0,y:{y0:.0f}}},{st});')
                js.append(f'tl.fromTo("#{fid}-{i}",{{opacity:1,y:{y0:.0f},rotation:0}},{{opacity:1,y:{y1:.0f},rotation:{rot * 2:.0f},duration:{d:.2f},ease:"none",{IR}}},{at + delay:.3f});')
        elif typ in ("zz", "hearts", "question"):
            txt = {"zz": "Zz", "hearts": "❤❤", "question": "?"}[typ]
            col = {"zz": "#FFFFFF", "hearts": "#FF3B5C", "question": "#FFFFFF"}[typ]
            html.append(f'<div id="{fid}" class="fxabs fxtxt" style="left:{f.get("x", 70)}%;top:{f.get("y", 25)}%;color:{col};opacity:0" data-layout-allow-occlusion>{txt}</div>')
            js.append(f'tl.set("#{fid}",{{opacity:0,scale:0}},{st});tl.fromTo("#{fid}",{{opacity:0,scale:0}},{{opacity:1,scale:1,duration:0.22,ease:"back.out(2.5)",{IR}}},{at:.3f});')
            js.append(f'tl.fromTo("#{fid}",{{y:0}},{{y:-20,duration:0.45,ease:"sine.inOut",yoyo:true,repeat:{max(1, int((du - f.get("at", 0)) / 0.45) - 1)},{IR}}},{at:.3f});')
        elif typ == "number":
            h_, j_ = number(f, fid, st, du, W, H)
            html.append(h_); js.extend(j_)
        elif typ == "ball_to_lens":
            html.append(f'<div id="{fid}" class="fxabs" style="left:50%;top:55%;width:{W * 0.25:.0f}px;height:{W * 0.25:.0f}px;margin:-{W * 0.125:.0f}px 0 0 -{W * 0.125:.0f}px;opacity:0">'
                        f'<svg viewBox="-50 -50 100 100" width="100%" height="100%"><circle r="46" fill="#FFF" stroke="#111" stroke-width="4"/>'
                        f'<path d="M0,-14 L13,-4 L8,12 L-8,12 L-13,-4Z" fill="#111"/></svg></div>')
            js.append(f'tl.set("#{fid}",{{opacity:0,scale:0.2}},{st});')
            js.append(f'tl.fromTo("#{fid}",{{opacity:1,scale:0.2,rotation:0,filter:"blur(0px)"}},{{opacity:1,scale:5,rotation:220,filter:"blur(6px)",duration:{d},ease:"power3.in",{IR}}},{at:.3f});')
            js.append(f'tl.set("#{fid}",{{opacity:0}},{at + d:.3f});')
    return "".join(html), js


def _stroke(px):
    """8-direction black outline + soft drop shadow, like the captions"""
    d = [(px, 0), (-px, 0), (0, px), (0, -px), (px * .7, px * .7), (-px * .7, px * .7), (px * .7, -px * .7), (-px * .7, -px * .7)]
    return ",".join(f"{x:.1f}px {y:.1f}px 0 #000" for x, y in d) + f",0 {px * 1.6:.0f}px {px * 2.5:.0f}px rgba(0,0,0,.55)"


def number(f, fid, st, du, W, H):
    """Big caption-style number that slams in, counts up, then punches (no card): premium number display.
    keys: to, from (0), prefix, suffix (inside the number, e.g. "$"/"M"), label (big word under it, e.g. "GOALS"),
          sub (small line above, e.g. "IN ONE GAME, AGE 13"), x, y (% centre), size (% of width for the digits, 20),
          color (#FFD60A), rot (-5), at, dur (count time, 0.9)"""
    v0, v1 = f.get("from", 0), f["to"]
    dec = 0 if float(v1).is_integer() else 1
    pre, suf = f.get("prefix", ""), f.get("suffix", "")
    col = f.get("color", "#FFD60A")
    fs = W * f.get("size", 20) / 100
    at = st + f.get("at", 0)
    d = f.get("dur", 0.9)
    rot = f.get("rot", -5)
    sub = f.get("sub")
    lab = f.get("label")

    def fmt(v):
        s = f"{v:,.{dec}f}"
        return f"{pre}{s}{suf}"
    burst = "".join(f'<path d="M0,0 L{math.cos(math.radians(a - 6)) * 100:.1f},{math.sin(math.radians(a - 6)) * 100:.1f} '
                    f'L{math.cos(math.radians(a + 6)) * 100:.1f},{math.sin(math.radians(a + 6)) * 100:.1f}Z" fill="{col}"/>' for a in range(0, 360, 30))
    html = (f'<div id="{fid}" class="fxabs fxnum" style="left:{f.get("x", 50)}%;top:{f.get("y", 24)}%;opacity:0" data-layout-allow-occlusion>'
            f'<svg id="{fid}-burst" class="fxburst" viewBox="-100 -100 200 200" style="width:{fs * 3.2:.0f}px;height:{fs * 3.2:.0f}px;'
            f'margin:-{fs * 1.6:.0f}px 0 0 -{fs * 1.6:.0f}px;opacity:0">{burst}</svg>'
            f'<div class="fxnum-in" style="transform:rotate({rot}deg)">'
            + (f'<div class="fxnum-sub" style="font-size:{fs * 0.22:.0f}px;text-shadow:{_stroke(fs * 0.03)}">{sub}</div>' if sub else "")
            + f'<div id="{fid}-n" class="fxnum-n" style="font-size:{fs:.0f}px;color:{col};text-shadow:{_stroke(fs * 0.06)}">{fmt(v0)}</div>'
            + (f'<div class="fxnum-lab" style="font-size:{fs * 0.42:.0f}px;text-shadow:{_stroke(fs * 0.04)}">{lab}</div>' if lab else "")
            + "</div></div>")
    js = [f'tl.set("#{fid}",{{opacity:0,scale:0.2}},{st});tl.set("#{fid}-burst",{{opacity:0,scale:0.3,rotation:0}},{st});',
          f'tl.fromTo("#{fid}",{{opacity:1,scale:2.2}},{{opacity:1,scale:1,duration:0.18,ease:"power3.in",{IR}}},{at:.3f});',
          f'(function(){{const o={{v:{v0}}};const el=document.getElementById("{fid}-n");'
          f'tl.fromTo(o,{{v:{v0}}},{{v:{v1},duration:{d},ease:"power2.out",{IR},onUpdate:()=>{{el.textContent="{pre}"+'
          f'o.v.toLocaleString("en-US",{{minimumFractionDigits:{dec},maximumFractionDigits:{dec}}})+"{suf}";}}}},{at + 0.1:.3f});}})();',
          f'tl.fromTo("#{fid}",{{scale:1}},{{scale:1.22,duration:0.09,ease:"power2.out",yoyo:true,repeat:1,{IR}}},{at + 0.1 + d:.3f});',
          f'tl.fromTo("#{fid}-burst",{{opacity:0.95,scale:0.4,rotation:0}},{{opacity:0,scale:1.5,rotation:25,duration:0.45,ease:"power2.out",{IR}}},{at + 0.1 + d:.3f});',
          f'tl.fromTo("#{fid}",{{y:0}},{{y:-12,duration:0.5,ease:"sine.inOut",yoyo:true,repeat:{max(1, int((du - f.get("at", 0) - d) / 0.5))},{IR}}},{at + 0.3 + d:.3f});']
    return html, js


CSS = """
.fxnum {{ width:0; height:0; z-index:6; }}
.fxnum-in {{ position:absolute; left:0; top:0; transform-origin:0 0; }}
.fxnum-in > div {{ position:absolute; left:0; transform:translateX(-50%); white-space:nowrap; text-align:center; font-family:"Montserrat",sans-serif; font-weight:900; line-height:1; }}
.fxnum-n {{ top:0; transform:translate(-50%,-50%) !important; letter-spacing:-0.02em; }}
.fxnum-sub {{ bottom:0; color:#FFFFFF; transform:translate(-50%,-260%) !important; letter-spacing:0.02em; }}
.fxnum-lab {{ top:0; color:#FFFFFF; transform:translate(-50%,90%) !important; }}
.fxburst {{ position:absolute; left:0; top:0; }}
.fxsvg {{ position:absolute; left:0; top:0; pointer-events:none; overflow:visible; }}
.fxfull {{ position:absolute; inset:0; pointer-events:none; }}
.fxabs {{ position:absolute; pointer-events:none; }}
.fxtxt {{ font-weight:900; font-size:{px}px; line-height:1; transform-origin:50% 50%; text-shadow:6px 0 0 #000,-6px 0 0 #000,0 6px 0 #000,0 -6px 0 #000; }}
"""
