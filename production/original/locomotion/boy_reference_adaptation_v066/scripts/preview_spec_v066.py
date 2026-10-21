"""Fast local diagnostic of the hand-placed fill/stroke lists before Blender."""

from pathlib import Path
from PIL import Image, ImageDraw
from pose8_spec_v066 import POSE

root = Path(__file__).resolve().parents[1]
root.joinpath("evidence").mkdir(exist_ok=True)
scale = 2
image = Image.new("RGBA", (660*scale, 720*scale))
draw = ImageDraw.Draw(image)
commands = [("fill", row) for row in POSE["fills"]] + [("line", row) for row in POSE["lines"]]
for kind, row in sorted(commands, key=lambda command: command[1][1]):
    if kind == "fill":
        _, _, color, points = row
        draw.polygon([(x*scale, y*scale) for x, y in points], fill=color)
    else:
        _, _, color, width, points = row
        draw.line([(x*scale, y*scale) for x, y in points], fill=color, width=max(1, round(width*scale)), joint="curve")
pose = image.resize((660,720), Image.Resampling.LANCZOS)
out = Image.new("RGBA", (660,720), (216,216,212,255))
out.alpha_composite(pose)
out.alpha_composite(Image.open(root.parent / "boy_reference_adaptation_v065" / "reference" / "Retained_Painted_Head_From_A006_For_Phase08_v065.png").convert("RGBA"))
path = root / "evidence" / "Phase08_Manual_Point_Trial_v066.png"
out.convert("RGB").save(path)
print(path, len(POSE["fills"]), len(POSE["lines"]))
