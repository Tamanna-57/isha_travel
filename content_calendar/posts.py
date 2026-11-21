# Safari sign-up campaign: 8 weeks, Mon 23 Nov 2026 - Sun 17 Jan 2027.
# 3 posts/week on @lostandfree (LAF) + 2 posts/week on @travelwithisha (TWI).
# {{...}} = details Lost & Free must confirm before posting. Never post with a {{ }} left in.

# ---------- reusable shooting instructions ----------
TH = ("SETUP A, talking head at home: face a window at 45 deg (never with the window behind you), lights and fans off. "
      "Phone on a tripod/stack of books at eye level, about 1 m away, VERTICAL, 4K 30fps, camera grid ON. "
      "Eyes on the upper grid line, frame mid-chest up, one palm of space above your head. Long-press your face to lock focus + exposure. "
      "AirPods or lapel mic. Start each take already leaning in, mid-energy, no 'hi guys'. Say every line 3 times, pause 1 sec between lines. "
      "End by recording 5 sec of silence.")
TH_OUT = ("SETUP O, outdoor talking head: 0.5x selfie with arm fully out, phone slightly below eye level, sky/trees behind you, "
          "sun beside you (not behind the phone, not in your eyes). Morning before 10:30 or after 4 pm. 3 takes per line, walk 2 steps while talking if it feels natural.")
VO = ("SETUP B, voiceover: quietest room you have (a wardrobe full of clothes kills echo). Phone/AirPods 20 cm from your mouth, Voice Memos is fine. "
      "Each line 3 ways: normal, slower, warmer. 2 sec silence before and after each line.")
FLAT = ("Top-down flat-lay on a bed/floor near a window in daylight. Hold the phone flat directly above (the grid's level crosshair turns yellow), "
        "vertical, 4K 30fps. Your hands come in from the bottom of the frame. No shadows from your body; no overhead tube light.")
ARCH = "Send ORIGINAL files (Google Drive / AirDrop / WhatsApp 'send as document'). Never normal WhatsApp video or Instagram downloads: they are too compressed."
SEND = "Upload to the shared Drive folder 'Raw - <post ID>' and name files like W1-L1_take2.mov."

# ---------- posts ----------
# fields: id, week, date, day, time, acct, collab, type, fmt, title, goal, cta,
#         script, screenplay, onscreen, shots[(shot, how)], source, shoot_by, edit, caption, deps
P = []
def add(**k): P.append(k)

# ======================= WEEK 1 · 23-29 Nov · PHASE 1: LAUNCH + TRUST =======================
add(id="W1-L1", week=1, date="Mon 23 Nov 2026", day="Mon", time="7:30 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Reel", fmt="B · storytime + safari B-roll (30-35 s)",
    title="\"Details are out. I'm taking you to the jungle.\"",
    goal="SIGN-UPS. Pays off the teaser reel ('details are coming out soon'). First post with real dates, price and seats.",
    cta="Comment SAFARI → auto-DM with Isha's tracked sign-up link",
    script=(
        "1. \"Maine bola tha details soon aayengi. Toh… ye rahi.\" (zips bag)\n"
        "2. \"{{N}} din. {{location}}. Lost & Free ke saath.\"\n"
        "3. \"Subah {{time}} baje open jeep. Thandi hawa. Aur jungle ki pehli awaaz.\"\n"
        "4. \"Din mein {{activity}}, raat ko {{campfire / stars}}. Network nahi. Bas jungle.\"\n"
        "5. \"Main inke saath kyun ja rahi hoon? Kyunki ye animals ko chase nahi karte. Engine band karke wait karte hain.\"\n"
        "6. \"{{dates}}. Sirf {{seats}} seats. {{₹ price}}, sab included.\"\n"
        "7. \"Comment SAFARI, main link bhejti hoon. Chalo, jungle bula raha hai.\""),
    screenplay=(
        "0.0-2.5s  HOOK: tight shot, Isha zips a duffel shut and looks up into the lens on 'ye rahi'. Title DETAILS ARE OUT lands on frame 1.\n"
        "2.5-6s    Hard cut to LAF jeep footage on a forest track; numbered card 01 '{{N}} days · {{location}}'.\n"
        "6-12s     3 fast cuts (≈1.2 s each): jeep at dawn → alarm-call deer → guide with binoculars. Cards 02, 03 like the 'How to see a tiger' reel.\n"
        "12-18s    Back to Isha talking head (punch-in 110%) for 'kyun'. Split-screen: Isha top, LAF tiger photo bottom on 'chase nahi karte'.\n"
        "18-25s    Details card on paper background: dates · seats · price · inclusions, each line ticks in with a sound.\n"
        "25-32s    Isha direct to lens: COMMENT 'SAFARI' lockup (same as teaser) + DM-ping SFX. Last line 'jungle bula raha hai' → cut to black on a bird call (loops)."),
    onscreen="DETAILS ARE OUT · 01 {{N}} days · {{location}} · 02 {{time}} AM open jeep · 03 No network · {{dates}} · {{seats}} seats · {{₹ price}} · Comment SAFARI",
    shots=[
        ("Talking head, all 7 lines (outfit: khaki/olive linen shirt, same as teaser)", TH),
        ("Zip-the-bag opener: duffel on your lap, zip it shut, look up into the lens", "Same Setup A framing. Bag in the lower third, face upper third. 3 takes; on the last one smile as you look up."),
        ("Packing hands B-roll: binoculars, cap, boots, notebook go into the bag (4 × 3 sec)", FLAT),
        ("Walking out of your front door with the bag (5 sec)", "Phone on tripod in the corridor at chest height; you walk past the lens and out. Lights on, door open, daylight if possible."),
    ],
    source="Isha shoot (Sat 21/Sun 22 Nov) + LAF safari footage (jeep, deer, guide, tiger) + LAF logo",
    shoot_by="Sun 22 Nov",
    edit=("Same look as the 'How to see a tiger' reel (Inter Display ExtraBold, yellow keywords, numbered cards, split screen) so the series feels connected. "
          "Original iPhone colour on Isha, no LUT. 1.1x speed, tight pauses. SFX: zip, card ticks, DM ping on SAFARI. No cursive anywhere."),
    caption=("Details are out 🐾\n\n{{N}} days in {{location}} with @lostandfree: open-jeep safaris at sunrise, no network, nights under the stars.\n"
             "📅 {{dates}} · 🪑 only {{seats}} seats · ₹{{price}} all-inclusive\n\nComment SAFARI and I'll DM you the link 👇\n\n"
             "#safari #wildlifeindia #tigersafari #junglesafari #travelwithisha #lostandfree #indiatravel #wildlifephotography"),
    deps="BLOCKING: safari name, location, dates, price, inclusions, seat count; Isha's tracked link; SAFARI keyword auto-DM switched on.")

add(id="W1-T1", week=1, date="Tue 24 Nov 2026", day="Tue", time="7:00 PM", acct="@travelwithisha", collab="—",
    type="Reel", fmt="C · photo story with voiceover (25-30 s)",
    title="\"7 years of waking up at 5 AM for animals\"",
    goal="REACH + TRUST. Shows Isha is a real wildlife photographer (her own 2018-2025 photos), so the safari feels like her world, not an ad.",
    cta="Save + 'which one is your favourite?' in comments. Soft line: 'this time you're coming with me' (safari link in stories).",
    script=(
        "VO (calm, close to mic):\n"
        "1. \"2018 mein maine pehli baar jungle mein camera uthaya tha.\"\n"
        "2. \"Tab se, har trip pe ek hi rule: subah 5 baje uthna hai.\"\n"
        "3. \"Kabhi ek harrier mila. Kabhi ek ullu jo blink hi nahi karta tha. Aur ek din… ye.\" (tiger)\n"
        "4. \"Saat saal, hazaaron photos. Lekin sabse best moment camera mein nahi hota.\"\n"
        "5. \"Woh hota hai jab jungle ek second ke liye bilkul chup ho jaata hai.\"\n"
        "6. \"Is baar… main akeli nahi ja rahi.\""),
    screenplay=(
        "0-2s     HOOK: Isha's tiger photo, slow push; text 7 YEARS OF 5 AM ALARMS. Alarm-clock SFX on frame 1.\n"
        "2-14s    Her photos beat-cut (~0.9 s each): harrier, jackal, owl, kingfisher, deer… each with year tag (2018, 2019…) in small bold type, camera-shutter SFX per photo.\n"
        "14-17s   Tiger photo holds 2.5 s on 'aur ek din… ye'.\n"
        "17-24s   Isha's face: 3 sec clip of her with camera (archive or new) + 'chup' moment: sound drops to silence for 0.7 s.\n"
        "24-28s   Last line over her talking-head close-up, small text 'this time, you're coming with me' → loops to alarm."),
    onscreen="7 YEARS OF 5 AM ALARMS · year tags · THIS TIME, YOU'RE COMING WITH ME",
    shots=[
        ("Voiceover lines 1-6", VO),
        ("15-20 of your best wildlife photos from 2018-2025 (the zip already has 21; add any tiger/owl/kingfisher/harrier originals)", ARCH),
        ("One 5-sec clip of you holding your camera at a window, lifting it to your eye", "Setup A light. Side-on to the window, phone at eye level 1.5 m away, you raise the camera slowly and freeze. 3 takes."),
        ("Talking-head line 6 to camera, whispered, small smile", TH),
    ],
    source="Isha archive (zip 24 Dec 2018 - 2 Aug 2025 is in the repo) + 1 new clip + VO",
    shoot_by="Sun 22 Nov",
    edit="Format C, beat-cut on a warm acoustic track. Photos full-frame with slow push (her own photos only, no stock). Year tags in bold sans, one colour. Shutter SFX per photo. Original colour.",
    caption=("2018 → 2025. Same alarm, same jungle, still not bored 🐅\n\nWhich one's your favourite? Tell me the number 👇\n\n"
             "This winter I'm taking a few of you with me. Link in my stories.\n\n#wildlifephotography #indianwildlife #tiger #birdsofindia #travelwithisha"),
    deps="Isha confirms which photos she's happy to publish; check none are already on her grid.")

