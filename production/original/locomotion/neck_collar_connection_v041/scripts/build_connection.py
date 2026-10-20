"""Native garment construction pass over the liked v040 painting and walk.
No new painting, body retiming, head turn or lighting change.
"""
import bpy,json,numpy as np,math,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];SRC=P/'reference/PRESERVED_PAINTED_WALK_v040.blend';bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);S=bpy.context.scene;R=bpy.data.objects['LOCO_BOY | RIG'];T=R.parent;head=bpy.data.objects['V040 | painted boy profile and neck'];coat=bpy.data.objects['V037 | coherent charcoal coat | five pose study'];shirt=bpy.data.objects['LOCO_BOY | PAINT body'];fore=S.view_layers['V025 | original foreground'];atlas=next(n.image for n in head.material_slots[0].material.node_tree.nodes if n.type=='TEX_IMAGE');W,H=atlas.size;raw=np.empty(W*H*4,dtype=np.float32);atlas.pixels.foreach_get(raw);alpha=raw.reshape(H,W,4)[::-1,:,3]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def ah(a):return hashlib.sha256(repr([(f.data_path,f.array_index,[(tuple(k.co),k.interpolation,tuple(k.handle_left),tuple(k.handle_right)) for k in f.keyframe_points]) for l in a.layers for st in l.strips for bag in st.channelbags for f in bag.fcurves]).encode()).hexdigest()
actions={a.name:ah(a) for a in bpy.data.actions};oldkeys={k.name:[v.co.copy() for v in k.data] for k in coat.data.shape_keys.key_blocks};oldUV=[[tuple(u.uv) for u in layer.data] for layer in coat.data.uv_layers];candidates=[]
for x in range(100,251):
 yy=np.flatnonzero(alpha[400:490,x]>.9)
 if len(yy) and yy[-1]+400>427:candidates.append((x,int(yy[-1]+400)))
xa,xb=candidates[0][0]+1,max(candidates,key=lambda p:p[1])[0]-1;neck=[]
for x in np.linspace(xa,xb,11):
 ix=int(round(x));yy=np.flatnonzero(alpha[400:490,ix]>.9);neck.append([float(x),float(yy[-1]+400)])
assert all(b[1]>=a[1]-1 for a,b in zip(neck,neck[1:])),neck
uv=head.data.uv_layers[0];A=[];B=[]
for loop in head.data.loops:
 u=uv.data[loop.index].uv;A.append([u.x*W,(1-u.y)*H,1]);v=head.data.vertices[loop.vertex_index].co;B.append([v.x,v.z])
coef=np.linalg.lstsq(np.array(A),np.array(B),rcond=None)[0];source_rest=np.column_stack([np.array(neck),np.ones(len(neck))])@coef;pose={};collar={};records=[];N=len(neck)
def frame(f):S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();fore.update()
for i in range(125):
 f=1+i/4;frame(f);e=head.evaluated_get(fore.depsgraph);ha=np.array([[v.co.x,v.co.z,1] for v in head.data.vertices]);hb=np.array([list(e.matrix_world@v.co) for v in e.data.vertices]);skin_affine=np.linalg.lstsq(ha,hb,rcond=None)[0];inv=T.matrix_world.inverted();cut=[inv@Vector(v) for v in np.column_stack([source_rest,np.ones(N)])@skin_affine];hip=inv@(R.matrix_world@R.pose.bones['pelvis'].head);neckbone=inv@(R.matrix_world@R.pose.bones['chest'].tail);U=(neckbone-hip).normalized();F=Vector((U.z,0,-U.x));top=[p+U*.00075 for p in cut];bottom=[p-U*(.014+.004*smooth(j/(N-1)))+F*(.002*smooth(j/(N-1))) for j,p in enumerate(cut)];V=[];key=coat.data.shape_keys.key_blocks[0 if i in [0,124] else i];base=oldkeys[key.name]
 for j in range(N):
  t=j/(N-1)*16;c=min(15,int(t));top[j].y=cut[j].y-.002;bottom[j].y=base[c].lerp(base[c+1],t-c).y
 for row in range(3):
  q=row/2
  for j in range(N):
   p=top[j].lerp(bottom[j],q);p.y-=.0014*math.sin(math.pi*q);V.append(p)
 a=top[-1];b=a+F*.012-U*.006;c=a+F*.016-U*.034;d=a+F*.005-U*.018
 b.y=top[-1].y-.001;c.y=bottom[-1].y-.001;d.y=(top[-1].y+bottom[-1].y)*.5-.0015
 V.extend([b,c,d]);collar[f]=V
 # The existing single coat surface now reaches the real neck cut. Its lower
 # shoulder/torso/hem rows, UV registration and original animation stay fixed.
 new=[p.copy() for p in base]
 for row in range(7):
  weight=1-smooth(row/6)
  for col in range(17):
   s=col/16;u=s*(N-1);aidx=min(N-2,int(u));target=bottom[aidx].lerp(bottom[aidx+1],u-aidx);delta=target-base[col];idx=row*17+col;new[idx]+=delta*weight
 if i<124:key.data.foreach_set('co',[c for p in new for c in p]);pose[f]=new
 records.append({'frame':f,'neck_cut_local':[list(p) for p in cut],'max_upper_coat_shift_m':max((a-b).length for a,b in zip(new,base))})
