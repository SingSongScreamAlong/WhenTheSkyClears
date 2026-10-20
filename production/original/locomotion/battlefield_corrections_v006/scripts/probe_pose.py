import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Battlefield_Drawn_Corrections_v006.blend'),load_ui=False)
s=bpy.context.scene;out=[]
for f in [1,37,47,58,81,101]:
 s.frame_set(f);bpy.context.view_layer.update()
 for r in s.objects:
  if r.type=='ARMATURE':out.append({'frame':f,'who':r.get('character'),'bones':{n:list(r.pose.bones[n].head) for n in ['pelvis','thigh_near','shin_near','foot_near','thigh_far','shin_far','foot_far']}})
(P/'evidence/pose_points.json').write_text(json.dumps(out,indent=2))
