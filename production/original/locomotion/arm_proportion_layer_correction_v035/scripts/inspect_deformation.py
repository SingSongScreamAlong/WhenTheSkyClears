import bpy,json,math
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'reference/PREFERRED_v033.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;rig=bpy.data.objects['LOCO_BOY | RIG'];out={'meshes':{},'leg_samples':[]}
for side in ['near','far']:
 for kind in ['drawn sleeve','drawn skin','drawn source gray cuff']:
  o=bpy.data.objects['V007_BOY | '+kind+' '+side];r={'modifiers':[],'drivers':[],'bounds':[[min(v.co[i] for v in o.data.vertices),max(v.co[i] for v in o.data.vertices)] for i in range(3)]}
  for m in o.modifiers:
   d={'name':m.name,'type':m.type}
   if m.type=='NODES':d['nodes']=[{'name':n.name,'type':n.bl_idname,'inputs':[(x.name, str(x.default_value)) for x in n.inputs if hasattr(x,'default_value')],'drivers':[(fc.data_path,fc.driver.expression,[(v.name,[(t.id.name if t.id else None,t.data_path,t.bone_target,t.transform_type) for t in v.targets]) for v in fc.driver.variables]) for fc in n.id_data.animation_data.drivers] if n.id_data.animation_data else []} for n in m.node_group.nodes]
   if m.type=='SUBSURF':d.update({'levels':m.levels,'render_levels':m.render_levels})
   r['modifiers'].append(d)
  out['meshes'][o.name]=r
for f in [1+i/4 for i in range(125)]:
 S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();row={'frame':f,'legs':{}}
 for side in ['near','far']:
  a=rig.pose.bones['thigh_'+side];b=rig.pose.bones['shin_'+side];H=rig.matrix_world@a.head;K=rig.matrix_world@a.tail;A=rig.matrix_world@b.tail;o=bpy.data.objects['V024 continuous '+side+' trouser drawing'];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());vv=[e.matrix_world@v.co for v in e.data.vertices];centers=[(vv[i*7]+vv[i*7+6])*.5 for i in range(97)]
  def dist(p,a,b):
   t=max(0,min(1,(p-a).dot(b-a)/(b-a).length_squared));return (p-(a+(b-a)*t)).length
  row['legs'][side]={'hip':list(H),'knee':list(K),'ankle':list(A),'thigh_m':(K-H).length,'shin_m':(A-K).length,'knee_join_error_m':(a.tail-b.head).length,'bone_scale':[list(a.scale),list(b.scale)],'centers': [list(p) for p in centers] if f in [11,20,27] else None,'contour_center_distance_to_nearest_axis_max_m':max(min(dist(p,H,K),dist(p,K,A)) for p in centers),'cuff_center':list(centers[-1])}
 out['leg_samples'].append(row)
(P/'evidence/DEFORMATION_AND_LEG_STRUCTURE_AUDIT.json').write_text(json.dumps(out,indent=2));print('DEFORMATION_AUDIT_COMPLETE',flush=True)
