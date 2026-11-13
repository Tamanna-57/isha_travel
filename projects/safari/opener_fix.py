"""Opener fix for safari_reel_INTERIM_open-on-isha.mp4 (2026-11-13).

Client: "sync just this first clip with the glitched clip ... make it smooth and add the caption and everything
from the TOO LOUD section".

What was wrong in the interim (frames 0-89, 0.00-2.97 s):
  * 0.00-1.27 s was a FROZEN still of Isha while the audio already says the first line -> lips don't move.
  * 1.27-2.97 s the talking clip ran ~0.1-0.2 s behind its own audio and had a hard 1.11x punch-in mid-gesture.
Fix:
  * the reel's audio is kept untouched (already mastered, -14 LUFS); only its silent head is trimmed (TRIM).
  * the whole opener is rebuilt from Isha's take (inbox/safari_opener/isha_first_clip_whatsapp.mp4), retimed onto
    that audio. The interim plays the line 1.265x faster than the take; the map comes from DTW on MFCCs
    (interim = 0.7906 * take + 0.4402 s, residual sd 21 ms). In-between frames are optical-flow interpolated,
    so the speed-up has no judder.
  * one smooth push-in (1.00 -> 1.11, same end framing as the interim) instead of the hard punch-in.
  * colour matched to the interim's grade (per-channel histogram transfer over matched frames).
  * title (kicker + TOO LOUD) and karaoke captions rebuilt with the same fonts, sizes and positions, measured to
    the pixel against the interim. Title is on from frame 0 (it is the cover frame). Word timings are the interim's own.
  * frame 90 onward (the jungle cut and everything after) is the interim, unchanged.

    python projects/safari/opener_fix.py
"""
import subprocess
from pathlib import Path
import numpy as np, cv2

P = Path(__file__).resolve().parent
ROOT = P.parent.parent
INB = ROOT / "inbox" / "safari_opener"
TAKE = INB / "isha_first_clip_whatsapp.mp4"
INTERIM = INB / "safari_reel_INTERIM_open-on-isha.mp4"
B = P / "build" / "opener_fix"; FR = B / "frames"
OUT = P / "out" / "safari_reel_v6_synced-open.mp4"
FONTS = ROOT / "fonts"
FPS, W, H = 30, 1080, 1920

TRIM_F = 13                  # interim frames dropped from the head (silent; the take starts 0.44 s into the audio)
TRIM = TRIM_F / FPS
CUT_F = 90                   # first interim frame kept as-is (jungle shot)
N_OPEN = CUT_F - TRIM_F      # rebuilt frames
A_MAP, B_MAP = 0.7906, 0.4402            # interim_time = A * take_time + B
S0 = W / 464                              # take is 464x832: full frame
S1 = 2.587                                # interim end framing (measured)


def frames(path, n=None):
    c = cv2.VideoCapture(str(path)); out = []
    while n is None or len(out) < n:
        ok, f = c.read()
        if not ok:
            break
        out.append(f)
    return out


def take_time(interim_t):
    return (interim_t - B_MAP) / A_MAP


def affine(s):
    """take -> 1080x1920, centred zoom s"""
    return np.float32([[s, 0, W / 2 - 232 * s], [0, s, H / 2 - 416 * s]])


# ------------------------------------------------------------------ colour: take -> interim grade
def build_luts(TK, IM):
    pairs = [(i, 2.318) for i in range(38, 48)] + [(i, S1) for i in range(74, 89)]
    src, dst = [], []
    for i, s in pairs:
        k = int(round(take_time(i / FPS) * FPS)); k = min(max(k, 0), len(TK) - 1)
        w = cv2.warpAffine(TK[k], affine(s), (W, H), flags=cv2.INTER_AREA)
        m = np.ones((H, W), bool); m[180:520] = False; m[1270:1420] = False   # skip text bands
        m[:, :40] = m[:, -40:] = False
        src.append(w[m]); dst.append(IM[i][m])
    src, dst = np.concatenate(src), np.concatenate(dst)
    luts = []
    for ch in range(3):
        hs = np.bincount(src[:, ch], minlength=256).cumsum() / len(src)
        hd = np.bincount(dst[:, ch], minlength=256).cumsum() / len(dst)
        lut = np.interp(hs, hd, np.arange(256))
        lut = np.convolve(np.pad(lut, 4, mode="edge"), np.ones(9) / 9, "valid")   # smooth the curve
        luts.append(np.clip(lut, 0, 255).astype(np.uint8))
    return luts


# ------------------------------------------------------------------ retime with optical-flow in-betweens
DIS = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
_flow_cache = {}

def flows(TK, i):
    if i not in _flow_cache:
        g0 = cv2.cvtColor(TK[i], cv2.COLOR_BGR2GRAY); g1 = cv2.cvtColor(TK[i + 1], cv2.COLOR_BGR2GRAY)
        _flow_cache[i] = (DIS.calc(g0, g1, None), DIS.calc(g1, g0, None))
    return _flow_cache[i]

