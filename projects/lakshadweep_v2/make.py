"""Lakshadweep reel v2: the client's final draft (IMG_3950.MP4) finished in the reference style.

Same look as projects/lakshadweep/make.py (client reference: WhatsApp Video 2026-11-02 at 3.36.24 PM.mp4):
word-by-word blur-in captions, Inter Display Medium + Instrument Serif Italic keyword, soft shadow, tiny handle.

Fixes over v1:
  * grade: split face / B-roll grades; skin chroma ~23 (v1 was ~33 = orange, over-saturated faces)
  * captions: every line is MEASURED after rendering and shrunk to fit x 130..950; block kept in y 240..1470
  * captions: placed per page by face detection on the graded picture (never over her face)
  * timing: words from forced alignment of the exact transcript (align.py), not whisper guesses
  * sound: voice clean-up chain, retimed music bed (synth.py), 2026-style restrained SFX (Mixkit + library)

Usage:  python synth.py && python align.py && python match_pickup.py && python make.py   (--skip-base reuses build/base.mp4)
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

P = Path(__file__).resolve().parent
ROOT = P.parent.parent
SRC = ROOT / "inbox/lakshadweep_v2/IMG_3950.MP4"
B = P / "build"
OUT = P / "out"
NAME = "lakshadweep_reel_v2"
FPS = 30
DUR = 38.233
SR = 48000
FONTS = ROOT / "fonts"
FONTS_REL = "../../../fonts"      # ffmpeg filter args choke on "C:", so filters run from build/ with a relative path

SANS, SERIF = "Inter Display Medium", "Instrument Serif"
FS_SANS, FS_KW = 120, 156
HANDLE = "@travelwisha"

# safe zone for caption blocks (1080x1920): IG top bar above 240, caption/UI below 1470, buttons right of 950
SAFE_X0, SAFE_X1 = 130, 950
SAFE_Y0, SAFE_Y1 = 240, 1470
MAX_W = 2 * min(540 - SAFE_X0, SAFE_X1 - 540)     # centred at 540 -> 820 px
HANDLE_Y = 1505

# ------------------------------------------------------------------ shots
# (start, kind, zoom0, zoom1)  kind F = talking head, B = B-roll. Cuts from scene detection on the draft.
SHOTS = [
    (0.000, "F", 1.00, 1.00),   # ek friend ka message aata hai
    (1.400, "B", 1.00, 1.05),   # phone chat
    (2.967, "F", 1.00, 1.00),   # aur before you can even think / you say yes
    (5.667, "B", 1.00, 1.05),   # airport
    (7.233, "F", 1.00, 1.00),   # just to see the most
    (8.400, "B", 1.05, 1.00),   # boat wake (pull)
    (9.167, "B", 1.00, 1.05),   # plane tail
    (10.200, "F", 1.00, 1.00),  # and then you land on a small island
    (12.300, "B", 1.00, 1.04),  # beach
    (13.800, "B", 1.00, 1.04),  # feet in the water
    (15.833, "B", 1.00, 1.04),  # cycling
    (18.300, "F", 1.00, 1.00),  # and then comes day two
    (19.867, "B", 1.00, 1.04),  # dive briefing
    (21.700, "B", 1.05, 1.00),  # dive boat (pull)
    (23.833, "F", 1.00, 1.00),  # life mein pehli baar
    (25.567, "B", 1.00, 1.05),  # underwater, divers
    (27.433, "B", 1.00, 1.04),  # coral
    (28.767, "B", 1.04, 1.00),  # fish (pull)
    (29.933, "F", 1.00, 1.00),  # aur ek silence
    (31.270, "F", 1.07, 1.07),  # punch-in on "jo upar kabhi nhi milegi" (same take)
    (33.233, "B", 1.00, 1.05),  # sunset
    (34.333, "B", 1.00, 1.04),  # palms -> island mosque tilt (replaces the diver-with-flag shot, see REPLACE)
    (35.300, "B", 1.00, 1.04),  # anemone
    (36.500, "B", 1.00, 1.05),  # island walk
]
CUTS = [s[0] for s in SHOTS] + [DUR]
# shot start -> (replacement clip, source in-point). 2026-11-02: client swapped the diver-with-flag shot for
# IMG_3883.MOV (palms tilting down to the mosque); 1.3 s in = the mosque rising into frame.
REPLACE = {34.333: (ROOT / "inbox/lakshadweep_v2/IMG_3883.MOV", 1.3)}

HDR_TO_SDR = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
              "zscale=t=bt709:m=bt709:r=tv,format=gbrp")
# talking head: lift mids, pull red/yellow saturation down a touch and rotate it slightly toward gold
# (measured on her cheeks: L 63.8, chroma 23.4, hue 56.5  vs v1: L 61.6, chroma 33.1, hue 55.1)
GRADE_F = ("curves=master='0/0 0.06/0.05 0.45/0.54 0.85/0.885 1/0.97',"
           "huesaturation=colors=r+y:saturation=-0.08:hue=4,colorbalance=rm=-0.01:gm=0.004")
# B-roll: same lift, vibrance (protects already-saturated colour), sea/sky a little richer, warm tones held back
GRADE_B = ("curves=master='0/0 0.07/0.055 0.45/0.53 0.85/0.89 1/0.98',vibrance=intensity=0.12,"
           "huesaturation=colors=c+b:saturation=0.10,huesaturation=colors=r+y:saturation=-0.06")

def run(cmd, **kw):
    print("  $", " ".join(str(c) for c in cmd)[:240])
    subprocess.run(cmd, check=True, **kw)

def render_base():
    n = len(SHOTS)
    fc = [f"[0:v]fps={FPS},{HDR_TO_SDR},scale=2160:3840:flags=lanczos,split={n}" + "".join(f"[s{i}]" for i in range(n))]
    extra = []                                       # replacement clips -> extra ffmpeg inputs
    for i, ((a, kind, z0, z1), b) in enumerate(zip(SHOTS, CUTS[1:])):
        frames = max(1, round((b - a) * FPS))
        z = f"{z0}+({z1}-{z0})*on/{frames}"
        py = 0.35 if kind == "F" else 0.5          # punch-in on a face: keep the face where it was, grow downward
        g = GRADE_F if kind == "F" else GRADE_B
        zp = f"zoompan=z='{z}':x='iw/2-iw/zoom/2':y='(ih-ih/zoom)*{py}':d=1:s=1080x1920:fps={FPS},{g}[v{i}]"
        if a in REPLACE:
            path, s0 = REPLACE[a]
            extra.append(path)
            k = len(extra)
            # real speed (60 fps -> 30 fps by dropping frames, no slow-mo), same HDR->SDR + grade as the draft
            fc.append(f"[s{i}]nullsink")
            fc.append(f"[{k}:v]trim=start={s0}:duration={b - a + 0.05},setpts=PTS-STARTPTS,fps={FPS},{HDR_TO_SDR},"
                      f"scale=2160:3840:flags=lanczos,trim=end_frame={frames},{zp}")
            continue
        fc.append(f"[s{i}]trim=start={a}:end={b},setpts=PTS-STARTPTS,{zp}")
    fc.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0,format=yuv420p,"
              "setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv[v]")
    (B / "base.fc").write_text(";\n".join(fc), encoding="utf-8")
    run(["ffmpeg", "-y", "-v", "error", "-stats", "-i", str(SRC), *[x for p in extra for x in ("-i", str(p))],
         "-/filter_complex", str(B / "base.fc"),
         "-map", "[v]", "-an", "-t", str(DUR), "-c:v", "libx264", "-preset", "medium", "-crf", "12", "-pix_fmt", "yuv420p",
         "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", str(B / "base.mp4")])

# ------------------------------------------------------------------ captions
# "|" = line break, *word* = serif-italic keyword. Words are matched in order to build/words.json (forced alignment).
# pref = preferred block centre (fraction of 1920); the face check moves it if it would touch her face.
TALK = 0.70
PAGES = [
    ("ek friend ka | *message* aata hai", TALK),
    ("*Lakshadweep* | chalegi?", 0.22),
    ("aur before you | can even *think*", TALK),
    ("you say *yes*", TALK),
    ("to a never ending | *layover*", 0.70),
    ("just to see | the most", TALK),
    ("*turquoise* | blue water", 0.30),
    ("from your *window*", 0.30),
    ("and then | you *land*", TALK),
    ("on a small | *island*", TALK),
    ("where day one | is just", 0.25),
    ("*beach,* breeze | and water", 0.25),
    ("friends | ke sath", 0.17),
    ("bohot saari | *masti*", 0.17),
    ("and then comes | *day two*", TALK),
    ("masks on, | *regulators* in", 0.22),
    ("all set for | our first *dive*", 0.30),
    ("life mein | *pehli baar*", TALK),
    ("you breathe | *underwater*", 0.70),
    ("bas *corals,*", 0.40),
    ("*colourful* fish", 0.62),
    ("aur ek | *silence*", TALK),
    ("jo upar kabhi | nhi *milegi*", TALK),
    ("par ek *dive*", 0.25),
    ("kabhi enough | nhi hoti", 0.72),   # low: the anemone shot has a masked diver up top (YuNet cannot see masked faces)
    ("so stay tuned", 0.30),
    ("for *part 2*", 0.30),
]
HOLD = 1.1          # a page stays at most this long after its last word, unless the next page starts sooner
# pages that should end exactly on a cut instead (page index -> time)
PAGE_END = {1: 2.967, 4: 7.233, 7: 10.20, 10: 13.80, 13: 18.30, 14: 19.867, 16: 23.833, 17: 25.567, 19: 28.767, 20: 29.933, 22: 33.233, 26: DUR}

def parse_pages():
    words = json.loads((B / "words.json").read_text(encoding="utf-8"))
    k = 0
    pages = []
    for i, (txt, pref) in enumerate(PAGES):
        lines = []
        for ln in txt.split("|"):
            ws = []
            for w in ln.split():
                kw = w.startswith("*") or w.endswith("*")
                t = words[k]["start"]
                k += 1
                ws.append({"text": w.strip("*"), "kw": kw, "t": t})
            lines.append(ws)
        pages.append({"lines": lines, "pref": pref})
    assert k == len(words), f"{k} caption words vs {len(words)} aligned words"
    for i, pg in enumerate(pages):
        last = pg["lines"][-1][-1]["t"]
        nxt = pages[i + 1]["lines"][0][0]["t"] if i + 1 < len(pages) else DUR
        end = PAGE_END.get(i, last + HOLD + 0.3)
        pg["end"] = min(end, nxt)
        pg["t0"] = pg["lines"][0][0]["t"]
    return pages

def at(t):
    t = max(0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"

STEADY = r"\1a&H00&\3a&H9A&\4a&H70&"          # fill opaque, soft dark halo (blurred outline), soft shadow
HIDDEN = r"\1a&HFF&\3a&HFF&\4a&HFF&"

def line_text(words, show, scale=1.0):
    parts = []
    for k, w in enumerate(words):
        font = (rf"\fn{SERIF}\i1\fs{FS_KW * scale:.1f}" if w["kw"] else rf"\fn{SANS}\i0\fs{FS_SANS * scale:.1f}")
        sep = " " if k < len(words) - 1 else ""
        parts.append("{" + font + show(k) + "}" + w["text"] + sep)
    return "".join(parts)

HDR = rf"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{SANS},{FS_SANS},&H00FFFFFF,&H00FFFFFF,&H9A101418,&H70202020,0,0,0,0,100,100,-1,0,1,4,3,5,0,0,0,1
Style: Handle,Playfair Display,30,&H40FFFFFF,&H40FFFFFF,&HFF000000,&HA0000000,0,0,0,0,100,100,1,0,1,0,1.5,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def render_mask_frames(events, nframes, fps=10):
    """render ASS events on black -> list of bool masks (1080x1920)"""
    (B / "measure.ass").write_text(HDR + "\n".join(events) + "\n", encoding="utf-8")
    cmd = ["ffmpeg", "-v", "error", "-f", "lavfi", "-i", f"color=c=black:s=1080x1920:r={fps}:d={nframes / fps}",
           "-vf", f"ass=measure.ass:fontsdir={FONTS_REL}", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True, cwd=B).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 1920, 1080)
    return [f > 40 for f in fr[:nframes]]

def pitch_of(pg):
    return 108 if any(w["kw"] for ln in pg["lines"] for w in ln) else 98

def measure_pages(pages):
    """per page: shrink factor so its widest line fits MAX_W, and the block's vertical extent around its centre"""
    shown = lambda j: STEADY
    ev = []
    for i, pg in enumerate(pages):
        n = len(pg["lines"])
        for li, words in enumerate(pg["lines"]):
            y = 960 - pitch_of(pg) * (n - 1) / 2 + li * pitch_of(pg)
            ev.append(f"Dialogue: 0,{at(i * 0.1)},{at(i * 0.1 + 0.1)},Cap,,0,0,0,,{{\\an5\\pos(540,{y:.0f})\\q2}}{line_text(words, shown)}")
    masks = render_mask_frames(ev, len(pages))
    for pg, m in zip(pages, masks):
        xs = np.where(m.any(0))[0]
        ys = np.where(m.any(1))[0]
        w = xs.max() - xs.min()
        pg["scale"] = min(1.0, MAX_W / w)
        pg["h_up"] = (960 - ys.min()) * pg["scale"]
        pg["h_dn"] = (ys.max() - 960) * pg["scale"]
        pg["w"] = w * pg["scale"]

