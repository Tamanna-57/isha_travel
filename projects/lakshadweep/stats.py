import numpy as np,glob,sys
from PIL import Image
def st(f):
  a=np.asarray(Image.open(f).convert('RGB'),float); y=0.2126*a[...,0]+0.7152*a[...,1]+0.0722*a[...,2]
  hsv=np.asarray(Image.open(f).convert('HSV'),float)
  return y.mean(),np.percentile(y,5),np.percentile(y,95),hsv[...,1].mean()/255
for p in sys.argv[1:]:
  s=np.array([st(f) for f in sorted(glob.glob(p+'*.png'))]); print(p, 'mean %.0f p5 %.0f p95 %.0f sat %.2f'%tuple(s.mean(0)), 'per-frame', np.round(s[:,0]).astype(int))
