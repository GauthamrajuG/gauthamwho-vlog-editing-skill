"""Grade the transparent 3D layer to the footage and composite it behind him.

Usage: gpu-ai python compose_still.py plate.png cg_rgba.png person_rgba.png out.png

Matching (measured on the plate, see the session notes):
  - blacks: footage 1st-pct luma is ~6, raw CG ~16 -> levels so CG blacks land at the plate's
  - warmth: wall reads r-b +4 -> slight warm tint on the CG
  - softness + grain: CG is crisper and cleaner than phone footage -> 0.6 px blur + fine grain
Shadows: the CG alpha, blurred and offset away from the front-left light, multiplied onto the wall.
"""
import sys

import cv2
import numpy as np


def grade_cg(cg_rgb, alpha, plate):
    lum_plate = cv2.cvtColor(plate.astype(np.uint8), cv2.COLOR_BGR2GRAY)
    black_plate = float(np.percentile(lum_plate, 1))
    lum_cg = cv2.cvtColor(np.clip(cg_rgb, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
    black_cg = float(np.percentile(lum_cg[alpha > 0.9], 1)) if (alpha > 0.9).any() else black_plate
    # levels: CG black -> plate black, keep whites
    lift = black_cg - black_plate
    out = (cg_rgb - lift) * (255.0 / max(1.0, 255.0 - lift))
    # warm tint matching the wall (BGR)
    out[..., 2] *= 1.018
    out[..., 0] *= 0.982
    # a touch less saturation, phone-like
    grey = out.mean(axis=2, keepdims=True)
    out = grey + (out - grey) * 0.93
    return np.clip(out, 0, 255)


def soften_and_grain(rgb, alpha, seed=0):
    blur = cv2.GaussianBlur(rgb, (0, 0), 0.6)
    rng = np.random.default_rng(seed)
    grain = rng.normal(0, 1.4, rgb.shape[:2]).astype(np.float32)[..., None]
    return np.clip(blur + grain * (alpha[..., None] > 0), 0, 255), cv2.GaussianBlur(alpha, (0, 0), 0.6)


def wall_shadow(plate, alpha, dx=22, dy=30, sigma=22, strength=0.30):
    a = cv2.GaussianBlur(alpha, (0, 0), sigma)
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    a = cv2.warpAffine(a, M, (alpha.shape[1], alpha.shape[0]))
    return plate * (1 - strength * a[..., None])


def compose(plate, cg_rgba, person_rgba, seed=0):
    plate = plate.astype(np.float32)
    alpha = cg_rgba[..., 3].astype(np.float32) / 255.0
    cg = cg_rgba[..., :3].astype(np.float32)
    # premultiplied -> straight for grading
    straight = np.where(alpha[..., None] > 0.002, cg / np.maximum(alpha[..., None], 1e-3), 0)
    straight = grade_cg(straight, alpha, plate)
    straight, alpha = soften_and_grain(straight, alpha, seed)
    out = wall_shadow(plate, alpha)
    out = out * (1 - alpha[..., None]) + straight * alpha[..., None]
    if person_rgba is not None:
        pa = person_rgba[..., 3:4].astype(np.float32) / 255.0
        out = out * (1 - pa) + plate * pa
    return np.clip(out, 0, 255).astype(np.uint8)


if __name__ == "__main__":
    plate = cv2.imread(sys.argv[1])
    cg = cv2.imread(sys.argv[2], cv2.IMREAD_UNCHANGED)
    person = cv2.imread(sys.argv[3], cv2.IMREAD_UNCHANGED)
    out = compose(plate, cg, person)
    cv2.imwrite(sys.argv[4], out)
    print("wrote", sys.argv[4])
