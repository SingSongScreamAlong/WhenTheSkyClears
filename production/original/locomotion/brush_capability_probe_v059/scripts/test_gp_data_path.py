"""Test explicit Grease Pencil stroke-data editing, not pointer brush input."""

import bpy
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
evidence = root / "evidence"
evidence.mkdir(parents=True, exist_ok=True)

gp = bpy.data.grease_pencils.new("GP Data Path Scratch")
obj = bpy.data.objects.new("GP Data Path Scratch", gp)
bpy.context.scene.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
layer = gp.layers.new("Explicit Samples", set_active=True)
frame = layer.frames.new(1)
drawing = frame.drawing

material = bpy.data.materials.new("Test Black")
bpy.data.materials.create_gpencil_data(material)
material.grease_pencil.color = (0.025, 0.025, 0.025, 1.0)
gp.materials.append(material)

report = {"version": bpy.app.version_string, "method": "direct Grease Pencil RNA data mutation", "before": len(drawing.strokes)}

straight = [(-2.5, 1.2, 0.0), (-1.6, 1.2, 0.0), (-0.7, 1.2, 0.0), (0.2, 1.2, 0.0)]
drawing.add_strokes([len(straight)])
stroke = drawing.strokes[0]
for point, coords in zip(stroke.points, straight):
    point.position = coords
    point.radius = 0.06
    point.opacity = 1.0
report["after_straight"] = len(drawing.strokes)
report["straight_points"] = [list(point.position) for point in drawing.strokes[0].points]
report["stroke_members"] = [name for name in dir(stroke) if not name.startswith("_")]
report["point_members"] = [name for name in dir(stroke.points[0]) if not name.startswith("_")]

area = next(a for a in bpy.context.screen.areas if a.type == "VIEW_3D")
region = next(r for r in area.regions if r.type == "WINDOW")
with bpy.context.temp_override(window=bpy.context.window, area=area, region=region):
    report["undo_poll"] = bpy.ops.ed.undo.poll()
    if report["undo_poll"]:
        try:
            report["undo_result"] = list(bpy.ops.ed.undo())
        except Exception as exc:
            report["undo_error"] = repr(exc)

try:
    report["after_undo_data_exists"] = gp.name in bpy.data.grease_pencils
    report["after_undo_stroke_count"] = len(bpy.data.grease_pencils[gp.name].layers[0].frames[0].drawing.strokes)
except Exception as exc:
    report["after_undo_error"] = repr(exc)

(evidence / "GP_DATA_PATH_FIRST_PASS.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("GP_DATA_JSON", json.dumps(report))
