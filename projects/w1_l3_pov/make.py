"""W1-L3 (v3: camera-POV) · Fri 27 Nov · @lostandfree (tag @travelwithisha) · "POV: 5:30 AM, your first jungle safari" — 15 s, format D.

No jeep-POV footage from Lost & Free yet, so the POV is built from Isha's own photos + real jungle sound
(engine, birds, deer alarm call, silence, growl), ending on Isha's finger-on-lips "shh" from her R1 album.
Feedback applied: Anton opening title (two-tone), only her photos, natural grade + saturation trim on her clip,
no gaps/flashes (qa_flash), SFX on every visual beat, punchy (no shot over 2.4 s). No speech -> no captions.
Usage: python make.py --no-render && python sfx.py && python make.py
"""
import json, subprocess, sys
from pathlib import Path
P = Path(__file__).resolve().parent
ROOT = P.parent.parent
L1, T1 = "../w1_l1_details_out/broll/", "../w1_t1_7years/broll/"

# v3 (26 Nov, "not a basic slideshow; realistic SFX + transitions"): every photo is a shot taken through Isha's
# camera — handheld drift, AF hunt, real shutter + 2-frame flash + freeze, snap zoom on the tiger (viewfinder.py).
# (src, in, dur, note)
SHOTS = [
    ("broll/vf_dawn.mp4", 0.0, 2.20, "dawn through the lens, AF hunts; alarm cut dead, engine starts"),
    ("broll/vf_kingfisher.mp4", 0.0, 1.90, "ENGINE OFF: kingfisher, shutter"),
    ("broll/vf_jackal.mp4", 0.0, 2.00, "deer alarm call, jackal ears up, shutter"),
    ("broll/vf_owl.mp4", 0.0, 1.70, "something's coming: leaves, branch snaps"),
    ("broll/vf_tiger.mp4", 0.0, 2.80, "snap zoom + growl + 4-shot burst"),
    ("broll/vf_jeeps.mp4", 0.0, 2.10, "pull back: the jeeps, tourists' shutters"),
]
ISHA = ("../../inbox/r1/r1_clip03.mov", 8.45, 9.95)     # Isha, finger on lips (after "chup"), audio off

def build():
    clips, T = [], [0.0]
    for src, a, d, _ in SHOTS:
        clips.append({"src": src, "in": a, "out": a + d, "audio": False, "grade": "none"})
        T.append(T[-1] + d)
    clips.append({"src": ISHA[0], "in": ISHA[1], "out": ISHA[2], "audio": False, "grade": "natural", "sat": 0.85, "punch": 1.08})
    T.append(T[-1] + ISHA[2] - ISHA[1])
    titles = [
        {"type": "hook", "text": "POV: 5:30 AM", "font": "condensed", "color": "marigold", "size": 200, "y": 130, "start": 0, "end": T[1]},
        {"type": "hook", "text": "YOUR FIRST JUNGLE SAFARI", "font": "condensed", "color": "chalk", "size": 110, "y": 345, "start": 0, "end": T[1]},
        {"type": "hook", "text": "ENGINE OFF.", "size": 125, "y": 300, "start": T[1], "end": T[2]},
        {"type": "hook", "text": "ALARM CALL.", "size": 125, "y": 300, "start": T[2], "end": T[3]},
        {"type": "hook", "text": "SOMETHING'S COMING…", "size": 120, "y": 300, "start": T[3], "end": T[4]},
        {"type": "hook", "text": "THERE.", "font": "condensed", "color": "marigold", "size": 260, "y": 170, "start": T[4] + 0.35, "end": T[5]},
        {"type": "hook", "text": "WORTH THE 5:30 ALARM.", "size": 115, "y": 300, "start": T[5], "end": T[6]},
        {"type": "hook", "text": "SEND THIS TO YOUR 5 AM FRIEND", "size": 110, "start": T[6], "end": T[7]},
    ]
    edit = {"name": "w1_l3_pov", "format": "D", "grade": "none", "clips": clips,
            "captions": {"style": "karaoke", "words": "words.json", "enabled": False}, "titles": titles}
    if (P / "sfx_bed.wav").exists():
        edit["music"] = {"src": "sfx_bed.wav", "start": 0, "gain_db": 0, "duck": False}
    (P / "words.json").write_text("[]")
    (P / "edit.json").write_text(json.dumps(edit, indent=1))
    (P / "timeline.json").write_text(json.dumps(T))
    print("timeline", [round(t, 2) for t in T])

if __name__ == "__main__":
    build()
    if "--no-render" not in sys.argv:
        subprocess.run([sys.executable, str(ROOT / "pipeline/isha.py"), "render", str(P / "edit.json")], check=True)
