"""Storyboard for the air-fryer / slow-world motion-graphics beat (Reel 29 v5).

Rough placement sketches on the real SDR v5 frames — NOT the final art. Shows
where each element sits, when it moves, and what it does. Panels at/after the
punch-in (59.65) use the depth-test cut-outs so the globe is drawn behind him.
"""
import glob
import math
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 540, 960
MASKS = "D:/Claude/Video/work/depth/work/masks/subject"
FONT = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
SMALL = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 17)


def frame(t):
    p = f"sb/f_{t:.3f}s.png"
    return Image.open(p).convert("RGB").resize((W, H))


def mask(t):
    idx = round((t - 59.65) * 60)
    p = f"{MASKS}/{idx:05d}.png"
    if idx < 1 or not os.path.exists(p):
        return None
    m = cv2.resize(cv2.imread(p, 0), (W, H))
    return Image.fromarray(cv2.GaussianBlur(m, (0, 0), 1))


def fryer(d, x, y, s=1.0, tray_in=1.0, glow=False, rot=0, alpha=255):
    """Air fryer sketch: body + separate tray (tray_in 0 = out to the right, 1 = inside)."""
    bw, bh = 150 * s, 175 * s
    d.rounded_rectangle([x, y, x + bw, y + bh], 26 * s, fill=(28, 28, 32, alpha), outline=(90, 90, 100, alpha), width=3)
    d.rounded_rectangle([x + 22 * s, y + 18 * s, x + bw - 22 * s, y + 52 * s], 10 * s, fill=(10, 10, 12, alpha))
    d.text((x + 52 * s, y + 22 * s), "200", fill=(255, 140, 40, alpha) if glow else (120, 70, 30, alpha), font=FONT)
    bx = x + bw - 40 * s
    d.ellipse([bx, y + 60 * s, bx + 20 * s, y + 80 * s], fill=(255, 120, 30, alpha) if glow else (70, 70, 80, alpha))
    off = (1 - tray_in) * 120 * s
    d.rounded_rectangle([x + 14 * s + off, y + 95 * s, x + bw - 14 * s + off, y + bh - 14 * s], 14 * s,
                        fill=(45, 45, 52, alpha), outline=(120, 120, 130, alpha), width=2)
    d.rounded_rectangle([x + bw / 2 - 18 * s + off, y + bh - 20 * s, x + bw / 2 + 18 * s + off, y + bh + 6 * s],
                        6 * s, fill=(20, 20, 24, alpha))
    if glow:
        for r in (30, 46):
            d.ellipse([bx - r + 10 * s, y + 70 * s - r, bx + r + 10 * s, y + 70 * s + r], outline=(255, 150, 60, 140), width=2)


def hand(d, x, y, s=1.0):
    d.rounded_rectangle([x, y, x + 26 * s, y + 70 * s], 13 * s, fill=(222, 170, 130, 255))
    d.rounded_rectangle([x - 14 * s, y + 46 * s, x + 46 * s, y + 110 * s], 20 * s, fill=(222, 170, 130, 255))


def globe(d, cx, cy, r, fast=True, alpha=255):
    d.ellipse([cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10], fill=(120, 190, 255, 60))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(30, 90, 190, alpha), outline=(150, 210, 255, alpha), width=3)
    for blob in ((-0.35, -0.25, 0.35), (0.25, 0.1, 0.28), (-0.1, 0.45, 0.22)):
        bx, by, br = cx + blob[0] * r, cy + blob[1] * r, blob[2] * r
        d.ellipse([bx - br, by - br * 0.7, bx + br, by + br * 0.7], fill=(70, 170, 100, alpha))
    for k in (-0.5, 0, 0.5):
        d.ellipse([cx - r * abs(math.cos(k * 1.2)), cy - r, cx + r * abs(math.cos(k * 1.2)), cy + r], outline=(180, 220, 255, 120), width=1)
    if fast:
        for i in range(5):
            yy = cy - r * 0.6 + i * r * 0.3
            d.line([cx - r - 60, yy, cx - r - 15, yy], fill=(255, 255, 255, 200), width=3)
            d.line([cx + r + 15, yy, cx + r + 60, yy], fill=(255, 255, 255, 200), width=3)


def arrow(d, a, b, col=(255, 230, 0, 255)):
    d.line([a, b], fill=col, width=4)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    for da in (2.6, -2.6):
        d.line([b, (b[0] + 18 * math.cos(ang + da), b[1] + 18 * math.sin(ang + da))], fill=col, width=4)