def page_events(pg, yc):
    out = []
    n = len(pg["lines"])
    s = pg["scale"]
    pitch = pitch_of(pg) * s
    y0 = yc - pitch * (n - 1) / 2
    for li, words in enumerate(pg["lines"]):
        y = round(y0 + li * pitch)
        for k, w in enumerate(words):
            t, end = w["t"], pg["end"]
            entry = rf"\bord0\shad0\1a&HFF&\blur14\t(0,200,\1a&H00&\blur0)"
            ta = line_text(words, lambda j: entry if j == k else HIDDEN, s)
            out.append(f"Dialogue: 2,{at(t)},{at(min(end, t + 0.22))},Cap,,0,0,0,,{{\\an5\\pos(540,{y})\\q2}}{ta}")
            if end > t + 0.18:
                steady = HIDDEN + rf"\1a&H00&\blur6\t(0,140,{STEADY})"
                tb = line_text(words, lambda j: steady if j == k else HIDDEN, s)
                out.append(f"Dialogue: 1,{at(t + 0.18)},{at(end)},Cap,,0,0,0,,{{\\an5\\pos(540,{y})\\q2}}{tb}")
    return out

# ------------------------------------------------------------------ faces
MODEL = ROOT / "models/face_detection_yunet_2023mar.onnx"
FW, FH = 540, 960

