import math, random
from gfx import *
from env import *
from char import draw_char, CHARS, extra

def cam(ctx, z=1.0, cx=540, cy=960, sx=0, sy=0, rot=0):
    ctx.translate(W / 2 + sx, H / 2 + sy); ctx.rotate(rot); ctx.scale(z, z); ctx.translate(-cx, -cy)

def popk(t, t0, d=0.28):
    u = seg(t, t0, t0 + d)
    if u <= 0: return 0.0
    if u >= 1: return 1.0
    return eout(u) * (1 + 0.35 * math.sin(u * math.pi))

def cnt_col(s): return RED if s.startswith('−') or s.startswith('-') else GOLD

def C(ctx, who, x, y, s=1.0, cnt=None, ca=1.0, cpop=1.0, glitch=0.0, t=0.0, ck=None, ccol=None, sparkle=False, **kw):
    info = draw_char(ctx, who, x, y, s, **kw)
    if cnt is not None and info and cpop > 0.01:
        cx, cy = info['top'][0], info['top'][1] - 46 * s
        k = ck or max(0.8, min(1.3, s))
        if sparkle: sparkles(ctx, cx, cy, 120 * k, t)
        counter(ctx, cx, cy, cnt, k=k, a=ca * kw.get('alpha', 1.0), glitch=glitch, t=t, pop=cpop, col=ccol or cnt_col(cnt))
    return info

def sparkles(ctx, x, y, r, t, n=10, col=GOLD):
    rnd = random.Random(int(x * 7 + y))
    for i in range(n):
        ph = (t * 0.8 + rnd.random()) % 1
        a = rnd.random() * 6.28; rr = r * (0.5 + 0.6 * ph)
        px, py = x + math.cos(a) * rr, y + math.sin(a) * rr * 0.6 - ph * 30
        sz = 7 * math.sin(ph * math.pi)
        ctx.save(); ctx.translate(px, py); ctx.rotate(0.785)
        rgba(ctx, col, 0.9 * math.sin(ph * math.pi)); ctx.rectangle(-sz / 2, -sz / 2, sz, sz); ctx.fill(); ctx.restore()

def coins(ctx, t, t0, n=40, area=(0, 1080), seed=1, bills=False):
    if t < t0: return
    rnd = random.Random(seed)
    for i in range(n):
        st = t0 + rnd.random() * 1.5
        if t < st: continue
        u = t - st; x = rnd.uniform(*area) + math.sin(u * 3 + i) * 30; y = -100 + u * rnd.uniform(500, 900) + 300
        if y > 2100: continue
        ctx.save(); ctx.translate(x, y); ctx.rotate(u * rnd.uniform(-4, 4))
        if bills:
            rect(ctx, -40, -20, 80, 40, hexc('5BB08A')); rect(ctx, -32, -13, 64, 26, hexc('8FD1A8')); text(ctx, "€", 0, 0, 22, hexc('2E7A53'))
        else:
            ctx.scale(abs(math.cos(u * 6 + i)) + 0.1, 1)
            ctx.arc(0, 0, 18, 0, 6.283); rgba(ctx, GOLD); ctx.fill(); ctx.arc(0, 0, 12, 0, 6.283); rgba(ctx, hexc('D9A23B')); ctx.fill()
        ctx.restore()

def table(ctx, x, y, w, top=hexc('E8E2D0'), leg=hexc('8A8A94'), a=1.0):
    rect(ctx, x - w / 2, y - 100, w, 16, top, a); rect(ctx, x - w / 2, y - 86, w, 6, mix(top, BLACK, 0.25), a)
    rect(ctx, x - w / 2 + 16, y - 84, 10, 84, leg, a); rect(ctx, x + w / 2 - 26, y - 84, 10, 84, leg, a)

def chair(ctx, x, y, f=1, a=1.0):
    rect(ctx, x - 34, y - 104, 68, 10, hexc('4F86C6'), a); rect(ctx, x - f * 34 - (6 if f > 0 else -2), y - 190, 8, 96, hexc('4F86C6'), a)
    rect(ctx, x - 28, y - 94, 6, 94, hexc('6A6A74'), a); rect(ctx, x + 22, y - 94, 6, 94, hexc('6A6A74'), a)

def tray(ctx, x, y, ang=0.0, food=True, a=1.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang)
    rrect(ctx, -62, -9, 124, 18, 5); rgba(ctx, hexc('E07A3B'), a); ctx.fill()
    if food:
        rrect(ctx, -50, -26, 44, 18, 6); rgba(ctx, WHITE, a); ctx.fill(); rect(ctx, -46, -24, 36, 10, hexc('C98A4B'), a)
        ctx.arc(20, -18, 12, 3.14, 6.28); rgba(ctx, hexc('E8C07A'), a); ctx.fill(); ctx.arc(46, -16, 9, 0, 6.28); rgba(ctx, hexc('C8323A'), a); ctx.fill()
    ctx.restore()

def trash(ctx, x, y):
    ctx.move_to(x - 46, y - 140); ctx.line_to(x + 46, y - 140); ctx.line_to(x + 38, y); ctx.line_to(x - 38, y); ctx.close_path(); rgba(ctx, hexc('5A6670')); ctx.fill()
    rect(ctx, x - 52, y - 152, 104, 16, hexc('6E7C86'))
    for i in (-20, 0, 20): line(ctx, [(x + i, y - 125), (x + i * 0.85, y - 14)], 4, hexc('46525A'))
    rect(ctx, x - 20, y - 168, 26, 18, hexc('E8E2D0')); ctx.arc(x + 20, y - 160, 9, 0, 6.28); rgba(ctx, hexc('9A6A3A')); ctx.fill()

def flies(ctx, x, y, t):
    for i in range(3):
        fx = x + math.sin(t * 7 + i * 2) * 40 + math.sin(t * 13 + i) * 10; fy = y + math.cos(t * 6 + i * 3) * 25
        ctx.arc(fx, fy, 3.5, 0, 6.28); rgba(ctx, BLACK); ctx.fill()

def phone_obj(ctx, x, y, s=1.0, ang=0.0, glowa=0.6, screen=hexc('BFD8FF')):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    glow(ctx, 0, 0, 170, hexc('7FB2FF'), glowa)
    rrect(ctx, -24, -42, 48, 84, 9); rgba(ctx, BLACK); ctx.fill(); rrect(ctx, -19, -36, 38, 70, 5); rgba(ctx, screen); ctx.fill()
    ctx.restore()

def laptop(ctx, x, y, s=1.0, flick=0.0, code=True):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    glow(ctx, 0, -80, 320, hexc('7FB2FF'), 0.35 * (1 - flick * 0.3))
    ctx.move_to(-95, 0); ctx.line_to(-75, -160); ctx.line_to(75, -160); ctx.line_to(95, 0); ctx.close_path(); rgba(ctx, hexc('3A3F55')); ctx.fill()
    ctx.move_to(-84, -8); ctx.line_to(-67, -152); ctx.line_to(67, -152); ctx.line_to(84, -8); ctx.close_path(); rgba(ctx, hexc('1C2545')); ctx.fill()
    pts = [(-60, -40), (-35, -60), (-10, -50), (15, -95), (40, -85), (60, -130)]
    line(ctx, pts, 5, hexc('5BD18A')); ctx.arc(60, -130, 6, 0, 6.28); rgba(ctx, hexc('5BD18A')); ctx.fill()
    rect(ctx, -115, 0, 230, 12, hexc('5A5F75'))
    ctx.restore()

def sneakers(ctx, x, y, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    for dx in (-28, 20):
        ctx.move_to(dx - 32, 0); ctx.line_to(dx - 32, -24); ctx.curve_to(dx - 10, -28, dx, -12, dx + 32, -9); ctx.line_to(dx + 34, 0); ctx.close_path()
        rgba(ctx, WHITE); ctx.fill_preserve(); ctx.set_line_width(3); rgba(ctx, BLACK); ctx.stroke(); line(ctx, [(dx - 32, -3), (dx + 34, -3)], 6, RED)
    ctx.restore()

def back_head(ctx, x, y, s=1.0):  # Léo seen from behind (over-shoulder)
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -120, 40, 240, 400, 80); rgba(ctx, WHITE); ctx.fill(); rrect(ctx, -116, 44, 232, 400, 78); rgba(ctx, hexc('8C909C')); ctx.fill()
    ctx.arc(0, 30, 100, 0, 6.28); rgba(ctx, WHITE); ctx.fill(); ctx.arc(0, 30, 96, 0, 6.28); rgba(ctx, hexc('6F7380')); ctx.fill()
    for i, a in enumerate((-2.5, -2.0, -1.5, -1.0, -0.55)):
        p = (math.cos(a) * 70, -10 + math.sin(a) * 70); q = (math.cos(a + 0.22) * 98, -10 + math.sin(a + 0.22) * 98); r = (math.cos(a + 0.45) * 70, -10 + math.sin(a + 0.45) * 70)
        ctx.move_to(*p); ctx.line_to(*q); ctx.line_to(*r); ctx.close_path(); ctx.set_line_width(8); rgba(ctx, WHITE); ctx.stroke_preserve(); rgba(ctx, hexc('0A0A0F')); ctx.fill()
    ctx.arc(0, -10, 78, 0, 6.28); rgba(ctx, WHITE); ctx.fill(); ctx.arc(0, -10, 74, 0, 6.28); rgba(ctx, hexc('0A0A0F')); ctx.fill()
    for i, a in enumerate((-2.5, -2.0, -1.5, -1.0, -0.55)):
        p = (math.cos(a) * 66, -10 + math.sin(a) * 66); q = (math.cos(a + 0.22) * 94, -10 + math.sin(a + 0.22) * 94); r = (math.cos(a + 0.45) * 66, -10 + math.sin(a + 0.45) * 66)
        ctx.move_to(*p); ctx.line_to(*q); ctx.line_to(*r); ctx.close_path(); rgba(ctx, hexc('0A0A0F')); ctx.fill()
    ctx.restore()

