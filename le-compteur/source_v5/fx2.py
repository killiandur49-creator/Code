import math, random, cairo
from gfx import *

def god_rays(ctx, x, y, ang, length, width, n=5, col=hexc('FFF2C8'), a=0.18, t=0.0, spread=0.25):
    for i in range(n):
        k = (i - (n - 1) / 2) / max(1, n - 1)
        aa = ang + k * spread
        w0 = width * (0.6 + 0.4 * math.sin(i * 2.1)); w1 = w0 * 2.4
        flick = 0.75 + 0.25 * math.sin(t * 0.9 + i * 1.7)
        dx, dy = math.sin(aa), math.cos(aa)
        px, py = -dy, dx
        x0, y0 = x + k * width * 2, y
        pts = [(x0 - px * w0, y0 - py * w0), (x0 + px * w0, y0 + py * w0),
               (x0 + dx * length + px * w1, y0 + dy * length + py * w1), (x0 + dx * length - px * w1, y0 + dy * length - py * w1)]
        g = cairo.LinearGradient(x0, y0, x0 + dx * length, y0 + dy * length)
        g.add_color_stop_rgba(0, col[0], col[1], col[2], a * flick); g.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
        ctx.move_to(*pts[0])
        for p in pts[1:]: ctx.line_to(*p)
        ctx.close_path(); ctx.set_source(g); ctx.fill()

def dust(ctx, x, y, w, h, t, n=40, col=hexc('FFF2C8'), a=0.5, seed=1):
    rnd = random.Random(seed)
    for i in range(n):
        px = x + (rnd.random() * w + t * rnd.uniform(-8, 8)) % w
        py = y + (rnd.random() * h + t * rnd.uniform(4, 14)) % h
        r = rnd.uniform(1.2, 3.2); tw = 0.5 + 0.5 * math.sin(t * rnd.uniform(1, 3) + i)
        ctx.arc(px, py, r, 0, 6.283); rgba(ctx, col, a * tw); ctx.fill()

def spotlight(ctx, x, y, r, dark=0.7, col=BLACK):
    g = cairo.RadialGradient(x, y, r * 0.35, x, y, r * 1.6)
    g.add_color_stop_rgba(0, col[0], col[1], col[2], 0); g.add_color_stop_rgba(1, col[0], col[1], col[2], dark)
    ctx.set_source(g); ctx.paint()

def grade(ctx, col, a=0.3, op=cairo.OPERATOR_SOFT_LIGHT):
    ctx.save(); ctx.set_operator(op); rgba(ctx, col, a); ctx.paint(); ctx.restore()

def lens_flare(ctx, x, y, t, col=GOLD, a=1.0):
    glow(ctx, x, y, 220, col, 0.55 * a); glow(ctx, x, y, 60, WHITE, 0.9 * a)
    ctx.save(); ctx.translate(x, y); ctx.rotate(0.15 * math.sin(t))
    for ang in (0, math.pi / 2):
        ctx.save(); ctx.rotate(ang)
        g = cairo.LinearGradient(-500, 0, 500, 0)
        g.add_color_stop_rgba(0, 1, 1, 1, 0); g.add_color_stop_rgba(0.5, 1, 0.95, 0.8, 0.55 * a); g.add_color_stop_rgba(1, 1, 1, 1, 0)
        ctx.set_source(g); ctx.rectangle(-500, -3, 1000, 6); ctx.fill(); ctx.restore()
    ctx.restore()
    cx, cy = W / 2, H / 2
    for k, (f, r, al) in enumerate(((0.4, 40, 0.18), (0.7, 22, 0.25), (1.3, 70, 0.12), (1.7, 30, 0.2))):
        px, py = x + (cx - x) * f * 2, y + (cy - y) * f * 2
        ctx.arc(px, py, r, 0, 6.283); rgba(ctx, col, al * a); ctx.fill()

