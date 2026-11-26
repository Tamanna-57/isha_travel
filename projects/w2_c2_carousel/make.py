"""W2-C2 · Wed 2 Dec · @lostandfree x @travelwithisha · Carousel 8 slides 1080x1350 · "Corbett, unfiltered" 2/3.
Design: Lost & Free editorial (gold serif headlines, white body); Anton only on the cover (ties the series together).
Only Isha's own photos. Text kept inside the 4:5 safe area (60 px margins, nothing in the bottom 90 px but the footer).
Usage: python make.py  -> out/W2-C2_slide_1..8.png + out/W2-C2_carousel.pdf"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageFilter
import numpy as np
P = Path(__file__).resolve().parent; ROOT = P.parent.parent; F = ROOT / "fonts"
L1, T1 = ROOT / "projects/w1_l1_details_out/broll/isha", ROOT / "projects/w1_t1_7years/broll/isha"
W, H, M = 1080, 1350, 72
GOLD, MARI, WHITE = (222, 184, 98), (246, 196, 69), (255, 255, 255)
f = lambda n, s: ImageFont.truetype(str(F / n), s)
SERIF, BODY, BODYB, ANTON = "PlayfairDisplay-Bold.ttf", "Poppins-Medium.ttf", "Poppins-SemiBold.ttf", "Anton-Regular.ttf"
ARROW = "InterDisplay-SemiBold.ttf"

# (photo, focus x, focus y, lift(gamma, sat) or None, text position, kicker, headline, body lines, note)
SLIDES = [
    (L1 / "tiger_lookup.jpg", 0.5, 0.35, None, "cover", None, None, None, None),
    (L1 / "tiger_walk.jpg", 0.62, 0.40, None, "bottom", "THE GOOD NEWS", "3,682 tigers.",
     ["India counted 3,682 wild tigers in 2022,", "about three-quarters of the world's.", "That's real progress."], "Source: NTCA, Status of Tigers 2022"),
    (L1 / "misty_tiger.jpg", 0.5, 0.62, None, "top", "BUT", "A tiger count is one number.", ["A forest is thousands of them."], None),
    (T1 / "kite.jpg", 0.5, 0.62, None, "top", "WHAT A HEALTHY FOREST NEEDS", "More than tigers.",
     ["•  Prey: deer, gaur, langur", "•  Grasslands and water", "•  Birds and small predators", "•  Corridors to other forests"], None),
    (L1 / "jeeps_tiger.jpg", 0.5, 0.70, None, "top", "THE PRESSURES YOU DON'T SEE", "It's not just poaching.",
     ["•  Shrinking corridors", "•  Invasive weeds like lantana", "•  Roads through the forest", "•  Jeeps crowding one sighting"], None),
    (L1 / "jackal.jpg", 0.56, 0.40, None, "bottom", "THE UNCOMFORTABLE PART", "More tigers, same forest.",
     ["can mean more conflict with the", "villages at its edge."], None),
    (L1 / "kingfisher_moss.jpg", 0.69, 0.62, (1.45, 1.6), "top", "WHAT WE DO", "We watch the whole forest.",
     ["•  Small groups: only 4 seats a jeep", "•  We never chase or crowd a sighting.", "    We wait.", "•  Every sighting counts,", "    from kingfisher to dhole"], None),
    (T1 / "nightjar.jpg", 0.5, 0.5, None, "fit", None, "Come for the tiger.\nFall for the whole forest.",
     ["Save this  ·  Comment SAFARI for the link"], None),
]

def cover_crop(im, fx, fy):
    s = max(W / im.width, H / im.height); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(int(im.width * fx - W / 2), 0), im.width - W); y = min(max(int(im.height * fy - H / 2), 0), im.height - H)
    return im.crop((x, y, x + W, y + H))

def gradient(img, where, strength=0.86, span=0.62):
    a = np.zeros((H, 1), np.float32); n = int(H * span)
    ramp = np.linspace(0, 1, n) ** 1.6 * strength
    if where == "bottom": a[H - n:, 0] = ramp
    else: a[:n, 0] = ramp[::-1]
    arr = np.asarray(img).astype(np.float32) * (1 - a[..., None])
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))

def wrap(d, text, font, maxw):
    out = []
    for para in text.split("\n"):
        line = ""
        for w in para.split():
            t = (line + " " + w).strip()
            if d.textlength(t, font=font) <= maxw: line = t
            else: out.append(line); line = w
        out.append(line)
    return out

def footer(d, k, n):
    fs = f(BODYB, 26)
    d.text((M, H - 62), "@lostandfree  ×  @travelwithisha", font=fs, fill=(255, 255, 255, 230))
    x = W - M
    if k < n:
        d.text((x, H - 66), "→", font=f(ARROW, 30), fill=(255, 255, 255, 230), anchor="ra"); x -= 52
    d.text((x, H - 62), f"{k}/{n}", font=fs, fill=(255, 255, 255, 230), anchor="ra")

def slide(k, spec):
    path, fx, fy, lift, pos, kick, head, body, note = spec
    im = Image.open(path).convert("RGB")
    if lift:
        g, s = lift; im = im.point(lambda v: int(255 * (v / 255) ** (1 / g))); im = ImageEnhance.Color(im).enhance(s)
    if pos == "fit":                                          # whole photo on black (its edges are black: Isha's nightjar note)
        canvas = Image.new("RGB", (W, H), (0, 0, 0)); s = W / im.width
        im = im.resize((W, round(im.height * s)), Image.LANCZOS); canvas.paste(im, (0, 150)); im = canvas
        d = ImageDraw.Draw(im); y = 150 + im.height if False else 150 + round(1280 * s) + 40
        d.text((M, y), "AND THE ONES YOU'D DRIVE RIGHT PAST", font=f(BODYB, 28), fill=GOLD); y += 70
        hf = f(SERIF, 72)
        for line in ("Come for the tiger.", "Fall for the whole forest."): d.text((M, y), line, font=hf, fill=GOLD); y += 86
        d.text((M, y + 24), "Save this  ·  Comment SAFARI for the link", font=f(BODY, 38), fill=WHITE)
        return im
    im = cover_crop(im, fx, fy)
    if pos == "cover":
        im = gradient(im, "bottom", 0.92, 0.5)
        im = gradient(im, "top", 0.6, 0.2)
        d = ImageDraw.Draw(im)
        d.text((M, M), "CORBETT, UNFILTERED  ·  2/3", font=f(BODYB, 30), fill=MARI)
        y = 752
        for txt, col, size in (("WE CELEBRATE", WHITE, 112), ("TIGER NUMBERS.", WHITE, 112), ("BUT IS THE", MARI, 112), ("FOREST OK?", MARI, 112)):
            d.text((M, y), txt, font=f(ANTON, size), fill=col); y += 118
        d.text((M, H - 66), "the uncomfortable truth", font=f(BODYB, 30), fill=WHITE)
        d.text((M + d.textlength("the uncomfortable truth", font=f(BODYB, 30)) + 16, H - 70), "→", font=f(ARROW, 32), fill=WHITE)
        return im
    im = gradient(im, pos, 0.88, 0.66)
    if pos == "bottom": im = gradient(im, "top", 0.0, 0.1)
    else: im = gradient(im, "bottom", 0.55, 0.16)              # keeps the footer legible
    d = ImageDraw.Draw(im)
    hf, bf, kf = f(SERIF, 72 if len(head) < 26 else 62), f(BODY, 38), f(BODYB, 28)
    hl = wrap(d, head, hf, W - 2 * M)
    block = (44 if kick else 0) + len(hl) * int(hf.size * 1.18) + 24 + len(body) * 54 + (50 if note else 0)
    y = M + 10 if pos == "top" else H - 110 - block
    if kick: d.text((M, y), kick, font=kf, fill=GOLD); y += 44
    for line in hl: d.text((M, y), line, font=hf, fill=GOLD); y += int(hf.size * 1.18)
    y += 24
    for line in body: d.text((M, y), line, font=bf, fill=WHITE); y += 54
    if note: d.text((M, y + 14), note, font=f(BODY, 24), fill=(235, 235, 235))
    return im

if __name__ == "__main__":
    imgs = []
    for k, spec in enumerate(SLIDES, 1):
        im = slide(k, spec); d = ImageDraw.Draw(im)
        if k > 1: footer(d, k, len(SLIDES))
        im.save(P / f"out/W2-C2_slide_{k}.png"); imgs.append(im)
    imgs[0].save(P / "out/W2-C2_carousel.pdf", save_all=True, append_images=imgs[1:], resolution=150)
    sheet = Image.new("RGB", (270 * 8, 338)); [sheet.paste(i.resize((270, 338)), (270 * j, 0)) for j, i in enumerate(imgs)]
    sheet.save(P / "out/contact_sheet.png"); print("8 slides + pdf")
