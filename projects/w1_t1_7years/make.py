"""W1-T1 · Tue 24 Nov · @travelwithisha · "7 years of 5 AM alarms" — built from Isha's R2 album (inbox/r2, 6 clips).

Takes (see TAKES.md): c1 only take · c3 only full take (c2 is a false start) · c4 take 4 · c5 take 3 · c6 take 3.
Applies everything Isha asked for on the Monday reel (W1-L1 v1-v3):
  * bold Anton opening title, two-tone (marigold over white)
  * karaoke captions with the important words highlighted (marigold, 12% bigger)
  * only her own photos as B-roll (archive zip), each numbered so people can comment their favourite
  * house "natural" colour correction on her clips
  * pauses tightened (every internal pause cut down to ~0.15-0.3 s), 1.1x speed, more face than photos
  * frame-by-frame scan for 1-frame flashes after render (qa_flash.py)
Usage:  python sfx.py && python make.py
"""
import json, subprocess, sys
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parent.parent
SPEED = 1.1
W = json.loads((P / "takes_words.json").read_text(encoding="utf-8"))

# (clip, in, out, punch, words key or None, Roman Hinglish, brolls [(name, at_out, dur, broll_in)], speech span for
#  proportional timing when the word count doesn't match)
SEGS = [
    # opening line split with a punch-in at "wo bhi" so the first cut lands < 2.5 s
    (1, 3.40, 5.47, 1.00, "r2_clip01_hi", "7 saal ki wildlife photography,", []),
    (1, 5.47, 6.88, 1.12, "r2_clip01_hi", "wo bhi ek hi reel mein,", []),
    (1, 7.22, 8.98, 1.08, "r2_clip01_hi", "aur har subah ka ek hi rule:",
     [("kingfisher_fish", 0.00, 0.55, 0), ("nightjar", 0.55, 0.53, 0), ("kite", 1.08, 0.53, 0)]),
    (1, 9.30, 10.62, 1.00, "r2_clip01_hi", "paanch baje ka alarm.", []),
    (3, 4.42, 8.13, 1.00, "r2_clip03_en", "Kabhi ek wild dhole mila, sharing intimate moments with its mate.",
     [("dholes", 0.45, 2.92, 0)]),
    (3, 8.43, 13.88, 1.08, "r2_clip03_en", "Toh kabhi ek Indian jackal who looked straight at the camera, ya phir kabhi ek owl,",
     [("jackal", 0.80, 2.60, 0), ("owl", 4.25, 0.71, 0)]),
    (3, 14.17, 16.53, 1.00, "r2_clip03_en", "jo beautifully camouflage ho gaya tha.", [("owl", 0.0, 2.15, 0.71)]),
    (3, 17.55, 18.62, 1.08, "r2_clip03_en", "Aur ek din…", []),
    (3, 18.84, 19.95, 1.00, None, "ye.", [("tiger_lookup", 0.0, 1.01, 0)], (18.96, 19.40)),
    (4, 25.50, 28.90, 1.00, "r2_clip04_en", "Lekin the best moment kabhi ek photo nahi hota.", []),
    (5, 21.25, 25.25, 1.08, None, "Wo second hota hai, jab poora jungle ekdum shaant ho jaata hai.",
     [("kingfisher_moss", 1.55, 2.10, 0)], (21.36, 25.08)),
    (6, 22.15, 26.60, 1.00, "r2_clip06_en", "Aur iss baar tum mere saath chal rahe ho, through Lost & Free Safaris.", []),
]
SILENT_AFTER = 10         # after this segment: 0.8 s of pure silence on the same kingfisher shot (the "silence" beat)
EMPH = {"7", "saal", "wildlife", "photography", "reel", "subah", "rule", "paanch", "baje", "alarm", "wild", "dhole",
        "intimate", "mate", "indian", "jackal", "straight", "camera", "owl", "beautifully", "camouflage", "din", "ye",
        "best", "moment", "photo", "second", "jungle", "ekdum", "shaant", "iss", "baar", "saath", "lost", "&", "free", "safaris"}


def seg_words(key, t0, t1, roman, span=None):
    words = roman.split()
    ws = [w for s in W[key] for w in s["w"] if t0 - 0.15 <= w[0] <= t1] if key else []
    if ws and len(ws) == len(words):
        return [(x, (max(t0, w[0]), min(t1, w[1]))) for x, w in zip(words, ws)]
    a, b = span if span else (max(t0, ws[0][0]), min(t1, ws[-1][1]))
    a, b = max(a, t0), min(b, t1)
    tot = sum(len(x) for x in words); out, t = [], a
    for x in words:
        d = (b - a) * len(x) / tot; out.append((x, (t, t + d))); t += d
    return out


