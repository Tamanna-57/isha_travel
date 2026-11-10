# Bhai Dooj reel (R3 "To all the bhais I found on the road") — first draft

Clips: `bhai dooj/IMG_2418–2425.MOV` (Isha at home with the tika thali, in her recorded order) + her own
B-roll: Lakshadweep (`inbox/lakshadweep_part2`: boat, scuba instructor, dive, friends, fish) and two of her
safari photos from the archive zip (tiger past the jeeps, tiger on the road).

## Build
```bash
python projects/bhai_dooj/prep.py                                        # photo B-roll + original music -> build/
python pipeline/isha.py render projects/bhai_dooj/edit.json --stage assemble
python projects/bhai_dooj/align.py                                       # words.json + end-card timing
python pipeline/isha.py render projects/bhai_dooj/edit.json --stage finish
```
Transcription: whisper-small (Hindi + English passes) proofread into Roman Hinglish. Word timings come from the
voice energy of each phrase (`align.py`), since the whisper model here gives no word times.

## What she says (captions)
Aaj Bhai Dooj, aur mere paas ek nahi, bahut saare bhai. Aur mujhe ye sab travel karte hue mile.
Mere woh bhai, jinhone mujhe pahadon mein ekdum safe rakha hai. Aur mere scuba instructors, jinhone mujhe
12 meter underwater kuch nahi hone diya. Aur mere safari guide, jinhone jungle ke beech-o-beech mujhe bahut
crazy experiences karwaye. Aur aise bahut saare log, jinhone mujhe apni behen maankar, aise crazy jagahon pe
kuch nahi hone diya. (Thank you.) Thank you for keeping me safe when I was far away from home. Happy Bhai Dooj!

## Open items
- Names for the labels (brief: name + place). Labels now say only the role; add names in `edit.json` titles.
- OK from the people on screen (scuba instructor on the boat, divers, Lakshadweep friends) before posting.
- Length 32.7 s vs the brief's 25–30 s: every line she recorded is in. To get under 30 s, drop one line
  (e.g. "Aur mujhe ye sab travel karte hue mile").
- Words to double-check by ear: "safe rakha hai", "Aur aise bahut saare log", "aise crazy jagahon pe".
- Labels use the `label` title type (bold, hard shadow, no box). Ending: her last clip fades to black as the
  tika finger reaches the lens; end card on black; music ends on one santoor strum + bell.
- Pahadon line: B-roll from `bhai dooj/IMG_0551.MOV` 5.5–7.6 s (Isha walking in, snowy peaks).
- Music is an original synth bed (synth.py: santoor, dholak, manjira, tanpura, temple bell). Swap for a
  trending Instagram sound if preferred: post `bhai_dooj_clean.mp4`-style without music or lower `gain_db`.
