import math, random
from gfx import *
from env import *
from char import draw_char, CHARS, extra
from fx2 import *

# ---------------------------------------------------------------- scale system
PX = 2.35            # pixels per centimetre for a character of scale 1 (170 cm ~ 400 px)
HOR = {'hall': 860, 'cafe': 780, 'court': 1000, 'class': 1000, 'kitchen': 950, 'bed': 950,
       'boil': 950, 'roof': 1000, 'street': 1000, 'bath': 950}
YREF = 1360
def ds(env, y):
    """perspective scale for something standing on the floor at screen-world y"""
    return max(0.25, (y - HOR[env]) / (YREF - HOR[env]))

def cam(ctx, z=1.0, cx=540, cy=960, sx=0, sy=0, rot=0):
    ctx.translate(W / 2 + sx, H / 2 + sy); ctx.rotate(rot); ctx.scale(z, z); ctx.translate(-cx, -cy)

def handheld(t, amp=6, seed=0):
    return (amp * (math.sin(t * 1.7 + seed) * 0.6 + math.sin(t * 3.1 + seed * 2) * 0.4),
            amp * (math.sin(t * 1.3 + seed * 3) * 0.6 + math.sin(t * 2.6 + seed) * 0.4))

def popk(t, t0, d=0.28):
    u = seg(t, t0, t0 + d)
    if u <= 0: return 0.0
    if u >= 1: return 1.0
    return eout(u) * (1 + 0.35 * math.sin(u * math.pi))

def cnt_col(s): return RED if s.startswith('−') or s.startswith('-') else (WHITE if s.startswith('0,00') else GOLD)

def C(ctx, who, x, y, s=1.0, cnt=None, ca=1.0, cpop=1.0, glitch=0.0, t=0.0, ck=None, ccol=None, sparkle=False, **kw):
    info = draw_char(ctx, who, x, y, s, **kw)
    if cnt is not None and info and cpop > 0.01:
        ss = info['s']
        cx, cy = info['top'][0], info['top'][1] - 46 * ss
        k = ck or max(0.75, min(1.3, ss))
        if sparkle: sparkles(ctx, cx, cy, 120 * k, t)
        counter(ctx, cx, cy, cnt, k=k, a=ca * kw.get('alpha', 1.0), glitch=glitch, t=t, pop=cpop, col=ccol or cnt_col(cnt))
    return info

def talk(t, on=True): return ('talk' if int(t * 9) % 2 else 'flat') if on else 'flat'
def lt_line(S, i): return S['lines'][i]['start'] if len(S['lines']) > i else 0
def lt_end(S, i): return S['lines'][i]['start'] + S['lines'][i]['dur'] if len(S['lines']) > i else 0
def speaking(S, t, i):
    if len(S['lines']) <= i: return False
    ln = S['lines'][i]; return ln['start'] <= t <= ln['start'] + ln['dur']
def anyspeak(S, t, idx): return any(speaking(S, t, i) for i in idx)

def sparkles(ctx, x, y, r, t, n=10, col=GOLD):
    rnd = random.Random(int(x * 7 + y))
    for i in range(n):
        ph = (t * 0.8 + rnd.random()) % 1
        a = rnd.random() * 6.28; rr = r * (0.5 + 0.6 * ph)
        px, py = x + math.cos(a) * rr, y + math.sin(a) * rr * 0.6 - ph * 30
        sz = 7 * math.sin(ph * math.pi)
        ctx.save(); ctx.translate(px, py); ctx.rotate(0.785)
        rgba(ctx, col, 0.9 * math.sin(ph * math.pi)); ctx.rectangle(-sz / 2, -sz / 2, sz, sz); ctx.fill(); ctx.restore()

def coins(ctx, t, t0, n=40, area=(0, 1080), seed=1, bills=False, k=1.0):
    if t < t0: return
    rnd = random.Random(seed)
    for i in range(n):
        st = t0 + rnd.random() * 1.5
        if t < st: continue
        u = t - st; x = rnd.uniform(*area) + math.sin(u * 3 + i) * 30; y = -100 + u * rnd.uniform(500, 900) + 300
        if y > 2100: continue
        ctx.save(); ctx.translate(x, y); ctx.rotate(u * rnd.uniform(-4, 4)); ctx.scale(k, k)
        if bills:
            rect(ctx, -40, -20, 80, 40, hexc('5BB08A')); rect(ctx, -32, -13, 64, 26, hexc('8FD1A8')); text(ctx, "€", 0, 0, 22, hexc('2E7A53'))
        else:
            ctx.scale(abs(math.cos(u * 6 + i)) + 0.1, 1)
            ctx.arc(0, 0, 18, 0, 6.283); rgba(ctx, GOLD); ctx.fill(); ctx.arc(0, 0, 12, 0, 6.283); rgba(ctx, hexc('D9A23B')); ctx.fill()
        ctx.restore()

# ---------------------------------------------------------------- props (real sizes)
def table(ctx, x, y, w_cm=120, s=1.0, top=hexc('E8E2D0'), leg=hexc('8A8A94'), a=1.0):
    w = w_cm * PX * s; h = 75 * PX * s; th = 5 * PX * s
    rect(ctx, x - w / 2, y - h, w, th, top, a); rect(ctx, x - w / 2, y - h + th, w, th * 0.5, mix(top, BLACK, 0.25), a)
    lw = 4 * PX * s
    rect(ctx, x - w / 2 + lw, y - h + th, lw, h - th, leg, a); rect(ctx, x + w / 2 - 2 * lw, y - h + th, lw, h - th, leg, a)
    return y - h   # table top y

def chair(ctx, x, y, f=1, s=1.0, a=1.0, col=hexc('4F86C6')):
    seat = 45 * PX * s; back = 88 * PX * s; w = 42 * PX * s; th = 4 * PX * s
    rect(ctx, x - w / 2, y - seat, w, th, col, a)
    bx = x - f * w / 2 - (th if f > 0 else 0)
    rect(ctx, bx, y - back, th, back - seat + th, col, a)
    rect(ctx, x - w / 2 + th, y - seat + th, th * 0.7, seat - th, hexc('6A6A74'), a); rect(ctx, x + w / 2 - th * 1.7, y - seat + th, th * 0.7, seat - th, hexc('6A6A74'), a)

def tray(ctx, x, y, ang=0.0, food=True, a=1.0, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s * PX * 45 / 124, s * PX * 45 / 124)
    rrect(ctx, -62, -9, 124, 18, 5); rgba(ctx, hexc('E07A3B'), a); ctx.fill()
    if food:
        rrect(ctx, -50, -26, 44, 18, 6); rgba(ctx, WHITE, a); ctx.fill(); rect(ctx, -46, -24, 36, 10, hexc('C98A4B'), a)
        ctx.arc(20, -18, 12, 3.14, 6.28); rgba(ctx, hexc('E8C07A'), a); ctx.fill(); ctx.arc(46, -16, 9, 0, 6.28); rgba(ctx, hexc('C8323A'), a); ctx.fill()
    ctx.restore()

def trash(ctx, x, y, s=1.0):
    k = s * PX * 70 / 168
    ctx.save(); ctx.translate(x, y); ctx.scale(k, k)
    ctx.move_to(-46, -140); ctx.line_to(46, -140); ctx.line_to(38, 0); ctx.line_to(-38, 0); ctx.close_path(); rgba(ctx, hexc('5A6670')); ctx.fill()
    rect(ctx, -52, -152, 104, 16, hexc('6E7C86'))
    for i in (-20, 0, 20): line(ctx, [(i, -125), (i * 0.85, -14)], 4, hexc('46525A'))
    rect(ctx, -20, -168, 26, 18, hexc('E8E2D0')); ctx.arc(20, -160, 9, 0, 6.28); rgba(ctx, hexc('9A6A3A')); ctx.fill()
    ctx.restore()
    return y - 168 * k

def flies(ctx, x, y, t, s=1.0):
    for i in range(3):
        fx = x + (math.sin(t * 7 + i * 2) * 40 + math.sin(t * 13 + i) * 10) * s; fy = y + math.cos(t * 6 + i * 3) * 25 * s
        ctx.arc(fx, fy, 3.0 * s, 0, 6.28); rgba(ctx, BLACK); ctx.fill()

def phone_obj(ctx, x, y, s=1.0, ang=0.0, glowa=0.5, screen=hexc('BFD8FF'), rec=False, t=0.0):
    k = s * PX * 16 / 84 * 1.35
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(k, k)
    if glowa: glow(ctx, 0, 0, 220, hexc('7FB2FF'), glowa)
    rrect(ctx, -24, -42, 48, 84, 9); rgba(ctx, BLACK); ctx.fill(); rrect(ctx, -19, -36, 38, 70, 5); rgba(ctx, screen); ctx.fill()
    if rec and int(t * 2) % 2 == 0:
        ctx.arc(0, -52, 7, 0, 6.28); rgba(ctx, RED); ctx.fill()
    ctx.restore()

def laptop(ctx, x, y, s=1.0, flick=0.0, chart_up=True):
    k = s * PX * 34 / 190 * 1.25
    ctx.save(); ctx.translate(x, y); ctx.scale(k, k)
    glow(ctx, 0, -80, 380, hexc('7FB2FF'), 0.38 * (1 - flick * 0.3))
    ctx.move_to(-95, 0); ctx.line_to(-75, -160); ctx.line_to(75, -160); ctx.line_to(95, 0); ctx.close_path(); rgba(ctx, hexc('3A3F55')); ctx.fill()
    ctx.move_to(-84, -8); ctx.line_to(-67, -152); ctx.line_to(67, -152); ctx.line_to(84, -8); ctx.close_path(); rgba(ctx, hexc('1C2545')); ctx.fill()
    pts = [(-60, -40), (-35, -60), (-10, -50), (15, -95), (40, -85), (60, -130)] if chart_up else [(-60, -130), (-35, -110), (-10, -115), (15, -70), (40, -80), (60, -40)]
    line(ctx, pts, 6, hexc('5BD18A') if chart_up else RED)
    rect(ctx, -115, 0, 230, 12, hexc('5A5F75'))
    ctx.restore()

def sneakers(ctx, x, y, s=1.0):
    k = s * PX * 30 / 64
    ctx.save(); ctx.translate(x, y); ctx.scale(k, k)
    for dx in (-28, 20):
        ctx.move_to(dx - 32, 0); ctx.line_to(dx - 32, -24); ctx.curve_to(dx - 10, -28, dx, -12, dx + 32, -9); ctx.line_to(dx + 34, 0); ctx.close_path()
        rgba(ctx, WHITE); ctx.fill_preserve(); ctx.set_line_width(3); rgba(ctx, BLACK); ctx.stroke(); line(ctx, [(dx - 32, -3), (dx + 34, -3)], 6, RED)
    ctx.restore()

def backpack(ctx, x, y, s=1.0, ang=0.0, open_=False):
    k = s * PX * 42 / 110
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(k, k)
    rrect(ctx, -40, -110, 80, 110, 22); rgba(ctx, hexc('3A4566')); ctx.fill()
    rrect(ctx, -30, -55, 60, 40, 10); rgba(ctx, hexc('2E3756')); ctx.fill()
    if open_: rect(ctx, -30, -118, 60, 14, hexc('F4F1E6'))
    ctx.restore()

def papers(ctx, x, y, t, t0, s=1.0, n=7, seed=3):
    if t < t0: return
    rnd = random.Random(seed); u = t - t0
    for i in range(n):
        vx = rnd.uniform(-260, 260) * s; vy = rnd.uniform(-420, -160) * s
        px = x + vx * min(u, 1.2) * 0.9; py = y + vy * u + 520 * s * u * u
        py = min(py, y + 10 * s)
        ctx.save(); ctx.translate(px, py); ctx.rotate(u * rnd.uniform(-5, 5) if py < y else rnd.uniform(-0.5, 0.5)); ctx.scale(s * PX * 21 / 50, s * PX * 21 / 50)
        rect(ctx, -25, -35, 50, 70, hexc('F4F1E6'));
        for kk in range(4): rect(ctx, -18, -24 + kk * 12, 36 - kk * 6, 3, hexc('9A9A9A'))
        ctx.restore()

