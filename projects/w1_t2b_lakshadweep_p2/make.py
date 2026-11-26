"""W1-T2b (v2, rebuilt from raws) · Sat 28 Nov · @travelwithisha · Lakshadweep Part 2 + "Part 3? The jungle." end card.

v1 reused the old Part 2 render (old captions burned in). v2 rebuilds it from the raw clips (inbox/lakshadweep_part2,
Git LFS) so every house rule from Isha's feedback applies:
  * A-roll = IMG_3982 (her monologue). Every pause > 0.35 s cut down to ~0.16 s; 1.08x speed.
  * natural grade + saturation x0.85 on her and on the HDR dive clips (tone-mapped to SDR)
  * karaoke captions with key words highlighted · Anton titles (two-tone) · one "12 M DOWN" landmark beat
  * B-roll on the lines it illustrates, clear water only (no murky coral: IMG_3974 left out), no near-duplicate shots
  * real SFX (boat, splash, bubbles, underwater, waves) via sfx.py · end card on her tiger photo
Usage: python make.py --no-render && python sfx.py && python make.py
"""
import json, subprocess, sys
from pathlib import Path
P = Path(__file__).resolve().parent
ROOT = P.parent.parent
IN = "../../inbox/lakshadweep_part2/"
A = IN + "IMG_3982.MP4"
SPEED = 1.08
W = json.loads((P / "th_words.json").read_text())                  # faster-whisper words on IMG_3982 (start, end, word)
PAUSES = [(0.29, 0.81), (2.46, 3.43), (4.67, 5.30), (6.88, 7.36), (8.55, 9.10), (11.28, 11.74), (17.95, 18.48),
          (23.18, 23.91), (27.49, 28.56), (31.36, 31.84)]          # measured silences > 0.35 s (audio RMS)
END_SRC = 33.40
CARD = 2.6
FIX = {"fir": "phir", "realise,": "realise,", "meters": "metres"}
EMPH = {"dive", "enough", "round", "2", "open", "waters", "deep", "sea", "12", "metres", "down", "dil", "ocean", "dhadak",
        "calm", "magic", "raat", "10", "baje", "everything", "dark", "people", "light", "stars", "random", "yes",
        "peaceful", "moment", "life"}
# B-roll by spoken words: (first word index, last word index, clip, clip in-point)
BROLL = [
    ("So", "2.", "IMG_3971.MOV", 0.6),            # "So I went for round 2."  -> Isha in her mask on the boat
    ("Open", "sea,", "IMG_3972.MOV", 0.4),        # "Open waters, deep sea,"  -> gear on deck, the sea rushing past
    ("12", "down.", "IMG_3815.MP4", 0.5),         # "12 metres down."          -> divers over the coral
    ("never", "calm.", "IMG_3976.MP4", 9.0),      # "never felt so calm."      -> striped fish + divers, blue water
    ("So", "baje,", "IMG_3884.MOV", 0.3, 1),      # "So raat ke 10 baje,"      -> sunset (2nd "So")
    ("you", "behind", "IMG_3970.MOV", 2.0, 1),    # "you leave everything behind" -> evening sea
    ("and", "people.", "IMG_3979.MP4", 0.3, 0),   # "and walk into the dark ocean with your people." -> her friends
    ("the", "life.", "IMG_3889.MOV", 0.3, 2),     # "the most peaceful moment of your life." -> calm clear shallows
]

def segments():
    segs, t = [], 0.73
    for a, b in PAUSES[1:]:
        segs.append((t, a + 0.08)); t = b - 0.08
    segs.append((t, END_SRC))
    return segs

def word_index(word, nth=0, after=0):
    hits = [i for i, w in enumerate(W) if w[2] == word and i >= after]
    return hits[nth]

