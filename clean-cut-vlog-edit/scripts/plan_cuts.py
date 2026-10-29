"""Plan a clean-cut edit: which source ranges to keep, in source order.

Usage:
    python -I plan_cuts.py plan.json

plan.json (all times in source seconds):
{
  "duration": 96.533,                 # source length (probe.py)
  "transcript": "transcript.json",    # transcribe.py output (word timings)
  "shots": "shots.json",              # ffmpeg-skill scenes.py --shots --json
  "intro_end": 9.05,                  # [0, intro_end] plays untouched (0 = none)
  "protect": [[55.7, 60.0], [83.0, 96.5]],   # a range protects every WHOLE shot it
                                             # overlaps by 0.3 s or more
  "remove": [[30.12, 30.90]],         # stammers / repeated takes to drop
  "gap": 0.25,                        # silence between words longer than this is cut
  "gap_overrides": [[52.0, 70.0, 1.0]],   # optional: a looser gap inside a range (an
                                          # out-of-breath scene whose pauses ARE the content)
  "pad": 0.08,                        # air kept before the first / after the last word
  "broll": "trim",                    # "trim" = shave empty head/tail of non-talking
                                      # shots, "keep" = play them whole
  "broll_max": 0,                     # >0: also cap each unprotected silent shot at
                                      # this many seconds (keeps its opening)
  "fps": 60                           # source frame rate (probe.py), default 30
}

Prints the segment list build_reel.py reads, writes it to segments.txt next to
plan.json, and reports every word a cut touches (it should only ever be words
inside "remove").
"""
import json
import os
import sys


plan_path = sys.argv[1]
base = os.path.dirname(os.path.abspath(plan_path))
P = json.load(open(plan_path, encoding="utf-8"))
rel = lambda p: p if os.path.isabs(p) else os.path.join(base, p)

dur = P["duration"]
FRAME = 1 / P.get("fps", 30)
MIN_PROTECT = 0.3  # overlap a protect range needs to claim a shot
gap, pad = P.get("gap", 0.25), P.get("pad", 0.08)
words = [w for s in json.load(open(rel(P["transcript"]), encoding="utf-8")) for w in s["words"]]
words.sort(key=lambda w: w["s"])
shots = json.load(open(rel(P["shots"]), encoding="utf-8"))["shots"]
removes = [tuple(r) for r in P.get("remove", [])]


def overlaps(a0, a1, b0, b1):
    return a0 < b1 and b0 < a1


def in_remove(t):
    return any(a <= t <= b for a, b in removes)


# 1. Classify shots.
for sh in shots:
    sh["talk"] = any(overlaps(w["s"], w["e"], sh["start"], sh["end"]) for w in words)
    sh["protected"] = any(min(b, sh["end"]) - max(a, sh["start"]) >= MIN_PROTECT
                          for a, b in P.get("protect", []))

# A non-talking shot sitting between two protected shots is protected too:
# the creator asked for that whole stretch to play as shot.
for i in range(1, len(shots) - 1):
    if not shots[i]["talk"] and shots[i - 1]["protected"] and shots[i + 1]["protected"]:
        shots[i]["protected"] = True

keep = []
intro_end = P.get("intro_end", 0) or 0
if intro_end:
    keep.append((0.0, intro_end))

# 2. Protected shots play whole.
for sh in shots:
    if sh["protected"]:
        keep.append((sh["start"], sh["end"]))

# 3. Speech islands: words closer than `gap` stay together, longer silences go.
live = [w for w in words if not in_remove((w["s"] + w["e"]) / 2)]
islands = []
gap_at = lambda t: next((g for a, b, g in P.get("gap_overrides", []) if a <= t <= b), gap)
for w in live:
    if islands and w["s"] - islands[-1][1] <= gap_at(w["s"]):
        islands[-1][1] = max(islands[-1][1], w["e"])
    else:
        islands.append([w["s"], w["e"]])
for a, b in islands:
    keep.append((max(0.0, a - pad), min(dur, b + pad)))

