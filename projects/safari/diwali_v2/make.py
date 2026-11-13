"""Diwali x wildlife reel — v2 ("What the forest hears after Diwali"), 2026-11-13.

Client feedback addressed in this version:
  - open on Isha, keep her on camera the whole time (no full-screen cutaways)
  - wildlife shown as POP-UP CARDS below her face (over her torso), so viewers see the
    animal she names while she keeps talking
  - Lost & Free logo is a bottom card at the CTA (was top-left, above her head)
  - bold/raw captions: Inter Display ExtraBold (was serif Playfair italic)
  - audio de-glitched: the source .MOV carries TWO audio tracks — an Apple spatial "APAC"
    track that ffmpeg cannot decode (the glitch) and a clean AAC stereo track (stream a:1).
    We use the AAC track, process the voice and master to -14 LUFS.
  - over-saturation fixed: the source is 10-bit HLG HDR; we tone-map HLG->SDR (BT.709) and
    pull saturation slightly below the old render.

Source take: ../../../bhai dooj/diwali_lost/IMG_4068.MOV  (raw, rotation 90, HEVC Main10 HLG).
Caption wording/timing are mapped to the speech-energy envelope + the previous reel's script
(this environment has no audio monitoring); verify against the real voice and tweak PAGES.

Stages:  python make.py            # base -> compose -> audio -> mux
         python make.py --skip-base / --skip-comp to reuse intermediates.
Intermediates in build/, deliverable in out/ (both gitignored).
"""
import subprocess, sys
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

P = Path(__file__).resolve().parent
REPO = P.parents[2]
RAW = REPO / "bhai dooj/diwali_lost/IMG_4068.MOV"
ASSETS = REPO / "projects/safari/assets"
FONTS = REPO / "fonts"
BED = REPO / "sfx_library/dl_safari/2434-preview.mp3"
B = P / "build"; OUT = P / "out"
B.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)

FPS, W, H = 30, 1080, 1920
SRC_IN, SRC_OUT = 1.5, 25.8            # trim leading/trailing room tone
DUR = SRC_OUT - SRC_IN                 # 24.3 s
NF = int(round(DUR * FPS))
NAME = "safari_reel_v2"

# HLG HDR -> SDR BT.709, mild desaturate/contrast to match her skin without the HDR blowout
TM = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
      "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=saturation=0.86:contrast=1.04:gamma=0.985")

def run(cmd):
    print("  $", " ".join(str(c) for c in cmd)[:180]); subprocess.run(cmd, check=True)

# ------------------------------------------------------------------ stage 1: base
def base():
    vf = (f"{TM},scale={W}:{H},setsar=1,"
          f"zoompan=z='min(1.0+0.0009*in,1.07)':d=1:x='iw/2-(iw/zoom/2)':y='ih*0.44-(ih/zoom/2)':"
          f"s={W}x{H}:fps={FPS},format=yuv420p")
    run(["ffmpeg", "-y", "-v", "error", "-ss", str(SRC_IN), "-to", str(SRC_OUT), "-i", str(RAW),
         "-map", "0:0", "-an", "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "15",
         "-r", str(FPS), str(B / "base.mp4")])

# ------------------------------------------------------------------ cards + captions
YEL, WHITE = (246, 196, 69), (255, 255, 255)
CARD_W, CARD_H, CARD_CX, CARD_CY, CARD_R = 516, 432, 540, 1362, 30

def font(px):
    return ImageFont.truetype(str(FONTS / "InterDisplay-ExtraBold.ttf"), px)

def expo_out(x):
    x = min(1.0, max(0.0, x)); return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)

def grade_animal(img):
    f = img.astype(np.float32) / 255; g = f.mean(2, keepdims=True)
    f = g + (f - g) * 0.92; f = np.clip((f - 0.5) * 1.06 + 0.5, 0, 1)
    f[..., 0] *= 1.015; f[..., 2] *= 0.985
    return np.clip(f * 255, 0, 255).astype(np.uint8)

def cover(img, w, h, fx=0.5, fy=0.45):
    ih, iw = img.shape[:2]; s = max(w / iw, h / ih); cw, ch = w / s, h / s
    x0 = np.clip(fx * iw - cw / 2, 0, iw - cw); y0 = np.clip(fy * ih - ch / 2, 0, ih - ch)
    M = np.array([[s, 0, -x0 * s], [0, s, -y0 * s]], np.float32)
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REFLECT)

