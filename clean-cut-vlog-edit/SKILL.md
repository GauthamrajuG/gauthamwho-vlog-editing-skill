---
name: clean-cut-vlog-edit
description: Use when the user (a Tamil/English vlog creator, GauthamWho) hands over their own phone footage — a single clip they already assembled in order, or a folder like "Reel 29" — and asks to edit it, make it a reel, make it "high retention", tighten it, cut the empty spaces, or add punch-ins/zooms, even when they only paste a path. Also use when they want graphics, 3D objects, characters or effects (like the air fryer, globe or ghost) composited INTO their real footage at a moment they name, with or without a script of what should happen, tracked to the room or to them. Takes priority over reel-edit, short-form-edit, directing-live-video and any skill that restructures, decorates or adds music to footage.
---

# Clean-cut vlog edit

## Overview

The creator has already done the story edit: the clip arrives in the order they want, shot by
shot, often with small deliberate sequences built in (show the bag → drop it → a black clip →
walk in). **Your job: remove the dead air while they talk, add a few consistent face punch-ins
on the lines that matter, and deliver it in a colour that looks like their iPhone original —
nothing else.** "High retention" from this creator means tight talking plus a handful of
punch-ins, never hooks, transitions, music, graphics or reordering.

Approved reference: Reel 29 → `Reel 29/Reel29_clean_SDR_v5.mp4` (posted) and
`Reel29_clean_HDR_v5.mp4`. Every rule below comes from what the creator accepted or rejected
while making it.

**This skill does two jobs:**
- **Job A, the clean edit** (below): every time they ask for an edit.
- **Job B, story graphics**: 3D objects or characters composited into the real footage at a
  moment they name, often from a script they give ("at 0:36 a ghost rises behind my left
  shoulder, then…"). It runs on its own when they bring a clip just for graphics, or after
  Job A is approved. Approved examples: Reel 29 v6 (air fryer + slowing globe) and v7 (the
  hooded ghost). Job B never changes the rules of Job A.
Only Job B may open Remotion. Everything in "Story graphics (Job B)" below is mandatory for it.

## When to use

- Their own vlog / day-in-the-life footage, already ordered (one long clip, usually iPhone HEVC
  Dolby Vision profile 8.4 / HLG HDR, 60 fps, 9:16, Tamil speech).
- "Edit this", "make it a reel", "high retention", "cut the empty spaces", "add zooms".
- Even if they also mention Remotion, HyperFrames, "centre the frame", "transitions" or
  "effects" — those words do not license effects. The punch-ins below are the effect.

- Job B: "add a graphic / animation / 3D object / ghost / effect to my clip at 0:36", "here is
  my clip and the script of what should happen", "track it to the video", "like the air fryer".

Not for: fully animated videos with no real footage (GoldKiller/Vox-style explainers, ads
built from a script alone: use directing-live-video), or footage someone explicitly asks to
restructure.

## The finished edit, as a recipe

1. **Uncut opening** — 0:00 to the last word of the first talking shot + 0.2 s, exactly as
   shot (no cuts, no punch-ins).
2. **Talking stretches** — every silence between words longer than **0.25 s** removed, with
   **0.08 s** of air kept before the first and after the last word. Stammers and repeated
   words removed (the stumbled take goes, the clean one stays). Never cut inside a word.
   Exception: when the pauses are the content (out of breath after a set, a deliberate dramatic
   beat), keep them with a looser gap for that range (`gap_overrides`, e.g. 1.0 s) — offer
   this in the intake message when you see such a scene.
3. **Non-talking shots** — kept in place, in order. Only an *empty* head or tail is shaved
   (≈12 % each end, max 0.4 s). Never shave:
   - the **completion of an action** (plug in → *switch on*; drop food → *close the lid*);
   - a **deliberate micro-sequence** the creator built (show the bag → drop it → **black
     clip** → walk in). A black clip between shots is a creator transition, not an error.
   When a shot's head or tail holds any of these, keep the shot whole.
4. **Protected shots play whole** — everything the creator names, and by default:
   single-angle actions of any length (food into the air fryer + lid closing, a whole set of
   squats, a pour), silent moments to camera
   (a look, a wink while washing up), and the payoff (plating) through to the end.
   A non-talking shot between two protected shots is protected too.
5. **Face punch-ins** — see the next section. The only reframing in the whole edit.
6. **Joins** — plain hard cuts in source order. Nothing between them.
7. **Picture** — the original's colour and framing, Dolby Vision kept, original fps (60).
8. **Sound** — only their recording: a 20 ms fade at every join, loudness −14 LUFS with true
   peak ≤ −1 dBTP. No music, no sound effects.
9. **Two files** next to the source (folder "Reel 30" → name `Reel30`):
   - `Reel30_clean_SDR.mp4` — **the default, the one that gets posted.** H.264 BT.709, made
     from the clip's own Dolby Vision mapping, so every phone shows the bright iPhone look.
   - `Reel30_clean_HDR.mp4` — Dolby Vision 8.4 HEVC 10-bit, for HDR phones / archive.
10. **Final hand-off** — when the creator approves a version, copy it into
   `Reel 30/Final video/` with a unique, versioned name they can refer to later:
   `GauthamWho_Reel30_<Topic>_v<N>_SDR.mp4` (Topic = 1–2 words for the reel's idea, e.g.
   `GauthamWho_Reel29_AirFryerWorld_v6_SDR.mp4`). Keep the working files where they are.
   Don't send it to Telegram unless asked (bots can't send over 50 MB; the creator said no
   need).

