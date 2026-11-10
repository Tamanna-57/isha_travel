"""Original festive music bed for the Bhai Dooj reel, synthesised in numpy (no licensing issues).

Instruments (all synthetic): tanpura drone (Sa-Pa), santoor (Karplus-Strong double strings with tremolo),
dholak (kaherwa theka), manjira chings, a temple bell, soft claps in the finale. Key D, raag Khamaj flavour, 100 BPM.

Arc (times come from edit.json via prep.py):
  0          temple bell + santoor alone (her hook "Aaj Bhai Dooj")
  t_groove   dholak + manjira enter on the first cut
  t_soft     "Thank you..." -> dholak drops out, santoor + drone only (keep the emotion)
  t_final    "Happy Bhai Dooj!" -> bell, dholak + claps back, rings out to the end
Writes 48 kHz stereo float WAV.
"""
import sys
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
rng = np.random.default_rng(11)

def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)

def env_exp(n, tau):
    return np.exp(-np.arange(n) / (tau * SR))

def ks_pluck(freq, dur, bright=0.6, decay=0.996):
    """Karplus-Strong string: santoor-like when bright and short"""
    n = int(dur * SR); p = max(2, int(round(SR / freq)))
    buf = rng.uniform(-1, 1, p) * bright + np.sin(2 * np.pi * np.arange(p) / p) * (1 - bright)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = decay * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    att = np.minimum(1, np.arange(n) / (0.002 * SR))
    return out * att

_cache = {}
def santoor(m, dur=1.4, vel=1.0):
    key = (m, dur)
    if key not in _cache:
        f = mtof(m)
        a = ks_pluck(f, dur, 0.75, 0.9965) + 0.8 * ks_pluck(f * 1.0035, dur, 0.7, 0.9962)   # two detuned strings
        _cache[key] = a / (np.abs(a).max() + 1e-9)
    return _cache[key] * vel

def bell(f0=523.0, dur=4.0):
    n = int(dur * SR); t = np.arange(n) / SR
    out = np.zeros(n)
    for r, a, tau in [(0.5, 0.5, 2.5), (1.0, 1.0, 1.8), (2.0, 0.6, 1.1), (2.76, 0.45, 0.9), (5.4, 0.25, 0.5), (8.93, 0.12, 0.3)]:
        out += a * np.sin(2 * np.pi * f0 * r * t + rng.uniform(0, 6)) * np.exp(-t / tau) * (1 + 0.003 * np.sin(2 * np.pi * 4 * t))
    return out * np.minimum(1, t / 0.003) / 2.2

def dholak_bass(vel=1.0, dur=0.45):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 75 + 95 * np.exp(-t / 0.04)                     # pitch drop of the bass head
    ph = 2 * np.pi * np.cumsum(f) / SR
    return vel * np.sin(ph) * np.exp(-t / 0.16) * np.minimum(1, t / 0.002)

def dholak_high(vel=1.0, dur=0.25, tone=410):
    n = int(dur * SR); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * tone * t) * np.exp(-t / 0.05) + 0.5 * np.sin(2 * np.pi * tone * 1.52 * t) * np.exp(-t / 0.03)
    slap = sosfilt(butter(2, [1500, 6000], "bandpass", fs=SR, output="sos"), rng.standard_normal(n)) * np.exp(-t / 0.012)
    return vel * (0.8 * body + 0.35 * slap) * np.minimum(1, t / 0.001)

def manjira(vel=1.0, dur=0.9, open_=True):
    n = int(dur * SR); t = np.arange(n) / SR
    out = np.zeros(n)
    for f, a in [(2630, 1), (3910, 0.8), (5320, 0.6), (7140, 0.4), (9050, 0.25)]:
        out += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6))
    tau = 0.35 if open_ else 0.04
    hiss = sosfilt(butter(2, 6000, "highpass", fs=SR, output="sos"), rng.standard_normal(n)) * 0.06
    return vel * (out / 3 + hiss) * np.exp(-t / tau) * 0.8 * np.minimum(1, t / 0.0015)

def clap(vel=1.0, dur=0.2):
    n = int(dur * SR); t = np.arange(n) / SR
    nz = sosfilt(butter(2, [900, 4000], "bandpass", fs=SR, output="sos"), rng.standard_normal(n))
    e = np.exp(-t / 0.03) + 0.6 * np.exp(-np.maximum(0, t - 0.012) / 0.02) * (t > 0.012)
    return vel * nz * e

def tanpura(dur, root=50):
    """Pa-Sa-Sa-Sa' plucks with buzzy harmonics, every 2.4 s"""
    n = int(dur * SR); out = np.zeros(n)
    notes = [root + 7 - 12, root, root, root - 12]
    t0, k = 0.0, 0
    while t0 < dur:
        f = mtof(notes[k % 4]); ln = int(min(3.2, dur - t0) * SR); t = np.arange(ln) / SR
        s = np.zeros(ln)
        for h in range(1, 14):
            s += (1 / h) * np.sin(2 * np.pi * f * h * t) * (0.5 + 0.5 * np.sin(2 * np.pi * (0.3 + 0.05 * h) * t + h)) ** 2
        s *= np.exp(-t / 2.2) * np.minimum(1, t / 0.01)
        i = int(t0 * SR); out[i:i + ln] += s[: n - i]
        t0 += 0.6; k += 1
    return out / (np.abs(out).max() + 1e-9)

