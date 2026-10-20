"""Cold-open both saved pose files and check editability and framing."""

import bpy
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from pose_specs import POSES

results = []
for phase in (6, 8):
    source = ROOT / "native" / f"Boy_Phase{phase:02d}_Point_Authored_Redraw_v065.blend"
    bpy.ops.wm.open_mainfile(filepath=str(source))
    spec = POSES[phase]
    meshes = [ob for ob in bpy.data.objects if ob.type == "MESH"]
    curves = [ob for ob in bpy.data.objects if ob.type == "CURVE"]
    actual_points = sum(len(ob.data.vertices) for ob in meshes)
    actual_points += sum(sum(len(s.points) for s in ob.data.splines) for ob in curves)
    expected_points = sum(len(row[3]) for row in spec["fills"])
    expected_points += sum(len(row[4]) for row in spec["lines"])
    scene = bpy.context.scene
    joints = spec["joints"]
    def length(a, b):
        return round(math.dist(joints[a], joints[b]), 2)
    result = {
        "phase": phase,
        "file": str(source),
        "blender_version": bpy.app.version_string,
        "mesh_fills": len(meshes),
        "editable_detail_curves": len(curves),
        "authored_points_actual": actual_points,
        "authored_points_expected": expected_points,
        "camera": scene.camera.name if scene.camera else None,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
        "film_transparent": scene.render.film_transparent,
        "packed_reference_images": [im.name for im in bpy.data.images if im.packed_file],
        "segment_pixels": {
            "rear_or_trailing_thigh": length("hip", "rear_knee" if phase == 6 else "trailing_knee"),
            "rear_or_trailing_shin": length("rear_knee", "rear_ankle") if phase == 6 else length("trailing_knee", "trailing_ankle"),
            "front_thigh": length("hip", "front_knee") if "front_knee" in joints else length("hip", "stance_knee"),
            "front_shin": length("front_knee", "front_ankle") if "front_knee" in joints else length("stance_knee", "stance_ankle"),
        },
    }
    result["technical_pass"] = (
        len(meshes) == len(spec["fills"])
        and len(curves) == len(spec["lines"])
        and actual_points == expected_points
        and result["resolution"] == [660, 720]
        and bool(scene.camera)
        and len(result["packed_reference_images"]) >= 2
    )
    results.append(result)

out = ROOT / "evidence" / "TWO_POSE_COLD_OPEN_v065.json"
out.write_text(json.dumps(results, indent=2), encoding="utf-8")
print("TWO_POSE_COLD_OPEN_V065", json.dumps(results))
if not all(r["technical_pass"] for r in results):
    raise RuntimeError("Native cold-open validation failed")