def letters_pile(ctx, x, y, n=7, stamps=0, s=1.0, t=0.0):
    rnd = random.Random(11)
    for i in range(n):
        ox = (rnd.random() - 0.5) * 70 * s; oy = -i * 4 * s; ang = (rnd.random() - 0.5) * 0.5
        ctx.save(); ctx.translate(x + ox, y + oy); ctx.rotate(ang); ctx.scale(s * 0.75, s * 0.75)
        rect(ctx, -60, -40, 120, 80, hexc('F4F1E6')); rect(ctx, -60, -40, 120, 18, hexc('C8323A'))
        text(ctx, "RELANCE", 0, -31, 14, WHITE)
        for k in range(3): rect(ctx, -46, -10 + k * 14, 80 - k * 15, 5, hexc('9A9A9A'))
        if i < stamps:
            ctx.save(); ctx.rotate(-0.3); rrect(ctx, -52, -6, 104, 36, 5); ctx.set_line_width(4); rgba(ctx, hexc('2E9B4A')); ctx.stroke()
            text(ctx, "PAYÉ", 0, 12, 26, hexc('2E9B4A')); ctx.restore()
        ctx.restore()

def envelope(ctx, x, y, s=1.0, ang=0.0, cash=True):
    k = s * PX * 22 / 110
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(k, k)
    if cash:
        for i in range(3): rect(ctx, -46 + i * 6, -58 + i * 3, 90, 40, hexc('5BB08A')); rect(ctx, -40 + i * 6, -52 + i * 3, 78, 28, hexc('8FD1A8'))
    rect(ctx, -55, -36, 110, 72, hexc('E8DCC0')); ctx.move_to(-55, -36); ctx.line_to(0, 6); ctx.line_to(55, -36); ctx.set_line_width(3); rgba(ctx, hexc('B8A88A')); ctx.stroke()
    ctx.restore()

def mug(ctx, x, y, s=1.0):
    k = s * PX * 10 / 40
    ctx.save(); ctx.translate(x, y); ctx.scale(k, k)
    rrect(ctx, -18, -40, 36, 40, 6); rgba(ctx, WHITE); ctx.fill(); ctx.set_line_width(6); rgba(ctx, WHITE); ctx.arc(22, -22, 10, -1.4, 1.4); ctx.stroke()
    ctx.restore()

def chart_card(ctx, cx, cy, up=True, t=1.0, title="", a=1.0, w=360, h=240):
    if a <= 0: return
    ctx.save(); ctx.translate(cx, cy); ctx.scale(0.85 + 0.15 * eout(a), 0.85 + 0.15 * eout(a))
    rrect(ctx, -w / 2, -h / 2 + 8, w, h, 22); rgba(ctx, BLACK, 0.4 * a); ctx.fill()
    rrect(ctx, -w / 2, -h / 2, w, h, 22); rgba(ctx, hexc('11162A'), 0.96 * a); ctx.fill()
    if title: text(ctx, title, 0, -h / 2 + 34, 30, RED if not up else hexc('5BD18A'), a)
    col = hexc('5BD18A') if up else RED
    rnd = random.Random(5 if up else 6); n = 14; pts = []
    for i in range(n):
        u = i / (n - 1); base = u if up else 1 - u
        v = clamp(base * 0.8 + 0.1 + (rnd.random() - 0.5) * 0.18)
        pts.append((-w / 2 + 24 + u * (w - 48), h / 2 - 22 - v * (h - 90)))
    kk = max(2, int(n * clamp(t)))
    line(ctx, pts[:kk], 7, col, a); ctx.arc(pts[kk - 1][0], pts[kk - 1][1], 9, 0, 6.28); rgba(ctx, col, a); ctx.fill()
    ctx.restore()

def card(ctx, cx, cy, top, big, sub=None, a=1.0, col=None):
    if a <= 0: return
    w, h = 620, 320; k = 0.85 + 0.15 * eout(a)
    ctx.save(); ctx.translate(cx, cy); ctx.scale(k, k)
    rrect(ctx, -w / 2, -h / 2 + 10, w, h, 40); rgba(ctx, BLACK, 0.4 * a); ctx.fill()
    rrect(ctx, -w / 2, -h / 2, w, h, 40); rgba(ctx, hexc('F4F6FB'), 0.97 * a); ctx.fill()
    rect(ctx, -w / 2 + 40, -h / 2 + 90, w - 80, 3, hexc('D0D4E0'), a)
    text(ctx, top, 0, -h / 2 + 50, 34, hexc('5A6080'), a, mono=True)
    text(ctx, big, 0, 40, 92 if len(big) < 12 else 64, col or hexc('1A1E33'), a)
    if sub: text(ctx, sub, 0, 120, 30, hexc('5A6080'), a)
    ctx.restore()

def bubble(ctx, x, y, s, a=1.0, k=1.0):
    if a <= 0: return
    w = text_w(ctx, s, 30) + 44
    ctx.save(); ctx.translate(x, y); ctx.scale(k, k)
    rrect(ctx, -w / 2, -32, w, 64, 30); rgba(ctx, hexc('4F86C6'), a); ctx.fill()
    text(ctx, s, 0, 0, 30, WHITE, a); ctx.restore()

def impact_lines(ctx, x, y, t, t0, r=160, col=WHITE):
    u = seg(t, t0, t0 + 0.35)
    if u <= 0 or u >= 1: return
    for i in range(12):
        a = i * 0.5236 + 0.2
        r0 = r * (0.4 + 0.5 * u); r1 = r0 + r * 0.6 * (1 - u)
        line(ctx, [(x + math.cos(a) * r0, y + math.sin(a) * r0), (x + math.cos(a) * r1, y + math.sin(a) * r1)], 7 * (1 - u) + 1, col, 1 - u)

def ring_light(ctx, x, y, s=1.0):
    r = 22 * PX * s
    glow(ctx, x, y, r * 3.0, hexc('FFF6E0'), 0.55)
    ctx.set_line_width(5 * PX * s * 0.6); rgba(ctx, hexc('FFF9EC')); ctx.arc(x, y, r, 0, 6.283); ctx.stroke()
    line(ctx, [(x, y + r), (x, y + 160 * PX * s * 0.6)], 3 * PX * s * 0.5, hexc('3A3F4B'))

def flicker(t, seed=0): return 1 if random.Random(int(t * 20) + seed).random() > 0.15 else 0.55

def vote(ctx, t, q, opts, foot):
    vgrad(ctx, 0, 0, W, H, hexc('0B1020'), hexc('1A1030'))
    glow(ctx, 540, 900, 700, GOLD, 0.18 + 0.05 * math.sin(t * 5))
    a = seg(t, 0, 0.2)
    lines = q if isinstance(q, list) else [q]
    for i, l in enumerate(lines):
        text(ctx, l, 540, 620 + i * 100, 80, WHITE, a, stroke=8, scale=lerp(1.25, 1, eout(seg(t, 0, 0.3))))
    oy = 620 + len(lines) * 100 + 110
    for i, o in enumerate(opts):
        k = popk(t, 0.2 + i * 0.12)
        if k <= 0: continue
        ctx.save(); ctx.translate(540, oy + i * 170); ctx.scale(k, k)
        rrect(ctx, -360, -56, 720, 124, 62); rgba(ctx, BLACK, 0.4); ctx.fill()
        rrect(ctx, -360, -62, 720, 124, 62); rgba(ctx, [GOLD, WHITE][i % 2]); ctx.fill()
        text(ctx, o, 0, 0, 56, hexc('1A1E33')); ctx.restore()
    for i, f in enumerate(foot):
        text(ctx, f, 540, oy + len(opts) * 170 + 40 + i * 70, 44, [GOLD, hexc('BFD0FF')][i % 2], seg(t, 0.5, 0.8), stroke=5)

def phone_screen(ctx, t, draw_content, a=1.0, views=None, likes=None):
    """full-screen phone UI (social video)"""
    pw, ph = 760, 1360; x0, y0 = (W - pw) / 2, 330
    rrect(ctx, x0 - 18, y0 - 18, pw + 36, ph + 36, 70); rgba(ctx, hexc('111118'), a); ctx.fill()
    ctx.save(); rrect(ctx, x0, y0, pw, ph, 56); ctx.clip()
    rgba(ctx, BLACK); ctx.paint()
    ctx.save(); ctx.translate(x0, y0); ctx.scale(pw / W, ph / H * 1.0); draw_content(ctx); ctx.restore()
    vgrad(ctx, x0, y0 + ph - 420, pw, 420, hexc('000000', 0.0), hexc('000000', 0.75))
    if views is not None:
        text(ctx, f"▶ {views}", x0 + 40, y0 + 60, 34, WHITE, a, align='l')
    if likes is not None:
        for i, (ic, val) in enumerate((("♥", likes), ("✎", int(likes / 7)), ("↗", int(likes / 15)))):
            yy = y0 + 520 + i * 150
            text(ctx, ic, x0 + pw - 70, yy, 60, WHITE if i else hexc('FF4D6D'), a)
            text(ctx, f"{val}", x0 + pw - 70, yy + 56, 26, WHITE, a)
    ctx.restore()

MSGS = ["T'es dispo ?", "On se voit ce soir ?", "Prête-moi 50 €", "Frérot ❤", "T'as un compte où ?", "C'est vrai ?!", "Tu m'invites ?", "On était potes non ?"]
HATE = ["ptdr le clochard", "même son sweat est fauché", "MDRRRR", "il mange à côté de la poubelle", "le SDF du lycée", "Maxime le goat"]

# ================================================================ PART 1
def s1_01(ctx, t, d, S):
    ctx.save()
    z = lerp(3.3, 3.7, ease(t / d))
    cam(ctx, z, 540, 1400)
    bg(ctx, 'cafe8', env_cafe, sigma=8)
    rect(ctx, -400, -300, 2000, 2600, BLACK, 0.4)
    god_rays(ctx, 640, 1150, 0.35, 700, 30, n=5, col=GOLD, a=0.25, t=t)
    turn = ease(seg(t, 0.8, 2.0))
    C(ctx, 'ines', 540, 1720, 1.0, face=lerp(-0.9, 0.0, turn), eyes='wide' if turn > 0.6 else 'smug', mouth='o' if t > 2.4 else 'flat',
      gaze=(lerp(-0.6, 0, turn), 0), rim=mix(GOLD, WHITE, 0.4), shadow=False)
    ctx.restore()
    p = ein(seg(t, 1.0, d - 0.5)); v = lerp(-3400, 1_000_000, p)
    s = ('−' + (fmt_eur2(-v) if -v < 1000 else fmt_eur(-v))) if v < -0.004 else (fmt_eur2(v) if v < 1000 else fmt_eur(v))
    if t > 0.9:
        sparkles(ctx, 540, 560, 260, t, 16, GOLD if v >= 0 else RED)
        counter(ctx, 540, 560, s, k=1.9, col=GOLD if v >= 0 else RED, pop=popk(t, 0.9) * (1 + 0.04 * math.sin(t * 60) * (0 < p < 1)))
        text(ctx, "MON COMPTEUR", 540, 470, 34, WHITE, seg(t, 0.9, 1.2), mono=True, stroke=6)
    if p >= 1: lens_flare(ctx, 760, 560, t, a=1 - seg(t, d - 0.3, d))

def s1_02(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.0, 1.12, ease(t / d)), lerp(520, 560, t / d), 1110)
    bg(ctx, 'court', env_court, sigma=2)
    god_rays(ctx, 900, 200, 0.45, 1500, 50, n=6, col=hexc('FFF2C8'), a=0.16, t=t)
    vals = ['340 €', '1 250 €', '85 €', '4 900 €', '−12 €', '760 €', '2 300 €', '18 900 €', '610 €']
    ppl = [(-60, 1300, 1), (150, 1320, -1), (330, 1380, 1), (760, 1310, -1), (930, 1360, -1), (1150, 1300, 1), (40, 1460, 1), (1020, 1470, -1), (640, 1290, 1)]
    l0 = lt_line(S, 0)
    order = sorted(range(len(ppl)), key=lambda i: ppl[i][1])
    for j, i in enumerate(order):
        x, y, f = ppl[i]; s = ds('court', y)
        C(ctx, extra(i), x + f * t * 40 * s, y, s, cnt=vals[i], cpop=popk(t, l0 + 0.4 + j * 0.28), t=t, face=f * 0.7, walk=t * 5.5 + i,
          eyes='happy' if i % 3 == 0 else 'normal', mouth=['smile', 'flat', 'grin'][i % 3])
    s = ds('court', 1490)
    C(ctx, 'leo', 545, 1490, s, face=0, eyes='normal', mouth='flat', gaze=(0.5 * math.sin(t * 1.3), -0.6), lean=0.3)
    dust(ctx, 0, 300, 1080, 1100, t, n=30)
    ctx.restore()

