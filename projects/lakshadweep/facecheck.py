"""Find captions that sit on a face, and suggest the nearest clear y for each page.

1. YuNet face detection on every frame of out/<name>_clean.mp4 (the picture exactly as delivered, zooms included)
2. captions.ass rendered alone on black -> exact text pixels per frame
3. per page: does the text block (+margin) touch any face box (padded for hair/forehead/chin)?
4. per page: nearest y (fraction of 1920) where the block clears every face for the whole page, inside safe zones

Usage: python facecheck.py            -> report + build/face_fix.json
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np
import cv2

P = Path(__file__).resolve().parent
sys.path.insert(0, str(P))
import make

W, H = 540, 960                 # analysis resolution (half of 1080x1920)
S = 1080 / W
MODEL = P.parent.parent / "models/face_detection_yunet_2023mar.onnx"
MARGIN = 28                     # px (full-res) of air between caption block and face box
SAFE_TOP, SAFE_BOT = 170, 1530  # caption block must stay inside these (full-res y)

def frames(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    sz = W * H * (3 if "bgr24" in cmd else 1)
    while True:
        b = p.stdout.read(sz)
        if len(b) < sz:
            break
        yield np.frombuffer(b, np.uint8)
    p.wait()

def detect_faces(video):
    det = cv2.FaceDetectorYN.create(str(MODEL), "", (W, H), score_threshold=0.55, nms_threshold=0.3, top_k=20)
    out = []
    cmd = ["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    for f in frames(cmd):
        img = f.reshape(H, W, 3)
        _, faces = det.detect(img)
        boxes = []
        if faces is not None:
            raw = [(float(x), float(y), float(w), float(h), float(sc)) for x, y, w, h, *rest, sc in faces]
            big = max((r[3] for r in raw), default=0)
            for x, y, w, h, sc in raw:
                if sc < 0.7:
                    continue
                # torso false positives: smaller box sitting below a bigger face's chin
                if any(h < 0.8 * H2 and y > Y2 + 0.8 * H2 and abs((x + w / 2) - (X2 + W2 / 2)) < W2 for X2, Y2, W2, H2, _ in raw):
                    continue
                # pad: hair/forehead above, chin below, a little to the sides (full-res coords)
                x0, y0, x1, y1 = (x - 0.12 * w) * S, (y - 0.35 * h) * S, (x + 1.12 * w) * S, (y + 1.06 * h) * S
                boxes.append([x0, y0, x1, y1, sc])
        out.append(boxes)
    return out

def caption_masks():
    """bool text mask per frame (full timeline), at analysis resolution"""
    cmd = ["ffmpeg", "-v", "error", "-f", "lavfi", "-i", f"color=c=black:s=1080x1920:r={make.FPS}:d={make.DUR}",
           "-vf", f"ass=captions_only.ass:fontsdir=../../../fonts,scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=make.B)
    sz = W * H
    while True:
        b = p.stdout.read(sz)
        if len(b) < sz:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W) > 60

def main():
    make.build_ass(make.B / "captions_only.ass", with_handle=False)
    faces = detect_faces(make.OUT / f"{make.NAME}_clean.mp4")
    pages = make.parse_pages()
    nF = len(faces)
    # page block extents (full-res) = union of the page's text pixels at its final state
    page_of = {}
    for i, pg in enumerate(pages):
        t0 = pg["lines"][0][0]["t"]
        for fr in range(int(round(t0 * make.FPS)), min(nF, int(round(pg["end"] * make.FPS)))):
            page_of[fr] = i
    ext = {}
    for fr, m in enumerate(caption_masks()):
        if fr not in page_of or not m.any():
            continue
        ys, xs = np.where(m)
        i = page_of[fr]
        e = ext.get(i, [1e9, 1e9, -1, -1])
        ext[i] = [min(e[0], xs.min() * S), min(e[1], ys.min() * S), max(e[2], xs.max() * S), max(e[3], ys.max() * S)]
    report, fixes = [], {}
    for i, pg in enumerate(pages):
        if i not in ext:
            continue
        x0, y0, x1, y1 = ext[i]
        frs = [fr for fr, k in page_of.items() if k == i and fr < nF]
        fb = [b for fr in frs for b in faces[fr]]
        def hits(dy):
            a0, a1 = y0 + dy - MARGIN, y1 + dy + MARGIN
            n = 0
            for fr in frs:
                if any(not (x1 + MARGIN < bx0 or x0 - MARGIN > bx1 or a1 < by0 or a0 > by1) for bx0, by0, bx1, by1, _ in faces[fr]):
                    n += 1
            return n
        h0 = hits(0)
        cy = pg["y"] * 1920
        best = None
        if h0:
            for step in range(0, 1400, 6):
                for dy in (step, -step):
                    if y0 + dy < SAFE_TOP or y1 + dy > SAFE_BOT:
                        continue
                    if hits(dy) == 0:
                        best = dy
                        break
                if best is not None:
                    break
        txt = " ".join(w["text"] for ln in pg["lines"] for w in ln)
        frames_with_face = sum(1 for fr in frs if faces[fr])
        report.append((i, txt, pg["y"], h0, len(frs), frames_with_face, best))
        if h0 and best is not None:
            fixes[i] = round((cy + best) / 1920, 3)
    print(f"{'#':>2} {'page':32s} {'y':>5} {'face-hit frames':>16} {'frames w/ face':>15}  -> new y")
    for i, txt, y, h0, n, nf, best in report:
        new = f"{fixes[i]:.3f}" if i in fixes else ("NO CLEAR SPOT" if h0 else "ok")
        print(f"{i:2d} {txt[:32]:32s} {y:5.2f} {h0:7d}/{n:<8d} {nf:15d}  -> {new}")
    (make.B / "face_fix.json").write_text(json.dumps(fixes, indent=1))
    (make.B / "faces.json").write_text(json.dumps(faces))

if __name__ == "__main__":
    main()
