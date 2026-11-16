import math, random, cairo, numpy as np
from gfx import *
BLACK = hexc('0A0A0F')
BX0, BY0, BW, BH = -420, -300, 1920, 2520   # cached background world rect

def quad(ctx, pts, c, a=1.0):
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path(); rgba(ctx, c, a); ctx.fill()

def label(ctx, s, x, y, size=26, fg=WHITE, bg=hexc('2A2A33'), a=1.0, mono=False):
    w = text_w(ctx, s, size, mono) + size * 1.2
    rrect(ctx, x - w / 2, y - size * 0.85, w, size * 1.7, 6); rgba(ctx, bg, a); ctx.fill()
    text(ctx, s, x, y, size, fg, a, mono=mono)

# ---------- perspective hallway ----------
def env_hall(ctx, night=False, t=0):
    vp = (540, 860)
    wall = hexc('20294A') if night else hexc('E6DCC3'); floor_c = hexc('141A30') if night else hexc('CBBE9E'); ceil = hexc('1A2140') if night else hexc('F1EBDD')
    L, R_, T, B = -420, 1500, -300, 2220
    bw, bh = 300, 380  # back wall size
    bx0, bx1, by0, by1 = vp[0] - bw / 2, vp[0] + bw / 2, vp[1] - bh * 0.62, vp[1] + bh * 0.38
    quad(ctx, [(L, T), (R_, T), (bx1, by0), (bx0, by0)], ceil)
    quad(ctx, [(L, B), (R_, B), (bx1, by1), (bx0, by1)], floor_c)
    quad(ctx, [(L, T), (bx0, by0), (bx0, by1), (L, B)], mix(wall, BLACK, 0.06))
    quad(ctx, [(R_, T), (bx1, by0), (bx1, by1), (R_, B)], mix(wall, BLACK, 0.1))
    rect(ctx, bx0, by0, bw, bh, mix(wall, WHITE, 0.08) if not night else mix(wall, BLACK, 0.2))
    # back door / window
    rect(ctx, vp[0] - 60, by1 - 190, 120, 190, hexc('8A6A4A') if not night else hexc('2A2440'))
    rect(ctx, vp[0] - 40, by1 - 170, 80, 60, hexc('BFE3FF') if not night else hexc('3A4A7A'))
    # floor tiles lines
    for i in range(-12, 13):
        x = vp[0] + i * 140
        ctx.move_to(lerp(bx0, bx1, (i + 12) / 24), by1); ctx.line_to(vp[0] + (x - vp[0]) * 9, B)
        ctx.set_line_width(2); rgba(ctx, BLACK, 0.06 if not night else 0.15); ctx.stroke()
    for k in range(1, 14):
        u = (k / 14) ** 2.2; y = lerp(by1, B, u)
        line(ctx, [(lerp(bx0, L, u * 1.0), y), (lerp(bx1, R_, u), y)], 2, BLACK, 0.05 if not night else 0.12)
    # ceiling lights
    for k in range(1, 7):
        u = (k / 7) ** 1.8; y = lerp(by0, T, u); hw = lerp(30, 260, u); hh = lerp(4, 40, u)
        quad(ctx, [(vp[0] - hw, y), (vp[0] + hw, y), (vp[0] + hw * 0.9, y + hh), (vp[0] - hw * 0.9, y + hh)], hexc('FFFDF0') if not night else hexc('3A4570'))
        if not night: glow(ctx, vp[0], y + hh, hw * 1.6, hexc('FFF6D8'), 0.25)
    # side walls: lockers, doors, boards (parametric along depth)
    cols = [hexc('2E8C8C'), hexc('D9A23B')] if not night else [hexc('1D4A55'), hexc('5A4A2A')]
    def wall_quad(side, u0, u1, v0, v1):
        # u: depth 0 (far) .. 1 (near) ; v: 0 (floor) .. 1 (ceiling) proportion of wall height
        def P(u, v):
            xe = L if side < 0 else R_
            xb = bx0 if side < 0 else bx1
            x = lerp(xb, xe, u)
            yf = lerp(by1, B, u); yc = lerp(by0, T, u)
            return (x, lerp(yf, yc, v))
        return [P(u0, v0), P(u1, v0), P(u1, v1), P(u0, v1)]
    for side in (-1, 1):
        segs = 26
        for k in range(segs):
            u0 = (k / segs) ** 2.0; u1 = ((k + 1) / segs) ** 2.0
            kind = (k + (0 if side < 0 else 3)) % 9
            if kind in (4,):  # door
                quad(ctx, wall_quad(side, u0, u1, 0, 0.62), hexc('8A6A4A') if not night else hexc('2E2640'))
                quad(ctx, wall_quad(side, u0 + (u1 - u0) * 0.2, u1 - (u1 - u0) * 0.2, 0.42, 0.56), hexc('BFE3FF') if not night else hexc('2A3A6A'))
            elif kind in (7,):  # notice board
                quad(ctx, wall_quad(side, u0, u1, 0.3, 0.58), hexc('7A5A3A'))
                quad(ctx, wall_quad(side, u0 + (u1 - u0) * 0.1, u1 - (u1 - u0) * 0.1, 0.34, 0.54), hexc('C9A57A') if not night else hexc('4A3A2A'))
                for j, cc in enumerate((hexc('F2F2F2'), hexc('E2709F'), hexc('8EC9FF'))):
                    uu = u0 + (u1 - u0) * (0.18 + j * 0.24)
                    quad(ctx, wall_quad(side, uu, uu + (u1 - u0) * 0.18, 0.38 + 0.04 * (j % 2), 0.5), cc, 0.9 if not night else 0.35)
            else:
                c = cols[k % 2]
                q = wall_quad(side, u0, u1, 0, 0.55)
                quad(ctx, q, c)
                ctx.move_to(*q[0]); ctx.line_to(*q[3]); ctx.set_line_width(max(1, 3 * u1)); rgba(ctx, BLACK, 0.25); ctx.stroke()
                for vv in (0.42, 0.45, 0.48):
                    a_ = wall_quad(side, u0 + (u1 - u0) * 0.25, u1 - (u1 - u0) * 0.25, vv, vv + 0.008)
                    quad(ctx, a_, BLACK, 0.3)
        # baseboard
        quad(ctx, wall_quad(side, 0, 1, 0, 0.03), BLACK, 0.2)
    if not night:
        glow(ctx, 540, 900, 900, hexc('FFF2D0'), 0.12)

