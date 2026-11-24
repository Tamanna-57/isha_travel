# Week 2 (30 Nov - 6 Dec) update, 24 Nov: three topics from the Monday-reel feedback become a 3-part @lostandfree
# series "Corbett, unfiltered". Each post: base fields (posts.py shape) + v2 fields (posts_v2.py shape) in one dict.
# Facts marked VERIFY must be checked against the cited source before posting; never post a number we can't source.
from posts import TH, TH_OUT, VO, ARCH

# Learnings from Isha's feedback on the W1-L1 and W1-T1 edits, applied to every reel below
LEARN = ("House rules from Isha's feedback: bold Anton opening title (two-tone marigold/white); karaoke captions with the key "
         "words highlighted in marigold; only her own photos (or Lost & Free's) as B-roll; natural colour correction on her "
         "clips; every pause tightened, 1.1x speed; no gap or flash between photos (frame scan before delivery); SFX on "
         "every visual beat; face back on screen every 2-3 photos.")

W2 = []

W2.append(dict(
    id="W2-C1", week=2, date="Mon 30 Nov 2026", day="Mon", time="7:30 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Reel", fmt="B · storytime + map + her forest photos (30-35 s) · Corbett, unfiltered 1/3",
    title="\"Before Jim Corbett became a national park, this forest had a very different story\"",
    goal="REACH + AUTHORITY (history hooks get shared and saved). Positions Lost & Free as people who know the forest, a week after the Corbett announcement.",
    cta="Comment SAFARI (Part 2 on Wednesday)",
    keyword="Jim Corbett National Park history",
    hooks=("1. CURIOSITY (recommended): Isha to lens · TEXT 'BEFORE IT WAS JIM CORBETT…' · SAYS 'Jim Corbett National Park banne se pehle, is jungle ki kahaani bilkul alag thi.'\n"
           "2. SURPRISE (Trial Reel): TEXT 'THE MAN THIS PARK IS NAMED AFTER HUNTED TIGERS'\n"
           "3. AUTHORITY: TEXT 'INDIA'S FIRST NATIONAL PARK HAD A DIFFERENT NAME'\n"
           "4. TIMELINE: TEXT '1936 → 1973: THE STORY NOBODY TELLS YOU'\n"
           "5. QUESTION: TEXT 'WHO WAS JIM CORBETT, REALLY?'"),
    script=("Jim Corbett National Park banne se pehle, is jungle ki kahaani bilkul alag thi. "
            "1936 mein ye India ka pehla national park bana, aur naam tha Hailey National Park. "
            "Phir iska naam Ramganga hua, aur uske baad Jim Corbett. "
            "Aur Jim Corbett kaun the? Ek shikari, jo man-eater tigers ko track karte the. "
            "Aur wahi insaan aage chalke tigers ko bachane ki baat karne laga. "
            "1973 mein Project Tiger yahin se shuru hua. "
            "Toh agli baar jab jeep mein baitho, yaad rakhna: ye jungle second chances ki kahaani hai. "
            "Comment SAFARI.  (≈80 words)\n"
            "VERIFY before shooting: Hailey NP 1936 · renamed Ramganga (1954-55) then Corbett (1956-57) · Project Tiger launched at Corbett 1 Apr 1973 "
            "(sources: Corbett Tiger Reserve / Uttarakhand Forest Dept, NTCA). Say only the years we've confirmed."),
    screenplay=(
        "0-3s   SHOT Isha to lens, leaning in | TEXT (Anton) BEFORE IT WAS / JIM CORBETT… | SAYS 'Jim Corbett National Park banne se pehle…'\n"
        "3-8s   SHOT Google Earth fly-in to Corbett (Ramganga reservoir) | TEXT 1936 · INDIA'S FIRST NATIONAL PARK | SAYS '1936 mein ye India ka pehla national park bana…'\n"
        "8-12s  SHOT her misty-forest tiger photo, slow push | TEXT HAILEY → RAMGANGA → CORBETT (each name ticks in) | SAYS 'naam tha Hailey… Ramganga… Jim Corbett.'\n"
        "12-16s SHOT Isha, punch-in | TEXT WHO WAS JIM CORBETT? | SAYS 'Aur Jim Corbett kaun the?'\n"
        "16-21s SHOT her tiger-walking photo, desaturated to b/w then colour returns on 'bachane' | TEXT A HUNTER… WHO BECAME A CONSERVATIONIST | SAYS 'Ek shikari… bachane ki baat karne laga.'\n"
        "21-25s SHOT her tiger-on-road photo | TEXT 1973 · PROJECT TIGER STARTS HERE | SAYS '1973 mein Project Tiger yahin se shuru hua.'\n"
        "25-31s SHOT Isha to lens | TEXT A FOREST OF SECOND CHANCES · COMMENT \"SAFARI\" | SAYS 'Toh agli baar… Comment SAFARI.'\n"
        "31-32s SHOT back to the opening framing → LOOPS"),
    onscreen="BEFORE IT WAS JIM CORBETT… · 1936 · INDIA'S FIRST NATIONAL PARK · HAILEY → RAMGANGA → CORBETT · WHO WAS JIM CORBETT? · A HUNTER… WHO BECAME A CONSERVATIONIST · 1973 · PROJECT TIGER STARTS HERE · A FOREST OF SECOND CHANCES · COMMENT \"SAFARI\" · PART 1/3",
    cover="Isha + misty forest split, text BEFORE IT WAS JIM CORBETT… (Anton) inside the 4:5 area; small 'PART 1/3'.",
    sends="Sent to the history/trivia friend and to anyone who's been to Corbett ('did you know this?').",
    shots=[("Talking head, all lines, 3 takes each (outfit different from the R1 maroon top; olive/khaki works for the series)", TH),
           ("Google Earth screen recording: India → Uttarakhand → Corbett / Ramganga reservoir, 10 sec, 2 recordings",
            "Google Earth app, 3D on, start zoomed out on India, search 'Jim Corbett National Park', let it fly in. Phone screen-record, vertical."),
           ("Optional: 3 sec of you flipping through an old book / map (any) for the history mood", "Top-down on a table by the window, hands only, slow page turn.")],
    source="Isha shoot + Google Earth recording + her archive photos (misty tiger, tiger walking, tiger on road)",
    shoot_by="Sat 28 Nov",
    edit="Format B. " + LEARN + " History beat: one photo goes b/w and colour returns on 'bachane' (the only special effect). Ticks on each year/name.",
    caption=("Jim Corbett National Park history: before it was 'Corbett', this forest had a very different story 🐅\n\n"
             "1936: India's first national park, called Hailey National Park. Then Ramganga. Then Corbett, after a hunter of man-eaters who became one of the forest's loudest defenders. "
             "And in 1973, Project Tiger began right here.\n\n"
             "Part 1 of 3: Corbett, unfiltered. Part 2 on Wednesday.\n\n"
             "Want to see it with us? Comment SAFARI.\n\n"
             "#jimcorbettnationalpark #tigersafari #wildlifeindia #lostandfree #JungleWithIsha"),
    deps="VERIFY all dates with Corbett Tiger Reserve / Uttarakhand Forest Dept / NTCA. No archival photos of Jim Corbett unless Lost & Free has the rights."))

