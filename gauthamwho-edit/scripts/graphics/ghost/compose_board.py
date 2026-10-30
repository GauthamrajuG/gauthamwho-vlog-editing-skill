"""Storyboard v3: the six ghost poses (board/cg/element-<i>.png) composited onto the real
frames with the same look-development as the approved style frame, then laid out as a
captioned sheet with the exit path drawn in.

Per panel (linear light):
  figure   graded to the plate (black level, defocus, plate noise), full body to the frame
           bottom (no smoke cut), ragged only along its outline; motion blur along its
           travel on the swoop panels
  light    the eyes are a red light at E; inverse-square falloff. On him: rim on edges
           facing E, and when E is behind him (swoop) a back-light rim all round his
           silhouette near E. On the wall: a local spill only.
  him      SAM matte refined with a guided filter (hair strands) on top
  bloom    lens glow from the visible eyes
"""
import json

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

H, W = 1920, 1080
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
RED = np.array([0.05, 0.10, 1.0], np.float32)  # BGR, linear
TS = ["36.30", "36.60", "36.95", "37.30", "37.55", "37.75"]
# eye-line positions (px) and travel per frame (px) for each pose, from GhostBoard.tsx
POSE = [(965, 1495), (950, 1366), (938, 1372), (978, 1318), (360, 1360), (70, 1040)]
VEL = [(0, -6), (0, -2), (-1, 0), (1, -1), (-26, -6), (-22, -14)]
EYES = [0, 0.25, 1, 1.2, 1, 0.9]


def lin(x):
    return np.power(np.clip(x, 0, 1), 2.2)


def srgb(x):
    return np.power(np.clip(x, 0, 1), 1 / 2.2)


def fbm(scale, octaves=3, seed=0):
    r = np.random.default_rng(seed)
    out, amp, tot = np.zeros((H, W), np.float32), 1.0, 0.0
    for o in range(octaves):
        n = cv2.GaussianBlur(r.random((H, W)).astype(np.float32), (0, 0), scale / 2 ** o)
        out += amp * (n - n.mean()) / (n.std() + 1e-6)
        tot += amp
        amp *= 0.55
    return out / tot


def guided(I, p, r, eps):
    box = lambda x: cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
    mI, mp = box(I), box(p)
    a_ = (box(I * p) - mI * mp) / (box(I * I) - mI * mI + eps)
    return box(a_) * I + box(mp - a_ * mI)


def motion_blur(img, v):
    n = int(max(abs(v[0]), abs(v[1])) * 1.5)
    if n < 2:
        return img
    acc = np.zeros_like(img)
    for k in range(n):
        f = k / (n - 1) - 0.5
        M = np.float32([[1, 0, -v[0] * 1.5 * f], [0, 1, -v[1] * 1.5 * f]])
        acc += cv2.warpAffine(img, M, (W, H))
    return acc / n


