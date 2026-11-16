import sys, os, wave, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from scipy.signal import lfilter, butter
import timeline
from timeline import T
SR = 44100; N = int(timeline.DUR * SR)
def set_part(part):
    global N
    N = int(timeline.DURS[part] * SR)
rng = np.random.default_rng(0)
def tt(d): return np.arange(int(d * SR)) / SR
def env(n, a=0.005, r=0.2):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    nr = min(n, int(r * SR)); e[-nr:] *= np.linspace(1, 0, nr); return e
def lp(x, fc, o=2): b, a = butter(o, fc / (SR / 2)); return lfilter(b, a, x)
def hp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), 'high'); return lfilter(b, a, x)
def saw(f, t): return 2 * ((f * t) % 1) - 1

# ---- sfx ----
def sfx(name):
    if name == 'tick':
        t = tt(0.03); return 0.35 * np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 180)
    if name == 'pop':
        t = tt(0.12); f = 500 + 900 * np.exp(-t * 40); return 0.4 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 30)
    if name == 'cash':
        t = tt(0.9)
        ding = (np.sin(2 * np.pi * 1318 * t) + 0.6 * np.sin(2 * np.pi * 2637 * t) + 0.3 * np.sin(2 * np.pi * 1975 * t)) * np.exp(-t * 5)
        rat = hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 25) * 0.5
        return 0.35 * (ding + rat)
    if name in ('bass', 'bass_soft'):
        t = tt(1.8); f = 70 * np.exp(-t * 0.8) + 30
        x = np.tanh(2.5 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t * 2.2) * env(len(t), 0.004, 0.3)
        return x * (0.9 if name == 'bass' else 0.5)
    if name == 'boom':
        t = tt(2.5); f = 90 * np.exp(-t * 3) + 28
        x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.5)
        n = lp(rng.standard_normal(len(t)), 800) * np.exp(-t * 4) * 0.8
        return 0.9 * np.tanh(1.8 * (x + n))
    if name == 'hit':
        t = tt(0.5); n = lp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 18)
        k = np.sin(2 * np.pi * np.cumsum(120 * np.exp(-t * 10) + 45) / SR) * np.exp(-t * 9)
        return 0.6 * (n * 0.6 + k)
    if name == 'crash':
        t = tt(1.0); n = hp(rng.standard_normal(len(t)), 1500) * np.exp(-t * 6)
        cl = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 14) for f in (523, 811, 1240, 1777))
        return 0.35 * (n + 0.4 * cl)
    if name == 'whoosh':
        t = tt(0.6); n = rng.standard_normal(len(t)); e = np.sin(np.pi * t / 0.6) ** 2
        return 0.35 * lp(n, 1800) * e
    if name == 'shimmer':
        t = tt(2.5); x = sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate((1760, 2217, 2637, 3520)))
        return 0.08 * x * np.exp(-t * 1.4) * env(len(t), 0.05, 0.4)
    if name == 'glitch':
        t = tt(0.7); x = np.sign(np.sin(2 * np.pi * (200 + 1800 * (rng.random(len(t)) > 0.97).cumsum() % 900) * t))
        gate = (np.floor(t * 28) % 3 != 0)
        return 0.18 * x * gate * env(len(t), 0.002, 0.1) + 0.1 * hp(rng.standard_normal(len(t)), 4000) * gate
    if name == 'notif':
        t = tt(0.4); return 0.25 * (np.sin(2 * np.pi * 1046 * t) * (t < 0.12) + np.sin(2 * np.pi * 1568 * t) * (t >= 0.12)) * np.exp(-(t % 0.12) * 20)
    if name == 'type':
        out = np.zeros(int(1.2 * SR))
        for i in range(12):
            s = int(i * 0.08 * SR); c = sfx('tick') * 0.8; out[s:s + len(c)] += c
        return out
    if name == 'steam':
        t = tt(3.5); return 0.06 * hp(rng.standard_normal(len(t)), 2500) * env(len(t), 0.8, 1.5)
    if name == 'door':
        t = tt(1.2); return 0.3 * lp(rng.standard_normal(len(t)), 400) * np.exp(-t * 3) + 0.2 * np.sin(2 * np.pi * 60 * t) * np.exp(-t * 4)
    if name == 'camera':
        t = tt(0.15); return 0.3 * hp(rng.standard_normal(len(t)), 2000) * np.exp(-t * 60)
    if name == 'rewind':
        t = tt(0.35); f = 300 + 2500 * t; return 0.05 * lp(saw(1, np.cumsum(f) / SR), 3000) * env(len(t), 0.02, 0.1)
    if name == 'chime':
        t = tt(2.0); return 0.18 * sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 2) for f in (880, 1320))
    if name == 'freeze':
        t = tt(0.35); return 0.35 * hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 30) + 0.25 * np.sin(2 * np.pi * 900 * t) * np.exp(-t * 25)
    if name == 'whoosh_slow':
        t = tt(1.4); n = rng.standard_normal(len(t)); e = np.sin(np.pi * t / 1.4) ** 2
        return 0.25 * lp(n, 900) * e
    if name == 'boom_soft':
        return sfx('boom') * 0.5
    if name == 'coins':
        out = np.zeros(int(2.0 * SR))
        for i in range(26):
            s0 = int(rng.random() * 1.7 * SR); t = tt(0.25); f = rng.uniform(2500, 4200)
            x = 0.12 * np.sin(2 * np.pi * f * t) * np.exp(-t * 30); out[s0:s0 + len(x)] += x
        return out
    if name == 'stamp':
        t = tt(0.3); return 0.6 * np.tanh(3 * np.sin(2 * np.pi * np.cumsum(140 * np.exp(-t * 20) + 50) / SR)) * np.exp(-t * 14) + 0.2 * lp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 40)
    if name == 'locker':
        t = tt(1.2)
        x = sum(np.sin(2 * np.pi * f * t + i) * np.exp(-t * (6 + i)) for i, f in enumerate((180, 410, 690, 1130, 1700)))
        n = lp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 25)
        return 0.45 * np.tanh(1.5 * (0.5 * x + n))
    if name == 'slam':
        t = tt(0.8); k = np.sin(2 * np.pi * np.cumsum(90 * np.exp(-t * 12) + 40) / SR) * np.exp(-t * 7)
        n = lp(rng.standard_normal(len(t)), 1200) * np.exp(-t * 30)
        return 0.8 * np.tanh(2 * (k + n))
    if name == 'phone_vibe':
        t = tt(0.9); g = ((t % 0.3) < 0.18).astype(float)
        return 0.25 * np.sign(np.sin(2 * np.pi * 150 * t)) * g * lp(np.ones(len(t)), 300) * np.exp(-t * 0.5)
    raise KeyError(name)

