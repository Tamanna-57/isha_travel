#!/usr/bin/env python3
"""
Isha reel pipeline: turns raw clips + an edit.json cut list into a finished 9:16 reel
in the house style defined in ../ISHA_REEL_SYSTEM.md.

Commands
  probe <files...>                 specs of every clip (fps, VFR, HDR, rotation, audio)
  sheet <file> [--n 16]            contact sheet PNG next to the file (or --out)
  transcribe <file> [--model ..]   word-level timestamps via ffmpeg's whisper filter -> <file>.words.json
  beats <music>                    beat times for beat-cutting -> <music>.beats.json
  render <edit.json> [--stage ..]  assemble -> captions/titles -> grade/mix/loudness -> deliverables
  qa <final.mp4>                   specs, loudness, shot rhythm, contact sheet

Only depends on ffmpeg/ffprobe on PATH, numpy and Pillow.
"""
import argparse, json, math, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # .../isha
FONTS = ROOT / "fonts"
MODELS = ROOT / "models"
W, H, FPS = 1080, 1920, 30

# ------------------------------------------------------------------ brand tokens
# ASS colours are &HBBGGRR&
C = {
    "ink": "&H111111&", "chalk": "&HFFFFFF&", "ivory": "&HE5F6FF&",
    "marigold": "&H45C4F6&", "sindoor": "&H3D26D7&", "saffron": "&H2B9CF3&",
    "paper": "&HEAF3F7&", "grey": "&H9A9A9A&",
}
PAPER_RGB = "0xF7F3EA"

# role -> (family name as libass sees it, font file, bold flag, Windows fallback family, fallback bold)
# libass only distinguishes Regular/Bold inside a family, so in-between weights are addressed by their own
# legacy family names ("Poppins SemiBold", "Playfair Display SemiBold", ...) with bold off.
FONT_ROLES = {
    "serif":      ("Playfair Display SemiBold", "PlayfairDisplay-SemiBold.ttf", 0, "Georgia", 1),
    "serif_reg":  ("Playfair Display", "PlayfairDisplay-Regular.ttf", 0, "Georgia", 0),
    "serif_it":   ("Instrument Serif", "InstrumentSerif-Italic.ttf", 0, "Georgia", 0),
    "sans_semi":  ("Poppins SemiBold", "Poppins-SemiBold.ttf", 0, "Segoe UI Semibold", 0),
    "sans_med":   ("Poppins Medium", "Poppins-Medium.ttf", 0, "Segoe UI", 0),
    "sans_bold":  ("Poppins", "Poppins-Bold.ttf", 1, "Segoe UI", 1),
    "sans_xbold": ("Poppins ExtraBold", "Poppins-ExtraBold.ttf", 0, "Segoe UI Black", 0),
    "sans_light": ("Poppins Light", "Poppins-Light.ttf", 0, "Segoe UI Light", 0),
    "caps":       ("Montserrat", "Montserrat-Bold.ttf", 1, "Segoe UI", 1),
    "condensed":  ("Anton", "Anton-Regular.ttf", 0, "Impact", 0),
    "script":     ("Allura", "Allura-Regular.ttf", 0, "Segoe Script", 0),
    "roman":      ("Cinzel SemiBold", "Cinzel-SemiBold.ttf", 0, "Palatino Linotype", 1),
    "marker":     ("Caveat", "Caveat-Bold.ttf", 1, "Segoe Print", 1),
    "mono":       ("Courier Prime", "CourierPrime-Regular.ttf", 0, "Consolas", 0),
}

def fnt(role):
    """(family, bold) for a role: the brand font if its file is in fonts/, else the Windows fallback"""
    fam, file, bold, fb, fb_bold = FONT_ROLES[role]
    return (fam, bold) if (FONTS / file).exists() else (fb, fb_bold)

def font(role):
    return fnt(role)[0]

def fn_tag(role):
    """inline override switching to a role's font and weight"""
    fam, bold = fnt(role)
    return f"\\fn{fam}\\b{bold}"

STOP = set("""a an the is am are was were be been to of and or but in on at for with from by as it its i me my
you your he she we they them this that these those so do did does not no yes just very really also then than
there here what which who when where how all any some can could will would should into out up down over about
hai hain tha thi the ho hu hun hoon main mai mein me mera meri mere tum tu aap ka ki ke ko se pe par aur ya
toh to bhi na nahi nahin ye yeh wo woh vo is us ek jo kya kaise kyun kab abhi bas phir fir hi""".split())

# ------------------------------------------------------------------ helpers
def run(cmd, cwd=None, quiet=True, capture=False):
    cmd = [str(c) for c in cmd]
    if not quiet:
        print("  $", " ".join(cmd))
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-4000:])
        raise SystemExit(f"command failed: {cmd[0]} (exit {r.returncode})")
    return r if capture else None

def ffprobe(path):
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path], capture=True)
    return json.loads(r.stdout)

def frac(s):
    try:
        n, d = s.split("/"); return float(n) / float(d) if float(d) else 0.0
    except Exception:
        return 0.0

def clip_info(path):
    j = ffprobe(path)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    dur = float(j["format"].get("duration", 0) or 0)
    info = {"file": str(path), "duration": round(dur, 3), "has_audio": a is not None}
    if v:
        rot = 0
        for sd in v.get("side_data_list", []) or []:
            if "rotation" in sd:
                rot = int(float(sd["rotation"]))
        rot = int(v.get("tags", {}).get("rotate", rot))
        w, h = v.get("width"), v.get("height")
        if abs(rot) in (90, 270):
            w, h = h, w
        r_fps, a_fps = frac(v.get("r_frame_rate", "0/1")), frac(v.get("avg_frame_rate", "0/1"))
        trc = v.get("color_transfer", "")
        info.update({
            "width": w, "height": h, "rotation": rot, "fps": round(a_fps or r_fps, 3),
            "vfr": bool(r_fps and a_fps and abs(r_fps - a_fps) > 0.05),
            "codec": v.get("codec_name"), "pix_fmt": v.get("pix_fmt"),
            "color_transfer": trc, "color_primaries": v.get("color_primaries", ""),
            "hdr": trc in ("arib-std-b67", "smpte2084"),
        })
    if a:
        info.update({"audio_channels": a.get("channels"), "audio_rate": a.get("sample_rate")})
    return info

