import bpy,json,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
O=Path(r'WTSC_LOCAL_USER\Documents\Codex\2026-10-16\task\world_art_v048')
out=[]
for f in ['WTSC_Painted_World_Full_Trailer_Editable_v040.blend','WTSC_Open_Battlefield_Refinement_v047g.blend']:
 p=R/'shots/world'/f
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
 d={'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'scenes':[],'images':[{'name':i.name,'size':list(i.size),'path':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images]}
 for s in bpy.data.scenes:
  q={'name':s.name,'frames':[s.frame_start,s.frame_end],'camera':s.camera.name if s.camera else None,'objects':len(s.objects),'compositor':[]}
  if s.compositing_node_group:q['compositor']=[{'name':n.name,'type':n.bl_idname,'scene':n.scene.name if hasattr(n,'scene') and n.scene else None} for n in s.compositing_node_group.nodes]
  if 'WORLD_CORRECTED' in s.name or 'BATTLEFIELD_REFINEMENT' in s.name:
   bpy.context.window.scene=s;s.frame_set(1201 if 'CORRECTED' in s.name else 1849)
   q['world_objects']=[{'name':o.name,'type':o.type,'location':list(o.location),'dimensions':list(o.dimensions),'parent':o.parent.name if o.parent else None,'hide_render':o.hide_render,'materials':[m.name for m in o.data.materials if m] if hasattr(o.data,'materials') else []} for o in s.objects]
   q['material_nodes']={m.name:[{'name':n.name,'type':n.bl_idname,'image':n.image.name if hasattr(n,'image') and n.image else None} for n in m.node_tree.nodes] for m in bpy.data.materials if m.use_nodes and any(o.type=='MESH' and m in list(o.data.materials) for o in s.objects) and ('path' in m.name.lower() or 'panorama' in m.name.lower() or 'School' in m.name or 'village' in m.name.lower())}
   q['camera_samples']=[]
   for frame in ([241,841,1201,1609,1849,1921,2161] if 'CORRECTED' in s.name else [1801,1849,1901,1920]):
    s.frame_set(frame);bpy.context.view_layer.update();q['camera_samples'].append({'frame':frame,'camera_matrix':[list(v) for v in s.camera.matrix_world],'lens':s.camera.data.lens,'sensor':s.camera.data.sensor_width,'shift':[s.camera.data.shift_x,s.camera.data.shift_y]})
  d['scenes'].append(q)
 out.append(d)
(O/'native_inventory.json').write_text(json.dumps(out,indent=2))
print('WORLD_NATIVE_INVENTORY',[(x['file'],[(s['name'],s['objects'],s['frames']) for s in x['scenes']]) for x in out],flush=True)
