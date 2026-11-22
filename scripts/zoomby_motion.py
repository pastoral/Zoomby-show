"""Character acting, lip sync, hands, emotions and animated charts for build_project.py.

Everything here returns HTML strings and GSAP timeline lines (strings). All tweens are seek-safe:
explicit fromTo values with immediateRender:false, and a reset tl.set at the start of each shot.
See ../references/build.md (Character acting, Charts) for the JSON keys.
"""
import html, math

IR = "immediateRender:false"

# emotion -> (head key in the rig, automatic body acting, symbol next to the head)
EMOTIONS = {
    "neutral":   ("neutral",   [],                                         None),
    "talk":      ("neutral",   [],                                         None),
    "happy":     ("happy",     [{"type": "celebrate", "at": 0.1}],         "✨"),
    "laugh":     ("laugh",     [{"type": "bounce", "at": 0.1}],            "😂"),
    "smug":      ("smug",      [{"type": "tilt", "at": 0.2, "amt": 8}],    None),
    "sad":       ("sad",       [{"type": "slump", "at": 0.1}],             "💧"),
    "angry":     ("angry",     [{"type": "stomp", "at": 0.1}],             "💢"),
    "surprised": ("surprised", [{"type": "jolt", "at": 0.1}],              "❗"),
    "shock":     ("shock",     [{"type": "jolt", "at": 0.1}],              "❗"),
    "scared":    ("scared",    [{"type": "step_back", "at": 0.05}, {"type": "tremble", "at": 0.3}], "💦"),
    "confused":  ("confused",  [{"type": "tilt", "at": 0.2, "amt": 12}],   "❓"),
    "love":      ("love",      [{"type": "bounce", "at": 0.1, "amt": 0.008}], "❤️"),
}
# when the rig lacks a head for an emotion, fall back along this chain
FALLBACK = {"happy": "laugh", "laugh": "happy", "smug": "neutral", "sad": "neutral", "angry": "shock",
            "surprised": "shock", "shock": "surprised", "scared": "shock", "confused": "neutral", "love": "happy"}


def esc(s):
    return html.escape(str(s), quote=True)


def resolve_rig(ch, P):
    """ch may say {"rig": "tux", "emotion": "sad"} instead of explicit src/head/mouth paths.
    P["rigs"][name] = {"body": path, "neck": [x%, y%], "heads": {emotion: path}, "mouth_half": path, "mouth_open": path}"""
    ch = dict(ch)
    rig = (P.get("rigs") or {}).get(ch.get("rig"))
    emo = ch.get("emotion")
    if rig:
        ch.setdefault("src", rig["body"])
        ch.setdefault("neck", rig.get("neck", [50, 28]))
        heads = rig.get("heads", {})
        key = EMOTIONS.get(emo or "neutral", ("neutral",))[0]
        tried = set()
        while key not in heads and key not in tried and key in FALLBACK:
            tried.add(key); key = FALLBACK[key]
        ch.setdefault("head", heads.get(key) or heads.get("neutral"))
        talking = ch.get("talk", emo in (None, "neutral", "talk", "smug", "happy"))
        if talking and key in ("neutral", "smug") and rig.get("mouth_half"):
            ch.setdefault("mouth", rig.get("mouth_open") or rig["mouth_half"])
            ch.setdefault("mouth_half", rig["mouth_half"])
    if emo in EMOTIONS and ch.get("auto_act", True):
        auto = [dict(m) for m in EMOTIONS[emo][1]]
        ch["moves"] = auto + list(ch.get("moves", []))
        if EMOTIONS[emo][2] and ch.get("emotion_symbol", True) and "symbol" not in ch:
            ch["symbol"] = EMOTIONS[emo][2]
    return ch