def detect_faces(video):
    import cv2
    det = cv2.FaceDetectorYN.create(str(MODEL), "", (FW, FH), score_threshold=0.6, nms_threshold=0.3, top_k=20)
    out = []
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"scale={FW}:{FH}", "-f", "rawvideo",
                          "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    sz = FW * FH * 3
    S = 1080 / FW
    while True:
        b = p.stdout.read(sz)
        if len(b) < sz:
            break
        img = np.frombuffer(b, np.uint8).reshape(FH, FW, 3)
        _, faces = det.detect(img)
        boxes = []
        raw = [(float(f[0]), float(f[1]), float(f[2]), float(f[3]), float(f[-1])) for f in (faces if faces is not None else [])]
        for x, y, w, h, sc in raw:
            if sc < 0.7 or w < 25:          # tiny faces (divers far away, crowd) don't block text
                continue
            # hands/torso false positives: a smaller box sitting below a bigger face's chin
            if any(h < 0.85 * H2 and y > Y2 + 0.8 * H2 for X2, Y2, W2, H2, s2 in raw if s2 >= 0.7):
                continue
            # pad: hair/forehead above, to the chin below, a little to the sides
            boxes.append([(x - 0.15 * w) * S, (y - 0.40 * h) * S, (x + 1.15 * w) * S, (y + 1.0 * h) * S])
        out.append(boxes)
    p.wait()
    return out

