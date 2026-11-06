"""Original music bed + sound effects for the Lakshadweep reel, synthesised in numpy (no licensing issues).
Writes build/music.wav and build/sfx.wav (48 kHz stereo float32), both exactly DUR seconds long.

Music arc (follows the story):
  0.0 - 27.45   warm lo-fi bed under the voice (EP chords, pad, soft kick/shaker)
  27.45         "aur ek silence"  -> everything drops out, only her voice
  29.4 - 30.47  reverse swell back in
  30.47 - end   music-led outro, full arrangement + pluck melody, resolves on D and rings out
"""
import numpy as np
from pathlib import Path
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR = 48000
DUR = 39.133
N = int(DUR * SR)
OUT = Path(__file__).parent / "build"
rng = np.random.default_rng(7)

BPM = 100
BEAT = 60 / BPM
BAR = 4 * BEAT
DROP_T = 27.45          # music cuts out ("aur ek silence")
OUTRO_T = 30.467        # downbeat of the outro = the cut to the goat shot
T0 = OUTRO_T - 13 * BAR  # grid anchored so a bar starts exactly on the outro cut
END_T = OUTRO_T + 3 * BAR  # final D chord

def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)

def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)

def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x)

def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)

def add(buf, sig, t, gain=1.0, pan=0.0):
    """mix mono sig into stereo buf at time t (equal-power pan -1..1)"""
    i = int(round(t * SR))
    if i >= len(buf):
        return
    j0 = max(0, -i)
    sig = sig[j0:]
    i = max(0, i)
    n = min(len(sig), len(buf) - i)
    if n <= 0:
        return
    a = (pan + 1) * np.pi / 4
    buf[i:i + n, 0] += sig[:n] * gain * np.cos(a)
    buf[i:i + n, 1] += sig[:n] * gain * np.sin(a)

def reverb(stereo, seconds=1.8, wet=0.25, predelay=0.02, tone=5000):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    out = stereo.copy()
    for ch in range(2):
        ir = rng.standard_normal(n) * np.exp(-t * 6.9 / seconds)
        ir = lp(ir, tone)
        ir = np.concatenate([np.zeros(int(predelay * SR)), ir])
        ir /= np.sqrt((ir ** 2).sum())
        out[:, ch] = stereo[:, ch] * (1 - wet) + fftconvolve(stereo[:, ch], ir)[:len(stereo)] * wet * 1.4
    return out

def env_adsr(n, a=0.005, d=0.0, s=1.0, r=0.05):
    e = np.ones(n) * s
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr and nr < n:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e

# ------------------------------------------------------------------ instruments
def ep_note(m, dur, vel=1.0):
    """electric-piano-ish tone: decaying harmonics + a short bell 'tine'"""
    f = mtof(m)
    n = int((dur + 1.2) * SR)
    t = np.arange(n) / SR
    amps = [1, 0.55, 0.32, 0.18, 0.10, 0.06, 0.04]
    x = sum(a * np.sin(2 * np.pi * f * (k + 1) * t) * np.exp(-t * (1.3 + 0.8 * k)) for k, a in enumerate(amps))
    x += 0.30 * np.sin(2 * np.pi * f * 7.03 * t) * np.exp(-t * 14)        # tine
    x *= 1 + 0.08 * np.sin(2 * np.pi * 4.2 * t)                           # gentle tremolo
    x *= env_adsr(n, a=0.004, r=0.4)
    off = int(dur * SR)                                                    # release after note-off
    x[off:] *= np.exp(-np.arange(n - off) / SR * 6)
    return x * vel * 0.18

