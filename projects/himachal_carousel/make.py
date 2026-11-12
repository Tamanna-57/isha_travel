#!/usr/bin/env python3
"""
Himachal 3-villages carousel renderer (Kalpa / Chitkul / Tosh) for @travelwithisha.

Reads slides.json, puts Isha's photos from photos/ under the text, and renders
9 slides at 1080x1350 (4:5) in the house type system:
  - big titles / cover hook  -> Anton
  - serif lines / facts       -> Playfair Display (SemiBold / Italic)
  - handwritten "notes from Isha" / tips -> Caveat (marigold)
  - handle + counters         -> Montserrat
Natural grade, upper-third text (anton.cltx carousel reference), text kept inside
the 4:5 safe area. Missing photos render as a labelled placeholder that doubles as
the shot brief, so the layout + copy can be reviewed before the real photos arrive.

    python projects/himachal_carousel/make.py        # -> out/slide_01.png ... slide_09.png + out/contact.png

Deps: Pillow, numpy (same as the reel pipeline).
"""
import json, os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(ROOT, "fonts")
PHOTOS = os.path.join(HERE, "photos")
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# ---- brand tokens (RGB) ---------------------------------------------------
C = {
    "ink": (17, 17, 17), "chalk": (255, 255, 255), "ivory": (255, 246, 229),
    "marigold": (246, 196, 69), "sindoor": (215, 38, 61), "saffron": (243, 156, 43),
    "paper": (247, 243, 234), "grey": (154, 154, 154),
}

def font(fname, size):
    return ImageFont.truetype(os.path.join(FONTS, fname), size)

F = {
    "anton":   lambda s: font("Anton-Regular.ttf", s),
    "serif":   lambda s: font("PlayfairDisplay-SemiBold.ttf", s),
    "serif_i": lambda s: font("PlayfairDisplay-Italic.ttf", s),
    "caveat":  lambda s: font("Caveat-Bold.ttf", s),
    "mont":    lambda s: font("Montserrat-SemiBold.ttf", s),
    "mont_b":  lambda s: font("Montserrat-Bold.ttf", s),
}

# ---- geometry -------------------------------------------------------------
W, H = 1080, 1350
MARGIN = 96
COLW = W - 2 * MARGIN          # text column width

# =========================================================================
# photo / placeholder
# =========================================================================
def natural_grade(im):
    """A light, true-to-life lift: tiny S-curve contrast, lifted blacks, warm mids,
    gentle vibrance. Not a filter. Mirrors luts/Isha_Natural in spirit."""
    a = np.asarray(im).astype(np.float32) / 255.0
    # lift blacks ~8/255, soft highlight roll-off, +4% contrast around 0.5
    a = 0.031 + a * 0.945
    a = np.clip(a + (a - 0.5) * 0.08 * (1 - np.abs(a - 0.5) * 2), 0, 1)
    # warm push in mids: +R, -B slightly, weighted to midtones
    midw = (1 - np.abs(a - 0.5) * 2).clip(0, 1)
    a[..., 0] = np.clip(a[..., 0] + 0.020 * midw[..., 0], 0, 1)
    a[..., 2] = np.clip(a[..., 2] - 0.015 * midw[..., 2], 0, 1)
    # vibrance (raise low-sat pixels more)
    mx = a.max(-1, keepdims=True); mn = a.min(-1, keepdims=True)
    sat = (mx - mn)
    boost = (1 - sat) * 0.14
    mean = a.mean(-1, keepdims=True)
    a = np.clip(a + (a - mean) * boost, 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8))

def cover_fit(im, w, h):
    im = ImageOps.exif_transpose(im).convert("RGB")
    s = max(w / im.width, h / im.height)
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    x = (im.width - w) // 2; y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))