def card(ctx, cx, cy, top, big, sub=None, a=1.0, col=WHITE):
    if a <= 0: return
    w, h = 620, 320; k = 0.85 + 0.15 * eout(a)
    ctx.save(); ctx.translate(cx, cy); ctx.scale(k, k)
    rrect(ctx, -w / 2, -h / 2 + 10, w, h, 40); rgba(ctx, BLACK, 0.4 * a); ctx.fill()
    rrect(ctx, -w / 2, -h / 2, w, h, 40); rgba(ctx, hexc('F4F6FB'), 0.97 * a); ctx.fill()
    rect(ctx, -w / 2 + 40, -h / 2 + 90, w - 80, 3, hexc('D0D4E0'), a)
    text(ctx, top, 0, -h / 2 + 50, 34, hexc('5A6080'), a, mono=True)
    text(ctx, big, 0, 40, 92, col if col is not WHITE else hexc('1A1E33'), a)
    if sub: text(ctx, sub, 0, 120, 30, hexc('5A6080'), a)
    ctx.restore()

def bubble(ctx, x, y, s, a=1.0, k=1.0):
    if a <= 0: return
    w = text_w(ctx, s, 30) + 44
    ctx.save(); ctx.translate(x, y); ctx.scale(k, k)
    rrect(ctx, -w / 2, -32, w, 64, 30); rgba(ctx, hexc('4F86C6'), a); ctx.fill()
    text(ctx, s, 0, 0, 30, WHITE, a); ctx.restore()

def talk(t, on=True): return ('talk' if int(t * 9) % 2 else 'flat') if on else 'flat'

def lt_line(S, i): return S['lines'][i]['start'] if len(S['lines']) > i else 0
def speaking(S, t, i):
    ln = S['lines'][i]; return ln['start'] <= t <= ln['start'] + ln['dur']

def flicker(t, seed=0): return 1 if random.Random(int(t * 20) + seed).random() > 0.15 else 0.55

# =================== PART 1 ===================
def s1_01(ctx, t, d, S):
    ctx.save()
    z = lerp(3.3, 3.7, ease(t / d))
    cam(ctx, z, 540, 1400)
    bg(ctx, 'cafe8', env_cafe, sigma=8)
    rect(ctx, -400, -300, 2000, 2600, BLACK, 0.35)
    glow(ctx, 640, 1300, 380, GOLD, 0.3 + 0.2 * seg(t, 0, 0.6))
    turn = ease(seg(t, 0.8, 2.0))
    C(ctx, 'ines', 540, 1720, 1.0, face=lerp(-0.9, 0.0, turn), eyes='wide' if turn > 0.6 else 'smug', mouth='o' if t > 2.4 else 'flat', gaze=(lerp(-0.6, 0, turn), 0))
    ctx.restore()
    # Léo's counter rolling from debt to million
    p = ein(seg(t, 1.0, d - 0.5)); v = lerp(-3400, 1_000_000, p)
    s = ('−' + fmt_eur2(-v)) if v < 0 else fmt_eur2(v) if v < 1000 else fmt_eur(v)
    if t > 0.9:
        sparkles(ctx, 540, 560, 260, t, 16, GOLD if v >= 0 else RED)
        counter(ctx, 540, 560, s, k=1.9, col=GOLD if v >= 0 else RED, pop=popk(t, 0.9) * (1 + 0.04 * math.sin(t * 60) * (0 < p < 1)))
        text(ctx, "MON COMPTEUR", 540, 470, 34, WHITE, seg(t, 0.9, 1.2), mono=True, stroke=6)

def s1_02(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.0, 1.18, ease(t / d)), lerp(520, 560, t / d), 1000)
    bg(ctx, 'court', env_court, sigma=2)
    vals = ['340 €', '1 250 €', '85 €', '4 900 €', '−12 €', '760 €', '2 300 €', '18 900 €', '610 €']
    ppl = [(-80, 1330, 0.78, 1), (140, 1300, 0.7, -1), (330, 1360, 0.86, 1), (760, 1310, 0.74, -1), (930, 1350, 0.84, -1), (1150, 1300, 0.7, 1), (60, 1420, 0.95, 1), (1010, 1430, 0.95, -1), (640, 1290, 0.66, 1)]
    order = sorted(range(len(ppl)), key=lambda i: ppl[i][1])
    for j, i in enumerate(order):
        x, y, s, f = ppl[i]
        C(ctx, extra(i), x + f * t * 40 * s, y, s, cnt=vals[i], cpop=popk(t, 1.4 + j * 0.28), t=t, face=f * 0.7, walk=t * 5.5 * s + i,
          eyes='happy' if i % 3 == 0 else 'normal', mouth=['smile', 'flat', 'grin'][i % 3])
    C(ctx, 'leo', 540, 1480, 1.05, face=0, eyes='normal', mouth='flat', gaze=(0.5 * math.sin(t * 1.3), -0.6), lean=0.3)
    ctx.restore()

def s1_03(ctx, t, d, S):
    u = ease(seg(t, 0.3, d * 0.6))
    ctx.save(); cam(ctx, lerp(1.15, 1.75, u), lerp(470, 720, u), lerp(1040, 960, u))
    bg(ctx, 'hall', env_hall, sigma=3)
    # glass panel
    rect(ctx, 520, 520, 420, 820, hexc('243055'), 0.75)
    ctx.save(); ctx.rectangle(520, 520, 420, 820); ctx.clip()
    C(ctx, 'leo', 760, 1330, 0.95, face=-0.6, eyes='sad', mouth='frown', lean=0.4, alpha=0.5)
    if t > 1.2:
        counter(ctx, 742, 840, '−3 400 €', k=1.0, col=RED, glitch=0.5 if t < 1.6 else 0, t=t, pop=popk(t, 1.2))
    for k in range(3): line(ctx, [(560 + k * 90, 520), (760 + k * 90, 1340)], 26, WHITE, 0.05)
    ctx.restore()
    ctx.set_line_width(14); rgba(ctx, hexc('8A8A94')); ctx.rectangle(520, 520, 420, 820); ctx.stroke()
    C(ctx, 'leo', 330, 1360, 1.0, face=0.6, eyes='sad', mouth='frown', lean=0.4, gaze=(0.6, -0.1))
    ctx.restore()

def cafe_scene(ctx, t, rich_gaze=(0, 0), leo=True, leo_kw=None, rich_mouth=None, blink=False, with_ines=True, ines_kw=None, cnt=True):
    bg(ctx, 'cafe', env_cafe, sigma=2.5)
    glow(ctx, 820, 1050, 520, GOLD, 0.35)
    table(ctx, 820, 1230, 520, top=hexc('E8C46A'))
    rich = [('theo', 640, '19 400 €'), ('maxime', 820, '25 000 €'), ('chloe', 1000, '17 800 €')]
    for i, (w, x, c) in enumerate(rich):
        ca = (0.4 + 0.6 * (0.5 + 0.5 * math.sin(t * 16 + i))) if blink else 1
        C(ctx, w, x, 1230, 0.72, cnt=c if cnt else None, ca=ca, t=t, face=0.0 if w == 'maxime' else (0.4 if i == 0 else -0.4), pose='stand',
          eyes='happy' if rich_mouth == 'laugh' else 'smug', mouth=rich_mouth or ('smirk' if w == 'maxime' else 'smile'), gaze=rich_gaze, sparkle=(w == 'maxime'))
    if with_ines:
        C(ctx, 'ines', 1150, 1230, 0.72, cnt='12 400 €' if cnt else None, face=-0.6, eyes='happy', mouth='smile', **(ines_kw or {}))
    for x in (120, 360):
        table(ctx, x, 1180, 200, top=hexc('D8D2C0'))
    C(ctx, extra(1), 70, 1180, 0.62, face=0.5, pose='sit', mouth='smile'); C(ctx, extra(4), 410, 1180, 0.62, face=-0.5, pose='sit', mouth='flat')
    # lone table front-left with trash
    table(ctx, 210, 1560, 300, top=hexc('B8B0A0'))
    trash(ctx, 440, 1560); flies(ctx, 440, 1360, t)
    if leo:
        chair(ctx, 120, 1560, 1)
        C(ctx, 'leo', 120, 1560, 1.0, pose='sit', face=0.6, arms='hold', **(leo_kw or dict(eyes='sad', mouth='frown', gaze=(0.3, 0.5), lean=0.6)))
        tray(ctx, 235, 1452)

def s1_04(ctx, t, d, S):
    u = ease(seg(t, 1.7, 3.3))
    ctx.save(); cam(ctx, lerp(1.3, 1.45, u), lerp(860, 250, u), lerp(1060, 1290, u))
    cafe_scene(ctx, t)
    ctx.restore()

def s1_05(ctx, t, d, S):
    ix = lerp(-100, 700, ease(seg(t, 0, d)))
    ctx.save(); cam(ctx, 1.35, lerp(380, 760, ease(t / d)), 1080)
    bg(ctx, 'cafe', env_cafe, sigma=2.5)
    glow(ctx, 820, 1050, 520, GOLD, 0.35)
    table(ctx, 820, 1230, 520, top=hexc('E8C46A'))
    for i, (w, x, c) in enumerate([('theo', 640, '19 400 €'), ('maxime', 820, '25 000 €'), ('chloe', 1000, '17 800 €')]):
        C(ctx, w, x, 1230, 0.72, cnt=c, t=t, face=0.0 if w == 'maxime' else -0.3, eyes='smug', mouth='smile', sparkle=True)
    C(ctx, 'ines', ix, 1330, 0.9, cnt='12 400 €', t=t, face=0.6, walk=t * 5, eyes='happy' if t > 2 else 'normal', mouth='smile', gaze=(0.8, -0.5))
    ctx.restore()

