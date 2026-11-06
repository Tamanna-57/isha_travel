"""Safari announcement reel (IMG_2240.MP4), Lost & Free Safaris collab. Built 2026-11-04.

References: Video-11291.mp4 (MAIN: talking head + photo cards held at chest, bold pale-yellow sans titles up top,
one-word pale-yellow captions above the card) and Video-96135.mp4 (full-screen B-roll beats, Instrument Serif
Italic keywords, whooshes). Client: "2nd video is more the one u take inspo from, dont do it overextra".

Pipeline:  python make_lut.py && python base.py && python align.py && python synth.py && python make.py
  base.py   -> build/base.mp4  (HLG->SDR, safari_soft LUT, cut 33.90-35.30 "and if you want then")
  make.py   -> composite photos/cards/zoom (numpy) -> captions+titles (libass) -> sfx + mix -> out/
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np, cv2
from scipy.io import wavfile

P = Path(__file__).resolve().parent
ROOT = P.parent.parent
B, OUT, A = P / "build", P / "out", P / "assets"
NAME = "safari_reel"
FPS, SR = 30, 48000
NF = 1089
DUR = NF / FPS                      # 36.30
FONTS_REL = "../../../fonts"

def T(src):
    """source time -> final timeline (base.py drops 0.00-0.07 and 33.90-35.30)"""
    return src - 0.07 if src < 33.90 else src - 1.47

CUT = T(35.30)                      # 33.83: jump cut (punch-in hides it)

# ------------------------------------------------------------------ visuals (all times FINAL)
# cards: (t0, t1, image, focus x, focus y, crop zoom) - ref 2 style photo held in front of her chest
# v2 (client: "font exactly like Video-11291", their own draft was "over done"): ref 2 layout throughout.
# Measured on ref 2 (720x1280 -> x1.5): card 495x476, centred x 540 / y 1427; square corners, faint shadow.
CARD_C, CARD_W, CARD_H = (540, 1430), 496, 476
CARDS = [   # ref 2: photo cards on her chest for the list beats
    (T(2.40), T(3.20), "tiger_trees.jpg", 0.50, 0.42, 1.25),     # "...to see a TIGER"
    (T(4.12), T(4.76), "gypsy.jpg", 0.52, 0.55, 1.0),            # 1. an open jeep
    (T(4.76), T(5.52), "jeep_sal_forest.jpg", 0.55, 0.55, 1.0),  # 2. in the jungle
    (T(5.52), T(6.93), "jungle_road_mist.jpg", 0.5, 0.55, 1.0),  # 3. at 6 AM
]
# ref 1 (Video-96135) layout, added 2026-11-04 on request: SPLIT screen = photo on top, Isha talking underneath,
# caption sitting on the seam. Her picture is slid down so her face lands in the lower panel.
SEAM = 840                             # top panel 0..840, her panel 840..1920 (shows her rows 240..1320)
HER_ROW0 = 240
SPLIT = [   # (t0, t1, image or "LOGO", fx, fy, z0, z1)
    (T(8.08), T(10.06), "sal_forest.jpg", 0.50, 0.50, 1.00, 1.06),    # 4. the silence
    (T(10.06), T(12.78), "chital_fawn.jpg", 0.45, 0.17, 1.00, 1.05),  # 5. the alarm call
    # "years photographing these moments on my camera" (client's flag): photos change on each shutter
    (T(19.77), T(20.13), "leopard.jpg", 0.42, 0.45, 1.10, 1.12),
    (T(20.13), T(20.50), "elephant.jpg", 0.56, 0.40, 1.00, 1.02),
    (T(20.50), T(20.93), "sloth_bear.jpg", 0.33, 0.45, 1.25, 1.27),
    (T(20.93), T(21.43), "peacock.jpg", 0.45, 0.30, 1.00, 1.02),
    (T(21.43), T(22.55), "tiger_yawn.jpg", 0.52, 0.50, 1.00, 1.05),
    (T(30.15), T(32.43), "LOGO", 0, 0, 1, 1),                          # only while she says the brand name
]
SHUTTERS = [x[0] for x in SPLIT[2:7]]
LOGO_SPLIT = (T(30.15), T(32.43))
# ref 1 full-screen beats (two only)
FULL = [
    (T(12.78), T(14.05), "tiger_trail_jeep.jpg", 0.42, 0.62, 1.00, 1.09, None),   # "it's right there"
    (T(24.55), T(25.93), "tiger_eyes.jpg", 0.60, 0.58, 1.00, 1.06, None),         # "with your own eyes"
]

def in_split(t):
    return any(a <= t < b for a, b, *_ in SPLIT)

def in_full(t):
    return any(a <= t < b for a, b, *_ in FULL)

SILENT = T(9.06)                       # "everything will go SILENT": ambience + music stop here
HEARTBEATS = [T(15.02), T(15.82)]      # "pound" (zoom pulse on the lub)
ANCHOR_Y = 700                         # zoom anchor on her face (output px)

def rounded_rgba(img, w, h, r=22):
    if r == 0:
        return np.dstack([img, np.full((h, w), 255, np.uint8)])
    a = np.zeros((h, w), np.uint8)
    cv2.rectangle(a, (r, 0), (w - r, h), 255, -1); cv2.rectangle(a, (0, r), (w, h - r), 255, -1)
    for cx, cy in ((r, r), (w - r - 1, r), (r, h - r - 1), (w - r - 1, h - r - 1)):
        cv2.circle(a, (cx, cy), r, 255, -1, cv2.LINE_AA)
    return np.dstack([img, a])

def with_shadow(rgba, pad=50, blur=22, off=12, alpha=0.45):
    h, w = rgba.shape[:2]
    out = np.zeros((h + 2 * pad, w + 2 * pad, 4), np.float32)
    sh = np.zeros((h + 2 * pad, w + 2 * pad), np.float32)
    sh[pad + off:pad + off + h, pad:pad + w] = rgba[..., 3] / 255.0
    sh = cv2.GaussianBlur(sh, (0, 0), blur) * alpha
    out[..., 3] = sh
    a = rgba[..., 3:4] / 255.0
    reg = out[pad:pad + h, pad:pad + w]
    reg[..., :3] = rgba[..., :3] * a + reg[..., :3] * (1 - a)
    reg[..., 3] = a[..., 0] + reg[..., 3] * (1 - a[..., 0])
    return out

def crop_cover(img, w, h, fx, fy, z=1.0):
    ih, iw = img.shape[:2]
    s = max(w / iw, h / ih) * z
    cw, ch = w / s, h / s
    x0 = np.clip(fx * iw - cw / 2, 0, iw - cw); y0 = np.clip(fy * ih - ch / 2, 0, ih - ch)
    M = np.array([[s, 0, -x0 * s], [0, s, -y0 * s]], np.float32)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

def load_rgb(name):
    im = cv2.imread(str(A / name), cv2.IMREAD_COLOR)
    return cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

def photo_grade(img):
    """sit the web photos next to the footage: a hair less saturation, highlights kept off clip"""
    f = img.astype(np.float32) / 255
    f = 0.01 + 0.97 * f
    g = f.mean(2, keepdims=True)
    f = g + (f - g) * 0.95
    return np.clip(f * 255, 0, 255).astype(np.uint8)

def build_cards():
    out = []
    for t0, t1, name, fx, fy, z in CARDS:
        img = photo_grade(crop_cover(load_rgb(name), CARD_W, CARD_H, fx, fy, z))
        out.append((t0, t1, with_shadow(rounded_rgba(img, CARD_W, CARD_H, 0), blur=16, off=8, alpha=0.28)))   # ref 2: plain square photo
    return out

def make_logo_panel():
    """Lost & Free's forest green with their cream logo, full width of the top panel"""
    lg = cv2.cvtColor(cv2.imread(str(A / "logo.png"), cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA)
    panel = np.zeros((SEAM, 1080, 3), np.uint8); panel[:] = (51, 64, 51)
    lw = 760; lh = int(lg.shape[0] * lw / lg.shape[1])
    l = cv2.resize(lg, (lw, lh), interpolation=cv2.INTER_AREA).astype(np.float32)
    x0, y0 = (1080 - lw) // 2, (SEAM - lh) // 2 + 40
    al = l[..., 3:4] / 255
    panel[y0:y0 + lh, x0:x0 + lw] = (l[..., :3] * al + panel[y0:y0 + lh, x0:x0 + lw] * (1 - al)).astype(np.uint8)
    return panel

def ease_back(x, k=1.6):
    x = np.clip(x, 0, 1) - 1
    return 1 + (k + 1) * x ** 3 + k * x ** 2

def blend(frame, rgba, cx, cy, scale, alpha):
    if scale != 1.0:
        rgba = cv2.resize(rgba, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    h, w = rgba.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(1080, x0 + w), min(1920, y0 + h)
    src = rgba[ya - y0:yb - y0, xa - x0:xb - x0]
    a = src[..., 3:4] * alpha
    reg = frame[ya:yb, xa:xb].astype(np.float32)
    frame[ya:yb, xa:xb] = (src[..., :3] * a + reg * (1 - a)).astype(np.uint8)

def base_zoom(t):
    z = 1.0
    if t >= CUT:
        z = 1.09                                         # punch-in hides the jump cut
    for hb in HEARTBEATS:
        d = t - hb
        if 0 <= d < 0.45:
            z *= 1 + 0.035 * np.sin(np.pi * min(1, d / 0.08) / 2) * np.exp(-max(0, d - 0.08) * 9)
    return z

def composite():
    cards = build_cards()
    fulls = [(t0, t1, photo_grade(load_rgb(n)), fx, fy, z0, z1, snap) for t0, t1, n, fx, fy, z0, z1, snap in FULL]
    splits = [(t0, t1, None if n == "LOGO" else photo_grade(load_rgb(n)), fx, fy, z0, z1) for t0, t1, n, fx, fy, z0, z1 in SPLIT]
    logo_panel = make_logo_panel()
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
        z = base_zoom(t)
        s = 0.75 * z
        ay = ANCHOR_Y
        M = np.array([[s, 0, 540 - 720 * s], [0, s, ay - (ay / 0.75) * s]], np.float32)
        frame = cv2.warpAffine(src, M, (1080, 1920), flags=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR,
                               borderMode=cv2.BORDER_REFLECT)
        for t0, t1, img, fx, fy, z0, z1 in splits:
            if t0 <= t < t1:
                zz = z0 + (z1 - z0) * (t - t0) / (t1 - t0)
                her = frame[HER_ROW0:HER_ROW0 + 1920 - SEAM].copy()
                top = logo_panel if img is None else crop_cover(img, 1080, SEAM, fx, fy, zz)
                frame = np.vstack([top, her])
        for t0, t1, img, fx, fy, z0, z1, snap in fulls:
            if t0 <= t < t1:
                zz = z0 + (z1 - z0) * (t - t0) / (t1 - t0)
                if snap is not None and t >= snap:
                    zz *= 1 + 0.06 * min(1, (t - snap) / 0.12)        # snap-zoom on the bark
                frame = crop_cover(img, 1080, 1920, fx, fy, zz)
        for t0, t1, rgba in cards:
            if t0 <= t < t1:
                age = t - t0
                sc = 0.94 + 0.06 * ease_back(age / 0.14)            # ref 2 cards basically cut in; just a hint of pop
                al = min(1.0, age / 0.06)
                cy = CARD_C[1]
                blend(frame, rgba, CARD_C[0], cy, sc, al)
        for st in SHUTTERS:                                             # tiny flash on each shutter
            d = t - st
            if 0 <= d < 0.10:
                frame = np.clip(frame.astype(np.float32) + 255 * 0.10 * (1 - d / 0.10), 0, 255).astype(np.uint8)
        enc.stdin.write(frame.tobytes())
        if fi % 150 == 0:
            print(f"  composite {fi}/{NF}", flush=True)
    enc.stdin.close(); enc.wait(); dec.wait()

# ------------------------------------------------------------------ text
# v2: ONE typeface like ref 2 (Video-11291): a heavy, tight grotesque (looks like SF Pro Display Heavy, which can't be
# licensed off-Apple). Closest free match: Inter Display ExtraBold (fonts/InterDisplay-ExtraBold.ttf, cut from Inter-VF
# opsz 32 / wght 800). Sizes calibrated to ref 2 at 1080 px: title cap height ~41 px, caption "trip" ~80 px wide,
# subtitle cap ~22 px. Pale yellow #F6EEA2, soft dark drop shadow, no outline, no serif accents, no animation.
YEL = "&H00A2EEF6&"
SUBC = "&H00F3EDED&"                 # ref 2 subtitle white (#EDEDF3)
FONT, FONT_SUB = "Inter Display ExtraBold", "Inter Display Bold"
FS_TITLE, FS_WORD, FS_SUB = 84, 72, 44
WORD_Y, TITLE_Y = 1150, 300
TITLES = [  # (t0, t1, line, sub) - ref 2's list format: a numbered title per beat
    (0.0, T(3.20), "How to see a tiger", "Safari Edition"),
    (T(3.28), T(4.12), "All you need:", None),
    (T(4.12), T(4.76), "1. An open jeep", None),
    (T(4.76), T(5.52), "2. In the jungle", None),
    (T(5.52), T(6.93), "3. At 6 AM", None),
    (T(8.08), T(10.06), "4. The silence", None),
    (T(10.06), T(12.78), "5. The alarm call", None),
    (T(12.78), T(16.61), "6. The tiger", None),
    (CUT, DUR, "Comment “SAFARI”", "and be the first to know"),
]

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
Style: T,{FONT},{FS_TITLE},{YEL},{YEL},&H00000000,&H00000000,0,0,0,0,100,100,0.6,0,1,0,0,5,0,0,0,1
Style: W,{FONT},{FS_WORD},{YEL},{YEL},&H00000000,&H00000000,0,0,0,0,100,100,0.5,0,1,0,0,5,0,0,0,1
Style: S,{FONT_SUB},{FS_SUB},{SUBC},{SUBC},&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def text_layers(t0, t1, style, x, y, txt, layer):
    """ref 2 look: crisp fill + a soft dark drop shadow (wide faint glow + tight offset shadow), as separate layers"""
    glow = rf"{{\an5\pos({x},{y + 3})\1c&H000000&\1a&HA8&\bord5\3c&H000000&\3a&HA8&\blur12}}"
    drop = rf"{{\an5\pos({x + 2},{y + 4})\1c&H000000&\1a&H78&\bord1\3c&H000000&\3a&H90&\blur3}}"
    fill = rf"{{\an5\pos({x},{y})}}"
    return [f"Dialogue: {layer},{at(t0)},{at(t1)},{style},,0,0,0,,{glow}{txt}",
            f"Dialogue: {layer + 1},{at(t0)},{at(t1)},{style},,0,0,0,,{drop}{txt}",
            f"Dialogue: {layer + 2},{at(t0)},{at(t1)},{style},,0,0,0,,{fill}{txt}"]

def caption_words():
    raw = json.loads((B / "words.json").read_text(encoding="utf-8"))
    ws = []
    for w in raw:
        if 33.90 <= w["start"] < 35.30:          # "and if you want then" is cut out
            continue
        txt = w["text"].strip(".,?!…").replace("...", "")
        txt = {"am": "AM"}.get(txt, txt)
        ws.append({"text": txt, "t": T(w["start"]), "end": T(w["end"])})
    # ref 2 shows ONE word at a time; a word followed within 0.15 s rides with the next one (no 2-frame flashes)
    groups, cur = [], []
    for i, w in enumerate(ws):
        cur.append(w)
        nxt = ws[i + 1] if i + 1 < len(ws) else None
        if nxt and nxt["t"] - cur[0]["t"] < 0.15 and len(cur) < 2:
            continue
        groups.append(cur); cur = []
    ev = []
    for i, g in enumerate(groups):
        t0 = g[0]["t"]
        nxt = groups[i + 1][0]["t"] if i + 1 < len(groups) else DUR
        t1 = min(nxt, g[-1]["end"] + 0.45, DUR)
        if CUT - 0.02 > t0 and t1 > CUT:
            t1 = CUT
        ev.append((t0, t1, " ".join(w["text"] for w in g)))
    return ev, ws

def title_events():
    ev = []
    for t0, t1, line, sub in TITLES:
        ev += text_layers(t0, t1, "T", 540, TITLE_Y, line, 4)
        if sub:
            ev += text_layers(t0, t1, "S", 540, TITLE_Y + 62, sub, 4)
    return ev

def build_ass(path, captions=True, titles=True):
    ev = []
    if captions:
        cw, _ = caption_words()
        edges = sorted({x for a0, b0, *_ in SPLIT + FULL for x in (a0, b0)})
        for a, b, txt in cw:
            cuts = [a] + [e for e in edges if a < e < b] + [b]       # re-seat the word when the layout changes
            for c0, c1 in zip(cuts, cuts[1:]):
                if c1 - c0 > 0.02:
                    ev += text_layers(c0, c1, "W", 540, SEAM if in_split(c0 + 0.01) else WORD_Y, txt, 1)   # ref 1: on the seam
    if titles:
        ev += title_events()
    path.write_text(HDR + "\n".join(ev) + "\n", encoding="utf-8")

def build_srt(path):
    _, ws = caption_words()
    lines, cur = [], []
    for w in ws:                                   # SRT in short phrases, broken at punctuation-ish gaps
        cur.append(w)
        if len(cur) >= 5 or w["text"] in ("tiger", "morning", "silent", "ring", "there", "moment", "that", "camera",
                                          "eyes", "screen", "you", "soon", "know"):
            lines.append(cur); cur = []
    if cur:
        lines.append(cur)
    def st(t):
        return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
    out = [f"{i}\n{st(l[0]['t'])} --> {st(l[-1]['end'] + 0.2)}\n{' '.join(w['text'] for w in l)}\n" for i, l in enumerate(lines, 1)]
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
    """Restrained, story-led: soft pops on each card (ref 2), real jungle sounds, and ONE big moment of silence."""
    b = np.zeros((NS, 2), np.float32)
    amb = np.zeros((NS, 2), np.float32)            # ambience bus (gets its own fades)
    place(b, DL + "swoosh_short_wind.mp3", 0.0, 0.5, 0.10, -22, align="peak", fout=0.2)       # she swings into frame
    for t0 in (T(2.40), T(3.28), T(4.12), T(4.76), T(5.52)):                                    # card / list pops (ref 2)
        place(b, POP, 0.0, 0.5, t0 + 0.01, -15, fin=0.002, fout=0.15)
    for t0 in (T(8.08), T(10.06), LOGO_SPLIT[0]):                                                 # split-screen cuts (ref 1)
        place(b, DL + "swoosh_short_wind.mp3", 0.0, 0.5, t0, -21, align="peak", fout=0.2)
    for t0 in ():
        place(b, POP, 0.0, 0.5, t0 + 0.01, -15, fin=0.002, fout=0.15)
    place(b, DS + "2712-preview.mp3", 0.9, 1.85, T(4.12) + 0.05, -26, fin=0.05, fout=0.35, pan=0.2)   # gypsy engine, far
    # jungle at dawn: birds from "in the jungle", a peacock on "6 AM", all of it gone on "silent"
    place(amb, DS + "2434-preview.mp3", 6.6, 6.6 + (SILENT - T(4.76)) + 0.05, T(4.76), -21, fin=0.6, fout=0.08, norm=False)
    place(b, DS + "peacock_call.ogg", 1.15, 2.35, T(5.70), -22, fin=0.02, fout=0.4, pan=-0.35)
    # ---- silence ---- then the alarm: two real barking-deer barks (Commons, Pench/forest recording)
    place(b, DS + "barking_deer_alarm.wav", 2.95, 3.75, T(10.56), -9, align="peak", fin=0.01, fout=0.35, pan=-0.15)
    place(b, DS + "barking_deer_alarm.wav", 8.45, 9.25, T(11.62), -12, align="peak", fin=0.01, fout=0.35, pan=0.25)
    # "it's right there": cut to the tiger walking at the jeep
    place(b, DL + "sweep_fast_small.mp3", 0.0, 0.7, T(12.78), -20, align="peak", fout=0.2)
    place(b, DL + "impact_whoosh_deep.mp3", 0.2, 2.6, T(12.78), -11, align="peak", fout=0.9)
    # "the way your heart will POUND"
    for hb, g in zip(HEARTBEATS, (-7, -11)):
        place(b, DS + "490-preview.mp3", 0.0, 1.1, hb, g, align="peak", fin=0.002, fout=0.25)
    # years of photographs: a shutter on every card
    for k, st in enumerate(SHUTTERS):
        place(b, DS + ("1430-preview.mp3" if k % 2 == 0 else "1440-preview.mp3"), 0.0, 0.6, st, -14, align="peak",
              fin=0.002, fout=0.1, pan=(-0.15 if k % 2 else 0.15))
    # "your own eyes": tiger full frame
    place(b, DL + "swoosh_short_wind.mp3", 0.0, 0.5, T(24.55), -19, align="peak", fout=0.2)
    place(b, DL + "impact_whoosh_deep.mp3", 0.2, 2.6, T(24.55), -20, align="peak", fout=0.7)
    # Lost & Free reveal: pop + shimmer
    place(b, POP, 0.0, 0.5, LOGO_SPLIT[0] + 0.01, -12, fin=0.002, fout=0.15)
    sys.path.insert(0, str(P.parent / "lakshadweep_v2"))
    import synth as V2
    sh = V2.sfx_shimmer((86, 90, 93, 98), 0.06, 0.07)
    i = int(LOGO_SPLIT[0] * SR); b[i:i + len(sh), 0] += sh[:NS - i] * 0.8; b[i:i + len(sh), 1] += sh[:NS - i] * 0.8
    # jump cut into the CTA
    place(b, DL + "sweep_fast_small.mp3", 0.0, 0.7, CUT, -22, align="peak", fout=0.2)
    place(b, POP, 0.0, 0.5, CUT + 0.01, -16, fin=0.002, fout=0.15)
    # quiet jungle air under the second half (she's outdoors; makes the garden feel like the forest edge)
    place(amb, DS + "2434-preview.mp3", 8.0, 8.0 + (DUR - T(16.61)), T(16.61), -33, fin=1.0, fout=0.6, norm=False)
    t = np.arange(NS) / SR
    gate = np.ones(NS); kill = (t >= SILENT - 0.05) & (t < SILENT + 0.10)
    gate[kill] = np.linspace(1, 0, kill.sum()); gate[(t >= SILENT + 0.10) & (t < T(16.61))] = 0
    return b + amb * gate[:, None]

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
          "[2:a]volume=-1dB[s0];[s0][vsc2]sidechaincompress=threshold=0.06:ratio=2:attack=15:release=250[s];"
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
            if x0 < 110 or x1 > 970 or y0 < 150 or y1 > 1536:
                bad.append(fr / FPS)
            t = fr / FPS
            if fr < len(faces) and faces[fr] and not in_full(t):
                fx, fy, fw, fh = faces[fr][0]
                z = base_zoom(t)       # face box was measured before zoom
                fx0, fx1 = 540 + (fx - 540) * z, 540 + (fx + fw - 540) * z
                fy0, fy1 = ANCHOR_Y + (fy - ANCHOR_Y) * z, ANCHOR_Y + (fy + fh - ANCHOR_Y) * z
                if in_split(t):        # her picture slides down into the lower panel
                    fy0, fy1 = max(SEAM, fy0 + SEAM - HER_ROW0), min(1920, fy1 + SEAM - HER_ROW0)
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