def char_inner_html(ch, cid):
    """body + optional head layer (with mouths) + optional hand layers, inside the flip wrapper"""
    mouth = ""
    if ch.get("mouth"):
        mouth += f'<img id="{cid}-open" class="char-img char-open" src="{esc(ch["mouth"])}" alt="" />'
    if ch.get("mouth") and ch.get("mouth_half"):
        mouth += f'<img id="{cid}-half" class="char-img char-open" src="{esc(ch["mouth_half"])}" alt="" />'
    inner = f'<img class="char-img" src="{esc(ch["src"])}" alt="" />'
    if ch.get("head"):
        nx, ny = ch.get("neck", [50, 28])
        inner += (f'<div id="{cid}-head" class="layer" style="transform-origin:{nx}% {ny}%">'
                  f'<img class="char-img" src="{esc(ch["head"])}" alt="" />{mouth}</div>')
    else:
        inner += mouth
    for k, hd in enumerate(ch.get("hands", [])):
        hflip = "scaleX(-1)" if hd.get("flip") else "none"
        inner += (f'<div id="{cid}-h{k}" class="hand" style="left:{hd.get("x", 70)}%;top:{hd.get("y", 45)}%;'
                  f'height:{hd.get("h", 16)}%;transform-origin:{hd.get("pivot", "50% 90%")};opacity:0">'
                  f'<img src="{esc(hd["src"])}" alt="" style="height:100%;transform:{hflip}" /></div>')
    return inner


def lips_js(ch, cid, st, du, words, cfg, f1):
    """Lip movement only where the character is speaking (shot "speaking": true, or "talk": true).
    lip "minimal" (default): one small half-open per word (>= 0.16 s), closed between words.
    lip "full": closed>half>open>half cycle. lip "none": the mouth stays as drawn."""
    mode = ch.get("lip", cfg["character"].get("lip", "minimal"))
    if mode == "none" or not (ch.get("mouth") and ch.get("talk", True)):
        return []
    out, half = [], bool(ch.get("mouth_half"))

    def put(state, t):
        out.append(f'tl.set("#{cid}-open",{{opacity:{1 if state == "open" else 0}}},{t:.3f});')
        if half:
            out.append(f'tl.set("#{cid}-half",{{opacity:{1 if state == "half" else 0}}},{t:.3f});')

    end = st + du - f1
    for w in words:
        if not (st <= w["s"] < st + du):
            continue
        wd = w["e"] - w["s"]
        if mode == "minimal":
            if wd < 0.16:
                continue
            put("half" if half else "open", w["s"])
            put("closed", min(w["s"] + max(0.1, wd * 0.55), end))
        else:
            seq = ["half", "open", "half", "closed"] if half else ["open", "closed"]
            t, k = w["s"], 0
            while t < min(w["e"], end):
                put(seq[k % len(seq)], t); t += cfg["character"]["mouth_s"]; k += 1
            put("closed", min(w["e"], end))
    return out


