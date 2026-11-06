"""Find libass sizes so the caption type matches the reference reel's width shares."""
import subprocess, numpy as np
from pathlib import Path
from PIL import Image

B = Path(__file__).parent / "build"
H = r"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: S,Inter Display Medium,80,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def width(text, tags, size):
    ev = r"Dialogue: 0,0:00:00.00,0:00:05.00,S,,0,0,0,,{\an5\q2\pos(540,960)\fs%d%s}%s" % (size, tags, text)
    (B / "c.ass").write_text(H + ev + "\n", encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "color=c=0x808080:s=1080x1920:d=1",
                    "-frames:v", "1", "-vf", "ass=c.ass:fontsdir=../../../fonts", "c.png"], check=True, cwd=B)
    a = np.asarray(Image.open(B / "c.png").convert("L"), int)
    c = np.where((abs(a - 128) > 30).any(0))[0]
    return c.max() - c.min()

for text, tags, target in [("gut-wrenching", "", 0.54), ("If you catch a", "", 0.46),
                           ("turbulence", r"\fnInstrument Serif\i1", 0.46), ("turquoise", r"\fnInstrument Serif\i1", 0.33)]:
    w100 = width(text, tags, 100)
    print(f"{text:16s} w@100={w100}  size for {target:.0%}: {100 * target * 1080 / w100:.1f}")