# ---------- cafeteria ----------
def env_cafe(ctx, night=False, warm=True):
    wall = hexc('BFD6D9'); floor_c = hexc('C9B591')
    rect(ctx, BX0, BY0, BW, 1520 - BY0, wall)
    rect(ctx, BX0, 1060, BW, 40, hexc('9DB9BD'))   # dado rail
    rect(ctx, BX0, 1100, BW, 300, hexc('A9C5C8'))
    # windows with sunlight
    for i in range(-1, 6):
        wx = i * 300 + 20
        rect(ctx, wx, 420, 220, 420, hexc('FFFFFF'))
        vgrad(ctx, wx + 10, 430, 200, 400, hexc('9ED3FF'), hexc('DDF1FF'))
        line(ctx, [(wx + 110, 430), (wx + 110, 830)], 8, WHITE); line(ctx, [(wx + 10, 630), (wx + 210, 630)], 8, WHITE)
        quad(ctx, [(wx + 10, 830), (wx + 210, 830), (wx + 420, 1400), (wx + 180, 1400)], hexc('FFF6D8'), 0.18)
    # menu board + serving counter at left
    rect(ctx, -380, 300, 340, 220, hexc('2A3A2E')); ctx.set_line_width(10); rgba(ctx, hexc('7A5A3A')); ctx.rectangle(-380, 300, 340, 220); ctx.stroke()
    text(ctx, "MENU DU JOUR", -210, 345, 30, WHITE); text(ctx, "Steak frites", -210, 400, 24, hexc('F2E6B8'), cond=0.9, bold=False)
    text(ctx, "Yaourt · Pomme", -210, 440, 24, hexc('F2E6B8'), cond=0.9, bold=False); text(ctx, "3,50 €", -210, 485, 30, GOLD)
    # clock
    ctx.arc(1280, 360, 60, 0, 2 * math.pi); rgba(ctx, WHITE); ctx.fill(); ctx.set_line_width(8); rgba(ctx, hexc('333333')); ctx.arc(1280, 360, 60, 0, 2 * math.pi); ctx.stroke()
    line(ctx, [(1280, 360), (1280, 320)], 6, hexc('222222')); line(ctx, [(1280, 360), (1308, 372)], 6, hexc('222222'))
    # floor
    vgrad(ctx, BX0, 1400 - 150, BW, 1200, floor_c, mix(floor_c, BLACK, 0.25))
    for i in range(-10, 30):
        line(ctx, [(i * 110 - 400, 1250), (i * 110 - 700, 2300)], 2, BLACK, 0.06)
    for k in range(12):
        y = 1250 + (k ** 1.6) * 18
        line(ctx, [(BX0, y), (BX0 + BW, y)], 2, BLACK, 0.05)
    # vending machine right
    rect(ctx, 1260, 700, 200, 560, hexc('C8323A')); rect(ctx, 1280, 730, 120, 360, hexc('1A1A22'))
    for r in range(5):
        for c in range(3): rect(ctx, 1290 + c * 38, 745 + r * 68, 28, 50, [hexc('E0A23B'), hexc('4F86C6'), hexc('5BB08A')][(r + c) % 3])
    text(ctx, "SNACK", 1360, 1140, 40, WHITE)

