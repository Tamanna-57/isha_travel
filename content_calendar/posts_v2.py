# v2 rewrite of the 8 posts (23 Nov - 2 Dec) using the social-media skills:
#   short-form-video-script / reels-script : 3-channel hook in 0-3 s, beats = SHOT | TEXT | SAYS (muted-first),
#       ~75 words per 30 s, visual change every 2-4 s, one CTA, ending that loops to frame 1, cover brief, "who sends this?"
#   hook-writer   : 5 hooks per post from different mechanisms, best one first (test #2 as a Trial Reel)
#   instagram-seo : one search keyword said in the first 3 s + on screen + in the caption's first line (<125 chars)
#   caption-writer: first line earns the "...more" tap, body delivers, ONE call to action
#   hashtag-strategy: max 5 tags (IG cap), topic + niche + campaign tag, rotated per post
#   carousel-writer : cover = hook + promise, one idea per slide, payoff slide then CTA slide
# Campaign tag: #JungleWithIsha (check on Instagram that it's unused before the first post).

from posts import TH

V2 = {}

V2["W1-L1"] = dict(
    keyword="tiger safari in {{park}}",
    hooks=("1. PAYOFF (recommended): zips bag → TEXT 'TIGER SAFARI: DATES ARE OUT' · SAYS 'Tiger safari ki details aa gayi.'\n"
           "2. SCARCITY (Trial Reel): TEXT 'ONLY {{seats}} SEATS' · SAYS 'Sirf {{seats}} log. Aur ek seat meri.'\n"
           "3. IDENTITY: TEXT 'NEVER SEEN A TIGER OUTSIDE A ZOO?' · SAYS 'Kabhi zoo ke bahar tiger dekha hai?'\n"
           "4. SPECIFIC: TEXT '{{N}} DAYS · 1 JUNGLE · 0 NETWORK'\n"
           "5. CALLBACK (for followers): TEXT 'REMEMBER \"DETAILS SOON\"?' · SAYS 'Yaad hai, details soon? Toh…'"),
    script=("Tiger safari ki details aa gayi. {{N}} din, {{park}}, Lost & Free ke saath. "
            "Subah saadhe paanch baje open jeep… engine band, aur poora jungle chup. "
            "Main inke saath isliye ja rahi hoon: ye animals ko chase nahi karte. Wait karte hain. "
            "{{dates}}. Sirf {{seats}} seats. ₹{{price}}, sab included. "
            "Comment karo SAFARI, main link bhejti hoon. Bag ready hai. Tumhara?  (≈60 words)"),
    screenplay=(
        "0-2s   SHOT Isha zips a duffel shut, looks up into the lens | TEXT TIGER SAFARI: DATES ARE OUT | SAYS 'Tiger safari ki details aa gayi.'\n"
        "2-5s   SHOT LAF jeep on a misty forest track | TEXT 01 · {{N}} days · {{park}} | SAYS '{{N}} din, {{park}}, Lost & Free ke saath.'\n"
        "5-8s   SHOT deer frozen, ears up | TEXT 02 · 5:30 AM open jeep | SAYS 'Subah saadhe paanch baje open jeep…'\n"
        "8-11s  SHOT guide lowers binoculars, engine cuts (sound drops) | TEXT 03 · engine off. silence. | SAYS '…engine band, aur poora jungle chup.'\n"
        "11-16s SHOT split: Isha top / tiger photo bottom | TEXT WE DON'T CHASE. WE WAIT. | SAYS 'Main inke saath isliye… wait karte hain.'\n"
        "16-22s SHOT paper card, lines tick in | TEXT {{dates}} · {{seats}} seats · ₹{{price}} all-in | SAYS '{{dates}}. Sirf {{seats}} seats…'\n"
        "22-27s SHOT Isha direct to lens, lean in | TEXT COMMENT \"SAFARI\" → link in your DMs | SAYS 'Comment karo SAFARI, main link bhejti hoon.'\n"
        "27-29s SHOT Isha unzips the bag again (same framing as 0s) | TEXT — | SAYS 'Bag ready hai. Tumhara?' → LOOPS into the zip at 0s"),
    onscreen="TIGER SAFARI: DATES ARE OUT · 01 {{N}} days · {{park}} · 02 5:30 AM open jeep · 03 engine off. silence. · WE DON'T CHASE. WE WAIT. · {{dates}} · {{seats}} seats · ₹{{price}} all-in · COMMENT \"SAFARI\"",
    cover="Isha holding the packed duffel, smiling at lens; centred text TIGER SAFARI · DATES OUT inside the 4:5 grid area.",
    sends="Sent to 'the friend I'd go with' → the split-cost / travel-buddy DM.",
    caption=("Tiger safari in {{park}} with me: dates, price and seats are finally out 🐅\n\n"
             "{{N}} days with @lostandfree. Open jeep at 5:30 AM, engine off when the jungle goes quiet, no network, nights under the stars.\n\n"
             "📅 {{dates}}\n🪑 Only {{seats}} seats\n💰 ₹{{price}}, stay + meals + {{N}} jeep safaris + naturalist included\n\n"
             "Honest bit: nobody can promise you a tiger. What we promise is the way we look for one: slowly, quietly, never chasing.\n\n"
             "Comment SAFARI and I'll DM you the sign-up link.\n\n"
             "#tigersafari #junglesafari #wildlifeindia #lostandfree #JungleWithIsha"),
)