def build():
    segs = segments()
    starts = [0.0]
    for a, b in segs:
        starts.append(starts[-1] + (b - a) / SPEED)
    def tl(t):   # source time -> timeline; times inside a removed pause clamp to the nearest kept edge
        for k, (a, b) in enumerate(segs):
            if t <= b + 0.01:
                return starts[k] + (max(t, a) - a) / SPEED
        return starts[-1]
    clips = [{"src": A, "in": a, "out": b, "speed": SPEED, "grade": "natural", "sat": 0.85,
              "punch": 1.0 if k % 2 == 0 else 1.08, "broll": []} for k, (a, b) in enumerate(segs)]
    # B-roll: place each request inside the segment(s) it spans
    spans = []
    for req in BROLL:
        w0, w1 = req[:2]; nth = req[4] if len(req) > 4 else 0
        i0 = word_index(w0, nth); i1 = word_index(w1, 0, i0)
        spans.append([W[i0][0] - 0.05, W[i1][1] + 0.05])
    for j in range(len(spans) - 1):          # no 1-3 frame face flash between two B-rolls (Isha's W1-L1 note)
        if spans[j + 1][0] - spans[j][1] < 0.6:
            spans[j][1] = spans[j + 1][0]
    spans[-1][1] = END_SRC                    # last B-roll runs into the end card
    for req, (t0, t1) in zip(BROLL, spans):
        src, bin_ = req[2], req[3]
        used = 0.0
        for k, (a, b) in enumerate(segs):
            s, e = max(t0, a), min(t1, b)
            if e - s <= 0.05: continue
            if s - a < 0.12: s = a                       # snap to the segment edges so no A-roll frames peek through
            if b - e < 0.12: e = b + 0.06                # (the cut between segments must land B-roll -> B-roll)
            at = (s - a) / SPEED; dur = (e - s) / SPEED
            clips[k]["broll"].append({"src": IN + src, "in": round(bin_ + used, 3), "at": round(at, 3), "dur": round(dur, 3),
                                      "grade": "natural", "sat": 0.9})
            used += dur
    words = []
    for w in W:
        txt = FIX.get(w[2], w[2]); k = txt.strip(",.?!").lower()
        s, e = tl(w[0]), tl(w[1])
        words.append({"text": txt.rstrip(",."), "start": round(s, 3), "end": round(e, 3),
                      **({"emph": True} if k in EMPH else {}), **({"br": True} if txt[-1] in ",.?" else {})})
    T_END = starts[-1]
    t12 = tl(W[word_index("12")][0])
    clips.append({"src": "../w1_l1_details_out/broll/isha_tiger_road.mp4", "in": 0.0, "out": CARD, "audio": False, "grade": "none"})
    titles = [
        {"type": "hook", "text": "LAKSHADWEEP", "font": "condensed", "color": "marigold", "size": 190, "y": 110, "start": 0.0, "end": 2.8},
        {"type": "hook", "text": "PART 2", "font": "condensed", "color": "chalk", "size": 150, "y": 330, "start": 0.0, "end": 2.8},
        {"type": "hook", "text": "12 M DOWN", "font": "condensed", "color": "marigold", "size": 220, "y": 150, "start": t12, "end": t12 + 1.6},
        {"type": "hook", "text": "PART 3?", "font": "condensed", "color": "marigold", "size": 250, "y": 160, "start": T_END, "end": T_END + CARD},
        {"type": "hook", "text": "THE JUNGLE.", "font": "condensed", "color": "chalk", "size": 175, "y": 440, "start": T_END + 0.25, "end": T_END + CARD},
        {"type": "hook", "text": "COMMENT \"SAFARI\" FOR THE LINK", "size": 105, "y": 1330, "start": T_END + 0.6, "end": T_END + CARD},
    ]
    edit = {"name": "w1_t2b_lakshadweep_p2", "format": "A", "grade": "natural", "clips": clips,
            "captions": {"style": "karaoke", "words": "words.json", "y": 1420}, "titles": titles, "voice": {"clean": True}}
    if (P / "sfx_bed.wav").exists():
        edit["music"] = {"src": "sfx_bed.wav", "start": 0, "gain_db": 0, "duck": False}
    (P / "edit.json").write_text(json.dumps(edit, indent=1))
    (P / "words.json").write_text(json.dumps(words, indent=1))
    marks = {"end": T_END, "t12": t12, "brolls": [(tl(W[word_index(r[0], r[4] if len(r) > 4 else 0)][0]), r[2]) for r in BROLL]}
    (P / "timeline.json").write_text(json.dumps(marks))
    print("A-roll", round(T_END, 2), "s + card", CARD, "| broll at", [(round(t, 2), s) for t, s in marks["brolls"]])

if __name__ == "__main__":
    build()
    if "--no-render" not in sys.argv:
        subprocess.run([sys.executable, str(ROOT / "pipeline/isha.py"), "render", str(P / "edit.json")], check=True)
