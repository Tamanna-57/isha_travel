#!/usr/bin/env python3
"""
Himachal 3-villages carousel (Kalpa / Chitkul / Tosh) for @travelwithisha.

v2 design (swarikaandaditya reference):
  - full-bleed photo, natural grade, photo stays dominant
  - bold Poppins display type, text anchored TOP-LEFT (minimal, upper band)
  - a per-photo ACCENT colour pulled from the image, on the kicker + title,
    so the type complements each picture; clean body text beneath
  - light/dark variants chosen from the band behind the text for contrast
  - no handle bar / counter / swipe chrome (only slide 9 carries a small handle)

    python projects/himachal_carousel/make.py   # -> out/slide_01.png .. 09 + out/contact.png

Deps: Pillow, numpy.
"""
import json, os, colorsys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(ROOT, "fonts")
PHOTOS = os.path.join(HERE, "photos")
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1350
MARGIN = 74

def font(fname, size):
    return ImageFont.truetype(os.path.join(FONTS, fname), size)

def F(role, size):
    return font({"xb": "Poppins-ExtraBold.ttf", "b": "Poppins-Bold.ttf",
                 "sb": "Poppins-SemiBold.ttf", "med": "Poppins-Medium.ttf"}[role], size)

# -------------------------------------------------------------------------
def natural_grade(im):
    a = np.asarray(im).astype(np.float32) / 255.0
    a = 0.031 + a * 0.945
    a = np.clip(a + (a - 0.5) * 0.07 * (1 - np.abs(a - 0.5) * 2), 0, 1)
    midw = (1 - np.abs(a - 0.5) * 2).clip(0, 1)
    a[..., 0] = np.clip(a[..., 0] + 0.018 * midw[..., 0], 0, 1)
    a[..., 2] = np.clip(a[..., 2] - 0.013 * midw[..., 2], 0, 1)
    mx = a.max(-1, keepdims=True); mn = a.min(-1, keepdims=True)
    mean = a.mean(-1, keepdims=True)
    a = np.clip(a + (a - mean) * (1 - (mx - mn)) * 0.12, 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8))

def cover_fit(im, w, h):
    im = ImageOps.exif_transpose(im).convert("RGB")
    s = max(w / im.width, h / im.height)
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    x = (im.width - w) // 2; y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))

def load_photo(name):
    p = os.path.join(PHOTOS, name)
    if not os.path.exists(p):
        return Image.new("RGB", (W, H), (40, 44, 52)), False
    return natural_grade(cover_fit(Image.open(p), W, H)), True

# -------------------------------------------------------------------------
# accent colour pulled from the photo's vivid pixels (circular-mean hue)
# -------------------------------------------------------------------------
def accent_hue(im, y0=70, y1=470):
    """Pick a warm, on-brand accent (Isha's marigold family) that complements the
    band behind the text. Cool / blue bands -> gold; warm golden bands -> terracotta
    so the type still contrasts and reads. Stays in a cohesive warm range (no pinks)."""
    hsv = np.asarray(im.crop((0, y0, W, y1)).resize((96, 72)).convert("HSV")).astype(np.float32)
    Hh = hsv[..., 0] * 360 / 255.0
    Ss = hsv[..., 1] / 255.0
    Vv = hsv[..., 2] / 255.0
    w = (Ss ** 1.5) * ((Vv > 0.15) & (Vv < 0.98))
    if w.sum() < 20:
        return 42.0, 0.6
    ang = np.deg2rad(Hh)
    mh = np.arctan2((np.sin(ang) * w).sum(), (np.cos(ang) * w).sum())
    bhue = (np.degrees(mh)) % 360
    bsat = float(np.average(Ss, weights=w + 1e-6))
    warm_band = bsat > 0.14 and (bhue <= 60 or bhue >= 330)   # golden / sunset sky
    return (15.0 if warm_band else 42.0), bsat

def band_luma(im, y0=70, y1=470):
    a = np.asarray(im.crop((0, y0, W, y1)).convert("L")).astype(np.float32)
    return float(np.percentile(a, 70))

def hsv(h, s, v):
    r, g, b = colorsys.hsv_to_rgb((h % 360) / 360.0, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))

# -------------------------------------------------------------------------
def measure(d, s, f):
    b = d.textbbox((0, 0), s, font=f); return b[2] - b[0], b[3] - b[1]