def pad_chord(notes, dur):
    n = int((dur + 0.6) * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for m in notes:
        f = mtof(m)
        for det in (-0.09, 0.0, 0.11):                                     # detuned saws
            ph = (f * 2 ** (det / 12) * t + rng.random()) % 1
            x += 2 * ph - 1
    x = hp(lp(x, 2200, 2), 160) / (len(notes) * 3)
    e = np.minimum(1, t / 0.5) * np.minimum(1, np.maximum(0, (dur + 0.6 - t) / 0.6))
    return x * e * 0.16

def bass_note(m, dur):
    f = mtof(m)
    n = int((dur + 0.1) * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t) * np.exp(-t * 3)
    return x * env_adsr(n, a=0.01, r=0.12) * np.exp(-t * 0.8) * 0.20

def kick():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 45 + 80 * np.exp(-t * 30)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)
    return x * 0.55

def shaker(acc=1.0):
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    x = hp(rng.standard_normal(n), 6000) * np.exp(-t * 60) * np.minimum(1, t / 0.006)
    return x * 0.16 * acc

def snap():
    n = int(0.2 * SR)
    t = np.arange(n) / SR
    x = bp(rng.standard_normal(n), 1200, 4000) * np.exp(-t * 35) + 0.4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 40)
    return x * 0.24

def pluck(m, vel=1.0):
    f = mtof(m)
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * f * t) + 0.45 * np.sin(4 * np.pi * f * t) * np.exp(-t * 5) + 0.2 * np.sin(6 * np.pi * f * t) * np.exp(-t * 9)) * np.exp(-t * 4.5)
    return x * np.minimum(1, t / 0.003) * vel * 0.09

# chord table: (bass root, EP/pad voicing) — D major: Dmaj9 | Bm9 | Gmaj9 | A9sus4
PROG = [(38, [54, 57, 61, 64]),   # Dmaj9   (F#3 A3 C#4 E4)
        (35, [54, 57, 61, 62]),   # Bm9     (F#3 A3 C#4 D4)
        (31, [54, 57, 59, 62]),   # Gmaj9   (F#3 A3 B3 D4)
        (33, [52, 55, 59, 62])]   # A9sus4  (E3 G3 B3 D4)
SCALE_PENT = [62, 64, 66, 69, 71, 74, 76, 78]   # D major pentatonic for the outro melody

def chord_at_bar(i):
    return PROG[(i - 13) % 4]      # bar 13 (the outro downbeat) is D

