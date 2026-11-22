# Code-drawn SVG puppets (character route "code")

On the code route Claude draws the characters, heads, hands, props and supporting cast in code with `scripts/zoomby_puppet.py`, and HyperFrames animates them directly. It needs no image generation and no credits, and the character stays identical in every scene. Only the photoreal backgrounds come from Google Flow or from the user's photos.

## Spec: `03_character/puppet.json`
```json
{
  "main": "dinho",
  "characters": {
    "dinho": {
      "label": "long curly black hair tied back, white headband, brown skin, slim",
      "skin": "#9C6744",
      "hair": {"style": "long_curly_tied", "color": "#1A1210"},
      "headband": "#FFFFFF",
      "facial_hair": null,
      "build": "slim",
      "outfits": {
        "brazil": {"shirt": "#FFD60A", "trim": "#139A43", "stripes": null, "shorts": "#1E4FBF", "socks": "#FFFFFF", "boots": "#111111"},
        "barca":  {"shirt": "#1D3F8F", "trim": null, "stripes": "#A50044", "stripe_n": 4, "shorts": "#13235A", "socks": "#1D3F8F", "boots": "#111111"}
      }
    },
    "defender": {"skin": "#E8B98F", "hair": {"style": "short", "color": "#6B4A2B"}, "facial_hair": "stubble", "build": "bulky",
                 "outfits": {"white": {"shirt": "#F4F4F4", "trim": "#CFCFCF", "shorts": "#F4F4F4", "socks": "#F4F4F4", "boots": "#111111"}}}
  },
  "props": {"pig": {"name": "pig"}, "can_blue": {"name": "can", "color": "#2E6BE6"}}
}
```
Field values:
- **`hair.style`:** `long_curly_tied` | `curly` | `afro` | `short` | `buzz` | `bald`.
- **`facial_hair`:** `null` | `stubble` | `beard` | `moustache`.
- **`build`:** `slim` | `regular` | `bulky`.
- **Outfit keys:** `shirt`, `trim` (collar and sleeve cuffs), `stripes` + `stripe_n`, `shorts`, `socks`, `boots`.

For non-football characters, use the shirt as a top and the shorts as trousers. Add a new style function in `zoomby_puppet.py` when a topic needs one (a suit or a dress, for example).

Describe a real person by looks only (hair, skin, build, kit colours), with no badges, sponsor logos or shirt numbers.

## Render the sheet for approval
```
python scripts/puppet_sheet.py <video>/03_character/puppet.json      # → 03_character/sheet/puppet_sheet_1..N.png
```
The sheet has these pages:
- each outfit in 12 key poses;
- the emotion grid, including the speaking half-open mouth;
- the hands, the props and the supporting cast.

Show all pages, then tweak the JSON from the user's notes ("hair longer" → `afro` or `curly`, "darker skin", other kit colours) and re-render.

## Poses (`pose`, `poses[]`)
- **Front view:** `front`, `wave`, `point`, `celebrate`, `hold_up` (holds the `hold` prop above the head), `arms_crossed`, `hands_hips`, `shrug`, `think`, `shush`, `sip` (holds the `hold` prop at the mouth), `slump`, `surprised`, `jump`, `count`, `thumbs`, `piggyback` (carries `carry`).
- **Side view (facing right; `flip: true` faces left):** `side_r`, `walk`, `run`, `three_quarter`.

## Emotions (`emotion`, `emotions[]`)
neutral, happy, laugh, smug, sad, angry, surprised, scared, confused, love, wink, sleepy, thinking, proud.
- **Mouth rule:** closed in every emotion except laugh (wide open) and surprised (small "o").
- On a shot with `"speaking": true`, closed mouths swap to a small half-open mouth on each word.

## Hands
Each pose sets its own hands: open, fist, hold, point, count1–3, peace, thumbs.

## Props
| Prop | Parameters |
|---|---|
| `can` | `color` |
| `passport` | |
| `bell` | |
| `sunglasses` | |
| `pig` | |
| `football` | |
| `trophy` | |
| `gold_bar` | |
| `phone` | |
| `mic` | |

- **Held by a character:** `"hold": "<prop id>"`, using the `hold_up` or `sip` pose.
- **Standing on its own in a shot:** `"props": [{"prop": "bell", "x": 80, "y": 72, "w": 16, "at": 0.6, "rot": 0}]`. The position is the centre in % of the frame, `w` is the width in % of the frame width, and it pops in at `at`.

## Character in a shot
```json
{"puppet": "dinho", "outfit": "brazil", "x": 50, "y": 60, "h": 62,
 "pose": "front", "emotion": "happy",
 "moves": [{"type": "run", "at": 0, "amt": -60, "dur": 0.8}],
 "poses": [{"at": 1.6, "pose": "celebrate"}],
 "emotions": [{"at": 1.0, "emotion": "surprised"}],
 "hold": "pig", "carry": "teammate", "carry_emotion": "laugh", "flip": false}
```
- `h` is the height of the puppet box in % of the frame. The figure fills about 85% of that box, with headroom for raised arms. Keep the face in the upper 15–45% of the frame.
- A `walk` or `run` move automatically plays a walk or run cycle (side view) while the character travels in. When the move ends, the puppet switches to `pose`.
- `"anim": "walk"` or `"run"` cycles in place for the whole shot.
- Pose changes tween in 0.2 s with a slight overshoot. Time them to the punchline word.
- Always on: blinks (when the eyes are open), head nods on the words (front view), plus the usual idle sway and breathing from `zoomby_motion.py`. All body `moves` (hop, lean, jolt, shake, slump…) work as with image rigs.
- The project JSON needs `"puppet_spec": "03_character/puppet.json"`.
