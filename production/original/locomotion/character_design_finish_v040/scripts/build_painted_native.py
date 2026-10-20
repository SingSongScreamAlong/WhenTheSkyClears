"""Isolated painted look candidate. Keeps body motion and original source parts.
New pixels are the unedited ImageGen parts atlas; UV registration is native.
The new profile is a fixed-view painted mesh, not a turnaround or 3D head.
"""
import bpy,json,math,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];SRC=P/'reference/PRESERVED_MOVEMENT_COLOR_v039.blend';bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);S=bpy.context.scene;R=bpy.data.objects['LOCO_BOY | RIG'];S.frame_set(1);bpy.context.view_layer.update();fore=S.view_layers['V025 | original foreground'];fore.update();atlas=bpy.data.images.load(str(P/'textures/WTSC_Boy_Painted_Parts_Atlas_v040.png'),check_existing=True);atlas.pack();W,H=atlas.size;raw=np.empty(W*H*4,dtype=np.float32);atlas.pixels.foreach_get(raw);pix=raw.reshape(H,W,4)[::-1];alpha=pix[:,:,3];UVNAME='V040 | separated painted part registration';records={};source_actions={a.name:hashlib.sha256(repr([(f.data_path,f.array_index,[(tuple(k.co),k.interpolation) for k in f.keyframe_points]) for l in a.layers for st in l.strips for bag in st.channelbags for f in bag.fcurves]).encode()).hexdigest() for a in bpy.data.actions}
ROIS={'head':(0,0,440,490),'coat':(500,0,820,585),'sleeve':(950,0,1200,585),'arm':(110,600,330,1190),'pants':(510,590,735,1245),'boot':(815,820,1254,1195)}
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def edges(role,y):
 x0,y0,x1,y1=ROIS[role];y=max(y0,min(y1-1,int(round(y))));row=alpha[y,x0:x1];idx=np.flatnonzero(row>.95)
 if len(idx)==0:
  rows=np.flatnonzero((alpha[y0:y1,x0:x1]>.95).any(axis=1));y=int(rows[np.argmin(abs(rows+y0-y))]+y0);idx=np.flatnonzero(alpha[y,x0:x1]>.95)
 return x0+int(idx[0]),x0+int(idx[-1]),y
def strip(role,s,y,inset=.06):
 a,b,y=edges(role,y)
 if role=='coat':
  # Empty armhole source is not a painted torso surface. Sample its adjacent
  # opaque side/front cloth until the armhole ends, then ease to the back hem.
  a=max(a,638*(1-smooth((y-245)/65))+a*smooth((y-245)/65))
 s=inset+(1-2*inset)*max(0,min(1,s));x=a+(b-a)*s;return (x/W,1-y/H)
def adduv(o,V):
 u=o.data.uv_layers.get(UVNAME) or o.data.uv_layers.new(name=UVNAME)
 for l in o.data.loops:u.data[l.index].uv=V[l.vertex_index]
 o.data.uv_layers.active_index=0
 return u
cache={}
def finishmat(o,kind):
 original=o.material_slots[0].material;key=(original.name,kind)
 if key in cache:m=cache[key]
 else:
  original.use_fake_user=True;m=original.copy();m.name='V040 PAINT | '+kind+' | '+original.name;ns=m.node_tree.nodes;lk=m.node_tree.links;uv=ns.new('ShaderNodeUVMap');uv.uv_map=UVNAME;tex=ns.new('ShaderNodeTexImage');tex.name='V040 original generated separated atlas | unedited';tex.image=atlas;tex.interpolation='Linear';tex.extension='EXTEND';lk.new(uv.outputs['UV'],tex.inputs['Vector'])
  if kind=='coat':
   ramp=next(n for n in ns if n.type=='VALTORGB' and n.name.startswith('V038 coat'));targets=[link.to_socket for link in list(ramp.outputs['Color'].links)];assert targets
   for socket in targets:
    for l in list(socket.links):lk.remove(l)
    lk.new(tex.outputs['Color'],socket)
  else:
   for em in [n for n in ns if n.type=='EMISSION']:
    for l in list(em.inputs['Color'].links):lk.remove(l)
    lk.new(tex.outputs['Color'],em.inputs['Color'])
  m['V040_scope']='Generated painted part atlas via explicit extra native UV layer; old alpha/edge masks retained. Original image and UVs retained. No light changes.';cache[key]=m
 o.material_slots[0].link='OBJECT';o.material_slots[0].material=m;records[o.name]={'kind':kind,'original_material':original.name,'paint_material':m.name,'original_UV_layers_retained':True,'geometry_and_actions_unchanged':True}
