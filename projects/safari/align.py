"""Forced alignment of the client's transcript (2026-11-04) to IMG_2240's voice (torchaudio MMS_FA). -> build/words.json"""
import json, re
from pathlib import Path
import numpy as np, torch, torchaudio
from scipy.io import wavfile
from scipy.signal import resample_poly
P = Path(__file__).resolve().parent
TRANSCRIPT = """You don't need to be a wildlife photographer to see a tiger.
All you need is an open jeep, in the jungle, at 6 am in the morning.
And then suddenly, everything will go silent.
An alarm call will ring...
and you will know, it's right there.
And the way your heart will pound in that moment? No reel will ever make you feel like that.
You know I've spent years photographing these moments on my camera.
But now I want you to see it with your own eyes, not on some screen.
And that's exactly why I'm hosting a safari with Lost & Free Safaris just for you.
Details are coming out soon, and if you want then comment SAFARI and you'll be the first to know."""
SPOKEN = {"6": "six", "am": "aym", "&": "and", "don't": "dont", "i've": "ive", "that's": "thats", "i'm": "im", "it's": "its", "you'll": "youll"}
def main():
    sr, x = wavfile.read(P / "build/src.wav")
    x = x.astype(np.float32).mean(1) / 32768
    x = resample_poly(x, 1, 3).astype(np.float32)
    wav = torch.from_numpy(x)[None]
    words = TRANSCRIPT.split()
    norm = [re.sub(r"[^a-z]", "", SPOKEN.get(w.lower().strip(".,?!"), w.lower())) for w in words]
    b = torchaudio.pipelines.MMS_FA
    model = b.get_model(); tok, aligner = b.get_tokenizer(), b.get_aligner()
    with torch.inference_mode():
        em, _ = model(wav)
        spans = aligner(em[0], tok(norm))
    r = wav.shape[1] / em.shape[1] / 16000
    out = [{"text": w, "start": round(sp[0].start * r, 3), "end": round(sp[-1].end * r, 3),
            "score": round(float(np.mean([s.score for s in sp])), 3)} for w, sp in zip(words, spans)]
    (P / "build/words.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(" ".join(f"{o['text']}@{o['start']:.2f}" + ("?" if o["score"] < 0.4 else "") for o in out))
main()
