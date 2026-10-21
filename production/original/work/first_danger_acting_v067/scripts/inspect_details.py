import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];R=O.parents[1]
for d in ['native','reference','evidence','previews','renders']:(O/d).mkdir(parents=True,exist_ok=True)
P=R/'work/first_danger_acting_v066/native/WTSC_First_Danger_Acting_v066.blend'
bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_FIRST_DANGER_ACTING_WORLD_v066'];bpy.context.window.scene=s;s.frame_set(990);bpy.context.view_layer.update()
data=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render or not any(t in o.name for t in ['BOY','GIRL']):continue
 if o.get('proportion_role')=='head' or o.get('wardrobe_role')=='hand':
  images={n.image for m in o.data.materials if m and m.node_tree for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
  for im in images:
   if im.packed_file:
    name=im.name.replace('/','_').replace('\\','_').replace(':','_')
    if not name.lower().endswith('.png'):name+='.png'
    (O/'reference'/name).write_bytes(im.packed_file.data)
  data.append({'name':o.name,'role':o.get('proportion_role',o.get('wardrobe_role')),'matrix_local':[list(r) for r in o.matrix_local],'vertices':[list(v.co) for v in o.data.vertices],'groups':[g.name for g in o.vertex_groups],'uvs':[{str(l.vertex_index):list(uv.data[l.index].uv) for l in o.data.loops} for uv in o.data.uv_layers],'images':[{'name':im.name,'size':list(im.size)} for im in images],'shape_keys':[k.name for k in o.data.shape_keys.key_blocks] if o.data.shape_keys else []})
(O/'evidence/DETAILS.json').write_text(json.dumps(data,indent=2))
print('DETAILS_READY',[(d['name'],d['images']) for d in data],flush=True)