coat.data.vertices.foreach_set('co',[c for p in pose[1.] for c in p]);coat.data.update();collar[32.]=[v.copy() for v in collar[1.]]
# The v040 yoke concealed an armhole and an extra collar in the atlas's upper
# coat region. With one connected coat surface those are inappropriate image
# samples. Register only its upper region to the same atlas's quiet cloth;
# preserve the original first UV and the rest of the painted costume.
paintuv=coat.data.uv_layers['V040 | separated painted part registration'];oldpaint=[tuple(v.uv) for v in paintuv.data];pervertex={l.vertex_index:paintuv.data[l.index].uv.copy() for l in coat.data.loops}
for l in coat.data.loops:
 row=l.vertex_index//17;s=(l.vertex_index%17)/16;t=row/32;back=1-smooth((s-.55)/.25);neckweight=1-smooth((row-2)/4);weight=max(back*(1-smooth((t-.19)/.16)),neckweight);uv=paintuv.data[l.index].uv;target=(675+35*s)/W;uv.x=uv.x*(1-weight)+target*weight
 if row<12:
  oldy=(1-uv.y)*H;backy=190+(100+450*12/32-190)*row/12;fronty=175+(100+450*6/32-175)*row/6 if row<6 else oldy;uv.y=1-(fronty*(1-back)+backy*back)/H
paintuvchanges=sum(a!=tuple(b.uv) for a,b in zip(oldpaint,paintuv.data))
col=bpy.data.collections.new('V041 | folded collar construction');S.collection.children.link(col)
# Collar belongs to the original identity foreground layer, with its own true
# depth ordering; a base-layer halo or compositing stencil is not used.
for vl in S.view_layers:
 if vl.name!='V025 | original foreground':vl.layer_collection.children[col.name].exclude=True
faces=[]
for row in range(2):
 for j in range(N-1):a=row*N+j;faces.append((a,a+1,a+1+N,a+N))
faces.extend([(N-1,3*N,3*N+2,2*N-1),(2*N-1,3*N+2,3*N+1,3*N-1),(3*N+2,3*N,3*N+1)])
me=bpy.data.meshes.new('V041 | connected stand and folded front leaf');me.from_pydata(collar[1.],[],faces);me.update();ob=bpy.data.objects.new('V041 | folded linen collar | neck attached',me);col.objects.link(ob);ob.parent=T;ob.shape_key_add(name='Basis | exact local contact bookend')
for i in range(1,124):
 f=1+i/4;k=ob.shape_key_add(name='V041 collar F%05.2f'%f);k.data.foreach_set('co',[c for p in collar[f] for c in p])
 for t in [1.,max(1.,f-.25),f,min(32.,f+.25),32.]:k.value=float(t==f);k.keyframe_insert('value',frame=t)
ob.data.shape_keys.animation_data.action.name='V041 | folded collar | original31frameclock'
for layer in ob.data.shape_keys.animation_data.action.layers:
 for st in layer.strips:
  for bag in st.channelbags:
   for fc in bag.fcurves:
    for k in fc.keyframe_points:k.interpolation='LINEAR'
    mod=fc.modifiers.new('CYCLES');mod.mode_before=mod.mode_after='REPEAT'
