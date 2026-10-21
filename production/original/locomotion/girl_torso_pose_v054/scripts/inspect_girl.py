import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];source=ROOT/'locomotion/authored_walk_beats_v053/native/WTSC_Authored_Walk_Beats_v053.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='23fc2578b499d6d2fded4f1d16a5466d93bea59b8bb7caa9eee26e7004a8a29b'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);S=bpy.data.scenes['V053 | AUTHORED WALK BEATS | v051 grounded feet'];bpy.context.window.scene=S
r=bpy.data.objects['V044 GIRL | estimated joint centres'];C=bpy.data.collections['V046 | restored original painted wardrobe'];out={}
for o in C.objects:
 if o.parent!=r or o.get('wardrobe_role') not in ('body','sleeve'):continue
 g={x.index:x.name for x in o.vertex_groups};verts=o.data.vertices
 rowlen=17 if o.get('wardrobe_role')=='body' else 9
 rows=[]
 for row in range(len(verts)//rowlen):
  vv=verts[row*rowlen:(row+1)*rowlen]
  if row in [0,1,3,5,7,9,12,16,20,24,28,32,40,48,56,64] or row==len(verts)//rowlen-1:
   rows.append({'row':row,'rear':[float(x) for x in vv[0].co],'front':[float(x) for x in vv[-1].co],'zmin':min(float(v.co.z) for v in vv),'zmax':max(float(v.co.z) for v in vv),'center':[float(x) for x in vv[len(vv)//2].co],'groups':[(g[k.group],float(k.weight)) for k in vv[len(vv)//2].groups]})
 out[o.name]={'role':o.get('wardrobe_role'),'vertices':len(verts),'rows':len(verts)//rowlen,'rowlen':rowlen,'shape_keys':[k.name for k in o.data.shape_keys.key_blocks] if o.data.shape_keys else [],'modifiers':[(m.name,m.type,m.object.name if hasattr(m,'object') and m.object else None) for m in o.modifiers],'materials':[m.name for m in o.data.materials],'uv_layers':[u.name for u in o.data.uv_layers],'rows_sample':rows}
for f in [1,4,5,9,13,17,20,21,25,29,33]:
 S.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();e=r.evaluated_get(dg);p=e.pose.bones
 out.setdefault('poses',[]).append({'frame':f,'pelvis_head':list(p['pelvis'].head),'pelvis_tail':list(p['pelvis'].tail),'chest_head':list(p['chest'].head),'chest_tail':list(p['chest'].tail),'near_arm_head':list(p['upper_arm_near'].head),'near_arm_tail':list(p['upper_arm_near'].tail)})
(P/'evidence/GIRL_MESH_INSPECTION.json').write_text(json.dumps(out,indent=2));print('V054_READ_ONLY_GIRL_MESH_INSPECTED',[(k,v['vertices'],v['rows'],v['rowlen']) for k,v in out.items() if k!='poses'])
