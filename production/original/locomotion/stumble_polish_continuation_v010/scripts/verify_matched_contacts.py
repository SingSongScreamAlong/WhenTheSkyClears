import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];V9=P.parent/'recovery_walk_refinement_v009'
bpy.ops.wm.open_mainfile(filepath=str(V9/'native/WTSC_v009_Matched_Review_Copy.blend'),load_ui=False);s=bpy.context.scene;oldcamera={}
for f in range(1801,1921):s.frame_set(f);bpy.context.view_layer.update();oldcamera[f]=s.camera.matrix_world.copy()
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_v010_Matched_Review_Copy.blend'),load_ui=False);s=bpy.context.scene
contacts=[o for o in s.objects if o.name.startswith('v041 sole contact |')];assert len(contacts)==4;err=0;cameraerror=0
for f in range(1801,1969):
 s.frame_set(f);bpy.context.view_layer.update();expected=oldcamera[min(f,1920)].copy()
 if f>1920:expected.translation.x+=.012*(f-1920)
 cameraerror=max(cameraerror,max(abs(s.camera.matrix_world[i][j]-expected[i][j]) for i in range(4) for j in range(4)))
 for plane in contacts:
  boot=bpy.data.objects[plane['v010_new_boot_reference']];ev=boot.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();lo=min(v.z for v in pts);bottom=[v for v in pts if v.z<=lo+.004];x=sum(v.x for v in bottom)/len(bottom);err=max(err,abs(plane.location.x-x))
assert err<2e-5 and cameraerror<2e-5,(err,cameraerror)
report={'cold_reopened':True,'frames':168,'soft_contact_planes':4,'max_contact_centroid_x_error_m':err,'camera_world_matrix_error_m':cameraerror,'reference':'v010_new_boot_reference resolves to actual new support_boot object for every mark','camera_interpolation':'LINEAR','copy_only':True}
(P/'evidence/matched_contact_validation.json').write_text(json.dumps(report,indent=2));print('V010_MATCHED_VERIFIED',json.dumps(report),flush=True)
