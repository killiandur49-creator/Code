import math, random
from gfx import *

GY = 1250  # default ground
def cam(ctx, z=1.0, cx=540, cy=960, rot=0.0, sx=0, sy=0):
    ctx.translate(W / 2 + sx, H / 2 + sy); ctx.rotate(rot); ctx.scale(z, z); ctx.translate(-cx, -cy)

def person(ctx, x, y, s=1.0, cnt=None, ca=1.0, ck=None, glitch=0.0, t=0.0, pop=1.0, ccol=GOLD, **kw):
    info = stick(ctx, x, y, s, **kw)
    if cnt is not None and info:
        counter(ctx, info['top'][0], info['top'][1] - 52 * max(s, 0.7), cnt, k=ck or max(0.7, min(1.2, s * 0.85)), a=ca * kw.get('a', 1.0),
                glitch=glitch, t=t, pop=pop, col=ccol)
    return info

def popk(t, t0):  # pop-in scale
    u = seg(t, t0, t0 + 0.25)
    if u <= 0: return 0.0
    return 1 + 0.25 * math.sin(u * math.pi) * (1 - u) + 0 * u if u < 1 else 1.0

# ---------------- environments ----------------
def floor(ctx, y=GY, c=hexc('080C18'), x0=-1200, x1=2300, lines=True):
    rect(ctx, x0, y, x1 - x0, 1500, c)
    if lines:
        for i in range(-20, 40):
            line(ctx, [(x0 + i * 120, y), (x0 + i * 120 - 220, y + 900)], 2, hexc('121A30'))
        line(ctx, [(x0, y), (x1, y)], 3, hexc('1E2850'))

def env_cafeteria(ctx, t=0, warm=1.0, x0=-1200, x1=2300, lamp=True):
    vgrad(ctx, x0, -400, x1 - x0, GY + 400, hexc('121A36'), hexc('0B1020'))
    for i in range(-4, 10):  # back windows
        wx = i * 260 + 40
        rect(ctx, wx, 380, 170, 300, hexc('17224A'))
        line(ctx, [(wx + 85, 380), (wx + 85, 680)], 6, hexc('0E1530'))
    if lamp:
        for i in range(-3, 9):
            lx = i * 330 + 150
            line(ctx, [(lx, 0), (lx, 170)], 3, hexc('20294A'))
            rect(ctx, lx - 50, 170, 100, 14, hexc('2A3358'))
            glow(ctx, lx, 190, 260, hexc('9FB4FF'), 0.10)
    floor(ctx, GY, x0=x0, x1=x1)

def env_courtyard(ctx, t=0):
    vgrad(ctx, -800, -300, 2700, 1300, hexc('0A1028'), hexc('1A2450'))
    glow(ctx, 820, 330, 90, hexc('E9EEF9'), 0.9); glow(ctx, 820, 330, 300, hexc('9FB4FF'), 0.18)
    rect(ctx, -400, 560, 1900, 600, hexc('101733'))  # building
    for r in range(4):
        for c in range(14):
            wx = -360 + c * 135; wy = 600 + r * 130
            lit = (c * 7 + r * 3) % 5 == 0
            rect(ctx, wx, wy, 70, 80, hexc('F5C242', 0.55) if lit else hexc('18214A'))
    rect(ctx, -400, 540, 1900, 30, hexc('161F42'))
    for tx in (-150, 1180):
        line(ctx, [(tx, GY), (tx, 980)], 22, hexc('1A1A2E'))
        ctx.arc(tx, 930, 150, 0, 2 * math.pi); rgba(ctx, hexc('0F2A2A')); ctx.fill()
    floor(ctx, GY, c=hexc('0C1122'))

def env_corridor(ctx, t=0, night=False, x0=-1200, x1=2400, warm=True):
    vgrad(ctx, x0, -300, x1 - x0, GY + 300, hexc('0E1430') if night else hexc('172150'), hexc('0B1020'))
    for i in range(-5, 12):
        wx = i * 420 + 60
        rect(ctx, wx, 330, 220, 330, hexc('0D1638') if night else hexc('2A3A78'))
        if warm and not night:
            ctx.move_to(wx, 660); ctx.line_to(wx + 220, 660); ctx.line_to(wx + 420, GY); ctx.line_to(wx + 120, GY); ctx.close_path()
            rgba(ctx, hexc('F5C242', 0.07)); ctx.fill()
        for j in range(3):  # lockers
            lx = wx + 250 + j * 55
            rect(ctx, lx, 760, 50, 490, hexc('1D2A55') if not night else hexc('141C3C'))
            line(ctx, [(lx + 10, 800), (lx + 40, 800)], 3, hexc('0B1020'))
            line(ctx, [(lx + 10, 815), (lx + 40, 815)], 3, hexc('0B1020'))
    floor(ctx, GY, c=hexc('0A0F20'))

def env_bedroom(ctx, t=0):
    vgrad(ctx, -800, -300, 2700, 1600, hexc('0A0F24'), hexc('070A16'))
    window_frame(ctx, 620, 360, 300, 380)
    glow(ctx, 820, 450, 60, hexc('E9EEF9'), 0.7)
    rect(ctx, -800, 1300, 2700, 800, hexc('05080F'))
    # bed
    rect(ctx, 80, 1150, 640, 70, hexc('1F2A55')); rect(ctx, 80, 1220, 640, 30, hexc('141C3C'))
    rect(ctx, 60, 1060, 30, 240, hexc('141C3C')); rrect(ctx, 100, 1115, 150, 45, 16); rgba(ctx, hexc('2E3A6E')); ctx.fill()

def env_boiler(ctx, t=0):
    vgrad(ctx, -800, -300, 2700, 1600, hexc('1A1210'), hexc('0B1020'))
    glow(ctx, 540, 700, 800, hexc('FF8A3D'), 0.22)
    for i, (y, w) in enumerate([(380, 40), (470, 26), (560, 34)]):
        line(ctx, [(-400, y), (1500, y)], w, hexc('3A2A24'))
        for k in range(-2, 10): rect(ctx, k * 200 + i * 40, y - w / 2 - 6, 18, w + 12, hexc('4A3830'))
    for x in (160, 930):
        line(ctx, [(x, 380), (x, GY)], 36, hexc('3A2A24'))
        ctx.arc(x, 820, 48, 0, 2 * math.pi); rgba(ctx, hexc('241A16')); ctx.fill()
        ctx.set_line_width(6); rgba(ctx, hexc('5A463A')); ctx.arc(x, 820, 48, 0, 2 * math.pi); ctx.stroke()
        line(ctx, [(x, 820), (x + 28 * math.cos(t * 2 + x), 820 + 28 * math.sin(t * 2 + x))], 5, hexc('FF8A3D'))
    rnd = random.Random(3)
    for i in range(14):
        ph = (t * 0.25 + rnd.random()) % 1
        sx = rnd.choice([160, 930]) + (rnd.random() - 0.5) * 60; sy = 380 - ph * 300
        glow(ctx, sx + ph * 40, sy, 70 + ph * 90, hexc('C9C3B0'), 0.25 * (1 - ph))
    floor(ctx, GY, c=hexc('0E0B0C'), lines=False)

