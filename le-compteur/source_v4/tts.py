import sys, os, wave, json, subprocess, tempfile, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
sys.path.insert(0, "/tmp/claude-0/-home-user-Code/15234d1e-2166-55a3-99cd-98630da7c6b2/scratchpad/tools")
from lines import L
from voicelab import K, resample, asr_fr, cer, load
VOICES = {
    'leo':    dict(dec={'ff_siwis': .4, 'bm_george': .6}, pros='bm_george', fk=0, speed=1.15),
    'maxime': dict(dec={'ff_siwis': .5, 'bm_daniel': .5}, pros='bm_daniel', fk=0, speed=1.0),
    'theo':   dict(dec={'ff_siwis': .5, 'am_michael': .5}, pros='am_michael', fk=0, speed=1.15),
    'armand': dict(dec={'ff_siwis': .5, 'bm_lewis': .5}, pros='bm_lewis', fk=0, speed=1.02),
    'pere':   dict(dec={'ff_siwis': .5, 'am_adam': .5}, pros='am_adam', fk=0, speed=1.05),
    'mere':   dict(dec={'ff_siwis': .6, 'af_heart': .4}, pros='af_heart', fk=0, speed=1.05),
    'ines':   dict(dec='ff_siwis', pros='ff_siwis', fk=0, speed=1.1),
    'samy':   dict(dec={'ff_siwis': .6, 'am_fenrir': .4}, pros='am_fenrir', fk=0, speed=1.05),
}
def mixv(spec):
    if isinstance(spec, str): return K.get_voice_style(spec)
    return sum(K.get_voice_style(n) * w for n, w in spec.items())
def style(v):
    a = mixv(v['dec']).copy(); b = mixv(v['pros']); a[..., 128:] = b[..., 128:]; return a
POLISH = ("highpass=f=70,equalizer=f=130:t=q:w=1:g=2,equalizer=f=320:t=q:w=1.2:g=-2,equalizer=f=3400:t=q:w=1.4:g=3,"
          "highshelf=f=9000:g=2,deesser=i=0.4,acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2")
def synth_line(spk, text, out):
    v = VOICES[spk]
    x, sr = K.create(text, voice=style(v), speed=v['speed'], lang='fr-fr')
    x = np.asarray(x, np.float32)
    with tempfile.TemporaryDirectory() as d:
        a = d + "/a.wav"
        with wave.open(a, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
        r = 2 ** (-v['fk'] / 12)
        fs = f"rubberband=pitch={r:.5f}:formant=shifted,rubberband=pitch={1 / r:.5f}:formant=preserved," if v['fk'] else ""
        af = fs + "aresample=44100," + POLISH + ",silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a, "-af", af, "-ac", "1", "-ar", "44100", out], check=True)
if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "vo"), exist_ok=True)
    parts = [int(p) for p in sys.argv[1:]] or [1, 2, 3]
    dj = os.path.join(HERE, "vo/durs.json"); D = json.load(open(dj)) if os.path.exists(dj) else {}
    for part in parts:
        for sid, t0, t1, lines in L[part]:
            for i, (off, spk, tts, sub, kw) in enumerate(lines):
                f = os.path.join(HERE, f"vo/p{part}_{sid}_{i}.wav")
                synth_line(spk, tts, f)
                x, sr = load(f); d = len(x) / sr
                h = asr_fr(resample(x, sr)); c = cer(tts, h)
                D[f"{part}_{sid}_{i}"] = dict(dur=d)
                flag = "  <-- CHECK" if c > 0.12 else ""
                print(f"P{part}-{sid}.{i} {spk:6s} {d:5.2f}s CER={c:.2f}{flag} | {h}", flush=True)
    json.dump(D, open(dj, "w"), indent=1)
