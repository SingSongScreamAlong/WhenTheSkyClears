import bpy,json
from pathlib import Path
s=bpy.context.scene;nt=bpy.data.node_groups.new('V060 output API probe','CompositorNodeTree');s.compositing_node_group=nt
n=nt.nodes.new('CompositorNodeOutputFile')
r={'node_properties':[p.identifier for p in n.bl_rna.properties],'node_inputs':[(p.name,p.identifier) for p in n.inputs]}
for name in ['file_output_items','file_slots','format','directory','file_name','base_path']:
 if hasattr(n,name):
  v=getattr(n,name)
  r[name]={'type':str(type(v)),'properties':[p.identifier for p in v.bl_rna.properties] if hasattr(v,'bl_rna') else [],'value':str(v)}
  try:r[name]['items']=[{'name':str(x),'properties':[p.identifier for p in x.bl_rna.properties]} for x in v]
  except:pass
Path(r'WTSC_LOCAL_WORKSPACE\work\trailer_development_v060\evidence\FILE_OUTPUT_API.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r,indent=2),flush=True)

fns=[]
for f in n.file_output_items.bl_rna.functions:
 fns.append({'name':f.identifier,'parameters':[{'name':p.identifier,'type':p.type,'enum':[v.identifier for v in p.enum_items] if p.type=='ENUM' else []} for p in f.parameters]})
Path(r'WTSC_LOCAL_WORKSPACE\work\trailer_development_v060\evidence\FILE_OUTPUT_FUNCTIONS.json').write_text(json.dumps(fns,indent=2))