def env_rooftop(ctx, t=0):
    vgrad(ctx, -800, -300, 2700, 1700, hexc('060A1C'), hexc('1A2450'))
    rnd = random.Random(5)
    for i in range(70):
        sx = rnd.uniform(-300, 1400); sy = rnd.uniform(0, 650)
        ctx.arc(sx, sy, rnd.uniform(1, 2.6), 0, 2 * math.pi); rgba(ctx, WHITE, 0.3 + 0.4 * abs(math.sin(t * 1.5 + i))); ctx.fill()
    for i in range(30):  # city
        bw = rnd.uniform(60, 140); bh = rnd.uniform(150, 520); bx = -300 + i * 60
        rect(ctx, bx, 1350 - bh, bw, bh + 200, hexc('0C1230'))
        for k in range(int(bh / 45)):
            for m in range(int(bw / 30)):
                if rnd.random() < 0.3: rect(ctx, bx + 8 + m * 30, 1350 - bh + 15 + k * 45, 12, 16, hexc('F5C242', 0.5 + 0.3 * rnd.random()))
    glow(ctx, 540, 1350, 900, hexc('F5C242'), 0.12)
    rect(ctx, -400, GY + 10, 1900, 900, hexc('070A14')); rect(ctx, -400, GY - 10, 1900, 24, hexc('1A2142'))

def env_desk(ctx, t=0, screens=1, day=0.0):
    vgrad(ctx, -800, -300, 2700, 1700, mix(hexc('090D20'), hexc('2A3A78'), day), hexc('070A16'))
    window_frame(ctx, 90, 330, 300, 380, sky=False)
    vgrad(ctx, 96, 336, 288, 368, mix(hexc('0E1736'), hexc('F5A05A'), day), mix(hexc('0A1028'), hexc('5A6AAA'), day))
    # rain
    rnd = random.Random(int(t * 12))
    for i in range(18):
        rx = 100 + rnd.random() * 280; ry = 340 + rnd.random() * 340
        line(ctx, [(rx, ry), (rx - 6, ry + 30)], 2, hexc('9FB4FF'), 0.5)
    # clock
    ctx.arc(820, 420, 70, 0, 2 * math.pi); rgba(ctx, hexc('1C2545')); ctx.fill()
    ctx.set_line_width(6); rgba(ctx, hexc('39436E')); ctx.arc(820, 420, 70, 0, 2 * math.pi); ctx.stroke()
    hh = (3 + t * 0.0) / 12 * 2 * math.pi
    line(ctx, [(820, 420), (820 + 36 * math.sin(hh), 420 - 36 * math.cos(hh))], 7, WHITE)
    line(ctx, [(820, 420), (820, 362)], 5, WHITE)
    rect(ctx, -800, 1300, 2700, 800, hexc('05080F'))
    rect(ctx, 150, 1040, 860, 26, hexc('2A3358')); rect(ctx, 180, 1066, 20, 240, hexc('1C2545')); rect(ctx, 960, 1066, 20, 240, hexc('1C2545'))

def laptop(ctx, x, y, s=1.0, a=1.0, flick=0.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    glow(ctx, 0, -80, 330, hexc('7FB2FF'), 0.35 * a * (1 - flick * 0.3))
    ctx.move_to(-90, 0); ctx.line_to(-70, -150); ctx.line_to(70, -150); ctx.line_to(90, 0); ctx.close_path(); rgba(ctx, hexc('1C2545'), a); ctx.fill()
    ctx.move_to(-80, -8); ctx.line_to(-63, -142); ctx.line_to(63, -142); ctx.line_to(80, -8); ctx.close_path(); rgba(ctx, hexc('9CC2FF'), 0.85 * a); ctx.fill()
    for i in range(5): line(ctx, [(-50, -120 + i * 22), (-50 + 40 + (i * 37) % 60, -120 + i * 22)], 5, hexc('2A3A78'), a)
    rect(ctx, -110, 0, 220, 12, hexc('2A3358'), a)
    ctx.restore()

def sneakers(ctx, x, y, s=1.0, a=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    for dx in (-26, 18):
        ctx.move_to(dx - 30, 0); ctx.line_to(dx - 30, -22); ctx.curve_to(dx - 10, -26, dx, -10, dx + 30, -8); ctx.line_to(dx + 32, 0); ctx.close_path()
        rgba(ctx, WHITE, a); ctx.fill(); line(ctx, [(dx - 30, 0), (dx + 32, 0)], 6, RED, a)
    ctx.restore()

def phone_card(ctx, cx, cy, t, top, big, sub=None, a=1.0, col=WHITE):
    if a <= 0: return
    w, h = 560, 300
    k = 0.9 + 0.1 * eout(a)
    ctx.save(); ctx.translate(cx, cy); ctx.scale(k, k)
    rrect(ctx, -w / 2, -h / 2, w, h, 36); rgba(ctx, hexc('0E1430'), 0.92 * a); ctx.fill_preserve()
    ctx.set_line_width(3); rgba(ctx, hexc('39436E'), a); ctx.stroke()
    text(ctx, top, 0, -h / 2 + 60, 44, hexc('9FB4FF'), a, mono=True)
    text(ctx, big, 0, 20, 70, col, a, mono=True)
    if sub: text(ctx, sub, 0, 100, 32, hexc('9FB4FF'), a)
    ctx.restore()

def rich_group(ctx, t, x, y, s=0.8, blink=0.0, laugh=False, cnts=True, gaze=(0, 0), heads=None, a=1.0):
    specs = [(-235, 'Théo', '19 400 €', ('sunglasses', 'watch'), 1), (0, 'Maxime', '25 000 €', ('chain',), -1 if False else 1), (235, 'Chloé', '17 800 €', ('sunglasses', 'watch', 'hair'), -1)]
    infos = []
    for i, (dx, n, c, o, f) in enumerate(specs):
        ca = 1.0 if blink == 0 else (0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 18 + i * 1.7)))
        infos.append(person(ctx, x + dx * s / 0.8, y, s, cnt=c if cnts else None, ca=ca * a, outfit=o, face=f, gaze=gaze, a=a,
                            mouth='laugh' if (laugh and int(t * 8 + i) % 2 == 0) else ('smirk' if laugh else 'smile')))
    return infos

# ---------------- PART 1 ----------------
def s1_01(ctx, t, d):
    fill_bg(ctx, DARK)
    b = seg(t, 0.0, 0.7)
    glow(ctx, 540, 820, 200 + 900 * eout(b), GOLD, 0.6 * (1 - 0.5 * b))
    z = lerp(1.0, 1.12, ease(t / d))
    ctx.save(); cam(ctx, z, 540, 900)
    turn = lerp(-1, 0, ease(seg(t, 0.9, 2.2)))
    stick(ctx, 540, 1900, 3.0, face=-1 if turn < -0.5 else 0, head_turn=turn, gaze=(0, 0), outfit=('hair',), mouth='flat', a=clamp(t / 0.5))
    glow(ctx, 540 + 160, 760, 260, GOLD, 0.25)
    ctx.restore()
    p = ein(seg(t, 1.4, d - 0.55))
    v = 1_000_000 * p
    counter(ctx, 540, 380, fmt_eur(v) if v >= 1000 else fmt_eur2(v), k=1.55, a=seg(t, 1.2, 1.5), pop=1 + 0.06 * math.sin(t * 40) * (p > 0 and p < 1))

