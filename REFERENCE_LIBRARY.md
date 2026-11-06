# Reference Library — what the reference reels actually do

Studied on 2026-10-23 in Chrome (logged-in Instagram). Each reel was frame-sampled every 0.2–0.33 s.
- **Cuts** were detected from frame-to-frame pixel change (threshold 28/255). Fast camera moves can register as cuts, so treat the counts as ±15%.
- **Luma and saturation** are averages over all sampled frames (8-bit).
- Some reels are DRM-protected (canvas reads black). Those were reviewed by stepping through the player and taking screenshots, so they have no numbers.

## Summary table

| # | Reel | Creator | Views | Len | Cuts | Avg shot | Luma (p5/mean/p95) | Sat | Format |
|---|---|---|---|---|---|---|---|---|---|
| R1 | [DbzscUISEci](https://www.instagram.com/reel/DbzscUISEci/) | iffy.explorer | — | 93.6 s | 36 | 2.6 s | 22 / 120 / 213 | .30 | A Story Walk |
| R2 | [DejsuOSzTcP](https://www.instagram.com/reel/DejsuOSzTcP/) | brindasharma | 320K | 41.4 s | 19 | 2.2 s | 23 / 105 / 188 | **.50** | A Story Walk |
| R3 | [DLkHzKDTe4L](https://www.instagram.com/reel/DLkHzKDTe4L/) | ronnie_and_barty | — | 25.4 s | 0 | single take | 29 / 101 / 212 | .30 | C Mood (single shot) |
| R4 | [DZPU1O1h_xO](https://www.instagram.com/reel/DZPU1O1h_xO/) | sailing_amrutha | — | 58.7 s | 49 | 1.2 s | 15 / 109 / 207 | .30 | A (day-in-life, brand) |
| R5 | [DeRR6iSh-vZ](https://www.instagram.com/reel/DeRR6iSh-vZ/) | bary__anastasiia | — | 12.1 s | ~12 (beat) | ~1.0 s | letterboxed | — | C Mood (letterbox lyric) |
| R6 | [Dc1F9HDv2-b](https://www.instagram.com/reel/Dc1F9HDv2-b/) | brindasharma | — | 47.3 s | 25 | 1.9 s | 20 / 98 / 206 | .30 | B Storytime |
| R7 | [DeMdFkxKgeo](https://www.instagram.com/reel/DeMdFkxKgeo/) | brindasharma | 462K | 55.6 s | 40 | 1.4 s | 21 / 110 / 209 | .30 | B Storytime (brand deal) |
| R8 | [Den1CxcTqLb](https://www.instagram.com/reel/Den1CxcTqLb/) | sayannath | 62K | 71.9 s | 59 | 1.2 s | 21 / 118 / 208 | .30 | A Story Walk + B-roll |
| V1 | [C7wJTJptchV](https://www.instagram.com/reel/C7wJTJptchV/) | sayannath | **10.3M** | 34.3 s | 23 | 1.5 s | **43** / 126 / 216 | .30 | C Cinematic |
| V2 | [DYV4sWJygu_](https://www.instagram.com/reel/DYV4sWJygu_/) | sayannath | **11.9M** | 41.1 s | DRM | long takes | — | — | D POV/Thrill |
| V3 | [DKKXrTVJOtT](https://www.instagram.com/reel/DKKXrTVJOtT/) | iffy.explorer | **10.3M** | 33.5 s | DRM | ~2 s | — | — | A Story Walk |
| V4 | [DGhschUS3Rm](https://www.instagram.com/reel/DGhschUS3Rm/) | sailing_amrutha | **21M** | 41.1 s | DRM | ~2 s | — | — | C Journey recap |
| V5 | [DD7OCAOvEIR](https://www.instagram.com/reel/DD7OCAOvEIR/) | brindasharma | **7.4M** | 58.1 s | 50 | **1.16 s** | 22 / 104 / 193 (warm R119 B89) | .40 | B Storytime |
| V6 | [DIOpmQvJ8iK](https://www.instagram.com/reel/DIOpmQvJ8iK/) | brindasharma | **6.6M** | 42.1 s | 13 | 3.2 s | 18 / 116 / 201 | .30 | A (BTS gag, rotated) |

**Averages across the measured reels:** shot length ≈ 1.8 s; blacks p5 ≈ 21; highlights p95 ≈ 205; saturation 0.30. These became the targets in `ISHA_REEL_SYSTEM.md §4`.

---

## R1 — iffy.explorer · "PoK / border terminology" explainer
- **Audio:** M. M. Keeravaani, *The King And His Sword* (cinematic score under the voice).
- **Shots:** all handheld selfie talking head in the Himalayas. Hard jump cuts on every sentence, location and outfit change across days (black puffer → beanie → maroon jacket). Cuts get denser after 55 s (every 0.6–1.2 s).
- **Captions:** transitional serif (Garamond/Playfair family). The **key word is big and white**, connecting words small in pale yellow, in reading order: "as China border / and **LoC**", "it is only **Pakistan-Occupied** / **Jammu** and". Centred at chest height, about 68% of frame height, no box, soft shadow.
- **Signature move:** **handwritten white marker notes** written on in the sky ("PoK Pakistan Tibet China", "LoC Border India-Pakistan"), with **red/yellow cross-outs** to correct a term ("~~Indo-China border~~ → INDO-TIBET"). Replaces graphics and makes facts feel personal.
- **Grade:** untouched-looking iPhone. Deep blue sky, warm skin, no LUT.

## R2 — brindasharma · "Japan mein cycling" (Asahikawa)
- **Shots:** 0.5x ultra-wide selfie (big sky, low angle), POV cycling with the basket in frame, hand-reveal shots (her hand in the foreground waving at the view), sun-flare shots, one whip/tilt transition near the end.
- **Titles:** heavy condensed sans **red** ("JAPAN", "CITY", "CYCLE'S") + overlapping white **script** word ("Mein", "the") + tiny red line-icon (bicycle). The red matches her red sweater, so the outfit is part of the palette.
- **Captions:** small **ALL CAPS** wide-tracked white sans (Montserrat-like), centred at about 73% height. They stay in the same spot over B-roll while the voiceover continues.
- **Grade:** vivid golden-hour, saturated blue sky (sat 0.50, the most saturated in the set), warm skin.

## R3 — ronnie_and_barty · monsoon clouds (Lizzy McAlpine, *To the Mountains*)
- One **sideways (rotated 90°)** landscape take, 25 s, no cuts, no on-screen text. Clouds roll over a green Himalayan slope while a tiny person in red walks through the frame for scale.
- The story is entirely in the post caption (reflective paragraph). Pure mood; the rotation makes people tilt their phone.

## R4 — sailing_amrutha · "Day in my life on a sailboat" (Lenskart B glasses, paid)
- **Title:** two-tier bold geometric sans: small "Welcome to" over a big **"DAY IN MY LIFE"**, then a small "on a sailboat". The brand intro uses the same pattern: small "through", big **"B by Lenskart"**.
- **Mix of** selfie and glasses-POV footage (4:3, letterboxed, with a "SHOT ON" badge). Quotes appear in a dark pill ("Hey Buddy").
- **Captions:** small white sans, sentence case, at about 82% height (a bit low). Fast 1.2 s average shot.

## R5 — bary__anastasiia · *Come Together* lyric reel (The Beatles)
- **Letterboxed** ~1.8:1 horizontal footage centred on black in a 9:16 frame. Cinematic and editorial.
- **Kinetic lyric type:** "One thing / I can / Tell you / Is / You **Got** To / Be", with each word popping on its syllable. Mixed condensed/high-contrast serif, upright and *italic*, different sizes, scattered layout. Then **"FREE"** in giant fat red slab serif, shrinking into outlined echoes.
- B-roll cut on the beat (~1 s): coast lookout, lighthouse, wind in a white outfit, surfers, kitesurfer.

## R6 — brindasharma · Orca snorkelling Part 2 (Norway)
- **Cold open:** 16:9 action footage **letterboxed** in the middle of a black frame, with the caption "What **Happened?**".
- **Storytime set:** desk, RGB podcast mic, warm room, plants on the shelf behind.
- **Captions:** left-aligned stacked block: light small words + **ExtraBold pale-yellow key word** ("Itna / **Expensive** / Tha", "Ship / For / **Five** / Days"). Left-centre placement beside the mic.
- **Map:** 3D globe zoom (Tromsø → Arctic Ocean, "+847 km") in a **rounded card on cream background**.
- About 50% B-roll (ship, orcas, sunsets), with the caption system continuing over it.

## R7 — brindasharma · IndiGo BluChip (paid partnership)
- Desk talking head with captions at the **top** (above her head): white sans with **yellow italic serif highlight words** ("I *booked* my *flights* to Bangkok", "*people* still").
- **Green-screen swaps:** she's cut out over B-roll (IndiGo plane, aircraft seats, restaurant).
- Brand logo card ("Earn IndiGo BluChips"), flight-path map animation on a satellite globe.

## R8 — sayannath · "Manifestation is real" (Richy Mitch & the Coal Miners, *Evergreen*)
- Walk-and-talk on a cliff path with a persistent **white pill hook at the top** for the whole reel: "This video will find you when the time is right 🙏".
- Tiny single-word white captions at chest level (unobtrusive).
- **B-roll as proof:** a news article screenshot with yellow-highlighter on the key sentence, celebrity interview clips with a bold yellow **"MANIFESTATION"** label, vision-board stock shots, his own past clips (studio, waterfall, cave). Cuts every ~1.2 s.

## V1 — sayannath · Kyrgyzstan (10.3M) ★
- **Concept hook:** a lone door frame standing in an empty steppe; he walks through it, "portal to another world". Black pill at the top: "This **country** is 'Sukoon'" (the keyword is red).
- **"KYRGYZSTAN"** in classic roman serif caps over 4 consecutive drone shots (lake, river canyon, red rocks, frame-in-landscape).
- **Captions:** warm **orange-gold serif**, two-tier ("The **world**", "has **amazing**", "**Indian** rupees").
- **Grade:** filmic, lifted blacks (p5 43, the only filmic one), muted greens, soft contrast. This is the `film` preset.

## V2 — sayannath · China cliff walk (11.9M) ★
- POV on a plank walkway over a drop. Top text in bold white sans with an emoji: "One wrong move and you'll meet the creator 😂". Then a selfie with a helmet, and the feet-on-ladder POV.
- Trending Bollywood remix. Barely any edit, which is the point: the visual does the work.

## V3 — iffy.explorer · Chenab Rail Bridge (10.3M) ★
- Walks toward the camera on the bridge deck. **Same serif two-tier captions as R1** ("World's / **highest railway bridge**"), so the caption style is her brand.
- **Landmark title:** yellow-lime condensed italic bold "CHENAB RAIL BRIDGE" + white small-caps subtitle "District Reasi, Jammu Division of J&K" + 🇮🇳.
- Fact caption ("1178 ft above Chenab River"), playful poses, drone shot of the bridge.

## V4 — sailing_amrutha · India → Africa sailing anniversary (21M) ★
- Raw night/cabin footage, red night-light, sunsets on deck.
- **Animated route map** (boat icon travelling a white path, Lakshadweep → Arabian Sea → Djibouti).
- **Typewriter monospace captions**, lowercase, small, centre-low ("we started sailing from", "made us more vigilant"). Feels like a journal or documentary.

## V5 — brindasharma · "the song on repeat" (7.4M) ★
- Emotional confession at home under warm tungsten (orange walls, R119 vs B89). **Fastest pacing in the set: 1.16 s average shot**, with jump cuts mid-sentence.
- **Karaoke captions:** Poppins-style SemiBold white, with the spoken words white and the upcoming ones grey ("Trip pe Jaa*ne*").
- Lyric lines quoted over B-roll in small regular sans with quotes (*"Beech Mein Ruk Jayega"*): motorbike POV in Ladakh, two riders on an empty road.

## V6 — brindasharma · "pahad ya samundar?" BTS (6.6M) ★
- She poses at Key monastery (Spiti) while a camera crew shoots. **Picture-in-picture** of the resulting photo pops in. Then **rotated 90° BTS footage** of the photographer, a playful gag.
- Shows the second time a deliberately sideways frame went viral in this set.

---

## Patterns that repeat (and therefore matter)

1. **Two-tier captions** (small connective words + big key word) appear in iffy (R1, V3), brinda (R6), sayannath (V1) and sailing titles (R4). This is the strongest shared typographic signal, so it's Isha's default.
2. **Serif for storytelling, sans for chatter.** Serif shows up on the more "documentary" reels (iffy, sayannath Kyrgyz); sans on the conversational ones (brinda storytime).
3. **Big place/chapter title** in nearly every travel reel: condensed caps (brinda, iffy) or roman caps (sayannath).
4. **Letterbox bands** are used for cold opens (R6) and the cinematic mood (R5).
5. **Rotated 90° frames** went viral twice (R3, V6).
6. **Maps:** globe zoom (R6, R7) and route map (V4) whenever distance or place matters.
7. **Hand-made graphics beat templates:** handwritten marker (R1), highlighter on article screenshots (R8).
8. **The grade is never a heavy filter.** Natural phone colour with warm skin; only one reel (V1) goes filmic.
9. **The voice carries the reel.** Music is score-like underneath, except mood (C) and POV (D) reels, where the song is the voice.
