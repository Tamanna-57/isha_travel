"""Leave Mumbai reel (R1) revamp: same edit, new captions in the client-approved look, a light grade, and a
Lost & Free Safaris logo pop-up. The picture edit, SFX, transitions and audio mix are kept as they are.

Needs the reel exported WITHOUT captions/text (same edit): set SRC below. Run:
    python projects/leave_mumbai/make.py            # -> out/leave_mumbai.mp4 (+ _clean, .srt, cover)
    python projects/leave_mumbai/make.py --preview  # renders over the old captioned file, layout check only

Look: projects/bhai_dooj/REEL_SPEC.md (karaoke captions, bold text, hard shadows, no boxes), with a twist for this
reel's vibe (a city rant that turns into a plan): one punch word per page in Poppins ExtraBold marigold,
single-word pages bigger, a sindoor Anton hook title, the data source as a small bold line.
"""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

P = Path(__file__).resolve().parent
ROOT = P.parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
import isha  # noqa: E402

B, OUT = P / "build", P / "out"
NAME = "leave_mumbai"
OLD = ROOT / "bhai dooj" / "R1_LeaveMumbai_C_captions_sfx_transitions_original_color.mp4"
SRC = ROOT / "bhai dooj" / "R1_LeaveMumbai_NO_CAPTIONS.mp4"     # <- the same edit exported without any text
W, H, FPS = 1080, 1920, 30
DUR = 35.10

# grade: a light touch. Luma-only contrast (no RGB curves, so skin doesn't get warmer), +3% saturation,
# fine sharpening. Measured on 4 frames: highlights p95 +3..8, saturation +0.01..0.04, skin R/B within 0.06.
GRADE = "eq=contrast=1.06:brightness=0.01:saturation=1.03,unsharp=5:5:0.25:5:5:0"

# ------------------------------------------------------------------ captions
# Her words as spoken (the previous edit's proofread captions), one entry per page:
# (page start s, text). *word* = punch word (Poppins ExtraBold marigold). A page that is only one *word* is a big punch.
PAGES = [
    (0.00, "yahi sochti hoon"),
    (0.88, "ki bas,"),
    (1.38, "ab toh *Mumbai*"),
    (2.12, "chhod dena *chahiye*"),
    (3.12, "main phir bhi"),
    (3.62, "rukne ki poori *koshish*"),
    (4.62, "karti hoon"),
    (5.12, "because it's my *city*"),
    (5.88, "you know"),
    (6.12, "and I *love* it"),
    (6.88, "but *honestly,*"),
    (7.62, "Mumbai has become"),
    (8.88, "*unlivable*"),
    (9.62, "*mangroves* are being cut,"),
    (10.88, "*rivers* are being polluted"),
    (12.12, "and honestly,"),
    (12.88, "aajkal koi"),
    (13.38, "kisi cheez ki *respect*"),
    (14.12, "hi nahi karta hai *yaar*"),
    (15.38, "aur har *Diwali*"),
    (16.38, "*pollution* aur bhi"),
    (17.12, "*zyada* badh jaata hai"),
    (18.12, "*13* out of"),
    (19.12, "the world's *20*"),
    (19.62, "most *polluted* cities"),
    (20.62, "are in *India*"),
    (21.62, "toh is saal"),
    (22.38, "meri sirf ek *request* hai"),
    (23.88, "itna socho ki"),
    (24.62, "humne *exactly* kiya kya hai"),
    (26.12, "aur ye sab humein"),
    (27.12, "laaya *kidhar* hai"),
    (27.88, "aur jab *saans* lene ki"),
    (28.88, "jagah chahiye ho,"),
    (29.88, "main *jungle* jaati hoon"),
    (30.88, "*Lost & Free Safaris* ke saath"),   # she says "Lost & Free"; "Safaris" = the brand name (client ask)
    (32.12, "aap bhi *chalna?*"),
    (32.88, "details coming out *soon*"),
    (34.12, "main har roz uthke..."),
]
SYL = {"13": 3, "20": 2, "Lost": 1, "&": 1, "Free": 1, "Safaris": 3, "Mumbai": 2, "Diwali": 3, "unlivable": 4,
       "mangroves": 2, "pollution": 3, "polluted": 3, "exactly": 3, "honestly,": 3, "respect": 2, "request": 2}
Y_CAP = 1340
FS, FS_KEY, FS_BIG = 115, 118, 150
GREY, WHITE, MARIGOLD, SINDOOR = isha.C["grey"], isha.C["chalk"], isha.C["marigold"], isha.C["sindoor"]
HARD = r"\bord0\shad5\4c&H000000&\4a&H26&"          # hard drop shadow, no outline, no blur (client ask)