add(id="W1-L2", week=1, date="Wed 25 Nov 2026", day="Wed", time="1:00 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Carousel (8 slides, 1080×1350)", fmt="Carousel · editorial (same design as the '6 things' carousel)",
    title="\"Your safari, day by day\"",
    goal="CONVERT people who watched Monday's reel but didn't comment: itinerary, inclusions, price in one saveable post.",
    cta="Comment SAFARI · save for later",
    script=(
        "S1 Cover: Isha photo + 'YOUR SAFARI, DAY BY DAY' · sub: {{dates}} · {{location}}\n"
        "S2 Day 1: {{arrival, check-in, evening nature walk / welcome dinner}}\n"
        "S3 Day 2: {{5:30 AM jeep safari · breakfast in the forest · afternoon safari}}\n"
        "S4 Day 3: {{…}} (add/remove day slides to match the real itinerary)\n"
        "S5 What's included: {{stay · all meals · {{N}} jeep safaris · naturalist · transfers}}\n"
        "S6 Not included: {{flights/trains · camera fees · tips}}\n"
        "S7 Price + seats: ₹{{price}} per person · {{seats}} seats · sign-ups close {{date}}\n"
        "S8 'Isha's coming. Are you?' · Comment SAFARI · @travelwithisha × @lostandfree"),
    screenplay="Slide order above. Swipe cue on S1. One photo per slide, full bleed, text in the lower half like the existing LAF carousel (gold serif headline + white body).",
    onscreen="As per slides (keep each slide under 30 words).",
    shots=[
        ("Cover photo: you in your safari outfit with binoculars, looking off-frame left (portrait, 4:5)", "Golden hour near a window or terrace. Phone in PHOTO mode, 1x, at your chest height, 1.5 m away. Take 20 frames; vary: looking left, laughing, binoculars up."),
    ],
    source="LAF photos for each day + 1 Isha photo",
    shoot_by="Sun 22 Nov",
    edit="Reuse the LAF carousel design system (gold serif titles, white body text, @lostandfree footer, page numbers). Keep body text big enough to read on a phone. No {{ }} left.",
    caption=("Everything you asked in the DMs, in one place 👇\n\n{{N}} days · {{location}} · {{dates}}\n₹{{price}} all-inclusive · {{seats}} seats only\n\n"
             "Comment SAFARI and we'll send you the sign-up link. Save this so you don't lose it.\n\n#safari #wildlifeindia #lostandfree #travelwithisha #junglesafari"),
    deps="BLOCKING: full itinerary + inclusions/exclusions from Lost & Free.")

add(id="W1-L3", week=1, date="Fri 27 Nov 2026", day="Fri", time="7:30 PM", acct="@lostandfree", collab="Tag @travelwithisha",
    type="Reel", fmt="D · POV (12-18 s)",
    title="\"POV: your alarm rings at 5:30 AM and you don't hate it\"",
    goal="REACH (shareable POV) that sends new viewers to the sign-up post.",
    cta="Share with the friend who'd come · comment SAFARI",
    script="No talking. Text carries it. Optional Isha whisper at the end: \"Shhh… sun.\" (listen)",
    screenplay=(
        "0-1.5s  Black screen, phone alarm sound → hand hits snooze (Isha's hand, real shot). HOOK text: POV: 5:30 AM AND YOU'RE NOT ANGRY\n"
        "1.5-5s  POV walking out into cold blue light, breath visible if possible / jeep engine starts (LAF).\n"
        "5-11s   LAF POV from the jeep on the forest track, long take; engine cuts; silence; alarm call.\n"
        "11-15s  Payoff: LAF tiger/leopard crossing (or deer staring at lens). Text: WORTH IT.\n"
        "15-17s  Isha whisper 'shhh… sun' over the forest; loops to alarm."),
    onscreen="POV: 5:30 AM AND YOU'RE NOT ANGRY · WORTH IT · (caption) comment SAFARI",
    shots=[
        ("Hand hitting the phone alarm in a dark room, then sitting up (5 sec)", "Lights off, only the phone screen glowing. Second phone on the bedside table pointing at the alarm phone, vertical. 3 takes."),
        ("Whisper 'shhh… sun' (3 takes)", VO),
    ],
    source="LAF jeep-POV + animal footage (needs a 6+ sec unbroken jeep POV) + 2 tiny Isha clips",
    shoot_by="Sun 22 Nov",
    edit="Format D: long takes, 0-3 cuts after the hook, trending sound OR real forest audio (test which one LAF prefers). Bold white hook text top. No captions needed.",
    caption=("The only alarm I've ever been happy about ⏰🐅\n\nSend this to the friend who'd actually wake up for it.\nSafari details: comment SAFARI.\n\n#safari #pov #wildlifeindia #lostandfree"),
    deps="LAF jeep POV clip (at least 6 sec, no shake).")

add(id="W1-T2", week=1, date="Sat 28 Nov 2026", day="Sat", time="11:00 AM", acct="@travelwithisha", collab="—",
    type="Carousel (7 slides)", fmt="Carousel · personal",
    title="\"Things travelling solo in India taught me (as a girl)\"",
    goal="TRUST + SAVES. Pre-answers the #1 safari worry ('is it safe for a solo girl?') in Isha's own voice.",
    cta="Save + 'add yours in the comments'. Last slide: 'Next solo trip? The jungle, with a group. Link in bio.'",
    script=(
        "S1 Cover (Isha photo, mountains): 'Travelling solo in India taught me…'\n"
        "S2 'Pick the host, not the hotel.' + 1 line from her own trips\n"
        "S3 'Tell 2 people where you are. Always.'\n"
        "S4 'The kindest people I met were strangers.' (road bhais callback)\n"
        "S5 'Book the first night. Leave the rest open.'\n"
        "S6 'Group trips are not boring. They're how I met my best travel friends.'\n"
        "S7 'My next one: the jungle, with a small group. Want in? Link in bio.'"),
    screenplay="7 slides, photo-led. Each slide: Isha's travel photo + one bold line + one small line in her words. Isha should rewrite each line in her voice.",
    onscreen="One lesson per slide (bold sans), small supporting line.",
    shots=[("6 solo-travel photos of you (Lakshadweep, Himachal, Uttarakhand, Maldives) – ideally ones not yet posted", ARCH)],
    source="Isha archive",
    shoot_by="Fri 27 Nov (photos only)",
    edit="Bold sans (no cursive), one accent colour, face visible on every slide. Text inside the 4:5 safe area.",
    caption=("Solo, not alone 🧳\n\nWhat would you add? Tell me in the comments.\n\nMy next trip is a small-group jungle safari with @lostandfree. Details in my bio.\n\n#solofemaletravel #indiatravel #travelwithisha #girlswhotravel"),
    deps="Isha edits the 6 lessons into her own words (Fri).")

# ======================= WEEK 2 · 30 Nov - 6 Dec =======================
add(id="W2-L1", week=2, date="Mon 30 Nov 2026", day="Mon", time="1:00 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Carousel (7 slides)", fmt="Carousel · FAQ",
    title="\"Is a safari safe for a solo girl? (and 5 more questions you sent us)\"",
    goal="REMOVE OBJECTIONS from the first week's DMs/comments: safety, fitness, network, food, cost, who's in the group.",
    cta="Comment SAFARI · DM questions",
    script=(
        "S1 Cover: Isha + 'You asked. We answered.'\n"
        "S2 Is it safe for solo women? {{LAF answer: female travellers %, rooms, guides, Isha travelling with the group}}\n"
        "S3 How fit do I need to be? {{answer}}\n"
        "S4 Will I definitely see a tiger? 'No one can promise that. Here's what we can promise: {{…}}'\n"
        "S5 Network? Food? {{answer}}\n"
        "S6 Who else is coming? {{age range / mostly first-timers / solo + friends}}\n"
        "S7 Still unsure? DM us / Comment SAFARI"),
    screenplay="Q in gold serif, answer in white. Honest tone (the 'no promise on tigers' slide builds trust).",
    onscreen="Per slide.",
    shots=[("Cover photo: you holding a phone showing DMs, laughing (portrait)", "Daylight, Setup A spot. Phone in PHOTO mode, 1x, chest height. 15 frames.")],
    source="LAF answers + LAF photos + 1 Isha photo",
    shoot_by="Sat 28 Nov",
    edit="Same LAF carousel system. Answers must be LAF's real answers; don't guess.",
    caption=("Your top 6 questions, answered honestly (yes, including the tiger one) 🐅\n\nMore questions? Drop them below.\nReady? Comment SAFARI.\n\n#safari #solofemaletravel #lostandfree #travelwithisha"),
    deps="BLOCKING: LAF's answers to the 6 questions; collect the real top questions from week-1 DMs.")

