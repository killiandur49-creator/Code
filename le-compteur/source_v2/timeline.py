import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json, os
from lines import L
import scenes
DUR = 62.0
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "vo/durs.json")))
FIXED = {(1, "13"), (2, "13")}
def ramp(a, b, t0, t1):
    from gfx import seg, ease
    return lambda t: a + (b - a) * ease(seg(t, t0, t1))
def s210_money(t, d=6.0):
    from gfx import seg, ein, lerp
    ks = [(0, 25_040), (1.7, 180_000), (3.4, 600_000), (5.1, 1_000_000)]; v = ks[0][1]
    for i in range(3):
        (a0, v0), (a1, v1) = ks[i], ks[i + 1]
        if t >= a0: v = lerp(v0, v1, ein(seg(t, a0, a1)))
    return v
H1 = dict(l1="JOUR 1 · LYCÉE", money=-3400, rank=1200)
H2 = dict(l1="JOUR 3 · 7 H 10", money=-3400, rank=1200)
H3 = dict(l1="MOIS 8 · LUNDI", money=4_700_000, rank=1)
HUDBASE = {1: H1, 2: H2, 3: H3}
EXTRA = {
 (1, "01"): dict(hud=None, trans='cut', fx=[("flash", -0.3, 0.3), ("speed", -0.9, -0.3), ("chroma", 0.0, 0.25)], sfx=[(0.0, "boom"), (0.05, "shimmer"), (1.0, "ticks_accel:-0.5"), (-0.35, "whoosh")]),
 (1, "02"): dict(trans='flash', fx=[("title", 0.0, 1.25, "6 MOIS PLUS TÔT", 900, 100, "white", True), ("tag", 1.4, 4.0, "LYCÉE VICTOR-LAMBERT · 8 H 02")], sfx=[(0.0, "type")] + [(1.4 + i * 0.28, "pop") for i in range(9)]),
 (1, "03"): dict(fx=[("banner", 0.1, 3.0, "RÈGLE N°1 : LE CHIFFRE NE MENT JAMAIS"), ("tag", 2.0, None, "DETTES : LOYER · CANTINE · TÉLÉPHONE", "red"), ("chroma", 1.2, 0.3)], sfx=[(0.1, "hit"), (1.2, "glitch"), (1.25, "bass")]),
 (1, "04"): dict(fx=[("tag", 0.3, 1.7, "LA TABLE DES RICHES", "gold"), ("tag", 2.6, None, "LÉO · 1 200e SUR 1 200", "red")], sfx=[(1.7, "whoosh")]),
 (1, "05"): dict(fx=[("freeze", 0.5, 1.6, "INÈS", "La plus regardée du lycée · 12 400 €", "pink")], sfx=[(0.5, "freeze"), (0.55, "hit")]),
 (1, "06"): dict(fx=[("bars", 0.0, None)], sfx=[(0.0, "whoosh_slow")]),
 (1, "07"): dict(fx=[("freeze", 0.15, 0.95, "MAXIME", "Fils de promoteur · n°1 du lycée", "red"), ("chroma", "L1+0.9", 0.3), ("speed", "L1+0.9", "L1+1.3")], sfx=[(0.15, "freeze"), (0.2, "hit"), ("L1+0.85", "whoosh"), ("L1+1.4", "crash"), ("L1+1.4", "bass"), ("L1+0.95", "bass")]),
 (1, "08"): dict(fx=[("bars", 0.0, None)], sfx=[(0.0, "bass_soft")]),
 (1, "09"): dict(hud=dict(l1="JOUR 1 · 21 H 47"), fx=[("tag", 0.7, 2.6, "LETTRES DE RELANCE : 7", "red"), ("card", 2.9, None, "21:47", "0", "MESSAGES REÇUS")], sfx=[(0.6, "whoosh"), (2.9, "notif")]),
 (1, "10"): dict(fx=[("tag", "L1-0.4", None, "M. ARMAND · CONCIERGE")], sfx=[]),
 (1, "11"): dict(trans='glitch', fx=[("chroma", 0.4, 0.5), ("zoomcut", -1.8)], sfx=[(0.4, "glitch"), (0.4, "bass"), (-1.8, "hit")]),
 (1, "12"): dict(fx=[("speed", -0.6, None)], sfx=[(-0.6, "riser:0.6")]),
 (1, "13"): dict(hud=None, trans='flash', fx=[("nosubs",)], sfx=[(0.0, "hit")]),
 (2, "01"): dict(trans='flash', fx=[("tag", 0.2, None, "LA CHAUFFERIE · 7 H 10")], sfx=[(0.0, "steam")]),
 (2, "02"): dict(trans='zoom', fx=[("banner", 0.05, None, "RÈGLE N°1 : UN CHIFFRE MONTRE CE QU'ILS ONT. PAS CE QU'ILS VALENT.")], sfx=[(0.05, "hit")]),
 (2, "03"): dict(fx=[("banner", 0.05, None, "RÈGLE N°2 : ACHÈTE QUAND LEUR CHIFFRE BAISSE. VENDS QUAND IL MONTE.")], sfx=[(0.05, "hit"), (0.3, "ticks:0.8")]),
 (2, "04"): dict(fx=[("banner", 0.05, None, "RÈGLE N°3 : NE DÉVOILE JAMAIS TON CHIFFRE. SANS RETOUR EN ARRIÈRE.")], sfx=[(0.05, "hit"), (1.0, "bass_soft")]),
 (2, "05"): dict(fx=[("title", -0.9, None, "40 € → 140 €", 960, 120, "gold", False), ("subsy", 960)], hud=None,
                 sfx=[(0.6, "whoosh"), (1.4, "cash"), ("P45", "whoosh"), ("P45+1.3", "cash"), (-0.9, "hit"), (-0.85, "ticks:0.5")]),
 (2, "06"): dict(hud=dict(l1="JOUR 23 · 2 H 14", money=ramp(-3300, -120, 0.4, 5.0)), fx=[("tag", 0.2, 1.8, "4 H DE SOMMEIL PAR NUIT")], sfx=[("stamps", 0.4, 7)]),
 (2, "07"): dict(hud=dict(l1="MOIS 1", money=ramp(-120, 0, 0.3, 1.3)), fx=[("tag", 1.5, None, "DETTES : 0 €", "green"), ("speed", 1.3, 1.8)], sfx=[(0.3, "ticks:1.0"), (1.3, "shimmer"), (1.3, "boom_soft")]),
 (2, "08"): dict(hud=dict(l1="MOIS 2", money=ramp(0, 14_800, 0.2, 4.5)), fx=[("tag", 0.6, None, "PLACE DE LÉO · VIDE DEPUIS 3 SEMAINES")], sfx=[(0.2, "ticks:4.0")]),
 (2, "09"): dict(hud=dict(l1="MOIS 3", money=ramp(14_800, 25_040, 0.2, 1.4), rank=ramp(1200, 1, 1.9, 3.2)), fx=[("title", 1.5, None, "MOIS 3 : 25 000 €", 620, 96, "gold", False), ("speed", 1.4, 2.0), ("chroma", 1.4, 0.2)],
                 sfx=[(0.2, "ticks:1.2"), (1.45, "boom"), (1.45, "cash"), (1.9, "ticks:1.3")]),
 (2, "10"): dict(hud=dict(l1="MOIS 4 → 6", money=s210_money, rank=1), trans='zoom', fx=[("punchcuts", 0.85)], sfx=[(0.0, "ticks_accel:-0.6"), (1.7, "cash"), (3.4, "cash"), (-0.6, "cash"), (-0.6, "boom")]),
 (2, "11"): dict(hud=dict(l1="MOIS 6 · 23 H 58", money=1_040_000, rank=1), fx=[("card", -2.6, None, "NOTIFICATIONS", "0", "Aucune"), ("bars", 0, None)], sfx=[(0.0, "bass_soft")]),
 (2, "12"): dict(hud=dict(l1="MOIS 8 · DIMANCHE", money=4_700_000, rank=1), sfx=[(0.3, "riser:6")]),
 (2, "13"): dict(hud=None, trans='flash', fx=[("nosubs",)], sfx=[(0.0, "hit")]),
 (3, "01"): dict(fx=[("bars", 0, None), ("tag", 1.8, None, "DETTES DE SA MÈRE : PAYÉES ✓", "green")], sfx=[(1.8, "pop")]),
 (3, "02"): dict(trans='cut', sfx=[(0.0, "door"), (0.9, "pop"), (1.1, "pop")]),
 (3, "03"): dict(fx=[("freeze", 0.0, 0.8, "MAXIME", "Toujours n°1… pour l'instant", "red")], sfx=[(0.0, "freeze"), (0.05, "hit"), (1.4, "whoosh"), ("L1-0.2", "bass_soft")]),
 (3, "04"): dict(hud=dict(l1="DÉVOILÉ · VISIBLE PAR TOUS"), fx=[("flash", 2.4, 0.35), ("speed", 2.4, 3.6), ("chroma", 2.4, 0.5), ("bars", 1.1, 2.4)], sfx=[(1.1, "riser:1.2"), (2.4, "boom"), (2.4, "shimmer"), (2.45, "crash"), (2.5, "cash"), (2.6, "coins")]),
 (3, "05"): dict(hud=dict(l1="DÉVOILÉ · VISIBLE PAR TOUS"), trans='zoom', fx=[("title", 0.0, 1.2, "SILENCE.", 640, 120, "white", False), ("zoomcut", "P36"), ("zoomcut", "P70")], sfx=[("P36", "camera"), ("P36+0.2", "camera"), ("P36+0.35", "camera"), ("P70", "hit")]),
 (3, "06"): dict(hud=dict(l1="DÉVOILÉ · VISIBLE PAR TOUS"), sfx=[("L1+0.6", "rewind"), ("L2-0.1", "rewind")]),
 (3, "07"): dict(hud=dict(l1="DÉVOILÉ · VISIBLE PAR TOUS"), fx=[("chroma", "P60", 0.25)], sfx=[("P60", "bass")]),
 (3, "08"): dict(hud=dict(l1="LUNDI · 23 H 12"), fx=[("card", 0.2, 0.4 + 0.25 * 8, "NOTIFICATIONS", ramp(0, 214, 0.3, 2.3), "")], sfx=[("notifs", 0.4, 8)]),
 (3, "09"): dict(hud=dict(l1="LUNDI · 23 H 40")),
 (3, "10"): dict(hud=dict(l1="MARDI · CANTINE"), fx=[("tag", "L1", None, "SAMY · NOUVEL ÉLÈVE")], sfx=[(0.2, "steps:2.2")]),
 (3, "11"): dict(hud=dict(l1="MARDI · CANTINE"), fx=[("title", -1.4, None, "Commente ARMAND pour la saison 2", 1460, 56, "gold", False), ("nosubs_after", -1.4), ("chroma", -1.4, 0.4)],
                 sfx=[(0.8, "chime"), (-1.4, "glitch"), (-0.9, "bass")]),
}

