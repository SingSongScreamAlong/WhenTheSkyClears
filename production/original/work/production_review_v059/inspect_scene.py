import bpy,json,hashlib,time
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
O=R/'work'/'production_review_v059';O.mkdir(parents=True,exist_ok=True)
S=R/'work'/'world_minimum_v058'/'WTSC_World_Development_v058_Packed.blend'
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False)
d={'source':str(S),'sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'version':bpy.app.version_string,'scenes':[],'objects':[],'materials':[]}
for s in bpy.data.scenes:
 d['scenes'].append({'name':s.name,'objects':len(s.objects),'camera':s.camera.name if s.camera else None,'range':[s.frame_start,s.frame_end],'fps':s.render.fps,'engine':s.render.engine,'compositor':bool(s.compositing_node_group),'resolution':[s.render.resolution_x,s.render.resolution_y]})
s=bpy.data.scenes['WTSC_WORLD_FOREGROUND_v058d'];bpy.context.window.scene=s;s.frame_set(1537)
for ob in s.objects:
 d['objects'].append({'name':ob.name,'type':ob.type,'location':list(ob.location),'world':list(ob.matrix_world.translation),'dimensions':list(ob.dimensions),'hide_render':ob.hide_render,'parent':ob.parent.name if ob.parent else None,'materials':[m.name if m else None for m in getattr(ob.data,'materials',[])],'action':ob.animation_data.action.name if ob.animation_data and ob.animation_data.action else None})
for m in bpy.data.materials:
 if m.node_tree:
  d['materials'].append({'name':m.name,'nodes':[{'name':n.name,'type':n.bl_idname,'image':n.image.name if hasattr(n,'image') and n.image else None,'inputs':{i.name:list(i.default_value) if hasattr(i.default_value,'__len__') and not isinstance(i.default_value,str) else i.default_value for i in n.inputs if hasattr(i,'default_value') and not i.is_linked}} for n in m.node_tree.nodes],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]})
(O/'scene_inspection.json').write_text(json.dumps(d,indent=2,default=str))
print('INSPECTION_READY',json.dumps(d['scenes']),flush=True)
