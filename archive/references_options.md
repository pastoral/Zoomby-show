# Writing the per-scene option menus

Both rounds use **AskUserQuestion, 4 scenes per call**: one question per scene, 3–4 options each, `multiSelect: false`.

- 8 scenes = 2 calls; 10 scenes = 3 calls (4 + 4 + 2, plus the hook and ending as questions in the last call if there is room).
- Put the recommended option first and mark it "(Recommended)".
- Options must be **genuinely different**: a different angle or device in Round 1, a different location or camera idea in Round 2. Don't offer four rewordings of one idea.
- The user can always pick "Other" and type their own; take it as given.
- Record every answer in `zoomby.project.json → scenes[i].round1` / `round2` right away.

## Round 1: story (before the storyboard)
Each scene question offers 3–4 **read-aloud lines** (set-up + punchline). Vary them by:
- **Angle:** which detail of the fact to lead with.
- **Punchline device:** see `story.md`.
- **Connector:** when the flow is "connectors".

Format:
- `header`: "Scene 7"
- `question`: "Scene 7 (badge 4): which line do you want for the [fact topic] fact?"
- option `label`: the device in ≤ 5 words, e.g. "Contrast flip".
- option `description`: the full line exactly as it will be spoken, e.g. "He eats cow heart and liver and burns 6,000 calories a day. That's not a diet, that's a crime scene."

Also ask in Round 1, once per video: the hook variant (3 options) and the ending variant (3–4 options).

## Round 2: visuals (after the character sheet, before the voice-over)
Round 2 runs in Stage 6, once the user's Flow images are in and checked. **Every package must use only images that exist**: the rigged front/side poses with the heads that were made, the action-pose images, the hands, props and cast in `03_character`, and the scene's background. Don't offer a pose, emotion or gesture that wasn't generated; name the files in the description (e.g. "main_run → front rig SMUG"). Optional extras the user made are fair game, and good material for variety.

Each scene question offers 3–4 **visual packages**. Each package fixes all five dimensions:
1. **Location/gag:** where the scene happens and what the character does (it becomes the Flow prompt).
2. **Camera + transition:** slow push-in / pan left / pull-out reveal / punch-in on the punchline, and whether the scene enters with a hard cut or a whip-blur.
3. **Acting:** the character's **emotion** (happy, laugh, smug, sad, angry, surprised, scared, confused, love) and **1–3 moves** timed to the line: walk/run in or out, hop, slide, lean on the punchline, jolt, shrug, slump, stomp, step back + tremble, celebrate, spin; plus at most one **hand gesture** (wave, point, thumbs up, fist pump, shaking fist, count).
4. **Data graphic** (only when the line has a real number, comparison or trend): a chart card — counter ("10,000"), bar/compare ("before 0 → after 8%"), line (a rise or crash), pie ("70%") — or "none".
5. **Caption/bubble:** the hero word to emphasise, plus a speech bubble (its text), a symbol (Zz, hearts, ?, sweat, flag) or none.

Format:
- option `label`: e.g. "Viking feast hall".
- option `description`: "Character in a Viking helmet at a long wooden table with bowls of heart and liver, warm lamplight · slow push-in, whip-blur in · SURPRISED, runs in from left, leans on 'crime scene', points · counter 0 → 6,000 KCAL · hero word CRIME".
- Vary the acting across the four packages too (e.g. one calm/smug, one big physical, one emotional), and across the video: no emotion more than 2 scenes in a row, 3–8 hand gestures and 1–4 charts per video.
- Use `preview` (markdown) when helpful: a 3-line shot plan (shot 1 / 2 / 3, about 1.5 s each). There is no voice-over yet, so estimate times at 190 wpm.
- Say in each package which shot, if any, is **speaking** (lips move); most packages need none.

Keep the packages varied across the video: no more than 3 scenes in a row in the same kind of location, at most 1 whip-blur every 2 scenes, and 2–4 bubbles per video in total.

## After each round
Summarise the picks in a compact table (scene, choice), then continue. After Round 2, write `storyboard_final.md` and `script_final.md` (`storyboard.md`) and ask for approval. That approval locks the script for the voice-over.

## Round 2 on the premium route: shot lists
Each option is a **shot list** for the fact (3–4 shots, 1.0–2.5 s each), not one package. Format the `description` as
`1) wide: <action> · 2) cu_face: <expression> · 3) top_down: <insert> · 4) ecu_face: <reaction> | camera: push + zoom-whip in, punch on "<word>" | fx: <fx>`.
Vary the four options by framing mix (one calm, one POV/insert-heavy, one face-heavy, one with cast), and keep at least 3 framings and one face close-up per option (`premium.md` §2).
