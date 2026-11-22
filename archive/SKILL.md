---
name: zoomby-show
description: Make a Zoomby Show style vertical short on any topic. Default premium look - semi-realistic 3D bodies with flat 2D cartoon heads inside AI-generated photoreal scene shots from Google Flow, many framings, 1-2 s cuts, animated eye darts and blinks, zoom-whips, shake and foreground FX - plus a 10→1 countdown badge, 1-2 word pop captions and a fast comedic voice-over. Other routes - SVG puppets drawn in code, or a Flow prompt sheet for a hand-made character sheet. Interactive - suggests 5 topics, creates an organised video folder, drafts the story with 3-4 line options per scene, storyboards, offers 3-4 shot-list options per scene, takes the user's voice-over and renders an MP4 with HyperFrames. Use for "Zoomby video", "Zoomby style", "10 weird things about…" cartoon shorts, Zoomby topic ideas, or a Flow character prompt sheet.
---

# Zoomby Show video maker

You make an 8–10 scene vertical short in the Zoomby Show style, and **the user chooses every scene**. Work through the stages in order and never skip a user checkpoint.

- Look and sound: `references/style.md`.
- Writing and topics: `references/story.md`.
- Storyboards: `references/storyboard.md`.
- Flow prompts: `references/flow-prompts.md`.
- Option menus: `references/options.md`.
- Build: `references/build.md`.
- **Premium route (default): `references/premium.md`.**
- Code-drawn puppets: `references/puppet.md`.
- Reference frames: `assets/reference/`.

