"""Render "through Isha's lens" camera-POV clips from her still photos (W1-L3 v3).

Each shot is drawn frame by frame (numpy + Pillow, piped to ffmpeg):
  * handheld drift (smooth multi-sine jitter, like holding a long lens in a jeep) + a slow push or pull
  * autofocus hunt: blur -> slightly sharp -> blur -> locked (AF box turns marigold on lock)
  * shutter: 2-frame white flash, the frame freezes for ~0.25 s (no drift) like the shot being taken
  * optional snap zoom at the start (the tiger)
  * viewfinder HUD: corner brackets, AF box, exposure line, shot counter — all inside the IG safe zone
Usage: python viewfinder.py   (writes broll/vf_*.mp4)
"""
import math, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

P = Path(__file__).resolve().parent
ROOT = P.parent.parent
FONTS = ROOT / "fonts"
W, H, FPS = 1080, 1920, 30
MARIGOLD = (246, 196, 69)
L1, T1 = ROOT / "projects/w1_l1_details_out/broll/isha", ROOT / "projects/w1_t1_7years/broll/isha"

# name: (image, subject x, subject y (0-1 of image), duration, zoom start, zoom end, af_hunt (start, lock), shutters, snap, exif, counter)
# the AF box tracks the subject point; LIFT = (gamma, saturation) for photos that are very dark (Isha: kingfisher)
LIFT = {"kingfisher": (1.45, 1.7)}
SHOTS = {
    "dawn":       (P / "broll/dawn_src.jpg", 0.50, 0.50, 2.2, 1.00, 1.06, (0.15, 0.75), [], False, "1/250  f/4  ISO 3200", 23),
    "kingfisher": (T1 / "kingfisher_moss.jpg", 0.69, 0.80, 1.9, 1.10, 1.16, (0.00, 0.55), [1.05], False, "1/1600  f/5.6  ISO 1600", 24),
    "jackal":     (T1 / "jackal.jpg", 0.46, 0.34, 2.0, 1.00, 1.07, (0.00, 0.45), [1.15], False, "1/2000  f/5.6  ISO 800", 25),
    "owl":        (T1 / "owl.jpg", 0.63, 0.40, 1.7, 1.00, 1.10, (0.00, 0.50), [], False, "1/800  f/5.6  ISO 2500", 26),
    "tiger":      (L1 / "tiger_walk.jpg", 0.66, 0.33, 2.8, 1.00, 1.32, (0.30, 0.65), [1.00, 1.17, 1.34, 1.51], True, "1/2500  f/5.6  ISO 1250", 27),
    "jeeps":      (L1 / "jeeps_tiger.jpg", 0.50, 0.70, 2.1, 1.18, 1.00, (0.00, 0.30), [0.95], False, "1/1000  f/6.3  ISO 640", 31),
}

def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)

def hud(af_locked, exif, counter, rec_on, af=(540, 960)):
    """transparent HUD layer"""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    white = (255, 255, 255, 215)
    L, T, R, B, arm, th = 110, 560, 950, 1450, 70, 5          # corner brackets; top band y<520 kept free for titles
    for (x, y, dx, dy) in [(L, T, 1, 1), (R, T, -1, 1), (L, B, 1, -1), (R, B, -1, -1)]:
        d.line([(x, y), (x + dx * arm, y)], fill=white, width=th); d.line([(x, y), (x, y + dy * arm)], fill=white, width=th)
    cx, cy, s = int(min(max(af[0], 200), 880)), int(min(max(af[1], 450), 1330)), 90   # AF box, on the subject, kept in the safe zone
    col = MARIGOLD + (255,) if af_locked else (255, 255, 255, 200)
    for (x, y, dx, dy) in [(cx - s, cy - s, 1, 1), (cx + s, cy - s, -1, 1), (cx - s, cy + s, 1, -1), (cx + s, cy + s, -1, -1)]:
        d.line([(x, y), (x + dx * 34, y)], fill=col, width=4); d.line([(x, y), (x, y + dy * 34)], fill=col, width=4)
    f = font("InterDisplay-SemiBold.ttf", 34)
    d.text((L + 6, B + 22), exif, font=f, fill=white)
    d.text((R - 6, B + 22), f"[{counter:03d}]", font=f, fill=white, anchor="ra")
    if rec_on:
        d.ellipse([(L + 6, T - 52), (L + 26, T - 32)], fill=(215, 38, 61, 230))
    d.text((L + 38, T - 58), "5:47 AM", font=font("InterDisplay-SemiBold.ttf", 32), fill=white)
    return im

