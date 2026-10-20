"""Create a blank, separate Grease Pencil file for real pointer-input tests."""

import bpy
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = root / "native" / "GP_UI_Brush_Blank_v059.blend"
out.parent.mkdir(parents=True, exist_ok=True)

for obj in tuple(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
gp = bpy.data.grease_pencils.new("UI Brush Scratch")
obj = bpy.data.objects.new("UI Brush Scratch", gp)
bpy.context.scene.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
layer = gp.layers.new("Pointer Input", set_active=True)
layer.frames.new(1)
material = bpy.data.materials.new("UI Test Black")
bpy.data.materials.create_gpencil_data(material)
material.grease_pencil.color = (0.02, 0.02, 0.02, 1.0)
gp.materials.append(material)
bpy.ops.object.mode_set(mode="PAINT_GREASE_PENCIL")
for area in bpy.context.screen.areas:
    if area.type == "VIEW_3D":
        space = area.spaces.active
        space.region_3d.view_perspective = "ORTHO"
        space.region_3d.view_rotation = (1, 0, 0, 0)
        space.region_3d.view_location = (0, 0, 0)
        space.region_3d.view_distance = 8
        space.shading.type = "SOLID"
        break
bpy.context.scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out), compress=True)
print("SCRATCH_READY", out, "mode", obj.mode, "brush", bpy.context.tool_settings.gpencil_paint.brush.name)
