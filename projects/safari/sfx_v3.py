def build_sfx():
    """v3 (client: "add the sound effects, rn it doesnt have those effects"): every visual move gets its own sound,
    mixed to be heard like the refs. Whoosh = layout change, pop = card/text in, tick = chapter number,
    shutter = photo, riser + impact = THE tiger reveal, reverse swell -> dead silence on "silent"."""
    b = np.zeros((NS, 2), np.float32)
    amb = np.zeros((NS, 2), np.float32)
    W1, SW, SC, SS = DS + "1491-preview.mp3", DL + "sweep_fast_small.mp3", DL + "swoosh_cinematic_wind.mp3", DL + "swoosh_short_wind.mp3"
    TICK, PL = DL + "click_interface_tone.mp3", DL + "pop_long.mp3"

    def whoosh(t, g=-12, kind=W1, pan=0.0):
        place(b, kind, 0.0, 1.2, t, g, align="peak", fout=0.25, pan=pan)

    def pop(t, g=-13, kind=POP):
        place(b, kind, 0.0, 0.45 if kind == POP else 0.4, t + 0.01, g, fin=0.002, fout=0.12)

    def tick(t, g=-15):
        place(b, TICK, 0.0, 0.2, t, g, fin=0.001, fout=0.06)

    # hook: she swings in + the title lands on frame 1
    whoosh(0.12, -11, SS); pop(0.0, -15, PL)
    # "to see a TIGER": first card rises in, drops out on her jump cut
    whoosh(T(2.40) + 0.08, -13); pop(T(2.40), -12)
    whoosh(T(3.20) + 0.05, -20, SS)
    tick(T(3.28), -14)                                                   # ALL YOU NEED
    # the list: card rises, then each next card swipes the last one out
    whoosh(T(4.12) + 0.08, -13); pop(T(4.12), -12)
    place(b, DS + "2712-preview.mp3", 0.9, 1.85, T(4.12) + 0.05, -19, fin=0.05, fout=0.35, pan=0.2)   # gypsy engine
    for t0, pan in ((T(4.76), 0.3), (T(5.52), -0.3)):
        whoosh(t0 + 0.06, -11, SW, pan); pop(t0 + 0.04, -15)
    place(b, DS + "peacock_call.ogg", 1.15, 2.35, T(5.70), -15, fin=0.02, fout=0.4, pan=-0.35)
    whoosh(T(6.93) + 0.05, -18, SS)                                      # list cards drop away
    # jungle at dawn under the list, gone on "silent"
    place(amb, DS + "2434-preview.mp3", 6.6, 6.6 + (SILENT - T(4.76)) + 0.05, T(4.76), -15, fin=0.6, fout=0.08, norm=False)
    # 04 the silence: split pushes down, number ticks in
    whoosh(T(8.08) + 0.12, -10, SC); tick(T(8.09), -14)
    # reverse swell that gets sucked into nothing exactly on "silent"
    rev = load(DL + "impact_reverse.mp3")
    pk = int(0.44 * SR)
    seg = rev[max(0, pk - int(0.9 * SR)):pk].copy()
    seg /= np.abs(seg).max() + 1e-9
    seg *= np.linspace(0, 1, len(seg))[:, None] ** 1.5 * 10 ** (-12 / 20)
    i1 = int(SILENT * SR); i0 = i1 - len(seg)
    b[i0:i1] += seg
    # 05 the alarm call
    whoosh(T(10.06) + 0.05, -13, SW); tick(T(10.07), -14)
    place(b, DS + "barking_deer_alarm.wav", 2.95, 3.75, BARKS[0], -5, align="peak", fin=0.01, fout=0.35, pan=-0.15)
    place(b, DS + "barking_deer_alarm.wav", 8.45, 9.25, BARKS[1], -8, align="peak", fin=0.01, fout=0.35, pan=0.25)
    # 06 THE TIGER (the one wow moment): riser under "and you will know", whoosh + sub impact on the cut
    place(b, DL + "riser_trailer.mp3", 0.4, 2.56, T(12.78) - 2.16, -15, fin=0.5, fout=0.02)
    place(b, DS + "2596-preview.mp3", 0.0, 2.2, T(12.78), -10, align="peak", fout=0.6)
    place(b, DL + "impact_whoosh_deep.mp3", 0.2, 2.6, T(12.78), -7, align="peak", fout=0.9)
    tick(T(12.80), -15)
    whoosh(T(14.05) + 0.05, -16, SS)                                     # back to her
    # "the way your heart will POUND"
    for hb, g in zip(HEARTBEATS, (-3, -7)):
        place(b, DS + "490-preview.mp3", 0.0, 1.1, hb, g, align="peak", fin=0.002, fout=0.25)
    # years of photographs: autofocus beep, split pushes in, a shutter on every photo
    place(b, DS + "1439-preview.mp3", 0.0, 0.5, SHUTTERS[0] - 0.32, -16, fin=0.002, fout=0.1)
    whoosh(SHUTTERS[0] + 0.1, -12, SC)
    for k, st in enumerate(SHUTTERS):
        place(b, DS + ("1430-preview.mp3" if k % 2 == 0 else "1440-preview.mp3"), 0.0, 0.6, st, -8, align="peak",
              fin=0.002, fout=0.1, pan=(-0.2 if k % 2 else 0.2))
    whoosh(T(22.55) + 0.05, -17, SS)
    # "your own eyes"
    whoosh(T(24.55) + 0.06, -11)
    place(b, DL + "impact_whoosh_deep.mp3", 0.2, 2.6, T(24.55), -14, align="peak", fout=0.7)
    whoosh(T(25.93) + 0.05, -17, SW)
    # Lost & Free: push, pop, shimmer
    whoosh(LOGO_SPLIT[0] + 0.12, -11, SC); pop(LOGO_SPLIT[0] + 0.05, -10, PL)
    sys.path.insert(0, str(P.parent / "lakshadweep_v2"))
    import synth as V2
    sh = V2.sfx_shimmer((86, 90, 93, 98), 0.06, 0.11)
    i = int((LOGO_SPLIT[0] + 0.05) * SR); n = min(len(sh), NS - i)
    b[i:i + n, 0] += sh[:n]; b[i:i + n, 1] += sh[:n]
    whoosh(LOGO_SPLIT[1] + 0.05, -17, SS)
    # CTA: jump-cut swoosh, "Comment" pops, "SAFARI" lands with weight, the last line ticks in
    whoosh(CUT + 0.05, -12, SW); pop(CUT + 0.01, -13, PL)
    pop(T(35.70), -9)
    place(b, DL + "impact_whoosh_deep.mp3", 0.2, 2.6, T(35.70) + 0.02, -15, align="peak", fout=0.8)
    tick(T(36.54), -15)
    # jungle air under the second half
    place(amb, DS + "2434-preview.mp3", 8.0, 8.0 + (DUR - T(16.61)), T(16.61), -27, fin=1.0, fout=0.6, norm=False)
    t = np.arange(NS) / SR
    gate = np.ones(NS); kill = (t >= SILENT - 0.05) & (t < SILENT + 0.10)
    gate[kill] = np.linspace(1, 0, kill.sum()); gate[(t >= SILENT + 0.10) & (t < T(16.61))] = 0
    out = b + amb * gate[:, None]
    out[(t >= SILENT + 0.02) & (t < BARKS[0] - 0.25)] = 0.0          # dead air between "silent" and the first bark
    return out