## Face punch-ins (the approved retention effect)

Vocabulary the creator uses — use these names in every message:

| Name | Meaning | Status |
|---|---|---|
| **Jump cut** | a cut inside a shot that removes time (the pauses) | always |
| **Punch-in** | hard cut to a tighter crop of the same shot (CU of the face), no movement | **yes** |
| **Punch-out / reset** | hard cut back to the normal framing | yes, at the next jump cut |
| **Eye-line lock** | the eyes stay at the same place every punch-in | yes, always |
| **ECU** | extreme close-up on only the eyes or only the mouth | **rejected** |
| **Detail punch / insert** | punch-in on an object or action (food, air fryer, hands) | **rejected** |
| **Pull-back with matte** | smaller than normal, black borders around | **rejected** |

The spec:

- **Size:** 130 % — one size for every punch-in.
- **How many:** one per talking scene, on its strongest line — a claim, a twist, a struggle
  or the call to action. About 2–4 per minute (retention-editing). Reel 29 (84 s): 5.
- **Where never:** the uncut opening, cooking / top-angle / protected b-roll shots.
- **Framing:** horizontally the crop zooms around the eyes (they keep their screen x, nothing
  slides sideways); vertically the eyes go onto the **upper-third line** as far as the frame
  allows (lands at ~33–39 % from the top).
- **Timing:** cut in where the line starts, hold until the **next jump cut**, cut back there,
  so the punch-out hides inside an existing cut. A punch-in never crosses a jump cut. If the
  line itself contains a jump cut (a pause inside it was removed), the punch-in starts at that
  cut instead — on the part of the line with the key words — and still ends at the next one.
- **Eye points are measured by eye** on gridded frames (`scripts/eye_grid.py`), never taken
  from face detection.

Reel 29's five (for calibration): "who'll put petrol?" · "so I don't want to eat here" ·
"it shouldn't go to waste" · "the time will be slow" · "you follow my…" (to the end).

## Intake: one message, at most four questions

Analyse first (probe, shots, transcript + English translation, dense contact sheet — see
`reference/pipeline.md`) so every question carries real timestamps. Then send **one** message:
a short shot list, the defaults you'll apply without asking, and **one AskUserQuestion call
with at most 4 questions** (2–4 options, recommended first):

| # | Question | Options | "Your call" default |
|---|---|---|---|
| 1 | Where does the uncut opening end? | after the first talking shot's last word (time) · end of that shot · after the next shot · no uncut opening | first |
| 2 | Which moments must play completely uncut? (multiSelect) | up to 4 detected candidates with times: single-angle actions, moments to camera, action sequences (plug→switch, bag→drop→black→walk-in), payoff → end. One action sequence = one option, black clip included; more than 4 → group neighbours | all of them |
| 3 | Which lines get a punch-in? (multiSelect) | one strongest line per talking scene, quoted in English with time; group if more than 4 scenes | all proposed |
| 4 | Silent shots you won't protect (name them): | shave only empty heads/tails · keep whole · shorten long ones to ~3 s (only if one runs over 5 s) | shave empty only |

