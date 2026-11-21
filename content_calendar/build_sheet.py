"""Builds Isha_Safari_Content_Calendar.xlsx from posts.py (uploaded to Google Sheets)."""
from collections import Counter
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from posts import P as ALL, TH, TH_OUT, VO, FLAT, ARCH

# Run ends Wed 2 Dec 2026 (contract review that day). Week 2 keeps Mon-Wed: the FAQ carousel, the sea-vs-jungle reel,
# and the price breakdown (moved from Fri 4 Dec to Wed 2 Dec because it converts; the guide reel needs LAF to film first).
KEEP = ["W1-L1", "W1-T1", "W1-L2", "W1-L3", "W1-T2b", "W2-L1", "W2-T1", "W2-L3"]
P = [dict(p) for k in KEEP for p in ALL if p["id"] == k]
for p in P:
    if p["id"] == "W2-L3":
        p.update(date="Wed 2 Dec 2026", day="Wed")
BACKLOG = [p for p in ALL if p["id"] not in KEEP]
from posts_v2 import V2          # v2: scripts, beats, hooks, captions, hashtags rewritten with the social-media skills
for p in P:
    p.update(V2[p["id"]])

OUT = Path(__file__).parent / "Isha_Safari_Content_Calendar.xlsx"
GREEN, GOLD, CREAM, SKY = "2E5B3B", "F6C445", "F7F3EA", "E3EEF7"
PHASE = {1: "1 · Launch + trust", 2: "2 · Objections + convert"}
thin = Side(style="thin", color="D0D0D0")

# sanity: week 1 = 3 LAF + 2 TWI; Mon-Wed of week 2 = 2 LAF + 1 TWI
c1 = Counter(p["acct"] for p in P if p["week"] == 1)
c2 = Counter(p["acct"] for p in P if p["week"] == 2)
assert (c1["@lostandfree"], c1["@travelwithisha"], c2["@lostandfree"], c2["@travelwithisha"]) == (3, 2, 2, 1)
assert len(P) == 8

wb = Workbook()

def sheet(title, headers, rows, widths, fill=GREEN, row_fill=None):
    ws = wb.create_sheet(title)
    ws.append(headers)
    for r in rows:
        ws.append(r)
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=fill)
        c.alignment = Alignment(wrap_text=True, vertical="center")
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
            c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
        if row_fill:
            f = row_fill(row)
            if f:
                for c in row:
                    c.fill = PatternFill("solid", fgColor=f)
    ws.freeze_panes = "C2" if len(headers) > 4 else "A2"
    ws.auto_filter.ref = ws.dimensions
    return ws

acct_fill = lambda row: CREAM if row[6].value == "@lostandfree" else SKY

