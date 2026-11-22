# Zoomby style spec (premium): look, motion, sound

Measured from 6 reference episodes (Haaland, Yamal, Mbappé, Ronaldo, Olise ×2; 25 fps, 47–65 s) and proven on the Ronaldinho video (`videos\2026-11-14-ronaldinho-weird-facts\`). Values marked *(m)* were measured. Override any parameter per video in `zoomby.project.json → params`.

## 0. Parameters (defaults)
```yaml
format:   { width: 1080, height: 1920, fps: 25, scenes: 8-10, seconds_per_fact: 4.5-6 }
badge:    { show: true, start_number: 10, color: "#8A3FE9", x_pct: 14, y_pct: 13, diameter_pct_w: 12 }
          # per-scene badge_color may follow the kit (e.g. Brazil yellow #FFD60A, Barcelona garnet #A50044)
caption:  { words_per_chunk: 2, min_chunk_s: 0.18, center_y_pct: 64, cap_height_pct_h: 3.2,
            font: "Montserrat", weight: 900, fill: "#FFFFFF", stroke: "#000000", stroke_px: 6, pop_from_scale: 0.9, pop_frames: 1 }
shots:    { per_fact: 3-4, median_s: 1.0-2.3, max_still_s: 2.9, framings_per_fact: ">=3 incl. one face close-up" }
camera:   { drift_pct: 8-14, punch_in_pct: 12-20, shake_frames: 3-6, zoom_whip: { scale: 1.38, blur_px: 22, dur_s: 0.22, max_ratio: 0.33 } }
eyes:     { dart_every_s: 0.4-0.8, blink_every_s: 2.3, widen_max: 1.1 }
numbers:  { style: "number pop", color: "#FFD60A", size_pct_w: 19-26, label: "white word under", sub: "small line above" }
audio:    { vo_wpm: 190, music_db: -26.2, master_lufs: -13 }
story:    { hook: "title-line | superlative question", flow: "connectors", ending: "legend | deadpan" }
publish:  { thumbnails: ["1080x1920 cover (embedded in the MP4)", "1280x720"], kit: "publish.md" }
```

## 1. Frame & safe zones
- Full-bleed 9:16; no bars, no blur bands.
- **Badge:** top-left, centre (14 %, 13 %), diameter ≈ 12 % of the width; a glossy sphere (light spot top-left → base colour → dark rim) with a heavy white numeral outlined in black. It appears with the first counted scene (never in the hook) and changes on the first frame of each scene.
- **Faces** in the upper 15–45 %; **caption centre** ≈ 64 % *(m 63–66)*; nothing important below 78 % (platform UI). Numbers and bubbles never cover the face or the badge.

## 2. Art
- **Character:** a **semi-realistic 3D body** (real hands, fabric folds, sitting, holding, leaning) in a **look-alike kit** (same colours and design, no badges, sponsors or numbers) with a **flat 2D cartoon head**: flat single skin tone, thin dark outline, big white oval eyes with small dark dot pupils, tiny nose line, simple mouth, hair as flat shapes, signature accessories (headband, moustache). Identity comes from hair, skin, accessories and kit; never a realistic face.
- **Scene:** every shot is one photoreal AI image with the character **inside** it, in cinematic light (warm interiors, golden hour, floodlit night, cold fluorescents for comedy).
- **Cast:** reporters, coaches, rivals, family, crowds all get cartoon heads in the same style; never a real-person photo.
- **Expression** is written into each shot's prompt (surprised, smug, laughing, heart eyes, proud with eyes closed, nervous).
- **Props:** literal and readable (gold bars, a pig, a contract, a service bell); products are unbranded look-alikes (plain blue/red cans).

## 3. Light, contrast, colour
- Keep Flow's vivid cinematic look (no extra grade on shot plates); high local contrast, saturated kits, warm highlights.
- The kit colours carry identity across shots.

## 4. Captions, numbers, bubbles
- **Captions:** 1–2 words, ALL CAPS, Montserrat 900, white with a black stroke and soft shadow, centred at ≈ 64 %, on screen 90–100 % of the runtime; a new chunk every 0.2–0.5 s on the word onset; 1-frame pop (0.9 → 1).
- **Numbers:** a **number pop**, never a chart card: big yellow digits with a thick black outline slam in (2.2 → 1), count up, punch (1.22×) with a yellow starburst, then float; white label word under it (GOALS, KILOS), optional small line above (IN ONE GAME, AGE 13). Place it in a clear area (sky, wall, empty side) away from face and badge.
- **Bubbles:** white comic oval, black outline, black heavy text (UNDERCOVER, BIG BRO, CHECK-IN?, BBQ!), 2–4 per video, popping on the punchline word; long words shrink to fit.
- **Symbols / FX text:** Zz, hearts, "?" — sparingly, on cue words.

## 5. Shots, motion, cuts
- **3–4 shots per fact**, cut on cue words; median shot 1.0–2.3 s *(m)*; any still longer than ~2.9 s gets a mid-shot punch-in.
- **Framings** (`premium.md` §2): wide, medium, cu_face, ecu_face, pov_hands, top_down, ots, two_shot, back_view, low_feet, aerial, insert — ≥ 3 per fact, one face close-up; the punchline usually on a reaction close-up or a sight-gag insert.
- **Camera never holds still** *(m ≈ 0 % static frames)*: push / pull / pan from frame 1 (drift 8–14 %), snap punch-in 12–20 % on the punchline word, 3–6 frame shake on impacts.
- **Transitions:** hard cuts; **zoom-whip** (scale 1.38 + 22 px blur → 1 in 0.22 s) into new locations or big beats, at most 1 in 3 cuts. No fades or wipes.
- **Eyes:** darts left/right/up every 0.4–0.8 s on face shots, blink every ~2.3 s, widen ≤ 1.1× on shock words.
- **FX:** camera flashes, white flash, shake, money rain, ball to lens, hearts, Zz, "?" — on cue words only.
- **Stills only by default.** The references use AI image→video for bodies; add it only on request after a 1-clip cost test.

## 6. Sound
- **VO:** recorded by the user; energetic comedic delivery ≈ 190 wpm *(m 160–225)*, starts on frame 1, no gaps. Spoken badge numbers are welcome.
- **Music:** upbeat playful bed (e.g. samba-funk for a Brazilian subject), looped to length, **−26.2 dB** under the VO.
- **SFX:** whoosh on every zoom-whip, impact on big beats, camera clicks under flashes, ping on number pops, pop on bubbles/punchlines, chime at the end.
- **Master:** ≈ −13 LUFS, peak ≤ −1 dBTP. After a music-only change keep the VO level by matching gain on speech frames.

## 7. Publish
- Thumbnails from a clean plate (the funniest face/prop moment, usually fact #1): 2–4 word hook in caption style (white line 1, yellow line 2), series line, badge number; vertical 1080×1920 (embedded as the MP4 cover) + 1280×720.
- `publish.md`: titles (main + A/B), descriptions, hashtags per platform, tags, pinned comment, posting checklist (`publish.md` reference).