def ass_time(t):
    t = max(0.0, t)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def ass_escape(s):
    return s.replace("\\", "\\\\").replace("{", "(").replace("}", ")").replace("\n", " ")

NOISE = re.compile(r"^[\[(♪*].*[\])♪*]$|^♪+$")      # whisper non-speech tags: [Music], (laughs), ♪

def clean_words(words):
    """drop non-speech tags and empty tokens from a words list (any source: whisper, hand-made, edited)"""
    return [w for w in words if w.get("text", "").strip() and not NOISE.match(w["text"].strip())]

def ff_path(p, base):
    """path for use inside an ffmpeg filter argument: relative to `base` (no drive colon to escape);
    on a different drive fall back to an absolute path with the colon escaped"""
    try:
        return os.path.relpath(Path(p).resolve(), base).replace("\\", "/")
    except ValueError:
        return str(Path(p).resolve()).replace("\\", "/").replace(":", "\\:")

def srt_time(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

# ------------------------------------------------------------------ probe / sheet
def cmd_probe(a):
    for f in a.files:
        i = clip_info(f)
        flags = []
        if i.get("vfr"): flags.append("VFR->conform")
        if i.get("hdr"): flags.append("HDR->tonemap")
        if i.get("rotation"): flags.append(f"rot{i['rotation']}")
        if not i["has_audio"]: flags.append("no-audio")
        print(f"{Path(f).name:40s} {i['duration']:7.2f}s {i.get('width')}x{i.get('height')} "
              f"{i.get('fps')}fps {i.get('codec')} {' '.join(flags)}")
    if a.json:
        print(json.dumps([clip_info(f) for f in a.files], indent=2))

def grab_frame(src, t, width=270):
    from PIL import Image
    import io
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(src), "-frames:v", "1",
                        "-vf", f"scale={width}:-2", "-f", "image2pipe", "-vcodec", "png", "-"],
                       capture_output=True)
    if not r.stdout:
        return None
    return Image.open(io.BytesIO(r.stdout)).convert("RGB")

