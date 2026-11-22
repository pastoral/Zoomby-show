"""Code-drawn SVG puppet characters for Zoomby videos (the "code" character route).

A puppet is a flat 2D cartoon (thick uniform black outline, flat colours + one shade, oversized head, big white
oval eyes) built from a small JSON spec (see ../references/puppet.md). Every limb is its own SVG group with a
pivot, so HyperFrames/GSAP can pose it, run walk/run cycles, switch emotions, blink, nod and move the mouth on
speaking shots - all seek-safe (explicit tl.set at shot start + fromTo tweens with immediateRender:false).

Public API
  puppet_svg(spec, pid, outfit, poses, emotions, speaking, holds, carry, views, props) -> "<svg ...>"
  puppet_js(ch, pid, spec, st, du, words) -> [GSAP lines]
  prop_svg(name, **params) -> "<g>"  (props: can, passport, bell, sunglasses, pig, football, trophy, gold_bar, phone, mic)
  VIEWBOX, ASPECT, POSES, EMOTIONS, HANDS, PROPS
"""
import html, math

OL = "#141414"          # outline colour
SW = 9                  # outline width (viewBox units; the body is ~1000 units tall)
VB = (-150, -190, 700, 1110)
VIEWBOX = " ".join(str(v) for v in VB)
ASPECT = VB[2] / VB[3]
IR = "immediateRender:false"


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


def S(fill, w=SW):
    return f'fill="{fill}" stroke="{OL}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'


def L(w=7):
    return f'fill="none" stroke="{OL}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"'


def cap(x, y0, y1, w, fill, extra=""):
    """vertical capsule centred on x from y0 to y1"""
    return f'<rect x="{x - w / 2:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{y1 - y0:.1f}" rx="{w / 2:.1f}" {S(fill)} {extra}/>'


# ------------------------------------------------------------------ spec defaults ------------------------------------------------------------------
DEFAULT_SPEC = {
    "skin": "#C68B5E",
    "hair": {"style": "short", "color": "#1E1612"},
    "headband": None,
    "facial_hair": None,          # None | "stubble" | "beard" | "moustache"
    "build": "slim",              # slim | regular | bulky
    "outfits": {"main": {"shirt": "#E63946", "trim": "#FFFFFF", "stripes": None, "shorts": "#1D3557",
                         "socks": "#FFFFFF", "boots": "#111111"}},
}
BUILD_W = {"slim": 1.0, "regular": 1.08, "bulky": 1.22}

# ------------------------------------------------------------------ geometry (front view) ------------------------------------------------------------------
HEAD_C = (200, 172)
HEAD_R = (120, 130)
NECK = (200, 300)
UPPER = 120     # shoulder -> elbow
FORE = 106      # elbow -> wrist
THIGH = 128
SHIN = 124
HIP_C = (200, 600)


def joints(view, bw):
    if view == "side":
        return {"shL": (186, 356), "shR": (214, 356), "hipL": (190, 600), "hipR": (210, 600)}
    dx = 74 * bw
    hx = 28 * bw
    return {"shL": (200 - dx, 356), "shR": (200 + dx, 356), "hipL": (200 - hx, 600), "hipR": (200 + hx, 600)}


# ------------------------------------------------------------------ emotions ------------------------------------------------------------------
# eyes: open | happy | wide | half | wink | heart | closed | closed_up ; brows: (angle L, angle R, dy) ; mouth: see MOUTHS
EMOTIONS = {
    "neutral":   dict(eyes="open", brows=(0, 0, 0), mouth="smile"),
    "talk":      dict(eyes="open", brows=(0, 0, 0), mouth="smile"),
    "happy":     dict(eyes="happy", brows=(-6, 6, -8), mouth="big_smile"),
    "laugh":     dict(eyes="happy", brows=(-10, 10, -12), mouth="laugh"),
    "smug":      dict(eyes="half", brows=(12, -6, 0), mouth="smirk"),
    "sad":       dict(eyes="open", look=(0, 7), brows=(-20, 20, 0), mouth="frown", extras=["tear"]),
    "angry":     dict(eyes="open", look=(0, 3), brows=(24, -24, 10), mouth="tight", extras=["red"]),
    "surprised": dict(eyes="wide", brows=(-6, 6, -20), mouth="o"),
    "shock":     dict(eyes="wide", brows=(-6, 6, -20), mouth="o"),
    "scared":    dict(eyes="wide", look=(0, 3), brows=(-18, 18, -12), mouth="wobbly", extras=["sweat"]),
    "confused":  dict(eyes="open", look=(6, -4), brows=(-16, 6, -2), brow_dy=(-8, 6), mouth="side"),
    "love":      dict(eyes="heart", brows=(-6, 6, -8), mouth="big_smile", extras=["blush"]),
    "wink":      dict(eyes="wink", brows=(0, -10, -2), mouth="big_smile"),
    "sleepy":    dict(eyes="closed", brows=(0, 0, 6), mouth="flat"),
    "thinking":  dict(eyes="open", look=(9, -9), brows=(-12, 8, -4), mouth="side"),
    "proud":     dict(eyes="closed_up", brows=(-6, 6, -8), mouth="big_smile", extras=["blush"]),
}
CLOSED_MOUTHS = {"smile", "big_smile", "smirk", "frown", "tight", "flat", "side", "wobbly"}
OPEN_EYES = {"open", "wide", "half"}
DARK = "#5E1515"
MOUTHS = {
    "smile":     f'<path d="M-30,-4 Q0,20 30,-4" {L(7)}/>',
    "big_smile": f'<path d="M-42,-10 Q0,30 42,-10" {L(7)}/><path d="M-48,-14 Q-44,-8 -40,-4" {L(5)}/><path d="M48,-14 Q44,-8 40,-4" {L(5)}/>',
    "half":      f'<path d="M-30,-4 Q0,26 30,-4 Q0,6 -30,-4Z" fill="{DARK}" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>',
    "laugh":     (f'<path d="M-46,-12 Q0,62 46,-12 Z" fill="{DARK}" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>'
                  f'<path d="M-38,-8 L38,-8 L33,4 Q0,9 -33,4Z" fill="#FFFFFF" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>'
                  f'<ellipse cx="0" cy="30" rx="17" ry="8" fill="#E86A7A"/>'),
    "o":         f'<ellipse cx="0" cy="4" rx="14" ry="19" fill="{DARK}" stroke="{OL}" stroke-width="6"/>',
    "frown":     f'<path d="M-26,12 Q0,-8 26,12" {L(7)}/>',
    "smirk":     f'<path d="M-26,4 Q8,12 34,-12" {L(7)}/>',
    "tight":     f'<path d="M-24,6 Q0,0 24,6" {L(8)}/>',
    "flat":      f'<path d="M-20,4 L20,4" {L(7)}/>',
    "wobbly":    f'<path d="M-28,4 q7,-8 14,0 t14,0 t14,0 t14,0" {L(6)}/>',
    "side":      f'<path d="M-4,6 Q16,10 34,-2" {L(7)}/>',
}


