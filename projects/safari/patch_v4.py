"""v4 patch for make.py (2026-11-04). Client: "split layout pictures can be better aligned", "the whole reel can be
much better", "needs more sound effects". Run once: python patch_v4.py"""
from pathlib import Path

p = Path(__file__).with_name("make.py")
s = p.read_text(encoding="utf-8")

def rep(a, b):
    global s
    assert a in s, "MISSING: " + a[:100]
    s = s.replace(a, b)

# ---------------------------------------------------------------- split framing (50/50, face-tracked, hand-framed)
rep('''SEAM, HER_ROW0 = 840, 240
SPLIT = [   # (t0, t1, image or "LOGO", fx, fy, z0, z1)
    (T(8.08), T(10.06), "sal_forest.jpg", 0.50, 0.50, 1.00, 1.07),
    (T(10.06), T(12.78), "chital_fawn.jpg", 0.45, 0.17, 1.00, 1.04),
    (T(19.77), T(20.13), "leopard.jpg", 0.42, 0.45, 1.10, 1.13),
    (T(20.13), T(20.50), "elephant.jpg", 0.56, 0.40, 1.00, 1.03),
    (T(20.50), T(20.93), "sloth_bear.jpg", 0.33, 0.45, 1.25, 1.28),
    (T(20.93), T(21.43), "peacock.jpg", 0.45, 0.30, 1.00, 1.03),
    (T(21.43), T(22.55), "tiger_yawn.jpg", 0.52, 0.50, 1.00, 1.06),''',
'''# v4 split: a true 50/50 like ref 1; every photo framed by hand on its subject (grid-checked, full-res originals);
# her half FACE-TRACKED at 1.0x so she always sits the same way (forehead ~0.24 face-heights under the seam).
SEAM = 960
SPLIT = [   # (t0, t1, image or "LOGO", fx, fy, z0, z1)
    (T(8.08), T(10.06), "sal_forest.jpg", 0.50, 0.55, 1.00, 1.06),     # road vanishing point centred
    (T(10.06), T(12.78), "chital_fawn.jpg", 0.50, 0.375, 1.00, 1.04),  # whole head, both ears
    (T(19.77), T(20.13), "leopard.jpg", 0.50, 0.50, 1.45, 1.50),       # leopard fills the middle
    (T(20.13), T(20.50), "elephant.jpg", 0.54, 0.47, 1.30, 1.34),
    (T(20.50), T(20.93), "sloth_bear.jpg", 0.36, 0.33, 1.70, 1.76),
    (T(20.93), T(21.43), "peacock.jpg", 0.35, 0.45, 1.15, 1.19),       # bird on the left third, tail falling right
    (T(21.43), T(22.55), "tiger_yawn.jpg", 0.50, 0.50, 1.00, 1.05),''')

rep('''def in_split(t):
    return any(a <= t < b for a, b, *_ in SPLIT)
''', '''def in_split(t):
    return any(a <= t < b for a, b, *_ in SPLIT)

EXIT_T = 0.25
def split_exit(t):
    """(split entry, progress) while a split pushes back out to full frame, else None"""
    for sp in SPLIT:
        b = sp[1]
        if b <= t < b + EXIT_T and not in_split(b + 0.001) and not any(f[0] <= b + 0.001 < f[1] for f in FULL):
            return sp, (t - b) / EXIT_T
    return None

def _her_rows():
    """per-frame top row of her half (1080 scale, zoom 1.0): forehead 0.24 face-heights below the seam, smoothed"""
    faces = json.loads((B / "faces.json").read_text())
    tops = np.full(len(faces), np.nan)
    for i, f in enumerate(faces):
        if f:
            x, y, w, h = f[0]
            tops[i] = y - 0.24 * h
    idx = np.arange(len(tops)); ok = ~np.isnan(tops)
    tops = np.interp(idx, idx[ok], tops[ok])
    from scipy.ndimage import median_filter, uniform_filter1d
    tops = uniform_filter1d(median_filter(tops, 21, mode="nearest"), 15, mode="nearest")
    return np.clip(tops, 0, SEAM).astype(int)
HER_ROWS = _her_rows()

def her_row(t):
    return int(HER_ROWS[min(len(HER_ROWS) - 1, max(0, int(round(t * FPS))))])
''')

rep('''    i = shot_index(t)
    a, b = SHOTS[i], SHOTS[min(i + 1, len(SHOTS) - 1)]''', '''    if in_split(t) or split_exit(t):
        return 1.0                                          # split: her half is face-tracked at 1.0x
    i = shot_index(t)
    a, b = SHOTS[i], SHOTS[min(i + 1, len(SHOTS) - 1)]''')