def riser(d):
    r = tt(d); u = r / d
    return (0.08 * lp(rng.standard_normal(len(r)), 2000) + 0.06 * np.sin(2 * np.pi * np.cumsum(200 + 600 * u ** 2) / SR)) * u ** 2

def place(buf, x, t, g=1.0):
    s = int(t * SR)
    if s >= len(buf) or s < 0: return
    e = min(len(buf), s + len(x)); buf[s:e] += g * x[:e - s]

def piano(f, d=2.5):
    t = tt(d); x = sum(np.sin(2 * np.pi * f * k * t) / k ** 1.5 * np.exp(-t * (1.5 + k)) for k in range(1, 6))
    return 0.22 * x * env(len(t), 0.003, 0.3)

def pad(dur, freqs, cut=900, amp=0.12):
    t = tt(dur); x = np.zeros(len(t))
    for f in freqs:
        for det in (-0.4, 0.4): x += saw(f + det, t)
    x = lp(x / len(freqs), cut) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.11 * t))
    return amp * x

def music(part, shots):
    m = np.zeros(N)
    st = {s['id']: s['t0'] for s in shots}
    Am = (110, 164.8, 261.6); F = (87.3, 130.8, 220); C = (130.8, 196, 329.6); G = (98, 146.8, 246.9); Em = (82.4, 123.5, 196)
    if part == 1:
        prog = [Am, F, Am, Em]
        for i in range(0, int(N / SR) + 1, 8): place(m, pad(8.5, prog[(i // 8) % 4], 700) * env(int(8.5 * SR), 1.0, 1.0), i)
        t = tt(N / SR); place(m, 0.08 * np.sin(2 * np.pi * 55 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t)), 0)
        for k in range(6):  # heartbeat in humiliation
            for base in (st['05'], st['07']):
                b = base + k * 0.85; place(m, sfx('bass_soft') * 0.3, b); place(m, sfx('bass_soft') * 0.18, b + 0.25)
        m[int(st['13'] * SR):] *= 0.3
    elif part == 2:
        prog = [Am, F, C, G]
        for i in range(0, int(N / SR) + 1, 8): place(m, pad(8.5, prog[(i // 8) % 4], 900) * env(int(8.5 * SR), 1.0, 1.0), i)
        t0, t1 = st['05'], st['11']; t = t0; bpm = 92
        m[int(st['07'] * SR):int(st['08'] * SR)] *= 0.35
        while t < t1:
            kick = sfx('bass_soft') * 0.4; place(m, kick[:int(0.3 * SR)], t)
            hat = hp(rng.standard_normal(int(0.05 * SR)), 6000) * np.exp(-tt(0.05) * 80) * 0.15
            place(m, hat, t + 30 / bpm)
            frac = (t - t0) / (t1 - t0); bpm = 92 + 70 * frac ** 1.5; t += 60 / bpm
        place(m, sfx('whoosh'), t1 - 0.5)
        m[int(st['11'] * SR):int(st['13'] * SR)] *= 0.4
        m[int(st['14'] * SR):] *= 0.3
    else:
        prog = [Am, F, Am, Em]
        T = st['04'] + 2.4
        for i in range(0, 20, 8): place(m, pad(8.5, prog[(i // 8) % 4], 800) * env(int(8.5 * SR), 1.0, 1.0), i)
        place(m, riser(T - 1.3 - st['03'] - 3.5) * 1.4, st['03'] + 3.5)
        m[int((T - 1.3) * SR):int(T * SR)] = 0  # silence before reveal
        prog2 = [C, G, Am, F]
        for k, i in enumerate(np.arange(T, st['06'], 4)): place(m, pad(4.5, prog2[k % 4], 1400, 0.11) * env(int(4.5 * SR), 0.5, 1.0), i)
        place(m, pad(st['08'] - st['06'] + 0.5, Am, 500, 0.1) * env(int((st['08'] - st['06'] + 0.5) * SR), 0.5, 0.5), st['06'])
        notes = [(Am, 220), (F, 174.6), (C, 261.6), (G, 196)]
        tp = st['08']; k = 0
        end = st['11'] + shots[-1]['dur'] - 1.4
        while tp < end:
            ch, root = notes[(k // 4) % 4]
            arp = [root, root * 1.5, root * 2, root * 1.5]
            place(m, piano(arp[k % 4]), tp); k += 1; tp += 0.5
        place(m, pad(2, (55, 82.4), 300, 0.15), end)
    m[N - int(0.4 * SR):] *= np.linspace(1, 0, int(0.4 * SR))
    return m

def load_wav(p):
    with wave.open(p) as w: return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768

def mix(part):
    set_part(part)
    shots, tempo = timeline.get(part)
    vo = np.zeros(N); fx = np.zeros(N)
    for s in shots:
        for ln in s['lines']:
            x = load_wav(ln['file'])
            if tempo > 1.001:
                import subprocess, tempfile
                with tempfile.TemporaryDirectory() as dd:
                    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", ln['file'], "-af", f"atempo={tempo:.4f}", "-ar", "44100", "-ac", "1", dd + "/t.wav"], check=True)
                    x = load_wav(dd + "/t.wav")
            rms = np.sqrt(np.mean(x[np.abs(x) > 0.01] ** 2)) if np.any(np.abs(x) > 0.01) else 0.1
            x = x * (0.16 / (rms + 1e-9))
            x = np.tanh(x * 1.2) / np.tanh(1.2)
            place(vo, x, s['t0'] + ln['start'])
        for item in s.get('sfx', []):
            if item[0] == 'stamps':
                _, t0, n = item
                for k in range(n):
                    tk = 0.4 + (s['dur'] - 0.8) * (k + 1) / 7
                    place(fx, sfx('stamp'), s['t0'] + tk); place(fx, sfx('tick'), s['t0'] + tk + 0.05)
                continue
            if isinstance(item[1], str) and item[1].startswith('notifs_fast'):
                t0 = T(s, item[0]); dur = float(item[1].split(':')[1])
                k = 0.0
                while k < dur: place(fx, sfx('notif') * 0.35, s['t0'] + t0 + k); k += max(0.06, 0.25 - k * 0.07)
                continue
            if item[0] == 'notifs':
                _, t0, n = item
                for k in range(n): place(fx, sfx('notif') * 0.6, s['t0'] + t0 + k * 0.25)
                continue
            t, name = item
            t = T(s, t)
            if ':' in name:
                kind, a = name.split(':'); a = float(a)
                if kind in ('ticks', 'ticks_accel'):
                    dur = a if a > 0 else s['dur'] + a - t
                    tk = 0.0
                    while tk < dur:
                        place(fx, sfx('tick'), s['t0'] + t + tk)
                        tk += (0.12 if kind == 'ticks' else max(0.035, 0.16 * (1 - tk / dur)))
                elif kind == 'steps':
                    tk = 0
                    while tk < a: place(fx, sfx('camera') * 0.5, s['t0'] + t + tk); tk += 0.42
                elif kind == 'riser':
                    place(fx, riser(a), s['t0'] + t)
            else:
                place(fx, sfx(name), s['t0'] + t)
    mus = music(part, shots)
    venv = np.convolve(np.abs(vo), np.ones(4410) / 4410, 'same')
    duck = 1 - 0.65 * np.clip(venv * 12, 0, 1)
    if os.environ.get('NOVO'): vo = vo * 0; duck = np.ones_like(duck)
    fxduck = 1 - 0.8 * np.clip(venv * 12, 0, 1)
    out = mus * duck * 0.9 + fx * fxduck * 0.8 + vo * 1.0
    out = np.tanh(out * 1.1) * 0.92
    st = np.stack([out, out], 1)
    with wave.open(f"chunks/p{part}_audio{os.environ.get('NOVO', '')}.wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())
    print("audio", part)

if __name__ == "__main__":
    os.makedirs("chunks", exist_ok=True)
    for p in sys.argv[1:]: mix(int(p))
