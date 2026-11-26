"""End-card SFX for W1-T2b: bubbles under the last water shot, then peacock + deep whoosh into the jungle card."""
import subprocess
from pathlib import Path
P = Path(__file__).resolve().parent
L = P.parent.parent / "sfx_library"
DUR, CARD = 34.70 - 0.067, 2.60
HITS = [  # (file, src_start, dur, at, gain_db)
    (L / "bubbles_deep.mp3", 0.0, 1.6, DUR - 1.5, -20),
    (L / "dl_2026_11" / "impact_whoosh_deep.mp3", 0.2, 1.8, DUR - 0.12, -15),
    (L / "dl_safari" / "peacock_call.ogg", 0.0, 2.2, DUR + 0.3, -14),
    (L / "dl_2026_11" / "pop_hard_click.mp3", 0.0, 0.5, DUR + 0.6, -16),
]
inp, fc = [], []
for i, (f, ss, d, at, g) in enumerate(HITS):
    inp += ["-ss", f"{ss}", "-t", f"{d}", "-i", str(f)]
    ms = int(at * 1000)
    fc.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,afade=out:st={max(0, d - 0.3)}:d=0.3,volume={g}dB,adelay={ms}|{ms}[s{i}]")
fc.append("".join(f"[s{i}]" for i in range(len(HITS))) + f"amix=inputs={len(HITS)}:normalize=0,apad,atrim=0:{DUR + CARD + 0.3}[o]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(fc), "-map", "[o]", "-ar", "48000", str(P / "sfx_bed.wav")], check=True)
print("sfx_bed.wav")
