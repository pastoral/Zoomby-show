# Writing the per-scene option menus

Both rounds use **AskUserQuestion, 4 scenes per call**: one question per scene, 3–4 options each, `multiSelect: false`.

- 8 scenes = 2 calls; 10 scenes = 3 calls (4 + 4 + 2, plus the hook and ending as questions in the last call if there is room).
- Put the recommended option first and mark it "(Recommended)".
- Options must be **genuinely different**: a different angle or device in Round 1, a different framing mix or gag in Round 2. Don't offer four rewordings of one idea.
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
- option `description`: the full line exactly as it will be spoken.

Also ask in Round 1, once per video: the hook variant (3 options), the ending variant (3–4 options), the badge colour (or "follows the kit") and connectors vs rapid-fire.

## Round 2: shot lists (after the character master, before the voice-over)
Each scene question offers 3–4 **shot lists** for the fact: 3–4 shots of 1.0–2.5 s, each from the framing menu in `premium.md` §2.

Format:
- option `label`: the idea in ≤ 5 words, e.g. "Sip then shock".
- option `description`: `1) wide: <picture> · 2) medium: <action> · 3) top_down: <insert> · 4) ecu_face: <reaction> | camera: push, zoom-whip in, punch on "<word>" | fx: <flashes / shake / number pop / bubble>`.

Rules:
- Every option has ≥ 3 framings and one face close-up; the punchline lands on the last shot (reaction close-up or sight-gag insert).
- Vary the four options by framing mix: one face-heavy, one POV/insert-heavy, one with cast, one big wide/aerial.
- Number facts get a **number pop** (`fx` type `number`) in the option, never a chart card.
- Across the video: at most 1 zoom-whip in 3 cuts, 2–4 bubbles in total, no more than 3 scenes in a row in the same kind of location, and no expression more than 2 shots in a row.
- Use `preview` (markdown) when helpful: the shot list with estimated times at 190 wpm.

## After each round
Summarise the picks in a compact table (scene, choice), then continue. After Round 2, write `shotlist.md`, `storyboard_final.md` and `script_final.md` (`storyboard.md`) and ask for approval. That approval locks the script for the voice-over.