V2["W1-T1"] = dict(
    keyword="wildlife photography in India",
    hooks=("1. PAYOFF (recommended): tiger photo + alarm SFX · TEXT '7 YEARS OF 5 AM ALARMS' · SAYS 'Saat saal ki wildlife photography, ek reel mein.'\n"
           "2. QUESTION (Trial Reel): TEXT 'WHICH ONE WOULD YOU WAKE UP AT 5 AM FOR?'\n"
           "3. AUTHORITY: TEXT 'WILDLIFE PHOTOGRAPHY IN INDIA · 2018 → 2025'\n"
           "4. CONTRARIAN: TEXT 'NONE OF THESE WERE LUCK'\n"
           "5. STORY: SAYS '2018 mein maine pehli baar jungle mein camera uthaya…'"),
    script=("Saat saal ki wildlife photography, ek reel mein. Har trip pe ek hi rule: 5 baje ka alarm. "
            "Kabhi harrier mila. Kabhi ek ullu jo blink hi nahi karta tha. Kabhi jackal jo seedha camera mein dekhta tha. "
            "Aur ek din… ye. Lekin best moment photo nahi hota. Woh second hota hai jab jungle bilkul chup ho jaata hai. "
            "Is baar… tum mere saath chal rahe ho.  (≈65 words)"),
    screenplay=(
        "0-2s   SHOT Isha's tiger photo, slow push, alarm-clock SFX | TEXT 7 YEARS OF 5 AM ALARMS | SAYS 'Saat saal ki wildlife photography, ek reel mein.'\n"
        "2-11s  SHOT her photos on the beat (~0.9 s each; never 2 birds in a row), shutter SFX each | TEXT year tag per photo (2018, 2019…) + 'which number?' counter 1-9 | SAYS 'Har trip pe ek hi rule… harrier… ullu… jackal…'\n"
        "11-14s SHOT tiger photo holds | TEXT AND THEN… THIS | SAYS 'Aur ek din… ye.'\n"
        "14-20s SHOT Isha lifts her camera at a window; audio drops to 0.7 s of silence | TEXT THE BEST PART ISN'T THE PHOTO | SAYS 'Lekin best moment photo nahi hota…'\n"
        "20-24s SHOT Isha whisper to lens, small smile | TEXT THIS TIME, YOU'RE COMING WITH ME | SAYS 'Is baar… tum mere saath chal rahe ho.'\n"
        "24-25s SHOT cut to black → alarm SFX → LOOPS to the tiger at 0s"),
    onscreen="7 YEARS OF 5 AM ALARMS · numbered photos 1-9 with years · AND THEN… THIS · THE BEST PART ISN'T THE PHOTO · THIS TIME, YOU'RE COMING WITH ME",
    cover="Her best tiger photo full-bleed, text 7 YEARS OF 5 AM ALARMS centred.",
    sends="Sent to friends who love animals/photography ('look at no. 4') → numbering the photos makes it easy to talk about.",
    caption=("Wildlife photography in India, 2018 → 2025: 7 years of 5 AM alarms in one reel 🐅\n\n"
             "A harrier in the grass, an owlet that refused to blink, a jackal that walked straight at my lens. And then one morning, a tiger.\n\n"
             "Which number is your favourite? Tell me below 👇\n\n"
             "(This winter I'm taking a few of you into the jungle with @lostandfree. Details are in my bio.)\n\n"
             "#wildlifephotography #indianwildlife #birdphotography #travelwithisha #JungleWithIsha"),
)