def eye(x, y, kind, look=(0, 0), side=""):
    lx, ly = look
    white = f'<ellipse cx="{x}" cy="{y}" rx="27" ry="34" fill="#FFFFFF" stroke="{OL}" stroke-width="6"/>'
    pupil = f'<circle cx="{x + 6 + lx}" cy="{y + 6 + ly}" r="9.5" fill="{OL}"/><circle cx="{x + 9 + lx}" cy="{y + 2 + ly}" r="3" fill="#FFFFFF"/>'
    if kind == "open":
        return white + pupil
    if kind == "wide":
        return (f'<ellipse cx="{x}" cy="{y}" rx="31" ry="40" fill="#FFFFFF" stroke="{OL}" stroke-width="6"/>'
                f'<circle cx="{x + 3 + lx}" cy="{y + 3 + ly}" r="7" fill="{OL}"/>')
    if kind == "half":
        return (white + pupil + f'<path d="M{x - 29},{y - 2} Q{x},{y - 44} {x + 29},{y - 2} Z" fill="SKIN" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>')
    if kind == "happy":
        return f'<path d="M{x - 25},{y + 8} Q{x},{y - 24} {x + 25},{y + 8}" {L(8)}/>'
    if kind == "closed":
        return f'<path d="M{x - 24},{y} Q{x},{y + 14} {x + 24},{y}" {L(7)}/>'
    if kind == "closed_up":
        return f'<path d="M{x - 24},{y + 4} Q{x},{y - 12} {x + 24},{y + 4}" {L(7)}/>'
    if kind == "heart":
        return (f'<path d="M{x},{y + 26} C{x - 40},{y} {x - 26},{y - 30} {x},{y - 12} C{x + 26},{y - 30} {x + 40},{y} {x},{y + 26}Z" '
                f'fill="#E8344E" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>')
    return white + pupil


def face_svg(emo, dx, speaking, fid):
    E = EMOTIONS.get(emo, EMOTIONS["neutral"])
    cx, cy = HEAD_C
    ex = (cx - 44 + dx, cx + 44 + dx) if dx == 0 else (cx - 26 + dx, cx + 50 + dx)
    ey = cy + 6
    look = E.get("look", (0, 0))
    ek = E["eyes"]
    parts = []
    if ek == "wink":
        parts += [eye(ex[0], ey, "open", look), eye(ex[1], ey, "happy")]
    else:
        parts += [eye(ex[0], ey, ek, look), eye(ex[1], ey, ek, look)]
    aL, aR, bdy = E["brows"]
    bd = E.get("brow_dy", (0, 0))
    for k, (x, a) in enumerate(((ex[0], aL), (ex[1], aR))):
        y = cy - 50 + bdy + bd[k]
        parts.append(f'<rect x="{x - 26}" y="{y - 6}" width="52" height="13" rx="6.5" fill="HAIR" transform="rotate({a} {x} {y})"/>')
    nx = cx + dx + (14 if dx else 0)
    parts.append(f'<path d="M{nx - 4},{cy + 30} Q{nx + 12},{cy + 42} {nx - 2},{cy + 50}" {L(6)}/>')
    mx, my = cx + dx + (8 if dx else 0), cy + 82
    m = E["mouth"]
    if speaking and m in CLOSED_MOUTHS:
        parts.append(f'<g class="mc" transform="translate({mx} {my})">{MOUTHS[m]}</g>'
                     f'<g class="mh" opacity="0" transform="translate({mx} {my})">{MOUTHS["half"]}</g>')
    else:
        parts.append(f'<g transform="translate({mx} {my})">{MOUTHS[m]}</g>')
    for x in E.get("extras", []):
        if x == "tear":
            parts.append(f'<path d="M{ex[1] + 14},{ey + 34} q-10,18 0,26 q10,-8 0,-26Z" fill="#6EC6FF" stroke="{OL}" stroke-width="4"/>')
        elif x == "sweat":
            parts.append(f'<path d="M{cx + 104},{cy - 70} q-14,24 0,34 q14,-10 0,-34Z" fill="#6EC6FF" stroke="{OL}" stroke-width="4"/>')
        elif x == "blush":
            parts += [f'<ellipse cx="{ex[0] - 14}" cy="{cy + 56}" rx="20" ry="10" fill="#FF7A8A" opacity="0.55"/>',
                      f'<ellipse cx="{ex[1] + 14}" cy="{cy + 56}" rx="20" ry="10" fill="#FF7A8A" opacity="0.55"/>']
        elif x == "red":
            parts += [f'<ellipse cx="{ex[0] - 12}" cy="{cy + 56}" rx="22" ry="11" fill="#E8344E" opacity="0.45"/>',
                      f'<ellipse cx="{ex[1] + 12}" cy="{cy + 56}" rx="22" ry="11" fill="#E8344E" opacity="0.45"/>']
    return f'<g id="{fid}" class="face">{"".join(parts)}</g>'


