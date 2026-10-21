import sys,json,bpy
from pathlib import Path
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import walk_common as W
S,rig,T,col,recipes=W.setup();rows=[]
for f in [1,4,7,10,13,16,19,22,25]:
 S.frame_set(f);saved=[]
 for o in [*W.api.CONTROLS.values(),rig,T]:
  if o.animation_data and o.animation_data.action:saved.append((o,o.animation_data.action,o.animation_data.action_slot));o.animation_data.action=None
 W.body_pose(f,rig,T,recipes,False,True);rows.append(W.validate(f,rig,recipes))
 for o,a,slot in saved:o.animation_data.action=a;o.animation_data.action_slot=slot
 W.api.key_controls(f);T.keyframe_insert('location',frame=f)
for o in [*W.api.CONTROLS.values(),rig,T]:W.interpolation(o,'CONSTANT')
S.frame_end=24;S.frame_set(1);S['V018_stage']='STEPPED KEYS; technical and silhouette gate before interpolation'
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Boy_Travelling_Walk_Blocking_v018.blend'),compress=True)
(P/'evidence/blocking_validation.json').write_text(json.dumps(rows,indent=2))
print('BLOCKING_MAX_IK',max(r['endpoint_error_m'] for row in rows for r in row['reach']));print('BLOCKING_REACHABLE',all(r['reachable'] for row in rows for r in row['reach']))
for f in [1,4,7,10,13,16,19,22,25]:
 S.frame_set(f);S.render.filepath=str(P/f'previews/BLOCKING/{f:04d}.png');bpy.ops.render.render(write_still=True)
print('V018_BLOCKING_COMPLETE')