def s1_03(ctx, t, d, S):
    c1 = lt_line(S, 1) - 0.05; c2 = lt_line(S, 2) - 0.05
    ctx.save()
    if t < c1:
        y = 1400; s = ds('hall', y)
        cam(ctx, lerp(1.45, 1.6, t / c1), 560, 1110)
        bg(ctx, 'hall', env_hall, sigma=3)
        info = C(ctx, 'crypto', 560, y, s, face=0.2, arms='phone', eyes='smug', mouth='smirk', cnt='−1 250 €', cpop=popk(t, 1.2), t=t)
        phone_obj(ctx, info['hand'][0] + 4, info['hand'][1] - 14, s, 0.15, glowa=0.2, screen=hexc('3A1A22'))
        ctx.restore(); ctx.save()
        chart_card(ctx, 790, 760, up=False, t=0.3 + 0.7 * seg(t, 0.2, 1.4), title="CRYPTO  −87 %", a=seg(t, 0.15, 0.4))
    elif t < c2:
        u = t - c1; y = 1420; s = ds('court', y)
        cam(ctx, lerp(1.25, 1.38, u / (c2 - c1)), 540, 1150)
        bg(ctx, 'court4', env_court, sigma=4)
        ring_light(ctx, 790, 1010, s)
        info = C(ctx, 'influ', 520, y, s, face=0.4, arms='phone', eyes='happy', mouth='smirk' if int(t * 3) % 2 else 'smile', cnt='9 €', cpop=popk(u, 1.5), t=t)
        phone_obj(ctx, info['hand'][0] + 6, info['hand'][1] - 16, s, -0.2, glowa=0.25, screen=hexc('F7C7DA'))
        for i in range(5):
            ph = (u * 0.9 + i * 0.21) % 1
            hx, hy = 330 + i * 40 + math.sin(u * 3 + i) * 20, 1150 - ph * 380
            ctx.save(); ctx.translate(hx, hy); ctx.scale(1 - ph * 0.3, 1 - ph * 0.3)
            ctx.move_to(0, 10); ctx.curve_to(-22, -8, -10, -24, 0, -12); ctx.curve_to(10, -24, 22, -8, 0, 10)
            rgba(ctx, hexc('E2709F'), 1 - ph); ctx.fill(); ctx.restore()
    else:
        u = t - c2; y = 1430; s = ds('class', y)
        cam(ctx, lerp(1.0, 1.1, u / max(0.1, d - c2)), 560, 830)
        bg(ctx, 'classE', env_class, sigma=2.5, board="ÉPARGNEZ ! ")
        C(ctx, 'prof', 790, y, s, face=-0.5, arms='point' if int(u * 2) % 2 == 0 else 'rest', eyes='angry', mouth=talk(t, True), cnt='−2 000 €', cpop=popk(u, 2.1), t=t)
    ctx.restore()

def s1_04(ctx, t, d, S):
    u = ease(seg(t, 0.3, d * 0.55))
    ctx.save(); cam(ctx, lerp(1.25, 1.75, u), lerp(480, 700, u), lerp(1080, 1010, u))
    bg(ctx, 'hall', env_hall, sigma=3)
    y = 1380; s = ds('hall', y)
    gx0, gy0, gw, gh = 560, y - 520 * s, 300 * s, 470 * s
    rect(ctx, gx0, gy0, gw, gh, hexc('243055'), 0.82)
    ctx.save(); ctx.rectangle(gx0, gy0, gw, gh); ctx.clip()
    C(ctx, 'leo', gx0 + gw * 0.55, y - 30 * s, s, face=-0.6, eyes='sad', mouth='frown', lean=0.4, alpha=0.5, shadow=False)
    if t > lt_line(S, 1) - 0.1:
        counter(ctx, gx0 + gw * 0.55, y - 30 * s - 460 * s, '−3 400 €', k=0.95, col=RED, glitch=0.5 if t < lt_line(S, 1) + 0.4 else 0, t=t, pop=popk(t, lt_line(S, 1) - 0.1))
    for k in range(3): line(ctx, [(gx0 + 40 + k * 70, gy0), (gx0 + 150 + k * 70, gy0 + gh)], 22, WHITE, 0.06)
    ctx.restore()
    ctx.set_line_width(10 * s); rgba(ctx, hexc('8A8A94')); ctx.rectangle(gx0, gy0, gw, gh); ctx.stroke()
    C(ctx, 'leo', 380, y, s, face=0.6, eyes='sad', mouth='frown', lean=0.4, gaze=(0.6, -0.1), rim=hexc('9FB4FF'))
    ctx.restore()
    grade(ctx, hexc('2A4AA0'), 0.25)

def s1_05(ctx, t, d, S):
    l0 = lt_line(S, 0); l1 = lt_line(S, 1)
    shove = l0 + 0.55; hit = shove + 0.22
    pov = t >= l1 - 0.05
    y = 1400; s = ds('hall', y)
    ctx.save()
    if not pov:
        sx, sy = handheld(t, 5)
        shk = (22 * math.exp(-(t - hit) * 6) * math.sin(t * 80)) if t > hit else 0
        cam(ctx, lerp(1.25, 1.4, ease(t / max(0.1, l1))), 600, 1090, sx=sx + shk, sy=sy)
        bg(ctx, 'hall', env_hall, sigma=2.5)
        fl = neon_flicker(t, 3)
        if fl < 1: rect(ctx, -500, -400, 2200, 3000, BLACK, 0.35)
        # Léo trajectory
        if t < shove:
            lx = lerp(560, 470, seg(t, 0, shove)); C(ctx, 'leo', lx, y, s, face=0.5, walk=t * 4, eyes='normal', mouth='flat', lean=0.3)
            backpack(ctx, lx - 40 * s, y - 250 * s, s * 0.8)
        else:
            u = seg(t, shove, hit)
            if u < 1:
                lx = lerp(470, 250, eout(u)); C(ctx, 'leo', lx, y, s, face=0.5, arms='fall', eyes='shock', mouth='O', tilt=-0.35 * u)
            else:
                v = seg(t, hit, hit + 0.35)
                if v < 1: C(ctx, 'leo', 250, y, s, face=0.5, arms='fall', eyes='shock', mouth='O', tilt=-0.35 * (1 - v))
                else: C(ctx, 'leo', 250, y, s, face=0.6, pose='floor', arms='head', eyes='sad', mouth='frown', tears=seg(t, hit + 0.8, hit + 2))
                backpack(ctx, 140, y + 10 * s, s * 0.8, -1.2, open_=True)
                papers(ctx, 180, y, t, hit, s)
            impact_lines(ctx, 190, y - 300 * s, t, hit, r=150)
        k = seg(t, shove - 0.2, shove + 0.05) * (1 - seg(t, shove + 0.3, shove + 0.6))
        C(ctx, 'maxime', 720 - 120 * k, y + 10, ds('hall', y + 10), cnt='25 000 €', t=t, face=-0.6, arms='push' if k > 0.3 else 'hips',
          eyes='angry', mouth=talk(t, speaking(S, t, 0)) if speaking(S, t, 0) else ('laugh' if t > hit and int(t * 8) % 2 else 'smirk'), sparkle=True)
        info = C(ctx, 'theo', 930, y - 30, ds('hall', y - 30), cnt='19 400 €', t=t, face=-0.6, arms='film', eyes='happy', mouth='laugh' if t > hit else 'grin')
        phone_obj(ctx, info['hand'][0] - 6, info['hand'][1] - 16, ds('hall', y - 30), -0.1, glowa=0.15, rec=True, t=t)
        C(ctx, 'chloe', 1060, y - 60, ds('hall', y - 60), cnt='17 800 €', t=t, face=-0.6, arms='phone' if t < hit else 'head', eyes='happy', mouth='laugh' if t > hit and int(t * 7) % 2 else 'grin')
        ctx.restore()
        if t > hit: rect(ctx, 0, 0, W, H, RED, 0.10 + 0.06 * math.sin(t * 16))
    else:
        u = t - (l1 - 0.05)
        cam(ctx, lerp(1.6, 1.75, u / max(0.1, d - l1)), 420, 1150, sx=handheld(t, 9)[0], sy=handheld(t, 9)[1])
        bg(ctx, 'hall', env_hall, sigma=2.5)
        C(ctx, 'leo', 250, y, s, face=0.6, pose='floor', arms='head', eyes='sad', mouth='frown', tears=0.8)
        backpack(ctx, 140, y + 10 * s, s * 0.8, -1.2, open_=True)
        C(ctx, 'maxime', 560, y + 10, ds('hall', y + 10), face=-0.5, arms='point', eyes='happy', mouth='laugh' if int(t * 8) % 2 else 'grin')
        ctx.restore()
        rect(ctx, 0, 0, W, H, BLACK, 0.12)
        rec_overlay(ctx, t, viewers=213 + int(u * 140))

def s1_06(ctx, t, d, S):
    c = lt_line(S, 1) - 0.1
    ctx.save()
    if t < c:
        ix = lerp(-100, 640, ease(seg(t, 0, c + 1.0)))
        cam(ctx, 1.25, lerp(400, 700, ease(t / max(0.1, c))), 1090)
        bg(ctx, 'cafe', env_cafe, sigma=2.5)
        yb = 1260; sb = ds('cafe', yb)
        glow(ctx, 820, 1050, 520, GOLD, 0.35)
        table(ctx, 820, yb, 220, sb, top=hexc('E8C46A'))
        for i, (w, x, cn) in enumerate((('theo', 640, '19 400 €'), ('maxime', 820, '25 000 €'), ('chloe', 1000, '17 800 €'))):
            C(ctx, w, x, yb - 20, ds('cafe', yb - 20), cnt=cn, t=t, face=0.0 if w == 'maxime' else -0.3, eyes='smug', mouth='smile', sparkle=True)
        y = 1360; C(ctx, 'ines', ix, y, ds('cafe', y), cnt='12 400 €', t=t, face=0.6, walk=t * 5, eyes='happy' if t > 1.6 else 'normal', mouth='smile', gaze=(0.8, -0.5))
    else:
        u = t - c
        cam(ctx, 1.1, 540, 1000)
        bg(ctx, 'cafe5', env_cafe, sigma=5)
        y = 1300; s = ds('cafe', y)
        C(ctx, 'ines', lerp(1250, -250, u / max(0.1, d - c)), y, s, cnt='12 400 €', t=t, face=-0.8, walk=t * 3.0, eyes='normal', mouth='flat', gaze=(-0.9, 0))
        # Léo seated, seen from behind (over the shoulder)
        yl = 1900; sl = ds('cafe', yl)
        C(ctx, 'leo', 260, yl, sl, pose='sit', face=0.5, back=True, shadow=False)
        ctx.restore(); ctx.save()
        grade(ctx, hexc('2A4AA0'), 0.3)
    ctx.restore()

