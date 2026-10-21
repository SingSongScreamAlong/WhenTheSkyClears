import bpy,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
nt=bpy.data.node_groups.new('TEMP_END_API','CompositorNodeTree')
out={}
for kind in ['CompositorNodeTransform','CompositorNodeMixRGB','CompositorNodeImage','CompositorNodeRGB','CompositorNodeRLayers']:
 try:
  n=nt.nodes.new(kind)
  out[kind]={'inputs':[(s.name,s.bl_idname) for s in n.inputs],'outputs':[(s.name,s.bl_idname) for s in n.outputs]}
  if kind=='CompositorNodeImage':out['image_user']=[p.identifier for p in n.image_user.bl_rna.properties if not p.is_readonly]
 except Exception as e:out[kind]=str(e)
out['scenes']=[s.name for s in bpy.data.scenes]
out['gp']=[(o.name,list(o.location)) for o in bpy.data.objects if o.type=='GREASEPENCIL']
out['title_collections']=[c.name for c in bpy.data.collections if 'title' in c.name.lower()]
(R/'notes/world_v016/ending_api_v032.json').write_text(json.dumps(out,indent=2))
print('END_API_SAVED')
