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

## Install

Copy the `clean-cut-vlog-edit` folder into your Claude Code skills folder:

- Windows: `C:\Users\<you>\.claude\skills\clean-cut-vlog-edit`
- macOS / Linux: `~/.claude/skills/clean-cut-vlog-edit`

Or from a terminal:

```bash
git clone https://github.com/GauthamrajuG/gauthamwho-vlog-editing-skill
```

then copy `gauthamwho-vlog-editing-skill/clean-cut-vlog-edit` into the skills folder above.
Restart Claude Code.

## Use

Put the video in its own folder (e.g. `Reel 30`) and tell Claude Code:

> Edit D:\Claude\Video\Reel 30 like last time

or type `/clean-cut-vlog-edit`. It analyses the clip, asks four short questions (where the
untouched opening ends, which moments stay uncut, which lines get a punch-in, what to do with
silent shots), then builds `Reel30_clean_SDR.mp4` (post this one) and `Reel30_clean_HDR.mp4`.

## Needs on the computer

- **ffmpeg** on PATH (gyan.dev "essentials" build is enough for editing)
- **ffmpeg full build** (gyan.dev) for the SDR file, plus a GPU with Vulkan — see
  `clean-cut-vlog-edit/reference/pipeline.md` §0 for the download link and checksum
- **Python 3** (the skill creates its own small environment for the speech transcriber)
- the **ffmpeg-skill** Claude skill (`npx ffmpeg-skill`) for analysis and checks

## What's inside

| File | What it is |
|---|---|
| `clean-cut-vlog-edit/SKILL.md` | the editing style, rules, intake questions and mistakes to avoid |
| `clean-cut-vlog-edit/reference/pipeline.md` | every step with exact commands, tools and PC fixes |
| `clean-cut-vlog-edit/scripts/plan_cuts.py` | turns the transcript + my answers into the cut list |
| `clean-cut-vlog-edit/scripts/eye_grid.py` | gridded frames to place the punch-ins on my eyes |
| `clean-cut-vlog-edit/scripts/build_reel.py` | builds the HDR + SDR files from the original |
| `clean-cut-vlog-edit/scripts/transcribe.py` | Tamil speech → word timings + English translation |
