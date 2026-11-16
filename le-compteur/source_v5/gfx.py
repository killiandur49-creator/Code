import cairo, math, random
W, H, FPS = 1080, 1920, 30
T_NOW = 0.0
def hexc(h, a=1.0):
    h = h.lstrip('#'); return (int(h[0:2],16)/255, int(h[2:4],16)/255, int(h[4:6],16)/255, a)
NAVY = hexc('0B1020'); NAVY2 = hexc('141B33'); NAVY3 = hexc('1C2545')
GOLD = hexc('F5C242'); RED = hexc('E5383B'); WHITE = hexc('F4F6FB'); GREY = hexc('8A8F9C')
DARK = hexc('060912'); BLACK = hexc('0A0A0F'); HAIR = hexc('5A3B2E'); CAP = hexc('3A4566'); BAG = hexc('4B6A88')

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lerp(a, b, t): return a + (b - a) * t
def ease(t): t = clamp(t); return t * t * (3 - 2 * t)
def eout(t): t = clamp(t); return 1 - (1 - t) ** 3
def ein(t): t = clamp(t); return t ** 3
def seg(t, a, b): return clamp((t - a) / (b - a)) if b > a else (1.0 if t >= b else 0.0)
def rgba(ctx, c, a=1.0): ctx.set_source_rgba(c[0], c[1], c[2], c[3] * a)
def mix(c1, c2, t): return tuple(lerp(c1[i], c2[i], t) for i in range(4))

def fill_bg(ctx, c):
    rgba(ctx, c); ctx.paint()

def vgrad(ctx, x, y, w, h, c1, c2):
    g = cairo.LinearGradient(x, y, x, y + h); g.add_color_stop_rgba(0, *c1); g.add_color_stop_rgba(1, *c2)
    ctx.set_source(g); ctx.rectangle(x, y, w, h); ctx.fill()

def glow(ctx, x, y, r, c, a=1.0):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, c[0], c[1], c[2], a * c[3])
    g.add_color_stop_rgba(0.4, c[0], c[1], c[2], a * c[3] * 0.35)
    g.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
    ctx.set_source(g); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()

def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()

def line(ctx, pts, w, c, a=1.0, cap=cairo.LINE_CAP_ROUND):
    ctx.set_line_width(w); ctx.set_line_cap(cap); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    rgba(ctx, c, a); ctx.stroke()

def rect(ctx, x, y, w, h, c, a=1.0):
    rgba(ctx, c, a); ctx.rectangle(x, y, w, h); ctx.fill()

# ---------- text ----------
SANS = "DejaVu Sans"; MONO = "DejaVu Sans Mono"
def set_font(ctx, size, mono=False, bold=True):
    ctx.select_font_face(MONO if mono else SANS, cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)

def text_w(ctx, s, size, mono=False, cond=0.86, bold=True):
    set_font(ctx, size, mono, bold); return ctx.text_extents(s).x_advance * (1.0 if mono else cond)

def text(ctx, s, x, y, size, c=WHITE, a=1.0, mono=False, align='c', stroke=0, scol=DARK, cond=0.86, bold=True, scale=1.0):
    """y is baseline-ish center: we center vertically on cap height"""
    if a <= 0.001 or not s: return
    if mono: cond = 1.0
    set_font(ctx, size, mono, bold)
    ext = ctx.text_extents(s); w = ext.x_advance * cond
    ctx.save(); ctx.translate(x, y); ctx.scale(scale, scale)
    ox = {'c': -w / 2, 'l': 0, 'r': -w}[align]
    ctx.translate(ox, size * 0.36); ctx.scale(cond, 1)
    ctx.move_to(0, 0); ctx.text_path(s)
    if stroke:
        ctx.set_line_width(stroke / cond); ctx.set_line_join(cairo.LINE_JOIN_ROUND); rgba(ctx, scol, a); ctx.stroke_preserve()
    rgba(ctx, c, a); ctx.fill()
    ctx.restore()
    return w

# ---------- counter ----------
def counter(ctx, x, y, s, k=1.0, a=1.0, col=GOLD, glitch=0.0, t=0.0, pop=1.0, big=False):
    if a <= 0.01 or pop <= 0.01: return
    size = 40 * k
    w = text_w(ctx, s, size, mono=True) + 34 * k; h = 62 * k
    ctx.save(); ctx.translate(x, y); ctx.scale(pop, pop)
    glow(ctx, 0, 0, w * 0.75, col, 0.28 * a)
    rrect(ctx, -w / 2, -h / 2, w, h, h / 2); rgba(ctx, DARK, 0.72 * a); ctx.fill_preserve()
    ctx.set_line_width(3 * k); rgba(ctx, col, 0.9 * a); ctx.stroke()
    if glitch > 0:
        rnd = random.Random(int(t * 30) * 7 + int(x))
        for i in range(3):
            dx = (rnd.random() - 0.5) * 22 * k * glitch
            cc = [RED, hexc('39D0FF'), col][i]
            text(ctx, s, dx, (rnd.random() - 0.5) * 6 * k * glitch, size, cc, a * (0.55 if i < 2 else 1), mono=True)
        if rnd.random() < 0.5 * glitch:
            yy = (rnd.random() - 0.5) * h; rect(ctx, -w / 2, yy, w, 5 * k, col, 0.6 * a)
    else:
        text(ctx, s, 0, 0, size, col, a, mono=True)
    ctx.restore()