def s1_06(ctx, t, d, S):
    ctx.save(); cam(ctx, 1.1, 540, 1000)
    bg(ctx, 'cafe5', env_cafe, sigma=5)
    ix = lerp(1300, -300, t / d)
    C(ctx, 'ines', ix, 1380, 1.25, cnt='12 400 €', t=t, face=-0.8, walk=t * 3.0, eyes='normal', mouth='flat', gaze=(-0.9, 0))
    back_head(ctx, 230, 1450, 2.1)
    ctx.restore()
    rect(ctx, 0, 0, W, H, hexc('3A5AAA'), 0.16)

def s1_07(ctx, t, d, S):
    sw = lt_line(S, 1) + 0.9  # swipe during "Moins que rien"
    sh = 18 * math.exp(-(t - sw - 0.5) * 5) * math.sin(t * 70) if t > sw + 0.5 else 0
    ctx.save(); cam(ctx, lerp(1.2, 1.35, ease(t / d)) + 0.1 * seg(t, sw, sw + 0.15) * (1 - seg(t, sw + 0.6, sw + 1.2)), 560, 1120, sx=sh)
    bg(ctx, 'cafe', env_cafe, sigma=2.5)
    for i, x in enumerate((80, 260, 860, 1040)):
        lau = t > sw
        C(ctx, extra(i + 2), x, 1200, 0.68, cnt=['4 900 €', '19 400 €', '17 800 €', '2 300 €'][i], ca=(0.4 + 0.6 * (0.5 + 0.5 * math.sin(t * 16 + i))) if lau else 1,
          face=0.6 if x < 540 else -0.6, eyes='happy' if lau else 'normal', mouth='laugh' if lau and int(t * 8 + i) % 2 else ('grin' if lau else 'o'), t=t)
    table(ctx, 650, 1520, 440)
    chair(ctx, 800, 1520, -1)
    leo_e = 'wide' if t < sw else 'sad'
    C(ctx, 'leo', 800, 1520, 1.0, pose='sit', face=-0.6, eyes=leo_e, mouth='flat' if t < sw else 'frown', gaze=(-0.5, -0.6), lean=0.4, arms='hold')
    k = seg(t, sw - 0.15, sw + 0.1)
    arm = ((lerp(0.4, 1.7, k), lerp(0.9, 1.9, k)), (-0.1, -0.05))
    talking = any(speaking(S, t, i) for i in range(len(S['lines'])))
    C(ctx, 'maxime', 400, 1520, 1.2, cnt='25 000 €', t=t, face=0.6, arms=arm, eyes='smug', mouth=talk(t, talking) if t < sw else ('laugh' if int(t * 8) % 2 else 'grin'), sparkle=True)
    if t < sw:
        tray(ctx, 640, 1414)
    else:
        u = seg(t, sw, sw + 0.7)
        tray(ctx, lerp(640, 900, u), lerp(1414, 1640, ein(u)), u * 3, food=u < 0.4)
        if u > 0.4:
            rnd = random.Random(1)
            for i in range(7):
                v = seg(t, sw + 0.5, sw + 0.9)
                ctx.arc(900 + (rnd.random() - 0.5) * 360 * eout(v), 1640 - 60 * math.sin(math.pi * v) * rnd.random(), 12, 0, 6.28)
                rgba(ctx, [hexc('E8C07A'), hexc('C8323A'), hexc('C98A4B')][i % 3]); ctx.fill()
    ctx.restore()
    if t > sw: rect(ctx, 0, 0, W, H, RED, 0.10 + 0.06 * math.sin(t * 16))

def s1_08(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.9, 1.15, ease(t / d)), 540, lerp(1330, 1150, ease(t / d)))
    bg(ctx, 'cafe5', env_cafe, sigma=5)
    rect(ctx, -500, -400, 2200, 3000, BLACK, 0.55)
    fa = 0.6 * (1 - seg(t, 0.5, d))
    for i, x in enumerate((40, 240, 840, 1040)):
        C(ctx, extra(i), x, 1220, 0.7, face=0.6 if x < 540 else -0.6, eyes='happy', mouth='laugh', alpha=fa)
    glow(ctx, 540, 1260, 460, hexc('9FB4FF'), 0.25)
    C(ctx, 'leo', 500, 1420, 1.0, pose='kneel', face=0.6, eyes='sad', mouth='frown', gaze=(0.5, 0.8), arms='reach', tears=seg(t, 1.5, 3.0))
    tray(ctx, 690, 1412, 0.15, food=False)
    rnd = random.Random(1)
    for i in range(6):
        ctx.arc(620 + i * 40 + rnd.random() * 20, 1414, 11, 0, 6.28); rgba(ctx, [hexc('E8C07A'), hexc('C8323A'), hexc('C98A4B')][i % 3]); ctx.fill()
    ctx.restore()

def s1_09(ctx, t, d, S):
    u = ease(seg(t, 0.6, 1.4)); back = ease(seg(t, 2.6, 3.4))
    zx = lerp(1.15, 1.9, u * (1 - back)); cx = lerp(520, 800, u * (1 - back)); cy = lerp(1060, 1220, u * (1 - back))
    ctx.save(); cam(ctx, zx, cx, cy)
    bg(ctx, 'bed', env_bedroom, sigma=2)
    bed(ctx, 60, 1340)
    rect(ctx, 640, 1140, 330, 20, hexc('5A4636')); rect(ctx, 660, 1160, 14, 180, hexc('4A3A2E')); rect(ctx, 935, 1160, 14, 180, hexc('4A3A2E'))
    glow(ctx, 900, 1000, 140, hexc('FFD58A'), 0.6); line(ctx, [(900, 1140), (900, 1040)], 6, hexc('8A8A94')); ctx.move_to(860, 1040); ctx.line_to(940, 1040); ctx.line_to(920, 990); ctx.line_to(880, 990); ctx.close_path(); rgba(ctx, hexc('E0A23B')); ctx.fill()
    letters(ctx, 790, 1110, n=7)
    info = C(ctx, 'leo', 330, 1340, 1.0, pose='sit', face=0.5, eyes='tired', mouth='frown', gaze=(0.5, 0.6), arms='phone', lean=0.5)
    phone_obj(ctx, info['hand'][0] + 6, info['hand'][1] - 14, 0.8, 0.3, glowa=0.6)
    ctx.restore()

def s1_10(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.2, 1.3, t / d), lerp(560, 600, t / d), 1060)
    bg(ctx, 'hall', env_hall, sigma=2.5)
    wv = lt_line(S, 1) - 0.2
    arms = 'mop' if t < wv else ((2.5, 2.9 + 0.35 * math.sin(t * 10)), (-0.1, 0.9))
    info = C(ctx, 'armand', 330, 1360, 1.0, face=0.5, arms=arms, eyes='happy' if t > wv else 'normal', mouth=talk(t, speaking(S, t, 1)) if t > wv else 'smile')
    mx = 330 + 60 + 15 * math.sin(t * 3) * (t < wv)
    line(ctx, [(info['handB'][0], info['handB'][1]), (mx + 40, 1350)], 7, hexc('B08A5A')); rrect(ctx, mx + 5, 1340, 74, 20, 6); rgba(ctx, hexc('C9C3B0')); ctx.fill()
    lx = lerp(1150, 760, ease(seg(t, 0, 2.6)))
    C(ctx, 'leo', lx, 1360, 0.98, face=-0.6, walk=t * 4.5 if t < 2.6 else None, eyes='sad' if t < wv else 'wide', mouth='flat' if t < wv + 0.3 else 'o', lean=0.45, gaze=(-0.3, 0.4 if t < wv else 0))
    ctx.restore()

def s1_11(ctx, t, d, S):
    cut = d * 0.62
    ctx.save()
    if t < cut:
        cam(ctx, lerp(1.25, 1.4, t / cut), 540, 1000)
        bg(ctx, 'hallN', env_hall, sigma=3, night=True)
        rect(ctx, -500, -400, 2200, 3000, BLACK, 0.45 * (1 - flicker(t) * 0.6))
        glow(ctx, 540, 600, 420, hexc('9FB4FF'), 0.25 * flicker(t))
        C(ctx, 'armand', 540, 1500, 1.5, face=-0.2, arms='mop', eyes='normal', mouth='flat', gaze=(-0.2, 0.5))
        counter(ctx, 540, 620, '— — —', k=1.8, glitch=1.0, t=t, pop=popk(t, 0.5))
    else:
        cam(ctx, lerp(2.6, 2.9, seg(t, cut, d)), 540, 1330)
        bg(ctx, 'hallN', env_hall, sigma=3, night=True)
        rect(ctx, -500, -400, 2200, 3000, BLACK, 0.4)
        C(ctx, 'leo', 540, 1700, 1.0, face=0, eyes='shock', mouth='O', gaze=(0, -0.4), sweat=True)
    ctx.restore()

def s1_12(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(2.0, 2.5, ease(t / d)), 540, 1200)
    bg(ctx, 'hallN', env_hall, sigma=5, night=True)
    rect(ctx, -500, -400, 2200, 3000, BLACK, 0.35)
    glow(ctx, 700, 1150, 380, GOLD, 0.45)
    up = ease(seg(t, 0.2, 0.9)); back = ease(seg(t, lt_line(S, 0) + 0.2, lt_line(S, 0) + 0.6))
    gz = (lerp(0, lerp(0.5, 0, back), up), lerp(0, lerp(-0.9, 0, back), up))
    C(ctx, 'armand', 540, 1560, 1.0, face=lerp(0.5, 0.0, back), eyes='wide' if back < 0.5 else 'smug', mouth=talk(t, speaking(S, t, 0)), gaze=gz, arms='rest', head_tilt=-0.12 * up * (1 - back))
    ctx.restore()

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

def s1_13(ctx, t, d, S):
    vote(ctx, t, "Tu lui fais confiance ?", ["OUI", "NON"], ["Commente ton choix", "La partie 2 est sur mon profil"])