add(id="W2-T1", week=2, date="Tue 1 Dec 2026", day="Tue", time="7:00 PM", acct="@travelwithisha", collab="—",
    type="Reel", fmt="B · storytime (35-45 s)",
    title="\"12 metres underwater vs a tiger 10 metres away: which scared me more?\"",
    goal="REACH via her strongest past content (scuba) and bridge the audience from sea to jungle.",
    cta="Comment 'SEA' or 'JUNGLE' · soft: 'jungle part is happening again in {{month}}, details in bio'",
    script=(
        "1. \"12 metre neeche, oxygen tank ke saath, Lakshadweep mein. Ya open jeep mein, tiger 10 metre door. Kaunsa zyada scary tha?\"\n"
        "2. \"Underwater sab slow hota hai. Tum saans pe focus karte ho, aur darr chala jaata hai.\"\n"
        "3. \"Jungle mein ulta hai. Sab chup. Aur woh silence… dil itna zor se dhadakta hai na.\"\n"
        "4. \"Honestly? Tiger. Kyunki paani mein main control mein thi. Jungle mein, jungle control mein hai.\"\n"
        "5. \"Aur yahi toh best part hai.\"\n"
        "6. \"Tum kya choose karoge, SEA ya JUNGLE? Comment karo.\""),
    screenplay=(
        "0-3s    HOOK: split screen, top = Isha underwater (Lakshadweep), bottom = tiger (her photo); text SEA vs JUNGLE.\n"
        "3-10s   Talking head; B-roll: her dive clips (bubbles SFX).\n"
        "10-20s  Jungle half: LAF jeep + her tiger photo, sound drops to silence + heartbeat SFX.\n"
        "20-30s  Verdict to camera, punch-in on 'Tiger'.\n"
        "30-38s  Ask: SEA or JUNGLE lockup, comments."),
    onscreen="SEA vs JUNGLE · 12 m · 10 m · VERDICT: TIGER · SEA or JUNGLE?",
    shots=[("Talking head, all 6 lines (different outfit from W1-L1; a blue/white top for 'sea')", TH),
           ("Your Lakshadweep/Maldives underwater clips (best 6-8, clear water only, no murky coral)", ARCH)],
    source="Isha shoot + dive archive + Isha tiger photo + LAF jeep",
    shoot_by="Sat 28 Nov",
    edit="Format B. Split-screen hook (she liked the split layout on the safari reel). Only clear, bright underwater shots; never two similar shots in a row. Bubbles + heartbeat SFX.",
    caption=("I've done both. One of them still gives me goosebumps 🌊🐅\n\nSEA or JUNGLE? Comment 👇\n\n#scubadiving #lakshadweep #tigersafari #travelwithisha #indiatravel"),
    deps="—")

add(id="W2-L2", week=2, date="Wed 2 Dec 2026", day="Wed", time="7:30 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Reel", fmt="A · story walk with guide (30-40 s)",
    title="\"Meet the man who hears the tiger before he sees it\"",
    goal="TRUST: introduce the LAF naturalist/guide who will be on Isha's safari. People sign up for people.",
    cta="Comment SAFARI",
    script=(
        "Isha (intro, to camera): \"Iss safari pe mere saath ek aur insaan hoga. Aur yeh insaan tiger ko dekhne se pehle sun leta hai.\"\n"
        "Guide (LAF footage, his words): {{2-3 short lines: how many years in the forest, how he reads alarm calls, his favourite sighting}}\n"
        "Isha (outro): \"{{Guide name}} ke saath {{dates}}. Comment SAFARI.\""),
    screenplay=(
        "0-2s   HOOK: guide close-up, hand to ear, text HE HEARS IT FIRST.\n"
        "2-6s   Isha intro talking head.\n"
        "6-28s  Guide piece-to-camera from LAF + B-roll of him tracking (pugmarks, pointing, binoculars). Name card: {{Name}} · {{N}} years in {{park}}.\n"
        "28-35s Isha outro + Comment SAFARI lockup."),
    onscreen="HE HEARS IT FIRST · {{Name}} · {{N}} years in the jungle · Comment SAFARI",
    shots=[("Talking head intro + outro lines", TH)],
    source="LAF must film the guide (brief below) + Isha 2 lines",
    shoot_by="Sat 28 Nov (Isha); LAF footage by Mon 30 Nov",
    edit="Format A. Lower-third name card in bold sans. Guide audio cleaned; captions always on (Hinglish). Original colour.",
    caption=("Meet {{Name}}. {{N}} years in the jungle, and he still hears the tiger before anyone sees it 🎧🐅\n\nHe's leading our {{dates}} safari. Comment SAFARI to join.\n\n#naturalist #wildlifeindia #lostandfree #travelwithisha"),
    deps="BLOCKING: LAF films the guide: vertical, 3 answers to 'how long have you been here / how do you know a tiger is near / best sighting ever', + 6 B-roll shots of him at work; his consent.")

add(id="W2-L3", week=2, date="Fri 4 Dec 2026", day="Fri", time="7:30 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Reel", fmt="A · explainer with marker notes (25-35 s)",
    title="\"What ₹{{price}} actually gets you\"",
    goal="CONVERT price-sensitive viewers: break the price into stay, food, safaris, guide so it feels fair.",
    cta="Comment SAFARI",
    script=(
        "1. \"₹{{price}} sunke log bolte hain 'itna?' Chalo, breakdown karte hain.\"\n"
        "2. \"{{N}} raat stay: ₹{{x}}. Saara khaana: ₹{{x}}.\"\n"
        "3. \"{{N}} jeep safaris, jo akele book karo toh ₹{{x}} padte hain.\"\n"
        "4. \"Naturalist, permits, transfers: ₹{{x}}.\"\n"
        "5. \"Aur ek cheez jiska price nahi hai: subah 6 baje jungle ka chup hona.\"\n"
        "6. \"Comment SAFARI, link bhejti hoon.\""),
    screenplay=(
        "0-2s   HOOK: Isha holds up a price tag / notebook showing ₹{{price}} and crosses out 'expensive?' (sindoor red marker line).\n"
        "2-22s  Each line: talking head + handwritten marker number pops in the top third, LAF B-roll L-cut under it.\n"
        "22-27s Line 5 over silent forest dawn (no music, just birds).\n"
        "27-32s CTA lockup."),
    onscreen="₹{{price}} · stay ₹{{x}} · food ₹{{x}} · safaris ₹{{x}} · guide+permits ₹{{x}} · silence: priceless",
    shots=[("Talking head, lines 1-6, holding a small notebook with ₹{{price}} written in marker", TH),
           ("Notebook close-up: you write the price then strike 'expensive?' (5 sec)", FLAT)],
    source="Isha shoot + LAF B-roll",
    shoot_by="Sat 28 Nov",
    edit="Marker-note style from the reel system (Caveat Bold handwriting is OK for the NUMBERS only; titles stay bold sans). Tick SFX on each number.",
    caption=("Let's talk money 💸\n\n₹{{price}} for {{N}} days = stay + every meal + {{N}} safaris + naturalist + permits + transfers.\n\nComment SAFARI for the link.\n\n#budgettravel #safari #lostandfree #travelwithisha"),
    deps="BLOCKING: LAF's honest cost breakdown (only real numbers).")

add(id="W2-T2", week=2, date="Sat 5 Dec 2026", day="Sat", time="7:00 PM", acct="@travelwithisha", collab="—",
    type="Reel", fmt="A · story walk from archive (35-45 s)",
    title="\"Himachal in December: the village where the road ends\"",
    goal="REACH, keeps the travel identity (mountains). Winter-travel intent is high in December.",
    cta="Save for your winter trip · comment your dream winter place",
    script=(
        "VO / talking head:\n"
        "1. \"Agar December mein sirf ek jagah jaa sakte ho, toh yahan jaao.\"\n"
        "2. \"{{Village}}. Road yahin khatam hoti hai.\"\n"
        "3. \"Subah minus mein temperature, chai haath garam karti hai, aur pahaad itne paas lagte hain.\"\n"
        "4. \"Kaise pahunche: {{route, hours}}. Kahan ruke: {{homestay}}. Budget: {{₹}}.\"\n"
        "5. \"Aur ek tip: subah 7 baje uthna. Pahaad pe pehli dhoop… bas.\""),
    screenplay=(
        "0-2s    HOOK: Google Earth zoom from Mumbai to the village (screen recording) + title IF ONLY ONE PLACE THIS DECEMBER.\n"
        "2-5s    Chapter title: village name in big Anton caps.\n"
        "5-35s   Archive clips, 1.5-2 s each, never two similar shots in a row (alternate: wide → Isha → detail → wide).\n"
        "35-42s  First-light shot holds, payoff line."),
    onscreen="IF ONLY ONE PLACE THIS DECEMBER · {{VILLAGE}} · route · stay · budget",
    shots=[("VO lines 1-5 (or talking head if you prefer)", VO),
           ("Google Earth screen recording: zoom from Mumbai to {{village}}, vertical phone screen-record, 10 sec", "Google Earth app on the phone, 3D on, start zoomed out on India, search the village, let it fly in. Do 2 recordings."),
           ("All your Himachal clips + photos from Kalpa/Chitkul/Tosh (originals)", ARCH)],
    source="Isha archive + screen recording + VO",
    shoot_by="Sat 28 Nov",
    edit="Format A, story walk. Bold Anton chapter title (sindoor). Original colour. Verify every travel fact (route/time/budget) with Isha before posting.",
    caption=("Bookmark this for December ❄️🏔️\n\nHow to reach: {{…}}\nWhere to stay: {{…}}\nBudget: {{…}}\n\nWhat's your dream winter place? 👇\n\n#himachal #wintertravel #travelwithisha #mountains"),
    deps="Isha picks the village (the Kalpa/Chitkul/Tosh carousel was planned on 10 Nov; choose the one she covered least).")

