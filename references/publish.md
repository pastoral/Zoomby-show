# Publish kit (Stage 11): publish.md + thumbnails

After the final render is approved, make the publish kit **without being asked**:
- `publish.md` in the video folder;
- two thumbnails in `07_render\`;
- the vertical thumbnail embedded in the MP4 as its cover image.

Example: `videos\2026-11-14-ronaldinho-weird-facts\publish.md`.

## 1. Thumbnails: `scripts/publish_kit.py`
```
python scripts/publish_kit.py <video> --plate 04_backgrounds/plates/<best>.jpg --line1 "HE WON" --line2 "A PIG?!" \
       --sub "8 WEIRD RONALDINHO FACTS" --badge 1 --video 07_render/<slug>.mp4
```
- **Plate:** use a **clean** plate (no captions or badge burned in): the funniest face or prop moment, usually the #1 fact or the best reaction close-up. The face must be big and readable.
- **Text:** a 2–4 word hook as a question or shock (`HE WON` / `A PIG?!`, `PAID IN` / `GOLD?!`).
  - Line 1 is white and line 2 yellow, both caption-style (Montserrat 900, black outline).
  - `--sub` is the series line (`8 WEIRD <NAME> FACTS`).
  - `--badge` is the countdown number of the fact shown.
- **Placement:** `--text-y` (default 0.64) sets where the text sits on the vertical cover. Keep it off the face and the main prop. `--crop-y` picks the 1080×1000 window of the plate used in the 16:9 panel.
- **Check:** look at both files before handing them over. Re-run with another plate or other words if the text covers the face.
- **Upload note:** YouTube and TikTok ignore an embedded cover. The user picks the thumbnail in each upload screen. Say so.

## 2. `publish.md` template
```
# Publish kit: <title>
File · resolution · length · loudness · platforms

## Title            main (≤ 60 chars, curiosity + 1–2 emoji) + 3–4 A/B alternatives built on different facts
## Description      YouTube (2–4 lines: hook, 3 teaser facts, a question for comments, subscribe line, 3 hashtags)
                    TikTok / Reels short caption (1–2 lines + 4–6 hashtags)
## Hashtags         YouTube (≤ 15, first 3 shown above the title) · TikTok (4–6) · Instagram (8–12)
## Tags             YouTube Studio tag list (name, name + each fact keyword, topic, "<subject> facts", "animated football")
## Pinned comment   numbered list of the facts with one emoji each + "Which one got you? 👇"
## Thumbnail        the two files + which plate and words were used + alternative frames
## Posting checklist
   category & audience (not made for kids) · burned-in captions + transcript upload · AI disclosure (Flow scenes)
   · music licence check before monetising · keep "reportedly" wording · best posting time · native uploads per platform
```
Rules:
- Use only facts from the verified script, worded the same way: keep "reportedly" on unconfirmed facts.
- No real logos or brand claims in the title. Brand names in descriptions are fine only when they are the fact.
- Flag uncertain figures (e.g. a deal value that sources disagree on) with a note in `publish.md`.
- Keep the tone of the video: an affectionate roast, never mocking appearance, race or hardship.