def s1_02(ctx, t, d):
    ctx.save(); cam(ctx, lerp(1.0, 1.14, ease(t / d)), 540, 1000)
    env_courtyard(ctx, t)
    rnd = random.Random(2)
    vals = ['340 €', '1 250 €', '85 €', '4 900 €', '12 €', '760 €', '2 300 €', '18 900 €']
    people = [(-60, 1270, 0.72, 1), (150, 1235, 0.62, -1), (330, 1300, 0.85, 1), (720, 1250, 0.7, -1), (900, 1290, 0.8, -1), (1120, 1240, 0.62, 1), (40, 1330, 0.95, 1), (980, 1340, 0.92, -1)]
    for i, (x, y, s, f) in enumerate(sorted(people, key=lambda p: p[1])):
        xx = x + f * t * 45 * s
        person(ctx, xx, y, s, cnt=vals[i], ca=1.0, pop=popk(t, 1.2 + i * 0.32), face=f, walk=t * 5 * s + i, outfit=(('hair',) if i % 3 == 1 else ()), mouth='smile' if i % 2 else None)
    stick(ctx, 540, 1320, 0.9, face=0, outfit=('hoodie',), hunch=0.4, mouth='flat', gaze=(0, -0.6))
    ctx.restore()

def s1_03(ctx, t, d):
    fill_bg(ctx, NAVY)
    z = lerp(1.0, 1.55, ease(seg(t, 0.4, d)))
    ctx.save(); cam(ctx, z, lerp(540, 700, ease(t / d)), lerp(960, 820, ease(t / d)))
    vgrad(ctx, -400, -200, 1900, 1500, hexc('0E1430'), hexc('090D1E'))
    window_frame(ctx, 470, 380, 470, 760)
    glow(ctx, 700, 760, 350, hexc('9FB4FF'), 0.08)
    # reflection
    ctx.save(); ctx.rectangle(476, 386, 458, 748); ctx.clip()
    stick(ctx, 780, 1240, 1.0, face=-1, outfit=('hoodie',), hunch=0.5, a=0.33, mouth='flat')
    counter(ctx, 770, 735, '0,00 €', k=0.95, a=0.85 * seg(t, 1.0, 1.4), pop=popk(t, 1.0))
    ctx.restore()
    floor(ctx, GY)
    stick(ctx, 300, GY, 1.0, face=1, outfit=('hoodie',), hunch=0.5, mouth='flat')
    ctx.restore()

def cafeteria_layout(ctx, t, show_leo=True, back_cnt=True, blink=0.0, laugh=False):
    env_cafeteria(ctx, t)
    glow(ctx, 760, 1000, 520, GOLD, 0.30)
    table(ctx, 760, 1130, 520, top=hexc('6B5A2A'))
    rich_group(ctx, t, 760, 1130, 0.62, blink=blink, laugh=laugh)
    for x, y in ((200, 1100), (1180, 1100)):
        table(ctx, x, y, 360)
        person(ctx, x - 70, y, 0.55, face=1, pose='sit', cnt=None)
        person(ctx, x + 80, y, 0.55, face=-1, pose='sit', cnt=None)
    # lone table front
    table(ctx, 180, 1420, 300)
    trash(ctx, 400, 1420)
    if show_leo:
        stick(ctx, 120, 1420, 0.95, face=1, pose='sit', outfit=('hoodie',), hunch=0.6, mouth='flat', gaze=(0, 0.4))
        tray(ctx, 210, 1336, food=True)

def s1_04(ctx, t, d):
    u = ease(seg(t, 1.6, 3.4))
    ctx.save(); cam(ctx, lerp(1.25, 1.35, u), lerp(760, 260, u), lerp(1000, 1180, u))
    cafeteria_layout(ctx, t)
    ctx.restore()

def s1_05(ctx, t, d):
    ix = lerp(1050, 300, t / d)
    ctx.save(); cam(ctx, 1.25, lerp(820, 470, t / d), 1080)
    env_cafeteria(ctx, t)
    glow(ctx, 420, 1000, 520, GOLD, 0.30)
    table(ctx, 420, 1200, 560, top=hexc('6B5A2A'))
    rich_group(ctx, t, 420, 1200, 0.72)
    person(ctx, ix, 1330, 0.85, cnt='12 400 €', face=-1, walk=t * 4.2, outfit=('hair',), gaze=(-0.4, -0.3), mouth='smile')
    ctx.restore()

def s1_06(ctx, t, d):
    ctx.save(); cam(ctx, 1.0, 540, 960)
    env_cafeteria(ctx, t)
    ix = lerp(1250, -250, ease(t / d) * 0.7 + 0.3 * t / d)
    person(ctx, ix, 1240, 1.35, cnt='12 400 €', face=-1, walk=t * 2.2, outfit=('hair',), gaze=(0, 0), mouth='flat')
    # Léo over-the-shoulder (back of head, bottom-left)
    ctx.save(); ctx.translate(170, 1700); ctx.scale(3.0, 3.0)
    line(ctx, [(0, 30), (0, 200)], 46, GREY); ctx.arc(-4, 8, 42, 0, 2 * math.pi); rgba(ctx, mix(GREY, DARK, 0.25)); ctx.fill()
    ctx.arc(0, -10, 33, 0, 2 * math.pi); rgba(ctx, WHITE); ctx.fill()
    ctx.restore()
    ctx.restore()
    rect(ctx, 0, 0, W, H, hexc('1A2A6A'), 0.18)

def s1_07(ctx, t, d):
    swipe = 1.4; fall0 = 1.55
    ctx.save()
    sh = 14 * math.exp(-(t - 3.2) * 6) * math.sin(t * 60) if t > 3.2 else 0
    cam(ctx, lerp(1.05, 1.18, ease(t / d)), 540, 1020, sx=sh)
    env_cafeteria(ctx, t)
    for i, x in enumerate((90, 330, 750, 990)):
        person(ctx, x, 1150, 0.62, cnt=['4 900 €', '19 400 €', '17 800 €', '2 300 €'][i], ca=0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 16 + i)),
               face=1 if x < 540 else -1, mouth='laugh' if int(t * 8 + i) % 2 else 'smile', outfit=(('sunglasses',) if i in (1, 2) else ()))
    table(ctx, 650, 1420, 420)
    stick(ctx, 760, 1420, 1.0, face=-1, pose='sit', outfit=('hoodie',), hunch=0.5, mouth='frown' if t > 2.6 else 'flat', gaze=(-0.3, -0.5))
    k = seg(t, swipe - 0.3, swipe)
    arm = ((-0.1, -0.05), (lerp(0.3, 1.6, k), lerp(0.6, 1.8, k)))
    person(ctx, 380, 1420, 1.25, cnt='25 000 €', face=1, outfit=('chain',), arms=arm, mouth='laugh' if t > 2.6 and int(t * 8) % 2 else 'smirk', ca=0.5 + 0.5 * (0.5 + 0.5 * math.sin(t * 16)))
    if t < fall0:
        tray(ctx, 620, 1318)
    else:
        u = seg(t, fall0, 3.2)
        tx = lerp(620, 820, u); ty = lerp(1318, 1500, ein(u)); ang = u * 2.4
        tray(ctx, tx, ty, ang, food=u < 0.5)
        if u > 0.6:
            rnd = random.Random(1)
            for i in range(6):
                fx = 820 + (rnd.random() - 0.5) * 300 * eout(seg(t, 3.0, 3.5)); fy = 1500 - 40 * math.sin(math.pi * seg(t, 3.0, 3.5)) * rnd.random()
                ctx.arc(fx, fy, 12, 0, 2 * math.pi); rgba(ctx, [hexc('E8C07A'), hexc('8BC48A')][i % 2]); ctx.fill()
    ctx.restore()
    if t > 2.6: rect(ctx, 0, 0, W, H, RED, 0.10 + 0.06 * math.sin(t * 16))

