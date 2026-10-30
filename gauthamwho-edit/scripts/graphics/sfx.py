"""Synthesised sound effects for the air-fryer / slow-world beat (no samples,
nothing to license). Writes sfx.wav: 48 kHz stereo, exactly the 373-frame window
(6.2167 s), each effect on its frame. Kept quiet (peaks around -16 dBFS) — they
sit under his voice.
"""
import numpy as np
import wave

SR = 48000
DUR = 373 / 60
rng = np.random.default_rng(29)
out = np.zeros((int(DUR * SR) + SR, 2), np.float32)


def env(n, a, d):
    """Attack (s) then exponential decay with time-constant d (s)."""
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def tone(f0, f1, dur, a=0.004, d=0.08, shape="sin"):
    n = int(dur * SR)
    f = np.geomspace(f0, f1, n)
    ph = 2 * np.pi * np.cumsum(f) / SR
    w = np.sin(ph) if shape == "sin" else np.sign(np.sin(ph)) * 0.3
    return w * env(n, a, d)


def noise_band(dur, lo, hi, a=0.05, d=0.2, sweep=None):
    """Band-limited noise (FFT mask); optional centre sweep (lo->hi Hz over time)."""
    n = int(dur * SR)
    x = rng.standard_normal(n)
    if sweep:
        out_ = np.zeros(n)
        hop = 1024
        for i in range(0, n, hop):
            seg = x[i:i + hop * 2]
            c = np.geomspace(*sweep, n)[min(i, n - 1)]
            spec = np.fft.rfft(seg)
            fr = np.fft.rfftfreq(len(seg), 1 / SR)
            spec *= np.exp(-((np.log(fr + 1) - np.log(c)) ** 2) / 0.35)
            y = np.fft.irfft(spec, len(seg)) * np.hanning(len(seg))
            out_[i:i + len(y)] += y[: n - i]
        x = out_
    else:
        spec = np.fft.rfft(x)
        fr = np.fft.rfftfreq(n, 1 / SR)
        spec[(fr < lo) | (fr > hi)] = 0
        x = np.fft.irfft(spec, n)
    x /= np.max(np.abs(x)) + 1e-9
    t = np.arange(n) / SR
    shape = np.minimum(1, t / a) * np.minimum(1, (dur - t) / max(d, 1e-3))
    return x * np.clip(shape, 0, 1)


def mix(*parts):
    """Sum signals of different lengths (each is (weight, signal))."""
    n = max(len(x) for _, x in parts)
    y = np.zeros(n)
    for wgt, x in parts:
        y[: len(x)] += wgt * x
    return y


def place(sig, frame, gain_db, pan=0.0):
    i = int(frame / 60 * SR)
    g = 10 ** (gain_db / 20)
    l, r = g * np.sqrt((1 - pan) / 2) * 1.414, g * np.sqrt((1 + pan) / 2) * 1.414
    out[i:i + len(sig), 0] += sig * l
    out[i:i + len(sig), 1] += sig * r


# globe pops in (right side)
place(tone(760, 380, 0.09, d=0.04), 14, -20, pan=0.5)
# fryer lands (left)
place(mix((1, tone(170, 85, 0.16, d=0.06)), (0.25, noise_band(0.05, 2000, 6000, a=0.002, d=0.04))), 18, -18, pan=-0.5)
# drawer slides in, then closes
place(noise_band(0.34, 600, 3000, a=0.12, d=0.12), 20, -24, pan=-0.45)
place(mix((1, tone(220, 120, 0.08, d=0.03)), (0.4, noise_band(0.03, 2500, 7000, a=0.001, d=0.02))), 40, -19, pan=-0.45)
# hand pops up
place(noise_band(0.12, 1500, 6000, a=0.03, d=0.06), 58, -27, pan=-0.4)
# the click
click = mix((0.6, noise_band(0.012, 3000, 12000, a=0.0005, d=0.008)), (1, tone(2400, 1800, 0.03, a=0.0005, d=0.008)))
place(click, 72, -14, pan=-0.35)
# the world slows: downward tape-stop sweep + air
place(mix((0.8, tone(520, 55, 0.85, a=0.02, d=0.6)), (0.3, noise_band(0.85, 0, 0, a=0.05, d=0.4, sweep=(3000, 300)))), 72, -21, pan=0.35)
# fryer thrown off left
place(noise_band(0.42, 0, 0, a=0.04, d=0.25, sweep=(2500, 400)), 131, -21, pan=-0.6)
# globe glides behind him
place(noise_band(0.75, 200, 1400, a=0.3, d=0.35), 132, -26, pan=0.1)
# exit whip, top-right
place(noise_band(0.3, 0, 0, a=0.12, d=0.08, sweep=(500, 5000)), 350, -19, pan=0.5)

out = out[: int(DUR * SR)]
peak = np.max(np.abs(out))
print("peak %.1f dBFS" % (20 * np.log10(peak + 1e-9)))
pcm = (np.clip(out, -1, 1) * 32767).astype(np.int16)
with wave.open("sfx.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote sfx.wav", round(len(out) / SR, 3), "s")
