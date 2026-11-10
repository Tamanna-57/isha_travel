"""Build the two A/B trial versions of the Leave Mumbai reel FROM THE CURRENT FINAL, changing only the top layer.

Base layer (never changed here): the final's clips, cut points, speed, takes, words.json, loudness target.
Top layer (per trial): heading/caption style + colours, title, music bed, SFX levels, transition effects.

  Trial A (ref style): the client's reference reel look: neon-lime hook line, white bold top captions, hard cuts,
                      lo-fi groove. Picture/voice = the final's assembled.mov itself.
  Trial B "Bold Pop": Caveat write-on title, pop captions (Montserrat caps), hot-pink keywords, whip/zoom/flash
                      intros (video only), upbeat bed. Re-cut for the effects; its voice track is then checked
                      sample-for-sample against the final's.

    python projects/leave_mumbai/build_trials.py [A] [B]
Every run ends with checks; it stops with an error if any base-layer check fails.
"""
import copy, json, shutil, subprocess, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
FINAL = ROOT / "projects" / "leave_mumbai"
sys.path.insert(0, str(ROOT / "pipeline"))
import isha  # noqa: E402

TRIALS = {
    "A": {
        "dir": "leave_mumbai_trialA", "name": "leave_mumbai_trialA_refstyle", "variant": "refstyle",
        "note": "TRIAL A, in the style of the client's reference (sailing_amrutha x ixigo reel): the final's picture and "
                "voice untouched; top layer only: her opening line as a neon-lime condensed-caps hook, then plain white "
                "rounded-bold phrases high in the frame (no word highlight), hard cuts, chart + logo card moved low, "
                "lo-fi bed.",
        "titles": [],
        "captions": {"style": "topbold", "words": "words.json", "key_color": "#D6EC47", "hook_until": 3.3, "y": 436},
        "music_gain": -15, "whoosh_gain": None, "fx": {},
    },
    "B": {
        "dir": "leave_mumbai_trialB", "name": "leave_mumbai_trialB_pop", "variant": "pop",
        "note": "TRIAL B 'Bold Pop': the final's cut and voice untouched; top layer only: Caveat write-on title, "
                "Montserrat caps captions popping in word by word, hot-pink keywords, whip/zoom/flash intros on "
                "room changes (video only), upbeat pop bed.",
        "titles": [{"type": "marker", "text": "every morning, I want to", "start": 0.0, "end": 2.4, "x": 540,
                    "y": 250, "size": 92, "rotate": -2, "color": "chalk", "write_ms": 350},
                   {"type": "marker", "text": "Leave Mumbai!", "start": 0.25, "end": 2.4, "x": 540, "y": 400,
                    "size": 205, "rotate": -3, "color": "#FF4F8B", "write_ms": 450}],
        "captions": {"style": "pop", "words": "words.json", "key_color": "#FF4F8B"},
        "music_gain": -15, "whoosh_gain": -17,
        # clip index -> intro effect, only on room/setting changes (same clips that get a whoosh)
        "fx": {2: "whip", 4: "zoom", 5: "whip", 7: "whip", 8: "flash", 12: "zoom", 16: "whip"},
    },
}

def probe_dur(f, s):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", s, "-show_entries", "stream=duration",
                        "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout.strip()
    return float(r) if r else 0.0

def pcm(f, sr=16000):
    a = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-map", "0:a:0", "-ac", "1", "-ar", str(sr),
                        "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(a, np.int16).astype(np.float32) / 32768

def check(ok, msg):
    print(("  [ok] " if ok else "  [FAIL] ") + msg)
    if not ok:
        raise SystemExit(f"check failed: {msg}")