# =================== PART 2 ===================
def s2_01(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.2, 1.45, ease(t / d)), 540, 1080)
    bg(ctx, 'boil', env_boiler, sigma=2.5)
    rnd = random.Random(3)
    for i in range(10):
        ph = (t * 0.3 + rnd.random()) % 1
        glow(ctx, rnd.choice([120, 960]) + ph * 40, 640 - ph * 280, 80 + ph * 100, hexc('E8E2D0'), 0.25 * (1 - ph))
    C(ctx, 'armand', 360, 1300, 1.0, face=0.6, arms='rest', eyes='normal', mouth=talk(t, speaking(S, t, 0)), cnt='— — —', glitch=0.3, t=t)
    C(ctx, 'leo', 740, 1300, 0.98, face=-0.6, eyes='wide', mouth='flat', lean=0.25)
    ctx.restore()

def rule_shot(ctx, t, d, S, kind):
    ctx.save()
    if kind == 1:
        cam(ctx, lerp(2.0, 2.2, t / d), 540, 1080)
        bg(ctx, 'boil6', env_boiler, sigma=6)
        u = ease(seg(t, 0, 0.5))
        glow(ctx, 540, 820, 260, GOLD, 0.6 * u)
        C(ctx, 'armand', 540, 1500, 1.0, face=0.1, arms=((lerp(0.2, 2.75, u), lerp(0.1, 3.0, u)), (-0.1, -0.05)), eyes='smug', mouth=talk(t, speaking(S, t, 0)), gaze=(0.2, -0.7))
    elif kind == 2:
        cam(ctx, 1.4, 540, 1010)
        bg(ctx, 'hall', env_hall, sigma=3)
        k = ease(seg(t, 0.5, 1.4))
        dv = lerp(200, 12, ease(seg(t, 0.2, 1.0)))
        C(ctx, extra(3), 380, 1360, 1.0, cnt=fmt_eur(dv), ccol=RED if dv < 50 else GOLD, t=t, face=0.6, arms='give', eyes='sad', mouth='frown', sweat=True)
        C(ctx, 'theo', 720, 1360, 1.0, cnt='3 900 €', t=t, face=-0.6, arms='give', eyes='smug', mouth='smirk')
        sneakers(ctx, lerp(470, 610, k), 1100, 0.9)
    else:
        cam(ctx, lerp(1.35, 1.5, t / d), 540, 1010)
        bg(ctx, 'boil', env_boiler, sigma=2.5)
        for x in (420, 680):
            ctx.move_to(x - 30, 1300); ctx.line_to(x + 30, 1300); ctx.line_to(x - 600, 1600); ctx.line_to(x - 720, 1580); ctx.close_path(); rgba(ctx, BLACK, 0.45); ctx.fill()
        C(ctx, 'leo', 640, 1300, 0.98, face=-0.6, eyes='wide', mouth='flat')
        C(ctx, 'armand', 470, 1300, 1.02, face=0.6, arms='shoulder', eyes='angry', mouth=talk(t, speaking(S, t, 0)))
    ctx.restore()
def s2_02(ctx, t, d, S): rule_shot(ctx, t, d, S, 1)
def s2_03(ctx, t, d, S): rule_shot(ctx, t, d, S, 2)
def s2_04(ctx, t, d, S): rule_shot(ctx, t, d, S, 3)

def s2_05(ctx, t, d, S):
    sp = lt_line(S, 1) - 0.1
    if t < sp:  # full screen: the buy
        ctx.save(); cam(ctx, lerp(1.3, 1.45, t / sp), 550, 1080)
        bg(ctx, 'hall', env_hall, sigma=3)
        k = ease(seg(t, 0.8, 1.7))
        dv = 12
        C(ctx, extra(3), 380, 1360, 1.0, cnt='12 €', ccol=RED, t=t, face=0.6, arms='give', eyes='sad', mouth='frown', sweat=True)
        C(ctx, 'leo', 720, 1360, 1.0, face=-0.6, arms='give', eyes='normal', mouth='flat')
        sneakers(ctx, lerp(480, 620, k), 1100, 0.9)
        if k > 0.9:
            label(ctx, "ACHAT : 40 €", 550, 1450, 36, bg=hexc('C8323A'))
        ctx.restore()
        return
    # split screen: top = buy, bottom = sell
    half = H / 2
    for part in (0, 1):
        ctx.save(); ctx.rectangle(0, part * half, W, half); ctx.clip()
        ctx.translate(0, part * half - half * 0.5 + (0 if part == 0 else 0))
        appear = 1.0 if part == 0 else seg(t, sp, sp + 0.25)
        ctx.translate((1 - eout(appear)) * (W if part else -W), 0)
        cam(ctx, 0.95, 540, 1000)
        bg(ctx, 'hall', env_hall, sigma=3)
        if part == 0:
            k = 1.0
            C(ctx, extra(3), 380, 1360, 0.95, cnt='12 €', t=t, face=0.6, arms='give', eyes='sad', mouth='frown')
            C(ctx, 'leo', 720, 1360, 0.95, face=-0.6, arms='give', eyes='normal', mouth='flat')
            sneakers(ctx, lerp(480, 620, k), 1110, 0.85)
            label(ctx, "ACHAT : 40 €", 540, 1405, 34, bg=hexc('C8323A'))
        else:
            k = ease(seg(t, lt_line(S, 1) + 0.4, lt_line(S, 1) + 1.2))
            C(ctx, 'leo', 380, 1360, 0.95, face=0.6, arms='give', eyes='happy' if k > 0.9 else 'normal', mouth='smile')
            C(ctx, 'chloe', 720, 1360, 0.95, cnt='17 800 €', t=t, face=-0.6, arms='give', eyes='happy', mouth='grin')
            sneakers(ctx, lerp(480, 620, k), 1110, 0.85)
            label(ctx, "VENTE : 140 €", 540, 1405, 34, bg=hexc('2E9B4A'))
            if k > 0.95: coins(ctx, t, lt_line(S, 1) + 1.2, n=18, area=(200, 880), seed=4)
        ctx.restore()
    rect(ctx, 0, half - 5, W, 10, WHITE)

def s2_06(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.35, 1.6, t / d), 640, 1120)
    bg(ctx, 'bed', env_bedroom, sigma=2)
    rect(ctx, 200, 1180, 860, 24, hexc('5A4636')); rect(ctx, 230, 1204, 18, 200, hexc('4A3A2E')); rect(ctx, 1010, 1204, 18, 200, hexc('4A3A2E'))
    n_st = int(seg(t, 0.4, d - 0.4) * 7 + 0.001)
    letters(ctx, 860, 1150, n=7, stamps=n_st)
    laptop(ctx, 560, 1180, 1.0, flick=random.Random(int(t * 10)).random())
    chair(ctx, 400, 1420, 1)
    C(ctx, 'leo', 400, 1420, 1.0, pose='sit', face=0.6, arms='reach', eyes='angry', mouth='flat', gaze=(0.6, 0.3), lean=0.5)
    ctx.restore()

def s2_07(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.3, 1.7, ease(seg(t, 0, d * 0.7))), lerp(560, 700, ease(t / d)), 1060)
    bg(ctx, 'bed', env_bedroom, sigma=2)
    rect(ctx, 520, 500, 420, 800, hexc('0E1736'), 0.85)
    ctx.save(); ctx.rectangle(520, 500, 420, 800); ctx.clip()
    zt = 1.3
    C(ctx, 'leo', 760, 1300, 0.95, face=-0.6, eyes='happy' if t > zt + 0.4 else 'wide', mouth='smile' if t > zt + 0.4 else 'o', alpha=0.55)
    v = lerp(-120, 0, ease(seg(t, 0.3, zt)))
    s = ('−' + fmt_eur2(-v)) if v < -0.004 else '0,00 €'
    counter(ctx, 742, 800, s, k=1.0, col=RED if v < -0.004 else WHITE, pop=1 + 0.25 * math.sin(math.pi * seg(t, zt, zt + 0.3)))
    if t > zt: sparkles(ctx, 742, 800, 160, t, 14, WHITE)
    ctx.restore()
    ctx.set_line_width(14); rgba(ctx, hexc('2E3963')); ctx.rectangle(520, 500, 420, 800); ctx.stroke()
    C(ctx, 'leo', 320, 1340, 1.0, face=0.6, eyes='happy' if t > zt + 0.4 else 'wide', mouth='smile' if t > zt + 0.4 else 'o', gaze=(0.6, -0.1), tears=0.6 * seg(t, zt + 0.6, zt + 1.6))
    ctx.restore()

def s2_08(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.35, 1.6, ease(t / d)), lerp(540, 380, ease(seg(t, 2.0, d))), 1240)
    bg(ctx, 'class', env_class, sigma=2.5)
    for i, x in enumerate((60, 330, 600, 870, 1140)):
        table(ctx, x, 1400, 200, top=hexc('C9A57A'), leg=hexc('6A6A74'))
        if i == 1:
            glow(ctx, x, 1300, 170, WHITE, 0.25); chair(ctx, x, 1470, 1); continue
        chair(ctx, x - 30, 1470, 1)
        if i == 2:
            info = C(ctx, 'ines', x - 30, 1470, 0.72, pose='sit', face=0.4, arms='phone', eyes='normal', mouth='flat', gaze=(0.4, 0.6))
            phone_obj(ctx, info['hand'][0], info['hand'][1] - 12, 0.55, glowa=0.3)
        elif i == 3:
            C(ctx, 'maxime', x - 30, 1470, 0.75, pose='sit', face=-0.4, eyes='happy', mouth='laugh' if int(t * 6) % 2 else 'grin')
        else:
            C(ctx, extra(i), x - 30, 1470, 0.7, pose='sit', face=0.3, eyes='normal', mouth='flat')
    ctx.restore()

