"""graded base cut: IMG_2240 HLG -> SDR -> safari_soft LUT, 1440x2560, two segments (drops 'and if you want then')"""
import subprocess
from pathlib import Path
P = Path(__file__).resolve().parent; B = P / "build"
SRC = P.parent.parent / "inbox/safari/IMG_2240.MP4"
SEGS = [(0.07, 33.90), (35.30, 37.75)]
HDR = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
       "zscale=t=bt709:m=bt709:r=tv,format=gbrp")
fc = [f"[0:v]fps=30,{HDR},lut3d=file=safari_soft.cube:interp=tetrahedral,split=2[a][b]"]
for i, (s, e) in enumerate(SEGS):
    fc.append(f"[{'ab'[i]}]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}]")
fc.append("[v0][v1]concat=n=2:v=1:a=0,format=yuv420p[v]")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-stats", "-i", str(SRC), "-filter_complex", ";".join(fc), "-map", "[v]",
                "-c:v", "libx264", "-preset", "medium", "-crf", "12", "-pix_fmt", "yuv420p", "base.mp4"], check=True, cwd=B)
