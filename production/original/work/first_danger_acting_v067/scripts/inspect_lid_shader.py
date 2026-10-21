import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parents[1];B=json.loads((O/'evidence/BUILD.json').read_text());bpy.ops.wm.open_mainfile(filepath=B['native'],load_ui=False,use_scripts=False)
for name in ['V044 GIRL | head','V067 GIRL | skin lid','V044 BOY | head']:
 o=bpy.data.objects[name];print(name,'ATTRS',[(a.name,a.data_type,a.domain) for a in o.data.attributes],'UVS',[u.name for u in o.data.uv_layers],flush=True)
 for m in o.data.materials:
  print(m.name,[(n.name,n.type,getattr(n,'uv_map',None),getattr(n,'attribute_name',None)) for n in m.node_tree.nodes if n.type in ['ATTRIBUTE','UVMAP','TEX_IMAGE','VERTEX_COLOR','GROUP']],flush=True)
