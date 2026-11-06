"""Bake the grade presets in isha.py into 33/64-point .cube LUTs for CapCut / Premiere / Resolve.
Grain (noise) can't live in a LUT and is dropped; add it in the editor (film look: ~5% grain).
Usage: python pipeline/make_luts.py"""
import io, re, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from isha import GRADES, ROOT

OUT = ROOT / "luts"
LEVEL = 8                      # hald level 8 -> 64^3 cube, 512x512 image
N = LEVEL * LEVEL
NAMES = {"natural": "Isha_Natural", "golden": "Isha_Golden", "indoor": "Isha_Indoor", "film": "Isha_Film"}

def hald(chain):
    vf = (chain + "," if chain else "") + "format=rgb24"
    r = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", f"haldclutsrc={LEVEL}", "-frames:v", "1",
                        "-vf", vf, "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True)
    return np.asarray(Image.open(io.BytesIO(r.stdout)).convert("RGB"), dtype=np.float64).reshape(-1, 3) / 255.0

def resample(rgb, size):
    """trilinear resample of the 64^3 lut to size^3 (33 = most compatible: CapCut, phones)"""
    lut = rgb.reshape(N, N, N, 3)                       # [b][g][r]
    x = np.linspace(0, N - 1, size); i0 = np.floor(x).astype(int).clip(0, N - 2); f = x - i0
    out = np.zeros((size, size, size, 3))
    for bi in range(size):
        for gi in range(size):
            b0, g0, fb, fg = i0[bi], i0[gi], f[bi], f[gi]
            r0, fr = i0, f[:, None]
            c = lambda b, g: lut[b, g, r0] * (1 - fr) + lut[b, g, r0 + 1] * fr
            out[bi, gi] = ((c(b0, g0) * (1 - fg) + c(b0, g0 + 1) * fg) * (1 - fb) +
                           (c(b0 + 1, g0) * (1 - fg) + c(b0 + 1, g0 + 1) * fg) * fb)
    return out.reshape(-1, 3)

def write_cube(path, rgb, title, size=N):
    lines = [f'TITLE "{title}"', f"LUT_3D_SIZE {size}", "DOMAIN_MIN 0.0 0.0 0.0", "DOMAIN_MAX 1.0 1.0 1.0"]
    lines += [f"{r:.6f} {g:.6f} {b:.6f}" for r, g, b in rgb]     # hald order = red fastest = .cube order
    path.write_text("\n".join(lines) + "\n")

OUT.mkdir(exist_ok=True)
ident = hald("")
i = np.arange(N ** 3)
expect = np.stack([i % N, (i // N) % N, i // (N * N)], 1) / (N - 1)   # red fastest, blue slowest
err = np.abs(ident - expect).max()
print(f"identity check: max error {err * 255:.2f}/255")
for key, name in NAMES.items():
    chain = re.sub(r",?noise=[^,]*", "", GRADES[key]).strip(",")
    rgb = hald(chain)
    write_cube(OUT / f"{name}_64.cube", rgb, name)
    write_cube(OUT / f"{name}.cube", resample(rgb, 33), name, 33)
    print(f"{name}.cube  (mean shift R{(rgb[:,0]-ident[:,0]).mean()*255:+.1f} G{(rgb[:,1]-ident[:,1]).mean()*255:+.1f} "
          f"B{(rgb[:,2]-ident[:,2]).mean()*255:+.1f})")