def place_pages(pages, faces, margin=30):
    nF = len(faces)
    for pg in pages:
        f0, f1 = int(pg["t0"] * FPS), min(nF, int(np.ceil(pg["end"] * FPS)))
        boxes = [bx for fr in range(f0, f1) for bx in faces[fr]]
        x0, x1 = 540 - pg["w"] / 2 - margin, 540 + pg["w"] / 2 + margin
        lo, hi = SAFE_Y0 + pg["h_up"], SAFE_Y1 - pg["h_dn"]
        pref = min(max(pg["pref"] * 1920, lo), hi)
        def hits(yc):
            a0, a1 = yc - pg["h_up"] - margin, yc + pg["h_dn"] + margin
            return sum(1 for bx0, by0, bx1, by1 in boxes if not (x1 < bx0 or x0 > bx1 or a1 < by0 or a0 > by1))
        cands = sorted(np.arange(lo, hi + 1, 6), key=lambda y: abs(y - pref))
        best = min(cands, key=lambda y: (hits(y), abs(y - pref)))
        pg["y"] = float(best)
        pg["face_hits"] = hits(best)
        pg["moved"] = round(best - pg["pref"] * 1920)

def build_ass(path, pages, with_captions=True, with_handle=True):
    ev = []
    if with_captions:
        for pg in pages:
            ev += page_events(pg, pg["y"])
    if with_handle:
        ev.append(f"Dialogue: 0,{at(0)},{at(DUR)},Handle,,0,0,0,,{{\\an5\\pos(540,{HANDLE_Y})}}{HANDLE}")
    path.write_text(HDR + "\n".join(ev) + "\n", encoding="utf-8")

