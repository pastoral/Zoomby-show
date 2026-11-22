# Zoomby style spec (look, motion, sound)

This spec was measured from 6 reference episodes (360×638, 25 fps, 47–65 s). Values marked *(m)* were measured. Override any parameter per video by changing it in `zoomby.project.json → params`.

## 0. Parameters (defaults)

```yaml
format:   { width: 1080, height: 1920, fps: 25, scenes: 10, seconds_per_scene: 4.5 }   # fps 25 (m) | 30
badge:    { show: true, start_number: 10, color: "#8A3FE9", x_pct: 14, y_pct: 13, diameter_pct_w: 12 }
          # colours seen: purple #8A3FE9 (m), silver #AFAFAB (m); hidden during the intro
caption:  { words_per_chunk: 2, min_chunk_s: 0.18, center_y_pct: 64, cap_height_pct_h: 3.2,
            font: "Montserrat", weight: 900, fill: "#FFFFFF", stroke: "#000000", stroke_px: 6,
            shadow: "0 4px 10px rgba(0,0,0,.55)", pop_from_scale: 0.9, pop_frames: 1 }
camera:   { drift_pct: 6, punch_in_pct: 20, whip_frames: 3, whip_blur_px: 40 }
character: { lip: "minimal", sway_deg: 1.6, nod_deg: 4 }   # lip: minimal (one small mouth-open per word) | full
acting:   { moves_per_shot: [1, 3], emotion_per_scene: true, hands_per_video: [3, 8], charts_per_video: [1, 4] }
look:     { mean_luma_pct: [32, 46], saturation: 0.45, warmth: 1.06, bg_blur_px: 2 }
audio:    { vo_wpm: 190, music_db: -18, sfx_db: -8, master_lufs: -13 }
story:    { hook: "title-line", flow: "connectors", ending: "deadpan" }
```

## 1. Frame & safe zones
- Full-bleed 9:16; no bars and no blur bands.
- **Badge:** top-left, centre at (14%, 13%), diameter ≈ 12% of the width. It is a glossy sphere: a radial gradient from a light spot at the top-left to the base colour, with a darker rim. The numeral is white, heavy, with a black outline. It appears with the first counted scene, never during the hook, and changes on the first frame of each scene.
- **Face zone:** the upper 15–45% of the height. **Caption centre:** ≈ 64% *(m 63–66)*. Keep everything important above 78% of the height (platform UI).

## 2. Art
- **Characters:** flat 2D head with a single skin tone, a **thick black outline** (≈ 6–9 px at 1080 w), white oval eyes with small black pupils, no nose or a tiny one, and a simple mouth. Identity comes from the hair silhouette, the outfit (kit, uniform, signature clothing) and skin tone. Never a realistic face.
- **Bodies:** semi-real or flat, in an accurate outfit. Supporting cast use the same head style.
- **Rig:** every main character is a **body layer + head layer** on a shared canvas (`scripts/rig_poses.py`), so the head tilts and nods on its own and heads swap for emotions without touching the body. Cartoon **hands** are separate small layers that sit on top of the body and gesture.
- **Emotion heads:** one head per emotion, all edited from the same neutral head so they match exactly: neutral, happy, laugh, smug, sad, angry, surprised, scared, confused, love, plus a side profile and a slightly-open-mouth neutral for lip-sync. Each scene shows the emotion the line calls for (shocked at a big number, sad at a loss, smug at a flex, scared at a danger).
- **Charts & graphs:** when a fact has a number, a comparison or a trend, show it as a chunky cartoon chart card: white card, 7 px black outline, hard black drop shadow, Montserrat 900, bright flat fills (`#FFD60A` yellow, `#3DDC84` green, `#4EA8FF` blue, `#FF5A5F` red). Types: bar, compare (2–3 bars), line (trend), counter (count-up number), pie (percentage).
- **Backgrounds:** photoreal, cinematic, AI-style locations, one per scene: interiors with warm practical lamps, golden-hour exteriors, dramatic skies.
- **Props:** literal and slightly oversized for the gag.

## 3. Light, contrast, colour
- Mean brightness 32–46% *(m)*, high local contrast (luma std ≈ 67–77 *(m)*), saturation ≈ 0.40–0.55 *(m)*.
- Backgrounds are warm and cinematic and slightly soft (shallow depth of field). Characters are flat-lit; the outline separates them from the background.
- Soft contact shadows (20–40%) under feet and props. No drop shadow on the character apart from a faint ground shadow.
- Palette clusters *(m)*: `#0E0A0A` shadows · `#372E1F`/`#765830` warm interiors · `#EBE9E9` whites · `#D2BBA5`/`#C77E4E` skin and warm walls · `#91877F`/`#495563` neutrals · `#86A9D9` sky · plus the subject's outfit colours.