# ---------- classroom ----------
def env_class(ctx, board="ÉCONOMIE · CH. 3"):
    sub = "L'ARGENT, ÇA SE GARDE !" if board.startswith('ÉPARGNEZ') else "OFFRE  ↗   DEMANDE  ↘"
    rect(ctx, BX0, BY0, BW, 1300 - BY0, hexc('EADFB8'))
    rect(ctx, BX0, 1080, BW, 220, hexc('D9C99A'))
    rect(ctx, 80, 380, 900, 420, hexc('2D4A3A')); ctx.set_line_width(16); rgba(ctx, hexc('8A6A4A')); ctx.rectangle(80, 380, 900, 420); ctx.stroke()
    text(ctx, board, 530, 470, 56, hexc('EFEFE6'), 0.92)
    text(ctx, sub, 530, 580, 40, hexc('EFEFE6'), 0.8, bold=False)
    line(ctx, [(300, 740), (420, 640), (540, 690), (680, 600), (800, 650)], 5, hexc('EFEFE6'), 0.7)
    for i, (x, c) in enumerate(((1080, hexc('4F86C6')), (1200, hexc('5BB08A')), (-150, hexc('E0A23B')))):
        rect(ctx, x, 420, 90, 120, c); rect(ctx, x + 12, 432, 66, 40, WHITE, 0.6)
    ctx.arc(-260, 380, 55, 0, 2 * math.pi); rgba(ctx, WHITE); ctx.fill(); ctx.set_line_width(7); rgba(ctx, hexc('333333')); ctx.arc(-260, 380, 55, 0, 2 * math.pi); ctx.stroke()
    for wx in (1100, 1350):
        rect(ctx, wx - 60, 620, 200, 330, WHITE); vgrad(ctx, wx - 50, 630, 180, 310, hexc('9ED3FF'), hexc('DDF1FF'))
    vgrad(ctx, BX0, 1300, BW, 1000, hexc('B58E62'), hexc('8A6A4A'))
    for i in range(-6, 20): line(ctx, [(BX0, 1300 + i * 60), (BX0 + BW, 1300 + i * 60)], 2, BLACK, 0.06)

