"""Explicit brush-input samples in an isolated Grease Pencil scratch scene.

This tests the Blender operator input path. It is not character art or a
procedural animation method. Every sample below is deliberately specified.
"""

import bpy
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
evidence = root / "evidence"
evidence.mkdir(parents=True, exist_ok=True)

gp = bpy.data.grease_pencils.new("Brush Input Scratch")
obj = bpy.data.objects.new("Brush Input Scratch", gp)
bpy.context.scene.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
layer = gp.layers.new("Strokes", set_active=True)
frame = layer.frames.new(1)

material = bpy.data.materials.new("Black Ink")
bpy.data.materials.create_gpencil_data(material)
material.grease_pencil.color = (0.025, 0.025, 0.025, 1.0)
gp.materials.append(material)

bpy.ops.object.mode_set(mode="PAINT_GREASE_PENCIL")
area = next(a for a in bpy.context.screen.areas if a.type == "VIEW_3D")
region = next(r for r in area.regions if r.type == "WINDOW")
brush = bpy.context.tool_settings.gpencil_paint.brush

report = {
    "version": bpy.app.version_string,
    "background": bpy.app.background,
    "area": area.type,
    "region_px": [region.width, region.height],
    "mode": obj.mode,
    "brush": brush.name if brush else None,
    "before_strokes": len(frame.drawing.strokes),
}

straight = [
    {"name": "line", "location": (0, 0, 0), "mouse": (500, 400), "mouse_event": (500, 400), "pressure": 1.0, "x_tilt": 0.0, "y_tilt": 0.0, "size": 16.0, "time": 0.00, "is_start": True},
    {"name": "line", "location": (0, 0, 0), "mouse": (550, 400), "mouse_event": (550, 400), "pressure": 1.0, "x_tilt": 0.0, "y_tilt": 0.0, "size": 16.0, "time": 0.05, "is_start": False},
    {"name": "line", "location": (0, 0, 0), "mouse": (600, 400), "mouse_event": (600, 400), "pressure": 1.0, "x_tilt": 0.0, "y_tilt": 0.0, "size": 16.0, "time": 0.10, "is_start": False},
    {"name": "line", "location": (0, 0, 0), "mouse": (650, 400), "mouse_event": (650, 400), "pressure": 1.0, "x_tilt": 0.0, "y_tilt": 0.0, "size": 16.0, "time": 0.15, "is_start": False},
]

with bpy.context.temp_override(window=bpy.context.window, area=area, region=region):
    report["operator_poll"] = bpy.ops.grease_pencil.brush_stroke.poll()
    try:
        report["straight_result"] = list(bpy.ops.grease_pencil.brush_stroke("INVOKE_DEFAULT", mode="NORMAL", stroke=straight))
    except Exception as exc:
        report["straight_error"] = repr(exc)

report["after_strokes"] = len(frame.drawing.strokes)
report["point_counts"] = [len(stroke.points) for stroke in frame.drawing.strokes]
report["sample_positions"] = [[list(point.position) for point in stroke.points] for stroke in frame.drawing.strokes]
(evidence / ("BLENDER_BRUSH_OPERATOR_BACKGROUND.json" if bpy.app.background else "BLENDER_BRUSH_OPERATOR_GUI.json")).write_text(json.dumps(report, indent=2), encoding="utf-8")
print("BRUSH_PROBE_JSON", json.dumps(report))
if not bpy.app.background:
    bpy.ops.wm.quit_blender()

