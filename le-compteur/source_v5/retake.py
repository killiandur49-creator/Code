import sys, os, json, shutil, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tts
from tts import _one, _mos, VOICES, load, resample, asr_fr, cer
from lines import L
JOBS = [  # (part, shot, line index, candidate texts)
    (1, "03", 1, ["L'influenceuse aux quarante mille abonnés : neuf euros."]),
    (1, "06", 0, ["Inès. Elle ne regarde que ceux qui ont de l'argent."]),
    (1, "10", 1, ["Bonjour, Léo.", "Bonjour, Léo !", "Bonjour... Léo."]),
    (3, "05", 0, ["Attends, Léo... on rigolait, hein ?", "Léo, attends... on rigolait, hein ?", "Hé, Léo... c'était pour rigoler, hein ?"]),
]
dj = os.path.join(HERE, "vo/durs.json"); D = json.load(open(dj))
changes = {}
for part, sid, idx, texts in JOBS:
    spk = [ln for s_, a, b, lines in [x for x in L[part] if x[0] == sid] for ln in lines][idx][1]
    base, tgt = VOICES[spk]
    best = None
    with tempfile.TemporaryDirectory() as d:
        k = 0
        for text in texts:
            for sp in [base, base - 0.06, base - 0.1, base + 0.04, base - 0.14, base]:
                f = f"{d}/t{k}.wav"; _one(spk, text, sp, tgt, f); k += 1
                x, sr = load(f); x16 = resample(x, sr); h = asr_fr(x16); c = cer(text, h); m = _mos(x16)
                sc = c - 0.03 * (m - 3.5)
                if best is None or sc < best[0]: best = (sc, c, h, f, text)
                if c <= 0.02: break
            if best[1] <= 0.02: break
        out = os.path.join(HERE, f"vo/p{part}_{sid}_{idx}.wav"); shutil.copy(best[3], out)
    x, sr = load(out); D[f"{part}_{sid}_{idx}"] = dict(dur=len(x) / sr)
    changes[(part, sid, idx)] = best[4]
    print(f"P{part}-{sid}.{idx} {spk}: CER={best[1]:.2f} text='{best[4]}' -> {best[2]}", flush=True)
json.dump(D, open(dj, "w"), indent=1)
json.dump({f"{k[0]}_{k[1]}_{k[2]}": v for k, v in changes.items()}, open(os.path.join(HERE, "vo/retake_texts.json"), "w"), ensure_ascii=False, indent=1)
