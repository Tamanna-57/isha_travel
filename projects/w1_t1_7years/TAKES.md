# W1-T1 · Tue 24 Nov · @travelwithisha · "7 years of 5 AM alarms" — take log (R2 album, 6 clips)

| Clip | Line | Takes | Used | Why |
|---|---|---|---|---|
| 1 | 7 saal ki wildlife photography, wo bhi ek hi reel mein, aur har subah ka ek hi rule: paanch baje ka alarm | 1 | **Only take** (3.40-10.62) | Split into 4 pieces: punch-in at "wo bhi" (first cut 1.9 s), pauses cut to ~0.3 s |
| 2 | "Kabhi ek wild dhole…" | 1 | — | False start ("cut") |
| 3 | Kabhi ek wild dhole mila… jackal… owl… aur ek din… ye | 1 full | **Take 1** (4.42-19.95) | 1.3 s pause before "aur ek din" cut; short beat kept before "ye" for the tiger reveal |
| 4 | Lekin the best moment kabhi ek photo nahi hota | 4 (3rd cut short) | **Take 4** (25.50-28.90) | Cleanest, steady eye line |
| 5 | Wo second hota hai, jab poora jungle ekdum shaant ho jaata hai | 3 (2nd cut short) | **Take 3** (21.25-25.25) | Says "second" (matches the script); + 0.8 s of real silence on the kingfisher shot |
| 6 | Aur iss baar tum mere saath chal rahe ho, through Lost & Free Safaris | 3 | **Take 3** (22.15-26.60) | Take 2 ends with an extra "See you" |

## Feedback from the Monday reel, applied here
- Bold Anton opening title, two-tone ("7 YEARS" marigold / "OF 5 AM ALARMS" white); same font for "5 AM." and "04 · THIS."
- Karaoke captions, important words highlighted (marigold, bigger); pages now break at sentence ends.
- Only Isha's own photos (archive zip): kingfisher with fish, nightjar, kite, dholes, jackal, owlet, tiger, kingfisher on moss. Numbered 01-04 so viewers can comment their favourite.
- Natural colour correction on her clips; 1.1x speed; every pause tightened.
- Frame-by-frame flash scan (qa_flash.py): no 1-3 frame flashes.
- SFX: shutter per montage photo, synthesised alarm beeps on "alarm", ticks on the numbered titles, riser + deep whoosh into the tiger, soft swooshes.
Rebuild: `python make.py --no-render && python sfx.py && python make.py`

## v2 · Isha's feedback (24 Nov)
1. **Less saturation:** her clips keep the natural grade, then saturation x0.85 (frame measure 0.30 → 0.27). Pipeline: clips take an optional "sat".
2. **Kingfisher on moss no longer dark/dull:** the original photo is very dark (avg luma ~36/255) and our crop cut the bird at the edge. Re-cropped so the whole bird is centred and bigger, lifted (gamma 1.45, saturation 1.3) → luma ~89; encoded with BT.709 tags.
3. **Nightjar shown whole (v3):** Isha: "use it as it is, the edges are black so it merges if you put it in the center". The photo is no longer cropped to fill; it's the full image centred on black (scaled 1.5x, trimming only vignette-black sides), so its black edges melt into the frame.
4. **Kingfisher more saturated (v4):** saturation 1.3 → 1.7 + vibrance 0.25 on that photo (frame saturation 0.43 → 0.65).
5. **More of her images (v5):** the opening montage on 'aur har subah ka ek hi rule' is now a 6-photo burst (~0.27 s each, shutter click per photo): kingfisher, mongoose, nightjar, harrier, little bird, duck. Mongoose, harrier, little bird and duck are new from her archive; the kite photo is out. 12 of her 21 archive photos are now in the reel.