def make_sheet(src, out, n=16, cols=8, times=None):
    from PIL import Image, ImageDraw
    dur = clip_info(src)["duration"]
    times = times or [round(dur * (i + 0.5) / n, 2) for i in range(n)]
    frames = [(t, grab_frame(src, t)) for t in times]
    frames = [(t, f) for t, f in frames if f is not None]
    if not frames:
        raise SystemExit("no frames decoded")
    fw, fh = frames[0][1].size
    rows = math.ceil(len(frames) / cols)
    sheet = Image.new("RGB", (cols * (fw + 4), rows * (fh + 4)), "black")
    d = ImageDraw.Draw(sheet)
    for i, (t, f) in enumerate(frames):
        x, y = (i % cols) * (fw + 4), (i // cols) * (fh + 4)
        sheet.paste(f, (x, y)); d.rectangle([x, y, x + 52, y + 16], fill=(200, 0, 0)); d.text((x + 3, y + 2), f"{t:.2f}s", fill="white")
    sheet.save(out)
    return out

def cmd_sheet(a):
    out = a.out or str(Path(a.file).with_suffix("")) + "_sheet.png"
    times = [float(x) for x in a.times.split(",")] if a.times else None
    print(make_sheet(a.file, out, n=a.n, times=times))

# ------------------------------------------------------------------ transcription
def parse_srt(text):
    out = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [l for l in block.strip().splitlines() if l.strip()]
        tl = next((l for l in lines if "-->" in l), None)
        if not tl:
            continue
        a_, b_ = [x.strip() for x in tl.split("-->")]
        def ms(t):
            h, m, rest = t.replace(".", ",").split(":"); s, f = rest.split(",")
            return int(h) * 3600 + int(m) * 60 + int(s) + int(f) / 1000
        txt = " ".join(lines[lines.index(tl) + 1:]).strip()
        if txt:
            out.append((ms(a_), ms(b_), txt))
    return out

def cmd_transcribe(a):
    model = Path(a.model) if a.model else next(iter(sorted(MODELS.glob("ggml-*.bin"))), None)
    if not model or not Path(model).exists():
        raise SystemExit(f"no whisper model found. Put a ggml model (e.g. ggml-small.bin) in {MODELS}")
    src = Path(a.file).resolve()
    out_srt = src.with_suffix(".whisper.srt")
    # ffmpeg filter args: escape ':' and '\' in paths -> use forward slashes, run from the model dir
    flt = (f"aresample=16000,aformat=sample_fmts=s16:channel_layouts=mono,"
           f"whisper=model={ff_path(model, src.parent)}:language={a.lang}:queue=10:max_len={a.max_len}"
           f":destination={out_srt.name}:format=srt")
    if a.vad:
        flt += f":vad_model={ff_path(a.vad, src.parent)}"
    run(["ffmpeg", "-y", "-v", "error", "-i", src.name, "-vn", "-af", flt, "-f", "null", "-"], cwd=src.parent, quiet=False)
    cues = parse_srt(out_srt.read_text(encoding="utf-8", errors="replace"))
    words = []
    for s, e, txt in cues:              # max_len~1 gives one word per cue; split any leftovers evenly within the cue
        parts = [p for p in txt.split() if not NOISE.match(p)]
        step = (e - s) / max(1, len(parts))
        for k, p in enumerate(parts):
            words.append({"text": p, "start": round(s + k * step, 3), "end": round(s + (k + 1) * step, 3)})
    out = Path(a.out) if a.out else src.with_suffix(".words.json")
    out.write_text(json.dumps(words, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{len(words)} words -> {out}\nProofread it (Roman Hinglish, names) before rendering captions.")

# ------------------------------------------------------------------ beats
def cmd_beats(a):
    import numpy as np
    sr = 22050
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", a.file, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True)
    x = np.frombuffer(r.stdout, dtype=np.float32)
    if x.size < sr:
        raise SystemExit("audio too short")
    hop, win = 512, 2048
    n = 1 + (len(x) - win) // hop
    idx = np.arange(win)[None, :] + hop * np.arange(n)[:, None]
    spec = np.abs(np.fft.rfft(x[idx] * np.hanning(win), axis=1))
    # 40 log-spaced bands, each weighted equally: hi-hats (many FFT bins) can't drown the kick (few bins)
    freqs = np.fft.rfftfreq(win, 1 / sr)
    edges = np.geomspace(30, 11000, 41)
    bands = np.stack([spec[:, (freqs >= lo) & (freqs < hi)].sum(axis=1) for lo, hi in zip(edges[:-1], edges[1:])], axis=1)
    bflux = np.maximum(0, np.diff(np.log1p(bands), axis=0))
    flux = bflux.sum(axis=1); flux = flux / (flux.std() + 1e-9)
    low = bflux[:, edges[1:] <= 160].sum(axis=1)          # kick / bass region: where the beat lives
    fps_env = sr / hop
    # flux[i] compares window i+1 with window i: the onset sits about at the centre of window i+1,
    # plus a measured 17 ms (beat bench: 7 synthetic tracks, constant early bias without it)
    t0 = (hop + win / 2) / sr + 0.017
    # tempo: autocorrelation in 70..180 BPM, weighted by a log-normal prior around 110 BPM (breaks 2:3 / 4:5
    # ambiguities from busy hats), refined to a fractional lag by parabolic interpolation
    f0 = flux - flux.mean()
    ac = np.correlate(f0, f0, mode="full")[len(f0) - 1:]
    lo_lag, hi_lag = int(fps_env * 60 / 180), int(fps_env * 60 / 70) + 1
    lags = np.arange(lo_lag, hi_lag)
    prior = np.exp(-0.5 * (np.log2(60 * fps_env / lags / 110) / 0.9) ** 2)
    k = int(lags[np.argmax(np.maximum(ac[lags], 0) * prior)])
    a_, b_, c_ = ac[k - 1], ac[k], ac[k + 1]
    period = k + 0.5 * (a_ - c_) / (a_ - 2 * b_ + c_ + 1e-12)          # in envelope frames
    bpm = 60 * fps_env / period
    # dynamic-programming beat tracking (Ellis 2007): onsets reward, deviation from the tempo penalised
    env = np.convolve(flux, np.exp(-0.5 * (np.arange(-int(period / 16) - 1, int(period / 16) + 2) / (period / 32)) ** 2), "same")
    window = np.arange(-int(round(2 * period)), -int(round(period / 2)) + 1)
    txwt = -100.0 * np.log(-window / period) ** 2
    score = np.zeros(len(env)); back = -np.ones(len(env), int)
    for i in range(len(env)):
        prev = i + window
        ok = prev >= 0
        if ok.any():
            cand = txwt[ok] + score[prev[ok]]
            j = int(np.argmax(cand)); score[i] = env[i] + cand[j]; back[i] = prev[ok][j]
        else:
            score[i] = env[i]
    # last beat: the best-scoring local maximum near the end, then backtrack
    tail = np.arange(max(0, len(score) - int(2 * period)), len(score))
    i = int(tail[np.argmax(score[tail])]); path = []
    while i >= 0:
        path.append(i); i = back[i]
    path = np.array(path[::-1])
    # phase check: very loud off-beat hats/snares can pull the grid half a beat off. Kicks/bass are mostly
    # low end, hats/snares are broadband, so compare the low-band *share* of the hits on vs. half-way
    # between the tracked beats; shift the grid by half a beat (re-snapped to onsets) if the kick is half-way
    half = int(round(period / 2)); r = max(1, int(period / 10))
    tot = bflux.sum(axis=1)
    pos_on = [p for p in path if p + half + r < len(low)]
    near = lambda a, pos: np.array([a[max(0, p - r):p + r + 1].max() for p in pos])
    low_on, low_off = near(low, pos_on), near(low, [p + half for p in pos_on])
    share_on = low_on / (near(tot, pos_on) + 1e-9)
    share_off = low_off / (near(tot, [p + half for p in pos_on]) + 1e-9)
    flipped = bool(len(pos_on) > 4 and low.sum() > 0.05 * tot.sum()       # the track has real low end
                   and low_off.mean() > 0.5 * low_on.mean()                # real hits half-way, not silence
                   and share_off.mean() > 1.5 * share_on.mean())           # and they're the low-heavy ones
    if flipped:
        path = np.array([p + half - r + int(np.argmax(env[max(0, p + half - r):p + half + r + 1]))
                         for p in path if p + half < len(env)])
    beats = [round(i / fps_env + t0, 3) for i in path]
    out = Path(a.out) if a.out else Path(a.file).with_suffix(".beats.json")
    out.write_text(json.dumps({"bpm": round(bpm, 1), "beats": beats}, indent=1), encoding="utf-8")
    print(f"~{bpm:.1f} BPM, {len(beats)} beats{' (phase moved to the kick/bass hits)' if flipped else ''} -> {out}")

# ------------------------------------------------------------------ grade presets
GRADES = {
    "none": "",
    "natural": ("eq=contrast=1.04,curves=master='0/0.03 0.5/0.5 0.85/0.845 1/0.96',"
                "vibrance=intensity=0.12,colorbalance=rm=0.015:bm=-0.015"),
    "golden": ("eq=contrast=1.04:saturation=1.06,curves=master='0/0.03 0.5/0.5 0.85/0.845 1/0.96',"
               "vibrance=intensity=0.10,colorbalance=rm=0.04:gm=0.01:bm=-0.04:rh=0.03:bh=-0.03"),
    "indoor": ("curves=master='0/0.03 0.5/0.52 1/0.96',colorbalance=rh=-0.05:bh=0.02:rm=-0.01,"
               "eq=saturation=0.96"),
    "film": ("curves=master='0/0.12 0.25/0.27 0.5/0.5 0.8/0.78 1/0.94',"
             "colorbalance=rs=-0.04:bs=0.05:rh=0.04:bh=-0.04,eq=saturation=0.92,noise=alls=5:allf=t"),
}
HDR_TO_SDR = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
              "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")

def card_mask(path, w, h, r=48):
    from PIL import Image, ImageDraw
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    m.save(path)

def atempo_chain(speed):
    parts, s = [], speed
    while s > 2.0: parts.append("atempo=2.0"); s /= 2.0
    while s < 0.5: parts.append("atempo=0.5"); s /= 0.5
    parts.append(f"atempo={s:.4f}")
    return ",".join(parts)

# ------------------------------------------------------------------ assemble
def build_segment(clip, i, proj, build, default_grade):
    src = (proj / clip["src"]).resolve()
    info = clip_info(src)
    t_in = float(clip.get("in", 0)); t_out = float(clip.get("out", info["duration"]))
    speed = float(clip.get("speed", 1.0)); punch = float(clip.get("punch", 1.0))
    frame = clip.get("frame", "fill"); rot = int(clip.get("rotate", 0))
    grade = clip.get("grade") or default_grade
    seg = build / f"seg_{i:03d}.mp4"
    dur_src = max(0.05, t_out - t_in)
    dur_out = dur_src / speed

    vf = []
    if info.get("hdr"):
        vf.append(HDR_TO_SDR)
    if speed != 1.0:                              # retime first so slow-mo keeps every source frame (60 fps -> 0.5x)
        vf.append(f"setpts=PTS/{speed}")
    vf.append(f"fps={FPS}")                       # then conform VFR / retimed footage to 30 fps CFR
    vf.append({90: "transpose=1", -90: "transpose=2", 270: "transpose=2", 180: "hflip,vflip"}.get(rot, "null"))
    if clip.get("wb") == "auto":
        vf.append("grayworld")
    if grade and GRADES.get(grade):
        vf.append(GRADES[grade])

    inputs = ["-ss", f"{t_in:.3f}", "-t", f"{dur_src:.3f}", "-i", str(src)]
    if frame == "fill":
        sw, sh = int(W * punch) // 2 * 2, int(H * punch) // 2 * 2
        vf.append(f"scale={sw}:{sh}:force_original_aspect_ratio=increase,crop={W}:{H}")
        fc = f"[0:v]{','.join(vf)},setsar=1,format=yuv420p[v]"
    elif frame in ("letterbox", "letterbox_wide"):
        crop = "crop=iw:min(ih\\,iw/2.0)," if frame == "letterbox_wide" else ""
        vf.append(f"{crop}scale={int(W*punch)//2*2}:-2,crop=min(iw\\,{W}):min(ih\\,{H}),pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black")
        fc = f"[0:v]{','.join(vf)},setsar=1,format=yuv420p[v]"
    elif frame == "blur":                          # horizontal clip over blurred fill
        fc = (f"[0:v]{','.join(vf)},split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
              f"gblur=sigma=40,eq=brightness=-0.08[bg];[b]scale={W}:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,format=yuv420p[v]")
    elif frame == "card":                          # rounded card on paper background (maps, screenshots)
        cw, ch = 920, 1500
        mask = build / "card_mask.png"
        if not mask.exists():
            card_mask(mask, cw, ch)
        inputs += ["-loop", "1", "-i", str(mask)]
        fc = (f"color=c={PAPER_RGB}:s={W}x{H}:r={FPS}[bg];"
              f"[0:v]{','.join(vf)},scale={cw}:{ch}:force_original_aspect_ratio=increase,crop={cw}:{ch},format=yuva420p[c];"
              f"[1:v]scale={cw}:{ch},format=gray[m];[c][m]alphamerge[cm];"
              f"[bg][cm]overlay=(W-w)/2:(H-h)/2-40:shortest=1,setsar=1,format=yuv420p[v]")
    else:
        raise SystemExit(f"unknown frame mode {frame}")

    # B-roll over this clip (L-cut): picture switches to the B-roll, this clip's voice keeps playing
    brolls = clip.get("broll", [])
    if brolls:
        fc = fc[: fc.rindex("[v]")] + "[v0]"
        n_in = inputs.count("-i")
        for k, b in enumerate(brolls):
            bsrc = (proj / b["src"]).resolve(); binfo = clip_info(bsrc)
            at, bd = float(b.get("at", 0)), float(b.get("dur", 1.2))
            inputs += ["-ss", f"{float(b.get('in', 0)):.3f}", "-t", f"{bd:.3f}", "-i", str(bsrc)]
            bvf = ([HDR_TO_SDR] if binfo.get("hdr") else []) + [f"fps={FPS}"]
            bg = b.get("grade") or grade
            if bg and GRADES.get(bg):
                bvf.append(GRADES[bg])
            bvf.append(f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,format=yuv420p")
            fc += (f";[{n_in + k}:v]{','.join(bvf)},setpts=PTS-STARTPTS+{at:.3f}/TB[b{k}]"
                   f";[v{k}][b{k}]overlay=enable='between(t,{at:.3f},{at + bd:.3f})':eof_action=pass[v{k + 1}]")
        fc += f";[v{len(brolls)}]null[v]"

    use_audio = clip.get("audio", True) and info["has_audio"]
    if use_audio:
        af = ["aresample=48000", "aformat=channel_layouts=stereo"]
        if speed != 1.0:
            af.append(atempo_chain(speed))
        af.append(f"volume={clip.get('gain_db', 0)}dB")
        fc += f";[0:a]{','.join(af)},apad[a]"
    else:
        fc += ";anullsrc=r=48000:cl=stereo[a]"
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
         "-t", f"{dur_out:.3f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "14",
         "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-ar", "48000", seg.with_suffix(".mov")])
    return seg.with_suffix(".mov"), dur_out

def assemble(edit, proj, build):
    segs = []
    print(f"assembling {len(edit['clips'])} clips")
    for i, clip in enumerate(edit["clips"]):
        path, d = build_segment(clip, i, proj, build, edit.get("grade", "natural"))
        segs.append((path, d, clip.get("transition", "cut"), float(clip.get("transition_dur", 0.25))))
        print(f"  seg {i:02d} {d:5.2f}s  {clip['src']}")
    inputs, fc, acc = [], [], 0.0
    for k, (p, *_) in enumerate(segs):
        inputs += ["-i", str(p)]
        # concat outputs AV_TIME_BASE; xfade needs both inputs on the same timebase
        fc.append(f"[{k}:v]settb=AVTB,setpts=PTS-STARTPTS[iv{k}];[{k}:a]asetpts=PTS-STARTPTS[ia{k}]")
    vl, al = "[iv0]", "[ia0]"; acc = segs[0][1]
    xmap = {"dissolve": "fade", "flash": "fadewhite", "whip": "slideleft", "whip_right": "slideright", "zoom": "zoomin"}
    for k in range(1, len(segs)):
        _, d, tr, td = segs[k]
        nv, na = f"[v{k}]", f"[a{k}]"
        if tr == "cut":
            fc.append(f"{vl}{al}[iv{k}][ia{k}]concat=n=2:v=1:a=1{nv}{na}")
            acc += d
        else:
            td = min(td, d / 2, acc / 2)
            fc.append(f"{vl}[iv{k}]xfade=transition={xmap.get(tr, 'fade')}:duration={td:.3f}:offset={acc - td:.3f}{nv}")
            fc.append(f"{al}[ia{k}]acrossfade=d={td:.3f}{na}")
            acc += d - td
        vl, al = nv, na
    out = build / "assembled.mov"
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc), "-map", vl, "-map", al,
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-pix_fmt", "yuv420p",
         "-c:a", "pcm_s16le", out])
    print(f"assembled {acc:.2f}s -> {out}")
    return out