# ------------------------------------------------------------------ music
def music():
    bed = np.zeros((N, 2))     # chords/pad/bass (everything tonal)
    drums = np.zeros((N, 2))
    top = np.zeros((N, 2))     # outro-only melody
    nbars = int((DUR - T0) / BAR) + 1
    for i in range(nbars):
        bt = T0 + i * BAR
        outro = bt >= OUTRO_T - 1e-6
        if bt > END_T + 1e-6:
            break
        root, voicing = chord_at_bar(i)
        if bt + BAR <= 0 and not outro:
            continue
        # skip the silence section entirely (bars that start inside it)
        if DROP_T <= bt < OUTRO_T - 1e-6:
            continue
        final = abs(bt - END_T) < 1e-6
        dur = BAR * (1.6 if final else 1.0)
        # pad
        add(bed, pad_chord(voicing, dur), bt, 1.0, 0)
        # EP: beat 1 full chord, a softer re-strike on the 'and' of 2 and on 4
        hits = [(0, 1.0, BEAT * 1.4)] if final else [(0, 1.0, BEAT * 1.4), (1.5, 0.55, BEAT * 0.9), (3, 0.65, BEAT * 0.9)]
        for b, v, d in hits:
            for k, m in enumerate(voicing):
                add(bed, ep_note(m, d, v * (0.9 + 0.1 * k)), bt + b * BEAT + k * 0.012, 1.0, -0.25 + 0.17 * k)
        # bass: beat 1 and the 'and' of 3
        add(bed, bass_note(root + 12, BEAT * 2.2 if final else BEAT * 1.4), bt, 1.0, 0)
        if not final:
            add(bed, bass_note(root + 12, BEAT * 1.2), bt + 2.5 * BEAT, 0.8, 0)
        if final:
            continue
        # drums (very light under the voice, fuller in the outro); start after the hook bar
        if bt >= T0 + BAR - 1e-6:
            dg = 1.0 if outro else 0.55
            for b in (0, 2) if not outro else (0, 1.75, 2, 2.75):
                if not outro or b in (0, 2) or rng.random() < 1:
                    add(drums, kick(), bt + b * BEAT, dg * (1 if b in (0, 2) else 0.45))
            for b in (1, 3):
                add(drums, snap(), bt + b * BEAT, dg * (0.8 if outro else 0.5), 0.15)
            for e in range(8):
                add(drums, shaker(1.0 if e % 2 else 0.55), bt + e * BEAT / 2 + 0.008 * rng.standard_normal(), dg, 0.35)
        # outro melody: rolling pentatonic 8ths drawn from chord-friendly notes
        if outro:
            pat = [0, 2, 4, 3, 5, 4, 2, 3]
            shift = {38: 0, 35: -1, 31: -2, 33: -1}[root]
            for e, p in enumerate(pat):
                m = SCALE_PENT[max(0, min(len(SCALE_PENT) - 1, p + shift + 1))]
                add(top, pluck(m, 0.8 + 0.2 * (e % 2 == 0)), bt + e * BEAT / 2, 1.0, 0.4 if e % 2 else -0.4)

    # ---- section shaping
    t = np.arange(N) / SR
    g = np.ones(N)
    g[t < OUTRO_T] = 0.42                        # bed under the voice (sidechain ducks it further)
    # drop: fast low-pass-ish fade into silence at DROP_T
    fade = (t >= DROP_T - 0.05) & (t < DROP_T + 0.45)
    g[fade] *= np.linspace(1, 0, fade.sum()) ** 2
    g[(t >= DROP_T + 0.45) & (t < OUTRO_T)] = 0
    # ending: hold the final chord, then fade the last 0.9 s
    g[t > DUR - 0.9] *= np.linspace(1, 0, (t > DUR - 0.9).sum())
    # gentle fade-in on the very first frames so it doesn't click
    g[t < 0.08] *= np.linspace(0, 1, (t < 0.08).sum())

    bed = reverb(bed, 2.2, 0.3)
    top = reverb(top, 2.6, 0.45)
    # simple ping-pong-ish delay on the melody
    d = int(BEAT * 0.75 * SR)
    top[d:, 0] += 0.35 * top[:-d, 1]
    top[d:, 1] += 0.35 * top[:-d, 0]
    drums = reverb(drums, 0.8, 0.12)
    # pumping: duck the bed slightly on each kick (lo-fi sidechain feel)
    pump = np.ones(N)
    for i in range(int((DUR - T0) / BEAT) + 1):
        bt = T0 + i * BEAT
        if i % 2 == 0 and 0 <= bt < DUR:
            j = int(bt * SR)
            k = min(N - j, int(0.35 * SR))
            pump[j:j + k] *= 1 - 0.18 * np.exp(-np.arange(k) / SR * 9)
    mix = (bed * pump[:, None] + drums + top) * g[:, None]
    # warm it up: tame harshness, keep lows tidy
    for ch in range(2):
        mix[:, ch] = hp(lp(mix[:, ch], 12000), 45)
    return mix

# ------------------------------------------------------------------ sound effects
def noise(n):
    return rng.standard_normal(n)

def sfx_ping():
    """message-received ping: two quick bell tones"""
    out = np.zeros(int(0.9 * SR))
    for f, t0, v in ((1318.5, 0.0, 0.8), (1760.0, 0.09, 1.0)):
        n = len(out) - int(t0 * SR)
        t = np.arange(n) / SR
        x = (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 20)) * np.exp(-t * 9) * np.minimum(1, t / 0.002)
        out[int(t0 * SR):] += x * v
    return out * 0.32

