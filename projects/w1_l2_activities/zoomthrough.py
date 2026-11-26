"""W1-L2 photo track: Isha's photos joined by ONE transition style used throughout, the zoom-through
(the outgoing shot accelerates in with a radial motion-blur, the incoming shot lands from 1.25x and settles).
This is one of the most-used transitions in high-reach travel reels (sources in NOTES.md). Each still also
carries a slow handheld drift so nothing sits like a slideshow. numpy + Pillow -> ffmpeg.
Usage: python zoomthrough.py   (writes broll/photos.mp4 + broll/photos_cuts.json)"""
import json, math, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
P = Path(__file__).resolve().parent; ROOT = P.parent.parent
L1, T1, L3 = ROOT / "projects/w1_l1_details_out/broll/isha", ROOT / "projects/w1_t1_7years/broll/isha", ROOT / "projects/w1_l3_pov/broll"
W, H, FPS, TR = 1080, 1920, 30, 5                         # TR = transition frames each side of a cut
# (image, focus x, focus y, seconds, lift (gamma, sat) or None)
SHOTS = [
    (L1 / "tiger_leaves.jpg", 0.50, 0.38, 1.9, None),        # hook: the tiger (only one of the five)
    (L3 / "dawn_src.jpg", 0.50, 0.45, 1.5, (1.1, 1.1)),       # 01 morning open jeep: dawn forest
    (L1 / "jeeps_tiger.jpg", 0.50, 0.55, 1.6, None),          #    jeeps + tiger
    (L1 / "tiger_road.jpg", 0.50, 0.50, 1.5, None),           # 02 evening safari
    (L1 / "jackal.jpg", 0.56, 0.50, 1.4, None),               #    jackal in golden light
    (T1 / "littlebird.jpg", 0.45, 0.42, 0.9, None),           # 03 birding walk
    (T1 / "duck.jpg", 0.40, 0.45, 0.9, (1.15, 1.1)),
    (T1 / "kingfisher_fish.jpg", 0.57, 0.50, 1.0, (1.35, 1.4)),
    (T1 / "mongoose.jpg", 0.30, 0.55, 1.0, None),             # 04 the small ones
    (L1 / "dholes.jpg", 0.40, 0.55, 1.2, None),
]

def load(path, lift):
    im = Image.open(path).convert("RGB")
    if lift:
        g, s = lift
        im = im.point(lambda v: int(255 * (v / 255) ** (1 / g)))
        im = ImageEnhance.Color(im).enhance(s)
    if im.height < 1200:                                     # small sources: upscale once so crops stay sharp-ish
        k = 1300 / im.height; im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    return im

def view(im, fx, fy, z, jx, jy):
    base = max(W / im.width, H / im.height) * 1.08
    s = base * z; cw, ch = W / s, H / s
    cx = min(max(im.width * fx + jx / s, cw / 2), im.width - cw / 2)
    cy = min(max(im.height * fy + jy / s, ch / 2), im.height - ch / 2)
    return np.asarray(im.resize((W, H), Image.BILINEAR, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))).astype(np.float32)

def radial_blur(arr, strength):
    """zoom blur: average of progressively upscaled copies about the centre"""
    if strength < 0.01: return arr
    acc = arr.copy(); n = 6
    im = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
    for k in range(1, n):
        z = 1 + strength * k / n; cw, ch = W / z, H / z
        acc += np.asarray(im.resize((W, H), Image.BILINEAR, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))).astype(np.float32)
    return acc / n

def main():
    imgs = [load(p, l) for p, *_ , l in SHOTS]
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p", "-c:v", "libx264", "-crf", "16",
                           "-preset", "veryfast", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                           str(P / "broll/photos.mp4")], stdin=subprocess.PIPE)
    cuts, t0 = [], 0.0
    for k, (im, (_, fx, fy, dur, _)) in enumerate(zip(imgs, SHOTS)):
        n = int(round(dur * FPS)); cuts.append(round(t0, 3)); t0 += n / FPS
        for i in range(n):
            t = (i + 0.5) / FPS
            z = 1.0 + 0.05 * i / n                            # slow push
            blur = 0.0
            if k > 0 and i < TR:                              # landing: 1.25x -> 1.0 (ease-out)
                u = (i + 1) / (TR + 1); z += 0.25 * (1 - u) ** 2; blur = 0.22 * (1 - u) ** 2
            if k < len(SHOTS) - 1 and i >= n - TR:            # take-off: accelerate in (ease-in)
                u = (i - (n - TR) + 1) / TR; z += 0.35 * u ** 2; blur = max(blur, 0.28 * u ** 2)
            a = 0.6 * math.sin(2 * math.pi * 0.8 * t + k) + 0.4 * math.sin(2 * math.pi * 1.7 * t + 2 * k)
            b = 0.6 * math.sin(2 * math.pi * 0.6 * t + 1 + k) + 0.4 * math.sin(2 * math.pi * 1.3 * t + k)
            arr = radial_blur(view(im, fx, fy, z, 6 * a, 6 * b), blur)
            ff.stdin.write(arr.clip(0, 255).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait()
    json.dump({"cuts": cuts, "end": round(t0, 3)}, open(P / "broll/photos_cuts.json", "w"))
    print("photos.mp4", round(t0, 2), "s, cuts", cuts)

if __name__ == "__main__":
    main()