def build_srt(path, pages):
    def st(t):
        return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
    out = []
    for i, pg in enumerate(pages, 1):
        words = [w for ln in pg["lines"] for w in ln]
        out.append(f"{i}\n{st(words[0]['t'])} --> {st(pg['end'])}\n{' '.join(w['text'] for w in words)}\n")
    path.write_text("\n".join(out), encoding="utf-8")

# ------------------------------------------------------------------ sound effects
LIB = ROOT / "sfx_library"
N = int(DUR * SR)
_cache = {}

def load(name):
    if name not in _cache:
        r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(LIB / name), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                           capture_output=True, check=True)
        _cache[name] = np.frombuffer(r.stdout, np.float32).reshape(-1, 2).copy()
    return _cache[name]

def place(buf, name, src_in, src_out, at_t, gain_db=0.0, fin=0.01, fout=0.05, align="start", pan=0.0):
    """cut src_in..src_out from a library file, peak-normalise, fade, gain, mix at timeline at_t.
    align='peak': at_t is where the loudest moment lands; align='end': at_t is where the cut ends"""
    x = load(name)[int(src_in * SR):int(src_out * SR)].copy()
    x /= np.abs(x).max() + 1e-9
    n = len(x)
    fi, fo = max(1, int(fin * SR)), max(1, int(fout * SR))
    x[:fi] *= np.linspace(0, 1, fi)[:, None]
    x[-fo:] *= np.linspace(1, 0, fo)[:, None]
    if pan:
        a = (pan + 1) * np.pi / 4
        x[:, 0] *= np.cos(a) * 1.414
        x[:, 1] *= np.sin(a) * 1.414
    if align == "peak":
        env = np.convolve(np.abs(x).mean(1), np.ones(960) / 960, "same")
        at_t -= env.argmax() / SR
    elif align == "end":
        at_t -= n / SR
    i = int(round(at_t * SR))
    j0 = max(0, -i); i = max(0, i)
    m = min(n - j0, N - i)
    if m > 0:
        buf[i:i + m] += x[j0:j0 + m] * 10 ** (gain_db / 20)

DL = "dl_2026_11/"       # Mixkit (Mixkit Sound Effects Free License), fetched 2026-11-02