# ------------------------------------------------------------------ captions (ASS)
STYLE_DEFAULTS = {  # style -> (max words/page, max chars/page)
    "serif": (5, 34), "sans": (3, 18), "karaoke": (4, 20), "caps": (4, 18), "top": (6, 30), "typewriter": (5, 28),
}

# libass font sizes, calibrated (pipeline/calibrate_type.py) so text occupies the same share of the frame
# width as in the reference reels. libass sizes by line height, so these look "big" as numbers.
SIZE = {
    "serif_key": 103, "serif_small": 60,        # iffy: "Pakistan-Occupied" = 59% width (fillers 58%)
    "sans_key": 128, "sans_small": 73,          # brinda orca: "Expensive" = 35% (fillers 57%)
    "karaoke": 115,                             # brinda 7.4M: "Trip pe Jaane se" = 50%
    "caps": 77,                                 # brinda Japan: "MAI HU ABHI AAJ" = 49%
    "top": 68, "top_accent": 86,                # brinda IndiGo: "I booked my flights" = 34%
    "mono": 49,                                 # sailing 21M: "we started sailing from" = 47%
    "chapter": 524, "script": 383,              # brinda Japan: "JAPAN" = 66%, "mein" = 33%
    "landmark": 169, "sub": 48,                 # iffy Chenab: "CHENAB RAIL BRIDGE" = 68%
    "place": 136,                               # sayannath: "KYRGYZSTAN" = 72%
    "pill": 81, "hook": 96, "fact": 78,         # sayannath / iffy
    "marker": 149,                              # iffy: "PoK Pakistan" = 49%
}

