"""Create the matched, two-pose review board from actual source pixels."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT.parents[0] / "muybridge_source_sequence_v064" / "reference"
OUT = ROOT / "previews" / "Boy_Two_Pose_Reference_Adaptation_Review_v065.png"
CW, CH = 660, 720
GAP, HEADER, ROWGAP, LEFT = 16, 74, 38, 20
W = LEFT * 2 + CW * 3 + GAP * 2
H = HEADER + CH * 2 + ROWGAP + 106
board = Image.new("RGB", (W, H), (231, 229, 224))
d = ImageDraw.Draw(board)
try:
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 23)
    small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 17)
except OSError:
    font = ImageFont.load_default()
    small = font

columns = [LEFT + i * (CW + GAP) for i in range(3)]
d.text((LEFT, 12), "Boy adaptation gate: two contrasting Muybridge phases", fill=(29, 29, 28), font=font)
d.text((LEFT, 43), "Actual A pixels  |  adult photographic source  |  point-authored child redraw", fill=(52, 52, 50), font=small)

for row, (phase, aframe) in enumerate(((6, 0), (8, 6))):
    yy = HEADER + row * (CH + ROWGAP)
    a = Image.open(ROOT / "reference" / f"A_v053_frame{aframe:03d}.png").convert("RGB")
    board.paste(a, (columns[0], yy))

    # Retain the source photo and its grid; scale the actual person to a matching
    # apparent height and position the floor on the same y=675 comparison line.
    photo = Image.open(SRC / f"phase{phase:02d}_source_crop.png").convert("RGB")
    crop = photo.crop((0, 125, photo.width, 548))
    resized = crop.resize((414, 565), Image.Resampling.LANCZOS)
    photo_panel = Image.new("RGB", (CW, CH), (28, 27, 23))
    photo_panel.paste(resized, (123, 110))
    board.paste(photo_panel, (columns[1], yy))

    native = Image.open(ROOT / "previews" / f"Boy_Phase{phase:02d}_Native_Redraw_v065.png").convert("RGBA")
    panel = Image.new("RGBA", (CW, CH), (216, 216, 212, 255))
    panel.alpha_composite(native)
    board.paste(panel.convert("RGB"), (columns[2], yy))
    d.rectangle((columns[2], yy + 674, columns[2] + CW - 1, yy + 676), fill=(118, 119, 116))
    for x in columns:
        d.rectangle((x, yy, x + CW - 1, yy + CH - 1), outline=(104, 104, 100), width=1)

    label_y = yy + CH + 5
    if row == 0:
        labels = (
            "A: v053 actual frame 0",
            "Source: adult phase 6, stride",
            "C6: editable child redraw",
        )
    else:
        labels = (
            "A: v053 actual frame 6",
            "Source: adult phase 8, support",
            "C8: editable child redraw",
        )
    for x, label in zip(columns, labels):
        d.text((x + 3, label_y), label, fill=(32, 32, 30), font=small)

d.text((LEFT, H - 31), "C = point-authored reference-based redraw; design/painting fidelity is under review, not a finished rotoscope.", fill=(49, 49, 47), font=small)
OUT.parent.mkdir(parents=True, exist_ok=True)
board.save(OUT, optimize=True)
print(OUT)