def s1_07(ctx, t, d, S):
    sw = lt_line(S, 1) + 0.5
    sh = 18 * math.exp(-(t - sw - 0.5) * 5) * math.sin(t * 70) if t > sw + 0.5 else 0
    ctx.save(); cam(ctx, lerp(0.95, 1.05, ease(t / d)) + 0.08 * seg(t, sw, sw + 0.15) * (1 - seg(t, sw + 0.6, sw + 1.2)), 560, 1230, sx=sh)
    bg(ctx, 'cafe', env_cafe, sigma=2.5)
    lau = t > sw
    yb = 1270
    for i, (who, x, cn) in enumerate((('theo', 90, '19 400 €'), (extra(2), 280, '4 900 €'), ('chloe', 860, '17 800 €'), (extra(5), 1050, '2 300 €'))):
        info = C(ctx, who, x, yb, ds('cafe', yb), cnt=cn, ca=(0.4 + 0.6 * (0.5 + 0.5 * math.sin(t * 16 + i))) if lau else 1,
                 face=0.6 if x < 540 else -0.6, arms='film' if who in ('theo', 'chloe') else ('point' if lau else 'rest'),
                 eyes='happy' if lau else 'normal', mouth='laugh' if lau and int(t * 8 + i) % 2 else ('grin' if lau else 'o'), t=t)
        if who in ('theo', 'chloe'): phone_obj(ctx, info['hand'][0], info['hand'][1] - 12, ds('cafe', yb), 0, glowa=0.1, rec=True, t=t)
    y = 1600; s = ds('cafe', y)
    top = table(ctx, 650, y, 110, s)
    trash(ctx, 900, y, s); flies(ctx, 900, y - 200 * s, t, s)
    chair(ctx, 760, y, -1, s)
    C(ctx, 'leo', 760, y, s, pose='sit', face=-0.6, eyes='wide' if t < sw else 'sad', mouth='flat' if t < sw else 'frown', gaze=(-0.5, -0.6), lean=0.4, arms='table')
    k = seg(t, sw - 0.15, sw + 0.1)
    arm = ((lerp(0.4, 1.7, k), lerp(0.9, 1.9, k)), (-0.1, -0.05))
    sm = ds('cafe', y + 20)
    C(ctx, 'maxime', 400, y + 20, sm, cnt='25 000 €', t=t, face=0.6, arms=arm, eyes='smug', mouth=talk(t, anyspeak(S, t, (0, 1))) if t < sw else ('laugh' if int(t * 8) % 2 else 'grin'), sparkle=True)
    if t < sw:
        tray(ctx, 620, top, s=s)
    else:
        u = seg(t, sw, sw + 0.7)
        tray(ctx, lerp(620, 880, u), lerp(top, y, ein(u)), u * 3, food=u < 0.4, s=s)
        if u > 0.4:
            rnd = random.Random(1)
            for i in range(7):
                v = seg(t, sw + 0.5, sw + 0.9)
                ctx.arc(880 + (rnd.random() - 0.5) * 360 * eout(v), y - 60 * math.sin(math.pi * v) * rnd.random(), 10 * s, 0, 6.28)
                rgba(ctx, [hexc('E8C07A'), hexc('C8323A'), hexc('C98A4B')][i % 3]); ctx.fill()
        impact_lines(ctx, 880, y - 40, t, sw + 0.7, r=120)
    ctx.restore()
    if t > sw: rect(ctx, 0, 0, W, H, RED, 0.10 + 0.06 * math.sin(t * 16))

def _bully_thumb(ctx):
    bg(ctx, 'hall', env_hall, sigma=2)
    y = 1400; s = ds('hall', y)
    C(ctx, 'leo', 300, y, s, face=0.6, pose='floor', arms='head', eyes='sad', mouth='frown')
    C(ctx, 'maxime', 620, y + 10, s, face=-0.5, arms='point', eyes='happy', mouth='laugh')

def s1_08(ctx, t, d, S):
    out = seg(t, d * 0.62, d * 0.62 + 0.5)
    views = int(lerp(0, 12000, ein(seg(t, 0.2, d * 0.6))))
    if out < 1:
        vgrad(ctx, 0, 0, W, H, hexc('0B1020'), hexc('1A1030'))
        ctx.save(); k = 1 + 0.6 * ein(out); ctx.translate(W / 2, H / 2); ctx.scale(1 / k, 1 / k); ctx.translate(-W / 2, -H / 2)
        def content(c):
            c.save(); cam(c, 1.2, 460, 1150); _bully_thumb(c); c.restore()
        phone_screen(ctx, t, content, views=f"{views:,}".replace(",", " "), likes=int(views / 9))
        comment_feed(ctx, t, HATE, t0=0.6, x=170, y=1500, gap=0.42)
        ctx.restore()
    if out > 0:
        a = out
        ctx.save(); ctx.push_group()
        cam(ctx, lerp(2.2, 1.6, ease(seg(t, d * 0.62, d))), 430, 1180)
        bg(ctx, 'bed', env_bedroom, sigma=2)
        yb = 1360; s = ds('bed', yb)
        bed(ctx, 40, yb, s)
        info = C(ctx, 'leo', 330, yb - 10, s, pose='sit', face=0.5, eyes='sad', mouth='frown', gaze=(0.5, 0.6), arms='phone', lean=0.5, tears=0.9, rim=hexc('7FB2FF'))
        phone_obj(ctx, info['hand'][0] + 6, info['hand'][1] - 14, s, 0.3, glowa=0.7)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(a); ctx.restore()
        spotlight(ctx, 540, 900, 420, 0.55 * a)

def s1_09(ctx, t, d, S):
    l0 = lt_line(S, 0); turn = seg(t, l0 + 2.0, l0 + 2.6)
    ctx.save(); cam(ctx, lerp(1.05, 1.18, ease(t / d)), 560, 1110)
    bg(ctx, 'kitchenN', env_kitchen, sigma=2, night=True)
    hanging_lamp(ctx, 600, 300, t, sway=0.03)
    y = 1440; s = ds('kitchen', y)
    top = table(ctx, 600, y, 140, s, top=hexc('B98A5E'), leg=hexc('6E5440'))
    letters_pile(ctx, 520, top - 6, n=7, s=s)
    chair(ctx, 720, y, -1, s)
    C(ctx, 'pere', 720, y, s, pose='sit', face=-0.5 if turn < 0.5 else -0.2, arms='head' if turn < 0.5 else 'table', eyes='tired' if turn < 0.5 else 'sad',
      mouth='frown', cnt='−8 200 €', t=t, lean=0.5)
    mx = 330
    C(ctx, 'mere', mx, y - 40, ds('kitchen', y - 40), face=-0.6 if turn < 0.5 else 0.3, arms='reach' if turn < 0.5 else 'rest',
      eyes='sad' if turn < 0.5 else 'happy', brows='sad', mouth='frown' if turn < 0.5 else 'smile', cnt='−1 900 €', t=t)
    C(ctx, 'leo', 960, y - 80, ds('kitchen', y - 80), face=-0.6, eyes='sad', mouth='flat', lean=0.3, alpha=lerp(0.0, 1.0, seg(t, 0.2, 0.6)))
    ctx.restore()
    spotlight(ctx, 560, 1000, 520, 0.45)

def s1_10(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.2, 1.3, t / d), lerp(560, 600, t / d), 1100)
    bg(ctx, 'hall', env_hall, sigma=2.5)
    god_rays(ctx, 540, 640, 0.0, 900, 40, n=5, col=hexc('FFF2C8'), a=0.18, t=t, spread=0.8)
    wv = lt_line(S, 1) - 0.2
    y = 1400; s = ds('hall', y)
    arms = 'mop' if t < wv else ((2.5, 2.9 + 0.35 * math.sin(t * 10)), (-0.1, 0.9))
    info = C(ctx, 'armand', 330, y, s, face=0.5, arms=arms, eyes='happy' if t > wv else 'normal', mouth=talk(t, speaking(S, t, 1)) if t > wv else 'smile')
    mx = 330 + 70 * s + 15 * math.sin(t * 3) * (t < wv)
    line(ctx, [(info['handB'][0], info['handB'][1]), (mx + 40 * s, y - 6)], 7 * s, hexc('B08A5A')); rrect(ctx, mx + 5 * s, y - 16 * s, 74 * s, 20 * s, 6); rgba(ctx, hexc('C9C3B0')); ctx.fill()
    lx = lerp(1150, 760, ease(seg(t, 0, 2.6)))
    C(ctx, 'leo', lx, y, s, face=-0.6, walk=t * 4.5 if t < 2.6 else None, eyes='sad' if t < wv else 'wide', mouth='flat' if t < wv + 0.3 else 'o', lean=0.45, gaze=(-0.3, 0.4 if t < wv else 0))
    dust(ctx, 0, 400, 1080, 1000, t, n=30)
    ctx.restore()

def s1_11(ctx, t, d, S):
    cut = d * 0.62
    ctx.save()
    if t < cut:
        cam(ctx, lerp(1.25, 1.4, t / cut), 540, 1040)
        bg(ctx, 'hall', env_hall, sigma=3)
        fl = flicker(t)
        rect(ctx, -500, -400, 2200, 3000, BLACK, 0.62 - 0.25 * (fl - 0.55))
        glow(ctx, 540, 620, 420, hexc('9FB4FF'), 0.25 * fl)
        y = 1560; s = ds('hall', y)
        C(ctx, 'armand', 540, y, s, face=-0.2, arms='mop', eyes='normal', mouth='flat', gaze=(-0.2, 0.5), rim=mix(hexc('9FB4FF'), WHITE, 0.3))
        counter(ctx, 540, 640, '— — —', k=1.8, glitch=1.0, t=t, pop=popk(t, 0.5))
    else:
        cam(ctx, lerp(2.6, 2.9, seg(t, cut, d)), 540, 1330)
        bg(ctx, 'hall5', env_hall, sigma=5)
        rect(ctx, -500, -400, 2200, 3000, BLACK, 0.5)
        C(ctx, 'leo', 540, 1700, 1.0, face=0, eyes='shock', mouth='O', gaze=(0, -0.4), sweat=True, rim=hexc('9FB4FF'), shadow=False)
    ctx.restore()

def s1_12(ctx, t, d, S):
    u = ease(t / d)
    ctx.save(); cam(ctx, lerp(2.6, 1.5, u), 540, 1100)          # background dolly-out
    bg(ctx, 'hall5', env_hall, sigma=5)
    rect(ctx, -500, -400, 2200, 3000, BLACK, 0.55)
    god_rays(ctx, 640, 600, 0.2, 900, 40, n=4, col=GOLD, a=0.25, t=t)
    ctx.restore()
    ctx.save(); cam(ctx, lerp(2.0, 2.25, u), 540, 1200)           # foreground push-in = vertigo
    up = ease(seg(t, 0.2, 0.9)); back = ease(seg(t, lt_line(S, 0) + 0.2, lt_line(S, 0) + 0.6))
    gz = (lerp(0, lerp(0.5, 0, back), up), lerp(0, lerp(-0.9, 0, back), up))
    C(ctx, 'armand', 540, 1560, 1.0, face=lerp(0.5, 0.0, back), eyes='wide' if back < 0.5 else 'smug', mouth=talk(t, speaking(S, t, 0)), gaze=gz,
      arms='rest', head_tilt=-0.12 * up * (1 - back), rim=mix(GOLD, WHITE, 0.3), shadow=False)
    ctx.restore()
    dust(ctx, 0, 0, 1080, 1920, t, n=40, col=GOLD, a=0.4)

def s1_13(ctx, t, d, S):
    vote(ctx, t, "Tu lui fais confiance ?", ["OUI", "NON"], ["Commente ton choix", "La partie 2 est sur mon profil"])

# ================================================================ PART 2
def _bulb(ctx, x, y, t, sway=0.06, length=420):
    ang = sway * math.sin(t * 1.3)
    ex, ey = x + math.sin(ang) * length, y + math.cos(ang) * length
    line(ctx, [(x, y), (ex, ey)], 3, hexc('2A2020'))
    glow(ctx, ex, ey, 520, hexc('FFB25A'), 0.45); glow(ctx, ex, ey, 60, hexc('FFF2C8'), 1.0)
    return ex, ey

