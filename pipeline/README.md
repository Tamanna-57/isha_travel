# Isha reel pipeline

`isha.py` turns raw clips + an `edit.json` cut list into a finished reel in the house style
(`../ISHA_REEL_SYSTEM.md`). It needs only ffmpeg/ffprobe (v9 full build with libass and whisper), Python 3, numpy and Pillow.

```
isha/
  ISHA_REEL_SYSTEM.md     the rulebook (formats, tokens, captions, grade, audio, shooting, QA)
  REFERENCE_LIBRARY.md    what each reference reel does, with measurements
  brand/                  visual boards (type, palette, captions, titles, grades) + safe-zone overlay
  fonts/                  29 static TTFs (9 Google families, OFL) — flat, libass reads only this level
    licenses/             OFL licence per family
    _variable_sources/    original variable fonts (static weights are cut from these)
  luts/                   Isha_Natural/Golden/Indoor/Film .cube (33-pt) + _64.cube
  models/ggml-small.bin   whisper.cpp model for transcription (multilingual)
  templates/              starting edit.json for formats A–D
  inbox/<reel>/           raw clips land here
  projects/<reel>/        edit.json, words.json, build/ (intermediates), out/ (deliverables)
  pipeline/
    isha.py               the pipeline
    calibrate_type.py     re-derive font sizes from reference width shares
    brandkit.py           re-render brand/ boards (run after changing styles)
    make_luts.py          re-bake luts/ from the grade presets
    make_static_fonts.py  cut static weights from fonts/_variable_sources
```

## Commands
```bash
python pipeline/isha.py probe inbox/goa/*.MOV            # fps / VFR / HDR / rotation / audio per clip
python pipeline/isha.py sheet inbox/goa/IMG_0042.MOV     # contact sheet PNG to see the clip
python pipeline/isha.py beats music/track.mp3            # BPM + beat times -> music/track.beats.json (format C)
python pipeline/isha.py render projects/goa/edit.json --stage assemble   # cut only (fast check)
python pipeline/isha.py transcribe projects/goa/build/assembled.mov --out projects/goa/words.json
#   -> proofread words.json (Roman Hinglish, names), mark key words with "emph": true if needed
python pipeline/isha.py render projects/goa/edit.json --stage finish     # captions, titles, mix, loudness, QA
python pipeline/isha.py qa projects/goa/out/goa.mp4 --format A           # re-run QA on any file
```
`render` with no `--stage` runs everything. Outputs land in `projects/<reel>/out/`:
- `<name>.mp4`
- `<name>_clean.mp4` (no captions or titles)
- `<name>.srt`
- `<name>_cover.png`
- `<name>_qa_sheet.png`

### Transcription
Transcription takes about 5× the clip length on this CPU with `ggml-small.bin` (roughly 5 minutes for a 60 s reel). The default `--lang en` gives Roman text, which we proofread into Hinglish. Use `--lang hi` only if you want Devanagari. Whisper's non-speech tags (`[Music]`, `(laughs)`, `♪`) are dropped, both when transcribing and again when captions are rendered.

### Beats (`beats`)
- Prints the BPM and writes the beat times. Use them to set clip lengths to 1 or 2 beats in format C.
- **Tempo:** onsets are measured in 40 log-spaced frequency bands with equal weight, so busy hi-hats can't drown the kick. A tempo prior around 110 BPM breaks 2:3 and 4:5 ambiguities.
- **Beat positions:** dynamic-programming beat tracking (Ellis 2007).
- **Phase check:** if very loud off-beat hats or snares pull the grid half a beat off, the beats are moved back onto the kick/bass hits. The output says `(phase moved to the kick/bass hits)` when this happens.
- **Bench, 2026-10-24:** 9 synthetic tracks with known beats (kick only, off-beat hats, pop groove, 16th hats at 140, late start, acoustic ballad at 76, house at 128, two extreme off-beat stress tests).
  - Tempo within 0.5 BPM.
  - 96–100% of beats within 50 ms.
  - Timing bias within ±5 ms, under a sixth of a frame.

  Real songs with swing, rubato or no percussion can still trip it. Glance at the cut points against the waveform before locking a beat-cut reel.

### QA (`qa`, also run at the end of `render`)
- **Always checked:**
  - 1080×1920
  - 30 fps CFR
  - BT.709 tags
  - −14 ±1 LUFS
  - true peak ≤ −1 dBFS
  - first cut ≤ 2.5 s