def placeholder(brief, village, layout="hero"):
    """Elegant muted mountain-tone gradient + the shot brief, so a missing photo
    still shows the layout and tells Isha exactly which photo to send."""
    tones = {
        "KALPA":   [(38, 52, 74), (74, 88, 104), (150, 140, 120)],
        "CHITKUL": [(44, 58, 70), (86, 104, 112), (126, 138, 130)],
        "TOSH":    [(40, 50, 66), (70, 92, 96), (138, 134, 110)],
    }.get(village, [(40, 48, 66), (80, 92, 104), (140, 134, 120)])
    top, mid, bot = tones
    g = np.zeros((H, W, 3), np.float32)
    ys = np.linspace(0, 1, H)[:, None]
    for i in range(3):
        col = np.where(ys < 0.5,
                       top[i] + (mid[i] - top[i]) * (ys / 0.5),
                       mid[i] + (bot[i] - mid[i]) * ((ys - 0.5) / 0.5))
        g[:, :, i] = col
    im = Image.fromarray(g.astype(np.uint8))
    # faint diagonal ridge bands for a mountain feel
    d = ImageDraw.Draw(im, "RGBA")
    for k, yy in enumerate([0.60, 0.72, 0.84]):
        pts = [(0, H * (yy + 0.04)), (W * 0.35, H * yy), (W * 0.65, H * (yy + 0.03)),
               (W, H * (yy - 0.02)), (W, H), (0, H)]
        d.polygon(pts, fill=(20, 26, 36, 60 + k * 20))
    im = im.filter(ImageFilter.GaussianBlur(2))
    d = ImageDraw.Draw(im, "RGBA")
    # Keep the placeholder caption LOW (y~0.74), out of the upper/mid text zones,
    # so the real slide copy stays clean to review. On real photos none of this draws.
    yb = H * 0.42 if layout == "end" else H * 0.735
    d.text((W / 2, yb), "—  ISHA'S PHOTO HERE  —", font=F["mont_b"](26),
           fill=(246, 196, 69, 235), anchor="mm")
    _wrapped(d, brief, F["mont"](27), int(W * 0.82), (W / 2, yb + 26), (255, 255, 255, 220),
             anchor="ma", leading=1.3, center=True, shadow=False)
    return im

def load_background(sp):
    p = os.path.join(PHOTOS, sp.get("photo", ""))
    if sp.get("photo") and os.path.exists(p):
        return natural_grade(cover_fit(Image.open(p), W, H)), True
    return placeholder(sp.get("photo_brief", ""), sp.get("village", ""), sp.get("layout", "hero")), False

# =========================================================================
# scrims so upper-third text always reads on any photo
# =========================================================================
def add_scrims(im, layout):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    arr = np.zeros((H, W, 4), np.float32)
    ys = np.linspace(0, 1, H)[:, None]
    # top scrim: strong at very top, gone by ~46%
    top = np.clip((0.46 - ys) / 0.46, 0, 1) ** 1.3
    top_strength = 165 if layout in ("feeling",) else 150
    # bottom scrim for the footer + end-card
    bot = np.clip((ys - 0.78) / 0.22, 0, 1) ** 1.4
    bot_strength = 150 if layout == "end" else 115
    a = top * top_strength + bot * bot_strength
    arr[..., 3] = np.clip(a, 0, 215) * np.ones((1, W))
    ov = Image.fromarray(arr.astype(np.uint8))
    return Image.alpha_composite(im.convert("RGBA"), ov)

# =========================================================================
# text helpers
# =========================================================================
def _measure(d, s, f):
    b = d.textbbox((0, 0), s, font=f); return b[2] - b[0], b[3] - b[1]

def fit_font(d, text, maker, max_w, start, lo=24):
    s = start
    while s > lo:
        if _measure(d, text, maker(s))[0] <= max_w:
            return maker(s)
        s -= 2
    return maker(lo)

def shadow_text(d, xy, s, f, fill, anchor="mm", sh=None, off=3, blur=True):
    # legibility halo is applied globally per slide; here just draw the glyph
    d.text(xy, s, font=f, fill=fill, anchor=anchor)

def _wrap_lines(d, text, f, max_w):
    words = text.split(); lines = []; cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if _measure(d, t, f)[0] <= max_w or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines

def _wrapped(d, text, f, max_w, xy, fill, anchor="ma", leading=1.28, center=True,
             shadow=True):
    x, y = xy
    lines = _wrap_lines(d, text, f, max_w)
    asc, desc = f.getmetrics(); lh = (asc + desc) * leading
    for i, ln in enumerate(lines):
        ly = y + i * lh
        a = "ma" if center else "la"
        d.text((x, ly), ln, font=f, fill=fill, anchor=a)
    return y + len(lines) * lh

