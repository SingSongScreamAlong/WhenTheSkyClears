import bpy,json
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Supported_Recovery_v007.blend'),load_ui=False);s=bpy.context.scene;s.frame_set(101);bpy.context.view_layer.update();rows=[]
for ob in s.objects:
 if ob.get('v007_role')=='drawn_hand' or ob.get('v006_role')=='drawn_hand':
  r=ob.parent;ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();vs=[ev.matrix_world@v.co for v in mesh.vertices];ev.to_mesh_clear();side='near' if 'near' in ob.name else 'far';pb=r.pose.bones['hand_'+side]
  rows.append({'name':ob.name,'bone_head':list(r.matrix_world@pb.head),'bone_y':list(pb.matrix.col[1]),'bounds':[min(v.x for v in vs),max(v.x for v in vs),min(v.z for v in vs),max(v.z for v in vs)]})
(P/'evidence/hand_geometry_probe.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows),flush=True)
