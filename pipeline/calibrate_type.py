"""Calibrate libass font sizes so on-screen text matches the reference reels' proportions.
Each target = width of a sample phrase as a fraction of the 1080 px frame, measured on reference frames
(see REFERENCE_LIBRARY.md). Prints the size that hits each target. Usage: python pipeline/calibrate_type.py"""
import subprocess, sys, tempfile
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import isha
from isha import FONTS

# (style, sample text, override tags, target width fraction, reference)
TARGETS = [
    ("Serif",    "Pakistan-Occupied",          "",            0.59, "iffy R1 @57s key word"),
    ("Sans",     "Expensive",                  isha.fn_tag("sans_xbold"), 0.35, "brinda R6 @17s key word"),
    ("Sans",     "Trip pe Jaane se",           "",            0.50, "brinda V5 @6s karaoke line"),
    ("Caps",     "MAI HU ABHI AAJ",            "",            0.49, "brinda R2 @1s"),
    ("Top",      "I booked my flights",        "",            0.34, "brinda R7 @3s (mixed line, sans part)"),
    ("Mono",     "we started sailing from",    "",            0.47, "sailing V4 @4s"),
    ("Chapter",  "JAPAN",                      "",            0.66, "brinda R2 @1s"),
    ("Script",   "mein",                       "",            0.33, "brinda R2 @1s"),
    ("Landmark", "CHENAB RAIL BRIDGE",         r"\fax-0.12",  0.68, "iffy V3 @9s"),
    ("Place",    "KYRGYZSTAN",                 "",            0.72, "sayannath V1 @8s"),
    ("Pill",     "This country is 'Sukoon'",   "",            0.61, "sayannath V1 @1s (box incl.)"),
    ("Hook",     "One wrong move and you'll",  "",            0.70, "sayannath V2 @0.5s"),
    ("Fact",     "1178 ft above Chenab River", "",            0.59, "iffy V3 @14s"),
    ("Marker",   "PoK Pakistan",               "",            0.49, "iffy R1 @4s"),
]

def measure(style, text, tags, size, tmp):
    # \q2 = no wrapping, so the width of the whole phrase is measured even when it's wider than the safe area
    ass = isha.ass_header() + isha.ev(0, 5, style, f"{{\\an5\\q2\\pos(540,960)\\fs{size}\\shad0\\bord0{tags}}}{text}") + "\n"
    if style == "Pill":   # keep the box: it's part of the visual width in the reference
        ass = isha.ass_header() + isha.ev(0, 5, style, f"{{\\an5\\q2\\pos(540,960)\\fs{size}{tags}}}{text}") + "\n"
    (tmp / "c.ass").write_text(ass, encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "color=c=0x808080:s=1080x1920:d=1",
                    "-frames:v", "1", "-vf", "ass=c.ass:fontsdir=fonts", "c.png"], cwd=tmp, check=True)
    a = np.asarray(Image.open(tmp / "c.png").convert("L"), dtype=int)
    cols = np.where((np.abs(a - 128) > 30).any(axis=0))[0]
    return (cols.max() - cols.min() + 1) / 1080 if cols.size else 0

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td); (tmp / "fonts").mkdir()
        for f in FONTS.glob("*.ttf"):
            (tmp / "fonts" / f.name).write_bytes(f.read_bytes())
        for style, text, tags, target, ref in TARGETS:
            s1, w1 = 100, measure(style, text, tags, 100, tmp)
            for _ in range(3):          # tracking/box padding don't scale linearly: iterate to converge
                s1 = round(s1 * target / w1)
                w1 = measure(style, text, tags, s1, tmp)
            print(f"{style:9s} size {s1:4d}  -> {w1:5.1%} (target {target:.0%})  '{text}'  [{ref}]")