def s2_09(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.35, 1.1, ease(t / d)), 540, 1060)
    bg(ctx, 'roof', env_roof, sigma=1.5)
    g = seg(t, 1.4, 1.9)
    glow(ctx, 540, 900, 300 + 500 * eout(g), GOLD, 0.5 * g)
    C(ctx, 'leo', 540, 1300, 1.0, face=0, eyes='wide' if g < 1 else 'normal', mouth='o' if g < 1 else 'smile', gaze=(0, -0.3), lean=lerp(0.3, 0.0, g))
    if g > 0: coins(ctx, t, 1.5, n=30, area=(0, 1080), seed=9)
    ph = (t % 2.0) / 0.8
    if ph < 1: glow(ctx, 560 + ph * 50, 880 - ph * 30, 25 + 45 * ph, WHITE, 0.25 * (1 - ph))
    ctx.restore()

def s2_10(ctx, t, d, S):
    cut = int(t / 0.85) % 4
    ctx.save()
    if cut == 0:
        cam(ctx, 1.4, 600, 1140); bg(ctx, 'bed', env_bedroom, sigma=2)
        rect(ctx, 200, 1180, 860, 24, hexc('5A4636'))
        for k, x in enumerate((420, 640, 860)): laptop(ctx, x, 1180, 0.95, flick=random.Random(int(t * 10) + k).random())
        for i in range(int(t * 2.5) % 9): rect(ctx, 260 + i * 30, 1140, 22, 40, hexc('E8E2D0')); rect(ctx, 260 + i * 30, 1140, 22, 7, hexc('6B4A2A'))
        C(ctx, 'leo', 640, 1520, 1.1, face=0, eyes='tired', mouth='flat', arms='reach', gaze=(0, -0.5))
    elif cut == 1:
        cam(ctx, 1.0); vgrad(ctx, 0, 0, W, H, hexc('1A2142'), hexc('3A2A6A'))
        rnd = random.Random(int(t * 7))
        for i in range(8):
            px = 540 + (rnd.random() - 0.5) * 820; py = 960 + (rnd.random() - 0.5) * 1100
            ctx.save(); ctx.translate(px, py); ctx.rotate((rnd.random() - 0.5) * 0.9)
            rect(ctx, -90, -110, 180, 220, WHITE); rect(ctx, -90, -110, 180, 50, RED)
            text(ctx, ['JAN', 'FÉV', 'MAR', 'AVR', 'MAI', 'JUIN', 'JUIL'][rnd.randint(0, 6)], 0, -85, 30, WHITE)
            text(ctx, str(rnd.randint(1, 31)), 0, 20, 90, hexc('1A1E33'), mono=True); ctx.restore()
    elif cut == 2:
        cam(ctx, 1.3, 540, 1060); bg(ctx, 'roof', env_roof, sigma=1.5)
        C(ctx, 'leo', 540, 1300, 1.0, face=0.3, arms='phone', eyes='normal', mouth='talk' if int(t * 8) % 2 else 'flat')
        phone_obj(ctx, 600, 920, 0.7, glowa=0.4)
    else:
        cam(ctx, 1.0); vgrad(ctx, 0, 0, W, H, hexc('2E1A10'), hexc('0B1020'))
        coins(ctx, t, (t // 0.85) * 0.85 - 1.0, n=50, area=(0, 1080), seed=int(t), bills=True)
    ctx.restore()
    ks = [(0, 25_040), (1.7, 180_000), (3.4, 600_000), (d - 0.6, 1_000_000)]
    v = ks[0][1]
    for i in range(3):
        (t0, v0), (t1, v1) = ks[i], ks[i + 1]
        if t >= t0: v = lerp(v0, v1, ein(seg(t, t0, t1)))
    sparkles(ctx, 540, 720, 250, t, 14)
    counter(ctx, 540, 720, fmt_eur(v), k=1.8, pop=1 + 0.05 * math.sin(t * 50))

def s2_11(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(2.4, 1.3, ease(seg(t, 0, d * 0.7))), lerp(390, 420, t / d), 1170)
    bg(ctx, 'bed', env_bedroom, sigma=2)
    rect(ctx, 0, 1220, 1080, 90, hexc('3A4A8A')); rect(ctx, 0, 1310, 1080, 60, hexc('2A3460'))
    rrect(ctx, 60, 1150, 200, 70, 24); rgba(ctx, hexc('DADFF0')); ctx.fill()
    ctx.save(); ctx.translate(600, 1228); ctx.rotate(-math.pi / 2)
    draw_char(ctx, 'leo', 0, 0, 1.0, face=0, eyes='tired', mouth='flat', gaze=(0.5, 0), arms=((0.3, 0.6), (-0.1, -0.05)))
    ctx.restore()
    ctx.save(); ctx.translate(380, 1160); ctx.rotate(-0.1)
    glow(ctx, 0, 0, 240, hexc('7FB2FF'), 0.35)
    rrect(ctx, -60, -32, 120, 64, 9); rgba(ctx, BLACK); ctx.fill(); rrect(ctx, -54, -26, 108, 52, 6); rgba(ctx, hexc('1A2450')); ctx.fill()
    ctx.save(); ctx.scale(1, -1); counter(ctx, 0, 0, '1 040 000 €', k=0.34, a=0.8); ctx.restore()
    ctx.restore()
    ctx.restore()

def s2_12(ctx, t, d, S):
    g = ease(seg(t, 0.4, d))
    ctx.save(); cam(ctx, lerp(1.25, 1.6, ease(t / d)), lerp(540, 660, ease(seg(t, lt_line(S, 2), d))), 1060)
    bg(ctx, 'bath', env_bath, sigma=2)
    glow(ctx, 330, 1050, 300 + 500 * g, GOLD, 0.12 + 0.35 * g)
    rrect(ctx, 500, 420, 460, 880, 30); rgba(ctx, hexc('8A9AA2')); ctx.fill()
    rrect(ctx, 520, 440, 420, 840, 20); rgba(ctx, hexc('A9C7D6')); ctx.fill()
    ctx.save(); rrect(ctx, 520, 440, 420, 840, 20); ctx.clip()
    glow(ctx, 730, 900, 380, GOLD, 0.3 * g)
    C(ctx, 'leo', 730, 1300, 1.0, face=-0.5, eyes='angry', mouth='flat', gaze=(-0.4, 0), lean=0)
    for k in range(3): line(ctx, [(560 + k * 100, 440), (760 + k * 100, 1280)], 30, WHITE, 0.08)
    ctx.restore()
    C(ctx, 'leo', 320, 1340, 1.0, face=0.6, eyes='sad' if t < lt_line(S, 2) else 'angry', mouth='flat', gaze=(0.6, 0), lean=lerp(0.5, 0.0, g))
    ctx.restore()

def s2_13(ctx, t, d, S):
    vote(ctx, t, ["Il dévoile son compteur", "ou il garde le secret ?"], ["DÉVOILER", "GARDER LE SECRET"], ["Commente ton choix", "La partie 3 est sur mon profil"])

# =================== PART 3 ===================
def s3_01(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.3, 1.45, t / d), lerp(440, 640, t / d), 1080)
    bg(ctx, 'hall', env_hall, sigma=3)
    glow(ctx, 540, 860, 600, GOLD, 0.3)
    rnd = random.Random(7)
    for i in range(6):
        x0 = 1500 + i * 230 - t * 170; s = 0.85 + 0.2 * rnd.random()
        C(ctx, extra(i), x0, 1330 + (i % 2) * 40, s, cnt=f"{rnd.randint(1, 90) * 100:,}".replace(",", " ") + " €", t=t, face=-0.7, walk=t * 6 + i, eyes='normal', mouth='talk' if i % 2 else 'smile')
    C(ctx, 'leo', lerp(320, 740, t / d), 1380, 1.0, face=0.5, walk=t * 2.4, eyes='normal', mouth='flat', lean=0)
    ctx.restore()

def s3_02(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.15, 1.35, ease(t / d)), 820, 1100)
    cafe_scene(ctx, t, leo=False, cnt=True)
    ctx.restore()
    o = ease(seg(t, 0.0, 0.9))
    if o < 1:
        rect(ctx, 0, 0, W / 2 * (1 - o), H, hexc('8A6A4A')); rect(ctx, W / 2 + W / 2 * o, 0, W / 2 * (1 - o), H, hexc('8A6A4A'))
        rect(ctx, W / 2 * (1 - o) - 30, 800, 14, 200, hexc('C9C3B0')); rect(ctx, W / 2 + W / 2 * o + 16, 800, 14, 200, hexc('C9C3B0'))
    glow(ctx, 540, 960, 1000, hexc('FFF2C8'), 0.7 * (1 - seg(t, 0.3, 1.5)))

def s3_03(ctx, t, d, S):
    l2 = lt_line(S, 1)
    focus = ease(seg(t, l2 - 0.2, l2 + 0.3))
    ctx.save(); cam(ctx, lerp(1.15, 1.9, focus), lerp(560, 720, focus), lerp(1120, 1180, focus))
    bg(ctx, 'cafe', env_cafe, sigma=2.5)
    rect(ctx, 1150, 650, 260, 700, hexc('FFF2C8'), 0.5)
    C(ctx, 'armand', 1270, 1300, 0.7, face=-0.4, arms='mop', cnt='— — —', glitch=0.6, t=t, eyes='smug', mouth='flat')
    turn = ease(seg(t, 0.6, 1.3))
    for i, x in enumerate((60, 200, 940, 1080)):
        f = 1 if x < 540 else -1
        C(ctx, extra(i), x, 1230, 0.62, face=f * lerp(0.0, 0.7, turn), eyes='wide' if turn > 0.5 else 'normal', mouth='o' if turn > 0.5 else 'flat', gaze=(f * turn * 0.7, 0))
    mt = speaking(S, t, 0)
    C(ctx, 'maxime', 300, 1520, 1.15, cnt='25 000 €', t=t, face=0.6, arms='point', eyes='smug', mouth=talk(t, mt) if mt else ('laugh' if int(t * 7) % 2 and t < l2 else 'smirk'), sparkle=True)
    C(ctx, 'leo', 730, 1520, 1.05, face=-0.3 if focus < 0.5 else -0.1, eyes='normal' if focus < 0.5 else 'smug', mouth=talk(t, speaking(S, t, 1)), lean=0)
    ctx.restore()

