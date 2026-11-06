import subprocess, sys, numpy as np, cv2
SRC = "../../../inbox/safari/IMG_2240.MP4"
HDR = ("zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
       "zscale=t=bt709:m=bt709:r=tv,format=gbrp")
def frame(t, grade):
    vf = f"{HDR},scale=1080:1920" + ("," + grade if grade else "")
    raw = subprocess.run(["ffmpeg","-v","error","-ss",str(t),"-i",SRC,"-frames:v","1","-vf",vf,"-f","rawvideo","-pix_fmt","bgr24","-"],capture_output=True,check=True).stdout
    return np.frombuffer(raw,np.uint8).reshape(1920,1080,3)
det = cv2.FaceDetectorYN.create("../../../models/face_detection_yunet_2023mar.onnx","",(540,960),0.6,0.3,5)
def stats(img):
    _,f = det.detect(cv2.resize(img,(540,960)))
    x,y,w,h = [int(v*2) for v in f[0][:4]]
    cheek = img[y+int(h*.45):y+int(h*.7), x+int(w*.15):x+int(w*.85)]
    lab = cv2.cvtColor(cheek, cv2.COLOR_BGR2Lab).reshape(-1,3).astype(float)
    L = lab[:,0]*100/255; a = lab[:,1]-128; b = lab[:,2]-128
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    bg = hsv[:500].reshape(-1,3)       # top band = foliage
    return f"skin L {np.median(L):.1f} C {np.median(np.hypot(a,b)):.1f} h {np.degrees(np.arctan2(np.median(b),np.median(a))):.1f} | luma {cv2.cvtColor(img,cv2.COLOR_BGR2GRAY).mean():.0f} | foliage sat {bg[:,1].mean()/255:.2f} hue {np.median(bg[:,0])*2:.0f}"
grades = {"none": "", "g": sys.argv[1] if len(sys.argv) > 1 else ""}
for t in (1.5, 15, 28):
    for k, g in grades.items():
        img = frame(t, g); print(t, k, stats(img))
        if k == "g": cv2.imwrite(f"grade_{t}.jpg", np.hstack([frame(t, ""), img])[::2, ::2])
