"""Register the manually authored phase-8 correction as editable Blender art.

Every body silhouette/mark comes from pose8_spec_v066.py. The painted A head is
retained as a clearly identified, front-facing raster art element; it is not
presented as a freshly painted contour or as a rotated head card.
"""

import bpy
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pose8_spec_v066 import POSE

root = Path(__file__).resolve().parents[1]
prior = root.parent / "boy_reference_adaptation_v065"
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 660
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.threads_mode = "FIXED"
scene.render.threads = 2
scene.render.film_transparent = True
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.view_settings.view_transform = "Standard"

def linear(v):
    v = v / 255
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

materials = {}
def ink(color):
    if color not in materials:
        raw = [int(color[i:i+2], 16) for i in (1, 3, 5)]
        base = [linear(v) for v in raw]
        mat = bpy.data.materials.new("Painted contour " + color)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        geometry = nodes.new("ShaderNodeNewGeometry")
        broad = nodes.new("ShaderNodeTexNoise")
        broad.inputs["Scale"].default_value = 3.2
        broad.inputs["Detail"].default_value = 3.0
        broad.inputs["Roughness"].default_value = 0.7
        mat.node_tree.links.new(geometry.outputs["Position"], broad.inputs["Vector"])
        wash = nodes.new("ShaderNodeMixRGB")
        wash.blend_type = "MIX"
        wash.inputs[1].default_value = (*[min(1, c * 0.87) for c in base], 1)
        wash.inputs[2].default_value = (*[min(1, c * 1.13) for c in base], 1)
        mat.node_tree.links.new(broad.outputs["Fac"], wash.inputs[0])
        emit = nodes.new("ShaderNodeEmission")
        mat.node_tree.links.new(wash.outputs["Color"], emit.inputs["Color"])
        output = nodes.new("ShaderNodeOutputMaterial")
        mat.node_tree.links.new(emit.outputs["Emission"], output.inputs["Surface"])
        mat.diffuse_color = (*base, 1)
        materials[color] = mat
    return materials[color]

def xy(point):
    x, y = point
    if not (0 <= x < 660 and 0 <= y < 720):
        raise ValueError(point)
    return ((x - 330) * .01, (360 - y) * .01)

for name, depth, color, points in POSE["fills"]:
    mesh = bpy.data.meshes.new(name + " | manual fill")
    mesh.from_pydata([(*xy(p), depth * .01) for p in points], [], [tuple(range(len(points)))])
    mesh.update()
    obj = bpy.data.objects.new("C8 v066 | " + name, mesh)
    scene.collection.objects.link(obj)
    mesh.materials.append(ink(color))
    obj["authoring"] = "manually placed editable fill points"
    obj["reference_phase"] = 8

for name, depth, color, width, points in POSE["lines"]:
    curve = bpy.data.curves.new(name + " | manual stroke", type="CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 1
    curve.bevel_depth = width * .005
    curve.bevel_resolution = 1
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for target, point in zip(spline.points, points):
        x, y = xy(point)
        target.co = (x, y, depth * .01 + .001, 1)
    obj = bpy.data.objects.new("C8 v066 | " + name, curve)
    scene.collection.objects.link(obj)
    curve.materials.append(ink(color))
    obj["authoring"] = "manually placed editable stroke points"

head_path = root / "reference" / "Retained_A006_Painted_Head_Dark_Safe_v066.png"
head = bpy.data.images.load(str(head_path))
head.pack()
head.use_fake_user = True
mat = bpy.data.materials.new("RETAINED v053 A006 head raster — not redraw")
mat.use_nodes = True
mat.surface_render_method = "DITHERED"
nodes = mat.node_tree.nodes
nodes.clear()
tex = nodes.new("ShaderNodeTexImage")
tex.image = head
transparent = nodes.new("ShaderNodeBsdfTransparent")
emission = nodes.new("ShaderNodeEmission")
mix = nodes.new("ShaderNodeMixShader")
output = nodes.new("ShaderNodeOutputMaterial")
mat.node_tree.links.new(tex.outputs["Color"], emission.inputs["Color"])
mat.node_tree.links.new(tex.outputs["Alpha"], mix.inputs[0])
mat.node_tree.links.new(transparent.outputs[0], mix.inputs[1])
mat.node_tree.links.new(emission.outputs[0], mix.inputs[2])
mat.node_tree.links.new(mix.outputs[0], output.inputs["Surface"])
mesh = bpy.data.meshes.new("Retained head image quad")
mesh.from_pydata([(-3.3,3.6,.15),(3.3,3.6,.15),(3.3,-3.6,.15),(-3.3,-3.6,.15)], [], [(0,1,2,3)])
mesh.update()
mesh.uv_layers.new(name="Full frame retained art UV")
for uv, value in zip(mesh.uv_layers.active.data, ((0,1),(1,1),(1,0),(0,0))):
    uv.uv = value
obj = bpy.data.objects.new("RETAINED v053 A006 HEAD | front-facing image", mesh)
scene.collection.objects.link(obj)
mesh.materials.append(mat)
obj["authoring"] = "retained approved raster; alpha isolated from A; not a new hand drawing"

for source in (
    prior / "reference" / "A_v053_frame006.png",
    root.parent / "muybridge_source_sequence_v064" / "reference" / "phase08_source_crop.png",
):
    im = bpy.data.images.load(str(source))
    im.pack()
    im.use_fake_user = True

camera_data = bpy.data.cameras.new("A-matched 660x720 camera")
camera_data.type = "ORTHO"
camera_data.ortho_scale = 7.2
camera = bpy.data.objects.new("A-matched 660x720 camera", camera_data)
scene.collection.objects.link(camera)
camera.location = (0, 0, 15)
scene.camera = camera

native = root / "native" / "Boy_Phase08_Manual_Painted_Contour_Correction_v066.blend"
render = root / "previews" / "Boy_Phase08_Native_Correction_v066.png"
native.parent.mkdir(parents=True, exist_ok=True)
render.parent.mkdir(parents=True, exist_ok=True)
scene.render.filepath = str(render)
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(native), compress=True)
bpy.ops.render.render(write_still=True)
report = {
    "native": str(native), "render": str(render),
    "blender": bpy.app.version_string,
    "editable_fill_count": len(POSE["fills"]),
    "editable_stroke_count": len(POSE["lines"]),
    "fill_points": sum(len(v[3]) for v in POSE["fills"]),
    "stroke_points": sum(len(v[4]) for v in POSE["lines"]),
    "leg_axes_from_v065": POSE["joints"],
    "head": "retained v053 A006 raster, front-facing packed alpha plane; not a hand redraw",
    "material": "manually authored shapes with low-amplitude procedural color wash; no generated contours",
}
(root / "evidence" / "PHASE08_NATIVE_BUILD_v066.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print("PHASE08_NATIVE_BUILD_V066", json.dumps(report))
