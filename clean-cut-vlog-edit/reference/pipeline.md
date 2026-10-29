# Clean-cut vlog edit — pipeline reference

Everything runs from a work folder outside the footage folder, e.g. `D:/Claude/Video/work/reel30/`.

```bash
S="$HOME/.claude/skills/ffmpeg-skill/scripts"        # ffmpeg-skill (analysis, checks)
K="$HOME/.claude/skills/clean-cut-vlog-edit"        # this skill
FULL="D:/Claude/Video/tools/ffmpeg-full/ffmpeg-9.0.2-full_build/bin/ffmpeg.exe"
SRC="D:/Claude/Video/Reel 30/IMG_XXXX.MP4"          # the creator's file — read only
W="D:/Claude/Video/work/reel30"; mkdir -p "$W"; cd "$W"
```

On Windows run Python as `py`; inside the venv as `.venv/Scripts/python`.

## 0. Tools, skills and the machine

### What is installed and why

| Tool / skill | Where | Used for |
|---|---|---|
| ffmpeg 9.0.2 essentials (on PATH) | `C:/Users/Gauthamraju/AppData/Local/Programs/ffmpeg/bin` | everything except the SDR conversion; its libx265 keeps Dolby Vision |
| **ffmpeg 9.0.2 full build** (gyan.dev) | `D:/Claude/Video/tools/ffmpeg-full/ffmpeg-9.0.2-full_build/bin/ffmpeg.exe` | only `libplacebo apply_dolbyvision` → the SDR file. Needs a Vulkan GPU (GTX 1650 works) |
| ffmpeg-skill 2.17.3 (`npx ffmpeg-skill`, repo kajisho5/ffmpeg-skill) | `~/.claude/skills/ffmpeg-skill` | probe, scenes, audio extract, look, check. **Not** for encoding this edit (drops Dolby Vision; `broll.py` is 8-bit) |
| faster-whisper (job venv) | `<work>/.venv` | Tamil word timings + English translation |
| opencv-python-headless **< 5** (job venv) | `<work>/.venv` | `eye_grid.py`. OpenCV 5 removed the Haar detector; the 4.x line is what's tested |
| skill **retention-editing** (thecraighewitt/skills) | `~/.claude/skills/retention-editing` | pacing rules: dead air > 1 s goes; 2–4 zoom-ins per minute on key moments; match edit energy to content |
| skills motion-art-direction, shot-composition (installed) | `~/.claude/skills/` | restraint pass, one consistent motion size, focal point on the upper-third line |

Skills looked at and **not** used (2026-10-29 search): reel-editor (nicolapocock — punch-in
on every sentence + every 2.2 s, the busy look the creator rejected), short-editing (melvynx)
and short-form-edit (motion graphics, captions, music on every beat), marketingskills/video
(AI generation), postplus editing-decision-engine (retired). Remotion and HyperFrames: not
used for this kind of edit.

Re-downloading the full build if it is missing (ask the creator first — it's a 169 MB download):
`https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z` → verify the SHA-256 against
the `.sha256` file published next to it (9.0.2: `f0e46253c70dfe902bac915dfb4224f0cf1b7c6eeab9da2ccc9a5581f9a71b13`)
→ extract with Windows' own tar (`C:/Windows/System32/tar.exe -xf ffmpeg-full.7z`; Git-Bash
tar cannot read 7z). Running a freshly downloaded exe needs the creator's explicit OK.

### Memory (this PC has 7.5 GB RAM and a leaking Windows service)

Check before every encode; need ≥ 3 GB free virtual memory:
```powershell
$o=Get-CimInstance Win32_OperatingSystem; "{0:N0} MB free" -f ($o.FreeVirtualMemory/1KB)
```
If it's low, find the cause:
```powershell
Get-Process | Sort-Object PagedMemorySize64 -Descending | Select -First 8 Name,Id,@{n='MB';e={[int]($_.PagedMemorySize64/1MB)}}
```
- A `svchost` of many GB is almost always **AppXSvc** (AppX Deployment Service — installs and
  updates Microsoft Store apps; it leaks memory on this PC, up to 11 GB). The creator fixes it
  without rebooting, in an **administrator** PowerShell: `Restart-Service AppXSvc -Force`
  (safe: no files lost, no apps closed). Optional prevention: Microsoft Store → Settings →
  App updates off.
