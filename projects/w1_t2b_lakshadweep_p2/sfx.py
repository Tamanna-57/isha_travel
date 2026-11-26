"""Real-sound bed for W1-T2b v2 (sits under Isha's voice; voice stays on top): boat, splash, bubbles/underwater,
evening waves, end card (bubbles -> peacock + growl). All recordings from sfx_library (Mixkit / Commons)."""
import json, subprocess
from pathlib import Path
P = Path(__file__).resolve().parent
L = P.parent.parent / "sfx_library"; S, D = L / "dl_safari", L / "dl_2026_11"
M = json.loads((P / "timeline.json").read_text())
END = M["end"]; B = {s: t for t, s in M["brolls"]}
HITS = [  # (file, src_start, dur, at, gain_db, fade_in, fade_out)
    (L / "motorboat_sea.mp3", 2.0, 1.6, B["IMG_3971.MOV"] - 0.05, -24, 0.1, 0.3),        # on the boat
    (L / "waves_close_loop.mp3", 0.0, 1.5, B["IMG_3972.MOV"], -24, 0.1, 0.3),            # sea rushing past the deck
    (L / "splash_jump_in.mp3", 0.0, 1.2, B["IMG_3815.MP4"] - 0.25, -16, 0.0, 0.4),       # roll in…
    (L / "underwater_ambience.mp3", 3.0, 2.2, B["IMG_3815.MP4"], -22, 0.2, 0.4),         # …12 m down
    (L / "bubbles_airtank.mp3", 0.0, 1.6, B["IMG_3815.MP4"] + 0.3, -22, 0.05, 0.4),      # regulator bubbles
    (L / "bubbles_deep.mp3", 0.0, 2.2, B["IMG_3976.MP4"], -24, 0.2, 0.4),                # "never felt so calm"
    (L / "waves_sea_loop.mp3", 0.0, 3.4, B["IMG_3884.MOV"], -24, 0.3, 0.5),              # sunset -> evening sea
    (L / "waves_small_rocks.mp3", 0.0, 1.8, B["IMG_3889.MOV"], -26, 0.3, 0.5),           # calm shallows
    (L / "bubbles_deep.mp3", 0.0, 1.2, END - 0.9, -22, 0.1, 0.3),                         # end card: water…
    (S / "peacock_call.ogg", 0.0, 2.2, END + 0.25, -14, 0.0, 0.3),                       # …into the jungle
    (S / "big_95.mp3", 0.35, 1.8, END + 0.9, -16, 0.04, 0.5),                            # low tiger growl
]
inp, fc = [], []
for i, (f, ss, d, at, g, fi, fo) in enumerate(HITS):
    inp += ["-ss", f"{ss}", "-t", f"{d}", "-i", str(f)]
    ms = int(max(0, at) * 1000)
    fc.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,afade=in:d={fi or 0.001},"
              f"afade=out:st={max(0, d - fo)}:d={fo or 0.001},volume={g}dB,adelay={ms}|{ms}[s{i}]")
fc.append("".join(f"[s{i}]" for i in range(len(HITS))) + f"amix=inputs={len(HITS)}:normalize=0,apad,atrim=0:{END + 3.0:.2f}[o]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(fc), "-map", "[o]", "-ar", "48000",
                str(P / "sfx_bed.wav")], check=True)
print("sfx_bed.wav", len(HITS), "layers")
