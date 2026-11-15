import math, cairo
from gfx import *

OUT = WHITE  # outline colour
BLACK = hexc('0A0A0F')
SKIN = BLACK
CHARS = {
    'leo':    dict(shirt=hexc('8C909C'), shirt2=hexc('6F7380'), pants=hexc('2B3040'), shoes=hexc('D9D9D9'), hair='messy', hood=True, patch=True),
    'ines':   dict(shirt=hexc('E2709F'), shirt2=hexc('C25683'), pants=hexc('3A3F6B'), shoes=hexc('F2F2F2'), hair='long', haircol=hexc('C98A4B')),
    'maxime': dict(shirt=hexc('C8323A'), shirt2=hexc('9E2229'), pants=hexc('1E2233'), shoes=hexc('F2F2F2'), hair='quiff', chain=True, watch=True),
    'theo':   dict(shirt=hexc('E8E8EE'), shirt2=hexc('C9C9D2'), pants=hexc('2F3B57'), shoes=hexc('8A5A3A'), hair='short', glasses=True, watch=True),
    'chloe':  dict(shirt=hexc('8B5BD6'), shirt2=hexc('6C42B0'), pants=hexc('22263A'), shoes=hexc('F2F2F2'), hair='pony', haircol=hexc('E8C46A'), watch=True),
    'armand': dict(shirt=hexc('2F4A7A'), shirt2=hexc('22385E'), pants=hexc('2F4A7A'), shoes=hexc('3A2A20'), hair='cap', mustache=True),
    'samy':   dict(shirt=hexc('3E9B6B'), shirt2=hexc('2E7A53'), pants=hexc('2B3040'), shoes=hexc('E0E0E0'), hair='curly', backpack=True),
}
EXTRA_COLS = [hexc(c) for c in ('4F86C6', 'E0A23B', '5BB08A', 'D9644A', '9A6FD1', '3FA7A3', 'C75B8E', '7C8B3A')]
def extra(i):
    return dict(shirt=EXTRA_COLS[i % 8], shirt2=mix(EXTRA_COLS[i % 8], BLACK, 0.25), pants=hexc(['2B3040', '3A3F6B', '22263A'][i % 3]), shoes=hexc('E6E6E6'),
                hair=['short', 'long', 'curly', 'pony', 'messy'][i % 5], haircol=[hexc('C98A4B'), hexc('6B3E22'), hexc('E8C46A')][i % 3])

ARMS = {  # (upper, lower) angles from straight down, screen space for facing right; mirrored for left
    'rest': ((0.10, 0.04), (-0.10, -0.04)),
    'point': ((1.50, 1.55), (-0.12, -0.05)),
    'raise': ((2.95, 3.05), (-0.12, -0.05)),
    'wave': ((2.5, 2.9), (-0.12, -0.05)),
    'hold': ((0.75, 1.65), (0.55, 1.55)),
    'phone': ((0.55, 2.7), (-0.12, -0.05)),
    'cross': ((0.35, -1.45), (-0.35, 1.45)),
    'pocket': ((0.16, -0.25), (-0.16, 0.25)),
    'shrug': ((0.9, -0.5), (-0.9, 0.5)),
    'head': ((2.3, -2.4), (-2.3, 2.4)),
    'reach': ((1.2, 1.3), (1.0, 1.15)),
    'give': ((1.25, 1.45), (-0.12, -0.05)),
    'shoulder': ((1.45, 1.75), (-0.12, -0.05)),
    'fist': ((2.6, 3.1), (-2.6, -3.1)),
    'mop': ((0.45, 1.2), (-0.1, 0.9)),
}

