"""Register one manually authored source-pixel point list as native Blender GP.

Usage: blender -b -t 2 --python build_source_phase_v064.py -- PHASE_NUMBER
No contour or pose points are generated here. This only converts documented crop
pixel coordinates into a common native camera space and renders that drawing.
"""

import bpy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
phase = int(sys.argv[sys.argv.index("--")+1])
if not 1 <= phase <= 12:
    raise RuntimeError("Phase must be 1..12")
spec_path = root / "phase_specs" / f"phase{phase:02d}.json"
spec = json.loads(spec_path.read_text(encoding="utf-8"))
if spec["phase"] != phase or spec["crop_size"] != [310,588]:
    raise RuntimeError("Phase spec or crop dimensions mismatch")
expected_rect = [31+(phase-1)*310,32,341+(phase-1)*310,620]
if spec["source_crop_xyxy"] != expected_rect:
    raise RuntimeError("Source rectangle mismatch")
source_jpeg = root.parent / "three_way_walk_test_v057" / "reference" / "Muybridge_Animal_Locomotion_Plate_2_1887.jpg"
source_sha = hashlib.sha256(source_jpeg.read_bytes()).hexdigest()
if source_sha != spec["source_sha256"]:
    raise RuntimeError("Retained source JPEG hash mismatch")
crop_path = root / "reference" / f"phase{phase:02d}_source_crop.png"
crop_sha = hashlib.sha256(crop_path.read_bytes()).hexdigest()
preflight = json.loads((root / "evidence" / "SOURCE_CROPS_VERIFIED_v064.json").read_text(encoding="utf-8"))
if preflight["original_source_sha256"] != source_sha or preflight["crop_sha256"][f"phase{phase:02d}"] != crop_sha:
    raise RuntimeError("Source crop was not pixel-verified against the original JPEG")

operator_file = root.parent / "native_curve_bridge_v060" / "scripts" / "native_curve_author.py"
module_spec = importlib.util.spec_from_file_location("wtsc_native_curve_author_v060", operator_file)
module = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(module)

bpy.ops.wm.read_factory_settings(use_empty=True)
module.register()
scene = bpy.context.scene
scene.frame_set(1)
gp = bpy.data.grease_pencils.new(f"Muybridge Plate 2 Phase {phase:02d} Manual Trace")
obj = bpy.data.objects.new(f"Phase {phase:02d} Manual GP Contours",gp)
scene.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
layer = gp.layers.new(f"Phase {phase:02d} Visible Contours",set_active=True)
layer.frames.new(1)
material = bpy.data.materials.new("Trace Cyan - Source Anatomy Study")
bpy.data.materials.create_gpencil_data(material)
material.grease_pencil.color=(0.025,0.86,0.95,1.0)
material.grease_pencil.show_stroke=True
material.grease_pencil.show_fill=False
gp.materials.append(material)

def pixel_to_object(pixel):
    x,y=pixel
    if not (0<=x<310 and 0<=y<588):
        raise RuntimeError(f"Point outside source crop: {pixel}")
    return ((x-155.0)*0.01,(294.0-y)*0.01,0.0)

names=[]
counts=[]
for contour in spec["contours"]:
    points=contour["points"]
    if len(points)<2:
        raise RuntimeError(f"Contour too short: {contour['name']}")
    positions=[pixel_to_object(p) for p in points]
    radius=0.004 if any(word in contour["name"] for word in ("hand","finger","seam","hint","visible_short")) else 0.0055
    result=bpy.ops.wtsc.add_native_curve(points_json=json.dumps(positions),base_radius=radius)
    if result!={"FINISHED"}:
        raise RuntimeError(f"Native operator failed on {contour['name']}: {result}")
    names.append(contour["name"])
    counts.append(len(points))

drawing=gp.layers.active.current_frame().drawing
if len(drawing.strokes)!=len(spec["contours"]) or [len(s.points) for s in drawing.strokes]!=counts:
    raise RuntimeError("Native stroke count or point counts mismatch")
source_image=bpy.data.images.load(str(crop_path),check_existing=True)
source_image.pack()
obj["approved_source_sha256"]=source_sha
obj["source_phase"]=phase
obj["source_crop_xyxy"]=','.join(map(str,expected_rect))
obj["trace_method"]="individually authored photo-pixel contour points; no synthesis"

cam_data=bpy.data.cameras.new("Registered Source Pixel Camera")
cam_data.type="ORTHO"
cam_data.ortho_scale=5.88
cam=bpy.data.objects.new("Registered Source Pixel Camera",cam_data)
scene.collection.objects.link(cam)
cam.location=(0,0,10)
scene.camera=cam
scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=620
scene.render.resolution_y=1176
scene.render.resolution_percentage=100
scene.render.threads_mode="FIXED"
scene.render.threads=2
scene.render.film_transparent=True
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGBA"
scene.view_settings.view_transform="Standard"
scene.render.filepath=str(root / "previews" / f"phase{phase:02d}_native_rgba_v064.png")
for area in bpy.context.screen.areas:
    if area.type=="VIEW_3D":
        area.spaces.active.region_3d.view_perspective="ORTHO"
        area.spaces.active.region_3d.view_rotation=(1,0,0,0)
        area.spaces.active.region_3d.view_location=(0,0,0)
        area.spaces.active.region_3d.view_distance=6.5
native=root / "native" / f"Muybridge_Phase{phase:02d}_Manual_Trace_v064.blend"
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
bpy.ops.render.render(write_still=True)
report={
    "blender_version":bpy.app.version_string,
    "phase":phase,
    "source_sha256_verified":True,
    "source_crop_exact_pixels_verified":True,
    "source_crop_xyxy":expected_rect,
    "native_path":str(native),
    "render_path":scene.render.filepath,
    "contour_names":names,
    "point_counts":counts,
    "stroke_count":len(names),
    "total_manually_authored_points":sum(counts),
    "registration":"X=(source_x-155)*0.01; Y=(294-source_y)*0.01; 620x1176 camera ortho_scale 5.88",
    "no_interpolation_or_pose_synthesis":True,
}
(root / "evidence" / f"PHASE{phase:02d}_NATIVE_BUILD_v064.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("SOURCE_PHASE_NATIVE_BUILD_V064",json.dumps(report))