def s1_08(ctx, t, d):
    fill_bg(ctx, DARK)
    z = lerp(1.6, 1.0, ease(t / d))
    ctx.save(); cam(ctx, z, 540, lerp(1150, 1000, ease(t / d)))
    env_cafeteria(ctx, t)
    rect(ctx, -1200, -400, 3500, 3000, DARK, 0.55)
    fa = 0.5 * (1 - seg(t, 0.5, d))
    for i, x in enumerate((60, 260, 820, 1020)):
        stick(ctx, x, 1150, 0.7, face=1 if x < 540 else -1, a=fa, mouth='laugh')
    glow(ctx, 540, 1200, 420, hexc('9FB4FF'), 0.22)
    stick(ctx, 520, 1300, 1.0, face=1, pose='kneel', outfit=('hoodie',), hunch=0.8, mouth='frown', gaze=(0.3, 0.8), arms=((0.9, 0.5), (1.2, 0.9)))
    tray(ctx, 680, 1290, 0.1, food=False)
    rnd = random.Random(1)
    for i in range(5):
        ctx.arc(600 + i * 45 + rnd.random() * 20, 1294, 11, 0, 2 * math.pi); rgba(ctx, [hexc('E8C07A'), hexc('8BC48A')][i % 2]); ctx.fill()
    ctx.restore()

def s1_09(ctx, t, d):
    ctx.save(); cam(ctx, lerp(1.0, 1.3, ease(t / d)), lerp(540, 420, ease(t / d)), lerp(960, 1000, ease(t / d)))
    env_bedroom(ctx, t)
    rect(ctx, -800, -300, 2700, 2500, DARK, 0.25)
    info = stick(ctx, 430, 1250, 1.0, face=1, pose='sit', outfit=('hoodie',), hunch=0.7, mouth='flat', gaze=(0.4, 0.6), arms=((0.7, 1.6), (0.8, 1.7)))
    phone(ctx, info['hand'][0] + 10, info['hand'][1] - 10, 0.7, 0.3, glowa=0.7)
    ctx.restore()

def s1_10(ctx, t, d):
    ctx.save(); cam(ctx, 1.1, lerp(560, 600, t / d), 1020)
    env_corridor(ctx, t)
    wave = math.sin(t * 9) * 0.4 if t > 3.2 else 0
    a_arm = ((-0.1, -0.05), (0.2, 0.1)) if t < 3.0 else ((-0.1, -0.05), (2.6, 2.9 + wave))
    person(ctx, 300, 1270, 1.0, face=1, outfit=('cap', 'mop'), arms=a_arm if t >= 3.0 else None, mouth='smile', cnt=None)
    lx = lerp(1150, 760, ease(seg(t, 0, 3.4)))
    stick(ctx, lx, 1270, 0.95, face=-1, outfit=('hoodie',), hunch=0.5, walk=t * 4 if t < 3.4 else None, mouth='flat' if t < 3.6 else 'o', gaze=(0, 0.3 if t < 3.4 else 0))
    ctx.restore()

def s1_11(ctx, t, d):
    fill_bg(ctx, DARK)
    fl = 0.75 + 0.25 * (1 if random.Random(int(t * 15)).random() > 0.2 else 0)
    ctx.save(); cam(ctx, lerp(1.0, 1.1, t / d), 540, 960)
    vgrad(ctx, -400, -300, 1900, 2600, hexc('101733'), hexc('05070F'))
    rect(ctx, -400, -300, 1900, 2600, DARK, 1 - fl * 0.8)
    glow(ctx, 540, 380, 380, hexc('9FB4FF'), 0.18 * fl)
    person(ctx, 540, 1500, 2.0, face=-1, outfit=('cap', 'mop'), mouth='flat', gaze=(-0.2, 0.4))
    counter(ctx, 540, 430, '— — —', k=1.5, a=seg(t, 0.8, 1.1), glitch=1.0, t=t)
    # Léo's wide eyes foreground
    ctx.save(); ctx.translate(540, 1830); ctx.scale(6, 6)
    ctx.arc(0, 0, 33, 0, 2 * math.pi); rgba(ctx, WHITE, 0.95); ctx.fill()
    for ex in (-12, 12):
        ctx.arc(ex, -10, 7.5 + 1.5 * seg(t, 0.8, 1.2), 0, 2 * math.pi); rgba(ctx, DARK); ctx.fill()
    ctx.restore()
    ctx.restore()

def s1_12(ctx, t, d):
    fill_bg(ctx, DARK)
    ctx.save(); cam(ctx, lerp(1.6, 2.0, ease(t / d)), 520, 820)
    env_corridor(ctx, t)
    rect(ctx, -1200, -300, 3600, 2600, DARK, 0.45)
    glow(ctx, 640, 700, 380, GOLD, 0.35)
    up = ease(seg(t, 0.5, 1.4)); back = ease(seg(t, 2.6, 3.1))
    gz = (lerp(0, lerp(-0.6, 0, back), up), lerp(0, lerp(-0.9, 0, back), up))
    stick(ctx, 520, 1270, 1.0, face=0 if back > 0.5 else -1, head_turn=lerp(-1, 0, back), outfit=('cap',), mouth='flat', gaze=gz, head_tilt=-0.15 * up * (1 - back))
    mx = 640; line(ctx, [(mx - 10, 1050), (mx + 30, 1265)], 7, hexc('B08A5A'))
    rrect(ctx, mx + 2, 1255, 60, 18, 6); rgba(ctx, hexc('C9C3B0')); ctx.fill()
    ctx.restore()

def vote(ctx, t, q, opts, foot):
    fill_bg(ctx, DARK)
    glow(ctx, 540, 900, 700, GOLD, 0.16 + 0.04 * math.sin(t * 4))
    a = seg(t, 0, 0.25)
    lines = q if isinstance(q, list) else [q]
    for i, l in enumerate(lines):
        text(ctx, l, 540, 560 + i * 100, 84, WHITE, a, stroke=8, scale=lerp(1.2, 1, eout(seg(t, 0, 0.3))))
    oy = 560 + len(lines) * 100 + 110
    for i, o in enumerate(opts):
        k = popk(t, 0.25 + i * 0.15)
        if k <= 0: continue
        yy = oy + i * 170
        ctx.save(); ctx.translate(540, yy); ctx.scale(k, k)
        rrect(ctx, -360, -62, 720, 124, 62); rgba(ctx, [GOLD, WHITE][i % 2], 0.95); ctx.fill()
        text(ctx, o, 0, 0, 58, DARK, 1)
        ctx.restore()
    for i, f in enumerate(foot):
        text(ctx, f, 540, oy + len(opts) * 170 + 50 + i * 70, 46, [GOLD, hexc('9FB4FF')][i % 2], seg(t, 0.6, 0.9))

