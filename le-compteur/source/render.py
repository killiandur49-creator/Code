import sys, os, subprocess, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from gfx import *
import timeline, overlay
from multiprocessing import Pool

GRAIN = None
def frame(ctx, part, shots, groups, t):
    global GRAIN
    if GRAIN is None: GRAIN = grain_surfaces(6)
    s = next((x for x in shots if x['t0'] <= t < x['t1']), shots[-1])
    lt = t - s['t0']; d = s['dur']
    ctx.save(); s['draw'](ctx, lt, d); ctx.restore()
    vignette(ctx)
    # grain
    ctx.save(); ctx.scale(2, 2); ctx.set_source_surface(GRAIN[int(t * 30) % 6], 0, 0); ctx.paint_with_alpha(0.035); ctx.restore()
    fx = s.get('fx', [])
    def T(x): return x if x is None or x >= 0 else d + x
    nosubs = any(f[0] == 'nosubs' for f in fx) or any(f[0] == 'nosubs_after' and lt >= T(f[1]) for f in fx)
    # HUD
    h = 'base' if 'hud' not in s else s['hud']
    if h is not None:
        hh = dict(timeline.HUDBASE[part])
        if h != 'base': hh.update(h)
        if 'hud2' in s and lt >= 2.6: hh.update(s['hud2'])
        hwrap = {k: ((lambda f: (lambda _t: f(lt)))(v) if callable(v) else v) for k, v in hh.items()}
        overlay.hud(ctx, t, hwrap, t / timeline.DUR)
    for f in fx:
        if f[0] == 'banner': overlay.banner(ctx, lt, T(f[1]), T(f[2]) if f[2] is not None else d - 0.05, f[3])
        elif f[0] == 'title': overlay.title(ctx, lt, T(f[1]), T(f[2]) if f[2] is not None else None, f[3], f[4], f[5], f[6], f[7])
        elif f[0] == 'phone':
            t0 = T(f[1]); a = seg(lt, t0, t0 + 0.2)
            big = f[4]
            if callable(big): big = str(int(round(big(lt))))
            from scenes import phone_card
            phone_card(ctx, W / 2, 700, lt, f[3], big, f[5], a)
        elif f[0] == 'flash':
            t0 = T(f[1]); 
            if lt >= t0: rect(ctx, 0, 0, W, H, WHITE, seg(lt, t0, t0 + f[2]))
    if not nosubs: overlay.subs(ctx, t, groups)
    # cut flash: tiny white flash at shot starts (except first)
    if s['t0'] > 0 and lt < 0.06: rect(ctx, 0, 0, W, H, WHITE, 0.12)

def render_chunk(args):
    part, f0, f1, out = args
    shots, tempo = timeline.get(part); groups = overlay.make_subs(shots)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        ctx = cairo.Context(surf); ctx.set_antialias(cairo.ANTIALIAS_GOOD)
        frame(ctx, part, shots, groups, fi / FPS)
        surf.flush(); p.stdin.write(bytes(surf.get_data()))
    p.stdin.close(); p.wait()
    return out

def still(part, t, out):
    shots, tempo = timeline.get(part); groups = overlay.make_subs(shots)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); ctx = cairo.Context(surf)
    frame(ctx, part, shots, groups, t); surf.write_to_png(out)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "stills":
        part = int(sys.argv[2])
        shots, _ = timeline.get(part)
        os.makedirs("stills", exist_ok=True)
        for s in shots:
            for k, fr in enumerate((0.35, 0.8)):
                still(part, s['t0'] + s['dur'] * fr, f"stills/p{part}_{s['id']}_{k}.png")
    elif cmd == "video":
        part = int(sys.argv[2]); N = int(timeline.DUR * FPS); n = 4
        os.makedirs("chunks", exist_ok=True)
        jobs = [(part, N * i // n, N * (i + 1) // n, f"chunks/p{part}_{i}.mp4") for i in range(n)]
        with Pool(n) as pool: outs = pool.map(render_chunk, jobs)
        with open(f"chunks/p{part}.txt", "w") as f:
            for o in outs: f.write(f"file '{os.path.abspath(o)}'\n")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", f"chunks/p{part}.txt", "-c", "copy", f"chunks/p{part}_video.mp4"], check=True)
        print("video done", part)
