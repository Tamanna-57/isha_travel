"""Original music bed for the safari reel (numpy, no licensing issues). Writes build/music.wav (48 kHz stereo).
Story arc on the FINAL timeline (source minus 0.07 s; minus 1.47 s after the 33.83 cut):
  0.29 - 8.99   A: tanpura drone (D) + santoor-ish pluck ostinato in D minor pentatonic, soft frame-drum pulse. Mystery.
  8.99          "everything will go SILENT" -> the music stops dead. Silence carries the alarm call + tiger reveal.
  16.54 - 30.08 B: back in on "No reel will ever..." - drone, warm pad (D major colour), pluck, light drums.
  28.7 - 30.08  swell into the Lost & Free reveal
  30.08 - end   C: full groove, pluck melody; final D chord at 35.5 rings under "...first to know"."""
import sys
from pathlib import Path
import numpy as np
from scipy.io import wavfile
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lakshadweep_v2"))
import synth as S                      # instruments from the Lakshadweep bed (ep_note, pad_chord, bass_note, kick, ...)
from synth import add, reverb, lp, hp, bp, mtof, pluck, pad_chord, bass_note, kick, shaker, env_adsr

SR = 48000
DUR = 35.93                           # v5: 0.37 s pause cut at 18.53
N = int(DUR * SR)
rng = np.random.default_rng(11)
DROP, RETURN, LOGO = 8.99, 16.54, 30.08 - 0.3667   # v5: logo moved up by the pause cut
BAR = (LOGO - RETURN) / 5            # 2.708 s -> 88.6 BPM; downbeats land on RETURN and LOGO
BEAT = BAR / 4
T0 = RETURN - 6 * BAR                 # 0.29: first downbeat, right on her first word
FINAL = LOGO + 2 * BAR                # 35.50