def wrap(d, text, f, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if measure(d, t, f)[0] <= max_w or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines

def fit(d, text, role, start, lo, max_w, max_lines):
    s = start
    while s > lo:
        f = F(role, s)
        lines = wrap(d, text, f, max_w)
        if len(lines) <= max_lines and max((measure(d, ln, f)[0] for ln in lines), default=0) <= max_w:
            return f, lines
        s -= 2
    f = F(role, lo)
    return f, wrap(d, text, f, max_w)

def draw_left(d, lines, f, x, y, fill, leading):
    asc, desc = f.getmetrics(); lh = (asc + desc) * leading
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=f, fill=fill, anchor="la")
    return y + len(lines) * lh

def tracked(d, text, f, x, y, fill, tr):
    text = text.upper()
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill, anchor="la")
        x += measure(d, ch, f)[0] + tr
    return x

def arrow(d, x, y, size, col):
    th = max(4, round(size * 0.13))
    d.line([(x, y), (x + size, y)], fill=col, width=th)
    d.line([(x + size, y), (x + size - size * 0.4, y - size * 0.32)], fill=col, width=th)
    d.line([(x + size, y), (x + size - size * 0.4, y + size * 0.32)], fill=col, width=th)

# -------------------------------------------------------------------------
def render_slide(sp):
    photo, ok = load_photo(sp["photo"])
    hue, strength = accent_hue(photo)
    p70 = band_luma(photo)
    bright = p70 >= 162            # bright band -> dark text + deep accent

    if bright:
        accent = hsv(hue, min(0.9, 0.55 + strength * 0.4), 0.52)
        body_col = (34, 28, 22)
        shadow = (255, 255, 255, 150)
    else:
        accent = hsv(hue, min(0.78, 0.5 + strength * 0.4), 0.98)
        body_col = (255, 247, 236)
        shadow = (0, 0, 0, 165)

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer, "RGBA")
    x = MARGIN
    y = 118
    maxw = W - MARGIN - 60

    if sp.get("kicker"):
        kf = F("sb", 30)
        tracked(d, sp["kicker"], kf, x, y, accent, 3)
        y += kf.getmetrics()[0] + kf.getmetrics()[1] + 16

    if sp.get("title"):
        short = len(sp["title"]) <= 14
        tf, tlines = fit(d, sp["title"], "xb",
                         start=132 if short else 72, lo=48,
                         max_w=maxw, max_lines=1 if short else 3)
        y = draw_left(d, tlines, tf, x, y, accent, 1.02) + 22

    if sp.get("body"):
        bf = F("med", 37)
        blines = wrap(d, sp["body"], bf, int(W * 0.72))
        yb = draw_left(d, blines, bf, x, y, body_col, 1.3)
        if sp.get("swipe"):
            arrow(d, x + 2, yb + 34, 40, accent)
        y = yb

    if sp.get("handle"):
        bmean = float(np.asarray(photo.crop((0, H - 150, W, H - 40)).convert("L")).mean())
        hfill = (34, 28, 22) if bmean >= 150 else (255, 247, 236)
        hf = F("sb", 28)
        tracked(d, sp.get("handle_text", "@travelwithisha"), hf, MARGIN, H - 92, hfill, 2)

    # soft shadow for legibility (keeps the colour readable on any photo)
    alpha = layer.split()[3]
    glow = alpha.filter(ImageFilter.GaussianBlur(5))
    sh = Image.new("RGBA", (W, H), shadow[:3] + (255,))
    sh.putalpha(glow.point(lambda a: int(a * (shadow[3] / 255.0))))
    out = Image.alpha_composite(photo.convert("RGBA"), sh)
    out = Image.alpha_composite(out, layer)
    return out.convert("RGB"), ok

# -------------------------------------------------------------------------
def main():
    spec = json.load(open(os.path.join(HERE, "slides.json")))
    thumbs = []
    for sp in spec["slides"]:
        im, ok = render_slide(sp)
        fn = os.path.join(OUT, f"slide_{sp['n']:02d}.png")
        im.save(fn)
        print("wrote", os.path.relpath(fn, ROOT), "" if ok else "(photo missing)")
        t = im.copy(); t.thumbnail((360, 450), Image.LANCZOS); thumbs.append(t)
    pad, tw, th = 18, 360, 450
    sheet = Image.new("RGB", (3 * tw + 4 * pad, 3 * th + 4 * pad), (14, 14, 14))
    for i, t in enumerate(thumbs):
        r, c = divmod(i, 3)
        sheet.paste(t, (pad + c * (tw + pad), pad + r * (th + pad)))
    sheet.save(os.path.join(OUT, "contact.png"))
    print("wrote", os.path.relpath(os.path.join(OUT, "contact.png"), ROOT))

if __name__ == "__main__":
    main()