def s1_13(ctx, t, d):
    vote(ctx, t, "Tu lui fais confiance ?", ["OUI", "NON"], ["Commente ton choix", "La partie 2 est sur mon profil"])

# ---------------- PART 2 ----------------
def s2_01(ctx, t, d):
    ctx.save(); cam(ctx, lerp(1.0, 1.3, ease(t / d)), 540, 1050)
    env_boiler(ctx, t)
    person(ctx, 330, GY, 1.05, face=1, outfit=('cap', 'mop'), mouth='flat', cnt='— — —', glitch=0.25, t=t, ccol=GOLD)
    stick(ctx, 760, GY, 0.98, face=-1, outfit=('hoodie',), hunch=0.4, mouth='flat')
    ctx.restore()

def s2_02(ctx, t, d):
    ctx.save(); cam(ctx, 1.8, 540, 900)
    env_boiler(ctx, t)
    rect(ctx, -800, -300, 2700, 2600, DARK, 0.35)
    u = ease(seg(t, 0.0, 0.6))
    person(ctx, 540, 1250, 1.0, face=0, outfit=('cap',), arms=((-0.1, -0.05), (lerp(0.2, 2.9, u), lerp(0.1, 3.1, u))), mouth='flat', gaze=(0.3, -0.6))
    glow(ctx, 540, 720, 200, GOLD, 0.5 * u)
    ctx.restore()

def s2_03(ctx, t, d):
    ctx.save(); cam(ctx, 1.45, 540, 1060)
    env_corridor(ctx, t)
    k = ease(seg(t, 0.6, 1.6))
    stick(ctx, 380, 1270, 1.0, face=1, mouth='frown', arms=((-0.1, 0), (1.2, 1.5)), gaze=(0.3, 0))
    stick(ctx, 700, 1270, 1.0, face=-1, outfit=('watch', 'sunglasses'), mouth='smirk', arms=((-0.1, 0), (1.2, 1.5)))
    sneakers(ctx, lerp(470, 610, k), 1060, 0.9)
    ctx.restore()
    rect(ctx, 0, 0, W, H, RED, 0.06)

def s2_04(ctx, t, d):
    ctx.save(); cam(ctx, lerp(1.25, 1.4, t / d), 540, 1060)
    vgrad(ctx, -800, -300, 2700, 1600, hexc('1A1210'), hexc('090D1E'))
    glow(ctx, 1000, 700, 600, hexc('FF8A3D'), 0.25)
    floor(ctx, GY, c=hexc('0E0B0C'), lines=False)
    for x, f in ((420, 1), (680, -1)):  # long shadows
        ctx.move_to(x - 20, GY); ctx.line_to(x + 20, GY); ctx.line_to(x - 600, GY + 260); ctx.line_to(x - 700, GY + 240); ctx.close_path(); rgba(ctx, DARK, 0.6); ctx.fill()
    stick(ctx, 680, GY, 0.98, face=-1, outfit=('hoodie',), hunch=0.3, mouth='flat')
    stick(ctx, 450, GY, 1.05, face=1, outfit=('cap',), mouth='flat', arms=((-0.1, -0.05), (1.3, 1.45)))
    ctx.restore()

def s2_05(ctx, t, d):
    ctx.save()
    if t < 2.4:
        cam(ctx, 1.4, 540, 1060); env_corridor(ctx, t)
        dv = 200 - 188 * ease(seg(t, 0.2, 1.0))
        person(ctx, 360, 1270, 1.0, face=1, mouth='frown', cnt=fmt_eur(dv), arms=((-0.1, 0), (1.2, 1.5)), gaze=(0.2, 0.3))
        stick(ctx, 720, 1270, 0.98, face=-1, outfit=('hoodie',), hunch=0.3, arms=((-0.1, 0), (1.2, 1.5)))
        sneakers(ctx, lerp(450, 620, ease(seg(t, 1.2, 2.0))), 1060, 0.9)
    else:
        cam(ctx, 1.4, 560, 1060); env_corridor(ctx, t + 5)
        stick(ctx, 380, 1270, 0.98, face=1, outfit=('hoodie',), hunch=0.2, arms=((-0.1, 0), (1.2, 1.5)), mouth='smile')
        person(ctx, 740, 1270, 1.0, face=-1, outfit=('watch', 'sunglasses'), mouth='smile', cnt='3 900 €', arms=((-0.1, 0), (1.2, 1.5)))
        sneakers(ctx, lerp(470, 640, ease(seg(t, 2.6, 3.4))), 1060, 0.9)
    ctx.restore()

def s2_06(ctx, t, d):
    ctx.save(); cam(ctx, lerp(1.0, 1.15, t / d), 560, 1000)
    env_desk(ctx, t)
    rnd = random.Random(4)
    for i in range(int(seg(t, 0, d) * 14)):
        nx = 260 + rnd.random() * 640; ny = 1015 + rnd.random() * 20
        ctx.save(); ctx.translate(nx, ny); ctx.rotate((rnd.random() - 0.5) * 0.5); rect(ctx, -30, -6, 60, 8, hexc('E8E2C8'), 0.8); ctx.restore()
    stick(ctx, 420, 1300, 1.0, face=1, pose='sit', outfit=('hoodie',), hunch=0.8, mouth='flat', gaze=(0.5, 0.2), arms=((0.9, 1.4), (1.0, 1.5)))
    laptop(ctx, 640, 1040, 1.1, flick=random.Random(int(t * 10)).random())
    ctx.restore()

def s2_07(ctx, t, d):
    ctx.save(); cam(ctx, lerp(1.0, 1.25, ease(t / d)), lerp(540, 300, ease(seg(t, 2.5, d))), 1050)
    vgrad(ctx, -800, -300, 2700, 1600, hexc('172150'), hexc('0B1020'))
    rect(ctx, 200, 420, 680, 300, hexc('12322A')); ctx.set_line_width(10); rgba(ctx, hexc('3A2A24')); ctx.rectangle(200, 420, 680, 300); ctx.stroke()
    floor(ctx, GY)
    for i, x in enumerate((60, 300, 560, 820, 1060)):
        table(ctx, x, 1190, 170)
        if i == 1:
            glow(ctx, x, 1100, 160, hexc('9FB4FF'), 0.15)
            continue
        if i == 2:
            stick(ctx, x - 40, 1190, 0.62, face=1, pose='sit', outfit=('hair',), gaze=(0.3, 0.7), arms=((0.7, 1.5), (0.8, 1.6)), mouth='flat')
            phone(ctx, x + 10, 1090, 0.45, glowa=0.4)
        elif i == 3:
            stick(ctx, x - 40, 1190, 0.66, face=-1, pose='sit', outfit=('chain',), mouth='smirk', gaze=(-0.4, 0))
        else:
            stick(ctx, x - 40, 1190, 0.6, face=1, pose='sit', mouth=None, gaze=(0.2, 0))
    ctx.restore()