- Another Claude session rendering (`node … remotion-cli.js render`, `ffmpeg … pre-encode`)
  also eats memory — wait for it; never stop someone else's process.
- Symptoms of low memory: `Cannot allocate memory`, `std::bad_alloc`, x265 `malloc … failed`,
  exit `0xC00000FD`, OpenBLAS / `mkl_malloc` errors, bash `fork: Resource temporarily unavailable`.

## 1. Probe

```bash
py "$S/probe.py" "$SRC" --json > probe.json
```
Note `duration`, `fps` (iPhone: 60), `hdr_format` ("Dolby Vision profile 8" = good), size.

## 2. Analyse

```bash
py "$S/scenes.py" "$SRC" --shots --json > shots.json
py "$S/look.py" "$SRC" --tiles 12x8 --width 2400 -o dense_sheet.png     # ~1 tile/s; read it all
py "$S/audio.py" "$SRC" -o "$W/audio.wav"
```
A closer look at any stretch: `py "$S/look.py" "$SRC" --at 82.9 --at 83.4 ... -o at/f.png`.
(`look.py` tone-maps HDR generically — fine for content, **not** for judging colour.)

### Transcriber (one venv per job)

```bash
py -m venv .venv
.venv/Scripts/python -m pip install -q --no-compile --no-cache-dir faster-whisper "opencv-python-headless<5"
export PYTHONIOENCODING=utf-8 OPENBLAS_NUM_THREADS=1
.venv/Scripts/python "$K/scripts/transcribe.py" audio.wav small transcribe ta
.venv/Scripts/python "$K/scripts/transcribe.py" audio.wav small translate ta
```
- `transcript_transcribe.json` = word timings for the cuts; `transcript_translate.json` =
  English, to understand what is said and pick the punch-in lines.
- Whisper's Tamil text is rough, its timings reliable — cut on timings, judge from the translation.
- `--no-compile --no-cache-dir` and `OPENBLAS_NUM_THREADS=1` matter on this machine.

### What to find on the sheet + transcript

- **Action sequences** to keep whole: plug → switch on; food in → lid closed; show bag → drop →
  black clip → walk in. Any black clip between shots is deliberate.
- **Single-angle actions**, **silent moments to camera**, the **payoff** (first shot of the
  finished dish) → protect candidates.
- **Stammers / repeats** (e.g. "air fryer-la… air fryer-la-la-la").
- **Each talking scene's strongest line** (claim, twist, struggle, CTA) → punch-in candidates.

## 3. Cut plan

`plan.json` (source seconds; a protect range claims every shot it overlaps by ≥ 0.3 s — keep
its ends ≥ 0.3 s inside shots):

```json
{
  "duration": 96.533,
  "transcript": "transcript_transcribe.json",
  "shots": "shots.json",
  "intro_end": 9.05,
  "protect": [[44.1, 51.0], [56.0, 58.4], [60.5, 65.5], [83.5, 95.0]],
  "remove": [[30.12, 30.90]],
  "gap": 0.25,
  "pad": 0.08,
  "broll": "trim",
  "broll_max": 0,
  "fps": 60
}
```
```bash
py -I "$K/scripts/plan_cuts.py" plan.json      # prints segments, writes segments.txt
```
Optional `"gap_overrides": [[a, b, 1.0]]` keeps pauses up to 1.0 s between a and b — for a
scene whose pauses are the content (out of breath after a set).

Required before building:
- `WORDS CUT BY MISTAKE: none`; every `CHECK -` line handled;
- the `protected shots` line matches what the creator named;
- every shaved b-roll head/tail checked on the sheet — no action completion, no black clip
  removed (if one was: add the shot to `protect`, re-run).

Reel 29's approved segments (83.8 s from 96.5 s):
```
0-9.05,10-11,12.22-13.88,14.67-16.26,16.41-18.4,18.7-19.4,19.95-22.05,22.45-24.56,
24.93-30.12,30.9-35.18,35.58-39.15,39.85-41.35,41.9-43.3,43.717-51.8,52.1-53.1,53.3-54.25,
54.4-55.4,55.617-72.15,72.45-74.2,76.1-79,80-81.8,82.917-96.533
```

