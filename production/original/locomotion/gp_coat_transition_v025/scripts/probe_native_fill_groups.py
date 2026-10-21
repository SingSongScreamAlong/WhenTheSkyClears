import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];bpy.ops.wm.read_factory_settings(use_empty=True)
op=bpy.ops.object.grease_pencil_add;report={'primitive_operator':op.get_rna_type().identifier,'type_enum':[(e.identifier,e.name) for e in op.get_rna_type().properties['type'].enum_items]}
op(type='MONKEY');o=bpy.context.object
report['layers']=[]
for l in o.data.layers:
    report['layers'].append({'name':l.name,'frames':[{'frame':f.frame_number,'attributes':[{'name':a.name,'type':a.data_type,'domain':a.domain,'values':[str(v) for v in a.data[:3]]} for a in f.drawing.attributes],'strokes':[{'material':s.material_index,'fill_id':s.fill_id,'cyclic':s.cyclic,'fill_opacity':s.fill_opacity,'fill_color':list(s.fill_color),'points':len(s.points)} for s in f.drawing.strokes[:8]]} for f in l.frames]})
report['materials']=[{'name':m.name,'show_fill':m.grease_pencil.show_fill,'fill_color':list(m.grease_pencil.fill_color),'show_stroke':m.grease_pencil.show_stroke,'use_nodes':m.use_nodes,'nodes':[{'id':n.bl_idname,'name':n.name,'inputs':[(i.name,str(getattr(i,'default_value',None))) for i in n.inputs]} for n in m.node_tree.nodes] if m.node_tree else None,'links':[(x.from_node.name,x.from_socket.name,x.to_node.name,x.to_socket.name) for x in m.node_tree.links] if m.node_tree else None} for m in o.data.materials]
(P/'evidence/NATIVE_PRIMITIVE_FILL_GROUPS.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