def s2_08(ctx, t, d):
    ctx.save(); cam(ctx, lerp(1.25, 1.05, ease(t / d)), 540, 1000)
    env_rooftop(ctx, t)
    g = seg(t, 1.6, 2.2)
    glow(ctx, 540, 850, 300 + 400 * eout(g), GOLD, 0.45 * g * (1 - 0.5 * seg(t, 2.5, d)))
    stick(ctx, 540, GY, 1.0, face=0, outfit=('hoodie',), hunch=lerp(0.3, 0.0, g), mouth='flat', gaze=(0, -0.4))
    if (t % 2.2) < 0.9:
        ph = (t % 2.2) / 0.9
        glow(ctx, 560 + ph * 60, 850 - ph * 40, 30 + 50 * ph, WHITE, 0.25 * (1 - ph))
    ctx.restore()

def s2_09(ctx, t, d):
    cut = int(t / 1.15) % 3
    day = 0.5 + 0.5 * math.sin(t * 2.6)
    ctx.save()
    if cut == 0:
        cam(ctx, 1.05, 560, 1000); env_desk(ctx, t, day=day)
        stick(ctx, 420, 1300, 1.0, face=1, pose='sit', outfit=('hoodie',), hunch=0.8, gaze=(0.5, 0.2), arms=((0.9, 1.4), (1.0, 1.5)))
        laptop(ctx, 600, 1040, 1.0); laptop(ctx, 830, 1040, 0.85)
        for i in range(int(t * 3) % 9):
            rect(ctx, 260 + i * 34, 1004, 26, 36, hexc('C9C3B0')); rect(ctx, 260 + i * 34, 1004, 26, 8, hexc('6B4A2A'))
    elif cut == 1:
        cam(ctx, 1.0, 540, 960); fill_bg(ctx, mix(NAVY, hexc('2A3A78'), day))
        rnd = random.Random(int(t * 8))
        for i in range(7):  # calendar pages flying
            px = 540 + (rnd.random() - 0.5) * 800; py = 960 + (rnd.random() - 0.5) * 1000
            ctx.save(); ctx.translate(px, py); ctx.rotate((rnd.random() - 0.5) * 0.8)
            rect(ctx, -90, -110, 180, 220, WHITE, 0.9); rect(ctx, -90, -110, 180, 50, RED, 0.9)
            text(ctx, str(rnd.randint(1, 31)), 0, 20, 90, DARK, 0.9, mono=True); ctx.restore()
    else:
        cam(ctx, 1.25, 540, 1000); env_desk(ctx, t, day=day)
        for k, x in enumerate((360, 560, 760)): laptop(ctx, x, 1040, 1.0, flick=random.Random(int(t * 10) + k).random())
        stick(ctx, 560, 1330, 1.1, face=0, outfit=('hoodie',), hunch=0.5, gaze=(0, -0.4), arms=((0.9, 1.4), (1.0, 1.5)))
    ctx.restore()
    ks = [(0, 25_040), (1.6, 180_000), (3.6, 600_000), (5.6, 1_000_000)]
    v = ks[0][1]
    for i in range(len(ks) - 1):
        (t0, v0), (t1, v1) = ks[i], ks[i + 1]
        if t >= t0: v = lerp(v0, v1, ein(seg(t, t0, t1)))
    counter(ctx, 540, 520, fmt_eur(v), k=1.6, pop=1 + 0.05 * math.sin(t * 50))

def s2_10(ctx, t, d):
    ctx.save(); cam(ctx, lerp(2.6, 1.15, ease(seg(t, 0, d * 0.75))), lerp(560, 520, t / d), lerp(1080, 1130, t / d))
    vgrad(ctx, -800, -300, 2700, 2600, hexc('0A0F24'), hexc('05080F'))
    rect(ctx, 0, 1180, 1080, 80, hexc('1F2A55')); rrect(ctx, 80, 1120, 170, 50, 16); rgba(ctx, hexc('2E3A6E')); ctx.fill()
    ctx.save(); ctx.translate(560, 1170); ctx.rotate(-math.pi / 2)
    stick(ctx, 0, 0, 1.0, face=-1, head_turn=0, outfit=('hoodie',), mouth='flat', gaze=(0.6, 0), arms=((-0.05, 0), (0.05, 0)))
    ctx.restore()
    ctx.save(); ctx.translate(560, 1092); ctx.rotate(-0.15)
    glow(ctx, 0, 0, 220, hexc('7FB2FF'), 0.35)
    rrect(ctx, -46, -26, 92, 52, 8); rgba(ctx, DARK); ctx.fill()
    rrect(ctx, -41, -21, 82, 42, 5); rgba(ctx, hexc('1A2450')); ctx.fill()
    ctx.save(); ctx.scale(1, -1); counter(ctx, 0, 0, '1 040 000 €', k=0.24, a=0.75); ctx.restore()
    ctx.restore()
    ctx.restore()

def s2_11(ctx, t, d):
    ctx.save(); cam(ctx, lerp(1.0, 1.2, ease(t / d)), 540, 1000)
    vgrad(ctx, -800, -300, 2700, 1600, hexc('0E1430'), hexc('070A16'))
    g = ease(seg(t, 0.5, d))
    glow(ctx, 330, 1000, 300 + 500 * g, GOLD, 0.15 + 0.35 * g)
    rrect(ctx, 520, 360, 440, 920, 30); rgba(ctx, hexc('3A4566')); ctx.fill()
    rrect(ctx, 540, 380, 400, 880, 20); rgba(ctx, hexc('1A2450')); ctx.fill()
    ctx.save(); rrect(ctx, 540, 380, 400, 880, 20); ctx.clip()
    glow(ctx, 740, 820, 380, GOLD, 0.25 * g)
    stick(ctx, 740, 1240, 1.0, face=-1, outfit=('hoodie',), hunch=0, mouth='flat', gaze=(-0.2, 0), head_tilt=-0.05)
    ctx.restore()
    floor(ctx, GY + 30)
    stick(ctx, 330, GY + 30, 1.0, face=1, outfit=('hoodie',), hunch=lerp(0.5, 0.1, g), mouth='flat', gaze=(0.3, 0))
    ctx.restore()

def s2_12(ctx, t, d):
    vote(ctx, t, ["Il dévoile son compteur", "ou il garde le secret ?"], ["DÉVOILER", "GARDER LE SECRET"], ["Commente ton choix", "La partie 3 est sur mon profil"])

# ---------------- PART 3 ----------------
def s3_01(ctx, t, d):
    ctx.save(); cam(ctx, lerp(1.15, 1.3, t / d), lerp(400, 640, t / d), 1040)
    env_corridor(ctx, t)
    glow(ctx, 1400, 900, 900, GOLD, 0.28)
    rnd = random.Random(7)
    for i in range(7):
        x0 = 1500 + i * 230 - t * 160; s = 0.8 + 0.25 * rnd.random()
        person(ctx, x0, 1270 + (i % 2) * 40, s, cnt=f"{rnd.randint(1, 90) * 100:,}".replace(",", " ") + " €", face=-1, walk=t * 5.5 + i, outfit=(('hair',) if i % 3 == 0 else ()))
    lx = lerp(300, 720, t / d)
    stick(ctx, lx, 1300, 1.0, face=1, outfit=('hoodie',), hunch=0.0, walk=t * 2.6, mouth='flat')
    ctx.restore()

