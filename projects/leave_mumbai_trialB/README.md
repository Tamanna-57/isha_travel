# Leave Mumbai — Trial B (reference style 2)

Style copied from the client's second reference (brindasharma "Auraton" reel, 14.3 s). Base layer = the final
(`projects/leave_mumbai`): same clips, cut points, speed, takes, voice and words (voice checked sample-identical).

| | Reference | Trial B |
|---|---|---|
| Captions | line builds word by word as spoken; content words heavy rounded sans in **yellow `#F0E366`**, filler words (ka, na, ke, se, hi) small **white**; soft dark shadow; upper third (~26% down) | `build` style: Poppins ExtraBold 100 yellow `#F2E25A` + Poppins SemiBold 64 white fillers, y 490; a line of only fillers gets its longest word in yellow |
| Title | none (the first line is the hook) | none |
| Cuts | fast; a few whip/motion bursts early, otherwise hard cuts | hard cuts + whip/zoom punches on room changes (video only, audio untouched) |
| Overlays | n/a | IQAir chart (yellow India slice) and Lost & Free Safaris card moved low (y ~1060) |
| Music | upbeat Bollywood | original upbeat pop bed, −15 dB ducked |

Build: `python projects/leave_mumbai/build_trials.py B` (checks the base layer against the final before rendering).