def tracked_caps(d, text, f, xy, fill, tracking=8, anchor_center=True, shadow=True):
    text = text.upper()
    total = sum(_measure(d, ch, f)[0] + tracking for ch in text) - tracking
    x = xy[0] - total / 2 if anchor_center else xy[0]
    y = xy[1]
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill, anchor="lm")
        x += _measure(d, ch, f)[0] + tracking

# =========================================================================
# shared chrome: footer (handle + counter) + accent rule
# =========================================================================
def footer(d, idx, total, cover=False):
    y = H - 64
    tracked_caps(d, "@TRAVELWITHISHA", F["mont"](26), (MARGIN + 150, y), C["ivory"],
                 tracking=5, anchor_center=True)
    # counter right
    cnt = f"{idx:02d} / {total:02d}"
    d.text((W - MARGIN, y), cnt, font=F["mont"](26), fill=C["ivory"], anchor="rm")
    if cover:
        sf = F["mont_b"](28)
        tracked_caps(d, "SWIPE", sf, (W / 2 - 24, y), C["marigold"], tracking=6, anchor_center=True)
        sw = sum(_measure(d, ch, sf)[0] + 6 for ch in "SWIPE") - 6
        draw_arrow(d, W / 2 - 24 + sw / 2 + 18, y, 26, C["marigold"])

def accent_rule(d, cx, y, w=120, col="marigold"):
    d.line([(cx - w / 2, y), (cx + w / 2, y)], fill=C[col], width=5)

def draw_arrow(d, x, y, size, col, shadow=True):
    """A small right-pointing arrow drawn as vectors (fonts lack a clean glyph)."""
    r, g, b = col
    L = size  # shaft length
    hw = size * 0.34  # head half-width
    hl = size * 0.42  # head length
    th = max(3, round(size * 0.14))
    d.line([(x, y), (x + L, y)], fill=(r, g, b), width=th)
    d.line([(x + L, y), (x + L - hl, y - hw)], fill=(r, g, b), width=th)
    d.line([(x + L, y), (x + L - hl, y + hw)], fill=(r, g, b), width=th)
    return x + L + hl

def caveat_block(d, text, label, cx, y, maxw, size=66, rot_label=-5):
    """A handwritten note from Isha: small label chip + Caveat lines (marigold)."""
    if label:
        lab = label.upper()
        lf = F["mont_b"](24)
        tracked_caps(d, lab, lf, (cx, y), C["marigold"], tracking=4, anchor_center=True)
        y += 40
    cf = F["caveat"](size)
    yb = _wrapped(d, text, cf, maxw, (cx, y), C["chalk"], leading=0.92, center=True)
    return yb

# =========================================================================
# layouts
# =========================================================================
def composite_with_halo(im, txt):
    """Put a soft dark halo behind everything on the text layer, then the crisp text.
    Mirrors the house 'shadow 45% + outline' rule, and keeps text legible on any photo."""
    alpha = txt.split()[3]
    glow = alpha.filter(ImageFilter.GaussianBlur(7))
    black = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    black.putalpha(glow.point(lambda a: int(min(255, a * 1.6))))
    out = Image.alpha_composite(im.convert("RGBA"), black)   # halo pass 1
    out = Image.alpha_composite(out, black)                  # pass 2 -> denser core
    return Image.alpha_composite(out, txt)

