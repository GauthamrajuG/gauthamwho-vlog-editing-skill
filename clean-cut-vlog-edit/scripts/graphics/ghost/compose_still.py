"""Style frame for the walk-in scare (v6 37.30 s): plate + hooded figure + red eye light.

Layers, all at 1080x1920, lighting done in linear light:
  plate     still_plate.png (uncropped original through its own Dolby Vision mapping)
  figure    ghost_cg.png (Remotion/three render on transparency), graded to the plate:
            black level, defocus like the wall behind him, the plate's own noise;
            the robe dissolves into smoke towards the bottom
  eyes      hot core + red bloom (lens glow) where they're not hidden by him
  light     the eyes are a red light source E. Irradiance falls off with distance
            (inverse square with a soft core). The wall and stairs reflect it in
            proportion to their brightness; on him it lands as a rim on the edges
            that face E (outward normal from his matte . direction to E), strongest
            on hair, ear and jaw, plus a faint wrap.
  him       still_matte.png (SAM 2.1), 1 px erode + 1.5 px feather, laid on top
Output: style_frame.png (+ style_frame_side.png: before/after).
"""
import cv2
import numpy as np

H, W = 1920, 1080
rng = np.random.default_rng(29)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
RED = np.array([0.05, 0.10, 1.0], np.float32)  # BGR, linear


def lin(x):
    return np.power(np.clip(x, 0, 1), 2.2)


def srgb(x):
    return np.power(np.clip(x, 0, 1), 1 / 2.2)


