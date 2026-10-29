"""Build the finished reel from the creator's ORIGINAL file: the clean cut, the
approved face punch-ins, Dolby Vision kept, plus the SDR version that is posted.

Usage (from the job's work folder):
    py -I build_reel.py build.json            # build both files
    py -I build_reel.py build.json --dry-run  # list pieces and totals only

build.json:
{
  "source":   "D:/Claude/Video/Reel 30/IMG_XXXX.MP4",   # the original, read only
  "out_dir":  "D:/Claude/Video/Reel 30",
  "name":     "Reel30",                                  # -> Reel30_clean_SDR.mp4 / _HDR.mp4
  "segments": "segments.txt",           # plan_cuts.py output (or a list of [a, b])
  "punches":  [[16.493, 18.40, 0.60, 0.47]],  # [src start, src end = next jump cut, eye x, eye y]
  "scale":    1.3,                      # punch-in size
  "ffmpeg_full": "D:/Claude/Video/tools/ffmpeg-full/ffmpeg-9.0.2-full_build/bin/ffmpeg.exe"
}

Why plain ffmpeg instead of ffmpeg-skill for this stage (all measured on Reel 29):
  - ffmpeg-skill's encodes drop the Dolby Vision RPU + dvcC: the picture plays as
    plain HLG and looks flatter than the original on Dolby players.
  - broll.py's overlay runs in 8-bit: 13 overlay passes flattened the HDR (v3).
  - libx265 keeps Dolby Vision with `-dolbyvision 1` (needs a VBV cap); the mp4
    muxer writes dvcC with `-strict unofficial`; a concat-demuxer stream copy
    keeps both. So every piece is encoded ONCE from the original and joined
    without a second encode.
  - The SDR file is made with libplacebo `apply_dolbyvision` (full ffmpeg build,
    Vulkan GPU): it applies the clip's own Dolby Vision mapping, the way an
    iPhone shows HDR on a non-HDR screen. ffmpeg-skill's color.py --to-sdr uses a
    generic tone map that came out dim and grey.
  - Audio is rebuilt separately from the original (same segments, 20 ms fades,
    two-pass loudnorm). AAC overshoots ~0.7 dB, so the ceiling is -2 dBTP to land
    at <= -1.0.
"""
import json
import os
import re
import subprocess
import sys

cfg_path = sys.argv[1]
DRY = "--dry-run" in sys.argv
base = os.path.dirname(os.path.abspath(cfg_path))
C = json.load(open(cfg_path, encoding="utf-8"))
rel = lambda p: p if os.path.isabs(p) else os.path.join(base, p)

SRC = C["source"]
SCALE = C.get("scale", 1.3)
FF_FULL = C.get("ffmpeg_full")
WORK = os.path.join(base, "build")
HDR_OUT = os.path.join(C["out_dir"], f"{C['name']}_clean_HDR.mp4")
SDR_OUT = os.path.join(C["out_dir"], f"{C['name']}_clean_SDR.mp4")


def probe():
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,r_frame_rate,color_transfer", "-of", "json", SRC],
                       capture_output=True, text=True, check=True)
    s = json.loads(r.stdout)["streams"][0]
    n, d = map(int, s["r_frame_rate"].split("/"))
    return s["width"], s["height"], round(n / d), s.get("color_transfer", "")


W, H, FPS, TRC = probe()
HDR = TRC in ("arib-std-b67", "smpte2084")
X265 = (f"colorprim=bt2020:transfer={TRC}:colormatrix=bt2020nc:"
        "vbv-maxrate=40000:vbv-bufsize=80000:log-level=error")
TAGS = ["-colorspace", "bt2020nc", "-color_primaries", "bt2020", "-color_trc", TRC]

if isinstance(C["segments"], str):
    SEGMENTS = [tuple(map(float, s.split("-"))) for s in open(rel(C["segments"])).read().strip().split(",")]
else:
    SEGMENTS = [tuple(s) for s in C["segments"]]
PUNCHES = [tuple(p) for p in C.get("punches", [])]

even = lambda v: int(round(v)) // 2 * 2
BW = even(W / SCALE)
BH = even(BW * H / W)
fr = lambda t: int(round(t * FPS))

for p in PUNCHES:
    if not any(fr(a) <= fr(p[0]) and fr(p[1]) <= fr(b) for a, b in SEGMENTS):
        raise SystemExit(f"punch {p[0]}-{p[1]} is not inside one segment; end it at the next jump cut")


def ff(*args, capture=False, exe="ffmpeg"):
    level = "info" if capture else "error"  # loudnorm prints its measurement at info level
    r = subprocess.run([exe, "-hide_banner", "-loglevel", level, "-nostdin", "-y", *args],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:])
        raise SystemExit("ffmpeg failed")
    return r.stderr