def blink_svg(dx, bid):
    cx, cy = HEAD_C
    ex = (cx - 44 + dx, cx + 44 + dx) if dx == 0 else (cx - 26 + dx, cx + 50 + dx)
    ey = cy + 6
    g = "".join(f'<ellipse cx="{x}" cy="{ey}" rx="33" ry="42" fill="SKIN"/><path d="M{x - 24},{ey} Q{x},{ey + 14} {x + 24},{ey}" {L(7)}/>' for x in ex)
    return f'<g id="{bid}" opacity="0">{g}</g>'


# ------------------------------------------------------------------ hair ------------------------------------------------------------------
def hair_back(style, col, view):
    cx, cy = HEAD_C
    out = []
    if style in ("long_curly_tied", "curly", "afro"):
        big = style == "afro"
        R = 150 if big else 128
        n = 13
        for i in range(n):
            a = math.radians(190 + i * (160 / (n - 1)))
            r = 46 if big else 34
            out.append(f'<circle cx="{cx + R * math.cos(a):.0f}" cy="{cy + 6 + R * math.sin(a) * 0.95:.0f}" r="{r}" {S(col, 7)}/>')
        if not big:  # side curls down to the jaw
            for (x, y) in ((76, 196), (70, 238), (324, 196), (330, 238)):
                if view == "side" and x > 200:
                    continue
                out.append(f'<circle cx="{x}" cy="{y}" r="30" {S(col, 7)}/>')
        if style == "long_curly_tied" and view == "side":  # ponytail at the back of the head
            for (x, y, r) in ((70, 150, 34), (40, 190, 30), (30, 236, 26), (34, 276, 22)):
                out.append(f'<circle cx="{x}" cy="{y}" r="{r}" {S(col, 7)}/>')
    elif style in ("short", "buzz"):
        out.append(f'<path d="M{cx - 124},{cy + 10} Q{cx - 130},{cy - 150} {cx},{cy - 146} Q{cx + 130},{cy - 150} {cx + 124},{cy + 10} Z" {S(col, 8)}/>')
    return "".join(out)


def hair_front(style, col, headband, view, dx):
    cx, cy = HEAD_C
    out = []
    if style in ("long_curly_tied", "curly", "afro"):
        n = 9
        for i in range(n):
            a = math.radians(205 + i * (130 / (n - 1)))
            out.append(f'<circle cx="{cx + dx * 0.3 + 104 * math.cos(a):.0f}" cy="{cy - 6 + 112 * math.sin(a):.0f}" r="24" {S(col, 6)}/>')
    elif style == "short":
        out.append(f'<path d="M{cx - 112},{cy - 40} Q{cx - 70},{cy - 120} {cx + dx * 0.3},{cy - 128} Q{cx + 80},{cy - 122} {cx + 114},{cy - 36} '
                   f'Q{cx + 60},{cy - 86} {cx + 10},{cy - 74} Q{cx - 50},{cy - 90} {cx - 112},{cy - 40} Z" {S(col, 7)}/>')
    elif style == "buzz":
        out.append(f'<path d="M{cx - 116},{cy - 30} Q{cx},{cy - 150} {cx + 116},{cy - 30} Q{cx},{cy - 104} {cx - 116},{cy - 30} Z" fill="{col}" opacity="0.85"/>')
    if headband:
        out.append(f'<path d="M{cx - 118},{cy - 52} Q{cx},{cy - 118} {cx + 118},{cy - 52} L{cx + 114},{cy - 30} Q{cx},{cy - 94} {cx - 114},{cy - 30} Z" {S(headband, 7)}/>')
    return "".join(out)


def facial_hair(kind, col, dx):
    cx, cy = HEAD_C
    if kind == "stubble":
        return f'<path d="M{cx - 96},{cy + 40} Q{cx + dx},{cy + 170} {cx + 96},{cy + 40} Q{cx + dx},{cy + 120} {cx - 96},{cy + 40}Z" fill="{col}" opacity="0.28"/>'
    if kind == "beard":
        return f'<path d="M{cx - 108},{cy + 20} Q{cx + dx},{cy + 190} {cx + 108},{cy + 20} Q{cx + 60},{cy + 76} {cx + dx},{cy + 70} Q{cx - 60},{cy + 76} {cx - 108},{cy + 20}Z" {S(col, 7)}/>'
    if kind == "moustache":
        return f'<path d="M{cx + dx - 34},{cy + 70} Q{cx + dx},{cy + 50} {cx + dx + 34},{cy + 70} Q{cx + dx},{cy + 62} {cx + dx - 34},{cy + 70}Z" {S(col, 5)}/>'
    return ""


# ------------------------------------------------------------------ hands (wrist at 0,0, hand extends along +y) ------------------------------------------------------------------
def _finger(x, length, ang, w=14, y0=30):
    return f'<rect x="{x - w / 2}" y="{y0}" width="{w}" height="{length}" rx="{w / 2}" {S("SKIN", 6)} transform="rotate({ang} {x} {y0})"/>'


def _fist():
    return (f'<rect x="-25" y="2" width="50" height="50" rx="18" {S("SKIN", 7)}/>'
            f'<path d="M-12,40 L-12,50 M2,40 L2,51 M15,40 L15,49" {L(4)}/>')


HANDS = {
    "open":   lambda: "".join(_finger(x, 36, a) for x, a in ((-15, 16), (-5, 4), (6, -4), (16, -16))) + _finger(-24, 26, 60, 15, 14) + f'<ellipse cx="0" cy="24" rx="25" ry="24" {S("SKIN", 7)}/>',
    "fist":   _fist,
    "hold":   _fist,
    "point":  lambda: _finger(10, 46, 0, 15, 34) + _fist(),
    "count1": lambda: _finger(10, 46, 0, 15, 34) + _fist(),
    "count2": lambda: _finger(2, 44, 8, 14, 34) + _finger(15, 44, -8, 14, 34) + _fist(),
    "peace":  lambda: _finger(0, 46, 16, 14, 34) + _finger(16, 46, -16, 14, 34) + _fist(),
    "count3": lambda: _finger(-10, 40, 12, 13, 34) + _finger(3, 44, 0, 13, 34) + _finger(16, 40, -12, 13, 34) + _fist(),
    "thumbs": lambda: _finger(-16, 34, 0, 18, 30) + _fist(),
}


