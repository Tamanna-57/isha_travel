"""Lakshadweep reel — edit in the style of the client reference (WhatsApp Video 2026-11-02 at 3.36.24 PM.mp4).

Reference look, matched here:
  * word-by-word captions that BUILD a 1-2 line phrase; each new word blurs + fades in (~0.2 s), nothing exits
  * lowercase grotesk sans (Inter Display Medium) + one condensed serif-italic keyword (Instrument Serif Italic, 1.3x)
  * soft grey drop shadow, no box; captions sit in the empty part of each shot (sky, water, chest band)
  * tiny serif handle watermark at the bottom
  * hard cuts, slow push-ins on B-roll, bright airy natural grade, soft music bed + motivated SFX

Usage:  python make.py            (after python synth.py)
"""
import json, re, subprocess
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parent.parent
SRC = ROOT / "inbox/lakshadweep/IMG_2201.MP4"
B = P / "build"
OUT = P / "out"
NAME = "lakshadweep_reel"
FPS = 30
DUR = 39.133

SANS, SERIF = "Inter Display Medium", "Instrument Serif"
FS_SANS, FS_KW = 120, 156          # calibrated to the reference width shares (calib.py)
HANDLE = "@travelwisha"

# ------------------------------------------------------------------ captions
# talking-head band: below her chin on every frame (checked with facecheck.py / YuNet), above the IG bottom UI
TALK_Y = 0.735
# "|" = line break, *word* = serif-italic keyword. One start time per word (timeline seconds).
# Words proofread from two whisper passes (en + hi) against the energy envelope; Roman Hinglish.
PAGES = [
    ("ek friend ka | *message* aata hai",        [0.05, 0.20, 0.38, 0.48, 0.70, 0.84], TALK_Y),
    ("*Lakshadweep* | chalegi?",                 [1.30, 1.68], 0.15),
    ("aur before you | can even *think*",        [2.70, 2.85, 3.10, 3.25, 3.45, 3.75], TALK_Y),
    ("you say *yes*",                            [4.20, 4.38, 4.52], TALK_Y),
    ("never-ending | *layover*",                 [5.05, 5.60], 0.72),
    ("just to see | the most",                   [6.25, 6.40, 6.50, 6.70, 6.82], TALK_Y),
    ("*turquoise* | blue water",                 [7.00, 7.50, 7.70], TALK_Y),
    ("from your *window*",                       [8.00, 8.15, 8.35], 0.30),
    ("and then | you *land*",                    [9.40, 9.55, 9.80, 10.00], TALK_Y),
    ("on a small | *island*",                    [10.20, 10.30, 10.40, 10.75], TALK_Y),
    ("where day one | is just",                  [11.25, 11.55, 11.75, 12.00, 12.15], 0.30),
    ("*beach,* breeze, | water",                 [12.50, 12.95, 13.45], 0.30),
    ("aur friends | ke saath",                   [14.00, 14.50, 14.95, 15.10], 0.145),
    ("bohot saari | *masti*",                    [15.40, 15.85, 16.05], 0.4),
    ("and then comes | *day* *two*",             [16.70, 16.85, 17.05, 17.30, 17.50], TALK_Y),
    ("masks on, | *regulators* in",              [18.45, 18.80, 19.00, 19.65], 0.25),
    ("all set for | a *first* *time*",           [20.45, 20.65, 20.85, 20.95, 21.00, 21.15], 0.33),
    ("life mein | *pehli* *baar*",               [21.75, 22.25, 22.45, 22.85], TALK_Y),
    ("you breathe | *underwater*",               [23.25, 23.45, 23.75], 0.71),
    ("bas *corals,*",                            [25.45, 25.65], 0.42),
    ("*colourful* fish",                         [26.40, 26.85], 0.62),
    ("aur ek | *silence*",                       [27.50, 27.65, 27.80], TALK_Y),
    ("jo upar kabhi | nahi *milegi*",            [28.40, 28.60, 28.95, 29.25, 29.50], TALK_Y),
    # outro (no voice): closing line from the client's own script, revealed on the music
    ("ek random *yes*",                          [32.95, 33.25, 33.65], 0.24),
    ("*Lakshadweep*",                            [37.45], 0.22),
]
PAGE_END = {1: 2.60, 3: 5.00, 7: 9.30, 9: 11.25, 13: 16.65, 14: 18.40, 15: 20.40, 16: 21.70, 17: 23.20,
            18: 25.40, 20: 27.45, 22: 30.45, 23: 35.60, 24: DUR}

