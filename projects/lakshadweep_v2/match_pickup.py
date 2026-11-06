"""Match the tone of the pickup line ("par ek dive kabhi enough nhi hoti, so stay tuned for part 2", 33.3 s -> end)
to the rest of the voice.

Measured on the draft: the pickup has +4..10 dB more low end below 300 Hz and a deep notch at 900-1600 Hz
(down to -24 dB) that the main recording doesn't have (its two halves differ by only +-4 dB there) — a different
mic / recording path. SNR inside the notch is still ~33 dB, so EQ can restore it without lifting noise.

Method: long-term average spectrum of voiced frames, main (0-32.95 s) vs pickup; iterate a smooth linear-phase FIR
correction (fine 100 Hz grid through the notch, 1/3 octave elsewhere) and apply it to the pickup only, crossfaded in
over 60 ms in the pause before "par" (cut to the sunset). Writes build/src_matched.wav, which make.py uses as the voice.
"""
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import firwin2, fftconvolve

P = Path(__file__).resolve().parent
B = P / "build"
MAIN = (0.0, 32.95)
PICK = (33.3, 38.2)
XFADE = 33.12           # gap between "milegi" (ends 32.91) and "par" (33.37)
N_FFT = 8192
PICK_GAIN_DB = 3.0      # pickup sat ~1.5 dB under the rest after the voice compressor; +3 dB in -> level

GRID = np.array(sorted(set([50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500] + list(range(600, 2700, 100)) +
                           [2900, 3150, 3500, 4000, 4500, 5000, 5650, 6300, 7100, 8000, 9000, 10000, 11200, 12500, 14000])))
EDGES = np.r_[GRID[0] / 1.12, np.sqrt(GRID[:-1] * GRID[1:]), GRID[-1] * 1.12]

def ltas(m, sr, a, b):
    s = m[int(a * sr):int(b * sr)]
    win = np.hanning(N_FFT)
    F, k = 0, 0
    for i in range(0, len(s) - N_FFT, N_FFT // 4):
        seg = s[i:i + N_FFT]
        if seg.std() > 0.012:           # voiced frames only
            F = F + np.abs(np.fft.rfft(seg * win)) ** 2
            k += 1
    fr = np.fft.rfftfreq(N_FFT, 1 / sr)
    return np.array([10 * np.log10(F[(fr >= lo) & (fr < hi)].sum() + 1e-12) for lo, hi in zip(EDGES[:-1], EDGES[1:])])

def smooth(v):
    return np.convolve(np.pad(v, 1, mode="edge"), [0.25, 0.5, 0.25], "valid")

def main():
    sr, x = wavfile.read(B / "src.wav")
    x = x.astype(np.float64)
    ref = ltas(x.mean(1), sr, *MAIN)
    f = np.r_[0, GRID, sr / 2] / (sr / 2)

    def apply(corr):
        g = 10 ** (np.r_[corr[0], corr, corr[-1]] / 20)
        h = firwin2(16383, f, g)
        return np.stack([fftconvolve(x[:, c], h, "same") for c in range(2)], 1)

    corr = np.zeros(len(GRID))
    for it in range(6):
        d = ltas(apply(corr).mean(1), sr, *PICK) - ref
        d -= np.median(d)
        corr = smooth(np.clip(corr - 0.7 * d, -10, 18))
        print(f"iter {it}: residual max {np.abs(d).max():4.1f} dB, rms {np.sqrt((d ** 2).mean()):.1f}")
    y = apply(corr) * 10 ** (PICK_GAIN_DB / 20)
    d = ltas(y.mean(1), sr, *PICK) - ref
    d -= np.median(d)
    print(f"final : residual max {np.abs(d).max():4.1f} dB, rms {np.sqrt((d ** 2).mean()):.1f}")
    t = np.arange(len(x)) / sr
    w = np.clip((t - XFADE) / 0.06, 0, 1)[:, None]
    out = x * (1 - w) + y * w
    # loudness of the pickup's speech vs the main speech (the compressor + loudnorm do the rest)
    wavfile.write(B / "src_matched.wav", sr, out.astype(np.float32))
    print("correction dB:", " ".join(f"{int(g)}:{c:+.1f}" for g, c in zip(GRID, corr)))

if __name__ == "__main__":
    main()
