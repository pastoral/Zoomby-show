# Google Flow prompts: character sheet (manual) and backgrounds

## Who generates what
- **Default (Stage 4):** the user generates everything by hand in Google Flow from the **prompt sheet** that `scripts/prompt_sheet.py` writes to `02_flow_prompts/` (.docx + .md). Claude writes the prompts but does **not** call Flow.
- **Fallback:** the `google-flow` MCP (bottom of this file), only when the user asks for it and gives a yes after seeing the prompts and credits.

## Character sheet prompt sheet (manual, Stage 4)
`prompt_sheet.py` builds it from `assets` in the project JSON. The sections are:
1. **How to use it in Flow:** Nano Banana 2.1; master front pose first, then attach it as the reference for everything else; 9:16 for poses and backgrounds, 1:1 for heads, hands and props; 2–4 generations at a time; save under the exact file names into `03_character/raw/` and `04_backgrounds/raw/`.
2. **Style lock:** `CHARACTER: <looks only>` · `STYLE: flat 2D cartoon character illustration, thick bold uniform black outline, flat cel colours with one soft shadow tone, big white oval eyes with small black pupils, tiny simple nose, slightly oversized head, mouth closed or a small gentle smile` · `BACKGROUND: plain pure white background, no text, no watermark, no logo`.
3. **Poses** (`<outfit>_<pose>.png`, 9:16, full body head to toe):
   - The master is `front`. Every other pose prompt starts "Using the attached character as the exact reference (same face, hair, outfit, colours and style): draw the character …".
   - Standard library: front, three_quarter_l/r, side_r, back, walk, run, jump, celebrate, point, arms_crossed, hands_hips, shrug, think, wave, sit, slump, surprised.
   - Custom storyboard poses are added from `assets.poses[].prompt`.
   - An action pose carries the scene's emotion in its prompt, because it is used as a whole image.
4. **Emotion heads** (`head_<emotion>.png`, 1:1):
   - `head_neutral` is drawn from the master pose. Every other head is an **edit of the cartoon head** (template below).
   - Library: neutral, neutral_half, happy, laugh, smug, sad, angry, surprised, scared, confused, love, wink, sleepy, thinking, proud, profile.
5. **Hands** (`hand_<gesture>.png`, 1:1): wave, point, thumbs, fist, peace, stop, count1–3, hold.
6. **Props and cast** (`prop_<id>.png`, `cast_<id>.png`), each with a safer fallback.
7. **Backgrounds** (`sceneNN.png`, 9:16): from each scene's `flow_prompt` / `flow_fallback`.
8. **File checklist:** ★ = needed by the storyboard; optional = extra acting options. The user was asked to make as many as possible, so the full library is always listed.

**Mouth rule:** every prompt keeps the mouth closed or only slightly open. `neutral_half` is a *small* opening for the occasional spoken word. Only `laugh` and `surprised` open wide. Never ask for "talking with mouth wide open" or "ahh" shapes.

The character is described by looks only. For a real person: hair, facial hair, skin tone, build, signature clothing colours, with no names, numbers that identify a club, badges or logos.

# Background prompts

## Template (keep it short)
```
[LOCATION + key props for the gag], [time of day / light: warm practical lamps | golden hour | dramatic dusk sky | bright daylight],
photorealistic cinematic photo, shallow depth of field, vertical 9:16 composition,
clear empty space in the upper-middle of the frame for a character, no people, no text, no logos, no watermark
```
- Use one location per prompt. Name the props the gag needs (e.g. "long wooden Viking table with bowls of raw meat, horned helmet on the bench").
- The empty space and "no people" matter: the cartoon character is composited later.
- When a scene needs a crowd or other people, use the cartoon cast; never ask Flow for real, recognisable people.
- For stadiums and brands, use generic stands and signage; the real club or brand names come from props or captions.

## Policy-safe prompts (Google Flow only)
Flow refuses some prompts with "This generation might violate our policies". Write every Flow prompt (backgrounds, cartoon heads, supporting cast) to pass the first time. These rules apply to Flow prompts only, not to the script or captions.

