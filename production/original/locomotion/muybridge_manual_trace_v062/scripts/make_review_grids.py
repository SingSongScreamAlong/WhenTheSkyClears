"""Nearest-neighbor inspection enlargements with coordinate grid only."""

from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1]
source = Image.open(root / "reference" / "phase06_source_crop.png").convert("RGB")


def make(name, box, scale, step):
    x0, y0, x1, y1 = box
    base = source.crop(box).resize(((x1-x0)*scale, (y1-y0)*scale), Image.Resampling.NEAREST).convert("RGBA")
    grid = Image.new("RGBA", base.size, (0,0,0,0))
    draw = ImageDraw.Draw(grid)
    for x in range((x0//step)*step, x1+1, step):
        if x >= x0:
            xpos = (x-x0)*scale
            draw.line((xpos,0,xpos,base.height-1), fill=(28,225,240,65), width=1)
            draw.text((xpos+2,2), str(x), fill=(125,248,250,220))
    for y in range((y0//step)*step, y1+1, step):
        if y >= y0:
            ypos = (y-y0)*scale
            draw.line((0,ypos,base.width-1,ypos), fill=(28,225,240,65), width=1)
            draw.text((2,ypos+2), str(y), fill=(125,248,250,220))
    Image.alpha_composite(base, grid).convert("RGB").save(root / "reference" / name)


make("head_grid_v062.png", (130,125,195,190), 9, 10)
make("shoulder_torso_grid_v062.png", (95,185,185,355), 4, 10)
make("fist_grid_v062.png", (185,282,250,350), 9, 10)
make("knees_grid_v062.png", (115,345,235,465), 5, 10)