def compose(i, t):
    plate8 = cv2.imread(f"work/ghost-mg/board/plate_{t}.png")
    plate = lin(plate8.astype(np.float32) / 255)
    m = cv2.imread(f"work/ghost-mg/board/matte_{t}.png", 0).astype(np.float32) / 255
    gray = cv2.cvtColor(plate8, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    him = np.clip(guided(gray, cv2.GaussianBlur(m, (0, 0), 1.0), 10, 2e-3), 0, 1)
    him = np.where(cv2.erode(m, np.ones((25, 25), np.uint8)) > 0.5, 1.0, him)
    him = np.where(cv2.dilate(m, np.ones((25, 25), np.uint8)) < 0.5, 0.0, him)[..., None]

    cg = cv2.imread(f"work/ghost-mg/board/cg/element-{i}.png", cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    a = cg[..., 3]
    eye = np.clip((cg[..., 2] - 0.6) * 4, 0, 1) * (cg[..., 2] > cg[..., 1] + 0.15) * a
    cloth = lin(cg[..., :3]) * (1 - eye[..., None])
    # ragged only along the outline
    soft = cv2.GaussianBlur(a, (0, 0), 4)
    rim = np.clip(1 - np.abs(soft - 0.5) * 2, 0, 1)
    a = np.clip(a * (1 + rim * 0.6 * fbm(5, seed=11 + i)), 0, 1)
    black = np.percentile(plate.mean(axis=2), 0.5)
    cloth = cloth + black * 0.9
    DEF = 2.2
    pm = cv2.GaussianBlur(cloth * a[..., None], (0, 0), DEF)  # premultiplied
    a = cv2.GaussianBlur(a, (0, 0), DEF)
    eye = cv2.GaussianBlur(eye, (0, 0), 1.0)
    pm, a, eye = motion_blur(pm, VEL[i]), motion_blur(a, VEL[i]), motion_blur(eye, VEL[i])

    hp = plate8.astype(np.float32) - cv2.GaussianBlur(plate8.astype(np.float32), (0, 0), 2)
    sigma = hp[(plate8.mean(axis=2) < 70) & (m < 0.5)].std() / 255

    E = np.array(POSE[i], np.float32)
    k = EYES[i]
    d2 = (XX - E[0]) ** 2 + (YY - E[1]) ** 2
    L = k / (1 + d2 / 240 ** 2)
    L_wall = 0.35 * k / (1 + d2 / 170 ** 2) * np.clip(1 - a * 0.9, 0, 1)
    albedo = 0.3 + 0.7 * np.sqrt(np.clip(plate.mean(axis=2, keepdims=True), 0, 1))
    bg = plate + albedo * L_wall[..., None] * RED * 0.55
    bg = bg * (1 - a[..., None]) + pm
    core = cv2.GaussianBlur(eye, (0, 0), 0.6)[..., None]
    bg = bg * (1 - core) + core * np.array([0.55, 0.75, 2.2], np.float32)

    mb = cv2.GaussianBlur(m, (0, 0), 14)
    gx = cv2.Sobel(mb, cv2.CV_32F, 1, 0, ksize=5)
    gy = cv2.Sobel(mb, cv2.CV_32F, 0, 1, ksize=5)
    gn = np.hypot(gx, gy) + 1e-6
    lx, ly = E[0] - XX, E[1] - YY
    ln = np.hypot(lx, ly) + 1e-6
    facing = np.clip(((-gx / gn) * lx + (-gy / gn) * ly) / ln, 0, 1) ** 1.5
    ex, ey = int(np.clip(E[0], 0, W - 1)), int(np.clip(E[1], 0, H - 1))
    behind = float(m[ey, ex]) if 0 <= E[0] < W else 0.0  # light source hidden behind him
    facing = np.maximum(facing, 0.6 * behind)
    dist_in = cv2.distanceTransform((cv2.GaussianBlur(m, (0, 0), 6) > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    band = cv2.GaussianBlur(np.exp(-dist_in / 16.0) * facing, (0, 0), 5)
    alb = 0.2 + 0.8 * np.sqrt(np.clip(plate.mean(axis=2, keepdims=True), 0, 1))
    lit = plate + alb * (L * band)[..., None] * RED * 2.0 + plate * (L * 0.12 * (1 - behind))[..., None] * RED
    out = bg * (1 - him) + lit * him

    vis = eye * (1 - him[..., 0])
    bloom = (cv2.GaussianBlur(vis, (0, 0), 5) * 1.2 + cv2.GaussianBlur(vis, (0, 0), 16) * 1.6 +
             cv2.GaussianBlur(vis, (0, 0), 48) * 2.2)
    out = out + bloom[..., None] * RED * 0.8
    res = srgb(out) + np.random.default_rng(i).normal(0, sigma, (H, W, 1)).astype(np.float32) * (a[..., None] * (1 - him))
    return (np.clip(res, 0, 1) * 255).astype(np.uint8)


CAPTIONS = [
    ("Rises", ["Behind your LEFT shoulder (screen right)", "it rises from below, cloth swaying. Still", "dark: blue dots = where it is. Low rumble."]),
    ("Shoulder level", ["Stops at your shoulder line and settles,", "hem still catching up. Eyes start", "to glow."]),
    ("Eyes ignite", ["Red eyes flash on. Their light lands on", "your neck, ear and jaw, and the wall", "around it. Hiss."]),
    ("Draws back", ["A breath before it moves: pulls back", "and sinks a little (anticipation).", "Yellow = its exit path, behind you."]),
    ("Swoops behind you", ["Curves down and BEHIND your neck (blue", "dots = its hidden body, trailing and", "rippling). Its light rims you. Whoosh."]),
    ("Out over your right", ["Rises out over your RIGHT shoulder", "(screen left), banking, robe streaming,", "and is gone before your bag swings up."]),
]
FONT = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
SMALL = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 17)
PATH = [(938, 1372), (978, 1318), (900, 1480), (650, 1560), (360, 1360), (70, 1040), (-160, 760)]

panels = []
for i, t in enumerate(TS):
    img = compose(i, t)
    cv2.imwrite(f"work/ghost-mg/board/panel_{i + 1}.png", img)
    pil = Image.fromarray(cv2.cvtColor(cv2.resize(img, (540, 960), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB))
    d = ImageDraw.Draw(pil, "RGBA")
    if i == 3:  # the exit path: a smooth curve through PATH
        pts = np.array(PATH, np.float32) / 2
        curve = []
        for j in range(len(pts) - 1):
            p0, p1 = pts[max(j - 1, 0)], pts[j]
            p2, p3 = pts[j + 1], pts[min(j + 2, len(pts) - 1)]
            for u in np.linspace(0, 1, 16, endpoint=False):
                curve.append(0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u ** 2 +
                                    (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3))
        curve = [tuple(c) for c in curve]
        for j in range(0, len(curve) - 1, 2):
            d.line([curve[j], curve[j + 1]], fill=(255, 220, 60, 235), width=4)
        end, prev = np.array(curve[-1]), np.array(curve[-4])
        v = (end - prev) / np.linalg.norm(end - prev)
        n = np.array([-v[1], v[0]])
        d.polygon([tuple(end + v * 14), tuple(end + n * 9), tuple(end - n * 9)], fill=(255, 220, 60, 235))
    if i in (0, 4, 5):  # dotted outline of the body where it is hidden (dark / behind him)
        ca = cv2.imread(f"work/ghost-mg/board/cg/element-{i}.png", cv2.IMREAD_UNCHANGED)[..., 3]
        cs, _ = cv2.findContours((ca > 128).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for c in cs:
            c = c[::6, 0, :] / 2
            for j in range(0, len(c) - 1, 2):
                d.line([tuple(c[j]), tuple(c[j + 1])], fill=(120, 220, 255, 220), width=3)
    title, lines = CAPTIONS[i]
    d.rectangle([0, 0, 540, 34], fill=(0, 0, 0, 190))
    d.text((10, 6), f"{t} s  {i + 1}  {title}", font=FONT, fill=(255, 220, 60))
    y = 960 - 14 - 22 * len(lines)
    d.rectangle([0, y - 10, 540, 960], fill=(0, 0, 0, 190))
    for ln_ in lines:
        d.text((12, y), ln_, font=SMALL, fill=(255, 255, 255))
        y += 22
    panels.append(pil)
    print("panel", i + 1, flush=True)

sheet = Image.new("RGB", (540 * 3 + 20, 960 * 2 + 10), (20, 20, 20))
for i, pn in enumerate(panels):
    sheet.paste(pn, ((i % 3) * 550, (i // 3) * 970))
sheet.save("work/ghost-mg/storyboard_v3.png")
print("wrote storyboard_v3.png")
