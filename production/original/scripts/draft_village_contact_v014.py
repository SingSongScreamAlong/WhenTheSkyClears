import bpy
import json
import sys
from pathlib import Path

root = Path(r"WTSC_LOCAL_WORKSPACE")
sys.path.insert(0, str(root / "scripts"))
from village_still_refinements_v014 import ground_contacts
scene = bpy.context.scene
report = ground_contacts(scene)
camera = scene.camera.copy()
camera.data = scene.camera.data.copy()
camera.name = "v014 | Contact draft camera"
scene.collection.objects.link(camera)
camera.data.lens = 150
camera.data.shift_x = -.45
camera.data.shift_y = -.388125
scene.camera = camera
out = root / "renders/village_lookdev/v014"
out.mkdir(parents=True, exist_ok=True)
scene.render.filepath = str(out / "Contact_Draft_v014_4K.png")
assert not Path(scene.render.filepath).exists()
bpy.ops.render.render(write_still=True, scene=scene.name)
(root / "notes/village_lookdev/contact_draft_v014.json").write_text(json.dumps(report, indent=2))
print("CONTACT_DRAFT_COMPLETE", json.dumps(report))
