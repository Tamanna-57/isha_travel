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

P = Path(__file__).resolve().parent             # project dir (overridden by --project for the trial versions)
ROOT = P.parent.parent
B = P / "build"
# per-version look: chart India colour + music bed
VARIANTS = {
    "final": {"india": (215, 38, 61), "music": "calm"},
    "ocean": {"india": (47, 128, 237), "music": "lofi"},
    "pop":   {"india": (255, 79, 139), "music": "pop"},
}
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
    handle = "@lostandfreesafaris"     # client-confirmed handle
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
    # soft pulse so the bed doesn't feel flat: gentle kick on beats 1 and 3, a light shaker on the 8ths
    beat = 60 / 76
    kick_t = np.arange(int(0.35 * SR)) / SR
    kick = np.sin(2 * np.pi * np.cumsum(55 + 70 * np.exp(-kick_t / 0.03)) / SR) * np.exp(-kick_t / 0.12) * 0.22
    sh_n = int(0.08 * SR)
    shaker = sosfilt(butter(2, 6500, "highpass", fs=SR, output="sos"), rng.standard_normal(sh_n)) * np.exp(-np.arange(sh_n) / SR / 0.02) * 0.035
    tb = 0.0; kb = 0
    while tb < dur - 0.4:
        i0 = int(tb * SR)
        if kb % 2 == 0:
            L = min(len(kick), n - i0); out[:, i0:i0 + L] += kick[:L]
        for half in (0, 0.5):
            j0 = int((tb + half * beat) * SR); L = min(sh_n, n - j0)
            if L > 0:
                out[0, j0:j0 + L] += shaker[:L] * (0.7 if half else 0.5); out[1, j0:j0 + L] += shaker[:L] * (0.5 if half else 0.7)
        tb += beat; kb += 1
    out = sosfilt(butter(2, [45, 9000], "bandpass", fs=SR, output="sos"), out, axis=1)
    lift = np.clip((t - t_lift) / 1.5, 0, 1) * 0.35 + 0.65                                # louder after the lift
    out *= lift
    out /= np.abs(out).max() + 1e-9; out *= 0.8
    wavfile.write(path, SR, out.T.astype(np.float32))

def _kick(sr, f0=50, f1=110, dec=0.14, amp=0.5):
    t = np.arange(int(0.4 * sr)) / sr
    return np.sin(2 * np.pi * np.cumsum(f0 + f1 * np.exp(-t / 0.03)) / sr) * np.exp(-t / dec) * amp

def _noise_hit(sr, lo, hi, dec, amp, rng, body=0.0, bf=190):
    n = int(0.3 * sr); t = np.arange(n) / sr
    nz = sosfilt(butter(2, [lo, hi], "bandpass", fs=sr, output="sos"), rng.standard_normal(n))
    return (nz * np.exp(-t / dec) + body * np.sin(2 * np.pi * bf * t) * np.exp(-t / 0.05)) * amp

def _add(out, x, t, gain=1.0, pan=0.0):
    i0 = int(t * SR)
    if i0 >= out.shape[1] or i0 < 0:
        return
    L = min(len(x), out.shape[1] - i0)
    out[0, i0:i0 + L] += x[:L] * gain * (1 - pan) / 2 * 2 ** 0.5
    out[1, i0:i0 + L] += x[:L] * gain * (1 + pan) / 2 * 2 ** 0.5

