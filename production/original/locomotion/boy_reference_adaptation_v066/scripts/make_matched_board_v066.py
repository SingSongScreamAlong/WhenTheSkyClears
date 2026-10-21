"""Match approved paint, v065 before, and one-pose v066 after at 660x720."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[1]
prior = root.parent / "boy_reference_adaptation_v065"
CW, CH = 660, 720
gap, left, top, bottom = 14, 16, 92, 78
board = Image.new("RGB", (left*2 + CW*3 + gap*2, top+CH+bottom), (234,232,228))
d = ImageDraw.Draw(board)
try:
    title = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 24)
    label = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 17)
except OSError:
    title = label = ImageFont.load_default()
d.text((left, 12), "Phase 8: one child support pose — painted reference / before / authored correction", fill=(29,30,29), font=title)
d.text((left, 46), "Identical 660 × 720 camera framing and floor line; source anatomy: Muybridge phase 8.", fill=(50,52,50), font=label)

paths = [
    prior / "reference" / "A_v053_frame006.png",
    prior / "previews" / "Boy_Phase08_Native_Redraw_v065.png",
    root / "previews" / "Boy_Phase08_Native_Correction_v066.png",
]
labels = [
    "A — actual v053 painted boy",
    "Before — v065 point study",
    "After — v066 manual correction + retained A head",
]
for i, (path, caption) in enumerate(zip(paths, labels)):
    x = left + i*(CW+gap)
    src = Image.open(path).convert("RGBA")
    panel = Image.new("RGBA", (CW,CH), (216,216,212,255))
    panel.alpha_composite(src)
    board.paste(panel.convert("RGB"), (x,top))
    d.rectangle((x,top,x+CW-1,top+CH-1), outline=(108,109,105), width=1)
    if i != 0:
        d.line((x, top+675, x+CW-1, top+675), fill=(111,112,109), width=1)
    d.text((x+2, top+CH+7), caption, fill=(35,35,34), font=label)

d.text((left, top+CH+43), "Review gate: support axes remain usable; coat/hand/boot painting and weight still trail the target. One static pose only.", fill=(55,55,53), font=label)
out = root / "previews" / "Boy_Phase08_A_Before_After_Matched_v066.png"
board.save(out, optimize=True)
print(out)