def syl(w):
    k = re.sub(r"[^\w&]", "", w)
    return SYL.get(k, SYL.get(w, max(1, len(re.findall(r"[aeiouy]+", k.lower())))))

def page_words():
    """word timings: each page's words spread by syllable weight over the first 85% of the page"""
    words = []
    for i, (t0, txt) in enumerate(PAGES):
        t1 = PAGES[i + 1][0] if i + 1 < len(PAGES) else DUR
        toks = re.findall(r"\*[^*]+\*|\S+", txt)
        units = []                                     # (text, punch?)
        for tk in toks:
            if tk.startswith("*"):
                units.append((tk.strip("*"), True))
            else:
                units.append((tk, False))
        wts = np.array([sum(syl(x) for x in u.split()) for u, _ in units], float)
        span = (t1 - t0) * 0.85
        edges = t0 + 0.04 + np.concatenate([[0], np.cumsum(wts)]) / wts.sum() * span
        for (u, pk), a, b in zip(units, edges[:-1], edges[1:]):
            words.append({"text": u, "start": round(a, 3), "end": round(b, 3), "punch": pk, "page": i})
    return words

def caption_events(words):
    evs = []
    for i, (t0, _) in enumerate(PAGES):
        t1 = PAGES[i + 1][0] if i + 1 < len(PAGES) else DUR
        pw = [w for w in words if w["page"] == i]
        single = len(pw) == 1 and pw[0]["punch"]
        body = []
        for w in pw:
            dt = int((w["start"] - t0) * 1000)
            txt = isha.ass_escape(w["text"])
            if w["punch"]:
                fs = FS_BIG if single else FS_KEY
                body.append(rf"{{\fnPoppins ExtraBold\b0\fs{fs}\1c{GREY}\alpha&H30&{HARD}"
                            rf"\t({dt},{dt + 1},\1c{MARIGOLD}\alpha&H00&)}}{txt} ")
            else:
                body.append(rf"{{\fnPoppins SemiBold\b0\fs{FS}\1c{GREY}\alpha&H30&{HARD}"
                            rf"\t({dt},{dt + 1},\1c{WHITE}\alpha&H00&)}}{txt} ")
        pop = r"\fscx92\fscy92\t(0,90,\fscx100\fscy100)" if single else ""
        evs.append(isha.ev(t0, t1, "Sans", rf"{{\an5\pos(540,{Y_CAP})\fad(40,0){pop}}}" + "".join(body).rstrip(), 1))
    return evs

def title_events():
    # hook title in the approved look (was "EVERY MORNING / I want to leave Mumbai" in serif):
    # a white Allura line, then LEAVE MUMBAI big in Anton sindoor, hard shadow
    fs = isha.fit("chapter", "LEAVE MUMBAI", 5, 0.66)
    evs = [
        isha.ev(0.0, 2.9, "Script", rf"{{\an5\pos(540,215)\fs120\1c{WHITE}{isha.POP_T}}}every morning, I want to", 3),
        isha.ev(0.12, 2.9, "Chapter", rf"{{\an5\pos(540,370)\fs{fs}\1c{SINDOOR}\shad6\4a&H40&{isha.POP_T}}}LEAVE MUMBAI", 2),
    ]
    # data source while she gives the IQAir stat: small, bold, hard shadow
    evs.append(isha.ev(18.12, 21.62, "Sans", rf"{{\an5\pos(540,1225)\fnPoppins SemiBold\fs34\1c{WHITE}{HARD}"
                                            r"\shad3\fad(120,120)}Source: IQAir World Air Quality Report 2024", 2))
    return evs

# ------------------------------------------------------------------ Lost & Free Safaris pop-up
LOGO = ROOT / "projects" / "safari" / "assets" / "logo.png"           # official cream logo, transparent
LOGO_BG = tuple(int(v) for v in (ROOT / "projects/safari/assets/logo_bg.txt").read_text().split())  # olive
POP_IN, POP_OUT = 30.88, 34.05            # "Lost & Free ke saath" -> through "details coming out soon"
CARD_W, CARD_H, CARD_X, CARD_Y = 400, 430, 110, 175   # top-left, where the old @lostandfree tag sat