V2["W1-L2"] = dict(
    # Isha (21 Nov): the day-by-day itinerary isn't fixed yet -> a REEL listing the activities, no days or times.
    time="7:30 PM", type="Reel", fmt="A · numbered list, talking head + B-roll (25-30 s)",
    title="\"Tiger safari is just the start: everything we'll do in the jungle\"",
    goal="CONVERT people who watched Monday's reel: shows what the trip actually feels like without committing to a day-by-day plan.",
    cta="Comment SAFARI → link in DMs",
    keyword="things to do on a jungle safari",
    hooks=("1. LIST (recommended): Isha holds up 6 fingers · TEXT '6 THINGS WE'LL DO IN THE JUNGLE (ONLY ONE IS THE TIGER)' · SAYS 'Jungle safari pe sirf tiger nahi dekhte.'\n"
           "2. CONTRARIAN (Trial Reel): TEXT 'THE TIGER IS THE LEAST OF IT' · SAYS 'Honestly, tiger toh bonus hai.'\n"
           "3. CURIOSITY: TEXT 'WHAT DO YOU EVEN DO ON A JUNGLE SAFARI?'\n"
           "4. IDENTITY: TEXT 'NOT A WILDLIFE PERSON? YOU'LL STILL LOVE #4'\n"
           "5. PAYOFF: first frame = bonfire under stars · TEXT 'THIS IS ALSO A SAFARI'"),
    script=("Jungle safari pe sirf tiger nahi dekhte. Ye sab karoge. "
            "Ek: subah open jeep, jab jungle jaag raha hota hai. "
            "Do: shaam ki safari, golden light mein. "
            "Teen: naturalist ke saath walk, pugmarks aur birds dhundhna. "
            "Chaar: bonfire aur jungle ki kahaaniyan. "
            "Paanch: raat ko taare, network zero. "
            "Chhe: mere saath wildlife photography, phone se bhi. "
            "Kaunsa sabse pehle karoge? Comment SAFARI, link bhejti hoon.  (≈60 words)\n"
            "Keep only the activities Lost & Free confirms; swap or drop the rest (a 4- or 5-item list works the same way)."),
    screenplay=(
        "0-2s   SHOT Isha to lens, holds up 6 fingers | TEXT 6 THINGS WE'LL DO IN THE JUNGLE (ONLY ONE IS THE TIGER) | SAYS 'Jungle safari pe sirf tiger nahi dekhte. Ye sab karoge.'\n"
        "2-5s   SHOT LAF open jeep at dawn | TEXT 01 · MORNING OPEN-JEEP SAFARI | SAYS 'Ek: subah open jeep…'\n"
        "5-8s   SHOT LAF evening safari, golden light | TEXT 02 · EVENING SAFARI | SAYS 'Do: shaam ki safari…'\n"
        "8-12s  SHOT LAF guide pointing at pugmarks / binoculars on a bird | TEXT 03 · NATURE WALK WITH A NATURALIST | SAYS 'Teen: naturalist ke saath walk…'\n"
        "12-15s SHOT LAF bonfire, people laughing | TEXT 04 · BONFIRE + JUNGLE STORIES | SAYS 'Chaar: bonfire…'\n"
        "15-18s SHOT night sky / torchlit camp | TEXT 05 · STARS. ZERO NETWORK. | SAYS 'Paanch: raat ko taare…'\n"
        "18-22s SHOT Isha with camera, showing her phone screen to someone | TEXT 06 · WILDLIFE PHOTOGRAPHY WITH ME | SAYS 'Chhe: mere saath wildlife photography…'\n"
        "22-27s SHOT Isha to lens, leans in | TEXT WHICH ONE FIRST? · COMMENT \"SAFARI\" | SAYS 'Kaunsa sabse pehle karoge? Comment SAFARI…'\n"
        "27-28s SHOT Isha raises 6 fingers again → LOOPS to 0s"),
    onscreen="6 THINGS WE'LL DO IN THE JUNGLE (ONLY ONE IS THE TIGER) · 01 MORNING OPEN-JEEP SAFARI · 02 EVENING SAFARI · 03 NATURE WALK WITH A NATURALIST · 04 BONFIRE + JUNGLE STORIES · 05 STARS. ZERO NETWORK. · 06 WILDLIFE PHOTOGRAPHY WITH ME · COMMENT \"SAFARI\"",
    cover="Isha holding up 6 fingers, text 6 THINGS WE'LL DO IN THE JUNGLE centred in the 4:5 area.",
    sends="Sent to the friend who says 'safari is boring, it's just animals'.",
    shots=[("Talking head: opening line (holding up 6 fingers) + closing line, 3 takes each. Outfit different from Monday's reel", TH),
           ("Optional: one short talking-head line per activity, so your face comes back between the B-roll (\"Ek: subah open jeep…\" etc.)", TH),
           ("You with your camera, showing the screen to someone off-camera (4 sec) for #6", "Setup A light, phone on tripod at chest height, side-on to the window; a friend's hand comes in to look at the screen.")],
    source="Isha shoot + LAF footage/photos for each activity (morning jeep, evening safari, walk, bonfire, night sky)",
    shoot_by="Sun 22 Nov",
    edit="Format A numbered list (same card style as the 'How to see a tiger' reel). Cut back to Isha's face every 2 activities. One sound per card (tick). Original colour.",
    caption=("Things to do on a jungle safari, besides the tiger 🐅🔥✨\n\n"
             "Morning open-jeep safari · evening safari in golden light · a nature walk with a naturalist · bonfire + jungle stories · stars with zero network · wildlife photography with @travelwithisha\n\n"
             "Which one would you do first? Comment SAFARI and we'll DM you the link for our {{dates}} trip.\n\n"
             "#junglesafari #tigersafari #wildlifeindia #lostandfree #JungleWithIsha"),
    deps="Lost & Free confirms which of the 6 activities are on the trip (drop the rest); LAF B-roll/photos for each activity. No days or times needed.",
)