def sample(TK, t):
    x = min(max(t * FPS, 0.0), len(TK) - 1.0)
    i = int(np.floor(x)); a = x - i
    if a < 0.02 or i >= len(TK) - 1:
        return TK[min(i, len(TK) - 1)]
    if a > 0.98:
        return TK[i + 1]
    f01, f10 = flows(TK, i)
    h, w = f01.shape[:2]
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    m0 = (gx - a * f01[..., 0], gy - a * f01[..., 1])
    m1 = (gx - (1 - a) * f10[..., 0], gy - (1 - a) * f10[..., 1])
    w0 = cv2.remap(TK[i], m0[0], m0[1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    w1 = cv2.remap(TK[i + 1], m1[0], m1[1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return cv2.addWeighted(w0, 1 - a, w1, a, 0)


def ease(x):
    x = min(1.0, max(0.0, x))
    return 0.5 - 0.5 * np.cos(np.pi * x)


# ------------------------------------------------------------------ overlays (ASS, brand styles from isha.py)
def ass_time(x):
    x = max(0.0, x); return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"

def write_ass(path):
    sh, ol = "&H8C000000&", "&HA0000000&"
    hdr = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\nScaledBorderAndShadow: yes\n"
           "YCbCr Matrix: TV.709\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
           "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, "
           "Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
           f"Style: Sans,Poppins SemiBold,115,&HFFFFFF&,&HFFFFFF&,{ol},{sh},0,0,0,0,100,100,0,0,1,1.5,4,5,110,130,60,1\n"
           f"Style: Chapter,Anton,292,&H3D26D7&,&H3D26D7&,{ol},{sh},0,0,0,0,100,100,0,0,1,0,6,5,60,60,60,1\n"
           f"Style: Kicker,Playfair Display,63,&HFFFFFF&,&HFFFFFF&,{ol},{sh},0,0,0,0,100,100,0,0,1,1.2,3,5,60,60,60,1\n"
           "\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    E = []
    t_end = 2.92 - TRIM                                   # interim: title fades out 2.80-2.92
    E.append(f"Dialogue: 2,{ass_time(0)},{ass_time(t_end)},Kicker,,0,0,0,,"
             r"{\an5\pos(540,250)\fad(0,120)}for 3 nights, the city was")
    E.append(f"Dialogue: 2,{ass_time(0)},{ass_time(t_end)},Chapter,,0,0,0,,"
             r"{\an5\pos(540,390)\fax-0.12\fad(0,120)}TOO LOUD")
    G, GOLD = "&H9A9A9A&", "&H45C4F6&"

    def page(start, end, words):
        ms = lambda x: int(round((x - TRIM - start) * 1000))
        body = []
        for w, t, emph in words:
            d = ms(t)
            if emph:
                body.append(rf"{{\fnPlayfair Display\b1\i1\fs126\1c&H2E7AA0&\alpha&H30&\t({d},{d + 1},\1c{GOLD}\alpha&H00&)}}{w}")
            else:
                body.append(rf"{{\1c{G}\alpha&H30&\t({d},{d + 1},\1c&HFFFFFF&\alpha&H00&)}}{w}")
        E.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Sans,,0,0,0,,"
                 + r"{\an5\pos(540,1340)\fad(40,0)}" + " ".join(body))

    # interim word timings (seconds on the interim timeline)
    page(1.267 - TRIM, 2.467 - TRIM, [("shehar", 1.300, 0), ("ne", 1.600, 0), ("bahut", 1.733, 0), ("shor", 2.233, 1)])
    page(2.467 - TRIM, CUT_F / FPS - TRIM, [("kar", 2.467, 0), ("liya,", 2.700, 0)])
    Path(path).write_text(hdr + "\n".join(E) + "\n", encoding="utf-8")


def main():
    FR.mkdir(parents=True, exist_ok=True)
    TK = frames(TAKE)
    IM = frames(INTERIM, CUT_F)
    luts = build_luts(TK, IM)
    for k in range(N_OPEN):
        t_int = (k + TRIM_F) / FPS
        f = sample(TK, take_time(t_int))
        s = S0 + (S1 - S0) * ease(k / (N_OPEN - 1))
        f = cv2.warpAffine(f, affine(s), (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
        blur = cv2.GaussianBlur(f, (0, 0), 1.3)
        f = cv2.addWeighted(f, 1.55, blur, -0.55, 0)                     # mild unsharp after the 2.3x upscale
        f = np.dstack([cv2.LUT(f[..., c], luts[c]) for c in range(3)])
        cv2.imwrite(str(FR / f"{k:04d}.png"), f)
    write_ass(B / "opener.ass")

    ass = str(B / "opener.ass").replace(":", r"\:")
    fc = (f"[0:v]scale=in_range=pc:out_color_matrix=bt709:out_range=tv,format=yuv420p,setsar=1,ass='{ass}':fontsdir='{FONTS}',settb=1/{FPS},setpts=N[o];"
          f"[1:v]trim=start_frame={CUT_F},setpts=PTS-STARTPTS,settb=1/{FPS},setsar=1[r];"
          f"[o][r]concat=n=2:v=1:a=0,format=yuv420p[v];"
          f"[1:a]atrim=start={TRIM},asetpts=PTS-STARTPTS[a]")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(FR / "%04d.png"), "-i", str(INTERIM),
                    "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-profile:v", "high", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p",
                    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
                    "-r", str(FPS), "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", str(OUT)],
                   check=True)
    print(OUT)


if __name__ == "__main__":
    main()