def music_lofi(path, dur, t_lift):
    """Trial A: lo-fi groove all the way through. 82 BPM, swung hats, boom-bap kick/snare, electric-piano
    7th chords (Am7 Fmaj7 Cmaj7 G6), round bass, a little vinyl crackle; on the lift a soft lead melody."""
    rng = np.random.default_rng(5); n = int(dur * SR) + 1; out = np.zeros((2, n))
    f = lambda m: 440 * 2 ** ((m - 69) / 12)
    beat = 60 / 82; bar = 4 * beat
    chords = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 64]]
    def ep(m, L):                                    # electric piano: sine + bell partial, tremolo, soft decay
        t = np.arange(int(L * SR)) / SR
        return ((np.sin(2 * np.pi * f(m) * t) + 0.18 * np.sin(2 * np.pi * f(m) * 4 * t) * np.exp(-t / 0.3))
                * np.exp(-t / 1.6) * (1 + 0.15 * np.sin(2 * np.pi * 5 * t)) * np.minimum(1, t / 0.005))
    kick, snare = _kick(SR, amp=0.55), _noise_hit(SR, 1200, 6000, 0.08, 0.22, rng, body=0.5)
    hat = _noise_hit(SR, 7000, 11000, 0.02, 0.10, rng)
    k = 0; t0 = 0.0
    while t0 < dur:
        ch = chords[k % 4]
        for j, m in enumerate(ch):
            _add(out, ep(m, bar + 0.4), t0 + 0.012 * j, 0.10, -0.3 + 0.2 * j)
            _add(out, ep(m, 1.2), t0 + 2.5 * beat + 0.012 * j, 0.06, 0.2 - 0.15 * j)
        tb = np.arange(int((bar + 0.2) * SR)) / SR
        bass = np.sin(2 * np.pi * f(ch[0] - 24) * tb) * np.minimum(1, tb / 0.01) * np.exp(-tb / 2.5) * 0.30
        _add(out, bass, t0)
        for bt, w in ((0, 1), (1.5, 0.7), (2.5, 0.8)):
            _add(out, kick, t0 + bt * beat, w)
        for bt in (1, 3):
            _add(out, snare, t0 + bt * beat, 1.0, 0.1)
        for e8 in range(8):
            sw = 0.09 * beat if e8 % 2 else 0.0     # swing
            _add(out, hat, t0 + e8 * beat / 2 + sw, 0.8 if e8 % 2 else 1.0, 0.35)
        if t0 + bar > t_lift:                      # lift: a simple lead line
            for j, m in enumerate([ch[3] + 12, ch[2] + 12, ch[1] + 12, ch[2] + 12]):
                ts = t0 + j * beat
                if ts >= t_lift:
                    _add(out, ep(m, 0.9), ts, 0.07, 0.25)
        t0 += bar; k += 1
    crackle = (rng.random(n) > 0.9993) * rng.standard_normal(n) * 0.25
    crackle = sosfilt(butter(2, 2500, "highpass", fs=SR, output="sos"), crackle)
    out += crackle * 0.4
    out = sosfilt(butter(2, [40, 11000], "bandpass", fs=SR, output="sos"), out, axis=1)
    out /= np.abs(out).max() + 1e-9; out *= 0.85
    wavfile.write(path, SR, out.T.astype(np.float32))

