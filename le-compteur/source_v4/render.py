import sys, os, subprocess, math, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import random
from gfx import *
import timeline
from timeline import T
from env import label
from scenes import card
from multiprocessing import Pool

TITLE = ["Et si tu voyais l'argent", "de tout le monde ?"]
PARTNAME = {1: "Partie 1 · Le chiffre au-dessus de nos têtes", 2: "Partie 2 · Le grind", 3: "Partie 3 · Le plus riche, le plus seul"}

def arr(surf):
    return np.ndarray((H, W, 4), np.uint8, surf.get_data(), strides=(surf.get_stride(), 4, 1))

# ------------- overlays -------------
def wrap(ctx, s, size, maxw, mono=False):
    words = s.split(' '); lines = []; cur = ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if text_w(ctx, test, size, mono) > maxw and cur: lines.append(cur); cur = w
        else: cur = test
    if cur: lines.append(cur)
    return lines

def header(ctx, part):
    y = 128
    for i, l in enumerate(TITLE):
        w = text_w(ctx, l, 50) + 40
        rrect(ctx, W / 2 - w / 2, y + i * 62 - 31, w, 62, 14); rgba(ctx, hexc('7A7A80'), 0.92); ctx.fill()
    for i, l in enumerate(TITLE): text(ctx, l, W / 2, y + i * 62, 50, WHITE)
    text(ctx, f"Partie {part}/3", W / 2, y + 135, 50, WHITE, stroke=8)

def hud(ctx, h, lt, prog):
    x, y = 46, 340
    m = h['money']; r = h['rank']
    m = m(lt) if callable(m) else m; r = r(lt) if callable(r) else r
    if m < -0.004: ms = '−' + (fmt_eur2(-m) if -m < 1000 else fmt_eur(-m)); mc = RED
    elif m < 0.005: ms = '0,00 €'; mc = WHITE
    else: ms = fmt_eur2(m) if m < 1000 else fmt_eur(m); mc = GOLD
    rs = f"{int(round(r)):,}".replace(",", " ") + " / 1 200"
    rows = [(h['l1'], WHITE), ("COMPTEUR " + ms, mc), ("RANG " + rs, RED if r > 1000 else (GOLD if r <= 1.5 else WHITE))]
    w = max(text_w(ctx, s, 27, mono=True) for s, _ in rows) + 40
    rrect(ctx, x - 16, y - 30, w, 40 * 3 + 18, 14); rgba(ctx, BLACK, 0.62); ctx.fill()
    rect(ctx, x - 16, y - 30, 6, 40 * 3 + 18, mc, 0.95)
    for i, (s, c) in enumerate(rows): text(ctx, s, x + 6, y + i * 40, 27, c, mono=True, align='l')
    rect(ctx, 0, 0, W, 9, BLACK, 0.5); rect(ctx, 0, 0, W * prog, 9, GOLD)

def banner(ctx, t, t0, t1, s):
    if t < t0 or t > t1: return
    u = seg(t, t0, t0 + 0.16); out = seg(t, t1 - 0.15, t1)
    lines = wrap(ctx, s, 48, 940)
    h = 64 + 58 * len(lines); y = 575
    dx = (1 - eout(u)) * -W + math.sin(t * 90) * 10 * (1 - seg(t, t0, t0 + 0.35))
    a = 1 - out
    ctx.save(); ctx.translate(dx, 0); ctx.rotate(-0.02)
    rect(ctx, -20, y - h / 2 + 10, W + 40, h, BLACK, 0.4 * a)
    rect(ctx, -20, y - h / 2, W + 40, h, RED, 0.96 * a); rect(ctx, -20, y - h / 2, W + 40, 6, hexc('FF9A9A'), a)
    for i, l in enumerate(lines): text(ctx, l, W / 2, y - (len(lines) - 1) * 29 + i * 58, 48, WHITE, a)
    ctx.restore()

def title(ctx, t, t0, t1, s, y, size, color, backdrop):
    if t < t0 or (t1 is not None and t > t1): return
    a = seg(t, t0, t0 + 0.12) * (1 - (seg(t, t1 - 0.15, t1) if t1 else 0))
    k = 1 + 0.35 * (1 - eout(seg(t, t0, t0 + 0.25)))
    col = GOLD if color == 'gold' else WHITE
    if backdrop: rect(ctx, 0, 0, W, H, BLACK, 0.92 * a)
    lines = wrap(ctx, s, size, 940)
    for i, l in enumerate(lines):
        yy = y - (len(lines) - 1) * size * 0.6 + i * size * 1.2
        if color == 'gold': glow(ctx, W / 2, yy, 460, GOLD, 0.18 * a)
        n = len(l); vis = l if not backdrop else l[:int(n * seg(t, t0, t0 + 0.6)) + 1]
        text(ctx, vis, W / 2, yy, size, col, a, stroke=size * 0.13, scale=k)