def build():
    clips, words, T = [], [], [0.0]
    for i, s in enumerate(SEGS):
        c, a, b, punch, key, roman, brolls = s[:7]
        span = s[7] if len(s) > 7 else None
        clips.append({"src": f"../../inbox/r2/r2_clip0{c}.mp4", "in": a, "out": b, "speed": SPEED, "punch": punch,
                      "grade": "natural",
                      "broll": [{"src": f"broll/isha_{n}.mp4", "in": bi, "at": at, "dur": d, "grade": "none"}
                                for n, at, d, bi in brolls]})
        for txt, (ws, we) in seg_words(key, a, b, roman, span):
            k = txt.strip(",.:…?").lower()
            words.append({"text": txt.rstrip(",.:"), "start": round(T[-1] + (ws - a) / SPEED, 3),
                          "end": round(T[-1] + (we - a) / SPEED, 3), **({"emph": True} if k in EMPH else {}),
                          **({"br": True} if txt[-1] in ",.:…?" else {})})   # page break at punctuation (not displayed)
        T.append(T[-1] + (b - a) / SPEED)
        if i == SILENT_AFTER:
            clips.append({"src": "broll/isha_kingfisher_moss.mp4", "in": 2.10, "out": 2.90, "audio": False, "grade": "none"})
            T.append(T[-1] + 0.80)
    # T index: 0 c1a | 1 c1a2 | 2 c1b | (then +1 on everything below) old: 1 c1b | 2 c1c | 3 c3a | 4 c3b | 5 c3c | 6 c3d | 7 c3e | 8 c4 | 9 c5 | 10 silent | 11 c6 | 12 end
    c3b = T[5]
    titles = [
        {"type": "hook", "text": "7 YEARS", "font": "condensed", "color": "marigold", "size": 300, "y": 100, "start": 0.0, "end": T[2]},
        {"type": "hook", "text": "OF 5 AM ALARMS", "font": "condensed", "color": "chalk", "size": 175, "y": 420, "start": 0.0, "end": T[2]},
        {"type": "hook", "text": "SAME RULE EVERY MORNING", "size": 115, "start": T[2], "end": T[3]},
        {"type": "hook", "text": "5 AM.", "font": "condensed", "color": "marigold", "size": 260, "y": 150, "start": T[3], "end": T[4]},
        {"type": "hook", "text": "01 · WILD DHOLES", "size": 120, "start": T[4] + 0.45, "end": T[5]},
        {"type": "hook", "text": "02 · INDIAN JACKAL", "size": 120, "start": c3b + 0.80, "end": c3b + 3.40},
        {"type": "hook", "text": "03 · SPOTTED OWLET", "size": 120, "start": c3b + 4.25, "end": T[7]},
        {"type": "hook", "text": "AND ONE DAY…", "size": 120, "start": T[7], "end": T[8]},
        {"type": "hook", "text": "04 · THIS.", "font": "condensed", "color": "marigold", "size": 220, "y": 150, "start": T[8], "end": T[9]},
        {"type": "hook", "text": "THE BEST MOMENT ISN'T A PHOTO", "size": 115, "start": T[9], "end": T[10]},
        {"type": "hook", "text": "IT'S THE SECOND THE JUNGLE GOES SILENT", "size": 115, "start": T[10], "end": T[12]},
        {"type": "hook", "text": "THIS TIME, YOU'RE COMING WITH ME", "size": 115, "start": T[12], "end": T[13]},
    ]
    edit = {"name": "w1_t1_7years", "format": "A", "grade": "natural", "clips": clips,
            "captions": {"style": "karaoke", "words": "words.json", "y": 1420}, "titles": titles, "voice": {"clean": True}}
    if (P / "sfx_bed.wav").exists():
        edit["music"] = {"src": "sfx_bed.wav", "start": 0, "gain_db": 0, "duck": False}
    (P / "edit.json").write_text(json.dumps(edit, indent=1, ensure_ascii=False))
    (P / "words.json").write_text(json.dumps(words, indent=1, ensure_ascii=False))
    (P / "timeline.json").write_text(json.dumps(T))
    print("timeline", [round(t, 2) for t in T])


if __name__ == "__main__":
    build()
    if "--no-render" not in sys.argv:
        subprocess.run([sys.executable, str(ROOT / "pipeline/isha.py"), "render", str(P / "edit.json")], check=True)
