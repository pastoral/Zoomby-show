---
name: zoomby-show
description: Make a premium Zoomby Show style vertical short on any topic - semi-realistic 3D bodies with flat 2D cartoon heads inside AI-generated photoreal scene shots from Google Flow, 3-4 framings per fact, 1-2 s cuts, animated eye darts and blinks, push-ins, punch-ins, zoom-whips, shake, foreground FX and caption-style number pops, plus a 10→1 countdown badge, 1-2 word pop captions and a fast comedic voice-over. Interactive - suggests 5 topics, creates an organised video folder, drafts the story with 3-4 line options per scene, storyboards, offers 3-4 shot-list options per scene, generates the shots, takes the user's voice-over, renders an MP4 with HyperFrames, then writes publish.md (titles, descriptions, hashtags, tags) and thumbnails. Use for "Zoomby video", "Zoomby style", "10 weird things about…" cartoon shorts, Zoomby topic ideas, or a Zoomby publish kit.
---

# Zoomby Show video maker (premium route only)

You make an 8–10 scene vertical short in the **premium Zoomby style**, and **the user chooses every scene**. Work through the stages in order and never skip a user checkpoint. There is only one route: **the character is inside AI-generated scene shots** (semi-real body + flat cartoon head), animated with camera, eyes and FX. Retired routes (SVG puppet, Flow prompt sheet, cut-out rig) are in `archive/`; don't use them.

- Premium look and shot rules: `references/premium.md` (read first).
- Look and sound spec: `references/style.md`.
- Writing and topics: `references/story.md`.
- Storyboards and shot lists: `references/storyboard.md`.
- Option menus: `references/options.md`.
- Flow prompts and policy rules: `references/flow-prompts.md`.
- Build, check, render: `references/build.md`.
- Publish kit: `references/publish.md`.