def load_rgb(p):
    return cv2.cvtColor(cv2.imread(str(p), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)

def make_card(animal_rgb=None, logo=False, fx=0.5, fy=0.42):
    pad, cw, ch = 60, CARD_W, CARD_H
    canvas = Image.new("RGBA", (cw + 2 * pad, ch + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 16, pad + cw, pad + ch + 16), radius=CARD_R, fill=130)
    sh = cv2.GaussianBlur(np.array(sh), (0, 0), 22)
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0)); shadow.putalpha(Image.fromarray(sh))
    canvas = Image.alpha_composite(canvas, shadow)
    if logo:
        bgc = tuple(int(v) for v in (ASSETS / "logo_bg.txt").read_text().split())
        panel = Image.new("RGB", (cw, ch), bgc)
        lg = Image.open(ASSETS / "logo.png").convert("RGBA")
        lw = int(cw * 0.74); lh = int(lg.height * lw / lg.width)
        lg = lg.resize((lw, lh), Image.LANCZOS); panel.paste(lg, ((cw - lw) // 2, (ch - lh) // 2), lg)
        photo = panel.convert("RGBA")
    else:
        photo = Image.fromarray(grade_animal(cover(animal_rgb, cw, ch, fx, fy))).convert("RGBA")
    mask = Image.new("L", (cw, ch), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw - 1, ch - 1), radius=CARD_R, fill=255)
    photo.putalpha(mask); canvas.alpha_composite(photo, (pad, pad))
    bd = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(bd).rounded_rectangle((pad, pad, pad + cw - 1, pad + ch - 1), radius=CARD_R,
                                         outline=(255, 255, 255, 235), width=6)
    return np.array(Image.alpha_composite(canvas, bd)).astype(np.float32) / 255.0

# (asset or "LOGO", t0, t1, fx, fy)  — times on the trimmed timeline (source - 1.5 s)
CARDS = [
    ("jungle_road_mist.jpg", 3.55, 6.95, 0.5, 0.5),
    ("chital_stag.jpg", 7.45, 9.15, 0.5, 0.45),
    ("isha_owl.jpg", 9.20, 12.05, 0.5, 0.40),
    ("chital_fawn.jpg", 12.10, 14.65, 0.5, 0.30),
    ("tiger_eyes.jpg", 14.80, 16.75, 0.55, 0.5),
    ("sal_forest.jpg", 16.90, 18.10, 0.5, 0.5),
    ("gypsy.jpg", 18.85, 21.10, 0.5, 0.5),
    ("LOGO", 21.40, 24.30, 0.5, 0.5),
]
# caption pages: (text, t0, t1) ; *word* = yellow keyword
PAGES = [
    ("Teen raaton tak", 0.30, 1.42), ("shehar ne bahut *shor*", 1.45, 2.95),
    ("Aur *jungle*?", 3.55, 4.60), ("woh bas *chup-chaap*", 4.65, 5.85), ("*sunta* raha", 5.88, 6.98),
    ("har *dhamaka*", 7.48, 8.28), ("har *dhuaan*", 8.32, 9.12),
    ("inke *kaan*", 12.12, 13.32), ("humse *zyada* sunte hain", 13.36, 14.62),
    ("unke liye *roshni* nahi", 14.82, 15.78), ("*darr* hai", 15.82, 16.74),
    ("isliye main *jungle* mein", 16.92, 18.05),
    ("*chup-chaap* rehna", 18.88, 19.98), ("pasand karti hoon", 20.02, 21.08),
    ("*Something* exciting", 21.45, 22.48), ("is coming your *way*", 22.52, 23.58),
    ("stay *tuned*", 23.62, 24.28),
]
CAP_FS, KW_FS, CAP_Y, MAXW = 70, 92, 1052, 900

def parse(text):
    return [(t.replace("*", ""), "*" in t) for t in text.split()]

def measure(toks, scale):
    w = 0
    for i, (t, kw) in enumerate(toks):
        f = font(int((KW_FS if kw else CAP_FS) * scale))
        bb = f.getbbox(t + (" " if i < len(toks) - 1 else "")); w += bb[2] - bb[0]
    return w

def draw_caption(frame, text, appear):
    toks = parse(text)
    scale = min(1.0, MAXW / max(1, measure(toks, 1.0)))
    s = (0.90 + 0.10 * expo_out(appear / 0.12)) * scale
    a = min(1.0, appear / 0.10)
    tw = measure(toks, s)
    th = max(font(int((KW_FS if kw else CAP_FS) * s)).getbbox(t)[3] for t, kw in toks)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    x = (W - tw) / 2; y = CAP_Y - th / 2
    for i, (t, kw) in enumerate(toks):
        f = font(int((KW_FS if kw else CAP_FS) * s)); word = t + (" " if i < len(toks) - 1 else "")
        d.text((x + 2, y + 4), word, font=f, fill=(0, 0, 0, int(150 * a)))
        for dx in (-2, 2):
            for dy in (-2, 2):
                d.text((x + dx, y + dy), word, font=f, fill=(0, 0, 0, int(120 * a)))
        d.text((x, y), word, font=f, fill=(YEL if kw else WHITE) + (int(255 * a),))
        x += f.getbbox(word)[2] - f.getbbox(word)[0]
    arr = np.array(ov).astype(np.float32); al = arr[..., 3:4] / 255.0
    frame[:] = (arr[..., :3] * al + frame * (1 - al)).astype(np.uint8)

def blend_rgba(frame, rgba, cx, cy, scale, alpha):
    if scale != 1.0:
        rgba = cv2.resize(rgba, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    h, w = rgba.shape[:2]; x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if xa >= xb or ya >= yb:
        return
    src = rgba[ya - y0:yb - y0, xa - x0:xb - x0]; al = src[..., 3:4] * alpha
    reg = frame[ya:yb, xa:xb].astype(np.float32)
    frame[ya:yb, xa:xb] = (src[..., :3] * 255 * al + reg * (1 - al)).astype(np.uint8)

def compose():
    cards = [(make_card(logo=True) if n == "LOGO" else make_card(load_rgb(ASSETS / n), fx=fx, fy=fy), t0, t1)
             for n, t0, t1, fx, fy in CARDS]
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(B / "base.mp4"),
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                            "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", str(B / "comp.mp4")],
                           stdin=subprocess.PIPE)
    sz = W * H * 3
    for fi in range(NF):
        buf = dec.stdout.read(sz)
        if len(buf) < sz:
            break
        t = fi / FPS; frame = np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()
        for rgba, t0, t1 in cards:
            if not (t0 - 0.02 <= t < t1 + 0.22):
                continue
            if t < t0 + 0.22:
                p = expo_out((t - t0) / 0.22); al = min(1.0, (t - t0) / 0.14); sc = 0.92 + 0.08 * p; dy = 26 * (1 - p)
            elif t >= t1:
                p = expo_out((t - t1) / 0.20); al = max(0.0, 1 - p); sc = 1.0 - 0.03 * p; dy = -12 * p
            else:
                al, sc, dy = 1.0, 1.0, 0.0
            if al > 0:
                blend_rgba(frame, rgba, CARD_CX, CARD_CY + dy, sc, al)
        for text, t0, t1 in PAGES:
            if t0 <= t < t1:
                draw_caption(frame, text, t - t0); break
        enc.stdin.write(frame.tobytes())
        if fi % 120 == 0:
            print(f"  compose {fi}/{NF}", flush=True)
    enc.stdin.close(); enc.wait(); dec.wait()

