import bpy,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');O=R/'work/trailer_development_v060'
reports={}
for name,P,scene in [('actor',O/'reference/PRESERVED_STEADY_PAIR_v047.blend','V047 | STEADY ORDINARY WALK | no stumble baseline'),('world',O/'reference/PRESERVED_WORLD_v058.blend','WTSC_WORLD_FOREGROUND_v058d')]:
 bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False);s=bpy.data.scenes[scene];bpy.context.window.scene=s;s.frame_set(1 if name=='actor' else 937);bpy.context.view_layer.update()
 h=next((o for o in s.objects if o.name.startswith('v016 | CHILDREN')),None)
 select=list(bpy.data.collections['V047 | AGE10 PAIR | steady ordinary walk'].all_objects) if name=='actor' else [h]+list(h.children_recursive)
 mats=set(m for ob in select if ob.type=='MESH' for m in ob.data.materials)
 def val(i):
  if not hasattr(i,'default_value'):return None
  v=i.default_value
  if hasattr(v,'__len__'):return list(v)
  if isinstance(v,(int,float,bool,str)):return v
  return str(v)
 reports[name]={'scene':s.name,'camera':{k:getattr(s.camera.data,k) for k in ['type','lens','sensor_width','sensor_height','sensor_fit','shift_x','shift_y']},'camera_frame':[list(p) for p in s.camera.data.view_frame(scene=s)],'objects':[{'name':o.name,'type':o.type,'loc':list(o.location),'world':[list(v) for v in o.matrix_world],'dims':list(o.dimensions),'hide':o.hide_render,'parent':o.parent.name if o.parent else None,'props':{k:str(v) for k,v in o.items() if k!='_RNA_UI'},'mats':[m.name for m in o.data.materials] if o.type=='MESH' else []} for o in select],'materials':[{'name':m.name,'nodes':[{'name':n.name,'type':n.type,'inputs':[(i.name,val(i)) for i in n.inputs]} for n in m.node_tree.nodes] if m.node_tree else [],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links] if m.node_tree else []} for m in mats]}
(O/'evidence/ACTOR_WORLD_INTERFACE.json').write_text(json.dumps(reports,indent=2,default=str))
print('ACTOR_INTERFACE_READY',flush=True)
