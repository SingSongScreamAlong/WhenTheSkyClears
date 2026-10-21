"""Render manually specified Muybridge contours as native Grease Pencil.

The contour vertices live in phase06_manual_contours.json and were placed by
eye on the reference crop. This script only registers them in Blender's camera
coordinate system; it does not discover, synthesize or interpolate anatomy.
"""

import bpy
import hashlib
import importlib.util
import json
from pathlib import Path


root = Path(__file__).resolve().parents[1]
spec = json.loads((root / "reference" / "phase06_manual_contours.json").read_text(encoding="utf-8"))
source = root.parent / "three_way_walk_test_v057" / "reference" / "Muybridge_Animal_Locomotion_Plate_2_1887.jpg"
actual_sha = hashlib.sha256(source.read_bytes()).hexdigest()
if actual_sha != spec["source_sha256"]:
    raise RuntimeError("Approved source hash changed")

operator_file = root.parent / "native_curve_bridge_v060" / "scripts" / "native_curve_author.py"
module_spec = importlib.util.spec_from_file_location("wtsc_native_curve_author_v060", operator_file)
module = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(module)

bpy.ops.wm.read_factory_settings(use_empty=True)
module.register()
scene = bpy.context.scene
scene.frame_set(1)
gp = bpy.data.grease_pencils.new("Muybridge Plate 2 Phase 06 Manual Trace")
obj = bpy.data.objects.new("Phase 06 Manual GP Contours", gp)
scene.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
layer = gp.layers.new("Phase 06 Visible Contours", set_active=True)
layer.frames.new(1)

material = bpy.data.materials.new("Trace Cyan - Source Anatomy Study")
bpy.data.materials.create_gpencil_data(material)
material.grease_pencil.color = (0.025, 0.86, 0.95, 1.0)
material.grease_pencil.show_stroke = True
material.grease_pencil.show_fill = False
gp.materials.append(material)


def pixel_to_object(pixel):
    # Registration only: one source pixel is 0.01 Blender world units.
    return ((pixel[0] - 155.0) * 0.01, (294.0 - pixel[1]) * 0.01, 0.0)


names = []
counts = []
for contour in spec["contours"]:
    positions = [pixel_to_object(pixel) for pixel in contour["points"]]
    radius = 0.0055 if contour["name"] not in (
        "far_arm_visible", "hip_to_front_thigh_seam", "hanging_hand_fingers"
    ) else 0.004
    outcome = bpy.ops.wtsc.add_native_curve(points_json=json.dumps(positions), base_radius=radius)
    if outcome != {"FINISHED"}:
        raise RuntimeError(f"Native operator failed on {contour['name']}: {outcome}")
    names.append(contour["name"])
    counts.append(len(positions))

drawing = gp.layers.active.current_frame().drawing
if len(drawing.strokes) != len(spec["contours"]):
    raise RuntimeError("Contours connected or stroke count changed")
if [len(stroke.points) for stroke in drawing.strokes] != counts:
    raise RuntimeError("Manually specified point counts changed")

source_image = bpy.data.images.load(str(root / "reference" / "phase06_source_crop.png"), check_existing=True)
source_image.pack()
obj["approved_source_sha256"] = actual_sha
obj["source_phase"] = 6
obj["source_crop_xyxy"] = "1581,32,1891,620"
obj["trace_method"] = "manual point-authored visible contours; no pose synthesis"

cam_data = bpy.data.cameras.new("Registered Source Pixel Camera")
cam_data.type = "ORTHO"
cam_data.ortho_scale = 5.88
cam = bpy.data.objects.new("Registered Source Pixel Camera", cam_data)
scene.collection.objects.link(cam)
cam.location = (0.0, 0.0, 10.0)
scene.camera = cam
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 620
scene.render.resolution_y = 1176
scene.render.resolution_percentage = 100
scene.render.threads_mode = "FIXED"
scene.render.threads = 2
scene.render.film_transparent = True
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.view_settings.view_transform = "Standard"
scene.render.filepath = str(root / "previews" / "phase06_native_trace_rgba.png")

for area in bpy.context.screen.areas:
    if area.type == "VIEW_3D":
        area.spaces.active.region_3d.view_perspective = "ORTHO"
        area.spaces.active.region_3d.view_rotation = (1, 0, 0, 0)
        area.spaces.active.region_3d.view_location = (0, 0, 0)
        area.spaces.active.region_3d.view_distance = 6.5

native_path = root / "native" / "Muybridge_Phase06_Manual_Trace_v061.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(native_path), compress=True)
bpy.ops.render.render(write_still=True)
report = {
    "blender_version": bpy.app.version_string,
    "source_sha256_verified": True,
    "source_crop": spec["source_crop_xyxy"],
    "phase": 6,
    "native_path": str(native_path),
    "render_path": scene.render.filepath,
    "contour_count": len(names),
    "contour_names": names,
    "point_counts": counts,
    "total_manually_specified_points": sum(counts),
    "registration": "X=(source_x-155)*0.01; Y=(294-source_y)*0.01; camera 620x1176 ortho_scale 5.88",
    "route": "temporary Blender-native Grease Pencil operator, not OS pointer delivery",
}
(root / "evidence" / "PHASE06_NATIVE_BUILD_v061.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("PHASE06_NATIVE_BUILD", json.dumps({k: v for k, v in report.items() if k != "contour_names"}))
