"""Fresh normal-file readback; performs no render and no scene mutation."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

root = Path(r"WTSC_LOCAL_WORKSPACE")
scene = bpy.context.scene
assert scene.name == "WTSC_VILLAGE_STILL_v013", scene.name
assert len(bpy.data.scenes) == 1
assert scene.frame_start == scene.frame_end == 1
assert scene.render.resolution_x == 3840 and scene.render.resolution_y == 2160
assert scene.render.resolution_percentage == 100
assert scene.camera and len(scene.objects) == 6
depsgraph = bpy.context.evaluated_depsgraph_get()
depsgraph.update()
objects = []
for obj in scene.objects:
    evaluated = obj.evaluated_get(depsgraph)
    corners = [evaluated.matrix_world @ Vector(c) for c in evaluated.bound_box]
    world_extent = [max(c[i] for c in corners) - min(c[i] for c in corners) for i in range(3)]
    objects.append({"name": obj.name, "type": obj.type, "location": list(obj.location),
                    "local_axis_dimensions": list(evaluated.dimensions),
                    "world_axis_extent": world_extent,
                    "has_animation": bool(obj.animation_data)})
    assert not obj.animation_data
    if obj.type == "MESH":
        assert world_extent[2] > 1 and world_extent[1] < .001, world_extent
pair = next(o for o in scene.objects if o.type == "GREASEPENCIL")
assert all(not l.use_lights for l in pair.data.layers)
assert all(tuple(m.grease_pencil.fill_color) == (0, 0, 0, 1) for m in pair.data.materials)
images = [i for i in bpy.data.images if i.type == "IMAGE" and i.size[0]]
assert len(images) == 3 and all(i.packed_file for i in images)
result = {"file": bpy.data.filepath, "active_scene": scene.name, "scenes": list(bpy.data.scenes.keys()),
          "resolution": [3840, 2160], "frames": [1, 1], "objects": objects,
          "all_three_rasters_packed": True, "flat_black_gp": True,
          "source_raster_sizes": [list(i.size) for i in images],
          "render_started": False, "scrolling_started": False,
          "approval": "Still review pending"}
(root / "notes/village_lookdev/native_reopen_v013.json").write_text(json.dumps(result, indent=2))
print("NATIVE_SOURCE_REOPEN_VERIFIED", json.dumps(result))
