"""Cold reopen validation of the project-owned native curve authoring proof."""

import bpy
import json
import math
from pathlib import Path


root = Path(__file__).resolve().parents[1]
expected = json.loads((root / "evidence" / "NATIVE_CURVE_GUI_TEST_v060.json").read_text(encoding="utf-8"))
obj = bpy.data.objects.get("UI Brush Scratch")
if obj is None or obj.type != "GREASEPENCIL":
    raise RuntimeError("Native curve proof object missing")
layer = obj.data.layers.active
frame = layer.current_frame()
if frame is None:
    raise RuntimeError("Native curve proof frame missing")
strokes = list(frame.drawing.strokes)
positions = [[list(point.position) for point in stroke.points] for stroke in strokes]
radii = [[float(point.radius) for point in stroke.points] for stroke in strokes]
counts = [len(stroke.points) for stroke in strokes]
source = [expected["curve_a"], expected["curve_b"]]
positions_match = len(positions) == len(source) and all(
    len(actual) == len(wanted) and all(
        math.dist(actual_point, wanted_point) < 1e-5
        for actual_point, wanted_point in zip(actual, wanted)
    ) for actual, wanted in zip(positions, source)
)
gap = math.dist(positions[0][-1], positions[1][0]) if len(positions) == 2 else None
report = {
    "blend": bpy.data.filepath,
    "version": bpy.app.version_string,
    "object_type": obj.type,
    "layer": layer.name,
    "frame": frame.frame_number,
    "stroke_count": len(strokes),
    "point_counts": counts,
    "positions": positions,
    "radii": radii,
    "material": obj.data.materials[0].name if obj.data.materials else None,
    "positions_match_specified": positions_match,
    "separate_endpoint_gap": gap,
    "passes": counts == [9, 7] and positions_match and gap is not None and gap > 1,
}
(root / "evidence" / "NATIVE_CURVE_COLD_REOPEN_v060.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("NATIVE_CURVE_COLD_REOPEN", json.dumps({k: v for k, v in report.items()
                                          if k not in ("positions", "radii")}))
if not report["passes"]:
    raise RuntimeError("Cold reopen failed native curve validation")