# ------------------------------------------------------------------ props (centred on 0,0, ~100-150 units) ------------------------------------------------------------------
def prop_svg(name, **p):
    if name == "can":
        c = p.get("color", "#2E6BE6")
        return (f'<g><rect x="-28" y="-52" width="56" height="104" rx="10" {S(c, 7)}/>'
                f'<rect x="-28" y="-52" width="56" height="14" rx="6" {S("#C9CED6", 6)}/>'
                f'<rect x="-14" y="-30" width="9" height="66" rx="4" fill="#FFFFFF" opacity="0.45"/></g>')
    if name == "passport":
        return (f'<g><rect x="-38" y="-50" width="76" height="100" rx="8" {S("#7A1F2B", 7)}/>'
                f'<circle cx="0" cy="-6" r="18" fill="none" stroke="#E2B84C" stroke-width="5"/>'
                f'<rect x="-20" y="24" width="40" height="6" rx="3" fill="#E2B84C"/></g>')
    if name == "bell":
        return (f'<g><rect x="-58" y="18" width="116" height="20" rx="8" {S("#9BA3AE", 7)}/>'
                f'<path d="M-50,20 Q-50,-48 0,-48 Q50,-48 50,20 Z" {S("#D9DEE5", 7)}/>'
                f'<rect x="-8" y="-66" width="16" height="20" rx="5" {S("#9BA3AE", 6)}/>'
                f'<path d="M-26,-20 Q-20,-36 -4,-40" fill="none" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round"/></g>')
    if name == "sunglasses":
        return (f'<g><rect x="-86" y="-22" width="72" height="46" rx="16" {S("#111111", 7)}/>'
                f'<rect x="14" y="-22" width="72" height="46" rx="16" {S("#111111", 7)}/>'
                f'<path d="M-14,-6 Q0,-16 14,-6" {L(8)}/>'
                f'<path d="M-70,-12 L-50,-12 M30,-12 L50,-12" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round" opacity="0.6"/></g>')
    if name == "pig":
        pk, dk = "#F7A8B8", "#E07890"
        legs = "".join(f'<rect x="{x}" y="30" width="20" height="40" rx="8" {S(pk, 6)}/>' for x in (-56, -28, 14, 40))
        return (f'<g>{legs}<path d="M-82,0 q-30,-6 -24,-26 q8,-14 18,0 q4,10 -6,10" {L(6)}/>'
                f'<ellipse cx="-6" cy="4" rx="84" ry="56" {S(pk, 7)}/>'
                f'<path d="M34,-70 L46,-102 L66,-70Z" {S(pk, 6)}/><path d="M84,-66 L104,-96 L110,-60Z" {S(pk, 6)}/>'
                f'<circle cx="74" cy="-34" r="46" {S(pk, 7)}/>'
                f'<ellipse cx="104" cy="-22" rx="22" ry="17" {S(dk, 6)}/><circle cx="97" cy="-22" r="4" fill="{OL}"/><circle cx="111" cy="-22" r="4" fill="{OL}"/>'
                f'<circle cx="62" cy="-48" r="7" fill="{OL}"/><circle cx="92" cy="-54" r="7" fill="{OL}"/>'
                f'<path d="M58,-6 Q74,8 90,0" {L(5)}/></g>')
    if name == "football":
        return (f'<g><circle cx="0" cy="0" r="44" {S("#FFFFFF", 7)}/>'
                f'<path d="M0,-16 L15,-5 L9,13 L-9,13 L-15,-5Z" fill="{OL}"/>'
                f'<path d="M0,-16 L0,-40 M15,-5 L38,-14 M9,13 L24,34 M-9,13 L-24,34 M-15,-5 L-38,-14" {L(5)}/></g>')
    if name == "trophy":
        g = "#F2C230"
        return (f'<g><rect x="-40" y="60" width="80" height="22" rx="6" {S("#8A5A2B", 7)}/><rect x="-12" y="30" width="24" height="34" {S(g, 7)}/>'
                f'<path d="M-50,-60 L50,-60 Q50,30 0,34 Q-50,30 -50,-60Z" {S(g, 7)}/>'
                f'<path d="M-50,-44 Q-86,-44 -70,-6 Q-62,8 -44,4 M50,-44 Q86,-44 70,-6 Q62,8 44,4" {L(8)}/></g>')
    if name == "gold_bar":
        return (f'<g><path d="M-60,30 L60,30 L44,-26 L-44,-26Z" {S("#F2C230", 7)}/>'
                f'<path d="M-30,-14 L20,-14" stroke="#FFF3B0" stroke-width="7" stroke-linecap="round"/></g>')
    if name == "phone":
        return f'<g><rect x="-30" y="-56" width="60" height="112" rx="12" {S("#222222", 7)}/><rect x="-21" y="-44" width="42" height="80" rx="4" fill="#5AB0FF"/></g>'
    if name == "mic":
        return f'<g><rect x="-10" y="0" width="20" height="90" rx="8" {S("#333333", 7)}/><circle cx="0" cy="-16" r="28" {S("#888888", 7)}/></g>'
    return ""


PROPS = ["can", "passport", "bell", "sunglasses", "pig", "football", "trophy", "gold_bar", "phone", "mic"]

# ------------------------------------------------------------------ poses ------------------------------------------------------------------
# angles in degrees (SVG, clockwise +). Arms hang down at 0; the screen-left arm (L) swings OUT with +, the right arm (R) with -.
# Legs: L out with +, R out with -. In the side view (facing right) a leg/arm moves FORWARD with -.
BASE = dict(view="front", shL=7, elL=-4, shR=-7, elR=4, hipL=3, knL=0, hipR=-3, knR=0, head=0, headY=0, lean=0, bodyY=0,
            handL="hold", handR="hold", hold=None)