def s3_04(ctx, t, d, S):
    T = 2.4
    ctx.save()
    sh = (24 * math.exp(-(t - T) * 3) * math.sin(t * 70)) if t > T else 0
    cam(ctx, lerp(1.2, 1.35, ease(t / d)) - 0.15 * seg(t, T, T + 0.15) * (1 - seg(t, T + 0.4, T + 2)), 560, 1100, sx=sh, sy=sh * 0.6)
    bg(ctx, 'cafe', env_cafe, sigma=2.5)
    dim = 0.6 * seg(t, 1.1, 1.5) * (1 - seg(t, T, T + 0.1))
    rect(ctx, -500, -400, 2200, 3000, BLACK, dim)
    if t > T:
        for j in range(3):
            u = seg(t, T + j * 0.15, T + 1.2 + j * 0.15)
            if 0 < u < 1:
                ctx.set_line_width(26 * (1 - u)); rgba(ctx, GOLD, 1 - u); ctx.arc(600, 760, 100 + 1300 * eout(u), 0, 6.283); ctx.stroke()
        glow(ctx, 600, 760, 800, GOLD, 0.6 * (1 - 0.5 * seg(t, T, d)))
    for i, x in enumerate((60, 220, 920, 1080)):
        k = seg(t, T, T + 0.35); f = 1 if x < 540 else -1
        C(ctx, extra(i), x, 1300, 0.7, face=f * 0.6, eyes='shock' if k > 0 else 'normal', mouth='O' if k > 0 else 'flat', arms='head' if k > 0 else 'rest', gaze=(f * 0.5, -0.6 * k))
        if k > 0 and k < 1: tray(ctx, x + 40, lerp(1170, 1290, ein(k)), 0.6 * k, food=False)
        elif k >= 1: tray(ctx, x + 40, 1290, 0.6, food=False)
    C(ctx, 'maxime', 330, 1360, 0.9, cnt='25 000 €', t=t, face=0.4, eyes='shock' if t > T else 'smug', mouth='O' if t > T else 'smirk')
    r = ease(seg(t, 0.1, 1.0))
    C(ctx, 'leo', 640, 1400, 1.05, face=0, arms=((lerp(0.1, 2.85, r), lerp(0.05, 3.05, r)), (-0.1, -0.05)), eyes='smug' if t > T else 'normal', mouth='flat', gaze=(0, -0.2))
    if t > T:
        sparkles(ctx, 640, 860, 320, t, 22)
        counter(ctx, 640, 860, '4 700 000 €', k=1.5, pop=popk(t, T, 0.35) or 1)
        coins(ctx, t, T + 0.1, n=60, area=(-100, 1200), seed=3)
    ctx.restore()

def s3_05(ctx, t, d, S):
    c1, c2 = d * 0.36, d * 0.7
    ctx.save()
    if t < c1:
        cam(ctx, lerp(2.4, 2.7, t / c1), 540, 1240); bg(ctx, 'cafe8', env_cafe, sigma=8)
        C(ctx, 'maxime', 540, 1640, 1.0, face=0, eyes='shock', mouth='O', cnt='25 000 €', ck=0.7, t=t, gaze=(0, -0.7), sweat=True)
    elif t < c2:
        cam(ctx, 1.6, 540, 1140); bg(ctx, 'cafe5', env_cafe, sigma=5)
        for i, x in enumerate((300, 540, 780)):
            k = seg(t, c1 + i * 0.12, c1 + 0.4 + i * 0.12)
            info = C(ctx, extra(i + 3), x, 1380, 0.85, face=0, eyes='shock', mouth='O', arms=((lerp(0.2, 2.3, k), lerp(0.1, 2.9, k)), (-0.1, -0.05)), gaze=(0, -0.4))
            if k > 0.3: phone_obj(ctx, info['hand'][0], info['hand'][1] - 34, 0.8, glowa=0.5)
    else:
        cam(ctx, lerp(2.4, 2.8, seg(t, c2, d)), 540, 1240); bg(ctx, 'cafe8', env_cafe, sigma=8)
        C(ctx, 'ines', 540, 1640, 1.0, face=0, eyes='shock', mouth='o', cnt='12 400 €', ck=0.7, t=t, gaze=(0, -0.5))
    ctx.restore()

def s3_06(ctx, t, d, S):
    fb0 = lt_line(S, 1) + 0.6; fb1 = lt_line(S, 2) - 0.1
    fb = fb0 <= t < fb1
    ctx.save()
    if not fb:
        cam(ctx, lerp(1.35, 1.6, ease(t / d)), 600, 1100)
        bg(ctx, 'cafe', env_cafe, sigma=2.5)
        u = ease(seg(t, 0, 2.6))
        C(ctx, 'leo', 780, 1400, 1.0, face=-0.6, eyes='normal' if t < fb1 else 'smug', mouth=talk(t, speaking(S, t, 1) or speaking(S, t, 2)))
        C(ctx, 'ines', lerp(150, 470, u), 1400, 0.95, cnt='12 400 €', t=t, face=0.6, walk=t * 4 if u < 1 else None, eyes='happy', mouth=talk(t, speaking(S, t, 0)) if speaking(S, t, 0) else 'grin', gaze=(0.6, -0.2))
    else:
        k = int((t - fb0) / ((fb1 - fb0) / 3)); lt = (t - fb0) % ((fb1 - fb0) / 3)
        cam(ctx, 1.3 + 0.1 * lt, 540, 1100)
        cafe_scene(ctx, t, leo=True, cnt=True, with_ines=False)
        ix = [lerp(900, 100, lt / 1.0), 520, lerp(100, 900, lt / 1.0)][min(k, 2)]
        C(ctx, 'ines', ix, 1420, 0.9, face=0.7 if k != 0 else -0.7, walk=t * 6 if k != 1 else None, eyes='happy', mouth='smile', gaze=(0.9 if k != 0 else 0.6, -0.5))
    ctx.restore()
    if fb:
        rect(ctx, 0, 0, W, H, hexc('8A6A3A'), 0.3)
        for i in range(0, H, 6): rect(ctx, 0, i, W, 2, BLACK, 0.15)
        label(ctx, "FLASH-BACK", 540, 1250, 34, fg=WHITE, bg=hexc('6A4A2A'))

def s3_07(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.45, 1.6, t / d), 600, 1110)
    bg(ctx, 'cafe', env_cafe, sigma=2.5)
    for x in (60, 200, 1000, 1140):
        C(ctx, extra(int(x) % 7), x, 1230, 0.62, face=0.6 if x < 540 else -0.6, eyes='wide', mouth='flat', alpha=0.85)
    lx = lerp(760, 840, ease(seg(t, 0, 0.6)))
    C(ctx, 'leo', lx, 1400, 1.0, face=-0.5, walk=t * 3 if t < 0.6 else None, eyes='smug', mouth=talk(t, speaking(S, t, 0)))
    jit = math.sin(t * 50) * 6 * (t > d * 0.6)
    C(ctx, 'ines', 470, 1400, 0.95, cnt='12 400 €', t=t, face=0.5, arms=((0.9, 1.2), (-0.1, -0.05)), eyes='sad', mouth='o', glitch=0.3 if t > d * 0.6 else 0)
    ctx.restore()
    rect(ctx, 0, 0, W, H, hexc('2A4AA0'), 0.2)

MSGS = ["T'es dispo ?", "On se voit ce soir ?", "Prête-moi 50 €", "Frérot ❤", "T'as un compte où ?", "C'est vrai ?!", "Tu m'invites ?", "On était potes non ?"]
def s3_08(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.6, 1.25, ease(t / d)), 540, 1110)
    bg(ctx, 'hallN', env_hall, sigma=3, night=True)
    rect(ctx, -500, -400, 2200, 3000, BLACK, 0.3)
    info = C(ctx, 'leo', 540, 1370, 1.0, pose='sit', face=0.4, eyes='tired', mouth='flat', gaze=(0.4, 0.6), arms='phone', lean=0.5)
    phone_obj(ctx, info['hand'][0] + 6, info['hand'][1] - 14, 0.8, 0.3, glowa=0.8)
    ctx.restore()
    rnd = random.Random(2)
    for i, m in enumerate(MSGS):
        t0 = 0.4 + i * 0.25
        k = popk(t, t0)
        if k > 0:
            bubble(ctx, rnd.uniform(260, 820), rnd.uniform(560, 1250), m, a=0.95 * (1 - seg(t, d - 0.5, d)), k=k)

def s3_09(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.6, 1.8, t / d), 540, 1080)
    bg(ctx, 'hallN', env_hall, sigma=4, night=True)
    rect(ctx, -500, -400, 2200, 3000, BLACK, 0.25)
    glow(ctx, 540, 820, 600, hexc('FFB25A'), 0.4)
    C(ctx, 'armand', 400, 1360, 1.05, face=0.5, arms='shoulder', eyes='happy', mouth=talk(t, speaking(S, t, 0)) if speaking(S, t, 0) else 'smile')
    C(ctx, 'leo', 690, 1360, 1.0, face=-0.5, eyes='normal', mouth='flat', gaze=(-0.4, -0.2))
    ctx.restore()