def s2_01(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.2, 1.4, ease(t / d)), 540, 1110)
    bg(ctx, 'boil', env_boiler, sigma=2.5)
    bx, by = _bulb(ctx, 540, 380, t)
    rnd = random.Random(3)
    for i in range(10):
        ph = (t * 0.3 + rnd.random()) % 1
        glow(ctx, rnd.choice([120, 960]) + ph * 40, 640 - ph * 280, 80 + ph * 100, hexc('E8E2D0'), 0.25 * (1 - ph))
    y = 1340; s = ds('boil', y)
    C(ctx, 'armand', 380, y, s, face=0.6, arms='rest', eyes='normal', mouth=talk(t, speaking(S, t, 0)), cnt='— — —', glitch=0.3, t=t, rim=hexc('FFB25A'))
    C(ctx, 'leo', 720, y, s, face=-0.6, eyes='wide', mouth='flat', lean=0.25, rim=hexc('FFB25A'))
    ctx.restore()
    grade(ctx, hexc('FF8A3D'), 0.18)

def rule_shot(ctx, t, d, S, kind):
    ctx.save()
    if kind == 1:
        cam(ctx, lerp(1.9, 2.1, t / d), 540, 1120)
        bg(ctx, 'boil6', env_boiler, sigma=6)
        bx, by = _bulb(ctx, 600, 560, t, sway=0.12, length=260)
        u = ease(seg(t, 0, 0.5))
        C(ctx, 'armand', 540, 1520, 1.0, face=0.1, arms=((lerp(0.2, 2.75, u), lerp(0.1, 3.0, u)), (-0.1, -0.05)), eyes='smug', mouth=talk(t, speaking(S, t, 0)),
          gaze=(0.2, -0.7), rim=hexc('FFB25A'), shadow=False)
    elif kind == 2:
        cam(ctx, 1.25, 545, 1080)
        bg(ctx, 'hall', env_hall, sigma=3)
        y = 1400; s = ds('hall', y)
        dv = lerp(200, 12, ease(seg(t, 0.4, 1.6)))
        C(ctx, extra(3), 300, y, s, cnt=fmt_eur(dv), ccol=RED if dv < 60 else GOLD, t=t, face=0.3, eyes='sad', mouth='frown', sweat=True, arms='head' if dv < 60 else 'rest')
        info = C(ctx, 'chloe', 820, y, s, cnt='17 800 €', t=t, face=-0.3, eyes='happy', mouth='smile', arms='phone', sparkle=True)
        phone_obj(ctx, info['hand'][0] + 4, info['hand'][1] - 14, s, -0.15, glowa=0.15)
        C(ctx, 'leo', 560, y - 70, ds('hall', y - 70), face=0, eyes='normal', mouth='flat', gaze=(-0.8 if int(t / 1.0) % 2 == 0 else 0.8, 0))
        text(ctx, "↓", 200, 830, 90, RED, seg(t, 0.4, 0.7), stroke=8); text(ctx, "↑", 930, 830, 90, hexc('2E9B4A'), seg(t, 1.6, 1.9), stroke=8)
    else:
        cam(ctx, lerp(1.3, 1.45, t / d), 545, 1060)
        bg(ctx, 'boil', env_boiler, sigma=2.5)
        bx, by = _bulb(ctx, 560, 380, t, sway=0.1)
        y = 1340; s = ds('boil', y)
        for x in (470, 640):   # long shadows that swing with the bulb
            dxs = (x - bx) * 2.2
            ctx.move_to(x - 30 * s, y); ctx.line_to(x + 30 * s, y); ctx.line_to(x + dxs + 60, y + 260); ctx.line_to(x + dxs - 60, y + 260); ctx.close_path(); rgba(ctx, BLACK, 0.45); ctx.fill()
        C(ctx, 'leo', 640, y, s, face=-0.6, eyes='wide', mouth='flat', rim=hexc('FFB25A'))
        C(ctx, 'armand', 470, y, s, face=0.6, arms='shoulder', eyes='angry', mouth=talk(t, speaking(S, t, 0)), rim=hexc('FFB25A'))
    ctx.restore()
    if kind != 2: grade(ctx, hexc('FF8A3D'), 0.16)
def s2_02(ctx, t, d, S): rule_shot(ctx, t, d, S, 1)
def s2_03(ctx, t, d, S): rule_shot(ctx, t, d, S, 2)
def s2_04(ctx, t, d, S): rule_shot(ctx, t, d, S, 3)

def s2_05(ctx, t, d, S):
    sp = lt_line(S, 1) - 0.1
    y = 1400; s = ds('hall', y)
    if t < sp:
        ctx.save(); cam(ctx, lerp(1.35, 1.5, t / sp), 550, 1100)
        bg(ctx, 'hall', env_hall, sigma=3)
        k = ease(seg(t, 0.8, 1.7))
        C(ctx, extra(3), 400, y, s, cnt='12 €', ccol=RED, t=t, face=0.6, arms='give', eyes='sad', mouth='frown', sweat=True)
        C(ctx, 'leo', 700, y, s, face=-0.6, arms='give', eyes='normal', mouth='flat')
        sneakers(ctx, lerp(490, 610, k), y - 205 * s, s)
        ctx.restore()
        if k > 0.9:
            from env import label
            label(ctx, "ACHAT : 40 €", 550, 1250, 36, bg=hexc('C8323A'))
        return
    half = H / 2
    for part in (0, 1):
        ctx.save(); ctx.rectangle(0, part * half, W, half); ctx.clip()
        ctx.translate(0, part * half - half * 0.5)
        appear = 1.0 if part == 0 else seg(t, sp, sp + 0.25)
        ctx.translate((1 - eout(appear)) * (W if part else -W), 0)
        cam(ctx, 0.95, 540, 1010)
        bg(ctx, 'hall', env_hall, sigma=3)
        from env import label
        if part == 0:
            C(ctx, extra(3), 400, y, s, cnt='12 €', ccol=RED, t=t, face=0.6, arms='give', eyes='sad', mouth='frown')
            C(ctx, 'leo', 700, y, s, face=-0.6, arms='give', eyes='normal', mouth='flat')
            sneakers(ctx, 610, y - 205 * s, s)
            label(ctx, "ACHAT : 40 €", 540, 1455, 34, bg=hexc('C8323A'))
        else:
            k = ease(seg(t, lt_line(S, 1) + 0.4, lt_line(S, 1) + 1.2))
            C(ctx, 'leo', 400, y, s, face=0.6, arms='give', eyes='happy' if k > 0.9 else 'normal', mouth='smile')
            C(ctx, 'chloe', 700, y, s, cnt='17 800 €', t=t, face=-0.6, arms='give', eyes='happy', mouth='grin')
            sneakers(ctx, lerp(490, 610, k), y - 205 * s, s)
            label(ctx, "VENTE : 140 €", 540, 1455, 34, bg=hexc('2E9B4A'))
            if k > 0.95: coins(ctx, t, lt_line(S, 1) + 1.2, n=18, area=(200, 880), seed=4)
        ctx.restore()
    rect(ctx, 0, half - 5, W, 10, WHITE)

def s2_06(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.4, 1.6, t / d), 640, 1150)
    bg(ctx, 'bed', env_bedroom, sigma=2)
    y = 1430; s = ds('bed', y)
    top = table(ctx, 640, y, 150, s, top=hexc('5A4636'), leg=hexc('4A3A2E'))
    n_st = int(seg(t, 0.4, d - 0.4) * 7 + 0.001)
    letters_pile(ctx, 860, top - 6, n=7, stamps=n_st, s=s)
    laptop(ctx, 600, top, s, flick=random.Random(int(t * 10)).random())
    mug(ctx, 720, top, s); mug(ctx, 750, top, s)
    chair(ctx, 430, y, 1, s)
    C(ctx, 'leo', 430, y, s, pose='sit', face=0.6, arms='table', eyes='angry', mouth='flat', gaze=(0.6, 0.3), lean=0.5, rim=hexc('7FB2FF'))
    ctx.restore()
    if n_st:
        ph = (seg(t, 0.4, d - 0.4) * 7) % 1
        if ph < 0.15: rect(ctx, 0, 0, W, H, WHITE, 0.15 * (1 - ph / 0.15))

def s2_07(ctx, t, d, S):
    ln = [lt_line(S, i) for i in range(4)]
    k = 0 if t < ln[1] - 0.1 else (1 if t < ln[2] - 0.1 else (2 if t < ln[3] - 0.1 else 3))
    y = 1440; s = ds('kitchen', y)
    ctx.save()
    if k in (0, 2):
        u = t - (0 if k == 0 else ln[2] - 0.1)
        cam(ctx, lerp(1.6, 1.75, u / 2.5) if k == 0 else lerp(2.0, 2.15, u / 2.0), 520, 1080 if k == 0 else 1040, sx=handheld(t, 4)[0], sy=handheld(t, 4)[1])
        bg(ctx, 'kitchen', env_kitchen, sigma=3, night=False)
        god_rays(ctx, 940, 380, -0.5, 900, 40, n=4, col=hexc('E3F1FF'), a=0.16, t=t)
        top = table(ctx, 560, y, 140, s, top=hexc('B98A5E'), leg=hexc('6E5440'))
        letters_pile(ctx, 640, top - 6, n=7, stamps=7, s=s)
        envelope(ctx, 470, top - 4, s, 0.1)
        slam = k == 2 and t > ln[2] + 0.2
        C(ctx, 'pere', 520, y, s, face=0.4, arms='slam' if slam else 'point', eyes='angry', mouth=talk(t, speaking(S, t, k)) if speaking(S, t, k) else 'yell', cnt='−8 200 €', t=t)
        if slam: impact_lines(ctx, 600, top, t, ln[2] + 0.2, r=140)
    elif k == 1:
        u = t - (ln[1] - 0.1)
        cam(ctx, lerp(1.7, 1.85, u / 1.5), 620, 1060)
        bg(ctx, 'kitchen', env_kitchen, sigma=4, night=False)
        C(ctx, 'leo', 620, y, s, face=-0.4, eyes='angry', brows='sad', mouth=talk(t, speaking(S, t, 1)), rim=hexc('E3F1FF'))
    else:
        u = t - (ln[3] - 0.1)
        cam(ctx, lerp(1.6, 1.75, u / 2.5), 520, 1080)
        bg(ctx, 'kitchen', env_kitchen, sigma=3, night=False)
        top = table(ctx, 600, y, 140, s, top=hexc('B98A5E'), leg=hexc('6E5440'))
        ex = lerp(470, 700, ease(seg(u, 0.6, 1.3)))
        envelope(ctx, ex, top - 4, s, 0.1)
        C(ctx, 'mere', 430, y, s, face=0.4, arms='give' if u > 0.5 else 'cross', eyes='sad', mouth=talk(t, speaking(S, t, 3)), tears=seg(u, 0.4, 1.6), cnt='−1 900 €', t=t)
    ctx.restore()
    if k in (0, 2): rect(ctx, 0, 0, W, H, RED, 0.06 + 0.04 * math.sin(t * 10))

def s2_08(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.3, 1.6, ease(seg(t, 0, d * 0.7))), lerp(560, 690, ease(t / d)), 1080)
    bg(ctx, 'bed', env_bedroom, sigma=2)
    y = 1380; s = ds('bed', y)
    gx0, gy0, gw, gh = 540, y - 520 * s, 330 * s, 470 * s
    rect(ctx, gx0, gy0, gw, gh, hexc('0E1736'), 0.88)
    ctx.save(); ctx.rectangle(gx0, gy0, gw, gh); ctx.clip()
    zt = 1.3
    C(ctx, 'leo', gx0 + gw * 0.55, y - 20 * s, s, face=-0.6, eyes='happy' if t > zt + 0.4 else 'wide', mouth='smile' if t > zt + 0.4 else 'o', alpha=0.55, shadow=False)
    v = lerp(-120, 0, ease(seg(t, 0.3, zt)))
    sv = ('−' + fmt_eur2(-v)) if v < -0.004 else '0,00 €'
    cyc = y - 20 * s - 460 * s
    counter(ctx, gx0 + gw * 0.55, cyc, sv, k=1.0, col=RED if v < -0.004 else WHITE, pop=1 + 0.25 * math.sin(math.pi * seg(t, zt, zt + 0.3)))
    if t > zt: sparkles(ctx, gx0 + gw * 0.55, cyc, 160, t, 14, WHITE)
    ctx.restore()
    ctx.set_line_width(12 * s); rgba(ctx, hexc('2E3963')); ctx.rectangle(gx0, gy0, gw, gh); ctx.stroke()
    C(ctx, 'leo', 360, y, s, face=0.6, eyes='happy' if t > zt + 0.4 else 'wide', mouth='smile' if t > zt + 0.4 else 'o', gaze=(0.6, -0.1), tears=0.6 * seg(t, zt + 0.6, zt + 1.6), rim=hexc('9FB4FF'))
    ctx.restore()

