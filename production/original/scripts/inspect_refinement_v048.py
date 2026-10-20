import bpy, json
from pathlib import Path
R=Path(__file__).resolve().parents[1];N=R/'notes/improvement_v048';N.mkdir(exist_ok=True)
s=bpy.data.scenes['WTSC_OPEN_BATTLEFIELD_REFINEMENT_v047g'];bpy.context.window.scene=s
root=next(o for o in s.objects if o.get('motion_revision')=='v007_drawn_pose_corrections')
rows=[]
for rig in [o for o in root.children_recursive if o.type=='ARMATURE']:
 for side in ['near','far']:
  ob=s.objects[f'V007_{rig["character"]} | drawn sleeve {side}']
  rows.append({'object':ob.name,'material':ob.data.materials[0].name,'key_first':[list(v.co) for v in ob.data.shape_keys.key_blocks['POSE_001'].data[:10]],'modifiers':[m.type for m in ob.modifiers]})
heads=[]
for ob in rig.children:
 if ob.get('v047_role')=='painted_head_exposure':
  mat=ob.data.materials[0]
  heads.append({'object':ob.name,'material':mat.name,'nodes':[{'name':n.name,'type':n.type,'inputs':[{ 'name':i.name,'value':str(i.default_value) if hasattr(i,'default_value') else '' ,'linked':i.is_linked} for i in n.inputs]} for n in mat.node_tree.nodes],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in mat.node_tree.links]})
(N/'construction_inspection.json').write_text(json.dumps({'sleeves':rows,'heads':heads},indent=2))
print('V048_INSPECTED',flush=True)