def build_sfx():
    """Restrained 2026 travel-reel sound design: soft whooshes on the big cuts, ambience beds that make each place
    real, ONE riser -> sub impact on the reveal (first breath underwater), a hard drop to silence on "aur ek silence",
    and a single payoff hit on "part 2"."""
    b = np.zeros((N, 2), np.float32)
    # 0:01.4  phone on screen: iMessage-style ping, then soft phone typing under "Lakshadweep chalegi?"
    place(b, "msg_iphone_text_received.mp3", 2.27, 3.05, 1.40, -9, fin=0.003, fout=0.25)
    place(b, DL + "typing_smartphone.mp3", 0.0, 1.3, 1.85, -23, fin=0.05, fout=0.3)
    # 0:05.67 airport: soft wind swoosh into the cut
    place(b, DL + "swoosh_cinematic_wind.mp3", 0.1, 1.2, 5.667, -15, align="peak", fout=0.3)
    # 0:08.4 boat wake / 0:09.17 plane tail
    place(b, "motorboat_sea.mp3", 10.0, 10.9, 8.36, -15, fin=0.08, fout=0.35)
    place(b, "plane_low_over.mp3", 0.2, 1.3, 9.12, -15, fin=0.15, fout=0.5)
    # 0:12.3 beach -> waves + birds; 0:13.8 feet in the water -> close waves
    place(b, "waves_birds_beach.mp3", 4.0, 5.6, 12.25, -14, fin=0.15, fout=0.5)
    place(b, "waves_close_loop.mp3", 6.0, 8.1, 13.75, -15, fin=0.3, fout=0.6)
    # 0:15.83 cycling -> bike bell
    place(b, "bike_bell_ring.mp3", 0.0, 1.6, 15.88, -11, fin=0.002, fout=0.6, pan=0.3)
    # 0:19.87 dive briefing -> small sweep; 0:21.7 dive boat -> water lapping
    place(b, DL + "sweep_fast_small.mp3", 0.0, 0.7, 19.867, -18, align="peak", fout=0.2)
    place(b, "waves_small_rocks.mp3", 10.0, 12.0, 21.65, -18, fin=0.3, fout=0.5)
    # 0:23.1 -> 0:25.57 THE reveal: riser under "life mein pehli baar", sub impact + splash on the cut underwater
    place(b, DL + "riser_trailer.mp3", 0.0, 2.55, 25.567, -19, fin=0.6, fout=0.02, align="end")
    place(b, DL + "impact_whoosh_deep.mp3", 0.2, 2.6, 25.567, -9, align="peak", fout=0.9)
    place(b, "splash_jump_in.mp3", 0.0, 1.4, 25.567, -14, align="peak", fout=0.5)
    place(b, "underwater_ambience.mp3", 2.0, 6.4, 25.55, -16, fin=0.1, fout=0.3)
    # "you breathe underwater" -> one real regulator breath
    place(b, "scuba_breathe_gear.mp3", 6.0, 8.6, 26.0, -13, fin=0.05, fout=0.3)
    # 0:27.43 coral / 0:28.77 fish -> air-tank bubbles, then everything stops at 0:29.93 ("aur ek silence")
    place(b, "bubbles_airtank.mp3", 0.3, 2.1, 27.80, -19, fin=0.2, fout=0.3, pan=-0.2)
    b[int(29.933 * SR):int(33.15 * SR)] *= 0.0
    # 0:33.23 back in on the sunset: wind swoosh + soft sea
    place(b, DL + "swoosh_ending_wind.mp3", 0.3, 1.9, 33.233, -17, align="peak", fin=0.3, fout=0.5)
    place(b, "waves_sea_loop.mp3", 3.0, 4.2, 33.30, -20, fin=0.3, fout=0.4)
    # 0:34.33 palms -> mosque (land shot): soft swoosh on the tilt + birds/breeze; 0:35.3 anemone -> bubble burst
    place(b, DL + "swoosh_short_wind.mp3", 0.0, 0.5, 34.333, -20, align="peak", fout=0.2)
    place(b, "waves_birds_beach.mp3", 8.0, 9.0, 34.33, -19, fin=0.08, fout=0.25)
    place(b, "bubbles_deep.mp3", 0.0, 1.0, 35.35, -19, fin=0.05, fout=0.4)
    # 0:36.5 island walk -> birds; 0:37.71 "part 2" -> soft UI tick + deep hit, the cliffhanger lands
    place(b, "waves_birds_beach.mp3", 14.0, 15.4, 36.45, -19, fin=0.1, fout=0.5)
    place(b, DL + "click_interface_tone.mp3", 0.0, 0.15, 37.71, -16, fin=0.001, fout=0.08)
    place(b, DL + "impact_whoosh_deep.mp3", 0.2, 2.6, 37.74, -11, align="peak", fout=0.4)
    return b

