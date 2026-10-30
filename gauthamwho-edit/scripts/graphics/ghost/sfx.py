"""Synthesised sound for the walk-in scare (nothing sampled or downloaded). 48 kHz stereo,
the 102-frame ghost window (L0 = v6 36.15 s). Kept under his voice.
  L8-L46   low rumble swelling as it rises (sub + filtered noise), behind his left (right pan)
  L48      a sharp breathy hiss + a tiny low hit when the eyes ignite
  L70-L94  whoosh sweeping right -> left as it swoops behind him and out
"""
import wave

import numpy as np

SR = 48000
N = 102
DUR = N / 60
rng = np.random.default_rng(31)
out = np.zeros((int(DUR * SR) + SR, 2), np.float32)


def band(dur, lo, hi):
    n = int(dur * SR)
    x = rng.standard_normal(n)
    spec = np.fft.rfft(x)
    fr = np.fft.rfftfreq(n, 1 / SR)
    spec[(fr < lo) | (fr > hi)] = 0
    x = np.fft.irfft(spec, n)
    return x / (np.abs(x).max() + 1e-9)


def place(sig, frame, db, pan_from, pan_to=None):
    pan_to = pan_from if pan_to is None else pan_to
    i = int(frame / 60 * SR)
    sig = sig[: len(out) - i]
    pan = np.linspace(pan_from, pan_to, len(sig))
    g = 10 ** (db / 20)
    out[i:i + len(sig), 0] += sig * g * np.sqrt((1 - pan) / 2) * 1.414
    out[i:i + len(sig), 1] += sig * g * np.sqrt((1 + pan) / 2) * 1.414


t = np.arange(int(0.65 * SR)) / SR
env = np.minimum(1, t / 0.45) * np.minimum(1, (0.65 - t) / 0.15)
rumble = (np.sin(2 * np.pi * 42 * t + 2 * np.sin(2 * np.pi * 0.7 * t)) * 0.7 + band(0.65, 30, 180) * 0.6) * env
place(rumble, 8, -16, 0.5)

t = np.arange(int(0.5 * SR)) / SR
hiss = band(0.5, 2500, 9000) * np.minimum(1, t / 0.01) * np.exp(-t / 0.16)
hit = np.sin(2 * np.pi * 70 * t * np.exp(-t * 3)) * np.exp(-t / 0.09)
place(hiss * 0.7 + hit * 0.8, 48, -18, 0.45)

n = int(0.45 * SR)
t = np.arange(n) / SR
x = rng.standard_normal(n)
y = np.zeros(n)
hop = 1024
for i in range(0, n, hop):  # band-pass that sweeps up then down
    seg = x[i:i + hop * 2]
    c = 400 + 2600 * np.sin(np.pi * min(1, i / n)) ** 1.5
    spec = np.fft.rfft(seg)
    fr = np.fft.rfftfreq(len(seg), 1 / SR)
    spec *= np.exp(-((np.log(fr + 1) - np.log(c)) ** 2) / 0.3)
    yy = np.fft.irfft(spec, len(seg)) * np.hanning(len(seg))
    y[i:i + len(yy)] += yy[: n - i]
whoosh = y / (np.abs(y).max() + 1e-9) * np.sin(np.pi * t / t[-1]) ** 1.2
place(whoosh, 70, -15, 0.6, -0.8)

out = out[: int(DUR * SR)]
print("peak %.1f dBFS" % (20 * np.log10(np.abs(out).max() + 1e-9)))
with wave.open("anim/ghost_sfx.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