def s3_10(ctx, t, d, S):
    u = ease(seg(t, 0.0, lt_line(S, 0) + 0.4))
    ctx.save(); cam(ctx, lerp(1.25, 1.6, ease(t / d)), lerp(500, 260, ease(t / d)), lerp(1200, 1330, ease(t / d)))
    bg(ctx, 'cafe', env_cafe, sigma=2.5)
    table(ctx, 820, 1230, 520, top=hexc('E8C46A'))
    for w, x in (('theo', 640), ('maxime', 820), ('chloe', 1000)):
        C(ctx, w, x, 1230, 0.72, face=-0.5, eyes='wide', mouth='flat', gaze=(-0.8, 0.2))
    table(ctx, 260, 1560, 300, top=hexc('B8B0A0')); trash(ctx, 480, 1560)
    chair(ctx, 140, 1560, 1)
    C(ctx, 'samy', 140, 1560, 0.85, pose='sit', face=0.6, cnt='0,00 €', ccol=WHITE, t=t, eyes='wide' if t < lt_line(S, 2) else 'happy', mouth=talk(t, speaking(S, t, 1)) if speaking(S, t, 1) else ('o' if t < lt_line(S, 2) else 'smile'), gaze=(0.6, 0))
    if u < 1:
        info = C(ctx, 'leo', lerp(1200, 400, u), 1560, 1.0, face=-0.6, walk=t * 5, arms='hold', eyes='normal', mouth='smile')
        tray(ctx, info['hand'][0] - 20, info['hand'][1] - 8)
    else:
        chair(ctx, 400, 1560, -1)
        C(ctx, 'leo', 400, 1560, 1.0, pose='sit', face=-0.6, eyes='happy' if t > lt_line(S, 2) else 'normal', mouth=talk(t, speaking(S, t, 0) or speaking(S, t, 2)) if (speaking(S, t, 0) or speaking(S, t, 2)) else 'smile')
        tray(ctx, 300, 1454)
    ctx.restore()

def s3_11(ctx, t, d, S):
    T2 = d - 1.4
    if t < T2:
        ctx.save(); cam(ctx, lerp(1.55, 1.8, ease(t / T2)), 270, 1300)
        bg(ctx, 'cafe5', env_cafe, sigma=5)
        rect(ctx, -500, -400, 2200, 3000, BLACK, 0.25)
        glow(ctx, 270, 1300, 500, GOLD, 0.5)
        table(ctx, 260, 1560, 300, top=hexc('B8B0A0')); trash(ctx, 480, 1560)
        chair(ctx, 140, 1560, 1); chair(ctx, 400, 1560, -1)
        C(ctx, 'samy', 140, 1560, 0.85, pose='sit', face=0.6, eyes='happy', mouth='laugh' if int(t * 6) % 2 else 'grin')
        C(ctx, 'leo', 400, 1560, 1.0, pose='sit', face=-0.6, eyes='happy', mouth='grin')
        tray(ctx, 300, 1454); tray(ctx, 200, 1454)
        m = seg(t, 0.8, 1.3)
        sparkles(ctx, 400, 1060, 140, t, 14)
        counter(ctx, 400, 1060, '4 700 000 €' if m < 0.5 else '1 AMI', k=1.0, pop=1 + 0.35 * math.sin(math.pi * m))
        ctx.restore()
    else:
        u = t - T2
        fill_bg(ctx, BLACK)
        ctx.save(); cam(ctx, lerp(1.6, 1.8, u / 1.4), 540, 1100)
        bg(ctx, 'hallN', env_hall, sigma=5, night=True)
        rect(ctx, -500, -400, 2200, 3000, BLACK, 0.6)
        glow(ctx, 540, 900, 400, RED, 0.25)
        C(ctx, 'armand', 540, 1450, 1.0, face=0, eyes='smug', mouth='flat')
        ctx.restore()
        counter(ctx, 540, 640, '— — —' if u < 0.5 else '89 JOURS', k=1.6, glitch=1.0 if u < 0.5 else 0.0, t=t, col=GOLD if u < 0.5 else RED, pop=1 + 0.3 * math.sin(math.pi * seg(u, 0.5, 0.8)))

# ======================= v3 overrides =======================
_o = {n: globals()[n] for n in ('s1_03', 's1_04', 's1_05', 's1_06', 's1_07', 's1_08', 's1_09', 's1_10', 's1_11', 's1_12', 's1_13', 's2_03', 's2_13', 's3_08', 's3_09')}
from env import env_street

def chart(ctx, x, y, w, h, up=True, t=1.0, col=None):
    col = col or (hexc('2E9B4A') if up else RED)
    rrect(ctx, x, y, w, h, 12); rgba(ctx, hexc('11162A')); ctx.fill()
    pts = []
    rnd = random.Random(5 if up else 6)
    n = 14
    for i in range(n):
        u = i / (n - 1)
        base = (u if up else 1 - u)
        v = clamp(base * 0.8 + 0.1 + (rnd.random() - 0.5) * 0.18)
        pts.append((x + 16 + u * (w - 32), y + h - 16 - v * (h - 32)))
    k = max(2, int(n * clamp(t)))
    line(ctx, pts[:k], 6, col)
    ctx.arc(pts[k - 1][0], pts[k - 1][1], 8, 0, 6.28); rgba(ctx, col); ctx.fill()

def ring_light(ctx, x, y, r=90):
    glow(ctx, x, y, r * 2.4, hexc('FFF6E0'), 0.5)
    ctx.set_line_width(18); rgba(ctx, hexc('FFF9EC')); ctx.arc(x, y, r, 0, 6.283); ctx.stroke()
    line(ctx, [(x, y + r), (x, y + r + 420)], 8, hexc('3A3F4B'))

def s1_03(ctx, t, d, S):
    c1 = lt_line(S, 1) - 0.05; c2 = lt_line(S, 2) - 0.05
    ctx.save()
    if t < c1:  # crypto guy
        u = t
        cam(ctx, lerp(1.55, 1.7, u / c1), 560, 1060)
        bg(ctx, 'hall', env_hall, sigma=3)
        info = C(ctx, 'crypto', 560, 1360, 1.05, face=0.2, arms='phone', eyes='smug', mouth='smirk',
                 cnt='−1 250 €', cpop=popk(t, 1.2), t=t)
        ctx.save(); ctx.translate(info['hand'][0] + 70, info['hand'][1] - 30); ctx.rotate(0.12)
        rrect(ctx, -46, -80, 92, 160, 12); rgba(ctx, BLACK); ctx.fill()
        chart(ctx, -40, -72, 80, 144, up=False, t=0.4 + 0.6 * seg(t, 0.2, 1.4)); ctx.restore()
    elif t < c2:  # influencer
        u = t - c1
        cam(ctx, lerp(1.55, 1.7, u / (c2 - c1)), 540, 1060)
        bg(ctx, 'court', env_court, sigma=4)
        ring_light(ctx, 780, 860, 90)
        info = C(ctx, 'influ', 520, 1360, 1.05, face=0.4, arms='phone', eyes='happy', mouth='smirk' if int(t * 3) % 2 else 'smile',
                 cnt='9 €', cpop=popk(u, 1.55), t=t)
        phone_obj(ctx, info['hand'][0] + 10, info['hand'][1] - 30, 0.75, -0.2, glowa=0.3, screen=hexc('F7C7DA'))
        for i in range(5):  # floating hearts
            ph = (u * 0.9 + i * 0.21) % 1
            hx, hy = 330 + i * 40 + math.sin(u * 3 + i) * 20, 1150 - ph * 380
            ctx.save(); ctx.translate(hx, hy); ctx.scale(1 - ph * 0.3, 1 - ph * 0.3)
            ctx.move_to(0, 10); ctx.curve_to(-22, -8, -10, -24, 0, -12); ctx.curve_to(10, -24, 22, -8, 0, 10)
            rgba(ctx, hexc('E2709F'), 1 - ph); ctx.fill(); ctx.restore()
    else:  # economics teacher
        u = t - c2
        cam(ctx, lerp(1.0, 1.1, u / max(0.1, d - c2)), 560, 800)
        bg(ctx, 'classE', env_class, sigma=2.5, board="ÉPARGNEZ ! ")
        C(ctx, 'prof', 760, 1430, 1.3, face=-0.5, arms='point' if int(u * 2) % 2 == 0 else 'rest', eyes='angry', mouth=talk(t, True),
          cnt='−2 000 €', cpop=popk(u, 2.2), t=t)
    ctx.restore()

def s1_04(ctx, t, d, S): _o['s1_03'](ctx, t, d, S)
def s1_05(ctx, t, d, S): _o['s1_04'](ctx, t, d, S)
def s1_06(ctx, t, d, S):
    c = lt_line(S, 1) - 0.1
    if t < c: _o['s1_05'](ctx, t, c + 1.5, S)
    else: _o['s1_06'](ctx, t - c, d - c, S)

def s1_07(ctx, t, d, S):
    sw = lt_line(S, 1) + 0.5
    sh = 18 * math.exp(-(t - sw - 0.5) * 5) * math.sin(t * 70) if t > sw + 0.5 else 0
    ctx.save(); cam(ctx, lerp(1.2, 1.35, ease(t / d)) + 0.1 * seg(t, sw, sw + 0.15) * (1 - seg(t, sw + 0.6, sw + 1.2)), 560, 1120, sx=sh)
    bg(ctx, 'cafe', env_cafe, sigma=2.5)
    lau = t > sw
    for i, (who, x, cn) in enumerate((('theo', 80, '19 400 €'), (extra(2), 260, '4 900 €'), ('chloe', 860, '17 800 €'), (extra(5), 1040, '2 300 €'))):
        C(ctx, who, x, 1200, 0.68, cnt=cn, ca=(0.4 + 0.6 * (0.5 + 0.5 * math.sin(t * 16 + i))) if lau else 1,
          face=0.6 if x < 540 else -0.6, eyes='happy' if lau else 'normal', mouth='laugh' if lau and int(t * 8 + i) % 2 else ('grin' if lau else 'o'), t=t)
    table(ctx, 650, 1520, 440)
    chair(ctx, 800, 1520, -1)
    C(ctx, 'leo', 800, 1520, 1.0, pose='sit', face=-0.6, eyes='wide' if t < sw else 'sad', mouth='flat' if t < sw else 'frown', gaze=(-0.5, -0.6), lean=0.4, arms='hold')
    k = seg(t, sw - 0.15, sw + 0.1)
    arm = ((lerp(0.4, 1.7, k), lerp(0.9, 1.9, k)), (-0.1, -0.05))
    talking = any(speaking(S, t, i) for i in range(len(S['lines'])))
    C(ctx, 'maxime', 400, 1520, 1.2, cnt='25 000 €', t=t, face=0.6, arms=arm, eyes='smug', mouth=talk(t, talking) if t < sw else ('laugh' if int(t * 8) % 2 else 'grin'), sparkle=True)
    if t < sw:
        tray(ctx, 640, 1414)
    else:
        u = seg(t, sw, sw + 0.7)
        tray(ctx, lerp(640, 900, u), lerp(1414, 1640, ein(u)), u * 3, food=u < 0.4)
        if u > 0.4:
            rnd = random.Random(1)
            for i in range(7):
                v = seg(t, sw + 0.5, sw + 0.9)
                ctx.arc(900 + (rnd.random() - 0.5) * 360 * eout(v), 1640 - 60 * math.sin(math.pi * v) * rnd.random(), 12, 0, 6.28)
                rgba(ctx, [hexc('E8C07A'), hexc('C8323A'), hexc('C98A4B')][i % 3]); ctx.fill()
    ctx.restore()
    if t > sw: rect(ctx, 0, 0, W, H, RED, 0.10 + 0.06 * math.sin(t * 16))