# ---------------- 1. Read me ----------------
ws = wb.active
ws.title = "Read me"
readme = [
    ["ISHA × LOST & FREE · SAFARI SIGN-UP CONTENT CALENDAR"],
    ["Mon 23 Nov → Wed 2 Dec 2026 · 8 posts · 3/week on @lostandfree + 2/week on @travelwithisha (week 2 runs Mon-Wed: 2 + 1)"],
    [""],
    ["MAIN GOAL", "Safari sign-ups from Instagram (50/50 deal). Every sign-up must come through the keyword SAFARI (comment → auto-DM) or Isha's tracked link, so it's counted."],
    ["HOW THE 10 DAYS WORK", "Mon 23 - Sun 29 Nov, LAUNCH + TRUST: real details, day-by-day itinerary, a shareable 5:30 AM POV, Isha as a wildlife photographer, solo-travel trust.\nMon 30 Nov - Wed 2 Dec, OBJECTIONS + CONVERT: FAQ (safety, fitness, tiger odds), sea vs jungle reach reel, what the price actually covers."],
    ["AIM (till Wed 2 Dec)", "Promote the safari and Lost & Free. Every one of the 8 posts points to the safari.\n@lostandfree (3/week): all safari posts, mostly COLLABS with @travelwithisha so they land on both grids, each ending on 'Comment SAFARI'.\n@travelwithisha (2/week): either promotes the safari directly or continues the series she's already posting (e.g. Lakshadweep Part 2), always with a safari hand-off: end card, caption line + link sticker in stories."],
    ["TABS", "Calendar = the overview (date, time, account, type, title).\nPost briefs = full script, screenplay (second-by-second), on-screen text, edit notes, caption, what's blocking.\nShots for Isha = every shot she has to send, with how to shoot it and the deadline. Isha: start here every Saturday.\nHow to shoot = the rules for every shoot (light, framing, sound, files).\nIsha's style = what Isha likes and dislikes, from her feedback so far. The edit follows these.\nNeeded from Lost & Free = details we must get before posts can go out.\nBacklog (after 2 Dec) = ideas already worked out, only used if the engagement continues."],
    ["REACH RULES (every post)", "1. Hook in the first 3 sec on all three channels at once: striking first frame + bold on-screen text + first spoken line. No intro, no 'hi guys', no logo.\n2. Muted-first: the on-screen text tells the whole story (most people watch without sound).\n3. Search keyword: said in the first 3 sec, shown on screen, and in the caption's first line.\n4. A new visual every 2-4 sec; reels 15-35 sec; one call to action; the last shot loops back into the first.\n5. Captions: first line under 125 characters earns the '...more' tap; max 5 hashtags (Instagram's cap): topic + niche + #JungleWithIsha.\n6. Post hook #1. Test hook #2 as an Instagram Trial Reel (shown to non-followers first) and keep the winner for the next post.\n7. Judge posts on 3-sec hold, average watch time, shares/sends and saves, not likes."],
    ["CAMPAIGN HASHTAG", "#JungleWithIsha on every post of both accounts, in bio and stories. Check on Instagram that the tag is unused before the first post."],
    ["{{ }} PLACEHOLDERS", "Anything in {{double brackets}} (dates, price, seats, location…) must be filled with Lost & Free's real details. Never post with a {{ }} left in, and only post a seat count if it's true that day."],
    ["SHOOT DAYS", "Sat 21 / Sun 22 Nov for week 1, Sat 28 Nov for 30 Nov - 2 Dec (see 'Isha shoots by' in Calendar)."],
    ["WED 2 DEC · REVIEW", "This calendar ends on Wed 2 Dec, the day the engagement is reviewed. Bring: reach, saves, shares and SAFARI comments per post (Insights at 24 h, and 7 days where a post is old enough), link taps, follower change on both accounts, and Lost & Free's sign-up count by keyword/link. The 'Backlog' tab has the ideas ready for after 2 Dec if the work continues."],
    ["STORIES (every day, not counted in the 8)", "Both accounts: share the day's post + one sticker (poll, quiz, question box or countdown). Safari link sticker daily on @lostandfree; on @travelwithisha every Mon, Wed, Fri. Save answers from question boxes for the FAQ posts."],
    ["MID-POINT CHECK (Sun 29 Nov)", "Pull Insights for each post (reach, saves, shares, SAFARI comments, link taps) + Lost & Free's sign-up count. Double down on the best hook type next week."],
]
for r in readme:
    ws.append(r)
ws.column_dimensions["A"].width = 30
ws.column_dimensions["B"].width = 120
ws["A1"].font = Font(bold=True, size=16, color=GREEN)
ws["A2"].font = Font(italic=True, size=11)
for row in ws.iter_rows(min_row=4):
    row[0].font = Font(bold=True, color=GREEN)
    for c in row:
        c.alignment = Alignment(wrap_text=True, vertical="top")

# ---------------- 2. Calendar ----------------
cal_rows = [[p["id"], p["week"], PHASE[p["week"]], p["date"], p["day"], p["time"] + " IST", p["acct"], p["collab"],
             p["type"], p["fmt"], p["title"], p["goal"], p["cta"], p["shoot_by"], p["source"], p["deps"], "Planned"] for p in P]
sheet("Calendar",
      ["ID", "Week", "Phase", "Date", "Day", "Post time", "Account", "Collab", "Content type", "Format / length",
       "Title / hook", "Goal", "Call to action", "Isha shoots by", "Footage source", "Blocking / needs", "Status"],
      cal_rows, [8, 6, 16, 16, 6, 12, 16, 22, 20, 26, 40, 45, 32, 16, 34, 40, 12], row_fill=acct_fill)

# ---------------- 3. Post briefs ----------------
brief_rows = [[p["id"], p["date"], p["time"] + " IST", p["acct"], p["type"], p["title"], p["keyword"], p["hooks"],
               p["script"], p["screenplay"], p["onscreen"], p["cover"], p["sends"],
               "\n".join(f"{i}. {s}" for i, (s, _) in enumerate(p["shots"], 1)),
               p["edit"], p["caption"], p["deps"]] for p in P]
sheet("Post briefs",
      ["ID", "Date", "Time", "Account", "Type", "Title / hook", "Search keyword (say it in 0-3 s, show it, put it in caption line 1)",
       "Hook options (use #1; test #2 as a Trial Reel)", "Script: what Isha says (Hinglish, say it your way)",
       "Screenplay: beat by beat (SHOT | on-screen TEXT | SAYS)", "On-screen text", "Cover", "Who would send this to whom",
       "Shots Isha sends (details in 'Shots for Isha')", "Edit notes", "Caption + hashtags (max 5)", "Blocking / needs"],
      brief_rows, [8, 15, 10, 15, 14, 28, 24, 50, 50, 75, 35, 32, 30, 40, 40, 50, 30],
      row_fill=lambda row: CREAM if row[3].value == "@lostandfree" else SKY)

