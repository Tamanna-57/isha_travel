# Bhai Dooj reel: full spec (client-approved, Nov 2026)

> **Why this file exists:** the client loved this reel: the captions, the bold text and the whole look.
> **It is the default look for new Isha reels** unless the client asks for something else.
> Visual reference: [`brand/06_client_approved_look.png`](../../brand/06_client_approved_look.png).
> Starting cut list: [`templates/E_client_approved.edit.json`](../../templates/E_client_approved.edit.json).
> Rulebook section: `ISHA_REEL_SYSTEM.md` §0.1.

Final: `out/bhai_dooj.mp4`, 33.2 s, 1080×1920, 30 fps, −14.0 LUFS, true peak −1.5 dBTP.
Brief: R3 "To all the bhais I found on the road" (post Wed 11 Nov, @travelwithisha).

---

## 1. What the client liked (keep doing this)
1. **Bold, clean text, no boxes.** Bold white letters with a hard drop shadow read on any background. She asked to
   remove the black box behind the labels and to make them bold with hard shadows.
2. **Smooth karaoke captions:** the whole phrase shows in grey and each word turns white as she says it.
3. **Her real voice carries the story.** B-roll plays *under* her voice (L-cut) exactly when she names a
   person or place, then the cut goes back to her face for the emotional line.
4. **A basic, honest edit, not "picturesque":** hard cuts on her sentences, natural grade, no flashy transitions.
5. **A soft ending:** when her finger comes to the lens, it **fades to black** and the end card sits on black.
6. **Festive but gentle music** under the voice, dropping out for the emotional line and resolving on a bell.

## 2. Type and colour (exact values)

| Element | Font (file in `fonts/`) | Size (libass) | Colour | Effects | Position (of 1080×1920) |
|---|---|---|---|---|---|
| **Captions** (`karaoke`) | Poppins SemiBold (`Poppins-SemiBold.ttf`) | 115 | words wait in **grey `#9A9A9A`** at 80%, turn **white `#FFFFFF`** on their spoken time | outline 1.5 px (37% black), shadow 4 px (45% black), 40 ms fade-in | centre x 540, **y 1340** |
| **Opening title** (`chapter`) | Anton (`Anton-Regular.ttf`), ALL CAPS | auto-fit; "HAPPY BHAI DOOJ" = 201 | **sindoor `#D7263D`** | no outline, shadow 6 px; pop 92→100% in 90 ms | y **330** |
| Script under the title | Allura (`Allura-Regular.ttf`) | scales with the title (146) | **white** | overlaps the lower third of the title | y 330 + 0.24 × title size |
| **Person labels** (`label`) | **Playfair Display Bold** (`PlayfairDisplay-Bold.ttf`) | 70 | **white**, `*keyword*` in **marigold `#F6C445`** | **no box, no outline, hard drop shadow 5 px at 85% black, no blur**; pop in 90 ms, fade out 120 ms | centre, **y 1060** (just above the caption band) |
| **End card** (`hook`) | Poppins Bold (`Poppins-Bold.ttf`) | 96 | white | outline 2 px; fade 60/100 ms | centre, **y 960**, on black |

- **One accent per text:** marigold only on the keyword of a label, sindoor only on the title.
- Emoji are never burned in (libass draws them monochrome); 🧡 👇 go in the post caption.
- Safe zones respected: nothing below y 1536 or right of x 950.
- Captions: max 4 words / 20 characters per page, a new page on a pause > 0.45 s or after punctuation, no lone filler
  words. `"until"` in the captions config clears the last caption before the fade to black.

## 3. Picture

| What | Setting |
|---|---|
| Talking head at home (warm ceiling light) | grade **`indoor`** (`luts/Isha_Indoor.cube`), iPhone HDR tone-mapped to SDR |
| Travel B-roll (sea, underwater, mountains) | grade **`natural`** (`luts/Isha_Natural.cube`) |
| Her photos (safari archive) | grade `none`, 9:16 fill with a slow 1.00→1.06 push-in, eased (`prep.py`) |
| Jump cuts | on every sentence; pauses inside a line cut out (2–4 frames of air) |
| Punch-in | **1.08–1.10** on every second cut from the same setup, to hide the jump |
| B-roll | L-cut over her voice, starts on the word that names the person/place, 0.9–2.1 s each |
| Transitions | hard cuts only, plus **one**: the 0.45 s fade to black at the end |

