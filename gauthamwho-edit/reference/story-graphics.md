# Story graphics: 3D motion graphics inside the footage (Job B)

Only when the creator asks for it, and only at the moments they name (a line, a shot, or their script). The approved example is
Reel 29's "after I switch on the air fryer, the world gets slow": v6, `Reel 29/Final
video/GauthamWho_Reel29_AirFryerWorld_v6_SDR.mp4`, at 57.5–63.7 s. The creator's words:
"Oh, I just love what you made."

The graphic is cut into the creator's latest approved SDR file. If they bring a clip just for
graphics, make the SDR plate from the original through its own Dolby Vision mapping (step 2)
and deliver the clip with the graphic. A graphic is never a reason to redo the edit. The
non-negotiable realism checklist is in SKILL.md ("Story graphics (Job B)").

## What the creator wants (every point came from their feedback)

| Wants | Rejected / not wanted |
|---|---|
| Small **3D objects that act out the line** (air fryer + hand presses the button, a globe that slows down) | Text or titles as the graphic (the depth text was a test; for the real thing they asked for objects) |
| Objects **modelled properly**: real shapes, bevels, materials, a display, a drawer that slides in | Flat or rough "clip-art" shapes |
| A **wrist-up hand** (fist with the index finger out) that pops up, clicks and pops away | A whole arm or forearm coming in from the frame edge |
| Motion with physics: springs, overshoot, squash before a fast exit, a stretch along the direction of travel | Speed lines, motion-graphics streaks |
| The globe turns **left to right**, fast, then slows after the click | Spinning the wrong way, or not reacting to the click |
| Colours that **belong in the room**: graded to the footage's black level, warmth and saturation, with grain, softness and a soft shadow on the wall | Clean "CG" colours that sit on top of the video |
| **Depth**: the element goes behind his head (his cut-out laid back on top) | Graphics pasted over his face |
| Camera tracking **only if it's accurate**; otherwise the graphic stays fixed | Tracking that drifts (on a plain wall it did; they said skip it) |
| A few small **SFX for the graphics only**, quiet under his voice | Music, whooshes on the cuts, SFX for things in the footage |
| A **storyboard as photos first**, then a still style frame, then the animation | Animating before the creator approves placement |
| "Premium", like a professional After Effects designer made it | AI-generated video (rejected outright) |

The punch-in rule still applies inside the graphic beat: the 130 % punch-in lands on the
line's key word (Reel 29: frame 130 of the beat, on "slow"). The graphics re-stage
themselves for the tighter crop (the fryer is thrown off, the globe glides behind his head).

## Pipeline (Reel 29 numbers; scripts in `scripts/graphics/`, Remotion in `templates/remotion-story-graphic/`)

0. **Window.** Find the line in the approved v5 SDR (`transcribe.py` words) and give it as
   v5 frames (Reel 29: 3450–3822 = 57.500–63.717 s, 373 frames). Map it back to source
   frames of the original (3956–4328) by walking the segment list.
1. **Storyboard** (`storyboard.py`): 6–8 rough panels drawn on the real frames. They show
   where each object sits, when it moves and what it does. Send it as a picture and wait for
   a yes.
2. **Plate**: the source frames, uncropped, through the same Dolby Vision mapping as the SDR
   file, lossless:
   ```bash
   "$FFMPEG_FULL" -init_hw_device vulkan -i IMG_9265.MP4 -vf "select=between(n\,3956\,4328),setpts=N/FRAME_RATE/TB,libplacebo=apply_dolbyvision=1:colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv:format=yuv420p" -an -c:v ffv1 -level 3 -r 60 plate.mkv
   ```
   Use the uncropped plate because the punch-in crop is applied after compositing.
3. **Cut-out** (`cutout_all.py`): SAM 2.1 base-plus on the GPU (gpu-ai venv), 20-frame
   chunks, each seeded with the previous chunk's last mask. It is resumable after a crash.
   Click points: face, hair, shirt = him; wall = not him. Start on a frame of the right shot
   (frame 0 of a window can belong to the previous shot, and SAM then picks the wall). It
   takes about 1.1 s per frame on the GTX 1650.
4. **3D layer** in Remotion with `@remotion/three` (three 0.178, @react-three/fiber 9, pinned
   to the Remotion version):
   - `shapes.ts`: rounded box/plane helpers;
   - `AirFryer.tsx`, `Hand.tsx`, `Globe.tsx`: modelled objects with props for their states.
     The globe uses world-atlas land + d3-geo on a canvas texture, a fresnel atmosphere and a
     tilt;
   - `Studio.tsx`: RoomEnvironment reflections and a warm key from the room's light direction;
   - `StyleFrame.tsx` / `CgLayer.tsx`: one still to approve the look first;
   - `Motion.tsx`: the beat. Springs for entrances, eased spin speed integrated per frame
     (so the slow-down is smooth), the throw, the glide behind him, then squash, whip and
     stretch for the exit.

   Render on transparency as a PNG sequence:
   ```bash
   npx remotion render AirFryerMotion work/<beat>/cg --sequence --image-format=png --gl=angle --concurrency=1
   ```
5. **Track** (`track_full.py`): wall corners, optical flow, RANSAC similarity, re-seeded every
   20 frames. **Validate it** (overlay a grid and look): if it is worse than none, save an
   identity `track.npy` and say so.
6. **Composite** (`compose_anim.py`, still version `compose_still.py`), per frame:
   - plate;
   - shadow: the CG alpha, blurred and offset away from the light, at 30 %;
   - CG: graded (lift its black to the plate's black, warm tint, 0.93 saturation, 0.6 px
     blur, fresh grain);
   - his matte on top (1 px erode + 1.5 px feather);
   - punch-in crop from the key word.

   It outputs H.264 BT.709 CRF 16 at 60 fps.
7. **SFX** (`sfx.py`): synthesised, nothing licensed or downloaded. Each sound sits on its
   frame and is panned to its object: pop, land, drawer, hand, **click**, tape-stop sweep on
   the slow-down, throw, glide, exit whip. They peak around −16 dBFS and are mixed at −3 dB
   under his voice.
8. **Insert into the full reel.** The video comes from the approved **SDR** file (no second
   HDR→SDR mapping). Read each part as its own input; never `split` + `trim` one input:
   ```bash
   ffmpeg -threads 2 -i v5_SDR.mp4 -threads 2 -i mg_clip.mp4 -threads 2 -ss 63.708 -i v5_SDR.mp4 -i sfx.wav \
     -filter_threads 1 -filter_complex "[0:v]trim=end_frame=3450,setpts=PTS-STARTPTS[v0];[2:v]trim=end_frame=1204,setpts=PTS-STARTPTS[v2];[1:v]setpts=PTS-STARTPTS,format=yuv420p[v1];[v0][v1][v2]concat=n=3:v=1:a=0[v];[3:a]volume=-3dB,adelay=57500|57500[s];[0:a]aresample=48000[voice];[voice][s]amix=inputs=2:normalize=0:duration=first[aout]" \
     -map "[v]" -map "[aout]" -c:v libx264 -preset medium -crf 15 -threads 3 -x264-params rc-lookahead=20 \
     -pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv -r 60 \
     -c:a aac -b:a 256k -movflags +faststart out.mp4
   ```
   `-ss` = (first frame after the beat − 0.5) / 60, so the seek lands exactly on that frame.
9. **Verify**:
   - frame count = the v5 count (`ffprobe -count_frames`; Reel 29: 5027);
   - the frames just before the beat, at its start, middle and end, and just after it all
     match their sources (mean difference < 1/255);
   - loudness −14 to −15 LUFS, peak ≤ −1 dBFS;
   - a contact strip across both joins and inside the beat.

The HDR/Dolby Vision file does not get the graphic unless the creator asks (it would need
the CG composited in HDR). Say so when you deliver.

## Memory traps hit on this beat

- `split` → `trim` → `concat` on one input makes ffmpeg hold every frame of the later branch
  in RAM while the first plays. That is about 3,000 raw 1080×1920 frames. It produced
  `Cannot allocate memory`; one run silently **dropped 128 frames** (2 s), so the picture
  drifted against the voice while the encode still "succeeded". Always check the frame count.
- With ~1 GB free, x264 `-preset slow` failed to `malloc`. Use `-threads 1–3`,
  `rc-lookahead=15–20` and `-preset medium`.

## Depth text (tested, loved, not used in the final)

"SLOW" set behind his head in the kitchen shot, using the same layers as step 6 (text from
HyperFrames as RGBA frames, `depth_text_composite.py`). Offer it only when the creator wants
words rather than objects. They still add captions themselves later.

## Example 2: the walk-in ghost (Reel 29 v7, approved)

`Reel 29/Final video/GauthamWho_Reel29_AirFryerGhost_v7_SDR.mp4`, 36.15–37.85 s (the dark
stair walk-in, plate_wide indexes 23..124 = source frames 2623..2724). This is a reaction
graphic with no spoken line: the creator picked the shot and described the beat. Code:
`scripts/graphics/ghost/`, Remotion `templates/remotion-ghost/`.

### What the creator asked for, and corrected

| Asked / corrected | Rule it became |
|---|---|
| "My right shoulder" turned out to mean **their own** right | **Sides are always the creator's body sides.** In a non-mirrored iPhone selfie (shop signs read normally), their LEFT shoulder is SCREEN RIGHT. Say both in every message: "your left shoulder (screen right)". |
| A white-sheet/cartoon ghost → "horror, dark body, dark clothes, glowing eyes, hyper realistic" | Hooded, dark-robed 3D figure (lathe profile with cloth folds, velvet sheen), black face void, two slanted emissive eyes (angry = inner corners low). |
| "The glow should reflect on me based on physics" | The eyes are a light source. Its inverse-square falloff is computed in **linear light**. On the person: a rim on the edges that face the eyes (outward normal from the blurred matte · direction to the eyes), and a back-light rim when the eyes are behind them. On the wall: only a local spill (the eyes face forward). Plus lens bloom from the visible eyes. |
| "Don't come up this high, only to my shoulder" | Peeks rise only to the shoulder line. Find it from the cut-out every frame. |
| "Lower body cut like a sticker" (a smoke dissolve at the chest) | **Full body**, solid down out of frame. No smoke cut. Ragged only along the outline. |
| "Not a sticker sliding to a place: a living thing with physics" | Rise with a **damped spring** (overshoot, settle) and **breathing**; **anticipation** before it moves; exit on a **Catmull-Rom curve** (dip behind the neck, out over the other shoulder), accelerating; the **hem follows the head through a spring** (secondary motion); cloth ripple speeds up with motion. Cap banking at ~0.3 rad: 0.5 rad + motion blur made the eyes read as "‖". |
| Storyboard v1/v2 were flat 2D sketches | Storyboard v3 = the **real 3D figure composited on the real frames**, with **dotted outlines** where it's hidden (dark, or behind them) and the exit path drawn in. That's what got approved. |

### Pipeline differences from the air fryer

- **Locked to the person, not the wall.** Their shoulder and head positions come from the
  cut-out every frame (`motion.py`, lightly smoothed), so the ghost rides the handheld shake.
  No optical-flow camera tracking needed.
- **The motion is solved in Python** (`motion.py` → `track.json` with x, y, rot, eyes, drag,
  phase, velocity per frame). Remotion only draws it (`GhostMotion.tsx`), and the compositor
  reads the same file for the light position and motion blur. There is one source of truth.
- **Hair:** refine the SAM matte with a guided filter on the plate (`guided()`, r 10, eps
  2e-3), solid inside and empty far outside, so strands stay in front of the figure.
- **Cut-outs on many frames** (`cutout_shot.py`): seed with a good single-frame matte, then
  propagate forward in 20-frame chunks and backward. It resumes from the last mask. Check
  IoU against the hand-checked storyboard mattes (≥ 0.97). For single frames, try 6 click
  sets (3 on the head, 3 on the body) and keep the best IoU. One click set alone sometimes
  dropped the head.
- **Sound** (`sfx.py`): low rumble as it rises, a hiss + low hit when the eyes ignite, and a
  whoosh panned right → left on the exit. About −13 dBFS peak before mixing; the mix stays
  at −14.9 LUFS.
- **Delivery:** a ~4.5 s preview with sound first (`preview.sh`). After the yes, swap the
  window into the latest approved full version as the next version number. Check the frame
  count and the frames at both joins.

### Traps

- Remotion `--sequence` names files `element-000.png` (zero-padded to the frame count).
- `CUDA error: unknown error / resource already mapped / Memory allocation failure` in SAM
  meant the PC was out of **RAM** (AppXSvc leak), not a GPU fault. Keep only 960-wide
  frames in memory and ask the creator to end AppXSvc (Task Manager → Details → svchost
  with that PID → End task).
