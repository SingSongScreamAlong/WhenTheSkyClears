import bpy,json
from pathlib import Path
O=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=r'WTSC_LOCAL_WORKSPACE\work\world_facade_v057\WTSC_Continuous_Painterly_Facade_Proof_v057.blend',load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_CONTINUOUS_FACADE_SOURCE_LIGHTING_v057_TEST'];bpy.context.window.scene=s
def node(n):
 return {'name':n.name,'type':n.type,'operation':getattr(n,'operation',None),'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None,'inputs':{x.name:(str(x.default_value) if hasattr(x,'default_value') else None) for x in n.inputs if not x.is_linked},'links':{x.name:[(l.from_node.name,l.from_socket.name) for l in x.links] for x in n.inputs if x.is_linked}}
rows=[]
for o in s.objects:
 if o.name in ['v020 | Walking path | continuous blended paint','v020 | Foreground bank | continuous blended paint'] or o.name.startswith('v048 | ') and 'soil bank' in o.name or o.name.startswith('v016 | Rooted grass') and int(o.name[-3:]) in [0,25,50,75,100]:
  rows.append({'name':o.name,'location':list(o.location),'dim':list(o.dimensions),'hide':o.hide_render,'vertices':[list(o.matrix_world@v.co) for v in o.data.vertices][:12],'uv':{u.name:[list(d.uv) for d in u.data][:12] for u in o.data.uv_layers},'materials':[{'name':m.name,'nodes':[node(n) for n in m.node_tree.nodes]} for m in o.data.materials]})
(O/'FOREGROUND_INSPECTION.json').write_text(json.dumps(rows,indent=2))
print('FOREGROUND_INSPECTED')
