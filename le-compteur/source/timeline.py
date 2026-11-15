import json, re
from lines import L
import scenes
DUR = 62.0
D = json.load(open("/tmp/claude-0/-home-user-Code/15234d1e-2166-55a3-99cd-98630da7c6b2/scratchpad/work/vo/durs.json"))
FIXED = {(1, "13"), (2, "12")}

# ---- per-shot extras: fx, hud, sfx ----
H1 = dict(l1="JOUR 1 · LYCÉE", money=0, rank=1200)
H2 = dict(l1="JOUR 3", money=0, rank=1200)
H3 = dict(l1="MOIS 8 · LUNDI", money=4_700_000, rank=1)
def ramp(a, b, t0, t1, curve=None):
    from gfx import seg, ease
    return lambda t: a + (b - a) * (curve or ease)(seg(t, t0, t1))
def s209_money(t):
    from gfx import seg, ein, lerp
    ks = [(0, 25_040), (1.6, 180_000), (3.6, 600_000), (5.6, 1_000_000)]; v = ks[0][1]
    for i in range(3):
        (a0, v0), (a1, v1) = ks[i], ks[i + 1]
        if t >= a0: v = lerp(v0, v1, ein(seg(t, a0, a1)))
    return v

EXTRA = {
 (1, "01"): dict(fx=[("flash", -0.35, 0.35)], hud=None, sfx=[(0.0, "boom"), (0.05, "shimmer"), (1.4, "ticks_accel:-0.55"), (-0.35, "whoosh")]),
 (1, "02"): dict(fx=[("title", 0.0, 1.3, "6 MOIS PLUS TÔT", 760, 96, "white", True)], sfx=[(0.0, "type")] + [(1.2 + i * 0.32, "pop") for i in range(8)]),
 (1, "03"): dict(fx=[("banner", 0.2, 3.6, "RÈGLE N°1 : LE CHIFFRE NE MENT JAMAIS")], sfx=[(0.2, "hit"), (1.0, "pop")]),
 (1, "05"): dict(sfx=[(0.3, "pop"), (0.6, "pop"), (0.9, "pop"), (1.2, "pop")]),
 (1, "07"): dict(sfx=[(1.4, "whoosh"), (3.2, "crash"), (3.2, "bass"), (2.6, "bass")]),
 (1, "08"): dict(sfx=[(0.0, "bass_soft")]),
 (1, "09"): dict(fx=[("phone", 1.0, None, "21:47", "MESSAGES REÇUS : 0", None)], hud=dict(l1="JOUR 1 · 21:47"), sfx=[(1.0, "notif")]),
 (1, "11"): dict(sfx=[(0.8, "glitch"), (0.8, "bass")]),
 (1, "12"): dict(sfx=[(2.6, "bass_soft")]),
 (1, "13"): dict(fx=[("nosubs",)], hud=None, sfx=[(0.0, "hit")]),
 (2, "01"): dict(sfx=[(0.0, "steam")]),
 (2, "02"): dict(fx=[("banner", 0.05, None, "RÈGLE N°1 : UN CHIFFRE MONTRE CE QU'ILS ONT. PAS CE QU'ILS VALENT.")], sfx=[(0.05, "hit")]),
 (2, "03"): dict(fx=[("banner", 0.05, None, "RÈGLE N°2 : ACHÈTE QUAND LEUR CHIFFRE BAISSE. VENDS QUAND IL MONTE.")], sfx=[(0.05, "hit")]),
 (2, "04"): dict(fx=[("banner", 0.05, None, "RÈGLE N°3 : NE DÉVOILE JAMAIS TON CHIFFRE.")], sfx=[(0.05, "hit"), (2.5, "bass_soft")]),
 (2, "05"): dict(fx=[("title", 2.7, None, "40 € → 140 €", 520, 110, "gold", False)], hud=dict(l1="JOUR 5", money=ramp(0, 40, 1.0, 1.4)), hud2=dict(money=ramp(40, 140, 2.7, 3.2)),
                 sfx=[(0.2, "bass_soft"), (1.4, "cash"), (2.7, "cash"), (2.9, "ticks:0.4")]),
 (2, "06"): dict(hud=dict(l1="JOUR 12 · 4 H DE SOMMEIL", money=ramp(140, 3_200, 0.3, 5.5)), sfx=[(0.3, "ticks:5.0")]),
 (2, "07"): dict(hud=dict(l1="MOIS 2", money=ramp(3_200, 14_800, 0.3, 5.5)), sfx=[(0.3, "ticks:5.0")]),
 (2, "08"): dict(fx=[("title", 1.7, None, "MOIS 3 : 25 000 €", 560, 92, "gold", False)], hud=dict(l1="MOIS 3", money=ramp(14_800, 25_040, 0.2, 1.6), rank=ramp(1200, 1, 2.1, 3.4)),
                 sfx=[(0.2, "ticks:1.4"), (1.7, "boom"), (1.7, "cash"), (2.1, "ticks:1.3")]),
 (2, "09"): dict(hud=dict(l1="MOIS 4 → 5", money=s209_money, rank=1), sfx=[(0.0, "ticks_accel:5.6"), (1.6, "cash"), (3.6, "cash"), (5.6, "cash"), (5.6, "boom")]),
 (2, "10"): dict(fx=[("phone", 2.4, None, "NOTIFICATIONS", "0", None)], hud=dict(l1="MOIS 5", money=1_040_000, rank=1), sfx=[(0.0, "bass_soft")]),
 (2, "11"): dict(hud=dict(l1="MOIS 8 · DIMANCHE", money=4_700_000, rank=1), sfx=[(0.5, "riser:5")]),
 (2, "12"): dict(fx=[("nosubs",)], hud=None, sfx=[(0.0, "hit")]),
 (3, "01"): dict(sfx=[]),
 (3, "02"): dict(sfx=[(0.0, "door"), (0.8, "pop"), (1.0, "pop")]),
 (3, "03"): dict(sfx=[(0.8, "whoosh"), (3.8, "bass_soft")]),
 (3, "04"): dict(hud=dict(l1="DÉVOILÉ · VISIBLE PAR TOUS", money=4_700_000, rank=1), sfx=[(2.5, "boom"), (2.5, "shimmer"), (2.5, "crash"), (2.6, "cash")]),
 (3, "05"): dict(fx=[("title", 0.0, 1.6, "Silence.", 640, 110, "white", False)], hud=dict(l1="DÉVOILÉ · VISIBLE PAR TOUS"), sfx=[(1.8, "camera"), (2.1, "camera"), (2.3, "camera"), (3.6, "crash")]),
 (3, "06"): dict(fx=[("title", 4.0, 6.9, "Elle ne regardait que ceux qui ont de l'argent.", 560, 64, "gold", False)], hud=dict(l1="DÉVOILÉ · VISIBLE PAR TOUS"), sfx=[(4.0, "rewind"), (6.9, "rewind")]),
 (3, "07"): dict(hud=dict(l1="DÉVOILÉ · VISIBLE PAR TOUS"), sfx=[(2.0, "bass")]),
 (3, "08"): dict(fx=[("phone", 0.4, None, "NOTIFICATIONS", ramp(0, 214, 0.5, 2.2), None)], hud=dict(l1="LUNDI · 23:12"), sfx=[(0.5, "notifs:1.7")]),
 (3, "09"): dict(hud=dict(l1="LUNDI · 23:40")),
 (3, "10"): dict(hud=dict(l1="MARDI · CANTINE"), sfx=[(0.2, "steps:2.4")]),
 (3, "11"): dict(fx=[("title", -1.4, None, "Commente ARMAND pour la saison 2", 1560, 54, "gold", False), ("nosubs_after", -1.4)], hud=dict(l1="MARDI · CANTINE"),
                 sfx=[(1.0, "chime"), (-1.4, "glitch"), (-0.85, "bass")]),
}
HUDBASE = {1: H1, 2: H2, 3: H3}

