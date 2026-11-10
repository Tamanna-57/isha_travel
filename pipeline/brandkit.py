"""Render the visual brand boards in ../brand from the same code that renders the reels.
Usage: python pipeline/brandkit.py"""
import json, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
import isha
from isha import ROOT, FONTS, W, H

BRAND = ROOT / "brand"
HEX = {"ink": "#111111", "chalk": "#FFFFFF", "ivory": "#FFF6E5", "marigold": "#F6C445", "sindoor": "#D7263D",
       "saffron": "#F39C2B", "paper": "#F7F3EA", "grey": "#9A9A9A"}
BG = "#141414"

def F(name, size):
    p = FONTS / name
    return ImageFont.truetype(str(p if p.exists() else "C:/Windows/Fonts/segoeui.ttf"), size)

# backgrounds that read like footage (sky / dusk / greens / warm room), so text contrast is judged honestly
BACKS = {  # top -> horizon -> bottom colours, horizon position
    "sky":   ((47, 111, 196), (176, 206, 236), (150, 118, 84), 0.62),
    "dusk":  ((31, 42, 74), (232, 150, 90), (58, 42, 32), 0.58),
    "green": ((120, 170, 220), (222, 232, 239), (70, 112, 48), 0.55),
    "room":  ((201, 138, 74), (230, 176, 113), (40, 30, 26), 0.66),
}

def back_png(name, tmp):
    import numpy as np
    out = tmp / f"bg_{name}.png"
    if out.exists():
        return out
    top, mid, bot, hz = BACKS[name]
    y = np.linspace(0, 1, H)[:, None]
    a, b, c = (np.array(v, float) for v in (top, mid, bot))
    col = np.where(y < hz, a + (b - a) * (y / hz), b + (c - b) * (np.clip(y - hz, 0, None) / (1 - hz)) ** 0.6)
    img = np.repeat(col[:, None, :], W, axis=1).reshape(H, W, 3)
    xx = np.linspace(-1, 1, W)[None, :]; yy = np.linspace(-1, 1, H)[:, None]
    img *= (1 - 0.22 * (xx ** 2 + yy ** 2))[..., None]                       # vignette
    img += np.random.default_rng(1).normal(0, 3, img.shape)                  # fine grain
    Image.fromarray(img.clip(0, 255).astype("uint8")).save(out)
    return out

def render_phone(ass_text, back, t, tmp, name):
    ass = tmp / f"{name}.ass"; ass.write_text(ass_text, encoding="utf-8")
    out = tmp / f"{name}.png"
    bg = back_png(back, tmp)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-t", "3", "-i", bg.name,
                    "-ss", f"{t:.2f}", "-frames:v", "1", "-vf", f"format=yuv420p,ass={ass.name}:fontsdir=fonts", out.name],
                   cwd=tmp, check=True)
    return Image.open(out).convert("RGB")