# ---------- courtyard ----------
def env_court(ctx):
    vgrad(ctx, BX0, BY0, BW, 1300, hexc('7FB8F0'), hexc('D7ECFF'))
    for cx, cy, r in ((150, 260, 70), (260, 240, 90), (380, 270, 60), (900, 200, 80), (1000, 220, 60)):
        ctx.arc(cx, cy, r, 0, 2 * math.pi); rgba(ctx, WHITE, 0.85); ctx.fill()
    rect(ctx, -300, 520, 1680, 760, hexc('E3C9A0'))
    rect(ctx, -300, 500, 1680, 40, hexc('B9533F'))
    rect(ctx, 290, 560, 500, 90, hexc('2A3A6A')); text(ctx, "LYCÉE VICTOR-LAMBERT", 540, 605, 44, WHITE)
    for r in range(3):
        for c in range(11):
            wx = -260 + c * 150; wy = 700 + r * 170
            if 330 < wx < 700 and r == 2: continue
            rect(ctx, wx, wy, 90, 110, hexc('FFFFFF')); vgrad(ctx, wx + 6, wy + 6, 78, 98, hexc('8EC0E8'), hexc('CFE6F8'))
    rect(ctx, 460, 1060, 160, 220, hexc('6B4A2E')); rect(ctx, 470, 1070, 65, 200, hexc('8A6A4A')); rect(ctx, 545, 1070, 65, 200, hexc('8A6A4A'))
    rect(ctx, BX0, 1280, BW, 1100, hexc('BFB6A3'))
    for i in range(-10, 30): line(ctx, [(i * 120 - 400, 1280), (i * 120 - 800, 2300)], 2, BLACK, 0.06)
    for tx in (-200, 1260):
        rect(ctx, tx - 16, 950, 32, 340, hexc('6B4A2E'))
        for dx, dy, r in ((0, 860, 150), (-90, 930, 100), (90, 930, 100)):
            ctx.arc(tx + dx, dy, r, 0, 2 * math.pi); rgba(ctx, hexc('4F9A5A')); ctx.fill()

# ---------- bedroom (night) ----------
def env_bedroom(ctx):
    vgrad(ctx, BX0, BY0, BW, 1600, hexc('1A2142'), hexc('11162E'))
    rect(ctx, 620, 380, 340, 420, hexc('2E3963')); vgrad(ctx, 632, 392, 316, 396, hexc('0E1736'), hexc('1F2C5A'))
    rnd = random.Random(3)
    for i in range(10):
        bx = 640 + i * 32; bh = rnd.uniform(60, 220); rect(ctx, bx, 788 - bh, 28, bh, hexc('0A1028'))
        for k in range(int(bh / 30)):
            if rnd.random() < 0.4: rect(ctx, bx + 8, 788 - bh + 10 + k * 30, 8, 10, GOLD, 0.6)
    ctx.arc(890, 450, 30, 0, 2 * math.pi); rgba(ctx, hexc('F2F2E6')); ctx.fill()
    line(ctx, [(790, 380), (790, 800)], 10, hexc('2E3963')); line(ctx, [(620, 590), (960, 590)], 10, hexc('2E3963'))
    for i, (px, c, ang) in enumerate(((120, hexc('C8323A'), -0.05), (300, hexc('4F86C6'), 0.04))):
        ctx.save(); ctx.translate(px, 520); ctx.rotate(ang); rect(ctx, -70, -100, 140, 200, c, 0.55); rect(ctx, -50, -70, 100, 60, WHITE, 0.3); ctx.restore()
    rect(ctx, BX0, 1300, BW, 1100, hexc('0C1022'))
    for i in range(-10, 30): line(ctx, [(i * 120 - 400, 1300), (i * 120 - 800, 2300)], 2, WHITE, 0.03)