Stated in the message text, not asked:
- stammers and repeated takes you found are removed — name them with times and say which take
  you keep (judged from the translation and timings; you cannot listen, so they can correct it);
- the estimated length — from a `plan_cuts.py` run with the defaults *before* the intake, so
  the number is real. ffmpeg-skill's Reels check flags anything over 90 s; Instagram itself
  allows longer Reels, so over 90 s is the creator's call — offer Q4 option 3, never cut into
  protected moments;
- an out-of-breath / dramatic-pause scene, if there is one: you'll keep its pauses (rule 2);
- what you will NOT do: no music, SFX, transitions, graphics, captions, ECUs, detail punches,
  pull-backs, reordering, Remotion or HyperFrames. If they asked to "centre the frame", say the
  framing stays original apart from the punch-ins, and ask them to name the shot if one
  specific shot looks badly framed to them;
- you deliver the SDR file (posted) and the HDR/Dolby Vision file.

## Workflow

1. **Machine check** — free memory ≥ 3 GB (`reference/pipeline.md` §0). If not, stop and ask
   the creator to restart `AppXSvc` (they run it; never kill processes yourself).
2. **Analyse** — probe; `scenes.py --shots`; audio → `transcribe.py` (transcribe + translate,
   Tamil); `look.py --tiles 12x8` contact sheet. Name every shot; find action sequences,
   black clips, moments to camera, stammers and each scene's strongest line. Run
   `plan_cuts.py` once with the defaults to get the length estimate for the intake.
3. **Intake** — the four questions above. Wait for the answer.
4. **Cut plan** — `plan.json` → `scripts/plan_cuts.py` → `segments.txt`. Must print
   `WORDS CUT BY MISTAKE: none`; act on every `CHECK -` line. Then open the sheet at every
   b-roll shave and confirm no action completion or black clip was trimmed (rule 3).
5. **Punch windows** — for each approved line: source start = first word − 0.08 s; end = the
   end of the segment it sits in (next jump cut). `scripts/eye_grid.py` at start and middle
   of each window → eye (x, y) fractions.
6. **Build** — `build.json` → `scripts/build_reel.py` (both files, from the original). Run it
   in the background; ~15 min for 85 s on this PC.
7. **Verify** (every item, before sending):
   - `check.py --platform reels` on the SDR file: 13 checks, 0 failed, only the subtitles WARN;
   - HDR file: `dv_profile=8` in ffprobe stream side data, Dolby Vision RPU on every frame;
   - 60 fps, duration = the plan's total;
   - frames at each punch-in from the **SDR file**: eyes on the upper-third line, same size,
     no sideways shift;
   - frames across each restored action sequence and protected shot: present, uncut.
8. **Report** — five labelled lines (`Done:` file, length, resolution, fps, colour, loudness ·
   `Steps:` · `Check:` · `Look:` the PNG you inspected · `Notes:`), then a plain list of every
   punch-in (time + line) and every remaining cut region, so the creator can ask for any of it
   back. Keep it simple: the creator is new to editing terms — explain any term you use.

## Story graphics (Job B)

Runs on its own (a clip brought just for graphics) or after the clean edit is approved, and
only at the moments the creator names. Approved example 1: Reel 29 v6, "after I switch on
the air fryer, the world gets slow". A modelled air fryer drops in and its drawer slides
shut, a wrist-up hand clicks the button, and a globe spinning left→right slows to a crawl.
On "slow" (the punch-in) the fryer is thrown off and the globe glides behind his head, then
squashes and whips away with a stretch.

### Ideas first (the creative engine)

When the creator gives a clip without a script, or asks for ideas, or a script leaves room:
run `reference/creative-engine.md` before anything else. That means the opportunity
inventory of the footage, at least one idea per lens (10 lenses, including the hidden passenger
like the ghost and the audience's viewing moment), the anti-generic filter (the 10-second
test, surprising-but-safe, fits the frame, send-worthy, 1–3 per reel), and the top 3 sketched
for them to choose from. Never offer the first obvious idea alone. Check
`D:/Claude/Video/lore.md` for callbacks.

### Use the best skills at every stage

