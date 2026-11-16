import sys, os, subprocess, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, "/tmp/claude-0/-home-user-Code/15234d1e-2166-55a3-99cd-98630da7c6b2/scratchpad/tools")
import timeline
from lines import L
from voicelab import asr_fr, cer, load
OUT = "/home/user/Code/le-compteur/v4"
for p in (1, 2, 3):
    wav = os.path.join(HERE, f"chunks/final_p{p}.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", f"{OUT}/LE_COMPTEUR_partie_{p}.mp4", "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
    x, sr = load(wav)
    sh, tempo = timeline.get(p)
    cs = []
    for s, (sid, a0, a1, lines) in zip(sh, L[p]):
        for ln, (off, spk, tts, sub, kw) in zip(s['lines'], lines):
            a = s['t0'] + ln['start'] - 0.05; b = a + ln['dur'] + 0.15
            seg = x[int(a * sr):int(b * sr)]
            h = asr_fr(seg); c = cer(tts, h); cs.append(c)
            if c > 0.15: print(f"  P{p}-{sid} {spk}: CER={c:.2f} | {tts} -> {h}")
    print(f"PART {p}: lines={len(cs)} mean CER={np.mean(cs):.3f} max={np.max(cs):.2f}", flush=True)