def fit(key, text, base_chars, base_frac, max_frac=0.76, grow=1.0):
    """scale a title down so `text` stays on one line inside the safe width (x 110..950 = 78%)"""
    n = max(1, len(text))
    return int(min(SIZE[key] * grow, SIZE[key] * (max_frac / base_frac) * (base_chars / n)))

def ass_header():
    sh = "&H8C000000&"   # 45% black shadow
    ol = "&HA0000000&"
    # margins keep auto-wrapped text inside the safe zone: x 110..950
    def s(name, role, size, col, italic=0, align=5, border=1, outline=1.2, shadow=3, back=sh, ocol=ol, sp=0):
        fam, bold = fnt(role)
        return (f"Style: {name},{fam},{size},{col},{col},{ocol},{back},{-1 if bold else 0},{italic},0,0,100,100,{sp},0,"
                f"{border},{outline},{shadow},{align},110,130,60,1")
    styles = [
        s("Serif", "serif", SIZE["serif_key"], C["chalk"], outline=1.5, shadow=4),
        s("Sans", "sans_semi", SIZE["karaoke"], C["chalk"], outline=1.5, shadow=4),
        s("Caps", "caps", SIZE["caps"], C["chalk"], sp=6, outline=1.0),
        s("Top", "sans_med", SIZE["top"], C["chalk"], align=8, outline=1.2),
        s("Mono", "mono", SIZE["mono"], C["chalk"], outline=1.0, shadow=3),
        s("Chapter", "condensed", SIZE["chapter"], C["sindoor"], outline=0, shadow=6),
        s("Script", "script", SIZE["script"], C["chalk"], outline=0, shadow=4),
        s("Landmark", "condensed", SIZE["landmark"], C["marigold"], outline=0, shadow=5),
        s("Sub", "caps", SIZE["sub"], C["chalk"], sp=2, outline=0.8),
        s("Place", "roman", SIZE["place"], C["chalk"], sp=8, outline=0, shadow=5),
        s("Pill", "serif_reg", SIZE["pill"], C["chalk"], border=3, outline=20, shadow=0, ocol=C["ink"].replace("&H", "&H00"), align=8),
        s("Marker", "marker", SIZE["marker"], C["chalk"], outline=0, shadow=3),
        s("Fact", "serif_reg", SIZE["fact"], C["marigold"], italic=-1, outline=1.2),
        s("Hook", "sans_bold", SIZE["hook"], C["chalk"], align=8, outline=2),
    ]
    return ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\n"
            "ScaledBorderAndShadow: yes\nYCbCr Matrix: TV.709\n\n[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
            "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
            "MarginR, MarginV, Encoding\n" + "\n".join(styles) +
            "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")

def ev(start, end, style, text, layer=0):
    return f"Dialogue: {layer},{ass_time(start)},{ass_time(end)},{style},,0,0,0,,{text}"

POP = r"\fad(40,0)\fscx92\fscy92\t(0,90,\fscx100\fscy100)"        # captions: pop in, hard swap out
POP_T = r"\fad(40,120)\fscx92\fscy92\t(0,90,\fscx100\fscy100)"    # titles: pop in, 120 ms fade out

def ass_color(v, default="chalk"):
    """brand token name or '#RRGGBB' -> ASS &HBBGGRR&"""
    if isinstance(v, str) and re.fullmatch(r"#?[0-9a-fA-F]{6}", v):
        h = v.lstrip("#").upper()
        return f"&H{h[4:6]}{h[2:4]}{h[0:2]}&"
    return C.get(v or default, C[default])