def _move(typ, mv, fx, hd, cidsel, t, W, H, has_head):
    amt, d = mv.get("amt"), mv.get("dur")
    J = []
    a_ = J.append
    if typ == "hop":
        hh = round(H * (amt or 0.05))
        a_(f'tl.fromTo("{fx}",{{y:-{hh},scaleY:1.06,scaleX:0.95}},{{y:0,scaleY:1,scaleX:1,duration:0.2,ease:"power2.in",{IR}}},{t});')
        a_(f'tl.fromTo("{fx}",{{scaleY:1,scaleX:1}},{{scaleY:0.9,scaleX:1.08,duration:0.07,ease:"power1.out",{IR}}},{t + 0.2:.3f});')
        a_(f'tl.fromTo("{fx}",{{scaleY:0.9,scaleX:1.08}},{{scaleY:1,scaleX:1,duration:0.22,ease:"back.out(3)",{IR}}},{t + 0.27:.3f});')
    elif typ in ("slide_l", "slide_r"):
        x0 = round(W * 0.7) * (-1 if typ == "slide_l" else 1)
        a_(f'tl.fromTo("{fx}",{{x:{x0},rotation:{-8 if x0 < 0 else 8}}},{{x:0,rotation:0,duration:0.32,ease:"back.out(1.5)",{IR}}},{t});')
    elif typ == "pop":
        a_(f'tl.fromTo("{fx}",{{scaleX:0.2,scaleY:0.2}},{{scaleX:1,scaleY:1,duration:0.3,ease:"back.out(2.2)",{IR}}},{t});')
    elif typ in ("walk", "run", "walk_out", "run_out"):
        # amt = travel in % of frame width (sign = direction it comes from / goes to); steps bob and rock
        run = typ.startswith("run")
        dist = round(W * (amt if amt is not None else (-60 if not typ.endswith("out") else 60)) / 100)
        d = d or (0.9 if run else 1.6)
        step = 0.17 if run else 0.3
        x_from, x_to = (dist, 0) if not typ.endswith("out") else (0, dist)
        lean = (6 if run else 2) * (1 if x_to - x_from > 0 else -1)
        reps = max(1, int(d / step) - 1)
        a_(f'tl.fromTo("{fx}",{{x:{x_from}}},{{x:{x_to},duration:{d},ease:"none",{IR}}},{t});')
        a_(f'tl.fromTo("{fx}",{{y:0}},{{y:-{round(H * (0.016 if run else 0.009))},duration:{step / 2:.3f},ease:"sine.out",yoyo:true,repeat:{reps * 2 + 1},{IR}}},{t});')
        a_(f'tl.fromTo("{fx}",{{rotation:{lean - 3}}},{{rotation:{lean + 3},duration:{step:.3f},ease:"sine.inOut",yoyo:true,repeat:{reps},{IR}}},{t});')
        a_(f'tl.fromTo("{fx}",{{rotation:{lean}}},{{rotation:0,duration:0.15,ease:"power2.out",{IR}}},{t + d:.3f});')
        a_(f'tl.set("{fx}",{{y:0}},{t + d:.3f});')
    elif typ == "lean":
        a, d = amt or 7, d or 0.9
        sc = round(1 + abs(a) / 150, 3)
        a_(f'tl.fromTo("{fx}",{{rotation:0,scaleX:1,scaleY:1}},{{rotation:{a},scaleX:{sc},scaleY:{sc},duration:0.18,ease:"power2.out",{IR}}},{t});')
        a_(f'tl.fromTo("{fx}",{{rotation:{a},scaleX:{sc},scaleY:{sc}}},{{rotation:0,scaleX:1,scaleY:1,duration:0.3,ease:"power2.inOut",{IR}}},{t + d:.3f});')
    elif typ == "jolt":
        j = round(H * 0.025)
        a_(f'tl.fromTo("{fx}",{{y:0,scaleX:1,scaleY:1}},{{y:-{j},scaleX:1.07,scaleY:1.1,duration:0.07,ease:"power2.out",{IR}}},{t});')
        a_(f'tl.fromTo("{fx}",{{y:-{j},scaleX:1.07,scaleY:1.1}},{{y:0,scaleX:1,scaleY:1,duration:0.45,ease:"elastic.out(1,0.35)",{IR}}},{t + 0.07:.3f});')
    elif typ in ("shake", "tremble"):
        a, d = amt or (14 if typ == "shake" else 5), d or (0.4 if typ == "shake" else 1.2)
        per = 0.05 if typ == "shake" else 0.035
        reps = max(1, int(d / per))
        a_(f'tl.fromTo("{fx}",{{x:-{a}}},{{x:{a},duration:{per},ease:"none",yoyo:true,repeat:{reps},{IR}}},{t});')
        a_(f'tl.set("{fx}",{{x:0}},{t + (reps + 1) * per:.3f});')
    elif typ == "bounce":
        a, d = amt or 0.012, d or 1.0
        reps = max(1, int(d / 0.15))
        a_(f'tl.fromTo("{fx}",{{y:0}},{{y:-{round(H * a)},duration:0.15,ease:"sine.out",yoyo:true,repeat:{reps},{IR}}},{t});')
    elif typ == "celebrate":  # happy: two quick hops with a wiggle
        for k in range(2):
            tk = t + k * 0.32
            a_(f'tl.fromTo("{fx}",{{y:0,rotation:0}},{{y:-{round(H * 0.03)},rotation:{4 if k else -4},duration:0.14,ease:"power2.out",{IR}}},{tk:.3f});')
            a_(f'tl.fromTo("{fx}",{{y:-{round(H * 0.03)},rotation:{4 if k else -4}}},{{y:0,rotation:0,duration:0.16,ease:"power2.in",{IR}}},{tk + 0.14:.3f});')
    elif typ == "slump":  # sad: sink, droop, head down
        d = d or 1.4
        a_(f'tl.fromTo("{fx}",{{y:0,scaleY:1,rotation:0}},{{y:{round(H * 0.012)},scaleY:0.95,rotation:2,duration:0.5,ease:"power2.out",{IR}}},{t});')
        a_(f'tl.fromTo("{fx}",{{y:{round(H * 0.012)},scaleY:0.95,rotation:2}},{{y:0,scaleY:1,rotation:0,duration:0.4,ease:"power2.inOut",{IR}}},{t + d:.3f});')
        if has_head:
            a_(f'tl.fromTo("{hd}",{{rotation:0,y:0}},{{rotation:9,y:{round(H * 0.006)},duration:0.5,ease:"power2.out",{IR}}},{t});')
            a_(f'tl.fromTo("{hd}",{{rotation:9,y:{round(H * 0.006)}}},{{rotation:0,y:0,duration:0.4,ease:"power2.inOut",{IR}}},{t + d:.3f});')
    elif typ == "stomp":  # angry: hop, shake, red glow
        d = d or 1.2
        a_(f'tl.fromTo("{fx}",{{y:-{round(H * 0.02)}}},{{y:0,duration:0.12,ease:"power3.in",{IR}}},{t});')
        reps = max(1, int(0.5 / 0.04))
        a_(f'tl.fromTo("{fx}",{{x:-9}},{{x:9,duration:0.04,ease:"none",yoyo:true,repeat:{reps},{IR}}},{t + 0.12:.3f});')
        a_(f'tl.set("{fx}",{{x:0}},{t + 0.12 + (reps + 1) * 0.04:.3f});')
        a_(f'tl.fromTo("{cidsel}",{{filter:"drop-shadow(0 0 0px rgba(255,40,40,0))"}},{{filter:"drop-shadow(0 0 26px rgba(255,40,40,0.95))",duration:0.15,yoyo:true,repeat:{max(1, int(d / 0.15))},{IR}}},{t});')
        a_(f'tl.set("{cidsel}",{{filter:"none"}},{t + (max(1, int(d / 0.15)) + 1) * 0.15:.3f});')
    elif typ == "step_back":  # scared/surprised: quick hop backwards
        dist = round(W * (amt or 6) / 100)
        a_(f'tl.fromTo("{fx}",{{x:0,rotation:0}},{{x:{dist},rotation:-6,duration:0.16,ease:"power3.out",{IR}}},{t});')
        a_(f'tl.fromTo("{fx}",{{x:{dist},rotation:-6}},{{x:{dist},rotation:0,duration:0.3,ease:"power2.out",{IR}}},{t + 0.16:.3f});')
    elif typ == "shrug":
        a_(f'tl.fromTo("{fx}",{{y:0,scaleY:1}},{{y:-{round(H * 0.008)},scaleY:1.03,duration:0.16,ease:"power2.out",yoyo:true,repeat:1,{IR}}},{t});')
        if has_head:
            a_(f'tl.fromTo("{hd}",{{rotation:0}},{{rotation:10,duration:0.2,ease:"power2.out",yoyo:true,repeat:1,repeatDelay:0.3,{IR}}},{t});')
    elif typ == "turn":  # flip to face the other way for the rest of the shot
        a_(f'tl.fromTo("{fx}",{{scaleX:1}},{{scaleX:-1,duration:0.18,ease:"power2.inOut",{IR}}},{t});')
    elif typ == "spin":
        a_(f'tl.fromTo("{fx}",{{rotation:0}},{{rotation:360,duration:{d or 0.5},ease:"power2.inOut",{IR}}},{t});')
    elif typ == "wobble":
        a, d = amt or 3, d or 2.0
        reps = max(1, int(d / 0.3))
        a_(f'tl.fromTo("{fx}",{{rotation:-{a}}},{{rotation:{a},duration:0.3,ease:"sine.inOut",yoyo:true,repeat:{reps},{IR}}},{t});')
    elif typ == "tilt" and has_head:
        a, d = amt or 10, d or 0.8
        a_(f'tl.fromTo("{hd}",{{rotation:0}},{{rotation:{a},duration:0.15,ease:"back.out(2)",{IR}}},{t});')
        a_(f'tl.fromTo("{hd}",{{rotation:{a}}},{{rotation:0,duration:0.25,ease:"power2.inOut",{IR}}},{t + d:.3f});')
    elif typ == "nod" and has_head:
        for k in range(mv.get("times", 2)):
            tk = t + k * 0.28
            a_(f'tl.fromTo("{hd}",{{y:0}},{{y:{round(H * 0.006)},duration:0.12,ease:"power1.out",yoyo:true,repeat:1,{IR}}},{tk:.3f});')
    return J


