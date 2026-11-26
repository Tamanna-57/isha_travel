"""Sound design for W1-L3 (the sound IS the reel): alarm, engine, forest, silence, deer alarm, heartbeat, growl."""
import json, subprocess
from pathlib import Path
P = Path(__file__).resolve().parent
L = P.parent.parent / "sfx_library"; D, S = L / "dl_2026_11", L / "dl_safari"
T = json.loads((P / "timeline.json").read_text()); END = T[-1]
alarm = P / "build_alarm.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=2000:d=1.25:sample_rate=48000", "-af",
                "volume='if(lt(mod(t,0.36),0.07)+between(mod(t,0.36),0.11,0.18),1,0)':eval=frame", str(alarm)], check=True)
# (file, src_start, dur, at, gain_db, fade_in, fade_out)
HITS = [
    (alarm, 0, 1.25, 0.00, -14, 0, 0.05),                                  # 5:30 AM alarm on black
    (S / "pench_night_safari.wav", 20.0, T[2] - T[1] + 0.3, T[1], -4, 0.3, 0.25),   # forest ambience, cuts at ENGINE OFF
    (S / "2712-preview.mp3", 0.0, 1.9, T[1] + 0.05, -14, 0.03, 0.5),       # gypsy engine starts
    (S / "peacock_call.ogg", 0.0, 2.0, T[1] + 1.0, -22, 0.05, 0.4),        # distant peacock
    (S / "barking_deer_alarm.wav", 2.6, 1.3, T[3] + 0.15, -6, 0.01, 0.3),  # ALARM CALL
    (S / "barking_deer_alarm.wav", 36.6, 1.1, T[3] + 1.15, -9, 0.01, 0.3),
    (S / "490-preview.mp3", 0.0, 1.1, T[4] + 0.10, -10, 0.01, 0.2),        # heartbeat
    (S / "490-preview.mp3", 0.0, 1.1, T[4] + 0.80, -8, 0.01, 0.2),
    (S / "big_95.mp3", 0.35, 1.9, T[5] + 0.05, -8, 0.04, 0.6),            # tiger growl
    (D / "impact_whoosh_deep.mp3", 0.2, 2.0, T[5] - 0.10, -14, 0, 0.6),
    (S / "pench_night_safari.wav", 40.0, END - T[6], T[6], -8, 0.3, 0.4), # forest returns
    (D / "swoosh_ending_wind.mp3", 0.0, 1.5, T[7], -20, 0, 0.4),
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
print("sfx_bed.wav", len(HITS), "layers")
