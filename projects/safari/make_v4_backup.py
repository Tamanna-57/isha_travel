"""v3 visual + type design for the safari reel (2026-11-04). Spliced in front of make.py's sound/deliver code.

Client feedback on v2: "it can be a lot better and more interesting to look at", "i dont like positioning of the
fonts, looks way too drafted and less edited". Fonts stay ref 2 (Video-11291) = Inter Display ExtraBold;
layout borrows from BOTH refs (ref 2 cards + numbered list, ref 1 Video-96135 split screen + full-screen beats).

Motion language (one of each, used everywhere):
  easing      expo-out (fast start, soft landing), no overshoot
  timing      base unit 0.30 s (enters 0.30, swaps 0.27, micro 0.16)
  transitions hard cut, or a push-slide along one axis
  stagger     words reveal on their spoken timestamps (blur-in 0.16 s)
  intensity   travel <= 160 px, scale 0.95 -> 1, rotation <= 3 deg
  texture     slow push on every shot, alternating punch-ins on her jump cuts, soft scrims, fine grain
  hero        ONE wow moment: the tiger reveal ("it's right there")
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np, cv2
from scipy.io import wavfile
from PIL import Image, ImageDraw, ImageFont

P = Path(__file__).resolve().parent
ROOT = P.parent.parent
B, OUT, A = P / "build", P / "out", P / "assets"
NAME = "safari_reel"
FPS, SR = 30, 48000
NF = 1089
DUR = NF / FPS
FONTS = ROOT / "fonts"
FONTS_REL = "../../../fonts"
FONT_FILE = FONTS / "InterDisplay-ExtraBold.ttf"
FONT_FILE_B = FONTS / "InterDisplay-Bold.ttf"

def T(src):
    """source time -> final timeline (base.py drops 0.00-0.07 and 33.90-35.30)"""
    return src - 0.07 if src < 33.90 else src - 1.47

CUT = T(35.30)

def expo_out(x):
    x = min(1.0, max(0.0, x))
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)

# ------------------------------------------------------------------ layout timeline (FINAL seconds)
# her jump cuts in the source (scene detection) -> per-shot camera: slow push, every other shot punched in
SRC_CUTS = [3.2, 3.9, 6.93, 10.7, 13.0, 13.87, 16.7, 18.7, 23.6, 24.6, 27.07, 32.43]
SHOTS = [0.0] + [T(c) for c in SRC_CUTS] + [CUT, DUR]

CARD_C, CARD_S = (540, 1452), 500
# (t0, t1, image, fx, fy, zoom, number, label, group) - group = cards that swipe into each other
CARDS = [
    (T(2.40), T(3.20), "tiger_road.jpg", 0.53, 0.50, 2.0, None, None, 0),
    (T(4.12), T(4.76), "gypsy.jpg", 0.52, 0.55, 1.05, "01", "An open jeep", 1),
    (T(4.76), T(5.52), "jeep_sal_forest.jpg", 0.55, 0.55, 1.05, "02", "In the jungle", 1),
    (T(5.52), T(6.93), "jungle_road_mist.jpg", 0.50, 0.55, 1.05, "03", "At 6 AM", 1),
]
# v4 split: a true 50/50 like ref 1; every photo framed by hand on its subject (grid-checked, full-res originals);
# her half FACE-TRACKED at 1.0x so she always sits the same way (forehead ~0.24 face-heights under the seam).
SEAM = 960
SPLIT = [   # (t0, t1, image or "LOGO", fx, fy, z0, z1)
    (T(8.08), T(10.06), "sal_forest.jpg", 0.50, 0.55, 1.00, 1.06),     # road vanishing point centred
    (T(10.06), T(12.78), "chital_fawn.jpg", 0.50, 0.375, 1.00, 1.04),  # whole head, both ears
    (T(19.77), T(20.13), "leopard.jpg", 0.50, 0.50, 1.45, 1.50),       # leopard fills the middle
    (T(20.13), T(20.50), "elephant.jpg", 0.54, 0.47, 1.30, 1.34),
    (T(20.50), T(20.93), "sloth_bear.jpg", 0.36, 0.33, 1.70, 1.76),
    (T(20.93), T(21.43), "peacock.jpg", 0.35, 0.45, 1.15, 1.19),       # bird on the left third, tail falling right
    (T(21.43), T(22.55), "tiger_yawn.jpg", 0.50, 0.50, 1.00, 1.05),
    (T(30.15), T(32.43), "LOGO", 0, 0, 1, 1),                      # only while she says the brand name
]
SHUTTERS = [x[0] for x in SPLIT[2:7]]
LOGO_SPLIT = (T(30.15), T(32.43))
BARKS = [T(10.56), T(11.62)]
FULL = [
    (0.0, T(1.14), "tiger_trees.jpg", 0.50, 0.45, 1.12, 1.00, None),              # cold open: "You don't need to be a"
    (T(12.78), T(14.05), "tiger_trail_jeep.jpg", 0.42, 0.62, 1.00, 1.10, None),   # HERO: "it's right there"
    (T(24.55), T(25.93), "tiger_eyes.jpg", 0.60, 0.58, 1.00, 1.07, None),         # "with your own eyes"
]
SILENT = T(9.06)
HEARTBEATS = [T(15.02), T(15.82)]
ANCHOR_Y = 700

def in_split(t):
    return any(a <= t < b for a, b, *_ in SPLIT)

EXIT_T = 0.25
def split_exit(t):
    """(split entry, progress) while a split pushes back out to full frame, else None"""
    for sp in SPLIT:
        b = sp[1]
        if b <= t < b + EXIT_T and not in_split(b + 0.001) and not any(f[0] <= b + 0.001 < f[1] for f in FULL):
            return sp, (t - b) / EXIT_T
    return None

def _her_rows():
    """per-frame top row of her half (1080 scale, zoom 1.0): forehead 0.24 face-heights below the seam, smoothed"""
    faces = json.loads((B / "faces.json").read_text())
    tops = np.full(len(faces), np.nan)
    for i, f in enumerate(faces):
        if f:
            x, y, w, h = f[0]
            tops[i] = y - 0.24 * h
    idx = np.arange(len(tops)); ok = ~np.isnan(tops)
    tops = np.interp(idx, idx[ok], tops[ok])
    from scipy.ndimage import median_filter, uniform_filter1d
    tops = uniform_filter1d(median_filter(tops, 21, mode="nearest"), 15, mode="nearest")
    return np.clip(tops, 0, SEAM).astype(int)
HER_ROWS = _her_rows()

def her_row(t):
    return int(HER_ROWS[min(len(HER_ROWS) - 1, max(0, int(round(t * FPS))))])

def in_full(t):
    return any(a <= t < b for a, b, *_ in FULL)

def card_at(t):
    return any(a <= t < b for a, b, *_ in CARDS)

def shot_index(t):
    return max(0, np.searchsorted(SHOTS, t, side="right") - 1)

def base_zoom(t):
    """camera on her: slow push inside each shot, alternate shots punched in (hides/accents the jump cuts)"""
    if in_split(t) or split_exit(t):
        return 1.0                                          # split: her half is face-tracked at 1.0x
    i = shot_index(t)
    a, b = SHOTS[i], SHOTS[min(i + 1, len(SHOTS) - 1)]
    prog = (t - a) / max(0.3, b - a)
    z = (1.10 if i % 2 == 1 else 1.0) * (1 + 0.035 * prog)
    if t >= CUT:
        z = 1.12 * (1 + 0.03 * (t - CUT) / (DUR - CUT))
    for hb in HEARTBEATS:
        d = t - hb
        if 0 <= d < 0.45:
            z *= 1 + 0.035 * np.sin(np.pi * min(1, d / 0.08) / 2) * np.exp(-max(0, d - 0.08) * 9)
    return z

# ------------------------------------------------------------------ image helpers
def crop_cover(img, w, h, fx, fy, z=1.0):
    ih, iw = img.shape[:2]
    s = max(w / iw, h / ih) * z
    cw, ch = w / s, h / s
    x0 = np.clip(fx * iw - cw / 2, 0, iw - cw); y0 = np.clip(fy * ih - ch / 2, 0, ih - ch)
    M = np.array([[s, 0, -x0 * s], [0, s, -y0 * s]], np.float32)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

def load_rgb(name):
    return cv2.cvtColor(cv2.imread(str(A / name), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)

def photo_grade(img):
    f = img.astype(np.float32) / 255
    f = 0.01 + 0.97 * f
    g = f.mean(2, keepdims=True)
    f = g + (f - g) * 0.95
    return np.clip(f * 255, 0, 255).astype(np.uint8)

def pil_font(path, px):
    return ImageFont.truetype(str(path), px)

def tracked_text(draw, xy, text, font, fill, tracking=0):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return x

def make_card(img, number, label, angle):
    """rounded photo card: number tag top-left, label on a soft bottom gradient, drop shadow, slight tilt"""
    S, r = CARD_S, 26
    photo = Image.fromarray(img).convert("RGBA")
    if label:
        grad = np.zeros((S, S, 4), np.uint8)
        ramp = np.clip((np.arange(S) - S * 0.55) / (S * 0.45), 0, 1) ** 1.4 * 170
        grad[..., 3] = ramp[:, None].astype(np.uint8)
        photo = Image.alpha_composite(photo, Image.fromarray(grad))
        d = ImageDraw.Draw(photo)
        d.text((30, S - 34), label, font=pil_font(FONT_FILE, 50), fill=(255, 255, 255, 255), anchor="ls")
    if number:
        d = ImageDraw.Draw(photo)
        f = pil_font(FONT_FILE, 30)
        w = d.textlength(number, font=f)
        d.rounded_rectangle((24, 24, 24 + w + 32, 24 + 50), radius=25, fill=(246, 238, 162, 255))
        d.text((24 + 16, 24 + 25), number, font=f, fill=(28, 32, 24, 255), anchor="lm")
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, S - 1, S - 1), radius=r, fill=255)
    photo.putalpha(Image.fromarray(np.minimum(np.array(photo)[..., 3], np.array(mask))))
    pad = 70
    canvas = Image.new("RGBA", (S + 2 * pad, S + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 14, pad + S, pad + S + 14), radius=r, fill=int(255 * 0.42))
    sh = cv2.GaussianBlur(np.array(sh), (0, 0), 20)
    canvas.putalpha(Image.fromarray(sh))
    canvas = Image.alpha_composite(canvas, Image.new("RGBA", canvas.size, (0, 0, 0, 0)))
    black = Image.new("RGBA", canvas.size, (0, 0, 0, 255)); black.putalpha(Image.fromarray(sh))
    canvas = black
    canvas.alpha_composite(photo, (pad, pad))
    canvas = canvas.rotate(angle, resample=Image.BICUBIC, expand=False)
    return np.array(canvas).astype(np.float32) / 255.0

def make_logo_panel():
    """Lost & Free forest green, cream logo, small tracked caps label above it"""
    lg = Image.open(A / "logo.png").convert("RGBA")
    panel = Image.new("RGBA", (1080, SEAM), (51, 64, 51, 255))
    lw = 700; lh = int(lg.height * lw / lg.width)
    lg = lg.resize((lw, lh), Image.LANCZOS)
    y0 = (SEAM - lh) // 2 + 60
    d = ImageDraw.Draw(panel)
    f = pil_font(FONT_FILE_B, 30)
    label = "A SAFARI HOSTED WITH"
    tr = 7
    w = sum(d.textlength(c, font=f) + tr for c in label) - tr
    lx = (1080 - w) / 2
    ly = y0 - 70
    d.line((lx - 70, ly + 15, lx - 22, ly + 15), fill=(248, 247, 230, 160), width=2)
    d.line((lx + w + 22, ly + 15, lx + w + 70, ly + 15), fill=(248, 247, 230, 160), width=2)
    tracked_text(d, (lx, ly), label, f, (248, 247, 230, 230), tr)
    return np.array(panel.convert("RGB")), lg, ((1080 - lw) // 2, y0)

def blend_rgba(frame, rgba, cx, cy, scale=1.0, alpha=1.0):
    if scale != 1.0:
        rgba = cv2.resize(rgba, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    h, w = rgba.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(frame.shape[1], x0 + w), min(frame.shape[0], y0 + h)
    if xa >= xb or ya >= yb:
        return
    src = rgba[ya - y0:yb - y0, xa - x0:xb - x0]
    a = src[..., 3:4] * alpha
    reg = frame[ya:yb, xa:xb].astype(np.float32)
    frame[ya:yb, xa:xb] = (src[..., :3] * 255 * a + reg * (1 - a)).astype(np.uint8)

# scrims + vignette + grain (texture tier: subliminal)
_yy = np.linspace(0, 1, 1920)[:, None]
SCRIM_BOT = np.clip((_yy - 0.52) / 0.48, 0, 1) ** 1.6 * 0.42
SCRIM_TOP = np.clip((0.24 - _yy) / 0.24, 0, 1) ** 1.5 * 0.30
_xx = np.linspace(-1, 1, 1080)[None, :]
VIGNETTE = (1 - 0.13 * np.clip(_xx ** 2 + ((_yy - 0.5) * 2) ** 2 - 0.35, 0, 1.5) / 1.5).astype(np.float32)
PANEL_SHADE = (1 - 0.5 * np.clip((np.linspace(0, 1, SEAM) - 0.66) / 0.34, 0, 1) ** 1.6)[:, None, None].astype(np.float32)
HB_VIG = (1 - 0.42 * np.clip(_xx ** 2 + ((_yy - 0.45) * 1.6) ** 2 - 0.25, 0, 1.2) / 1.2).astype(np.float32)
_rng = np.random.default_rng(3)
GRAIN = [(_rng.standard_normal((960, 540)) * 3.2).astype(np.float32) for _ in range(6)]

def texture(frame, fi, scrim=1.0):
    f = frame.astype(np.float32)
    shade = (1 - (SCRIM_BOT + SCRIM_TOP) * scrim) * VIGNETTE
    f *= shade[..., None] if shade.ndim == 2 else shade
    g = cv2.resize(GRAIN[fi % 6], (1080, 1920), interpolation=cv2.INTER_LINEAR)
    f += g[..., None]
    return np.clip(f, 0, 255).astype(np.uint8)

def desat(frame, k, dark):
    f = frame.astype(np.float32)
    g = f.mean(2, keepdims=True)
    return np.clip((g + (f - g) * k) * dark, 0, 255).astype(np.uint8)

# ------------------------------------------------------------------ compositor
def composite():
    cards = []
    for k, (t0, t1, n, fx, fy, z, num, label, grp) in enumerate(CARDS):
        img = photo_grade(crop_cover(load_rgb(n), CARD_S, CARD_S, fx, fy, z))
        cards.append((t0, t1, make_card(img, num, label, (-2.5, 2.0, -1.5, 2.5)[k % 4]), grp))
    fulls = [(t0, t1, photo_grade(load_rgb(n)), fx, fy, z0, z1) for t0, t1, n, fx, fy, z0, z1, _ in FULL]
    splits = [(t0, t1, None if n == "LOGO" else photo_grade(load_rgb(n)), fx, fy, z0, z1) for t0, t1, n, fx, fy, z0, z1 in SPLIT]
    logo_bg, logo_img, logo_xy = make_logo_panel()
    logo_rgba = np.array(logo_img).astype(np.float32) / 255
    MONTAGE = set(range(2, 7))
    # a split "enters" (push-down) only when the previous frame wasn't a split
    entering = {s[0] for s in splits if not in_split(s[0] - 0.05)}
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(B / "base.mp4"), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", str(FPS),
                            "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "13", "-pix_fmt", "yuv420p",
                            str(B / "comp.mp4")], stdin=subprocess.PIPE)
    sz = 1440 * 2560 * 3
    for fi in range(NF):
        buf = dec.stdout.read(sz)
        if len(buf) < sz:
            break
        t = fi / FPS
        src = np.frombuffer(buf, np.uint8).reshape(2560, 1440, 3)
        s = 0.75 * base_zoom(t)
        M = np.array([[s, 0, 540 - 720 * s], [0, s, ANCHOR_Y - (ANCHOR_Y / 0.75) * s]], np.float32)
        frame = cv2.warpAffine(src, M, (1080, 1920), flags=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR,
                               borderMode=cv2.BORDER_REFLECT)
        # "everything will go silent": the picture drains with the sound until the alarm call
        if SILENT <= t < T(10.06):
            k = expo_out((t - SILENT) / 0.6)
            frame = desat(frame, 1 - 0.45 * k, 1 - 0.08 * k)
        scrim = 1.0
        # ---- ref 1 split screen (photo top half, her bottom half; push-down in, push-up out, film-strip montage)
        def split_top(k, t):
            t0, t1, img, fx, fy, z0, z1 = splits[k]
            zz = z0 + (z1 - z0) * min(1, max(0, (t - t0) / (t1 - t0)))
            for bk in BARKS:                                            # snap-zoom on each bark
                if t0 <= bk <= t < bk + 0.6:
                    zz *= 1 + 0.07 * expo_out((t - bk) / 0.12) * (1 - 0.6 * min(1, (t - bk - 0.12) / 0.45) if t > bk + 0.12 else 1)
            if img is None:
                top = logo_bg.copy()
                al = expo_out((t - t0) / 0.4)
                lr = cv2.resize(logo_rgba, None, fx=0.95 + 0.05 * al, fy=0.95 + 0.05 * al, interpolation=cv2.INTER_AREA)
                blend_rgba(top, lr, logo_xy[0] + logo_img.width / 2, logo_xy[1] + logo_img.height / 2, 1.0, al)
                return top
            top = crop_cover(img, 1080, SEAM, fx, fy, zz)
            if SILENT <= t < T(10.06):
                kk = expo_out((t - SILENT) / 0.6)
                top = desat(top, 1 - 0.45 * kk, 1 - 0.08 * kk)
            return (top.astype(np.float32) * PANEL_SHADE).astype(np.uint8)

        def compose(frame, top, row0, p):
            """p = 1: full split. 0 < p < 1: mid-push (photo slides down from the top, she slides down with it)"""
            if p >= 1:
                return np.vstack([top, frame[row0:row0 + 1920 - SEAM]])
            out = frame.copy()
            shift = int(round((SEAM - row0) * p))
            if shift > 0:
                out[shift:] = frame[:1920 - shift]
            h = int(round(SEAM * p))
            if h > 0:
                out[:h] = top[SEAM - h:]
            return out

        for k, (t0, t1, img, fx, fy, z0, z1) in enumerate(splits):
            if t0 <= t < t1:
                top = split_top(k, t)
                prev = k - 1 if k > 0 and abs(splits[k - 1][1] - t0) < 0.02 else None
                if prev is not None and k in MONTAGE and prev in MONTAGE and t - t0 < 0.2:
                    q = expo_out((t - t0) / 0.2)                          # film-strip slide between photos
                    old = split_top(prev, t0 - 0.001)
                    off = int(round(1080 * (1 - q)))
                    top = np.hstack([old, top])[:, 1080 - off:2160 - off]
                p = expo_out((t - t0) / 0.3) if (t0 in entering and t - t0 < 0.3) else 1.0
                frame = compose(frame, top, her_row(t), p)
        ex = split_exit(t)
        if ex:
            sp, q = ex
            kx = SPLIT.index(sp)
            frame = compose(frame, split_top(kx, sp[1] - 0.001), her_row(t), 1 - expo_out(q))
        # ---- ref 1 full-screen beats
        for t0, t1, img, fx, fy, z0, z1 in fulls:
            if t0 <= t < t1:
                zz = z0 + (z1 - z0) * expo_out((t - t0) / (t1 - t0) * 0.8)
                frame = crop_cover(img, 1080, 1920, fx, fy, zz)
                if abs(t0 - T(12.78)) < 1e-6:                               # THE reveal: 2-frame flash + short shake
                    d = t - t0
                    if d < 0.35:
                        amp = 14 * (1 - d / 0.35) ** 2
                        dx, dy = amp * np.sin(d * 97), amp * np.cos(d * 71)
                        frame = cv2.warpAffine(frame, np.float32([[1.03, 0, -16 + dx], [0, 1.03, -29 + dy]]), (1080, 1920),
                                               borderMode=cv2.BORDER_REFLECT)
                    if d < 2 / FPS:
                        frame = np.clip(frame.astype(np.float32) * 0.4 + 255 * 0.6, 0, 255).astype(np.uint8)
        frame = texture(frame, fi, scrim)
        for hb in HEARTBEATS:                                               # "heart will POUND": edges throb
            d = t - hb
            if 0 <= d < 0.5:
                k = np.sin(np.pi * min(1, d / 0.07) / 2) * np.exp(-max(0, d - 0.07) * 7)
                frame = (frame.astype(np.float32) * (1 - (1 - HB_VIG) * k)[..., None]).astype(np.uint8)
        # ---- ref 2 cards (after the scrim so the photos stay clean)
        for k, (t0, t1, rgba, grp) in enumerate(cards):
            nxt_same = k + 1 < len(cards) and cards[k + 1][3] == grp and abs(cards[k + 1][0] - t1) < 0.05
            prv_same = k > 0 and cards[k - 1][3] == grp and abs(cards[k - 1][1] - t0) < 0.05
            last_end = t1 + (0.0 if nxt_same else 0.2)
            if not (t0 <= t < last_end + (0.27 if nxt_same else 0)):
                continue
            x, y, al = CARD_C[0], CARD_C[1], 1.0
            if prv_same:                                                # swipe in from the right
                p = expo_out((t - t0) / 0.27)
                x += 640 * (1 - p)
            else:                                                       # rise in
                p = expo_out((t - t0) / 0.3)
                y += 160 * (1 - p); al = min(1, (t - t0) / 0.12)
            if nxt_same and t >= t1:                                    # pushed out to the left by the next card
                q = expo_out((t - t1) / 0.27)
                x -= 640 * q
            elif not nxt_same and t >= t1:                              # leave: drop + fade
                q = (t - t1) / 0.2
                y += 120 * q; al *= 1 - q
            blend_rgba(frame, rgba, x, y, 0.95 + 0.05 * p, al)
        enc.stdin.write(frame.tobytes())
        if fi % 150 == 0:
            print(f"  composite {fi}/{NF}", flush=True)
    enc.stdin.close(); enc.wait(); dec.wait()

# ------------------------------------------------------------------ type (libass)
YEL, WHITE, BLK = "&HA2EEF6&", "&HFFFFFF&", "&H000000&"
FONT, FONT_B = "Inter Display ExtraBold", "Inter Display Bold"
EM = 0.70           # libass fs -> em px for Inter (calibrated: fs 100 -> cap height 51 px)
CAP_FS, KW_FS = 66, 84
MAX_W = 840

# caption pages: *word* = keyword (bigger, ref-2 yellow). Words map 1:1 onto build/words.json (after the cut).
PAGES = [
    "You don't need", "to be a *wildlife* photographer", "to see a *tiger*",
    "All you need is", "an *open* *jeep*", "in the *jungle*", "at *6* *AM* in the morning",
    "And then suddenly", "everything will go *silent*",
    "An *alarm* *call*", "will ring", "and you will know", "it's *right* *there*",
    "And the way", "your heart will *pound*", "in that moment",
    "No reel will ever", "make you *feel* like that",
    "You know I've spent", "*years* photographing", "these moments", "on my *camera*",
    "But now", "I want you to see it", "with your *own* *eyes*", "not on some *screen*",
    "And that's exactly why", "I'm hosting a *safari*", "with *Lost* *&* *Free* *Safaris*", "just for you",
    "Details are coming out *soon*",
    "comment SAFARI and you'll be the first to know",          # covered by the CTA lockup (not drawn as a caption)
]
NO_CAPTION = {len(PAGES) - 1}

def at(t):
    t = max(0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"

HDR = rf"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: X,{FONT},{CAP_FS},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0.5,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def load_words():
    raw = json.loads((B / "words.json").read_text(encoding="utf-8"))
    ws = []
    for w in raw:
        if 33.90 <= w["start"] < 35.30:
            continue
        txt = w["text"].strip(".,?!…").replace("...", "")
        ws.append({"text": {"am": "AM"}.get(txt, txt), "t": T(w["start"]), "end": T(w["end"])})
    return ws

def caption_pages():
    ws = load_words()
    k, pages = 0, []
    for i, p in enumerate(PAGES):
        words = []
        for tok in p.split():
            kw = tok.startswith("*") and tok.endswith("*")
            w = ws[k]; k += 1
            words.append({"text": w["text"], "kw": kw, "t": w["t"], "end": w["end"]})
        pages.append(words)
    assert k == len(ws), f"{k} caption words vs {len(ws)} aligned"
    out = []
    for i, words in enumerate(pages):
        t0 = words[0]["t"]
        nxt = pages[i + 1][0]["t"] if i + 1 < len(pages) else DUR
        t1 = min(nxt, words[-1]["end"] + 0.5)
        if t0 < CUT <= t1:
            t1 = CUT
        out.append({"words": words, "t0": t0, "t1": t1, "idx": i})
    return out, ws

def caption_words():          # kept for build_srt in the shared tail
    _, ws = caption_pages()
    return None, ws

STACK_KW = 112
def stack_lines(words):
    """ref-1 hierarchy: a page with a keyword becomes 2 lines - lead-in small, keyword(s) big (or keyword then tail)"""
    kws = [i for i, w in enumerate(words) if w["kw"]]
    if not kws or len(words) == 1 or all(w["kw"] for w in words):
        return [(words, False)]
    i = kws[0]
    if i > 0:
        return [(words[:i], False), (words[i:], True)]
    j = next(k for k, w in enumerate(words) if not w["kw"])
    return [(words[:j], True), (words[j:], False)]

def text_width(words, scale, kw_fs=None):
    tot = 0
    for j, w in enumerate(words):
        f = pil_font(FONT_FILE, int(((kw_fs or KW_FS) if w["kw"] else CAP_FS) * EM * scale))
        tot += f.getlength(w["text"] + (" " if j < len(words) - 1 else ""))
    return tot

def caption_y(t):
    if in_split(t + 0.01):
        return SEAM - 92                    # ref 1: on the bottom of the photo, just above the seam
    if card_at(t + 0.01):
        return 1112                         # ref 2: just above the card
    return 1268                             # her chest, over the bottom scrim

LAYERS = (  # glow, tight drop shadow, fill
    ("glow", rf"\1c{BLK}\3c{BLK}\bord6\blur14", r"\1a&HA0&\3a&HA0&", 0, 3),
    ("drop", rf"\1c{BLK}\3c{BLK}\bord1\blur3", r"\1a&H70&\3a&H88&", 2, 4),
    ("fill", r"\bord0\blur0", r"\1a&H00&", 0, 0),
)

def line_events(words, t_from, t_to, y, scale, reveal=True, layer0=1, x=540, align=5, extra="", kw_fs=None):
    """one caption line; each word blurs in on its own timestamp, layout never reflows (hidden words keep space)"""
    ev = []
    times = [w["t"] for w in words] if reveal else [t_from - 1] * len(words)
    cuts = sorted(set([t_from] + [tt for tt in times if t_from < tt < t_to])) + [t_to]
    for a, b in zip(cuts, cuts[1:]):
        if b - a < 0.01:
            continue
        for li, (kind, base, vis, dx, dy) in enumerate(LAYERS):
            parts = []
            for j, w in enumerate(words):
                fs = ((kw_fs or KW_FS) if w["kw"] else CAP_FS) * scale
                col = (YEL if w["kw"] else WHITE) if kind == "fill" else BLK
                if times[j] > a + 1e-6:
                    st = r"\1a&HFF&\3a&HFF&"
                elif reveal and abs(times[j] - a) < 1e-6:
                    st = r"\1a&HFF&\3a&HFF&\t(0,160," + vis + ")"
                    if kind == "fill":
                        st = r"\1a&HFF&\blur5\t(0,160,\1a&H00&\blur0)"
                else:
                    st = vis
                parts.append("{" + rf"\fs{fs:.1f}\1c{col}" + st + "}" + w["text"] + (" " if j < len(words) - 1 else ""))
            head = rf"{{\an{align}\pos({x + dx},{y + dy}){base}{extra}}}"
            ev.append(f"Dialogue: {layer0 + li},{at(a)},{at(b)},X,,0,0,0,,{head}{''.join(parts)}")
    return ev

def lockup(t0, t1, items, layer0=6):
    """static designed text: items = (text, fs, colour, x, y, align, spacing, appear_at)"""
    ev = []
    for text, fs, col, x, y, align, sp, t_in in items:
        for li, (kind, base, vis, dx, dy) in enumerate(LAYERS):
            c = col if kind == "fill" else BLK
            anim = (r"\1a&HFF&\3a&HFF&\t(0,200," + vis + ")") if kind != "fill" else r"\1a&HFF&\blur6\t(0,200,\1a&H00&\blur0)"
            if t_in <= 0.0:
                anim = vis if kind != "fill" else ""
            ev.append(f"Dialogue: {layer0 + li},{at(max(t0, t_in))},{at(t1)},X,,0,0,0,,"
                      f"{{\\an{align}\\pos({x + dx},{y + dy}){base}\\fs{fs}\\fsp{sp}\\1c{c}{anim}}}{text}")
    return ev

def chapter(t0, t1, num, title):
    """numbered list title, magazine style: small yellow number over a big white title, top-left"""
    return lockup(t0, t1, [(num, 54, YEL, 84, 258, 4, 1, t0 + 0.01), (title, 104, WHITE, 80, 340, 4, -0.5, t0 + 0.08)])

def title_events():
    ev = []
    # hook (frame 0): stacked, centred over her hairline - "How to see" small white, "a tiger" big yellow
    ev += lockup(0.0, T(3.20), [("How to see", 70, WHITE, 540, 236, 5, 0.5, 0.0), ("a tiger", 150, YEL, 540, 344, 5, -1, 0.0)])
    ev += lockup(T(3.28), T(6.93), [("ALL YOU NEED", 40, WHITE, 540, 262, 5, 8, T(3.28))])
    ev += chapter(T(8.08), T(10.06), "04", "The silence")
    ev += chapter(T(10.06), T(12.78), "05", "The alarm call")
    ev += chapter(T(12.78), T(14.05), "06", "The tiger")
    # CTA lockup over her chest (synced: "comment" -> "SAFARI" -> "first to know")
    t_c, t_s, t_f = CUT, T(35.70), T(36.54)
    ev += lockup(t_c, DUR, [("Comment", 72, WHITE, 540, 1150, 5, 0.5, t_c),
                            ("SAFARI", 176, YEL, 540, 1300, 5, 6, t_s),
                            ("to be the first to know", 46, WHITE, 540, 1440, 5, 0.5, t_f)])
    return ev

def build_ass(path, captions=True, titles=True):
    ev = []
    if captions:
        pages, _ = caption_pages()
        edges = sorted({x for a0, b0, *_ in SPLIT + FULL + CARDS for x in (a0, b0)})
        for pg in pages:
            if pg["idx"] in NO_CAPTION:
                continue
            words = pg["words"]
            lines = stack_lines(words)
            cuts = [pg["t0"]] + [e for e in edges if pg["t0"] < e < pg["t1"]] + [pg["t1"]]
            for j, (a, b) in enumerate(zip(cuts, cuts[1:])):   # re-seat the block when the layout changes
                if b - a > 0.02:
                    y = caption_y(a)
                    if len(lines) == 1:
                        sc = min(1.0, MAX_W / text_width(words, 1.0))
                        ev += line_events(words, a, b, y, sc, reveal=True)
                    else:
                        (l1, big1), (l2, big2) = lines
                        y1, y2 = (y - 64, y + 20) if big2 else (y - 34, y + 58)
                        for ln, yy in ((l1, y1), (l2, y2)):
                            sc = min(1.0, MAX_W / text_width(ln, 1.0, STACK_KW))
                            ev += line_events(ln, a, b, yy, sc, reveal=True, kw_fs=STACK_KW)
    if titles:
        ev += title_events()
    path.write_text(HDR + "\n".join(ev) + "\n", encoding="utf-8")

def build_srt(path):
    pages, _ = caption_pages()
    def st(t):
        return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
    out = [f"{i}\n{st(p['t0'])} --> {st(p['t1'])}\n{' '.join(w['text'] for w in p['words'])}\n" for i, p in enumerate(pages, 1)]
    path.write_text("\n".join(out), encoding="utf-8")


# ------------------------------------------------------------------ sound
LIB = ROOT / "sfx_library"
NS = int(DUR * SR)
_cache = {}

def load(name):
    if name not in _cache:
        r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(LIB / name), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                           capture_output=True, check=True)
        _cache[name] = np.frombuffer(r.stdout, np.float32).reshape(-1, 2).copy()
    return _cache[name]

def place(buf, name, src_in, src_out, at_t, gain_db=0.0, fin=0.01, fout=0.05, align="start", pan=0.0, norm=True):
    x = load(name)[int(src_in * SR):int(src_out * SR)].copy()
    if norm:
        x /= np.abs(x).max() + 1e-9
    n = len(x)
    fi, fo = max(1, int(fin * SR)), max(1, int(fout * SR))
    x[:fi] *= np.linspace(0, 1, fi)[:, None]
    x[-fo:] *= np.linspace(1, 0, fo)[:, None]
    if pan:
        a = (pan + 1) * np.pi / 4
        x[:, 0] *= np.cos(a) * 1.414; x[:, 1] *= np.sin(a) * 1.414
    if align == "peak":
        env = np.convolve(np.abs(x).mean(1), np.ones(960) / 960, "same")
        at_t -= env.argmax() / SR
    i = int(round(at_t * SR)); j0 = max(0, -i); i = max(0, i)
    m = min(n - j0, NS - i)
    if m > 0:
        buf[i:i + m] += x[j0:j0 + m] * 10 ** (gain_db / 20)

DS, DL = "dl_safari/", "dl_2026_11/"
POP = "msg_soft_pop.mp3"

def build_sfx():
    """v3 (client: "add the sound effects, rn it doesnt have those effects"): every visual move gets its own sound,
    mixed to be heard like the refs. Whoosh = layout change, pop = card/text in, tick = chapter number,
    shutter = photo, riser + impact = THE tiger reveal, reverse swell -> dead silence on "silent"."""
    b = np.zeros((NS, 2), np.float32)
    amb = np.zeros((NS, 2), np.float32)
    W1, SW, SC, SS = DS + "1491-preview.mp3", DL + "sweep_fast_small.mp3", DL + "swoosh_cinematic_wind.mp3", DL + "swoosh_short_wind.mp3"
    TICK, PL = DL + "click_interface_tone.mp3", DL + "pop_long.mp3"

    def whoosh(t, g=-12, kind=W1, pan=0.0):
        place(b, kind, 0.0, 1.2, t, g, align="peak", fout=0.25, pan=pan)

    def pop(t, g=-13, kind=POP):
        place(b, kind, 0.0, 0.45 if kind == POP else 0.4, t + 0.01, g, fin=0.002, fout=0.12)

    def tick(t, g=-15):
        place(b, TICK, 0.0, 0.2, t, g, fin=0.001, fout=0.06)

    # hook: she swings in + the title lands on frame 1
    whoosh(0.12, -11, SS); pop(0.0, -15, PL)
    # "to see a TIGER": first card rises in, drops out on her jump cut
    whoosh(T(2.40) + 0.08, -13); pop(T(2.40), -12)
    whoosh(T(3.20) + 0.05, -20, SS)
    tick(T(3.28), -14)                                                   # ALL YOU NEED
    # the list: card rises, then each next card swipes the last one out
    whoosh(T(4.12) + 0.08, -13); pop(T(4.12), -12)
    place(b, DS + "2712-preview.mp3", 0.9, 1.85, T(4.12) + 0.05, -19, fin=0.05, fout=0.35, pan=0.2)   # gypsy engine
    for t0, pan in ((T(4.76), 0.3), (T(5.52), -0.3)):
        whoosh(t0 + 0.06, -11, SW, pan); pop(t0 + 0.04, -15)
    place(b, DS + "peacock_call.ogg", 1.15, 2.35, T(5.70), -15, fin=0.02, fout=0.4, pan=-0.35)
    whoosh(T(6.93) + 0.05, -18, SS)                                      # list cards drop away
    # jungle at dawn under the list, gone on "silent"
    place(amb, DS + "2434-preview.mp3", 6.6, 6.6 + (SILENT - T(4.76)) + 0.05, T(4.76), -15, fin=0.6, fout=0.08, norm=False)
    # 04 the silence: split pushes down, number ticks in
    whoosh(T(8.08) + 0.12, -10, SC); tick(T(8.09), -14)
    # reverse swell that gets sucked into nothing exactly on "silent"
    rev = load(DL + "impact_reverse.mp3")
    pk = int(0.44 * SR)
    seg = rev[max(0, pk - int(0.9 * SR)):pk].copy()
    seg /= np.abs(seg).max() + 1e-9
    seg *= np.linspace(0, 1, len(seg))[:, None] ** 1.5 * 10 ** (-12 / 20)
    i1 = int(SILENT * SR); i0 = i1 - len(seg)
    b[i0:i1] += seg
    # 05 the alarm call
    whoosh(T(10.06) + 0.05, -13, SW); tick(T(10.07), -14)
    place(b, DS + "barking_deer_alarm.wav", 2.95, 3.75, BARKS[0], -5, align="peak", fin=0.01, fout=0.35, pan=-0.15)
    place(b, DS + "barking_deer_alarm.wav", 8.45, 9.25, BARKS[1], -8, align="peak", fin=0.01, fout=0.35, pan=0.25)
    # 06 THE TIGER (the one wow moment): riser under "and you will know", whoosh + sub impact on the cut
    place(b, DL + "riser_trailer.mp3", 0.4, 2.56, T(12.78) - 2.16, -15, fin=0.5, fout=0.02)
    place(b, DS + "2596-preview.mp3", 0.0, 2.2, T(12.78), -10, align="peak", fout=0.6)
    place(b, DL + "impact_whoosh_deep.mp3", 0.2, 2.6, T(12.78), -7, align="peak", fout=0.9)
    tick(T(12.80), -15)
    whoosh(T(14.05) + 0.05, -16, SS)                                     # back to her
    # "the way your heart will POUND"
    for hb, g in zip(HEARTBEATS, (-3, -7)):
        place(b, DS + "490-preview.mp3", 0.0, 1.1, hb, g, align="peak", fin=0.002, fout=0.25)
    # years of photographs: autofocus beep, split pushes in, a shutter on every photo
    place(b, DS + "1439-preview.mp3", 0.0, 0.5, SHUTTERS[0] - 0.32, -16, fin=0.002, fout=0.1)
    whoosh(SHUTTERS[0] + 0.1, -12, SC)
    for k, st in enumerate(SHUTTERS):
        place(b, DS + ("1430-preview.mp3" if k % 2 == 0 else "1440-preview.mp3"), 0.0, 0.6, st, -8, align="peak",
              fin=0.002, fout=0.1, pan=(-0.2 if k % 2 else 0.2))
    whoosh(T(22.55) + 0.05, -17, SS)
    # "your own eyes"
    whoosh(T(24.55) + 0.06, -11)
    place(b, DL + "impact_whoosh_deep.mp3", 0.2, 2.6, T(24.55), -14, align="peak", fout=0.7)
    whoosh(T(25.93) + 0.05, -17, SW)
    # Lost & Free: push, pop, shimmer
    whoosh(LOGO_SPLIT[0] + 0.12, -11, SC); pop(LOGO_SPLIT[0] + 0.05, -10, PL)
    sys.path.insert(0, str(P.parent / "lakshadweep_v2"))
    import synth as V2
    sh = V2.sfx_shimmer((86, 90, 93, 98), 0.06, 0.11)
    i = int((LOGO_SPLIT[0] + 0.05) * SR); n = min(len(sh), NS - i)
    b[i:i + n, 0] += sh[:n]; b[i:i + n, 1] += sh[:n]
    whoosh(LOGO_SPLIT[1] + 0.05, -17, SS)
    # CTA: jump-cut swoosh, "Comment" pops, "SAFARI" lands with weight, the last line ticks in
    whoosh(CUT + 0.05, -12, SW); pop(CUT + 0.01, -13, PL)
    pop(T(35.70), -9)
    place(b, DL + "impact_whoosh_deep.mp3", 0.2, 2.6, T(35.70) + 0.02, -15, align="peak", fout=0.8)
    tick(T(36.54), -15)
    # ---- v4 additions ("needs more sound effects"): every extra sound is motivated by a word or a move
    place(b, DS + "big_95.mp3", 0.35, 1.9, 0.18, -17, fin=0.05, fout=0.5)                 # cold open: low tiger growl
    whoosh(T(1.14) + 0.04, -14, SW)                                                        # cut from tiger to her
    place(b, DS + "big_5.mp3", 0.6, 3.0, T(12.78) + 0.12, -10, fin=0.04, fout=0.7)         # the reveal growls
    for k in range(3, 7):                                                                  # montage film-strip slides
        whoosh(SPLIT[k][0] + 0.07, -17, SW, (-0.3, 0.3)[k % 2])
    whoosh(T(16.93) + 0.03, -17, SW, 0.25); tick(T(16.93), -19)                            # "no REEL": phone flick
    tick(T(26.51), -12)                                                                    # "some SCREEN": screen tap
    place(b, "msg_iphone_text_received.mp3", 2.27, 3.05, T(33.54), -12, fin=0.003, fout=0.25)   # "coming out SOON": ping
    place(b, DL + "typing_smartphone.mp3", 2.45, 3.35, CUT + 0.08, -21, fin=0.02, fout=0.15)    # "comment": typing
    place(b, "msg_iphone_sent.mp3", 0.0, 1.5, T(35.70), -12, align="peak", fin=0.002, fout=0.2)  # "SAFARI": sent
    # jungle air under the second half
    place(amb, DS + "2434-preview.mp3", 8.0, 8.0 + (DUR - T(16.61)), T(16.61), -27, fin=1.0, fout=0.6, norm=False)
    t = np.arange(NS) / SR
    gate = np.ones(NS); kill = (t >= SILENT - 0.05) & (t < SILENT + 0.10)
    gate[kill] = np.linspace(1, 0, kill.sum()); gate[(t >= SILENT + 0.10) & (t < T(16.61))] = 0
    out = b + amb * gate[:, None]
    out[(t >= SILENT + 0.02) & (t < BARKS[0] - 0.25)] = 0.0          # dead air between "silent" and the first bark
    return out

VOICE = ("highpass=f=90:poles=2,afftdn=nf=-50:tn=1,"
         "equalizer=f=220:t=q:w=1.1:g=-3,equalizer=f=500:t=q:w=1.2:g=-1.5,"
         "equalizer=f=3300:t=q:w=1.0:g=3,equalizer=f=10000:t=h:w=0.7:g=2,"
         "deesser=i=0.3,acompressor=threshold=-24dB:ratio=3:attack=5:release=120:makeup=4,alimiter=limit=0.89:level=false")

def voice_wav():
    """source audio cut exactly like the picture (10 ms crossfade at the cut)"""
    fc = ("[0:a]aresample=48000,asplit=2[a][b];[a]atrim=start=0.07:end=33.90,asetpts=PTS-STARTPTS[x];"
          "[b]atrim=start=35.30:end=37.80,asetpts=PTS-STARTPTS[y];[x][y]acrossfade=d=0.012:c1=tri:c2=tri,"
          f"atrim=0:{DUR},apad=whole_dur={DUR}[v]")
    run(["ffmpeg", "-y", "-v", "error", "-i", str(ROOT / "inbox/safari/IMG_2240.MP4"), "-filter_complex", fc, "-map", "[v]",
         "-ac", "2", "-c:a", "pcm_f32le", str(B / "voice_cut.wav")])

def loudnorm(src, dst, I=-14, TP=-1.5):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af", f"loudnorm=I={I}:TP={TP}:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    ln = (f"loudnorm=I={I}:TP={TP}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-af", f"{ln},aresample={SR}", "-c:a", "pcm_s24le", str(dst)])
    return dst

def render_audio():
    fc = (f"[0:a]{VOICE},atrim=0:{DUR},apad=whole_dur={DUR},asplit=3[v][vsc][vsc2];"
          "[1:a]volume=-3dB[m0];[m0][vsc]sidechaincompress=threshold=0.02:ratio=6:attack=20:release=320:makeup=1[m];"
          "[2:a]volume=+1dB[s0];[s0][vsc2]sidechaincompress=threshold=0.12:ratio=1.4:attack=10:release=200[s];"
          f"[v][m][s]amix=inputs=3:normalize=0:duration=first,atrim=0:{DUR}[mix]")
    ins = ["-i", str(B / "voice_cut.wav"), "-i", str(B / "music.wav"), "-i", str(B / "sfx.wav")]
    run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", fc, "-map", "[mix]", "-c:a", "pcm_f32le", str(B / "mix_pre.wav")])
    fc2 = fc.replace("[v][m][s]amix=inputs=3", "[m]anullsink;[v][s]amix=inputs=2")
    run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", fc2, "-map", "[mix]", "-c:a", "pcm_f32le", str(B / "mix_nomusic_pre.wav")])
    return loudnorm(B / "mix_pre.wav", B / "mix.wav"), loudnorm(B / "mix_nomusic_pre.wav", B / "mix_nomusic.wav")

# ------------------------------------------------------------------ deliver
def run(cmd, **kw):
    print("  $", " ".join(str(c) for c in cmd)[:200])
    subprocess.run(cmd, check=True, **kw)

def encode(vf, audio, out):
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(B / "comp.mp4"), "-i", str(audio)]
    vf = (vf + "," if vf else "") + "setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv,format=yuv420p"
    cmd += ["-vf", vf, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high",
            "-x264-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "320k", "-ar", str(SR), "-movflags", "+faststart", "-shortest", str(out)]
    run(cmd, cwd=B)

def caption_qa():
    """captions + titles alone: inside x 110..970 / y 150..1536, and how often they touch her (padded) face box"""
    faces = json.loads((B / "faces.json").read_text())
    full = [(a, b) for a, b, *_ in FULL]
    build_ass(B / "qa.ass")
    cmd = ["ffmpeg", "-v", "error", "-f", "lavfi", "-i", f"color=c=black:s=1080x1920:r={FPS}:d={DUR}",
           "-vf", f"ass=qa.ass:fontsdir={FONTS_REL},scale=540:960", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=B)
    bad, touch, ext, fr = [], [], [9999, 9999, 0, 0], 0
    while True:
        buf = p.stdout.read(540 * 960)
        if len(buf) < 540 * 960:
            break
        m = np.frombuffer(buf, np.uint8).reshape(960, 540) > 40
        if m.any():
            ys, xs = np.where(m); x0, x1, y0, y1 = xs.min() * 2, xs.max() * 2, ys.min() * 2, ys.max() * 2
            ext = [min(ext[0], x0), min(ext[1], y0), max(ext[2], x1), max(ext[3], y1)]
            if x0 < 70 or x1 > 970 or y0 < 150 or y1 > 1536:
                bad.append(fr / FPS)
            t = fr / FPS
            if fr < len(faces) and faces[fr] and not in_full(t):
                fx, fy, fw, fh = faces[fr][0]
                z = base_zoom(t)       # face box was measured before zoom
                fx0, fx1 = 540 + (fx - 540) * z, 540 + (fx + fw - 540) * z
                fy0, fy1 = ANCHOR_Y + (fy - ANCHOR_Y) * z, ANCHOR_Y + (fy + fh - ANCHOR_Y) * z
                if in_split(t):        # her picture slides down into the lower panel
                    r0 = her_row(t)
                    fy0, fy1 = max(SEAM, fy0 + SEAM - r0), min(1920, fy1 + SEAM - r0)
                sub = m[int(fy0 / 2):int(fy1 / 2), int(fx0 / 2):int(fx1 / 2)]
                if sub.size and sub[:, :].any():
                    # eyes/nose/mouth are the middle of the box; touching hair/chin edge is OK
                    core = m[int((fy0 + 0.15 * (fy1 - fy0)) / 2):int((fy0 + 0.85 * (fy1 - fy0)) / 2),
                             int((fx0 + 0.15 * (fx1 - fx0)) / 2):int((fx0 + 0.85 * (fx1 - fx0)) / 2)]
                    if core.any():
                        touch.append(round(t, 1))
        fr += 1
    p.wait()
    print(f"text extents x {ext[0]}..{ext[2]}  y {ext[1]}..{ext[3]}  frames outside safe: {len(bad)}  frames on face core: {len(touch)}")
    if touch:
        print("  face-core times:", sorted(set(touch)))

def main(skip_comp=False):
    OUT.mkdir(exist_ok=True)
    if not skip_comp or not (B / "comp.mp4").exists():
        composite()
    build_ass(B / "captions.ass")
    build_ass(B / "titles_only.ass", captions=False)
    build_srt(OUT / f"{NAME}.srt")
    caption_qa()
    sfx = build_sfx()
    pk = np.abs(sfx).max()
    if pk > 0.95:
        sfx *= 0.95 / pk
    wavfile.write(B / "sfx.wav", SR, sfx.astype(np.float32))
    voice_wav()
    mix, mix_nm = render_audio()
    encode(f"ass=captions.ass:fontsdir={FONTS_REL}", mix, OUT / f"{NAME}.mp4")
    encode(f"ass=captions.ass:fontsdir={FONTS_REL}", mix_nm, OUT / f"{NAME}_no_music.mp4")
    encode("", mix, OUT / f"{NAME}_clean.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-ss", "2.6", "-i", str(OUT / f"{NAME}.mp4"), "-frames:v", "1", str(OUT / f"{NAME}_cover.png")])

if __name__ == "__main__":
    main(skip_comp="--skip-comp" in sys.argv)