## 4. Sound
- Voice: high-pass 80 Hz, light denoise, 3:1 compression (pipeline default).
- **Music:** original, generated in code (`synth.py`), so there are no licence issues. Key D, raag Khamaj feel, 100 BPM:
  tanpura drone, santoor (two detuned strings + tremolo flourishes), dholak kaherwa theka, manjira, temple bell,
  claps in the finale.
- **Music arc:** bell + santoor alone on the hook → dholak and manjira enter on the first cut → **drums drop out on
  "Thank you…"** (santoor + drone only) → bell + full groove on "Happy Bhai Dooj!" → drums stop 1.3 s before the end
  → one soft D-major santoor strum + bell rings out.
- Music at **−17 dB** under the voice with sidechain ducking (20 ms attack / 250 ms release); 0.6 s fade-out.
- Final loudness **−14 LUFS**, true peak **−1.5 dBTP**.

## 5. Structure (timeline of the final cut)

| Time (s) | Picture | Words (Roman Hinglish, as spoken) |
|---|---|---|
| 0.00–1.04 | face + thali, title "HAPPY BHAI DOOJ / to my road bhais" (0–2.6) | Aaj Bhai Dooj, |
| 1.04–3.70 | face, punch 1.10 | aur mere paas ek nahi, bahut saare bhai. |
| 3.70–5.94 | face → boat (IMG_3978) | Aur mujhe ye sab travel karte hue mile. |
| 5.94–9.48 | face → **mountains, Isha walking in (IMG_0551 5.5–7.6)** | Mere woh bhai, jinhone mujhe pahadon mein ekdum safe rakha hai. |
| 9.48–14.86 | face → instructor fitting her gear (IMG_3971) → instructor holding her underwater (IMG_3976) → face; label "My **scuba** instructors" | Aur mere scuba instructors, jinhone mujhe 12 meter underwater kuch nahi hone diya. |
| 14.86–20.67 | face → tiger past the jeeps (photo) → face → tiger on the road (photo); label "My **safari** guide" | Aur mere safari guide, jinhone jungle ke beech-o-beech mujhe bahut crazy experiences karwaye. |
| 20.67–27.13 | friends huddle (IMG_3979); label "**Travel** friends · Lakshadweep" → face → fish school (IMG_3981) → face | Aur aise bahut saare log, jinhone mujhe apni behen maankar, aise crazy jagahon pe kuch nahi hone diya. |
| 27.13–30.29 | face, punch 1.10, music soft | Thank you for keeping me safe when I was far away from home. |
| 30.29–31.60 | face, tika finger to the lens → fade to black | Happy Bhai Dooj! |
| 31.46–33.15 | black + "TAG YOUR ROAD WALA BHAI" | (music rings out) |

Pattern to reuse: **hook line + title (0–2.6 s) → one line per person, each with their own B-roll and a label → the
emotional thank-you on her face with the music pulled back → payoff line → fade to black → call-to-action card.**

## 6. How it was built (reproducible)
```bash
python projects/bhai_dooj/prep.py                                        # photo B-roll, black clip, music.wav
python pipeline/isha.py render projects/bhai_dooj/edit.json --stage assemble
python projects/bhai_dooj/align.py                                       # words.json, end-card + caption cut-off times
python pipeline/isha.py render projects/bhai_dooj/edit.json --stage finish
python projects/bhai_dooj/make_board.py                                  # brand/06_client_approved_look.png
```

## 7. Notes for the next edit
- **Transcription without `models/ggml-small.bin`:** Hugging Face is blocked in the cloud sessions, but GitHub works.
  `pip install sherpa-onnx` + the whisper-small ONNX model from the sherpa-onnx GitHub release
  (`releases/download/asr-models/sherpa-onnx-whisper-small.tar.bz2`). Pad each clip with ~20 s of silence or the
  Hindi output gets cut short. Run Hindi and English passes and proofread both into Roman Hinglish. Never invent words.
- **Word timings:** that model gives no word times, so `align.py` places words inside each phrase's voiced span by
  syllable weight. Check caption timing at real speed.
- **iPhone 16+ MOVs** carry an extra Apple spatial-audio track (APAC) that ffmpeg can't decode; the pipeline now
  uses the normal AAC track automatically.
- People on screen need their OK before posting; labels say only the role until Isha gives the names.
- Brief asked for 25–30 s; this cut is 33 s because every recorded line is in. Trim a line if length matters.