def s3_02(ctx, t, d):
    ctx.save(); cam(ctx, lerp(1.0, 1.2, ease(t / d)), 540, 1050)
    env_cafeteria(ctx, t)
    table(ctx, 540, 1250, 640, top=hexc('6B5A2A'))
    person(ctx, 300, 1250, 0.7, face=1, outfit=('sunglasses', 'watch'), mouth='smile')
    person(ctx, 540, 1250, 0.85, cnt='25 000 €', face=0, outfit=('chain',), mouth='smirk')
    person(ctx, 760, 1250, 0.75, cnt='12 400 €', face=-1, outfit=('hair',), mouth='smile', gaze=(-0.5, 0))
    ctx.restore()
    o = ease(seg(t, 0.0, 1.0))
    if o < 1:
        rect(ctx, 0, 0, W / 2 * (1 - o), H, hexc('1C2545')); rect(ctx, W / 2 + W / 2 * o, 0, W / 2 * (1 - o), H, hexc('1C2545'))
    glow(ctx, 540, 960, 900, hexc('FFF2C8'), 0.6 * (1 - seg(t, 0.4, 1.6)))

def s3_03(ctx, t, d):
    ctx.save(); cam(ctx, lerp(1.0, 1.12, t / d), 540, 1020)
    env_cafeteria(ctx, t)
    rect(ctx, 880, 560, 220, 690, hexc('2A3A78'))
    person(ctx, 990, 1250, 0.62, face=-1, outfit=('cap', 'mop'), cnt='— — —', glitch=0.6, t=t, mouth='flat')
    turn = ease(seg(t, 0.8, 1.6))
    for i, x in enumerate((120, 260, 820)):
        stick(ctx, x, 1150, 0.55, face=1 if x < 540 else -1, gaze=(turn * (1 if x < 540 else -1) * 0.6, 0.3), mouth='o' if turn > 0.5 else None)
    point = ((-0.1, -0.05), (1.4, 1.5))
    person(ctx, 250, 1420, 1.15, face=1, cnt='25 000 €', outfit=('chain',), arms=point, mouth='laugh' if int(t * 7) % 2 and t < 3.4 else 'smirk')
    stick(ctx, 680, 1420, 1.05, face=-1, outfit=('hoodie',), hunch=0.0, mouth='flat')
    ctx.restore()

def s3_04(ctx, t, d):
    T = 2.5
    ctx.save()
    sh = (18 * math.exp(-(t - T) * 3) * math.sin(t * 70)) if t > T else 0
    cam(ctx, lerp(1.0, 1.15, ease(t / d)), 540, 1060, sx=sh, sy=sh * 0.6)
    env_cafeteria(ctx, t)
    dim = 0.55 * seg(t, 1.2, 1.6) * (1 - seg(t, T, T + 0.1))
    rect(ctx, -1200, -400, 3500, 3000, DARK, dim)
    if t > T:
        u = seg(t, T, T + 1.2)
        ctx.set_line_width(20 * (1 - u)); rgba(ctx, GOLD, 1 - u); ctx.arc(540, 820, 100 + 1100 * eout(u), 0, 2 * math.pi); ctx.stroke()
        glow(ctx, 540, 760, 700, GOLD, 0.65 * (1 - 0.6 * seg(t, T, d)))
    for i, x in enumerate((90, 230, 860, 1000)):
        k = seg(t, T, T + 0.4)
        stick(ctx, x, 1250, 0.7, face=1 if x < 540 else -1, mouth='o' if k > 0 else None, arms=((-0.1, 0), (lerp(0.1, 2.3, k), lerp(0.1, 2.6, k))) if k > 0 else None,
              gaze=((1 if x < 540 else -1) * 0.5, -0.5 * k))
        if k > 0: tray(ctx, x + 40, lerp(1150, 1240, ein(seg(t, T, T + 0.4))), 0.4 * k, food=False)
    person(ctx, 300, 1300, 0.85, face=1, cnt='25 000 €', outfit=('chain',), mouth='o' if t > T else 'smirk')
    raise_ = ease(seg(t, 0.2, 1.2))
    stick(ctx, 600, 1330, 1.05, face=0, outfit=('hoodie',), arms=((-0.1, -0.05), (lerp(0.15, 2.8, raise_), lerp(0.08, 3.0, raise_))), mouth='flat', gaze=(0, -0.2))
    if t > T:
        counter(ctx, 600, 800, '4 700 000 €', k=1.25, pop=popk(t, T) or 1)
    ctx.restore()
    if t > T: rect(ctx, 0, 0, W, H, WHITE, 0.9 * (1 - seg(t, T, T + 0.35)))

def s3_05(ctx, t, d):
    cut = 0 if t < 1.7 else (1 if t < 3.4 else 2)
    ctx.save()
    if cut == 0:
        cam(ctx, 2.1, 540, 830); env_cafeteria(ctx, t)
        person(ctx, 540, 1250, 1.0, face=0, outfit=('chain',), mouth='o', cnt='25 000 €', gaze=(0, -0.6))
    elif cut == 1:
        cam(ctx, 1.5, 540, 1020); env_cafeteria(ctx, t)
        for i, x in enumerate((300, 540, 780)):
            k = seg(t, 1.7 + i * 0.15, 2.2 + i * 0.15)
            info = stick(ctx, x, 1250, 0.85, face=0, mouth='o', arms=((-0.1, 0), (lerp(0.2, 2.2, k), lerp(0.1, 2.8, k))), gaze=(0, -0.4))
            if k > 0.3: phone(ctx, info['hand'][0], info['hand'][1] - 30, 0.8, glowa=0.5)
    else:
        cam(ctx, 1.6, 560, 1030); env_cafeteria(ctx, t)
        for i, x in enumerate((340, 760)):
            u = seg(t, 3.4 + i * 0.2, 4.2 + i * 0.2)
            stick(ctx, x, 1250, 0.9, face=-1 if x > 540 else 1, mouth='o', arms=((-0.1, 0), (1.2, 1.4)), gaze=(0, -0.3))
            tray(ctx, x + (40 if x < 540 else -40), lerp(1110, 1240, ein(u)), 0.8 * u, food=u < 0.4)
    ctx.restore()

