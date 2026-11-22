#!/usr/bin/env python3
"""Write the Google Flow prompt sheet (.md + .docx) the user follows to make the character sheet by hand.

Usage:
  python prompt_sheet.py PROJECT.json OUT_DIR            # per video: OUT_DIR = <video>/02_flow_prompts
  python prompt_sheet.py --template OUT_DIR [--name N]   # generic sheet with [PLACEHOLDERS], every item optional

Reads zoomby.project.json -> "assets" (see ../templates/zoomby.project.example.json and
../references/storyboard.md). The full standard library (turnaround + action poses, emotion heads,
hands) is always listed - "as many images as possible" - and the items the storyboard needs are
marked with a star. Writes flow_prompt_sheet.md, flow_prompt_sheet.docx and flow_prompt_sheet.json
(the block spec). Mouth rule: closed or only slightly open everywhere except laugh / surprised.
"""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))

STYLE = ("flat 2D cartoon character illustration, thick bold uniform black outline, flat cel colours with one "
         "soft shadow tone, big white oval eyes with small black pupils, tiny simple nose, slightly oversized head, "
         "mouth closed or a small gentle smile")
WHITE = "plain pure white background, no text, no watermark, no logo"

# (id, what the pose is, aspect, side-view?)
POSES = [
    ("front", "standing straight and facing the camera, arms relaxed at the sides, calm closed-mouth smile, full body head to toe", "9:16"),
    ("three_quarter_l", "standing in a three-quarter view turned to the left, full body", "9:16"),
    ("three_quarter_r", "standing in a three-quarter view turned to the right, full body", "9:16"),
    ("side_r", "standing in full side profile facing right, arms relaxed, full body", "9:16"),
    ("back", "standing seen from behind, full body", "9:16"),
    ("walk", "walking to the right in mid-stride, side view, one leg forward, arms swinging, full body", "9:16"),
    ("run", "running fast to the right, side view, body leaning forward, one foot off the ground, full body", "9:16"),
    ("jump", "jumping happily in the air, both feet off the ground, arms up, full body", "9:16"),
    ("celebrate", "celebrating with both fists raised above the head, big happy smile, full body", "9:16"),
    ("point", "pointing forward at the viewer with the right hand, confident smile, full body", "9:16"),
    ("arms_crossed", "standing with arms crossed, confident half-smile, full body", "9:16"),
    ("hands_hips", "standing proudly with both hands on the hips, full body", "9:16"),
    ("shrug", "shrugging with both palms up and shoulders raised, puzzled look, full body", "9:16"),
    ("think", "thinking pose, one hand on the chin, looking up, full body", "9:16"),
    ("wave", "waving hello with the right hand, friendly smile, full body", "9:16"),
    ("sit", "sitting relaxed on a plain wooden stool, three-quarter view, full body", "9:16"),
    ("slump", "sad posture, shoulders slumped, head down, arms hanging, full body", "9:16"),
    ("surprised", "leaning back in surprise, both hands up near the face, eyes wide, small round mouth, full body", "9:16"),
]
HEADS = [
    ("neutral", None),
    ("neutral_half", "the same smile with the mouth only slightly open, as if saying one soft word (small opening, not wide)"),
    ("happy", "a big happy closed-mouth smile, eyes curved upward with joy"),
    ("laugh", "laughing happily with the mouth open and eyes squinted"),
    ("smug", "a confident half-smile with one eyebrow raised, mouth closed"),
    ("sad", "a sad face: eyebrows tilted up in the middle, small closed frown, one small tear"),
    ("angry", "a grumpy cartoon frown: eyebrows pulled down in a V, lips pressed together, cheeks slightly red"),
    ("surprised", "surprised: eyebrows high, eyes wide, small round open mouth"),
    ("scared", "nervous: eyes wide, eyebrows up, small wobbly closed mouth, small sweat drop"),
    ("confused", "puzzled: one eyebrow up, one down, closed mouth pushed to one side"),
    ("love", "delighted: heart-shaped eyes and a closed-mouth smile"),
    ("wink", "a cheeky wink with one eye closed and a closed-mouth smile"),
    ("sleepy", "sleepy: half-closed eyelids, relaxed closed mouth"),
    ("thinking", "thinking: eyes looking up to one side, mouth closed and pushed to one side"),
    ("proud", "proud: chin slightly up, eyes closed contentedly, closed-mouth smile"),
    ("profile", "the same character seen in side profile facing right, calm closed mouth"),
]
HANDS = [
    ("wave", "open palm facing the viewer, fingers spread, waving hello"),
    ("point", "index finger pointing up, other fingers curled"),
    ("thumbs", "thumbs up"),
    ("fist", "closed fist, knuckles facing the viewer"),
    ("peace", "two fingers in a peace sign"),
    ("stop", "open palm facing the viewer with fingers together, a 'stop' gesture"),
    ("count1", "holding up one finger, counting"),
    ("count2", "holding up two fingers, counting"),
    ("count3", "holding up three fingers, counting"),
    ("hold", "fingers curled in a relaxed grip as if holding a small object (empty hand)"),
]


