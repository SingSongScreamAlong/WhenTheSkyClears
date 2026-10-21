"""Make a coordinate grid over chosen original crop pixels for manual inspection."""

import argparse
from pathlib import Path
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("phase", type=int)
parser.add_argument("box", help="x0,y0,x1,y1 in crop pixels")
parser.add_argument("name")
parser.add_argument("--scale", type=int, default=5)
parser.add_argument("--step", type=int, default=10)
args = parser.parse_args()
x0,y0,x1,y1 = map(int,args.box.split(","))
source = Image.open(root / "reference" / f"phase{args.phase:02d}_source_crop.png").convert("RGB")
base = source.crop((x0,y0,x1,y1)).resize(((x1-x0)*args.scale,(y1-y0)*args.scale),Image.Resampling.NEAREST).convert("RGBA")
markings = Image.new("RGBA",base.size,(0,0,0,0))
draw = ImageDraw.Draw(markings)
for x in range((x0//args.step)*args.step,x1+1,args.step):
    if x>=x0:
        px=(x-x0)*args.scale
        draw.line((px,0,px,base.height-1),fill=(28,225,240,65),width=1)
        draw.text((px+2,2),str(x),fill=(125,248,250,220))
for y in range((y0//args.step)*args.step,y1+1,args.step):
    if y>=y0:
        py=(y-y0)*args.scale
        draw.line((0,py,base.width-1,py),fill=(28,225,240,65),width=1)
        draw.text((2,py+2),str(y),fill=(125,248,250,220))
out=root / "reference" / args.name
Image.alpha_composite(base,markings).convert("RGB").save(out)
print(out)