V2["W1-L3"] = dict(
    keyword="jungle safari POV",
    hooks=("1. POV (recommended): TEXT 'POV: 5:30 AM, YOUR FIRST JUNGLE SAFARI'\n2. SOUND (Trial Reel): TEXT 'THIS IS WHAT 5:30 AM SOUNDS LIKE IN A TIGER RESERVE 🔊'\n"
           "3. CHALLENGE: TEXT 'WAIT FOR THE SILENCE'\n4. RELATABLE: TEXT 'THE ONLY ALARM I DON'T SNOOZE'\n5. STAKES: TEXT 'ENGINE OFF. NOBODY MOVES.'"),
    script="No talking until the end. Isha whispers at 13 s: \"Shhh… sun.\"",
    screenplay=(
        "0-1.5s SHOT dark room, phone alarm, Isha's hand reaches for it but doesn't snooze | TEXT POV: 5:30 AM, YOUR FIRST JUNGLE SAFARI | SOUND alarm\n"
        "1.5-4s SHOT LAF: jeep engine starts in cold blue light | TEXT — | SOUND engine, birds\n"
        "4-9s   SHOT LAF jeep-POV, one unbroken take down the track | TEXT (small) day 1 · 5:47 AM | SOUND forest\n"
        "9-11s  SHOT jeep stops, engine off | TEXT ENGINE OFF. NOBODY MOVES. | SOUND sudden silence, then a deer alarm call\n"
        "11-14s SHOT LAF tiger/leopard crosses (or a deer staring into lens) | TEXT — | SOUND footsteps on dry leaves\n"
        "14-16s SHOT black; Isha whisper | TEXT — | SAYS 'Shhh… sun.' → alarm at 0s (LOOP)"),
    onscreen="POV: 5:30 AM, YOUR FIRST JUNGLE SAFARI · day 1 · 5:47 AM · ENGINE OFF. NOBODY MOVES.",
    cover="Jeep-POV frame on the misty track, text POV: YOUR FIRST JUNGLE SAFARI.",
    sends="'Send this to the one friend who'd actually wake up for this' → DM shares are the goal of this reel.",
    caption=("Jungle safari POV: 5:30 AM, an open jeep, and the moment the engine goes quiet 🐅🔊\n\n"
             "Watch it with the sound on.\n\n"
             "Send this to the one friend who'd actually wake up for it.\n\n"
             "(Our {{dates}} safari with @travelwithisha: details in our bio.)\n\n"
             "#junglesafari #safaripov #tigersafari #lostandfree #JungleWithIsha"),
)

