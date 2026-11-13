# P2 · Carousel — Kalpa · Chitkul · Tosh (9 slides, 1080×1350)

**Account:** @travelwithisha · **Post:** Tue, 7:00 PM IST · **Format:** 9-slide carousel, 3 slides per village

## Design — v2 (bolder, swarikaandaditya reference)
- Full-bleed photo, natural grade, **photo stays dominant**. **10 slides** (Tosh has 4, incl. stargazing).
- **Bold Poppins display type**, text anchored **top-left**, minimal.
- **Bright yellow accent** on the title + kicker (leans a touch warmer/gold on golden skies), with a
  strong dark drop-shadow so it pops on any photo; clean white body beneath.
- No handle bar / counter / "swipe" chrome. Only the end slide carries a small `@travelwithisha`.
- (v1 — the thinner Playfair serif, centred, white/black — is kept in git history if we want it back.)

Rendered slides: `out/slide_01.png … slide_10.png`. Proof: `out/contact.png`. Photos are Isha's own.

## Copy, slide by slide (v2, in Isha's voice)
1. **Kalpa (cover)** — *himachal, india · 3 villages that feel like another planet* · "the ones that made me forget the sea — swipe"
2. **Kalpa** — *Kalpa* · "Opened my window and the whole Kinnaur Kailash range was gold. Still not over that morning."
3. **Kalpa** — *if you're going* · "Stay up in old Kalpa, not Reckong Peo. Walk to Roghi for the viewpoint — knees shaking, so worth it."
4. **Chitkul** — *Chitkul* · "the last village before the Indo–Tibet border. The road literally just ends here."
5. **Chitkul** — *what stayed with me* · "Cleanest air I've ever breathed, the Baspa roaring, and the kind of quiet that makes you put the phone down."
6. **Chitkul** — *where to stay* · "Grab a riverside camp right on the Baspa. Falling asleep to the river rushing past is the whole point."
7. **Tosh** — *Tosh* · "where Parvati valley runs out of road and you finally just… stop."
8. **Tosh** — *the whole mood* · "Slow mornings, chai with a snow-peak in your face, nowhere to be. Didn't check the time once."
9. **Tosh (stargazing)** — *don't sleep early* · "Lights out and the whole Milky Way just shows up. Tosh has some of the clearest night skies I've ever seen."
10. **Tosh (end)** — *Which one are you saving for 2027?* · "tell me below, and save this — future you will thank you." · @travelwithisha

### Confirm in your own words if you have them (I kept these factual, not invented)
- **Slide 3:** where you actually stayed in Kalpa.
- **Slide 6:** whether you ate at the last dhaba.

## Photos used (Isha's own)
| File | Slide | What it is |
|---|---|---|
| `kalpa_1.jpg`   | 1 | Isha + the Kinnaur Kailash range (cover / thumbnail) |
| `kalpa_2.jpg`   | 2 | Golden Kinner Kailash spire |
| `kalpa_3.jpg`   | 3 | Railing viewpoint over the valley |
| `chitkul_1.jpg` | 4 | Chitkul village street under the snow massif |
| `chitkul_2.jpg` | 5 | Isha on a boulder by the Baspa |
| `chitkul_3.jpg` | 6 | Riverside camp / stay on the Baspa |
| `tosh_1.jpg`    | 7 | Tosh village on the slope |
| `tosh_2.jpg`    | 8 | Cafe menu, snow-peak balcony |
| `tosh_4.jpg`    | 9 | Milky Way night sky (stargazing) |
| `tosh_3.jpg`    | 10 | Golden alpenglow peak (end card) |

## Post caption
> Not everything I love is underwater 🏔️
>
> Kalpa, Chitkul and Tosh: three villages in Himachal that made me forget what day it was. Swipe for the tips I wish I'd had.
>
> Save this for your next mountain trip, and comment the one you'd pick first 👇
>
> #himachal #kalpa #chitkul #tosh #kinnaur #parvativalley #spiti #mountainsofindia #incredibleindia #travelwithisha

## Stories
Poll: **"Mountains 🏔️ or ocean 🌊?"** — results feed the safari-week stories.

## To render
```bash
python projects/himachal_carousel/make.py
```
Edit copy in `slides.json`; swap a photo by replacing the matching file in `photos/`.
