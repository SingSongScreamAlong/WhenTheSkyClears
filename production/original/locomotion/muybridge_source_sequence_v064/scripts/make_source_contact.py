"""Show all twelve unchanged top-row crop pixels at one common scale."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[1]
font_path = Path(r"C:\Windows\Fonts\arial.ttf")
font = ImageFont.truetype(str(font_path), 20) if font_path.exists() else ImageFont.load_default()
canvas = Image.new("RGB", (4*330+20, 3*630+20), (235,230,218))
draw = ImageDraw.Draw(canvas)
for phase in range(1,13):
    crop = Image.open(root / "reference" / f"phase{phase:02d}_source_crop.png").convert("RGB")
    if crop.size != (310,588):
        raise RuntimeError(f"Wrong crop size for phase {phase}")
    col, row = (phase-1)%4, (phase-1)//4
    x, y = 20+col*330, 20+row*630
    canvas.paste(crop, (x,y+27))
    draw.text((x,y), f"SOURCE PHASE {phase:02d}", fill=(35,33,29), font=font)
out = root / "previews" / "Original_12_Phase_Crops_v064.png"
canvas.save(out, optimize=True)
print(out)
