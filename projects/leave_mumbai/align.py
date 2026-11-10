"""Word timings for the Leave Mumbai reel -> words.json (timeline seconds).

Text = her exact words (the client's proofread captions, checked against whisper-small Hindi + English passes of
the raw clips). Times: each phrase's voiced span in the raw clip (clean phone audio) is shared out by syllable
weight, word starts snap to the nearest energy dip; words outside a clip's in/out are dropped, the rest are mapped
through edit.json onto the timeline. Same method as projects/bhai_dooj/align.py.
"""
import json, re, subprocess
from pathlib import Path
import numpy as np

P = Path(__file__).resolve().parent
SR, HOP = 16000, 160

# raw clip -> [(phrase, voiced span start, end)] in source seconds
# "|" = caption page break (hand-set so every page is a natural phrase); *word* = keyword highlight
SCRIPT = {
    "LM_02": [("main har roz uthke… |", 19.13, 19.90), ("yahi sochti hoon |", 19.96, 21.04), ("ki bas, |", 21.17, 21.52),
              ("ab toh *Mumbai* | chhod hi dena chahiye. |", 22.14, 23.91)],
    "LM_03": [("main phir bhi, | rukne ki poori *koshish* | karti hoon, because |", 22.98, 25.58),
              ("it's my *city,* | you know, and I *love* it. |", 25.90, 27.48)],
    "LM_04": [("but *honestly,* |", 4.56, 5.38), ("Mumbai has become |", 5.76, 6.98), ("*unlivable.* |", 7.21, 7.86)],
    "LM_05": [("*mangroves* are being cut, | *rivers* are being polluted | and honestly, |", 1.35, 4.68),
              ("aajkal koi | kisi cheez ki *respect* | hi nahi karta hai yaar. |", 4.81, 7.84)],
    "LM_06": [("aur har *Diwali,* | *pollution* aur bhi | zyada badh jaata hai. |", 5.97, 8.98)],
    "LM_07": [("*13* out of | the world's *20* | most *polluted* cities | are in *India.* |", 18.56, 22.40)],
    "LM_10": [("bas itna *socho* ki, | humne kiya kya hai. |", 3.33, 6.03)],     # take 4: the clear "kiya kya hai"
    "LM_11": [
              ("toh is saal, | meri sirf ek *request* hai. |", 15.85, 18.13),
              ("aur ye sab humein | laaya *kidhar* hai? |", 20.93, 23.31)],     # take 3 after "kya hai" (20.58-20.86)
    "LM_12": [("aur jab *saans* lene ki | jagah chahiye ho, |", 6.37, 8.44), ("main *jungle* jaati hoon, |", 8.97, 10.06),
              ("*Lost* *&* *Free* *Safaris* |", 10.59, 11.30),     # she says "Lost & Free"; "Safaris" = brand (client ask)
              ("ke saath, |", 11.30, 11.69), ("aap bhi *chalna?* |", 12.61, 13.32), ("details coming out *soon.* |", 13.72, 15.05)],
}
SYL = {"13": 2, "20": 2, "&": 1, "Safaris": 1, "Mumbai": 2, "Diwali": 3, "unlivable": 4, "mangroves": 2,
       "pollution": 3, "polluted": 3, "exactly": 3, "honestly,": 3, "respect": 2, "request": 2, "it's": 1,
       "world's": 1, "uthke…": 2, "details": 2, "coming": 2, "humein": 3, "jagah": 2, "saans": 1}

def syllables(w):
    k = re.sub(r"[^\w&'-]", "", w)
    return SYL.get(k, SYL.get(w, max(1, len(re.findall(r"[aeiouy]+", k.lower())))))

def energy(src):
    codecs = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_name",
                             "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout.split()
    ai = next(k for k, c in enumerate(codecs) if c not in ("unknown", "none"))
    a = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-map", f"0:a:{ai}", "-ac", "1", "-ar", str(SR),
                        "-f", "s16le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(a, np.int16).astype(np.float32) / 32768
    n = len(x) // HOP
    e = 20 * np.log10(np.sqrt((x[: n * HOP].reshape(n, HOP) ** 2).mean(1)) + 1e-6)
    return np.convolve(e, np.ones(3) / 3, "same")

def align_clip(src, phrases):
    e = energy(src)
    floor = max(e.max() - 32, np.percentile(e, 15) + 10)
    out = []
    for text, s0, s1 in phrases:
        toks = text.split()
        words, brk = [], []
        for tk in toks:
            if tk == "|":
                brk[-1] = True
            else:
                words.append(tk); brk.append(False)
        emph = [w.startswith("*") and w.endswith("*") and len(w) > 1 for w in words]
        words = [w.strip("*") if e else w for w, e in zip(words, emph)]
        f0, f1 = int(s0 * 100), int(s1 * 100)
        voiced = np.where(e[f0:f1] > floor)[0] + f0
        if len(voiced) < len(words):
            voiced = np.arange(f0, f1)
        wts = np.array([syllables(w) + 0.15 * len(w) for w in words])
        edges = np.concatenate([[0], np.cumsum(wts) / wts.sum()])
        idx = np.minimum((edges * len(voiced)).astype(int), len(voiced) - 1)
        starts = [voiced[i] for i in idx[:-1]]
        for k in range(1, len(starts)):
            c = starts[k]; lo, hi = max(starts[k - 1] + 5, c - 6), min(c + 7, f1)
            if hi > lo:
                starts[k] = lo + int(np.argmin(e[lo:hi]))
        ends = starts[1:] + [voiced[-1] + 1]
        for w, br, em, a, b in zip(words, brk, emph, starts, ends):
            out.append({"text": w, "start": a / 100, "end": max(a / 100 + 0.08, b / 100 - 0.02), "br": br, "emph": em})
    return out

def main():
    edit = json.loads((P / "edit.json").read_text(encoding="utf-8"))
    cache, words, acc = {}, [], 0.0
    for c in edit["clips"]:
        stem = Path(c["src"]).stem
        dur = (c["out"] - c["in"]) / c.get("speed", 1.0)
        if stem in SCRIPT:
            if stem not in cache:
                cache[stem] = align_clip((P / c["src"]).resolve(), SCRIPT[stem])
            for w in cache[stem]:
                mid = (w["start"] + w["end"]) / 2
                if c["in"] <= mid < c["out"]:
                    sp = c.get("speed", 1.0)
                    ww = {"text": w["text"], "start": round(acc + max(0.0, w["start"] - c["in"]) / sp, 3),
                          "end": round(acc + (min(c["out"], w["end"]) - c["in"]) / sp, 3)}
                    if w["br"]:
                        ww["br"] = True
                    if w["emph"]:
                        ww["emph"] = True
                    words.append(ww)
        acc += dur
    (P / "words.json").write_text(json.dumps(words, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(" ".join(f"{w['text']}@{w['start']:.2f}" for w in words))
    print(f"{len(words)} words, reel {acc:.2f}s")

if __name__ == "__main__":
    main()
