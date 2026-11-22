# Building and rendering a Zoomby video (HyperFrames)

## Folder layout (one per video)
`<Subject>\2D Animation\videos\YYYY-MM-DD-<short-topic>\` (see SKILL.md → Settings):
```
00_ideas.md
01_storyboard/   storyboard_initial.md, storyboard_final.md, script_final.md
02_flow_prompts/ flow_prompt_sheet.docx/.md/.json
03_character/    raw/ (user's Flow images) · body/<outfit>_<pose>.png · heads/head_<emotion>.png · hands/hand_<gesture>.png
                 props/prop_<id>.png, cast_<id>.png · rig/ (rig_poses.py: <outfit>_body.png, <outfit>_<emotion>.png, rigs.json)
04_backgrounds/  raw/sceneNN.png (untouched) · sceneNN.jpg + manifest.json (bg_process.py)
05_vo/           vo.wav (the user's, never re-written) · vo_words.json
06_project/      zoomby.project.json · index.html (written by build_project.py: edit the JSON, not this) · fonts/ · audio/ (music, sfx) · media/ (copied)
07_render/       <short-topic>.mp4
```
- Asset paths in the JSON are relative to the **video folder** (`paths.root`, default `..` from the JSON). `build_project.py` copies every referenced file from outside `06_project` into `06_project/media/` (same sub-path, refreshed when the source is newer), so the HyperFrames project is self-contained. Paths that already exist inside `06_project` (e.g. `audio/music.mp3`) are used as they are.
- Build: `python scripts/build_project.py 06_project/zoomby.project.json 06_project`.

## From choices to JSON
- **`words`:** word timings from the VO transcript (`npx hyperframes transcribe ../05_vo/vo.wav --json`, or local Whisper). Captions are generated from them automatically: 1–2 word chunks, ALL CAPS, popped in on the word onset.
- **One `scene` per countdown item, plus the hook.** `badge` is the number shown (null for the hook). Scene boundaries are the VO times where that scene's line starts and the next one starts.
- **`shots`:** 2–4 per scene, splitting the scene at phrase boundaries (gag set-up → action → reaction). Each shot has:
  - `bg`: the processed plate;
  - `camera`: `push` | `pull` | `pan-left` | `pan-right` | `none`;
  - `enter`: `cut` | `whip`;
  - `characters[]`: see **Character acting** below;
  - optional `bubble {text,x,y,at}`, `symbol {text,x,y,at}`, `punch {at,pct}`, `chart {...}` (see **Charts**).
- **Safe zones:** keep the character's face between y 15–45%. The caption sits at y ≈ 64%, so don't put a face, bubble or chart there.

## Character acting (characters[] keys)
Build the rig once per video: cut heads/hands with `scripts/cutout_white.py`, then `python scripts/rig_poses.py 03_character` and paste `03_character/rig/rigs.json` into the project JSON as `"rigs"`. Then a character is just:
```json
{"rig": "tux", "emotion": "surprised", "x": 40, "y": 60, "h": 62,
 "moves": [{"type": "run", "at": 0, "amt": -60, "dur": 0.8}, {"type": "lean", "at": 1.9, "amt": 6}],
 "hands": [{"src": "03_character/hands/hand_point.png", "anim": "point", "at": 1.9, "x": 78, "y": 42, "h": 15}]}
```
- **Placement:** `x`/`y` centre and `h` height in % of the frame; `flip`; `talk` (lip-sync on/off).
- **Rig + emotion:** `rig` picks `rigs[name]` (body, neck pivot, heads, mouths). `emotion` picks the head (falls back sensibly when a head is missing: angry→shock, scared→shock, happy→laugh…) and, unless `auto_act: false`, adds the matching body move and a small symbol by the head (`emotion_symbol: false` to drop it, or `symbol: "…"` to change it). Emotions: neutral, talk, happy, laugh, smug, sad, angry, surprised, shock, scared, confused, love.
- **Explicit layers** still work instead of `rig`: `src` (body or full image), `head`, `neck [x%, y%]`, `mouth`, `mouth_half`.
- **Lip-sync (only when speaking):** the lips move only on shots with `"speaking": true` (or a character with `"talk": true`); everywhere else the mouth stays as the head was drawn. `params.character.lip` = `"minimal"` (default: one small half-open mouth per word ≥ 0.16 s, closed between words), `"full"` (closed › half › open › half every `mouth_s`) or `"none"` (no lip movement anywhere). Per character: `"lip": "full"`. `params.character.talk_default: "always"` restores the old talk-on-every-shot behaviour.
- **Action poses:** a pose image like `body/main_run.png` (expression drawn in) is used directly: `{"src": "03_character/body/main_run.png", "x": 50, "y": 62, "h": 55, "moves": [...]}`, with no `rig` and no head swap. Moves, hands and symbols still work.
- **Always-on acting:** idle sway (`sway` degrees, default 1.6, use ~0.8 for close-ups) and breathing; head nods on the words (`nod: false`, `nod_amp`). `idle: false` turns sway off.
- **`moves[]`** — `{type, at (s from shot start), amt?, dur?}` on the body (head moves where noted):

| type | what it does | amt / dur |
|---|---|---|
| `walk` / `run` | enters from the side to its spot with step bob + rocking (run leans forward, faster steps) | `amt` = start offset in % of width (−60 = from the left), `dur` |
| `walk_out` / `run_out` | leaves the frame | `amt` = end offset (+70 = exits right), `dur` |
| `hop` | jumps in, squash on landing | `amt` = height (fraction of frame, 0.05) |
| `slide_l` / `slide_r` | slides in from the left/right with overshoot | — |
| `pop` | scales up from 20% | — |
| `lean` | leans in (rotation + slight scale) and back — punchlines | `amt` degrees (±), `dur` hold |
| `jolt` | shocked jump with elastic settle | — |
| `shake` / `tremble` | side shake (hit) / small fast shiver (scared) | `amt` px, `dur` |
| `bounce` | laughing up-down bounce | `amt`, `dur` |
| `celebrate` | two happy hops with a wiggle | — |
| `slump` | sad: sinks, droops, head down | `dur` |
| `stomp` | angry: stomp, shake, red glow | `dur` |
| `step_back` | scared/surprised hop backwards | `amt` % of width |
| `shrug` | shoulders up + head tilt | — |
| `turn` | flips to face the other way for the rest of the shot | — |
| `spin` | 360° spin | `dur` |
| `wobble` | slow rocking (being carried, dizzy) | `amt`, `dur` |
| `tilt` (head) | head tilt and back | `amt` degrees, `dur` |
| `nod` (head) | yes-nod | `times` |

- **`hands[]`** — `{src, anim, at, dur?, x, y, h, pivot?, flip?}`: a cartoon hand layer inside the character (it follows every body move). `x`/`y` are the hand's centre in % of the **character box**, `h` its height in % of the box (12–18 looks right). `anim`: `wave`, `point`, `thumbs`, `fist_pump`, `shake_fist`, `count`. It pops in at `at`, gestures, and fades before the shot ends.
- Moves in the same shot should not fight over the same property at the same time (e.g. `walk` and `lean` both rotate): space them out by their durations.

## Charts (shot `chart` key)
One animated chart card per shot, above the camera layer (punch-ins don't scale it):
```json
"chart": {"type": "counter", "from": 0, "to": 10000, "suffix": " PAIRS", "title": "Sneakers owned", "x": 50, "y": 28, "w": 80, "h": 18, "at": 0.4}
"chart": {"type": "compare", "data": [0, 8], "labels": ["before", "after"], "suffix": "%", "title": "WW stock", "at": 0.3}
"chart": {"type": "line", "data": [10, 11, 10.5, 12, 18], "suffix": "%", "title": "Stock price", "color": "#3DDC84"}
"chart": {"type": "pie", "to": 70, "title": "Of his time on the golf course"}
"chart": {"type": "bar", "data": [3, 7], "labels": ["Year 1", "Year 2"], "prefix": "$", "suffix": "M"}
```
- `type`: `bar` | `compare` (multi-colour bars) | `line` (draws on) | `counter` (counts up from `from` to `to`, `dur` default 1.1 s) | `pie` (`to` = percent).
- Position/size: `x`, `y` centre and `w`, `h` in % of the frame (defaults 50, 30, 78, 24); `at` = pop-in time in the shot; `title`, `prefix`, `suffix`, `color`, `colors`.
- Use only real numbers from the script, put the card in the upper half (y 24–36%), and move the character lower or to the side for that shot.

## What `scripts/build_project.py` writes
- Root 1080×1920, `data-fps` from the JSON, duration = the last shot's end.
- **Shot:** a `.clip` with whip wrapper > punch wrapper > camera wrapper > background `<img>` + character `<div>`s.
  - The camera tween moves the **single background plate together with the characters** (push/pull ≈ 6%, pan ±5% at 1.08 scale). There are no depth layers.
  - Whip: 3 frames of 40 px blur plus an 18% slide.
  - Punch: an instant scale set.
- **Characters:** `#cid` (position) › `#cid-fx` (keyframed moves, origin at the feet) › `#cid-idle` (sway/breath) › flip › body + `#cid-head` (origin at the neck; head images + mouths) + `#cid-hN` hand layers. All tweens are explicit `fromTo` with `immediateRender:false` and a reset `tl.set` at the shot start, so any frame can be seeked. The code lives in `scripts/zoomby_motion.py`.
- **Charts:** a `.ch-card` inside the whip layer, popping in and animating with GSAP (bars `scaleY`, SVG `strokeDashoffset`, counter via a tweened number).
- **Badge:** a `.clip` per counted scene, a glossy radial-gradient sphere with a white numeral outlined in black, top-left.
- **Captions:** a `.clip` per chunk, Montserrat 900 (local `fonts/Montserrat.ttf`, OFL), white with an 8-direction black outline plus a soft shadow. The pop is a 1-frame scale from 0.9 to 1.
- **Bubbles and symbols:** back-out pop; symbols bob.
- **Audio:** `<audio id="vo">` at 1.0, music at the `db` value, and SFX at their times. Every `<audio>` has an id (lint rule).

## Check → review → render
```
cd <video>/06_project
npx hyperframes check                       # fix every error; re-run build_project.py after JSON edits
npx hyperframes snapshot --at 1,5,12,25,40  # show these frames to the user
npx hyperframes render -o ../07_render/<short-topic>.mp4   # only after the user agrees
```
- **Expected `check` warnings: keep them, they are the Zoomby style** (the skill rule is to keep what the reference style does):
  - `line_unread`: captions are on screen 0.2–0.5 s by design.
  - `nested_structure_needs_subcomposition`: shots use wrapper divs.
  - `timeline_track_too_dense`: many caption clips.
  - `duplicate_media_discovery_risk`: the same plate is reused in two shots.

  Fix every **error**, and any other warning.
- Use `--fps 25` (or the project fps) when rendering in the cloud: `npx hyperframes cloud render --fps 25 --quality high -o ../07_render/<short-topic>.mp4`. **Ask first**, since this may use credits.
- Afterwards, check: loudness ≈ −12 to −14 LUFS (`ffmpeg -i ../07_render/<short-topic>.mp4 -af ebur128 -f null -`), no silent gaps, badge count = fact count.

## Fine control
- For anything the generator doesn't cover (a thrown prop, a falling-money effect, a flag pop), edit `index.html` **after** the final build, following `/hyperframes-core` and `/hyperframes-animation`. Note each hand edit in the JSON (`"manual_edits": [...]`) so a rebuild doesn't silently drop it.
- For the loudness mix and ducking of the music under the VO, use `/hyperframes-audio` (`data-automation` volume lane).

## Premium-route shot keys (scripts/zoomby_fx.py, scripts/eye_locate.py)
- `bg`: the processed shot plate (the character is inside the image; no `characters` needed).
- `drift`: camera move amount in % for this shot (premium 8–14).
- `enter: "zoom"`: zoom-whip in (scale 1.38 + blur → 1 in 0.22 s).
- `eyes`: `{"pair": <eye_locate pair>, "looks": [{"at", "dir"}], "blink": true, "wide": [{"at", "scale"}]}` — SVG eyes drawn over the still's own eyes inside the camera layer, so they follow camera moves.
- `fx`: `flash`, `camera_flashes`, `shake`, `money_rain`, `zz`, `hearts`, `question`, `ball_to_lens` (keys in `premium.md` §5).
- Per-scene `badge_color` overrides `params.badge.color`.
