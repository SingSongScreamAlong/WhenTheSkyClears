import bpy,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');w=bpy.data.scenes['WTSC_WORLD_CORRECTED_v037'];pair=next(o for o in w.objects if o.type=='GREASEPENCIL');rows=[]
for ob in w.objects:
 if ob.parent==pair or 'Camp | pinned' in ob.name:
  mats=[]
  if hasattr(ob.data,'materials'):
   for m in ob.data.materials:
    if not m or not m.node_tree:continue
    nt=m.node_tree;ems=[n for n in nt.nodes if n.type=='EMISSION'];mats.append({'name':m.name,'nodes':[(n.name,n.bl_idname) for n in nt.nodes],'emission_links':[{'node':n.name,'color_from':[(l.from_node.name,l.from_socket.name) for l in n.inputs[0].links]} for n in ems],'image_nodes':[{'name':n.name,'image':n.image.name if n.image else None,'vector_links':[(l.from_node.name,l.from_socket.name) for l in n.inputs[0].links]} for n in nt.nodes if n.type=='TEX_IMAGE']})
  rows.append({'object':ob.name,'parent':ob.parent.name if ob.parent else None,'materials':mats})
(R/'notes/world_v016/benchmark_inputs_v039.json').write_text(json.dumps(rows,indent=2));print('BENCHMARK_INPUTS_SAVED',flush=True)