# ======================= WEEK 3 · 7-13 Dec · PHASE 2: DESIRE =======================
add(id="W3-L1", week=3, date="Mon 7 Dec 2026", day="Mon", time="7:30 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Reel", fmt="C · sound-on explainer (20-25 s)",
    title="\"If you hear this sound in the jungle, don't move\"",
    goal="REACH (educational, sound-on, highly shareable) → comments SAFARI.",
    cta="Share · Comment SAFARI to hear it live",
    script=(
        "Isha VO, whisper:\n"
        "1. \"Agar jungle mein ye awaaz suno… (alarm call plays) …toh hilna mat.\"\n"
        "2. \"Ye ek deer hai, sabko bata raha hai: tiger yahin hai.\"\n"
        "3. \"Langur upar se dekhte hain, aur woh bhi chillate hain. (langur call)\"\n"
        "4. \"Guide engine band karta hai. Sab chup. Aur phir…\"\n"
        "5. \"…woh bahar aata hai.\""),
    screenplay=(
        "0-1.5s  HOOK: black screen, text TURN YOUR SOUND ON, then a real chital alarm call.\n"
        "1.5-8s  Deer frozen, ears up (LAF). Text: ALARM CALL = TIGER NEARBY.\n"
        "8-13s   Langur on a branch + its call.\n"
        "13-18s  Jeep engine off → silence 1 s.\n"
        "18-23s  Tiger walks out (LAF hero shot). Hold. Loop to black."),
    onscreen="TURN YOUR SOUND ON · ALARM CALL = TIGER NEARBY · LANGURS SEE IT FIRST · ENGINE OFF · …",
    shots=[("Whispered VO lines 1-5", VO)],
    source="LAF footage with REAL alarm-call audio (or sfx_library barking_deer_alarm.wav already in the repo) + Isha VO",
    shoot_by="Sat 5 Dec",
    edit="Format C. Real animal audio is the star; music very low or none. The repo already has the deer-alarm SFX from the safari reel.",
    caption=("Sound ON 🔊 This is how the jungle tells you a tiger is close.\n\nWant to hear it for real? Comment SAFARI.\n\n#wildlifefacts #tiger #junglesafari #lostandfree #travelwithisha"),
    deps="LAF deer + langur + tiger footage, ideally with original sound.")

add(id="W3-T1", week=3, date="Tue 8 Dec 2026", day="Tue", time="7:00 PM", acct="@travelwithisha", collab="—",
    type="Reel", fmt="A · money explainer (30-40 s)",
    title="\"My Lakshadweep trip cost breakdown (everyone asks)\"",
    goal="REACH + SAVES (money posts are the most-saved travel content). Builds authority before the safari push.",
    cta="Save · comment 'PLAN' and I'll reply with my itinerary",
    script=(
        "1. \"Lakshadweep expensive hai? Mera total tha ₹{{total}}. Breakdown dekho.\"\n"
        "2. \"Permit: ₹{{x}}. Flight/ship: ₹{{x}}.\"\n"
        "3. \"Stay: ₹{{x}} for {{N}} nights.\"\n"
        "4. \"Scuba: ₹{{x}}, aur honestly, sabse worth it.\"\n"
        "5. \"Khaana: ₹{{x}}. Total: ₹{{total}}.\"\n"
        "6. \"Save karlo, aur comment PLAN, main itinerary bhejti hoon.\""),
    screenplay="0-2s hook with ₹ total in big bold over her best Lakshadweep shot; each cost line = marker number + matching clip (permit paper, plane window, room, dive, food). End on dive shot + PLAN lockup.",
    onscreen="₹{{total}} · permit · travel · stay · scuba · food · comment PLAN",
    shots=[("Talking head lines 1-6 (bright top, beach vibe)", TH),
           ("Lakshadweep clips: permit/ticket, flight window, room, dive, food (originals)", ARCH)],
    source="Isha shoot + Lakshadweep archive",
    shoot_by="Sat 5 Dec",
    edit="Real numbers only from Isha. Tick SFX per number. Clear-water dive shots only.",
    caption=("Lakshadweep, fully broken down 💸🌊 Total ₹{{total}}.\n\nSave this, and comment PLAN for my day-by-day itinerary.\n\n#lakshadweep #budgettravel #travelwithisha #scuba"),
    deps="Isha's real trip costs.")

add(id="W3-L2", week=3, date="Wed 9 Dec 2026", day="Wed", time="1:00 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Carousel (8 slides)", fmt="Carousel · packing list",
    title="\"What to pack for a winter safari (it's colder than you think)\"",
    goal="SAVES + intent: people who save packing lists are planning to go.",
    cta="Save · Comment SAFARI",
    script=(
        "S1 Cover: Isha flat-lay photo · 'Pack this, not that'\n"
        "S2 Layers: the 6 AM jeep is {{X}}°C · fleece + windcheater\n"
        "S3 Colours: olive, khaki, brown. No white, no neon.\n"
        "S4 Cap, gloves, buff/scarf\n"
        "S5 Binoculars > zoom lens (Isha's tip)\n"
        "S6 Power bank + extra memory card\n"
        "S7 Don't bring: perfume, bright colours, loud speakers\n"
        "S8 Full list in one frame + Comment SAFARI"),
    screenplay="Each slide one item/category shot top-down on a plain bedsheet, bold item label, small reason line.",
    onscreen="Per slide.",
    shots=[("8 flat-lay photos: full layout + each category (layers, colours, cap/gloves, binoculars, power bank, 'don't bring' items)", FLAT + " Shoot as PHOTOS, 4:5. Same bedsheet and same light for all 8 so the carousel matches.")],
    source="Isha shoot",
    shoot_by="Sat 5 Dec",
    edit="LAF carousel system. Temperatures must come from LAF for the park and month.",
    caption=("The 6 AM jeep is no joke in December 🥶\n\nSave this list. Want to use it? Comment SAFARI.\n\n#packinglist #safari #lostandfree #travelwithisha"),
    deps="LAF: morning temperature for the park in {{month}}.")

add(id="W3-L3", week=3, date="Fri 11 Dec 2026", day="Fri", time="7:30 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Reel", fmt="C · beat-cut photo montage (15-20 s)",
    title="\"The tiger isn't the whole story\"",
    goal="Sets expectations honestly and sells the whole forest (owls, kingfishers, dholes). Fast, rewatchable.",
    cta="Comment the animal you want to see · SAFARI",
    script="On-screen text only + one Isha line at the end: \"Tiger mile na mile… jungle kabhi khaali haath nahi bhejta.\"",
    screenplay=(
        "0-1s   HOOK: text EVERYONE COMES FOR THE TIGER… over a tiger.\n"
        "1-14s  Hard beat cuts, one animal per beat: kingfisher, owl, dhole, langur, gaur, peacock, sloth bear, leopard (Isha's photos + LAF). Every animal different, never two birds in a row.\n"
        "14-18s Text: …BUT THEY LEAVE TALKING ABOUT THESE. Isha line over a final wide forest shot."),
    onscreen="EVERYONE COMES FOR THE TIGER… · …BUT THEY LEAVE TALKING ABOUT THESE",
    shots=[("Line to camera, outdoor if possible", TH_OUT), ("Any extra animal photos of yours not used in W1-T1", ARCH)],
    source="Isha photos + LAF photos",
    shoot_by="Sat 5 Dec",
    edit="Every cut exactly on a beat (cut 1 frame early). No repeats side by side. Shutter SFX on each.",
    caption=("The tiger gets the hype. The forest gets your heart 🦉🐦🐅\n\nWhich one do you want to see first? 👇 Comment SAFARI for dates.\n\n#indianwildlife #birdsofindia #lostandfree #travelwithisha"),
    deps="—")

add(id="W3-T2", week=3, date="Sat 12 Dec 2026", day="Sat", time="11:00 AM", acct="@travelwithisha", collab="—",
    type="Carousel (8 slides)", fmt="Carousel · listicle",
    title="\"6 places in India for wildlife this winter\"",
    goal="SAVES + positions Isha as the wildlife-travel person; slide 2 = the Lost & Free safari.",
    cta="Save · tag who you'd go with",
    script=(
        "S1 Cover: Isha with binoculars · 'Winter = wildlife season'\n"
        "S2 {{LAF safari park}}: 'where I'm going in {{month}}' (link in bio)\n"
        "S3-S7 5 more: e.g. Bharatpur (birds), Rann of Kutch (wild ass, flamingos), Kaziranga (rhino), Jawai (leopards), Chilika (dolphins) — 1 line each: best month + what you'll see\n"
        "S8 'Which one first? Comment.'"),
    screenplay="Photo per place (Isha's if she has them; else licensed/credited).",
    onscreen="Place · best month · what you'll see",
    shots=[("Cover photo with binoculars (can reuse W1-L2 session)", "Same as W1-L2 cover shoot."), ("Any of your photos from these places", ARCH)],
    source="Isha archive + credited photos",
    shoot_by="Fri 11 Dec",
    edit="Fact-check every best-month line. Bold sans, one accent colour.",
    caption=("Winter is wildlife season in India 🦩🦏🐆\n\nSave this, and tag the person you'd go with. I'm doing #2 in {{month}}, link in bio.\n\n#wildlifeindia #wintertravel #travelwithisha"),
    deps="Fact check; photo credits for non-Isha photos.")