## 4. Punch-in windows and eye points

For each approved line: start = its first word − 0.08 s (source time); end = the end of the
segment it sits in (the next jump cut). Then:
```bash
.venv/Scripts/python "$K/scripts/eye_grid.py" "$SRC" eyes.png 16.6 17.5 25.2 27.0 ...
```
Read the point between the eyes on each tile as fractions (lines are 10 %), average the two
tiles of each window. Reel 29's were 0.40–0.62 across, 0.47–0.53 down.

## 5. Build both files

`build.json`:
```json
{
  "source": "D:/Claude/Video/Reel 30/IMG_XXXX.MP4",
  "out_dir": "D:/Claude/Video/Reel 30",
  "name": "Reel30",
  "segments": "segments.txt",
  "punches": [[16.493, 18.40, 0.60, 0.47], [25.013, 30.12, 0.47, 0.47]],
  "scale": 1.3,
  "ffmpeg_full": "D:/Claude/Video/tools/ffmpeg-full/ffmpeg-9.0.2-full_build/bin/ffmpeg.exe"
}
```
```bash
py -I "$K/scripts/build_reel.py" build.json --dry-run   # pieces, punch-ins, total length
py -I "$K/scripts/build_reel.py" build.json > build.log 2>&1   # background; ~15 min / 85 s
```
What it does: each piece (segment, split at punch boundaries) encoded once from the original
with libx265 `-dolbyvision 1` (VBV cap required), punch pieces cropped to 1/1.3 of the frame
(eyes keep their x, eyes onto the upper third) and scaled back with lanczos → concat-demuxer
stream copy with `-strict unofficial` (keeps Dolby Vision) → audio rebuilt from the original
(20 ms fades, two-pass loudnorm −14 LUFS / −2 dBTP ceiling) → HDR file muxed by copy → SDR
file via the full build's `libplacebo apply_dolbyvision` → H.264 BT.709 CRF 16. It resumes:
finished pieces in `build/` are reused, so a failed run (e.g. low memory) just re-runs.

## 6. Verify

```bash
py "$S/check.py" "<out_dir>/Reel30_clean_SDR.mp4" --platform reels     # 13 checks, 0 failed
ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate:stream_side_data=dv_profile \
  -show_entries format=duration "<out_dir>/Reel30_clean_HDR.mp4"         # 60/1, dv_profile=8
ffprobe -v error -select_streams v:0 -read_intervals "%+#120" -show_frames \
  -show_entries frame_side_data=side_data_type "<out_dir>/Reel30_clean_HDR.mp4" | grep -c "Dolby Vision RPU"   # 120
py "$S/look.py" "<out_dir>/Reel30_clean_SDR.mp4" --at <mid of each punch> -o v/punch.png
py "$S/look.py" "<out_dir>/Reel30_clean_SDR.mp4" --tiles 8x5 --width 1800 -o v/sheet.png
```
Expected on the HDR file's Reels check: pixel format 10-bit and colour HLG flagged — that is
HDR, not a fault. Subtitles WARN on both — the creator wants no captions.

## 7. Iterating after feedback

Feedback arrives as "you cut X, leave it", "the switch-on is missing", "too many zooms". Map
each to a shot by looking at frames around the time, update `plan.json` (`protect` / `gap` /
`remove`) or `build.json` (`punches`), re-run `plan_cuts.py` and `build_reel.py` from the
original (delete `build/` when segments change). Never patch a previous output, never stack
re-encodes. Keep earlier versions until the creator approves the new one.

## Posting

The creator posts the **SDR** file: HDR uploads get Instagram's own automatic conversion on
non-HDR phones, which often looks flat, while the SDR file looks the same everywhere. To
compare for real, they can upload both to a private test (close-friends story / test account)
and watch on their iPhone and an older or Android phone. Move files to the phone by iCloud
Drive or cable, not WhatsApp/Telegram (they recompress and strip HDR).
