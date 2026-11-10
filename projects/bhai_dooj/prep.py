"""Prep for the Bhai Dooj reel: photo B-roll clips + the original music bed.

1. Isha's own safari photos (from the archive zip in the repo root) -> 1080x1920 30 fps clips with a slow push-in,
   build/broll/<name>.mp4, so the pipeline can use them as B-roll.
2. synth.py -> build/music.wav, with the music cues placed on this edit's cuts (read from edit.json).
Run before `isha.py render`.
"""
import io, json, subprocess, sys, zipfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps

P = Path(__file__).resolve().parent
ROOT = P.parent.parent
B = P / "build"
ZIP = ROOT / "24 Dec 2018 – 2 Aug 2025.zip"
W, H, FPS = 1080, 1920, 30

# name -> (file in the zip, centre x, centre y (0..1 of the photo), zoom start, zoom end, seconds)
PHOTOS = {
    "jeep_tiger": ("DSC_2505~2_Original.jpg", 0.52, 0.55, 1.00, 1.06, 2.6),   # tiger walking past the safari jeeps
    "tiger_road": ("20191001163304_IMG_6083_Original.JPG", 0.50, 0.50, 1.04, 1.00, 2.2),  # tiger on the jungle road
}
# end card: plain black, the last clip fades into it as her tika finger reaches the lens
BLACK_DUR = 2.0
# music cues: clip index in edit.json whose start is the cue
CUES = {"groove": 1, "soft": 12, "final": 13}

def photo_clip(name, src, cx, cy, z0, z1, dur, img=None):
    out = B / "broll" / f"{name}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    if img is None:
        with zipfile.ZipFile(ZIP) as z:
            member = next(m for m in z.namelist() if m.endswith("/" + src))
            img = ImageOps.exif_transpose(Image.open(io.BytesIO(z.read(member)))).convert("RGB")
    iw, ih = img.size
    base = max(W / iw, H / ih)                       # cover 9:16
    n = int(round(dur * FPS))
    proc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "14",
                             "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                             "-colorspace", "bt709", str(out)], stdin=subprocess.PIPE)
    for k in range(n):
        u = k / max(1, n - 1)
        u = 0.5 - 0.5 * np.cos(np.pi * u)              # ease in-out
        s = base * (z0 + (z1 - z0) * u)
        cw, ch = W / s, H / s                          # crop window in photo pixels
        x0 = min(max(cx * iw - cw / 2, 0), iw - cw); y0 = min(max(cy * ih - ch / 2, 0), ih - ch)
        fr = img.transform((W, H), Image.AFFINE, (cw / W, 0, x0, 0, ch / H, y0), resample=Image.BICUBIC)
        proc.stdin.write(fr.tobytes())
    proc.stdin.close(); proc.wait()
    print(f"photo clip: {out.relative_to(P)} ({dur}s)")

def black_clip():
    out = B / "broll" / "black.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}:d={BLACK_DUR}",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-pix_fmt", "yuv420p", str(out)], check=True)
    print(f"black clip: {out.relative_to(P)} ({BLACK_DUR}s)")

def main():
    B.mkdir(exist_ok=True)
    for name, args in PHOTOS.items():
        photo_clip(name, *args)
    black_clip()
    edit = json.loads((P / "edit.json").read_text(encoding="utf-8"))
    starts, acc = [], 0.0
    for c in edit["clips"]:
        if c.get("transition", "cut") != "cut":
            acc -= float(c.get("transition_dur", 0.25))      # xfade overlaps the two clips
        starts.append(acc)
        acc += (c["out"] - c["in"]) / c.get("speed", 1.0)
    subprocess.run([sys.executable, str(P / "synth.py"), str(B / "music.wav"), f"{acc:.3f}",
                    *(f"{starts[CUES[k]]:.3f}" for k in ("groove", "soft", "final"))], check=True)

if __name__ == "__main__":
    main()
