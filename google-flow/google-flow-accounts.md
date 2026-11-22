# Google Flow MCP: images only, across multiple accounts (rulebook)

This is the Google Flow rulebook for this skill. Skill files don't restate account, failover or pacing rules; they link here. The batch runner lives next to this file: `run_batch.py` + `batch_manifest.example.py`.

All stills, pose sets, plates, props and thumbnails come from **Google Flow** through the `google-flow` MCP server (gflow CLI). **No video is generated**; never call `gflow_generate_video` unless the user explicitly asks for AI video in that conversation. Image batches run in one go without asking first; skill approval gates for a character master or a thumbnail pick still apply. The user may have several Flow accounts, all their own, saved as gflow profiles. When one fails or runs out, switch to the next automatically.

## 1. One-time setup (the user does this; never type passwords)

1. The MCP server `google-flow` must be connected. Load its tools in one call:
   `ToolSearch select:mcp__google-flow__gflow_auth_status,mcp__google-flow__gflow_get_credits,mcp__google-flow__gflow_generate_image,mcp__google-flow__gflow_list_projects`
   If the tools are missing, ask the user to (re)connect the server; don't install anything yourself.
2. Each account is a named profile. The user signs in once per profile in their own terminal: `gflow auth login --profile <name>`.
   - **Don't add `--account <email>`**: it crashes the login. If that happened, rerun the plain command.
   - If Google blocks the window, add `--browser chrome`. Afterwards, verify with `gflow_auth_status(profile=<name>)`.
3. gflow keeps its profiles in its own data folder (on Windows `%LOCALAPPDATA%\ffroliva\gflow-cli`). Don't edit them by hand.
4. The user lists their profiles, in failover order, in a **private** file: `~/.gflow/profiles.json` (or the path in `$GFLOW_PROFILES`). Format: `profiles.example.json` next to this file. Never copy its contents into a skill file, a commit or any published page.

## 2. Profiles and projects (failover chain)

Read the private profiles file at the start of every Flow job. Each entry gives `profile`, `project`, `refs` (whether that profile accepts `reference_images`), `enabled` and a `note`. Use only enabled profiles, in file order.

Reference-image jobs (poses, expressions, plates, variants) need a profile with `refs: true`; some profiles only accept them with a project the user made in Flow's website. Pass `project=` on every call. Text-only jobs (plates from scratch, props) run on any enabled profile.

Never show account emails or profile details in any external request or published file.

## 3. Generating (one batch, no stops)

- `nano2` images cost **0 credits**, so there is no credit check or go-ahead before an image batch. Generate the whole `image_list.md` in one go, without asking, waiting or holding.
- Run **one call at a time**. Parallel calls on one profile tripped Flow's bot check (WAF 403 `PUBLIC_ERROR_UNUSUAL_ACTIVITY`).
- **Pace the batch.** Flow throttles the **PC/connection**, not only the account. All profiles share one IP, so switching accounts doesn't escape a throttle. See §4b.
  - Wait **15–20 s between image jobs** (`sleep 15` in Bash before the next call). Copying and checking the last image can fill part of that wait.
  - After about **25 images in a row**, take a 3-minute break (background `sleep 180`, continue when it ends).
  - Spread a long batch across profiles in turn (e.g. 10 on one, then 10 on the next) rather than running ~60 on one account. One account tripped the bot check after about 63 images in one day.
  - Only one session at a time should run Flow jobs on this PC. Before a batch, check that no other Claude session is mid-generation. If one is, wait for it or coordinate with it.
```
gflow_generate_image(
  prompt=<prompts.md>, aspect="9:16", model="nano2", count=1,
  profile="<first enabled profile>", project="<its project id>",
  reference_images=["<video>/03_character/master_<player>.jpg", "<video>/04_backgrounds/poses/<first pose>.jpg"])
```
- **Big batches: use the background runner** (`run_batch.py` + `batch_manifest.example.py` in this folder). Copy both into the video's image folder (e.g. `04_backgrounds/`), rename the example to `batch_manifest.py`, delete any old `flags.json` older than 3 h, fill `batch_manifest.py` with `(out, refs, prompt)` jobs in image_list order (plates after their source stills), test with `python run_batch.py 1`, then run `python run_batch.py` with Bash `run_in_background`. It reads the private profiles file, drives the CLI (`gflow image gen PROMPT --ref <file> --profile P --project ID --out <dir> --json`) one job at a time with 18 s gaps, skips files that already exist (safe to restart), applies §4 failover and the §4b rule, and logs to `batch_log.txt`. Exit code 2 = every profile flagged/resting: tell the user.
- MCP calls save files under gflow's output folder (by default `~/Documents/GoogleFlow/images/<date>/<media id>_1.jpg`). Copy each one into the video folder under its `image_list.md` name right away.
- Stills come back at 768×1376 (9:16) or 1024×1024 (1:1).

