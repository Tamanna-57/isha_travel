# Leave Mumbai — Trial A (reference style)

Style copied from the client's reference reel (sailing_amrutha x ixigo, 22.9 s). Base layer = the final
(`projects/leave_mumbai`): same clips, cut points, speed, takes, voice and words; `assembled.mov` is the final's own file.

| | Reference | Trial A |
|---|---|---|
| Hook | "PAY ATTENTION", condensed heavy caps, neon lime `#D6EC47`, thin dark edge, ~23% down | her opening line "YAHI SOCHTI HOON … CHHOD HI DENA CHAHIYE." in Anton caps, neon lime `#D6EC47` |
| Captions | white rounded-bold phrases, 2–4 words, high in frame (23% down), soft dark outline, no word highlight | `topbold`: Poppins Bold 86 white, y 436, soft dark outline + shadow; single-word punch ("unlivable.") 120 |
| Cuts | hard cuts only (energy from in-shot motion and pace) | hard cuts (no whooshes) |
| Overlays | n/a | IQAir chart (lime India slice) and Lost & Free Safaris card moved low (y ~1060) so they don't clash with the top captions |
| Music | n/a | lo-fi groove, −15 dB ducked |

Build: `python projects/leave_mumbai/build_trials.py A` (checks the base layer against the final before rendering).