V2["W1-T2b"] = dict(
    keyword="Lakshadweep scuba diving",
    hooks=("On-screen hook over the first underwater frame (the edit's VO stays as it is):\n"
           "1. CLIFFHANGER PAYOFF (recommended): 'LAKSHADWEEP PART 2: WHAT HAPPENED 12 M DOWN'\n2. STAKES (Trial Reel): '12 METRES DOWN, AND THEN…'\n"
           "3. SERIES: 'YOU ASKED FOR PART 2'\n4. SPECIFIC: 'MY 2ND DIVE IN LAKSHADWEEP'\n5. QUESTION: 'WOULD YOU GO 12 M DOWN?'"),
    script=("Part 2 voiceover is already recorded and edited (inbox/lakshadweep_part2/lakshadweep_reel_part2_no_music.mp4).\n"
            "NEW end line to camera (4 s): \"Paani ho gaya. Part 3? Jungle. Comment SAFARI.\""),
    screenplay=(
        "0-2s   SHOT strongest underwater frame from Part 2 | TEXT LAKSHADWEEP PART 2: WHAT HAPPENED 12 M DOWN | SAYS (existing VO)\n"
        "2-36s  Existing Part 2 edit unchanged (dive + night with friends); check no two similar underwater shots sit side by side.\n"
        "36-40s SHOT Isha talking head, same top/room as Part 1 | TEXT PART 3: JUNGLE 🐅 · COMMENT SAFARI | SAYS 'Paani ho gaya. Part 3? Jungle. Comment SAFARI.' | SOUND bubbles → bird call on the cut"),
    onscreen="LAKSHADWEEP PART 2: WHAT HAPPENED 12 M DOWN · (existing captions) · PART 3: JUNGLE · COMMENT SAFARI",
    cover="Isha underwater (mask, thumbs up) + PART 2 in the same style as Part 1's cover so they sit together on the grid.",
    sends="Sent to dive/beach friends planning Lakshadweep.",
    caption=("Lakshadweep scuba diving, Part 2: what happened 12 metres down, and the night after 🌊\n\n"
             "Missed Part 1? It's right before this on my grid.\n\n"
             "Part 3 is the jungle 🐅 {{dates}} with @lostandfree. Comment SAFARI and I'll send you the link.\n\n"
             "#lakshadweep #scubadiving #scubaindia #travelwithisha #JungleWithIsha"),
)

V2["W2-L1"] = dict(
    deps="Questions: written (below). Answers: from Lost & Free by Sat 28 Nov. Isha: run a story question box Mon 23-Thu 26 Nov and send the most-asked real questions.",
    keyword="tiger safari for solo female travellers",
    hooks=("Cover options:\n1. QUESTION (recommended): 'IS A TIGER SAFARI SAFE FOR A SOLO GIRL? Honest answers →'\n"
           "2. LIST: 'The 6 questions everyone DMs us before a safari →'\n3. CONTRARIAN: 'We won't promise you a tiger. Here's why →'\n"
           "4. IDENTITY: 'Going solo? Read this first →'\n5. MYTH: 'Safaris aren't only for families →'"),
    script=("S1 COVER (Isha laughing at her DMs): IS A TIGER SAFARI SAFE FOR A SOLO GIRL? · small: + 5 more questions you sent us →\n"
            "S2 SAFE FOR SOLO WOMEN? {{LAF's real answer: rooms, guides, who's in the group}} + 'Isha is travelling with the group.'\n"
            "S3 HOW FIT DO I NEED TO BE? {{answer}}\n"
            "S4 WILL I SEE A TIGER? 'Nobody honest can promise that. We can promise {{N}} safaris in the best zones + guides who listen for alarm calls.'\n"
            "S5 NETWORK? FOOD? {{answer}}\n"
            "S6 WHO ELSE IS COMING? {{age range · solo + friends · first-timers}}\n"
            "S7 PAYOFF: 'Most people who ask these come back as the calmest person in the jeep.' ({{only if LAF says so; else cut}})\n"
            "S8 CTA: Still unsure? Ask below, we answer every one · Ready? Comment SAFARI"),
    screenplay="Q headline in gold serif, answer ≤20 words in white. Honest tone; the 'no tiger promise' slide is the trust slide, don't cut it.\n"
               "WHO WRITES WHAT: the questions are already written (Isha doesn't need to make them). The ANSWERS come from Lost & Free (safety, fitness, network/food, group). "
               "Isha checks they sound true to her and adds 1 line in her own voice on S2. Better still: post a question box in stories Mon 23-Thu 26 Nov and swap in any real question asked more than once.",
    onscreen="As per slides.",
    cover="Isha on her phone, laughing; headline over the lower third.",
    sends="Sent by girls to the friend/parent who worries ('see, it's safe').",
    caption=("Is a tiger safari safe for solo female travellers? The 6 questions you DM'd us most, answered honestly 🐅\n\n"
             "Safety, fitness, network, food, who's coming, and yes, the tiger one.\n\n"
             "Ask anything else below; we answer every comment. When you're ready, comment SAFARI.\n\n"
             "#solofemaletravel #tigersafari #wildlifeindia #lostandfree #JungleWithIsha"),
)

