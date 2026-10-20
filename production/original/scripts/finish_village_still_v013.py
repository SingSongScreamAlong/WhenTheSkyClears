"""Refine the one review composition and save a normal editable Blender file."""
import bpy
import json
import math
from pathlib import Path

root = Path(r"WTSC_LOCAL_WORKSPACE")
scene = bpy.data.scenes["WTSC_VILLAGE_STILL_v012"]
bpy.context.window.scene = scene
scene.name = "WTSC_VILLAGE_STILL_v013"
scene.objects["v012 | Painted village"].location.x += 2.016
rear = scene.objects["v012 | Rear countryside"]
nt = rear.data.materials[0].node_tree
emit = next(n for n in nt.nodes if n.type == "EMISSION")
tex = next(n for n in nt.nodes if n.type == "TEX_IMAGE")
wash = nt.nodes.new("ShaderNodeMixRGB")
wash.name = "Distance wash"
wash.label = "Softer distant values; no glow on the children"
wash.blend_type = "MIX"
wash.inputs[0].default_value = .14
wash.inputs[2].default_value = (.35, .43, .5, 1)
nt.links.new(tex.outputs["Color"], wash.inputs[1])
nt.links.new(wash.outputs[0], emit.inputs[0])
for old in list(bpy.data.scenes):
    if old != scene:
        assert not old.objects, "Only remove the empty scene created by the library-file loader"
        bpy.data.scenes.remove(old)
scene.render.filepath = str(root / "renders/village_lookdev/Village_Still_v013_4K.png")
scene["iteration"] = "Single-frame v013: village moved right to clear child profiles; distant colors softened."
scene["approval"] = "Pending Conrad's still-frame approval. No scrolling or full-length render."
for obj in scene.objects:
    obj.name = obj.name.replace("v012 |", "v013 |")
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type == "VIEW_3D":
            area.spaces.active.region_3d.view_perspective = "CAMERA"
            area.spaces.active.shading.type = "MATERIAL"
pair = next(o for o in scene.objects if o.type == "GREASEPENCIL")
bpy.context.view_layer.update()
for obj in scene.objects:
    if obj.type == "MESH":
        assert obj.rotation_mode == "XYZ" and abs(obj.rotation_euler.x - math.pi / 2) < .0001
assert pair.animation_data is None
assert all(not l.use_lights for l in pair.data.layers)
assert (scene.frame_start, scene.frame_end) == (1, 1)
output = root / "shots/world/WTSC_Village_Still_Review_v013.blend"
assert not output.exists(), output
bpy.ops.wm.save_as_mainfile(filepath=str(output))
report = {
    "file": str(output),
    "blender": bpy.app.version_string,
    "scene": scene.name,
    "resolution": [3840, 2160],
    "frames": [1, 1],
    "objects": [{"name": o.name, "type": o.type, "location": list(o.location), "dimensions": list(o.dimensions)} for o in scene.objects],
    "images": [{"name": i.name, "size": list(i.size), "packed": bool(i.packed_file)}
               for i in bpy.data.images if i.type == "IMAGE" and i.size[0]],
    "native_camera": "Perspective, 50mm, side-on",
    "painted_planes": 4,
    "independent_depths_y": [-5, 2, 12, 40],
    "pure_black_light_independent_gp": True,
    "pose_changes": False,
    "animation": "None; one frame only",
    "reference_status": "Exact approved ink-and-wash image unavailable; inspected handoff image1 is provisional atmosphere reference",
    "art_approval": "Pending still review",
    "scrolling_test": "Not started; after still approval only",
}
(root / "notes/village_lookdev/native_source_v013.json").write_text(json.dumps(report, indent=2))
bpy.ops.render.render(write_still=True, scene=scene.name)
print("ONE_4K_REVIEW_FRAME_COMPLETE", json.dumps(report), flush=True)