def tanpura(m, dur, vel=1.0):
    """plucked drone string: rich harmonics, a 'jawari' brightness bump that slowly travels up the partials"""
    f = mtof(m)
    n = int((dur + 1.5) * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    centre = 3 + 9 * (1 - np.exp(-t * 1.2))          # buzzing formant moves from harmonic 3 -> 12
    for k in range(1, 22):
        if f * k > 9000:
            break
        a = k ** -0.9 * (1 + 1.6 * np.exp(-((k - centre) ** 2) / 6))
        x += a * np.sin(2 * np.pi * f * k * t * (1 + 0.0004 * k) + rng.random() * 6.28)
    x *= np.minimum(1, t / 0.015) * np.exp(-t * 0.45)
    return lp(x, 6000) * vel * 0.035

def santoor(m, vel=1.0):
    """hammered string: pluck + slightly inharmonic metallic shimmer, two detuned strings"""
    f = mtof(m)
    n = int(1.8 * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for d in (-0.0015, 0.0015):
        ff = f * (1 + d)
        x += (np.sin(2 * np.pi * ff * t) + 0.5 * np.sin(2 * np.pi * ff * 2.003 * t) * np.exp(-t * 4)
              + 0.25 * np.sin(2 * np.pi * ff * 3.01 * t) * np.exp(-t * 7) + 0.12 * np.sin(2 * np.pi * ff * 4.2 * t) * np.exp(-t * 12))
    x *= np.exp(-t * 3.2) * np.minimum(1, t / 0.002)
    return x * vel * 0.045

def frame_drum(low=True):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = (62 if low else 140) + (60 if low else 120) * np.exp(-t * 25)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (7 if low else 14))
    skin = bp(rng.standard_normal(n), 300, 2500) * np.exp(-t * 40) * 0.25
    return (body + skin) * np.minimum(1, t / 0.002) * (0.45 if low else 0.22)

MINPENT = [62, 65, 67, 69, 72, 74, 77, 79]           # D F G A C (mystery, section A)
MAJ = [62, 64, 66, 69, 71, 74, 76, 78]               # D E F# A B (warm, B/C)
PROG = [(38, [54, 57, 61, 64]), (35, [54, 57, 61, 62]), (31, [54, 57, 59, 62]), (33, [52, 55, 59, 62])]  # Dmaj9 Bm9 Gmaj9 A9sus4

def music():
    drone = np.zeros((N, 2)); bed = np.zeros((N, 2)); top = np.zeros((N, 2)); drums = np.zeros((N, 2))
    nb = int((DUR - T0) / BAR) + 2
    for i in range(-1, nb):
        bt = T0 + i * BAR
        if bt > FINAL + 1e-6:
            break
        sec = "A" if bt < DROP else ("X" if bt < RETURN - 1e-6 else ("B" if bt < LOGO - 1e-6 else "C"))
        if sec == "X":
            continue
        final = abs(bt - FINAL) < 1e-3
        # tanpura cycle Pa Sa Sa Sa(low) across the bar
        for b, m in ((0, 45), (1, 50), (2, 50), (3, 38)):
            add(drone, tanpura(m, BEAT * 1.6, 0.9 if b else 1.0), bt + b * BEAT, 1.0, -0.3 + 0.2 * b)
        if final:
            root, voicing = PROG[0]
            add(bed, pad_chord(voicing, BAR * 1.2), bt, 1.3, 0)
            add(bed, bass_note(root + 12, BAR * 0.9), bt, 1.0, 0)
            for k, m in enumerate([62, 66, 69, 74, 78]):
                add(top, santoor(m, 0.9), bt + k * 0.05, 1.0, -0.4 + 0.2 * k)
            add(drums, frame_drum(True), bt, 0.9)
            continue
        if sec == "A":
            scale, pat, vel = MINPENT, [0, 3, 2, 4, 3, 1, 2, 0], 0.75
        else:
            scale, pat, vel = MAJ, ([0, 2, 4, 3, 5, 4, 2, 3] if sec == "C" else [0, 3, 2, 4, 1, 3, 2, 4]), 0.85
            root, voicing = PROG[(i - 6) % 4]
            add(bed, pad_chord(voicing, BAR), bt, 0.9 if sec == "B" else 1.1, 0)
            add(bed, bass_note(root + 12, BEAT * 1.6), bt, 0.9, 0)
            if sec == "C":
                add(bed, bass_note(root + 12, BEAT * 1.0), bt + 2.5 * BEAT, 0.7, 0)
        for e, p in enumerate(pat):
            add(top, santoor(scale[p], vel * (1.0 if e % 2 == 0 else 0.7)), bt + e * BEAT / 2 + 0.006 * rng.standard_normal(),
                1.0, 0.35 if e % 2 else -0.35)
        # percussion: section A from the 2nd bar (soft), B light, C fuller
        if (sec == "A" and i >= 1) or sec in "BC":
            g = {"A": 0.5, "B": 0.55, "C": 1.0}[sec]
            for b in ((0, 2.5) if sec != "C" else (0, 1.5, 2, 3.5)):
                add(drums, frame_drum(True), bt + b * BEAT, g)
            for b in (1, 3):
                add(drums, frame_drum(False), bt + b * BEAT, g * 0.8, 0.2)
            if sec == "C":
                for e in range(8):
                    add(drums, shaker(1.0 if e % 2 else 0.5), bt + e * BEAT / 2, 0.8, 0.35)
    t = np.arange(N) / SR
    g = np.ones(N)
    g[t < LOGO] = 0.55                                   # under the voice (sidechain ducks it further)
    g[t < DROP] = 0.95                                   # section A is sparse (no pad), lift it to sit ~20 dB under
    g[(t >= LOGO - 1.4) & (t < LOGO)] = np.linspace(0.55, 0.70, ((t >= LOGO - 1.4) & (t < LOGO)).sum())
    g[t >= LOGO] = 0.62
    cut = (t >= DROP - 0.04) & (t < DROP + 0.12)          # hard but click-free stop on "silent"
    g[cut] *= np.linspace(1, 0, cut.sum()) ** 2
    g[(t >= DROP + 0.12) & (t < RETURN)] = 0
    back = (t >= RETURN - 0.02) & (t < RETURN + 0.6)      # bloom back in
    g[back] *= np.linspace(0.3, 1, back.sum())
    g[t < 0.06] *= np.linspace(0, 1, (t < 0.06).sum())
    g[t > DUR - 0.5] *= np.linspace(1, 0, (t > DUR - 0.5).sum())
    drone = reverb(drone, 2.4, 0.35); bed = reverb(bed, 2.2, 0.3); top = reverb(top, 2.4, 0.38)
    d = int(BEAT * 0.75 * SR)
    top[d:, 0] += 0.3 * top[:-d, 1]; top[d:, 1] += 0.3 * top[:-d, 0]
    drums = reverb(drums, 0.9, 0.15)
    mix = (drone * 0.9 + bed + top + drums * 0.9) * g[:, None]
    # riser into the logo (reverse-swell noise, tonal) lives in the music so it ducks with it
    rl = int(1.38 * SR); i0 = int((LOGO - 1.38) * SR)
    sw = (hp(rng.standard_normal(rl), 2500) * 0.25 + tanpura(57, 1.4, 0.8)[:rl] * 3) * (np.arange(rl) / rl) ** 2.5 * 0.5
    mix[i0:i0 + rl] += sw[:, None]
    # tidy: sharp stop must stay sharp, so the silence is re-zeroed after the reverb tails
    mix[(t >= DROP + 0.12) & (t < RETURN - 0.02)] *= 0
    for ch in range(2):
        mix[:, ch] = hp(lp(mix[:, ch], 11000), 40)
    mix[(t >= DROP + 0.14) & (t < RETURN - 0.02)] = 0
    return mix

if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "build"
    m = music()
    pk = np.abs(m).max()
    wavfile.write(out / "music.wav", SR, (m / pk * 0.89).astype(np.float32))
    print(f"music.wav peak {pk:.3f} len {len(m) / SR:.2f}s  BAR {BAR:.3f} ({240 / BAR:.1f} BPM) T0 {T0:.2f}")
