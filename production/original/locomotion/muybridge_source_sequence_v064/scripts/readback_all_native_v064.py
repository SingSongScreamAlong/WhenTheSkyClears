"""Cold-open all isolated .blend files and verify every explicit source-pixel point."""

import bpy
import json
import math
from pathlib import Path

root=Path(__file__).resolve().parents[1]
reports=[]
for phase in range(1,13):
    native=root / "native" / f"Muybridge_Phase{phase:02d}_Manual_Trace_v064.blend"
    spec=json.loads((root / "phase_specs" / f"phase{phase:02d}.json").read_text(encoding="utf-8"))
    bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False)
    obj=bpy.data.objects.get(f"Phase {phase:02d} Manual GP Contours")
    if obj is None or obj.type!="GREASEPENCIL":
        raise RuntimeError(f"Phase {phase}: editable GP object missing")
    layers=list(obj.data.layers)
    frames=list(layers[0].frames)
    strokes=list(frames[0].drawing.strokes)
    expected=[len(c["points"]) for c in spec["contours"]]
    observed=[len(s.points) for s in strokes]
    errors=[]
    for contour,stroke in zip(spec["contours"],strokes):
        for pixel,point in zip(contour["points"],stroke.points):
            target=((pixel[0]-155.0)*0.01,(294.0-pixel[1])*0.01,0.0)
            errors.append(math.dist(target,point.position))
    camera=bpy.context.scene.camera
    report={
        "phase":phase,
        "native_file":str(native),
        "object_type":obj.type,
        "layer_count":len(layers),
        "frame_count":len(frames),
        "stroke_count":len(strokes),
        "point_count":sum(observed),
        "expected_point_counts":expected,
        "observed_point_counts":observed,
        "max_coordinate_error_world_units":max(errors) if errors else None,
        "camera_ortho_scale":camera.data.ortho_scale if camera else None,
        "camera_resolution":[bpy.context.scene.render.resolution_x,bpy.context.scene.render.resolution_y],
        "passes":len(layers)==1 and len(frames)==1 and len(strokes)==len(spec["contours"]) and observed==expected and bool(errors) and max(errors)<1e-5 and camera is not None and abs(camera.data.ortho_scale-5.88)<1e-6 and bpy.context.scene.render.resolution_x==620 and bpy.context.scene.render.resolution_y==1176,
    }
    reports.append(report)
    if not report["passes"]:
        raise RuntimeError(f"Phase {phase}: native cold readback failed")
summary={
    "blender_version":bpy.app.version_string,
    "file_count":len(reports),
    "all_pass":all(r["passes"] for r in reports),
    "total_strokes":sum(r["stroke_count"] for r in reports),
    "total_manually_specified_points":sum(r["point_count"] for r in reports),
    "maximum_coordinate_error_world_units":max(r["max_coordinate_error_world_units"] for r in reports),
    "phases":reports,
}
(root / "evidence" / "ALL_12_COLD_REOPEN_v064.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
print("ALL_12_COLD_REOPEN_V064",json.dumps({k:v for k,v in summary.items() if k!="phases"}))
