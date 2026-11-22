# Premium route: semi-real bodies in scene shots + animated cartoon eyes (the only route)

Learned from 6 real Zoomby episodes (Haaland, Yamal, Mbappé, Ronaldo, Olise ×2) and proven on the full Ronaldinho video (`videos\2026-11-14-ronaldinho-weird-facts\`: 34 shots, 79 s). Every Zoomby video uses this route.

## What makes it look premium
| Area | Rule |
|---|---|
| Character | A **semi-realistic 3D body** in the kit (real hands, fabric folds, sitting, holding things) with a **flat 2D cartoon head**. The head has flat skin, a thin dark outline, big white oval eyes with small dark dot pupils, a tiny nose line, a simple mouth, and hair as flat shapes. |
| Scene | The character is **inside** the scene: at the table, on the sofa, signing, drinking. The cast (reporters, coach, grandma, rivals) have cartoon heads in the same style. Use no real-person photos. |
| Cut pace | **24–41 cuts per minute-long video. The median shot is 1.0–2.3 s; never hold a still for more than about 3 s.** Use 3–4 shots per fact. |
| Framings | Mix at least 3 per fact (see the menu below). Include one face close-up (`cu_face` or `ecu_face`) per fact. |
| Camera | Every shot moves from frame 1. Use `drift` 8–14% (push) or a pan, a snap `punch` on the punchline word, and `shake` on impacts. |
| Transitions | Hard cuts. Use a **zoom-whip** (`enter: "zoom"`: scale 1.38 + 22 px blur → 1 in 0.22 s) into a new location or on a big beat, at most 1 in every 3 cuts. |
| Face | **Eye darts** (left, right, centre, up) on the beat. Blink every 2–3 s. The expression is written into each shot's prompt (surprised, laughing, smug…). |
| FX | Use them sparingly, on cue words: camera flashes, a white flash, shake, money rain, a ball hitting the lens, Zz, hearts, "?". |
| Logos | **Look-alike kits and brands only.** Use the same colours and design, with no badges, sponsors, numbers or readable brand names. |
| Numbers | **No chart cards.** Show numbers as a caption-style **number pop** (`fx` type `number`): big yellow Montserrat 900 digits with a thick black outline that slam in, count up, punch and burst, with a white label under them (GOALS, KILOS) and an optional small line above. Keep it in a clear area away from the face and the badge. |
| Sound | Music bed at **−26.2 dB**. Use a whoosh or impact on every zoom-whip, camera clicks under flashes, and a pop on reveals. The final mix is about −13 LUFS. |

The references also animate bodies with AI video (image→video). This route uses **stills only**: the motion comes from the camera, eyes and FX. Add AI video only if the user asks, and only after a 1-clip cost test that the user has said yes to.

## 1. Character master (Flow nano2)
Consistency comes from two things used together: the **approved master passed as a reference image** on every shot (on the reference-capable profiles in the shared Flow rulebook), **plus** a **fixed character block** pasted word for word into every prompt.

Write the block once and keep it in the project JSON (`premium.character_block`). The Ronaldinho example:
```
a hybrid character: the BODY is a semi-realistic 3D render of a grown adult male footballer, broad shoulders, muscular athletic build, brown skin, realistic hands, realistic fabric folds, wearing a bright canary-yellow football shirt with a green round collar and green sleeve cuffs, royal-blue shorts, white socks and black boots, no logos, no badges, no numbers; the HEAD is a flat 2D cartoon head: oversized, flat brown skin colour, thin dark brown outline, wide square manly jaw, thin dark moustache line, thick dark eyebrows, big white oval eyes with small black dot pupils, tiny nose line, [EXPRESSION], long curly black hair tied back behind his head drawn as flat dark curly shapes, a thin white headband across the forehead, small flat ears
```
- The **master** is a full-body front view on plain white (`03_character\master_<outfit>.jpg`). Show it for approval and re-roll until the user likes it (generate the master itself text-only from the block). Once approved, it is **an input to Flow**: every shot with the character passes it as `reference_images`.
- Describe the person by looks only. Say "grown adult man" and "square jaw" explicitly, or Flow may soften the face.

## 2. Shot list: framing menu
| Framing | Use for | Prompt opening |
|---|---|---|
| `wide` | Establish the location, hero entrance | "Wide cinematic shot of [location]. [Centred / seated] is [character block] …" |
| `medium` | Action with the hands (drinking, signing, holding) | "Medium close-up shot: [character block] [action] …" |
| `cu_face` | Reaction | "Close-up of [character block] from the chest up, [expression] …" |
| `ecu_face` | Punchline reaction (best for eye animation) | "Extreme close-up of the character's face filling most of the frame, [expression] …" |
| `pov_hands` | Phone, contract, food, controller | "First-person POV shot looking down at realistic hands [action] …" |
| `top_down` | Table inserts, lying in bed or on a mat | "Top-down overhead shot looking straight down at [subject] …" |
| `ots` | The character facing a crowd, coach or interviewer | "Over-the-shoulder shot from behind [hair + shirt], looking at [cast] …" |
| `two_shot` | With a cast member | "[character block] standing next to [cast description with cartoon head] …" |
| `back_view` | Walking into a stadium, room or museum | "Shot from behind: the character walks toward [place] …" |
| `low_feet` | Boots, slides, socks gags | "Low ground-level shot of [feet/legs] on [surface] …" |
| `aerial` | Big or absurd moments | "High aerial drone view looking down at [scene], the character tiny in the middle …" |
| `insert` | A prop alone (contract, can, trophy, food) | "Close-up product-style shot of [prop] on [surface] …" |

**Every prompt ends with:** `photorealistic [room/stadium], cinematic lighting, vertical 9:16, no text, no logos, no watermark` (for inserts: `no readable text`).

**Cast:** `[role] with a semi-realistic body in [clothes] and a flat 2D cartoon head (flat skin tone, thin dark outline, big white oval eyes with small black dot pupils, simple mouth)`. Use groups for crowds. Policy rules from `flow-prompts.md` apply: no real names, no minors in adult roles, friendly verbs.

## 3. Generate and process
1. `gflow_generate_image` (nano2, 9:16, `profile`/`project` per the shared Flow rulebook, the master as `reference_images`) for each shot. Generate the whole shot list **in one go, without asking first** (the script lock is the approval), one job at a time with the rulebook's pacing. Use the background runner for big batches.
2. Copy the results to `04_backgrounds\shots\<ID>.jpg` (IDs from the shot list: `H1`, `1a`, … `E1`). Reframe them to 1080×1920 with `python scripts/bg_process.py shots\<ID>.jpg plates --name <ID> --no-grade`. Keep the vivid Flow look (no grade).
3. Show a contact sheet. Re-roll any shot with a wrong kit, a real logo, a double head, a realistic face, or a main character who looks like someone else (e.g. lost the headband or long hair): repeat the signature features in CAPITALS in the re-roll prompt.

## 4. Eyes: `scripts/eye_locate.py`
```
python scripts/eye_locate.py 04_backgrounds/plates/2e.jpg [--box x0,y0,x1,y1] [--all] > 04_backgrounds/eyes/2e.json
```
- It finds the cartoon eyes (white ovals with a dark pupil) and prints `{"pairs": [{"eyes": [{cx, cy, rx, ry} ×2], "skin", "ink"}]}` in percent of the plate.
- Use `--box` to pick the main character when the cast also has eyes.
- Faces in wide shots work down to eyes about 20 px wide.
- Skip shots where the eyes are closed or the face is in profile.

In the shot JSON:
```json
"eyes": {"pair": <pair>, "looks": [{"at": 0.15, "dir": "l"}, {"at": 0.55, "dir": "r"}, {"at": 0.95, "dir": "c"}, {"at": 1.8, "dir": "up"}],
         "blink": true, "wide": [{"at": 1.8, "scale": 1.08}]}
```
- `dir` is one of `l`, `r`, `c`, `up`, `down`, `ul`, `ur`. Put a look change every 0.4–0.8 s on face shots, landing on words.
- `wide` pops the eyes slightly on a shock word. Keep it at or below 1.1, or the eyes cover the brows.

## 5. Shot JSON (premium)
```json
{"start": 6.83, "end": 9.85, "bg": "04_backgrounds/plates/2e.jpg", "camera": "push", "drift": 8, "enter": "cut",
 "eyes": {...}, "punch": {"at": 1.82, "pct": 14},
 "fx": [{"type": "money_rain", "at": 0.75, "dur": 1.7, "dir": "up", "n": 14}]}
```
- `camera`: `push`, `pull`, `pan-left` or `pan-right`. `drift` is in % (8–14).
- `enter`: `cut`, `zoom` or `whip`.
- `fx` (`scripts/zoomby_fx.py`):

| Type | Keys |
|---|---|
| `flash` | `at`, `dur` |
| `camera_flashes` | `at`, `dur`, `n` |
| `shake` | `at`, `dur`, `amt` px |
| `money_rain` | `at`, `dur`, `dir` up/down, `n` |
| `zz`, `hearts`, `question` | `at`, `x`, `y` |
| `ball_to_lens` | `at`, `dur` |
| `number` | `to`, `from`, `prefix`, `suffix`, `label`, `sub`, `x`, `y`, `size` (% of width, 19–26), `color`, `rot`, `at`, `dur` |

- Captions, badge (per-scene `badge_color`), bubbles and symbols come from the scene/shot keys (`build.md`). Show numbers with `number`, never `chart`.
- Any still longer than ~2.9 s gets a mid-shot `punch` (12 %) so nothing holds.
- Build, check, snapshot and render as in `build.md`.

## 6. Mixing
- Use `music.db = -26.2`.
- After a music-only change, keep the VO level by matching gain on speech frames against the previous render. Don't re-run loudnorm on the whole mix.
- Otherwise finish with `loudnorm=I=-13:TP=-1.5`.

## 7. After the render
Make the publish kit (`publish.md`): thumbnails with `scripts/publish_kit.py` and the `publish.md` copy.
