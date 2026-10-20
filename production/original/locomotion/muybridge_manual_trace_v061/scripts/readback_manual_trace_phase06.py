"""Cold-open validation of the isolated manually specified GP trace."""

import bpy
import json
import math
from pathlib import Path


root = Path(__file__).resolve().parents[1]
spec = json.loads((root / "reference" / "phase06_manual_contours.json").read_text(encoding="utf-8"))
obj = bpy.data.objects.get("Phase 06 Manual GP Contours")
if obj is None or obj.type != "GREASEPENCIL":
    raise RuntimeError("Editable Grease Pencil trace object missing")
layer = obj.data.layers[0]
frame = layer.frames[0]
strokes = list(frame.drawing.strokes)


def expected_world(pixel):
    return ((pixel[0] - 155.0) * 0.01, (294.0 - pixel[1]) * 0.01, 0.0)


observed_counts = [len(stroke.points) for stroke in strokes]
expected_counts = [len(contour["points"]) for contour in spec["contours"]]
coordinate_errors = []
for contour, stroke in zip(spec["contours"], strokes):
    for pixel, point in zip(contour["points"], stroke.points):
        coordinate_errors.append(math.dist(expected_world(pixel), point.position))
report = {
    "native_file": bpy.data.filepath,
    "blender_version": bpy.app.version_string,
    "object_type": obj.type,
    "layer": layer.name,
    "frame": frame.frame_number,
    "stroke_count": len(strokes),
    "observed_point_counts": observed_counts,
    "expected_point_counts": expected_counts,
    "total_points": sum(observed_counts),
    "max_coordinate_error_world_units": max(coordinate_errors) if coordinate_errors else None,
    "material": obj.data.materials[0].name if obj.data.materials else None,
    "camera_type": bpy.context.scene.camera.data.type if bpy.context.scene.camera else None,
    "source_photo_packed": any(img.packed_file for img in bpy.data.images if img.name.startswith("phase06_source_crop")),
    "separate_strokes": len(strokes) == len(spec["contours"]),
    "passes": len(strokes) == len(spec["contours"]) and observed_counts == expected_counts
              and bool(coordinate_errors) and max(coordinate_errors) < 1e-5,
}
(root / "evidence" / "PHASE06_COLD_REOPEN_v061.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("PHASE06_COLD_REOPEN", json.dumps(report))
if not report["passes"]:
    raise RuntimeError("Manual tracing file failed cold reopen validation")