HEAD_MOVES = ("tilt", "nod", "slump", "shrug")


def acting_js(ch, cid, st, du, W, H, words):
    """idle sway/breathing, automatic head nods on words, keyframed moves, hand gestures"""
    fx, hd, idle, cs = f"#{cid}-fx", f"#{cid}-head", f"#{cid}-idle", f"#{cid}"
    J = [f'tl.set("{fx}",{{x:0,y:0,rotation:0,scaleX:1,scaleY:1}},{st});']
    has_head = bool(ch.get("head"))
    if ch.get("idle", True):
        sw = ch.get("sway", 1.6)
        J.append(f'tl.fromTo("{idle}",{{rotation:{-sw}}},{{rotation:{sw},duration:0.85,ease:"sine.inOut",yoyo:true,repeat:{max(1, int(du / 0.85))},{IR}}},{st});')
        J.append(f'tl.fromTo("{idle}",{{scaleY:1}},{{scaleY:1.014,duration:0.6,ease:"sine.inOut",yoyo:true,repeat:{max(1, int(du / 0.6))},{IR}}},{st});')
    moves = ch.get("moves", [])
    if has_head:
        J.append(f'tl.set("{hd}",{{rotation:0,y:0}},{st});')
    if has_head and ch.get("nod", True):
        amp = ch.get("nod_amp", 4)
        busy = [(st + m.get("at", 0) - 0.15, st + m.get("at", 0) + m.get("dur", 1.4) + 0.4) for m in moves if m["type"] in HEAD_MOVES]
        angles, prev, k = [-1, 0.8, -0.5, 1, -0.8, 0.4], 0.0, 0
        for w in words:
            if not (st <= w["s"] < st + du - 0.12) or (w["e"] - w["s"]) < 0.12 or any(a0 <= w["s"] <= a1 for a0, a1 in busy):
                continue
            a = round(angles[k % len(angles)] * amp, 2); k += 1
            J.append(f'tl.fromTo("{hd}",{{rotation:{prev}}},{{rotation:{a},duration:0.14,ease:"power1.out",{IR}}},{w["s"]:.3f});')
            prev = a
    for mv in moves:
        J += _move(mv["type"], mv, fx, hd, cs, round(st + mv.get("at", 0), 3), W, H, has_head)
    # hand gestures (hand PNG layers inside the body, so they follow every body move)
    for k, h in enumerate(ch.get("hands", [])):
        sel = f"#{cid}-h{k}"
        t = round(st + h.get("at", 0.2), 3)
        d = h.get("dur", max(0.6, du - h.get("at", 0.2) - 0.1))
        J.append(f'tl.set("{sel}",{{opacity:0,rotation:0,scale:1,x:0,y:0}},{st});')
        J.append(f'tl.fromTo("{sel}",{{opacity:0,scale:0.3}},{{opacity:1,scale:1,duration:0.2,ease:"back.out(2.5)",{IR}}},{t});')
        anim = h.get("anim", "wave")
        if anim == "wave":
            J.append(f'tl.fromTo("{sel}",{{rotation:-18}},{{rotation:18,duration:0.18,ease:"sine.inOut",yoyo:true,repeat:{max(1, int((d - 0.2) / 0.18))},{IR}}},{t + 0.2:.3f});')
        elif anim == "point":
            J.append(f'tl.fromTo("{sel}",{{scale:1}},{{scale:1.18,duration:0.12,ease:"power2.out",yoyo:true,repeat:3,{IR}}},{t + 0.2:.3f});')
        elif anim == "thumbs":
            J.append(f'tl.fromTo("{sel}",{{y:0,rotation:-6}},{{y:-14,rotation:6,duration:0.25,ease:"sine.inOut",yoyo:true,repeat:{max(1, int((d - 0.2) / 0.25))},{IR}}},{t + 0.2:.3f});')
        elif anim == "fist_pump":
            J.append(f'tl.fromTo("{sel}",{{y:0}},{{y:-40,duration:0.14,ease:"power2.out",yoyo:true,repeat:{max(1, int((d - 0.2) / 0.14))},{IR}}},{t + 0.2:.3f});')
        elif anim == "shake_fist":
            J.append(f'tl.fromTo("{sel}",{{rotation:-12,x:-6}},{{rotation:12,x:6,duration:0.07,ease:"none",yoyo:true,repeat:{max(1, int((d - 0.2) / 0.07))},{IR}}},{t + 0.2:.3f});')
        elif anim == "count":  # bob on each beat, for counting/listing
            J.append(f'tl.fromTo("{sel}",{{y:0}},{{y:-18,duration:0.2,ease:"power2.out",yoyo:true,repeat:{max(1, int((d - 0.2) / 0.2))},{IR}}},{t + 0.2:.3f});')
        J.append(f'tl.fromTo("{sel}",{{opacity:1}},{{opacity:0,duration:0.12,{IR}}},{min(st + du - 0.12, t + d):.3f});')
    return J


