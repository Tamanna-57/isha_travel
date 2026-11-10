# Leave Mumbai — Trial A "Ocean" (A/B test version)

Same cut, words, grade, chart and logo card as the final (`projects/leave_mumbai`). Changes only **colours + music**,
so its result tells us whether the palette and a fuller music bed help.

| | Final | Trial A |
|---|---|---|
| Heading | LEAVE MUMBAI, Anton, sindoor `#D7263D` | Anton, **cobalt `#2F80ED`** |
| Captions | karaoke white, keywords Playfair Bold Italic **marigold** | same, keywords **aqua `#56CCF2`** |
| Chart India slice | sindoor | cobalt |
| Music | calm pad, −17 dB | **lo-fi groove all through** (82 BPM, e-piano 7ths, boom-bap, vinyl crackle), −15 dB ducked |
| Cuts / SFX | hard cuts, soft whooshes, pops | same |

Build: `python projects/leave_mumbai/prep.py --project projects/leave_mumbai_trialA`, then
`python pipeline/isha.py render projects/leave_mumbai_trialA/edit.json` (uses the final's words.json).
