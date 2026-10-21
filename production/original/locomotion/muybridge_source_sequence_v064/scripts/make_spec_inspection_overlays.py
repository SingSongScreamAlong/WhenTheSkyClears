"""Diagnostic only: display hand-picked JSON points over source before native build."""

import json
from pathlib import Path
from PIL import Image, ImageDraw

root=Path(__file__).resolve().parents[1]
for path in sorted((root / "phase_specs").glob("phase*.json")):
    spec=json.loads(path.read_text(encoding="utf-8"))
    phase=spec["phase"]
    source=Image.open(root / "reference" / f"phase{phase:02d}_source_crop.png").convert("RGB").resize((620,1176),Image.Resampling.LANCZOS)
    draw=ImageDraw.Draw(source)
    for contour in spec["contours"]:
        draw.line([(2*x,2*y) for x,y in contour["points"]],fill=(0,238,232),width=2,joint="curve")
    output=root / "evidence" / f"phase{phase:02d}_POINT_LIST_INSPECTION_ONLY.png"
    source.save(output,optimize=True)
    print(output)