def render_slide(sp, total):
    bg, has_photo = load_background(sp)
    im = add_scrims(bg, sp.get("layout", "hero"))
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(txt, "RGBA")
    layout = sp.get("layout", "hero")
    cx = W / 2

    if layout == "cover":
        # tiny series kicker, big KALPA, handwritten note
        _wrapped(d, sp["kicker"], F["serif_i"](44), COLW - 40, (cx, 150), C["ivory"],
                 leading=1.2, center=True)
        tf = fit_font(d, sp["title"], F["anton"], COLW, 300)
        shadow_text(d, (cx, 430), sp["title"], tf, C["chalk"], anchor="mm", off=5)
        accent_rule(d, cx, 548, 150)
        if sp.get("note"):
            # "start here" + a hand-drawn arrow (Caveat has no clean arrow glyph)
            note_txt = sp["note"].replace("→", "").strip()
            cf = F["caveat"](72)
            tw = _measure(d, note_txt, cf)[0]
            ax = 44  # arrow + gap allowance
            x0 = cx - (tw + ax) / 2
            d.text((x0, 610), note_txt, font=cf, fill=C["marigold"], anchor="lm")
            draw_arrow(d, x0 + tw + 20, 612, 30, C["marigold"])
        footer(d, sp["n"], total, cover=True)

    elif layout == "hero":
        tf = fit_font(d, sp["title"], F["anton"], COLW, 300)
        shadow_text(d, (cx, 300), sp["title"], tf, C["chalk"], anchor="mm", off=5)
        accent_rule(d, cx, 400, 130)
        if sp.get("line"):
            _wrapped(d, sp["line"], F["serif_i"](50), COLW - 20, (cx, 452), C["ivory"],
                     leading=1.24, center=True)
        footer(d, sp["n"], total)

    elif layout == "feeling":
        if sp.get("eyebrow"):
            tracked_caps(d, sp["eyebrow"], F["mont_b"](30), (cx, 150), C["marigold"], tracking=6)
        accent_rule(d, cx, 196, 90)
        _wrapped(d, sp["line"], F["serif"](60), COLW, (cx, 250), C["chalk"],
                 leading=1.26, center=True)
        if sp.get("note"):
            d.text((cx, H - 150), sp["note"], font=F["caveat"](60), fill=C["marigold"], anchor="mm")
        footer(d, sp["n"], total)

    elif layout == "tip":
        if sp.get("eyebrow"):
            tracked_caps(d, sp["eyebrow"], F["mont_b"](30), (cx, 150), C["ivory"], tracking=6)
        accent_rule(d, cx, 196, 90)
        caveat_block(d, sp["note"], sp.get("note_label", "isha's tip"), cx, 258, COLW, size=70)
        footer(d, sp["n"], total)

    elif layout == "end":
        if sp.get("note"):
            caveat_block(d, sp["note"], sp.get("note_label", "isha's tip"), cx, 170, COLW, size=58)
        cf = fit_font(d, sp["cta"], F["serif"], COLW, 86)
        _wrapped(d, sp["cta"], cf, COLW, (cx, H * 0.56), C["chalk"], leading=1.12, center=True)
        accent_rule(d, cx, H * 0.56 + 150, 150)
        if sp.get("cta_sub"):
            tracked_caps(d, sp["cta_sub"], F["mont_b"](28), (cx, H * 0.56 + 196), C["marigold"],
                         tracking=3)
        footer(d, sp["n"], total)

    return composite_with_halo(im, txt).convert("RGB"), has_photo

# =========================================================================
def main():
    spec = json.load(open(os.path.join(HERE, "slides.json")))
    slides = spec["slides"]; total = len(slides)
    thumbs = []; missing = []
    for sp in slides:
        im, has_photo = render_slide(sp, total)
        fn = os.path.join(OUT, f"slide_{sp['n']:02d}.png")
        im.save(fn)
        if not has_photo:
            missing.append(sp.get("photo"))
        t = im.copy(); t.thumbnail((360, 450), Image.LANCZOS); thumbs.append(t)
        print("wrote", os.path.relpath(fn, ROOT), "" if has_photo else "(placeholder)")
    # contact sheet 3x3
    pad = 18; tw, th = 360, 450
    sheet = Image.new("RGB", (3 * tw + 4 * pad, 3 * th + 4 * pad), (12, 12, 12))
    for i, t in enumerate(thumbs):
        r, c = divmod(i, 3)
        sheet.paste(t, (pad + c * (tw + pad), pad + r * (th + pad)))
    sheet.save(os.path.join(OUT, "contact.png"))
    print("wrote", os.path.relpath(os.path.join(OUT, "contact.png"), ROOT))
    if missing:
        print(f"\n{len(missing)} slide(s) still need Isha's photo:", ", ".join(missing))

if __name__ == "__main__":
    main()