def parse_pages():
    pages = []
    for i, (txt, times, y) in enumerate(PAGES):
        lines, k = [], 0
        for ln in txt.split("|"):
            words = []
            for w in ln.split():
                kw = w.startswith("*")
                words.append({"text": w.strip("*"), "kw": kw, "t": times[k]})
                k += 1
            lines.append(words)
        assert k == len(times), f"page {i}: {k} words vs {len(times)} times"
        nxt = PAGES[i + 1][1][0] if i + 1 < len(PAGES) else DUR
        end = PAGE_END.get(i, min(nxt, times[-1] + 1.1))
        pages.append({"lines": lines, "y": y, "end": min(end, nxt)})
    return pages

def at(t):
    t = max(0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"

STEADY = r"\1a&H00&\3a&HC8&\4a&H78&"          # fill opaque, faint outline glow, soft shadow
HIDDEN = r"\1a&HFF&\3a&HFF&\4a&HFF&"

def line_text(words, show):
    """full line, every word present for stable layout; show(k) -> override tag for word k"""
    parts = []
    for k, w in enumerate(words):
        font = rf"\fn{SERIF}\i1\fs{FS_KW}" if w["kw"] else rf"\fn{SANS}\i0\fs{FS_SANS}"
        sep = " " if k < len(words) - 1 else ""
        parts.append("{" + font + show(k) + "}" + w["text"] + sep)
    return "".join(parts)

def build_ass(path, with_captions=True, with_handle=True):
    hdr = rf"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{SANS},{FS_SANS},&H00FFFFFF,&H00FFFFFF,&HC8000000,&H78202020,0,0,0,0,100,100,-1,0,1,2.5,3.5,5,0,0,0,1
Style: Handle,Playfair Display,30,&H40FFFFFF,&H40FFFFFF,&HFF000000,&HA0000000,0,0,0,0,100,100,1,0,1,0,1.5,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    if with_captions:
        for pg in parse_pages():
            n = len(pg["lines"])
            has_kw = [any(w["kw"] for w in ln) for ln in pg["lines"]]
            # line pitch: tighter between two sans lines, a bit more when a keyword line is involved (like the ref)
            pitch = 108 if any(has_kw) else 98
            y0 = pg["y"] * 1920 - pitch * (n - 1) / 2
            for li, words in enumerate(pg["lines"]):
                y = round(y0 + li * pitch)
                # keyword lines sit a touch lower so the italic's x-height lines up with the sans line above
                if has_kw[li] and li > 0:
                    y += 2
                for k, w in enumerate(words):
                    t, end = w["t"], pg["end"]
                    # A: entry — no outline/shadow so the fill itself can blur; blur 14 -> 0 and fade in
                    entry = rf"\bord0\shad0\1a&HFF&\blur14\t(0,200,\1a&H00&\blur0)"
                    ta = line_text(words, lambda j: entry if j == k else HIDDEN)
                    ev.append(f"Dialogue: 2,{at(t)},{at(min(end, t + 0.22))},Cap,,0,0,0,,{{\\an5\\pos(540,{y})\\q2}}{ta}")
                    # B: steady with the soft glow/shadow fading in, until the page ends
                    if end > t + 0.18:
                        steady = HIDDEN + rf"\1a&H00&\blur3\t(0,140,{STEADY})"
                        tb = line_text(words, lambda j: steady if j == k else HIDDEN)
                        ev.append(f"Dialogue: 1,{at(t + 0.18)},{at(end)},Cap,,0,0,0,,{{\\an5\\pos(540,{y})\\q2}}{tb}")
    if with_handle:
        ev.append(f"Dialogue: 0,{at(0)},{at(DUR)},Handle,,0,0,0,,{{\\an5\\pos(540,1650)}}{HANDLE}")
    path.write_text(hdr + "\n".join(ev) + "\n", encoding="utf-8")

def build_srt(path):
    out = []
    for i, pg in enumerate(parse_pages(), 1):
        words = [w for ln in pg["lines"] for w in ln]
        s = words[0]["t"]
        def st(t):
            return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d},{int(round(t % 1 * 1000)) % 1000:03d}"
        out.append(f"{i}\n{st(s)} --> {st(pg['end'])}\n{' '.join(w['text'] for w in words)}\n")
    path.write_text("\n".join(out), encoding="utf-8")

