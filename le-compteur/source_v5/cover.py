import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from scenes import *

def big_title(ctx, lines, y0, size=104, cols=None):
    for i, l in enumerate(lines):
        c = (cols or [WHITE] * len(lines))[i]
        text(ctx, l, W / 2, y0 + i * size * 1.12, size, c, 1.0, stroke=size * 0.14)
def badge(ctx, s, y):
    w = text_w(ctx, s, 54) + 70
    rrect(ctx, W / 2 - w / 2, y - 46, w, 92, 46); rgba(ctx, RED); ctx.fill()
    text(ctx, s, W / 2, y, 54, WHITE)
def cover(part, out):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); ctx = cairo.Context(surf)
    if part == 1:
        z, cx, cy = 1.45, 560, 1130
        ctx.save(); cam(ctx, z, cx, cy); bg(ctx, 'hall', env_hall, sigma=3)
        rect(ctx, -500, -400, 2200, 3000, BLACK, 0.35)
        y = 1460; s = ds('hall', y)
        il = C(ctx, 'leo', 560, y, s, face=0.2, eyes='sad', mouth='frown', lean=0.4, rim=hexc('9FB4FF'))
        im = C(ctx, 'maxime', 300, y - 60, ds('hall', y - 60), face=0.5, eyes='smug', mouth='smirk', alpha=0.95)
        ii = C(ctx, 'ines', 830, y - 60, ds('hall', y - 60), face=-0.5, eyes='smug', mouth='smirk', alpha=0.95)
        ctx.restore(); vignette(ctx, 0.6)
        S_ = lambda p_: (W / 2 + (p_[0] - cx) * z, H / 2 + (p_[1] - cy) * z)
        for inf, cn, k in ((im, '25 000 €', 0.9), (ii, '12 400 €', 0.9)):
            sx_, sy_ = S_(inf['top']); counter(ctx, sx_, sy_ - 40, cn, k=k)
        sx_, sy_ = S_(il['top']); sparkles(ctx, sx_, sy_ - 60, 160, 0.5, 14, RED); counter(ctx, sx_, sy_ - 60, '−3 400 €', k=1.35, col=RED)
        big_title(ctx, ["IL VOIT L'ARGENT", "DE TOUT LE MONDE"], 250, 96, [WHITE, GOLD])
        big_title(ctx, ["… SAUF LE SIEN"], 480, 78, [RED])
    elif part == 2:
        ctx.save(); cam(ctx, 1.35, 600, 1150); bg(ctx, 'bed', env_bedroom, sigma=2)
        y = 1430; s = ds('bed', y)
        top = table(ctx, 620, y, 150, s, top=hexc('5A4636'), leg=hexc('4A3A2E'))
        laptop(ctx, 560, top, s); laptop(ctx, 760, top, s * 0.9); chair(ctx, 400, y, 1, s)
        C(ctx, 'leo', 400, y, s, pose='sit', face=0.6, arms='table', eyes='angry', mouth='flat', lean=0.4, rim=hexc('7FB2FF'))
        ctx.restore(); vignette(ctx, 0.55)
        coins(ctx, 2.0, 0.0, n=40, area=(0, 1080), seed=12)
        big_title(ctx, ["DE −3 400 €", "À 1 MILLION"], 250, 108, [RED, GOLD])
        big_title(ctx, ["SES PARENTS NE LE", "CROIENT PAS…"], 500, 70, [WHITE, WHITE])
    else:
        z, cx, cy = 1.3, 600, 1200
        ctx.save(); cam(ctx, z, cx, cy); bg(ctx, 'cafe', env_cafe, sigma=2.5)
        god_rays(ctx, 640, 400, 0.0, 1300, 60, n=8, col=GOLD, a=0.25, t=1.0, spread=1.1)
        glow(ctx, 640, 900, 800, GOLD, 0.5)
        y = 1480; s = ds('cafe', y)
        im = C(ctx, 'maxime', 380, y, s, face=0.4, eyes='shock', mouth='O')
        il = C(ctx, 'leo', 660, y + 10, ds('cafe', y + 10), face=0, arms=((2.85, 3.05), (-0.1, -0.05)), eyes='smug', mouth='flat', rim=mix(GOLD, WHITE, 0.3))
        ctx.restore(); vignette(ctx, 0.5)
        S_ = lambda p_: (W / 2 + (p_[0] - cx) * z, H / 2 + (p_[1] - cy) * z)
        sx_, sy_ = S_(im['top']); counter(ctx, sx_ - 40, sy_ - 50, '25 000 €', k=0.9)
        sx_, sy_ = S_(il['top']); sparkles(ctx, sx_ + 60, sy_ - 110, 300, 1.0, 22); counter(ctx, min(sx_ + 60, 700), sy_ - 110, '4 700 000 €', k=1.45)
        big_title(ctx, ["IL A MONTRÉ", "SON CHIFFRE"], 250, 104, [WHITE, GOLD])
        big_title(ctx, ["DEVANT TOUT LE LYCÉE"], 480, 64, [WHITE])
    badge(ctx, f"PARTIE {part}/3", 1560)
    surf.write_to_png(out)
if __name__ == "__main__":
    os.makedirs("covers", exist_ok=True)
    for p in (1, 2, 3): cover(p, f"covers/couverture_partie_{p}.png")