## 4. Captions & bubbles
- **1–2 words per chunk**, ALL CAPS, heavy geometric sans (Montserrat 900), white with a black stroke and a soft shadow, centred at about 64%. They are on screen 90–100% of the runtime.
- A new chunk every 0.2–0.5 s, synced to the word onset. **Pop:** frame 1 at about 90% scale and 85% opacity, then frame 2 at 100%.
- Numbers are written as digits ("1.63M", "3000", "$144"). Two lines are allowed for short pairs.
- **Speech bubbles:** a white comic bubble with a black outline and black bold text ("WEIRDO", "Name?", ❤, "YES"), placed near the speaker's head with a 6-frame bounce in. Use 0–4 per video.
- **Symbols:** Zz, floating hearts, ?, sweat drop, flags. They pop in and gently bob.

## 5. Shots, motion, cuts
- **Scene types:**
  - **Hero shot:** stadium or landmark, the character running, posing, or a name close-up.
  - **Gag illustration:** the literal fact.
  - **Reaction close-up:** the head fills the frame.
  - **Proof shot:** TV, phone, poster, museum or document.
- **2–4 shots per scene**; the hook has 3–4 hero shots in about 3 s.
- **Cut-out animation (character acting):** the character is never a frozen sticker.
  - **Always on:** idle sway and breathing; the head nods and tilts on the spoken words.
  - **Lips: minimal.** One small mouth-open per spoken word (words shorter than 0.16 s are skipped), closed between words. The face and body carry the performance, not the mouth.
  - **Locomotion:** walk or run in from the side (step bob + rock), walk/run out, slide in on whips, hop in on cuts.
  - **Body:** lean in on punchlines, jolt on a shock, shrug, slump (sad), stomp with a red glow (angry), step back + tremble (scared), celebrate hops (happy), laughing bounce, spin, turn.
  - **Hands:** wave, point, thumbs up, fist pump, shaking fist, counting; at most one gesture per shot, 3–8 per video.
  - **Emotions:** pick the head for the line's feeling; the builder adds the matching body move and a small symbol next to the head (✨ happy, 💧 sad, 💢 angry, ❗ surprised, 💦 scared, ❓ confused, ❤️ love).
  - 1–3 moves per shot, timed to word onsets; the biggest move lands on the punchline.
- **Charts:** a chart card pops in on the number's word and animates (bars grow, line draws, counter counts up, pie fills) within about 1 s. Keep it in the upper half (centre y 26–36%) so it never covers the caption at 64%; put the character lower or to one side in that shot. 1–4 charts per video, only for real numbers from the script.
- Flying props and blinks are still welcome as hand edits (see `build.md` → Fine control).
- **The camera never holds still** *(m ≈ 0% static frames)*. Use a push-in, pull-out or pan of 3–10% per shot (sine in-out). A punch-in of about 20% can land on a punchline.
- **Cuts:** a real scene change every ≈ 1.2–2.6 s *(m)*, hard cuts on phrase boundaries. **Whip-blur** (3 frames of 40 px directional blur plus a slide) goes into stadium and action shots. No fades, dips or wipes.

## 6. Sound
- **VO:** supplied by the user. The reference voice is male, energetic and comedic at about 190 wpm *(m 160–225)*, starts on frame 1 and never leaves a gap.
- **Music:** an upbeat, playful bed, continuous, about 18 dB under the VO.
- **SFX:** a crowd swell and whoosh on the hook, whooshes on whips, pops on bubbles and symbols, comedic hits, and a bleep on censored words.
- **Master:** about −12 to −14 LUFS *(m −11.7 to −14.3)*, LRA ≈ 3.

## 7. Premium look (default route, see premium.md)
- Semi-realistic 3D body in a look-alike kit + flat 2D cartoon head (flat skin, thin dark outline, big white oval eyes with small dark pupils).
- 24–41 cuts per ~60 s video, median shot 1.0–2.3 s; 3–4 shots per fact; at least 3 framings per fact incl. one face close-up.
- Camera: push/pull/pan with `drift` 8–14 %, snap punch-in 12–20 % on the punchline word, 3–6 frame shake on impacts, zoom-whip (scale 1.38 + 22 px blur) into new locations.
- Face: eye darts every 0.4–0.8 s on face shots, blink every 2–3 s, eyes pop ≤1.1× on shock words.
- Numbers as caption-style number pops (no chart cards).
- Music bed at −26.2 dB under the VO; whoosh/impact on every zoom-whip; camera clicks under flashes; final mix ≈ −13 LUFS.
