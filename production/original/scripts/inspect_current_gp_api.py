import bpy, json
from pathlib import Path
root=Path(r"WTSC_LOCAL_WORKSPACE")
o=next(o for o in bpy.context.scene.objects if o.type=='GREASEPENCIL')
d=o.data.layers[0].frames[0].drawing
r={'drawing_functions':[p.identifier for p in d.bl_rna.functions], 'material_props':[p.identifier for p in o.data.materials[0].grease_pencil.bl_rna.properties], 'drawing_attrs':[{ 'name':a.name,'domain':a.domain,'data_type':a.data_type,'count':len(a.data)} for a in d.attributes]}
(root/'notes/village_lookdev/gp_api_v015.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r))