W2.append(dict(
    id="W2-C2", week=2, date="Wed 2 Dec 2026", day="Wed", time="1:00 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Carousel (8 slides, 1080×1350)", fmt="Carousel · myth-bust / data · Corbett, unfiltered 2/3",
    title="\"We celebrate tiger numbers. But are we measuring the health of the entire forest?\"",
    goal="SAVES + SHARES + TRUST. The 'uncomfortable truth' makes Lost & Free the thoughtful operator, not just a tiger-sighting seller.",
    cta="Save · share · comment SAFARI",
    keyword="tiger population in India",
    hooks=("Cover options:\n1. CONTRARIAN (recommended): 'WE CELEBRATE TIGER NUMBERS. BUT IS THE FOREST OK? →'\n"
           "2. DATA: '{{3,682}} TIGERS. THAT'S NOT THE WHOLE STORY →'\n3. QUESTION: 'What does a healthy forest actually look like? →'\n"
           "4. CURIOSITY: 'The number nobody talks about →'\n5. STAKES: 'Tigers are thriving. Is the jungle?'"),
    script=("S1 COVER (Isha's tiger photo): WE CELEBRATE TIGER NUMBERS. BUT IS THE FOREST OK? · small: the uncomfortable truth · 2/3 →\n"
            "S2 THE GOOD NEWS: India counted {{3,682}} tigers in 2022, about three-quarters of the world's wild tigers. That's real progress. (VERIFY: NTCA, Status of Tigers 2022)\n"
            "S3 BUT: a tiger count is one number. A forest is thousands.\n"
            "S4 WHAT A HEALTHY FOREST NEEDS: prey (deer, gaur, langur) · grasslands + water · birds and small predators · corridors to other forests\n"
            "S5 THE PRESSURES YOU DON'T SEE: shrinking corridors · invasive weeds like lantana · roads · jeeps crowding one sighting ({{LAF to confirm wording}})\n"
            "S6 MORE TIGERS IN THE SAME FOREST CAN MEAN MORE CONFLICT with villages at the edge. ({{LAF to confirm}})\n"
            "S7 WHAT WE DO: small groups · never crowd a sighting · our guides track birds and deer as closely as tigers · {{only add what Lost & Free actually does}}\n"
            "S8 CTA: Come for the tiger. Fall for the whole forest. · Save this · Comment SAFARI"),
    screenplay="Cover = question + promise. One idea per slide (headline ≤8 words + 1 short line). Photos change type every slide: tiger → grassland (her kite photo) → dholes → kingfisher → jackal → owl → Isha.",
    onscreen="As per slides; source line on S2 ('Source: NTCA, Status of Tigers 2022').",
    cover="Her tiger-looking-up photo, headline in Anton over the lower third, legible at thumbnail size; small '2/3'.",
    sends="Sent to the 'conservation is my thing' friend; screenshot-able S4.",
    shots=[("None to shoot. Send any photos of deer, gaur, grassland or waterholes you have (originals)", ARCH)],
    source="Isha's archive (tiger, grassland kite, dholes, kingfisher, jackal, owl) + Lost & Free's facts",
    shoot_by="Sat 28 Nov (photos only)",
    edit="Lost & Free editorial carousel design (gold serif headlines, white body). Anton only on the cover to tie the series together.",
    caption=("Tiger population in India keeps rising, and that's worth celebrating 🐅 But is the whole forest healthy?\n\n"
             "A tiger count is one number. A forest is prey, grasslands, water, birds, corridors and the villages at its edge. "
             "Swipe for what we look at on every safari.\n\n"
             "Part 2 of 3: Corbett, unfiltered. Save it, and comment SAFARI to come see the whole forest with us.\n\n"
             "Source: NTCA, Status of Tigers 2022.\n\n"
             "#tigerpopulation #wildlifeconservation #jimcorbettnationalpark #lostandfree #JungleWithIsha"),
    deps="VERIFY the tiger estimate + share with the NTCA 2022 report; Lost & Free approves slides 5-7 (their stance + what they actually do)."))