def emotion_symbol(ch, cid, left, top, wpx, hpx, st, du):
    """small symbol (💧 💢 ❗ ✨ …) popping next to the head; returns (html, js)"""
    sym = ch.get("symbol")
    if not sym:
        return "", []
    nx, ny = ch.get("neck", [50, 28])
    x = left + wpx * min(0.95, nx / 100 + 0.32)
    y = top + hpx * max(0.02, ny / 100 - 0.24)
    sid = f"{cid}-emo"
    h = (f'<div id="{sid}" class="emo-pos" style="left:{x:.0f}px;top:{y:.0f}px"><div id="{sid}-in" class="emo" '
         f'data-layout-allow-occlusion>{esc(sym)}</div></div>')
    at = st + 0.15
    js = [f'tl.fromTo("#{sid}-in",{{scale:0,opacity:0}},{{scale:1,opacity:1,duration:0.22,ease:"back.out(2.6)"}},{at:.3f});',
          f'tl.fromTo("#{sid}",{{y:0}},{{y:-12,duration:0.35,ease:"sine.inOut",yoyo:true,repeat:{max(1, int((du - 0.15) / 0.35) - 1)},{IR}}},{at:.3f});']
    return h, js


# ------------------------------------------------------------------ charts ------------------------------------------------------------------
PALETTE = ["#FFD60A", "#3DDC84", "#4EA8FF", "#FF5A5F", "#B388FF", "#FF9F1C"]