def s2_09(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.35, 1.1, ease(t / d)), 540, 1080)
    bg(ctx, 'roof', env_roof, sigma=1.5)
    g = seg(t, 1.4, 1.9)
    glow(ctx, 540, 900, 300 + 500 * eout(g), GOLD, 0.5 * g)
    if g > 0: god_rays(ctx, 540, 300, 0.0, 1100, 50, n=7, col=GOLD, a=0.18 * g, t=t, spread=1.0)
    y = 1330; s = ds('roof', y)
    C(ctx, 'leo', 540, y, s, face=0, eyes='wide' if g < 1 else 'normal', mouth='o' if g < 1 else 'smile', gaze=(0, -0.3), lean=lerp(0.3, 0.0, g), rim=mix(GOLD, WHITE, 0.3))
    if g > 0: coins(ctx, t, 1.5, n=30, area=(0, 1080), seed=9)
    ph = (t % 2.0) / 0.8
    if ph < 1: glow(ctx, 560 + ph * 50, 880 - ph * 30, 25 + 45 * ph, WHITE, 0.25 * (1 - ph))
    ctx.restore()

def s2_10(ctx, t, d, S):
    c1 = d * 0.3; c2 = d * 0.7
    ctx.save()
    if t < c1:
        cam(ctx, lerp(1.0, 1.1, t / c1), 540, 1080)
        bg(ctx, 'street', env_street, sigma=2.5)
        for i, (who, x, y, cn, f) in enumerate((('adulte1', 170, 1380, '86 000 €', 0.6), ('adulte2', 520, 1450, '−14 200 €', 0.3), ('patron', 880, 1390, '41 200 000 €', -0.4))):
            C(ctx, who, x + (f * 25 * t if who != 'patron' else 0), y, ds('street', y), face=f, walk=t * 4 + i if who != 'patron' else None, eyes='smug' if who == 'patron' else 'normal',
              mouth='smirk' if who == 'patron' else 'flat', cnt=cn, ck=0.85, cpop=popk(t, 0.15 + i * 0.22), t=t, sparkle=(who == 'patron'))
    elif t < c2:
        u = t - c1
        cam(ctx, lerp(2.0, 2.3, u / (c2 - c1)), 560, 1240)
        bg(ctx, 'street5', env_street, sigma=6)
        v = 41_200_000 + 760_000 * ein(seg(u, 0.1, c2 - c1))
        info = C(ctx, 'patron', 560, 1640, 1.0, face=0.1, arms='phone', eyes='smug', mouth='smirk', cnt=fmt_eur(v) + " ↑", ck=0.75, t=t, sparkle=True, shadow=False)
        phone_obj(ctx, info['hand'][0] + 6, info['hand'][1] - 16, 1.0, 0.2, glowa=0.2)
    else:
        u = t - c2
        cam(ctx, 1.25, 600, 1130)
        bg(ctx, 'bed', env_bedroom, sigma=2)
        y = 1430; s = ds('bed', y)
        top = table(ctx, 620, y, 150, s, top=hexc('5A4636'), leg=hexc('4A3A2E'))
        laptop(ctx, 560, top, s); laptop(ctx, 760, top, s * 0.9)
        chair(ctx, 400, y, 1, s)
        C(ctx, 'leo', 400, y, s, pose='sit', face=0.6, arms='table', eyes='angry', mouth='flat', gaze=(0.6, -0.1), lean=0.4, rim=hexc('7FB2FF'))
        v = lerp(25_040, 1_000_000, ein(seg(u, 0.1, d - c2 - 0.35)))
        S['hud_money'] = v
        ctx.restore(); ctx.save()
        chart_card(ctx, 800, 1080, up=True, t=0.3 + 0.7 * seg(u, 0, d - c2 - 0.3), title="ACTIONS  +312 %", a=seg(u, 0, 0.25))
        sparkles(ctx, 540, 640, 230, t, 14)
        counter(ctx, 540, 640, fmt_eur(v), k=1.6, pop=1 + 0.04 * math.sin(t * 50))
        if u > d - c2 - 0.4: coins(ctx, t, c2 + d - c2 - 0.4, n=30, area=(0, 1080), seed=12)
    ctx.restore()

def s2_11(ctx, t, d, S):
    ln = [lt_line(S, i) for i in range(3)]
    door = ease(seg(t, 0.0, 0.25)) * (1 - ease(seg(t, d - 0.45, d - 0.2)))
    slam = t > d - 0.25
    ctx.save(); cam(ctx, lerp(1.2, 1.32, ease(t / d)), 540, 1110, sx=handheld(t, 4)[0], sy=handheld(t, 4)[1])
    bg(ctx, 'bed', env_bedroom, sigma=2)
    rect(ctx, -500, -400, 2200, 3000, BLACK, 0.45)
    y = 1430; s = ds('bed', y)
    # door on the right: light floods in
    dx0 = 760; dw = 190 * s; dh = 490 * s
    rect(ctx, dx0, y - dh, dw, dh, hexc('0A0A10'))
    if door > 0:
        rect(ctx, dx0, y - dh, dw * door, dh, hexc('FFE7B0'), 0.95)
        ctx.move_to(dx0, y); ctx.line_to(dx0 + dw * door, y); ctx.line_to(dx0 - 700 * door, y + 500); ctx.line_to(dx0 - 900 * door, y + 500); ctx.close_path()
        rgba(ctx, hexc('FFE7B0'), 0.25); ctx.fill()
        C(ctx, 'pere', dx0 + dw * 0.5, y, s, face=-0.5, arms='point' if t < ln[2] else 'slam', eyes='angry', mouth=talk(t, anyspeak(S, t, (0, 2))) if anyspeak(S, t, (0, 2)) else 'yell',
          rim=hexc('FFE7B0'), alpha=door)
    top = table(ctx, 430, y, 130, s, top=hexc('5A4636'), leg=hexc('4A3A2E'))
    lap_closed = t > ln[2] + 0.2
    if not lap_closed:
        laptop(ctx, 400, top, s); laptop(ctx, 540, top, s * 0.9)
    else:
        rect(ctx, 360, top - 8 * s, 120 * s, 10 * s, hexc('3A3F55'))
    chair(ctx, 250, y, 1, s)
    turn = seg(t, ln[1] - 0.2, ln[1])
    C(ctx, 'leo', 250, y, s, pose='sit', face=lerp(0.6, 0.2, turn), arms='table' if turn < 0.5 else 'shrug', eyes='angry' if turn > 0.5 else 'tired',
      mouth=talk(t, speaking(S, t, 1)), rim=hexc('7FB2FF'), lean=0.4)
    if lap_closed: impact_lines(ctx, 420, top, t, ln[2] + 0.2, r=120)
    ctx.restore()
    if slam: rect(ctx, 0, 0, W, H, BLACK, 0.5 * seg(t, d - 0.25, d))

def s2_12(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(2.4, 1.35, ease(seg(t, 0, d * 0.7))), lerp(390, 420, t / d), 1170)
    bg(ctx, 'bed', env_bedroom, sigma=2)
    rect(ctx, 0, 1220, 1080, 90, hexc('3A4A8A')); rect(ctx, 0, 1310, 1080, 60, hexc('2A3460'))
    rrect(ctx, 60, 1150, 200, 70, 24); rgba(ctx, hexc('DADFF0')); ctx.fill()
    ctx.save(); ctx.translate(600, 1228); ctx.rotate(-math.pi / 2)
    draw_char(ctx, 'leo', 0, 0, 1.0, face=0, eyes='tired', mouth='flat', gaze=(0.5, 0), arms=((0.3, 0.6), (-0.1, -0.05)), shadow=False)
    ctx.restore()
    ctx.save(); ctx.translate(380, 1172); ctx.rotate(-0.1)
    glow(ctx, 0, 0, 240, hexc('7FB2FF'), 0.35)
    rrect(ctx, -24, -42, 48, 84, 8); rgba(ctx, BLACK); ctx.fill(); rrect(ctx, -19, -36, 38, 70, 5); rgba(ctx, hexc('1A2450')); ctx.fill()
    ctx.save(); ctx.rotate(math.pi / 2); ctx.scale(1, -1); counter(ctx, 0, 0, '1 040 000 €', k=0.24, a=0.8); ctx.restore()
    ctx.restore()
    # parents' door, light under it, then it goes dark
    rect(ctx, 820, 760, 200, 470, hexc('141A30'))
    rect(ctx, 820, 1222, 200, 8, hexc('FFE7B0'), 0.9 * (1 - seg(t, 1.0, 1.4)))
    ctx.restore()
    spotlight(ctx, 470, 1000, 420, 0.5)

def s2_13(ctx, t, d, S):
    g = ease(seg(t, 0.4, d))
    ctx.save(); cam(ctx, lerp(1.25, 1.6, ease(t / d)), lerp(540, 660, ease(seg(t, lt_line(S, 2), d))), 1060)
    bg(ctx, 'bath', env_bath, sigma=2)
    glow(ctx, 330, 1050, 300 + 500 * g, GOLD, 0.12 + 0.35 * g)
    y = 1360; s = ds('bath', y)
    mx0, my0, mw, mh = 520, y - 560 * s, 420 * s, 520 * s
    rrect(ctx, mx0 - 20, my0 - 20, mw + 40, mh + 40, 30); rgba(ctx, hexc('8A9AA2')); ctx.fill()
    rrect(ctx, mx0, my0, mw, mh, 20); rgba(ctx, hexc('A9C7D6')); ctx.fill()
    ctx.save(); rrect(ctx, mx0, my0, mw, mh, 20); ctx.clip()
    glow(ctx, mx0 + mw * 0.5, my0 + mh * 0.5, 380, GOLD, 0.3 * g)
    C(ctx, 'leo', mx0 + mw * 0.5, y + 10 * s, s, face=-0.5, eyes='angry', mouth='flat', gaze=(-0.4, 0), lean=0, shadow=False, rim=mix(GOLD, WHITE, 0.4))
    for k in range(3): line(ctx, [(mx0 + 40 + k * 100, my0), (mx0 + 240 + k * 100, my0 + mh)], 30, WHITE, 0.08)
    ctx.restore()
    C(ctx, 'leo', 320, y, s, face=0.6, eyes='sad' if t < lt_line(S, 2) else 'angry', mouth='flat', gaze=(0.6, 0), lean=lerp(0.5, 0.0, g), rim=mix(GOLD, WHITE, 0.4))
    ctx.restore()

def s2_14(ctx, t, d, S):
    vote(ctx, t, ["Il montre son compteur", "ou il garde le secret ?"], ["LE MONTRER", "GARDER LE SECRET"], ["Commente ton choix", "La partie 3 est sur mon profil"])

# ================================================================ PART 3
def s3_01(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.3, 1.45, t / d), lerp(440, 640, t / d), 1100)
    bg(ctx, 'hall', env_hall, sigma=3)
    god_rays(ctx, 540, 700, 0.0, 1000, 50, n=6, col=GOLD, a=0.2, t=t, spread=0.9)
    rnd = random.Random(7)
    for i in range(6):
        y = 1360 + (i % 2) * 40; x0 = 1500 + i * 230 - t * 170
        C(ctx, extra(i), x0, y, ds('hall', y), cnt=f"{rnd.randint(1, 90) * 100:,}".replace(",", " ") + " €", t=t, face=-0.7, walk=t * 6 + i, eyes='normal', mouth='talk' if i % 2 else 'smile')
    y = 1420
    C(ctx, 'leo', lerp(320, 740, t / d), y, ds('hall', y), face=0.5, walk=t * 2.4, eyes='normal', mouth='flat', lean=0, rim=mix(GOLD, WHITE, 0.3))
    dust(ctx, 0, 300, 1080, 1300, t, n=40, col=GOLD, a=0.45)
    ctx.restore()