def fbm(scale, octaves=5, seed=0):
    r = np.random.default_rng(seed)
    out = np.zeros((H, W), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        n = cv2.GaussianBlur(r.random((H, W)).astype(np.float32), (0, 0), scale / 2 ** o)
        n = (n - n.mean()) / (n.std() + 1e-6)
        out += amp * n
        tot += amp
        amp *= 0.55
    return out / tot


plate8 = cv2.imread("work/ghost-mg/still_plate.png")
plate = lin(plate8.astype(np.float32) / 255)
m = cv2.imread("work/ghost-mg/still_matte.png", 0).astype(np.float32) / 255


def guided(I, p, r, eps):
    """He et al. guided filter: the matte's edge follows the plate's own edges (hair strands)."""
    box = lambda x: cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
    mI, mp = box(I), box(p)
    a_ = (box(I * p) - mI * mp) / (box(I * I) - mI * mI + eps)
    b_ = mp - a_ * mI
    return box(a_) * I + box(b_)


gray = cv2.cvtColor(plate8, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
him = np.clip(guided(gray, cv2.GaussianBlur(m, (0, 0), 1.0), 10, 2e-3), 0, 1)
him = np.where(cv2.erode(m, np.ones((25, 25), np.uint8)) > 0.5, 1.0, him)  # solid inside
him = np.where(cv2.dilate(m, np.ones((25, 25), np.uint8)) < 0.5, 0.0, him)[..., None]  # nothing far out

# ---- the figure, graded to the plate ----------------------------------------
cg = cv2.imread("work/ghost-mg/ghost_cg.png", cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
a = cg[..., 3]
rgb = lin(cg[..., :3])
# eyes = the hot red pixels of the render; everything else is cloth
eye = np.clip((cg[..., 2] - 0.6) * 4, 0, 1) * (cg[..., 2] > cg[..., 1] + 0.15) * a
ys, xs = np.nonzero(eye > 0.5)
E = np.array([xs.mean(), ys.mean()], np.float32)
print("eyes at", E.round())
cloth = rgb * (1 - eye[..., None])

# smoke: from the chest down the robe thins out into turbulent smoke (no hard line:
# a smooth blend from solid cloth to smoke over ~350 px)
warp = fbm(60, seed=3) * 45
top = E[1] + 200
t = np.clip((YY + warp - top) / 350, 0, 1)
t = t * t * (3 - 2 * t)
# billowy, low-frequency smoke stretched upwards (rising), not speckle
smoke = cv2.resize(fbm(34, 2, seed=5)[::2, ::1], (W, H))
smoke = np.clip(0.55 + 0.9 * smoke, 0, 1)
dissolve = np.clip(1 - (YY + warp - top) / 650, 0, 1) * smoke
a_robe = a * ((1 - t) + t * dissolve)
# loose wisps curling off the shoulders and the hem
wisps = np.clip(cv2.resize(fbm(30, 2, seed=9)[::2, ::1], (W, H)) * 1.1 - 0.35, 0, 1) * np.clip(
    1 - np.hypot((XX - E[0] - 60) / 320, (YY - top - 260) / 380), 0, 1) * 0.3
wisps *= np.clip(1 - cv2.GaussianBlur(a, (0, 0), 40) * 0.6, 0, 1)
a_fig = np.clip(a_robe + wisps * (1 - a_robe), 0, 1)
# soft, slightly ragged cloth edge (a ghost, not a paper cut-out) - only along the outline
soft = cv2.GaussianBlur(a, (0, 0), 4) * (YY < top)  # the cloth outline above the smoke
rim = np.clip(1 - np.abs(soft - 0.5) * 2, 0, 1)  # 1 on the outline, 0 inside and outside
a_fig = np.clip(a_fig * (1 + rim * 0.6 * fbm(5, seed=11)), 0, 1)

# black level: the darkest cloth sits at the plate's own black, not pure 0
black = np.percentile(plate.mean(axis=2), 0.5)
cloth = cloth + black * 0.9
# the eyes light the brim from inside (already in the render) - keep it
# defocus: he's in focus, the figure is a step behind him, like the wall
DEF = 2.2
cloth = cv2.GaussianBlur(cloth, (0, 0), DEF)
a_fig = cv2.GaussianBlur(a_fig, (0, 0), DEF)
eye = cv2.GaussianBlur(eye, (0, 0), 1.0)
# the plate's own noise, measured on its dark wall, laid on the figure
hp = plate8.astype(np.float32) - cv2.GaussianBlur(plate8.astype(np.float32), (0, 0), 2)
dark = (plate8.mean(axis=2) < 70) & (m < 0.5)
sigma = hp[dark].std() / 255
print(f"plate noise sigma {sigma * 255:.1f}/255")

# ---- red light from the eyes ------------------------------------------------
d2 = ((XX - E[0]) ** 2 + (YY - E[1]) ** 2)
L = 1.0 / (1 + d2 / 240 ** 2)  # irradiance, 1 at the eyes
# the eyes face forward: little light goes back onto the wall behind the figure
L_wall = 0.35 / (1 + d2 / 170 ** 2) * np.clip(1 - a_fig * 0.9, 0, 1)  # only a local spill around the figure
albedo = 0.3 + 0.7 * np.sqrt(np.clip(plate.mean(axis=2, keepdims=True), 0, 1))
bg = plate + albedo * L_wall[..., None] * RED * 0.55

# figure over the wall, then its eyes
bg = bg * (1 - a_fig[..., None]) + cloth * a_fig[..., None]
core = cv2.GaussianBlur(eye, (0, 0), 0.6)[..., None]
bg = bg * (1 - core) + core * np.array([0.55, 0.75, 2.2], np.float32)

# him: rim light on the edges facing the eyes
mb = cv2.GaussianBlur(m, (0, 0), 14)  # smooth outline: the light doesn't care about matte jaggies
gx = cv2.Sobel(mb, cv2.CV_32F, 1, 0, ksize=5)
gy = cv2.Sobel(mb, cv2.CV_32F, 0, 1, ksize=5)
gn = np.hypot(gx, gy) + 1e-6
nx, ny = -gx / gn, -gy / gn  # outward normal
lx, ly = (E[0] - XX), (E[1] - YY)
ln = np.hypot(lx, ly) + 1e-6
facing = np.clip((nx * lx + ny * ly) / ln, 0, 1) ** 1.5
dist_in = cv2.distanceTransform((cv2.GaussianBlur(m, (0, 0), 6) > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
band = np.exp(-dist_in / 16.0)  # the light grazes the edge and wraps a little
band = cv2.GaussianBlur(band * facing, (0, 0), 5)
# brighter surfaces (skin, sweater) catch more of it; dark hair catches a thin sheen
skin_alb = 0.2 + 0.8 * np.sqrt(np.clip(plate.mean(axis=2, keepdims=True), 0, 1))
lit = plate + skin_alb * (L * band)[..., None] * RED * 2.0 + plate * (L * 0.12)[..., None] * RED

out = bg * (1 - him) + lit * him

# lens bloom from the visible eyes (happens in the camera, so it goes over everything)
vis = eye * (1 - him[..., 0])
bloom = (cv2.GaussianBlur(vis, (0, 0), 5) * 1.2 + cv2.GaussianBlur(vis, (0, 0), 16) * 1.6 +
         cv2.GaussianBlur(vis, (0, 0), 48) * 2.2)
out = out + bloom[..., None] * RED * 0.8

res = srgb(out)
grain = rng.normal(0, sigma, (H, W, 1)).astype(np.float32)
res = res + grain * (a_fig[..., None] * (1 - him))
res8 = (np.clip(res, 0, 1) * 255).astype(np.uint8)
cv2.imwrite("work/ghost-mg/style_frame.png", res8)
cv2.imwrite("work/ghost-mg/style_frame_side.png",
            cv2.resize(np.hstack([plate8, res8]), (1080, 960), interpolation=cv2.INTER_AREA))
print("wrote style_frame.png")