POSES = {
    "front":        {},
    "wave":         dict(shR=-142, elR=-28, handR="open"),
    "point":        dict(shR=-86, elR=0, handR="point"),
    "celebrate":    dict(shL=150, elL=18, shR=-150, elR=-18, handL="fist", handR="fist", bodyY=-14),
    "hold_up":      dict(shL=158, elL=26, shR=-158, elR=-26, handL="open", handR="open", hold="above", bodyY=-6),
    "arms_crossed": dict(shL=22, elL=-128, shR=-22, elR=128, handL="fist", handR="fist"),
    "hands_hips":   dict(shL=42, elL=-104, shR=-42, elR=104, handL="fist", handR="fist"),
    "shrug":        dict(shL=34, elL=-96, shR=-34, elR=96, handL="open", handR="open", head=7),
    "think":        dict(shR=40, elR=136, handR="fist", head=-6),
    "shush":        dict(shR=52, elR=128, handR="point", head=-4),
    "sip":          dict(shR=46, elR=130, handR="hold", hold="hand", head=-10),
    "slump":        dict(shL=2, elL=0, shR=-2, elR=0, headY=16, head=-4, bodyY=16),
    "surprised":    dict(shL=128, elL=52, shR=-128, elR=-52, handL="open", handR="open", lean=-4),
    "jump":         dict(shL=152, elL=10, shR=-152, elR=-10, hipL=24, knL=-56, hipR=-24, knR=56, bodyY=-90, handL="open", handR="open"),
    "count":        dict(shR=-160, elR=-10, handR="count1"),
    "count2":       dict(shR=-160, elR=-10, handR="count2"),
    "count3":       dict(shR=-160, elR=-10, handR="count3"),
    "thumbs":       dict(shR=-40, elR=-120, handR="thumbs"),
    "piggyback":    dict(shL=38, elL=-72, shR=-38, elR=72, handL="hold", handR="hold", lean=4),
    "side_r":       dict(view="side", shL=-8, elL=-6, shR=8, elR=-10, hipL=2, hipR=-2),
    "walk":         dict(view="side", shL=-24, elL=-14, shR=24, elR=-12, hipL=20, knL=18, hipR=-24, knR=6),
    "run":          dict(view="side", shL=-48, elL=-84, shR=44, elR=-74, hipL=30, knL=58, hipR=-44, knR=30, lean=10, bodyY=-12),
    "three_quarter": dict(view="side", shL=4, elL=-6, shR=-10, elR=8),
}
JOINTS = ["shL", "elL", "shR", "elR", "hipL", "knL", "hipR", "knR"]


def pose(name, **over):
    p = dict(BASE)
    p.update(POSES.get(name, {}))
    p.update(over)
    return p


def mirror(p):
    """the other half of a walk/run cycle"""
    q = dict(p)
    for a, b in (("shL", "shR"), ("elL", "elR"), ("hipL", "hipR"), ("knL", "knR")):
        q[a], q[b] = p[b], p[a]
    return q


# ------------------------------------------------------------------ body ------------------------------------------------------------------
def leg(px, py, kid, side_view, outfit, skin, hip, kn, bw, back=False):
    o = outfit
    sk = shade(skin, -0.18) if back else skin
    sock = shade(o.get("socks", "#FFFFFF"), -0.18) if back else o.get("socks", "#FFFFFF")
    boot = o.get("boots", "#111111")
    tw, sw_ = 60 * bw, 52 * bw
    if side_view:
        bootp = f'<path d="M{px - 26},{py + THIGH + SHIN - 8} L{px + 24},{py + THIGH + SHIN - 8} Q{px + 66},{py + THIGH + SHIN} {px + 64},{py + THIGH + SHIN + 30} L{px - 28},{py + THIGH + SHIN + 30} Z" {S(boot)}/>'
    else:
        bootp = f'<path d="M{px - 30},{py + THIGH + SHIN - 8} L{px + 30},{py + THIGH + SHIN - 8} Q{px + 40},{py + THIGH + SHIN + 30} {px + 4},{py + THIGH + SHIN + 32} L{px - 34},{py + THIGH + SHIN + 32} Q{px - 40},{py + THIGH + SHIN + 8} {px - 30},{py + THIGH + SHIN - 8}Z" {S(boot)}/>'
    ky = py + THIGH
    shin = (cap(px, ky - 10, ky + SHIN, sw_, sk) + f'<rect x="{px - sw_ / 2 - 1}" y="{ky + 50}" width="{sw_ + 2}" height="{SHIN - 46}" rx="10" {S(sock)}/>' + bootp)
    return (f'<g id="{kid}-hip" transform="rotate({hip} {px} {py})">' + cap(px, py - 20, ky + 10, tw, sk) +
            f'<g id="{kid}-kn" transform="rotate({kn} {px} {ky})">{shin}</g></g>')


def arm(px, py, aid, outfit, skin, sh, el, hand, hold_svg, back=False):
    o = outfit
    shirt = shade(o["shirt"], -0.2) if back else o["shirt"]
    sk = shade(skin, -0.18) if back else skin
    ey = py + UPPER
    wy = ey + FORE
    hands = "".join(f'<g class="hd-{k}" opacity="{1 if k == hand else 0}" transform="translate({px} {wy - 6})">{HANDS[k]().replace("SKIN", sk)}</g>' for k in HANDS)
    fore = cap(px, ey - 14, wy, 40, sk) + hands + (hold_svg or "")
    upper = cap(px, py - 10, ey + 12, 44, sk) + f'<path d="M{px - 32},{py - 16} Q{px},{py - 36} {px + 32},{py - 16} L{px + 30},{py + 58} L{px - 30},{py + 58} Z" {S(shirt)}/>'
    if o.get("stripes") and not back:
        upper += f'<rect x="{px - 6}" y="{py - 22}" width="12" height="78" fill="{o["stripes"]}"/>'
    if o.get("trim"):
        upper += f'<rect x="{px - 28}" y="{py + 48}" width="56" height="10" fill="{o["trim"]}" stroke="{OL}" stroke-width="5"/>'
    return f'<g id="{aid}-sh" transform="rotate({sh} {px} {py})">{upper}<g id="{aid}-el" transform="rotate({el} {px} {ey})">{fore}</g></g>'


