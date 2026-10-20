"""GUI-context undo check for explicit GP data, not a mouse brush stroke."""

import bpy
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
evidence = root / "evidence"
evidence.mkdir(parents=True, exist_ok=True)

gp = bpy.data.grease_pencils.new("Undo Scratch")
obj = bpy.data.objects.new("Undo Scratch", gp)
bpy.context.scene.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
layer = gp.layers.new("Test", set_active=True)
frame = layer.frames.new(1)
area = next(a for a in bpy.context.screen.areas if a.type == "VIEW_3D")
region = next(r for r in area.regions if r.type == "WINDOW")

report = {"background": bpy.app.background, "test": "editor undo of direct GP data mutation"}
with bpy.context.temp_override(window=bpy.context.window, area=area, region=region):
    report["undo_poll_before"] = bpy.ops.ed.undo.poll()
    report["undo_push_poll"] = bpy.ops.ed.undo_push.poll()
    if report["undo_push_poll"]:
        report["push_before"] = list(bpy.ops.ed.undo_push(message="before scratch stroke"))

frame.drawing.add_strokes([2])
frame.drawing.strokes[0].points[0].position = (-1, 0, 0)
frame.drawing.strokes[0].points[1].position = (1, 0, 0)
report["count_after_data_write"] = len(frame.drawing.strokes)

with bpy.context.temp_override(window=bpy.context.window, area=area, region=region):
    if bpy.ops.ed.undo_push.poll():
        report["push_after"] = list(bpy.ops.ed.undo_push(message="after scratch stroke"))
    report["undo_poll_after"] = bpy.ops.ed.undo.poll()
    if report["undo_poll_after"]:
        try:
            report["undo_result"] = list(bpy.ops.ed.undo())
        except Exception as exc:
            report["undo_error"] = repr(exc)

current = bpy.data.objects.get("Undo Scratch")
report["object_exists_after_undo"] = current is not None
if current:
    try:
        report["count_after_undo"] = len(current.data.layers[0].frames[0].drawing.strokes)
    except Exception as exc:
        report["count_after_undo_error"] = repr(exc)

(evidence / "GUI_UNDO_DATA_TEST.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("GUI_UNDO_DATA_JSON", json.dumps(report))
if not bpy.app.background:
    bpy.ops.wm.quit_blender()
