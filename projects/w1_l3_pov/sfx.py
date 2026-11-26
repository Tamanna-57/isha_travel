"""Sound design for W1-L3 — REAL recordings only (feedback 26 Nov: "use real sound effects").
No synthesised beeps, no cinematic whooshes/heartbeats. Sources: sfx_library/real (Mixkit field recordings, see SOURCES.txt),
sfx_library/dl_safari (Wikimedia Commons barking-deer alarm call; real tiger growl used in the approved safari teaser),
sfx_library/dl_2026_11/camera_shutter.mp3.
"""
import json, subprocess
from pathlib import Path
P = Path(__file__).resolve().parent
L = P.parent.parent / "sfx_library"; R, S, D = L / "real", L / "dl_safari", L / "dl_2026_11"
T = json.loads((P / "timeline.json").read_text()); END = T[-1]
# T: 0 black/alarm | 1.3 dawn | 3.5 engine off | 5.5 alarm call | 7.5 wait | 9.0 tiger | 11.4 jeeps | 13.6 Isha shh | 15.1
# (file, src_start, dur, at, gain_db, fade_in, fade_out)
# T: 0 dawn | 2.2 kingfisher (engine off) | 4.1 jackal (alarm call) | 6.1 owl (something's coming) | 7.8 tiger | 10.6 jeeps | 12.7 Isha | 14.2
SH = D / "camera_shutter.mp3"
HITS = [
    (R / "alarm_clock_ring_mixkit1003.mp3", 0.0, 0.75, 0.00, -8, 0.005, 0.01),          # real alarm clock… cut dead
    (R / "morning_birds_mixkit2472.mp3", 30.0, T[1] + 0.1, 0.70, -5, 0.05, 0.25),        # dawn birds
    (R / "car_engine_start_mixkit1566.mp3", 0.0, 1.5, 0.75, -6, 0.005, 0.3),             # jeep starts
    (R / "keys_mixkit1558.mp3", 0.0, 1.1, T[1] - 0.15, -8, 0.005, 0.2),                  # key turned: ENGINE OFF
    (R / "quiet_forest_mixkit1220.mp3", 20.0, T[4] - T[1], T[1], -6, 0.3, 0.3),           # the silence (real forest room tone)
    (SH, 0.0, 0.5, T[1] + 1.05, +2, 0.0, 0.1),                                           # kingfisher shot
    (S / "barking_deer_alarm.wav", 2.6, 1.3, T[2] + 0.10, -6, 0.01, 0.3),                # real alarm call
    (S / "barking_deer_alarm.wav", 36.6, 1.1, T[2] + 0.85, -9, 0.01, 0.3),
    (SH, 0.0, 0.5, T[2] + 1.15, +2, 0.0, 0.1),                                           # jackal shot
    (R / "leaves_step_mixkit2429.mp3", 0.0, 0.6, T[3] + 0.10, +3, 0.005, 0.2),           # something walking on dry leaves…
    (R / "leaves_step_mixkit2429.mp3", 0.0, 0.6, T[3] + 0.50, +5, 0.005, 0.2),
    (R / "leaves_step_mixkit2429.mp3", 0.0, 0.6, T[3] + 0.90, +7, 0.005, 0.2),
    (R / "branch_snap_jungle_mixkit2423.mp3", 9.3, 0.5, T[3] + 1.30, +6, 0.005, 0.2),    # …a branch snaps
    (S / "big_5.mp3", 0.6, 2.4, T[4] + 0.05, -6, 0.02, 0.6),                             # real tiger growl on the snap zoom
    (SH, 0.0, 0.4, T[4] + 1.00, +3, 0.0, 0.08), (SH, 0.0, 0.4, T[4] + 1.17, +3, 0.0, 0.08),   # 4-shot burst
    (SH, 0.0, 0.4, T[4] + 1.34, +3, 0.0, 0.08), (SH, 0.0, 0.4, T[4] + 1.51, +3, 0.0, 0.08),
    (R / "quiet_forest_mixkit1220.mp3", 60.0, T[-1] - T[4], T[4], -4, 0.2, 0.4),         # forest stays under the rest
    (SH, 0.0, 0.5, T[5] + 0.30, -2, 0.0, 0.1), (SH, 0.0, 0.5, T[5] + 0.60, -3, 0.0, 0.1),     # tourists' cameras
    (SH, 0.0, 0.5, T[5] + 0.95, +2, 0.0, 0.1),                                           # Isha's last shot
    (R / "morning_birds_mixkit2472.mp3", 60.0, T[-1] - T[6] + 0.3, T[6], +2, 0.2, 0.3),  # birds come back for her "shh"
]
inp, fc = [], []
for i, (f, ss, d, at, g, fi, fo) in enumerate(HITS):
    inp += ["-ss", f"{ss}", "-t", f"{d}", "-i", str(f)]
    ms = int(at * 1000)
    fc.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,afade=in:d={fi or 0.001},"
              f"afade=out:st={max(0, d - fo)}:d={fo or 0.001},volume={g}dB,adelay={ms}|{ms}[s{i}]")
fc.append("".join(f"[s{i}]" for i in range(len(HITS))) + f"amix=inputs={len(HITS)}:normalize=0,apad,atrim=0:{END + 0.5:.2f}[o]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(fc), "-map", "[o]", "-ar", "48000",
                str(P / "sfx_bed.wav")], check=True)
print("sfx_bed.wav", len(HITS), "layers (all real recordings)")