- **With `--format` (or the edit's `"format"`):** reel length and average shot length against that format's target.

  | Format | Length | Avg shot |
  |---|---|---|
  | A | 35–75 s | 1.5–2.5 s |
  | B | 40–60 s | 1.1–2.0 s |
  | C | 12–35 s | 0.8–1.5 s |
  | D | 10–25 s | ≥ 1.5 s |
- **Output:** writes a contact sheet.

## edit.json
Paths are relative to the project folder. All times are in seconds. Title and caption times are on the **final timeline**.

```jsonc
{
  "name": "goa-sunset",
  "format": "A",                       // A story walk | B storytime | C cinematic | D POV (also sets QA targets)
  "grade": "natural",                  // natural | golden | indoor | film | none (default for every clip)
  "clips": [
    {
      "src": "../../inbox/goa/IMG_0042.MOV",
      "in": 3.20, "out": 5.10,         // source in/out
      "punch": 1.12,                   // 1.0–1.15 scale-in (hide jump cuts)
      "speed": 1.0,                    // 0.25–4, audio pitch-preserved; slow-mo from 60 fps keeps every frame
      "frame": "fill",                 // fill | letterbox | letterbox_wide | blur | card
      "rotate": 0,                     // 90 / -90 / 180 (the deliberate sideways look)
      "audio": true, "gain_db": 0,     // false = silent clip (music only)
      "grade": null,                   // per-clip override
      "wb": null,                      // "auto" = grayworld white balance before the look
      "broll": [                       // L-cut: picture switches to B-roll, this clip's voice continues
        {"src": "../../inbox/goa/IMG_0050.MOV", "in": 1.0, "at": 0.8, "dur": 1.4, "grade": null}
      ],
      "transition": "cut",             // INTO this clip: cut | dissolve | flash | whip | whip_right | zoom
      "transition_dur": 0.2
    }
  ],
  "captions": { "style": "serif", "words": "words.json", "y": null, "enabled": true },
              // serif | sans | karaoke | caps | top | typewriter
  "titles": [
    {"type": "chapter",  "text": "Goa", "script": "mein", "start": 1.2, "end": 3.0,
                         "color": "sindoor", "script_color": "chalk"},
    {"type": "landmark", "text": "Dudhsagar Falls", "sub": "Goa–Karnataka border", "start": 9, "end": 11.5, "color": "marigold"},
    {"type": "place",    "text": "Kyrgyzstan", "start": 5, "end": 7},
    {"type": "pill",     "text": "This *country* is 'Sukoon'", "start": 0, "end": 4},
    {"type": "hook",     "text": "One wrong move and you'll meet the creator", "start": 0, "end": 3},
    {"type": "fact",     "text": "1178 ft above Chenab River", "start": 12, "end": 14, "color": "marigold"},
    {"type": "label",    "text": "My *scuba* instructors", "start": 9.9, "end": 13.8},   // no box, soft glow
    {"type": "marker",   "text": "PoK  Pakistan\nTibet. China", "start": 0.3, "end": 3,
                         "x": 540, "y": 300, "rotate": -3, "color": "chalk", "size": 149, "strike": false}
  ],
  "music": { "src": "../../music/track.mp3", "start": 0, "gain_db": -18, "duck": true },
  "voice": { "clean": true }
}
```

### Titles
- **Colours:** every `color` / `script_color` takes a brand token (`chalk`, `ivory`, `marigold`, `sindoor`, `saffron`, `ink`, `paper`, `grey`) or a hex value like `"#C62828"`. For example, match the chapter title to Isha's outfit.
- **Default positions (y of 1920):**

  | Title | y |
  |---|---|
  | chapter | 370 |
  | landmark | 280 |
  | pill | 300 |
  | hook | 260 |
  | marker | 330 |
  | place | 960 |
  | fact | 1090 (just above the caption band, so a fact and a caption can share the screen) |
  | label | 1090 (same band as fact) |

  Any title takes an explicit `"y"`.
- **With `top` captions:** the top-anchored titles (chapter, landmark, pill, hook, marker) move down 300 px automatically so they don't collide with the captions. An explicit `"y"` always wins.
- **Auto-fit:** chapter, landmark and place titles shrink so they stay on one line inside the 78% safe width.

### words.json
```json
[{"text": "Japan", "start": 0.82, "end": 1.20, "emph": true}, {"text": "mein", "start": 1.20, "end": 1.45}]
```
- Word-level, in timeline time.
- `emph` forces the big/accent treatment. Without it the longest non-filler word per page is picked; Hinglish fillers like *hai, toh, ka, mein* are never emphasised.
- Pagination never ends a page on *the/of/ka/ki* and never leaves a filler word alone.

## Notes
- **Footage handling:**
  - iPhone HDR (HLG/PQ) is detected and tone-mapped to SDR BT.709 automatically.
  - VFR and retimed footage is conformed to 30 fps.
  - Rotation metadata is honoured.
- **Font weights:** libass only tells Regular from Bold inside a family. So in-between weights are called by their own family names ("Playfair Display SemiBold", "Poppins ExtraBold", "Poppins Light", "Cinzel SemiBold", …) via `FONT_ROLES` in `isha.py`. If a font file is missing, that role falls back to a Windows font.
- **Font sizes:** calibrated to the references with `calibrate_type.py`. Re-run it after changing any font, then copy the sizes into `SIZE` in `isha.py` and re-run `brandkit.py`.
- **Emoji:** burned-in text uses libass, which won't render colour emoji. Keep emoji in the post caption.
- **Made outside the pipeline:** kinetic lyric type, globe zooms and "green-screen" cut-outs are made in CapCut, Google Earth Studio or After Effects, then dropped in as clips (`frame: card` or `fill`).
- **Other drives:** clips or models on another drive work; filter paths fall back to escaped absolute paths.
- **Verified 2026-10-23:**
  - **Synthetic edit:** 6 clips, every frame mode, flash and whip transitions, all caption styles and titles. QA passed: −13.9 LUFS, 30 fps CFR, BT.709.
  - **Speech run:** TTS speech → Whisper → serif captions + landmark title + B-roll L-cut. All 23 words transcribed correctly at −14.0 LUFS.
- **Verified 2026-10-24:**
  - **Edge-case edit:** HDR HEVC 10-bit, 60 fps → 0.5× slow-mo (all 60 frames kept), a rotation-metadata clip, VFR with no audio, a vertical clip in letterbox mode, top captions with a hex-coloured chapter title, and a fact line. All rendered and QA passed.
  - **LUT check:** `.cube` LUTs match the pipeline grade within about 1/255 on average (worst 3/255).
  - **Beat bench:** see the Beats section above.
