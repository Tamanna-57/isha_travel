"""W1-L1 · Mon 23 Nov · @lostandfree × @travelwithisha collab
"Tiger safari: details are out" — built from Isha's R1 album (inbox/r1, 7 clips, 2-4 takes per line).

Takes chosen (see TAKES.md for why):
  c1 take 2  "Safari ki details aa chuki hain"                 (camera pushed at lens: strongest hook frame)
  c2 only    "Four nights and five days in Jim Corbett National Park, Lost & Free Safaris ke saath"
  c3 take 1  "Subah saade paanch baje, open jeep, engine band aur poora jungle chup"  (+ finger-on-lips hold)
  c4 take 2  "Main inke saath isi liye jaati hoon kyunki ye animals ko chase nahi karte hain. Ye wait karte hain"
  c5 take 2  "Only 4 seats aur ek price mein sab included"     (take 1 stops before 'sab included')
  c6 take 2  "Comment karo SAFARI, tab tak main link bhej deti hoon"
  c7 take 1  "Mera toh bag ready hai, aur tumhara?"            (bag clearly in frame → loops to the camera hook)

Usage:  python make.py   (writes edit.json + words.json, then runs the pipeline)
Word timings come from faster-whisper (medium) on each take: scratch file r1_words.json, copied here as takes_words.json.
"""
import json, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parent.parent
SPEED = 1.1          # client note (R1 Leave Mumbai, 9 Nov): faster, tighter
W = json.loads((P / "takes_words.json").read_text(encoding="utf-8"))

# (clip, in, out, punch, whisper key, Roman Hinglish words in spoken order, brolls [(name, at_out, dur)])
TAKES = [
    (1, 19.62, 22.50, 1.00, "r1_clip01_hi", "Safari ki details aa chuki hain", []),
    (2, 2.82, 8.10, 1.08, "r1_clip02_en",
     "Four nights and five days in Jim Corbett National Park, Lost & Free Safaris ke saath.",
     [("isha_tiger_road", 0.35, 2.90)]),
    (3, 2.58, 9.60, 1.00, "r1_clip03_hi", "Subah saade paanch baje, open jeep, engine band aur poora jungle chup.",
     [("isha_misty_tiger", 0.45, 1.55), ("isha_jeeps_tiger", 2.00, 1.10), ("isha_tiger_leaves", 3.10, 1.95)]),
    # Isha (22 Nov): cut the gap between "chase" and "wait" -> 0.53 s pause (23.55-24.08) removed, photos back to back
    (4, 19.55, 23.55, 1.10, "r1_clip04_hiseg",
     "Main inke saath isi liye jaati hoon kyunki ye animals ko chase nahi karte hain.",
     [("isha_tiger_walk", 2.35, 1.30)]),
    (4, 24.08, 25.40, 1.00, "r1_clip04_hiseg", "Ye wait karte hain.", [("isha_dholes", 0.0, 1.21)]),
    (5, 12.74, 16.50, 1.00, "r1_clip05_hi", "Only 4 seats aur ek price mein sab included.", []),
    (6, 12.45, 15.45, 1.08, "r1_clip06_hi", "Comment karo SAFARI, tab tak main link bhej deti hoon.", []),
    (7, 3.92, 6.80, 1.00, "r1_clip07_hi", "Mera toh bag ready hai, aur tumhara?", []),
]
# Isha (22 Nov): highlight the important words (marigold + bigger) -- matched lowercase, punctuation stripped
EMPH = {"safari", "details", "four", "nights", "five", "days", "jim", "corbett", "lost", "&", "free", "safaris",
        "saade", "paanch", "baje", "open", "jeep", "engine", "band", "jungle", "chup", "chase", "wait",
        "only", "4", "seats", "price", "sab", "included", "comment", "link", "bag", "ready", "tumhara"}


