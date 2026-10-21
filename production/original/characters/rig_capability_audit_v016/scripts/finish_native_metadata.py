import bpy,hashlib,json,struct
from pathlib import Path
P=Path(__file__).resolve().parents[1];results=[]
def meshhash():
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();h=hashlib.sha256()
 for o in sorted((o for o in bpy.context.scene.objects if o.type=='MESH'),key=lambda o:o.name):
  h.update(o.name.encode());e=o.evaluated_get(dg)
  for v in e.data.vertices:h.update(struct.pack('fff',*v.co))
 return h.hexdigest()
for path in sorted((P/'native').glob('*.blend')):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);S=bpy.context.scene;S.frame_set(1);before=meshhash()
 for rig in [o for o in S.objects if o.type=='ARMATURE']:
  rig['motion_status']='v016 technical linkage study; final-art readiness UNPASSED; no performance approval';rig['performance_version']='Performance paused; v016 rig capability tests only';rig['review']='Actual retained painting and original rig. Review cuffs, deep cloth shapes, occlusion and missing head turn before any final-art claim.'
 S['artistic_acceptance']=False
 for name in ['build_rig_audit.py','rig_pose_api.py','diagnostic_poses.py','live_contours.py']:
  if bpy.data.texts.get(name):bpy.data.texts[name].clear();bpy.data.texts[name].write((P/'scripts'/name).read_text())
 after=meshhash();assert before==after
 bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);results.append({'file':path.name,'geometry_unchanged_during_metadata_cleanup':before==after,'frame1_evaluated_mesh_hash':after})
(P/'evidence/final_native_metadata_cleanup.json').write_text(json.dumps(results,indent=2));print('NATIVE_METADATA_CLEAN',len(results))