def sfx_whoosh(length=0.55, lo=250, hi=3500, peak=0.6):
    """band-limited noise swept up then down; loudest at 'peak' fraction of its length"""
    n = int(length * SR)
    t = np.arange(n) / SR
    x = noise(n)
    pos = t / length
    shape = np.where(pos < peak, (pos / peak) ** 2, ((1 - pos) / (1 - peak)) ** 1.5)
    # time-varying filter approximated by crossfading 6 static band-passes
    centers = np.geomspace(lo, hi, 6)
    sweep = np.where(pos < peak, pos / peak, 1 - (pos - peak) / (1 - peak) * 0.6)
    y = np.zeros(n)
    for k, c in enumerate(centers):
        w = np.exp(-((sweep * 5 - k) ** 2) / 1.2)
        y += bp(x, c / 1.6, min(c * 1.6, SR / 2 - 100)) * w
    return y * shape * 0.5

def sfx_plane(length=1.6):
    n = int(length * SR)
    t = np.arange(n) / SR
    rumble = lp(noise(n), 500, 3) * 2.2
    whine = bp(noise(n), 1800, 4200) * 0.35
    shape = np.sin(np.pi * t / length) ** 2
    return (rumble + whine) * shape * 0.35

def sfx_waves(length, rate=0.17, level=0.18):
    n = int(length * SR)
    t = np.arange(n) / SR
    brown = np.cumsum(noise(n)); brown = hp(brown, 40); brown /= np.abs(brown).max() + 1e-9
    wash = lp(noise(n), 1400, 2) * 0.6 + brown * 0.8
    mod = 0.35 + 0.65 * (0.5 + 0.5 * np.sin(2 * np.pi * rate * t - 1.2)) ** 2
    fade = np.minimum(1, np.minimum(t / 0.6, (length - t) / 0.6))
    return wash * mod * fade * level

def sfx_bell():
    """bicycle bell: inharmonic metal partials, two quick strikes with a rattle"""
    n = int(1.2 * SR)
    out = np.zeros(n)
    partials = [(2093, 1.0), (3370, 0.6), (4890, 0.35), (6520, 0.2)]
    for t0, v in ((0.0, 0.8), (0.15, 1.0)):
        m = n - int(t0 * SR)
        t = np.arange(m) / SR
        x = sum(a * np.sin(2 * np.pi * f * t + rng.random()) * np.exp(-t * (4 + i * 2)) for i, (f, a) in enumerate(partials))
        x *= 1 + 0.25 * np.sin(2 * np.pi * 28 * t)       # rattle
        out[int(t0 * SR):] += x * np.minimum(1, t / 0.001) * v
    return out * 0.13

def sfx_plunge():
    """splash into the water + muffled whoosh down"""
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    splash = bp(noise(n), 500, 6000) * np.exp(-t * 9) * np.minimum(1, t / 0.01)
    under = lp(noise(n), 350, 3) * 3 * np.exp(-t * 2.2) * np.minimum(1, t / 0.08)
    return (splash * 0.5 + under * 0.6) * 0.5

def sfx_underwater(length, level=0.22):
    n = int(length * SR)
    t = np.arange(n) / SR
    brown = np.cumsum(noise(n)); brown = hp(brown, 25); brown /= np.abs(brown).max() + 1e-9
    x = lp(brown, 260, 3) * 2.5
    fade = np.minimum(1, np.minimum(t / 0.3, (length - t) / 0.5))
    return x * fade * level

def sfx_bubbles(length, density=14, level=0.11):
    n = int(length * SR)
    out = np.zeros(n)
    k = int(length * density)
    for _ in range(k):
        t0 = rng.random() * (length - 0.06)
        d = 0.02 + 0.04 * rng.random()
        m = int(d * SR)
        tt = np.arange(m) / SR
        f0 = 350 + 900 * rng.random()
        f = f0 * (1 + 2.2 * tt / d)                         # rising chirp = bubble
        b = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / d) ** 2
        i = int(t0 * SR)
        out[i:i + m] += b * (0.4 + 0.6 * rng.random())
    return out * level

