# Leave Mumbai reel (R1) — rebuilt from Isha's raw clips

**Final:** `out/leave_mumbai.mp4` (39.1 s at 1.08×, 1080×1920, 30 fps, −12 LUFS) + `_clean.mp4`, `.srt`, `_cover.png`.

Raw clips: the client's Google Photos album → `inbox/leave_mumbai/LM_01–12.MOV` (4K HDR, 60 fps; not in git).
Target edit: `bhai dooj/R1_LeaveMumbai_C_captions_sfx_transitions_original_color.mp4`, used only as the
reference for shot order. Every reference moment was matched to its raw clip by audio cross-correlation.
The reference had sped up and clipped her words (source ran 10–15 % faster than the edit); this cut is at her
natural speed and every cut sits in a real pause, so no word is clipped. Hence 42 s instead of 35 s.

## Build
```bash
python projects/leave_mumbai/prep.py                                        # chart + logo overlays, music
python pipeline/isha.py render projects/leave_mumbai/edit.json --stage assemble
python projects/leave_mumbai/align.py                                       # words.json (hand-set page breaks)
python pipeline/isha.py render projects/leave_mumbai/edit.json --stage finish
```

## Look (client-approved Bhai Dooj look, `projects/bhai_dooj/REEL_SPEC.md`)
- **Captions:** karaoke, Poppins SemiBold 115, grey → white as spoken, y 1340. Every page break is set by
  hand ("|" in `align.py`) so each page is one natural phrase. **Keywords** (`*word*` in `align.py`, one per page:
  Mumbai, koshish, city, love, unlivable, mangroves, rivers, respect, Diwali, pollution, 13, 20, polluted, India,
  request, exactly, kidhar, saans, jungle, Lost & Free Safaris, chalna, soon) in Playfair Display Bold Italic, marigold.
- **Hook (0–2.6 s):** label "every morning, I want to" (Playfair Bold, hard shadow) over **LEAVE MUMBAI** (Anton, sindoor).
- **Chart (21.7–25.8 s):** IQAir 2024 donut, India 13 of the world's 20 most polluted cities, "India's air: over
  10× the WHO safe limit", small source credit. Data: IQAir 2024 World Air Quality Report.
- **Lost & Free Safaris (37.4–41.6 s):** official logo card (`projects/safari/assets/logo.png`, brand olive,
  @lostandfree), pops in with a soft pop. Caption "Lost & Free Safaris" (she says "Lost & Free"; "Safaris"
  added as the brand name, per the client).
- **Grade:** `lift` (luma contrast +6 %, +1 % brightness, +3 % saturation, fine sharpening): no warmth change,
  so she isn't pale or yellow.
- **Music:** original calm pad with a soft pulse (gentle kick + light shaker) at −17 dB, ducked under her voice;
  opens up on "main jungle jaati hoon". **SFX:** quiet air whoosh (−21 dB) on each room change, soft pop on the
  chart and the logo card.
- **Structure:** 16 clips, hard cuts, punch-ins 1.08 on every 2nd cut from the same setup. It ends on "main har
  roz uthke…" and loops into "yahi sochti hoon", the cut on a clean silence.

| # | Raw clip | Source in–out | Words |
|---|---|---|---|
| 1–2 | LM_02 | 19.92–21.60, 22.06–24.02 | yahi sochti hoon ki bas, ab toh Mumbai chhod hi dena chahiye |
| 3–4 | LM_03 | 22.88–27.60 | main phir bhi rukne ki poori koshish karti hoon because it's my city you know and I love it |
| 5 | LM_04 | 4.45–8.00 | but honestly, Mumbai has become unlivable |
| 6–7 | LM_05 | 1.25–7.98 | mangroves are being cut … hi nahi karta hai yaar |
| 8 | LM_06 | 5.86–9.10 | aur har Diwali pollution aur bhi zyada badh jaata hai |
| 9 | LM_07 | 18.45–22.55 | 13 out of the world's 20 most polluted cities are in India |
| 10–12 | LM_11 / LM_10 | LM_11 15.75–17.93 (take 3) · **LM_10 3.27–6.07 (take 4: the clear "kiya kya hai"; takes 1 and 3 sound like "kiya kahan hai")** · LM_11 20.89–23.42 (take 3, starts on "aur") | toh is saal meri sirf ek request hai · bas itna socho ki, humne kiya kya hai · aur ye sab humein laaya kidhar hai |
| 13–16 | LM_12 | 6.27–11.82, 12.50–15.20 | aur jab saans lene ki jagah chahiye ho, main jungle jaati hoon, Lost & Free ke saath, aap bhi chalna? details coming out soon |
| 17 | LM_02 | 19.03–19.92 | main har roz uthke… |
