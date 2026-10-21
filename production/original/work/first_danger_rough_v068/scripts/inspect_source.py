import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'work/first_danger_rough_v068'
for d in ['native','evidence','previews','renders','drawings','reference']:(O/d).mkdir(parents=True,exist_ok=True)
P=R/'work/first_danger_acting_v067/native/WTSC_First_Danger_Acting_v067e.blend'
bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False)
S=bpy.data.scenes['WTSC_FIRST_DANGER_ACTING_WORLD_v067'];bpy.context.window.scene=S;S.frame_set(957);bpy.context.view_layer.update()
data={'source':str(P),'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'camera':{'name':S.camera.name,'matrix':[list(a) for a in S.camera.matrix_world],'scale':S.camera.data.ortho_scale},'scenes':list(bpy.data.scenes.keys()),'objects':[]}
for o in S.objects:
 if any(x in o.name for x in ['BOY','GIRL','shared travel','color time','contact']):
  q={'name':o.name,'type':o.type,'hidden':o.hide_render,'parent':o.parent.name if o.parent else None,'parent_type':o.parent_type,'matrix':[list(a) for a in o.matrix_world],'props':dict(o.items())}
  if o.type=='MESH':
   dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);v=[e.matrix_world@a.co for a in e.data.vertices]
   q.update({'verts':len(o.data.vertices),'bounds':[[min(a[i] for a in v),max(a[i] for a in v)] for i in range(3)],'materials':[m.name for m in o.data.materials if m]})
  if o.type=='ARMATURE':q['bones']={b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'length':b.length} for b in o.data.bones}
  data['objects'].append(q)
data['materials']=[]
for m in bpy.data.materials:
 if any(a in m.name for a in ['BOY','GIRL','Boy','Girl','head','Head']):
  data['materials'].append({'name':m.name,'nodes':[{'name':n.name,'type':n.type,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None,'inputs':{p.name:str(p.default_value) for p in n.inputs if not p.is_linked and hasattr(p,'default_value')}} for n in m.node_tree.nodes] if m.node_tree else []})
(O/'evidence/SOURCE.json').write_text(json.dumps(data,indent=2,default=str))
for im in bpy.data.images:
 if im.packed_file and any(t in im.name.lower() for t in ['pair','boy','girl']):
  name=im.name.replace('/','_').replace('\\','_').replace(':','_')
  if not name.endswith('.png'):name+='.png'
  (O/'reference'/name).write_bytes(im.packed_file.data)
print('V068_SOURCE_READY',len(data['objects']),flush=True)
