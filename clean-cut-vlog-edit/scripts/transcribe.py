"""Word-timed transcript of a WAV with faster-whisper, CPU-only, low memory.

Usage (from the job's work folder, with the job venv):
    .venv/Scripts/python transcribe.py audio.wav [model] [task] [lang]
        model: tiny | base | small (default small)
        task:  transcribe (default) | translate  (translate = English text, to
               understand what is said; timings come from the transcribe pass)
        lang:  ta, en, hi, ... (default: auto-detect)

Writes transcript_<task>.json: [{start, end, text, words: [{w, s, e}]}].

The WAV is read with the standard library and resampled with numpy instead
of letting faster-whisper decode it: some PyAV builds reject faster-whisper's
`metadata_errors` argument. Set OPENBLAS_NUM_THREADS=1 on low-memory machines.
"""
import json
import sys
import wave

import numpy as np
from faster_whisper import WhisperModel

path = sys.argv[1]
model = sys.argv[2] if len(sys.argv) > 2 else "small"
task = sys.argv[3] if len(sys.argv) > 3 else "transcribe"
lang = sys.argv[4] if len(sys.argv) > 4 else None

w = wave.open(path)
sr, ch = w.getframerate(), w.getnchannels()
a = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, ch).mean(1) / 32768.0
a = np.interp(np.arange(0, len(a), sr / 16000), np.arange(len(a)), a).astype(np.float32)

m = WhisperModel(model, device="cpu", compute_type="int8", cpu_threads=2)
segs, info = m.transcribe(a, task=task, language=lang, condition_on_previous_text=False,
                          word_timestamps=True, vad_filter=False)
print("lang", info.language, round(info.language_probability, 2), file=sys.stderr)

out = []
for s in segs:
    out.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                "words": [{"w": x.word, "s": round(x.start, 2), "e": round(x.end, 2)} for x in s.words]})
    print(f"{s.start:6.2f}-{s.end:6.2f} {s.text.strip()}")
json.dump(out, open(f"transcript_{task}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
