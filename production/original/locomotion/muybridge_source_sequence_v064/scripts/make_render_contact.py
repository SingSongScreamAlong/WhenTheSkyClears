"""Contact sheet from native Blender alpha over exact source pixels."""

import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument("phases",help="comma-separated list of actually rendered phase numbers")
parser.add_argument("name",help="output PNG filename")
args=parser.parse_args()
phases=[int(s) for s in args.phases.split(",")]
cols=min(4,len(phases))
rows=(len(phases)+cols-1)//cols
font_path=Path(r"C:\Windows\Fonts\arial.ttf")
font=ImageFont.truetype(str(font_path),17) if font_path.exists() else ImageFont.load_default()
small=ImageFont.truetype(str(font_path),13) if font_path.exists() else ImageFont.load_default()
canvas=Image.new("RGB",(cols*330+20,rows*630+42),(236,231,219))
draw=ImageDraw.Draw(canvas)
report={"phases":phases,"actual_native_render_alpha":True,"source_crop_size":[310,588],"native_render_size":[620,1176],"source_sha256":{},"render_sha256":{}}
for i,phase in enumerate(phases):
    source_path=root / "reference" / f"phase{phase:02d}_source_crop.png"
    render_path=root / "previews" / f"phase{phase:02d}_native_rgba_v064.png"
    source=Image.open(source_path).convert("RGB").resize((620,1176),Image.Resampling.LANCZOS)
    render=Image.open(render_path).convert("RGBA")
    if render.size!=source.size:
        raise RuntimeError("Source/render size mismatch")
    layer=Image.new("RGBA",render.size,(8,238,231,0))
    layer.putalpha(render.getchannel("A").point(lambda value:round(value*0.72)))
    overlay=Image.alpha_composite(source.convert("RGBA"),layer).convert("RGB").resize((310,588),Image.Resampling.LANCZOS)
    col,row=i%cols,i//cols
    x,y=20+col*330,20+row*630
    canvas.paste(overlay,(x,y+26))
    draw.text((x,y),f"PHASE {phase:02d} - SOURCE + GP",fill=(36,34,30),font=font)
    report["source_sha256"][str(phase)]=hashlib.sha256(source_path.read_bytes()).hexdigest()
    report["render_sha256"][str(phase)]=hashlib.sha256(render_path.read_bytes()).hexdigest()
draw.text((20,rows*630+13),"Each overlay uses its own manually authored native Blender GP render. Source frame timing is unknown.",fill=(59,55,48),font=small)
out=root / "previews" / args.name
canvas.save(out,optimize=True)
report["contact_sheet"]=str(out)
report["contact_sheet_sha256"]=hashlib.sha256(out.read_bytes()).hexdigest()
evidence=root / "evidence" / (out.stem+".json")
evidence.write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps({"path":str(out),"bytes":out.stat().st_size,"phases":phases}))