def board(phones, title, out, cols=None, label_h=110, scale=0.5):
    cols = cols or len(phones)
    pw, ph = int(W * scale), int(H * scale)
    rows = (len(phones) + cols - 1) // cols
    pad, head = 40, 150
    img = Image.new("RGB", (pad + cols * (pw + pad), head + rows * (ph + label_h + pad)), BG)
    d = ImageDraw.Draw(img)
    d.text((pad, 40), title, font=F("Anton-Regular.ttf", 64), fill=HEX["chalk"])
    for i, (im, lab, sub) in enumerate(phones):
        x = pad + (i % cols) * (pw + pad); y = head + (i // cols) * (ph + label_h + pad)
        img.paste(im.resize((pw, ph), Image.LANCZOS), (x, y))
        d.rounded_rectangle([x - 2, y - 2, x + pw + 2, y + ph + 2], radius=14, outline="#333333", width=3)
        d.text((x, y + ph + 14), lab, font=F("Poppins-SemiBold.ttf", 30), fill=HEX["marigold"])
        d.text((x, y + ph + 54), sub, font=F("Poppins-Regular.ttf", 22), fill="#BBBBBB")
    img.save(out)
    print(out)

def W_(text, s, e, emph=False):
    return {"text": text, "start": s, "end": e, **({"emph": True} if emph else {})}

def seq(words, t0=0.1, step=0.3, emph=()):
    return [W_(w, t0 + k * step, t0 + (k + 1) * step, w in emph) for k, w in enumerate(words)]

def caption_board(tmp):
    demos = [
        ("serif", "sky", 1.1, seq(["it", "is", "only", "Pakistan-Occupied", "Jammu", "and"], step=0.18, emph=("Pakistan-Occupied", "Jammu")),
         "3.1 Serif Two-Tier", "Format A default · y 1300"),
        ("sans", "room", 0.8, seq(["Itna", "Expensive", "Tha"], emph=("Expensive",)),
         "3.2 Bold Sans Two-Tier", "Format B storytime · left block"),
        ("karaoke", "room", 0.75, seq(["Trip", "pe", "jaane", "se"]),
         "3.3 Karaoke Reveal", "emotional storytime · y 1340"),
        ("caps", "dusk", 0.8, seq(["mai", "hu", "abhi", "aaj"]),
         "3.5 Spaced Caps", "light vlog / day-in-life · y 1400"),
        ("top", "sky", 1.5, seq(["I", "booked", "my", "flights", "to", "Bangkok"], step=0.2, emph=("booked", "flights")),
         "3.4 Top Sans + Italic", "brand deals / explainers · y 330"),
        ("typewriter", "dusk", 0.95, seq(["we", "started", "sailing", "from"], step=0.25),
         "Typewriter", "journey recap (format C) · y 1380"),
    ]
    phones = []
    for style, back, t, words, lab, sub in demos:
        evs = isha.caption_events(words, style)
        phones.append((render_phone(isha.ass_header() + "\n".join(evs) + "\n", back, t, tmp, f"cap_{style}"), lab, sub))
    board(phones, "CAPTION STYLES  —  real pipeline renders (1080x1920)", BRAND / "03_caption_styles.png", cols=3)

def titles_board(tmp):
    demos = [
        ([{"type": "chapter", "text": "Japan", "script": "mein", "start": 0, "end": 5}], "sky",
         seq(["Mai", "hu", "abhi", "aaj"], t0=0.2, emph=("aaj",)), "Chapter title", "Anton sindoor + Allura script"),
        ([{"type": "landmark", "text": "Chenab Rail Bridge", "sub": "District Reasi, J&K", "start": 0, "end": 5},
          {"type": "fact", "text": "1178 ft above Chenab River", "start": 0, "end": 5}], "green", [],
         "Landmark + fact", "Anton marigold (sheared) · Playfair italic"),
        ([{"type": "place", "text": "Kyrgyzstan", "start": 0, "end": 5}], "green", [],
         "Place name", "Cinzel SemiBold +8 tracking, centre"),
        ([{"type": "pill", "text": "This *country* is 'Sukoon'", "start": 0, "end": 5}], "sky",
         seq(["The", "world"], t0=0.2, emph=("world",)), "Hook pill", "Playfair on ink box · sindoor keyword"),
        ([{"type": "label", "text": "My *scuba* instructors", "start": 0, "end": 5}], "sky",
         seq(["kuch", "nahi", "hone", "diya"], t0=0.2, emph=("diya",)), "Person label", "Playfair SemiBold, soft glow, no box"),
        ([{"type": "hook", "text": "One wrong move and you'll meet the creator", "start": 0, "end": 5}], "green", [],
         "Hook line (POV)", "Poppins Bold top · format D"),
        ([{"type": "marker", "text": "PoK  Pakistan\nTibet.  China", "start": 0, "end": 5, "y": 300},
          {"type": "marker", "text": "Indo-China", "start": 0, "end": 5, "y": 560, "color": "sindoor", "strike": True, "size": 80, "rotate": 2}],
         "sky", seq(["border", "is", "actually"], t0=0.2, emph=("border",)), "Marker notes", "Caveat write-on · sindoor = correction"),
    ]
    phones = []
    for i, (titles, back, words, lab, sub) in enumerate(demos):
        evs = (isha.caption_events(words, "serif") if words else []) + isha.title_events(titles)
        txt = isha.ass_header() + "\n".join(evs) + "\n"
        txt = txt.replace("\\\\N", "\\N")
        phones.append((render_phone(txt, back, 1.2, tmp, f"title_{i}"), lab, sub))
    board(phones, "TITLES & ON-SCREEN TEXT", BRAND / "04_titles.png", cols=3)

def type_specimen():
    rows = [
        ("Playfair Display", "PlayfairDisplay-SemiBold.ttf", "Caption serif (key word) · SemiBold 600", "Pakistan-Occupied Kashmir"),
        ("Playfair Display Italic", "PlayfairDisplay-Italic.ttf", "Fact line · Italic 400", "1178 ft above Chenab River"),
        ("Instrument Serif Italic", "InstrumentSerif-Italic.ttf", "Highlight word in top captions", "booked my flights"),
        ("Poppins", "Poppins-ExtraBold.ttf", "Sans key word · ExtraBold 800", "Itna Expensive Tha"),
        ("Poppins", "Poppins-SemiBold.ttf", "Karaoke / storytime · SemiBold 600", "Trip pe jaane se pehle"),
        ("Poppins", "Poppins-Light.ttf", "Sans filler words · Light 300", "itna · tha · ki"),
        ("Montserrat", "Montserrat-Bold.ttf", "Spaced caps captions · Bold 700, +6", "M A I   H U   A B H I   A A J"),
        ("Anton", "Anton-Regular.ttf", "Chapter / landmark titles", "JAPAN · CHENAB RAIL BRIDGE"),
        ("Allura", "Allura-Regular.ttf", "Script accent over titles", "mein · the · diaries"),
        ("Cinzel", "Cinzel-SemiBold.ttf", "Place names (format C) · SemiBold, +8", "K Y R G Y Z S T A N"),
        ("Caveat", "Caveat-Bold.ttf", "Handwritten marker notes · Bold", "PoK  Pakistan  Tibet. China"),
        ("Courier Prime", "CourierPrime-Regular.ttf", "Typewriter journey captions", "we started sailing"),
    ]
    Wd, rh, pad = 2000, 150, 60
    img = Image.new("RGB", (Wd, 170 + rh * len(rows) + pad), BG)
    d = ImageDraw.Draw(img)
    d.text((pad, 50), "TYPE SYSTEM  —  9 families, all Google Fonts (OFL, free for commercial use)", font=F("Anton-Regular.ttf", 56), fill=HEX["chalk"])
    for i, (fam, file, role, sample) in enumerate(rows):
        y = 170 + i * rh
        d.line([pad, y - 10, Wd - pad, y - 10], fill="#2a2a2a", width=2)
        d.text((pad, y + 10), fam, font=F("Poppins-SemiBold.ttf", 30), fill=HEX["marigold"])
        d.text((pad, y + 52), role, font=F("Poppins-Regular.ttf", 22), fill="#BBBBBB")
        d.text((pad, y + 84), file, font=F("CourierPrime-Regular.ttf", 20), fill="#777777")
        d.text((640, y + 18), sample, font=F(file, 84), fill=HEX["chalk"])
    img.save(BRAND / "01_type_specimen.png"); print(BRAND / "01_type_specimen.png")

def palette():
    sw = [("marigold", "primary accent", "caption filler words, highlight word, landmark titles"),
          ("sindoor", "secondary accent", "chapter titles, hook keyword, corrections/cross-outs"),
          ("chalk", "text", "caption key words, place names"),
          ("ivory", "soft text", "sans filler words"),
          ("saffron", "cinematic accent", "format C captions (warm gold)"),
          ("ink", "base", "pills, letterbox bars, shadows"),
          ("paper", "card bg", "map / screenshot cards"),
          ("grey", "pending", "karaoke words not yet spoken")]
    cw, ch, pad = 470, 380, 40
    img = Image.new("RGB", (pad + 4 * (cw + pad), 150 + 2 * (ch + pad)), BG)
    d = ImageDraw.Draw(img)
    d.text((pad, 40), "COLOUR TOKENS", font=F("Anton-Regular.ttf", 64), fill=HEX["chalk"])
    for i, (k, role, use) in enumerate(sw):
        x = pad + (i % 4) * (cw + pad); y = 150 + (i // 4) * (ch + pad)
        d.rounded_rectangle([x, y, x + cw, y + 220], radius=18, fill=HEX[k], outline="#333333", width=2)
        d.text((x, y + 236), f"{k}  {HEX[k]}", font=F("Poppins-SemiBold.ttf", 32), fill=HEX["chalk"])
        d.text((x, y + 282), role, font=F("Poppins-Medium.ttf", 24), fill=HEX["marigold"])
        d.text((x, y + 316), use, font=F("Poppins-Regular.ttf", 20), fill="#BBBBBB")
    img.save(BRAND / "02_palette.png"); print(BRAND / "02_palette.png")

def safe_zones():
    """Transparent 1080x1920 overlay (drop on top of the timeline in CapCut/Premiere) + annotated board."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    red = (215, 38, 61, 90); gold = (246, 196, 69, 60); line = (255, 255, 255, 160)
    d.rectangle([0, 1536, W, H], fill=red)            # bottom UI (caption, audio, username)
    d.rectangle([950, 700, W, 1536], fill=red)        # right action rail
    d.rectangle([0, 0, W, 150], fill=red)             # top UI
    d.rectangle([110, 230, 970, 440], fill=gold)      # title band
    d.rectangle([110, 1150, 970, 1460], fill=gold)    # caption band
    for y in (300, 330, 960, 1300, 1400):
        d.line([110, y, 970, y], fill=line, width=2)
    f = F("Poppins-SemiBold.ttf", 30)
    d.text((130, 236), "TITLE BAND  y 230–440", font=f, fill="white")
    d.text((130, 1156), "CAPTION BAND  y 1150–1460 (default 1300)", font=f, fill="white")
    d.text((130, 1560), "NO TEXT — Instagram caption / audio / username", font=f, fill="white")
    d.text((960, 710), "NO\nTEXT\nicons", font=F("Poppins-SemiBold.ttf", 26), fill="white")
    d.text((130, 40), "NO TEXT — top bar", font=f, fill="white")
    d.text((130, 930), "place name  y 960", font=F("Poppins-Regular.ttf", 26), fill="white")
    ov.save(BRAND / "safe_zone_overlay_1080x1920.png"); print(BRAND / "safe_zone_overlay_1080x1920.png")

def grade_board():
    """Colour ramps (skin, sky, foliage, neutral) through each look, so the effect of each LUT is visible."""
    import numpy as np
    ramps = [("skin", [(60, 38, 28), (150, 100, 78), (224, 178, 150)]), ("sky", [(20, 50, 110), (70, 130, 210), (190, 220, 245)]),
             ("foliage", [(20, 40, 15), (70, 120, 40), (170, 210, 120)]), ("neutral", [(0, 0, 0), (128, 128, 128), (255, 255, 255)])]
    rw, rh = 900, 70
    strip = np.zeros((rh * len(ramps), rw, 3), np.uint8)
    for i, (_, (a, b, c)) in enumerate(ramps):
        for x in range(rw):
            t = x / (rw - 1); p, q, u = (a, b, t * 2) if t < 0.5 else (b, c, t * 2 - 1)
            strip[i * rh:(i + 1) * rh, x] = [p[k] + (q[k] - p[k]) * u for k in range(3)]
    tmp = Path(tempfile.mkdtemp()); src = tmp / "ramps.png"; Image.fromarray(strip).save(src)
    looks = ["none", "natural", "golden", "indoor", "film"]
    pad, lab = 40, 300
    img = Image.new("RGB", (lab + rw + pad * 2, 150 + len(looks) * (strip.shape[0] + 60)), BG)
    d = ImageDraw.Draw(img)
    d.text((pad, 40), "GRADE LOOKS  (luts/*.cube)", font=F("Anton-Regular.ttf", 64), fill=HEX["chalk"])
    for i, lk in enumerate(looks):
        out = tmp / f"{lk}.png"
        vf = (isha.GRADES[lk].replace(",noise=alls=5:allf=t", "") + "," if isha.GRADES[lk] else "") + "format=rgb24"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf", vf, str(out)], check=True)
        y = 150 + i * (strip.shape[0] + 60)
        img.paste(Image.open(out).convert("RGB"), (lab + pad, y))
        d.text((pad, y + 20), "original" if lk == "none" else f"Isha_{lk.title()}", font=F("Poppins-SemiBold.ttf", 34), fill=HEX["marigold"])
        d.text((pad, y + 70), "skin / sky / foliage / grey", font=F("Poppins-Regular.ttf", 20), fill="#999999")
    img.save(BRAND / "05_grades.png"); print(BRAND / "05_grades.png")

if __name__ == "__main__":
    BRAND.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        (tmp / "fonts").mkdir()
        for f in FONTS.glob("*.ttf"):
            (tmp / "fonts" / f.name).write_bytes(f.read_bytes())
        type_specimen(); palette(); caption_board(tmp); titles_board(tmp); safe_zones(); grade_board()
