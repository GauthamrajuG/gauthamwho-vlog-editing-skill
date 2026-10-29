"""SAM 2.1 cut-out of Gautham on every frame of the ghost window: plate_wide.mkv indexes
23..124 (v6 36.15-37.85 s; the walk-in shot starts at index 23). Seeded on index 32 (v6
36.30) with the board matte of that frame, propagated forward in 20-frame chunks (each
seeded with the previous chunk's last mask) and backward to 23. Masks are hole-filled
and keep only the largest piece. Writes anim/masks/<index>.png at 1080x1920 (white = him)."""
import os

import cv2
import numpy as np
import torch
from transformers import Sam2VideoModel, Sam2VideoProcessor

A, B, SEED = 23, 124, 32
W = 960
os.makedirs("anim/masks", exist_ok=True)
cap = cv2.VideoCapture("plate_wide.mkv")
FW, FH = int(cap.get(3)), int(cap.get(4))
H = int(FH * W / FW)
small = {}  # only the 960-wide frames stay in memory
for i in range(B + 1):
    ok, f = cap.read()
    if i >= A:
        small[i] = cv2.cvtColor(cv2.resize(f, (W, H)), cv2.COLOR_BGR2RGB)

dev = "cuda"
model = Sam2VideoModel.from_pretrained("facebook/sam2.1-hiera-base-plus").to(dev).eval()
proc = Sam2VideoProcessor.from_pretrained("facebook/sam2.1-hiera-base-plus")


def clean(lg):
    hard = (cv2.resize(lg.astype(np.float32), (FW, FH), interpolation=cv2.INTER_CUBIC) > 0).astype(np.uint8)
    hard = cv2.morphologyEx(hard, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(hard)
    if n > 1:
        hard = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    inv = (1 - hard).copy()
    cv2.floodFill(inv, np.zeros((FH + 2, FW + 2), np.uint8), (0, 0), 2)
    hard[inv == 1] = 1
    return hard


def run(idx_list, seed_mask):
    """Propagate through idx_list (in that order) seeded with a mask on its first frame."""
    s = proc.init_video_session(video=[small[i] for i in idx_list], inference_device=dev,
                                video_storage_device="cpu", inference_state_device="cpu", dtype=torch.float32)
    proc.add_inputs_to_inference_session(inference_session=s, frame_idx=0, obj_ids=1,
                                         input_masks=seed_mask.astype(np.uint8))
    res = {}
    with torch.inference_mode():
        model(inference_session=s, frame_idx=0)
        for o in model.propagate_in_video_iterator(s, start_frame_idx=0):
            lg = proc.post_process_masks([o.pred_masks], original_sizes=[[H, W]], binarize=False)[0]
            res[idx_list[o.frame_idx]] = lg.squeeze().cpu().numpy()
    return res


seed = cv2.resize(cv2.imread("board/matte_36.30.png", 0), (W, H)) > 127
# forward (resumes after a crash from the last mask written)
done = sorted(int(f[:5]) for f in os.listdir("anim/masks") if int(f[:5]) >= SEED)
a, cur = SEED, seed
if done:
    a = done[-1]
    cur = cv2.resize(cv2.imread(f"anim/masks/{a:05d}.png", 0), (W, H)) > 127
while a < B:
    b = min(B, a + 20)
    r = run(list(range(a, b + 1)), cur)
    for i, lg in r.items():
        cv2.imwrite(f"anim/masks/{i:05d}.png", clean(lg) * 255)
    cur = r[b] > 0
    a = b
    print("forward to", b, flush=True)
# backward
r = run(list(range(SEED, A - 1, -1)), seed) if not os.path.exists(f"anim/masks/{A:05d}.png") else {}
for i, lg in r.items():
    if i != SEED:
        cv2.imwrite(f"anim/masks/{i:05d}.png", clean(lg) * 255)
print("backward to", A)
# check against the six board mattes
for t, i in [("36.30", 32), ("36.60", 50), ("36.95", 71), ("37.30", 92), ("37.55", 107), ("37.75", 119)]:
    m = cv2.imread(f"anim/masks/{i:05d}.png", 0) > 127
    ref = cv2.imread(f"board/matte_{t}.png", 0) > 127
    print(t, "IoU vs board matte", round((m & ref).sum() / (m | ref).sum(), 3))
