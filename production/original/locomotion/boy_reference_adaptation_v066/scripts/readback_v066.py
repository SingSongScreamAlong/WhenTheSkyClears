"""Cold-open and render the saved one-pose native, checking editability."""

import bpy
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "scripts"))
from pose8_spec_v066 import POSE

native = root / "native" / "Boy_Phase08_Manual_Painted_Contour_Correction_v066.blend"
bpy.ops.wm.open_mainfile(filepath=str(native))
scene = bpy.context.scene
objects = list(bpy.data.objects)
fills = [obj for obj in objects if obj.type == "MESH" and obj.get("authoring") == "manually placed editable fill points"]
strokes = [obj for obj in objects if obj.type == "CURVE" and obj.get("authoring") == "manually placed editable stroke points"]
head = [obj for obj in objects if obj.get("authoring", "").startswith("retained approved raster")]
packed = [img.name for img in bpy.data.images if img.packed_file]
checks = {
    "fill_count": len(fills) == len(POSE["fills"]),
    "stroke_count": len(strokes) == len(POSE["lines"]),
    "fill_points": sum(len(obj.data.vertices) for obj in fills) == sum(len(v[3]) for v in POSE["fills"]),
    "stroke_points": sum(sum(len(s.points) for s in obj.data.splines) for obj in strokes) == sum(len(v[4]) for v in POSE["lines"]),
    "retained_head_plane": len(head) == 1,
    "packed_images": len(packed) >= 3,
    "matched_frame": (scene.render.resolution_x,scene.render.resolution_y) == (660,720),
    "camera": bool(scene.camera and scene.camera.data.type == "ORTHO" and abs(scene.camera.data.ortho_scale - 7.2) < 1e-5),
    "transparent_output": scene.render.film_transparent,
}
result = {"native": str(native), "blender": bpy.app.version_string, "checks": checks,
          "all_technical_checks_passed": all(checks.values()), "packed_images": packed,
          "mesh_fills": len(fills), "editable_strokes": len(strokes),
          "camera_name": scene.camera.name if scene.camera else None,
          "camera_ortho_scale": scene.camera.data.ortho_scale if scene.camera else None}
out = root / "evidence" / "PHASE08_COLD_OPEN_v066.json"
out.write_text(json.dumps(result, indent=2), encoding="utf-8")
if not result["all_technical_checks_passed"]:
    raise RuntimeError(json.dumps(result))
scene.render.filepath = str(root / "evidence" / "Phase08_Cold_Open_Render_v066.png")
bpy.ops.render.render(write_still=True)
print("PHASE08_COLD_OPEN_V066", json.dumps(result))
