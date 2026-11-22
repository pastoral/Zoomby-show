# zoomby-show

A Claude Code skill that makes a premium vertical cartoon Short on any topic ("10 weird things about…"): semi-realistic 3D bodies with flat 2D cartoon heads, placed inside photoreal scene shots from **Google Flow**.

- 3–4 framings per fact and 1–2 s cuts, with animated eye darts and blinks, push-ins, punch-ins, zoom-whips, shake, foreground FX and caption-style number pops.
- A 10→1 countdown badge, 1–2 word pop captions and a fast comedic voice-over (yours).
- It's interactive: it suggests 5 topics, drafts the story with 3–4 line options per scene, storyboards, offers shot-list options, generates the shots, takes your voice-over and renders the MP4 with **HyperFrames**.
- It finishes with a `publish.md` (titles, descriptions, hashtags, tags) and thumbnails.

> Independent fan-made tooling. Not affiliated with, endorsed by or connected to the Zoomby Show channel. Use it to make your own original videos: don't copy anyone's characters, branding or footage.

## Install

```powershell
git clone https://github.com/pastoral/zoomby-show "$env:USERPROFILE\.claude\skills\zoomby-show"
cd "$env:USERPROFILE\.claude\skills\zoomby-show\scripts"
npm install
```

Or clone it anywhere and link it into `~/.claude/skills/zoomby-show`. Then, in Claude Code: "make a Zoomby-style video about octopuses".

## Requirements

- [Claude Code](https://claude.com/claude-code)
- The `google-flow` MCP server (gflow CLI), signed in with at least one profile: `gflow auth login --profile <name>`
- [HyperFrames](https://www.npmjs.com/package/hyperframes) (`npx hyperframes`), Node 20+, ffmpeg
- Python 3.11+ with `Pillow`, `numpy` and `scipy` (for `scripts/`)

## Setup

1. **Your Flow profiles (private).** Copy `google-flow/profiles.example.json` to `~/.gflow/profiles.json` and list your own gflow profiles and project ids in failover order. Set `$GFLOW_PROFILES` to use another path. This file stays on your PC and is never committed.
2. **Where videos go.** Set the `VIDEO_WORK_ROOT` environment variable to your video work folder. Each Short gets its own folder under `%VIDEO_WORK_ROOT%\<Subject>\2D Animation\videos\`. If it isn't set, the skill asks you.
3. **Reference frames.** `assets/reference/README.md` lists the art-direction frames the style guide refers to. They were cut from another creator's videos, so they aren't included. Add your own targets there if you want them.

## What's inside

| Path | What it is |
|---|---|
| `SKILL.md` | The workflow Claude follows, from topic to publish kit |
| `references/` | Story, storyboard, shot options, style, Flow prompts, build and publish guides |
| `google-flow/` | Flow rulebook, batch runner, example manifest and profiles file |
| `scripts/` | Project builder, cutouts, eye locator, motion/FX helpers, prompt-sheet and publish-kit generators |
| `archive/` | Retired routes (code-drawn puppet, prompt sheet), kept for reference |

## License

MIT, see [LICENSE](LICENSE).
