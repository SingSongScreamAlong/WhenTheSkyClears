"""Editable-data path proof from explicit samples; NOT mouse/pen brush input.

No character contour or animation is generated here. The two sample lists
are fixed test shapes chosen to verify stroke separation and persistence.
"""

import bpy
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
native = root / "native"
previews = root / "previews"
evidence = root / "evidence"
for folder in (native, previews, evidence):
    folder.mkdir(parents=True, exist_ok=True)

scene = bpy.context.scene
for old in tuple(bpy.data.objects):
    bpy.data.objects.remove(old, do_unlink=True)

gp = bpy.data.grease_pencils.new("GP Input Path Evidence")
obj = bpy.data.objects.new("GP Input Path Evidence", gp)
scene.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
layer = gp.layers.new("Explicit Samples", set_active=True)
frame = layer.frames.new(1)
drawing = frame.drawing

ink = bpy.data.materials.new("Matte Black Test Ink")
bpy.data.materials.create_gpencil_data(ink)
ink.grease_pencil.color = (0.018, 0.018, 0.018, 1.0)
ink.grease_pencil.show_stroke = True
ink.grease_pencil.show_fill = False
gp.materials.append(ink)

cam_data = bpy.data.cameras.new("Proof Camera")
cam_data.type = "ORTHO"
cam_data.ortho_scale = 8.0
cam = bpy.data.objects.new("Proof Camera", cam_data)
scene.collection.objects.link(cam)
cam.location = (0.0, 0.0, 10.0)
scene.camera = cam
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 640
scene.render.resolution_y = 360
scene.render.resolution_percentage = 100
scene.render.threads_mode = "FIXED"
scene.render.threads = 2
scene.render.image_settings.file_format = "PNG"
scene.world.use_nodes = True
scene.world.node_tree.nodes.get("Background").inputs["Color"].default_value = (0.88, 0.88, 0.85, 1.0)
scene.frame_set(1)

straight = [(-2.6, 1.1, 0.0), (-2.0, 1.1, 0.0), (-1.4, 1.1, 0.0), (-0.8, 1.1, 0.0)]
curve = [(-2.5, 0.0, 0.0), (-1.8, 0.4, 0.0), (-1.1, 0.5, 0.0), (-0.4, 0.1, 0.0), (0.3, -0.2, 0.0), (1.0, 0.0, 0.0), (1.8, 0.5, 0.0), (2.5, 0.5, 0.0)]
separate = [(1.1, -1.2, 0.0), (1.5, -1.2, 0.0), (1.9, -1.2, 0.0)]

def set_points(stroke, positions, radius):
    for point, coords in zip(stroke.points, positions):
        point.position = coords
        point.radius = radius
        point.opacity = 1.0
    stroke.material_index = 0

report = {"version": bpy.app.version_string, "path": "direct Grease Pencil drawing data; not interactive brush", "before": len(drawing.strokes)}
drawing.add_strokes([len(straight)])
set_points(drawing.strokes[0], straight, 0.055)
report["straight_count"] = len(drawing.strokes)
report["straight_point_count"] = len(drawing.strokes[0].points)
bpy.ops.wm.save_as_mainfile(filepath=str(native / "GP_Data_Straight_v059.blend"), compress=True)
scene.render.filepath = str(previews / "GP_Data_Straight_v059.png")
bpy.ops.render.render(write_still=True)

drawing.remove_strokes(indices=[0])
report["after_explicit_remove"] = len(drawing.strokes)
report["removal_is_undo"] = False

drawing.add_strokes([len(curve), len(separate)])
set_points(drawing.strokes[0], curve, 0.055)
set_points(drawing.strokes[1], separate, 0.09)
report["final_stroke_count"] = len(drawing.strokes)
report["final_point_counts"] = [len(s.points) for s in drawing.strokes]
report["final_positions"] = [[list(p.position) for p in s.points] for s in drawing.strokes]
report["final_radii"] = [[p.radius for p in s.points] for s in drawing.strokes]
bpy.ops.wm.save_as_mainfile(filepath=str(native / "GP_Data_Two_Separate_v059.blend"), compress=True)
scene.render.filepath = str(previews / "GP_Data_Two_Separate_v059.png")
bpy.ops.render.render(write_still=True)

(evidence / "GP_DATA_PROOF.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("GP_DATA_PROOF_JSON", json.dumps({k:v for k,v in report.items() if k not in ("final_positions","final_radii")}))
