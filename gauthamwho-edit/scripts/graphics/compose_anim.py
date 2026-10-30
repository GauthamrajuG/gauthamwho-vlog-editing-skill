"""Composite the air-fryer / slow-world beat (373 frames) and its sound.

Per frame i:
  plate      plate.mkv frame i (uncropped SDR, same DV mapping as v5)
  cg         cg/element-<i>.png — the 3D layer in frame-66 coordinates
  tracked    cg warped by track.npy[i] so it stays locked to the wall
  graded     fixed grade measured once on frame 66 (blacks, warmth, saturation),
             0.6 px softness, fresh grain each frame
  shadow     the tracked alpha, blurred, offset away from the front-left light
  depth      his cut-out (masks/i) laid back on top
  punch-in   from frame 130: crop (100, 444, 830, 1476) -> 1080x1920, like v5
Sound: v5's own audio for 57.500-63.717 s + sfx.wav, mixed under the voice.
Output: mg_clip.mp4 (H.264 BT.709 CRF 16, 60 fps).
"""
import glob
import subprocess
import sys

import cv2
import numpy as np

sys.path.insert(0, "..")
from compose_still import grade_cg  # noqa: E402

V5_SDR = "D:/Claude/Video/Reel 29/Reel29_clean_SDR_v5.mp4"
START, END = 3450 / 60, 3823 / 60
PUNCH, CROP = 130, (100, 444, 830, 1476)
W, H = 1080, 1920

cg_files = sorted(glob.glob("cg/*.png"))
track = np.load("track.npy")
cap = cv2.VideoCapture("plate.mkv")
N = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
assert len(cg_files) == N == len(track), (len(cg_files), N, len(track))

# --- one fixed grade, measured on the style-frame moment (frame 66) ---------
cap.set(cv2.CAP_PROP_POS_FRAMES, 66)
_, ref_plate = cap.read()
ref_cg = cv2.imread(cg_files[66], cv2.IMREAD_UNCHANGED).astype(np.float32)
ref_a = ref_cg[..., 3] / 255.0
lum_plate = cv2.cvtColor(ref_plate, cv2.COLOR_BGR2GRAY)
BLACK_PLATE = float(np.percentile(lum_plate, 1))
straight = ref_cg[..., :3] / np.maximum(ref_a[..., None], 1e-3)
lum_cg = cv2.cvtColor(np.clip(straight, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
BLACK_CG = float(np.percentile(lum_cg[ref_a > 0.9], 1))
LIFT = BLACK_CG - BLACK_PLATE
print(f"grade: CG black {BLACK_CG:.0f} -> plate black {BLACK_PLATE:.0f}")
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)


def grade(rgb):
    out = (rgb - LIFT) * (255.0 / max(1.0, 255.0 - LIFT))
    out[..., 2] *= 1.018
    out[..., 0] *= 0.982
    grey = out.mean(axis=2, keepdims=True)
    return np.clip(grey + (out - grey) * 0.93, 0, 255)


def matte(i):
    m = cv2.imread(f"masks/{i:05d}.png", 0)
    m = cv2.erode(m, np.ones((3, 3), np.uint8))
    return cv2.GaussianBlur(m.astype(np.float32) / 255.0, (0, 0), 1.5)[..., None]


rng = np.random.default_rng(0)
ff = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "60", "-i", "-",
     "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-colorspace", "bt709",
     "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", "mg_video.mp4"],
    stdin=subprocess.PIPE)

for i in range(N):
    ok, plate = cap.read()
    plate = plate.astype(np.float32)
    cg = cv2.imread(cg_files[i], cv2.IMREAD_UNCHANGED).astype(np.float32)
    cg = cv2.warpAffine(cg, track[i], (W, H), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
    a = cg[..., 3] / 255.0
    rgb = grade(np.where(a[..., None] > 0.002, cg[..., :3] / np.maximum(a[..., None], 1e-3), 0))
    rgb = cv2.GaussianBlur(rgb, (0, 0), 0.6) + rng.normal(0, 1.4, (H, W, 1)).astype(np.float32) * (a[..., None] > 0)
    a = cv2.GaussianBlur(a, (0, 0), 0.6)
    sh = cv2.warpAffine(cv2.GaussianBlur(a, (0, 0), 22), np.float32([[1, 0, 22], [0, 1, 30]]), (W, H))
    out = plate * (1 - 0.30 * sh[..., None])
    out = out * (1 - a[..., None]) + rgb * a[..., None]
    m = matte(i)
    out = out * (1 - m) + plate * m
    if i >= PUNCH:
        x, y, w, h = CROP
        out = cv2.resize(out[y:y + h, x:x + w], (W, H), interpolation=cv2.INTER_LANCZOS4)
    ff.stdin.write(np.clip(out, 0, 255).astype(np.uint8).tobytes())
    if i % 60 == 0:
        print("frame", i, flush=True)
ff.stdin.close()
ff.wait()

# --- sound: his voice from v5 for this window + the effects, under the voice ---
subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-ss", f"{START:.6f}", "-t", f"{END - START:.6f}", "-i", V5_SDR, "-i", "sfx.wav",
     "-filter_complex", "[0:a]aresample=48000[v];[1:a]volume=-3dB[s];[v][s]amix=inputs=2:normalize=0:duration=first[a]",
     "-map", "[a]", "-c:a", "pcm_s16le", "mg_audio.wav"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "mg_video.mp4", "-i", "mg_audio.wav", "-map", "0:v", "-map", "1:a",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "mg_clip.mp4"], check=True)
print("wrote mg_clip.mp4")