def lamp_cone(ctx, x, y, w_top, w_bot, h, col=hexc('FFD58A'), a=0.35):
    g = cairo.LinearGradient(x, y, x, y + h)
    g.add_color_stop_rgba(0, col[0], col[1], col[2], a); g.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
    ctx.move_to(x - w_top / 2, y); ctx.line_to(x + w_top / 2, y); ctx.line_to(x + w_bot / 2, y + h); ctx.line_to(x - w_bot / 2, y + h); ctx.close_path()
    ctx.set_source(g); ctx.fill()

def hanging_lamp(ctx, x, y, t=0.0, on=True, sway=0.0):
    ang = sway * math.sin(t * 1.4)
    ex, ey = x + math.sin(ang) * 260, y + math.cos(ang) * 260
    line(ctx, [(x, y), (ex, ey)], 3, hexc('2A2A33'))
    ctx.move_to(ex - 60, ey + 40); ctx.line_to(ex + 60, ey + 40); ctx.line_to(ex + 26, ey); ctx.line_to(ex - 26, ey); ctx.close_path(); rgba(ctx, hexc('C8323A')); ctx.fill()
    if on:
        lamp_cone(ctx, ex, ey + 40, 120, 900, 900, a=0.30)
        glow(ctx, ex, ey + 44, 120, hexc('FFE7B0'), 0.9)

def neon_flicker(t, seed=0, rate=18):
    r = random.Random(int(t * rate) + seed * 1000).random()
    return 0.35 if r < 0.12 else 1.0

def speedlines_dir(ctx, t, ang=0.0, a=0.6, n=30):
    rnd = random.Random(int(t * 30))
    ctx.save(); ctx.translate(W / 2, H / 2); ctx.rotate(ang)
    for i in range(n):
        y = rnd.uniform(-H, H); x = rnd.uniform(-W, W); L = rnd.uniform(200, 600)
        line(ctx, [(x, y), (x + L, y)], rnd.uniform(2, 6), WHITE, a * rnd.uniform(0.3, 1))
    ctx.restore()

def rec_overlay(ctx, t, viewers=213, live=True):
    m = 70
    for (x0, y0, sx, sy) in ((m, 430, 1, 1), (W - m, 430, -1, 1), (m, 1560, 1, -1), (W - m, 1560, -1, -1)):
        line(ctx, [(x0, y0 + sy * 80), (x0, y0), (x0 + sx * 80, y0)], 6, WHITE, 0.9)
    if int(t * 2) % 2 == 0:
        ctx.arc(m + 40, 500, 14, 0, 6.283); rgba(ctx, RED); ctx.fill()
    text(ctx, "REC", m + 92, 500, 34, WHITE, 0.95, align='l')
    if live:
        rrect(ctx, W - m - 230, 478, 110, 44, 8); rgba(ctx, RED); ctx.fill()
        text(ctx, "DIRECT", W - m - 175, 500, 24, WHITE)
        text(ctx, f"{viewers}", W - m - 60, 500, 30, WHITE, align='c')
    secs = int(t) % 60
    text(ctx, f"00:{secs:02d}", W / 2, 1600, 30, WHITE, 0.9, mono=True)

def comment_feed(ctx, t, comments, t0=0.0, x=80, y=1250, gap=0.45):
    shown = [c for i, c in enumerate(comments) if t >= t0 + i * gap]
    for k, cmt in enumerate(reversed(shown[-5:])):
        yy = y - k * 92; a = 1.0 - k * 0.15
        w = text_w(ctx, cmt, 34) + 120
        rrect(ctx, x, yy - 36, w, 72, 36); rgba(ctx, BLACK, 0.55 * a); ctx.fill()
        ctx.arc(x + 36, yy, 22, 0, 6.283); rgba(ctx, [hexc('E2709F'), hexc('4F86C6'), hexc('5BB08A'), hexc('E0A23B')][(len(shown) - k) % 4], a); ctx.fill()
        text(ctx, cmt, x + 72, yy, 34, WHITE, a, align='l')
