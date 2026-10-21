"""GUI proof: two native curves, Undo second, repeat, save editable file."""

import bpy
import importlib.util
import json
from pathlib import Path


root = Path(__file__).resolve().parents[1]
module_path = root / "scripts" / "native_curve_author.py"
spec = importlib.util.spec_from_file_location("native_curve_author_v060", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.register()

obj = bpy.data.objects.get("UI Brush Scratch")
if obj is None or obj.type != "GREASEPENCIL":
    raise RuntimeError("The preserved blank Grease Pencil seed was not loaded")
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
if obj.mode != "OBJECT":
    bpy.ops.object.mode_set(mode="OBJECT")
bpy.context.scene.frame_set(1)

curve_a = [
    (-2.8, 0.1, 0.0), (-2.4, 0.65, 0.0), (-1.8, 1.04, 0.0),
    (-1.05, 1.22, 0.0), (-0.25, 1.17, 0.0), (0.55, 0.83, 0.0),
    (1.25, 0.36, 0.0), (1.9, 0.05, 0.0), (2.55, 0.23, 0.0),
]
curve_b = [
    (-2.35, -0.72, 0.0), (-1.72, -0.95, 0.0), (-1.02, -1.1, 0.0),
    (-0.25, -1.16, 0.0), (0.55, -1.1, 0.0), (1.31, -0.88, 0.0),
    (2.17, -0.62, 0.0),
]


def counts():
    current = bpy.data.objects.get("UI Brush Scratch")
    frame = current.data.layers.active.current_frame()
    return [len(stroke.points) for stroke in frame.drawing.strokes]


report = {
    "version": bpy.app.version_string,
    "background": bpy.app.background,
    "route": "Blender Grease Pencil data operator, not OS pointer brush input",
    "seed": bpy.data.filepath,
    "curve_a": curve_a,
    "curve_b": curve_b,
    "before": counts(),
}
assert report["before"] == [], report["before"]
report["add_a"] = list(bpy.ops.wtsc.add_native_curve(points_json=json.dumps(curve_a), base_radius=0.048))
report["after_a"] = counts()
assert report["after_a"] == [9], report["after_a"]
area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
region = next(region for region in area.regions if region.type == "WINDOW")
with bpy.context.temp_override(window=bpy.context.window, area=area, region=region):
    report["checkpoint_a"] = list(bpy.ops.ed.undo_push(message="native curve A"))
report["add_b"] = list(bpy.ops.wtsc.add_native_curve(points_json=json.dumps(curve_b), base_radius=0.06))
report["after_b"] = counts()
assert report["after_b"] == [9, 7], report["after_b"]

with bpy.context.temp_override(window=bpy.context.window, area=area, region=region):
    report["checkpoint_b"] = list(bpy.ops.ed.undo_push(message="native curve B"))
    report["undo_poll"] = bpy.ops.ed.undo.poll()
    report["undo"] = list(bpy.ops.ed.undo())
report["after_undo"] = counts()
assert report["after_undo"] == [9], report["after_undo"]

report["repeat_b"] = list(bpy.ops.wtsc.add_native_curve(points_json=json.dumps(curve_b), base_radius=0.06))
report["after_repeat"] = counts()
assert report["after_repeat"] == [9, 7], report["after_repeat"]

out = root / "native" / "GP_Native_Curve_Proof_v060.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(out), compress=True)
report["saved"] = str(out)
(root / "evidence" / "NATIVE_CURVE_GUI_TEST_v060.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("NATIVE_CURVE_GUI_TEST", json.dumps({k: v for k, v in report.items()
                                           if k not in ("curve_a", "curve_b")}))
