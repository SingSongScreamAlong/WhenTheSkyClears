"""Fresh native reopen and render of exactly one review still."""
import bpy
import json
from pathlib import Path

root = Path(r"WTSC_LOCAL_WORKSPACE")
scene = bpy.data.scenes["WTSC_VILLAGE_STILL_v012"]
bpy.context.window.scene = scene
assert scene.frame_start == scene.frame_end == 1
assert (scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage) == (3840, 2160, 100)
assert len(scene.objects) == 6
pair = next(o for o in scene.objects if o.type == "GREASEPENCIL")
assert pair.animation_data is None
assert all(tuple(m.grease_pencil.fill_color) == (0, 0, 0, 1) for m in pair.data.materials)
assert all(not l.use_lights for l in pair.data.layers)
images = [i for i in bpy.data.images if i.type == "IMAGE" and i.size[0] > 0]
assert images and all(i.packed_file for i in images)
report = {
    "file": bpy.data.filepath,
    "scene": scene.name,
    "blender": bpy.app.version_string,
    "resolution": [3840, 2160],
    "frames": [1, 1],
    "objects": [{"name": o.name, "type": o.type, "location": list(o.location)} for o in scene.objects],
    "images": [{"name": i.name, "size": list(i.size), "packed": bool(i.packed_file)} for i in images],
    "pure_black_light_independent_gp": True,
    "animation": "None",
    "still_approval": "Pending Conrad's review",
    "scrolling_review": "Not started; awaits still approval",
}
(root / "notes/village_lookdev/native_reopen_v012.json").write_text(json.dumps(report, indent=2))
print("SINGLE_FRAME_NATIVE_REOPEN_VERIFIED", json.dumps(report), flush=True)
scene.frame_set(1)
bpy.ops.render.render(write_still=True, scene=scene.name)
print("ONE_4K_STILL_RENDER_COMPLETE", scene.render.filepath, flush=True)