# 3b. Silent footage at the HEAD or TAIL of a talking shot (walking up before
# speaking, setting the air fryer before explaining it) is b-roll, not dead
# air, once it runs 1.5 s or more: keep its first half (max 2 s). Silences
# BETWEEN words are always pauses and always go, however long.
SILENT_BROLL = 1.5
for sh in shots:
    if not sh["talk"] or sh["protected"]:
        continue
    inside = [(max(a, sh["start"]), min(b, sh["end"])) for a, b in islands
              if overlaps(a, b, sh["start"], sh["end"])]
    if not inside:
        continue
    for a, b in ((sh["start"], inside[0][0]), (inside[-1][1], sh["end"])):
        if b - a >= SILENT_BROLL:
            keep.append((a + 0.06, a + 0.06 + min(2.0, 0.5 * (b - a))))

# 4. Non-talking, unprotected shots.
for sh in shots:
    if sh["talk"] or sh["protected"]:
        continue
    a, b = sh["start"], sh["end"]
    if P.get("broll", "trim") == "trim":
        t = min(0.4, 0.12 * (b - a))
        a, b = a + t, b - t
    if P.get("broll_max", 0) > 0:
        b = min(b, a + P["broll_max"])
    if b - a >= 0.3:
        keep.append((a, b))

# 5. Stammers come out of everything except protected / intro ranges.
def cut_removes(seg):
    out = [seg]
    for r0, r1 in removes:
        nxt = []
        for a, b in out:
            if overlaps(a, b, r0, r1) and not (a < intro_end and b <= intro_end):
                if a < r0:
                    nxt.append((a, r0))
                if r1 < b:
                    nxt.append((r1, b))
            else:
                nxt.append((a, b))
        out = nxt
    return out

protected_or_intro = [(0.0, intro_end)] if intro_end else []
protected_or_intro += [(s["start"], s["end"]) for s in shots if s["protected"]]
segs = []
for a, b in keep:
    if any(a >= p0 - 1e-6 and b <= p1 + 1e-6 for p0, p1 in protected_or_intro):
        segs.append((a, b))
    else:
        segs += cut_removes((a, b))

# 6. Union, merging anything closer than two frames.
segs.sort()
merged = []
for a, b in segs:
    if b - a < 2 * FRAME:
        continue
    if merged and a - merged[-1][1] < 2 * FRAME:
        merged[-1][1] = max(merged[-1][1], b)
    else:
        merged.append([a, b])

kept = lambda t: any(a - 1e-6 <= t <= b + 1e-6 for a, b in merged)
touched = [w for w in words if not (kept(w["s"] + 0.04) and kept(w["e"] - 0.04))]
unexpected = [w for w in touched if not in_remove((w["s"] + w["e"]) / 2)]
quiet_shots = [s for s in shots if not s["talk"] and s.get("audio_rms", 0) > 0.05 and not s["protected"]]

seg_str = ",".join(f"{a:.3f}-{b:.3f}".replace(".000", "") for a, b in merged)
open(os.path.join(base, "segments.txt"), "w").write(seg_str)
total = sum(b - a for a, b in merged)
print(f"{len(merged)} segments, {total:.2f} s of {dur:.2f} s")
for a, b in merged:
    print(f"  {a:7.3f} - {b:7.3f}  ({b - a:5.2f} s)")
print("words cut on purpose:", " ".join(f"{w['s']}-{w['e']}" for w in touched if w not in unexpected) or "none")
print("WORDS CUT BY MISTAKE:", " ".join(f"{w['s']}-{w['e']}" for w in unexpected) or "none")
edge = [(a, b) for a, b in P.get("protect", [])
        if any(abs(t - x) < 0.3 for t in (a, b) for s in shots for x in (s["start"], s["end"]))]
if edge:
    print("CHECK - protect ranges within 0.3 s of a shot boundary (set them inside the shot):",
          " ".join(f"{a}-{b}" for a, b in edge))
print("protected shots:", " ".join(f"{s['start']:.2f}-{s['end']:.2f}" for s in shots if s["protected"]) or "none")
if total > 90:
    print(f"CHECK - {total:.1f} s is over the 90 s that check.py --platform reels allows; tell the user")
if quiet_shots:
    print("CHECK - loud shots with no transcribed words (untranscribed speech?):",
          " ".join(f"{s['start']:.2f}-{s['end']:.2f}" for s in quiet_shots))
print("segments.txt written")