- **No real names.** Never name the celebrity, other public figures, brands, teams or trademarks in a Flow prompt. Describe them by look instead: "bearded man with a short black buzz cut".
- **Real-person photo reference: neutral expressions only.** With a photo of a real person attached, ask only for calm or positive faces: smile, smirk, grin, laugh, surprise. No shouting, anger, fear, pain, crying, sweat or strain.
- **Expressive variants: edit the cartoon, not the photo.** First generate the neutral cartoon head from the photo. Then make every other expression (talking mouth, shock, laugh) by attaching that **cartoon** head as the reference and writing "Edit the attached cartoon head: keep exactly the same character, style… only change the expression to…". This also keeps lip-sync pairs matching.
- **Friendly verbs.** "talking happily with mouth open in a wide 'ahh' shape", not "shouting / yelling / screaming". "surprised", not "terrified". "cheerful", not "aggressive".
- **Children: storybook style, nothing adult.** Write "cute storybook-style cartoon of a happy little baby character", with innocent props (cushion, toy microphone). Never give a child adult attitude or accessories: no smirk, sunglasses, money, jewellery, office or business roles. When the gag needs a child in an adult role, prefer an object stand-in (an empty tiny chair with a miniature suit and a pacifier) and let a speech bubble make the joke.
- **No violence or danger on people.** Fire, crashes or storms are fine on empty locations (a bus on fire with nobody around). Never put a person in danger, injured or fighting. Strain gags (guards carrying someone) come from the composite and sweat-drop symbols, not from the prompt.
- **No body or appearance words aimed at a person.** Use "round full face" or "bulky", never "fat", "obese" or "ugly".
- **Words that tend to trip filters:** shout, scream, yell, attack, blood, weapon, gun, drunk, sexy, naked, kid/child + adult role, and real names. Swap them for neutral wording.
- **Always offer a fallback.** For any risky prompt, write a safer B version (an object stand-in or a generic mascot with no reference) next to it, so a refusal costs one retry, not a rewrite.
- **Pace the calls.** Flow's bot check (`PUBLIC_ERROR_UNUSUAL_ACTIVITY`, HTTP 403) trips after many generations and upscales in a short burst. Send them a few at a time with gaps between batches. On a 403, stop and tell the user: never retry in a loop.

## Example prompts

| Scene | Prompt |
|---|---|
| Diet gag | Rustic Viking feast hall, long wooden table with bowls of raw meat, horned helmet on the bench, warm hanging lamp light, photorealistic cinematic photo, shallow depth of field, vertical 9:16, clear empty space upper-middle for a character, no people, no text, no watermark |
| Sleep gag | Cosy hotel bedroom at night, white duvet, five footballs on the bed, warm bedside lamps, … (same tail) |
| Hero | Huge football stadium at golden hour, packed blurred stands, green pitch in foreground, dramatic sky, … (same tail) |

## Process
1. Write one prompt (plus a safer fallback) for each scene that has no user photo, into the scene's `flow_prompt` / `flow_fallback`. They go into the prompt sheet, and the user generates them by hand.
2. Only if the user asks Claude to generate them: show them all in a numbered list with the credit balance and ask once, "Generate these N images in Flow?". On a yes, call the Flow connector's image tool once per prompt. Ask for vertical 9:16 when the tool supports aspect ratios; otherwise take the widest result and reframe in `bg_process.py`. Save each result as `04_backgrounds/raw/sceneNN.png`.
3. If a result has people, text or wrong props, offer a regenerate (asking again if credits apply), or clean it with a mask (`bg_process.py --mask`).
4. Run `scripts/bg_process.py` on every raw image.

## Connector: `google-flow` MCP (fallback only; tool names)
Load the tools with ToolSearch `select:mcp__google-flow__gflow_auth_status,mcp__google-flow__gflow_get_credits,mcp__google-flow__gflow_generate_image,mcp__google-flow__gflow_upscale_image`.

| Step | Tool | Notes |
|---|---|---|
| 1. Session check | `gflow_auth_status` | Free. If it isn't signed in, ask the user to run `gflow auth login`, then stop. |
| 2. Credits | `gflow_get_credits` | Free. Show the balance next to the prompt list when asking for approval. |
| 3. Generate | `gflow_generate_image` | `prompt`, **`aspect: "9:16"`**, `count: 1` (or 2 for a choice), **`model: "nano2"` (Nano Banana 2.1) for every image: backgrounds, heads and cast; don't switch to `nano-pro` or another model unless the user asks**, `project_name: "zoomby-<slug>"`. Returns **local file paths**; copy them to `04_backgrounds/raw/sceneNN.png`. **Spends credits: ask first.** |
| 4. Upscale (optional) | `gflow_upscale_image` | `media_id` from the generate result, `scale: "2k"`. Free. Use it when the result is under 1080 px wide, before `bg_process.py`. |