# ---------------- 4. Shots for Isha ----------------
shot_rows = []
for p in P:
    for i, (s, how) in enumerate(p["shots"], 1):
        if s == "None":
            shot_rows.append([p["shoot_by"], p["id"], p["date"], p["acct"], p["title"], "-", "Nothing to shoot: Lost & Free design / footage", "—", "—"])
            continue
        shot_rows.append([p["shoot_by"], p["id"], p["date"], p["acct"], p["title"], i, s, how,
                          "Archive: send originals" if how == ARCH else "New shoot"])
sheet("Shots for Isha",
      ["Shoot / send by", "Post ID", "Post date", "Account", "Post", "Shot #", "Shot to send", "How to shoot it", "New or archive", "Done ✓"],
      [r + [""] for r in shot_rows], [16, 8, 16, 15, 34, 7, 50, 90, 18, 8],
      row_fill=lambda row: CREAM if row[3].value == "@lostandfree" else SKY)

# ---------------- 5. How to shoot ----------------
guide = [
    ["Every shoot", "Phone settings", "Vertical 9:16, 4K at 30 fps (1080p 60 fps only if storage is full). Camera grid ON. Clean the lens. Keep your normal iPhone colour: we don't add filters, so don't use beauty or colour filters either."],
    ["Every shoot", "Focus + exposure", "Long-press on your face (or the subject) until 'AE/AF LOCK' shows, so brightness doesn't jump mid-take."],
    ["Every shoot", "Framing", "Eyes on the upper grid line. Mid-chest up for talking heads. One palm of space above your head. Keep the right side and the bottom fifth of the frame free of important things (Instagram buttons and captions cover them)."],
    ["Every shoot", "Takes", "Each line 3 times. Start already leaning in, mid-energy (no 'hi guys', no pause before the first word). 1 sec pause between lines so we can cut cleanly. After each reel, 3 sec of a natural laugh/look-away."],
    ["Every shoot", "Outfits", "Change outfit + background between posts that go out on different days so the feed doesn't look like one long video. Safari posts: olive/khaki/linen (matches the teaser). Strong colours are fine on @travelwithisha."],
    ["Light", "Indoor (Setup A)", TH],
    ["Light", "Outdoor (Setup O)", TH_OUT],
    ["Light", "Golden hour", "Sun beside or behind you as a rim light, exposure on your face. Best 4:00-5:30 pm in Mumbai in winter."],
    ["Light", "Never", "Window behind you · overhead tube light · mixed warm + white bulbs · direct midday sun on your face · flash."],
    ["Sound", "Voiceover (Setup B)", VO],
    ["Sound", "Room tone", "5 sec of silence at every setup, every time (we use it to clean noise)."],
    ["Sound", "Mic", "AirPods or lapel mic for talking heads. Fan, AC and TV off. If firecrackers/traffic are loud, re-take."],
    ["B-roll", "Top-down / flat-lay", FLAT],
    ["B-roll", "Hands + details", "3 sec per detail, hold still, then a slow move (push in or slide sideways). Hands enter from the bottom."],
    ["B-roll", "Screen recordings", "Google Earth app, 3D on, start zoomed out on India, search the place, let it fly in. 2 recordings each."],
    ["Files", "How to send", ARCH],
    ["Files", "Naming", "Post ID + what + take, e.g. W1-L1_talkinghead_take2.mov, W3-L2_flatlay_layers.jpg. Upload to the Drive folder 'Raw - <post ID>'."],
    ["Files", "Archive photos", "Send the original photo (HEIC/JPG from camera or Lightroom export at full size), never a screenshot."],
    ["People", "Other people on camera", "Anyone recognisable (guides, friends, group members) must say OK to being posted. Blur private chats and names."],
]
sheet("How to shoot", ["Topic", "Rule", "Instructions"], guide, [16, 24, 130])