TAGCOL = {'red': hexc('B3262E'), 'gold': hexc('B88A1E'), 'green': hexc('2E8B4A'), None: hexc('22222A')}
def tag(ctx, t, t0, t1, s, col=None):
    if t < t0 or (t1 is not None and t > t1): return
    a = seg(t, t0, t0 + 0.12) * (1 - (seg(t, t1 - 0.12, t1) if t1 else 0))
    k = 1 + 0.25 * (1 - eout(seg(t, t0, t0 + 0.2)))
    ctx.save(); ctx.translate(W / 2, 1255); ctx.scale(k, k)
    label(ctx, s, 0, 0, 32, WHITE, TAGCOL[col], a); ctx.restore()

def freeze_card(ctx, t, t0, t1, name, desc, col):
    u = seg(t, t0, t0 + 0.18); a = 1 - seg(t, t1 - 0.12, t1)
    c = {'pink': hexc('E2709F'), 'red': hexc('C8323A'), 'blue': hexc('4F86C6')}.get(col, GOLD)
    ctx.save(); ctx.translate((1 - eout(u)) * -700, 0)
    ctx.save(); ctx.translate(70, 1150); ctx.rotate(-0.04)
    rect(ctx, -30, -70, 700, 96, c, 0.95 * a)
    text(ctx, name, 20, -22, 84, WHITE, a, align='l', stroke=8)
    rect(ctx, -30, 34, 820, 56, BLACK, 0.8 * a)
    text(ctx, desc, 0, 62, 34, WHITE, a, align='l')
    ctx.restore(); ctx.restore()

def speed_lines(ctx, t, a=1.0):
    rnd = random.Random(int(t * 30))
    for i in range(46):
        ang = rnd.random() * 6.283; r0 = rnd.uniform(380, 620); r1 = r0 + rnd.uniform(300, 900)
        ctx.move_to(540 + math.cos(ang) * r0, 960 + math.sin(ang) * r0); ctx.line_to(540 + math.cos(ang) * r1, 960 + math.sin(ang) * r1)
        ctx.set_line_width(rnd.uniform(3, 9)); rgba(ctx, WHITE, 0.55 * a); ctx.stroke()

def word_times(start, dur, words):
    wts = []
    for w in words:
        k = len(w) + 2
        if w[-1:] in '.?!…»': k += 5
        elif w[-1:] in ',:': k += 3
        wts.append(k)
    tot = sum(wts); out = []; acc = start
    for w, k in zip(words, wts): out.append(acc); acc += dur * k / tot
    return out

def make_subs(shots):
    groups = []
    for s in shots:
        for ln in s['lines']:
            if not ln['sub']: continue
            sub = re.sub(r'(\d)\s+(?=\d{3})', '\\1\u00a0', ln['sub']); sub = re.sub(r'(\d)\s+(?=€|cm)', '\\1\u00a0', sub)
            words = [w for w in sub.split(' ') if w]
            merged = []
            for w in words:
                if w in (':', '?', '!', '»', '€') and merged: merged[-1] += '\u00a0' + w
                elif merged and merged[-1] == '«': merged[-1] += '\u00a0' + w
                else: merged.append(w)
            ts = word_times(s['t0'] + ln['start'], ln['dur'], merged)
            kws = set(k.replace(' ', '\u00a0') for k in ln['kw'])
            cur = []; cl = 0; gs = []
            for w, tt in zip(merged, ts):
                core = w.replace('\u00a0»', '').replace('«\u00a0', '')
                cur.append((w, tt, core in kws or w in kws or core.rstrip('.,?!:') in {k.rstrip('.,?!:') for k in kws}))
                cl += len(w) + 1
                if cl >= 15 or w[-1:] in '.?!…' or w.endswith('»'): gs.append(cur); cur = []; cl = 0
            if cur: gs.append(cur)
            end = s['t0'] + ln['start'] + ln['dur'] + 0.3
            for i, g in enumerate(gs):
                t1 = gs[i + 1][0][1] if i + 1 < len(gs) else end
                groups.append(dict(t0=g[0][1], t1=t1, words=g))
    return groups

def subs(ctx, t, groups, y=1420):
    for g in groups:
        if g['t0'] <= t < g['t1']:
            size = 86
            full = ' '.join(w[0] for w in g['words'])
            tw = text_w(ctx, full, size)
            if tw > 980: size *= 980 / tw; tw = 980
            x = W / 2 - tw / 2; sp = text_w(ctx, ' ', size)
            for (w, wt, kw) in g['words']:
                ww = text_w(ctx, w, size)
                if wt <= t + 0.02:
                    k = 1 + 0.12 * (1 - eout(seg(t, wt, wt + 0.12)))
                    text(ctx, w, x + ww / 2, y, size, GOLD if kw else WHITE, 1.0, stroke=size * 0.16, scale=k)
                x += ww + sp
            return

