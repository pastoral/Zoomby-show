# Storyboards: initial (before the character sheet) and final (after it)

## Initial storyboard: `01_storyboard/storyboard_initial.md`
Written after Round 1. It tells the prompt sheet exactly which images to draw. Use one block per scene:

```
### Scene 3 · badge 8 · "sleep" fact
LINE:      He sleeps with five footballs on his bed. Not one. Five.
LOCATION:  cosy hotel bedroom at night, five footballs on the duvet   (bg idea → flow_prompt)
SHOTS:     1) wide, character walks in yawning  2) close-up, surprised at the balls  3) smug on the punchline
CHARACTER: outfit main · poses: walk, front · emotions: sleepy → surprised → smug
MOUTH:     closed; slightly open on "Five" only · SPEAKING: shot 3
HANDS:     count (5 fingers → use count3 + wave)  · PROPS: football ×5 (in the bg)  · CAST: none
CHART:     none          · BUBBLE/SYMBOL: Zz
```

Rules:
- **Mouth:** closed by default. Slightly open (`neutral_half`) only on shots where the character speaks a word to camera. Wide open only for laugh or surprised. Mark `SPEAKING` on the shots that need lip movement; in many scenes no shot needs it.
- **Variety:** across the video, use 3–6 different poses, 5–8 emotions, 3–8 hand gestures, and at most 1 supporting-cast design. Reuse the same outfit unless a gag needs another.
- **Charts:** only for real numbers, comparisons or trends from the verified script.
- **Backgrounds:** one per scene (a shot may reuse its scene's plate). Write the `flow_prompt` and a safer `flow_fallback` now.

End the file with the **asset list**, the union of all scenes:

| Type | File | Scenes |
|---|---|---|
| Pose | `main_front.png`, `main_walk.png`, … | 1, 3, 7 |
| Head | `head_neutral.png`, `head_neutral_half.png`, `head_surprised.png`, … | … |
| Hand | `hand_point.png`, … | … |
| Prop / cast | `prop_golden_boot.png`, `cast_goalkeeper.png` | … |
| Background | `scene01.png` … `scene10.png` | one each |

Mirror it into `zoomby.project.json`:
- `storyboard_initial`: one object per scene.
- `assets`: `character` (id, look in words only, skin), `outfits[]`, `poses[] {outfit, pose, emotion?, prompt? (custom pose), scenes}`, `heads[] {emotion, scenes}`, `hands[] {gesture, scenes}`, `props[]`, `cast[]`.
- Each scene's `flow_prompt` and `flow_fallback`.

`scripts/prompt_sheet.py` reads these. Standard pose ids: front, three_quarter_l, three_quarter_r, side_r, back, walk, run, jump, celebrate, point, arms_crossed, hands_hips, shrug, think, wave, sit, slump, surprised. Any other id needs a `prompt`.

## Image check (Stage 5)
After the user says the images are ready, write a short report in chat and add `assets.status` to the JSON (`supplied` / `missing` / `off-model` / `extra`):
- **Missing ★ items:** say which scenes they affect and offer either a redo prompt or a re-plan that uses images that exist.
- **Off-model:** a different face, hair, outfit colours or art style, text or watermark, a cropped body, or a non-white background. Suggest the fix (re-roll with the master pose as the reference, or the fallback prompt).
- **Extras:** optional poses, heads or hands that were made. List the gags they open up; Round 2 can use them.

## Final storyboard: `01_storyboard/storyboard_final.md`
Written after Round 2, with the same block format plus:
- `PACKAGE`: the chosen Round 2 option;
- `USES`: the exact files (rig + emotion, or a pose `src`, hands, props, background);
- `CAMERA`, `ENTER` (cut / whip), `MOVES` with the word each one lands on;
- `CHART`, `BUBBLE` / `SYMBOL`, `SPEAKING` shots.

Differences from the initial storyboard (a re-planned scene, a changed line) are marked **CHANGED** with a one-line reason.

Then write `script_final.md`: the hook, the lines with connectors, the ending, the word count and the estimated length (words ÷ 190 × 60 s). The user's approval **locks the script**, and the voice-over is recorded from this file.
