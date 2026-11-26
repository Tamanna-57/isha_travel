"""W1-T2b · Sat 28 Nov · @travelwithisha · Lakshadweep Part 2 + "Part 3? The jungle." safari end card.

Uses the finished Part 2 edit as-is (inbox/lakshadweep_part2/lakshadweep_reel_part2_no_music.mp4, 34.7 s, same caption
style as Part 1 so the series matches) and adds:
  * opening series title in the house Anton style ("LAKSHADWEEP" marigold / "PART 2" white) for the first 3 s
  * a 2.6 s end card on Isha's own tiger-on-the-road photo: "PART 3? THE JUNGLE." + COMMENT "SAFARI"
  * SFX: bubbles under the last water shot -> peacock call + deep whoosh into the jungle
Isha's 4-sec spoken end line wasn't shot; the end card is text-only (swap her line in when it arrives).
Usage: python sfx.py && python make.py
"""
import json, subprocess, sys
from pathlib import Path
P = Path(__file__).resolve().parent
ROOT = P.parent.parent
SRC, SRC_DUR = "../../inbox/lakshadweep_part2/lakshadweep_reel_part2_no_music.mp4", 34.70
DUR = SRC_DUR - (11.700 - 11.633)     # timeline length of the Part 2 edit after the 2-frame cut
CARD = 2.60
# 2-frame leftover jump (punched-in face, frames 349-350 = 11.633-11.700 s) removed: Isha flagged flashes on W1-L1
CUT_A, CUT_B = 11.633, 11.700
clips = [
    {"src": SRC, "in": 0.0, "out": CUT_A, "grade": "none"},
    {"src": SRC, "in": CUT_B, "out": SRC_DUR, "grade": "none"},
    {"src": "../w1_l1_details_out/broll/isha_tiger_road.mp4", "in": 0.0, "out": CARD, "audio": False, "grade": "none"},
]
titles = [
    {"type": "hook", "text": "LAKSHADWEEP", "font": "condensed", "color": "marigold", "size": 190, "y": 110, "start": 0.0, "end": 3.0},
    {"type": "hook", "text": "PART 2", "font": "condensed", "color": "chalk", "size": 150, "y": 330, "start": 0.0, "end": 3.0},
    {"type": "hook", "text": "PART 3?", "font": "condensed", "color": "marigold", "size": 250, "y": 160, "start": DUR, "end": DUR + CARD},
    {"type": "hook", "text": "THE JUNGLE.", "font": "condensed", "color": "chalk", "size": 175, "y": 440, "start": DUR + 0.25, "end": DUR + CARD},
    {"type": "hook", "text": "COMMENT \"SAFARI\" FOR THE LINK", "size": 105, "y": 1330, "start": DUR + 0.6, "end": DUR + CARD},
]
edit = {"name": "w1_t2b_lakshadweep_p2", "format": "A", "grade": "none", "clips": clips,
        "captions": {"style": "karaoke", "words": "words.json", "enabled": False}, "titles": titles}
if (P / "sfx_bed.wav").exists():
    edit["music"] = {"src": "sfx_bed.wav", "start": 0, "gain_db": 0, "duck": False}
(P / "words.json").write_text("[]")
(P / "edit.json").write_text(json.dumps(edit, indent=1))
if __name__ == "__main__" and "--no-render" not in sys.argv:
    subprocess.run([sys.executable, str(ROOT / "pipeline/isha.py"), "render", str(P / "edit.json")], check=True)