for side in ['near','far']:
 for part in ['drawn sleeve','drawn source gray cuff','drawn skin']:
  o=bpy.data.objects['V007_BOY | '+part+' '+side];count=len(o.data.vertices)//2;coords=[]
  for i in range(len(o.data.vertices)):
   s=i%2;t=(i//2)/(count-1)
   if part=='drawn skin':coords.append(strip('arm',s,623+t*(954-623)))
   else:
    if 'cuff' in part:t=(15+i//2)/18
    y=35+(475-35)*t/(15/18) if t<15/18 else 475+(550-475)*(t-15/18)/(3/18);coords.append(strip('sleeve',s,y))
  adduv(o,coords);finishmat(o,'skin' if part=='drawn skin' else 'linen' if 'cuff' in part else 'sleeve')
 o=bpy.data.objects['V007_BOY | articulated drawn hand '+side];B=R.data.bones['hand_'+side].matrix_local.inverted();V=[B@v.co for v in o.data.vertices];xmin,xmax=min(v.x for v in V),max(v.x for v in V);ymin,ymax=min(v.y for v in V),max(v.y for v in V);coords=[strip('arm',1-(v.x-xmin)/(xmax-xmin),953+(v.y-ymin)/(ymax-ymin)*(1166-953),.09) for v in V];adduv(o,coords);finishmat(o,'skin hand')
 o=bpy.data.objects['V024 continuous '+side+' trouser drawing'];coords=[]
 for i in range(len(o.data.vertices)):
  t=(i//7)/96;s=(i%7)/6;y=609+(1140-609)*t/.92 if t<.92 else 1140+(1204-1140)*(t-.92)/.08;coords.append(strip('pants',s,y))
 adduv(o,coords);finishmat(o,'trousers')
coat=bpy.data.objects['V037 | coherent charcoal coat | five pose study'];adduv(coat,[strip('coat',(i%17)/16,100+(550-100)*(i//17)/32,.045) for i in range(len(coat.data.vertices))]);finishmat(coat,'coat')
body=bpy.data.objects['LOCO_BOY | PAINT body'];V=[v.co for v in body.data.vertices];xmin,xmax=min(v.x for v in V),max(v.x for v in V);zmin,zmax=min(v.z for v in V),max(v.z for v in V);adduv(body,[strip('sleeve',(v.x-xmin)/(xmax-xmin),488+50*(zmax-v.z)/(zmax-zmin),.15) for v in V]);finishmat(body,'linen collar')
# Resolve the inherited broad collar/yoke drawing into a cloth shoulder with
# two small linen folds. Coordinates are calculated from the original UVs at
# the existing F1 chest pose, then remain fixed to that UV field in animation.
# They are not camera/world-following overlays or an extra light.
bpy.context.view_layer.update();e=body.evaluated_get(bpy.context.view_layer.depsgraph);qa=[];qb=[]
for li in e.data.loops:
 uv=e.data.uv_layers[0].data[li.index].uv;w=e.matrix_world@e.data.vertices[li.vertex_index].co;qa.append([uv.x,uv.y,1]);qb.append([w.x,w.z])
coefbody=np.linalg.lstsq(np.array(qa),np.array(qb),rcond=None)[0];fiterr=float(np.max(np.abs(np.array(qa)@coefbody-np.array(qb))));assert fiterr<1e-5,fiterr
bm=body.material_slots[0].material;bn=bm.node_tree.nodes;bl=bm.node_tree.links
def mn(op,a,b=None):
 n=bn.new('ShaderNodeMath');n.operation=op
 for value,i in [(a,0),(b,1)]:
  if value is None:continue
  if isinstance(value,(float,int)):n.inputs[i].default_value=value
  else:bl.new(value,n.inputs[i])
 return n.outputs[0]
def poly_mask(x,z,pts):
 from mathutils.geometry import tessellate_polygon
 vv=[Vector((a,b,0)) for a,b in pts];result=None
 for triangle in tessellate_polygon([vv]):
  tri=tuple(vv[i] for i in triangle) if isinstance(triangle[0],int) else tuple(triangle);orient=(tri[1].x-tri[0].x)*(tri[2].y-tri[0].y)-(tri[1].y-tri[0].y)*(tri[2].x-tri[0].x);sgn=1 if orient>0 else -1;inside=None
  for a,b in zip(tri,tri[1:]+tri[:1]):
   cross=mn('SUBTRACT',mn('MULTIPLY',b.x-a.x,mn('SUBTRACT',z,a.y)),mn('MULTIPLY',b.y-a.y,mn('SUBTRACT',x,a.x)));q=mn('GREATER_THAN',mn('MULTIPLY',cross,sgn),-.0000001);inside=q if inside is None else mn('MULTIPLY',inside,q)
  result=inside if result is None else mn('MAXIMUM',inside,result)
 return result
buv=bn.new('ShaderNodeUVMap');buv.uv_map=body.data.uv_layers[0].name;sep=bn.new('ShaderNodeSeparateXYZ');bl.new(buv.outputs[0],sep.inputs[0]);xz=[mn('ADD',mn('ADD',mn('MULTIPLY',sep.outputs['X'],float(coefbody[0,i])),mn('MULTIPLY',sep.outputs['Y'],float(coefbody[1,i]))),float(coefbody[2,i])) for i in range(2)]
ring=poly_mask(*xz,[(-.053,1.119),(.031,1.101),(.052,1.078),(-.057,1.098)]);leaf=poly_mask(*xz,[(.031,1.101),(.077,1.079),(.061,1.048),(.040,1.071)]);linen=bn.get('V040 original generated separated atlas | unedited');coatfield=bn.new('ShaderNodeTexImage');coatfield.name='V040 quiet shoulder cloth field';coatfield.image=atlas;coatfield.inputs['Vector'].default_value=(710/W,1-155/H,0);dark=bn.new('ShaderNodeMixRGB');dark.blend_type='MULTIPLY';dark.inputs[0].default_value=1.;bl.new(linen.outputs['Color'],dark.inputs[1]);dark.inputs[2].default_value=(.82,.82,.82,1);mix1=bn.new('ShaderNodeMixRGB');bl.new(ring,mix1.inputs[0]);bl.new(coatfield.outputs['Color'],mix1.inputs[1]);bl.new(dark.outputs[0],mix1.inputs[2]);mix2=bn.new('ShaderNodeMixRGB');bl.new(leaf,mix2.inputs[0]);bl.new(mix1.outputs[0],mix2.inputs[1]);bl.new(linen.outputs['Color'],mix2.inputs[2])
constant_uv=bn.new('ShaderNodeCombineXYZ');constant_uv.name='V040 garment-attached shoulder painting coordinates';shoulder_u=mn('DIVIDE',mn('ADD',690,mn('MULTIPLY',mn('DIVIDE',mn('ADD',xz[0],.081),.176),34)),W);shoulder_v=mn('SUBTRACT',1,mn('DIVIDE',mn('ADD',105,mn('MULTIPLY',mn('DIVIDE',mn('SUBTRACT',1.122,xz[1]),.123),100)),H));bl.new(shoulder_u,constant_uv.inputs['X']);bl.new(shoulder_v,constant_uv.inputs['Y']);bl.new(constant_uv.outputs[0],coatfield.inputs['Vector'])
for em in [n for n in bn if n.type=='EMISSION']:
 for link in list(em.inputs['Color'].links):bl.remove(link)
 bl.new(mix2.outputs[0],em.inputs['Color'])
records[body.name]['collar_repair']='Inherited broad cream yoke becomes coat-colored shoulder; two small garment-UV-attached linen collar folds, no source raster edit.';records[body.name]['UV_to_existing_F1_chest_affine_fit_error_m']=fiterr
near=bpy.data.objects['V033 | near | canonical painted shoe'];V=[v.co for v in near.data.vertices];xmin,xmax=min(v.x for v in V),max(v.x for v in V);zmin,zmax=min(v.z for v in V),max(v.z for v in V)
def rowx(z):
 xs=[]
 for ed in near.data.edges:
  a,b=[near.data.vertices[i].co for i in ed.vertices]
  if min(a.z,b.z)-1e-7<=z<=max(a.z,b.z)+1e-7:
   if abs(b.z-a.z)<1e-8:xs.extend([a.x,b.x])
   else:xs.append(a.x+(b.x-a.x)*(z-a.z)/(b.z-a.z))
 return (min(xs),max(xs)) if xs else (xmin,xmax)
uv=[]
for v in V:
 a,b=rowx(v.z);s=(v.x-a)/(b-a) if b-a>1e-7 else .5;uv.append(strip('boot',s,850+(1169-850)*(zmax-v.z)/(zmax-zmin),.025))
adduv(near,uv);finishmat(near,'matching leather boot');far=bpy.data.objects['V033 | far | canonical painted shoe'];far.material_slots[0].link='OBJECT';far.material_slots[0].material=near.material_slots[0].material;records[far.name]={'kind':'matching leather boot','same_mesh_and_material_as_near':True,'geometry_and_actions_unchanged':True}
# A new fixed-profile head paint mesh is bound to the original rigid head bone.
# Preserve the source head hidden for comparison; do not rotate a flat card for turns.
old=bpy.data.objects['PERF_BOY | original head'];oldimage=bpy.data.images['Pair_Painterly_Near_Age_v015.png'];ow,oh=oldimage.size;ar=np.empty(ow*oh*4,dtype=np.float32);oldimage.pixels.foreach_get(ar);oa=ar.reshape(oh,ow,4)[::-1,:,3];A=[];B=[]
for l in old.data.loops:
 uv=old.data.uv_layers.active.data[l.index].uv;A.append([uv.x*ow,(1-uv.y)*oh,1]);v=old.data.vertices[l.vertex_index].co;B.append([v.x,v.z])
coef=np.linalg.lstsq(np.array(A),np.array(B),rcond=None)[0];aa=np.array(A);x0,x1=int(aa[:,0].min()),int(aa[:,0].max())+1;y0,y1=int(aa[:,1].min()),int(aa[:,1].max())+1;yy,xx=np.mgrid[y0:y1,x0:x1];inside=np.zeros(xx.shape,dtype=bool)
for poly in old.data.polygons:
 tri=[]
 for li in poly.loop_indices:
  uv=old.data.uv_layers.active.data[li].uv;tri.append((uv.x*ow,(1-uv.y)*oh))
 masks=[]
 for a,b in zip(tri,tri[1:]+tri[:1]):masks.append((b[0]-a[0])*(yy-a[1])-(b[1]-a[1])*(xx-a[0]))
 inside |= np.logical_or(np.logical_and.reduce([m>=0 for m in masks]),np.logical_and.reduce([m<=0 for m in masks]))
mask=inside&(oa[y0:y1,x0:x1]>.3);sourceRest=np.column_stack([xx[mask],yy[mask],np.ones(mask.sum())])@coef;rx0,rz0=sourceRest.min(axis=0);rx1,rz1=sourceRest.max(axis=0);gx0,gy0,gx1,gy1=ROIS['head'];py,px=np.nonzero(alpha[gy0:gy1,gx0:gx1]>.3);gx0,gx1=int(px.min()),int(px.max())+1;gy0,gy1=int(py.min()),int(py.max())+1
# Fit to the exact old painted occupancy in rest space, preserving head scale.
verts=[(rx0,-.045,rz0),(rx1,-.045,rz0),(rx1,-.045,rz1),(rx0,-.045,rz1)];me=bpy.data.meshes.new('V040 | editable fixed profile paint plane');me.from_pydata(verts,[],[(0,1,2,3)]);me.update();head=old.copy();head.data=me;head.name='V040 | painted boy profile and neck';head.animation_data_clear()
for c in old.users_collection:c.objects.link(head)
head.vertex_groups.clear();groups={old.vertex_groups[g.group].name for v in old.data.vertices for g in v.groups if g.weight>.999};assert groups=={'head'},groups;vg=head.vertex_groups.new(name='head');vg.add(list(range(4)),1,'REPLACE');hu=me.uv_layers.new(name=UVNAME)
for l,u in zip(me.loops,[(gx0/W,1-gy1/H),(gx1/W,1-gy1/H),(gx1/W,1-gy0/H),(gx0/W,1-gy0/H)]):hu.data[l.index].uv=u
m=bpy.data.materials.new('V040 PAINT | complete fixed child profile');m.use_nodes=True;n=m.node_tree.nodes;n.clear();lk=m.node_tree.links;uv=n.new('ShaderNodeUVMap');uv.uv_map=UVNAME;tex=n.new('ShaderNodeTexImage');tex.image=atlas;tex.interpolation='Linear';lk.new(uv.outputs['UV'],tex.inputs['Vector']);em=n.new('ShaderNodeEmission');lk.new(tex.outputs['Color'],em.inputs['Color']);tr=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');lk.new(tex.outputs['Alpha'],mix.inputs[0]);lk.new(tr.outputs[0],mix.inputs[1]);lk.new(em.outputs[0],mix.inputs[2]);out=n.new('ShaderNodeOutputMaterial');lk.new(mix.outputs[0],out.inputs['Surface']);me.materials.append(m);head.hide_render=False;head.hide_viewport=False;old.hide_render=True;old.hide_viewport=True;head['V040_scope']='Intentional new painted fixed right profile, fitted to original painted head occupancy and bound to unchanged head bone. No 3D head, head turn or facial rig claimed. Original head preserved hidden.'
newactions={a.name:hashlib.sha256(repr([(f.data_path,f.array_index,[(tuple(k.co),k.interpolation) for k in f.keyframe_points]) for l in a.layers for st in l.strips for bag in st.channelbags for f in bag.fcurves]).encode()).hexdigest() for a in bpy.data.actions};assert source_actions==newactions;assert near.data==far.data and near.material_slots[0].material==far.material_slots[0].material
S['V040_status']='ISOLATED PAINTED CHARACTER LOOK STUDY, responding to4/10 model feedback. Original preferred walk/coat cycle intact. New separated painted atlas, explicit extra UVs and a new fixed-profile head mesh. Not approved or production integrated. New illustration is not animation quality evidence.';text=bpy.data.texts.new('READ_FIRST_v040');text.write(S['V040_status']);S.frame_set(1);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=480;S.render.resolution_y=720;S.render.resolution_percentage=100
report={'scope':S['V040_status'],'blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'atlas_sha256':hashlib.sha256((P/'textures/WTSC_Boy_Painted_Parts_Atlas_v040.png').read_bytes()).hexdigest(),'atlas_unedited_and_packed':True,'material_registrations':records,'source_action_datablocks_unchanged':source_actions==newactions,'intentional_head_geometry_change':{'source_preserved_hidden':old.name,'new_head':head.name,'rest_painted_occupancy_bounds':[[float(rx0),float(rx1)],[float(rz0),float(rz1)]],'atlas_head_pixel_bounds':[gx0,gy0,gx1,gy1],'same_original_head_bone_binding':True,'fixed_profile_only':True},'original_mesh_rest_shape_and_original_UVs_retained_except_new_separate_head':True,'lighting_world_timing_foot_paths_unchanged':True,'shoe_geometry_and_new_material_shared':True,'generated_source_limitations':['Exploratory asset design includes coat buttons/pocket and a new profile/hair painting; identity/design acceptance is pending.','Body outlines and hand contours are inherited; mapped painting alone does not finish the model.']};(P/'evidence/NATIVE_PAINTED_BUILD.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Painted_Character_Look_STUDY_v040.blend'),compress=True);print('V040_PAINTED_NATIVE_BUILT',json.dumps({k:v for k,v in report.items() if k!='material_registrations'}),flush=True)
