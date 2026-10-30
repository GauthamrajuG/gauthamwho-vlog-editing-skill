"""Storyboard v3, step 1: full-resolution plates and SAM 2.1 cut-outs for the six panels,
plus his LEFT shoulder line (screen right) in each, so the ghost can rise to it.

v6 frame n = source frame n + 454 = plate_wide.mkv index n + 454 - 2600.
Click points come from the 540-wide storyboard masks of the same frames (sb/m_<t>.png).
Writes board/plate_<t>.png, board/matte_<t>.png and board/geom.json.
"""
import json
import os

import cv2
import numpy as np
import torch
from transformers import Sam2VideoModel, Sam2VideoProcessor

TS = ["36.30", "36.60", "36.95", "37.30", "37.55", "37.75"]
os.makedirs("board", exist_ok=True)
dev = "cuda"
model = Sam2VideoModel.from_pretrained("facebook/sam2.1-hiera-base-plus").to(dev).eval()
proc = Sam2VideoProcessor.from_pretrained("facebook/sam2.1-hiera-base-plus")
cap = cv2.VideoCapture("plate_wide.mkv")
geom = {}
for t in TS:
    idx = round(float(t) * 60) + 454 - 2600
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    _, plate = cap.read()
    cv2.imwrite(f"board/plate_{t}.png", plate)
    FH, FW = plate.shape[:2]
    W, H = 960, int(FH * 960 / FW)
    small = cv2.cvtColor(cv2.resize(plate, (W, H)), cv2.COLOR_BGR2RGB)
    sb = cv2.resize(cv2.imread(f"sb/m_{t}.png", 0), (W, H)) > 127
    inside = cv2.erode(sb.astype(np.uint8), np.ones((61, 61), np.uint8)) > 0
    outside = cv2.dilate(sb.astype(np.uint8), np.ones((61, 61), np.uint8)) == 0
    # several click sets; keep the cut-out that best matches the storyboard mask (IoU)
    best = None
    for seed in range(1, 7):
        rng = np.random.default_rng(seed)
        # 3 points on the head (top third of him) + 3 on the body, so the head is never dropped
        yx = np.argwhere(inside)
        y0, y1 = yx[:, 0].min(), yx[:, 0].max()
        head = yx[yx[:, 0] < y0 + 0.3 * (y1 - y0)]
        body = yx[yx[:, 0] > y0 + 0.6 * (y1 - y0)]
        pos = np.vstack([head[rng.choice(len(head), 3, replace=False)],
                         body[rng.choice(len(body), 3, replace=False)]])[:, ::-1].tolist()
        neg = np.argwhere(outside)[rng.choice(outside.sum(), 4, replace=False)][:, ::-1].tolist()
        s = proc.init_video_session(video=[small], inference_device=dev, video_storage_device="cpu",
                                    inference_state_device="cpu", dtype=torch.float32)
        proc.add_inputs_to_inference_session(inference_session=s, frame_idx=0, obj_ids=1,
                                             input_points=[[pos + neg]], input_labels=[[[1] * 6 + [0] * 4]])
        with torch.inference_mode():
            out = model(inference_session=s, frame_idx=0)
        lg = proc.post_process_masks([out.pred_masks], original_sizes=[[H, W]], binarize=False)[0].squeeze().cpu().numpy()
        iou = ((lg > 0) & sb).sum() / max(1, ((lg > 0) | sb).sum())
        if best is None or iou > best[0]:
            best = (iou, lg)
    print(t, f"IoU with storyboard mask {best[0]:.2f}")
    lg = best[1]
    hard = (cv2.resize(lg.astype(np.float32), (FW, FH), interpolation=cv2.INTER_CUBIC) > 0).astype(np.uint8)
    hard = cv2.morphologyEx(hard, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(hard)
    hard = (lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    inv = (1 - hard).copy()
    cv2.floodFill(inv, np.zeros((FH + 2, FW + 2), np.uint8), (0, 0), 2)
    hard[inv == 1] = 1
    cv2.imwrite(f"board/matte_{t}.png", hard * 255)
    # his left shoulder (screen right): top of the matte across x = 860..1040
    cols = range(860, 1041, 20)
    tops = [int(np.argmax(hard[:, x] > 0)) if hard[:, x].any() else FH for x in cols]
    # right edge of his head/neck at the shoulder line minus 200 px
    row = hard[max(0, int(np.median(tops)) - 200)]
    neck_r = int(np.nonzero(row)[0].max()) if row.any() else 700
    geom[t] = {"shoulder_y": int(np.median(tops)), "neck_right_x": neck_r, "idx": idx}
    print(t, geom[t], f"him {hard.mean():.0%}", flush=True)
json.dump(geom, open("board/geom.json", "w"), indent=1)
