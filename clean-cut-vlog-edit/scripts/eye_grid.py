"""Gridded frames for measuring where the eyes are in each punch-in window.

Usage (job venv, it needs opencv):
    .venv/Scripts/python eye_grid.py SOURCE.mp4 OUT.png T1 T2 T3 ...

Takes one frame per time (source seconds) with ffmpeg-skill look.py and draws a
10 % grid on each (lines numbered 1-9 across and down). Read the midpoint between
the eyes as fractions of the frame (x, y) — take two times per window, at its
start and middle, and use the average. Face detection is NOT used for this: on
Reel 29 it mixed two positions in one shot, missed faces in night shots, and its
box centre sits below the eye line.
"""
import glob
import os
import subprocess
import sys

import cv2
import numpy as np

src, out, times = sys.argv[1], sys.argv[2], sys.argv[3:]
S = os.path.expanduser("~/.claude/skills/ffmpeg-skill/scripts")
tmp = os.path.splitext(out)[0] + "_frames"
os.makedirs(tmp, exist_ok=True)
args = [a for t in times for a in ("--at", t)]
subprocess.run(["py", f"{S}/look.py", src, *args, "-o", os.path.join(tmp, "f.png"), "--json-brief"],
               capture_output=True, check=True)

tiles = []
for f in sorted(glob.glob(os.path.join(tmp, "f_*.png")), key=lambda p: float(p.rsplit("_", 1)[-1][:-5])):
    im = cv2.resize(cv2.imread(f), (270, 480))
    for i in range(1, 10):
        x, y = 27 * i, 48 * i
        cv2.line(im, (x, 0), (x, 480), (0, 255, 255), 1)
        cv2.line(im, (0, y), (270, y), (0, 255, 255), 1)
        cv2.putText(im, str(i), (x + 1, 10), 0, 0.3, (0, 255, 0), 1)
        cv2.putText(im, str(i), (1, y - 2), 0, 0.3, (0, 255, 0), 1)
    cv2.putText(im, f.rsplit("_", 1)[-1][:-5], (30, 470), 0, 0.55, (0, 0, 255), 2)
    tiles.append(im)
tiles += [np.zeros_like(tiles[0])] * (-len(tiles) % 6)
cv2.imwrite(out, np.vstack([np.hstack(tiles[i:i + 6]) for i in range(0, len(tiles), 6)]))
print("wrote", out, f"({len(times)} frames)")