V2["W2-T1"] = dict(
    keyword="scuba diving vs tiger safari",
    hooks=("1. VERSUS (recommended): split screen · TEXT '12 M UNDERWATER vs A TIGER 10 M AWAY' · SAYS '12 metre underwater, ya tiger 10 metre door: zyada scary kya tha?'\n"
           "2. STAKES (Trial Reel): TEXT 'ONLY ONE OF THESE MADE MY HEART STOP'\n3. IDENTITY: TEXT 'SEA PERSON OR JUNGLE PERSON?'\n"
           "4. AUTHORITY: TEXT 'SCUBA DIVING vs TIGER SAFARI: I'VE DONE BOTH'\n5. CURIOSITY: SAYS 'Sab bolte hain scuba scary hai. Unhone jungle nahi dekha.'"),
    script=("12 metre underwater, ya tiger 10 metre door: zyada scary kya tha? "
            "Paani mein sab slow hota hai. Saans pe focus karo, darr chala jaata hai. "
            "Jungle mein ulta. Sab chup… aur dil itna zor se dhadakta hai. "
            "Verdict? Tiger. Paani mein main control mein thi. Jungle mein, jungle control mein hai. "
            "Tum? Sea ya jungle? Comment karo.  (≈60 words)"),
    screenplay=(
        "0-3s   SHOT split: Isha underwater top / tiger bottom | TEXT 12 M UNDERWATER vs A TIGER 10 M AWAY | SAYS '12 metre underwater… zyada scary kya tha?'\n"
        "3-8s   SHOT clear-water dive clips, bubbles SFX | TEXT SEA: EVERYTHING SLOWS DOWN | SAYS 'Paani mein sab slow hota hai…'\n"
        "8-14s  SHOT LAF jeep stops, engine off; heartbeat SFX under silence | TEXT JUNGLE: TOTAL SILENCE | SAYS 'Jungle mein ulta. Sab chup…'\n"
        "14-20s SHOT Isha talking head, punch-in on 'Tiger' | TEXT VERDICT: TIGER 🐅 | SAYS 'Verdict? Tiger…'\n"
        "20-25s SHOT Isha smiling, points down to comments | TEXT SEA 🌊 or JUNGLE 🐅? | SAYS 'Tum? Sea ya jungle? Comment karo.'\n"
        "25-26s SHOT back to the split screen → LOOPS"),
    onscreen="12 M UNDERWATER vs A TIGER 10 M AWAY · SEA: EVERYTHING SLOWS DOWN · JUNGLE: TOTAL SILENCE · VERDICT: TIGER · SEA or JUNGLE?",
    cover="The split screen (Isha diving / tiger) with VS in the middle.",
    sends="Sent to the 'sea vs mountains' debate friend; the comment question drives replies.",
    caption=("Scuba diving vs tiger safari: I've done both, and only one made my heart actually stop 🌊🐅\n\n"
             "12 m down in Lakshadweep, I was in control. 10 m from a tiger, the jungle was.\n\n"
             "SEA or JUNGLE? Tell me below 👇\n\n"
             "(Team jungle: I'm going again {{dates}} with @lostandfree. Link in bio.)\n\n"
             "#scubadiving #tigersafari #lakshadweep #travelwithisha #JungleWithIsha"),
)