## 4. Automatic failover

- If a job fails (timeout, "Unknown Error", `flow-host-migrated`, `media-upload-rejected`, "status 4", out of credits), retry **once** on the same profile. If it fails again, move to the next enabled profile and carry on with the same image.
- Images are free, so a "charged: maybe" result on an image is safe to re-run.
- Say every switch in a progress line: "profile 1 failed twice → now profile 2".
- If every profile fails: stop, and tell the user what's done and what's left.

## 4b. PC-wide throttle: cool down instead of burning through accounts
**What happened once:** one account tripped the bot check after about 63 images. For the next 17 minutes, **every** profile failed with the same `Unknown Error` (the same `sha256:` signatures), on unrelated prompts, even a plain football photo. Then, with nothing changed locally, all of them worked again. Account failover only used up the chain.

**"Unusual activity" rule:**
1. A profile raises "unusual activity" (WAF 403 / `PUBLIC_ERROR_UNUSUAL_ACTIVITY`) → **switch automatically** to the next profile and keep going.
2. If the new profile also raises "unusual activity" **within 3 minutes of that switch** → **cool down 20 minutes**. Otherwise carry on generating.
3. After the cool-down, resume on the **next unflagged** profile (skip both flagged ones).
4. A flagged profile **rests 3 hours** from its flag, then it is allowed again (the runner keeps flag times in `flags.json`, so a restart remembers).
5. Every profile flagged or resting → **stop and tell the user** what's done and what's missing.

**Other throttle signs** (no WAF message): 2 different profiles failing back to back with the same `Unknown Error` / `sha256:` detail, or flow.google.com timing out from this PC. Treat it like rule 2: cool down 20 min, then continue on the next profile.

An image that fails on 2+ profiles **outside** a throttle window (others succeed around it) is a prompt that Flow rejects. Rewrite the prompt (soften wording, drop the risky detail), or fall back to a held still. Don't keep retrying it.

Diagnose afterwards from gflow's local records in its data folder: `gflow.db` (tables `operations` and `generation_queue`, with `profile_name`, `status`, `error_json`) and `incidents/<date>/*/manifest.json` (error class, e.g. `WafRejectionError`).

## 5. Consistency across accounts

- Saved Flow characters (`@Name`) and projects belong to one account. Keep masters and pose stills as **local files** and pass them via `reference_images`, so any profile can continue a set.
- For a pose or expression set, always pass the set's first image (and the master). Then a pose made on a different account still matches.

## 6. Troubleshooting
| Symptom | Fix |
|---|---|
| `flow-host-migrated` with `reference_images` | That profile is agent-only without a web project. Use the next profile, or ask the user to make a project in Flow's website, upload one image there and accept the "rights to use this image" dialog themselves. Then they put that project id in their profiles file. |
| Transport timeout after submit | Free for images: retry once, then fail over. |
| `signed_out_shell` | The user reruns `gflow auth login --profile <name>`. |
| HTTP 429/503 | Wait; don't loop. |
| WAF "unusual activity", or the same `Unknown Error` on 2+ profiles in a row | Follow the §4b rule: switch profile; a second flag within 3 min of the switch → cool down 20 min; flagged profiles rest 3 h; all flagged → stop and tell the user. |
| Gflow browser jobs all fail with "_bootstrap_and_resolve_locale" | A dead Windows proxy is on. The user turns it off. |
| Off-model face or wrong pose | Capitalise the signature features or the pose, add the neighbouring pose as a reference, re-roll (≤2 without asking). |
| Upgrade gflow | The user closes Claude Code (the MCP server locks the folder), then runs `uv tool install --force gflow-cli@latest`. |