def star(need):
    return "★" if need else "optional"


def scenes_txt(sc):
    return ", ".join(str(s) for s in sc) if sc else "-"


def make(P, template=False, bg_only=False):
    A = P.get("assets") or {}
    C = A.get("character") or {}
    name = C.get("id", "hero")
    look = C.get("look") or "[CHARACTER LOOK: age, hair style and colour, facial hair, skin tone, face shape, build - looks only, no real names]"
    outfits = A.get("outfits") or [{"id": "main", "desc": "[OUTFIT: main clothing, colours, shoes, accessories - no logos or brand names]"}]
    need_pose = {(p.get("outfit", outfits[0]["id"]), p["pose"]): p for p in A.get("poses", [])}
    need_head = {h["emotion"]: h for h in A.get("heads", [])}
    need_hand = {h["gesture"]: h for h in A.get("hands", [])}
    title = P.get("title") or "Zoomby video"
    B, rows = [], [["File", "Section", "Aspect", "Scenes", "Need"]]

    def item(fname, section, aspect, need, scenes, prompt, ref=None, fallback=None):
        meta = f"**{fname}** · {star(need)} · {aspect}" + (f" · scenes {scenes_txt(scenes)}" if scenes else "") + (f" · reference: `{ref}`" if ref else "")
        B.append({"t": "P", "text": meta})
        B.append({"t": "CODE", "text": prompt})
        if fallback:
            B.append({"t": "NOTE", "text": "Safer fallback if Flow refuses: " + fallback})
        rows.append([fname, section, aspect, scenes_txt(scenes), star(need)])

    B.append({"t": "title", "title": "Google Flow Prompt Sheet" if not template else "Zoomby Character Sheet: Google Flow Prompt Template",
              "subtitle": title if not template else "Fill in the [PLACEHOLDERS], then generate in Google Flow",
              "intro": ["Generate these images yourself in **Google Flow** and save each one under the **file name** shown. "
                        "★ = this video's storyboard needs it; *optional* = extra images that give more acting options (make as many as you can).",
                        "**Mouths stay closed or only slightly open.** Only *laugh* and *surprised* open wide: the face and body carry the performance, not lip-sync."]})

    B.append({"t": "H", "text": "How to Use This Sheet in Flow"})
    for t in ["**Model:** Nano Banana 2.1 (`nano2`) for every image.",
              "**Order:** make the **master front pose** first (the first pose in the poses section). Re-roll until you love it, then attach it as the **reference image** for every other pose, head and hand, so the character stays identical.",
              "**Heads:** make `head_neutral.png` from the master pose, then make every other expression by **editing that cartoon head** (attach it, use the edit prompt). Never edit a real photo.",
              "**Aspect:** 9:16 for full-body poses and backgrounds, 1:1 for heads, hands and props.",
              "**Pace:** 2–4 generations at a time with short breaks. If Flow shows an unusual-activity error, stop for a while.",
              "**Refusals:** use the *safer fallback* line under the prompt. Never add real names, brands, club badges or logos.",
              "**Saving:** characters, heads, hands, props and cast go to `03_character/raw/`; backgrounds go to `04_backgrounds/raw/`. Use the exact file names: Claude builds the rig from them."]:
        B.append({"t": "P", "text": t})

    if bg_only:
        return make_bg_only(P, B, rows, item)
    B.append({"t": "H", "text": "Character Style Lock"})
    B.append({"t": "P", "text": "Every character prompt below already includes this block. Edit the look/outfit here once if you change the character."})
    B.append({"t": "CODE", "text": f"CHARACTER: {look}\nSTYLE: {STYLE}\nBACKGROUND: {WHITE}"})
    for o in outfits:
        B.append({"t": "P", "text": f"**Outfit {o['id']}:** {o['desc']}"})

    # A. poses
    B.append({"t": "H", "text": "Character Turnaround and Action Poses"})
    B.append({"t": "P", "text": "One full set per outfit. Full body head to toe, nothing cropped, feet visible, centred with white space around."})
    for o in outfits:
        lib = list(POSES) + [(p["pose"], p.get("prompt", p["pose"].replace("_", " ")), "9:16")
                             for (oo, pid), p in need_pose.items() if oo == o["id"] and pid not in {x[0] for x in POSES}]
        for pid, what, asp in lib:
            n = need_pose.get((o["id"], pid))
            emo = f", {n['emotion']} expression" if n and n.get("emotion") and pid != "front" else ""
            if pid == "front" and o is outfits[0]:
                pr = f"Full-body cartoon character sheet pose of {look}, wearing {o['desc']}, {what}. {STYLE}, {WHITE}"
                ref = None
            elif pid == "front":  # other outfits: same character as the master, only the clothes change
                pr = (f"Using the attached character as the exact reference (same face, hair, body, pose and style): "
                      f"keep everything identical and only change the clothes to {o['desc']}. {STYLE}, {WHITE}")
                ref = f"{outfits[0]['id']}_front.png"
            else:
                pr = (f"Using the attached character as the exact reference (same face, hair, outfit, colours and style): "
                      f"draw the character {what}{emo}, wearing {o['desc']}. {STYLE}, {WHITE}")
                ref = f"{o['id']}_front.png"
            need = (pid == "front") or bool(n) or (pid in ("side_r",) and bool(need_pose))
            item(f"{o['id']}_{pid}.png", "Pose", asp, need, (n or {}).get("scenes"), pr, ref)

    # B. heads
    B.append({"t": "H", "text": "Emotion Heads (edit the cartoon, not a photo)"})
    B.append({"t": "P", "text": "Head and short neck only, facing the camera, same size and framing in every head, so they swap cleanly."})
    for hid, expr in HEADS:
        n = need_head.get(hid)
        if hid == "neutral":
            pr = (f"Using the attached character as the exact reference: draw only the character's cartoon head and short neck, facing the camera, "
                  f"calm closed-mouth smile, centred. {STYLE}, {WHITE}")
            ref = f"{outfits[0]['id']}_front.png"
        else:
            pr = ("Edit the attached cartoon head: keep exactly the same character, style, outline, colours, hair and framing, "
                  f"and only change the expression to {expr}. {WHITE}")
            ref = "head_neutral.png"
        need = hid in ("neutral", "neutral_half") or bool(n) or (hid == "profile" and any(o == "side_r" or p in ("walk", "run", "side_r") for (o, p) in need_pose))
        item(f"head_{hid}.png", "Head", "1:1", need, (n or {}).get("scenes"), pr, ref)
    for hid, h in need_head.items():
        if hid not in {x[0] for x in HEADS}:
            item(f"head_{hid}.png", "Head", "1:1", True, h.get("scenes"),
                 "Edit the attached cartoon head: keep exactly the same character, style, outline, colours, hair and framing, "
                 f"and only change the expression to {h.get('prompt', hid)}. {WHITE}", "head_neutral.png")

    # C. hands
    B.append({"t": "H", "text": "Hand Gestures"})
    skin = C.get("skin", "[SKIN TONE]")
    for gid, what in HANDS:
        n = need_hand.get(gid)
        pr = (f"Single cartoon hand {what}, {skin} skin, flat 2D cartoon illustration, thick bold uniform black outline, "
              f"simple rounded fingers, wrist cut off cleanly at the bottom, no arm, {WHITE}")
        item(f"hand_{gid}.png", "Hand", "1:1", bool(n), (n or {}).get("scenes"), pr)

    # D. props and cast
    props, cast = A.get("props", []), A.get("cast", [])
    B.append({"t": "H", "text": "Props and Supporting Cast"})
    if not (props or cast):
        B.append({"t": "P", "text": "None needed by the storyboard. Add any prop as: `[OBJECT], slightly oversized, flat 2D cartoon illustration, thick bold uniform black outline, flat colours, " + WHITE + "`."})
    for p in props:
        item(f"prop_{p['id']}.png", "Prop", "1:1", True, p.get("scenes"),
             f"{p['prompt']}, slightly oversized, flat 2D cartoon illustration, thick bold uniform black outline, flat colours, {WHITE}",
             fallback=p.get("fallback"))
    for c in cast:
        item(f"cast_{c['id']}.png", "Cast", "9:16", True, c.get("scenes"),
             f"Full-body cartoon character of {c['prompt']}, same art style as the attached character. {STYLE}, {WHITE}",
             ref=f"{outfits[0]['id']}_front.png", fallback=c.get("fallback"))

    # E. backgrounds
    B.append({"t": "H", "text": "Scene Backgrounds (photoreal, 9:16)"})
    B.append({"t": "P", "text": "Empty locations: no people, no text. The cartoon character is added later, so leave clear space in the upper-middle."})
    bgs = A.get("backgrounds") or [{"file": f"scene{i:02d}.png", "scene": sc.get("id"), "prompt": sc.get("flow_prompt"),
                                     "fallback": sc.get("flow_fallback")} for i, sc in enumerate(P.get("scenes", [])) if sc.get("flow_prompt")]
    if not bgs:
        B.append({"t": "CODE", "text": "[LOCATION + key props for the gag], [warm practical lamps | golden hour | dramatic dusk sky | bright daylight], "
                  "photorealistic cinematic photo, shallow depth of field, vertical 9:16 composition, clear empty space in the upper-middle "
                  "of the frame for a character, no people, no text, no logos, no watermark"})
    for b in bgs:
        item(b["file"], "Background", "9:16", True, [b.get("scene")] if b.get("scene") else None, b["prompt"], fallback=b.get("fallback"))

    B.append({"t": "H", "text": "File Checklist"})
    B.append({"t": "P", "text": f"{sum(1 for r in rows[1:] if r[4] == '★')} required (★) and {sum(1 for r in rows[1:] if r[4] != '★')} optional images. Tick them off as you save them."})
    B.append({"t": "table", "widths": [2900, 1500, 900, 2200, 1100], "rows": rows})
    return B


