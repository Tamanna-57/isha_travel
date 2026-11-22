"""SFX bed for W1-L1, timed to the final timeline from make.py (run make.py --no-render first)."""
import json, subprocess
from pathlib import Path

P = Path(__file__).resolve().parent
L = P.parent.parent / "sfx_library"
D = L / "dl_2026_11"
words = json.loads((P / "words.json").read_text())
at = lambda w, n=0: [x["start"] for x in words if x["text"] == w][n]
DUR = 30.0   # longer than the reel; the mix is trimmed to the video

# (file, time on timeline, gain dB)
HITS = [
    (D / "camera_shutter.mp3", 0.05, -10),                 # hook: camera at the lens
    (D / "pop_hard_click.mp3", 2.85, -14),                 # JIM CORBETT card
    (D / "swoosh_short_wind.mp3", 2.95, -18),              # into tiger-on-road B-roll
    (D / "swoosh_short_wind.mp3", 7.87, -18),              # dawn road
    (D / "sweep_fast_small.mp3", 9.42, -18),               # open jeep
    (D / "swoosh_cinematic_wind.mp3", 10.52, -20),         # sal forest (engine off)
    (D / "impact_whoosh_deep.mp3", at("chase") - 0.25, -16),  # tiger walking (her photo)
    (D / "pop_hard_click.mp3", at("4"), -14),              # ONLY 4 SEATS
    (L / "msg_iphone_sent.mp3", at("SAFARI"), -12),        # comment SAFARI
    (D / "swoosh_ending_wind.mp3", at("Mera"), -18),        # bag reveal / loop
]

inp, fc = [], []
for i, (f, t, g) in enumerate(HITS):
    inp += ["-i", str(f)]
    ms = int(t * 1000)
    fc.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={g}dB,adelay={ms}|{ms}[s{i}]")
fc.append("".join(f"[s{i}]" for i in range(len(HITS))) + f"amix=inputs={len(HITS)}:normalize=0,apad,atrim=0:{DUR}[o]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(fc), "-map", "[o]",
                "-ar", "48000", str(P / "sfx_bed.wav")], check=True)
print("sfx_bed.wav", len(HITS), "hits")