W2.append(dict(
    id="W2-C3", week=2, date="Fri 4 Dec 2026", day="Fri", time="7:30 PM", acct="@lostandfree", collab="Collab with @travelwithisha",
    type="Reel", fmt="A · talking head + her photos (25-30 s) · Corbett, unfiltered 3/3",
    title="\"Your first safari might not include a tiger sighting. Here's why you should go anyway.\"",
    goal="CONVERT the fence-sitters: answers the #1 objection honestly (also the 'will I see a tiger?' FAQ). Ends the series on the sign-up ask.",
    cta="Comment SAFARI → link in DMs",
    keyword="first jungle safari",
    hooks=("1. HONESTY (recommended): Isha to lens · TEXT (Anton) YOU MIGHT NOT SEE A TIGER. · SAYS 'Sach bataun? Pehli safari pe shayad tiger na dikhe.'\n"
           "2. CONTRARIAN (Trial Reel): TEXT 'STOP GOING ON SAFARI FOR THE TIGER'\n"
           "3. STORY (only if true for Isha): TEXT 'MY FIRST SAFARI: ZERO TIGERS. BEST MORNING EVER.'\n"
           "4. LIST: TEXT '4 THINGS YOU'LL SEE EVEN IF THE TIGER DOESN'T SHOW'\n"
           "5. QUESTION: TEXT 'NO TIGER = WASTED SAFARI?'"),
    script=("Sach bataun? Pehli safari pe shayad tiger na dikhe. Aur agar koi guarantee de, toh samajh jaana jhooth hai. "
            "Lekin phir bhi jaana chahiye. Kyunki jungle sirf tiger nahi hai. "
            "Subah ki pehli dhoop. Alarm calls. Birds jo tumne kabhi dekhe hi nahi. Aur ek aisa silence jo shehar mein kabhi nahi milta. "
            "Aur jab tiger dikhta hai na… woh isliye special hota hai, kyunki guaranteed nahi tha. "
            "Comment SAFARI, chalo saath chalte hain.  (≈70 words)"),
    screenplay=(
        "0-2s   SHOT Isha to lens, small shrug | TEXT (Anton) YOU MIGHT NOT / SEE A TIGER. | SAYS 'Sach bataun? Pehli safari pe shayad tiger na dikhe.'\n"
        "2-5s   SHOT Isha, punch-in | TEXT NOBODY CAN GUARANTEE ONE | SAYS 'Aur agar koi guarantee de, toh samajh jaana jhooth hai.'\n"
        "5-8s   SHOT Isha | TEXT GO ANYWAY. HERE'S WHY: | SAYS 'Lekin phir bhi jaana chahiye. Kyunki jungle sirf tiger nahi hai.'\n"
        "8-10s  SHOT her misty-forest photo | TEXT 01 · FIRST LIGHT | SAYS 'Subah ki pehli dhoop.'\n"
        "10-12s SHOT her jackal photo (ears up) | TEXT 02 · ALARM CALLS | SAYS 'Alarm calls.'\n"
        "12-14s SHOT her kingfisher-with-fish photo | TEXT 03 · BIRDS YOU'VE NEVER SEEN | SAYS 'Birds jo tumne kabhi dekhe hi nahi.'\n"
        "14-17s SHOT her kingfisher-on-moss photo, sound drops to silence | TEXT 04 · REAL SILENCE | SAYS 'Aur ek aisa silence…'\n"
        "17-22s SHOT Isha to lens | TEXT — | SAYS 'Aur jab tiger dikhta hai na…'\n"
        "22-25s SHOT her tiger photo (impact whoosh) | TEXT BECAUSE IT WASN'T GUARANTEED | SAYS '…kyunki guaranteed nahi tha.'\n"
        "25-28s SHOT Isha leans in | TEXT COMMENT \"SAFARI\" · PART 3/3 | SAYS 'Comment SAFARI, chalo saath chalte hain.' → LOOPS"),
    onscreen="YOU MIGHT NOT SEE A TIGER. · NOBODY CAN GUARANTEE ONE · GO ANYWAY. HERE'S WHY: · 01 FIRST LIGHT · 02 ALARM CALLS · 03 BIRDS YOU'VE NEVER SEEN · 04 REAL SILENCE · BECAUSE IT WASN'T GUARANTEED · COMMENT \"SAFARI\"",
    cover="Isha with a small shrug, text YOU MIGHT NOT SEE A TIGER. (Anton) centred in the 4:5 area; small '3/3'.",
    sends="Sent to the friend who says 'what if we don't see anything?'",
    shots=[("Talking head, all lines, 3 takes each (outfit different from Monday's and Tuesday's)", TH),
           ("Optional, if true: a 1-minute voice note of your own first no-tiger safari, so we can swap in hook 3", VO)],
    source="Isha shoot + her archive photos (misty forest, jackal, kingfishers, tiger)",
    shoot_by="Sat 28 Nov",
    edit="Format A. " + LEARN + " Numbered list 01-04 with a tick per number; silence beat on 04; deep whoosh on the tiger.",
    caption=("First jungle safari and no tiger? Here's why it's still worth going 🌿🐅\n\n"
             "Nobody honest can guarantee a tiger. What you will get: first light in the forest, alarm calls, birds you've never seen, "
             "and a silence the city never gives you. And when the tiger does show up, it means more because it wasn't promised.\n\n"
             "Part 3 of 3: Corbett, unfiltered. Comment SAFARI and we'll DM you the link for {{dates}}.\n\n"
             "#junglesafari #tigersafari #jimcorbettnationalpark #lostandfree #JungleWithIsha"),
    deps="Safari dates/price for the DM link; Isha confirms the script feels true to her."))

