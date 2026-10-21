import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Unpainted_Motion_Rebuild_v011.blend'),load_ui=False);s=bpy.context.scene;s.frame_set(44);bpy.context.view_layer.update();rows=[]
for rig in [o for o in s.objects if o.type=='ARMATURE']:
 for ob in rig.children:
  if ob.type!='MESH':continue
  name=ob.vertex_groups[0].name;pb=rig.pose.bones[name];rest=rig.data.bones[name];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();pts=[ev.matrix_world@v.co for v in me.vertices];center=sum(pts,Vector())/len(pts);ev.to_mesh_clear();basecenter=sum((v.co for v in ob.data.vertices),Vector())/len(ob.data.vertices)
  rows.append({'object':ob.name,'group':name,'matrix_basis':[list(v) for v in ob.matrix_basis],'parent_inverse':[list(v) for v in ob.matrix_parent_inverse],'base_center':list(basecenter),'bone_rest_head':list(rest.head_local),'bone_rest_tail':list(rest.tail_local),'posed_head_world':list(rig.matrix_world@pb.head),'posed_tail_world':list(rig.matrix_world@pb.tail),'evaluated_center':list(center),'bbox':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]})
(P/'evidence/binding_inspection.json').write_text(json.dumps(rows,indent=2));print(json.dumps([r for r in rows if any(k in r['object'] for k in ['head','chest','thigh_near','flat sole near'])]),flush=True)