# ---------------- 6. Isha's style ----------------
style = [
    ["Likes", "Hinglish, personal storytelling to camera, like iffy.explorer, brindasharma, sayannath, sailing_amrutha", "Reel system + every brief"],
    ["Likes", "Her ORIGINAL iPhone colour: no heavy grading or LUT looks", "Client note 9 Nov: 'don't change the colour gradings, use the exact videos'"],
    ["Likes", "Faster pace: tight pauses, ~1.1-1.15x speed", "R1 v3 client notes (9 Nov)"],
    ["Likes", "Bigger, bold captions; bold titles (e.g. BHAI DOOJ really big)", "R1 v3 notes + R3 voice note (10 Nov)"],
    ["Likes", "Sound effects that follow the story (whooshes, ticks, pings, animal calls)", "Safari reel v3 feedback: 'add the sound effects'"],
    ["Likes", "Edited, designed look: numbered cards, split screen, full-screen photo beats", "Safari reel v2 → v3 feedback"],
    ["Likes", "Her own wildlife photos in the edit (harrier, jackal, owl, tiger)", "Safari reel v5 + Diwali wildlife reel"],
    ["Likes", "Loop endings and cliffhangers (R1 loop, 'woh Part 2 mein')", "R1 v2 LOOP, Lakshadweep Part 1"],
    ["Likes", "Lost & Free editorial look: gold serif headlines, white body, dark forest photos", "'6 things' carousel (post lost and free/)"],
    ["Dislikes", "Cursive/script fonts on busy footage", "R3 voice note: 'we shouldn't be using a cursive font… so many colours'"],
    ["Dislikes", "Text colours that change from page to page; typography that looks 'drafted'", "R3 voice note + safari v2 feedback"],
    ["Dislikes", "Too little of her face", "R3 voice note: 'there needs to be a little more in the face'"],
    ["Dislikes", "Murky / random shots (e.g. dull coral close-ups)", "Lakshadweep reorder (12 Nov)"],
    ["Dislikes", "Similar clips next to each other, repetitive order", "Lakshadweep reorder (12 Nov)"],
    ["Dislikes", "Long pauses, slow pace", "R1 v3 notes"],
    ["Rules", "Captions always on (Hinglish in Roman script), never invent words she didn't say", "ISHA_REEL_SYSTEM.md §9"],
    ["Rules", "One special transition max, hard cuts otherwise; one big title per reel", "ISHA_REEL_SYSTEM.md §0"],
    ["Rules", "Safe zones: no text in the bottom 20% or right edge; covers readable in the 4:5 grid crop", "ISHA_REEL_SYSTEM.md §10"],
    ["Rules", "Export without music we don't own; add trending audio inside Instagram", "ISHA_REEL_SYSTEM.md §6"],
]
sheet("Isha's style", ["Type", "What", "Where it came from"], style, [12, 80, 60],
      row_fill=lambda row: {"Likes": "E6F2E8", "Dislikes": "FBE6E6", "Rules": CREAM}.get(row[0].value))

# ---------------- 7. Needed from Lost & Free ----------------
need = [
    ["Safari details: name, park/location, dates, nights, price, inclusions/exclusions, seats, sign-up close date", "Before Sun 22 Nov", "W1-L1, W1-L2, W2-L1, W2-L3", "Open"],
    ["Isha's tracked sign-up link (UTM) and/or code, for the 50/50 split", "Before Sun 22 Nov", "Every post", "Open"],
    ["SAFARI keyword auto-DM switched on (ManyChat or Meta automation) on BOTH accounts", "Before Mon 23 Nov", "Every post", "Open"],
    ["Which handle to tag: @lostandfree or @lostandfreesafaris (their carousel says @lostandfreesafaris)", "Before Mon 23 Nov", "Every post", "Open"],
    ["Safari footage + photos with permission: jeep POV (6+ s unbroken), dawn forest, alarm-call deer, guide, camp, tiger", "Before Sun 22 Nov", "W1-L1, W1-L3, W2-T1, W2-L3", "Open"],
    ["Which activities are on the trip (morning + evening safari, nature walk, bonfire, stargazing, photography with Isha) + B-roll/photos of each. No day-by-day plan needed yet", "Before Sun 22 Nov", "W1-L2", "Open"],
    ["Answers to FAQ: solo women safety, fitness, tiger odds, network, food, who's in the group", "Before Sat 28 Nov", "W2-L1", "Open"],
    ["Honest cost breakdown (stay, food, safaris, permits, transfers)", "Before Mon 30 Nov", "W2-L3", "Open"],
    ["Sign-up report by link/keyword (for the Wed 2 Dec review)", "Sun 29 Nov + Wed 2 Dec", "Review", "Open"],
]
sheet("Needed from Lost & Free", ["What", "Needed by", "Used in", "Status"], need, [90, 18, 34, 10])

# ---------------- 8. Backlog ----------------
sheet("Backlog (after 2 Dec)", ["Was planned for", "Account", "Type", "Idea", "Goal"],
      [[p["date"], p["acct"], p["type"], p["title"], p["goal"]] for p in BACKLOG], [16, 16, 24, 50, 80],
      row_fill=lambda row: CREAM if row[1].value == "@lostandfree" else SKY)

wb.save(OUT)
print("saved", OUT, "posts", len(P), "shots", len(shot_rows))
