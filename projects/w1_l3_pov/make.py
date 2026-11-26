"""W1-L3 · Fri 27 Nov · @lostandfree (tag @travelwithisha) · "POV: 5:30 AM, your first jungle safari" — 15 s, format D.

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

# (src, in, dur, note)
SHOTS = [
    ("broll/black.mp4", 0.0, 1.30, "black: phone alarm"),
    ("broll/isha_dawn.mp4", 0.0, 2.20, "dawn forest (cropped above the tiger so the reveal stays a surprise), engine starts"),
    (T1 + "isha_kingfisher_moss.mp4", 0.6, 2.00, "engine off: silence"),
    (T1 + "isha_jackal.mp4", 0.4, 2.00, "deer alarm call, ears up"),
    (T1 + "isha_owl.mp4", 0.4, 1.50, "wait for it (heartbeat)"),
    (L1 + "isha_tiger_walk.mp4", 0.0, 2.40, "THE TIGER (growl, whoosh)"),
    (L1 + "isha_jeeps_tiger.mp4", 0.0, 2.20, "worth the alarm"),
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
        {"type": "hook", "text": "POV: 5:30 AM", "font": "condensed", "color": "marigold", "size": 260, "y": 560, "start": 0, "end": T[1]},
        {"type": "hook", "text": "YOUR FIRST JUNGLE SAFARI", "font": "condensed", "color": "chalk", "size": 140, "y": 860, "start": 0, "end": T[1]},
        {"type": "hook", "text": "5:47 AM · OPEN JEEP", "size": 115, "start": T[1] + 0.2, "end": T[2]},
        {"type": "hook", "text": "ENGINE OFF.", "size": 125, "start": T[2], "end": T[3]},
        {"type": "hook", "text": "ALARM CALL. NOBODY MOVES.", "size": 115, "start": T[3], "end": T[4]},
        {"type": "hook", "text": "WAIT FOR IT…", "size": 125, "start": T[4], "end": T[5]},
        {"type": "hook", "text": "WORTH THE ALARM.", "font": "condensed", "color": "marigold", "size": 200, "y": 150, "start": T[6], "end": T[7]},
        {"type": "hook", "text": "SEND THIS TO YOUR 5 AM FRIEND", "size": 110, "start": T[7], "end": T[8]},
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