def paginate(words, style):
    maxw, maxc = STYLE_DEFAULTS[style]
    pages, cur = [], []
    for w in words:
        if cur:
            gap = w["start"] - cur[-1]["end"]
            chars = sum(len(x["text"]) + 1 for x in cur) + len(w["text"])
            if gap > 0.45 or len(cur) >= maxw or chars > maxc or re.search(r"[.?!,;:]$", cur[-1]["text"]):
                pages.append(cur); cur = []
        cur.append(w)
    if cur:
        pages.append(cur)
    # don't end a page on a dangling article/preposition ("than the | Eiffel Tower"): push it to the next page
    lead = {"the", "a", "an", "of", "to", "in", "on", "at", "for", "with", "my", "your", "ka", "ki", "ke", "ek"}
    for k in range(len(pages) - 1):
        while (len(pages[k]) > 1 and re.sub(r"\W", "", pages[k][-1]["text"]).lower() in lead
               and not re.search(r"[.?!,;:]$", pages[k][-1]["text"])
               and pages[k + 1][0]["start"] - pages[k][-1]["end"] < 0.45):
            pages[k + 1].insert(0, pages[k].pop())
    # never leave a lone filler word ("and", "hai") on its own page: glue it to the page before
    for k in range(len(pages) - 1, 0, -1):
        w = pages[k]
        if (len(w) == 1 and re.sub(r"\W", "", w[0]["text"]).lower() in STOP
                and w[0]["start"] - pages[k - 1][-1]["end"] < 0.45):
            pages[k - 1] += w
            del pages[k]
    return pages

def pick_emphasis(page):
    if any(w.get("emph") for w in page):
        return {i for i, w in enumerate(page) if w.get("emph")}
    cands = [(len(re.sub(r"\W", "", w["text"])), i) for i, w in enumerate(page)
             if re.sub(r"\W", "", w["text"]).lower() not in STOP]
    if not cands:
        return {max(range(len(page)), key=lambda i: len(page[i]["text"]))}
    cands.sort(reverse=True)
    pick = {cands[0][1]}
    if len(page) >= 4 and len(cands) > 1 and cands[1][0] >= 5:
        pick.add(cands[1][1])
    return pick

def caption_events(words, style, y=None):
    evs = []
    pages = paginate(words, style)
    for pi, page in enumerate(pages):
        start = page[0]["start"]
        nxt = pages[pi + 1][0]["start"] if pi + 1 < len(pages) else page[-1]["end"] + 0.5
        end = min(nxt, page[-1]["end"] + 0.7)
        emph = pick_emphasis(page)
        if style == "serif":                          # inline: small marigold fillers, big white key word(s)
            body = []
            for i, w in enumerate(page):
                t = ass_escape(w["text"])
                if i in emph:
                    body.append(f"{{\\fs{SIZE['serif_key']}\\1c{C['chalk']}}}{t} ")
                else:
                    body.append(f"{{\\fs{SIZE['serif_small']}\\1c{C['marigold']}}}{t} ")
            evs.append(ev(start, end, "Serif", f"{{\\an5\\pos(540,{y or 1300}){POP}}}" + "".join(body).rstrip()))
        elif style == "sans":                         # stacked, left aligned, key word big marigold
            lines = []
            for i, w in enumerate(page):
                t = ass_escape(w["text"])
                if i in emph:
                    lines.append(f"{{{fn_tag('sans_xbold')}\\fs{SIZE['sans_key']}\\1c{C['marigold']}}}{t}")
                else:
                    lines.append(f"{{{fn_tag('sans_light')}\\fs{SIZE['sans_small']}\\1c{C['ivory']}}}{t}")
            evs.append(ev(start, end, "Sans", f"{{\\an4\\pos(120,{y or 1150}){POP}}}" + r"\N".join(lines)))
        elif style == "karaoke":                      # whole page visible, grey -> white as each word is spoken
            body = []
            for w in page:
                dt = int((w["start"] - start) * 1000)
                body.append(f"{{\\1c{C['grey']}\\alpha&H30&\\t({dt},{dt + 1},\\1c{C['chalk']}\\alpha&H00&)}}{ass_escape(w['text'])} ")
            evs.append(ev(start, end, "Sans", f"{{\\an5\\pos(540,{y or 1340})\\fad(40,0)}}" + "".join(body).rstrip()))
        elif style == "caps":
            txt = " ".join(ass_escape(w["text"]).upper() for w in page)
            evs.append(ev(start, end, "Caps", f"{{\\an5\\pos(540,{y or 1400}){POP}}}{txt}"))
        elif style == "top":
            body = []
            for i, w in enumerate(page):
                t = ass_escape(w["text"])
                if i in emph:
                    body.append(f"{{{fn_tag('serif_it')}\\i1\\fs{SIZE['top_accent']}\\1c{C['marigold']}}}{t}"
                                f"{{{fn_tag('sans_med')}\\i0\\fs{SIZE['top']}\\1c{C['chalk']}}} ")
                else:
                    body.append(t + " ")
            evs.append(ev(start, end, "Top", f"{{\\an8\\pos(540,{y or 300}){POP}}}" + "".join(body).rstrip()))
        elif style == "typewriter":
            body = []
            for w in page:
                dt = int((w["start"] - start) * 1000)
                body.append(f"{{\\alpha&HFF&\\t({dt},{dt + 1},\\alpha&H00&)}}{ass_escape(w['text']).lower()} ")
            evs.append(ev(start, end, "Mono", f"{{\\an5\\pos(540,{y or 1380})}}" + "".join(body).rstrip()))
        else:
            raise SystemExit(f"unknown caption style {style}")
    return evs