class Shapes:
    def __init__(self): self.items = []
    def seg(self, a, b, w, c): self.items.append(('seg', a, b, w, c))
    def poly(self, pts, c): self.items.append(('poly', pts, c))
    def circ(self, p, r, c): self.items.append(('circ', p, r, c))
    def draw(self, ctx, ow, alpha):
        for pass_ in (0, 1):
            for it in self.items:
                k = it[0]
                if k == 'seg':
                    _, a, b, w, c = it
                    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.move_to(*a); ctx.line_to(*b)
                    ctx.set_line_width(w + (2 * ow if pass_ == 0 else 0)); rgba(ctx, OUT if pass_ == 0 else c, alpha); ctx.stroke()
                elif k == 'poly':
                    _, pts, c = it
                    ctx.move_to(*pts[0])
                    for p in pts[1:]: ctx.line_to(*p)
                    ctx.close_path(); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
                    if pass_ == 0:
                        ctx.set_line_width(2 * ow); rgba(ctx, OUT, alpha); ctx.stroke_preserve(); ctx.fill()
                    else:
                        rgba(ctx, c, alpha); ctx.fill()
                elif k == 'circ':
                    _, p, r, c = it
                    ctx.arc(p[0], p[1], r + (ow if pass_ == 0 else 0), 0, 2 * math.pi); rgba(ctx, OUT if pass_ == 0 else c, alpha); ctx.fill()

def Pt(o, ang, L): return (o[0] + math.sin(ang) * L, o[1] + math.cos(ang) * L)