def s3_06(ctx, t, d):
    fb = (4.0 <= t < 6.9)
    ctx.save()
    if not fb:
        u = ease(seg(t, 0, 3.4)) if t < 4 else 1.0
        cam(ctx, lerp(1.2, 1.45, ease(t / d)), 560, 1030)
        env_cafeteria(ctx, t)
        stick(ctx, 760, 1300, 1.0, face=-1, outfit=('hoodie',), mouth='flat')
        person(ctx, lerp(150, 430, u), 1300, 0.95, cnt='12 400 €', face=1, walk=t * 4 if u < 1 else None, outfit=('hair',), mouth='smile', gaze=(0.5, -0.2),
               arms=((-0.1, 0), (0.9, 1.4)) if u >= 1 and t > 7 else None)
    else:
        k = int((t - 4.0) / 0.97)
        cam(ctx, 1.3, 540, 1040)
        env_cafeteria(ctx, t)
        if k == 1:
            glow(ctx, 760, 1050, 380, GOLD, 0.35); rich_group(ctx, t, 760, 1200, 0.6)
            person(ctx, 280, 1300, 0.9, face=1, outfit=('hair',), gaze=(0.6, -0.4), mouth='smile')
        else:
            stick(ctx, 280 if k == 0 else 760, 1300, 0.9, face=1 if k == 0 else -1, pose='sit', outfit=('hoodie',), hunch=0.6, mouth='flat')
            person(ctx, lerp(900, 120, (t - 4.0 - k * 0.97) / 0.97) if k == 0 else lerp(150, 950, (t - 4 - k * 0.97) / 0.97), 1260, 0.85,
                   face=-1 if k == 0 else 1, walk=t * 6, outfit=('hair',), gaze=(0, -0.2), mouth='flat')
    ctx.restore()
    if fb:
        rect(ctx, 0, 0, W, H, hexc('6B5A8A'), 0.28)
        for i in range(0, H, 6): rect(ctx, 0, i, W, 2, DARK, 0.18)

def s3_07(ctx, t, d):
    ctx.save(); cam(ctx, lerp(1.3, 1.4, t / d), 560, 1030)
    env_cafeteria(ctx, t)
    for x in (120, 260, 900, 1020):
        stick(ctx, x, 1150, 0.6, face=1 if x < 540 else -1, mouth='flat', gaze=((1 if x < 540 else -1) * 0.6, 0.2), a=0.8)
    lx = lerp(720, 800, ease(seg(t, 0, 0.8)))
    stick(ctx, lx, 1300, 1.0, face=-1, outfit=('hoodie',), mouth='flat', walk=t * 3 if t < 0.8 else None)
    jit = (math.sin(t * 60) * 5 * seg(t, 2.0, 2.3)) if t > 2.0 else 0
    person(ctx, 430, 1300, 0.95, cnt='12 400 €', face=1, outfit=('hair',), mouth='o', arms=((-0.1, 0), (0.9, 1.3)), ck=None)
    ctx.restore()
    if t > 2.0:
        pass
    rect(ctx, 0, 0, W, H, hexc('2A4AA0'), 0.18)

def s3_08(ctx, t, d):
    ctx.save(); cam(ctx, lerp(1.4, 1.1, ease(t / d)), 540, 1050)
    env_corridor(ctx, t, night=True)
    rect(ctx, -1200, -400, 3600, 3000, DARK, 0.35)
    for i, x in enumerate((-100, 0, 1150, 1250)):
        stick(ctx, x, 1180, 0.5, face=1, a=0.18)
    info = stick(ctx, 540, 1270, 1.0, face=1, pose='sit', outfit=('hoodie',), hunch=0.6, gaze=(0.4, 0.6), arms=((0.7, 1.6), (0.8, 1.7)), mouth='flat')
    phone(ctx, info['hand'][0] + 10, info['hand'][1] - 10, 0.7, 0.3, glowa=0.8)
    ctx.restore()

def s3_09(ctx, t, d):
    ctx.save(); cam(ctx, lerp(1.5, 1.65, t / d), 540, 1000)
    env_corridor(ctx, t, night=True)
    rect(ctx, -1200, -400, 3600, 3000, DARK, 0.3)
    glow(ctx, 540, 700, 600, hexc('FFB25A'), 0.35)
    line(ctx, [(540, 0), (540, 520)], 3, hexc('39436E')); glow(ctx, 540, 540, 120, hexc('FFD58A'), 0.8)
    person(ctx, 400, 1270, 1.05, face=1, outfit=('cap', 'mop'), mouth='smile', arms=((-0.1, 0), (0.6, 0.7)))
    stick(ctx, 680, 1270, 1.0, face=-1, outfit=('hoodie',), mouth='flat', gaze=(0, -0.2))
    ctx.restore()

def s3_10(ctx, t, d):
    u = ease(seg(t, 0.2, 2.6))
    ctx.save(); cam(ctx, lerp(1.0, 1.35, ease(t / d)), lerp(540, 300, ease(t / d)), lerp(1050, 1200, ease(t / d)))
    env_cafeteria(ctx, t)
    glow(ctx, 900, 1000, 450, GOLD, 0.2); table(ctx, 900, 1130, 420, top=hexc('6B5A2A'))
    rich_group(ctx, t, 900, 1130, 0.55, cnts=False)
    table(ctx, 260, 1420, 300); trash(ctx, 470, 1420)
    person(ctx, 140, 1420, 0.8, face=1, pose='sit', outfit=('backpack',), hunch=0.4, cnt='0,00 €', mouth='flat' if t < 2 else 'smile', gaze=(0.5, 0.2 if t < 1.5 else 0))
    if u < 1:
        info = stick(ctx, lerp(1100, 380, u), 1420, 1.0, face=-1, outfit=('hoodie',), walk=t * 4.5, arms=((-0.1, 0), (1.1, 1.55)), mouth='smile')
        tray(ctx, info['hand'][0] - 20, info['hand'][1] - 6)
    else:
        stick(ctx, 380, 1420, 1.0, face=-1, pose='sit', outfit=('hoodie',), mouth='smile')
        tray(ctx, 300, 1336)
    ctx.restore()

def s3_11(ctx, t, d):
    T2 = d - 1.4
    if t < T2:
        ctx.save(); cam(ctx, lerp(1.35, 1.6, ease(t / T2)), 260, 1200)
        env_cafeteria(ctx, t)
        rect(ctx, -1200, -400, 3500, 3000, DARK, 0.35)
        glow(ctx, 260, 1200, 500, GOLD, 0.45)
        table(ctx, 260, 1420, 300); trash(ctx, 470, 1420)
        person(ctx, 140, 1420, 0.8, face=1, pose='sit', outfit=('backpack',), mouth='smile', gaze=(0.4, 0))
        m = seg(t, 0.9, 1.4)
        stick(ctx, 380, 1420, 1.0, face=-1, pose='sit', outfit=('hoodie',), mouth='smile')
        counter(ctx, 380, 1050, '4 700 000 €' if m < 0.5 else '1 AMI', k=1.0, pop=1 + 0.3 * math.sin(m * math.pi), a=1)
        tray(ctx, 260, 1336)
        ctx.restore()
    else:
        u = t - T2
        fill_bg(ctx, DARK)
        ctx.save(); cam(ctx, 1.4, 540, 900)
        glow(ctx, 540, 700, 500, GOLD, 0.25)
        stick(ctx, 540, 1250, 1.0, face=0, outfit=('cap', 'mop'), mouth='flat', gaze=(0, 0))
        counter(ctx, 540, 760, '— — —' if u < 0.55 else '89 JOURS', k=0.9, glitch=1.0 if u < 0.55 else 0.0, t=t, col=GOLD if u < 0.55 else RED)
        ctx.restore()
