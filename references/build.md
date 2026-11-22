# Building and rendering a Zoomby video (HyperFrames, premium)

## Folder layout (one per video)
See SKILL.md → Settings. Asset paths in the JSON are relative to the **video folder** (`paths.root`, default `..` from the JSON). `build_project.py` copies every referenced file from outside `06_project` into `06_project/media/` (same sub-path, refreshed when the source is newer), so the HyperFrames project is self-contained. Paths that already exist inside `06_project` (e.g. `audio/music.mp3`) are used as they are.

Build: `python scripts/build_project.py 06_project/zoomby.project.json 06_project`.

## Project JSON
- **`words`:** word timings from the VO (`05_vo/vo_words.json`). Captions are generated from them automatically: 1–2 word chunks, ALL CAPS, popped in on the word onset, trailing periods/commas dropped.
- **One `scene` per countdown item, plus the hook and the ending.** `badge` is the number shown (null for hook/ending); optional `badge_color` per scene. Scene boundaries are the VO times where that scene's line starts (spoken badge numbers mark them well).
- **`shots`** (3–4 per fact, cut on cue words):
```json
{"start": 21.38, "end": 24.36, "bg": "04_backgrounds/plates/2e.jpg", "camera": "push", "drift": 8, "enter": "cut",
 "eyes": {"pair": {...eye_locate pair...}, "looks": [{"at": 0.15, "dir": "l"}, {"at": 0.55, "dir": "r"}], "blink": true,
          "wide": [{"at": 1.82, "scale": 1.08}]},
 "punch": {"at": 1.82, "pct": 14},
 "bubble": {"text": "BBQ!", "x": 70, "y": 22, "at": 1.1},
 "fx": [{"type": "money_rain", "at": 0.75, "dur": 1.7, "dir": "up", "n": 14},
        {"type": "number", "at": 0.15, "to": 23, "label": "GOALS", "sub": "IN ONE GAME, AGE 13", "x": 50, "y": 27, "size": 26}]}
```
  - `camera`: `push` | `pull` | `pan-left` | `pan-right`; `drift` in % (8–14).
  - `enter`: `cut` | `zoom` (zoom-whip: scale 1.38 + 22 px blur → 1 in 0.22 s) | `whip` (linear blur slide).
  - `punch`: snap scale-up at `at` (s from shot start) by `pct`.
  - `eyes`: SVG eyes drawn over the still's own cartoon eyes inside the camera layer (they follow camera moves); `dir` = `l` `r` `c` `up` `down` `ul` `ur`.
  - `fx` (`scripts/zoomby_fx.py`): `flash`, `camera_flashes`, `shake`, `money_rain`, `zz`, `hearts`, `question`, `ball_to_lens`, `number` — keys in `premium.md` §5.
  - `bubble` / `symbol`: comic bubble or floating symbol; long bubble words shrink to fit.
- **`music`:** `{"src": "audio/music.mp3", "db": -26.2}`; **`sfx`:** `[{"src", "t", "dur", "db"}]`; **`vo`:** `{"src": "05_vo/vo.mp3"}`.
- **Safe zones:** faces 15–45 %, caption ≈ 64 %; numbers and bubbles never on a face or the badge.

## What `build_project.py` writes
- Root 1080×1920, `data-fps` from the JSON, duration = `duration` or the last shot's end.
- **Shot:** a `.clip` with whip wrapper › punch wrapper › camera wrapper › plate `<img>` + eye SVG; FX and number pops sit above the camera layer.
- **Badge:** a `.clip` per counted scene (glossy sphere, white numeral outlined in black, per-scene colour).
- **Captions:** a `.clip` per chunk, Montserrat 900 (local `fonts/Montserrat.ttf`), white with an 8-direction black outline and a soft shadow, 1-frame pop.
- **Audio:** `<audio id="vo">`, music at its `db`, SFX at their times (every `<audio>` has an id).
- All tweens are seek-safe (`tl.set` at the shot start + `fromTo` with `immediateRender:false`).

## Check → review → render
```
cd <video>/06_project
npx hyperframes check                        # fix every error; re-run build_project.py after JSON edits
npx hyperframes snapshot --at 0.9,2.6,…      # 16–24 frames + frames inside an eye dart, a number pop, an FX moment
npx hyperframes render -o ../07_render/<short-topic>.mp4   # only after the user agrees; run in the background
```
- Expected `check` warnings (keep them; they are the Zoomby style): `line_unread`, `nested_structure_needs_subcomposition`, `timeline_track_too_dense`, `duplicate_media_discovery_risk`. Fix every **error**.
- Snapshot PNGs land in `.hyperframes/artifacts/snapshots/<id>/`; deep video folders can exceed Windows MAX_PATH for Python, so copy them with the shell to a short path before reading them in Python.
- **Loudness:** first render → `ffmpeg -i raw.mp4 -c:v copy -af loudnorm=I=-13:TP=-1.5:LRA=11 -ar 48000 -c:a aac -b:a 192k out.mp4`. Re-render after a music-only change → measure momentary loudness (`ebur128=metadata=1`) of the previous render and the new raw render, apply the median speech-frame difference as `volume=<dB>` + `alimiter=limit=0.84`, so the VO stays identical.
- Afterwards check: −12 to −14 LUFS, no silent gaps (`silencedetect=n=-45dB:d=0.8`), badge count = fact count. Keep earlier renders as `<slug>_vN-<label>.mp4`.
- Then make the publish kit (`publish.md`).

## Fine control
For anything the generator doesn't cover, edit `index.html` **after** the final build following `/hyperframes-core` and `/hyperframes-animation`, and note each hand edit in the JSON (`"manual_edits": [...]`) so a rebuild doesn't silently drop it.