V2["W2-L3"] = dict(
    keyword="{{park}} safari cost",
    hooks=("1. MYTH (recommended): notebook '₹{{price}} — expensive?' crossed out · SAYS '₹{{price}} ki tiger safari. Chalo, breakdown karte hain.'\n"
           "2. SPECIFIC (Trial Reel): TEXT 'WHERE EVERY RUPEE OF A ₹{{price}} SAFARI GOES'\n"
           "3. COMPARISON (only if true): TEXT 'BOOKED ALONE, THIS COSTS ₹{{x}}'\n4. QUESTION: TEXT 'HOW MUCH DOES A TIGER SAFARI REALLY COST?'\n5. SPEED: TEXT 'SAFARI COST, EXPLAINED IN 30 SECONDS'"),
    script=("₹{{price}} ki tiger safari. Chalo, breakdown karte hain. "
            "{{N}} raat stay: ₹{{x}}. Saara khaana: ₹{{x}}. "
            "{{N}} jeep safaris: ₹{{x}}. Sabse bada hissa yahi hai. "
            "Naturalist, permits, transfers: ₹{{x}}. "
            "Aur subah 6 baje jungle ki khamoshi? Uska koi price nahi. "
            "{{seats}} seats bachi hain. Comment SAFARI.  (≈50 words)"),
    screenplay=(
        "0-2s   SHOT notebook: Isha writes ₹{{price}}, red marker strikes 'expensive?' | TEXT {{PARK}} SAFARI COST, BROKEN DOWN | SAYS '₹{{price}} ki tiger safari. Chalo, breakdown karte hain.'\n"
        "2-5s   SHOT LAF stay/room | TEXT STAY · {{N}} nights · ₹{{x}} (tick SFX) | SAYS '{{N}} raat stay…'\n"
        "5-8s   SHOT LAF food | TEXT ALL MEALS · ₹{{x}} | SAYS 'Saara khaana…'\n"
        "8-12s  SHOT LAF jeeps lined up at the gate | TEXT {{N}} JEEP SAFARIS · ₹{{x}} ← the biggest part | SAYS '{{N}} jeep safaris… sabse bada hissa yahi hai.'\n"
        "12-16s SHOT LAF guide at the permit gate | TEXT NATURALIST + PERMITS + TRANSFERS · ₹{{x}} | SAYS 'Naturalist, permits, transfers…'\n"
        "16-21s SHOT dawn forest, no music, birds only | TEXT 6 AM SILENCE · ₹0 | SAYS 'Aur subah 6 baje… koi price nahi.'\n"
        "21-25s SHOT Isha to lens | TEXT {{seats}} SEATS LEFT · COMMENT \"SAFARI\" | SAYS '{{seats}} seats bachi hain. Comment SAFARI.'\n"
        "25-26s SHOT back to the notebook price → LOOPS"),
    onscreen="{{PARK}} SAFARI COST, BROKEN DOWN · STAY ₹{{x}} · MEALS ₹{{x}} · {{N}} JEEP SAFARIS ₹{{x}} · NATURALIST + PERMITS ₹{{x}} · 6 AM SILENCE ₹0 · COMMENT \"SAFARI\"",
    cover="Notebook close-up with ₹{{price}} and the red strike-through, text SAFARI COST, BROKEN DOWN.",
    sends="Sent to the friend who said 'too expensive' → screenshot-able numbers.",
    caption=("{{park}} safari cost: where every rupee of ₹{{price}} goes 💸🐅\n\n"
             "Stay ₹{{x}} · all meals ₹{{x}} · {{N}} jeep safaris ₹{{x}} · naturalist, permits and transfers ₹{{x}}.\n"
             "6 AM jungle silence: free.\n\n"
             "{{seats}} seats left for {{dates}} with @travelwithisha. Comment SAFARI and we'll DM you the link.\n\n"
             "#tigersafari #safaricost #wildlifeindia #lostandfree #JungleWithIsha"),
)