def music_pop(path, dur, t_lift, t_chart):
    """Trial B: upbeat pop bed. 104 BPM, soft four-on-the-floor kick, claps on 2 and 4, open hats on the off-beats,
    plucky filtered-saw arpeggio (Am F C G), sub bass; a riser into the chart; brighter octave on the lift."""
    rng = np.random.default_rng(9); n = int(dur * SR) + 1; out = np.zeros((2, n))
    f = lambda m: 440 * 2 ** ((m - 69) / 12)
    beat = 60 / 104; bar = 4 * beat
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
    def pluck(m, L=0.35, bright=1.0):
        t = np.arange(int(L * SR)) / SR
        saw = 2 * ((f(m) * t) % 1) - 1
        lp = sosfilt(butter(2, min(9000, 1800 + 3000 * bright), "lowpass", fs=SR, output="sos"), saw)
        return lp * np.exp(-t / 0.12) * np.minimum(1, t / 0.003)
    kick = _kick(SR, 45, 120, 0.11, 0.6)
    clap = _noise_hit(SR, 900, 4000, 0.05, 0.22, rng)
    ohat = _noise_hit(SR, 6000, 12000, 0.06, 0.07, rng)
    k = 0; t0 = 0.0
    while t0 < dur:
        ch = chords[k % 4]; lift = t0 >= t_lift - 0.01
        for bt in range(4):
            _add(out, kick, t0 + bt * beat, 0.9)
            _add(out, ohat, t0 + (bt + 0.5) * beat, 1.0, 0.3)
        for bt in (1, 3):
            _add(out, clap, t0 + bt * beat, 1.0, -0.15)
        for s16 in range(16):
            m = ch[s16 % 3] + (12 if (s16 // 3) % 2 else 0) + (12 if lift else 0)
            _add(out, pluck(m, bright=1.4 if lift else 1.0), t0 + s16 * beat / 4, 0.09, -0.35 + 0.7 * ((s16 % 4) / 3))
        tb = np.arange(int(bar * SR)) / SR
        _add(out, np.sin(2 * np.pi * f(ch[0] - 24) * tb) * np.minimum(1, tb / 0.01) * np.minimum(1, (bar - tb) / 0.05) * 0.28, t0)
        t0 += bar; k += 1
    # riser (filtered noise swelling for 1.6 s) into the chart
    L = int(1.6 * SR); t = np.arange(L) / SR
    nz = sosfilt(butter(2, [2000, 9000], "bandpass", fs=SR, output="sos"), rng.standard_normal(L)) * (t / 1.6) ** 2 * 0.25
    _add(out, nz, max(0, t_chart - 1.6))
    out = sosfilt(butter(2, [35, 13000], "bandpass", fs=SR, output="sos"), out, axis=1)
    out /= np.abs(out).max() + 1e-9; out *= 0.85
    wavfile.write(path, SR, out.T.astype(np.float32))

# ------------------------------------------------------------------ main
def main():
    global POP_IN, POP_OUT, CH_IN, CH_OUT, P, B, SIND
    if "--project" in sys.argv:                       # trial versions live in their own project folders
        P = (Path.cwd() / sys.argv[sys.argv.index("--project") + 1]).resolve(); B = P / "build"
    B.mkdir(exist_ok=True)
    edit = json.loads((P / "edit.json").read_text(encoding="utf-8"))
    var = VARIANTS[edit.get("_variant", "final")]
    SIND = var["india"]
    starts, acc = [], 0.0
    for c in edit["clips"]:
        starts.append(acc); acc += (c["out"] - c["in"]) / c.get("speed", 1.0)
    cue = {c.get("_cue"): starts[i] for i, c in enumerate(edit["clips"]) if c.get("_cue")}
    CH_IN, CH_OUT = cue["chart"] + 0.08, cue["chart_end"]
    POP_IN, POP_OUT = cue["logo"] + 0.05, cue["logo_end"]
    chart_clip(); popup_clip()
    if var["music"] == "lofi":
        music_lofi(str(B / "music.wav"), acc + 0.5, cue["lift"])
    elif var["music"] == "pop":
        music_pop(str(B / "music.wav"), acc + 0.5, cue["lift"], CH_IN)
    else:
        music(str(B / "music.wav"), acc + 0.5, cue["lift"])
    # write the overlay/sfx timing back into edit.json
    edit["overlays"] = [{"src": "build/chart.mov", "at": round(CH_IN, 3), "x": CH_X - 4, "y": CH_Y - 4},
                        {"src": "build/logo.mov", "at": round(POP_IN, 3), "x": CARD_X - 4, "y": CARD_Y - 4}]
    sfx = [{"src": "../../sfx_library/msg_soft_pop.mp3", "at": round(POP_IN, 3), "gain_db": -14},
           {"src": "../../sfx_library/msg_soft_pop.mp3", "at": round(CH_IN, 3), "gain_db": -16}]
    for i, c in enumerate(edit["clips"]):              # a quiet air whoosh where the room/setting changes
        if c.get("_whoosh") and starts[i] > 0.3:
            sfx.append({"src": "../../sfx_library/dl_2026_11/swoosh_short_wind.mp3", "at": round(starts[i] - 0.18, 3),
                        "gain_db": -21})
    edit["sfx"] = sfx
    (P / "edit.json").write_text(json.dumps(edit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"reel {acc:.2f}s · chart {CH_IN:.2f}-{CH_OUT:.2f} · logo {POP_IN:.2f}-{POP_OUT:.2f} · lift {cue['lift']:.2f}")

if __name__ == "__main__":
    main()
