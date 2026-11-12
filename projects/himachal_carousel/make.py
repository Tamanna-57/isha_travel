#!/usr/bin/env python3
"""
Himachal 3-villages carousel (Kalpa / Chitkul / Tosh) for @travelwithisha.

Design follows the anton.cltx reference carousel the client sent:
  - full-bleed photo, natural grade, photo stays dominant
  - minimal text in the TOP band only (~top 22%), centred
  - ONE serif family (Playfair Display): upright for titles/body, italic for kickers/subtitles
  - two colours only: white OR near-black, chosen per slide for contrast with the sky
  - no accent colour, no handwriting, no handle bar / counter / swipe chrome
    (only slide 9 carries a small centred handle, like the reference end card)

    python projects/himachal_carousel/make.py   # -> out/slide_01.png .. 09 + out/contact.png

Deps: Pillow, numpy.
"""
import json, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FONTS = os.path.join(ROOT, "fonts")
PHOTOS = os.path.join(HERE, "photos")
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1350
INK = (26, 24, 22)          # near-black text
CHALK = (255, 255, 255)     # white text

def font(fname, size):
    return ImageFont.truetype(os.path.join(FONTS, fname), size)

def F(role, size):
    return font({"reg": "PlayfairDisplay-Regular.ttf",
                 "it":  "PlayfairDisplay-Italic.ttf",
                 "med": "PlayfairDisplay-Medium.ttf" if os.path.exists(os.path.join(FONTS, "PlayfairDisplay-Medium.ttf"))
                        else "PlayfairDisplay-Regular.ttf"}[role], size)

# -------------------------------------------------------------------------
# photo: natural grade + 4:5 cover-fit
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
# contrast: sample the band behind the text, pick white or dark + a whisper scrim
# -------------------------------------------------------------------------
def top_band_luma(im, y0=90, y1=470):
    a = np.asarray(im.crop((0, y0, W, y1)).convert("L")).astype(np.float32)
    return float(a.mean()), float(np.percentile(a, 70))

def apply_scrim(im, mode):
    """A very light top gradient so text reads without hiding the photo.
    mode 'dark'  -> faint dark veil under white text
    mode 'light' -> faint light veil under near-black text
    Both fade out by ~42% height."""
    ys = np.linspace(0, 1, H)[:, None]
    fall = np.clip((0.44 - ys) / 0.44, 0, 1) ** 1.35
    ov = np.zeros((H, W, 4), np.float32)
    if mode == "dark":
        ov[..., 3] = (fall * 115) * np.ones((1, W))
    else:
        ov[..., :3] = 255.0
        ov[..., 3] = (fall * 95) * np.ones((1, W))
    return Image.alpha_composite(im.convert("RGBA"), Image.fromarray(ov.astype(np.uint8)))

# -------------------------------------------------------------------------
# text
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

def fit_title(d, text, max_w, start, lo, max_lines, role="reg"):
    s = start
    while s > lo:
        f = F(role, s)
        lines = wrap(d, text, f, max_w)
        if len(lines) <= max_lines and max((measure(d, ln, f)[0] for ln in lines), default=0) <= max_w:
            return f, lines
        s -= 2
    f = F(role, lo)
    return f, wrap(d, text, f, max_w)

def draw_center(d, lines, f, cx, y, fill, leading, soft):
    asc, desc = f.getmetrics(); lh = (asc + desc) * leading
    for i, ln in enumerate(lines):
        yy = y + i * lh
        if soft:
            d.text((cx, yy), ln, font=f, fill=soft, anchor="ma")  # handled on shadow layer
        d.text((cx, yy), ln, font=f, fill=fill, anchor="ma")
    return y + len(lines) * lh

def small_caps_spacing(d, text, f, cx, y, fill, tracking):
    text = text.upper()
    total = sum(measure(d, ch, f)[0] + tracking for ch in text) - tracking
    x = cx - total / 2
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill, anchor="la")
        x += measure(d, ch, f)[0] + tracking

def arrow(d, x, y, size, col):
    th = max(3, round(size * 0.12))
    d.line([(x, y), (x + size, y)], fill=col, width=th)
    d.line([(x + size, y), (x + size - size * 0.4, y - size * 0.32)], fill=col, width=th)
    d.line([(x + size, y), (x + size - size * 0.4, y + size * 0.32)], fill=col, width=th)

# -------------------------------------------------------------------------
def render_slide(sp):
    photo, ok = load_photo(sp["photo"])
    mean, p70 = top_band_luma(photo)
    dark_text = p70 >= 165          # bright sky -> near-black text (elegant, reference-style)
    fill = INK if dark_text else CHALK
    im = apply_scrim(photo, "light" if dark_text else "dark")

    # text on its own layer, with a faint matching halo for safety on busy photos
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer, "RGBA")
    cx = W / 2
    maxw = int(W * 0.84)
    y = 150

    if sp.get("kicker"):
        kf = F("it", 40)
        d.text((cx, y), sp["kicker"], font=kf, fill=fill, anchor="ma")
        y += kf.getmetrics()[0] + kf.getmetrics()[1] + 18

    if sp.get("title"):
        role = "it" if sp.get("title_italic") else "reg"
        # village names get bigger presence; long lines shrink to fit <=3 lines
        short = len(sp["title"]) <= 14
        tf, tlines = fit_title(d, sp["title"], maxw,
                               start=104 if short else 62, lo=44,
                               max_lines=1 if short else 3, role=role)
        yb = draw_center(d, tlines, tf, cx, y, fill, 1.08, None)
        # cover swipe arrow sits inline after a one-line title is uncommon; put it with body
        y = yb + 24

    if sp.get("body"):
        role = "it" if sp.get("body_italic") else "reg"
        bf = F(role, 37)
        blines = wrap(d, sp["body"], bf, int(W * 0.80))
        yb = draw_center(d, blines, bf, cx, y, fill, 1.34, None)
        if sp.get("swipe"):
            # a small arrow centred under the subtitle
            arrow(d, cx - 16, yb + 30, 34, fill)
        y = yb

    if sp.get("handle"):
        # the end-card handle sits at the bottom; pick its colour from the bottom band
        bmean = float(np.asarray(photo.crop((0, H - 150, W, H - 40)).convert("L")).mean())
        hfill = INK if bmean >= 150 else CHALK
        hf = F("it", 32)
        hx, hy = cx, H - 86
        # its own soft shadow so it reads regardless of the global halo colour
        hs = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(hs).text((hx, hy), sp.get("handle_text", "@travelwithisha"),
                                font=hf, fill=(0, 0, 0, 160) if hfill == CHALK else (255, 255, 255, 160),
                                anchor="ma")
        hs = hs.filter(ImageFilter.GaussianBlur(4))
        layer.alpha_composite(hs)
        d.text((hx, hy), sp.get("handle_text", "@travelwithisha"), font=hf, fill=hfill, anchor="ma")

    # subtle halo: blur the text alpha, tint opposite of text, composite under text
    alpha = layer.split()[3]
    glow = alpha.filter(ImageFilter.GaussianBlur(5))
    halo_col = (255, 255, 255, 255) if dark_text else (0, 0, 0, 255)
    halo = Image.new("RGBA", (W, H), halo_col)
    halo.putalpha(glow.point(lambda a: int(a * (0.45 if dark_text else 0.62))))
    out = Image.alpha_composite(im, halo)
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
