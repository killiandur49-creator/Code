import sys, os, wave, json, subprocess, tempfile, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, "/tmp/claude-0/-home-user-Code/15234d1e-2166-55a3-99cd-98630da7c6b2/scratchpad/tools")
from lines import L
from voicelab import K, resample, asr_fr, cer, load
VCD = "/tmp/claude-0/-home-user-Code/15234d1e-2166-55a3-99cd-98630da7c6b2/scratchpad/vclab"
# speaker -> (kokoro source speed, FreeVC target reference or None for native siwis)
VOICES = {'leo': (1.12, 'bm_george'), 'maxime': (1.08, 'am_liam'), 'theo': (1.18, 'am_puck'), 'armand': (1.0, 'bm_lewis'),
          'pere': (1.05, 'am_adam'), 'mere': (1.03, 'af_sarah'), 'ines': (1.1, None), 'samy': (1.05, 'am_eric')}
POLISH = ("highpass=f=70,equalizer=f=140:t=q:w=1:g=1.5,equalizer=f=330:t=q:w=1.2:g=-1.5,equalizer=f=3300:t=q:w=1.4:g=2.5,"
          "highshelf=f=9000:g=1.5,deesser=i=0.35,acompressor=threshold=-20dB:ratio=2.5:attack=6:release=90:makeup=1.5")
VC = None
def vc():
    global VC
    if VC is None:
        import torch; torch.set_num_threads(4)
        from TTS.api import TTS
        VC = TTS("voice_conversion_models/multilingual/vctk/freevc24", progress_bar=False)
    return VC
def save(x, sr, p):
    with wave.open(p, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
def _one(spk, text, speed, tgt, out):
    x, sr = K.create(text, voice=K.get_voice_style('ff_siwis'), speed=speed, lang='fr-fr'); x = np.asarray(x, np.float32)
    with tempfile.TemporaryDirectory() as d:
        a = d + "/a.wav"; save(x, sr, a)
        if tgt:
            b = d + "/b.wav"; vc().voice_conversion_to_file(source_wav=a, target_wav=f"{VCD}/tgt_{tgt}.wav", file_path=b)
            y, s2 = load(b); y = y / (np.abs(y).max() + 1e-9) * 0.9
            base_speed = VOICES[spk][0]
            if abs(speed - base_speed) > 0.01:   # bring back to the character's nominal pace
                c = d + "/c.wav"; save(y, s2, c)
                subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", c, "-af", f"atempo={base_speed / speed:.4f}", "-ar", str(s2), b], check=True)
                y, s2 = load(b)
            a = d + "/c2.wav"; save(y, s2, a)
        af = "aresample=44100," + POLISH + ",silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a, "-af", af, "-ac", "1", "-ar", "44100", out], check=True)

def _mos(x16):
    try:
        from speechmos import dnsmos
        x16 = x16 / (np.abs(x16).max() + 1e-9) * 0.95
        return dnsmos.run(x16.astype(np.float32), sr=16000)['p808_mos']
    except Exception:
        return 3.5

def synth_line(spk, text, out, max_takes=6):
    """best-of-N: several source speeds x stochastic conversions, keep the clearest take"""
    base, tgt = VOICES[spk]
    speeds = [base, base - 0.08, base + 0.05, base - 0.12, base, base - 0.04] if tgt else [base, base - 0.06, base + 0.04]
    best = None
    with tempfile.TemporaryDirectory() as d:
        for k, sp in enumerate(speeds[:max_takes]):
            f = f"{d}/take{k}.wav"; _one(spk, text, sp, tgt, f)
            x, sr = load(f); x16 = resample(x, sr)
            h = asr_fr(x16); c = cer(text, h); m = _mos(x16)
            score = c - 0.03 * (m - 3.5)
            if best is None or score < best[0]: best = (score, c, m, h, f, k)
            if c <= 0.02 and m >= 3.8: break
        import shutil; shutil.copy(best[4], out)
    return best[1], best[3], best[5] + 1

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "vo"), exist_ok=True)
    parts = [int(p) for p in sys.argv[1:]] or [1, 2, 3]
    dj = os.path.join(HERE, "vo/durs.json"); D = json.load(open(dj)) if os.path.exists(dj) else {}
    for part in parts:
        for sid, t0, t1, lines in L[part]:
            for i, (off, spk, tts, sub, kw) in enumerate(lines):
                f = os.path.join(HERE, f"vo/p{part}_{sid}_{i}.wav")
                c, h, ntk = synth_line(spk, tts, f)
                x, sr = load(f); d = len(x) / sr
                D[f"{part}_{sid}_{i}"] = dict(dur=d)
                print(f"P{part}-{sid}.{i} {spk:6s} {d:5.2f}s CER={c:.2f} takes={ntk}{'  <-- CHECK' if c > 0.12 else ''} | {h}", flush=True)
    json.dump(D, open(dj, "w"), indent=1)