# ======================= WEEK 4 · 14-20 Dec =======================
add(id="W4-L1", week=4, date="Mon 14 Dec 2026", day="Mon", time="7:30 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Reel", fmt="B · storytime (40-50 s)",
    title="\"3 days without my phone in the jungle. Here's what happened.\"",
    goal="DESIRE: the emotional reason to go (digital detox), told by Isha.",
    cta="Comment SAFARI",
    script=(
        "1. \"Pichli baar jungle mein, 3 din tak mera phone sirf ek camera tha. Network hi nahi tha.\"\n"
        "2. \"Pehla din: main har 10 minute mein phone check kar rahi thi. Aadat.\"\n"
        "3. \"Doosra din: maine notice kiya, main birds ki awaaz pehchanne lagi thi.\"\n"
        "4. \"Teesra din: maine sunset dekha. Bina photo liye. Pehli baar.\"\n"
        "5. \"Mumbai wapas aake… 400 notifications. Aur ek bhi important nahi tha.\"\n"
        "6. \"Is baar {{dates}}. Phone band. Chalo?\""),
    screenplay=(
        "0-2s   HOOK: phone screen 'No Service' close-up, text 3 DAYS. NO NETWORK.\n"
        "2-40s  Talking head ↔ jungle B-roll (≥40% B-roll). Day 1 / Day 2 / Day 3 numbered cards.\n"
        "40-46s '400 notifications' gag: real phone buzzing with notification SFX.\n"
        "46-50s CTA."),
    onscreen="3 DAYS. NO NETWORK. · DAY 1 · DAY 2 · DAY 3 · 400 NOTIFICATIONS · {{dates}}",
    shots=[("Talking head, lines 1-6 (cosy home setup, warm lamp in background)", TH),
           ("Phone close-up showing 'No Service' / airplane mode (3 sec)", "Put the phone in airplane mode, hold it in your hand near the window, second phone films it vertically 20 cm away. Tap focus on the screen."),
           ("Phone buzzing with notifications on a table (4 sec)", "Turn airplane mode off with notifications waiting; film from above.")],
    source="Isha shoot + LAF/Isha jungle B-roll",
    shoot_by="Sat 12 Dec",
    edit="Format B, sans two-tier captions. More face: talking head at least 50%. SFX: notification buzzes, birds.",
    caption=("I didn't miss a single notification. I missed the jungle 🌿📵\n\n{{dates}} · {{location}} · {{seats}} seats. Comment SAFARI.\n\n#digitaldetox #safari #lostandfree #travelwithisha"),
    deps="Isha must have actually done this (keep the story true; change details to match her real trip).")

add(id="W4-T1", week=4, date="Tue 15 Dec 2026", day="Tue", time="7:00 PM", acct="@travelwithisha", collab="—",
    type="Reel", fmt="B · storytime (40-50 s)",
    title="\"The scariest moment of all my travels\"",
    goal="REACH (story hooks perform best for her: the cliffhanger dive message, R1 loop). Ends with a teaser to the jungle.",
    cta="Comment your scariest travel moment",
    script=(
        "Isha picks her real story (e.g. the 12 m dive, a mountain road, a wildlife encounter). Structure:\n"
        "1. Hook line: \"Main sach mein sochi thi, aaj toh gayi.\"\n"
        "2. Where + when (1 line).\n"
        "3. What went wrong (2-3 short lines, build tension).\n"
        "4. The turn: who/what saved her.\n"
        "5. Lesson in 1 line.\n"
        "6. \"Agla adventure? Jungle. Aur is baar tum bhi aa sakte ho.\""),
    screenplay="0-2s letterboxed cold open of the place (16:9 on black) + 'What happened?'; desk storytime ↔ B-roll; heartbeat SFX at the peak; end on her smile.",
    onscreen="WHAT HAPPENED? · place · year · lesson",
    shots=[("Talking head, her story in short lines", TH), ("Any footage/photos from that trip", ARCH)],
    source="Isha shoot + archive",
    shoot_by="Sat 12 Dec",
    edit="Format B with letterbox cold open. Karaoke captions (emotional). Keep the true story; don't dramatise beyond what happened.",
    caption=("I genuinely thought this was it 😮‍💨\n\nWhat's your scariest travel moment? 👇\n\n#travelstories #storytime #travelwithisha"),
    deps="Isha sends a 1-min voice note of the story first so we can trim the script.")

add(id="W4-L2", week=4, date="Wed 16 Dec 2026", day="Wed", time="1:00 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Carousel (7 slides)", fmt="Carousel · photography tips",
    title="\"Isha's phone + camera settings for safari photos\"",
    goal="SAVES + authority. Shows people they'll come home with great photos.",
    cta="Save · Comment SAFARI",
    script=(
        "S1 Cover: Isha's best tiger photo · 'Shoot it like a photographer'\n"
        "S2 Phone: lock exposure on the animal, don't use digital zoom past 3x\n"
        "S3 Phone: burst mode for birds in flight\n"
        "S4 Camera: shutter 1/1000+ for moving animals, auto ISO\n"
        "S5 Golden rule: eyes in focus, leave space in front of the animal\n"
        "S6 Don't: flash. Ever.\n"
        "S7 'Practise with me in {{location}}' · Comment SAFARI"),
    screenplay="Each slide: one of Isha's photos showing the tip + settings box.",
    onscreen="Per slide, with settings in a small box (e.g. 1/1600 · f/5.6 · ISO 800).",
    shots=[("The camera settings (EXIF) of 6 of your photos — screenshot from Lightroom/Photos info", "In Photos app swipe up on the photo to see the camera info; screenshot it.")],
    source="Isha photos + settings",
    shoot_by="Sat 12 Dec",
    edit="Use her real EXIF numbers. Editorial LAF design.",
    caption=("Save this before your safari 📸\n\nWant to practise with me? Comment SAFARI.\n\n#wildlifephotography #photographytips #lostandfree #travelwithisha"),
    deps="Isha's EXIF screenshots.")

add(id="W4-L3", week=4, date="Fri 18 Dec 2026", day="Fri", time="7:30 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Reel", fmt="Trend / skit (10-15 s)",
    title="\"Tag the friend who'd survive a 5 AM safari\"",
    goal="REACH via tags + group sign-ups (friends booking together).",
    cta="Tag a friend · Comment SAFARI for 2",
    script=(
        "Skit, Isha plays two characters (split by outfit):\n"
        "Friend A (pyjamas, under blanket): \"5 baje? Pagal hai kya?\"\n"
        "Friend B (safari outfit, binoculars): \"Tiger dikha toh?\"\n"
        "Friend A (already standing in shoes): \"…chal.\""),
    screenplay="3 shots, hard cuts on a trending sound, final shot both 'friends' (split screen of the two takes) walking out the door. Text: TAG YOUR 5 AM FRIEND.",
    onscreen="TAG YOUR 5 AM FRIEND · comment SAFARI if you're booking as 2",
    shots=[("Skit shot 1: under a blanket in bed, line A", "Bedroom, warm lamp, phone on tripod at bed height. 3 takes, big facial expression."),
           ("Skit shot 2: safari outfit, binoculars, line B", TH),
           ("Skit shot 3: pyjamas + shoes on, standing, '…chal'", "Same framing as shot 2, so the jump feels like a cut-away gag.")],
    source="Isha shoot",
    shoot_by="Sat 12 Dec",
    edit="Fast, funny, trending audio added in-app (we export without music). Bold hook text top.",
    caption=("We all have one 😂 Tag yours.\n\nBooking as a pair? Comment SAFARI.\n\n#travelbuddy #safari #lostandfree #travelwithisha"),
    deps="Pick a trending sound on Fri morning.")

add(id="W4-T2", week=4, date="Sat 19 Dec 2026", day="Sat", time="11:00 AM", acct="@travelwithisha", collab="—",
    type="Carousel (10 slides)", fmt="Carousel · photo dump",
    title="\"Uttarakhand, as I remember it\"",
    goal="Grid aesthetics + saves; keeps the mountains pillar alive between safari posts.",
    cta="Save",
    script="10 best Uttarakhand photos; caption is a short story (5-6 lines) in Isha's words. No text on photos except slide 1 (place name).",
    screenplay="Order: strongest wide → Isha portrait → detail → wide…, never two similar frames together.",
    onscreen="Slide 1: UTTARAKHAND (bold).",
    shots=[("Your 15 best Uttarakhand photos (we'll pick 10)", ARCH)],
    source="Isha archive",
    shoot_by="Thu 17 Dec",
    edit="Light consistency check only; keep her colours.",
    caption="(Isha's 5-6 line story from the trip)\n\n#uttarakhand #mountains #travelwithisha #himalayas",
    deps="Isha writes the caption story.")

# ======================= WEEK 5 · 21-27 Dec =======================
add(id="W5-L1", week=5, date="Mon 21 Dec 2026", day="Mon", time="1:00 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Carousel (8 slides)", fmt="Carousel · ethics",
    title="\"7 things we never do on safari\"",
    goal="TRUST + differentiation (eco-conscious, small groups). Matches the LAF '6 things' tone.",
    cta="Save · Comment SAFARI",
    script=(
        "S1 Cover: 'Our jungle rules'\n"
        "S2 We never chase an animal.\nS3 We never crowd a sighting ({{max}} jeeps).\nS4 We never feed anything.\n"
        "S5 We never play music in the jeep.\nS6 We never litter, not even a toffee wrapper.\nS7 We never promise a tiger.\n"
        "S8 'If that sounds like your kind of trip: Comment SAFARI'"),
    screenplay="One rule per slide over a calm wildlife photo, gold numerals.",
    onscreen="Per slide.",
    shots=[("None from Isha", "—")],
    source="LAF photos",
    shoot_by="—",
    edit="LAF editorial design. LAF must confirm each rule is their actual practice.",
    caption=("The jungle was here first 🌿 These are our 7 rules.\n\nIf this is your kind of trip, comment SAFARI.\n\n#responsibletourism #safari #lostandfree #travelwithisha"),
    deps="LAF confirms rules + jeep cap.")