def _fmt(v, prefix="", suffix=""):
    if isinstance(v, (int, float)) and abs(v) >= 1000 and float(v).is_integer():
        s = f"{int(v):,}"
    elif isinstance(v, float) and not v.is_integer():
        s = f"{v:.1f}"
    else:
        s = str(int(v)) if isinstance(v, (int, float)) else str(v)
    return f"{prefix}{s}{suffix}"


def chart(cfgc, sid, st, du, W, H):
    """Animated chart card. cfgc: {type: bar|line|counter|pie|compare, x,y,w,h (% of frame, centre x/y), at, title,
    data: [numbers], labels: [str], prefix, suffix, from, to, color}. Returns (html, js)."""
    typ = cfgc.get("type", "bar")
    cx, cy = cfgc.get("x", 50), cfgc.get("y", 30)
    w, h = W * cfgc.get("w", 78) / 100, H * cfgc.get("h", 24) / 100
    left, top = W * cx / 100 - w / 2, H * cy / 100 - h / 2
    cid = f"{sid}-chart"
    at = round(st + cfgc.get("at", 0.3), 3)
    pre, suf = cfgc.get("prefix", ""), cfgc.get("suffix", "")
    col = cfgc.get("color", PALETTE[0])
    title = cfgc.get("title", "")
    pad = w * 0.06
    th = h * 0.2 if title else 0
    iw, ih = w - 2 * pad, h - 2 * pad - th
    inner, js = "", []
    js.append(f'tl.fromTo("#{cid}",{{scale:0.4,opacity:0,rotation:-4}},{{scale:1,opacity:1,rotation:0,duration:0.32,ease:"back.out(2)"}},{at});')
    t0 = at + 0.25
    if typ in ("bar", "compare"):
        data = cfgc.get("data", [1]); labels = cfgc.get("labels", [""] * len(data))
        n = len(data); mx = max(data) or 1
        gap = iw * 0.08; bw = (iw - gap * (n - 1)) / n
        lab_h = ih * 0.18
        for k, v in enumerate(data):
            bh = (ih - lab_h * 2) * (v / mx)
            x = pad + k * (bw + gap)
            c = cfgc.get("colors", PALETTE)[k % len(PALETTE)] if typ == "compare" or n > 1 else col
            inner += (f'<div id="{cid}-b{k}" class="ch-bar" style="left:{x:.0f}px;top:{pad + th + ih - lab_h - bh:.0f}px;width:{bw:.0f}px;height:{bh:.0f}px;background:{c}"></div>'
                      f'<div id="{cid}-v{k}" class="ch-val" style="left:{x - 20:.0f}px;width:{bw + 40:.0f}px;top:{pad + th + ih - lab_h - bh - lab_h:.0f}px;font-size:{lab_h * 0.8:.0f}px">{esc(_fmt(v, pre, suf))}</div>'
                      f'<div class="ch-lab" style="left:{x - 20:.0f}px;width:{bw + 40:.0f}px;top:{pad + th + ih - lab_h + 6:.0f}px;font-size:{lab_h * 0.7:.0f}px">{esc(labels[k] if k < len(labels) else "")}</div>')
            js.append(f'tl.fromTo("#{cid}-b{k}",{{scaleY:0}},{{scaleY:1,duration:0.5,ease:"back.out(1.6)",{IR}}},{t0 + k * 0.18:.3f});')
            js.append(f'tl.fromTo("#{cid}-v{k}",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.2,ease:"power2.out",{IR}}},{t0 + k * 0.18 + 0.35:.3f});')
    elif typ == "line":
        data = cfgc.get("data", [1, 2]); n = len(data); mn, mx = min(data), max(data)
        rng = (mx - mn) or 1
        pts = [(pad + iw * k / (n - 1), pad + th + ih * 0.9 - ih * 0.8 * (v - mn) / rng) for k, v in enumerate(data)]
        L = sum(math.dist(pts[k], pts[k + 1]) for k in range(n - 1))
        pstr = " ".join(f"{x:.0f},{y:.0f}" for x, y in pts)
        ex, ey = pts[-1]
        inner += (f'<svg class="ch-svg" width="{w:.0f}" height="{h:.0f}" viewBox="0 0 {w:.0f} {h:.0f}">'
                  f'<polyline points="{pts[0][0]:.0f},{pad + th + ih:.0f} {pstr} {ex:.0f},{pad + th + ih:.0f}" fill="{col}" opacity="0.18" />'
                  f'<polyline id="{cid}-ln" points="{pstr}" fill="none" stroke="#000" stroke-width="22" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="{L:.0f}" stroke-dashoffset="{L:.0f}" />'
                  f'<polyline id="{cid}-lc" points="{pstr}" fill="none" stroke="{col}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="{L:.0f}" stroke-dashoffset="{L:.0f}" />'
                  f'</svg><div id="{cid}-dot" class="ch-dot" style="left:{ex - 22:.0f}px;top:{ey - 22:.0f}px;background:{col}"></div>'
                  f'<div id="{cid}-end" class="ch-val" style="left:{ex - 180:.0f}px;width:200px;top:{ey - 90:.0f}px;font-size:{h * 0.16:.0f}px;text-align:right">{esc(_fmt(data[-1], pre, suf) if cfgc.get("end_label", True) else "")}</div>')
        for sel in ("ln", "lc"):
            js.append(f'tl.fromTo("#{cid}-{sel}",{{strokeDashoffset:{L:.0f}}},{{strokeDashoffset:0,duration:0.9,ease:"power2.inOut",{IR}}},{t0:.3f});')
        js.append(f'tl.fromTo("#{cid}-dot",{{scale:0}},{{scale:1,duration:0.25,ease:"back.out(3)",{IR}}},{t0 + 0.85:.3f});')
        js.append(f'tl.fromTo("#{cid}-end",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.2,{IR}}},{t0 + 0.9:.3f});')
    elif typ == "counter":
        v0, v1 = cfgc.get("from", 0), cfgc.get("to", 100)
        dec = 0 if float(v1).is_integer() else 1
        inner += (f'<div id="{cid}-num" class="ch-num" style="top:{pad + th:.0f}px;height:{ih:.0f}px;line-height:{ih:.0f}px;font-size:{min(ih * 0.8, iw / max(4, len(_fmt(v1, pre, suf))) * 1.3):.0f}px;color:{col}">{esc(_fmt(v0, pre, suf))}</div>')
        js.append(f'(function(){{const o={{v:{v0}}};const el=document.getElementById("{cid}-num");'
                  f'tl.fromTo(o,{{v:{v0}}},{{v:{v1},duration:{cfgc.get("dur", 1.1)},ease:"power2.out",{IR},onUpdate:()=>{{el.textContent="{esc(pre)}"+'
                  f'o.v.toLocaleString("en-US",{{minimumFractionDigits:{dec},maximumFractionDigits:{dec}}})+"{esc(suf)}";}}}},{t0:.3f});}})();')
        js.append(f'tl.fromTo("#{cid}-num",{{scale:1}},{{scale:1.12,duration:0.12,yoyo:true,repeat:1,ease:"power2.out",{IR}}},{t0 + cfgc.get("dur", 1.1):.3f});')
    elif typ == "pie":
        pct = cfgc.get("to", 50)
        r = min(iw, ih) * 0.38; C = 2 * math.pi * r
        pcx, pcy = w / 2, pad + th + ih / 2
        inner += (f'<svg class="ch-svg" width="{w:.0f}" height="{h:.0f}" viewBox="0 0 {w:.0f} {h:.0f}">'
                  f'<circle cx="{pcx:.0f}" cy="{pcy:.0f}" r="{r:.0f}" fill="#EEE" stroke="#000" stroke-width="10" />'
                  f'<circle id="{cid}-arc" cx="{pcx:.0f}" cy="{pcy:.0f}" r="{r / 2:.0f}" fill="none" stroke="{col}" stroke-width="{r:.0f}" '
                  f'stroke-dasharray="{C / 2:.1f}" stroke-dashoffset="{C / 2:.1f}" transform="rotate(-90 {pcx:.0f} {pcy:.0f})" />'
                  f'<circle cx="{pcx:.0f}" cy="{pcy:.0f}" r="{r:.0f}" fill="none" stroke="#000" stroke-width="10" /></svg>'
                  f'<div id="{cid}-pct" class="ch-val" style="left:0;width:{w:.0f}px;top:{pcy - r * 0.35:.0f}px;font-size:{r * 0.6:.0f}px">{esc(_fmt(pct, pre, suf or "%"))}</div>')
        js.append(f'tl.fromTo("#{cid}-arc",{{strokeDashoffset:{C / 2:.1f}}},{{strokeDashoffset:{C / 2 * (1 - pct / 100):.1f},duration:0.8,ease:"power2.out",{IR}}},{t0:.3f});')
        js.append(f'tl.fromTo("#{cid}-pct",{{opacity:0,scale:0.5}},{{opacity:1,scale:1,duration:0.25,ease:"back.out(2)",{IR}}},{t0 + 0.6:.3f});')
    html_ = (f'<div id="{cid}" class="ch-card" data-layout-allow-occlusion style="left:{left:.0f}px;top:{top:.0f}px;width:{w:.0f}px;height:{h:.0f}px">'
             + (f'<div class="ch-title" style="height:{th:.0f}px;line-height:{th:.0f}px;font-size:{th * 0.62:.0f}px">{esc(title)}</div>' if title else "")
             + inner + "</div>")
    return html_, js