def jitter(t, amp):
    return (amp * (0.6 * math.sin(2 * math.pi * 0.9 * t) + 0.3 * math.sin(2 * math.pi * 2.3 * t + 1.1) + 0.1 * math.sin(2 * math.pi * 6.1 * t + 2.0)),
            amp * (0.6 * math.sin(2 * math.pi * 0.7 * t + 0.5) + 0.3 * math.sin(2 * math.pi * 1.9 * t + 2.2) + 0.1 * math.sin(2 * math.pi * 5.3 * t)))

def blur_at(t, hunt):
    a, b = hunt
    if t < a: return 14.0
    if t >= b: return 0.0
    u = (t - a) / (b - a)                                    # hunt: 14 -> 2 -> 7 -> 0
    keys = [(0, 14), (0.35, 2), (0.6, 7), (1.0, 0)]
    for (u0, v0), (u1, v1) in zip(keys, keys[1:]):
        if u <= u1:
            return v0 + (v1 - v0) * (u - u0) / (u1 - u0)
    return 0.0

def render(name):
    img_path, fx, fy, dur, z0, z1, hunt, shutters, snap, exif, counter = SHOTS[name]
    src = Image.open(img_path).convert("RGB")
    if name in LIFT:
        g, sat = LIFT[name]
        src = src.point(lambda v: int(255 * (v / 255) ** (1 / g)))
        from PIL import ImageEnhance
        src = ImageEnhance.Color(src).enhance(sat)
    # base scale: image covers 1.15x the frame so drift/zoom never shows an edge
    base = max(W / src.width, H / src.height) * 1.15
    n = int(round(dur * FPS))
    out = P / "broll" / f"vf_{name}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p", "-c:v", "libx264",
                           "-crf", "16", "-preset", "veryfast", "-colorspace", "bt709", "-color_primaries", "bt709",
                           "-color_trc", "bt709", str(out)], stdin=subprocess.PIPE)
    frozen_until, frozen_state = -1, None
    shot_count = counter
    for i in range(n):
        t = i / FPS
        # zoom: snap (fast ease-out over 0.28 s) or slow linear push/pull
        if snap:
            u = min(1.0, t / 0.28); z = z0 + (z1 - z0) * (1 - (1 - u) ** 3)
        else:
            z = z0 + (z1 - z0) * (t / dur)
        jx, jy = jitter(t, 9.0)
        flash = 0.0
        for st in shutters:
            if st <= t < st + 2 / FPS:
                flash = 0.85 if t < st + 1 / FPS else 0.45
            if i == round(st * FPS):
                frozen_until = st + 0.25; frozen_state = (z, jx, jy); shot_count += 1
        if t < frozen_until and frozen_state:
            z, jx, jy = frozen_state
        s = base * z
        cw, ch = W / s, H / s                                    # source window size
        cx = min(max(src.width * fx + jx / s, cw / 2), src.width - cw / 2)
        cy = min(max(src.height * fy + jy / s, ch / 2), src.height - ch / 2)
        box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
        frame = src.resize((W, H), Image.LANCZOS, box=box)
        r = blur_at(t, hunt)
        if r > 0.3:
            frame = frame.filter(ImageFilter.GaussianBlur(r))
        arr = np.asarray(frame).astype(np.float32)
        # soft vignette (lens feel)
        if i == 0:
            yy, xx = np.mgrid[0:H, 0:W]
            vig = 1 - 0.28 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 2
            vig = np.clip(vig, 0.72, 1)[..., None].astype(np.float32)
        arr *= vig
        if flash:
            arr = arr * (1 - flash) + 255 * flash
        frame = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
        afx = (src.width * fx - box[0]) * s; afy = (src.height * fy - box[1]) * s     # subject position in the frame
        h = hud(r < 0.3, exif, shot_count, (i // 15) % 2 == 0, (afx, afy))
        frame.paste(h, (0, 0), h)
        ff.stdin.write(frame.tobytes())
    ff.stdin.close(); ff.wait()
    print(out.name, n, "frames")

if __name__ == "__main__":
    import sys
    for name in (sys.argv[1:] or SHOTS):
        render(name)
