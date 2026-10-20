import bpy,json
from pathlib import Path
root=Path(r'WTSC_LOCAL_WORKSPACE')
s=bpy.context.scene
rows=[]
for o in s.objects:
    rows.append({'name':o.name,'type':o.type,'loc':list(o.location),'rot':list(o.rotation_euler),'scale':list(o.scale),'verts':len(o.data.vertices) if o.type=='MESH' else None,'materials':[{'name':m.name,'nodes':[(n.name,n.type) for n in m.node_tree.nodes] if m.use_nodes else []} for m in o.data.materials] if hasattr(o.data,'materials') else []})
(root/'notes/world_v016/source_inventory.json').write_text(json.dumps({'scene':s.name,'objects':rows,'render':s.render.engine,'world':s.world.name,'compositor':s.compositing_node_group.name if s.compositing_node_group else None,'samples':s.eevee.taa_render_samples if hasattr(s,'eevee') else None},indent=2))
print('INVENTORY_SAVED',len(rows))
