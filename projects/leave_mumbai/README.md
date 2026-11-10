# Leave Mumbai reel (R1) — caption + grade revamp

Source: `bhai dooj/R1_LeaveMumbai_C_captions_sfx_transitions_original_color.mp4` (35.1 s, the client's edit with
captions, SFX and transitions burned in). The edit stays as it is; only the text layer, the grade and the
Lost & Free moment change.

**Waiting on:** the same edit exported **without any text** (no captions, no title, no source line, no
@lostandfree / "count me in" tags) → save as `bhai dooj/R1_LeaveMumbai_NO_CAPTIONS.mp4`, then
`python projects/leave_mumbai/make.py`.
Draft until then: `detext.py` removes the old text from the captioned file (inpainting, no blur), then
`make.py --preview` renders on that.

## What changes
- **Captions:** the client-approved karaoke look (Poppins SemiBold 115, grey → white as spoken, hard drop shadow,
  no box, y 1340), with a twist for this reel's mood (city rant → plan): one **punch word per page** in Poppins
  ExtraBold **marigold**; single-word pages bigger (*unlivable*). Words are her exact words from the previous
  proofread captions; page times read off the old captions (±0.12 s).
- **Hook title (0–2.9 s):** "every morning, I want to" (Allura, white) over **LEAVE MUMBAI** (Anton, sindoor).
- **IQAir chart (18.1–21.6 s), replaces the source text line:** paper card, animated donut: India 13 of the world's
  20 most polluted cities (sindoor) vs rest of the world 7 (grey), "India's air: over 10× the WHO safe limit"
  (India avg PM2.5 50.6 µg/m³ vs WHO 5), small source credit. Data: IQAir 2024 World Air Quality Report.
- **Lost & Free Safaris (30.9–34.0 s):** one caption "Lost & Free Safaris ke saath, aap bhi chalna?" (she says "Lost & Free";
  "Safaris" added as the brand name, per the client) + a pop-up card: the official logo
  (`projects/safari/assets/logo.png`) on the brand olive, "@lostandfree" under it, top-left, pops in with a soft pop sound.
- **Grade:** luma-only contrast +6%, brightness +1%, saturation +3%, light sharpening. No warmth change; skin R/B
  within 0.06 of the original on test frames, so she doesn't look pale, orange or oversaturated.
- Audio: her mix as delivered (−14.2 LUFS), plus the one pop.
