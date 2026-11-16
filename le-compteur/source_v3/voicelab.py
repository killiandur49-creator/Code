import sys, os, wave, json, re, unicodedata, numpy as np, sherpa_onnx
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from asr import recognizer, load
from kokoro_onnx import Kokoro
DL = "/tmp/claude-0/-home-user-Code/15234d1e-2166-55a3-99cd-98630da7c6b2/scratchpad/dl/"
K = Kokoro(DL + "kokoro/kokoro-v1.0.onnx", DL + "kokoro/voices-v1.0.bin")
def resample(x, sr, to=16000):
    import scipy.signal as ss
    from math import gcd
    g = gcd(sr, to); return ss.resample_poly(x, to // g, sr // g).astype(np.float32)
def f0_median(x, sr=16000):
    f0 = []
    for i in range(0, len(x) - 1024, 800):
        fr = x[i:i + 1024]
        if np.sqrt((fr ** 2).mean()) < 0.02: continue
        ac = np.correlate(fr, fr, 'full')[1023:]; lo, hi = sr // 400, sr // 60
        k = lo + np.argmax(ac[lo:hi])
        if ac[k] > 0.35 * ac[0]: f0.append(sr / k)
    return float(np.median(f0)) if f0 else 0.0
EX = {}
def extractor(name):
    if name not in EX:
        cfg = sherpa_onnx.SpeakerEmbeddingExtractorConfig(model=DL + "spk/" + name, num_threads=4)
        EX[name] = sherpa_onnx.SpeakerEmbeddingExtractor(cfg)
    return EX[name]
def embed(x, name, sr=16000):
    ex = extractor(name); s = ex.create_stream(); s.accept_waveform(sr, x); s.input_finished()
    e = np.array(ex.compute(s)); return e / np.linalg.norm(e)
def num_words(s):
    from num2words import num2words
    s = re.sub(r'(\d)[\s\u00a0\u202f.](?=\d{3})', r'\1', s)
    return re.sub(r'\d+', lambda m: ' ' + num2words(int(m.group()), lang='fr') + ' ', s)
def norm_txt(s):
    s = num_words(s).lower().replace('-', ' '); s = unicodedata.normalize('NFD', s); s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()
def cer(a, b):
    a, b = norm_txt(a), norm_txt(b)
    d = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev, d[0] = d[0], i
        for j, cb in enumerate(b, 1):
            cur = min(d[j] + 1, d[j - 1] + 1, prev + (ca != cb)); prev, d[j] = d[j], cur
    return d[len(b)] / max(1, len(a))
REC = None
def asr_fr(x, sr=16000):
    global REC
    if REC is None:
        Ms = "/tmp/claude-0/-home-user-Code/15234d1e-2166-55a3-99cd-98630da7c6b2/scratchpad/dl/asr/sherpa-onnx-whisper-small/"
        REC = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=Ms + "small-encoder.int8.onnx", decoder=Ms + "small-decoder.int8.onnx", tokens=Ms + "small-tokens.txt", language="fr", task="transcribe", num_threads=4)
    x = np.concatenate([np.zeros(4000, np.float32), x, np.zeros(8000, np.float32)])
    s = REC.create_stream(); s.accept_waveform(sr, x); REC.decode_stream(s); return s.result.text.strip()
def synth(text, voice, speed=1.1, lang='fr-fr'):
    v = voice
    if isinstance(voice, dict):  # blend
        v = sum(K.get_voice_style(n) * w for n, w in voice.items())
    x, sr = K.create(text, voice=v, speed=speed, lang=lang)
    return x.astype(np.float32), sr