# 1. Pieces: every segment, split at punch boundaries, in source frames.
pieces = []
for a, b in SEGMENTS:
    fa, fb = fr(a), fr(b)
    cuts = sorted({fa, fb, *[fr(p[0]) for p in PUNCHES if fa < fr(p[0]) < fb],
                   *[fr(p[1]) for p in PUNCHES if fa < fr(p[1]) < fb]})
    for s, e in zip(cuts, cuts[1:]):
        punch = next((p for p in PUNCHES if fr(p[0]) <= s and e <= fr(p[1])), None)
        pieces.append((s, e, punch))

total = sum(e - s for s, e, _ in pieces) / FPS
print(f"{W}x{H} {FPS} fps {'HDR ' + TRC if HDR else 'SDR'} | {len(SEGMENTS)} segments, "
      f"{len(pieces)} pieces, {len(PUNCHES)} punch-ins, {total:.2f} s")
if DRY:
    for i, (s, e, p) in enumerate(pieces):
        print(f"  {i:02d} {s / FPS:8.3f}-{e / FPS:8.3f}{'  punch' if p else ''}")
    sys.exit()

os.makedirs(WORK, exist_ok=True)
listing = []
for i, (s, e, punch) in enumerate(pieces):
    path = os.path.join(WORK, f"p{i:02d}.mp4")
    vf = []
    if punch:
        ex, ey = punch[2], punch[3]
        x = even(min(max(ex * W * (1 - 1 / SCALE), 0), W - BW))   # eyes keep their x on screen
        y = even(min(max(ey * H - BH / 3, 0), H - BH))            # eyes onto the upper-third line
        vf = ["-vf", f"crop={BW}:{BH}:{x}:{y},scale={W}:{H}:flags=lanczos"]
    if not os.path.exists(path):
        enc = (["-c:v", "libx265", "-dolbyvision", "1", "-preset", "medium", "-crf", "16",
                "-pix_fmt", "yuv420p10le", "-tag:v", "hvc1", "-x265-params", X265, *TAGS]
               if HDR else
               ["-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p"])
        ff("-ss", f"{s / FPS:.6f}", "-i", SRC, "-frames:v", str(e - s), "-map", "0:v:0", *vf,
           *enc, "-strict", "unofficial", path)
    print(f"piece {i:02d}/{len(pieces)}{' punch' if punch else ''}", flush=True)
    listing.append(f"file '{os.path.basename(path)}'")

open(os.path.join(WORK, "list.txt"), "w").write("\n".join(listing) + "\n")
video = os.path.join(WORK, "video.mp4")
ff("-f", "concat", "-safe", "0", "-i", os.path.join(WORK, "list.txt"), "-map", "0:v:0",
   "-c", "copy", "-strict", "unofficial", video)

# 2. Audio from the original: same segments, 20 ms fade at every join, loudness.
parts, labels = [], []
for i, (a, b) in enumerate(SEGMENTS):
    sa, sb = fr(a) / FPS, fr(b) / FPS
    parts.append(f"[0:a:0]atrim={sa:.6f}:{sb:.6f},asetpts=PTS-STARTPTS,"
                 f"afade=t=in:d=0.02,afade=t=out:st={sb - sa - 0.02:.6f}:d=0.02[a{i}]")
    labels.append(f"[a{i}]")
raw = os.path.join(WORK, "audio_raw.wav")
ff("-i", SRC, "-filter_complex", ";".join(parts) + ";" + "".join(labels) +
   f"concat=n={len(SEGMENTS)}:v=0:a=1[cat]", "-map", "[cat]", "-c:a", "pcm_s16le", raw)
log = ff("-i", raw, "-af", "loudnorm=I=-14:TP=-2:LRA=11:print_format=json", "-f", "null", "-",
         capture=True)
m = json.loads(re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", log, re.S)[-1])
ln = (f"loudnorm=I=-14:TP=-2:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
      f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
audio = os.path.join(WORK, "audio.m4a")
ff("-i", raw, "-af", ln, "-ar", "48000", "-c:a", "aac", "-b:a", "256k", audio)

# 3. The HDR / Dolby Vision file: picture and sound both stream-copied.
ff("-i", video, "-i", audio, "-map", "0:v:0", "-map", "1:a:0", "-c", "copy",
   "-strict", "unofficial", "-movflags", "+faststart", "-shortest", HDR_OUT)
print("hdr", HDR_OUT, flush=True)

# 4. The SDR file (the one that gets posted): the clip's own Dolby Vision mapping.
if HDR:
    if not FF_FULL or not os.path.exists(FF_FULL):
        raise SystemExit("ffmpeg_full (with libplacebo) missing: SDR not made; see reference/pipeline.md")
    ff("-init_hw_device", "vulkan", "-i", HDR_OUT, "-map", "0:v:0", "-map", "0:a:0", "-vf",
       "libplacebo=apply_dolbyvision=1:colorspace=bt709:color_primaries=bt709:color_trc=bt709:"
       "range=tv:format=yuv420p",
       "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high", "-pix_fmt", "yuv420p",
       "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
       "-c:a", "copy", "-movflags", "+faststart", SDR_OUT, exe=FF_FULL)
    print("sdr", SDR_OUT, flush=True)
print("done")
