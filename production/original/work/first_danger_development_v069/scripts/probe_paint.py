import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parents[1];R=O.parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'work/first_danger_rough_v068/native/WTSC_First_Danger_Rough_Acting_v068e.blend'),load_ui=False,use_scripts=False)
rows=[]
for name in ['V046 BOY | tailored coat','V046 GIRL | tailored knee-length dress','V046 BOY | painted continuous rolled sleeve far','V046 GIRL | painted continuous rolled sleeve far','V046 BOY | painted forearm near','V046 BOY | painted rigid-axis trousers near','V046 GIRL | original painted stockings near','V044 BOY | boot near','V044 BOY | head','V044 GIRL | head']:
 ob=bpy.data.objects[name];uv=ob.data.uv_layers.active
 rows.append({'object':name,'uv_bounds':[[min(x.uv[i] for x in uv.data),max(x.uv[i] for x in uv.data)] for i in range(2)],'materials':[{'name':m.name,'nodes':[{'name':n.name,'type':n.type,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None,'uv':n.uv_map if n.type=='UVMAP' else None} for n in m.node_tree.nodes],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]} for m in ob.data.materials if m]})
(O/'evidence/PAINT_PROBE.json').write_text(json.dumps(rows,indent=2));print('PAINT_PROBE_READY',flush=True)