add(id="W5-T1", week=5, date="Tue 22 Dec 2026", day="Tue", time="7:00 PM", acct="@travelwithisha", collab="—",
    type="Reel", fmt="C · year recap, beat-cut (20-25 s)",
    title="\"2026 in 20 seconds\"",
    goal="REACH + shares (year-end recap season). Ends on the jungle as 'what's next'.",
    cta="Comment your best trip of 2026",
    script="No VO. Text: '2026' → month tags. Final text: 'and 2027 starts in the jungle 🐅' (caption: link in bio).",
    screenplay="Every beat = a new trip moment in time order (Lakshadweep dive, mountains, Diwali, Mumbai, safari teaser…). Drum-roll intro = 8 quick flashes like the Polaroid reel she liked. Last 2 s: jungle, text 2027.",
    onscreen="2026 · month tags · 2027 STARTS IN THE JUNGLE",
    shots=[("Your 30-40 best clips/photos of 2026 (1-3 sec each is enough)", ARCH),
           ("1 new clip: you look at the camera and wink/smile, outdoor (3 sec)", TH_OUT)],
    source="Isha archive 2026",
    shoot_by="Sat 19 Dec",
    edit="Cut on every beat, exactly (measure the track: claps/snares). No similar shots side by side. Original colour.",
    caption=("2026, you were a good one 🌊🏔️🐅\n\nWhat was your best trip this year? 👇\nAnd 2027… starts in the jungle. Link in bio.\n\n#2026recap #yearinreview #travelwithisha"),
    deps="Choose track; we export without music, add it in Instagram.")

add(id="W5-L2", week=5, date="Wed 23 Dec 2026", day="Wed", time="7:30 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Reel", fmt="A · BTS (20-30 s)",
    title="\"Behind the scenes: planning your safari with Lost & Free\"",
    goal="TRUST + soft urgency: real seat count, real planning call.",
    cta="Comment SAFARI · '{{N}} seats left'",
    script=(
        "1. \"Aaj Lost & Free team ke saath planning call thi.\"\n"
        "2. \"Jeep routes final, stay final, aur… {{N}} seats already gaye.\"\n"
        "3. \"Bas {{remaining}} bache hain.\"\n"
        "4. \"Agar soch rahe ho, abhi comment karo SAFARI.\""),
    screenplay="Laptop video call (LAF team on screen, blurred if needed) → map / route on screen → Isha reaction → seat-count card ticking down.",
    onscreen="PLANNING CALL · ROUTES ✓ STAY ✓ · {{remaining}} SEATS LEFT",
    shots=[("Over-shoulder: you on a video call with the LAF team (10 sec)", "Phone on tripod behind your shoulder, laptop screen in frame, room lamp on, exposure locked on the laptop screen."),
           ("Talking head lines 1-4", TH)],
    source="Isha shoot + LAF on call",
    shoot_by="Sat 19 Dec",
    edit="Only post the seat number if it's true today.",
    caption=("Routes ✅ Stay ✅ Seats… going 👀\n\n{{remaining}} left for {{dates}}. Comment SAFARI.\n\n#safari #lostandfree #travelwithisha"),
    deps="BLOCKING: real seat count from LAF on the day.")

add(id="W5-L3", week=5, date="Fri 25 Dec 2026", day="Fri", time="11:00 AM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Reel", fmt="Trend (8-12 s)",
    title="\"All I want for Christmas is… (a tiger sighting)\"",
    goal="Light, festive reach on Christmas morning; gift angle ('gift a safari').",
    cta="Tag who you'd gift it to · Comment SAFARI",
    script="Lip-sync/trend: Isha with a Santa cap opens a 'gift' box → binoculars inside → cut to tiger. Text: ALL I WANT FOR CHRISTMAS IS… / …THIS.",
    screenplay="3 cuts: gift box open (reaction) → binoculars to eyes → LAF tiger looking back. Ends with 'Gift a safari 🎁' card.",
    onscreen="ALL I WANT FOR CHRISTMAS IS… · …THIS · GIFT A SAFARI",
    shots=[("Opening a wrapped box, Santa cap, big reaction (3 takes)", TH),
           ("Binoculars up to your eyes, looking straight into the lens (3 sec)", TH)],
    source="Isha shoot + LAF tiger",
    shoot_by="Sat 19 Dec",
    edit="Trending festive audio added in-app. Under 12 s.",
    caption=("Dear Santa, just one tiger please 🎅🐅\n\nTag who you'd gift a safari to. Comment SAFARI for details.\n\n#merrychristmas #safari #lostandfree #travelwithisha"),
    deps="LAF to confirm if gifting/booking for someone else is possible.")

add(id="W5-T2", week=5, date="Sat 26 Dec 2026", day="Sat", time="11:00 AM", acct="@travelwithisha", collab="—",
    type="Static post (single photo)", fmt="Post",
    title="\"My one travel rule for 2027\"",
    goal="Engagement (comments) + grid variety; low effort during holidays.",
    cta="Comment your rule",
    script="Photo of Isha in nature + long caption (her rule, e.g. 'Fewer places, longer stays' or 'Wake up for the sunrise'). On-image text: none or 3 bold words.",
    screenplay="Single image.",
    onscreen="Optional: MY 2027 RULE",
    shots=[("One strong portrait from the archive OR new one at golden hour", "Golden hour, sun to your side, phone 1x at chest height, 2 m away, you looking at the horizon. 20 frames.")],
    source="Isha",
    shoot_by="Thu 24 Dec",
    edit="—",
    caption="(Isha writes her rule + why, 4-5 lines)\n\nWhat's yours? 👇\n\n#travelwithisha #2027goals",
    deps="Isha writes the caption.")

# ======================= WEEK 6 · 28 Dec - 3 Jan · PHASE 3: URGENCY =======================
add(id="W6-L1", week=6, date="Mon 28 Dec 2026", day="Mon", time="1:00 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Carousel (9 slides)", fmt="Carousel · year recap",
    title="\"Isha's best wildlife frames of 2026\"",
    goal="DESIRE: her photography proves the experience; last slide = '2027 starts in the jungle'.",
    cta="Comment SAFARI",
    script="S1 'Best of 2026, from my camera' · S2-S8 one photo each with a 1-line story (where, what happened) · S9 '2027's first frame could be yours. {{dates}}. Comment SAFARI.'",
    screenplay="Photo-led, minimal text in the lower third.",
    onscreen="Per slide one-liner.",
    shots=[("7 best wildlife photos taken in 2026 + 1-line story each", ARCH)],
    source="Isha",
    shoot_by="Sat 26 Dec",
    edit="LAF design, credit 'Photo: @travelwithisha' on each slide.",
    caption=("7 frames, 7 stories from 2026 📸\n\nThe next one could be yours: {{dates}}. Comment SAFARI.\n\n#wildlifephotography #bestof2026 #lostandfree #travelwithisha"),
    deps="—")

add(id="W6-T1", week=6, date="Tue 29 Dec 2026", day="Tue", time="7:00 PM", acct="@travelwithisha", collab="—",
    type="Reel", fmt="A · talking head + archive (25-35 s)",
    title="\"My 2027 travel bucket list\"",
    goal="REACH (bucket-list season). #1 on the list = the safari, so her own followers see it as her plan, not an ad.",
    cta="Comment which one you'd join me on",
    script=(
        "1. \"2027 mein ye 5 jagah. Aur pehli wali already book hai.\"\n"
        "2. \"Number 5: {{place}}…\" (4 → 2, one line each, Isha's real wishes)\n"
        "3. \"Number 1: jungle, {{month}}, aur main akeli nahi ja rahi.\"\n"
        "4. \"Kaunsi trip pe aaoge mere saath?\""),
    screenplay="Countdown 5→1, each with a Google Earth flash or archive shot; #1 gets the LAF jungle B-roll and a stamp 'BOOKED ✓'.",
    onscreen="2027 BUCKET LIST · 5 · 4 · 3 · 2 · 1 JUNGLE (BOOKED ✓)",
    shots=[("Talking head lines (New-Year-ish outfit)", TH), ("Screen recordings: Google Earth fly-ins to her 4 other places (5 sec each)", "Same method as W2-T2.")],
    source="Isha shoot + screen recordings + LAF B-roll",
    shoot_by="Sat 26 Dec",
    edit="Fast countdown, numbers in big Anton, one colour.",
    caption=("5 trips for 2027. #1 is already booked 🐅\n\nWhich one would you join me on? 👇 (#1 has seats, link in bio)\n\n#bucketlist #2027travel #travelwithisha"),
    deps="Isha's real 4 other places.")

