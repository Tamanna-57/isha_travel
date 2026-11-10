"""brand/06_client_approved_look.png: real frames from the client-approved Bhai Dooj reel, annotated.
Run after a finish render: python projects/bhai_dooj/make_board.py"""
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

P = Path(__file__).resolve().parent
ROOT = P.parent.parent
SRC = P / "out" / "bhai_dooj.mp4"
OUT = ROOT / "brand" / "06_client_approved_look.png"
F = lambda name, size: ImageFont.truetype(str(ROOT / "fonts" / name), size)

FRAMES = [  # time, label, spec
    (0.50, "Hook title + karaoke caption", "Anton sindoor + Allura · Poppins SemiBold 115"),
    (8.20, "L-cut B-roll under her voice", "caption keeps running · grade natural"),
    (10.50, "Person label (bold, hard shadow)", "Playfair Bold 70 · marigold word · no box"),
    (17.20, "Label + caption on busy B-roll", "label y 1060 · caption y 1340"),
    (28.30, "Talking head, emotional line", "grade indoor · punch-in 1.10"),
    (32.60, "End card on black", "Poppins Bold 96 · after fade to black"),
]
TW, TH, PAD, LAB = 360, 640, 28, 92

def grab(t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(SRC), "-frames:v", "1",
                          "-vf", f"scale={TW}:{TH}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return Image.frombytes("RGB", (TW, TH), raw)

def main():
    cols, rows = 3, 2
    W = PAD + cols * (TW + PAD); H = 150 + rows * (TH + LAB + PAD)
    img = Image.new("RGB", (W, H), (21, 21, 21)); d = ImageDraw.Draw(img)
    d.text((PAD, 30), "CLIENT-APPROVED LOOK", font=F("Anton-Regular.ttf", 56), fill=(255, 255, 255))
    d.text((PAD, 100), "Bhai Dooj reel, Nov 2026 · default for new reels · spec: projects/bhai_dooj/REEL_SPEC.md",
           font=F("Poppins-Medium.ttf", 20), fill=(154, 154, 154))
    for k, (t, lab, sub) in enumerate(FRAMES):
        x = PAD + (k % cols) * (TW + PAD); y = 150 + (k // cols) * (TH + LAB + PAD)
        img.paste(grab(t), (x, y))
        d.rectangle([x, y, x + TW - 1, y + TH - 1], outline=(60, 60, 60))
        d.text((x, y + TH + 12), lab, font=F("Poppins-SemiBold.ttf", 21), fill=(246, 196, 69))
        d.text((x, y + TH + 44), sub, font=F("Poppins-Regular.ttf", 16), fill=(200, 200, 200))
        d.text((x + 8, y + 6), f"{t:.1f}s", font=F("Poppins-Medium.ttf", 16), fill=(255, 255, 255))
    img.save(OUT, optimize=True)
    print(OUT)

if __name__ == "__main__":
    main()
