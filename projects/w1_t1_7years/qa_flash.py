"""Scan a render for 1-3 frame shots (flashes). Usage: python qa_flash.py out/<name>_clean.mp4"""
import subprocess, sys, numpy as np
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", sys.argv[1], "-vf", "scale=54:96,format=gray", "-f", "rawvideo", "-"],
                     capture_output=True).stdout
f = np.frombuffer(raw, np.uint8).reshape(-1, 96, 54).astype(float)
d = np.abs(np.diff(f, axis=0)).mean((1, 2))
cuts = [i + 1 for i in range(len(d)) if d[i] > 18]
short = [(round(cuts[k] / 30, 2), cuts[k + 1] - cuts[k]) for k in range(len(cuts) - 1) if cuts[k + 1] - cuts[k] <= 3]
print("frames", len(f), "| cuts", [round(c / 30, 2) for c in cuts]); print("shots <= 3 frames (check):", short)