def build(part, tempo=1.0):
    shots = []
    for sid, t0, t1, lines in L[part]:
        base = t1 - t0
        placed = []; prev = -1
        for i, (off, spk, tts, sub, kw) in enumerate(lines):
            d = D[f"{part}_{sid}_{i}"]["dur"] / tempo
            st = max(off, prev + 0.15) if prev > 0 else off
            placed.append(dict(start=st, dur=d, spk=spk, sub=sub, kw=kw, file=f"vo/p{part}_{sid}_{i}.wav"))
            prev = st + d
        need = (prev + 0.4) if lines else base
        if (part, sid) == (3, '11'): need += 1.4
        shots.append(dict(id=sid, base=base, need=need, lines=placed, draw=getattr(scenes, f"s{part}_{sid}")))
    for s in shots:
        s['dur'] = s['base'] if (part, s['id']) in FIXED else max(s['base'], s['need'])
    excess = sum(s['dur'] for s in shots) - DUR
    if excess > 0:
        slack = {s['id']: (0 if (part, s['id']) in FIXED else max(0.0, s['dur'] - max(s['need'], 2.6))) for s in shots}
        tot = sum(slack.values())
        if tot < excess: return None
        for s in shots: s['dur'] -= excess * slack[s['id']] / tot
    elif excess < 0:
        nonfixed = [s for s in shots if (part, s['id']) not in FIXED]
        for s in nonfixed: s['dur'] += -excess / len(nonfixed)
    t = 0.0
    for s in shots:
        s['t0'] = t; t += s['dur']; s['t1'] = t
        s.update({k: v for k, v in EXTRA.get((part, s['id']), {}).items()})
    return shots

def get(part):
    for tempo in (1.0, 1.04, 1.08, 1.12, 1.16, 1.2):
        sh = build(part, tempo)
        if sh: return sh, tempo
    raise SystemExit("cannot fit")

if __name__ == "__main__":
    for p in (1, 2, 3):
        sh, tempo = get(p)
        print("PART", p, "tempo", tempo)
        for s in sh: print(f"  {s['id']} {s['t0']:6.2f}-{s['t1']:6.2f} dur={s['dur']:.2f} base={s['base']:.1f} need={s['need']:.2f}")