def torso(view, outfit, bw, pid):
    o = outfit
    k = 0.72 if view == "side" else 1.0
    w = lambda x: 200 + (x - 200) * k * bw
    d = (f"M{w(150)},330 Q200,318 {w(250)},330 L{w(282)},350 Q{w(292)},362 {w(286)},384 L{w(262)},562 "
         f"L{w(138)},562 L{w(114)},384 Q{w(108)},362 {w(118)},350 Z")
    shorts = (f'<path d="M{w(138)},548 L{w(262)},548 L{w(274)},652 L{w(206)},652 L200,630 L{w(194)},652 L{w(126)},652 Z" {S(o.get("shorts", "#1D3557"))}/>')
    clip = f'{pid}-{view}-tc'
    out = f'<clipPath id="{clip}"><path d="{d}"/></clipPath><path d="{d}" fill="{o["shirt"]}"/>'
    if o.get("stripes"):
        n = o.get("stripe_n", 5)
        out += "".join(f'<rect x="{w(100 + i * 200 / n * 1.0) - 1:.0f}" y="300" width="{200 / n / 2 * k * bw:.0f}" height="280" fill="{o["stripes"]}" clip-path="url(#{clip})"/>'
                       for i in range(n + 1))
    out += f'<path d="M{w(140)},420 Q200,450 {w(262)},420 L{w(262)},562 L{w(138)},562 Z" fill="#000" opacity="0.08" clip-path="url(#{clip})"/>'
    out += f'<path d="{d}" fill="none" stroke="{OL}" stroke-width="{SW}" stroke-linejoin="round"/>'
    if o.get("trim"):
        out += f'<path d="M{w(172)},331 L200,376 L{w(228)},331" fill="none" stroke="{OL}" stroke-width="{SW + 10}" stroke-linejoin="round"/>'
        out += f'<path d="M{w(172)},331 L200,376 L{w(228)},331" fill="none" stroke="{o["trim"]}" stroke-width="12" stroke-linejoin="round"/>'
    return out + shorts


def one_view(spec, pid, outfit_name, view, p, emotions, speaking, hold_svg, carry_svg):
    """one view (front|side) of the puppet in pose p; ids {pid}-{view}-*"""
    o = spec["outfits"][outfit_name]
    skin = spec["skin"]
    bw = BUILD_W.get(spec.get("build", "slim"), 1.0)
    hair = spec.get("hair") or {}
    hs, hc = hair.get("style", "short"), hair.get("color", "#1E1612")
    J = joints(view, bw)
    vid = f"{pid}-{view}"
    dx = 34 if view == "side" else 0
    side = view == "side"
    above = hold_svg if p.get("hold") == "above" else ""
    in_hand = hold_svg if p.get("hold") == "hand" else ""
    legs = (leg(*J["hipL"], f"{vid}-L", side, o, skin, p["hipL"], p["knL"], bw, back=side) +
            leg(*J["hipR"], f"{vid}-R", side, o, skin, p["hipR"], p["knR"], bw))
    armL = arm(*J["shL"], f"{vid}-aL", o, skin, p["shL"], p["elL"], p["handL"], None, back=side)
    armR = arm(*J["shR"], f"{vid}-aR", o, skin, p["shR"], p["elR"], p["handR"],
               f'<g transform="translate({J["shR"][0]} {J["shR"][1] + UPPER + FORE + 40}) rotate({-(p["shR"] + p["elR"])})">{in_hand}</g>' if in_hand else None)
    cx, cy = HEAD_C
    ears = (f'<circle cx="{cx - 118 + (40 if side else 0)}" cy="{cy + 14}" r="22" {S(skin, 7)}/>' +
            ("" if side else f'<circle cx="{cx + 118}" cy="{cy + 14}" r="22" {S(skin, 7)}/>'))
    faces = "".join(face_svg(e, dx, speaking, f"{vid}-f-{e}") for e in emotions)
    head = (hair_back(hs, hc, view) + ears +
            f'<ellipse cx="{cx}" cy="{cy}" rx="{HEAD_R[0]}" ry="{HEAD_R[1]}" {S(skin)}/>' +
            f'<path d="M{cx - 84},{cy + 90} Q{cx},{cy + 150} {cx + 84},{cy + 90} Q{cx},{cy + 128} {cx - 84},{cy + 90}Z" fill="#000" opacity="0.07"/>' +
            facial_hair(spec.get("facial_hair"), hc, dx) + faces + blink_svg(dx, f"{vid}-blink") +
            hair_front(hs, hc, spec.get("headband"), view, dx))
    head = head.replace("SKIN", skin).replace("HAIR", hc)
    neck = f'<rect x="{200 - 28}" y="{276}" width="56" height="70" rx="10" {S(skin)}/><rect x="172" y="320" width="56" height="18" fill="#000" opacity="0.12"/>'
    upper = (("" if not side else armL) + neck + torso(view, o, bw, pid) +
             f'<g id="{vid}-head" transform="translate(0 {p["headY"]}) rotate({p["head"]} {NECK[0]} {NECK[1]})">{head}</g>' +
             ("" if side else armL) + armR + (f'<g transform="translate(200 {-40})">{above}</g>' if above else ""))
    body = (f'<g id="{vid}-body" transform="translate(0 {p["bodyY"]})">{carry_svg or ""}{legs}'
            f'<g id="{vid}-upper" transform="rotate({p["lean"]} {HIP_C[0]} {HIP_C[1]})">{upper}</g></g>')
    return f'<g id="{vid}" class="pview">{body}</g>'


