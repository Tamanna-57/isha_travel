"""SFX bed for W1-T1 (run `python make.py --no-render` first so words.json/timeline.json exist)."""
import json, subprocess
from pathlib import Path

P = Path(__file__).resolve().parent
L = P.parent.parent / "sfx_library"
D = L / "dl_2026_11"
words = json.loads((P / "words.json").read_text())
T = json.loads((P / "timeline.json").read_text())
at = lambda w, n=0: [x["start"] for x in words if x["text"].strip("…") == w][n]

# digital alarm: 3 pairs of 2 kHz beeps (synthesised, no file needed)
alarm = P / "build_alarm.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=2000:d=1.1:sample_rate=48000",
                "-af", "volume='if(lt(mod(t,0.36),0.07)+between(mod(t,0.36),0.11,0.18),1,0)':eval=frame,afade=out:st=1.0:d=0.1",
                str(alarm)], check=True)

HITS = [
    *[(D / "camera_shutter.mp3", T[2] + k * 0.267, -13) for k in range(6)],   # 6-photo montage, one click each
    (alarm, at("alarm") - 0.05, -16),                      # "paanch baje ka ALARM"
    (D / "pop_hard_click.mp3", T[4] + 0.45, -15),          # 01 dholes
    (D / "pop_hard_click.mp3", T[5] + 0.80, -15),          # 02 jackal
    (D / "pop_hard_click.mp3", T[5] + 4.25, -15),          # 03 owl
    (D / "riser_drama.mp3", T[7] - 0.6, -24),              # "aur ek din…" build
    (D / "impact_whoosh_deep.mp3", T[8] - 0.05, -14),      # 04 tiger
    (D / "swoosh_short_wind.mp3", T[10] + 1.50, -20),       # into the quiet kingfisher shot
    (D / "swoosh_ending_wind.mp3", T[12] + 0.05, -20),     # "aur iss baar…"
]
inp, fc = [], []
for i, (f, t, g) in enumerate(HITS):
    inp += ["-i", str(f)]
    ms = max(0, int(t * 1000))
    fc.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={g}dB,adelay={ms}|{ms}[s{i}]")
fc.append("".join(f"[s{i}]" for i in range(len(HITS))) + f"amix=inputs={len(HITS)}:normalize=0,apad,atrim=0:{T[-1] + 1:.2f}[o]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", ";".join(fc), "-map", "[o]", "-ar", "48000",
                str(P / "sfx_bed.wav")], check=True)
print("sfx_bed.wav", len(HITS), "hits")
