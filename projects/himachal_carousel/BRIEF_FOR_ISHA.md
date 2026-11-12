# P2 · Carousel — Kalpa · Chitkul · Tosh (9 slides, 1080×1350)

**Account:** @travelwithisha · **Post:** Tue, 7:00 PM IST · **Format:** 9-slide carousel, 3 slides per village
**Design:** full-bleed photo + text in the upper third (the `anton.cltx` reference style), Isha type system
(Anton titles, Playfair serif lines, **Caveat** handwritten notes in marigold), natural grade, text inside the 4:5 safe area.

The proof in `out/contact.png` is rendered with the **real brand fonts** but with **placeholder backgrounds**,
because the Google Photos links don't open from this workspace. Each placeholder prints the photo it needs,
so this file + the proof double as the shot list. Drop the 9 photos in `photos/` and re-render — that's it.

---

## The 9 photos needed (put in `projects/himachal_carousel/photos/`)

| File | Slide | What it should be |
|---|---|---|
| `kalpa_1.jpg`   | 1 (cover) | Best **wide** mountain photo **with Isha in it**, Kinnaur Kailash behind, morning. This is the post thumbnail. |
| `kalpa_2.jpg`   | 2 | Kinnaur Kailash peaks at **sunrise** (golden glow), or Isha looking out at them. |
| `kalpa_3.jpg`   | 3 | Old Kalpa character: apple orchard, old wooden houses, the monastery/temple, or the Roghi road. |
| `chitkul_1.jpg` | 4 | **Wide** Baspa valley + Chitkul's wooden houses (Isha in frame if you have one). |
| `chitkul_2.jpg` | 5 | The Baspa river, or Isha by the river / in the potato fields. |
| `chitkul_3.jpg` | 6 | The 'Last Dhaba of Hindustan' board, the Mathi Devi wooden temple, or food by the river. |
| `tosh_1.jpg`    | 7 | **Wide** Tosh on the slope with the snow peaks at the head of Parvati valley. |
| `tosh_2.jpg`    | 8 | Cafe/balcony view over the valley, chai or maggi in hand, snow peaks behind. |
| `tosh_3.jpg`    | 9 | Strong **closing wide** — Isha with the valley behind her, or peaks at golden hour. |

Portrait/vertical photos frame best, but any orientation works (the renderer center-crops to 4:5).

---

## The copy, slide by slide (tweak any line, then re-render)

1. **KALPA** (cover) — kicker *"3 Himachal villages that feel like another planet"* · title **KALPA** · *start here →*
2. **the view** — "I woke up to the whole Kinnaur Kailash range turning gold — straight from the window, no filter, no crowd." · note: *that tall one is Kinner Kailash, ~6,050 m*
3. **if you go** — tip: *"Stay up in old Kalpa, not down in Reckong Peo. Walk to Roghi village for the view they call 'Suicide Point' — the drop is unreal. Mornings in Apr–Jun give the clearest peaks."*
4. **CHITKUL** — "the last inhabited village before the Indo–Tibet border"
5. **why it stays with you** — "The Baspa running ice-cold, the cleanest air I've ever breathed, and a silence that makes you forget your phone exists." · note: *3,450 m · end of the old trade route*
6. **if you go** — tip: *"Eat at the 'Hindustan ka Aakhri Dhaba', sit by the Baspa with chai, and come May–October — the road shuts with the first snow."*
7. **TOSH** — "where Parvati valley simply runs out of road"
8. **the mood** — "Slow mornings, chai with a snow-peak view, and nowhere you have to be. Tosh is the full stop at the end of the valley." · note: *park at Barshaini, walk up the last bit*
9. **TOSH** (end) — tip: *"Stay a night higher up for sunrise on the peaks, and walk to Kutla for an even quieter view."* · CTA: **"Which one are you saving for 2027?"** · *save this · comment the one you'd pick first*

### 3 things only Isha can confirm (I kept these to verifiable facts; make them personal if you like)
- **Slide 3:** where did you actually stay in Kalpa? Swap the "stay up in old Kalpa" line for the real place/area if you want to name it.
- **Slide 6:** did you eat at the last dhaba? If not, I'll soften it to a general "don't skip it" line.
- **Slides 3, 6, 9:** these are the "tip" slides. Everything in them is true for the villages, but they read best in *your* exact words — send edits and I'll drop them in.

---

## Post caption (from the plan)
> Not everything I love is underwater 🏔️
>
> Kalpa, Chitkul and Tosh: three villages in Himachal that made me forget what day it was. Swipe for the tips I wish I'd had.
>
> Save this for your next mountain trip, and comment the one you'd pick first 👇
>
> #himachal #kalpa #chitkul #tosh #kinnaur #parvativalley #spiti #mountainsofindia #incredibleindia #travelwithisha

## Stories
Poll: **"Mountains 🏔️ or ocean 🌊?"** — results feed the safari-week stories ("or… the jungle? 🐅").

---

## To render
```bash
python projects/himachal_carousel/make.py
```
Outputs `out/slide_01.png … slide_09.png` (1080×1350) + `out/contact.png` (3×3 proof).
Edit wording in `slides.json`; swap photos in `photos/`. Missing photos fall back to the labelled placeholder.