## Settings
- **VIDEOS_BASE:** `%VIDEO_WORK_ROOT%\<Subject>\2D Animation\videos\` `VIDEO_WORK_ROOT` is an environment variable holding the user's video work folder; if it is unset, ask the user where their videos live before creating anything.
  - `<Subject>` is `Football` for football topics. Other subjects get a category name (e.g. `Science`, `History`, `Animals`, `Celebrities`); create it if it is new.
- **Video folder:** `VIDEOS_BASE\YYYY-MM-DD-<short-topic>\`, using today's date and a 3–5 word kebab-case topic. Create it **right after the topic is chosen**:
  ```
  00_ideas.md            topic, angle, verified facts, brief answers
  01_storyboard\         storyboard_initial.md, shotlist.md, storyboard_final.md, script_final.md
  03_character\          master_<outfit>.jpg (approved look), character_block.txt
  04_backgrounds\shots\  raw Flow shot images (shotID.jpg)
  04_backgrounds\plates\ 1080x1920 plates (bg_process.py --no-grade);  eyes\  eye_locate.py JSON
  05_vo\                 voice-over + word-level transcript json
  06_project\            zoomby.project.json, index.html, fonts\, audio\ (music, sfx), snapshots\
  07_render\             <short-topic>.mp4, thumbnail_vertical_1080x1920.jpg, thumbnail_1280x720.jpg
  publish.md             title, descriptions, hashtags, tags, pinned comment, checklist
  ```
- **Topic log:** `VIDEOS_BASE\_ideas\YYYY-MM-DD-topics.md`.
- **State:** `06_project\zoomby.project.json` (schema: `templates/zoomby.project.example.json`). Update `stage` after every stage, so `/zoomby-show` on an existing folder resumes where it stopped. Asset paths in the JSON are relative to the video folder.
- **Google Flow:** images use `model: "nano2"`, `aspect: "9:16"`. Accounts, each profile's `project=` id, failover, pacing (one job at a time, 15–20 s apart), the "unusual activity" rule and the background batch runner all follow the **Flow rulebook** `google-flow/google-flow-accounts.md`. Read it before any Flow call. **Reference images:** pass the approved character master (`03_character\master_<outfit>.jpg`) as `reference_images` on every shot with the main character, plus the previous shot of the same set when continuity matters. Keep pasting the character block word for word too.

**Who provides what:**

| Item | Provided by |
|---|---|
| Topic ideas, story, options, storyboards, shot lists, all Flow images, animation, captions, sound bed, render, publish kit | Claude |
| Topic pick, Round 1 and Round 2 picks, character master approval, shot-list (script lock) approval, preview approval | User |
| Recorded voice-over (after the script locks) | User |

## Stage 1: Topic + brief
1. If the user gave no topic, ask in one AskUserQuestion: "Suggest 5 topics" or "I have a topic", plus the brief: scenes (8 or 10), hook (title line, superlative question, shocking fact first), ending (cliffhanger, deadpan, simile, legend, gag), badge colour (or "follows the kit"). Use the defaults from `references/style.md` for everything else; the user can override any parameter.
2. **5 topics:** follow `references/story.md` → *Topic suggestions*. Read `VIDEOS_BASE\_ideas\` and the existing video folders first, write a numbered list (title, angle, 3 sample facts, gag locations), save it to `_ideas\YYYY-MM-DD-topics.md`, then stop for the pick.
3. Pick the `<Subject>` and short topic, tell the user the folder path, create the folder tree, and write `00_ideas.md`.

## Stage 2: Story + Round 1 (lines)
1. Research and **verify every fact** (web search); write "reportedly" for anything you can't confirm.
2. Order the scenes mild → wild, best last (#1).
3. Offer 3–4 line options per scene (`references/options.md` → *Round 1*): AskUserQuestion, **4 scenes per call**, plus hook/ending/badge/connectors in the last call.
4. Assemble the draft script (≈ 160–210 words). If it runs over ~65 s at 190 wpm, trim connectors and words first, never the chosen punchlines.

## Stage 3: Initial storyboard
Write `01_storyboard\storyboard_initial.md` (`references/storyboard.md`): per scene the line, location, the 3–4 visual beats (set-up → detail → reaction → punchline), outfit, cast, props and any number to show. Mirror it into the JSON. Show a summary and **stop for approval**.

## Stage 4: Character master
1. Write the fixed **character block** (`references/premium.md` §1): looks only, no real names, one block per outfit (kits are look-alike: same colours, no badges, sponsors or numbers). Save it to `03_character\character_block.txt` and the JSON (`premium.character_block`).
2. Generate the full-body master per outfit on white (`03_character\master_<outfit>.jpg`). Show it and **stop for approval**; re-roll on request ("older", "square jaw", "longer hair").

## Stage 5: Round 2 (shot lists) + final storyboard
1. For each scene offer **3–4 shot-list options** (`references/options.md` → *Round 2*) in batches of 4 scenes: 3–4 shots of 1.0–2.5 s, ≥ 3 framings incl. one face close-up, with action, expression, cast, camera (`drift`, `punch`, `enter`), eye looks, `fx` and number pops.
2. Write `01_storyboard\shotlist.md` (every shot: ID, approx. words, framing, picture, face/camera/FX) and `storyboard_final.md`; adjust lines where a shot suggests a better gag, flagging every change.
3. Write `script_final.md` (word count, estimated length). **The script locks on approval.**

## Stage 6: Generate the shots
1. Generate every shot **in one go, without asking first**: the script lock in Stage 5 is the approval. Use the character block + framing template from `references/premium.md` §2 and the master as a reference image, one job at a time with pacing per the Flow rulebook (the background runner for big batches), into `04_backgrounds\shots\<ID>.jpg`.
2. Reframe each to 1080×1920: `python scripts/bg_process.py shots\<ID>.jpg plates --name <ID> --no-grade`.
3. Show a contact sheet. **Re-roll** any shot with an off-model main character (wrong hair, headband, kit, face like another character), a real logo or readable brand, a double head, or a realistic face.

## Stage 7: Voice-over
1. Ask for the voice-over of `script_final.md`, saved in `05_vo\`.
2. Transcribe at word level (`npx hyperframes transcribe <vo> --json`, or local faster-whisper) and save the JSON in `05_vo\`. Drop end-of-file hallucinations, fix name spellings, merge split tokens ("Coca" + "-Cola"), and recover any missed word (e.g. a spoken badge number) by checking the audio energy.
3. Map words to scenes and report any differences from the script (spoken badge numbers are fine: scenes then start on them).

## Stage 8: Eyes, sound, timeline
1. Run `python scripts/eye_locate.py plates\<ID>.jpg --all > eyes\<ID>.json` on every face shot; pick the main character's pair (`--box` or by position). Shots with closed, heart or hidden eyes stay as drawn.
2. Music bed + SFX with `media-use` (the HeyGen catalog is free when signed in): loop the bed to the video length, **music at `db: -26.2`**; SFX: whoosh on every zoom-whip, impact on big beats, camera clicks under flashes, ping on number pops, pop on bubbles and punchlines, chime at the end. Ask before any paid generation.
3. Fill the JSON shots from the shot list and the word timings (`references/premium.md` §5): cut on cue words, `eyes` looks every 0.4–0.8 s, `punch` on the punchline word, `fx` on cue words, numbers as `fx` type `number` (never chart cards), bubbles 2–4 per video, per-scene `badge_color`. Any still longer than ~2.9 s gets a mid-shot punch-in.

## Stage 9: Build, preview, render
1. `python scripts/build_project.py 06_project\zoomby.project.json 06_project`, then `npx hyperframes check` in `06_project` and fix every error (long bubble words shrink automatically; drop auto emotion emoji with `emotion_symbol: false` if they collide).
2. Snapshot 16–24 frames across the video plus frames inside an eye dart, a number pop and an FX moment; show a contact sheet (`06_project\snapshots\`). Fix overlaps (number or bubble on the face or badge).
3. After the user agrees: `npx hyperframes render -o ..\07_render\<slug>.mp4` (run it in the background), then set loudness: normalise to −13 LUFS (`loudnorm=I=-13:TP=-1.5`) on a first render; on a re-render after a music-only change, keep the VO level by matching gain on speech frames against the previous render. Keep previous renders as `_vN-<label>.mp4`.

## Stage 10: Revise
The user can re-pick any shot list, re-roll any shot, or change numbers, bubbles, levels. Rebuild only what changed, check, re-render.

## Stage 11: Publish kit
Right after the final render, without being asked (`references/publish.md`):
1. Thumbnails: `python scripts/publish_kit.py <video> --plate 04_backgrounds/plates/<best>.jpg --line1 … --line2 … --sub "8 WEIRD <NAME> FACTS" --badge N --video 07_render/<slug>.mp4` → vertical + 16:9 thumbnails, vertical one embedded as the MP4 cover. Check both images.
2. Write `publish.md`: main title + A/B alternatives, YouTube description, TikTok/Reels caption, hashtags per platform, YouTube tags, pinned comment, thumbnail notes, posting checklist.
3. Send the MP4, both thumbnails and `publish.md` to the user.

## Rules
- Checkpoints, in order: topic → Round 1 lines → initial storyboard → character master → Round 2 shot lists (script lock; shots then generate without a further go-ahead) → voice-over → preview frames before rendering.
- Always 3–4 options per scene, in batches of 4 scenes.
- Never spend credits (Flow, HeyGen, cloud render) without a yes in this conversation. Stills only: AI video (Flow Veo) only if the user asks, after a 1-clip cost test they said yes to.
- Pacing: 3–4 shots per fact, median shot 1.0–2.3 s, nothing held over ~3 s without a punch-in; every shot moves from frame 1.
- Look-alike kits and products only (no badges, sponsors, numbers, readable brand names); cartoon-headed cast only; no real-person photos.
- Safe zones: faces in the upper 15–45 %, caption centre ≈ 64 %, nothing important below 78 %; numbers and bubbles never on the face or the badge.
- Numbers as caption-style number pops; music at −26.2 dB under the VO, VO and SFX untouched.
- The tone is an affectionate roast: never mock appearance, race, religion or hardship. Real people only for public facts. Flow prompts describe looks only, never names.
- Keep every file inside the video folder layout; never write into the skill folder.
