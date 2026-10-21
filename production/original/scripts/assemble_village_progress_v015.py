"""Current progress frame; full world animation continues after this source checkpoint."""
import bpy
import json
import sys
from pathlib import Path

root = Path(r"WTSC_LOCAL_WORKSPACE")
sys.path.insert(0, str(root / "scripts"))
from painterly_pair_native_v015 import apply_painterly_pair
from village_still_refinements_v014 import ground_contacts, detail_tile
scene = bpy.context.scene
assert scene.name == "WTSC_VILLAGE_STILL_v013"
camera = scene.camera
camera_pose = [list(r) for r in camera.matrix_world]
character = apply_painterly_pair(scene, root)
contacts = ground_contacts(scene, character["soles"])
tiles = [
    detail_tile(scene.objects["v013 | Painted village"], root / "sets/village_lookdev/v014/Bakery_Detail_Repaint.png", [.325,.68,.13,.67], "Bakery newly painted detail"),
    detail_tile(scene.objects["v013 | Walking path"], root / "sets/village_lookdev/v014/Path_Detail_Repaint.png", [.25,.46,.06,.22], "Path newly painted detail"),
]
scene.name = "WTSC_VILLAGE_PROGRESS_v015"
scene["status"] = "Progress frame for authorized animated trailer world pass. Not an approval gate."
scene["scope"] = "Current village staging, corrected contact, local paint detail and near-age painterly held children. World motion work continues."
scene["latest_user_direction"] = "Animate the world; children held; painterly dark figures with subtle gray/white-eye accents; boy slightly taller/older; visible depth and detail separation."
scene["reference_status"] = "PROVISIONAL: exact originally approved ink-and-wash image still missing. User likes current direction."
for obj in scene.objects:
    obj.name = obj.name.replace("v013 |", "v015 |")
out = root / "renders/village_lookdev/v015"
out.mkdir(parents=True, exist_ok=True)
wide = out / "Village_Progress_v015_Wide_4K.png"
scene.render.filepath = str(wide)
source = root / "shots/world/WTSC_Village_Progress_v015.blend"
assert not source.exists() and not wide.exists()
for text in bpy.data.texts:
    if text.name.startswith("START HERE"):
        text.clear()
        text.write("Current v015 progress village. Latest user instructions supersede the older still-only review gate.\n"
                   "Continue into the full 100-second world animation; keep child pose held.\n"
                   "Native editable GP boundary with matched painted fill. Boy slightly taller/older.\n"
                   "Four flat backdrop paintings, with two new local detail tiles. No modeled buildings claimed.\n"
                   "Exact original approved ink-and-wash reference is missing; direction remains provisional.\n")
assert camera_pose == [list(r) for r in camera.matrix_world]
bpy.ops.wm.save_as_mainfile(filepath=str(source))
bpy.ops.render.render(write_still=True, scene=scene.name)
detail_cam = camera.copy()
detail_cam.data = camera.data.copy()
detail_cam.name = "v015 | Contact and character inspection camera"
scene.collection.objects.link(detail_cam)
detail_cam.data.lens = 150
detail_cam.data.shift_x = -.45
detail_cam.data.shift_y = -.388125
scene.camera = detail_cam
scene.render.filepath = str(out / "Children_Contact_v015_4K.png")
bpy.ops.render.render(write_still=True, scene=scene.name)
scene.camera = camera
scene.render.filepath = str(wide)
report = {"source": str(source), "scene": scene.name, "wide": str(wide),
          "closeup": str(out / "Children_Contact_v015_4K.png"), "resolution": [3840,2160],
          "camera_unchanged_from_v013": True, "contacts": contacts, "detail_tiles": tiles,
          "characters": {k:v for k,v in character.items() if k not in ["points","uv"]},
          "provenance": "Native Blender renders. Existing source v013 opened read-only in a separate process and saved to a new file. No animation rendered yet in this checkpoint.",
          "world_animation": "Authorized and continuing. This progress frame is not a request to pause.",
          "reference": "PROVISIONAL exact approved reference missing"}
(root / "notes/village_lookdev/progress_v015.json").write_text(json.dumps(report,indent=2))
print("PROGRESS_WIDE_AND_CONTACT_COMPLETE", json.dumps(report), flush=True)
