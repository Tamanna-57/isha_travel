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
    (T(2.40), T(3.20), "tiger_trees.jpg", 0.50, 0.42, 1.25, None, None, 0),
    (T(4.12), T(4.76), "gypsy.jpg", 0.52, 0.55, 1.05, "01", "An open jeep", 1),
    (T(4.76), T(5.52), "jeep_sal_forest.jpg", 0.55, 0.55, 1.05, "02", "In the jungle", 1),
    (T(5.52), T(6.93), "jungle_road_mist.jpg", 0.50, 0.55, 1.05, "03", "At 6 AM", 1),
]
SEAM, HER_ROW0 = 840, 240
SPLIT = [   # (t0, t1, image or "LOGO", fx, fy, z0, z1)
    (T(8.08), T(10.06), "sal_forest.jpg", 0.50, 0.50, 1.00, 1.07),
    (T(10.06), T(12.78), "chital_fawn.jpg", 0.45, 0.17, 1.00, 1.04),
    (T(19.77), T(20.13), "leopard.jpg", 0.42, 0.45, 1.10, 1.13),
    (T(20.13), T(20.50), "elephant.jpg", 0.56, 0.40, 1.00, 1.03),
    (T(20.50), T(20.93), "sloth_bear.jpg", 0.33, 0.45, 1.25, 1.28),
    (T(20.93), T(21.43), "peacock.jpg", 0.45, 0.30, 1.00, 1.03),
    (T(21.43), T(22.55), "tiger_yawn.jpg", 0.52, 0.50, 1.00, 1.06),
    (T(30.15), T(32.43), "LOGO", 0, 0, 1, 1),                      # only while she says the brand name
]
SHUTTERS = [x[0] for x in SPLIT[2:7]]
LOGO_SPLIT = (T(30.15), T(32.43))
BARKS = [T(10.56), T(11.62)]
FULL = [
    (T(12.78), T(14.05), "tiger_trail_jeep.jpg", 0.42, 0.62, 1.00, 1.10, None),   # HERO: "it's right there"
    (T(24.55), T(25.93), "tiger_eyes.jpg", 0.60, 0.58, 1.00, 1.07, None),         # "with your own eyes"
]
SILENT = T(9.06)
HEARTBEATS = [T(15.02), T(15.82)]
ANCHOR_Y = 700

def in_split(t):
    return any(a <= t < b for a, b, *_ in SPLIT)

def in_full(t):
    return any(a <= t < b for a, b, *_ in FULL)

def card_at(t):
    return any(a <= t < b for a, b, *_ in CARDS)

def shot_index(t):
    return max(0, np.searchsorted(SHOTS, t, side="right") - 1)

def base_zoom(t):
    """camera on her: slow push inside each shot, alternate shots punched in (hides/accents the jump cuts)"""
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
    split_starts = [s[0] for s in splits]
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
        # ---- ref 1 split screen
        for t0, t1, img, fx, fy, z0, z1 in splits:
            if t0 <= t < t1:
                zz = z0 + (z1 - z0) * (t - t0) / (t1 - t0)
                for bk in BARKS:                                        # snap-zoom on each bark
                    if t0 <= bk <= t < bk + 0.6:
                        zz *= 1 + 0.07 * expo_out((t - bk) / 0.12) * (1 - 0.6 * min(1, (t - bk - 0.12) / 0.45) if t > bk + 0.12 else 1)
                if img is None:
                    top = logo_bg.copy()
                    a = expo_out((t - t0) / 0.4)
                    lr = cv2.resize(logo_rgba, None, fx=0.95 + 0.05 * a, fy=0.95 + 0.05 * a, interpolation=cv2.INTER_AREA)
                    blend_rgba(top, lr, logo_xy[0] + logo_img.width / 2, logo_xy[1] + logo_img.height / 2, 1.0, a)
                else:
                    top = crop_cover(img, 1080, SEAM, fx, fy, zz)
                    if SILENT <= t < T(10.06):
                        k = expo_out((t - SILENT) / 0.6)
                        top = desat(top, 1 - 0.45 * k, 1 - 0.08 * k)
                for st in SHUTTERS:                                     # shutter: quick flash on the photo only
                    if 0 <= t - st < 0.1:
                        top = np.clip(top.astype(np.float32) + 255 * 0.35 * (1 - (t - st) / 0.1), 0, 255).astype(np.uint8)
                her = frame[HER_ROW0:HER_ROW0 + 1920 - SEAM]
                if t0 in entering and t - t0 < 0.3:                     # push-down entrance
                    p = expo_out((t - t0) / 0.3)
                    off = int(round(SEAM * (1 - p)))                      # photo panel slides down from the top
                    out = frame.copy()
                    shift = int(round((SEAM - HER_ROW0) * p))           # her picture slides down by up to 600 px
                    out[shift:] = frame[:1920 - shift]
                    out[:SEAM - off] = top[off:]
                    frame = out
                else:
                    frame = np.vstack([top, her])
        # ---- ref 1 full-screen beats
        for t0, t1, img, fx, fy, z0, z1 in fulls:
            if t0 <= t < t1:
                zz = z0 + (z1 - z0) * expo_out((t - t0) / (t1 - t0) * 0.8)
                frame = crop_cover(img, 1080, 1920, fx, fy, zz)
        frame = texture(frame, fi, scrim)
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

def text_width(words, scale):
    tot = 0
    for j, w in enumerate(words):
        f = pil_font(FONT_FILE, int((KW_FS if w["kw"] else CAP_FS) * EM * scale))
        tot += f.getlength(w["text"] + (" " if j < len(words) - 1 else ""))
    return tot

def caption_y(t):
    if in_split(t + 0.01):
        return SEAM                         # ref 1: on the seam
    if card_at(t + 0.01):
        return 1112                         # ref 2: just above the card
    return 1268                             # her chest, over the bottom scrim

LAYERS = (  # glow, tight drop shadow, fill
    ("glow", rf"\1c{BLK}\3c{BLK}\bord6\blur14", r"\1a&HA0&\3a&HA0&", 0, 3),
    ("drop", rf"\1c{BLK}\3c{BLK}\bord1\blur3", r"\1a&H70&\3a&H88&", 2, 4),
    ("fill", r"\bord0\blur0", r"\1a&H00&", 0, 0),
)

def line_events(words, t_from, t_to, y, scale, reveal=True, layer0=1, x=540, align=5, extra=""):
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
                fs = (KW_FS if w["kw"] else CAP_FS) * scale
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
            sc = min(1.0, MAX_W / text_width(words, 1.0))
            cuts = [pg["t0"]] + [e for e in edges if pg["t0"] < e < pg["t1"]] + [pg["t1"]]
            for j, (a, b) in enumerate(zip(cuts, cuts[1:])):   # re-seat the line when the layout changes
                if b - a > 0.02:
                    ev += line_events(words, a, b, caption_y(a), sc, reveal=True)
    if titles:
        ev += title_events()
    path.write_text(HDR + "\n".join(ev) + "\n", encoding="utf-8")

def build_srt(path):
    pages, _ = caption_pages()
    def st(t):
        return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
    out = [f"{i}\n{st(p['t0'])} --> {st(p['t1'])}\n{' '.join(w['text'] for w in p['words'])}\n" for i, p in enumerate(pages, 1)]
    path.write_text("\n".join(out), encoding="utf-8")

