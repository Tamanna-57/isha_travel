"""Word timings for the Bhai Dooj reel -> words.json (timeline seconds), and the end-card timing in edit.json.

Her lines were transcribed with whisper-small (Hindi + English passes, then proofread into Roman Hinglish by hand).
Whisper gives no word times here, so words are placed inside the voiced span of each phrase: the span's voiced
frames (energy above the clip's noise floor) are shared out by syllable weight, then every word start snaps to the
nearest energy dip within 60 ms. Phrase spans were read off the energy envelope of each clip.
Words in parts of a clip that the edit cuts out are dropped; the rest are mapped through edit.json onto the timeline.
"""
import json, re, subprocess
from pathlib import Path
import numpy as np

P = Path(__file__).resolve().parent
SR, HOP = 16000, 160          # 10 ms frames

# clip -> [(phrase, span start, span end)] in source seconds
SCRIPT = {
    "IMG_2418": [("Aaj Bhai Dooj,", 0.05, 0.98), ("aur mere paas ek nahi, bahut saare bhai.", 1.30, 3.82)],
    "IMG_2419": [("Aur mujhe ye sab travel karte hue mile.", 0.56, 2.67)],
    "IMG_2420": [("Mere woh bhai, jinhone mujhe pahadon mein ekdum safe rakha hai.", 0.17, 3.57)],
    "IMG_2421": [("Aur mere scuba instructors,", 0.25, 1.40), ("jinhone mujhe 12 meter underwater", 1.54, 4.45),
                 ("kuch nahi hone diya.", 4.73, 5.65)],
    "IMG_2422": [("Aur mere safari guide,", 0.13, 1.34), ("jinhone jungle ke beech-o-beech mujhe bahut", 1.72, 4.59),
                 ("crazy experiences karwaye.", 4.71, 6.06)],
    "IMG_2423": [("Aur aise bahut saare log, jinhone mujhe apni behen maankar, aise", 0.24, 4.14),
                 ("crazy jagahon pe", 4.41, 5.63), ("kuch nahi hone diya.", 6.10, 7.02)],
    "IMG_2424": [("Thank you.", 0.72, 1.22), ("Thank you for keeping me safe when I was far away from home.", 1.78, 4.76)],
    "IMG_2425": [("Happy Bhai Dooj!", 1.02, 1.83)],
}
SYL = {"12": 2, "instructors": 3, "experiences": 5, "beech-o-beech": 3, "karwaye": 3, "safari": 3, "underwater": 4,
       "jinhone": 3, "maankar": 2, "jagahon": 3, "keeping": 2, "away": 2, "crazy": 2, "travel": 2, "guide": 1,
       "scuba": 2, "meter": 2, "ekdum": 2, "pahadon": 3, "behen": 2, "Thank": 1, "home": 1, "safe": 1, "were": 1}
EMPH = {"Bhai", "Dooj", "bhai.", "travel", "safe", "scuba", "underwater", "safari", "jungle", "crazy", "behen",
        "home.", "Dooj!", "12"}

def syllables(w):
    k = re.sub(r"[^\w-]", "", w)
    if k in SYL:
        return SYL[k]
    return max(1, len(re.findall(r"[aeiouy]+", k.lower())))

def energy(src):
    # first decodable audio track (iPhone MOVs put an undecodable APAC spatial track first)
    codecs = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_name",
                             "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout.split()
    ai = next(k for k, c in enumerate(codecs) if c not in ("unknown", "none"))
    a = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-map", f"0:a:{ai}", "-ac", "1", "-ar", str(SR),
                        "-f", "s16le", "-"],
                       capture_output=True, check=True).stdout
    x = np.frombuffer(a, np.int16).astype(np.float32) / 32768
    n = len(x) // HOP
    e = 20 * np.log10(np.sqrt((x[: n * HOP].reshape(n, HOP) ** 2).mean(1)) + 1e-6)
    return np.convolve(e, np.ones(3) / 3, "same")

def align_clip(src, phrases):
    e = energy(src)
    floor = max(e.max() - 30, np.percentile(e, 20) + 8)
    out = []
    for text, s0, s1 in phrases:
        words = text.split()
        f0, f1 = int(s0 * 100), int(s1 * 100)
        voiced = np.where(e[f0:f1] > floor)[0] + f0
        if len(voiced) < len(words):
            voiced = np.arange(f0, f1)
        wts = np.array([syllables(w) + 0.15 * len(w) for w in words])
        edges = np.concatenate([[0], np.cumsum(wts) / wts.sum()])
        idx = np.minimum((edges * len(voiced)).astype(int), len(voiced) - 1)
        starts = [voiced[i] for i in idx[:-1]]
        for k in range(1, len(starts)):                      # snap to the nearest dip (+-60 ms)
            c = starts[k]; lo, hi = max(starts[k - 1] + 5, c - 6), min(c + 7, f1)
            if hi > lo:
                starts[k] = lo + int(np.argmin(e[lo:hi]))
        ends = starts[1:] + [voiced[-1] + 1]
        for w, a, b in zip(words, starts, ends):
            out.append({"text": w, "start": a / 100, "end": max(a / 100 + 0.08, b / 100 - 0.02)})
    return out

def main():
    edit = json.loads((P / "edit.json").read_text(encoding="utf-8"))
    cache, words, acc = {}, [], 0.0
    for c in edit["clips"]:
        if c.get("transition", "cut") != "cut":
            acc -= float(c.get("transition_dur", 0.25))      # xfade overlaps the two clips
        stem = Path(c["src"]).stem
        sp = c.get("speed", 1.0); dur = (c["out"] - c["in"]) / sp
        if stem in SCRIPT and c.get("audio", True):
            if stem not in cache:
                cache[stem] = align_clip((P / c["src"]).resolve(), SCRIPT[stem])
            for w in cache[stem]:
                mid = (w["start"] + w["end"]) / 2
                if c["in"] <= mid < c["out"]:
                    ww = {"text": w["text"],
                          "start": round(acc + max(0.0, w["start"] - c["in"]) / sp, 3),
                          "end": round(acc + min(c["out"], w["end"]) - c["in"], 3) if sp == 1 else None}
                    if w["text"] in EMPH:
                        ww["emph"] = True
                    words.append(ww)
        acc += dur
    (P / "words.json").write_text(json.dumps(words, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(" ".join(f"{w['text']}@{w['start']:.2f}" for w in words))
    # end card: from the end of "Dooj!" to the end of the reel
    last = next(w for w in reversed(words) if w["text"] == "Dooj!")
    for t in edit["titles"]:
        if t["type"] == "hook" and t["text"].startswith("TAG"):
            t["start"], t["end"] = round(last["end"] + 0.1, 2), round(acc, 2)
    (P / "edit.json").write_text(json.dumps(edit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(words)} words, reel {acc:.2f}s, end card {last['end'] + 0.1:.2f}-{acc:.2f}")

if __name__ == "__main__":
    main()