def build(key):
    cfg = TRIALS[key]
    d = ROOT / "projects" / cfg["dir"]; b = d / "build"
    b.mkdir(parents=True, exist_ok=True)
    final = json.loads((FINAL / "edit.json").read_text(encoding="utf-8"))
    # ---- base layer: copied from the final, untouched
    e = {"_note": cfg["note"], "name": cfg["name"], "_variant": cfg["variant"], "format": final["format"],
         "grade": final["grade"], "clips": copy.deepcopy(final["clips"]), "lufs": final.get("lufs", -14)}
    for i, f in cfg["fx"].items():
        e["clips"][i]["fx"] = f                      # video-only intro effect
    shutil.copy(FINAL / "words.json", d / "words.json")
    # ---- top layer
    e["titles"] = cfg["titles"]; e["captions"] = cfg["captions"]
    e["music"] = {"src": "build/music.wav", "start": 0, "gain_db": cfg["music_gain"], "duck": True}
    (d / "edit.json").write_text(json.dumps(e, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(FINAL / "prep.py"), "--project", str(d.relative_to(ROOT))], check=True,
                   cwd=ROOT)                         # music, chart (version colour), logo card, overlays + sfx times
    e = json.loads((d / "edit.json").read_text(encoding="utf-8"))
    if cfg["whoosh_gain"] is None:                   # this style uses clean hard cuts: no whooshes
        e["sfx"] = [s for s in e["sfx"] if "swoosh" not in s["src"]]
    for s in e["sfx"]:
        if "swoosh" in s["src"]:
            s["gain_db"] = cfg["whoosh_gain"]
    (d / "edit.json").write_text(json.dumps(e, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ---- picture + voice
    fa = FINAL / "build" / "assembled.mov"
    if not cfg["fx"]:
        shutil.copy(fa, b / "assembled.mov")         # literally the final's base layer
    else:
        for f in b.glob("seg_*.mov"):
            f.unlink()                               # never reuse old segments
        isha.assemble(e, d, b)
    asm = b / "assembled.mov"
    print(f"\nTrial {key}: base-layer checks")
    vf, af = probe_dur(fa, "v"), probe_dur(fa, "a")
    va, aa = probe_dur(asm, "v"), probe_dur(asm, "a")
    check(abs(va - vf) < 0.05 and abs(aa - af) < 0.05, f"length matches the final (video {va:.2f}/{vf:.2f}, audio {aa:.2f}/{af:.2f})")
    check(abs(va - aa) < 0.05, "audio runs as long as the video")
    x, y = pcm(asm), pcm(fa)
    n = min(len(x), len(y)); diff = np.abs(x[:n] - y[:n]).max()
    check(diff < 2e-3, f"voice track identical to the final's (max sample difference {diff:.5f})")
    check(json.loads((d / "words.json").read_text()) == json.loads((FINAL / "words.json").read_text()),
          "captions = the final's words, timings and page breaks")

    # ---- top layer render (full quality)
    final_mp4 = isha.finish(e, d, b, asm)
    isha.qa(final_mp4, e.get("format"), e.get("lufs", -14))
    print(f"\nTrial {key}: output checks")
    vo, ao = probe_dur(final_mp4, "v"), probe_dur(final_mp4, "a")
    check(abs(vo - vf) < 0.1 and abs(ao - vo) < 0.05, f"output {vo:.2f}s video, {ao:.2f}s audio")
    z = pcm(final_mp4, 8000); tail = z[int((vo - 4.5) * 8000):]
    win = [20 * np.log10(np.sqrt((tail[i:i + 1600] ** 2).mean()) + 1e-6) for i in range(0, len(tail) - 1600, 1600)]
    check(min(win) > -45, f"sound all the way through the last 4.5 s (quietest 0.2 s window {min(win):.0f} dB)")
    phone = final_mp4.with_name(final_mp4.stem + "_POST.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(final_mp4), "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "22", "-maxrate", "7M", "-bufsize", "14M", "-pix_fmt", "yuv420p", "-color_primaries",
                    "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-c:a", "copy", "-movflags",
                    "+faststart", str(phone)], check=True)
    print(f"  -> {phone}")

if __name__ == "__main__":
    for k in (sys.argv[1:] or ["A", "B"]):
        build(k)
