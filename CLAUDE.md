# Isha — reel editing workspace

Client: **Isha**. Short-form (Instagram Reels) editing in the style of the reference creators
(iffy.explorer, brindasharma, sayannath, sailing_amrutha, ronnie_and_barty, bary__anastasiia).

When the user sends clips (or says "edit this"), follow **`ISHA_REEL_SYSTEM.md`**. It is the source of truth for
formats, captions, titles, grade, audio, export and QA. Evidence for each rule: `REFERENCE_LIBRARY.md`.
Tooling: `pipeline/isha.py` (see `pipeline/README.md`). Brand assets: `fonts/` (29 static TTFs, loaded automatically),
`luts/` (grade looks as .cube), `brand/` (visual boards + safe-zone overlay), `templates/` (edit.json per format A–D),
`models/ggml-small.bin` (whisper). After changing any style in isha.py, re-run `pipeline/brandkit.py` so the boards stay true.

Workflow every time:
1. Put clips in `inbox/<reel>/`, then `probe` + `sheet` them and look at the sheets.
2. Confirm the topic, the one-line takeaway and the format (A story walk / B storytime / C cinematic / D POV) with the user.
3. Write `projects/<reel>/edit.json`. `render --stage assemble`, review `build/assembled_sheet.png`.
4. `transcribe` the assembled cut, then proofread `words.json` into Roman Hinglish. Never invent words.
5. `render --stage finish` → check QA output + stills → deliver `out/` paths. Ask the user to watch at real speed.

Rules: hard cuts by default, at most one special transition, captions always on (1–4 words, two-tier),
one chapter title, natural grade, −14 LUFS, safe zones (no text below y=1536 or right of x=950).
