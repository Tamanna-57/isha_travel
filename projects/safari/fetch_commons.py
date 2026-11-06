"""search Wikimedia Commons, download 600px thumbs + metadata, build a labelled contact sheet"""
import json, sys, urllib.request, urllib.parse, io, re, time
UA = {"User-Agent": "IshaReelBot/1.0 (reel editing tool)"}
def get(url):
    for k in range(6):
        try:
            time.sleep(1.0)
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA)).read()
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(5 * (k + 1))
    raise RuntimeError("rate limited")
from PIL import Image, ImageDraw
def api(**p):
    p.update(action="query", format="json")
    return json.loads(get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p)))
queries = json.loads(sys.argv[1]); out = sys.argv[2]
meta = []
for q in queries:
    d = api(generator="search", gsrsearch=q + " filetype:bitmap", gsrnamespace=6, gsrlimit=8, prop="imageinfo",
            iiprop="url|size|extmetadata", iiurlwidth=600)
    for pg in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda x: x.get("index", 0)):
        ii = pg["imageinfo"][0]; m = ii["extmetadata"]
        if ii["width"] < 1500: continue
        meta.append(dict(q=q, title=pg["title"], url=ii["url"], thumb=ii["thumburl"], w=ii["width"], h=ii["height"],
                         lic=m.get("LicenseShortName", {}).get("value", "?"),
                         artist=re.sub("<[^>]+>", "", m.get("Artist", {}).get("value", "?"))[:60]))
ims = []
for i, x in enumerate(meta):
    try:
        b = get(x["thumb"])
        im = Image.open(io.BytesIO(b)).convert("RGB"); im.thumbnail((300, 300))
        c = Image.new("RGB", (300, 330), "black"); c.paste(im, ((300 - im.width) // 2, 0))
        ImageDraw.Draw(c).text((4, 305), f"{i} {x['lic'][:12]} {x['title'][5:30]}", fill="yellow")
        ims.append(c)
    except Exception as e:
        print("fail", i, e); ims.append(Image.new("RGB", (300, 330)))
cols = 8; rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 300, rows * 330))
for i, c in enumerate(ims): sheet.paste(c, (i % cols * 300, i // cols * 330))
sheet.save(out + ".jpg", quality=85)
json.dump(meta, open(out + ".json", "w"), indent=1)
print(len(meta))
