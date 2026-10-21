"""Cold-open readback for isolated Grease Pencil data proof."""

import bpy
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
obj = bpy.data.objects.get("GP Input Path Evidence")
if not obj or obj.type != "GREASEPENCIL":
    raise RuntimeError("Scratch Grease Pencil object missing after cold reopen")
frame = obj.data.layers[0].frames[0]
strokes = frame.drawing.strokes
report = {
    "blend": bpy.data.filepath,
    "version": bpy.app.version_string,
    "object_type": obj.type,
    "layer": obj.data.layers[0].name,
    "frame": frame.frame_number,
    "stroke_count": len(strokes),
    "point_counts": [len(stroke.points) for stroke in strokes],
    "positions": [[list(point.position) for point in stroke.points] for stroke in strokes],
    "radii": [[point.radius for point in stroke.points] for stroke in strokes],
    "material": obj.data.materials[0].name if obj.data.materials else None,
}
report["passes_expected_counts"] = report["stroke_count"] == 2 and report["point_counts"] == [8, 3]
report["separate_ends"] = (
    list(strokes[0].points[-1].position),
    list(strokes[1].points[0].position),
)
(root / "evidence" / "GP_COLD_REOPEN.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("GP_COLD_REOPEN_JSON", json.dumps({k:v for k,v in report.items() if k not in ("positions","radii")}))