add(id="W6-L2", week=6, date="Wed 30 Dec 2026", day="Wed", time="7:30 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Reel", fmt="B · direct to camera (20-25 s)",
    title="\"New year resolution: see a tiger with your own eyes, not on a screen\"",
    goal="CONVERT with the New Year motivation spike. Echoes the teaser line ('not on some screen').",
    cta="Comment SAFARI",
    script=(
        "1. \"Har saal resolution: gym, diet, savings. Is saal ek alag try karo.\"\n"
        "2. \"Apni aankhon se ek tiger dekhna. Reel pe nahi.\"\n"
        "3. \"{{dates}}, {{location}}. {{remaining}} seats.\"\n"
        "4. \"Comment SAFARI. Ye wala resolution tootega nahi.\""),
    screenplay="Hook: a fake resolutions list (GYM ✗ DIET ✗) crossed out in red marker, last line written: SEE A TIGER ✓. Then talking head + LAF tiger + CTA.",
    onscreen="2027 RESOLUTIONS · GYM ✗ · DIET ✗ · SEE A TIGER ✓ · {{remaining}} seats",
    shots=[("Notebook: you write a resolutions list and cross items out, then write 'SEE A TIGER' (8 sec)", FLAT), ("Talking head lines 1-4", TH)],
    source="Isha shoot + LAF tiger",
    shoot_by="Sat 26 Dec",
    edit="Marker-style list; tick SFX. Keep it under 25 s.",
    caption=("The only resolution you won't break 🐅✅\n\n{{dates}} · {{remaining}} seats left. Comment SAFARI.\n\n#newyearresolution #safari #lostandfree #travelwithisha"),
    deps="Seat count true on the day.")

add(id="W6-L3", week=6, date="Fri 1 Jan 2027", day="Fri", time="11:00 AM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Static post (single image, 1080×1350)", fmt="Post · poster",
    title="\"Your first plan of 2027\"",
    goal="Clean, screenshot-able poster on New Year's Day with the key details.",
    cta="Comment SAFARI · link in bio",
    script="Poster: big tiger photo · 'YOUR FIRST PLAN OF 2027' · {{dates}} · {{location}} · ₹{{price}} · {{remaining}} seats · 'with @travelwithisha'",
    screenplay="Single image, LAF editorial style.",
    onscreen="As above.",
    shots=[("None", "—")],
    source="LAF design",
    shoot_by="—",
    edit="Text inside the 4:5 safe area; readable at thumbnail size.",
    caption=("Happy New Year 🎉 Start it in the jungle.\n\n{{dates}} · {{location}} · {{remaining}} seats. Comment SAFARI.\n\n#happynewyear2027 #safari #lostandfree #travelwithisha"),
    deps="Final details.")

add(id="W6-T2", week=6, date="Sat 2 Jan 2027", day="Sat", time="11:00 AM", acct="@travelwithisha", collab="—",
    type="Carousel (6 slides)", fmt="Carousel · reflective",
    title="\"Things I'll do differently as a traveller in 2027\"",
    goal="Engagement + saves; personal voice. One slide mentions travelling more responsibly (ties to LAF values).",
    cta="Comment the one you relate to",
    script="S1 cover · S2 'Fewer places, longer stays' · S3 'Leave every place cleaner' · S4 'Phone down at sunrise' · S5 'Go with people who respect the place' · S6 'Starting with the jungle in {{month}}'. Isha to rewrite in her words.",
    screenplay="Photo per slide, bold line + small line.",
    onscreen="Per slide.",
    shots=[("6 photos of you from different trips", ARCH)],
    source="Isha archive",
    shoot_by="Thu 31 Dec",
    edit="Bold sans; her face visible on most slides.",
    caption="(Isha's intro line)\n\nWhich one do you relate to? 👇\n\n#travelwithisha #responsibletravel #2027",
    deps="Isha rewrites lines.")

# ======================= WEEK 7 · 4-10 Jan =======================
add(id="W7-L1", week=7, date="Mon 4 Jan 2027", day="Mon", time="7:30 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Reel", fmt="A · contrarian (20-30 s)",
    title="\"This safari is NOT for you if…\"",
    goal="CONVERT the right people (qualifies + creates curiosity). Contrarian hooks drive comments.",
    cta="Comment SAFARI if you're still here",
    script=(
        "1. \"Ye safari tumhare liye NAHI hai agar…\"\n"
        "2. \"…tumhe 5 baje uthna pasand nahi.\"\n"
        "3. \"…tumhe jeep mein selfie music chahiye.\"\n"
        "4. \"…tum sirf tiger ke liye aa rahe ho aur baaki jungle boring lagta hai.\"\n"
        "5. \"Abhi bhi dekh rahe ho? Toh tum humare type ke ho. Comment SAFARI.\""),
    screenplay="Each 'not for you' line = Isha shaking head + quick gag clip (snooze, speaker, yawning at a bird). Last line: big smile, CTA.",
    onscreen="NOT FOR YOU IF… · ✗ 5 AM · ✗ LOUD MUSIC · ✗ ONLY TIGERS · STILL HERE? COMMENT SAFARI",
    shots=[("Talking head lines 1-5", TH), ("3 tiny gag clips: hitting snooze, holding a speaker, yawning (2 sec each)", "Same Setup A framing, exaggerated expressions, 2 takes each.")],
    source="Isha shoot",
    shoot_by="Sat 2 Jan",
    edit="Red ✗ marks, bold sans, quick cuts (1 s).",
    caption=("Honestly, it's not for everyone 🤷‍♀️\n\nStill here? Comment SAFARI. {{remaining}} seats.\n\n#safari #lostandfree #travelwithisha"),
    deps="—")

add(id="W7-T1", week=7, date="Tue 5 Jan 2027", day="Tue", time="7:00 PM", acct="@travelwithisha", collab="—",
    type="Reel", fmt="B · Q&A (30-40 s)",
    title="\"Job + travel: how I actually afford it\"",
    goal="REACH (most-asked creator question) + relatable; mentions group trips as the cheaper way to do wildlife.",
    cta="Comment your question for the next Q&A",
    script=(
        "Isha answers in her real words. Suggested structure:\n"
        "1. \"Sabse zyada pucha jaata hai: travel afford kaise karti ho?\"\n"
        "2. 3 honest tips (e.g. long weekends, budgeting per month, group trips split costs).\n"
        "3. \"Aur wildlife ke liye group trips sabse sasta option hain, isliye main is baar group mein ja rahi hoon.\""),
    screenplay="Question box screenshot as hook → desk talking head → B-roll of trips per tip.",
    onscreen="'HOW DO YOU AFFORD TRAVEL?' · TIP 1 · TIP 2 · TIP 3",
    shots=[("Talking head answers", TH), ("Screenshot of the question box", "Post a 'Ask me anything' story sticker on Mon, screenshot the best question.")],
    source="Isha shoot + archive",
    shoot_by="Sat 2 Jan",
    edit="Format B, top captions style.",
    caption=("The honest answer 💸✈️\n\nDrop your next question 👇\n\n#travelonabudget #travelwithisha"),
    deps="Isha's real tips.")

add(id="W7-L2", week=7, date="Wed 6 Jan 2027", day="Wed", time="1:00 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Carousel (8 slides)", fmt="Carousel · final details",
    title="\"Final details: everything you need before you book\"",
    goal="CONVERT: updated itinerary, how to reach, payment, cancellation, sign-up deadline.",
    cta="Comment SAFARI · link in bio",
    script="S1 'Final details' · S2 dates + meeting point · S3 how to reach from Mumbai/Delhi · S4 itinerary summary · S5 inclusions · S6 payment + cancellation · S7 your questions round 2 · S8 'Sign-ups close {{date}}' + CTA",
    screenplay="LAF editorial.",
    onscreen="Per slide.",
    shots=[("None", "—")],
    source="LAF",
    shoot_by="—",
    edit="Every number from LAF's final sheet.",
    caption=("Everything, final and confirmed ✅\n\nSign-ups close {{date}}. Comment SAFARI.\n\n#safari #lostandfree #travelwithisha"),
    deps="BLOCKING: meeting point, transport, payment + cancellation policy.")

add(id="W7-L3", week=7, date="Fri 8 Jan 2027", day="Fri", time="7:30 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Reel", fmt="C · ASMR packing (15-20 s)",
    title="\"Packing for the jungle (sound on)\"",
    goal="Rewatchable, satisfying; signals the trip is real and close.",
    cta="Comment SAFARI · '{{remaining}} seats'",
    script="No VO. Only sounds: zip, velcro, binocular case click, camera battery click. Final text: 'see you in {{N}} days'.",
    screenplay="10-12 top-down close-ups, 1.2-1.5 s each, every item a different type of sound; end on bag zipped + text.",
    onscreen="PACKING FOR THE JUNGLE 🔊 · SEE YOU IN {{N}} DAYS · {{remaining}} SEATS",
    shots=[("10-12 top-down packing close-ups with clear sound (cap, fleece, binoculars, camera, battery, notebook, torch, water bottle, zip)", FLAT + " Record sound with the phone mic close (30 cm). Room silent.")],
    source="Isha shoot",
    shoot_by="Sat 2 Jan",
    edit="Real sound only, boost it; no music. Different from W1-L1 packing (closer, slower, sound-led).",
    caption=("Sound on 🔊 {{N}} days to go.\n\nLast {{remaining}} seats: comment SAFARI.\n\n#asmr #packwithme #safari #lostandfree #travelwithisha"),
    deps="—")