def bed(ctx, x, y, w=620):
    rect(ctx, x, y - 120, w, 70, hexc('3A4A8A')); rect(ctx, x, y - 50, w, 50, hexc('2A3460'))
    rect(ctx, x - 20, y - 230, 30, 230, hexc('2A3460')); rrect(ctx, x + 20, y - 160, 160, 48, 18); rgba(ctx, hexc('DADFF0')); ctx.fill()

def letters(ctx, x, y, n=7, t=0, stamps=0):
    rnd = random.Random(11)
    for i in range(n):
        ox = (rnd.random() - 0.5) * 140; oy = -i * 9; ang = (rnd.random() - 0.5) * 0.4
        ctx.save(); ctx.translate(x + ox, y + oy); ctx.rotate(ang)
        rect(ctx, -60, -40, 120, 80, hexc('F4F1E6')); rect(ctx, -60, -40, 120, 18, hexc('C8323A'))
        text(ctx, "RELANCE", 0, -31, 14, WHITE)
        for k in range(3): rect(ctx, -46, -10 + k * 14, 80 - k * 15, 5, hexc('9A9A9A'))
        if i < stamps:
            ctx.save(); ctx.rotate(-0.3); rrect(ctx, -52, -6, 104, 36, 5); ctx.set_line_width(4); rgba(ctx, hexc('2E9B4A')); ctx.stroke()
            text(ctx, "PAYÉ", 0, 12, 26, hexc('2E9B4A')); ctx.restore()
        ctx.restore()

# ---------- boiler room ----------
def env_boiler(ctx):
    vgrad(ctx, BX0, BY0, BW, 1600, hexc('3A2A24'), hexc('1A1210'))
    glow(ctx, 540, 760, 900, hexc('FF8A3D'), 0.28)
    for i, (y, w) in enumerate([(360, 46), (450, 30), (540, 38)]):
        line(ctx, [(BX0, y), (BX0 + BW, y)], w, hexc('6A4A3A')); line(ctx, [(BX0, y - w * 0.25), (BX0 + BW, y - w * 0.25)], w * 0.25, hexc('8A6A54'))
        for k in range(-3, 12): rect(ctx, k * 190 + i * 40, y - w / 2 - 6, 18, w + 12, hexc('7A5A44'))
    for x in (120, 960):
        rect(ctx, x - 110, 640, 220, 640, hexc('4A3A32')); rect(ctx, x - 110, 640, 220, 30, hexc('6A5244'))
        ctx.arc(x, 820, 52, 0, 2 * math.pi); rgba(ctx, hexc('E8E2D0')); ctx.fill(); ctx.set_line_width(8); rgba(ctx, hexc('2A2020')); ctx.arc(x, 820, 52, 0, 2 * math.pi); ctx.stroke()
        line(ctx, [(x, 820), (x + 30, 790)], 5, RED)
        for k in range(4): rect(ctx, x - 80 + k * 46, 1000, 26, 26, hexc('2A2020'))
    rect(ctx, BX0, 1280, BW, 1100, hexc('241A16'))
    rect(ctx, 400, 1150, 280, 130, hexc('5A4636')); text(ctx, "DANGER", 540, 1215, 34, hexc('F2D23B'))

# ---------- rooftop (night) ----------
def env_roof(ctx):
    vgrad(ctx, BX0, BY0, BW, 1700, hexc('070B1E'), hexc('2A2F6A'))
    rnd = random.Random(5)
    for i in range(90):
        ctx.arc(rnd.uniform(BX0, BX0 + BW), rnd.uniform(BY0, 650), rnd.uniform(1, 3), 0, 2 * math.pi); rgba(ctx, WHITE, rnd.uniform(0.3, 0.9)); ctx.fill()
    ctx.arc(860, 340, 70, 0, 2 * math.pi); rgba(ctx, hexc('F4F1E0')); ctx.fill(); glow(ctx, 860, 340, 260, hexc('BFD0FF'), 0.25)
    for layer, (base, col, dens) in enumerate(((1160, hexc('141A3A'), 0.25), (1280, hexc('0C1028'), 0.4))):
        x = BX0
        while x < BX0 + BW:
            bw = rnd.uniform(70, 160); bh = rnd.uniform(160, 520) * (1.2 - layer * 0.3)
            rect(ctx, x, base - bh, bw, bh + 400, col)
            for k in range(int(bh / 40)):
                for m in range(int(bw / 28)):
                    if rnd.random() < dens: rect(ctx, x + 8 + m * 28, base - bh + 14 + k * 40, 12, 16, GOLD, rnd.uniform(0.35, 0.9))
            x += bw + 6
    glow(ctx, 540, 1300, 900, GOLD, 0.15)
    rect(ctx, BX0, 1280, BW, 1100, hexc('1A1E33')); rect(ctx, BX0, 1270, BW, 26, hexc('3A4066'))