def puppet_svg(spec, pid, outfit, pose_names=("front",), emotions=("neutral",), speaking=False, hold=None, carry=None, show_view=None):
    """Full SVG for one puppet. Every view used by pose_names is rendered (hidden unless it is the first pose's view)."""
    spec = {**DEFAULT_SPEC, **spec}
    ps = [pose(n) if isinstance(n, str) else n for n in pose_names]
    views = []
    for p in ps:
        if p["view"] not in views:
            views.append(p["view"])
    first = show_view or ps[0]["view"]
    hold_svg = prop_svg(**hold) if isinstance(hold, dict) else (prop_svg(hold) if hold else "")
    out = []
    for v in views:
        pv = next(p for p in ps if p["view"] == v)
        out.append(one_view(spec, pid, outfit, v, pv, list(dict.fromkeys(emotions)), speaking, hold_svg, carry)
                   .replace('class="pview"', f'class="pview" opacity="{1 if v == first else 0}"', 1))
    return (f'<svg id="{pid}" xmlns="http://www.w3.org/2000/svg" viewBox="{VIEWBOX}" width="100%" height="100%" '
            f'style="position:absolute;inset:0;overflow:visible">{"".join(out)}</svg>')


# ------------------------------------------------------------------ animation ------------------------------------------------------------------
def _origins(spec, view):
    bw = BUILD_W.get(spec.get("build", "slim"), 1.0)
    J = joints(view, bw)
    return {"shL": J["shL"], "elL": (J["shL"][0], J["shL"][1] + UPPER), "shR": J["shR"], "elR": (J["shR"][0], J["shR"][1] + UPPER),
            "hipL": J["hipL"], "knL": (J["hipL"][0], J["hipL"][1] + THIGH), "hipR": J["hipR"], "knR": (J["hipR"][0], J["hipR"][1] + THIGH)}


def _sel(vid, j):
    side = {"shL": "aL-sh", "elL": "aL-el", "shR": "aR-sh", "elR": "aR-el", "hipL": "L-hip", "knL": "L-kn", "hipR": "R-hip", "knR": "R-kn"}[j]
    return f"#{vid}-{side}"


def _set_pose(J_, vid, O, p, t):
    for j in JOINTS:
        ox, oy = O[j]
        J_.append(f'tl.set("{_sel(vid, j)}",{{rotation:{p[j]},svgOrigin:"{ox} {oy}"}},{t:.3f});')
    J_.append(f'tl.set("#{vid}-upper",{{rotation:{p["lean"]},svgOrigin:"{HIP_C[0]} {HIP_C[1]}"}},{t:.3f});')
    J_.append(f'tl.set("#{vid}-head",{{rotation:{p["head"]},y:{p["headY"]},svgOrigin:"{NECK[0]} {NECK[1]}"}},{t:.3f});')
    J_.append(f'tl.set("#{vid}-body",{{y:{p["bodyY"]}}},{t:.3f});')
    for side in ("L", "R"):
        for k in HANDS:
            J_.append(f'tl.set("#{vid}-a{side}-sh .hd-{k}",{{opacity:{1 if p["hand" + side] == k else 0}}},{t:.3f});')


def _tween_pose(J_, vid, O, a, b, t, d=0.2, ease="back.out(1.6)"):
    for j in JOINTS:
        if a[j] != b[j]:
            ox, oy = O[j]
            J_.append(f'tl.fromTo("{_sel(vid, j)}",{{rotation:{a[j]}}},{{rotation:{b[j]},svgOrigin:"{ox} {oy}",duration:{d},ease:"{ease}",{IR}}},{t:.3f});')
    if a["lean"] != b["lean"]:
        J_.append(f'tl.fromTo("#{vid}-upper",{{rotation:{a["lean"]}}},{{rotation:{b["lean"]},svgOrigin:"{HIP_C[0]} {HIP_C[1]}",duration:{d},ease:"{ease}",{IR}}},{t:.3f});')
    if (a["head"], a["headY"]) != (b["head"], b["headY"]):
        J_.append(f'tl.fromTo("#{vid}-head",{{rotation:{a["head"]},y:{a["headY"]}}},{{rotation:{b["head"]},y:{b["headY"]},svgOrigin:"{NECK[0]} {NECK[1]}",duration:{d},ease:"{ease}",{IR}}},{t:.3f});')
    if a["bodyY"] != b["bodyY"]:
        J_.append(f'tl.fromTo("#{vid}-body",{{y:{a["bodyY"]}}},{{y:{b["bodyY"]},duration:{d},ease:"{ease}",{IR}}},{t:.3f});')
    for side in ("L", "R"):
        if a["hand" + side] != b["hand" + side]:
            J_.append(f'tl.set("#{vid}-a{side}-sh .hd-{a["hand" + side]}",{{opacity:0}},{t + d * 0.5:.3f});')
            J_.append(f'tl.set("#{vid}-a{side}-sh .hd-{b["hand" + side]}",{{opacity:1}},{t + d * 0.5:.3f});')


def plan(ch):
    """timeline of (t_rel, pose_name) for a puppet character: walk/run moves drive a leg cycle first"""
    seq = [(0.0, ch.get("pose", "front"))]
    for m in ch.get("moves", []):
        if m["type"] in ("walk", "run"):
            seq = [(0.0, m["type"]), (m.get("at", 0) + m.get("dur", 0.8), ch.get("pose", "front"))]
    for c in ch.get("poses", []):
        seq.append((c["at"], c["pose"]))
    seq.sort(key=lambda x: x[0])
    return seq


def emotion_plan(ch):
    seq = [(0.0, ch.get("emotion", "neutral"))]
    for c in ch.get("emotions", []):
        seq.append((c["at"], c["emotion"]))
    return sorted(seq, key=lambda x: x[0])