# ------------------------------------------------------------------ picture
CUTS = [0, 1.3, 2.7, 5.167, 6.633, 7.7, 8.4, 9.333, 11.267, 12.667, 14.5, 16.767, 18.2, 19.9, 21.833,
        23.433, 25.167, 26.367, 27.433, 28.4, 30.467, 32.667, 34.333, 35.567, 37.333, DUR]
# (zoom at start, zoom at end) per shot. Talking head alternates 1.00 / 1.07 to hide the jump cuts
# (and punches in on "jo upar" mid-shot); B-roll gets a slow push (or pull) like a gimbal drift.
MOTION = [
    (1.00, 1.00),  # face          ek friend ka message
    (1.00, 1.07),  # phone chat    Lakshadweep chalegi?
    (1.07, 1.07),  # face          aur before you can even think
    (1.00, 1.05),  # airport
    (1.00, 1.00),  # face
    (1.05, 1.00),  # boat wake (pull)
    (1.00, 1.05),  # plane tail
    (1.07, 1.07),  # face          and then you land
    (1.00, 1.04),  # beach
    (1.00, 1.04),  # feet in water
    (1.00, 1.04),  # cycling
    (1.00, 1.00),  # face          day two
    (1.00, 1.04),  # dive briefing
    (1.05, 1.00),  # dive boat (pull)
    (1.07, 1.07),  # face          life mein pehli baar
    (1.00, 1.05),  # underwater
    (1.00, 1.04),  # coral
    (1.04, 1.00),  # fish (pull)
    (1.00, 1.00),  # face          aur ek silence
    (1.08, 1.08),  # face punch    jo upar kabhi nahi milegi
    (1.00, 1.04),  # goat          (outro)
    (1.00, 1.06),  # sunset
    (1.00, 1.04),  # diver with flag
    (1.00, 1.04),  # anemone
    (1.00, 1.05),  # walk
]
assert len(MOTION) == len(CUTS) - 1

HDR_TO_SDR = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
              "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
# bright, airy, natural (measured against the reference: mean ~117, p5 ~25, sat ~0.45)
GRADE = ("curves=master='0/0 0.08/0.05 0.5/0.57 0.88/0.9 1/0.98',eq=saturation=1.10,"
         "vibrance=intensity=0.10,colorbalance=rm=0.006:bm=-0.006")

def run(cmd, **kw):
    print("  $", " ".join(str(c) for c in cmd)[:300])
    subprocess.run(cmd, check=True, **kw)

def render_base():
    n = len(MOTION)
    fc = [f"[0:v]fps={FPS},{HDR_TO_SDR},{GRADE},scale=2160:3840:flags=lanczos,split={n}" + "".join(f"[s{i}]" for i in range(n))]
    for i, ((z0, z1), a, b) in enumerate(zip(MOTION, CUTS, CUTS[1:])):
        frames = max(1, round((b - a) * FPS))
        z = f"{z0}+({z1}-{z0})*on/{frames}"
        # talking head (static zoom): pivot at the caption band so her face grows upward, away from the text
        py = 0.72 if z0 == z1 and z0 > 1 else 0.5
        fc.append(f"[s{i}]trim=start={a}:end={b},setpts=PTS-STARTPTS,"
                  f"zoompan=z='{z}':x='iw/2-iw/zoom/2':y='(ih-ih/zoom)*{py}':d=1:s=1080x1920:fps={FPS}[v{i}]")
    fc.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0,format=yuv420p,"
              "setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv[v]")
    (B / "base.fc").write_text(";\n".join(fc), encoding="utf-8")
    run(["ffmpeg", "-y", "-v", "error", "-stats", "-i", str(SRC), "-/filter_complex", str(B / "base.fc"),
         "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "12", "-pix_fmt", "yuv420p",
         "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", str(B / "base.mp4")])

