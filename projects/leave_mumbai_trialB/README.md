# Leave Mumbai — Trial B "Bold Pop" (A/B test version)

Same cut and words as the final (`projects/leave_mumbai`). Changes **fonts, effects, transitions and music**, so its
result tells us whether a punchier, more "edited" style works for Isha's audience.

| | Final | Trial B |
|---|---|---|
| Title | label + LEAVE MUMBAI (Anton, sindoor) | **Caveat handwritten**, writes itself on: "every morning, I want to" (white) + "Leave Mumbai!" (**hot pink `#FF4F8B`**) |
| Captions | karaoke (whole line, words light up) | **`pop`: Montserrat Bold ALL CAPS, each word pops in as she says it**, keywords pink, hard shadow |
| Room changes | hard cuts | **whip** (zoom + motion blur) / **zoom** / **flash** intros (`fx`, video only: audio untouched) |
| Chart India slice | sindoor | hot pink |
| Music | calm pad | **upbeat pop** (104 BPM, four-on-the-floor, claps, plucky arpeggio, riser into the chart), −15 dB ducked |
| SFX | whooshes −21 dB | whooshes −17 dB (matched to the whips), pops |

Build: `python projects/leave_mumbai/prep.py --project projects/leave_mumbai_trialB`, then
`python pipeline/isha.py render projects/leave_mumbai_trialB/edit.json`.