a = s.index("        # ---- ref 1 split screen")
b = s.index("        # ---- ref 1 full-screen beats")
s = s[:a] + '''        # ---- ref 1 split screen (photo top half, her bottom half; push-down in, push-up out, film-strip montage)
        def split_top(k, t):
            t0, t1, img, fx, fy, z0, z1 = splits[k]
            zz = z0 + (z1 - z0) * min(1, max(0, (t - t0) / (t1 - t0)))
            for bk in BARKS:                                            # snap-zoom on each bark
                if t0 <= bk <= t < bk + 0.6:
                    zz *= 1 + 0.07 * expo_out((t - bk) / 0.12) * (1 - 0.6 * min(1, (t - bk - 0.12) / 0.45) if t > bk + 0.12 else 1)
            if img is None:
                top = logo_bg.copy()
                al = expo_out((t - t0) / 0.4)
                lr = cv2.resize(logo_rgba, None, fx=0.95 + 0.05 * al, fy=0.95 + 0.05 * al, interpolation=cv2.INTER_AREA)
                blend_rgba(top, lr, logo_xy[0] + logo_img.width / 2, logo_xy[1] + logo_img.height / 2, 1.0, al)
                return top
            top = crop_cover(img, 1080, SEAM, fx, fy, zz)
            if SILENT <= t < T(10.06):
                kk = expo_out((t - SILENT) / 0.6)
                top = desat(top, 1 - 0.45 * kk, 1 - 0.08 * kk)
            return (top.astype(np.float32) * PANEL_SHADE).astype(np.uint8)

        def compose(frame, top, row0, p):
            """p = 1: full split. 0 < p < 1: mid-push (photo slides down from the top, she slides down with it)"""
            if p >= 1:
                return np.vstack([top, frame[row0:row0 + 1920 - SEAM]])
            out = frame.copy()
            shift = int(round((SEAM - row0) * p))
            if shift > 0:
                out[shift:] = frame[:1920 - shift]
            h = int(round(SEAM * p))
            if h > 0:
                out[:h] = top[SEAM - h:]
            return out

        for k, (t0, t1, img, fx, fy, z0, z1) in enumerate(splits):
            if t0 <= t < t1:
                top = split_top(k, t)
                prev = k - 1 if k > 0 and abs(splits[k - 1][1] - t0) < 0.02 else None
                if prev is not None and k in MONTAGE and prev in MONTAGE and t - t0 < 0.2:
                    q = expo_out((t - t0) / 0.2)                          # film-strip slide between photos
                    old = split_top(prev, t0 - 0.001)
                    off = int(round(1080 * (1 - q)))
                    top = np.hstack([old, top])[:, 1080 - off:2160 - off]
                p = expo_out((t - t0) / 0.3) if (t0 in entering and t - t0 < 0.3) else 1.0
                frame = compose(frame, top, her_row(t), p)
        ex = split_exit(t)
        if ex:
            sp, q = ex
            kx = SPLIT.index(sp)
            frame = compose(frame, split_top(kx, sp[1] - 0.001), her_row(t), 1 - expo_out(q))
''' + s[b:]

rep('''    split_starts = [s[0] for s in splits]''', '''    MONTAGE = set(range(2, 7))''')
rep('''_rng = np.random.default_rng(3)''', '''PANEL_SHADE = (1 - 0.5 * np.clip((np.linspace(0, 1, SEAM) - 0.66) / 0.34, 0, 1) ** 1.6)[:, None, None].astype(np.float32)
_rng = np.random.default_rng(3)''')
rep('''    if in_split(t + 0.01):
        return SEAM                         # ref 1: on the seam''', '''    if in_split(t + 0.01):
        return SEAM - 92                    # ref 1: on the bottom of the photo, just above the seam''')
rep('''                if in_split(t):        # her picture slides down into the lower panel
                    fy0, fy1 = max(SEAM, fy0 + SEAM - HER_ROW0), min(1920, fy1 + SEAM - HER_ROW0)''',
    '''                if in_split(t):        # her picture slides down into the lower panel
                    r0 = her_row(t)
                    fy0, fy1 = max(SEAM, fy0 + SEAM - r0), min(1920, fy1 + SEAM - r0)''')

# ---------------------------------------------------------------- cold open (ref 1): full-screen tiger under the hook
rep('''FULL = [
    (T(12.78), T(14.05), "tiger_trail_jeep.jpg", 0.42, 0.62, 1.00, 1.10, None),   # HERO: "it's right there"''',
    '''FULL = [
    (0.0, T(1.14), "tiger_trees.jpg", 0.50, 0.45, 1.12, 1.00, None),              # cold open: "You don't need to be a"
    (T(12.78), T(14.05), "tiger_trail_jeep.jpg", 0.42, 0.62, 1.00, 1.10, None),   # HERO: "it's right there"''')
rep('''    (T(2.40), T(3.20), "tiger_trees.jpg", 0.50, 0.42, 1.25, None, None, 0),''',
    '''    (T(2.40), T(3.20), "tiger_road.jpg", 0.53, 0.50, 2.0, None, None, 0),''')
