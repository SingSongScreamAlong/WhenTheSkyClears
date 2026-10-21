import bpy,json
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\work\color_arc_v063');bpy.ops.wm.open_mainfile(filepath=str(O/'native/WTSC_Shared_Color_To_Charcoal_v063.blend'),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_SHARED_COLOR_TO_CHARCOAL_v063'];bpy.context.window.scene=s;c=bpy.data.objects['V063 | shared color to charcoal | both children'];m=bpy.data.objects['V044 GIRL | head'].material_slots[0].material;nodes=[n for n in m.node_tree.nodes if n.name.startswith('V063 | shared color to charcoal /')]
r=[]
for g in [1,981,2305]:
 s.frame_set(g);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();em=m.evaluated_get(dg);en=em.node_tree.nodes[nodes[0].name]
 dr=[{'path':f.data_path,'valid':f.driver.is_valid,'type':f.driver.type,'expression':f.driver.expression,'vars':[(v.name,v.type,v.targets[0].id.name if v.targets[0].id else None,v.targets[0].data_path) for v in f.driver.variables]} for f in m.node_tree.animation_data.drivers]
 r.append({'g':g,'p':float(c['charcoal_progress']),'raw':nodes[0].inputs[0].default_value,'eval':en.inputs[0].default_value,'mat':m.name,'drivers':dr})
(O/'evidence/DRIVER_DIAGNOSIS.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
