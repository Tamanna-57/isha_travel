"""Forced alignment of the client's exact transcript to the draft's voice (torchaudio MMS_FA, CPU).

Whisper (en + hi passes) disagreed by up to 0.4 s on the Hinglish lines, so caption timing comes from here instead.
Writes build/words.json: [{"text", "start", "end", "score"}] in timeline seconds.
"""
import json, re
from pathlib import Path
import numpy as np
import torch, torchaudio
from scipy.io import wavfile
from scipy.signal import resample_poly

P = Path(__file__).resolve().parent
TRANSCRIPT = """Ek friend ka message aata hai
Lakshadweep chalegi?
Aur before you can even think
You say yes
To a never ending layover
Just to see the most turquoise blue water from your window.
And then you land on a small island
Where day one is just beach, breeze and water
Friends ke sath bohot saari masti.
And then comes day two
Masks on, regulators in
All set for our first dive
Life mein pehli baar
You breathe underwater
Bas corals, colourful fish
Aur ek silence jo upar kabhi nhi milegi
Par ek dive kabhi enough nhi hoti,
So stay tuned for part 2."""

# spoken forms for the aligner (display text is kept as written)
SPOKEN = {"nhi": "nahi", "2": "two", "lakshadweep": "lakshadweep"}

def main():
    sr, x = wavfile.read(P / "build/src.wav")
    x = x.mean(1).astype(np.float32)
    x = resample_poly(x, 1, 3).astype(np.float32)          # 48k -> 16k
    wav = torch.from_numpy(x)[None]
    words = TRANSCRIPT.split()
    norm = [re.sub(r"[^a-z']", "", SPOKEN.get(w.lower().strip(".,?"), w.lower())) for w in words]

    bundle = torchaudio.pipelines.MMS_FA
    model = bundle.get_model()
    tok, aligner = bundle.get_tokenizer(), bundle.get_aligner()
    with torch.inference_mode():
        emission, _ = model(wav)
        spans = aligner(emission[0], tok(norm))
    ratio = wav.shape[1] / emission.shape[1] / 16000      # seconds per emission frame
    out = []
    for w, sp in zip(words, spans):
        out.append({"text": w, "start": round(sp[0].start * ratio, 3), "end": round(sp[-1].end * ratio, 3),
                    "score": round(float(np.mean([s.score for s in sp])), 3)})
    (P / "build/words.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(" ".join(f"{o['text']}@{o['start']:.2f}" + ("?" if o["score"] < 0.4 else "") for o in out))

if __name__ == "__main__":
    main()