def card_image():
    s = 3                                                # supersample for clean edges
    card = Image.new("RGBA", (CARD_W * s, CARD_H * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, CARD_W * s - 1, CARD_H * s - 1], radius=34 * s, fill=LOGO_BG + (255,))
    lg = Image.open(LOGO).convert("RGBA")
    lw = int(CARD_W * s * 0.80); lh = int(lg.height * lw / lg.width)
    lg = lg.resize((lw, lh), Image.LANCZOS)
    card.alpha_composite(lg, ((CARD_W * s - lw) // 2, int(26 * s)))
    f = ImageFont.truetype(str(ROOT / "fonts" / "Poppins-SemiBold.ttf"), 30 * s)
    handle = "@lostandfree"
    tw = d.textlength(handle, font=f)
    d.text(((CARD_W * s - tw) / 2, CARD_H * s - 58 * s), handle, font=f, fill=(247, 243, 234, 255))
    card = card.resize((CARD_W, CARD_H), Image.LANCZOS)
    # hard drop shadow like the captions
    sh = Image.new("RGBA", (CARD_W + 12, CARD_H + 12), (0, 0, 0, 0))
    a = card.split()[3].point(lambda v: int(v * 0.55))
    sh.paste(Image.new("RGBA", card.size, (0, 0, 0, 255)), (8, 8), a)
    sh.alpha_composite(card, (0, 0))
    return sh

def popup_clip():
    """RGBA frames of the card: pops in (scale 0.80 -> 1.0, ease-out 0.28 s), holds, fades out 0.2 s"""
    out = B / "popup.mov"
    card = card_image()
    n = int(round((POP_OUT - POP_IN) * FPS))
    cw, ch = card.size
    proc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{cw}x{ch}",
                             "-r", str(FPS), "-i", "-", "-c:v", "qtrle", str(out)], stdin=subprocess.PIPE)
    for k in range(n):
        t = k / FPS
        u = min(1.0, t / 0.28); e = 1 - (1 - u) ** 3
        sc = 0.80 + 0.20 * e + 0.03 * np.sin(np.pi * u) * (u < 1)       # tiny overshoot = "pop"
        al = min(1.0, t / 0.12) * min(1.0, max(0.0, (POP_OUT - POP_IN - t) / 0.2))
        fr = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        im = card.resize((max(1, int(cw * sc)), max(1, int(ch * sc))), Image.BICUBIC)
        a = im.split()[3].point(lambda v: int(v * al)); im.putalpha(a)
        fr.alpha_composite(im, ((cw - im.width) // 2, (ch - im.height) // 2))
        proc.stdin.write(fr.tobytes())
    proc.stdin.close(); proc.wait()
    return out

# ------------------------------------------------------------------ render
def render(src, preview=False):
    B.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
    words = page_words()
    (P / "words.json").write_text(json.dumps([{k: w[k] for k in ("text", "start", "end")} for w in words],
                                             indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (B / "subs.ass").write_text(isha.ass_header() + "\n".join(caption_events(words) + title_events()) + "\n",
                                encoding="utf-8")
    pop = popup_clip()
    info = isha.clip_info(src)
    tm = (isha.HDR_TO_SDR + ",") if info.get("hdr") else ""
    fonts = isha.ff_path(isha.FONTS, B)
    tag = "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv,format=yuv420p"
    name = NAME + ("_preview" if preview else "")
    # pop sound: one soft pop under the logo (the edit's own SFX stay as they are)
    sfx = ROOT / "sfx_library" / "msg_soft_pop.mp3"
    fc_base = (f"[0:v]{tm}fps={FPS},{GRADE}[g];"
               f"[1:v]setpts=PTS-STARTPTS+{POP_IN}/TB[p];"
               f"[g][p]overlay={CARD_X - 4}:{CARD_Y - 4}:eof_action=pass[ov]")
    au = (f";[2:a]adelay={int(POP_IN * 1000)}|{int(POP_IN * 1000)},volume=-14dB,aformat=channel_layouts=stereo[s];"
          f"[0:a]aformat=channel_layouts=stereo[a0];[a0][s]amix=inputs=2:duration=first:normalize=0[a]")
    enc = ["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-x264-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709", "-r", str(FPS),
           "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart"]
    ins = ["-i", str(src), "-i", str(pop), "-i", str(sfx)]
    final = OUT / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex",
                    fc_base + f";[ov]ass=subs.ass:fontsdir={fonts},{tag}[v]" + au,
                    "-map", "[v]", "-map", "[a]", *enc, str(final)], check=True, cwd=B)
    if not preview:
        clean = OUT / f"{name}_clean.mp4"                # graded, no text, no pop-up
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-vf", f"{tm}fps={FPS},{GRADE},{tag}",
                        "-map", "0:v", "-map", "0:a", *enc, str(clean)], check=True)
        isha.write_srt(OUT / f"{name}.srt", [{k: w[k] for k in ("text", "start", "end")} for w in words])
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1.2", "-i", str(final), "-frames:v", "1",
                        str(OUT / f"{name}_cover.png")], check=True)
    print(final)
    isha.qa(final)

if __name__ == "__main__":
    prev = "--preview" in sys.argv
    src = OLD if prev else SRC
    if not src.exists():
        raise SystemExit(f"missing {src}: export the reel without captions/text and save it there")
    render(src, preview=prev)
