import bpy,json
from pathlib import Path
from mathutils import Vector
O=Path(r'WTSC_LOCAL_WORKSPACE\work\production_look_v061')
bpy.ops.wm.open_mainfile(filepath=str(O/'reference/PRESERVED_v060.blend'),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v060'];bpy.context.window.scene=s;s.frame_set(981)
names=['v020 | Walking path | continuous blended paint','v020 | Foreground bank | continuous blended paint','v016 | Woods | near rooted oaks','v030 | High crown foreground oak 1']
r={}
for name in names:
 o=bpy.data.objects.get(name)
 if not o:continue
 r[name]={'type':o.type,'matrix':[list(v) for v in o.matrix_world],'dimensions':list(o.dimensions),'hide':o.hide_render,'bbox':[[min((o.matrix_world@Vector(c))[a] for c in o.bound_box),max((o.matrix_world@Vector(c))[a] for c in o.bound_box)] for a in range(3)],'verts':len(o.data.vertices) if o.type=='MESH' else 0,'mats':[]}
 for m in o.data.materials:
  r[name]['mats'].append({'name':m.name,'nodes':[{'type':v.bl_idname,'name':v.name,'image':v.image.filepath if v.type=='TEX_IMAGE' and v.image else None,'size':list(v.image.size) if v.type=='TEX_IMAGE' and v.image else None} for v in m.node_tree.nodes] if m.use_nodes else []})
r['visible_plant_sets']=[{'name':o.name,'xyz':list(o.matrix_world.translation),'dim':list(o.dimensions)} for o in s.objects if not o.hide_render and any(t in o.name.lower() for t in ['foreground','woods','canopy','oak','mist','sky'])]
r['scene']={'engine':s.render.engine,'world':s.world.name,'color':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'nodes':[(n.name,n.bl_idname) for n in s.compositing_node_group.nodes] if s.compositing_node_group else []}
(O/'evidence/DEPTH_INPUT_INSPECTION.json').write_text(json.dumps(r,indent=2));print('DEPTH_INSPECT_READY')
