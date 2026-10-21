import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];s=bpy.data.scenes['WTSC_OPEN_BATTLEFIELD_REFINEMENT_v047a'];bpy.context.window.scene=s
root=next(o for o in s.objects if o.get('motion_revision')=='v007_drawn_pose_corrections')
rows=[]
for f in [1844,1901]:
 s.frame_set(f);bpy.context.view_layer.update()
 for rig in [o for o in root.children_recursive if o.type=='ARMATURE']:
  for side in ['near','far']:
   arm=next(o for o in rig.children if o.name==f'V007_{rig["character"]} | drawn skin {side}');ev=arm.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();end=(mesh.vertices[-2].co+mesh.vertices[-1].co)*.5;ev.to_mesh_clear()
   hand=next(o for o in rig.children if 'articulated drawn hand '+side in o.name);ev=hand.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();points=[v.co.copy() for v in mesh.vertices];ev.to_mesh_clear()
   row={'frame':f,'who':rig['character'],'side':side,'skin_end_rig':list(end),'bone_hand_rig':list(rig.pose.bones['hand_'+side].head),'delta':(end-rig.pose.bones['hand_'+side].head).length,'first_hand_vertices':[list(p) for p in points[:5]]};rows.append(row);print(json.dumps(row),flush=True)
(R/'notes/improvement_v047/arm_connections.json').write_text(json.dumps(rows,indent=2))