def music_fx():
    """music bed with an underwater low-pass while we're under (25.57 -> 29.93), crossfaded in/out"""
    sr, m = wavfile.read(B / "music.wav")
    m = m.astype(np.float64)
    sos = butter(4, 600, "lowpass", fs=sr, output="sos")
    lp = np.stack([sosfilt(sos, m[:, c]) for c in range(2)], 1) * 1.25
    t = np.arange(len(m)) / sr
    w = np.clip((t - 25.48) / 0.12, 0, 1) * np.clip((29.98 - t) / 0.08, 0, 1)
    out = m * (1 - w[:, None]) + lp * w[:, None]
    wavfile.write(B / "music_fx.wav", sr, out.astype(np.float32))

# ------------------------------------------------------------------ mix
VOICE = ("highpass=f=90:poles=2,highpass=f=90:poles=2,afftdn=nf=-48:tn=1,"
         "equalizer=f=210:t=q:w=1.1:g=-3.5,equalizer=f=480:t=q:w=1.2:g=-1.5,"
         "equalizer=f=3400:t=q:w=1.0:g=3.5,equalizer=f=10000:t=h:w=0.7:g=2.5,"
         "deesser=i=0.3,acompressor=threshold=-26dB:ratio=3:attack=5:release=110:makeup=4,"
         "alimiter=limit=0.89:level=false")

def render_audio():
    fc = (f"[0:a]aresample={SR},aformat=channel_layouts=stereo,{VOICE},atrim=0:{DUR},apad=whole_dur={DUR},asplit=3[v][vsc][vsc2];"
          "[1:a]volume=0dB,treble=g=3:f=3000:t=s:w=0.6[m0];"
          "[m0][vsc]sidechaincompress=threshold=0.02:ratio=6:attack=20:release=320:makeup=1[m];"
          "[2:a]volume=-2dB[s0];"
          "[s0][vsc2]sidechaincompress=threshold=0.05:ratio=2.5:attack=15:release=250[s];"
          f"[v][m][s]amix=inputs=3:normalize=0:duration=first,atrim=0:{DUR}[mix]")
    # voice = the draft's audio with the pickup line tone-matched to the rest (match_pickup.py)
    voice_src = B / "src_matched.wav"
    ins = ["-i", str(voice_src), "-i", str(B / "music_fx.wav"), "-i", str(B / "sfx.wav")]
    run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", fc, "-map", "[mix]", "-c:a", "pcm_f32le", str(B / "mix_pre.wav")])
    fc2 = fc.replace("[v][m][s]amix=inputs=3", "[m]anullsink;[v][s]amix=inputs=2")
    run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", fc2, "-map", "[mix]", "-c:a", "pcm_f32le", str(B / "mix_nomusic_pre.wav")])
    # voice alone (for checking the clean-up)
    run(["ffmpeg", "-y", "-v", "error", "-i", str(voice_src), "-af", f"aresample={SR},{VOICE}", "-c:a", "pcm_f32le", str(B / "voice_only_pre.wav")])
    return (loudnorm(B / "mix_pre.wav", B / "mix.wav"), loudnorm(B / "mix_nomusic_pre.wav", B / "mix_nomusic.wav"),
            loudnorm(B / "voice_only_pre.wav", B / "voice_only.wav"))

def loudnorm(src, dst, I=-14, TP=-1.5):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af", f"loudnorm=I={I}:TP={TP}:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    ln = (f"loudnorm=I={I}:TP={TP}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-af", f"{ln},aresample={SR}", "-c:a", "pcm_s24le", str(dst)])
    return dst

# ------------------------------------------------------------------ deliver
def encode(video_filter, audio, out):
    cmd = ["ffmpeg", "-y", "-v", "error", "-stats", "-i", str(B / "base.mp4"), "-i", str(audio)]
    if video_filter:
        cmd += ["-vf", video_filter]
    cmd += ["-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high",
            "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-r", str(FPS), "-c:a", "aac", "-b:a", "320k", "-ar", str(SR), "-movflags", "+faststart", "-shortest", str(out)]
    run(cmd, cwd=B)