def title_events(titles, top_captions=False):
    """top_captions: the reel uses `top` captions (y 300), so top-anchored titles move down out of their way"""
    evs = []
    bump = 300 if top_captions else 0
    for t in titles:
        s, e = float(t["start"]), float(t["end"])
        typ = t["type"]
        txt_up = ass_escape(t.get("text", "")).upper()
        if typ == "chapter":
            y = t.get("y", 370 + bump); col = ass_color(t.get("color"), "sindoor")
            fs = fit("chapter", txt_up, 5, 0.66)
            evs.append(ev(s, e, "Chapter", f"{{\\an5\\pos(540,{y})\\fs{fs}\\1c{col}{POP_T}}}{txt_up}", 2))
            if t.get("script"):
                sfs = int(SIZE["script"] * min(1.0, fs / SIZE["chapter"]))
                evs.append(ev(s + 0.12, e, "Script", f"{{\\an5\\pos(540,{y + int(fs * 0.24)})\\fs{sfs}"
                                                     f"\\1c{ass_color(t.get('script_color'), 'chalk')}{POP_T}}}"
                                                     f"{ass_escape(t['script'])}", 3))
        elif typ == "landmark":
            y = t.get("y", 280 + bump)
            fs = fit("landmark", txt_up, 18, 0.68)
            evs.append(ev(s, e, "Landmark", f"{{\\an5\\pos(540,{y})\\fs{fs}\\fax-0.12"
                                            f"\\1c{ass_color(t.get('color'), 'marigold')}{POP_T}}}{txt_up}", 2))
            if t.get("sub"):
                evs.append(ev(s + 0.15, e, "Sub", f"{{\\an5\\pos(540,{y + int(fs * 0.30) + 42})\\fad(120,120)}}"
                                                  f"{ass_escape(t['sub']).upper()}", 2))
        elif typ == "place":
            fs = fit("place", txt_up, 10, 0.72)
            evs.append(ev(s, e, "Place", f"{{\\an5\\pos(540,{t.get('y', 960)})\\fs{fs}\\fad(250,250)}}{txt_up}", 2))
        elif typ == "pill":                       # *word* -> sindoor keyword
            txt = re.sub(r"\*(.+?)\*", lambda m: f"{{\\1c{C['sindoor']}}}{m.group(1)}{{\\1c{C['chalk']}}}", ass_escape(t["text"]))
            evs.append(ev(s, e, "Pill", f"{{\\an8\\pos(540,{t.get('y', 300 + bump)})\\fad(80,80)}}{txt}", 4))
        elif typ == "hook":
            evs.append(ev(s, e, "Hook", f"{{\\an8\\pos(540,{t.get('y', 260 + bump)})\\fad(60,100)}}{ass_escape(t['text'])}", 4))
        elif typ == "fact":                       # sits just above the caption band so both can be on screen
            evs.append(ev(s, e, "Fact", f"{{\\an5\\pos(540,{t.get('y', 1090)})\\1c{ass_color(t.get('color'), 'marigold')}"
                                        f"{POP_T}}}{ass_escape(t['text'])}", 2))
        elif typ == "marker":                     # handwritten write-on, optional strike-through
            size = t.get("size", SIZE["marker"]); x, y = t.get("x", 540), t.get("y", 330 + bump)
            col = ass_color(t.get("color"), "chalk")
            lines = t["text"].split("\n")
            wpx = max(len(l) * size * 0.30 for l in lines); hpx = size * 0.8 * len(lines)
            x1, x2 = int(x - wpx / 2 - 40), int(x + wpx / 2 + 40); y1, y2 = int(y - hpx / 2 - 60), int(y + hpx / 2 + 60)
            dur = int(t.get("write_ms", 450))
            strike = r"\s1" if t.get("strike") else ""
            txt = r"\N".join(ass_escape(l) for l in lines)
            evs.append(ev(s, e, "Marker", f"{{\\an5\\pos({x},{y})\\fs{size}\\1c{col}\\frz{t.get('rotate', -3)}{strike}"
                                          f"\\clip({x1},{y1},{x1},{y2})\\t(0,{dur},\\clip({x1},{y1},{x2},{y2}))\\fad(0,120)}}{txt}", 5))
        else:
            raise SystemExit(f"unknown title type {typ}")
    return evs

def write_ass(path, words, cap_cfg, titles):
    evs = []
    style = cap_cfg.get("style", "serif")
    if words and cap_cfg.get("enabled", True):
        evs += caption_events(words, style, cap_cfg.get("y"))
    evs += title_events(titles or [], top_captions=bool(words) and cap_cfg.get("enabled", True) and style == "top")
    Path(path).write_text(ass_header() + "\n".join(evs) + "\n", encoding="utf-8")

def write_srt(path, words):
    pages = paginate(words, "top")
    lines = []
    for i, p in enumerate(pages, 1):
        lines += [str(i), f"{srt_time(p[0]['start'])} --> {srt_time(p[-1]['end'])}", " ".join(w["text"] for w in p), ""]
    Path(path).write_text("\n".join(lines), encoding="utf-8")

# ------------------------------------------------------------------ finish (audio mix + burn-in)
def loudnorm_measure(wav):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(wav), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    return json.loads(m.group(0)) if m else None

def finish(edit, proj, build, assembled):
    name = edit.get("name", proj.name)
    out_dir = proj / "out"; out_dir.mkdir(exist_ok=True)
    dur = clip_info(assembled)["duration"]

    # 1) audio mix: voice chain + music bed with sidechain ducking
    mix = build / "mix.wav"
    voice = ("highpass=f=80,afftdn=nf=-25,acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=2"
             if edit.get("voice", {}).get("clean", True) else "anull")
    m = edit.get("music")
    if m and m.get("src"):
        msrc = (proj / m["src"]).resolve()
        fc = (f"[0:a]{voice},asplit=2[v][vsc];"
              f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={m.get('gain_db', -16)}dB[mus];")
        if m.get("duck", True):
            fc += "[mus][vsc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=250:makeup=1[mduck];"
        else:
            fc += "[vsc]anullsink;[mus]anull[mduck];"
        fc += f"[v][mduck]amix=inputs=2:duration=first:normalize=0,afade=t=out:st={max(0, dur - 0.6):.2f}:d=0.6[out]"
        run(["ffmpeg", "-y", "-v", "error", "-i", assembled, "-ss", str(m.get("start", 0)), "-stream_loop", "-1", "-i", msrc,
             "-filter_complex", fc, "-map", "[out]", "-t", f"{dur:.3f}", "-c:a", "pcm_s16le", mix])
    else:
        run(["ffmpeg", "-y", "-v", "error", "-i", assembled, "-af", voice, "-vn", "-c:a", "pcm_s16le", mix])
    meas = loudnorm_measure(mix)
    if meas and meas.get("input_i") not in (None, "-inf"):
        ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={meas['input_i']}:measured_TP={meas['input_tp']}:"
              f"measured_LRA={meas['input_lra']}:measured_thresh={meas['input_thresh']}:offset={meas['target_offset']}:linear=true")
    else:
        ln = "anull"   # silent track

    # 2) subtitles file
    words_path = edit.get("captions", {}).get("words")
    words = clean_words(json.loads((proj / words_path).read_text(encoding="utf-8"))) \
        if words_path and (proj / words_path).exists() else []
    cap = edit.get("captions", {})
    if cap.get("enabled", True) and cap.get("style") and not words:
        print(f"! captions enabled but no words file ({words_path}). Run: isha.py transcribe {build / 'assembled.mov'} "
              f"--out {proj / (words_path or 'words.json')}  — rendering without captions.")
    ass = build / "subs.ass"
    write_ass(ass, words, cap, edit.get("titles", []))
    if words:
        write_srt(out_dir / f"{name}.srt", words)

    fonts_rel = ff_path(FONTS, build)
    enc = ["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-x264-params", "colorprim=bt709:transfer=bt709:colormatrix=bt709",
           "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", "-r", str(FPS)]
    final = out_dir / f"{name}.mp4"; clean = out_dir / f"{name}_clean.mp4"
    tag = "setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv,format=yuv420p"
    run(["ffmpeg", "-y", "-v", "error", "-i", assembled.name, "-i", mix.name, "-map", "0:v", "-map", "1:a",
         "-vf", f"ass=subs.ass:fontsdir={fonts_rel},{tag}", "-af", ln, *enc, os.path.relpath(final, build)], cwd=build)
    run(["ffmpeg", "-y", "-v", "error", "-i", assembled.name, "-i", mix.name, "-map", "0:v", "-map", "1:a",
         "-vf", tag, "-af", ln, *enc, os.path.relpath(clean, build)], cwd=build)
    # cover: first chapter/place title frame, else 1s
    tt = next((t for t in edit.get("titles", []) if t["type"] in ("chapter", "landmark", "place")), None)
    ct = (float(tt["start"]) + 0.4) if tt else min(1.0, dur / 2)
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{ct:.2f}", "-i", final, "-frames:v", "1", out_dir / f"{name}_cover.png"])
    print(f"done:\n  {final}\n  {clean}\n  {out_dir / (name + '_cover.png')}")
    return final

