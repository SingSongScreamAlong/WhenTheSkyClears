import bpy,json,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');O=R/'locomotion/garment_continuity_v047'
P=O/'reference/PRESERVED_v046_INPUT.blend'
bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False);s=bpy.data.scenes['V046 | AGE10 BONES | restored painted clothing'];bpy.context.window.scene=s;s.frame_set(1)
d={'source':str(P),'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'scene':s.name,'properties':{k:str(s[k]) for k in s.keys()},'scene_range':[s.frame_start,s.frame_end],'camera':{'name':s.camera.name,'matrix':[list(v) for v in s.camera.matrix_world],'ortho':s.camera.data.ortho_scale},'images':[{'name':i.name,'size':list(i.size),'path':i.filepath,'packed':bool(i.packed_file)} for i in bpy.data.images if i.type!='RENDER_RESULT'],'objects':[]}
for ob in s.objects:
 if not ob.hide_render and ob.type=='MESH':
  row={'name':ob.name,'vertices':len(ob.data.vertices),'parent':ob.parent.name if ob.parent else None,'properties':{k:str(ob[k]) for k in ob.keys()},'materials':[m.name for m in ob.data.materials],'modifiers':[(m.name,m.type) for m in ob.modifiers],'shape_count':len(ob.data.shape_keys.key_blocks) if ob.data.shape_keys else 0,'y_range':[min(v.co.y for v in ob.data.vertices),max(v.co.y for v in ob.data.vertices)]}
  if ob.name.startswith('V046 BOY | tailored'):
   row['coords']=[list(v.co) for v in ob.data.vertices];row['uv']=[[list(x.uv) for x in lay.data] for lay in ob.data.uv_layers]
  d['objects'].append(row)
(O/'evidence/NATIVE_SOURCE_INSPECTION.json').write_text(json.dumps(d,indent=2))
print(json.dumps({k:d[k] for k in ['properties','scene_range','camera','images']},indent=2),flush=True)
print('VISIBLE_OBJECTS',[(o['name'],o['vertices'],o['y_range']) for o in d['objects']],flush=True)
