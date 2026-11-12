# P2 · Carousel — Kalpa · Chitkul · Tosh (9 slides, 1080×1350)

**Account:** @travelwithisha · **Post:** Tue, 7:00 PM IST · **Format:** 9-slide carousel, 3 slides per village

## Design (matches the `anton.cltx` reference)
- Full-bleed photo, natural grade, **photo stays dominant**.
- **Minimal serif text in the top ~22% only** — the rest of the frame is clean.
- **One font**, Playfair Display: upright for titles/body, italic for kickers & subtitles.
- **Two colours only** — white or near-black, chosen per slide for contrast with the sky.
- No accent colour, no handwriting, no handle bar / counter / "swipe" chrome. Only slide 9 carries a
  small centred `@travelwithisha`, like the reference end card.

Rendered slides: `out/slide_01.png … slide_09.png`. Proof: `out/contact.png`. All photos are Isha's own,
pulled from the three shared albums (video stills and screen-grabs were skipped).

## Copy, slide by slide
1. **Kalpa (cover)** — *3 Himachal villages that feel like another planet* · "swipe for the ones that made me forget what day it was →"
2. **Kalpa** — *Kalpa* · "Wake up to the Kinnaur Kailash range turning gold, right from your window."
3. **Kalpa** — *if you go* · "Stay up in old Kalpa, and walk to Roghi for the viewpoint they call 'Suicide Point'."
4. **Chitkul** — *Chitkul* · "the last inhabited village before the Indo–Tibet border"
5. **Chitkul** — *the Baspa valley* · "The cleanest air I've ever breathed, and a silence that makes you forget your phone exists."
6. **Chitkul** — *if you go* · "Eat at the last dhaba of Hindustan, and come May–October, before the snow shuts the road."
7. **Tosh** — *Tosh* · "where Parvati valley simply runs out of road"
8. **Tosh** — *the mood* · "Slow mornings, chai with a snow-peak view, and nowhere you have to be."
9. **Tosh (end)** — *Which one are you saving for 2027?* · "tell me below — and save this for the trip" · @travelwithisha

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
| `chitkul_3.jpg` | 6 | Green-roof homestay / cafe |
| `tosh_1.jpg`    | 7 | Tosh village on the slope |
| `tosh_2.jpg`    | 8 | Cafe menu, snow-peak balcony |
| `tosh_3.jpg`    | 9 | Golden alpenglow peak |

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
