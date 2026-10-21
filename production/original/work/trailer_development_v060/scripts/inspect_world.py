import bpy,json,hashlib,datetime
from pathlib import Path
from mathutils import Vector
R=Path(r'WTSC_LOCAL_WORKSPACE');O=R/'work/trailer_development_v060'
P=R/'work/world_minimum_v058/WTSC_World_Development_v058_Packed.blend'
bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_WORLD_FOREGROUND_v058d'];bpy.context.window.scene=s
def bounds(ob):
 e=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
 if ob.type=='GREASEPENCIL':
  pts=[e.matrix_world@p.vector for l in e.data.layers for f in l.frames[:1] for p in f.drawing.attributes['position'].data]
 elif ob.type=='MESH':pts=[e.matrix_world@v.co for v in e.data.vertices]
 else:return None
 return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)] if pts else None
report={'source':str(P),'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'scene':s.name,'camera':{'name':s.camera.name,'type':s.camera.data.type,'lens':s.camera.data.lens,'ortho_scale':s.camera.data.ortho_scale},'collections':[{'name':c.name,'objects':len(c.all_objects)} for c in s.collection.children],'samples':[]}
for f in [241,937,961,993,1056,1201,1537,2161]:
 s.frame_set(f);bpy.context.view_layer.update()
 row={'frame':f,'camera_matrix':[list(x) for x in s.camera.matrix_world],'actors':[],'empty_roots':[]}
 for ob in s.objects:
  if 'CHILDREN' in ob.name or ob.type=='GREASEPENCIL':
   row['actors'].append({'name':ob.name,'type':ob.type,'parent':ob.parent.name if ob.parent else None,'world':[list(x) for x in ob.matrix_world],'bbox':bounds(ob),'hide':ob.hide_render})
  if ob.type=='EMPTY' and (not ob.parent or 'CHILDREN' in ob.name):row['empty_roots'].append({'name':ob.name,'loc':list(ob.matrix_world.translation)})
 report['samples'].append(row)
report['selected_objects']=[]
for ob in s.objects:
 if ob.type in ['MESH','LIGHT'] and any(t in ob.name.lower() for t in ['ground','path','contact','light','mist','smoke','fire','camp','school','children']):
  report['selected_objects'].append({'name':ob.name,'type':ob.type,'parent':ob.parent.name if ob.parent else None,'loc':list(ob.matrix_world.translation),'dimensions':list(ob.dimensions),'hide':ob.hide_render,'materials':[m.name for m in ob.data.materials] if ob.type=='MESH' else [],'properties':{k:str(v) for k,v in ob.items() if k!='_RNA_UI'}})
report['materials']=[]
for mat in bpy.data.materials:
 if any(t in mat.name.lower() for t in ['skin','child','painter','contact','light','mist']):
  report['materials'].append({'name':mat.name,'nodes':[{'name':n.name,'type':n.type,'inputs':[(i.name,list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value) for i in n.inputs if hasattr(i,'default_value') and isinstance(i.default_value,(int,float))]} for n in mat.node_tree.nodes] if mat.node_tree else []})
(O/'evidence/WORLD_CURRENT_INSPECTION.json').write_text(json.dumps(report,indent=2,default=str))
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.eevee.taa_render_samples=24;s.render.image_settings.file_format='PNG'
for f in [937,993,1056]:
 s.frame_set(f);s.render.filepath=str(O/f'previews/world_source_{f}.png');bpy.ops.render.render(write_still=True,scene=s.name)
print('WORLD_INSPECTION_READY',flush=True)
