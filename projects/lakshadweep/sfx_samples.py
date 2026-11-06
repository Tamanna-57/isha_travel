"""Sound-effects track built from real recordings (isha/sfx_library) -> build/sfx.wav (replaces the synth SFX).

Sources (all free for commercial use):
  Mixkit (Mixkit Sound Effects Free License): waves, motorboat, splash, whooshes, bike bell, plane, bubbles
  Pixabay (Pixabay Content License): iPhone-style message ping, scuba regulator breathing, underwater ambience
Run after synth.py (music) and before make.py --skip-base.
"""
import subprocess
from pathlib import Path
import numpy as np
from scipy.io import wavfile

import synth   # reuse the synth boom + shimmer for the outro accent

P = Path(__file__).resolve().parent
LIB = P.parent.parent / "sfx_library"
SR, DUR = 48000, 39.133
N = int(DUR * SR)

_cache = {}
def load(name):
    if name not in _cache:
        r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(LIB / name), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                           capture_output=True, check=True)
        _cache[name] = np.frombuffer(r.stdout, np.float32).reshape(-1, 2).copy()
    return _cache[name]

def place(buf, name, src_in, src_out, at, gain_db=0.0, fin=0.01, fout=0.05, align="start", pan=0.0):
    """cut src_in..src_out from a library file, normalise its peak to 0 dBFS, fade, gain, and mix at timeline `at`.
    align='peak': `at` is where the loudest moment of the cut lands (whooshes/splashes hit the cut)"""
    x = load(name)[int(src_in * SR):int(src_out * SR)].copy()
    x /= np.abs(x).max() + 1e-9
    n = len(x)
    fi, fo = max(1, int(fin * SR)), max(1, int(fout * SR))
    x[:fi] *= np.linspace(0, 1, fi)[:, None]
    x[-fo:] *= np.linspace(1, 0, fo)[:, None]
    if pan:
        a = (pan + 1) * np.pi / 4
        x[:, 0] *= np.cos(a) * 1.414
        x[:, 1] *= np.sin(a) * 1.414
    if align == "peak":
        env = np.convolve(np.abs(x).mean(1), np.ones(960) / 960, "same")
        at -= env.argmax() / SR
    i = int(round(at * SR))
    j0 = max(0, -i); i = max(0, i)
    m = min(n - j0, N - i)
    if m > 0:
        buf[i:i + m] += x[j0:j0 + m] * 10 ** (gain_db / 20)

def build():
    b = np.zeros((N, 2), np.float32)
    # 0:01.3  WhatsApp chat on screen -> iPhone message-received ping (descending two-note)
    place(b, "msg_iphone_text_received.mp3", 2.27, 3.05, 1.30, -7, fin=0.003, fout=0.25)
    # 0:05.17 cut into the airport -> fast cinematic whoosh, peak on the cut
    place(b, "whoosh_cinematic_fast.mp3", 0.3, 1.33, 5.167, -9, align="peak", fout=0.15)
    # 0:07.7  boat wake -> real motorboat + water
    place(b, "motorboat_sea.mp3", 10.0, 11.0, 7.62, -13, fin=0.08, fout=0.35)
    # 0:08.4  plane tail -> low plane flying over, swell across the shot, gone under her voice
    place(b, "plane_low_over.mp3", 0.2, 2.6, 8.05, -14, fin=0.25, fout=0.7)
    # 0:11.27 beach -> waves with birds; 0:12.67 feet in the water -> close gentle waves
    place(b, "waves_birds_beach.mp3", 4.0, 6.0, 11.20, -12, fin=0.15, fout=0.5)
    place(b, "waves_close_loop.mp3", 6.0, 8.3, 12.45, -13, fin=0.4, fout=0.6)
    # 0:14.55 cycling -> real bike bell
    place(b, "bike_bell_ring.mp3", 0.0, 1.6, 14.58, -8, fin=0.002, fout=0.6, pan=0.3)
    # 0:19.9  dive boat -> water lapping + distant boat
    place(b, "waves_small_rocks.mp3", 10.0, 12.2, 19.82, -17, fin=0.3, fout=0.5)
    # 0:23.43 going under -> jump-in splash on the cut, then underwater ambience
    place(b, "splash_jump_in.mp3", 0.0, 1.6, 23.433, -9, align="peak", fout=0.6)
    place(b, "underwater_ambience.mp3", 2.0, 6.2, 23.43, -15, fin=0.15, fout=0.4)
    # 0:23.3  "you breathe underwater" -> one real regulator breath: inhale hiss, then exhale bubbles
    place(b, "scuba_breathe_gear.mp3", 6.0, 8.7, 23.30, -10, fin=0.05, fout=0.3)
    # 0:25.2 corals / 0:26.4 fish -> soft air-tank bubbles
    place(b, "bubbles_airtank.mp3", 0.3, 2.3, 25.25, -18, fin=0.2, fout=0.4, pan=-0.2)
    # (27.43 "aur ek silence": everything stops — only her voice)
    # 0:29.4 -> 0:30.47 back in: air whoosh into the outro + the synth sub boom on the downbeat
    place(b, "whoosh_air.mp3", 0.2, 1.4, synth.OUTRO_T - 0.04, -13, align="peak", fout=0.3)
    boom = synth.sfx_boom()
    i = int(synth.OUTRO_T * SR); m = min(len(boom), N - i)
    b[i:i + m] += (boom[:m] * 0.6)[:, None].astype(np.float32)
    # 0:32.67 sunset -> soft sea + sparkle as "ek random yes" appears
    place(b, "waves_sea_loop.mp3", 3.0, 5.0, 32.62, -18, fin=0.3, fout=0.5)
    place(b, "whoosh_magic_sparkle.mp3", 0.1, 1.6, 32.90, -19, fin=0.01, fout=0.5)
    # 0:34.33 diver with flag / anemone -> exhale bubble burst + underwater bed
    place(b, "underwater_ambience.mp3", 8.0, 11.2, 34.30, -17, fin=0.1, fout=0.4)
    place(b, "scuba_diver_underwater.mp3", 2.7, 5.0, 34.45, -11, fin=0.05, fout=0.6)
    # 0:37.33 island walk -> birds + distant waves, under the final title
    place(b, "waves_birds_beach.mp3", 14.0, 15.9, 37.30, -16, fin=0.1, fout=0.8)
    place(b, "whoosh_magic_sparkle.mp3", 0.1, 1.6, 37.42, -22, fin=0.01, fout=0.5)
    return b

if __name__ == "__main__":
    b = build()
    peak = np.abs(b).max()
    if peak > 0.95:
        b *= 0.95 / peak
    wavfile.write(P / "build/sfx.wav", SR, b.astype(np.float32))
    print(f"sfx.wav from real recordings, peak {peak:.2f}")
