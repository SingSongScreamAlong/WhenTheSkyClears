"""Fix only newly created v012 cards: native importer selects quaternion rotation."""
import bpy
import json
import math
from pathlib import Path

root = Path(r"WTSC_LOCAL_WORKSPACE")
scene = bpy.data.scenes["WTSC_VILLAGE_STILL_v012"]
for obj in scene.objects:
    if obj.type == "MESH":
        obj.rotation_mode = "XYZ"
        obj.rotation_euler = (math.pi / 2, 0, 0)
with bpy.context.temp_override(scene=scene, view_layer=scene.view_layers[0]):
    scene.view_layers[0].update()
output = root / "shots/world/WTSC_Village_Still_Review_v012.blend"
note = bpy.data.texts["START HERE | v012 still review"]
bpy.data.libraries.write(str(output), {scene, note}, path_remap="RELATIVE", fake_user=True, compress=True)
evidence = json.loads((root / "notes/village_lookdev/native_assembly_v012.json").read_text())
evidence["objects"] = [{"name": o.name, "type": o.type, "location": list(o.location), "dimensions": list(o.dimensions)} for o in scene.objects]
evidence["native_import_alignment"] = "Image importer uses quaternion mode; set XYZ explicitly for side-on XZ cards."
(root / "notes/village_lookdev/native_assembly_v012.json").write_text(json.dumps(evidence, indent=2))
print(json.dumps(evidence))
