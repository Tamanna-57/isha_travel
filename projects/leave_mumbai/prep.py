"""Prep for the Leave Mumbai reel (rebuilt from Isha's raw clips): animated overlays + an original music bed.

  build/chart.mov   IQAir 2024 donut chart (alpha), shown while she says "13 out of the world's 20 ... India"
  build/logo.mov    Lost & Free Safaris logo card (alpha), pops in on "Lost & Free"
  build/music.wav   calm original bed (numpy synth): low pad under the rant, lifts on "main jungle jaati hoon"
Times come from edit.json (clip starts), so re-run after changing the cut:  python projects/leave_mumbai/prep.py
"""
import json, math, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

P = Path(__file__).resolve().parent
ROOT = P.parent.parent
B = P / "build"
FPS = 30

# ------------------------------------------------------------------ Lost & Free Safaris pop-up
LOGO = ROOT / "projects" / "safari" / "assets" / "logo.png"           # official cream logo, transparent
LOGO_BG = tuple(int(v) for v in (ROOT / "projects/safari/assets/logo_bg.txt").read_text().split())  # olive
POP_IN, POP_OUT = 0.0, 0.0                 # set from edit.json in main()
CARD_W, CARD_H, CARD_X, CARD_Y = 400, 430, 110, 175   # top-left, where the old @lostandfree tag sat

