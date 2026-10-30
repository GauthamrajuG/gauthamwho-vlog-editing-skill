# GauthamWho — day-in-the-life video editing skill

A Claude Code skill that edits my own pre-ordered phone vlogs (Instagram: **@GauthamWho**)
the way I like them:

- my shot order stays exactly as I edited it;
- the gaps while I talk are cut (pauses over 0.25 s), stammers removed;
- actions and my little sequences stay whole (plug in → switch on; show the bag → drop it →
  black clip → walk in);
- one 130 % face punch-in per talking scene, on its strongest line, eyes always on the same line;
- no music, sound effects, transitions, graphics or captions;
- my iPhone colour kept (Dolby Vision), delivered as an **SDR file to post** plus an HDR file.
- **add-on, only when I ask:** a 3D story graphic that acts out one line (Reel 29: an air
  fryer whose button gets clicked and a spinning globe that slows down), graded into the
  room, behind me, with small sound effects for the graphic only;
- a second approved story graphic: a hyper-real hooded **ghost** that rises behind my left
  shoulder, lights me with its red eyes like a real light, and swoops out behind my neck
  (left/right always means MY body's side);
- the approved final goes into `Final video/` as `GauthamWho_Reel<N>_<Topic>_v<N>_SDR.mp4`.

Built and approved on Reel 29 (October 2026); story graphics approved in Reel 29 v6 (air fryer) and v7 (ghost).

## Companion skills

For story graphics the skill reads other skills at each stage (`gauthamwho-edit/reference/skill-routing.md`).
Install these alongside it:
- [CloudAI-X/threejs-skills](https://github.com/CloudAI-X/threejs-skills) (MIT): copy its 13 `skills/threejs-*` folders into the skills folder.
- Already on the original PC: directing-live-video, business-motion-film, shot-recipes, animation-principles,
  shot-composition, color-motion, motion-art-direction, remotion-best-practices.
The three compositing / shot-direction / social-short guides from
[calesthio/generative-media-skills](https://github.com/calesthio/generative-media-skills) (MIT) are bundled in
`gauthamwho-edit/vendor/`.

## How to call it

| Type in Claude Code | You get |
|---|---|
| `/gauthamwho-edit D:\Claude\Video\Reel 30` | the clean edit: one message with up to 4 questions, then the SDR + HDR files |
| `/gauthamwho-ideas D:\Claude\Video\Reel 30` | the creative engine only: the opportunity list, the top 3 ideas sketched on your frames, and the rest in one line each. Nothing is built |
| `/gauthamwho-start D:\Claude\Video\Reel 30` | both in one message: the edit questions plus a creative menu. The clean edit is built, then the ideas you pick go through the graphics steps |
| `/gauthamwho-edit D:\Claude\Video\Reel 30 at 0:36 a ghost rises behind my left shoulder…` | that graphic from your script: beat sheet → storyboard → still → preview → full video |

Install all three folders (`gauthamwho-edit`, `gauthamwho-ideas`, `gauthamwho-start`). The last
two are short command files that run parts of `gauthamwho-edit`.

## Install

Copy the `gauthamwho-edit`, `gauthamwho-ideas` and `gauthamwho-start` folders into your Claude Code skills folder:

- Windows: `C:\Users\<you>\.claude\skills\gauthamwho-edit`
- macOS / Linux: `~/.claude/skills/gauthamwho-edit`

Or from a terminal:

```bash
git clone https://github.com/GauthamrajuG/gauthamwho-vlog-editing-skill
```

then copy `gauthamwho-vlog-editing-skill/gauthamwho-edit` into the skills folder above.
Restart Claude Code.

## Use

Put the video in its own folder (e.g. `Reel 30`) and tell Claude Code:

> Edit D:\Claude\Video\Reel 30 like last time

or type `/gauthamwho-edit`. It analyses the clip, asks four short questions (where the
untouched opening ends, which moments stay uncut, which lines get a punch-in, what to do with
silent shots), then builds `Reel30_clean_SDR.mp4` (post this one) and `Reel30_clean_HDR.mp4`.

## Needs on the computer

- **ffmpeg** on PATH (gyan.dev "essentials" build is enough for editing)
- **ffmpeg full build** (gyan.dev) for the SDR file, plus a GPU with Vulkan — see
  `gauthamwho-edit/reference/pipeline.md` §0 for the download link and checksum
- **Python 3** (the skill creates its own small environment for the speech transcriber)
- the **ffmpeg-skill** Claude skill (`npx ffmpeg-skill`) for analysis and checks

## What's inside

| File | What it is |
|---|---|
| `gauthamwho-edit/SKILL.md` | the editing style, rules, intake questions and mistakes to avoid |
| `gauthamwho-edit/reference/pipeline.md` | every step with exact commands, tools and PC fixes |
| `gauthamwho-edit/scripts/plan_cuts.py` | turns the transcript + my answers into the cut list |
| `gauthamwho-edit/scripts/eye_grid.py` | gridded frames to place the punch-ins on my eyes |
| `gauthamwho-edit/scripts/build_reel.py` | builds the HDR + SDR files from the original |
| `gauthamwho-edit/scripts/transcribe.py` | Tamil speech → word timings + English translation |