def fmt_eur(v):
    v = int(round(v)); s = f"{v:,}".replace(",", " ")
    return s + " €"
def fmt_eur2(v):
    if v < 1000:
        return (f"{v:.2f}".replace(".", ",")) + " €"
    return fmt_eur(v)

# ---------- stickman ----------
def P(o, ang, L):  # ang: 0 = down; positive rotates toward +x
    return (o[0] + math.sin(ang) * L, o[1] + math.cos(ang) * L)

def stick(ctx, x, y, s=1.0, face=1, gaze=(0, 0), pose='stand', walk=None, arms=None, hunch=0.0,
          outfit=(), a=1.0, mouth=None, head_turn=None, eyes_closed=False, lw=9, head_tilt=0.0, kneel=0.0, bob=True):
    """x,y = feet on ground. face: -1 left, 1 right, 0 front."""
    if a <= 0.01: return
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    f = face if face != 0 else 1
    R = 33; thigh = 78; shin = 76; torso = 135; up = 66; low = 64
    lean = hunch * 0.28
    # legs
    if pose == 'sit':
        hip = (0, -98)
        k1 = P(hip, f * math.pi / 2 * 0.95, thigh); k2 = P(hip, f * math.pi / 2 * 0.9, thigh)
        legs = [(hip, k1, P(k1, f * 0.05, shin)), (hip, k2, P(k2, -f * 0.1, shin))]
    elif pose == 'kneel':
        hip = (0, -104)
        k1 = P(hip, f * 1.25, thigh); k2 = P(hip, -f * 0.3, thigh)
        legs = [(hip, k1, (k1[0], -2)), (hip, k2, (k2[0] - f * 70, -4))]
        lean = max(lean, 0.3)
    else:
        if walk is not None:
            sw = math.sin(walk); b = (abs(math.cos(walk)) * 6) if bob else 0
            hip = (0, -thigh - shin + b)
            a1 = 0.42 * sw; a2 = -0.42 * sw
            k1 = P(hip, f * a1, thigh); k2 = P(hip, f * a2, thigh)
            kb1 = 0.35 * max(0, -math.sin(walk + 0.9)); kb2 = 0.35 * max(0, math.sin(walk + 0.9))
            legs = [(hip, k1, P(k1, f * (a1 - kb1), shin)), (hip, k2, P(k2, f * (a2 - kb2), shin))]
        else:
            hip = (0, -thigh - shin)
            legs = [(hip, P(hip, 0.1, thigh), None), (hip, P(hip, -0.1, thigh), None)]
            legs = [(hip, legs[0][1], P(legs[0][1], 0.1, shin)), (hip, legs[1][1], P(legs[1][1], -0.1, shin))]
    neck = (hip[0] + math.sin(lean) * f * torso, hip[1] - math.cos(lean) * torso)
    hlean = lean * 1.6 + head_tilt
    head = (neck[0] + math.sin(hlean) * f * (R + 8), neck[1] - math.cos(hlean) * (R + 8))
    sh = (lerp(neck[0], hip[0], 0.12), lerp(neck[1], hip[1], 0.12))
    if arms is None:
        if walk is not None:
            sw = math.sin(walk) * 0.45
            arms = ((-sw, -sw * 0.6 + 0.25), (sw, sw * 0.6 + 0.25))
        else:
            arms = ((-0.12, -0.05), (0.14, 0.08))
    armpts = []
    for (ua, la) in arms:
        e = P(sh, f * (ua + lean * 0.5), up); hnd = P(e, f * (la + lean * 0.5), low); armpts.append((sh, e, hnd))
    col = WHITE
    # behind-body accessories
    if 'backpack' in outfit:
        bx = lerp(neck[0], hip[0], 0.4) - f * 30; by = lerp(neck[1], hip[1], 0.45)
        rrect(ctx, bx - 26, by - 46, 52, 92, 16); rgba(ctx, BAG, a); ctx.fill()
    if 'hair' in outfit:
        hx, hy = head
        ctx.move_to(hx - R * 1.05, hy + 4)
        ctx.curve_to(hx - R * 1.35, hy - R * 1.5, hx + R * 1.35, hy - R * 1.5, hx + R * 1.05, hy + 4)
        ctx.curve_to(hx + R * 1.25, hy + R * 1.2, hx + R * 1.0, hy + R * 1.8, hx + R * 0.75, hy + R * 1.9)
        ctx.line_to(hx - R * 0.75, hy + R * 1.9)
        ctx.curve_to(hx - R * 1.0, hy + R * 1.8, hx - R * 1.25, hy + R * 1.2, hx - R * 1.05, hy + 4)
        rgba(ctx, HAIR, a); ctx.fill()
    if 'hoodie' in outfit:
        hx, hy = head
        ctx.arc(hx - f * 6, hy + 8, R + 11, 0, 2 * math.pi); rgba(ctx, mix(GREY, DARK, 0.25), a); ctx.fill()
    # legs
    for l in legs: line(ctx, l, lw, col, a)
    # torso
    if 'hoodie' in outfit:
        line(ctx, [neck, hip], 44, GREY, a)
        line(ctx, [(hip[0] - 18, hip[1] - 4), (hip[0] + 18, hip[1] - 4)], 10, mix(GREY, DARK, 0.3), a)
    else:
        line(ctx, [neck, hip], lw, col, a)
    # arms
    for (s0, e, hnd) in armpts:
        if 'hoodie' in outfit:
            line(ctx, [s0, e, hnd], 20, GREY, a)
        line(ctx, [s0, e, hnd], lw, col, a)
    if 'watch' in outfit:
        hnd = armpts[1][2]; e = armpts[1][1]
        wx, wy = lerp(e[0], hnd[0], 0.8), lerp(e[1], hnd[1], 0.8)
        ctx.arc(wx, wy, 9, 0, 2 * math.pi); rgba(ctx, GOLD, a); ctx.fill()
    if 'chain' in outfit:
        cx, cy = lerp(neck[0], hip[0], 0.1), lerp(neck[1], hip[1], 0.1)
        ctx.set_line_width(8); rgba(ctx, GOLD, a)
        ctx.arc(cx, cy, 30, 0.15 * math.pi, 0.85 * math.pi); ctx.stroke()
        ctx.arc(cx, cy + 30, 8, 0, 2 * math.pi); ctx.fill()
    if 'mop' in outfit:
        hnd = armpts[1][2]
        top = (hnd[0] + f * 8, hnd[1] - 90); bot = (hnd[0] + f * 40, 0 - 6)
        line(ctx, [top, bot], 7, hexc('B08A5A'), a)
        rrect(ctx, bot[0] - 30, bot[1] - 10, 60, 18, 6); rgba(ctx, hexc('C9C3B0'), a); ctx.fill()
    # head
    hx, hy = head
    ctx.arc(hx, hy, R, 0, 2 * math.pi); rgba(ctx, col, a); ctx.fill()
    if 'hair' in outfit:  # fringe
        ctx.arc(hx, hy, R + 2, math.pi * 1.05, math.pi * 1.95); ctx.close_path(); rgba(ctx, HAIR, a); ctx.fill()
    if 'cap' in outfit:
        ctx.arc(hx, hy - 4, R + 2, math.pi, 2 * math.pi); ctx.close_path(); rgba(ctx, CAP, a); ctx.fill()
        line(ctx, [(hx, hy - 6), (hx + f * (R + 26), hy - 4)], 9, CAP, a)
    # face
    ht = face if head_turn is None else head_turn
    ex = ht * 13 + gaze[0] * 6; ey = -2 + gaze[1] * 6
    if ht == 0:
        e1, e2 = (hx - 12 + gaze[0] * 6, hy + ey), (hx + 12 + gaze[0] * 6, hy + ey)
    else:
        e1, e2 = (hx + ex - 3 * ht, hy + ey), (hx + ex + 13 * ht, hy + ey)
    if 'sunglasses' in outfit:
        line(ctx, [(e1[0] - 9, e1[1]), (e2[0] + 9, e2[1])], 13, DARK, a, cap=cairo.LINE_CAP_BUTT)
    elif eyes_closed:
        for e in (e1, e2): line(ctx, [(e[0] - 5, e[1] + 1), (e[0] + 5, e[1] + 1)], 4, DARK, a)
    else:
        for e in (e1, e2): ctx.arc(e[0], e[1], 4.6, 0, 2 * math.pi); rgba(ctx, DARK, a); ctx.fill()
    if mouth:
        mx = hx + ht * 10 + gaze[0] * 3; my = hy + 16
        ctx.set_line_width(4); rgba(ctx, DARK, a)
        if mouth == 'smile': ctx.arc(mx, my - 6, 9, 0.2 * math.pi, 0.8 * math.pi); ctx.stroke()
        elif mouth == 'frown': ctx.arc(mx, my + 6, 8, 1.2 * math.pi, 1.8 * math.pi); ctx.stroke()
        elif mouth == 'o': ctx.arc(mx, my, 5.5, 0, 2 * math.pi); ctx.fill()
        elif mouth == 'smirk': ctx.move_to(mx - 8, my); ctx.curve_to(mx - 2, my + 3, mx + 4, my + 2, mx + 10, my - 5); ctx.stroke()
        elif mouth == 'laugh':
            ctx.arc(mx, my - 2, 10, 0, math.pi); ctx.close_path(); ctx.fill()
        elif mouth == 'flat': line(ctx, [(mx - 7, my), (mx + 7, my)], 4, DARK, a)
    ctx.restore()
    return dict(head=(x + hx * s, y + hy * s), top=(x + hx * s, y + (hy - R) * s), hand=(x + armpts[1][2][0] * s, y + armpts[1][2][1] * s),
                handL=(x + armpts[0][2][0] * s, y + armpts[0][2][1] * s))

