"""Depth test, step 3: footage -> SLOW text -> Gautham's cut-out on top.

Layers per frame (all 1080x1920):
  plate  = clip.mp4 frame
  text   = text_frames/frame_NNNNNN.png (RGBA, HyperFrames render)
  matte  = work/masks/subject/NNNNN.png, softened: 1 px erode + 1.5 px feather
           so the edge reads as a real edge, not a cut-out sticker.
Output: depth_test.mp4 (H.264 BT.709 like the SDR deliverable) with clip.mp4's audio.
"""
import glob
import os
import subprocess

import cv2
import numpy as np

CLIP = "clip.mp4"
OUT = "depth_test.mp4"
cap = cv2.VideoCapture(CLIP)
fps = cap.get(cv2.CAP_PROP_FPS)
W, H = int(cap.get(3)), int(cap.get(4))
texts = sorted(glob.glob("text_frames/*.png"))

ff = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(fps),
     "-i", "-", "-i", CLIP, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
     "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
     "-color_range", "tv", "-c:a", "copy", "-shortest", OUT],
    stdin=subprocess.PIPE)

kernel = np.ones((3, 3), np.uint8)
for f in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))):
    ok, plate = cap.read()
    if not ok:
        break
    out = plate.astype(np.float32)
    if f < len(texts):
        t = cv2.imread(texts[f], cv2.IMREAD_UNCHANGED).astype(np.float32)
        a = t[..., 3:4] / 255.0
        out = out * (1 - a) + t[..., :3] * a
    mp = f"work/masks/subject/{f:05d}.png"
    if os.path.exists(mp):
        m = cv2.imread(mp, cv2.IMREAD_GRAYSCALE)
        m = cv2.erode(m, kernel, iterations=1)
        m = cv2.GaussianBlur(m.astype(np.float32) / 255.0, (0, 0), 1.5)[..., None]
        out = out * (1 - m) + plate.astype(np.float32) * m
    ff.stdin.write(np.clip(out, 0, 255).astype(np.uint8).tobytes())
ff.stdin.close()
ff.wait()
print("wrote", OUT)