# ---------- bathroom (mirror) ----------
def env_bath(ctx):
    rect(ctx, BX0, BY0, BW, 2600, hexc('DCE6EA'))
    for i in range(-10, 40):
        line(ctx, [(BX0, i * 80), (BX0 + BW, i * 80)], 2, hexc('B9C6CC'))
        line(ctx, [(BX0 + i * 80, BY0), (BX0 + i * 80, 2300)], 2, hexc('B9C6CC'))
    rect(ctx, BX0, 1280, BW, 1100, hexc('8A9AA2'))

def blur_surface(surf, sigma):
    if sigma <= 0: return surf
    from scipy.ndimage import gaussian_filter
    w, h = surf.get_width(), surf.get_height()
    a = np.ndarray((h, w, 4), np.uint8, surf.get_data(), strides=(surf.get_stride(), 4, 1)).copy()
    for c in range(3): a[..., c] = gaussian_filter(a[..., c], sigma)
    out = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
    b = np.ndarray((h, w, 4), np.uint8, out.get_data(), strides=(out.get_stride(), 4, 1)); b[:] = a; out.mark_dirty()
    return out

_CACHE = {}
def bg(ctx, name, fn, sigma=2.5, **kw):
    key = (name, sigma, tuple(sorted(kw.items())))
    if key not in _CACHE:
        surf = cairo.ImageSurface(cairo.FORMAT_RGB24, BW, BH); c = cairo.Context(surf); c.translate(-BX0, -BY0)
        fn(c, **kw); surf.flush()
        _CACHE[key] = blur_surface(surf, sigma)
    ctx.save(); ctx.set_source_surface(_CACHE[key], BX0, BY0); ctx.get_source().set_filter(cairo.FILTER_BILINEAR); ctx.paint(); ctx.restore()

# ---------- business district (day) ----------
def env_street(ctx):
    vgrad(ctx, BX0, BY0, BW, 1500, hexc('8EC5F2'), hexc('E3F1FF'))
    rnd = random.Random(21)
    x = BX0
    while x < BX0 + BW:
        bw = rnd.uniform(160, 300); bh = rnd.uniform(700, 1300); col = rnd.choice([hexc('5C7FA8'), hexc('6F93B8'), hexc('4E6E94'), hexc('8AA6C4')])
        rect(ctx, x, 1300 - bh, bw, bh, col)
        for k in range(int(bh / 70)):
            for m in range(int(bw / 46)):
                rect(ctx, x + 12 + m * 46, 1300 - bh + 20 + k * 70, 30, 46, hexc('CFE6F8') if (k + m) % 3 else hexc('A9CDEB'), 0.85)
        x += bw + 18
    rect(ctx, BX0, 1240, BW, 60, hexc('B9B4AA'))
    rect(ctx, BX0, 1300, BW, 1100, hexc('8F8A80'))
    for i in range(-10, 30): line(ctx, [(i * 160 - 400, 1300), (i * 160 - 800, 2300)], 2, BLACK, 0.06)
    for lx in (-200, 500, 1200):
        rect(ctx, lx - 8, 820, 16, 480, hexc('3A3F4B')); rrect(ctx, lx - 40, 800, 80, 26, 10); rgba(ctx, hexc('3A3F4B')); ctx.fill()
