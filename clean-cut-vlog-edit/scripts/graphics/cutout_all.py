"""SAM 2.1 cut-out of Gautham on every frame of plate.mkv (GPU, 30-frame chunks).
Click points are on frame 0, as fractions of the frame. Writes masks/NNNNN.png
(white = him) at 1080x1920.
"""
import os
import time

import cv2
import numpy as np
import torch
from transformers import Sam2VideoModel, Sam2VideoProcessor

VIDEO = "plate.mkv"
W = 960
P = [(0.23, 0.57), (0.21, 0.44), (0.28, 0.88), (0.12, 0.95), (0.40, 0.97), (0.78, 0.22), (0.82, 0.62), (0.15, 0.12)]
L = [1, 1, 1, 1, 1, 0, 0, 0]

cap = cv2.VideoCapture(VIDEO)
N = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
FW, FH = int(cap.get(3)), int(cap.get(4))
cap.release()
H = int(FH * W / FW)
PTS = [[int(x * W), int(y * H)] for x, y in P]

dev = "cuda"
model = Sam2VideoModel.from_pretrained("facebook/sam2.1-hiera-base-plus").to(dev).eval()
proc = Sam2VideoProcessor.from_pretrained("facebook/sam2.1-hiera-base-plus")


def read_frames(a, b):
    c = cv2.VideoCapture(VIDEO)
    c.set(cv2.CAP_PROP_POS_FRAMES, a)
    out = []
    for _ in range(a, b + 1):
        ok, im = c.read()
        if not ok:
            break
        out.append(cv2.cvtColor(cv2.resize(im, (W, H)), cv2.COLOR_BGR2RGB))
    return out


def chunk(frames, points=None, labels=None, mask=None):
    s = proc.init_video_session(video=frames, inference_device=dev, video_storage_device="cpu",
                                inference_state_device="cpu", dtype=torch.float32)
    if mask is None:
        proc.add_inputs_to_inference_session(inference_session=s, frame_idx=0, obj_ids=1,
                                             input_points=[[points]], input_labels=[[labels]])
    else:
        proc.add_inputs_to_inference_session(inference_session=s, frame_idx=0, obj_ids=1,
                                             input_masks=mask.astype(np.uint8))
    res = {}
    with torch.inference_mode():
        model(inference_session=s, frame_idx=0)
        for o in model.propagate_in_video_iterator(s, start_frame_idx=0):
            m = proc.post_process_masks([o.pred_masks], original_sizes=[[H, W]], binarize=True)[0]
            res[o.frame_idx] = m.squeeze().cpu().numpy().astype(bool)
    return res


os.makedirs("masks", exist_ok=True)
t0, a, seed = time.time(), 0, None
done = sorted(int(f[:5]) for f in os.listdir("masks"))
if done:  # resume after a crash: continue from the last mask, seeded with it
    a = done[-1]
    last = cv2.imread(f"masks/{a:05d}.png", 0)
    seed = cv2.resize(last, (W, H)) > 127
    print("resuming at frame", a, flush=True)
while a < N - 1:
    b = min(N - 1, a + 20)
    fr = read_frames(a, b)
    r = chunk(fr, PTS, L) if seed is None else chunk(fr, mask=seed)
    for k, m in r.items():
        full = cv2.resize(m.astype(np.uint8) * 255, (FW, FH), interpolation=cv2.INTER_LINEAR)
        cv2.imwrite(f"masks/{a + k:05d}.png", full)
    seed, a = r[len(fr) - 1], b
    print(f"frames {a}/{N - 1}  {time.time() - t0:.0f}s", flush=True)
print("done", len(os.listdir("masks")), "masks", f"{time.time() - t0:.0f}s")