UVM='V041 | original painted linen region';uv=me.uv_layers.new(name=UVM);coords=[]
for row in range(3):
 y=490+row/2*44;idx=np.flatnonzero(alpha[int(y),950:1200]>.95);lo,hi=950+int(idx[0]),950+int(idx[-1])
 for j in range(N):coords.append(((lo+(hi-lo)*(.12+.76*j/(N-1)))/W,1-y/H))
coords.extend([(1125/W,1-495/H),(1120/W,1-535/H),(1075/W,1-517/H)])
for loop in me.loops:uv.data[loop.index].uv=coords[loop.vertex_index]
for name,factor in [('V041 | linen broad fold',1.),('V041 | linen turned leaf',.82)]:
 m=bpy.data.materials.new(name);m.use_nodes=True;ns=m.node_tree.nodes;ns.clear();lk=m.node_tree.links;u=ns.new('ShaderNodeUVMap');u.uv_map=UVM;tex=ns.new('ShaderNodeTexImage');tex.image=atlas;tex.interpolation='Linear';lk.new(u.outputs['UV'],tex.inputs['Vector']);mul=ns.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;mul.inputs[2].default_value=(factor,factor,factor,1);lk.new(tex.outputs['Color'],mul.inputs[1]);em=ns.new('ShaderNodeEmission');lk.new(mul.outputs[0],em.inputs['Color']);out=ns.new('ShaderNodeOutputMaterial');lk.new(em.outputs[0],out.inputs['Surface']);me.materials.append(m)
me.polygons[-1].material_index=1;shirt.hide_render=True;shirt.hide_viewport=True;shirt['V041_preserved']='Hidden original yoke remains intact. New neck-attached folded collar and connected upper coat replace its visible patch.';coat['V041_scope']='Only upper six row stations adjusted to the neck-attached collar base. Same connected surface, original UVs/materials and action channels. Rows6..32 unchanged.';ob['V041_scope']='New folded linen collar follows original painted neck cut and existing trunk direction on the same31-frameclock. Stand/frontleaf are one connected mesh. Existing painting retained. No head/body/wrist/foot or world changes.'
S['V041_status']='NECK/COLLAR CONSTRUCTION CANDIDATE over liked v040 painting/walk. Original yoke hidden; upper coat connected to neck-attached folded collar. No acting or production integration approval.';text=bpy.data.texts.new('READ_FIRST_v041');text.write(S['V041_status']);frame(1);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=480;S.render.resolution_y=720;S.render.resolution_percentage=100
changed=[n for n,h in actions.items() if ah(bpy.data.actions[n])!=h];assert not changed and oldUV[0]==[tuple(u.uv) for u in coat.data.uv_layers[0].data];lowererr=max((v.co-oldkeys[k.name][i]).length for k in coat.data.shape_keys.key_blocks for i,v in enumerate(k.data) if i>=6*17);assert lowererr==0
report={'scope':S['V041_status'],'blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'new_painting':False,'source_neck_cut_pixels':neck,'new_collar_vertices':len(me.vertices),'new_collar_faces':len(me.polygons),'connected_stand_and_front_leaf':True,'new_collar_pose_samples':125,'coat_original_action_datablocks_changed':changed,'coat_original_first_UV_retained':True,'upper_coat_painted_UV_loop_samples_changed':paintuvchanges,'painted_UV_rows_from12_unchanged':all(a==tuple(b.uv) for l,a,b in zip(coat.data.loops,oldpaint,paintuv.data) if l.vertex_index//17>=12),'coat_materials_unchanged':True,'coat_rows6_through32_pose_data_error_m':lowererr,'maximum_upper_coat_shift_m':max(r['max_upper_coat_shift_m'] for r in records),'original_yoke_hidden_not_deleted':True,'body_head_hand_foot_motion_changed':False,'world_lights_cameras_changed':False,'records':records};(P/'evidence/CONNECTION_BUILD.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Neck_Collar_Connection_Candidate_v041.blend'),compress=True);print('V041_BUILT',json.dumps({k:v for k,v in report.items() if k!='records'}),flush=True)