def card_image():
    s = 3                                                # supersample for clean edges
    card = Image.new("RGBA", (CARD_W * s, CARD_H * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, CARD_W * s - 1, CARD_H * s - 1], radius=34 * s, fill=LOGO_BG + (255,))
    lg = Image.open(LOGO).convert("RGBA")
    lw = int(CARD_W * s * 0.80); lh = int(lg.height * lw / lg.width)
    lg = lg.resize((lw, lh), Image.LANCZOS)
    card.alpha_composite(lg, ((CARD_W * s - lw) // 2, int(26 * s)))
    f = ImageFont.truetype(str(ROOT / "fonts" / "Poppins-SemiBold.ttf"), 30 * s)
    handle = "@lostandfree"
    tw = d.textlength(handle, font=f)
    d.text(((CARD_W * s - tw) / 2, CARD_H * s - 58 * s), handle, font=f, fill=(247, 243, 234, 255))
    card = card.resize((CARD_W, CARD_H), Image.LANCZOS)
    # hard drop shadow like the captions
    sh = Image.new("RGBA", (CARD_W + 12, CARD_H + 12), (0, 0, 0, 0))
    a = card.split()[3].point(lambda v: int(v * 0.55))
    sh.paste(Image.new("RGBA", card.size, (0, 0, 0, 255)), (8, 8), a)
    sh.alpha_composite(card, (0, 0))
    return sh

def popup_clip():
    """RGBA frames of the card: pops in (scale 0.80 -> 1.0, ease-out 0.28 s), holds, fades out 0.2 s"""
    out = B / "logo.mov"
    card = card_image()
    n = int(round((POP_OUT - POP_IN) * FPS))
    cw, ch = card.size
    proc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{cw}x{ch}",
                             "-r", str(FPS), "-i", "-", "-c:v", "qtrle", str(out)], stdin=subprocess.PIPE)
    for k in range(n):
        t = k / FPS
        u = min(1.0, t / 0.28); e = 1 - (1 - u) ** 3
        sc = 0.80 + 0.20 * e + 0.03 * np.sin(np.pi * u) * (u < 1)       # tiny overshoot = "pop"
        al = min(1.0, t / 0.12) * min(1.0, max(0.0, (POP_OUT - POP_IN - t) / 0.2))
        fr = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        im = card.resize((max(1, int(cw * sc)), max(1, int(ch * sc))), Image.BICUBIC)
        a = im.split()[3].point(lambda v: int(v * al)); im.putalpha(a)
        fr.alpha_composite(im, ((cw - im.width) // 2, (ch - im.height) // 2))
        proc.stdin.write(fr.tobytes())
    proc.stdin.close(); proc.wait()
    return out

# ------------------------------------------------------------------ IQAir chart (replaces the source text line)
# IQAir 2024 World Air Quality Report: 13 of the world's 20 most polluted cities are in India; India's average PM2.5
# is 50.6 ug/m3, over 10x the WHO annual guideline (5 ug/m3). https://www.iqair.com/newsroom/waqr-2024-pr
CH_IN, CH_OUT = 0.0, 0.0                   # set from edit.json in main()
CH_W, CH_H, CH_X, CH_Y = 830, 440, 125, 150
PAPER, INK, MUTED, REST = (247, 243, 234), (17, 17, 17), (95, 95, 95), (140, 140, 140)
SIND = (215, 38, 61)

def chart_frame(t):
    s = 3
    f = lambda n, z: ImageFont.truetype(str(ROOT / "fonts" / n), z * s)
    im = Image.new("RGBA", (CH_W * s, CH_H * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, CH_W * s - 1, CH_H * s - 1], radius=30 * s, fill=PAPER + (255,))
    # donut: India 13/20 sweeps in (0.15-0.85 s, ease-out), then the rest of the world
    cx, cy, r, th = 200 * s, 205 * s, 150 * s, 50 * s
    u = min(1.0, max(0.0, (t - 0.15) / 0.7)); e = 1 - (1 - u) ** 3
    a_in = 360 * 13 / 20 * e
    box = [cx - r, cy - r, cx + r, cy + r]
    if e > 0.995:
        d.pieslice(box, -90 + a_in, 270, fill=REST + (255,))
    if a_in > 0.5:
        d.pieslice(box, -90, -90 + a_in, fill=SIND + (255,))
    if e > 0.995:                                             # 2 px paper gaps between the two segments
        for ang in (-90, -90 + a_in):
            import math
            x2 = cx + (r + 4) * math.cos(math.radians(ang)); y2 = cy + (r + 4) * math.sin(math.radians(ang))
            d.line([cx, cy, x2, y2], fill=PAPER + (255,), width=3 * s)
    d.ellipse([cx - r + th, cy - r + th, cx + r - th, cy + r - th], fill=PAPER + (255,))
    num = str(int(round(13 * e)))
    tw = d.textlength(num, font=f("Anton-Regular.ttf", 92)); d.text((cx - tw / 2, cy - 86 * s), num, font=f("Anton-Regular.ttf", 92), fill=INK)
    tw = d.textlength("of 20", font=f("Poppins-SemiBold.ttf", 26)); d.text((cx - tw / 2, cy + 46 * s), "of 20", font=f("Poppins-SemiBold.ttf", 26), fill=MUTED)
    # right column
    x = 395 * s
    d.text((x, 34 * s), "World's 20 most", font=f("Poppins-Bold.ttf", 38), fill=INK)
    d.text((x, 82 * s), "polluted cities", font=f("Poppins-Bold.ttf", 38), fill=INK)
    d.text((x, 132 * s), "2024", font=f("Poppins-SemiBold.ttf", 26), fill=MUTED)
    for k, (col, lab, n) in enumerate([(SIND, "India", "13"), (REST, "Rest of the world", "7")]):
        y = (196 + 52 * k) * s
        d.rounded_rectangle([x, y + 6 * s, x + 26 * s, y + 32 * s], radius=6 * s, fill=col + (255,))
        d.text((x + 40 * s, y), lab, font=f("Poppins-SemiBold.ttf", 30), fill=INK)
        nw = d.textlength(n, font=f("Poppins-Bold.ttf", 30)); d.text((CH_W * s - 40 * s - nw, y), n, font=f("Poppins-Bold.ttf", 30), fill=INK)
    d.text((x, 318 * s), "India's air: over 10×", font=f("Poppins-SemiBold.ttf", 25), fill=INK)
    d.text((x, 352 * s), "the WHO safe limit", font=f("Poppins-SemiBold.ttf", 25), fill=INK)
    src = "Source: IQAir World Air Quality Report 2024"
    tw = d.textlength(src, font=f("Poppins-Regular.ttf", 17)); d.text(((CH_W * s - tw) / 2, CH_H * s - 34 * s), src, font=f("Poppins-Regular.ttf", 17), fill=MUTED)
    im = im.resize((CH_W, CH_H), Image.LANCZOS)
    sh = Image.new("RGBA", (CH_W + 12, CH_H + 12), (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", im.size, (0, 0, 0, 255)), (8, 8), im.split()[3].point(lambda v: int(v * 0.55)))
    sh.alpha_composite(im, (0, 0))
    return sh

def chart_clip():
    out = B / "chart.mov"
    n = int(round((CH_OUT - CH_IN) * FPS))
    cw, ch = CH_W + 12, CH_H + 12
    proc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{cw}x{ch}",
                             "-r", str(FPS), "-i", "-", "-c:v", "qtrle", str(out)], stdin=subprocess.PIPE)
    for k in range(n):
        t = k / FPS
        card = chart_frame(t)
        u = min(1.0, t / 0.25); sc = 0.9 + 0.1 * (1 - (1 - u) ** 3)
        al = min(1.0, t / 0.12) * min(1.0, max(0.0, (CH_OUT - CH_IN - t) / 0.2))
        fr = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        im = card.resize((int(cw * sc), int(ch * sc)), Image.BICUBIC)
        im.putalpha(im.split()[3].point(lambda v: int(v * al)))
        fr.alpha_composite(im, ((cw - im.width) // 2, (ch - im.height) // 2))
        proc.stdin.write(fr.tobytes())
    proc.stdin.close(); proc.wait()
    return out

# ------------------------------------------------------------------ render
# ------------------------------------------------------------------ music: calm original bed
SR = 48000
def music(path, dur, t_lift):
    """A minor pad (Am - F - C - G), 76 BPM feel, soft. Under the rant it stays low and dark;
    from t_lift ("main jungle jaati hoon") it opens up: brighter voicing + soft plucked arpeggio."""
    n = int(dur * SR) + 1; t = np.arange(n) / SR
    rng = np.random.default_rng(3)
    out = np.zeros((2, n))
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55, 60], [55, 59, 62]]   # Am F C G
    bar = 4 * 60 / 76
    f = lambda m: 440 * 2 ** ((m - 69) / 12)
    k = 0; t0 = 0.0
    while t0 < dur:
        ch = chords[k % 4]; seg = (t >= t0) & (t < t0 + bar + 0.6)
        tt = t[seg] - t0
        env = np.minimum(1, tt / 0.8) * np.minimum(1, np.maximum(0, (bar + 0.6 - tt) / 0.8))
        for j, m in enumerate(ch):
            for det, pan in ((-0.07, -0.4), (0.07, 0.4)):
                ph = rng.uniform(0, 6)
                w = (np.sin(2 * np.pi * f(m + det) * tt + ph) + 0.25 * np.sin(4 * np.pi * f(m + det) * tt + ph))
                out[0, seg] += w * env * 0.06 * (1 - pan) / 2
                out[1, seg] += w * env * 0.06 * (1 + pan) / 2
        out[:, seg] += np.sin(2 * np.pi * f(ch[0] - 12) * tt) * env * 0.05             # soft bass
        if t0 + bar > t_lift:                                                           # lift: plucked arpeggio
            for s_ in range(8):
                ts = t0 + s_ * bar / 8
                if ts < t_lift or ts >= dur:
                    continue
                m = ch[s_ % len(ch)] + 12
                i0 = int(ts * SR); L = int(0.9 * SR); tt2 = np.arange(L) / SR
                pl = (np.sin(2 * np.pi * f(m) * tt2) + 0.3 * np.sin(4 * np.pi * f(m) * tt2)) * np.exp(-tt2 / 0.35) * 0.09
                L = min(L, n - i0); out[0, i0:i0 + L] += pl[:L] * 0.8; out[1, i0:i0 + L] += pl[:L]
        t0 += bar; k += 1
    out = sosfilt(butter(2, [60, 9000], "bandpass", fs=SR, output="sos"), out, axis=1)
    lift = np.clip((t - t_lift) / 1.5, 0, 1) * 0.35 + 0.65                                # louder after the lift
    out *= lift
    out /= np.abs(out).max() + 1e-9; out *= 0.8
    wavfile.write(path, SR, out.T.astype(np.float32))

# ------------------------------------------------------------------ main
def main():
    global POP_IN, POP_OUT, CH_IN, CH_OUT
    B.mkdir(exist_ok=True)
    edit = json.loads((P / "edit.json").read_text(encoding="utf-8"))
    starts, acc = [], 0.0
    for c in edit["clips"]:
        starts.append(acc); acc += (c["out"] - c["in"]) / c.get("speed", 1.0)
    cue = {c.get("_cue"): starts[i] for i, c in enumerate(edit["clips"]) if c.get("_cue")}
    CH_IN, CH_OUT = cue["chart"] + 0.08, cue["chart_end"]
    POP_IN, POP_OUT = cue["logo"] + 0.05, cue["logo_end"]
    chart_clip(); popup_clip()
    music(str(B / "music.wav"), acc + 0.5, cue["lift"])
    # write the overlay/sfx timing back into edit.json
    edit["overlays"] = [{"src": "build/chart.mov", "at": round(CH_IN, 3), "x": CH_X - 4, "y": CH_Y - 4},
                        {"src": "build/logo.mov", "at": round(POP_IN, 3), "x": CARD_X - 4, "y": CARD_Y - 4}]
    edit["sfx"] = [{"src": "../../sfx_library/msg_soft_pop.mp3", "at": round(POP_IN, 3), "gain_db": -14}]
    (P / "edit.json").write_text(json.dumps(edit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"reel {acc:.2f}s · chart {CH_IN:.2f}-{CH_OUT:.2f} · logo {POP_IN:.2f}-{POP_OUT:.2f} · lift {cue['lift']:.2f}")

if __name__ == "__main__":
    main()
