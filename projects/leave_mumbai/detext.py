"""Remove the old burned-in text from the captioned Leave Mumbai file (draft stand-in until the client sends a
text-free export). Only the letters and their shadows are replaced, by inpainting from the pixels around them
(OpenCV Telea); nothing is blurred.

Text found per frame = bright, low-saturation pixels that stand out from a local median of the frame, inside the
zones where the old text sat (caption band always; title zone 0-3.1 s; source line 18-21.7 s).
Writes build/detexted.mp4 (SDR BT.709, 30 fps, original audio).
    python projects/leave_mumbai/detext.py [--frames t1,t2,...]   # --frames: test stills to build/detext_test/
"""
import subprocess, sys
from pathlib import Path
import numpy as np, cv2

P = Path(__file__).resolve().parent
ROOT = P.parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
import isha  # noqa: E402

SRC = ROOT / "bhai dooj" / "R1_LeaveMumbai_C_captions_sfx_transitions_original_color.mp4"
B = P / "build"
W, H, FPS = 1080, 1920, 30
# (t0, t1, y0, y1, x0, x1, kind): where the old text lived
#   light = white captions with a soft dark shadow; any = title strokes on the plain wall; rect = fill the whole box
ZONES = [
    (0.0, 99, 1255, 1440, 40, 1040, "light"),     # caption band (one line, centre y ~1340)
    (0.0, 3.1, 330, 585, 30, 1050, "any"),        # EVERY MORNING / I want to leave Mumbai
    (18.0, 21.7, 1203, 1250, 255, 825, "rect"),   # "Source: IQAir ..." pill
    (30.9, 34.1, 335, 425, 130, 520, "rect"),     # @lostandfree / count me in tags (under the logo card anyway)
]
K = lambda n: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (n, n))

def blobs(m, maxh=110, maxw=180, maxa=5000):
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros_like(m)
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if 2 <= h <= maxh and w <= maxw and a <= maxa:
            keep[lab == i] = 255
    return keep

def text_mask(img, y0, y1, x0, x1, kind):
    full = np.zeros(img.shape[:2], np.uint8)
    if kind == "rect":
        full[y0:y1, x0:x1] = 255
        return full
    roi = img[y0:y1, x0:x1]
    hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
    v = hsv[..., 2].astype(np.int16); s = hsv[..., 1].astype(np.int16)
    gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
    dev = gray.astype(np.int16) - cv2.medianBlur(gray, 41).astype(np.int16)
    if kind == "light":
        m = (((v > 150) & (s < 70) & (dev > 22)) | ((dev > 40) & (s < 110))).astype(np.uint8) * 255
        m = blobs(cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8)))
        # the old captions carry a soft drop shadow down-right: grow the mask to cover it
        m = cv2.dilate(m, K(21))
        m = np.maximum(m, np.roll(cv2.dilate(m, K(9)), (6, 6), (0, 1)))
    else:
        lab = cv2.cvtColor(roi, cv2.COLOR_RGB2LAB).astype(np.int16)
        bg = cv2.medianBlur(cv2.cvtColor(roi, cv2.COLOR_RGB2LAB), 41).astype(np.int16)
        d = np.abs(lab - bg).sum(2)
        m = blobs((d > 18).astype(np.uint8) * 255, maxh=150, maxw=900, maxa=60000)
        m = cv2.dilate(m, K(17))
    full[y0:y1, x0:x1] = m
    return full

def clean(img, t):
    out = img
    for t0, t1, y0, y1, x0, x1, kind in ZONES:
        if t0 <= t < t1:
            m = text_mask(out, y0, y1, x0, x1, kind)
            if m.any():
                pad = 24
                ya, yb = max(0, y0 - pad), min(H, y1 + pad)
                sub = cv2.inpaint(np.ascontiguousarray(out[ya:yb]), m[ya:yb], 7, cv2.INPAINT_TELEA)
                out = out.copy(); out[ya:yb] = sub
    return out

def frames(src, ss=None, n=None):
    vf = isha.HDR_TO_SDR + f",fps={FPS},format=rgb24"
    cmd = ["ffmpeg", "-v", "error"] + (["-ss", str(ss)] if ss is not None else []) + ["-i", str(src)] + \
          (["-frames:v", str(n)] if n else []) + ["-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)

def main():
    B.mkdir(exist_ok=True)
    if "--frames" in sys.argv:
        out = B / "detext_test"; out.mkdir(exist_ok=True)
        for t in map(float, sys.argv[sys.argv.index("--frames") + 1].split(",")):
            img = next(frames(SRC, t, 1))
            cv2.imwrite(str(out / f"{t:.1f}_a.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            cv2.imwrite(str(out / f"{t:.1f}_b.png"), cv2.cvtColor(clean(img, t), cv2.COLOR_RGB2BGR))
        print(out); return
    dst = B / "detexted.mp4"
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-i", str(SRC), "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                            "-preset", "medium", "-crf", "12", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
                            "-color_trc", "bt709", "-colorspace", "bt709", "-c:a", "copy", "-shortest", str(dst)],
                           stdin=subprocess.PIPE)
    for k, img in enumerate(frames(SRC)):
        enc.stdin.write(clean(img, k / FPS).tobytes())
    enc.stdin.close(); enc.wait()
    print(dst, k + 1, "frames")

if __name__ == "__main__":
    main()