def kw_times(groups):
    return [wt for g in groups for (w, wt, kw) in g['words'] if kw]

# ------------- frame -------------
def frame(surf, part, shots, groups, kwt, t):
    ctx = cairo.Context(surf)
    s = next((x for x in shots if x['t0'] <= t < x['t1']), shots[-1])
    lt = t - s['t0']; d = s['dur']
    fx = s.get('fx', [])
    def TT(x): return T(s, x)
    # freeze?
    fr = next((f for f in fx if f[0] == 'freeze' and TT(f[1]) <= lt < TT(f[2])), None)
    slt = TT(fr[1]) if fr else lt
    # camera post transform
    z = 1.0; ox = oy = 0.0
    for kt in kwt:  # punch zoom on keywords
        if 0 <= t - kt < 0.35: z += 0.045 * (1 - (t - kt) / 0.35)
    for f in fx:
        if f[0] == 'zoomcut':
            t0 = TT(f[1])
            if 0 <= lt - t0 < 0.22: z += 0.25 * (1 - eout((lt - t0) / 0.22))
        if f[0] == 'punchcuts':
            q = lt % f[1]; z += 0.12 * (1 - eout(min(1, q / 0.2)))
    if fr: z += 0.10 * eout(seg(lt, TT(fr[1]), TT(fr[1]) + 0.25))
    imp = None
    for f in fx:
        if f[0] == 'impact':
            t0 = TT(f[1])
            if 0 <= lt - t0 < 0.3: imp = lt - t0
    if imp is not None:
        z += 0.07 * (1 - imp / 0.3)
        rr = random.Random(int(t * 60))
        ox += (rr.random() - 0.5) * 50 * (1 - imp / 0.3); oy += (rr.random() - 0.5) * 50 * (1 - imp / 0.3)
    trans = s.get('trans', 'whip')
    tu = seg(lt, 0, 0.14) if s['t0'] > 0 else 1
    if trans == 'whip' and tu < 1: ox = (1 - eout(tu)) * 420
    if trans == 'zoom' and lt < 0.2: z += 0.35 * (1 - eout(lt / 0.2))
    ctx.save()
    ctx.translate(W / 2 + ox, H / 2 + oy); ctx.scale(z, z); ctx.translate(-W / 2, -H / 2)
    s['draw'](ctx, slt, d, s)
    ctx.restore()
    vignette(ctx, 0.45)
    surf.flush()
    A = None
    def getA():
        return arr(surf)
    # numpy post fx
    if fr:
        A = getA(); g = (A[..., :3].astype(np.uint16).sum(2) // 3).astype(np.uint8)
        k = 0.75
        for c in range(3): A[..., c] = (A[..., c] * (1 - k) + g * k * 0.85).astype(np.uint8)
    if trans == 'whip' and tu < 1:
        A = getA(); n = int(90 * (1 - tu)) + 1
        cs = np.cumsum(A[..., :3].astype(np.int32), axis=1)
        out = (cs[:, n:] - cs[:, :-n]) // n
        A[:, n // 2: n // 2 + out.shape[1], :3] = out.astype(np.uint8)
    for f in fx:
        if f[0] == 'chroma':
            t0 = TT(f[1])
            if t0 <= lt < t0 + f[2]:
                A = getA(); sft = int(14 * (1 - (lt - t0) / f[2])) + 2
                A[:, sft:, 2] = A[:, :-sft, 2].copy(); A[:, :-sft, 0] = A[:, sft:, 0].copy()
    if imp is not None and imp < 0.12:
        A = getA(); sft = 18
        A[:, sft:, 2] = A[:, :-sft, 2].copy(); A[:, :-sft, 0] = A[:, sft:, 0].copy()
        if imp < 0.05: A[..., :3] = 255 - A[..., :3]
    if trans == 'glitch' and lt < 0.25:
        A = getA(); rnd = np.random.default_rng(int(t * 30))
        for _ in range(8):
            y0 = rnd.integers(0, H - 80); h = rnd.integers(10, 80); sh = rnd.integers(-80, 80)
            A[y0:y0 + h, :, :3] = np.roll(A[y0:y0 + h, :, :3], sh, axis=1)
    surf.mark_dirty()
    ctx = cairo.Context(surf)
    # overlays (screen space)
    for f in fx:
        if f[0] == 'speed':
            t0 = TT(f[1]); t1 = TT(f[2]) if f[2] is not None else d
            if t0 <= lt < t1: speed_lines(ctx, t, 1 - seg(lt, t1 - 0.2, t1))
        if f[0] == 'bars':
            t0 = TT(f[1]); t1 = TT(f[2]) if f[2] is not None else d + 1
            if t0 <= lt < t1:
                k = eout(seg(lt, t0, t0 + 0.3)) * (1 - seg(lt, t1 - 0.2, t1)); bh = 170 * k
                rect(ctx, 0, 0, W, bh, BLACK); rect(ctx, 0, H - bh, W, bh, BLACK)
    if part and s.get('hud', 'base') is not None:
        hh = dict(timeline.HUDBASE[part]); h = s.get('hud', 'base')
        if h != 'base': hh.update(h)
        if 'hud_money' in s: hh['money'] = s.pop('hud_money')
        hud(ctx, hh, lt, t / timeline.DURS[part])
    header(ctx, part)
    nosubs = False
    for f in fx:
        k = f[0]
        if k == 'banner': banner(ctx, lt, TT(f[1]), TT(f[2]) if f[2] is not None else d - 0.05, f[3])
        elif k == 'title': title(ctx, lt, TT(f[1]), TT(f[2]), f[3], f[4], f[5], f[6], f[7])
        elif k == 'tag': tag(ctx, lt, TT(f[1]), TT(f[2]), f[3], f[4] if len(f) > 4 else None)
        elif k == 'freeze' and fr is f: freeze_card(ctx, lt, TT(f[1]), TT(f[2]), f[3], f[4], f[5])
        elif k == 'card':
            t0 = TT(f[1]); t1 = TT(f[2]) if f[2] is not None else d + 1
            if t0 <= lt < t1:
                big = f[4]; big = str(int(round(big(lt)))) if callable(big) else big
                card(ctx, W / 2, 720, f[3], big, f[5], seg(lt, t0, t0 + 0.2) * (1 - seg(lt, t1 - 0.15, t1)), col=RED if big == '0' else WHITE)
        elif k == 'flash':
            t0 = TT(f[1])
            neg = isinstance(f[1], (int, float)) and f[1] < 0
            if t0 <= lt: rect(ctx, 0, 0, W, H, WHITE, seg(lt, t0, t0 + f[2]) if neg else 1 - seg(lt, t0, t0 + f[2]))
        elif k == 'nosubs': nosubs = True
        elif k == 'nosubs_after' and lt >= TT(f[1]): nosubs = True
    if fr and lt - TT(fr[1]) < 0.08: rect(ctx, 0, 0, W, H, WHITE, 0.8)
    if imp is not None and 0.05 <= imp < 0.14: rect(ctx, 0, 0, W, H, WHITE, 0.55 * (1 - (imp - 0.05) / 0.09))
    sy = next((f[1] for f in fx if f[0] == 'subsy'), 1420)
    if not nosubs: subs(ctx, t, groups, sy)
    if s['t0'] > 0 and trans == 'flash' and lt < 0.15: rect(ctx, 0, 0, W, H, WHITE, 1 - lt / 0.15)

def setup(part):
    shots, tempo = timeline.get(part); groups = make_subs(shots); return shots, groups, kw_times(groups)

def render_chunk(args):
    part, f0, f1, out = args
    shots, groups, kwt = setup(part)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        frame(surf, part, shots, groups, kwt, fi / FPS)
        surf.flush(); p.stdin.write(bytes(surf.get_data()))
    p.stdin.close(); p.wait(); return out

def still(part, t, out, setup_=None):
    shots, groups, kwt = setup_ or setup(part)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); frame(surf, part, shots, groups, kwt, t); surf.write_to_png(out)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "stills":
        part = int(sys.argv[2]); st = setup(part)
        os.makedirs("stills", exist_ok=True)
        fr = [float(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else [0.3, 0.75]
        for s in st[0]:
            for k, f in enumerate(fr): still(part, s['t0'] + s['dur'] * f, f"stills/p{part}_{s['id']}_{k}.png", st)
    elif cmd == "at":
        part = int(sys.argv[2]); st = setup(part)
        for x in sys.argv[3].split(','): still(part, float(x), f"stills/at_p{part}_{x}.png", st)
    elif cmd == "video":
        part = int(sys.argv[2]); N = int(timeline.DURS[part] * FPS); n = 4
        os.makedirs("chunks", exist_ok=True)
        jobs = [(part, N * i // n, N * (i + 1) // n, f"chunks/p{part}_{i}.mp4") for i in range(n)]
        with Pool(n) as pool: outs = pool.map(render_chunk, jobs)
        with open(f"chunks/p{part}.txt", "w") as f:
            for o in outs: f.write(f"file '{os.path.abspath(o)}'\n")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", f"chunks/p{part}.txt", "-c", "copy", f"chunks/p{part}_video.mp4"], check=True)
        print("video done", part)