## Settings
- **VIDEOS_BASE:** `%VIDEO_WORK_ROOT%\<Subject>\2D Animation\videos\`
  - `<Subject>` is `Football` for football topics. Other subjects get a category name (e.g. `Science`, `History`, `Animals`, `Celebrities`); create it if it is new.
- **Video folder:** `VIDEOS_BASE\YYYY-MM-DD-<short-topic>\`, using today's date and a 3–5 word kebab-case topic (e.g. `2026-11-14-ronaldinho-weird-facts`). Create it, with the layout below, **right after the topic is chosen**:
  ```
  00_ideas.md            topic, angle, verified facts, brief answers
  01_storyboard\         storyboard_initial.md, storyboard_final.md, script_final.md
  02_flow_prompts\       flow_prompt_sheet.docx / .md   (scripts/prompt_sheet.py)
  03_character\raw\      user's Flow images (file names from the sheet)
  03_character\body\ heads\ hands\ props\ rig\    cut-outs + rigs.json
  04_backgrounds\raw\    Flow images / user photos;  04_backgrounds\sceneNN.jpg + manifest.json (processed)
  05_vo\                 voice-over + word-level transcript json
  06_project\            zoomby.project.json, index.html, fonts\, audio\ (music, sfx), snapshots
  07_render\             <short-topic>.mp4
  ```
- **Topic log:** `VIDEOS_BASE\_ideas\YYYY-MM-DD-topics.md`.
- **State:** `06_project\zoomby.project.json` (schema: `templates/zoomby.project.example.json`). Update `stage` after every stage, so `/zoomby-show` on an existing folder resumes where it stopped.
- **Asset paths** in the JSON are relative to the video folder (`03_character/…`, `04_backgrounds/…`, `05_vo/…`).

**Who provides what:**

| Item | Provided by |
|---|---|
| Topic ideas, story, options, storyboards, Flow prompt sheet, captions, animation, sound bed, render | Claude |
| Topic pick, script and storyboard approvals | User |
| Characters: **premium route** = Claude generates every shot (character inside the scene) in Google Flow and animates the eyes; **code route** = SVG puppets drawn by Claude (`03_character\puppet.json`); **Flow route** = images the user makes in Google Flow from the prompt sheet | Claude / User |
| Backgrounds | Google Flow: Claude via the `google-flow` MCP (after a yes on prompts + credits), or the user by hand from the sheet, or the user's own photos |
| Recorded voice-over, after the final storyboard | User |

## Stage 1: Topic + brief
1. If the user gave no topic, ask in one AskUserQuestion: "Suggest 5 topics" or "I have a topic". The question also covers the brief:
   - scenes (8 or 10),
   - hook (title line, superlative question, or shocking fact first),
   - ending (cliffhanger, deadpan, simile, legend or gag),
   - badge colour,
   - **character route:** **premium** (recommended: the real Zoomby look; Claude generates about 30 scene shots in Google Flow with the semi-real body and cartoon head inside each scene), code (SVG puppets drawn by Claude: free, any pose, simpler look) or Flow (the user draws a character sheet in Google Flow).

   Use the defaults from `references/style.md` for everything else; the user can override any parameter (§0).
2. **5 topics:** follow `references/story.md` → *Topic suggestions*.
   - Read `VIDEOS_BASE\_ideas\` and the existing video folders first, to avoid repeats.
   - Write a numbered list: title, angle, 3 sample facts, gag locations.
   - Save it to `_ideas\YYYY-MM-DD-topics.md`, then stop. The user replies with a number or their own topic.
3. Pick the `<Subject>` and short topic, tell the user the folder path, create the folder tree, and write `00_ideas.md`.

## Stage 2: Story + Round 1 (lines)
1. Research and **verify every fact**. Use web search when available; write "reportedly" for anything you can't confirm.
2. Order the scenes mild → wild, with the best one last (#1).
3. Offer 3–4 line options per scene (`references/options.md` → *Round 1*): AskUserQuestion, **4 scenes per call**.
4. Assemble the draft script.

## Stage 3: Initial storyboard
Write `01_storyboard\storyboard_initial.md` following `references/storyboard.md`. For each scene, it covers:
- the line, location/gag and background idea;
- the character's poses and actions;
- the emotion and **mouth state** (closed by default, slightly open only when speaking, wide only for laugh/surprise), and whether the character is **speaking**;
- hands, outfit, props, supporting cast, and a chart if the line has a number.

It ends with the **asset list**. Mirror it into the JSON (`storyboard_initial`, `assets`). Show a summary and **stop for approval or edits**.

## Stage 4 (premium route): character master
1. Write the fixed **character block** (`references/premium.md` §1, looks only) and store it as `premium.character_block` in the project JSON; set `character_route: "premium"`.
2. `gflow_auth_status`, `gflow_get_credits`, then generate the master full-body image per outfit (nano2, 9:16) into `03_character\master_<outfit>.jpg`. **Stop for approval** and re-roll on request ("older", "darker skin", "more cartoony head").
3. Flow does text-to-image only on this account (reference images and edits are refused), so every later prompt repeats the character block word for word.
4. Skip to Stage 6; the scene shots are generated after Round 2.

## Stage 4 (code route): SVG puppets
1. Write `03_character\puppet.json` from the storyboard (`references/puppet.md`): the main character (looks only: skin, hair style, headband, facial hair, build, one outfit per shirt/costume), the supporting cast, and the props. Set `character_route: "code"` and `puppet_spec` in the project JSON.
2. Run `python scripts/puppet_sheet.py 03_character\puppet.json` and show every page of `03_character\sheet\`. **Stop for approval or tweaks** (hair, skin, kit colours, build), re-render after each change.
3. Backgrounds: run `scripts/prompt_sheet.py` (it writes a backgrounds-only sheet on the code route). If the user wants Claude to generate them, use the `google-flow` MCP: `gflow_auth_status`, `gflow_get_credits`, show the prompts + balance, and **after a yes** call `gflow_generate_image` (`model: "nano2"`, `aspect: "9:16"`, `project_name: "zoomby-<slug>"`) 2–3 at a time; copy each result to `04_backgrounds\raw\sceneNN.png`; on a refusal retry once with `flow_fallback`; on a 403 stop and tell the user. Then skip to Stage 6.

## Stage 4 (Flow route): Google Flow prompt sheet
1. Fill `assets.character` (looks only, **no real names**), the outfits, and each scene's `flow_prompt` / `flow_fallback` (`references/flow-prompts.md`).
2. Run `python scripts/prompt_sheet.py 06_project\zoomby.project.json 02_flow_prompts`. It writes the .docx and .md, with the full pose, head and hand library; this video's needs are marked ★.
3. Give the user the file paths and the key rules:
   - master front pose first, used as the reference for everything else;
   - edit the cartoon head for expressions;
   - save under the exact file names into `03_character\raw\` and `04_backgrounds\raw\`.
4. **Do not call Flow yourself.** Use the `google-flow` MCP only if the user asks, and only after showing the prompts and credits and getting a yes.

## Stage 5 (Flow route): Image hand-off + check
Wait for the user to say the images are in place (or to send them). Then:
- inventory `03_character\raw` and `04_backgrounds\raw` against the asset list;
- show a contact sheet;
- report what is **missing**, what is **off-model** (a different face, outfit or style; text in the image), and any **extras** that open up gags.

The user re-generates or accepts. Then cut the images out:
- **Heads, hands and props:** `scripts/cutout_white.py` into `heads\`, `hands\` and `props\` (`--crop-like` the neutral head for every head variant).
- **Poses:** `cutout_white.py` (or `npx hyperframes remove-background`) into `body\`.
- **Rig:** `python scripts/rig_poses.py 03_character`, then put `rig\rigs.json` into the JSON as `rigs`. This rigs the front and side poses. Action poses (run, jump, celebrate…) are used as whole images through `src`, with the expression drawn in.

## Stage 6: Final storyboard + Round 2 (visuals)
**Premium route:** each package is a **shot list** of 3–4 shots (1.0–2.5 s each) from the framing menu in `references/premium.md` §2 (at least 3 framings per fact, one face close-up), with the action, expression, cast, camera (`drift`, `punch`, `enter: zoom`), eye looks and `fx`. After the user picks, write each shot's Flow prompt (character block + framing template), show the shot list once, and after a yes generate the shots (nano2, 9:16, 2–3 at a time) into `04_backgrounds\shots\`; reframe with `bg_process.py --no-grade` into `04_backgrounds\plates\`; show a contact sheet and re-roll bad shots.

1. For each scene, offer 3–4 visual packages (`references/options.md` → *Round 2*), in batches of 4 scenes, **built only from the images that exist** (code route: any pose, emotion, hand and prop in `references/puppet.md`, plus the backgrounds that exist). Each package covers the location, camera and transition, acting, chart, and caption or bubble.
2. Adjust lines where the images suggest a better gag, flagging every change.
3. Write `01_storyboard\storyboard_final.md` and `script_final.md` (word count, and estimated length = words ÷ 190 × 60 s).
4. **The script locks on approval.**

## Stage 7: Voice-over
1. Ask for the voice-over of `script_final.md`, saved in `05_vo\`.
2. Transcribe it at word level (`npx hyperframes transcribe <vo> --json`, or local Whisper) and save the JSON in `05_vo\`.
3. Map the words to scenes, report any differences from the script, and store the scene times and `words` in the project JSON.

## Stage 8: Backgrounds + sound
1. Premium route: plates are already made in Stage 6; run `python scripts/eye_locate.py <plate> [--box …]` on every face shot and put the pair into the shot's `eyes`. Other routes: run `scripts/bg_process.py` on each `04_backgrounds\raw\` image, writing to `04_backgrounds\sceneNN.jpg`. It reframes to 1080×1920, applies an optional cleanup mask and the Zoomby grade, and writes a manifest. Show a contact sheet.
2. Pick a music bed and SFX (whoosh, pop, crowd, bleep, camera clicks, impact) with `media-use` (the HeyGen catalog is free when signed in), saved in `06_project\audio\`; loop the bed to the video length. **Music at `db: -26.2`** under the VO. Ask before any paid generation.

## Stage 9: Build & render
1. Fill the shots: premium route shots as `{"bg": "plates/shotNN.jpg", "camera", "drift", "enter", "eyes", "punch", "fx"}` (no character layers: the character is in the image; `references/premium.md` §5); code route characters as `{"puppet", "outfit", "pose", "poses", "emotion", "emotions", "moves", "hold", "carry"}` plus free-standing `props` (`references/puppet.md`); Flow route characters as `{"rig", "emotion", "moves", "hands"}`, or `{"src"}` for an action pose; plus `chart`.
   - Set **`"speaking": true` only on shots where the character is talking**; lips stay still elsewhere. `params.character.lip` can be `minimal` (default), `full` or `none`.
   - Time the biggest move to the punchline word and the chart pop to the number's word.
2. Run `python scripts/build_project.py 06_project\zoomby.project.json 06_project`. Media from the other folders is copied into `06_project\media\`.
3. Run `npx hyperframes check` in `06_project` and fix any errors.
4. Snapshot 4–6 frames plus a move and a chart (premium: also frames inside an eye dart and an FX moment), and show them.
5. Render after the user agrees: `npx hyperframes render -o ..\07_render\<short-topic>.mp4`. Check loudness; if it is outside −12 to −14 LUFS, normalise the audio without re-encoding the picture: `ffmpeg -i in.mp4 -c:v copy -af loudnorm=I=-13:TP=-1.5:LRA=11 -ar 48000 -c:a aac -b:a 192k out.mp4`.

## Stage 10: Revise
The user can re-pick any scene's option or swap any image. Rebuild only that scene's data, then run `build_project.py`, check and re-render.

## Rules
- Checkpoints, in order:
  1. topic,
  2. Round 1 lines,
  3. initial storyboard,
  4. character master approval (premium), puppet sheet approval (code) or prompt sheet hand-off + image check (Flow),
  5. Flow prompts (premium shot list or backgrounds) + credits before generating,
  6. Round 2 + final storyboard (script lock),
  7. voice-over,
  8. preview frames before rendering.
- Always 3–4 options per scene, in batches of 4 scenes.
- Premium pacing: 3–4 shots per fact, median shot 1.0–2.3 s, never hold a still over about 3 s; every shot moves from frame 1.
- Stills only by default; AI video (Flow Veo, image→video) only when the user asks, after a 1-clip cost test they said yes to.
- Kits and brands are look-alike: same colours, no badges, sponsors, numbers or readable brand names.
- Never spend credits (Flow, HeyGen, cloud render) without a yes in this conversation.
- Mouths stay closed or only slightly open. Lips move only on `speaking` shots; the face and body carry the performance.
- Safe zones: the face in the upper 15–45%, the caption centre at about 64%, nothing important below 78%.
- Charts only for real numbers from the verified script. On the premium route show them as `number` pops (caption-style digits), not chart cards.
- The tone is an affectionate roast: never mock appearance, race, religion or hardship. Use real people only for public facts. Flow prompts describe looks only, never names.
- Keep every file inside the video folder layout; never write into the skill folder.