`reference/skill-routing.md` maps each stage (ideas, beat sheet, look, lighting/compositing,
motion, camera, framing, motion blur, sound, retention, review) to the installed skills and the
exact files to read: directing-live-video, business-motion-film, shot-recipes,
animation-principles, motion-doctrine, shot-composition, color-motion, the 13 threejs-* skills,
remotion-best-practices, and the vendored vfx-compositing / cinematic-shot-direction /
social-short-production guides in `vendor/`. It also lists the skills that are **never** used
(paid APIs, AI video). Our rules override all of them.

### From their script to frames (do this before any storyboard)

1. Analyse the clip as in Job A: probe, shots, Tamil word timings + translation, contact sheet.
2. Turn the script into a **beat sheet**. Each beat = what happens, to which object, from frame
   → to frame (60 fps). A spoken line is located by its word timings, an action ("when I walk
   in") by its shot. Note where the person is in every beat (shoulder line, head, hands),
   measured from the frames.
3. Send the beat sheet in **one message** with the questions that are really open: sides
   ("your left shoulder = screen right?"), how realistic, sound yes/no, and anything in the
   script that can't fit the frames (say why, offer the nearest version). Wait for the answer.
4. Then the approval ladder, a yes at every rung, never skipped:
   **storyboard on the real frames → storyboard with the real 3D composited (dotted outline
   where hidden, the path drawn in) → one full-quality still → animation → ~4–5 s preview with
   sound → swapped into the full video as the next version** (`Final video/` naming, rule 10).

### The realism checklist (every object, every frame — non-negotiable)

1. **Whole object, always.** Model and render the complete body or object, including the parts
   hidden behind the person or below the frame edge. Never end a body in a straight line,
   fade or dissolve it to save modelling, or build only the visible half: when it moves, the
   viewer sees all of it. Only the person's cut-out (or a real foreground object) hides it.
2. **Depth.** SAM 2.1 cut-out of the person on every frame, refined with a guided filter so
   hair strands stay in front. Graphics go behind them where the script says. Nothing is
   pasted over a face.
3. **Locked to the scene.** Anchor to the person (shoulder or head measured from the cut-out
   each frame) or to a surface by camera tracking, but only if the tracking is validated (grid
   overlay). If it isn't accurate, keep it fixed and say so.
4. **Lit by the room.** Key light from the scene's real light direction and colour (look at
   which surfaces are bright), a dim fill, reflections from an environment map. A dark scene
   gets a dark object that is still readable by its rim.
5. **Graded to the footage.** Lift the CG blacks to the plate's black level, match warmth and
   saturation, soften to the plate's sharpness, defocus by depth (behind the person = like
   the wall), add the plate's own measured noise, and motion-blur along the travel.
6. **Shadows.** A soft contact or cast shadow on the nearest surface, away from the light.
7. **Light it gives off lights the world.** Glowing eyes, screens or fire are light sources,
   computed in linear light with inverse-square falloff: a rim on the person's edges that face
   it, a back-light rim when it's behind them, a local spill on nearby walls, and lens bloom
   on what's visible.
8. **Moves like it's alive or has weight.** Springs with overshoot, anticipation before a big
   move, arcs and curves (never straight sticker slides), easing, secondary motion (cloth,
   hems, tails trail through a spring follower), breathing when still. Cap banking (~0.3 rad).
9. **Sides are the creator's body sides.** In a non-mirrored iPhone selfie their LEFT is
   SCREEN RIGHT. Always write both.
10. **Sound only for the graphic.** Synthesised, soft and sparse (no glitches, sparkles,
    buzzers, dings, long risers), at most one every 1.5–2 s, under the voice; overall
    −14 to −15 LUFS.
11. **Self-check before showing anything.** Look at frames across the whole beat, twice.
    Check the frame count of every output and the frames at both joins (difference < 1/255
    against the sources).
12. 60 fps, no AI-generated video, no paid services.

What made example 1 land (from their feedback):
- **objects act out the words**: no text, no speed lines;
- **properly modelled 3D** (Remotion + `@remotion/three`) with physics in the motion;
- **graded into the room**: black level, warmth, grain, softness, a soft wall shadow;
- **depth**: their SAM 2.1 cut-out laid back on top, so the graphic sits behind them;
- **tracking only if it's accurate**; otherwise fixed (on a plain wall it drifted, so it
  was skipped);
- the quality bar is a professional After Effects designer.