def sfx_riser(length=1.1):
    """reverse-cymbal style swell"""
    n = int(length * SR)
    t = np.arange(n) / SR
    x = hp(noise(n), 3000) * 0.6 + bp(noise(n), 800, 3000) * 0.3
    shape = (t / length) ** 3
    return x * shape * 0.32

def sfx_boom():
    n = int(2.0 * SR)
    t = np.arange(n) / SR
    f = 38 + 50 * np.exp(-t * 8)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    air = lp(noise(n), 2500) * np.exp(-t * 5) * 0.25
    return (sub + air) * np.minimum(1, t / 0.004) * 0.45

def sfx_shimmer(notes=(86, 90, 93, 98), gap=0.07, level=0.07):
    n = int(2.5 * SR)
    out = np.zeros(n)
    for k, m in enumerate(notes):
        f = mtof(m)
        i = int(k * gap * SR)
        t = np.arange(n - i) / SR
        out[i:] += (np.sin(2 * np.pi * f * t) + 0.2 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t * 8)) * np.exp(-t * 2.6) * np.minimum(1, t / 0.002)
    return out * level

def sfx():
    b = np.zeros((N, 2))
    add(b, sfx_ping(), 1.30, 1.0, 0.1)                      # WhatsApp chat on screen
    add(b, sfx_whoosh(0.5, 300, 4000, 0.65), 5.167 - 0.33, 0.55, -0.2)   # into the airport
    add(b, sfx_waves(0.9, 0.5, 0.20), 7.65, 1.0, 0)         # boat wake
    add(b, sfx_plane(1.5), 8.0, 1.0, 0.3)                   # plane tail
    add(b, sfx_waves(3.4, 0.17, 0.16), 11.2, 1.0, -0.1)     # beach + feet in the water
    add(b, sfx_bell(), 14.55, 1.0, 0.35)                     # bicycle bell
    add(b, sfx_waves(2.1, 0.25, 0.10), 19.85, 1.0, 0.1)     # on the dive boat
    add(b, sfx_whoosh(0.4, 400, 3000, 0.7), 23.433 - 0.3, 0.35, 0)
    add(b, sfx_plunge(), 23.40, 1.0, 0)                      # going under
    add(b, sfx_underwater(4.25), 23.43, 1.0, 0)              # muffled underwater bed
    add(b, sfx_bubbles(1.0, 26, 0.12), 23.75, 1.0, 0.2)      # "you breathe underwater"
    add(b, sfx_bubbles(2.5, 6, 0.08), 25.2, 1.0, -0.2)
    add(b, sfx_riser(1.05), OUTRO_T - 1.05, 1.0, 0)          # swell back in after the silence
    add(b, sfx_boom(), OUTRO_T, 1.0, 0)
    add(b, sfx_shimmer(), 32.95, 1.0, 0.2)                   # "ek random yes" over the sunset
    add(b, sfx_underwater(1.3, 0.12), 34.33, 1.0, 0)
    add(b, sfx_bubbles(1.2, 12, 0.08), 34.4, 1.0, -0.3)
    add(b, sfx_shimmer((81, 86, 88, 93), 0.09, 0.06), 37.45, 1.0, -0.2)  # final title
    b = reverb(b, 1.2, 0.18)
    return b

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    m = music()
    s = sfx()
    for name, x in (("music", m), ("sfx", s)):
        peak = np.abs(x).max()
        wavfile.write(OUT / f"{name}.wav", SR, (x / max(peak, 1e-9) * 0.89).astype(np.float32) if name == "music" else x.astype(np.float32))
        print(f"{name}.wav  peak {peak:.3f}  len {len(x) / SR:.3f}s")
