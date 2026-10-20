import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(r'WTSC_LOCAL_WORKSPACE');s=bpy.data.scenes['WTSC_WORLD_CENTERED_v035'];bpy.context.window.scene=s;s.frame_set(1)
rows=[]
for o in s.objects:
 if o.type=='GREASEPENCIL' or any(k in o.name.lower() for k in ['pair','children','painted village','walking path','one coherent','continuous blended']):
  b=[o.matrix_world@Vector(v) for v in o.bound_box];rows.append({'name':o.name,'parent':o.parent.name if o.parent else None,'location':list(o.location),'type':o.type,'bounds':[min(p.x for p in b),max(p.x for p in b),min(p.z for p in b),max(p.z for p in b)]})
nt=bpy.data.node_groups.new('TEMP_GLARE_API','CompositorNodeTree');n=nt.nodes.new('CompositorNodeGlare')
report={'objects':rows,'glare_properties':[p.identifier for p in n.bl_rna.properties if not p.is_readonly],'glare_inputs':[(s.name,s.bl_idname,str(s.default_value) if hasattr(s,'default_value') else None) for s in n.inputs]}
(R/'notes/world_v016/atmosphere_api_v036.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