- **Character consistency (optional):** `gflow_generate_image` accepts `reference_images` (local paths). If the user wants the cartoon character drawn into a background, pass the character sheet there. The default is still empty plates with the character composited by the template.
- `gflow_download_media` is for videos only and is not needed for backgrounds.
- `gflow_generate_video` exists, but the Zoomby style animates in HyperFrames, so don't use it unless the user asks.
- If the connector is missing or the auth check fails, say so plainly and ask for background photos. Never present a stock or placeholder image as a Flow result.

## Character heads, emotions and hands (prompt details, policy-safe)
The character is a **flat cartoon head on a semi-real body cut-out** (see `style.md` §2), so Flow only draws heads and hands; the bodies come from the user's character sheet. Every image uses `model: "nano2"`, `aspect: "1:1"`, plain white background, so `scripts/rig_poses.py` can cut it out by edge flood-fill. Generate in small batches (2–4 at a time).

**1. Neutral head** (reference = the user's face close-up crop from the sheet). Calm or positive wording only:
```
cartoon mascot head of a cheerful man with [hair], [beard], [skin tone], round full face, head and short neck only, facing the camera, confident closed-mouth smile, flat 2D cartoon illustration, thick bold uniform black outline, single flat skin tone, big white oval eyes with small black pupils, tiny simple nose, plain pure white background, no text, no watermark
```

**2. Every other expression: edit the neutral cartoon head** (reference = your finished `head_neutral.png`, never the photo). Template:
```
Edit the attached cartoon head: keep exactly the same character, style, outline, colors, hair, beard and framing, and only change the expression to [EXPRESSION]. Plain pure white background, no text, no watermark
```
| File | [EXPRESSION] (friendly wording that passes the filter) |
|---|---|
| `head_neutral_half.png` | the same smile with the mouth only slightly open, as if saying one soft word (a small opening, not wide; **used for lip movement on speaking shots**) |
| `head_happy.png` | a big happy smile, eyes curved upward with joy |
| `head_laugh.png` | laughing happily with the mouth open and eyes squinted |
| `head_smug.png` | a confident half-smile with one eyebrow raised |
| `head_sad.png` | a sad face: eyebrows tilted up in the middle, small frown, one small tear |
| `head_angry.png` | a grumpy cartoon frown: eyebrows pulled down in a V, lips pressed together, cheeks slightly red |
| `head_surprised.png` | surprised: eyebrows high, eyes wide, small round open mouth |
| `head_scared.png` | nervous: eyes wide, eyebrows up, wobbly worried mouth, small sweat drop |
| `head_confused.png` | puzzled: one eyebrow up, one down, mouth to one side |
| `head_love.png` | delighted: heart-shaped eyes and a big smile |
| `head_profile.png` | the same character seen in side profile facing right, calm closed mouth |

Avoid "screaming, yelling, furious, terrified, crying hard, rage" in any of these: they get refused. "Grumpy", "nervous", "surprised", "sad with a small tear" pass.

**3. Hands** (no reference needed; match the skin tone). One hand per image, wrist at the bottom:
```
single cartoon hand [GESTURE], [skin tone] skin, flat 2D cartoon illustration, thick bold uniform black outline, simple rounded fingers, wrist cut off cleanly at the bottom, plain pure white background, no arm, no text, no watermark
```
| File | [GESTURE] |
|---|---|
| `hand_wave.png` | open palm facing the viewer, fingers spread, waving hello |
| `hand_point.png` | index finger pointing up, other fingers curled |
| `hand_thumbs.png` | thumbs up |
| `hand_fist.png` | closed fist, knuckles facing the viewer |
| `hand_peace.png` | two fingers in a peace sign |

Cut them out like the heads (flood-fill from the edges keeps the white eyes and teeth), then run `scripts/rig_poses.py`.