def panel(t, draw_fn, title, lines):
    base = frame(t).convert("RGBA")
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    comp = Image.alpha_composite(base, layer)
    m = mask(t)
    if m is not None:  # depth: put him back on top of the graphics
        comp = Image.composite(base, comp, m)
    top = ImageDraw.Draw(comp)
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_overlay = getattr(draw_fn, "overlay", None)
    if draw_overlay:
        draw_overlay(ImageDraw.Draw(over))
        comp = Image.alpha_composite(comp, over)
    card = Image.new("RGB", (W, H + 200), (18, 18, 22))
    card.paste(comp.convert("RGB"), (0, 0))
    c = ImageDraw.Draw(card)
    c.text((14, H + 10), title, fill=(255, 210, 60), font=FONT)
    for i, ln in enumerate(lines):
        c.text((14, H + 46 + i * 24), ln, fill=(230, 230, 235), font=SMALL)
    return card


def p1(d):  # 57.85 assemble
    fryer(d, 40, 120, 0.95, tray_in=0.35)
    globe(d, 410, 210, 85, fast=True)
p1.overlay = lambda d: arrow(d, (250, 330), (190, 300))


def p2(d):  # 58.60 press
    fryer(d, 40, 120, 0.95, tray_in=1.0)
    hand(d, 150, 40, 0.9)
    globe(d, 410, 210, 85, fast=True)


def p3(d):  # 59.30 slow
    fryer(d, 40, 120, 0.95, tray_in=1.0, glow=True)
    globe(d, 410, 210, 85, fast=False)
p3.overlay = lambda d: d.text((330, 315), "spin slows", fill=(255, 230, 0), font=SMALL)


def p4(d):  # 59.90 throw + globe moves
    fryer(d, -60, 60, 0.9, glow=True, alpha=200)
    globe(d, 330, 200, 120, fast=False)
p4.overlay = lambda d: (arrow(d, (120, 250), (10, 200)), arrow(d, (450, 120), (360, 170)))


def p5(d):  # 60.90 centre, big, slow
    globe(d, 270, 250, 230, fast=False)


def p6(d):  # 62.60 hold
    globe(d, 270, 250, 235, fast=False)


def p7(d):  # 63.55 stretch exit
    cx, cy = 420, 120
    d.ellipse([cx - 90, cy - 300, cx + 90, cy + 60], fill=(30, 90, 190, 230), outline=(150, 210, 255, 255), width=3)
    for i in range(6):
        d.line([cx - 60 + i * 24, cy + 70, cx - 120 + i * 24, cy + 260], fill=(255, 255, 255, 120), width=3)
p7.overlay = lambda d: arrow(d, (330, 300), (480, 40))


def p0(d):  # 57.20 fridge shot - nothing yet
    pass


panels = [
    (57.20, p0, "57.20  fridge shot", ["\"mix it well\" — nothing on screen yet.", "Graphics enter on the cut to you (57.49)."]),
    (57.85, p1, "57.5-58.2  assemble", ["\"if we switch on the air fryer\"", "Fryer body drops in top-left; tray slides in.", "Globe pops in top-right, spinning FAST."]),
    (58.60, p2, "58.6  the press", ["Small hand pops down, presses the button.", "Button + display glow orange. Soft click."]),
    (59.30, p3, "58.7-59.6  the world slows", ["Globe decelerates: fast -> very slow.", "Low 'time-slow' whoosh."]),
    (59.90, p4, "59.65-60.4  'the time will be slow'", ["On the punch-in: fryer is thrown off left.", "Globe glides to centre, grows, goes BEHIND you."]),
    (60.90, p5, "60.4-63.3  slow world", ["Big globe behind your head, turning slowly.", "Your hand passes in front of it (cut-out)."]),
    (62.60, p6, "62.6  hold", ["\"for justice\" — still slowly turning,", "a soft glow pulse, nothing busy."]),
    (63.55, p7, "63.3-63.7  exit", ["Globe whips off top-right with a stretch,", "gone before the cut to the timer shot (63.71)."]),
]
cards = [panel(t, fn, title, lines) for t, fn, title, lines in panels]
row1 = np.hstack([np.array(c) for c in cards[:4]])
row2 = np.hstack([np.array(c) for c in cards[4:]])
sheet = Image.fromarray(np.vstack([row1, row2]))
sheet.save("storyboard.png")
print("storyboard.png", sheet.size)