Second approved example, Reel 29 v7: a **hyper-real hooded ghost** on the dark walk-in. It
rises behind their LEFT shoulder (screen right) only to shoulder level, its red eyes light
them and the wall like a real light, then it swoops behind their neck on a curve and out
over the other shoulder. It moves like a living thing (spring rise, breathing,
anticipation, trailing cloth) and has a full body, never a sticker cut.
- **Sides = the creator's own body sides.** Write "your left shoulder (screen right)".
- **Light from a graphic must physically light the person and the room** (rim, back-light,
  local spill, bloom) when the creator asks for realism.
- Storyboard with the real 3D figure on the real frames (dotted where hidden) → still →
  4.5 s preview with sound → full video.

Full pipeline, numbers and traps: `reference/story-graphics.md`. Code to start from:
`scripts/graphics/` (+ `ghost/`), `templates/remotion-story-graphic/` and `templates/remotion-ghost/`.

## Judging colour (where every earlier attempt went wrong)

- The creator judges against their **iPhone original**. Dolby Vision players (iPhone) show it
  bright and punchy; VLC on Windows ignores Dolby Vision; ffmpeg-skill `look.py` previews use a
  generic tone map that is *darker* than the real look. Never declare colour "matching" from
  `look.py` frames of an HDR file — compare frames taken from the **SDR file**.
- The SDR file must come from `libplacebo apply_dolbyvision` (the clip's own Dolby Vision
  mapping). ffmpeg-skill `color.py --to-sdr` came out dim and grey — rejected.
- Never process HDR through ffmpeg-skill `broll.py` (its overlay runs in 8-bit) or through
  multiple re-encodes: v3 went through 13 overlay passes and went flat. Encode each piece once
  from the original; join with a stream copy.

## Common mistakes (all made on Reel 29, all rejected)

| What happened | What the creator wanted |
|---|---|
| Hooks, flash-forwards, whip/zoom transitions, flashes, music, SFX, HyperFrames graphics | Hard cuts, their audio, no graphics |
| Reordered (payoff shot as a hook) | Their order, untouched |
| Converted to SDR with a generic tone map; later dropped Dolby Vision | Original look: Dolby Vision kept, SDR from the clip's own DV mapping |
| Face-tracking reframe / constant zoom to "centre the frame" | Original framing; only the approved punch-ins |
| 36 punch-ins: ECUs on eyes/mouth, detail punches, black-border pull-backs, framing jumping up and down | One 130 % face punch-in per scene, eye-line locked, eyes on the upper third |
| Built v3 with 13 overlay passes (8-bit) → flat colour | One encode per piece, stream-copy join |
| Trimmed inside protected moments (drop into the air fryer, the wink, the plating) | Those play whole |
| Shaved the "switch on" after the plug, and the bag drop + black clip + walk-in | Action completions and creator micro-sequences stay |
| Natural 0.7 s pause threshold | 0.25 s gaps cut while talking |
| Cut the opening | The opening plays uncut |

## Red flags — stop and re-read the recipe

- You are opening Remotion or HyperFrames, or choosing a transition, font, music or SFX —
  unless the creator asked for a story graphic (Job B), and then only for those beats.
- Job B: you offered one idea, or ideas a generic AI would give, without running the creative
  engine; or you used a skill from the "never" list in skill-routing.md.
- Job B: a body or object ends in a straight line or fades out where it's "not seen", you
  skipped a rung of the approval ladder, a glowing thing doesn't light its surroundings, the
  graphic is sharper/cleaner/brighter-black than the footage, or it slides in a straight line.
- An ffmpeg command uses `split` + `trim` on one long input (it buffers frames in RAM and
  can drop frames silently), or you're delivering without checking the frame count.
- You are about to run ffmpeg-skill `broll.py`, `color.py --to-sdr` or `fit.py` on this footage.
- A punch-in is in the opening, on b-roll, crosses a jump cut, isn't 130 %, or a scene has two.
- A segment list moves a shot out of order, or trims a black clip or an action's completion.
- You judged colour from `look.py` frames of the HDR file, or from VLC.
- You started cutting before the intake answer, or encoding with < 3 GB free memory.

Exact commands, file formats, tools, downloads and machine fixes: `reference/pipeline.md`.
Story graphics: `reference/story-graphics.md`. Ideas: `reference/creative-engine.md`.
Which skill at which stage: `reference/skill-routing.md`.
