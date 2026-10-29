"""The ghost's motion for the walk-in shot, one pose per frame, locked to Gautham.

Local frame L = plate_wide index - 23 (L0 = v6 36.15 s, the first frame of the shot).
Anchors come from his cut-out every frame (anim/masks), lightly smoothed, so the ghost
moves with him and the handheld camera:
  shoulder  top of his LEFT shoulder (screen right), at x = 965
  head      centroid of the top third of his silhouette
Beats (storyboard v3):
  L8-L30   rises from behind his left shoulder to just above it (damped spring, overshoot)
  L30-L62  settles and breathes; eyes ignite at L48 (flicker), it leans towards his neck
  L62-L70  anticipation: pulls back and sinks
  L70-L94  swoops down behind his neck and out over his right shoulder (screen left) on a
           Catmull-Rom curve, accelerating; banks into the turn
Secondary motion: the body's hem follows the head with lag (drag), the cloth ripples
faster the faster it moves. Writes src/ghost/track.json (Remotion reads it) and
anim/track.json (the compositor reads it).
"""
import json

import cv2
import numpy as np

A, B = 23, 124
N = B - A + 1
PX = 358.3  # pixels per scene unit at z = 0 (fov 30, camera z 10, 1920 px tall)


def smooth(x, k=5):
    pad = np.pad(x, ((k // 2, k // 2), (0, 0)), mode="edge")
    return np.array([pad[i:i + k].mean(axis=0) for i in range(len(x))])


shoulder, head = [], []
for i in range(A, B + 1):
    m = cv2.imread(f"anim/masks/{i:05d}.png", 0) > 127
    tops = [np.argmax(m[:, x]) if m[:, x].any() else 1920 for x in range(905, 1026, 15)]
    shoulder.append([965, float(np.median(tops))])
    yx = np.argwhere(m)
    y0, y1 = yx[:, 0].min(), yx[:, 0].max()
    top = yx[yx[:, 0] < y0 + 0.33 * (y1 - y0)]
    head.append([top[:, 1].mean(), top[:, 0].mean()])
shoulder, head = smooth(np.array(shoulder)), smooth(np.array(head))


def spring01(t, zeta=0.45, w=9.0):
    """Damped spring step response, 0 -> 1 with overshoot; t in seconds from the start."""
    if t <= 0:
        return 0.0
    wd = w * np.sqrt(1 - zeta ** 2)
    return float(1 - np.exp(-zeta * w * t) * (np.cos(wd * t) + zeta * w / wd * np.sin(wd * t)))


def ease(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def catmull(pts, u):
    """Point on a Catmull-Rom spline through pts at u in [0, 1]."""
    pts = np.asarray(pts, float)
    n = len(pts) - 1
    s = min(u * n, n - 1e-6)
    j = int(s)
    t = s - j
    p0, p1, p2, p3 = pts[max(j - 1, 0)], pts[j], pts[j + 1], pts[min(j + 2, n)]
    return 0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2 +
                  (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)


pos, rotz, roty, eyes = [], [], [], []
rng = np.random.default_rng(13)
for L in range(N):
    sh, hd = shoulder[L], head[L]
    # ---- peek (relative to his left shoulder) ----
    r = spring01((L - 8) / 60)
    dx = -15 * r
    dy = 170 + (-95 - 170) * r
    if L >= 30:
        dy += 6 * np.sin(2 * np.pi * (L - 30) / 28)  # breathing
    dx -= 25 * ease((L - 48) / 12)                   # leans in towards his neck
    tilt = 0.2 * ease((L - 48) / 12)
    # anticipation
    ant = ease((L - 62) / 8)
    dx += 40 * ant
    dy += 45 * ant
    tilt += -0.28 * ant
    p = sh + [dx, dy]
    ry = -0.35
    # ---- swoop (curve behind his neck, out over his right shoulder) ----
    if L >= 70:
        u = np.clip((L - 70) / 24, 0, 1) ** 1.6  # accelerating
        start = sh + [-15 - 25 + 40, -95 + 45]
        ctrl = [start, sh + [-60, 105], hd + [60, 430], hd + [-300, 270], [70, hd[1] + 10], [-320, hd[1] - 320]]
        p = catmull(ctrl, u)
        ry = -0.35 + 0.5 * ease((L - 70) / 14)
    pos.append(p)
    roty.append(ry)
    rotz.append(tilt)
    # eyes: off, a flicker at L46-49, on by L54, a touch hotter during the anticipation
    if L < 46:
        e = 0.0
    elif L < 50:
        e = [0.35, 0.0, 0.85, 0.4][L - 46]
    else:
        e = 0.4 + 0.6 * ease((L - 50) / 4) + 0.2 * ant
    if L > 94:
        e = 0.0
    eyes.append(e * (1 + 0.04 * rng.standard_normal()))  # a living flicker

pos = np.array(pos)
vel = np.gradient(pos, axis=0)
# bank into the turn while it moves fast; a lagged follower makes it settle, not snap
bank = np.zeros(N)
for L in range(1, N):
    target = rotz[L] + np.clip(-vel[L, 0] * 0.005, -0.3, 0.3)
    bank[L] = bank[L - 1] + (target - bank[L - 1]) * 0.35
# the hem follows the head with lag (secondary motion), in scene units, y up
tail = pos[0].copy()
tv = np.zeros(2)
drag = []
for L in range(N):
    # damped spring follower: the hem is pulled towards the head, overshoots a little
    acc = (pos[L] - tail) * 0.09 - tv * 0.38
    tv = tv + acc
    tail = tail + tv
    d = (tail - pos[L]) / PX
    drag.append([float(np.clip(d[0], -1.3, 1.3)), float(np.clip(-d[1], -0.9, 0.9) - 0.0)])
speed = np.hypot(vel[:, 0], vel[:, 1])
phase = np.cumsum(0.12 + speed * 0.012)

track = []
for L in range(N):
    track.append({
        "x": round(float(pos[L, 0]), 2), "y": round(float(pos[L, 1]), 2), "s": 0.95,
        "rot": [0.05, round(float(roty[L]), 4), round(float(bank[L]), 4)],
        "eyes": round(float(max(0.0, eyes[L])), 3), "drag": [round(drag[L][0], 4), round(drag[L][1], 4)],
        "phase": round(float(phase[L]), 3), "vx": round(float(vel[L, 0]), 2), "vy": round(float(vel[L, 1]), 2),
        "visible": bool(L >= 8 and L <= 95),
    })
json.dump(track, open("anim/track.json", "w"))
json.dump(track, open("../../src/ghost/track.json", "w"))
for L in (8, 20, 30, 48, 62, 70, 80, 88, 94):
    print(L, track[L]["x"], track[L]["y"], "eyes", track[L]["eyes"], "drag", track[L]["drag"], "bank", track[L]["rot"][2])
