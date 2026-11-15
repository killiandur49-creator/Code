import math, re
from gfx import *

def wrap(ctx, s, size, maxw, mono=False):
    words = s.split(' '); lines = []; cur = ''
    for w in words:
        test = (cur + ' ' + w).strip()
        if text_w(ctx, test, size, mono) > maxw and cur: lines.append(cur); cur = w
        else: cur = test
    if cur: lines.append(cur)
    return lines

def banner(ctx, t, t0, t1, s):
    if t < t0 or t > t1: return
    u = seg(t, t0, t0 + 0.18); out = seg(t, t1 - 0.2, t1)
    lines = wrap(ctx, s, 50, 920)
    h = 70 + 62 * len(lines); y = 470
    dx = (1 - eout(u)) * -W + math.sin(t * 90) * 8 * (1 - seg(t, t0, t0 + 0.35))
    a = 1 - out
    ctx.save(); ctx.translate(dx, 0)
    rect(ctx, 0, y - h / 2 + 8, W, h, DARK, 0.5 * a)
    rect(ctx, 0, y - h / 2, W, h, RED, 0.94 * a)
    rect(ctx, 0, y - h / 2, W, 6, hexc('FF8A8A'), a)
    for i, l in enumerate(lines):
        text(ctx, l, W / 2, y - (len(lines) - 1) * 31 + i * 62, 50, WHITE, a)
    ctx.restore()

def title(ctx, t, t0, t1, s, y, size, color, backdrop):
    if t < t0 or (t1 is not None and t > t1): return
    a = seg(t, t0, t0 + 0.15) * (1 - (seg(t, t1 - 0.2, t1) if t1 else 0))
    k = 1 + 0.25 * (1 - eout(seg(t, t0, t0 + 0.25)))
    col = GOLD if color == 'gold' else WHITE
    lines = wrap(ctx, s, size, 940)
    if backdrop:
        rect(ctx, 0, 0, W, H, DARK, 0.85 * a)
    for i, l in enumerate(lines):
        yy = y - (len(lines) - 1) * size * 0.6 + i * size * 1.2
        if color == 'gold': glow(ctx, W / 2, yy, 420, GOLD, 0.12 * a)
        text(ctx, l, W / 2, yy, size, col, a, stroke=size * 0.12, scale=k)

def hud(ctx, t, h, prog):
    if h is None: return
    x, y = 44, 150
    l1 = h['l1']; m = h['money']; r = h['rank']
    m = m(t) if callable(m) else m; r = r(t) if callable(r) else r
    ms = fmt_eur2(m) if m < 1000 else fmt_eur(m)
    rs = f"{int(round(r)):,}".replace(",", " ") + " / 1 200"
    rows = [(l1, WHITE), ("MON COMPTEUR : " + ms, GOLD), ("RANG : " + rs, RED if r > 1000 else (GOLD if r <= 1 else WHITE))]
    w = max(text_w(ctx, s, 30, mono=True) for s, _ in rows) + 44
    rrect(ctx, x - 16, y - 34, w, 44 * 3 + 24, 16); rgba(ctx, DARK, 0.62); ctx.fill()
    rect(ctx, x - 16, y - 34, 6, 44 * 3 + 24, GOLD, 0.9)
    for i, (s, c) in enumerate(rows):
        text(ctx, s, x + 6, y + i * 44, 30, c, 1.0, mono=True, align='l')
    # progress bar (tension)
    rect(ctx, 0, 0, W, 10, DARK, 0.6); rect(ctx, 0, 0, W * prog, 10, GOLD, 0.95)

def word_times(start, dur, words):
    wts = []
    for w in words:
        k = len(w) + 2
        if w[-1:] in '.?!…»': k += 5
        elif w[-1:] in ',:': k += 3
        wts.append(k)
    tot = sum(wts); out = []; acc = start
    for w, k in zip(words, wts):
        out.append(acc); acc += dur * k / tot
    return out

def make_subs(shots):
    """returns list of groups: dict(t0,t1,words=[(w,ts,kw)])"""
    groups = []
    for s in shots:
        for ln in s['lines']:
            if not ln['sub']: continue
            sub = re.sub(r'(\d)\s+(?=\d{3})', '\\1\u00a0', ln['sub']); sub = re.sub(r'(\d)\s+(?=€|cm)', '\\1\u00a0', sub); words = [w for w in sub.split(' ') if w]
            words = [w for w in words]
            # merge isolated punctuation
            merged = []
            for w in words:
                if w in (':', '?', '!', '»', '€') and merged: merged[-1] += ' ' + w
                elif merged and merged[-1] == '«': merged[-1] += ' ' + w
                else: merged.append(w)
            ts = word_times(s['t0'] + ln['start'], ln['dur'], merged)
            kws = set(k.replace(' ', ' ') for k in ln['kw'])
            cur = []; cl = 0
            for w, tt in zip(merged, ts):
                cur.append((w, tt, w.replace('»', '').replace(' »', '').strip(' ') in kws or w in kws))
                cl += len(w) + 1
                if cl >= 15 or w[-1:] in '.?!…' or w.endswith('»'):
                    groups.append(cur); cur = []; cl = 0
            if cur: groups.append(cur)
            end = s['t0'] + ln['start'] + ln['dur']
            # set group windows
            groups[-1] = groups[-1]
            for g in groups:
                pass
            if groups: groups[-1].append(('__END__', end + 0.35, False))
    out = []
    for i, g in enumerate(groups):
        end = None
        if g[-1][0] == '__END__': end = g[-1][1]; g = g[:-1]
        nxt = groups[i + 1][0][1] if i + 1 < len(groups) else 1e9
        t1 = min(end if end else nxt, nxt) if end else nxt
        out.append(dict(t0=g[0][1], t1=t1, words=g))
    return out

def subs(ctx, t, groups, y=1400):
    for g in groups:
        if g['t0'] <= t < g['t1']:
            size = 92
            ws = [w for w in g['words'] if w[1] <= t + 0.02]
            full = ' '.join(w[0] for w in g['words'])
            tw = text_w(ctx, full, size)
            if tw > 960: size = size * 960 / tw; tw = 960
            x = W / 2 - tw / 2
            sp = text_w(ctx, ' ', size)
            for (w, wt, kw) in g['words']:
                ww = text_w(ctx, w, size)
                if wt <= t + 0.02:
                    k = 1 + 0.07 * (1 - eout(seg(t, wt, wt + 0.12)))
                    text(ctx, w, x + ww / 2, y, size, GOLD if kw else WHITE, 1.0, stroke=size * 0.14, scale=k)
                x += ww + sp
            return