def cmd_render(a):
    edit_path = Path(a.edit).resolve(); proj = edit_path.parent
    edit = json.loads(edit_path.read_text(encoding="utf-8"))
    build = proj / "build"; build.mkdir(exist_ok=True)
    assembled = build / "assembled.mov"
    if a.stage in ("all", "assemble") or not assembled.exists():
        assembled = assemble(edit, proj, build)
        make_sheet(assembled, build / "assembled_sheet.png", n=24, cols=12)
    if a.stage in ("all", "finish"):
        final = finish(edit, proj, build, assembled)
        if not a.no_qa:
            qa(final, edit.get("format"))

# ------------------------------------------------------------------ QA
# format -> (min length s, max length s, min avg shot s, max avg shot s), from ISHA_REEL_SYSTEM.md §1
FORMAT_TARGETS = {"A": (35, 75, 1.5, 2.5), "B": (40, 60, 1.1, 2.0), "C": (12, 35, 0.8, 1.5), "D": (10, 25, 1.5, 25)}

def qa(path, fmt=None):
    i = clip_info(path)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    I = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr); TP = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
    r2 = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-vf", "scdet=threshold=12", "-an", "-f", "null", "-"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    cuts = re.findall(r"lavfi\.scd\.time:\s*([\d.]+)", r2.stderr)
    nshots = len(cuts) + 1
    j = ffprobe(path); v = next(s for s in j["streams"] if s["codec_type"] == "video")
    checks = [
        ("resolution 1080x1920", (i.get("width"), i.get("height")) == (W, H)),
        ("30 fps CFR", abs(i.get("fps", 0) - FPS) < 0.01 and not i.get("vfr")),
        ("BT.709 tagged", v.get("color_primaries") == "bt709" and v.get("color_transfer") == "bt709"),
        (f"loudness {I[-1] if I else '?'} LUFS (target -14±1)", bool(I) and abs(float(I[-1]) + 14) <= 1.0),
        (f"true peak {TP[-1] if TP else '?'} dBFS (<= -1.0)", bool(TP) and float(TP[-1]) <= -1.0),
        (f"first cut at {float(cuts[0]):.2f}s (<= 2.5s)" if cuts else "no cuts detected", bool(cuts) and float(cuts[0]) <= 2.5),
    ]
    if fmt in FORMAT_TARGETS:
        lo, hi, slo, shi = FORMAT_TARGETS[fmt]; avg = i["duration"] / nshots
        checks += [(f"length {i['duration']:.0f}s (format {fmt}: {lo}-{hi}s)", lo <= i["duration"] <= hi),
                   (f"avg shot {avg:.2f}s (format {fmt}: {slo}-{shi}s)", slo <= avg <= shi)]
    print(f"\nQA {Path(path).name}: {i['duration']:.1f}s, {nshots} shots, avg shot {i['duration'] / nshots:.2f}s")
    for label, ok in checks:
        print(f"  [{'x' if ok else ' '}] {label}")
    sheet = make_sheet(path, str(Path(path).with_suffix("")) + "_qa_sheet.png", n=24, cols=12)
    print(f"  sheet: {sheet}")

def cmd_qa(a):
    qa(a.file, a.format)

# ------------------------------------------------------------------ main
def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("probe"); s.add_argument("files", nargs="+"); s.add_argument("--json", action="store_true"); s.set_defaults(f=cmd_probe)
    s = sp.add_parser("sheet"); s.add_argument("file"); s.add_argument("--n", type=int, default=16); s.add_argument("--times"); s.add_argument("--out"); s.set_defaults(f=cmd_sheet)
    s = sp.add_parser("transcribe"); s.add_argument("file"); s.add_argument("--model"); s.add_argument("--lang", default="en")
    s.add_argument("--max-len", dest="max_len", type=int, default=1); s.add_argument("--vad"); s.add_argument("--out"); s.set_defaults(f=cmd_transcribe)
    s = sp.add_parser("beats"); s.add_argument("file"); s.add_argument("--out"); s.set_defaults(f=cmd_beats)
    s = sp.add_parser("render"); s.add_argument("edit"); s.add_argument("--stage", choices=["all", "assemble", "finish"], default="all")
    s.add_argument("--no-qa", action="store_true"); s.set_defaults(f=cmd_render)
    s = sp.add_parser("qa"); s.add_argument("file"); s.add_argument("--format", choices=list(FORMAT_TARGETS)); s.set_defaults(f=cmd_qa)
    a = p.parse_args(); a.f(a)

if __name__ == "__main__":
    main()
