import bpy,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
nt=bpy.data.node_groups.new('TEMP_END_API2','CompositorNodeTree');out={}
out['types']=[x for x in dir(bpy.types) if x.startswith('CompositorNode') and any(w in x.lower() for w in ['mix','image','movie','alpha','math'])]
for kind in ['ShaderNodeMix','CompositorNodeImage','CompositorNodeSetAlpha','CompositorNodeAlphaOver']:
 try:
  n=nt.nodes.new(kind)
  if kind=='ShaderNodeMix':n.data_type='RGBA'
  out[kind]={'inputs':[(s.name,s.identifier,s.bl_idname,str(s.default_value)[:100] if hasattr(s,'default_value') else '') for s in n.inputs],'outputs':[(s.name,s.identifier) for s in n.outputs],'properties':[p.identifier for p in n.bl_rna.properties if not p.is_readonly]}
 except Exception as e:out[kind]=str(e)
(R/'notes/world_v016/ending_api2_v032.json').write_text(json.dumps(out,indent=2))