CSS = """
.hand {{ position:absolute; transform:translate(-50%,-50%); }}
.emo-pos {{ position:absolute; width:0; height:0; z-index:6; }}
.emo {{ position:absolute; left:-80px; top:-60px; width:160px; text-align:center; font-size:{emo_px}px; line-height:1; white-space:nowrap; }}
.ch-card {{ position:absolute; z-index:4; background:#fff; border:7px solid #000; border-radius:28px; box-shadow:0 10px 0 #000, 0 18px 30px rgba(0,0,0,.45); overflow:visible; font-family:"Montserrat",sans-serif; font-weight:900; }}
.ch-title {{ position:absolute; left:0; right:0; top:{pad}px; text-align:center; color:#000; letter-spacing:-0.01em; text-transform:uppercase; }}
.ch-bar {{ position:absolute; border:6px solid #000; border-radius:12px 12px 4px 4px; transform-origin:50% 100%; box-sizing:border-box; }}
.ch-val {{ position:absolute; text-align:center; color:#000; white-space:nowrap; }}
.ch-lab {{ position:absolute; text-align:center; color:#333; white-space:nowrap; text-transform:uppercase; }}
.ch-svg {{ position:absolute; left:0; top:0; overflow:visible; }}
.ch-dot {{ position:absolute; width:44px; height:44px; border-radius:50%; border:7px solid #000; box-sizing:border-box; }}
.ch-num {{ position:absolute; left:0; right:0; text-align:center; -webkit-text-stroke:8px #000; paint-order:stroke fill; }}
"""
