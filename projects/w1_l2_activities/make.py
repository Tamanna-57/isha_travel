"""W1-L2 · activities reel · "5 things we do on a jungle safari (only one is the tiger)" · Lost & Free collab.

No new footage exists for this post yet (LAF activity footage never arrived), so it is built from what is real:
  * Isha's own wildlife photos, joined by ONE transition style used throughout (zoom-through, zoomthrough.py)
  * Isha's real R1 takes that Monday's reel did NOT use: clip01 take 1 (camera pushed to the lens),
    clip06 take 1 ("Comment Safari, tab tak main link bhej deti hoon"), clip07 take 2 ("Mera toh bag ready hai, aur tumhara?")
  * real field recordings only (sfx.py): engine, dawn birds, peacock, night jungle, leaves, shutter, tiger
House rules: Anton two-tone titles in the top band · karaoke captions with key words highlighted · sat 0.85 on her ·
1.08x · no A-roll flashes · nothing below y 1536 / right of x 950.
Activity list = the calendar's, minus bonfire + stars (no real photo of either): LAF must confirm before posting.
Usage: python zoomthrough.py && python make.py --no-render && python sfx.py && python make.py
"""
import json, subprocess, sys
from pathlib import Path
P = Path(__file__).resolve().parent; ROOT = P.parent.parent
R1 = "../../inbox/r1/"
SP = 1.08
PH = json.loads((P / "broll/photos_cuts.json").read_text())
c = PH["cuts"]; T_PH = PH["end"]
CAM = (6.30, 8.30)                     # clip01 take 1: camera comes up to the lens (muted, shutter SFX)
C6 = (3.72, 6.66)                      # clip06 take 1
C7 = (17.50, 20.05)                    # clip07 take 2
t_cam = T_PH; t6 = t_cam + (CAM[1] - CAM[0]); t7 = t6 + (C6[1] - C6[0]) / SP; T_END = t7 + (C7[1] - C7[0]) / SP
# (text, src start, src end, emph, page break after) — Roman Hinglish, proofread against the take
W6 = [("Comment", 3.80, 4.42, 0, 0), ("SAFARI,", 4.42, 4.96, 1, 1), ("tab", 5.06, 5.32, 0, 0), ("tak", 5.32, 5.40, 0, 0),
      ("main", 5.40, 5.62, 0, 0), ("link", 5.62, 5.92, 1, 0), ("bhej", 5.92, 6.32, 0, 0), ("deti", 6.32, 6.46, 0, 0), ("hoon.", 6.46, 6.60, 0, 1)]
W7 = [("Mera", 17.60, 17.95, 0, 0), ("toh", 17.95, 18.05, 0, 0), ("bag", 18.05, 18.30, 1, 0), ("ready", 18.30, 18.60, 1, 0),
      ("hai,", 18.60, 18.80, 0, 1), ("aur", 19.15, 19.35, 0, 0), ("tumhara?", 19.35, 19.90, 1, 0)]

def words():
    out = []
    for ws, t0, src0, end in ((W6, t6, C6[0], C6[1]), (W7, t7, C7[0], C7[1])):
        for txt, s, e, em, br in ws:
            out.append({"text": txt.rstrip(",."), "start": round(t0 + (s - src0) / SP, 3), "end": round(t0 + (min(e, end) - src0) / SP, 3),
                        **({"emph": True} if em else {}), **({"br": True} if br else {})})
    return out

def H(text, start, end, y, size, color="chalk", font="condensed"):
    return {"type": "hook", "text": text, "font": font, "color": color, "size": size, "y": y, "start": round(start, 3), "end": round(end, 3)}

def build():
    clips = [
        {"src": "broll/photos.mp4", "in": 0.0, "out": T_PH, "audio": False, "grade": "none"},
        {"src": R1 + "r1_clip01.mov", "in": CAM[0], "out": CAM[1], "audio": False, "grade": "natural", "sat": 0.85, "punch": 1.06},
        {"src": R1 + "r1_clip06.mov", "in": C6[0], "out": C6[1], "speed": SP, "grade": "natural", "sat": 0.85},
        {"src": R1 + "r1_clip07.mov", "in": C7[0], "out": C7[1], "speed": SP, "grade": "natural", "sat": 0.85, "punch": 1.08},
    ]
    items = [("01", "MORNING OPEN JEEP", c[1], c[3]), ("02", "EVENING SAFARI", c[3], c[5]), ("03", "BIRDING WALK", c[5], c[8]),
             ("04", "THE SMALL ONES", c[8], t_cam), ("05", "PHOTOGRAPHY WITH ME", t_cam, t6)]
    titles = [H("5 THINGS WE DO", 0.0, c[1], 110, 175, "marigold"), H("ON A JUNGLE SAFARI", 0.0, c[1], 320, 105),
              H("ONLY ONE IS THE TIGER", 0.55, c[1], 455, 62, font="sans_semi")]
    for n, label, a, b in items:
        titles += [H(n, a, b, 100, 230, "marigold"), H(label, a + 0.12, b, 360, 100 if len(label) < 16 else 84)]
    titles += [H("COMMENT \"SAFARI\"", t6, T_END, 120, 150, "marigold"), H("FOR THE LINK", t6 + 0.15, T_END, 300, 90)]
    edit = {"name": "w1_l2_activities", "format": "A", "grade": "natural", "clips": clips,
            "captions": {"style": "karaoke", "words": "words.json", "y": 1420}, "titles": titles, "voice": {"clean": True}}
    if (P / "sfx_bed.wav").exists():
        edit["music"] = {"src": "sfx_bed.wav", "start": 0, "gain_db": 0, "duck": False}
    (P / "edit.json").write_text(json.dumps(edit, indent=1))
    (P / "words.json").write_text(json.dumps(words(), indent=1))
    (P / "timeline.json").write_text(json.dumps({"cuts": c, "cam": t_cam, "c6": t6, "c7": t7, "end": T_END}))
    print("length", round(T_END, 2), "| cam", round(t_cam, 2), "c6", round(t6, 2), "c7", round(t7, 2))

if __name__ == "__main__":
    build()
    if "--no-render" not in sys.argv:
        subprocess.run([sys.executable, str(ROOT / "pipeline/isha.py"), "render", str(P / "edit.json")], check=True)
