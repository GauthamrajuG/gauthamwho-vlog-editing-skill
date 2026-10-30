"""Style frame, step 1: the plate frame (v6 frame 2238 = source 2692 = plate_wide index 92)
and Gautham's SAM 2.1 cut-out at full resolution. Click points come from the storyboard
mask of the same frame (sb/m_37.30.png, 540 wide): points inside him and on the wall."""
import cv2
import numpy as np
import torch
from transformers import Sam2VideoModel, Sam2VideoProcessor

IDX = 92
cap = cv2.VideoCapture("plate_wide.mkv")
cap.set(cv2.CAP_PROP_POS_FRAMES, IDX)
_, plate = cap.read()
cv2.imwrite("still_plate.png", plate)
FH, FW = plate.shape[:2]

W = 960
H = int(FH * W / FW)
small = cv2.cvtColor(cv2.resize(plate, (W, H)), cv2.COLOR_BGR2RGB)
sb = cv2.resize(cv2.imread("sb/m_37.30.png", 0), (W, H)) > 127
inside = cv2.erode(sb.astype(np.uint8), np.ones((61, 61), np.uint8)) > 0
outside = cv2.dilate(sb.astype(np.uint8), np.ones((61, 61), np.uint8)) == 0
rng = np.random.default_rng(1)
pos = np.argwhere(inside)[rng.choice(inside.sum(), 6, replace=False)][:, ::-1].tolist()
neg = np.argwhere(outside)[rng.choice(outside.sum(), 4, replace=False)][:, ::-1].tolist()

dev = "cuda"
model = Sam2VideoModel.from_pretrained("facebook/sam2.1-hiera-base-plus").to(dev).eval()
proc = Sam2VideoProcessor.from_pretrained("facebook/sam2.1-hiera-base-plus")
s = proc.init_video_session(video=[small], inference_device=dev, video_storage_device="cpu",
                            inference_state_device="cpu", dtype=torch.float32)
proc.add_inputs_to_inference_session(inference_session=s, frame_idx=0, obj_ids=1,
                                     input_points=[[pos + neg]], input_labels=[[[1] * 6 + [0] * 4]])
with torch.inference_mode():
    out = model(inference_session=s, frame_idx=0)
m = proc.post_process_masks([out.pred_masks], original_sizes=[[H, W]], binarize=False)[0].squeeze().cpu().numpy()
m = cv2.resize(m.astype(np.float32), (FW, FH), interpolation=cv2.INTER_CUBIC)
m = (np.clip(m * 2.0 + 0.5, 0, 1) * 255).astype(np.uint8)  # logits -> soft matte around the 0 edge
cv2.imwrite("still_mask.png", m)
print("him:", f"{(m > 127).mean():.0%} of frame")
