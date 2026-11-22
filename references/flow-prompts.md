# Google Flow prompts (premium shots) and policy rules

Claude generates every image through the `google-flow` MCP once the script is locked (no separate go-ahead for the batch). Prompt structure, the character block and the framing menu are in `premium.md` §1–2; this file holds the call settings, the policy rules and worked examples.

## Connector: `google-flow` MCP
**Accounts, project ids, failover, pacing, the "unusual activity" rule, cool-downs, the batch runner and troubleshooting follow the Flow rulebook `google-flow/google-flow-accounts.md`.** Read it before any Flow call; this file doesn't repeat it.

| Step | Tool | Notes |
|---|---|---|
| Generate | `gflow_generate_image` | `prompt`, `aspect: "9:16"`, `model: "nano2"` (Nano Banana 2.1, always), `count: 1`, `profile=` + `project=` per the rulebook's chain. **`reference_images`:** the approved master (`03_character/master_<outfit>.jpg`) on every shot with the main character, plus the previous shot of the same set for continuity, plus any other recurring character's master. Returns local paths; copy to `04_backgrounds/shots/<ID>.jpg` (masters to `03_character/`). |

- **Consistency = reference image + character block.** The master goes in as a reference **and** the block is still pasted word for word. Reference images alone drift on the flat cartoon head, and the block alone drifts on hair and outfit.
- A one-off error ("Something went wrong") costs nothing: retry **once**, with a shorter, simpler prompt if it was long. Then follow the rulebook's failover.
- `gflow_generate_video` (Veo) only if the user asks for AI video, after a 1-clip cost test they said yes to.

## Policy-safe prompts
Write every prompt to pass the first time.
- **No real names** of the subject, other people, teams, brands or trademarks; describe by looks ("grown adult male footballer, long curly black hair tied back, thin white headband").
- **Look-alike kits and products:** "bright canary-yellow football shirt with a green round collar … no logos, no badges, no numbers"; "plain unbranded blue soda can".
- **Friendly verbs:** "laughing", "surprised", "nervous wobbly smile" — not shouting, screaming, terrified, furious, crying hard.
- **Children:** innocent football situations only (a boy dribbling, a kid goalkeeper sitting among balls); never an adult role, money, alcohol or attitude props.
- **No danger or injury on people**; comedy comes from the situation (handing over a briefcase, ringing a service bell).
- **No body or appearance words aimed at a person** ("bulky", "round full face", never "fat" or "ugly").
- **Words that trip filters:** shout, scream, attack, blood, weapon, gun, drunk, sexy, naked, kid/child + adult role, real names.
- Every prompt ends with `photorealistic …, cinematic lighting, vertical 9:16, no text, no logos, no watermark` (`no readable text` for documents and passports).

## Worked examples (Ronaldinho video)
| Shot | Prompt (abridged; character block in full in the real prompt) |
|---|---|
| Hook wide | "Wide cinematic low-angle shot in a huge football stadium at golden hour …: a hybrid character sprinting straight toward the camera dribbling a white football at his feet. [character block, big excited grin] …" |
| POV insert | "First-person POV shot looking down at two realistic brown-skinned hands opening a shiny metal briefcase … packed with stacks of gleaming gold bars …" |
| Cast crowd | "Wide shot of packed stadium stands at night: rows of football fans in white … with semi-realistic bodies and flat 2D cartoon heads (…), all standing up and applauding …" |
| Reaction ECU | "Extreme close-up of a hybrid character's face filling most of the frame, overjoyed, with big red heart-shaped eyes and a huge open-mouthed grin … [head block]" |
| Aerial | "High aerial top-down drone view looking straight down at a concrete five-a-side football court in a prison yard …, one player in a bright canary-yellow shirt dribbling …" |
| Climax | "… a grown adult man lifts a cute happy pink pig above his head with both realistic hands like a trophy … LONG curly black hair tied back in a ponytail …, a thin WHITE HEADBAND …" (capitals on signature features fixed an off-model first roll) |