def caption_qa(pages, faces):
    """render captions alone, check every frame: inside the safe zone, and not touching a (padded) face box"""
    ev = []
    for pg in pages:
        ev += page_events(pg, pg["y"])
    nF = int(DUR * FPS)
    (B / "captions_only.ass").write_text(HDR + "\n".join(ev) + "\n", encoding="utf-8")
    cmd = ["ffmpeg", "-v", "error", "-f", "lavfi", "-i", f"color=c=black:s=1080x1920:r={FPS}:d={DUR}",
           "-vf", f"ass=captions_only.ass:fontsdir={FONTS_REL},scale=540:960", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=B)
    bad_safe, bad_face, ext = [], [], [9999, 9999, 0, 0]
    fr = 0
    while True:
        buf = p.stdout.read(540 * 960)
        if len(buf) < 540 * 960:
            break
        m = np.frombuffer(buf, np.uint8).reshape(960, 540) > 40
        if m.any():
            ys, xs = np.where(m)
            x0, x1, y0, y1 = xs.min() * 2, xs.max() * 2, ys.min() * 2, ys.max() * 2
            ext = [min(ext[0], x0), min(ext[1], y0), max(ext[2], x1), max(ext[3], y1)]
            if x0 < SAFE_X0 - 4 or x1 > SAFE_X1 + 4 or y0 < SAFE_Y0 - 4 or y1 > SAFE_Y1 + 4:
                bad_safe.append(fr / FPS)
            if fr < len(faces):
                for bx0, by0, bx1, by1 in faces[fr]:
                    if not (x1 < bx0 or x0 > bx1 or y1 < by0 or y0 > by1):
                        bad_face.append(fr / FPS)
                        break
        fr += 1
    p.wait()
    print(f"caption extents x {ext[0]}..{ext[2]}  y {ext[1]}..{ext[3]}   (safe x {SAFE_X0}..{SAFE_X1}, y {SAFE_Y0}..{SAFE_Y1})")
    print(f"frames outside safe zone: {len(bad_safe)}   frames touching a face: {len(bad_face)}")
    if bad_face:
        print("  face-touch times:", sorted(set(round(t, 1) for t in bad_face)))
    return bad_safe, bad_face

def main(skip_base=False):
    OUT.mkdir(exist_ok=True)
    B.mkdir(exist_ok=True)
    if not skip_base or not (B / "base.mp4").exists():
        render_base()
    pages = parse_pages()
    measure_pages(pages)
    faces = detect_faces(B / "base.mp4")
    (B / "faces.json").write_text(json.dumps(faces))
    place_pages(pages, faces)
    for i, pg in enumerate(pages):
        txt = " ".join(w["text"] for ln in pg["lines"] for w in ln)
        print(f"{i:2d} {pg['t0']:6.2f}-{pg['end']:6.2f} {txt[:30]:30s} scale {pg['scale']:.2f} w {pg['w']:4.0f} "
              f"y {pg['y']:5.0f} moved {pg['moved']:+5d} face-hits {pg['face_hits']}")
    build_ass(B / "captions.ass", pages)
    build_srt(OUT / f"{NAME}.srt", pages)
    caption_qa(pages, faces)
    sfx = build_sfx()
    pk = np.abs(sfx).max()
    if pk > 0.95:
        sfx *= 0.95 / pk
    wavfile.write(B / "sfx.wav", SR, sfx.astype(np.float32))
    music_fx()
    mix, mix_nm, vo = render_audio()
    fonts = FONTS_REL
    encode(f"ass=captions.ass:fontsdir={fonts}", mix, OUT / f"{NAME}.mp4")
    encode(f"ass=captions.ass:fontsdir={fonts}", mix_nm, OUT / f"{NAME}_no_music.mp4")
    build_ass(B / "handle.ass", pages, with_captions=False)
    encode(f"ass=handle.ass:fontsdir={fonts}", mix, OUT / f"{NAME}_no_captions.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-ss", "1.9", "-i", str(OUT / f"{NAME}.mp4"), "-frames:v", "1", str(OUT / f"{NAME}_cover.png")])

if __name__ == "__main__":
    main(skip_base="--skip-base" in sys.argv)