def cafe_rich(ctx, t, yb=1260, cnt=True, laugh=False):
    sb = ds('cafe', yb)
    glow(ctx, 820, 1050, 520, GOLD, 0.35)
    table(ctx, 820, yb, 220, sb, top=hexc('E8C46A'))
    for i, (w, x, c) in enumerate((('theo', 640, '19 400 €'), ('maxime', 820, '25 000 €'), ('chloe', 1000, '17 800 €'))):
        C(ctx, w, x, yb - 20, ds('cafe', yb - 20), cnt=c if cnt else None, t=t, face=0.0 if w == 'maxime' else (0.4 if i == 0 else -0.4),
          eyes='happy' if laugh else 'smug', mouth=('laugh' if laugh else ('smirk' if w == 'maxime' else 'smile')), sparkle=(w == 'maxime'))

def s3_02(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.15, 1.35, ease(t / d)), 820, 1120)
    bg(ctx, 'cafe', env_cafe, sigma=2.5)
    cafe_rich(ctx, t)
    y = 1300; C(ctx, 'ines', 1150, y, ds('cafe', y), cnt='12 400 €', t=t, face=-0.6, eyes='happy', mouth='smile')
    ctx.restore()
    o = ease(seg(t, 0.0, 0.9))
    if o < 1:
        rect(ctx, 0, 0, W / 2 * (1 - o), H, hexc('8A6A4A')); rect(ctx, W / 2 + W / 2 * o, 0, W / 2 * (1 - o), H, hexc('8A6A4A'))
        rect(ctx, W / 2 * (1 - o) - 30, 800, 14, 200, hexc('C9C3B0')); rect(ctx, W / 2 + W / 2 * o + 16, 800, 14, 200, hexc('C9C3B0'))
    glow(ctx, 540, 960, 1000, hexc('FFF2C8'), 0.7 * (1 - seg(t, 0.3, 1.5)))
    if t < 1.2: god_rays(ctx, 540, 0, 0.0, 1900, 120, n=5, col=hexc('FFF2C8'), a=0.3 * (1 - seg(t, 0.4, 1.2)), t=t, spread=0.7)

def s3_03(ctx, t, d, S):
    l1 = lt_line(S, 1); l2 = lt_line(S, 2)
    pov = l1 - 0.05 <= t < l2 - 0.1
    y = 1560; s = ds('cafe', y)
    ctx.save()
    if not pov:
        focus = ease(seg(t, l2 - 0.2, l2 + 0.3))
        cam(ctx, lerp(1.0, 1.6, focus), lerp(560, 700, focus), lerp(1220, 1180, focus), sx=handheld(t, 4)[0])
        bg(ctx, 'cafe', env_cafe, sigma=2.5)
        if focus > 0: rect(ctx, -500, -400, 2200, 3000, BLACK, 0.4 * focus)
        rect(ctx, 1150, 650, 260, 700, hexc('FFF2C8'), 0.5)
        C(ctx, 'armand', 1270, 1310, ds('cafe', 1310), face=-0.4, arms='mop', cnt='— — —', glitch=0.6, t=t, eyes='smug', mouth='flat')
        turn = ease(seg(t, 0.6, 1.3))
        for i, x in enumerate((60, 200, 940, 1080)):
            f = 1 if x < 540 else -1; yy = 1280
            C(ctx, extra(i), x, yy, ds('cafe', yy), face=f * lerp(0.0, 0.7, turn), eyes='wide' if turn > 0.5 else 'normal', mouth='o' if turn > 0.5 else 'flat', gaze=(f * turn * 0.7, 0))
        grab = seg(t, 0.4, 0.8)
        info = C(ctx, 'theo', 140, y - 40, ds('cafe', y - 40), face=0.5, arms='film', eyes='happy', mouth='laugh' if int(t * 6) % 2 else 'grin')
        phone_obj(ctx, info['hand'][0] + 4, info['hand'][1] - 14, ds('cafe', y - 40), 0, glowa=0.1, rec=True, t=t)
        C(ctx, 'maxime', 400, y, s, cnt='25 000 €', t=t, face=0.6, arms='grab' if grab > 0.5 else 'rest', eyes='smug', mouth=talk(t, speaking(S, t, 0)) if speaking(S, t, 0) else 'smirk', sparkle=True)
        C(ctx, 'leo', 640, y, s, face=-0.3 if focus < 0.5 else -0.1, eyes='normal' if focus < 0.5 else 'smug', mouth=talk(t, speaking(S, t, 2)), lean=0,
          head_tilt=0.12 * grab * (1 - focus), rim=mix(GOLD, WHITE, 0.3) if focus > 0.3 else None)
    else:
        u = t - (l1 - 0.05)
        cam(ctx, lerp(1.4, 1.55, u / 1.6), 520, 1250, sx=handheld(t, 9)[0], sy=handheld(t, 9)[1])
        bg(ctx, 'cafe', env_cafe, sigma=2.5)
        C(ctx, 'maxime', 400, y, s, face=0.6, arms='grab', eyes='happy', mouth='laugh' if int(t * 8) % 2 else 'grin')
        C(ctx, 'leo', 640, y, s, face=-0.3, eyes='normal', mouth='flat', head_tilt=0.12)
        ctx.restore(); ctx.save()
        rec_overlay(ctx, t, viewers=980 + int(u * 600))
    ctx.restore()

def s3_04(ctx, t, d, S):
    T = 2.4
    ctx.save()
    sh = (24 * math.exp(-(t - T) * 3) * math.sin(t * 70)) if t > T else 0
    zb = lerp(1.2, 1.35, ease(t / d)) - 0.15 * seg(t, T, T + 0.15) * (1 - seg(t, T + 0.4, T + 2))
    cam(ctx, zb, 560, 1150, sx=sh, sy=sh * 0.6)
    bg(ctx, 'cafe', env_cafe, sigma=2.5)
    dim = 0.6 * seg(t, 1.1, 1.5) * (1 - seg(t, T, T + 0.1))
    rect(ctx, -500, -400, 2200, 3000, BLACK, dim)
    if t > T:
        god_rays(ctx, 640, 300, 0.0, 1300, 60, n=8, col=GOLD, a=0.25 * (1 - 0.5 * seg(t, T, d)), t=t, spread=1.1)
        for j in range(3):
            u = seg(t, T + j * 0.15, T + 1.2 + j * 0.15)
            if 0 < u < 1:
                ctx.set_line_width(26 * (1 - u)); rgba(ctx, GOLD, 1 - u); ctx.arc(640, 820, 100 + 1300 * eout(u), 0, 6.283); ctx.stroke()
        glow(ctx, 640, 800, 800, GOLD, 0.6 * (1 - 0.5 * seg(t, T, d)))
    yb = 1320
    for i, x in enumerate((60, 220, 940, 1090)):
        k = seg(t, T, T + 0.35); f = 1 if x < 540 else -1
        sb = ds('cafe', yb)
        info = C(ctx, extra(i), x, yb, sb, face=f * 0.6, eyes='shock' if k > 0 else 'normal', mouth='O' if k > 0 else 'flat', arms='head' if k > 0 else 'rest', gaze=(f * 0.5, -0.6 * k))
        if k > 0: tray(ctx, x + 40 * sb, lerp(yb - 176 * sb, yb, ein(k)), 0.6 * k, food=False, s=sb)
    y = 1450; s = ds('cafe', y)
    info = C(ctx, 'theo', 160, y - 30, ds('cafe', y - 30), face=0.5, arms='film' if t < T else 'head', eyes='shock' if t > T else 'happy', mouth='O' if t > T else 'grin')
    if t < T: phone_obj(ctx, info['hand'][0] + 4, info['hand'][1] - 14, ds('cafe', y - 30), 0, glowa=0.1, rec=True, t=t)
    else:
        pu = seg(t, T, T + 0.6); phone_obj(ctx, lerp(info['hand'][0], 260, pu), lerp(info['hand'][1], y, ein(pu)), ds('cafe', y - 30), pu * 4, glowa=0.0)
    C(ctx, 'maxime', 380, y, s, cnt='25 000 €', t=t, face=0.4, eyes='shock' if t > T else 'smug', mouth='O' if t > T else 'smirk')
    r = ease(seg(t, 0.1, 1.0))
    C(ctx, 'leo', 660, y + 10, ds('cafe', y + 10), face=0, arms=((lerp(0.1, 2.85, r), lerp(0.05, 3.05, r)), (-0.1, -0.05)), eyes='smug' if t > T else 'normal', mouth='flat',
      gaze=(0, -0.2), rim=mix(GOLD, WHITE, 0.3) if t > T else None)
    if t > T:
        sparkles(ctx, 660, 840, 320, t, 22)
        counter(ctx, 660, 840, '4 700 000 €', k=1.5, pop=popk(t, T, 0.35) or 1)
        coins(ctx, t, T + 0.1, n=60, area=(-100, 1200), seed=3)
    ctx.restore()
    if t > T: lens_flare(ctx, 660, 760, t, a=1 - seg(t, T + 1.2, d))

def s3_05(ctx, t, d, S):
    l1 = lt_line(S, 1) - 0.1
    ctx.save()
    if t < l1:
        cam(ctx, lerp(2.5, 2.75, t / l1), 540, 1250)
        bg(ctx, 'cafe8', env_cafe, sigma=8)
        rect(ctx, -500, -400, 2200, 3000, BLACK, 0.25)
        C(ctx, 'maxime', 540, 1660, 1.0, face=0.2, arms='hands_up', eyes='wide', brows='sad', mouth='grin', sweat=True, cnt='25 000 €', ck=0.7, t=t, shadow=False)
    else:
        u = t - l1
        cam(ctx, lerp(2.6, 2.85, u / max(0.1, d - l1)), 540, 1250)
        bg(ctx, 'cafe8', env_cafe, sigma=8)
        rect(ctx, -500, -400, 2200, 3000, BLACK, 0.35)
        C(ctx, 'leo', 540, 1660, 1.0, face=-0.15, eyes='smug', brows='angry', mouth=talk(t, speaking(S, t, 1)), cnt='4 700 000 €', ck=0.7, t=t, rim=mix(GOLD, WHITE, 0.3), shadow=False)
    ctx.restore()
    grade(ctx, hexc('2A4AA0'), 0.18)

def s3_06(ctx, t, d, S):
    fb0 = lt_line(S, 1) + 0.6; fb1 = lt_line(S, 2) - 0.1
    fb = fb0 <= t < fb1
    ctx.save()
    y = 1440; s = ds('cafe', y)
    if not fb:
        u = ease(seg(t, 0, 2.6)) if t < 4 else 1.0
        cam(ctx, lerp(1.25, 1.45, ease(t / d)), 600, 1150)
        bg(ctx, 'cafe', env_cafe, sigma=2.5)
        C(ctx, 'leo', 780, y, s, face=-0.6, eyes='normal' if t < fb1 else 'smug', mouth=talk(t, anyspeak(S, t, (1, 2))), cnt='4 700 000 €', ck=0.8, t=t)
        C(ctx, 'ines', lerp(150, 470, u), y, s, cnt='12 400 €', t=t, face=0.6, walk=t * 4 if u < 1 else None, eyes='happy',
          mouth=talk(t, speaking(S, t, 0)) if speaking(S, t, 0) else 'grin', gaze=(0.6, -0.2))
    else:
        k = int((t - fb0) / ((fb1 - fb0) / 3)); lt = (t - fb0) % ((fb1 - fb0) / 3)
        cam(ctx, 1.15 + 0.1 * lt, 600, 1200)
        bg(ctx, 'cafe', env_cafe, sigma=2.5)
        cafe_rich(ctx, t)
        yl = 1600; sl = ds('cafe', yl)
        table(ctx, 260, yl, 110, sl, top=hexc('B8B0A0')); trash(ctx, 470, yl, sl)
        chair(ctx, 150, yl, 1, sl)
        C(ctx, 'leo', 150, yl, sl, pose='sit', face=0.6, arms='table', eyes='sad', mouth='flat', lean=0.5)
        ix = [lerp(1000, 300, lt / 1.0), 640, lerp(300, 1000, lt / 1.0)][min(k, 2)]
        C(ctx, 'ines', ix, y, s, face=0.7 if k != 0 else -0.7, walk=t * 6 if k != 1 else None, eyes='happy', mouth='smile', gaze=(0.9 if k != 0 else 0.6, -0.5))
    ctx.restore()
    if fb:
        grade(ctx, hexc('8A6A3A'), 0.5, cairo.OPERATOR_OVERLAY)
        for i in range(0, H, 6): rect(ctx, 0, i, W, 2, BLACK, 0.15)
        from env import label
        label(ctx, "FLASH-BACK", 540, 1255, 34, fg=WHITE, bg=hexc('6A4A2A'))

