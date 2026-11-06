"""Safari grade v3 (2026-11-04). Client on v2: "she looks pale / grey", then "it looks very weird".
Diagnosis: v2 pushed skin and foliage separately with narrow HSV hue bands -> patchy face (rosy cheeks, grey forehead),
and the hable tone-map left whites at ~190/255 so the whole frame read grey.
v3 is one smooth, global correction (no hue-band tricks on skin):
  1. luminance curve with a soft shoulder: whites ~190 -> ~236, skin mids up a little, blacks kept deep
     (RGB scaled by Y'/Y so hue and saturation ratios stay put; anything that would clip is eased toward grey)
  2. tiny warm white balance, so the white top reads clean, not cyan-grey
  3. saturation: everything x1.04, yellow-greens only gently calmed (wide, smooth hue window), skin untouched
Usage: python make_lut3.py out.cube [white_in] [gamma] [sat] [green_sat]"""
import sys
import numpy as np
from pathlib import Path

N = 33
WHITE_IN = float(sys.argv[2]) if len(sys.argv) > 2 else 0.81     # input level that becomes ~0.93 (hable white top ~0.75)
GAMMA = float(sys.argv[3]) if len(sys.argv) > 3 else 0.98
SAT = float(sys.argv[4]) if len(sys.argv) > 4 else 0.88
GREEN_SAT = float(sys.argv[5]) if len(sys.argv) > 5 else 0.85
WB = np.array([1.012, 1.0, 0.985])

def tone(y):
    x = np.clip((y - 0.035) / (WHITE_IN - 0.035), 0, None)            # black point + exposure
    x = x ** GAMMA
    k = 0.80                                                          # soft shoulder above 0.80
    over = np.maximum(x - k, 0)
    x = np.where(x > k, k + (1 - k) * (1 - np.exp(-over / (1 - k))), x)
    s = x + 0.035 * np.sin(2 * np.pi * (x - 0.5)) * -1.0 * (1 - np.abs(2 * x - 1) ** 1.5)   # gentle S
    return np.clip(0.008 + 0.985 * s, 0, 1)

g = np.linspace(0, 1, N)
b, gg, r = np.meshgrid(g, g, g, indexing="ij")                        # .cube order: r fastest
rgb = np.stack([r, gg, b], -1) * WB
Y = rgb @ np.array([0.2126, 0.7152, 0.0722])
Yt = tone(Y)
out = rgb * (Yt / np.maximum(Y, 1e-4))[..., None]
# saturation in a luma/chroma split; hue of the chroma vector decides the gentle green calm
chroma = out - Yt[..., None]
cb, cr = out[..., 2] - Yt, out[..., 0] - Yt
hue = np.degrees(np.arctan2(cb, cr)) % 360            # skin ~ 330-360/0-20, foliage ~ 235-265
d = np.minimum(np.abs(hue - 255), 360 - np.abs(hue - 255))
w = np.where(d < 45, 0.5 + 0.5 * np.cos(np.pi * d / 45), 0.0)
sat = SAT * (1 - w) + GREEN_SAT * w
out = Yt[..., None] + chroma * sat[..., None]
# anything out of gamut: pull toward its own luma instead of hard-clipping one channel (no hue shifts)
hi = out.max(-1); lo = out.min(-1)
f = np.ones_like(hi)
m = hi > 1
f[m] = np.minimum(f[m], (1 - Yt[m]) / np.maximum(hi[m] - Yt[m], 1e-6))
m = lo < 0
f[m] = np.minimum(f[m], Yt[m] / np.maximum(Yt[m] - lo[m], 1e-6))
out = Yt[..., None] + (out - Yt[..., None]) * f[..., None]
out = np.clip(out, 0, 1)
lines = ['TITLE "Isha Safari v3"', f"LUT_3D_SIZE {N}"] + ["%.6f %.6f %.6f" % tuple(v) for v in out.reshape(-1, 3)]
Path(sys.argv[1] if len(sys.argv) > 1 else "build/safari_v3.cube").write_text("\n".join(lines) + "\n")
