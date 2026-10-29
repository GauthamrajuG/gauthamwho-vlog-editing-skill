"""Composite the walk-in scare, every frame of the window (plate_wide 23..124, v6 36.15 s on).

Same look-development as the approved style frame and storyboard v3 (compose_board.py):
figure graded to the plate (black level, defocus, plate noise, motion blur along its
travel), ragged only on its outline; red eye light with inverse-square falloff - a rim
on his edges facing the eyes, a back-light rim when the eyes are behind him, a local
spill on the wall; his guided-filter matte on top; lens bloom from the visible eyes.
Inputs: plate_wide.mkv, anim/masks/<idx>.png, anim/cg/element-<L>.png, anim/track.json.
Output: anim/ghost_window.mp4 (H.264 BT.709 CRF 12, 60 fps, 102 frames).
"""
import json
import subprocess

import cv2
import numpy as np

A = 23
H, W = 1920, 1080
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
RED = np.array([0.05, 0.10, 1.0], np.float32)
track = json.load(open("anim/track.json"))
N = len(track)


def lin(x):
    return np.power(np.clip(x, 0, 1), 2.2)


def srgb(x):
    return np.power(np.clip(x, 0, 1), 1 / 2.2)


def fbm(scale, seed):
    r = np.random.default_rng(seed)
    out, amp, tot = np.zeros((H, W), np.float32), 1.0, 0.0
    for o in range(3):
        n = cv2.GaussianBlur(r.random((H, W)).astype(np.float32), (0, 0), scale / 2 ** o)
        out += amp * (n - n.mean()) / (n.std() + 1e-6)
        tot += amp
        amp *= 0.55
    return out / tot


EDGE_NOISE = [fbm(5, 11 + k) for k in range(4)]  # cycled slowly so the outline crawls a little


def guided(I, p, r, eps):
    box = lambda x: cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
    mI, mp = box(I), box(p)
    a_ = (box(I * p) - mI * mp) / (box(I * I) - mI * mI + eps)
    return box(a_) * I + box(mp - a_ * mI)


def motion_blur(img, v):
    n = int(max(abs(v[0]), abs(v[1])) * 1.2)
    if n < 2:
        return img
    acc = np.zeros_like(img)
    for k in range(n):
        f = k / (n - 1) - 0.5
        acc += cv2.warpAffine(img, np.float32([[1, 0, -v[0] * 1.2 * f], [0, 1, -v[1] * 1.2 * f]]), (W, H))
    return acc / n


cap = cv2.VideoCapture("plate_wide.mkv")
cap.set(cv2.CAP_PROP_POS_FRAMES, A)
ff = subprocess.Popen(
    ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "60", "-i", "-",
     "-c:v", "libx264", "-preset", "medium", "-crf", "12", "-threads", "2", "-pix_fmt", "yuv420p",
     "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
     "anim/ghost_window.mp4"], stdin=subprocess.PIPE)