# ------------------------------------------------------------------ sound
VOICE_END = 30.30
def render_audio():
    # voice: clean-up chain (rumble cut, denoise, mud cut, presence, de-ess, gentle compression)
    voice = ("highpass=f=85,afftdn=nf=-38:tn=1,"
             "equalizer=f=250:t=q:w=1.0:g=-2.5,equalizer=f=3200:t=q:w=1.2:g=2.5,equalizer=f=11000:t=h:w=0.7:g=1.5,"
             "deesser=i=0.35,acompressor=threshold=-22dB:ratio=3:attack=6:release=120:makeup=3,"
             f"afade=t=out:st={VOICE_END - 0.2}:d=0.25,atrim=0:{DUR},apad=whole_dur={DUR}")
    fc = (f"[0:a]aresample=48000,aformat=channel_layouts=stereo,{voice},asplit=3[v][vsc][vsc2];"
          # music: sits ~18 dB under the voice and ducks further while she talks
          "[1:a]volume=-3dB,treble=g=4:f=3000:t=s:w=0.6[m0];"
          "[m0][vsc]sidechaincompress=threshold=0.025:ratio=5:attack=20:release=320:makeup=1[m];"
          "[2:a]volume=-4dB[s0];"
          "[s0][vsc2]sidechaincompress=threshold=0.05:ratio=2.5:attack=15:release=250[s];"
          "[v][m][s]amix=inputs=3:normalize=0:duration=first,atrim=0:" + str(DUR) + "[mix]")
    pre = B / "mix_pre.wav"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(SRC), "-i", str(B / "music.wav"), "-i", str(B / "sfx.wav"),
         "-filter_complex", fc, "-map", "[mix]", "-c:a", "pcm_f32le", "-ar", "48000", str(pre)])
    # voice + SFX only (for adding a trending sound inside Instagram)
    fc2 = fc.replace("[v][m][s]amix=inputs=3", "[m]anullsink;[v][s]amix=inputs=2")
    pre2 = B / "mix_nomusic_pre.wav"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(SRC), "-i", str(B / "music.wav"), "-i", str(B / "sfx.wav"),
         "-filter_complex", fc2, "-map", "[mix]", "-c:a", "pcm_f32le", "-ar", "48000", str(pre2)])
    return loudnorm(pre, B / "mix.wav"), loudnorm(pre2, B / "mix_nomusic.wav")

def loudnorm(src, dst, I=-14, TP=-1.5):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af", f"loudnorm=I={I}:TP={TP}:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    ln = (f"loudnorm=I={I}:TP={TP}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-af", f"{ln},aresample=48000", "-c:a", "pcm_s24le", str(dst)])
    return dst

# ------------------------------------------------------------------ deliver
def encode(video_filter, audio, out):
    cmd = ["ffmpeg", "-y", "-v", "error", "-stats", "-i", str(B / "base.mp4"), "-i", str(audio)]
    if video_filter:
        cmd += ["-vf", video_filter]
    cmd += ["-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high",
            "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-r", str(FPS), "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", "-shortest", str(out)]
    run(cmd, cwd=B)

def main(skip_base=False):
    OUT.mkdir(exist_ok=True)
    B.mkdir(exist_ok=True)
    build_ass(B / "captions.ass")
    build_ass(B / "handle.ass", with_captions=False)
    build_srt(OUT / f"{NAME}.srt")
    if not skip_base or not (B / "base.mp4").exists():
        render_base()
    mix, mix_nm = render_audio()
    fonts = "../../../fonts"
    encode(f"ass=captions.ass:fontsdir={fonts}", mix, OUT / f"{NAME}.mp4")
    encode(f"ass=captions.ass:fontsdir={fonts}", mix_nm, OUT / f"{NAME}_no_music.mp4")
    encode(None, mix, OUT / f"{NAME}_clean.mp4")
    prev = OUT / "vscode_preview"
    prev.mkdir(exist_ok=True)
    for f in (f"{NAME}.mp4", f"{NAME}_no_music.mp4", f"{NAME}_clean.mp4"):
        run(["ffmpeg", "-y", "-v", "error", "-i", str(OUT / f), "-map", "0", "-c:v", "copy", "-c:a", "libopus",
             "-b:a", "192k", "-movflags", "+faststart", str(prev / f.replace(".mp4", "_vscode.mp4"))])
    run(["ffmpeg", "-y", "-v", "error", "-ss", "4.70", "-i", str(OUT / f"{NAME}.mp4"), "-frames:v", "1",
         str(OUT / f"{NAME}_cover.png")])

if __name__ == "__main__":
    import sys
    main(skip_base="--skip-base" in sys.argv)