def build(part, tempo=1.0):
    shots = []
    for sid, t0, t1, lines in L[part]:
        base = t1 - t0
        placed = []; prev = -1
        for i, (off, spk, tts, sub, kw) in enumerate(lines):
            d = D[f"{part}_{sid}_{i}"]["dur"] / tempo
            st = max(off, prev + 0.15) if prev > 0 else off
            placed.append(dict(start=st, dur=d, spk=spk, sub=sub, kw=kw, file=os.path.join(HERE, f"vo/p{part}_{sid}_{i}.wav")))
            prev = st + d
        need = (prev + 0.35) if lines else base
        if (part, sid) == (3, '11'): need += 1.4
        if (part, sid) == (3, '04'): need = max(need, 6.0)
        shots.append(dict(id=sid, base=base, need=need, lines=placed, draw=getattr(scenes, f"s{part}_{sid}")))
    for s in shots:
        s['dur'] = s['base'] if (part, s['id']) in FIXED else max(s['base'], s['need'])
    excess = sum(s['dur'] for s in shots) - DUR
    if excess > 0:
        slack = {s['id']: (0 if (part, s['id']) in FIXED else max(0.0, s['dur'] - max(s['need'], 2.5))) for s in shots}
        tot = sum(slack.values())
        if tot < excess: return None
        for s in shots: s['dur'] -= excess * slack[s['id']] / tot
    elif excess < 0:
        nf = [s for s in shots if (part, s['id']) not in FIXED]
        for s in nf: s['dur'] += -excess / len(nf)
    t = 0.0
    for s in shots:
        s['t0'] = t; t += s['dur']; s['t1'] = t
        s.update(EXTRA.get((part, s['id']), {}))
    return shots

def get(part):
    for tempo in (1.0, 1.04, 1.08, 1.12, 1.16, 1.2, 1.25):
        sh = build(part, tempo)
        if sh: return sh, tempo
    raise SystemExit("cannot fit")

def T(S, x):
    """resolve relative time spec within shot S"""
    if x is None: return None
    if isinstance(x, str):
        import re
        m = re.match(r'([LP])(\d+)([+-][\d.]+)?$', x)
        base = S['lines'][int(m.group(2))]['start'] if m.group(1) == 'L' else S['dur'] * int(m.group(2)) / 100
        return base + (float(m.group(3)) if m.group(3) else 0)
    return x if x >= 0 else S['dur'] + x

if __name__ == "__main__":
    for p in (1, 2, 3):
        sh, tempo = get(p); print("PART", p, "tempo", tempo)
        for s in sh: print(f"  {s['id']} {s['t0']:6.2f}-{s['t1']:6.2f} dur={s['dur']:.2f} need={s['need']:.2f}")
