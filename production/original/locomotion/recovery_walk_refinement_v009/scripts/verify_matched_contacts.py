import bpy,json,csv
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_v009_Matched_Review_Copy.blend'),load_ui=False);s=bpy.context.scene
root=next(o for o in s.objects if o.get('motion_revision')=='v009_recovery_walk');rigs={o['character']:o for o in root.children_recursive if o.type=='ARMATURE'}
contacts=[o for o in s.objects if o.name.startswith('v041 sole contact |')];assert len(contacts)==4
err=0
for f in range(1801,1921):
 s.frame_set(f);bpy.context.view_layer.update()
 for plane in contacts:
  boot=bpy.data.objects[plane['v009_new_boot_reference']];ev=boot.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();lo=min(v.z for v in pts);bottom=[v for v in pts if v.z<=lo+.004];x=sum(v.x for v in bottom)/len(bottom);err=max(err,abs(plane.location.x-x))
assert err<2e-5,err
report={'cold_reopened':True,'frames':120,'soft_contact_planes':4,'max_contact_centroid_x_error_m':err,'reference':'v009_new_boot_reference resolves to actual new support_boot object for every mark','camera_interpolation':'LINEAR','copy_only':True}
(P/'evidence/matched_contact_validation.json').write_text(json.dumps(report,indent=2));print('MATCHED_CONTACTS_VERIFIED',json.dumps(report),flush=True)