# ---------- props ----------
def table(ctx, x, y, w, c=hexc('2A3358'), a=1.0, top=hexc('39436E')):
    rect(ctx, x - w / 2, y - 92, w, 14, top, a)
    rect(ctx, x - w / 2 + 14, y - 80, 8, 80, c, a); rect(ctx, x + w / 2 - 22, y - 80, 8, 80, c, a)

def bench(ctx, x, y, w, a=1.0):
    rect(ctx, x - w / 2, y - 50, w, 10, hexc('2A3358'), a); rect(ctx, x - w / 2 + 10, y - 42, 6, 42, hexc('222A48'), a); rect(ctx, x + w / 2 - 16, y - 42, 6, 42, hexc('222A48'), a)

def trash(ctx, x, y, a=1.0):
    ctx.move_to(x - 42, y - 120); ctx.line_to(x + 42, y - 120); ctx.line_to(x + 34, y); ctx.line_to(x - 34, y); ctx.close_path()
    rgba(ctx, hexc('2E3A3A'), a); ctx.fill()
    rect(ctx, x - 48, y - 130, 96, 14, hexc('3D4B4B'), a)
    for i in (-18, 0, 18): line(ctx, [(x + i, y - 105), (x + i * 0.85, y - 12)], 4, hexc('243030'), a)

