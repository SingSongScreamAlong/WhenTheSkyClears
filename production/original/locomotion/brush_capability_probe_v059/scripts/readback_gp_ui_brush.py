"""Cold-open readback of the actual DCC-CUA Grease Pencil brush input."""

import bpy
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
obj = bpy.data.objects.get("UI Brush Scratch")
if not obj or obj.type != "GREASEPENCIL":
    raise RuntimeError("UI brush scratch Grease Pencil object missing")
layers = list(obj.data.layers)
frames = list(layers[0].frames) if layers else []
strokes = list(frames[0].drawing.strokes) if frames else []
report = {
    "blend": bpy.data.filepath,
    "version": bpy.app.version_string,
    "object_type": obj.type,
    "layer": layers[0].name if layers else None,
    "frame": frames[0].frame_number if frames else None,
    "stroke_count": len(strokes),
    "point_counts": [len(stroke.points) for stroke in strokes],
    "positions": [[list(point.position) for point in stroke.points] for stroke in strokes],
    "radii": [[point.radius for point in stroke.points] for stroke in strokes],
    "material": obj.data.materials[0].name if obj.data.materials else None,
}
(root / "evidence" / "GP_UI_BRUSH_COLD_REOPEN.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("GP_UI_BRUSH_COLD_REOPEN", json.dumps({k: v for k, v in report.items()
                                           if k not in ("positions", "radii")}))