def make_bg_only(P, B, rows, item):
    """code character route: characters are SVG puppets drawn by Claude, so only the backgrounds are listed"""
    B[0]["intro"] = ["The characters, heads, hands and props of this video are **drawn in code** (SVG puppets, `03_character/puppet.json`). "
                     "Only the **photoreal backgrounds** come from Google Flow: Claude generates them through the Flow connector after your yes, "
                     "or you make them here by hand and save them as `04_backgrounds/raw/sceneNN.png`."]
    B[:] = [b for b in B if not (b["t"] == "P" and any(k in b["text"] for k in ("**Order:**", "**Heads:**")))]
    for b in B:
        if b["t"] == "P" and b["text"].startswith("**Aspect:**"):
            b["text"] = "**Aspect:** 9:16 for every background."
        if b["t"] == "P" and b["text"].startswith("**Saving:**"):
            b["text"] = "**Saving:** `04_backgrounds/raw/sceneNN.png` (00 = the hook, the last number = the ending)."
    B.append({"t": "H", "text": "Scene Backgrounds (photoreal, 9:16)"})
    B.append({"t": "P", "text": "Empty locations: no people, no text. The cartoon character is added later, so leave clear space in the upper-middle."})
    for i, sc in enumerate(P.get("scenes", [])):
        if sc.get("flow_prompt"):
            item(f"scene{i:02d}.png", "Background", "9:16", True, [sc.get("id")], sc["flow_prompt"], fallback=sc.get("flow_fallback"))
    B.append({"t": "H", "text": "File Checklist"})
    B.append({"t": "table", "widths": [2900, 1500, 900, 2200, 1100], "rows": rows})
    return B


