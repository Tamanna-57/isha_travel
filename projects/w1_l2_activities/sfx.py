"""Sound design for W1-L2: REAL field recordings only (Isha, 26 Nov: "use real sound effects"; no synthetic whooshes).
Every cut lands on the sound of the thing on screen (research: SFX tied to cuts/text reveals lifts retention).
Sources: sfx_library/real (Mixkit free licence, SOURCES.txt), sfx_library/dl_safari (Commons recordings), camera_shutter."""
import json, subprocess
from pathlib import Path
P = Path(__file__).resolve().parent
L = P.parent.parent / "sfx_library"; R, S, D = L / "real", L / "dl_safari", L / "dl_2026_11"
T = json.loads((P / "timeline.json").read_text()); c = T["cuts"]; END = T["end"]
SH = D / "camera_shutter.mp3"
HITS = [  # (file, src_start, dur, at, gain_db, fade_in, fade_out)
    (R / "quiet_forest_mixkit1220.mp3", 5.0, c[1] + 0.2, 0.0, -8, 0.05, 0.2),            # hook: the forest…
    (S / "big_5.mp3", 0.6, 1.9, 0.15, -8, 0.02, 0.5),                                    # …and a real tiger growl
    (R / "car_engine_start_mixkit1566.mp3", 0.0, 1.6, c[1] - 0.05, -7, 0.005, 0.4),      # 01 open jeep starts
    (R / "morning_birds_mixkit2472.mp3", 30.0, c[3] - c[1], c[1] + 0.3, -7, 0.3, 0.2),   #    dawn chorus
    (S / "peacock_call.ogg", 0.0, 1.8, c[3] - 0.02, -6, 0.0, 0.4),                       # 02 evening: peacock
    (S / "pench_night_safari.wav", 5.0, c[5] - c[3], c[3] + 0.2, -6, 0.3, 0.2),           #    dusk jungle (Pench recording)
    (R / "morning_birds_mixkit2472.mp3", 60.0, c[8] - c[5], c[5], -4, 0.05, 0.2),        # 03 birding walk: birds up close
    (SH, 0.0, 0.4, c[5] + 0.35, -1, 0.0, 0.08), (SH, 0.0, 0.4, c[6] + 0.35, -1, 0.0, 0.08), (SH, 0.0, 0.4, c[7] + 0.35, -1, 0.0, 0.08),
    (R / "leaves_step_mixkit2429.mp3", 0.0, 0.6, c[8] + 0.05, +3, 0.005, 0.2),          # 04 small ones: something in the leaves
    (R / "leaves_rustle_mixkit2430.mp3", 0.0, 1.0, c[8] + 0.45, -2, 0.05, 0.3),
    (R / "leaves_step_mixkit2429.mp3", 0.0, 0.6, c[9] + 0.05, +5, 0.005, 0.2),
    (S / "barking_deer_alarm.wav", 2.6, 1.0, c[9] + 0.5, -10, 0.01, 0.3),
    (SH, 0.0, 0.4, T["cam"] + 0.55, +2, 0.0, 0.08), (SH, 0.0, 0.4, T["cam"] + 0.72, +2, 0.0, 0.08),   # 05 her camera: burst
    (SH, 0.0, 0.4, T["cam"] + 0.89, +2, 0.0, 0.08),
    (R / "quiet_forest_mixkit1220.mp3", 40.0, END - T["cam"], T["cam"], -12, 0.2, 0.4),  # forest room tone under her voice
]
inp, fc = [], []
for i, (f, ss, d, at, g, fi, fo) in enumerate(HITS):
    inp += ["-ss", f"{ss}", "-t", f"{d}", "-i", str(f)]
    ms = int(max(0, at) * 1000)
    fc.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,afade=in:d={fi or 0.001},"
              f"afade=out:st={max(0, d - fo)}:d={fo or 0.001},volume={g}dB,adelay={ms}|{ms}[s{i}]")
fc.append("".join(f"[s{i}]" for i in range(len(HITS))) + f"amix=inputs={len(HITS)}:normalize=0,apad,atrim=0:{END + 0.3:.2f}[o]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(fc), "-map", "[o]", "-ar", "48000",
                str(P / "sfx_bed.wav")], check=True)
print("sfx_bed.wav", len(HITS), "layers (all real recordings)")
