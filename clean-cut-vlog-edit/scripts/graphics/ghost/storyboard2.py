"""Storyboard v2 for the red-eyed ghost beat (Reel 29 v6, dark walk-in shot 36.25-38.45 s).

Changes from v1 (creator's notes): the ghost rises on the SCREEN-RIGHT side (his left
shoulder) and exits behind his head to SCREEN LEFT; it is a dark hooded, dark-robed horror
figure with glowing red eyes; the eyes' red light falls on him (rim light on the side
facing it) and on the walls and staircase around (inverse-square falloff, times the
surface's own brightness).
Still a rough sketch for placement and timing, not the final hyper-real render.
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 540, 960
FONT = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
SMALL = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 17)
RED = np.array([30, 25, 255], np.float32) / 255.0  # BGR light colour
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
rng = np.random.default_rng(7)
SMOKE = cv2.GaussianBlur(rng.random((H, W)).astype(np.float32), (0, 0), 9)
SMOKE = (SMOKE - SMOKE.min()) / (SMOKE.max() - SMOKE.min())


def hooded(cx, cy, s=1.0, tilt=0.0):
    """Alpha of a hooded robed figure whose eye line is at (cx, cy), plus its face-void alpha."""
    a = np.zeros((H, W), np.float32)
    hood = np.array([[0, -95], [38, -78], [62, -35], [66, 20], [58, 70], [120, 120], [175, 260], [190, 520],
                     [-190, 520], [-175, 260], [-120, 120], [-58, 70], [-66, 20], [-62, -35], [-38, -78]], np.float32)
    face = np.array([[0, -48], [30, -30], [38, 10], [26, 52], [0, 66], [-26, 52], [-38, 10], [-30, -30]], np.float32)
    r = np.deg2rad(tilt)
    rot = np.array([[np.cos(r), -np.sin(r)], [np.sin(r), np.cos(r)]], np.float32)
    for poly, val, tgt in ((hood, 1.0, "a"), (face, 1.0, "f")):
        p = (poly * s) @ rot.T + [cx, cy]
        if tgt == "a":
            cv2.fillPoly(a, [p.astype(np.int32)], val)
        else:
            f = np.zeros((H, W), np.float32)
            cv2.fillPoly(f, [p.astype(np.int32)], val)
    a = cv2.GaussianBlur(a, (0, 0), 5 * s)
    # robe dissolves into smoke towards the bottom
    fade = np.clip(1 - (YY - (cy + 160 * s)) / (260 * s), 0, 1)
    a *= fade * (0.75 + 0.35 * SMOKE)
    return np.clip(a, 0, 1), cv2.GaussianBlur(f, (0, 0), 4 * s)


def eyes_glow(cx, cy, s, tilt, k):
    g = np.zeros((H, W), np.float32)
    r = np.deg2rad(tilt)
    for dx in (-17, 17):
        ex = cx + (dx * np.cos(r)) * s
        ey = cy + (dx * np.sin(r)) * s
        cv2.ellipse(g, (int(ex), int(ey)), (int(8 * s), int(4 * s)), tilt - 14 * np.sign(dx), 0, 360, 1.0, -1)
    core = cv2.GaussianBlur(g, (0, 0), 1.2) * k
    halo = cv2.GaussianBlur(g, (0, 0), 10 * s) * 3.0 * k
    return core, halo


def light(ex, ey, k, r0=150.0):
    """Red irradiance from the eyes at every pixel (inverse-square with a soft core)."""
    d2 = ((XX - ex) ** 2 + (YY - ey) ** 2) / r0 ** 2
    return k / (1 + d2)


def compose(t, ghosts, extra_light=None):
    """ghosts: list of (cx, cy, s, tilt, eyes, alpha) drawn behind him; light from every eye pair."""
    plate = cv2.imread(f"sb/f_{t}.png").astype(np.float32) / 255
    him = cv2.GaussianBlur(cv2.imread(f"sb/m_{t}.png", 0).astype(np.float32) / 255, (0, 0), 1.2)[..., None]
    L = np.zeros((H, W), np.float32)
    for cx, cy, s, tilt, k, al in ghosts:
        L += light(cx, cy, 0.8 * k * al) if al >= 0.5 else 0
    if extra_light:
        L += light(*extra_light)
    # background: wall/staircase reflect the red light by their own brightness
    bg = plate + plate * L[..., None] * RED * 1.4
    # figure(s) behind him
    for cx, cy, s, tilt, k, al in ghosts:
        a, face = hooded(cx, cy, s, tilt)
        a = a[..., None] * al
        robe = np.array([0.045, 0.035, 0.04], np.float32) + 0.05 * SMOKE[..., None]
        # the eyes light the inside of the hood
        robe = robe + (light(cx, cy, 0.9 * k, 45 * s)[..., None] * RED * 0.6) * (1 - face[..., None] * 0.7)
        robe = robe * (1 - face[..., None] * 0.85)  # the face is a black void
        bg = bg * (1 - a) + robe * a
        core, halo = eyes_glow(cx, cy, s, tilt, k * al)
        bg = bg + halo[..., None] * RED * 0.9 + core[..., None] * np.array([0.7, 0.75, 1.0], np.float32)
    # him: red rim light on the edge that faces the light, plus a faint wrap
    m = cv2.imread(f"sb/m_{t}.png", 0).astype(np.float32) / 255
    inner = cv2.GaussianBlur(cv2.erode(m, np.ones((15, 15), np.uint8)), (0, 0), 6)
    rim = np.clip(m - inner, 0, 1) * 2.2
    lit = plate + plate * (L * (rim + 0.08))[..., None] * RED * 2.0 + (L * rim * 0.10)[..., None] * RED
    out = bg * (1 - him) + lit * him
    return np.clip(out * 255, 0, 255).astype(np.uint8)


def panel(img, t, title, lines, arrow=None):
    pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    d = ImageDraw.Draw(pil, "RGBA")
    d.rectangle([0, 0, W, 34], fill=(0, 0, 0, 190))
    d.text((10, 6), f"{t} s  {title}", font=FONT, fill=(255, 220, 60))
    if arrow:
        (x0, y0), (x1, y1) = arrow
        d.line([(x0, y0), (x1, y1)], fill=(255, 220, 60, 230), width=4)
        v = np.array([x1 - x0, y1 - y0], float); v /= np.linalg.norm(v); n = np.array([-v[1], v[0]])
        tip = np.array([x1, y1]); d.polygon([tuple(tip + v * 14), tuple(tip + n * 10), tuple(tip - n * 10)], fill=(255, 220, 60, 230))
    y = H - 14 - 22 * len(lines)
    d.rectangle([0, y - 10, W, H], fill=(0, 0, 0, 190))
    for ln in lines:
        d.text((12, y), ln, font=SMALL, fill=(255, 255, 255))
        y += 22
    return pil


def whip(t):
    # motion-blurred pass behind his head, right -> left
    trail = [(x, 410 + (x - 150) * 0.05, 0.95, -4, 1.0, a) for x, a in ((330, 0.10), (270, 0.16), (210, 0.25), (150, 0.55), (95, 0.8))]
    return compose(t, trail)


panels = [
    panel(compose("36.30", [(470, 660, 1.0, 0, 0.0, 0.5)]), "36.30", "1  Calm",
          ["Dark walk-in. A hooded shadow starts", "rising behind your LEFT shoulder", "(screen right). Low rumble."], arrow=((505, 720), (505, 600))),
    panel(compose("36.60", [(470, 545, 1.0, 0, 0.25, 0.9)]), "36.60", "2  It rises",
          ["Dark hood + robe slide up behind you.", "Eyes start to glow: a faint red", "tint on the wall behind."]),
    panel(compose("36.95", [(462, 440, 1.0, -4, 1.0, 1.0)]), "36.95", "3  Eyes ignite",
          ["Red eyes flash on. Their light hits", "your hair, ear and cheek (red rim)", "and the wall + stairs. Hiss SFX."]),
    panel(compose("37.30", [(436, 428, 1.05, -14, 1.25, 1.0)]), "37.30", "4  Leans in",
          ["Tilts towards your ear, stares at", "the viewer. Stronger red on you.", "Holds ~0.3 s."]),
    panel(whip("37.55"), "37.55", "5  Whips away",
          ["Shoots BEHIND your head to screen", "LEFT and off. The red light sweeps", "across you with it. Whoosh."], arrow=((420, 330), (60, 330))),
    panel(compose("37.75", [], extra_light=(-60, 420, 0.5)), "37.75", "6  Gone",
          ["Off screen left; last red glow fades", "on the wall. Your bag swings up as", "usual. Then your black clip."]),
]
sheet = Image.new("RGB", (W * 3 + 20, H * 2 + 10), (20, 20, 20))
for i, pn in enumerate(panels):
    sheet.paste(pn, ((i % 3) * (W + 10), (i // 3) * (H + 10)))
sheet.save("storyboard_v2.png")
print("wrote storyboard_v2.png")
