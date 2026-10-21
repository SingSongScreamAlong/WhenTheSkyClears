"""Diagnostic raster of the manually authored contour lists before native build."""

from pathlib import Path
from PIL import Image, ImageDraw
from pose_specs import POSES

root=Path(__file__).resolve().parents[1]
scale=2
for phase,spec in POSES.items():
    image=Image.new("RGBA",(660*scale,720*scale),(0,0,0,0))
    draw=ImageDraw.Draw(image)
    commands=[("fill",v) for v in spec["fills"]]+[("line",v) for v in spec["lines"]]
    for kind,entry in sorted(commands,key=lambda item:item[1][1]):
        if kind=="fill":
            name,z,color,points=entry
            draw.polygon([(x*scale,y*scale) for x,y in points],fill=color)
        else:
            name,z,color,width,points=entry
            draw.line([(x*scale,y*scale) for x,y in points],fill=color,width=max(1,round(width*scale)),joint="curve")
    output=image.resize((660,720),Image.Resampling.LANCZOS)
    paper=Image.new("RGBA",output.size,(216,216,212,255))
    paper.alpha_composite(output)
    path=root / "evidence" / f"pose{phase:02d}_POINT_LIST_DIAGNOSTIC.png"
    paper.convert("RGB").save(path)
    print(phase,len(spec["fills"]),len(spec["lines"]),path)