# ------------------------------------------------------------------ stage 3: audio
VC = ("atrim=1.5:25.8,asetpts=PTS-STARTPTS,highpass=f=85,afftdn=nf=-26:tn=1,"
      "equalizer=f=250:t=q:w=1.1:g=-2,equalizer=f=3200:t=q:w=1.1:g=2.5,equalizer=f=9000:t=h:w=0.7:g=1.5,"
      "acompressor=threshold=-22dB:ratio=3:attack=6:release=130:makeup=3,alimiter=limit=0.9,aresample=48000")

def audio():
    # clean AAC stereo = stream a:1 (a:0 is the undecodable Apple spatial APAC track)
    run(["ffmpeg", "-y", "-v", "error", "-i", str(RAW), "-map", "0:a:1", "-ac", "2",
         "-c:a", "pcm_s16le", str(B / "voice_raw.wav")])
    fc = (f"[0:a]{VC},asplit=2[v][vk];"
          f"[1:a]aformat=channel_layouts=stereo,atrim=0:{DUR},asetpts=PTS-STARTPTS,"
          f"afade=t=in:st=0:d=1.3,afade=t=out:st={DUR-1.3:.2f}:d=1.3,volume=-26dB[bed0];"
          f"[bed0][vk]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=320[bedd];"
          f"[v][bedd]amix=inputs=2:normalize=0:duration=first[m]")
    run(["ffmpeg", "-y", "-v", "error", "-i", str(B / "voice_raw.wav"), "-i", str(BED),
         "-filter_complex", fc, "-map", "[m]", "-ac", "2", "-c:a", "pcm_f32le", str(B / "mix_pre.wav")])
    import json
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(B / "mix_pre.wav"),
                        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    run(["ffmpeg", "-y", "-v", "error", "-i", str(B / "mix_pre.wav"), "-af", f"{ln},aresample=48000",
         "-c:a", "pcm_s16le", str(B / "mix.wav")])

# ------------------------------------------------------------------ stage 4: mux
def mux():
    run(["ffmpeg", "-y", "-v", "error", "-i", str(B / "comp.mp4"), "-i", str(B / "mix.wav"),
         "-map", "0:v", "-map", "1:a",
         "-vf", "setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv,format=yuv420p",
         "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-profile:v", "high",
         "-x264-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", "-shortest",
         str(OUT / f"{NAME}.mp4")])

if __name__ == "__main__":
    if "--skip-base" not in sys.argv and "--skip-comp" not in sys.argv:
        base()
    if "--skip-comp" not in sys.argv:
        compose()
    audio()
    mux()
    print("done ->", OUT / f"{NAME}.mp4")