def puppet_js(ch, pid, spec, st, du, words):
    spec = {**DEFAULT_SPEC, **spec}
    J_ = []
    seq = plan(ch)
    eseq = emotion_plan(ch)
    views = list(dict.fromkeys(pose(n)["view"] for _, n in seq))
    emos = list(dict.fromkeys(e for _, e in eseq))
    end = st + du
    # views + faces: visibility over time
    cur_view = None
    for i, (t, name) in enumerate(seq):
        v = pose(name)["view"]
        if v != cur_view:
            for vv in views:
                J_.append(f'tl.set("#{pid}-{vv}",{{opacity:{1 if vv == v else 0}}},{st + t:.3f});')
            cur_view = v
    for vv in views:
        for i, (t, e) in enumerate(eseq):
            for ee in emos:
                J_.append(f'tl.set("#{pid}-{vv}-f-{ee}",{{opacity:{1 if ee == e else 0}}},{st + t:.3f});')
        J_.append(f'tl.set("#{pid}-{vv}-blink",{{opacity:0}},{st:.3f});')
    # initial pose for every view, then pose changes / cycles
    for vv in views:
        first = next((pose(n) for _, n in seq if pose(n)["view"] == vv), pose("front"))
        _set_pose(J_, f"{pid}-{vv}", _origins(spec, vv), first, st)
    for i, (t, name) in enumerate(seq):
        p = pose(name)
        vid = f"{pid}-{p['view']}"
        O = _origins(spec, p["view"])
        t_abs = st + t
        t_next = st + seq[i + 1][0] if i + 1 < len(seq) else end
        if name in ("walk", "run") or ch.get("anim") == name:
            half = 0.26 if name == "walk" else 0.16
            reps = max(1, int((t_next - t_abs) / half) - 1)
            q = mirror(p)
            for j in JOINTS:
                if p[j] != q[j]:
                    ox, oy = O[j]
                    J_.append(f'tl.fromTo("{_sel(vid, j)}",{{rotation:{p[j]}}},{{rotation:{q[j]},svgOrigin:"{ox} {oy}",duration:{half},ease:"sine.inOut",yoyo:true,repeat:{reps},{IR}}},{t_abs:.3f});')
            J_.append(f'tl.fromTo("#{vid}-body",{{y:{p["bodyY"]}}},{{y:{p["bodyY"] - (10 if name == "walk" else 16)},duration:{half / 2},ease:"sine.inOut",yoyo:true,repeat:{reps * 2 + 1},{IR}}},{t_abs:.3f});')
            last = q if reps % 2 == 0 else p
        else:
            last = p
        if i + 1 < len(seq):
            nxt = pose(seq[i + 1][1])
            if nxt["view"] == p["view"]:
                _tween_pose(J_, vid, O, last, nxt, t_next)
            else:
                _set_pose(J_, f"{pid}-{nxt['view']}", _origins(spec, nxt["view"]), nxt, t_next)
    # blinks (only while the eyes are open)
    t = st + 0.9
    while t < end - 0.2:
        emo = [e for (tt, e) in eseq if st + tt <= t][-1]
        vv = [pose(n)["view"] for (tt, n) in seq if st + tt <= t][-1]
        if EMOTIONS.get(emo, EMOTIONS["neutral"])["eyes"] in OPEN_EYES:
            J_.append(f'tl.set("#{pid}-{vv}-blink",{{opacity:1}},{t:.3f});')
            J_.append(f'tl.set("#{pid}-{vv}-blink",{{opacity:0}},{t + 0.09:.3f});')
        t += 2.7
    # head nods on the words
    if ch.get("nod", True):
        amp = ch.get("nod_amp", 3)
        angles, k = [-1, 0.8, -0.5, 1, -0.8, 0.4], 0
        for w in words:
            if not (st + 0.1 <= w["s"] < end - 0.15) or (w["e"] - w["s"]) < 0.12:
                continue
            vv = [pose(n)["view"] for (tt, n) in seq if st + tt <= w["s"]][-1]
            p = [pose(n) for (tt, n) in seq if st + tt <= w["s"]][-1]
            if p["view"] != "front" or [n for (tt, n) in seq if st + tt <= w["s"]][-1] in ("walk", "run"):
                continue
            a = p["head"] + angles[k % len(angles)] * amp; k += 1
            J_.append(f'tl.to("#{pid}-{vv}-head",{{rotation:{a:.2f},svgOrigin:"{NECK[0]} {NECK[1]}",duration:0.14,ease:"power1.out"}},{w["s"]:.3f});')
    # mouth on speaking shots: half-open on each word, closed between words
    if ch.get("talk"):
        J_.append(f'tl.set("#{pid} .mh",{{opacity:0}},{st:.3f});')
        J_.append(f'tl.set("#{pid} .mc",{{opacity:1}},{st:.3f});')
        for w in words:
            if not (st <= w["s"] < end) or (w["e"] - w["s"]) < 0.14:
                continue
            J_.append(f'tl.set("#{pid} .mh",{{opacity:1}},{w["s"]:.3f});tl.set("#{pid} .mc",{{opacity:0}},{w["s"]:.3f});')
            off = min(w["s"] + max(0.1, (w["e"] - w["s"]) * 0.55), end - 0.04)
            J_.append(f'tl.set("#{pid} .mh",{{opacity:0}},{off:.3f});tl.set("#{pid} .mc",{{opacity:1}},{off:.3f});')
    return J_


def rider(spec, pid, outfit, emotion="laugh"):
    """a smaller puppet riding piggyback (pass as carry= to puppet_svg); drawn behind the carrier"""
    spec = {**DEFAULT_SPEC, **spec}
    p = pose("front", shL=58, elL=-50, shR=-58, elR=50, hipL=58, knL=-84, hipR=-58, knR=84, handL="open", handR="open")
    o = outfit if outfit in spec["outfits"] else next(iter(spec["outfits"]))
    return f'<g transform="translate(200 262) scale(0.74) translate(-200 -600)">{one_view(spec, pid, o, "front", p, [emotion], False, "", None)}</g>'


def needed(ch):
    """poses and emotions a character uses in one shot (to render only what is needed)"""
    names = [n for _, n in plan(ch)]
    if ch.get("anim") in ("walk", "run"):
        names.insert(0, ch["anim"])
    return names, [e for _, e in emotion_plan(ch)]