# Sat 5 Dec @travelwithisha: the Himachal-in-December reel (base post W2-T2 in posts.py) gets the v2 treatment
W2T2_V2 = dict(
    keyword="Himachal in December",
    hooks=("1. TIMELINESS (recommended): Google Earth fly-in · TEXT 'IF YOU GO ANYWHERE THIS DECEMBER, GO HERE' · SAYS 'Agar December mein sirf ek jagah ja sakte ho, toh yahan jaao.'\n"
           "2. SPECIFIC (Trial Reel): TEXT 'WHERE THE ROAD ENDS IN HIMACHAL'\n3. PAYOFF: first frame = her best snowy shot · TEXT '-5°C AND WORTH IT'\n"
           "4. IDENTITY: TEXT 'FOR PEOPLE WHO HATE CROWDED HILL STATIONS'\n5. QUESTION: TEXT 'MANALI AGAIN? TRY THIS INSTEAD.'"),
    script=("Agar December mein sirf ek jagah ja sakte ho, toh yahan jaao. {{Village}}. Road yahin khatam hoti hai. "
            "Subah minus mein temperature, chai haath garam karti hai, aur pahaad itne paas lagte hain. "
            "Kaise pahunche: {{route}}. Kahan ruke: {{homestay}}. Budget: ₹{{x}}. "
            "Aur ek tip: subah 7 baje uthna. Pahaad pe pehli dhoop… bas. Save kar lo.  (≈60 words)"),
    screenplay=(
        "0-2s   SHOT Google Earth fly-in Mumbai → {{village}} | TEXT (Anton) IF YOU GO ANYWHERE THIS DECEMBER, GO HERE | SAYS 'Agar December mein…'\n"
        "2-4s   SHOT her widest Himachal shot | TEXT (Anton, marigold) {{VILLAGE}} | SAYS '{{Village}}. Road yahin khatam hoti hai.'\n"
        "4-14s  SHOT archive clips 1.5-2 s each, alternate wide → Isha → detail (never two similar shots in a row) | TEXT — | SAYS 'Subah minus mein…'\n"
        "14-22s SHOT 3 info cards over clips | TEXT HOW TO REACH · WHERE TO STAY · BUDGET (tick each) | SAYS 'Kaise pahunche… Budget…'\n"
        "22-27s SHOT first light on the mountains, hold | TEXT WAKE UP AT 7. TRUST ME. | SAYS 'Aur ek tip…'\n"
        "27-28s SHOT cut back to the globe → LOOPS"),
    onscreen="IF YOU GO ANYWHERE THIS DECEMBER, GO HERE · {{VILLAGE}} · HOW TO REACH · WHERE TO STAY · BUDGET · WAKE UP AT 7. TRUST ME.",
    cover="Her best Himachal frame with the village name in Anton (marigold) in the 4:5 area.",
    sends="Sent to the friend planning a December trip.",
    edit="Format A story walk. " + LEARN,
    caption=("Himachal in December: if you can go to only one place, go here ❄️🏔️\n\n"
             "How to reach: {{route}}\nWhere to stay: {{homestay}}\nBudget: ₹{{x}}\n\n"
             "Save this for your winter trip. (And if you'd rather trade snow for jungle, my Corbett safari with @lostandfree has a few seats left. Link in bio.)\n\n"
             "#himachal #himachaltourism #wintertravel #travelwithisha #JungleWithIsha"),
)