def tray(ctx, x, y, ang=0.0, a=1.0, food=True):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang)
    rrect(ctx, -55, -9, 110, 18, 5); rgba(ctx, hexc('6E7BA8'), a); ctx.fill()
    if food:
        ctx.arc(-22, -16, 13, math.pi, 2 * math.pi); rgba(ctx, hexc('E8C07A'), a); ctx.fill()
        ctx.arc(20, -14, 10, math.pi, 2 * math.pi); rgba(ctx, hexc('8BC48A'), a); ctx.fill()
    ctx.restore()

def phone(ctx, x, y, s=1.0, ang=0.0, a=1.0, glowa=0.6, screen=hexc('BFD8FF')):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
    glow(ctx, 0, 0, 160, hexc('7FB2FF'), glowa * a)
    rrect(ctx, -22, -38, 44, 76, 8); rgba(ctx, DARK, a); ctx.fill()
    rrect(ctx, -18, -33, 36, 64, 5); rgba(ctx, screen, a); ctx.fill()
    ctx.restore()

def window_frame(ctx, x, y, w, h, a=1.0, sky=True, t=0.0):
    if sky:
        vgrad(ctx, x, y, w, h, hexc('1A2A55', a), hexc('0E1736', a))
    ctx.set_line_width(12); rgba(ctx, hexc('2E3963'), a); ctx.rectangle(x, y, w, h); ctx.stroke()
    line(ctx, [(x + w / 2, y), (x + w / 2, y + h)], 8, hexc('2E3963'), a); line(ctx, [(x, y + h / 2), (x + w, y + h / 2)], 8, hexc('2E3963'), a)

def grain_surfaces(n=6):
    import numpy as np
    out = []
    for i in range(n):
        rng = np.random.default_rng(i)
        g = rng.integers(0, 255, (H // 2, W // 2), dtype=np.uint8)
        arr = np.zeros((H // 2, W // 2, 4), dtype=np.uint8)
        arr[..., 0] = g; arr[..., 1] = g; arr[..., 2] = g; arr[..., 3] = 255
        surf = cairo.ImageSurface.create_for_data(memoryview(arr.copy()).cast('B'), cairo.FORMAT_ARGB32, W // 2, H // 2) if False else None
        s2 = cairo.ImageSurface(cairo.FORMAT_ARGB32, W // 2, H // 2)
        buf = s2.get_data(); np.frombuffer(buf, np.uint8)[:] = arr.reshape(-1)
        s2.mark_dirty(); out.append(s2)
    return out

def vignette(ctx, k=0.55):
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.38, W / 2, H / 2, H * 0.78)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, k)
    ctx.set_source(g); ctx.paint()