def take_words(key, t0, t1, roman):
    ws = [w for s in W[key] for w in s["w"] if t0 - 0.4 <= w[0] <= t1]
    words = roman.split()
    if len(ws) == len(words):
        spans = [(max(t0, w[0]), min(t1, w[1])) for w in ws]
    else:   # spread over the spoken span by character length
        a, b = max(t0, ws[0][0]), min(t1, ws[-1][1])
        tot = sum(len(x) for x in words); spans, t = [], a
        for x in words:
            d = (b - a) * len(x) / tot; spans.append((t, t + d)); t += d
    return list(zip(words, spans))


def build():
    clips, words, t_line = [], [], 0.0
    for c, a, b, punch, key, roman, brolls in TAKES:
        clips.append({"src": f"../../inbox/r1/r1_clip0{c}.mov", "in": a, "out": b, "speed": SPEED, "punch": punch,
                      "grade": "natural",       # Isha (22 Nov): colour-correct -> house natural grade on her clips
                      "broll": [{"src": f"broll/{n}.mp4", "in": 0, "at": at, "dur": d, "grade": "none"} for n, at, d in brolls]})
        for txt, (s, e) in take_words(key, a, b, roman):
            words.append({"text": txt.rstrip(",."), "start": round(t_line + (s - a) / SPEED, 3),
                          "end": round(t_line + (e - a) / SPEED, 3), **({"emph": True} if txt.strip(",.?").lower() in EMPH else {})})
        t_line += (b - a) / SPEED
    T = [0.0]
    for _, a, b, *_ in TAKES:
        T.append(T[-1] + (b - a) / SPEED)
    titles = [
        # Isha (22 Nov): opening title bolder + different font -> Anton, two lines, marigold over white
        {"type": "hook", "text": "TIGER SAFARI", "font": "condensed", "color": "marigold", "size": 270, "y": 110, "start": 0.0, "end": T[1]},
        {"type": "hook", "text": "DETAILS ARE OUT", "font": "condensed", "color": "chalk", "size": 180, "y": 400, "start": 0.0, "end": T[1]},
        {"type": "landmark", "text": "JIM CORBETT", "sub": "4 NIGHTS · 5 DAYS · LOST & FREE SAFARIS", "start": T[1] + 0.25, "end": T[2]},
        {"type": "hook", "text": "5:30 AM · OPEN JEEP", "size": 120, "start": T[2] + 0.4, "end": T[2] + 3.0},
        {"type": "hook", "text": "ENGINE OFF. SILENCE.", "size": 120, "start": T[2] + 3.1, "end": T[3]},
        {"type": "hook", "text": "WE DON'T CHASE. WE WAIT.", "size": 120, "start": T[3] + 2.3, "end": T[5]},
        {"type": "hook", "text": "ONLY 4 SEATS · ONE PRICE · ALL INCLUDED", "size": 120, "start": T[5], "end": T[6]},
        {"type": "hook", "text": "COMMENT \"SAFARI\" FOR THE LINK", "size": 120, "start": T[6], "end": T[7]},
        {"type": "hook", "text": "MY BAG IS READY. YOURS?", "size": 120, "start": T[7], "end": T[8]},
    ]
    edit = {"name": "w1_l1_details_out", "format": "B", "grade": "natural", "clips": clips,
            "captions": {"style": "karaoke", "words": "words.json", "y": 1420}, "titles": titles, "voice": {"clean": True}}
    if (P / "sfx_bed.wav").exists():
        edit["music"] = {"src": "sfx_bed.wav", "start": 0, "gain_db": 0, "duck": False}
    (P / "edit.json").write_text(json.dumps(edit, indent=1, ensure_ascii=False))
    (P / "words.json").write_text(json.dumps(words, indent=1, ensure_ascii=False))
    print("timeline", [round(t, 2) for t in T])
    return T


if __name__ == "__main__":
    build()
    if "--no-render" not in sys.argv:
        subprocess.run([sys.executable, str(ROOT / "pipeline/isha.py"), "render", str(P / "edit.json")], check=True)
