"""Camera track for the whole 373-frame plate, wall only.

Corners on the wall (his cut-out, dilated, is excluded), followed with
Lucas-Kanade optical flow and fitted per frame with a RANSAC similarity
transform (shift + rotation + scale). Corners are re-seeded every 20 frames so
the track never runs dry as he moves. The transforms are chained, then
re-anchored on frame 66 (the approved style frame), so frame 66 = identity.
Writes track.npy: (373, 2, 3) affine matrices mapping frame-66 coordinates
into each frame (full 1080x1920 pixels), lightly smoothed (3-frame window) to
remove sub-pixel jitter without lagging real motion.
"""
import os

import cv2
import numpy as np

REF = 66
S = 0.5  # track at half resolution
cap = cv2.VideoCapture("plate.mkv")
N = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
grays, excl = [], []
for i in range(N):
    ok, f = cap.read()
    g = cv2.cvtColor(cv2.resize(f, None, fx=S, fy=S), cv2.COLOR_BGR2GRAY)
    grays.append(g)
    mp = f"masks/{i:05d}.png"
    if os.path.exists(mp):
        m = cv2.resize(cv2.imread(mp, 0), (g.shape[1], g.shape[0]))
        m = cv2.dilate(m, np.ones((25, 25), np.uint8))
        excl.append(m < 128)
    else:
        excl.append(np.ones_like(g, bool))


def seed(i):
    mask = (excl[i] * 255).astype(np.uint8)
    return cv2.goodFeaturesToTrack(grays[i], maxCorners=400, qualityLevel=0.003, minDistance=6, mask=mask)


chain = [np.eye(3)]
pts = seed(0)
stats = []
for i in range(1, N):
    if pts is None or len(pts) < 40 or i % 20 == 0:
        pts = seed(i - 1)
    nxt, st, _ = cv2.calcOpticalFlowPyrLK(grays[i - 1], grays[i], pts, None, winSize=(31, 31), maxLevel=4)
    a, b = pts[st == 1], nxt[st == 1]
    keep = excl[i][np.clip(b[:, 1].astype(int), 0, grays[i].shape[0] - 1), np.clip(b[:, 0].astype(int), 0, grays[i].shape[1] - 1)]
    a, b = a[keep], b[keep]
    M, inl = cv2.estimateAffinePartial2D(a, b, method=cv2.RANSAC, ransacReprojThreshold=1.0)
    if M is None:
        M, inl = np.array([[1, 0, 0], [0, 1, 0]], float), np.zeros((1, 1))
    M = M.copy()
    M[:, 2] /= S  # to full-resolution pixels
    chain.append(np.vstack([M, [0, 0, 1]]) @ chain[-1])
    stats.append(int(inl.sum()))
    pts = b[inl.ravel() == 1].reshape(-1, 1, 2) if inl is not None and inl.sum() > 0 else None

chain = np.array(chain)
ref_inv = np.linalg.inv(chain[REF])
rel = np.array([c @ ref_inv for c in chain])  # frame-66 coords -> frame i
sm = rel.copy()
for i in range(1, N - 1):
    sm[i] = (rel[i - 1] + 2 * rel[i] + rel[i + 1]) / 4
np.save("track.npy", sm[:, :2, :])
print("frames", N, "| inliers per frame min %d median %d" % (min(stats), int(np.median(stats))))
print("shift at frame 0: (%.0f, %.0f)  at 372: (%.0f, %.0f) px" % (sm[0, 0, 2], sm[0, 1, 2], sm[-1, 0, 2], sm[-1, 1, 2]))
