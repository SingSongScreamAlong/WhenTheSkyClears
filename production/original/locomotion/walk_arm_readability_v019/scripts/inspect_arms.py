import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];R=P.parents[1];sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api
bpy.ops.wm.open_mainfile(filepath=str(R/'locomotion/reference_walk_exercise_v018/native/WTSC_Boy_Travelling_Walk_v018.blend'),load_ui=False,use_scripts=False);rigs,controls=api.initialize_from_scene();r=rigs['BOY'];S=bpy.context.scene
def pts(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [r.matrix_world.inverted()@e.matrix_world@v.co for v in e.data.vertices]
out=[]
for f in [1,7,10,11,12,13,14,15,16,19,22,25]:
 S.frame_set(f);bpy.context.view_layer.update();row={'frame':f,'controls':{},'meshes':{}}
 for side in ['near','far']:
  o=controls['BOY','WRIST_'+side];row['controls'][side]={'wrist':list(r.matrix_world.inverted()@o.matrix_world.translation),'shoulder':list(r.pose.bones['upper_arm_'+side].head),'elbow':list(r.pose.bones['forearm_'+side].head),'FrontLayer':o.get('FrontLayer')}
 for o in r.children:
  if o.type!='MESH':continue
  if o.get('v007_role') in ['drawn_hand','drawn_arm','drawn_cuff'] or o.get('skin_region')=='body':
   V=pts(o);row['meshes'][o.name]={'min':[min(v[k] for v in V) for k in range(3)],'max':[max(v[k] for v in V) for k in range(3)],'location':list(o.location)}
 out.append(row)
(P/'evidence/v018_arm_inspection.json').write_text(json.dumps(out,indent=2));print(json.dumps([{'frame':x['frame'],'controls':x['controls'],'depths':{n:(v['min'][1],v['max'][1]) for n,v in x['meshes'].items()}} for x in out if x['frame'] in [1,10,13,16,22]]))