add(id="W7-T2", week=7, date="Sat 9 Jan 2027", day="Sat", time="7:00 PM", acct="@travelwithisha", collab="—",
    type="Reel", fmt="A · gear (20-30 s)",
    title="\"What's in my wildlife camera bag\"",
    goal="Niche authority, saves; photographers are prime safari buyers.",
    cta="Save · comment your gear question",
    script="Isha holds up each item: camera body, lens, binoculars, phone clip, rain cover, beanbag; one line each on why.",
    screenplay="Top-down unpack, each item gets a label card; end with bag packed + 'next stop: jungle'.",
    onscreen="Item names + 1-word reason",
    shots=[("Unpacking your camera bag item by item (top-down)", FLAT), ("Talking head intro line", TH)],
    source="Isha shoot",
    shoot_by="Sat 2 Jan",
    edit="Labels in bold sans, one colour.",
    caption=("Everything I carry for wildlife 📸\n\nSave it. Gear questions? 👇\n\n#cameragear #wildlifephotography #travelwithisha"),
    deps="—")

# ======================= WEEK 8 · 11-17 Jan · LAST CALL =======================
add(id="W8-L1", week=8, date="Mon 11 Jan 2027", day="Mon", time="7:30 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Reel", fmt="C · montage (10-15 s)",
    title="\"Last call: {{remaining}} seats\"",
    goal="URGENCY. Short, fast, one message.",
    cta="Comment SAFARI · link in bio",
    script="Isha 1 line at the end: \"Last {{remaining}} seats. Ab nahi toh agle saal.\"",
    screenplay="8 fastest, best moments from all campaign footage (≈1 s each) → seat counter card {{remaining}} → Isha line.",
    onscreen="LAST CALL · {{remaining}} SEATS · CLOSES {{date}}",
    shots=[("One line to camera", TH)],
    source="Campaign footage + LAF",
    shoot_by="Sat 9 Jan",
    edit="Only if the seat number is true.",
    caption=("Last call 🚨 {{remaining}} seats · closes {{date}}.\n\nComment SAFARI now.\n\n#lastcall #safari #lostandfree #travelwithisha"),
    deps="Real seat count.")

add(id="W8-T1", week=8, date="Tue 12 Jan 2027", day="Tue", time="7:00 PM", acct="@travelwithisha", collab="—",
    type="Reel", fmt="A · day-in-life (30-40 s)",
    title="\"One week before the jungle: day in my life\"",
    goal="Excitement + authenticity from her own account in the final week.",
    cta="Comment 'COMING' if you're joining me",
    script="Short VO lines over her day: wake up, coffee, checking the group chat ('{{N}} of you are coming!'), shopping for gear, evening packing. Last line: \"7 din. Aur mujhe neend nahi aa rahi.\"",
    screenplay="Format A, 1.2-1.5 s cuts, time stamps on screen (7:00 AM, 1 PM, 9 PM).",
    onscreen="7 DAYS TO GO · time stamps",
    shots=[("10-15 short clips of your day (3-5 sec each): waking, coffee, group chat screen, shopping, packing", TH_OUT + " Indoor clips: Setup A light. Vary angles; never 2 similar shots back to back."), ("VO lines", VO)],
    source="Isha shoot",
    shoot_by="Sat 9 Jan",
    edit="Spaced caps captions (day-in-life). Blur any private chat names.",
    caption=("7 days to go and I'm already awake at 5 AM 😅🐅\n\nComing with me? Comment COMING.\n\n#dayinmylife #travelwithisha"),
    deps="Group-chat screenshot with names blurred.")

add(id="W8-L2", week=8, date="Wed 13 Jan 2027", day="Wed", time="7:30 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Reel", fmt="B · testimonial (20-30 s)",
    title="\"Why they booked (real people from the group)\"",
    goal="SOCIAL PROOF for the last fence-sitters.",
    cta="Comment SAFARI before {{date}}",
    script="2-3 people who signed up send a 5-sec selfie video: 'Main {{name}}, aur main aa rahi/raha hoon kyunki…'. Isha closes: 'Aur tum?'",
    screenplay="Grid of selfie clips → one by one full screen → Isha close.",
    onscreen="WHY THEY BOOKED · names · AND YOU?",
    shots=[("Isha close line", TH)],
    source="Sign-ups (with written consent) + Isha",
    shoot_by="Sat 9 Jan",
    edit="Only real people with consent. If fewer than 2, swap this for a LAF past-guest testimonial.",
    caption=("They're in. Are you? 🐾\n\nSign-ups close {{date}}. Comment SAFARI.\n\n#safari #lostandfree #travelwithisha"),
    deps="Consent + clips from 2-3 sign-ups (LAF to request).")

add(id="W8-L3", week=8, date="Fri 15 Jan 2027", day="Fri", time="11:00 AM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Static post (single image)", fmt="Post · countdown",
    title="\"Sign-ups close tonight\"",
    goal="Final conversion push on the last day.",
    cta="Link in bio / Comment SAFARI (auto-DM until midnight)",
    script="Poster: 'SIGN-UPS CLOSE TONIGHT' · {{remaining}} seats · {{dates}} · tiger photo",
    screenplay="Single image + story link sticker every 3 hours on both accounts.",
    onscreen="SIGN-UPS CLOSE TONIGHT",
    shots=[("None", "—")],
    source="LAF design",
    shoot_by="—",
    edit="Bold, high contrast, readable as a thumbnail.",
    caption=("Tonight at midnight, sign-ups close ⏳\n\nComment SAFARI or tap the link in bio.\n\n#lastchance #safari #lostandfree #travelwithisha"),
    deps="Close date confirmed.")

add(id="W8-T2", week=8, date="Sat 16 Jan 2027", day="Sat", time="7:00 PM", acct="@travelwithisha", collab="Collab with @lostandfree",
    type="Reel", fmt="B · loop (25-30 s)",
    title="\"Remember when I said I want to leave Mumbai every morning?\"",
    goal="Pays off the Diwali loop reel (R1) and closes the campaign story; sets up trip content and the next batch waitlist.",
    cta="Follow for the trip · comment NEXT for the next batch",
    script=(
        "1. \"Yaad hai Diwali pe maine kaha tha, har subah Mumbai chhodne ka mann karta hai?\"\n"
        "2. \"Toh… ab main sach mein ja rahi hoon. Aur {{N}} log mere saath.\"\n"
        "3. \"Thank you, sach mein.\"\n"
        "4. \"Agla batch? Comment NEXT. Ab jungle se milte hain.\""),
    screenplay="Opens on the same framing/outfit as R1 (callback) → departure: bag, door, cab/train window → group photo or LAF jeep → loop to 'yaad hai'.",
    onscreen="REMEMBER THIS? · {{N}} OF YOU ARE COMING · NEXT BATCH: COMMENT NEXT",
    shots=[("Talking head in the same spot + outfit as the Diwali 'leave Mumbai' reel", TH + " Match the R1 framing: same seat, same background, same outfit."),
           ("Departure clips: locking the door, cab/train window, station/airport (3-4 sec each)", TH_OUT)],
    source="Isha shoot",
    shoot_by="Sat 16 Jan (morning)",
    edit="Loop like R1: last line cuts back into the first. Original colour.",
    caption=("I said I'd leave Mumbai. I didn't say I'd go alone 🐅💛\n\nThank you to everyone coming. Next batch? Comment NEXT.\n\n#travelwithisha #lostandfree #safari"),
    deps="If the safari date is later than 16 Jan, move this to the departure day and post 'last call' content until then.")

# ---- replacement for Sat 28 Nov (aim: TWI promotes the safari OR her existing series) ----
add(id="W1-T2b", week=1, date="Sat 28 Nov 2026", day="Sat", time="7:00 PM", acct="@travelwithisha", collab="—",
    type="Reel", fmt="Existing series · Lakshadweep Part 2 + safari end card (≈40 s)",
    title="\"Lakshadweep Part 2: what happened 12 metres down\"",
    goal="Pays off Part 1's cliffhanger ('…woh Part 2 mein'), so her own followers come back, then hands them to the safari with a 4-sec end card.",
    cta="Save · 'Part 3? Jungle.' → comment SAFARI / link in bio",
    script=(
        "Part 2 voiceover is already recorded and edited (inbox/lakshadweep_part2/lakshadweep_reel_part2_no_music.mp4).\n"
        "NEW end line, to camera (4 sec): \"Paani ho gaya. Part 3? Jungle. {{dates}}, Lost & Free ke saath. Comment SAFARI.\""),
    screenplay=(
        "0-36s   Part 2 as edited (dive at 12 m, the night with friends). Open on the strongest underwater frame with 'PART 2' so Part-1 viewers recognise it.\n"
        "36-40s  Hard cut to Isha talking head for the new end line; text PART 3: JUNGLE 🐅 + Comment SAFARI; bubbles SFX → bird call on the cut."),
    onscreen="PART 2 · (existing captions) · PART 3: JUNGLE · Comment SAFARI",
    shots=[("End line to camera, 3 takes (same top/room as Part 1 if possible, so it feels like the series)", TH)],
    source="Existing Part 2 render in the repo + 1 new 4-sec line",
    shoot_by="Sat 28 Nov (morning)",
    edit="Reuse the Part 2 edit as it is (same captions and handle style as Part 1). Only append the end card. Add music in Instagram (render has no music).",
    caption=("Part 2 🌊 what happened 12 m down, and the night after.\n\nPart 3 is the jungle 🐅 {{dates}} with @lostandfree. Comment SAFARI for the link.\n\n"
             "#lakshadweep #scubadiving #travelwithisha #lostandfree #safari"),
    deps="Confirm Part 2 isn't posted yet. If it is, use the backlog's 'solo travel' carousel with a safari last slide instead.")
