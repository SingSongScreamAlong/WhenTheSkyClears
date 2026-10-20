import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'reference/PRESERVED_GARMENT_v037.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene;r={}
for o in S.objects:
 if o.type!='MESH' or o.hide_render:continue
 if not any(t in o.name for t in ['BOY','V024 continuous','V033 |','V037 | coherent']):continue
 d={'materials':[],'UV_range':None,'vertices':len(o.data.vertices),'collections':[c.name for c in o.users_collection]}
 if o.data.uv_layers.active:d['UV_range']=[[min(v.uv[i] for v in o.data.uv_layers.active.data),max(v.uv[i] for v in o.data.uv_layers.active.data)] for i in range(2)]
 for slot in o.material_slots:
  m=slot.material
  if not m:continue
  d['materials'].append({'name':m.name,'slot_link':slot.link,'nodes':[(n.name,n.type) for n in m.node_tree.nodes] if m.use_nodes else [],'image_nodes':[(n.name,n.image.name,list(n.image.size)) for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if m.use_nodes else []})
 r[o.name]=d
(P/'evidence/COLOR_MATERIAL_INSPECTION.json').write_text(json.dumps(r,indent=2));print('COLOR_MATERIALS_INSPECTED',json.dumps({n:{'materials':[(m['name'],m['slot_link']) for m in d['materials']],'UV':d['UV_range']} for n,d in r.items()}),flush=True)
