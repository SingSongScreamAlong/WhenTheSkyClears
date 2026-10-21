import bpy,json,math
from pathlib import Path
O=Path(__file__).resolve().parents[1];B=json.loads((O/'evidence/BUILD.json').read_text());bpy.ops.wm.open_mainfile(filepath=B['native'],load_ui=False,use_scripts=False);S=bpy.data.scenes[B['world_scene']];bpy.context.window.scene=S
rows={w:[] for w in ['BOY','GIRL']};previous={}
for i in range(335):
 g=913+i*.5;S.frame_set(int(g),subframe=g-int(g));bpy.context.view_layer.update()
 for w in rows:
  r=bpy.data.objects['V044 '+w+' | estimated joint centres'];H=r.pose.bones['upper_arm_near'].head;E=r.pose.bones['upper_arm_near'].tail;W=r.pose.bones['forearm_near'].tail
  sign=(E-H).cross(W-E).y
  if w in previous:rows[w].append({'frame':g,'elbow_step_m':(E-previous[w][0]).length,'wrist_step_m':(W-previous[w][1]).length,'bend_cross_y':sign})
  previous[w]=(E.copy(),W.copy())
out={w:sorted(v,key=lambda x:x['elbow_step_m'],reverse=True)[:8] for w,v in rows.items()};(O/'evidence/ELBOW_SPACING_PILOT.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