def to_md(B):
    out = []
    n = 0
    for b in B:
        t = b["t"]
        if t == "title":
            out += [f"# {b['title']}", f"*{b['subtitle']}*", ""] + [x + "\n" for x in b["intro"]]
        elif t == "H":
            n += 1; out += ["", f"## {n}. {b['text']}", ""]
        elif t in ("P", "SUB"):
            out.append(("- " if t == "SUB" else "") + b["text"] + ("" if t == "SUB" else "\n"))
        elif t == "NOTE":
            out.append(f"> {b['text']}\n")
        elif t == "CODE":
            out += ["```", b["text"], "```", ""]
        elif t == "table":
            r = b["rows"]
            out += ["| " + " | ".join(r[0]) + " |", "|" + "---|" * len(r[0])] + ["| " + " | ".join(x) + " |" for x in r[1:]] + [""]
    return "\n".join(out).replace("\n\n\n", "\n\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project", nargs="?")
    ap.add_argument("out_dir")
    ap.add_argument("--template", action="store_true")
    ap.add_argument("--name", default="flow_prompt_sheet")
    ap.add_argument("--backgrounds-only", action="store_true", help="default when the project's character_route is 'code'")
    A = ap.parse_args()
    P = {"title": "Generic template"} if A.template else json.load(open(A.project, encoding="utf8"))
    B = make(P, A.template, A.backgrounds_only or P.get("character_route") == "code")
    os.makedirs(A.out_dir, exist_ok=True)
    base = os.path.join(A.out_dir, A.name)
    json.dump(B, open(base + ".json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    open(base + ".md", "w", encoding="utf8").write(to_md(B))
    hdr = "Zoomby Show · Flow prompt sheet" + ("" if A.template else " · " + (P.get("slug") or ""))
    subprocess.run(["node", os.path.join(HERE, "prompt_sheet_docx.js"), base + ".json", base + ".docx", hdr], check=True)
    print(json.dumps({"md": base + ".md", "docx": base + ".docx", "items": sum(1 for b in B if b["t"] == "CODE")}))


if __name__ == "__main__":
    sys.exit(main())
