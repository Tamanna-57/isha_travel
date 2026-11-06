"""Cut static weights out of the variable Google fonts in ../fonts (libass renders static files reliably).
Re-run after adding a new variable font: python pipeline/make_static_fonts.py"""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

FONTS = Path(__file__).resolve().parent.parent / "fonts"
WEIGHTS = {400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold", 800: "ExtraBold", 900: "Black"}
PLAN = {  # variable source (fonts/_variable_sources) -> weights to cut into fonts/
    "PlayfairDisplay-VF.ttf": [400, 600, 700, 800],
    "PlayfairDisplay-Italic-VF.ttf": [400, 600, 700],
    "Montserrat-VF.ttf": [400, 600, 700, 800],
    "Cinzel-VF.ttf": [400, 600, 700],
    "Caveat-VF.ttf": [400, 700],
}

for rel, weights in PLAN.items():
    src = FONTS / "_variable_sources" / rel
    lo, hi = None, None
    axes = {a.axisTag: (a.minValue, a.maxValue) for a in TTFont(src)["fvar"].axes}
    lo, hi = axes["wght"]
    for w in weights:
        if not lo <= w <= hi:
            continue
        italic = "Italic" in src.name
        style = WEIGHTS[w] + ("Italic" if italic else "")
        if style == "RegularItalic":
            style = "Italic"
        try:
            inst = instantiateVariableFont(TTFont(src), {"wght": w}, updateFontNames=True)
        except ValueError:          # STAT table lacks this weight: name the instance ourselves
            inst = instantiateVariableFont(TTFont(src), {"wght": w})
            fam = inst["name"].getBestFamilyName()
            nice = style.replace("SemiBold", "SemiBold ").replace("Italic", " Italic").strip().replace("  ", " ")
            n = inst["name"]
            if w in (400, 700):
                n.setName(fam, 1, 3, 1, 0x409); n.setName("Bold" if w == 700 else "Regular", 2, 3, 1, 0x409)
            else:                   # non-RIBBI weight: typographic family/subfamily (ids 16/17) + legacy names
                n.setName(f"{fam} {nice}", 1, 3, 1, 0x409); n.setName("Regular", 2, 3, 1, 0x409)
                n.setName(fam, 16, 3, 1, 0x409); n.setName(nice, 17, 3, 1, 0x409)
            n.setName(f"{fam} {nice}", 4, 3, 1, 0x409); n.setName(f"{fam.replace(' ', '')}-{style}", 6, 3, 1, 0x409)
            inst["OS/2"].usWeightClass = w
        out = FONTS / f"{src.name.split('-')[0]}-{style}.ttf"
        inst.save(out)
        names = inst["name"]
        print(f"{out.relative_to(FONTS)}  family='{names.getBestFamilyName()}' style='{names.getBestSubFamilyName()}' "
              f"weight={inst['OS/2'].usWeightClass}")