def draw_char(ctx, who, x, y, s=1.0, face=0.0, pose='stand', arms='rest', walk=None, eyes='normal', mouth='flat', gaze=(0, 0),
              brows=None, lean=0.0, alpha=1.0, blink=False, armsL=None, head_tilt=0.0, hold=None, ow=3.2, sweat=False, tears=0.0, bob=0.0):
    """face: -1 (looking left) .. 0 (front) .. 1 (looking right). Returns anchor dict in world coords."""
    C = CHARS[who] if isinstance(who, str) else who
    if alpha <= 0.01: return None
    f = 1 if face >= 0 else -1
    af = abs(face)
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    sh = Shapes()
    R = 46; thigh = 86; shin = 84; torso = 132
    hipw = lerp(15, 7, af)
    # ---------- legs ----------
    if pose == 'sit':
        hip = (0, -108)
        legs = []
        for i, dx in enumerate((-hipw, hipw)):
            h = (hip[0] + dx * 0.5, hip[1]); k = (h[0] + f * 80, h[1] + 4); ft = (k[0] + f * (6 - i * 10), k[1] + shin)
            legs.append((h, k, ft))
    elif pose == 'kneel':
        hip = (0, -98)
        legs = [((hip[0] - f * 4, hip[1]), (-f * 10, -10), (-f * 92, -6)), ((hip[0] + f * 4, hip[1]), (f * 84, -84), (f * 86, -2))]
        lean = max(lean, 0.32)
    elif pose == 'lie':
        hip = (0, -170)
        legs = [((-hipw, hip[1]), (-hipw, -84), (-hipw - 2, 0)), ((hipw, hip[1]), (hipw, -84), (hipw + 2, 0))]
    else:
        if walk is not None:
            sw = math.sin(walk); b = abs(math.cos(walk)) * 7
            hip = (0, -thigh - shin + b)
            legs = []
            for i, (dx, sg) in enumerate(((-hipw, 1), (hipw, -1))):
                a1 = 0.42 * sw * sg
                kb = 0.45 * max(0, -math.sin(walk * sg + 0.9) if sg > 0 else math.sin(walk + 0.9 + math.pi))
                h = (hip[0] + dx * 0.4, hip[1]); k = Pt(h, f * a1, thigh); ft = Pt(k, f * (a1 - kb), shin)
                legs.append((h, k, ft))
        else:
            hip = (0, -thigh - shin)
            legs = []
            for dx in (-hipw, hipw):
                h = (dx, hip[1]); k = (dx * 1.12, hip[1] + thigh); ft = (dx * 1.22, 0)
                legs.append((h, k, ft))
    lean_r = lean * 0.3
    neck = (hip[0] + math.sin(lean_r) * f * torso, hip[1] - math.cos(lean_r) * torso)
    hd = (neck[0] + math.sin(lean_r * 1.5 + head_tilt) * f * (R + 6), neck[1] - math.cos(lean_r * 1.5 + head_tilt) * (R + 6) + bob)
    shw = lerp(30, 12, af)
    shL = (neck[0] - shw, neck[1] + 12); shR = (neck[0] + shw, neck[1] + 12)
    # arms
    A = ARMS.get(arms, ARMS['rest']) if isinstance(arms, str) else arms
    if walk is not None and arms == 'rest':
        swg = math.sin(walk) * 0.5
        A = ((-swg * f + 0.08, -swg * f * 0.5 + 0.35 * f * 0.0), (swg * f - 0.08, swg * f * 0.5))
    if armsL is not None: A = (A[0], armsL)
    # facing: first entry is the 'front' arm (towards facing direction)
    front_sh = shR if f > 0 else shL; back_sh = shL if f > 0 else shR
    def arm(shp, ang):
        ua, la = ang
        e = Pt(shp, f * ua, 64); hnd = Pt(e, f * la, 62); return e, hnd
    eF, hF = arm(front_sh, A[0]); eB, hB = arm(back_sh, A[1])
    # ---------- build shapes ----------
    if C.get('backpack'):
        bx = neck[0] - f * 36; by = lerp(neck[1], hip[1], 0.42)
        sh.poly([(bx - 26, by - 52), (bx + 26, by - 52), (bx + 30, by + 50), (bx - 30, by + 50)], hexc('C9862E'))
    if C.get('hair') == 'long':
        hc = C['haircol']
        pts = []
        for i in range(0, 181, 12):  # top arc
            a_ = math.radians(180 + i)
            pts.append((hd[0] + math.cos(a_) * R * 1.16, hd[1] + math.sin(a_) * R * 1.16))
        for i in range(0, 11):  # right side down, flaring
            u = i / 10
            pts.append((hd[0] + R * (1.16 + 0.12 * math.sin(u * 3.14)), hd[1] + u * R * 1.75))
        for i in range(0, 9):  # rounded bottom
            u = i / 8
            pts.append((hd[0] + R * 1.16 * math.cos(u * 3.14) , hd[1] + R * 1.75 + math.sin(u * 3.14) * R * 0.18))
        for i in range(10, -1, -1):
            u = i / 10
            pts.append((hd[0] - R * (1.16 + 0.12 * math.sin(u * 3.14)), hd[1] + u * R * 1.75))
        sh.poly(pts, hc)
    if C.get('hood'):
        sh.circ((hd[0] - f * 8 * (1 - af * 0.3), hd[1] + 18), R + 8, C['shirt2'])
    # back arm
    sh.seg(back_sh, eB, 21, C['shirt2']); sh.seg(eB, hB, 15, BLACK); sh.circ(hB, 10, BLACK)
    # legs
    for (h, k, ft) in legs:
        sh.seg(h, k, 24, C['pants']); sh.seg(k, ft, 21, C['pants'])
        sh.poly([(ft[0] - 12 + f * 0, ft[1] - 10), (ft[0] + f * 26, ft[1] - 8), (ft[0] + f * 28, ft[1] + 4), (ft[0] - 13, ft[1] + 4)], C['shoes'])
    # torso
    tw_top = lerp(34, 20, af); tw_bot = lerp(28, 18, af)
    sh.poly([(neck[0] - tw_top, neck[1] + 6), (neck[0] + tw_top, neck[1] + 6), (hip[0] + tw_bot, hip[1] + 14), (hip[0] - tw_bot, hip[1] + 14)], C['shirt'])
    # neck + head
    sh.seg(neck, (hd[0], hd[1] + R * 0.6), 14, BLACK)
    sh.circ(hd, R, BLACK)
    hs = C.get('hair')
    if hs == 'messy':
        for i, a in enumerate((-2.4, -1.9, -1.4, -0.9, -0.4)):
            p = (hd[0] + math.cos(a) * R * 0.95, hd[1] + math.sin(a) * R * 0.95); q = (hd[0] + math.cos(a + 0.25) * (R + 14), hd[1] + math.sin(a + 0.25) * (R + 14))
            r_ = (hd[0] + math.cos(a + 0.5) * R * 0.95, hd[1] + math.sin(a + 0.5) * R * 0.95)
            sh.poly([p, q, r_], BLACK)
    elif hs == 'quiff':
        sh.poly([(hd[0] - R * 0.8, hd[1] - R * 0.6), (hd[0] + f * R * 0.2, hd[1] - R * 1.45), (hd[0] + f * R * 1.05, hd[1] - R * 1.1), (hd[0] + R * 0.85, hd[1] - R * 0.5)], BLACK)
    elif hs == 'curly':
        for i in range(7):
            a = -math.pi + i * math.pi / 6
            sh.circ((hd[0] + math.cos(a) * R * 0.92, hd[1] + math.sin(a) * R * 0.92), 15, BLACK)
    elif hs == 'pony':
        sh.circ((hd[0] - f * R * 1.05, hd[1] - R * 0.3), 18, C['haircol'])
        sh.poly([(hd[0] - f * R * 1.1, hd[1] - R * 0.2), (hd[0] - f * R * 1.55, hd[1] + R * 0.9), (hd[0] - f * R * 1.0, hd[1] + R * 0.8)], C['haircol'])
    elif hs == 'short':
        sh.poly([(hd[0] - R * 0.95, hd[1] - R * 0.35), (hd[0] - R * 0.6, hd[1] - R * 1.08), (hd[0] + R * 0.6, hd[1] - R * 1.08), (hd[0] + R * 0.95, hd[1] - R * 0.35)], BLACK)
    # front arm
    sh.seg(front_sh, eF, 22, C['shirt']); sh.seg(eF, hF, 16, BLACK); sh.circ(hF, 10.5, BLACK)
    sh.draw(ctx, ow, alpha)
    # ---------- details (no outline) ----------
    hx, hy = hd
    if C.get('hood'):
        # hoodie strings + pocket + worn patch
        line(ctx, [(neck[0] - 9, neck[1] + 12), (neck[0] - 10, neck[1] + 48)], 4, hexc('E6E6E6'), alpha)
        line(ctx, [(neck[0] + 9, neck[1] + 12), (neck[0] + 10, neck[1] + 44)], 4, hexc('E6E6E6'), alpha)
        rrect(ctx, hip[0] - 22, hip[1] - 44, 44, 32, 8); rgba(ctx, C['shirt2'], alpha); ctx.fill()
        if C.get('patch'):
            rrect(ctx, neck[0] + f * 8, neck[1] + 60, 14, 12, 3); rgba(ctx, hexc('5B5F6B'), alpha); ctx.fill()
            line(ctx, [(neck[0] - 20, neck[1] + 80), (neck[0] - 12, neck[1] + 86)], 2.5, hexc('5B5F6B'), alpha)
    if C.get('chain'):
        ctx.set_line_width(6); rgba(ctx, GOLD, alpha); ctx.arc(neck[0], neck[1] + 6, 26, 0.15 * math.pi, 0.85 * math.pi); ctx.stroke()
        ctx.arc(neck[0], neck[1] + 34, 7, 0, 2 * math.pi); ctx.fill()
        # jacket zip
        line(ctx, [(neck[0], neck[1] + 40), (hip[0], hip[1] + 10)], 3, C['shirt2'], alpha)
    if who == 'armand' or C is CHARS.get('armand'):
        rect(ctx, neck[0] - 18, neck[1] + 30, 36, 26, C['shirt2'], alpha)
        line(ctx, [(neck[0] - 18, neck[1] + 8), (neck[0] - 16, neck[1] + 32)], 4, hexc('C9A64A'), alpha)
        line(ctx, [(neck[0] + 18, neck[1] + 8), (neck[0] + 16, neck[1] + 32)], 4, hexc('C9A64A'), alpha)
    if C.get('watch'):
        wx, wy = lerp(eF[0], hF[0], 0.78), lerp(eF[1], hF[1], 0.78)
        ctx.arc(wx, wy, 8, 0, 2 * math.pi); rgba(ctx, GOLD, alpha); ctx.fill()
    if C.get('hair') == 'long':  # fringe on top of head
        ctx.save(); ctx.arc(hx, hy, R + 1, 0, 2 * math.pi); ctx.clip()
        ctx.move_to(hx - R * 1.1, hy - R * 0.2); ctx.curve_to(hx - R * 0.6, hy - R * 0.55, hx + f * R * 0.2, hy - R * 0.45, hx + f * R * 0.5, hy - R * 0.9)
        ctx.curve_to(hx + R * 0.9, hy - R * 0.5, hx + R * 1.1, hy - R * 0.2, hx + R * 1.2, hy - R * 0.1); ctx.line_to(hx + R * 1.2, hy - R * 1.3); ctx.line_to(hx - R * 1.2, hy - R * 1.3); ctx.close_path()
        rgba(ctx, C['haircol'], alpha); ctx.fill(); ctx.restore()
    if C.get('hair') == 'cap':
        ctx.arc(hx, hy - 6, R + 3, math.pi, 2 * math.pi); ctx.close_path(); rgba(ctx, hexc('2F4A7A'), alpha); ctx.fill()
        line(ctx, [(hx, hy - 8), (hx + f * (R + 30) * max(af, 0.4) + (0 if af > 0.2 else 0), hy - 6)], 10, hexc('2F4A7A'), alpha)
        rect(ctx, hx - 10, hy - R + 4, 20, 10, hexc('C9A64A'), alpha)
    # ---------- face ----------
    fx = hx + face * 16; fy = hy + 2
    gx, gy = gaze
    sep = lerp(17, 12, af)
    e1 = (fx - sep, fy - 4); e2 = (fx + sep, fy - 4)
    if C.get('glasses'):
        for e in (e1, e2): rrect(ctx, e[0] - 13, e[1] - 9, 26, 18, 6); rgba(ctx, hexc('1A1A22'), alpha); ctx.fill_preserve(); ctx.set_line_width(2); rgba(ctx, WHITE, alpha * 0.8); ctx.stroke()
        line(ctx, [(e1[0] + 13, e1[1]), (e2[0] - 13, e2[1])], 3, WHITE, alpha * 0.8)
    elif blink or eyes == 'closed':
        for e in (e1, e2): line(ctx, [(e[0] - 8, e[1] + 2), (e[0] + 8, e[1] + 2)], 4, WHITE, alpha)
    elif eyes == 'happy':
        for e in (e1, e2):
            ctx.set_line_width(4.5); rgba(ctx, WHITE, alpha); ctx.arc(e[0], e[1] + 4, 8, math.pi * 1.1, math.pi * 1.9); ctx.stroke()
    else:
        ew, eh, pr = 9, 11, 5
        if eyes == 'shock': ew, eh, pr = 13, 14, 3.5
        if eyes == 'wide': ew, eh, pr = 11.5, 13, 5
        for e in (e1, e2):
            ctx.save(); ctx.translate(e[0], e[1]); ctx.scale(ew / eh, 1); ctx.arc(0, 0, eh, 0, 2 * math.pi); ctx.restore()
            rgba(ctx, WHITE, alpha); ctx.fill()
            ctx.arc(e[0] + gx * (ew - pr - 1) + face * 2, e[1] + gy * (eh - pr - 1), pr, 0, 2 * math.pi); rgba(ctx, BLACK, alpha); ctx.fill()
            if eyes == 'smug' or eyes == 'tired':
                rect(ctx, e[0] - ew - 1, e[1] - eh - 1, 2 * ew + 2, eh * (1.0 if eyes == 'smug' else 0.8), BLACK, alpha)
                line(ctx, [(e[0] - ew, e[1] - eh * (0.0 if eyes == 'smug' else 0.2)), (e[0] + ew, e[1] - eh * (0.0 if eyes == 'smug' else 0.2))], 3, WHITE, alpha)
    b = brows or {'angry': 'angry', 'sad': 'sad', 'shock': 'up', 'smug': 'flat'}.get(eyes)
    if b:
        for i, e in enumerate((e1, e2)):
            sgn = -1 if i == 0 else 1
            inner = e[0] - sgn * 10; outer = e[0] + sgn * 10
            if b == 'angry': p, q = (inner, e[1] - 12), (outer, e[1] - 22)
            elif b == 'sad': p, q = (inner, e[1] - 24), (outer, e[1] - 15)
            elif b == 'up': p, q = (inner, e[1] - 26), (outer, e[1] - 26)
            else: p, q = (inner, e[1] - 18), (outer, e[1] - 18)
            line(ctx, [p, q], 4.5, WHITE, alpha)
    if C.get('mustache'):
        ctx.move_to(fx - 16, fy + 14); ctx.curve_to(fx - 8, fy + 6, fx + 8, fy + 6, fx + 16, fy + 14); ctx.curve_to(fx + 6, fy + 12, fx - 6, fy + 12, fx - 16, fy + 14)
        rgba(ctx, hexc('BFBFC8'), alpha); ctx.fill()
    mx, my = fx + gx * 2, fy + 22
    ctx.set_line_width(4.5); rgba(ctx, WHITE, alpha); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if mouth == 'smile': ctx.arc(mx, my - 8, 10, 0.2 * math.pi, 0.8 * math.pi); ctx.stroke()
    elif mouth == 'grin': ctx.arc(mx, my - 4, 12, 0, math.pi); ctx.close_path(); ctx.fill()
    elif mouth == 'frown': ctx.arc(mx, my + 8, 9, 1.2 * math.pi, 1.8 * math.pi); ctx.stroke()
    elif mouth == 'o': ctx.arc(mx, my, 6.5, 0, 2 * math.pi); ctx.fill(); ctx.arc(mx, my, 3, 0, 2 * math.pi); rgba(ctx, BLACK, alpha); ctx.fill()
    elif mouth == 'O': ctx.save(); ctx.translate(mx, my + 2); ctx.scale(1, 1.3); ctx.arc(0, 0, 9, 0, 2 * math.pi); ctx.restore(); ctx.fill()
    elif mouth == 'smirk': ctx.move_to(mx - 10, my); ctx.curve_to(mx - 2, my + 4, mx + 6, my + 2, mx + 12, my - 6); ctx.stroke()
    elif mouth == 'laugh':
        ctx.arc(mx, my - 4, 13, 0, math.pi); ctx.close_path(); ctx.fill()
        ctx.arc(mx, my + 3, 6, 0, math.pi); rgba(ctx, hexc('C8323A'), alpha); ctx.fill()
    elif mouth == 'flat': ctx.move_to(mx - 8, my); ctx.line_to(mx + 8, my); ctx.stroke()
    elif mouth == 'talk': ctx.save(); ctx.translate(mx, my); ctx.scale(1, 0.6); ctx.arc(0, 0, 8, 0, 2 * math.pi); ctx.restore(); ctx.fill()
    if sweat:
        ctx.move_to(hx + R * 0.8, hy - R * 0.4); ctx.curve_to(hx + R * 0.95, hy - R * 0.1, hx + R * 0.95, hy, hx + R * 0.8, hy); ctx.curve_to(hx + R * 0.65, hy, hx + R * 0.65, hy - R * 0.1, hx + R * 0.8, hy - R * 0.4)
        rgba(ctx, hexc('8EC9FF'), alpha); ctx.fill()
    if tears > 0:
        for e in (e1, e2):
            line(ctx, [(e[0], e[1] + 12), (e[0] - 1, e[1] + 12 + 30 * tears)], 4, hexc('8EC9FF'), alpha * 0.9)
    ctx.restore()
    W_ = lambda p: (x + p[0] * s, y + p[1] * s)
    return dict(head=W_(hd), top=W_((hd[0], hd[1] - R - (18 if hs in ('quiff', 'messy', 'cap') else 6))), hand=W_(hF), handB=W_(hB), neck=W_(neck), hip=W_(hip))
