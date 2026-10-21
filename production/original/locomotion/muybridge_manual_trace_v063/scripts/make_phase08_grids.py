"""Coordinate inspection enlargements of the unaltered phase 8 crop only."""

from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1]
source = Image.open(root / "reference" / "phase08_candidate.png").convert("RGB")


def grid(name, box, scale, step=10):
    x0, y0, x1, y1 = box
    base = source.crop(box).resize(((x1-x0)*scale, (y1-y0)*scale), Image.Resampling.NEAREST).convert("RGBA")
    markings = Image.new("RGBA", base.size, (0,0,0,0))
    draw = ImageDraw.Draw(markings)
    for x in range((x0//step)*step, x1+1, step):
        if x >= x0:
            px = (x-x0)*scale
            draw.line((px,0,px,base.height-1), fill=(28,225,240,65), width=1)
            draw.text((px+2,2), str(x), fill=(125,248,250,220))
    for y in range((y0//step)*step, y1+1, step):
        if y >= y0:
            py = (y-y0)*scale
            draw.line((0,py,base.width-1,py), fill=(28,225,240,65), width=1)
            draw.text((2,py+2), str(y), fill=(125,248,250,220))
    Image.alpha_composite(base, markings).convert("RGB").save(root / "reference" / name)


grid("phase08_full_grid.png", (35,105,220,555), 2, 20)
grid("phase08_head_grid.png", (105,110,185,205), 6)
grid("phase08_torso_grid.png", (90,190,195,365), 4)
grid("phase08_knees_feet_grid.png", (35,330,220,550), 4)
grid("phase08_hand_grid.png", (140,320,195,372), 10, 5)
grid("phase08_knee_grid.png", (110,390,175,455), 8, 5)
grid("phase08_lifted_foot_grid.png", (0,455,105,540), 6, 5)