# full-screen zoom: allow pull-backs (z0 > z1) with the same expo curve
rep('''                zz = z0 + (z1 - z0) * expo_out((t - t0) / (t1 - t0) * 0.8)
                frame = crop_cover(img, 1080, 1920, fx, fy, zz)''',
    '''                zz = z0 + (z1 - z0) * expo_out((t - t0) / (t1 - t0) * 0.8)
                frame = crop_cover(img, 1080, 1920, fx, fy, zz)
                if abs(t0 - T(12.78)) < 1e-6:                               # THE reveal: 2-frame flash + short shake
                    d = t - t0
                    if d < 0.35:
                        amp = 14 * (1 - d / 0.35) ** 2
                        dx, dy = amp * np.sin(d * 97), amp * np.cos(d * 71)
                        frame = cv2.warpAffine(frame, np.float32([[1.03, 0, -16 + dx], [0, 1.03, -29 + dy]]), (1080, 1920),
                                               borderMode=cv2.BORDER_REFLECT)
                    if d < 2 / FPS:
                        frame = np.clip(frame.astype(np.float32) * 0.4 + 255 * 0.6, 0, 255).astype(np.uint8)''')
# heartbeat: edges darken with each beat
rep('''        frame = texture(frame, fi, scrim)''', '''        frame = texture(frame, fi, scrim)
        for hb in HEARTBEATS:                                               # "heart will POUND": edges throb
            d = t - hb
            if 0 <= d < 0.5:
                k = np.sin(np.pi * min(1, d / 0.07) / 2) * np.exp(-max(0, d - 0.07) * 7)
                frame = (frame.astype(np.float32) * (1 - (1 - HB_VIG) * k)[..., None]).astype(np.uint8)''')
rep('''_rng = np.random.default_rng(3)''', '''HB_VIG = (1 - 0.42 * np.clip(_xx ** 2 + ((_yy - 0.45) * 1.6) ** 2 - 0.25, 0, 1.2) / 1.2).astype(np.float32)
_rng = np.random.default_rng(3)''')

# ---------------------------------------------------------------- stacked editorial captions (ref 1 hierarchy)
rep('''def line_events(words, t_from, t_to, y, scale, reveal=True, layer0=1, x=540, align=5, extra=""):''',
    '''def line_events(words, t_from, t_to, y, scale, reveal=True, layer0=1, x=540, align=5, extra="", kw_fs=None):''')
rep('''                fs = (KW_FS if w["kw"] else CAP_FS) * scale''', '''                fs = ((kw_fs or KW_FS) if w["kw"] else CAP_FS) * scale''')
rep('''            words = pg["words"]
            sc = min(1.0, MAX_W / text_width(words, 1.0))
            cuts = [pg["t0"]] + [e for e in edges if pg["t0"] < e < pg["t1"]] + [pg["t1"]]
            for j, (a, b) in enumerate(zip(cuts, cuts[1:])):   # re-seat the line when the layout changes
                if b - a > 0.02:
                    ev += line_events(words, a, b, caption_y(a), sc, reveal=True)''',
    '''            words = pg["words"]
            lines = stack_lines(words)
            cuts = [pg["t0"]] + [e for e in edges if pg["t0"] < e < pg["t1"]] + [pg["t1"]]
            for j, (a, b) in enumerate(zip(cuts, cuts[1:])):   # re-seat the block when the layout changes
                if b - a > 0.02:
                    y = caption_y(a)
                    if len(lines) == 1:
                        sc = min(1.0, MAX_W / text_width(words, 1.0))
                        ev += line_events(words, a, b, y, sc, reveal=True)
                    else:
                        (l1, big1), (l2, big2) = lines
                        y1, y2 = (y - 64, y + 20) if big2 else (y - 34, y + 58)
                        for ln, yy in ((l1, y1), (l2, y2)):
                            sc = min(1.0, MAX_W / text_width(ln, 1.0, STACK_KW))
                            ev += line_events(ln, a, b, yy, sc, reveal=True, kw_fs=STACK_KW)''')
rep('''def text_width(words, scale):
    tot = 0
    for j, w in enumerate(words):
        f = pil_font(FONT_FILE, int((KW_FS if w["kw"] else CAP_FS) * EM * scale))''',
    '''STACK_KW = 112
def stack_lines(words):
    """ref-1 hierarchy: a page with a keyword becomes 2 lines - lead-in small, keyword(s) big (or keyword then tail)"""
    kws = [i for i, w in enumerate(words) if w["kw"]]
    if not kws or len(words) == 1 or all(w["kw"] for w in words):
        return [(words, False)]
    i = kws[0]
    if i > 0:
        return [(words[:i], False), (words[i:], True)]
    j = next(k for k, w in enumerate(words) if not w["kw"])
    return [(words[:j], True), (words[j:], False)]

def text_width(words, scale, kw_fs=None):
    tot = 0
    for j, w in enumerate(words):
        f = pil_font(FONT_FILE, int(((kw_fs or KW_FS) if w["kw"] else CAP_FS) * EM * scale))''')

p.write_text(s, encoding="utf-8")
print("patched")