def s1_08(ctx, t, d, S): _o['s1_08'](ctx, t, d, S)
def s1_09(ctx, t, d, S):
    _o['s1_09'](ctx, t, d, S)
def s1_10(ctx, t, d, S): _o['s1_10'](ctx, t, d, S)

def s1_11(ctx, t, d, S):
    cut = d * 0.62
    ctx.save()
    if t < cut:
        cam(ctx, lerp(1.25, 1.4, t / cut), 540, 1000)
        bg(ctx, 'hall', env_hall, sigma=3)
        rect(ctx, -500, -400, 2200, 3000, BLACK, 0.62 - 0.25 * (flicker(t) - 0.55))
        glow(ctx, 540, 600, 420, hexc('9FB4FF'), 0.25 * flicker(t))
        C(ctx, 'armand', 540, 1500, 1.5, face=-0.2, arms='mop', eyes='normal', mouth='flat', gaze=(-0.2, 0.5))
        counter(ctx, 540, 620, '— — —', k=1.8, glitch=1.0, t=t, pop=popk(t, 0.5))
    else:
        cam(ctx, lerp(2.6, 2.9, seg(t, cut, d)), 540, 1330)
        bg(ctx, 'hall5', env_hall, sigma=5)
        rect(ctx, -500, -400, 2200, 3000, BLACK, 0.5)
        C(ctx, 'leo', 540, 1700, 1.0, face=0, eyes='shock', mouth='O', gaze=(0, -0.4), sweat=True)
    ctx.restore()

def s1_12(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(2.0, 2.5, ease(t / d)), 540, 1200)
    bg(ctx, 'hall5', env_hall, sigma=5)
    rect(ctx, -500, -400, 2200, 3000, BLACK, 0.55)
    glow(ctx, 700, 1150, 380, GOLD, 0.45)
    up = ease(seg(t, 0.2, 0.9)); back = ease(seg(t, lt_line(S, 0) + 0.2, lt_line(S, 0) + 0.6))
    gz = (lerp(0, lerp(0.5, 0, back), up), lerp(0, lerp(-0.9, 0, back), up))
    C(ctx, 'armand', 540, 1560, 1.0, face=lerp(0.5, 0.0, back), eyes='wide' if back < 0.5 else 'smug', mouth=talk(t, speaking(S, t, 0)), gaze=gz, arms='rest', head_tilt=-0.12 * up * (1 - back))
    ctx.restore()

def s1_13(ctx, t, d, S): _o['s1_13'](ctx, t, d, S)

def s2_03(ctx, t, d, S):
    ctx.save(); cam(ctx, 1.3, 540, 1010)
    bg(ctx, 'hall', env_hall, sigma=3)
    dv = lerp(200, 12, ease(seg(t, 0.4, 1.6)))
    C(ctx, extra(3), 330, 1360, 1.0, cnt=fmt_eur(dv), ccol=RED if dv < 60 else GOLD, t=t, face=0.3, eyes='sad', mouth='frown', sweat=True, arms='head' if dv < 60 else 'rest')
    C(ctx, 'chloe', 800, 1360, 1.0, cnt='17 800 €', t=t, face=-0.3, eyes='happy', mouth='smile', arms='phone', sparkle=True)
    C(ctx, 'leo', 565, 1300, 0.8, face=0, eyes='normal', mouth='flat', gaze=(-0.8 if int(t / 1.0) % 2 == 0 else 0.8, 0))
    a = seg(t, 0.4, 0.7)
    text(ctx, "↓", 230, 760, 90, RED, a, stroke=8); text(ctx, "↑", 900, 760, 90, hexc('2E9B4A'), seg(t, 1.6, 1.9), stroke=8)
    ctx.restore()

def s2_10(ctx, t, d, S):
    c1 = d * 0.3; c2 = d * 0.7
    ctx.save()
    if t < c1:
        cam(ctx, lerp(1.0, 1.1, t / c1), 540, 1040)
        bg(ctx, 'street', env_street, sigma=2.5)
        for i, (who, x, y, cn, f) in enumerate((('adulte1', 170, 1360, '86 000 €', 0.6), ('adulte2', 520, 1430, '−14 200 €', 0.3), ('patron', 870, 1360, '41 200 000 €', -0.4))):
            C(ctx, who, x + (f * 25 * t if who != 'patron' else 0), y, 1.0, face=f, walk=t * 4 + i if who != 'patron' else None, eyes='smug' if who == 'patron' else 'normal',
              mouth='smirk' if who == 'patron' else 'flat', cnt=cn, ck=0.85, cpop=popk(t, 0.15 + i * 0.22), t=t, sparkle=(who == 'patron'))
        C(ctx, 'leo', 560, 1700, 1.5, face=0.4, eyes='wide', mouth='o', gaze=(0.5, -0.6), alpha=1.0) if False else None
    elif t < c2:
        u = t - c1
        cam(ctx, lerp(2.0, 2.3, u / (c2 - c1)), 560, 1220)
        bg(ctx, 'street5', env_street, sigma=6)
        v = 41_200_000 + 760_000 * ein(seg(u, 0.1, c2 - c1))
        C(ctx, 'patron', 560, 1620, 1.0, face=0.1, arms='phone', eyes='smug', mouth='smirk', cnt=fmt_eur(v) + " ↑", ck=0.75, t=t, sparkle=True)
        phone_obj(ctx, 640, 1290, 0.6, 0.2, glowa=0.3)
    else:
        u = t - c2
        cam(ctx, 1.25, 600, 1100)
        bg(ctx, 'bed', env_bedroom, sigma=2)
        rect(ctx, 200, 1180, 860, 24, hexc('5A4636'))
        laptop(ctx, 470, 1180, 0.95)
        chart(ctx, 620, 920, 300, 240, up=True, t=0.3 + 0.7 * seg(u, 0, d - c2 - 0.3))
        C(ctx, 'leo', 380, 1420, 1.0, pose='sit', face=0.6, arms='reach', eyes='angry', mouth='flat', gaze=(0.6, -0.1), lean=0.4)
        v = lerp(25_040, 1_000_000, ein(seg(u, 0.1, d - c2 - 0.35)))
        S['hud_money'] = v
        sparkles(ctx, 540, 640, 230, t, 14)
        ctx.restore(); ctx.save()
        counter(ctx, 540, 640, fmt_eur(v), k=1.6, pop=1 + 0.04 * math.sin(t * 50))
        if u > d - c2 - 0.4: coins(ctx, t, c2 + d - c2 - 0.4, n=30, area=(0, 1080), seed=12)
    ctx.restore()

def s2_13(ctx, t, d, S):
    vote(ctx, t, ["Il montre son compteur", "ou il garde le secret ?"], ["LE MONTRER", "GARDER LE SECRET"], ["Commente ton choix", "La partie 3 est sur mon profil"])

def s3_08(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.6, 1.3, ease(t / d)), 520, 1130)
    bg(ctx, 'bed', env_bedroom, sigma=2.5)
    bed(ctx, 60, 1340)
    rect(ctx, -500, -400, 2200, 3000, BLACK, 0.25)
    info = C(ctx, 'leo', 380, 1340, 1.0, pose='sit', face=0.4, eyes='tired', mouth='flat', gaze=(0.4, 0.6), arms='phone', lean=0.5)
    phone_obj(ctx, info['hand'][0] + 6, info['hand'][1] - 14, 0.8, 0.3, glowa=0.8)
    ctx.restore()
    rnd = random.Random(2)
    for i, m in enumerate(MSGS):
        k = popk(t, 0.4 + i * 0.25)
        if k > 0: bubble(ctx, rnd.uniform(300, 800), rnd.uniform(580, 1200), m, a=0.95 * (1 - seg(t, d - 0.5, d)), k=k)

def s3_09(ctx, t, d, S):
    ctx.save(); cam(ctx, lerp(1.5, 1.65, t / d), 540, 1060)
    bg(ctx, 'hall', env_hall, sigma=3)
    glow(ctx, 540, 820, 600, hexc('FFE2A8'), 0.35)
    info = C(ctx, 'armand', 450, 1360, 1.05, face=0.5, arms='shoulder', eyes='happy', mouth=talk(t, speaking(S, t, 0)) if speaking(S, t, 0) else 'smile')
    C(ctx, 'leo', 620, 1360, 1.0, face=-0.5, eyes='normal', mouth='flat' if t < d * 0.8 else 'smile', gaze=(-0.4, -0.2))
    line(ctx, [(info['handB'][0], info['handB'][1]), (300, 1350)], 7, hexc('B08A5A')); rrect(ctx, 262, 1340, 74, 20, 6); rgba(ctx, hexc('C9C3B0')); ctx.fill()
    ctx.restore()
