"""Safari look LUT (v2 2026-11-04: client said v1 'looks a bit dull' -> more contrast + colour) (33^3, applied after HLG->SDR tone-map). Ref 2 (Video-11291) colour: soft, natural, muted greens.
- foliage (HSV hue 55-115 deg): saturation x0.70, hue nudged +5 deg (lime -> leaf green), value x0.93
- skin (hue 5-50): saturation x0.90 (cheek chroma ~29 -> ~23, memory: no saturated faces), hue kept
- everything else x0.90; gentle filmic S-curve with a lifted black floor (~10/255) and soft highlight roll-off"""
import numpy as np, colorsys, sys
from pathlib import Path
N = 33
def band(h, a, b, soft=12):
    """1 inside [a,b] degrees, raised-cosine to 0 over `soft` degrees outside"""
    d = np.maximum(a - h, h - b)
    return np.where(d <= 0, 1.0, np.where(d >= soft, 0.0, 0.5 + 0.5 * np.cos(np.pi * d / soft)))
def curve(x):
    x = np.clip((x - 0.065) / (0.955 - 0.065), 0, 1)        # black point down (tone-mapped HLG sits ~40/255)
    y = 0.012 + 0.975 * x                                   # tiny floor lift, protect highlights
    s = y + 0.055 * np.sin(2 * np.pi * (y - 0.5)) * -1.0 * (1 - np.abs(2 * y - 1) ** 1.5)  # S-curve: punchier mids
    return np.clip(s, 0, 1)
g = np.linspace(0, 1, N)
lines = [f"TITLE \"Isha Safari Soft\"", f"LUT_3D_SIZE {N}"]
out = np.zeros((N, N, N, 3))
for bi, b in enumerate(g):
    for gi, gg in enumerate(g):
        for ri, r in enumerate(g):
            h, s, v = colorsys.rgb_to_hsv(r, gg, b)
            hd = h * 360
            fol, skin = band(hd, 55, 115), band(hd, 5, 50, 10)
            other = 1 - np.maximum(fol, skin)
            sat = fol * 0.86 + skin * 0.84 + other * 1.06
            hd2 = hd + 5 * fol + 3 * skin
            v2 = v * (1 - 0.04 * fol * min(1, s * 2))
            rr, gg2, bb = colorsys.hsv_to_rgb((hd2 % 360) / 360, min(1, s * sat), v2)
            out[bi, gi, ri] = curve(np.array([rr, gg2, bb]))
for bi in range(N):
    for gi in range(N):
        for ri in range(N):
            lines.append("%.6f %.6f %.6f" % tuple(out[bi, gi, ri]))
Path(sys.argv[1] if len(sys.argv) > 1 else "build/safari_soft.cube").write_text("\n".join(lines) + "\n")