rng = np.random.default_rng(7)
for L in range(N):
    _, plate8 = cap.read()
    p = track[L]
    k = p["eyes"]
    if not p["visible"] and k == 0:
        ff.stdin.write(plate8.tobytes())
        continue
    plate = lin(plate8.astype(np.float32) / 255)
    m = cv2.imread(f"anim/masks/{A + L:05d}.png", 0).astype(np.float32) / 255
    gray = cv2.cvtColor(plate8, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    him = np.clip(guided(gray, cv2.GaussianBlur(m, (0, 0), 1.0), 10, 2e-3), 0, 1)
    him = np.where(cv2.erode(m, np.ones((25, 25), np.uint8)) > 0.5, 1.0, him)
    him = np.where(cv2.dilate(m, np.ones((25, 25), np.uint8)) < 0.5, 0.0, him)[..., None]

    cg = cv2.imread(f"anim/cg/element-{L:03d}.png", cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    a = cg[..., 3]
    eye = np.clip((cg[..., 2] - 0.6) * 4, 0, 1) * (cg[..., 2] > cg[..., 1] + 0.15) * a
    cloth = lin(cg[..., :3]) * (1 - eye[..., None])
    soft = cv2.GaussianBlur(a, (0, 0), 4)
    rim = np.clip(1 - np.abs(soft - 0.5) * 2, 0, 1)
    a = np.clip(a * (1 + rim * 0.6 * EDGE_NOISE[(L // 6) % 4]), 0, 1)
    cloth = cloth + np.percentile(plate.mean(axis=2), 0.5) * 0.9
    pm = cv2.GaussianBlur(cloth * a[..., None], (0, 0), 2.2)
    a = cv2.GaussianBlur(a, (0, 0), 2.2)
    eye = cv2.GaussianBlur(eye, (0, 0), 1.0)
    v = (p["vx"], p["vy"])
    pm, a, eye = motion_blur(pm, v), motion_blur(a, v), motion_blur(eye, (v[0] * 0.5, v[1] * 0.5))

    hp = plate8.astype(np.float32) - cv2.GaussianBlur(plate8.astype(np.float32), (0, 0), 2)
    sel = (plate8.mean(axis=2) < 70) & (m < 0.5)
    sigma = (hp[sel].std() if sel.sum() > 1000 else 1.3) / 255

    E = np.array([p["x"], p["y"]], np.float32)
    d2 = (XX - E[0]) ** 2 + (YY - E[1]) ** 2
    L_him = k / (1 + d2 / 240 ** 2)
    L_wall = 0.35 * k / (1 + d2 / 170 ** 2) * np.clip(1 - a * 0.9, 0, 1)
    albedo = 0.3 + 0.7 * np.sqrt(np.clip(plate.mean(axis=2, keepdims=True), 0, 1))
    bg = plate + albedo * L_wall[..., None] * RED * 0.55
    bg = bg * (1 - a[..., None]) + pm
    core = cv2.GaussianBlur(eye, (0, 0), 0.6)[..., None]
    bg = bg * (1 - core) + core * np.array([0.55, 0.75, 2.2], np.float32)

    out = bg * (1 - him)
    if k > 0:
        mb = cv2.GaussianBlur(m, (0, 0), 14)
        gx = cv2.Sobel(mb, cv2.CV_32F, 1, 0, ksize=5)
        gy = cv2.Sobel(mb, cv2.CV_32F, 0, 1, ksize=5)
        gn = np.hypot(gx, gy) + 1e-6
        lx, ly = E[0] - XX, E[1] - YY
        ln = np.hypot(lx, ly) + 1e-6
        facing = np.clip(((-gx / gn) * lx + (-gy / gn) * ly) / ln, 0, 1) ** 1.5
        ex, ey = int(np.clip(E[0], 0, W - 1)), int(np.clip(E[1], 0, H - 1))
        behind = float(m[ey, ex]) if 0 <= E[0] < W and 0 <= E[1] < H else 0.0
        facing = np.maximum(facing, 0.6 * behind)
        dist_in = cv2.distanceTransform((cv2.GaussianBlur(m, (0, 0), 6) > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
        band = cv2.GaussianBlur(np.exp(-dist_in / 16.0) * facing, (0, 0), 5)
        alb = 0.2 + 0.8 * np.sqrt(np.clip(plate.mean(axis=2, keepdims=True), 0, 1))
        lit = plate + alb * (L_him * band)[..., None] * RED * 3.0 + plate * (L_him * 0.2 * (1 - behind))[..., None] * RED
        out = out + lit * him
    else:
        out = out + plate * him
    vis = eye * (1 - him[..., 0])
    bloom = (cv2.GaussianBlur(vis, (0, 0), 5) * 1.2 + cv2.GaussianBlur(vis, (0, 0), 16) * 1.6 +
             cv2.GaussianBlur(vis, (0, 0), 48) * 2.2)
    out = out + bloom[..., None] * RED * 0.8
    res = srgb(out) + rng.normal(0, sigma, (H, W, 1)).astype(np.float32) * (a[..., None] * (1 - him))
    ff.stdin.write((np.clip(res, 0, 1) * 255).astype(np.uint8).tobytes())
    if L % 10 == 0:
        print("frame", L, flush=True)
ff.stdin.close()
ff.wait()
print("wrote anim/ghost_window.mp4")
