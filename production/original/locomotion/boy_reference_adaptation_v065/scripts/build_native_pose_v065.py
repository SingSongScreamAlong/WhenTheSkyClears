"""Build one editable point-authored boy pose as native Blender contours.

Every polygon and detail path is explicitly listed in pose_specs.py. This
script only registers those points as separate mesh/curve objects and renders
them at the 660x720 A-review camera scale; it generates no pose geometry.
"""

import bpy
import hashlib
import json
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pose_specs import POSES

root=Path(__file__).resolve().parents[1]
phase=int(sys.argv[sys.argv.index("--")+1])
if phase not in POSES:
    raise RuntimeError("Only the two explicitly authored phases are available")
spec=POSES[phase]

bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
scene.frame_set(1)
scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=660
scene.render.resolution_y=720
scene.render.resolution_percentage=100
scene.render.threads_mode="FIXED"
scene.render.threads=2
scene.render.film_transparent=True
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGBA"
scene.view_settings.view_transform="Standard"

def linear(c):
    c=c/255.0
    return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4

materials={}
def material(color):
    if color not in materials:
        channels=[int(color[i:i+2],16) for i in (1,3,5)]
        rgba=tuple(linear(c) for c in channels)+(1.0,)
        mat=bpy.data.materials.new(f"Ink/Paint {color}")
        mat.use_nodes=True
        nodes=mat.node_tree.nodes
        nodes.clear()
        emission=nodes.new("ShaderNodeEmission")
        emission.inputs["Color"].default_value=rgba
        emission.inputs["Strength"].default_value=1.0
        output=nodes.new("ShaderNodeOutputMaterial")
        mat.node_tree.links.new(emission.outputs["Emission"],output.inputs["Surface"])
        mat.diffuse_color=rgba
        materials[color]=mat
    return materials[color]

def xy(point):
    x,y=point
    if not (0<=x<660 and 0<=y<720):
        raise RuntimeError(f"Point outside 660x720 review frame: {point}")
    return ((x-330)*0.01,(360-y)*0.01)

part_records=[]
for name,layer,color,points in spec["fills"]:
    if len(points)<3:
        raise RuntimeError(f"Polygon {name} has too few points")
    positions=[(*xy(p),layer*0.01) for p in points]
    mesh=bpy.data.meshes.new(f"{name} | authored contour")
    mesh.from_pydata(positions,[],[tuple(range(len(positions)))])
    mesh.update()
    obj=bpy.data.objects.new(f"{phase:02d} | {name}",mesh)
    scene.collection.objects.link(obj)
    obj.data.materials.append(material(color))
    obj["method"]="individually point-authored filled contour"
    obj["source_phase"]=phase
    part_records.append({"name":name,"type":"MESH","points":len(points),"color":color})

for name,layer,color,width,points in spec["lines"]:
    if len(points)<2:
        raise RuntimeError(f"Detail path {name} has too few points")
    curve=bpy.data.curves.new(f"{name} | authored detail",type="CURVE")
    curve.dimensions="3D"
    curve.resolution_u=1
    curve.bevel_depth=width*0.005
    curve.bevel_resolution=1
    spline=curve.splines.new("POLY")
    spline.points.add(len(points)-1)
    for target,point in zip(spline.points,points):
        x,y=xy(point)
        target.co=(x,y,layer*0.01+0.001,1.0)
    obj=bpy.data.objects.new(f"{phase:02d} | {name}",curve)
    scene.collection.objects.link(obj)
    obj.data.materials.append(material(color))
    obj["method"]="individually point-authored detail path"
    obj["source_phase"]=phase
    part_records.append({"name":name,"type":"CURVE","points":len(points),"color":color,"width_pixels":width})

camera_data=bpy.data.cameras.new("Matched A Studio Camera")
camera_data.type="ORTHO"
camera_data.ortho_scale=7.2
camera=bpy.data.objects.new("Matched A Studio Camera",camera_data)
scene.collection.objects.link(camera)
camera.location=(0,0,15)
scene.camera=camera

source_crop=root.parent / "muybridge_source_sequence_v064" / "reference" / f"phase{phase:02d}_source_crop.png"
a_frame=root / "reference" / f"A_v053_frame{spec['reference_A_frame']:03d}.png"
for path in (source_crop,a_frame):
    if not path.exists():
        raise RuntimeError(f"Required comparison source missing: {path}")
    bpy.data.images.load(str(path),check_existing=True).pack()

scene.render.filepath=str(root / "previews" / f"Boy_Phase{phase:02d}_Native_Redraw_v065.png")
native=root / "native" / f"Boy_Phase{phase:02d}_Point_Authored_Redraw_v065.blend"
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
bpy.ops.render.render(write_still=True)

report={
    "phase":phase,
    "blender_version":bpy.app.version_string,
    "native_path":str(native),
    "render_path":scene.render.filepath,
    "reference_A_frame":spec["reference_A_frame"],
    "source_photo_phase":phase,
    "joint_guides":spec["joints"],
    "part_count":len(part_records),
    "polygon_count":len(spec["fills"]),
    "detail_path_count":len(spec["lines"]),
    "total_individually_authored_points":sum(p["points"] for p in part_records),
    "parts":part_records,
    "camera":"660x720 orthographic; ortho_scale=7.2; same frame coordinates as v053 A",
    "actual_A_frame_sha256":hashlib.sha256(a_frame.read_bytes()).hexdigest(),
    "actual_photo_crop_sha256":hashlib.sha256(source_crop.read_bytes()).hexdigest(),
    "method":"manual point-authored reference-based redraw; sampled palette; no puppet deformation, automatic trace, or generated inbetweens",
}
(root / "evidence" / f"BOY_PHASE{phase:02d}_NATIVE_BUILD_v065.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("BOY_REFERENCE_REDRAW_BUILD_V065",json.dumps({k:v for k,v in report.items() if k!="parts"}))