def place(buf, x, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= buf.shape[1] or i < 0:
        return
    seg = x[: buf.shape[1] - i] * gain
    buf[0, i:i + len(seg)] += seg * np.sqrt(0.5 * (1 - pan))
    buf[1, i:i + len(seg)] += seg * np.sqrt(0.5 * (1 + pan))

def main(out, dur, t_groove, t_soft, t_final):
    n = int(dur * SR) + 1
    mix = np.zeros((2, n))
    BPM = 100; BEAT = 60 / BPM; E = BEAT / 2           # eighth note
    t_end = dur - 1.3                                  # drums and motif stop here; a last strum rings out
    # grid anchored so a bar starts exactly on the final "Happy Bhai Dooj"
    bars_before = int(np.ceil(t_final / (4 * BEAT)))
    t0 = t_final - bars_before * 4 * BEAT

    # tanpura bed, soft, whole reel
    place(mix, tanpura(dur) * 0.16, 0.0)

    # temple bells
    place(mix, bell(523.0, 4.0) * 0.55, 0.0, pan=-0.2)
    place(mix, bell(587.0, 4.0) * 0.6, t_final, pan=0.2)

    # santoor: raag Khamaj-ish motif in D. Chord per bar: D, G, C (komal Ni), D
    D = 62
    motifs = [
        [D, D + 4, D + 7, D + 9, D + 7, D + 4, D + 2, D + 4],          # D F# A B A F# E F#
        [D + 5, D + 9, D + 12, D + 9, D + 7, D + 5, D + 4, D + 2],     # G B D' B A G F# E
        [D + 10, D + 9, D + 7, D + 5, D + 4, D + 5, D + 7, D + 4],     # C' B A G F# G A F#
        [D + 2, D + 4, D + 2, D, D - 3, D, D + 4, D],                  # E F# E D B, D F# D
    ]
    bar = 0; t = t0
    while t < dur:
        mot = motifs[bar % 4]
        soft = t_soft <= t < t_final
        for k, m in enumerate(mot):
            tt = t + k * E
            if tt < 0 or tt >= t_end:
                continue
            vel = (0.55 if k % 2 == 0 else 0.4) * (0.75 if soft else 1.0)
            if soft and k % 2 == 1:
                continue                                                # half the notes in the emotional part
            place(mix, santoor(m, 1.4, vel), tt, pan=-0.25 + 0.1 * (k % 3))
            if not soft and k in (3, 7) and tt >= t_groove:            # festive tremolo flourish
                for r in (1, 2):
                    place(mix, santoor(m, 0.5, vel * 0.45), tt + r * E / 3, pan=-0.2)
        # low santoor root on the downbeat
        if t < t_end:
            place(mix, santoor(mot[0] - 12, 1.6, 0.35 * (0.8 if soft else 1)), t, pan=0.0)
        t += 4 * BEAT; bar += 1

    # dholak kaherwa: Dha Ge Na Ti | Na Ka Dhi Na  (eighths)
    theka = [("B", 1.0, "H", 0.7), ("B", 0.5, None, 0), (None, 0, "H", 0.8), (None, 0, "h", 0.4),
             (None, 0, "H", 0.75), ("B", 0.35, "s", 0.6), ("B", 0.85, "H", 0.65), (None, 0, "H", 0.7)]
    t = t0; k = 0
    while t < dur:
        if t >= t_groove - 1e-3 and not (t_soft <= t < t_final) and t < t_end:
            b, bv, h, hv = theka[k % 8]
            g = 1.0 if t >= t_final else 0.85
            if b:
                place(mix, dholak_bass(bv * g), t, 0.9, pan=0.05)
            if h == "H":
                place(mix, dholak_high(hv * g), t, 0.55, pan=0.15)
            elif h == "h":
                place(mix, dholak_high(hv * g, tone=450), t, 0.45, pan=0.15)
            elif h == "s":
                place(mix, dholak_high(hv * g, tone=330), t, 0.5, pan=0.1)
            if k % 4 == 2:                                              # manjira on the off-beat of beats 1 and 3
                place(mix, manjira(0.5 * g, open_=(k % 8 == 2)), t, 0.2, pan=-0.35)
            if t >= t_final and k % 4 == 2:
                place(mix, clap(0.9), t, 0.5, pan=0.3)
        t += E; k += 1

    # ending: one soft D-major santoor strum + low root, left to ring
    for k, m in enumerate([D - 12, D, D + 4, D + 7, D + 12, D + 16]):
        place(mix, santoor(m, 2.4, 0.5 if k else 0.4), t_end + 0.06 * k, pan=-0.3 + 0.12 * k)
    place(mix, bell(587.0, 3.0) * 0.3, t_end, pan=0.2)

    # gentle low-cut + soft master
    mix = sosfilt(butter(2, 45, "highpass", fs=SR, output="sos"), mix, axis=1)
    mix = np.tanh(1.3 * mix / (np.abs(mix).max() + 1e-9)) / np.tanh(1.3)
    mix *= 0.89
    wavfile.write(out, SR, mix.T.astype(np.float32))
    print(f"music: {dur:.2f}s -> {out}")

if __name__ == "__main__":
    out, dur, a, b, c = sys.argv[1], *map(float, sys.argv[2:6])
    main(out, dur, a, b, c)