def s3_07(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.35, 1.5, t / d), 600, 1150)
    bg(ctx, 'cafe', env_cafe, sigma=2.5)
    for x in (60, 200, 1000, 1140):
        yy = 1290
        C(ctx, extra(int(x) % 7), x, yy, ds('cafe', yy), face=0.6 if x < 540 else -0.6, eyes='wide', mouth='flat', alpha=0.85)
    y = 1440; s = ds('cafe', y)
    lx = lerp(760, 840, ease(seg(t, 0, 0.6)))
    C(ctx, 'leo', lx, y, s, face=-0.5, walk=t * 3 if t < 0.6 else None, eyes='smug', mouth=talk(t, speaking(S, t, 0)), cnt='4 700 000 €', ck=0.8, t=t)
    C(ctx, 'ines', 470, y, s, cnt='12 400 €', t=t, face=0.5, arms=((0.9, 1.2), (-0.1, -0.05)), eyes='sad', mouth='o', glitch=0.3 if t > d * 0.6 else 0)
    ctx.restore()
    grade(ctx, hexc('2A4AA0'), 0.3)

def s3_08(ctx, t, d, S):
    ln = [lt_line(S, i) for i in range(4)]
    hug = seg(t, ln[3] + 1.0, ln[3] + 1.6)
    ctx.save(); cam(ctx, lerp(1.25, 1.45, ease(t / d)), 580, 1110)
    bg(ctx, 'kitchenN', env_kitchen, sigma=2, night=True)
    hanging_lamp(ctx, 600, 300, t, sway=0.02)
    y = 1440; s = ds('kitchen', y)
    top = table(ctx, 600, y, 140, s, top=hexc('B98A5E'), leg=hexc('6E5440'))
    show = t > ln[1]
    if show: laptop(ctx, 600, top, s)
    phone_obj(ctx, 700, top - 4, s, 1.57, glowa=0.25 if int(t * 3) % 2 else 0.05)
    if hug < 0.5:
        C(ctx, 'pere', 380, y, s, face=0.5, arms='rest' if t < ln[1] else 'reach', eyes='sad', brows='sad', mouth=talk(t, speaking(S, t, 0)) if speaking(S, t, 0) else 'frown', cnt='1 240 €', t=t)
        C(ctx, 'mere', 230, y - 30, ds('kitchen', y - 30), face=0.5, arms='cross', eyes='sad', mouth=talk(t, speaking(S, t, 2)) if speaking(S, t, 2) else 'frown', cnt='860 €', t=t, tears=seg(t, ln[2], ln[2] + 1.0))
        C(ctx, 'leo', 820, y, s, face=-0.5, arms='show' if show else 'rest', eyes='normal', mouth=talk(t, anyspeak(S, t, (1, 3))), cnt='4 700 000 €', ck=0.8, t=t)
    else:
        C(ctx, 'pere', 520, y, s, face=0.4, arms='shoulder', eyes='closed', mouth='smile', tears=0.7, cnt='1 240 €', t=t)
        C(ctx, 'leo', 760, y, s, face=-0.2, arms='hug', eyes='closed', mouth='smile', tears=0.6, cnt='4 700 000 €', ck=0.8, t=t)
        C(ctx, 'mere', 680, y - 10, ds('kitchen', y - 10), face=0.5, arms='hug', eyes='closed', mouth='smile', tears=1.0, cnt='860 €', t=t)
    ctx.restore()
    ins = ln[1] + 0.35 <= t < ln[2] - 0.1
    if ins:
        u = t - (ln[1] + 0.35)
        vgrad(ctx, 0, 0, W, H, hexc('2A2018'), hexc('120E0A'))
        ctx.save(); ctx.translate(W / 2, 980); k = 1.0 + 0.05 * u; ctx.scale(k, k)
        glow(ctx, 0, -40, 700, hexc('7FB2FF'), 0.35)
        rrect(ctx, -440, -330, 880, 600, 30); rgba(ctx, hexc('3A3F55')); ctx.fill()
        rrect(ctx, -410, -300, 820, 540, 16); rgba(ctx, hexc('F4F6FB')); ctx.fill()
        text(ctx, "RELEVÉ DE COMPTE-TITRES", 0, -240, 40, hexc('1A1E33'))
        rect(ctx, -360, -200, 720, 3, hexc('D0D4E0'))
        rows = [("Solde", "4 700 000 €"), ("Impôts payés", "✓ déclaré"), ("Origine", "placements légaux")]
        for i, (a1, b1) in enumerate(rows):
            text(ctx, a1, -340, -140 + i * 70, 34, hexc('5A6080'), align='l'); text(ctx, b1, 340, -140 + i * 70, 34, hexc('2E9B4A') if i else hexc('1A1E33'), align='r')
        chart_card(ctx, 0, 140, up=True, t=0.4 + 0.6 * seg(u, 0, 1.2), title="", a=1.0, w=700, h=150)
        rrect(ctx, -500, 270, 1000, 34, 10); rgba(ctx, hexc('5A5F75')); ctx.fill()
        ctx.restore()
    glow(ctx, 540, 900, 900, hexc('FFD58A'), 0.25 * hug)

def s3_09(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.45, 1.6, t / d), 540, 1100)
    bg(ctx, 'hall', env_hall, sigma=3)
    god_rays(ctx, 540, 640, 0.0, 900, 40, n=5, col=hexc('FFE2A8'), a=0.2, t=t, spread=0.8)
    y = 1400; s = ds('hall', y)
    info = C(ctx, 'armand', 455, y, s, face=0.5, arms='shoulder', eyes='happy', mouth=talk(t, speaking(S, t, 0)) if speaking(S, t, 0) else 'smile')
    C(ctx, 'leo', 625, y, s, face=-0.5, eyes='normal', mouth='flat' if t < d * 0.8 else 'smile', gaze=(-0.4, -0.2), cnt='4 700 000 €', ck=0.75, t=t)
    line(ctx, [(info['handB'][0], info['handB'][1]), (300, y - 10)], 7 * s, hexc('B08A5A')); rrect(ctx, 262, y - 20, 74, 20, 6); rgba(ctx, hexc('C9C3B0')); ctx.fill()
    dust(ctx, 0, 400, 1080, 1000, t, n=30)
    ctx.restore()

def s3_10(ctx, t, d, S):
    u = ease(seg(t, 0.0, lt_line(S, 0) + 0.4))
    y = 1600; s = ds('cafe', y)
    ctx.save(); cam(ctx, lerp(1.0, 1.25, ease(t / d)), lerp(520, 330, ease(t / d)), lerp(1250, 1330, ease(t / d)))
    bg(ctx, 'cafe', env_cafe, sigma=2.5)
    yb = 1260; sb = ds('cafe', yb)
    table(ctx, 820, yb, 220, sb, top=hexc('E8C46A'))
    for w, x in (('theo', 640), ('maxime', 820), ('chloe', 1000)):
        C(ctx, w, x, yb - 20, ds('cafe', yb - 20), face=-0.5, eyes='wide', mouth='flat', gaze=(-0.8, 0.2))
    top = table(ctx, 260, y, 110, s, top=hexc('B8B0A0')); trash(ctx, 470, y, s)
    chair(ctx, 150, y, 1, s)
    C(ctx, 'samy', 150, y, s, pose='sit', face=0.6, cnt='0,00 €', t=t, eyes='wide' if t < lt_line(S, 2) else 'happy',
      mouth=talk(t, speaking(S, t, 1)) if speaking(S, t, 1) else ('o' if t < lt_line(S, 2) else 'smile'), gaze=(0.6, 0))
    if u < 1:
        info = C(ctx, 'leo', lerp(1200, 400, u), y, s, face=-0.6, walk=t * 5, arms='hold', eyes='normal', mouth='smile', cnt='4 700 000 €', ck=0.8, t=t)
        tray(ctx, info['hand'][0] - 20 * s, info['hand'][1] - 6 * s, s=s)
    else:
        chair(ctx, 390, y, -1, s)
        C(ctx, 'leo', 390, y, s, pose='sit', face=-0.6, eyes='happy' if t > lt_line(S, 2) else 'normal',
          mouth=talk(t, anyspeak(S, t, (0, 2))) if anyspeak(S, t, (0, 2)) else 'smile', cnt='4 700 000 €', ck=0.8, t=t)
        tray(ctx, 310, top, s=s)
    ctx.restore()

def s3_11(ctx, t, d, S):
    T2 = d - 1.4
    if t < T2:
        y = 1600; s = ds('cafe', y)
        ctx.save(); cam(ctx, lerp(1.3, 1.5, ease(t / T2)), 270, 1360)
        bg(ctx, 'cafe5', env_cafe, sigma=5)
        rect(ctx, -500, -400, 2200, 3000, BLACK, 0.25)
        glow(ctx, 270, 1300, 500, GOLD, 0.5)
        god_rays(ctx, 270, 500, 0.0, 1000, 40, n=5, col=GOLD, a=0.2, t=t, spread=0.6)
        top = table(ctx, 260, y, 110, s, top=hexc('B8B0A0')); trash(ctx, 470, y, s)
        chair(ctx, 150, y, 1, s); chair(ctx, 390, y, -1, s)
        C(ctx, 'samy', 150, y, s, pose='sit', face=0.6, eyes='happy', mouth='laugh' if int(t * 6) % 2 else 'grin')
        info = C(ctx, 'leo', 390, y, s, pose='sit', face=-0.6, eyes='happy', mouth='grin')
        tray(ctx, 310, top, s=s); tray(ctx, 200, top, s=s)
        m = seg(t, 0.8, 1.3)
        cx, cy = info['top'][0], info['top'][1] - 46 * info['s']
        sparkles(ctx, cx, cy, 140, t, 14)
        counter(ctx, cx, cy, '4 700 000 €' if m < 0.5 else '1 AMI', k=1.0, pop=1 + 0.35 * math.sin(math.pi * m))
        ctx.restore()
    else:
        u = t - T2
        fill_bg(ctx, BLACK)
        ctx.save(); cam(ctx, lerp(1.6, 1.8, u / 1.4), 540, 1100)
        bg(ctx, 'hallN', env_hall, sigma=5, night=True)
        rect(ctx, -500, -400, 2200, 3000, BLACK, 0.6)
        glow(ctx, 540, 900, 400, RED, 0.25)
        C(ctx, 'armand', 540, 1450, 1.0, face=0, eyes='smug', mouth='flat', rim=hexc('FF6A6A'))
        ctx.restore()
        counter(ctx, 540, 640, '— — —' if u < 0.5 else '89 JOURS', k=1.6, glitch=1.0 if u < 0.5 else 0.0, t=t, col=GOLD if u < 0.5 else RED, pop=1 + 0.3 * math.sin(math.pi * seg(u, 0.5, 0.8)))

def bed(ctx, x, y, s=1.0):
    L_ = 200 * PX * s; Hh = 55 * PX * s
    rect(ctx, x, y - Hh, L_, Hh * 0.55, hexc('3A4A8A')); rect(ctx, x, y - Hh * 0.45, L_, Hh * 0.45, hexc('2A3460'))
    rect(ctx, x - 12 * s, y - Hh * 1.9, 14 * s, Hh * 1.9, hexc('2A3460')); rrect(ctx, x + 20 * s, y - Hh - 40 * s, 150 * s, 44 * s, 16 * s); rgba(ctx, hexc('DADFF0')); ctx.fill()
