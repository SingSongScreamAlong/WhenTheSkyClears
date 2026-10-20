"""Native v024: continuous v021 support and v022-inspired trouser/coat drawings.
Three cycles at original31frames/30fps. All output isolated. No frame handlers."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api;import motion_model as M
BASE=P/'reference/BASE_PAINTED_v022_COPY.blend';bpy.ops.wm.open_mainfile(filepath=str(BASE),load_ui=False,use_scripts=False);S=bpy.context.scene;rigs,c=api.initialize_from_scene();rig=rigs['BOY'];T=rig.parent
pack=bpy.data.collections['WTSC_PAINTED_WHOLE_POSE_CORRECTIVES_v022'];pack.name='WTSC_CONTINUOUS_COAT_WALK_v024';oldcol=bpy.data.collections['V022 | editable pose replacement drawings'];oldcol.hide_render=True;oldcol.hide_viewport=True
oldctrl=bpy.data.objects['V022 | WHOLE POSE ART | two selected poses']
if oldctrl.animation_data:oldctrl.animation_data.action=None
oldctrl['loading']=oldctrl['passing']=0.
body=next(o for o in rig.children if o.type=='MESH' and o.get('skin_region')=='body')
for mod in list(body.modifiers):
 if mod.name.startswith('V022'):body.modifiers.remove(mod)
legs={s:bpy.data.objects['V007_BOY | drawn leg '+s] for s in ['near','far']}
for o in legs.values():
 for path in ['hide_render','hide_viewport']:
  try:o.driver_remove(path)
  except:pass
 o.hide_render=o.hide_viewport=False
boots=json.loads((P/'reference/ORIGINAL_BOY_BOOT_PIVOTS_v018.json').read_text());rest=rig.data.bones
def clear_action(o):
 if o.animation_data:
  o.animation_data.action=None
  for t in list(o.animation_data.nla_tracks):o.animation_data.nla_tracks.remove(t)
def fcurves(id):
 if id.animation_data and id.animation_data.action:
  for l in id.animation_data.action.layers:
   for st in l.strips:
    for bag in st.channelbags:yield from bag.fcurves
def pts(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [e.matrix_world@v.co for v in e.data.vertices]
def keylin(id):
 for fc in fcurves(id):
  for k in fc.keyframe_points:k.interpolation='LINEAR'
goals={}
for side in ['near','far']:
 pivot=bpy.data.objects['V020 | '+side+' | ACTUAL_SOLE_PIVOT'];goal=bpy.data.objects['V020 | '+side+' | SOLE_BONE_GOAL'];swing=bpy.data.objects['V020 | '+side+' | SWING_BONE_GOAL'];cts=[ct for ct in c['BOY','ANKLE_'+side].constraints if ct.type=='COPY_TRANSFORMS']
 clear_action(pivot);clear_action(goal);clear_action(swing);pivot.location=(0,0,0);pivot.rotation_euler=(0,0,0);pivot.scale=(1,1,1);goal.matrix_parent_inverse=Matrix.Identity(4)
 cts[0].influence=1.;cts[1].influence=0.;goals[side]=(pivot,goal,cts)
animated=[*c.values(),rig,T,*[g[1] for g in goals.values()]]
for o in animated:clear_action(o)
art=bpy.data.collections.new('V024 | continuous painted representation');pack.children.link(art)
srcdata=json.loads((P/'reference/fbx_source_inspection.json').read_text());SRC={round(r['frame'],6):r for r in srcdata['samples']}
def source(f):
 w=round(2+(f-2)%31,6);B=SRC[w]['bones'];return {n:{e:Vector((-v[e][1],0,v[e][2])) for e in ['head','tail']} for n,v in B.items()}
def gaussian(q,peak,width):d=(q-peak+15.5)%31-15.5;return math.exp(-(d/width)**2)
def cloth(v,H,ch,q):
 z=v.z-H.z;t=z/max(.01,ch.z-H.z);cx=H.x+t*(ch.x-H.x);x=v.x-cx;sx=math.tanh(x/.075);front=.5+.5*math.tanh(x/.045);back=1-front
 load=min(1,gaussian(q,2.25,3.3)+gaussian(q,18.25,3.2));passing=min(1,gaussian(q,8.4,3.8)+gaussian(q,24.6,3.5));lag=math.sin(4*math.pi*(q-1.8)/31)
 fix=max(0,min(1,(.385-z)/.14));fix=fix*fix*(3-2*fix);waist=math.exp(-((z-.16)/.12)**2);low=math.exp(-((z-.025)/.105)**2);middle=math.exp(-((z-.22)/.15)**2)
 dx=(.010*middle-.030*sx*waist-(.055+.035*passing)*front*low+(.016-.012*load)*back*low+.008*lag*low)*fix
 dz=(-.014*load*waist+.045*passing*back*low+.011*front*low-.008*load*back*low)*fix
 # A coherent folded waist surface: convex panel plus compressed diagonal valley.
 fold=z-(.125+.26*x);valley=math.exp(-(fold/.019)**2)*waist;rim=math.exp(-((fold-.023)/.021)**2)*waist
 dx+=(-.007*front*valley*load)*fix;dz+=(-.006*valley*(.45+.55*load))*fix
 dy=-(.014*(1-sx*sx)*middle+.007*(1-sx*sx)*low)*fix
 shade=1+(-.18*back*middle-.26*valley*(.45+.55*load)+.20*rim-.10*front*low+.28*(1-sx*sx)*middle)*fix
 return Vector((dx,dy,dz)),max(.55,min(1.40,shade))
def hermite(A,B,mA,mB,t):return (2*t**3-3*t*t+1)*A+(t**3-2*t*t+t)*mA+(-2*t**3+3*t*t)*B+(t**3-t*t)*mB
def interp(t,knots):
 for (a,v),(b,w) in zip(knots,knots[1:]):
  if t<=b:return v+(w-v)*(t-a)/(b-a)
 return knots[-1][1]
def center(H,K,E,t):
 u=(K-H).normalized();v=(E-K).normalized();mid=(u+v).normalized();l1=(K-H).length;l2=(E-K).length;tk=.58
 return hermite(H,K,u*l1,mid*l1,t/tk) if t<=tk else hermite(K,E,mid*l2,v*l2,(t-tk)/(1-tk))
leg_uv={s:{l.vertex_index:ob.data.uv_layers.active.data[l.index].uv.copy() for l in ob.data.loops} for s,ob in legs.items()}
def trouser(side,oldV,q,D):
 C=[(oldV[2*i]+oldV[2*i+1])/2 for i in range(33)];H=C[0]+Vector((0,0,.060));K=rig.matrix_world@rig.pose.bones['shin_'+side].head;K.y=H.y;E=C[32];hipw=(oldV[1]-oldV[0]).length/2;cw=(oldV[-1]-oldV[-2]).length/2;out=[];uvs=[];alph=[];cols=[0,.035,.27,.5,.73,.965,1]
 for i in range(97):
  t=i/96;Cen=center(H,K,E,t);tan=(center(H,K,E,min(1,t+.002))-center(H,K,E,max(0,t-.002))).normalized();N=Vector((-tan.z,0,tan.x))
  src=interp(t,[(0,0),(.58,.5),(.79,23/32),(.825,24/32),(.91,27/32),(1,1)]);j=min(31,int(src*32));a=src*32-j;uv0=leg_uv[side][2*j].lerp(leg_uv[side][2*j+2],a);uv1=leg_uv[side][2*j+1].lerp(leg_uv[side][2*j+3],a)
  w=interp(t,[(0,hipw),(.22,hipw*.91),(.48,.047),(.58,.044),(.73,.045),(.79,.042),(.825,.0465),(.90,.0465),(.927,.0315),(1,cw)])
  bend=(K-H).normalized().angle((E-K).normalized());cap=math.exp(-((t-.58)/.095)**2);sign=1 if (K-H).cross(E-K).y>=0 else -1
  for jcol,s in enumerate(cols):
   xx=s*2-1;v=Cen+N*(xx*w+sign*.0055*cap*max(0,xx*sign)**2*min(1,bend/.8));roll=math.exp(-((t-.865)/.038)**2);v+=tan*(roll*(.003*(s-.5)+.007*(1-xx*xx)));v.x-=D;out.append(v);uvs.append(uv0.lerp(uv1,s*.98+.01));alph.append(0 if jcol in [0,6] else 1)
 return out,uvs,alph
bodycache=[];shadecache=[];legcache={'near':[],'far':[]};legmapping={};metrics=[]
for step in range(373):
 q=step/4;f=1+q;S.frame_set(int(f),subframe=f-int(f));saved=[]
 for o in animated:
  if o.animation_data and o.animation_data.action:saved.append((o,o.animation_data.action,o.animation_data.action_slot));o.animation_data.action=None
 r=M.evaluate(q);D=r['D'];T.location=(D,0,0);bpy.context.view_layer.update();Hworld=Vector((r['H'][0],0,r['H'][1]));H=Hworld-Vector((D,0,0))
 for side in ['near','far']:
  pivot,goal,cts=goals[side];d=r['feet'][side];flat=Matrix(boots[side]['flat_bone']);F=Matrix.Rotation(d['angle'],4,'Y')@flat.to_3x3().to_4x4();F.translation=(d['A'][0],0,d['A'][1]);goal.matrix_world=F;pivot['active_vertex']=d['meta'].get('vertex',-1)
 pel=rest['pelvis'].matrix_local;api.target('BOY','HIP',Matrix.Translation(H)@Matrix.Rotation(r['pelvis'],4,'Y')@Matrix.Translation(-pel.translation)@pel)
 rv=rest['chest'].tail_local-rest['chest'].head_local;chrot=r['chest']-math.atan2(rv.x,rv.z);cd=Matrix.Translation(H)@Matrix.Rotation(chrot,4,'Y')@Matrix.Translation(-pel.translation);api.target('BOY','CHEST',cd@rest['chest'].matrix_local);h0=cd@rest['head'].matrix_local;hv=rest['head'].tail_local-rest['head'].head_local;turn=r['head']-chrot-math.atan2(hv.x,hv.z);api.target('BOY','HEAD_PROFILE',Matrix.Translation(h0.translation)@Matrix.Rotation(turn,4,'Y')@Matrix.Translation(-h0.translation)@h0);bpy.context.view_layer.update()
 for side in ['near','far']:
  hip=rig.pose.bones['thigh_'+side].head;K=Vector((r['knees'][side][0]-D,hip.y,r['knees'][side][1]));A=Vector((r['feet'][side]['A'][0]-D,hip.y,r['feet'][side]['A'][1]));api.target('BOY','LEG_POLE_'+side,Matrix.Translation(K+(K-(hip+A)/2)*4))
 B=source(9.75+q)
 for side,ss in [('near','R'),('far','L')]:
  sh=rig.pose.bones['upper_arm_'+side].head;source_u=(B['Elbow_'+ss]['head']-B['Shoulder_'+ss]['head']).normalized();su=math.atan2(source_u.x,-source_u.z);leg_u=M.evaluate(q-1)['angles'][side][0];mean_u={'near':.1142809274577463,'far':.2344164084896745}[side];uangle=-.60*(leg_u-mean_u)+.20*(su+.15);vangle=uangle+.32+.06*math.sin(2*math.pi*(q-(0 if side=='near' else 16))/31);u=Vector((math.sin(uangle),0,-math.cos(uangle)));v=Vector((math.sin(vangle),0,-math.cos(vangle)));E=sh+u*rest['upper_arm_'+side].length;W=E+v*rest['forearm_'+side].length;L=rest['upper_arm_'+side].length+rest['forearm_'+side].length
  if L-(W-sh).length<.0008:W=sh+(W-sh).normalized()*(L-.0008)
  hand_angle=vangle+.08;hd=Vector((math.sin(hand_angle),0,-math.cos(hand_angle)));ang=math.atan2(hd.z,hd.x);hb=rest['hand_'+side];dd=hb.tail_local-hb.head_local;rot=math.atan2(math.cos(ang),math.sin(ang))-math.atan2(dd.x,dd.z);Wmat=Matrix.Translation(W)@Matrix.Rotation(rot,4,'Y')@hb.matrix_local.to_3x3().to_4x4();ob=c['BOY','WRIST_'+side]
  for key in ['TorsoFollow','BraceFollow','Reach','Brace','FrontLayer']:ob[key]=0.
  ob.update_tag();api.target('BOY','WRIST_'+side,Wmat);api.target('BOY','ARM_POLE_'+side,Matrix.Translation(E+(E-(sh+W)/2)*4))
 api.choose_planes('BOY',{});bpy.context.view_layer.update()
 if q<=30 and q==int(q):
  ch=rig.matrix_world@rig.pose.bones['chest'].tail;inv=body.matrix_world.inverted().to_3x3();deltas=[];shades=[]
  for v in pts(body):
   delta,shade=cloth(v,Hworld,ch,q);deltas.append(inv@delta);shades.append(shade)
  bodycache.append(deltas);shadecache.append(shades)
  for side,ob in legs.items():
   v,u,a=trouser(side,pts(ob),q,D);legcache[side].append(v);legmapping[side]=(u,a)
 if q==int(q) or any(abs(q-t)<.001 for t in [18.5,19.25,31]):
  feet=[]
  for side in ['near','far']:
   V=pts(bpy.data.objects[boots[side]['object']]);d=r['feet'][side];err=None
   if d['mode']=='CONTACT':
    j=d['meta']['vertex'];err=(V[j]-Vector((d['meta']['anchor_xz'][0],V[j].y,0))).length
   feet.append({'side':side,'mode':d['mode'],'actual_sole_min_z_m':min(v.z for v in V),'contact_error_m':err})
  metrics.append({'q':q,'feet':feet,'IK':api.reach_report()})
 for o,a,slot in saved:o.animation_data.action=a;o.animation_data.action_slot=slot
 api.key_controls(f);T.keyframe_insert('location',frame=f)
 for side in ['near','far']:
  pivot,goal,_=goals[side]
  for path in ['location','rotation_quaternion','scale']:goal.keyframe_insert(path,frame=f)
  pivot.keyframe_insert('["active_vertex"]',frame=f)
for o in animated:keylin(o)
for side in ['near','far']:
 for fc in fcurves(goals[side][0]):
  for k in fc.keyframe_points:k.interpolation='CONSTANT'
# Continuous coat: interpolate local post-deformation displacements and pigment-plane value.
g=bpy.data.node_groups.new('V024 | continuous shaped and shaded painted coat','GeometryNodeTree');g.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');g.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');n=g.nodes;L=g.links;inp=n.new('NodeGroupInput');out=n.new('NodeGroupOutput');vs=None;ss=None
for i in range(31):
 va=body.data.attributes.new('V024_coat_delta_%02d'%i,'FLOAT_VECTOR','POINT');va.data.foreach_set('vector',[x for v in bodycache[i] for x in v]);sa=body.data.attributes.new('V024_coat_shade_%02d'%i,'FLOAT','POINT');sa.data.foreach_set('value',shadecache[i])
 w=n.new('ShaderNodeValue')
 for f in range(1,33):w.outputs[0].default_value=float((f-1)%31==i);w.outputs[0].keyframe_insert('default_value',frame=f)
 av=n.new('GeometryNodeInputNamedAttribute');av.data_type='FLOAT_VECTOR';av.inputs['Name'].default_value=va.name;sc=n.new('ShaderNodeVectorMath');sc.operation='SCALE';L.new(av.outputs['Attribute'],sc.inputs[0]);L.new(w.outputs[0],sc.inputs[3])
 aa=n.new('GeometryNodeInputNamedAttribute');aa.data_type='FLOAT';aa.inputs['Name'].default_value=sa.name;mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';L.new(aa.outputs['Attribute'],mul.inputs[0]);L.new(w.outputs[0],mul.inputs[1])
 if vs is None:vs=sc.outputs[0];ss=mul.outputs[0]
 else:
  add=n.new('ShaderNodeVectorMath');add.operation='ADD';L.new(vs,add.inputs[0]);L.new(sc.outputs[0],add.inputs[1]);vs=add.outputs[0];addf=n.new('ShaderNodeMath');addf.operation='ADD';L.new(ss,addf.inputs[0]);L.new(mul.outputs[0],addf.inputs[1]);ss=addf.outputs[0]
pos=n.new('GeometryNodeSetPosition');L.new(inp.outputs['Geometry'],pos.inputs['Geometry']);L.new(vs,pos.inputs['Offset']);store=n.new('GeometryNodeStoreNamedAttribute');store.data_type='FLOAT';store.domain='POINT';store.inputs['Name'].default_value='V024CoatShade';L.new(pos.outputs['Geometry'],store.inputs['Geometry']);L.new(ss,store.inputs['Value']);L.new(store.outputs['Geometry'],out.inputs['Geometry']);mod=body.modifiers.new('V024 continuous coat contour, convexity and folded value planes','NODES');mod.node_group=g
keylin(g)
for fc in fcurves(g):fc.modifiers.new('CYCLES')
mat=body.data.materials[0].copy();mat.name='V024 | original coat pigments with posed fold value';body.data.materials[0]=mat;nd=mat.node_tree.nodes;lk=mat.node_tree.links;em=next(x for x in nd if x.type=='EMISSION');oldlink=em.inputs['Color'].links[0];original=oldlink.from_socket;lk.remove(oldlink);a=nd.new('ShaderNodeAttribute');a.attribute_name='V024CoatShade';mul=nd.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1.;lk.new(original,mul.inputs[1]);lk.new(a.outputs['Fac'],mul.inputs[2]);lk.new(mul.outputs[0],em.inputs['Color'])
# Two persistent trouser drawings with31interpolated shape samples; no visibility switches.
for side in ['near','far']:
 verts=legcache[side][0];faces=[]
 for i in range(96):
  for j in range(6):a=i*7+j;faces.append((a,a+1,a+8,a+7))
 mesh=bpy.data.meshes.new('V024 continuous '+side+' trouser drawing');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new(mesh.name,mesh);art.objects.link(ob);ob.parent=T;mesh.materials.append(bpy.data.materials['V022 | original trouser pigments | relocated rolled cuff']);uv=mesh.uv_layers.new(name='Original v015 pigments, fixed anatomical mapping');uvs,alph=legmapping[side]
 for l in mesh.loops:uv.data[l.index].uv=uvs[l.vertex_index]
 col=mesh.color_attributes.new(name='V022_EdgeAlpha',type='FLOAT_COLOR',domain='POINT')
 for i,a in enumerate(alph):col.data[i].color=(1,1,1,a)
 ob.shape_key_add(name='Basis')
 for i in range(1,31):
  key=ob.shape_key_add(name='V024 pose sample %02d'%i);key.data.foreach_set('co',[x for v in legcache[side][i] for x in v])
  for f in range(1,33):key.value=float((f-1)%31==i);key.keyframe_insert('value',frame=f)
 keylin(mesh.shape_keys)
 for fc in fcurves(mesh.shape_keys):fc.modifiers.new('CYCLES')
 ob['V024_scope']='Continuous pose-drawing proof, not a general3D trouser model'
for ob in legs.values():ob.hide_render=True
for colname in ['V020 | source skeleton render','V020 | child native skeleton render']:bpy.data.collections[colname].hide_render=True
bpy.data.objects['V020 | SOURCE52 | exact FBX sampled poses'].hide_set(True)
stage=bpy.data.collections['V020 | study stage and sole controls'];cam=bpy.data.objects.new('V024 | CLOSE portrait',bpy.data.cameras.new('V024 portrait close'));stage.objects.link(cam);cam.parent=T;cam.location=(0,-7,.75);cam.rotation_euler=(math.pi/2,0,0);cam.data.type='ORTHO';cam.data.sensor_fit='HORIZONTAL';cam.data.ortho_scale=1.10
# Small world-fixed floor cues so travelling boots can be judged against stationary marks.
floor=bpy.data.materials.new('V024 muted floor ruler');floor.use_nodes=True;ns=floor.node_tree.nodes;ns.clear();e=ns.new('ShaderNodeEmission');e.inputs[0].default_value=(.52,.51,.48,1);o=ns.new('ShaderNodeOutputMaterial');floor.node_tree.links.new(e.outputs[0],o.inputs['Surface'])
verts=[];faces=[]
for j in range(-80,161):
 x=j*.1;z=.008 if j%5==0 else .004;i=len(verts);verts.extend([(x-.0006,-.08,0),(x+.0006,-.08,0),(x+.0006,-.08,z),(x-.0006,-.08,z)]);faces.append((i,i+1,i+2,i+3))
mesh=bpy.data.meshes.new('V024 floor ticks');mesh.from_pydata(verts,[],faces);ob=bpy.data.objects.new(mesh.name,mesh);stage.objects.link(ob);mesh.materials.append(floor)
S.render.fps=30;S.frame_start=1;S.frame_end=93;S.render.resolution_percentage=100;S['V024_status']='Isolated continuous3cycle walking/cloth proof; artistic approval OPEN';S['V024_stride_m']=M.STRIDE;S['V024_period_frames']=31;S['V024_art']='Original v015 source image retained. Convex shaped coat and posed pigment fold value; two continuously morphing trouser drawings.';S['V024_no_hard_pose_switches']=True
S.frame_set(17,subframe=.25);S.camera=cam;S.render.resolution_x=360;S.render.resolution_y=540
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Continuous_Coat_Walk_v024.blend'),compress=True)
(P/'evidence/authored_contact_checks.json').write_text(json.dumps(metrics,indent=2))
print('V024_NATIVE',json.dumps({'unreachable':[(r['q'],k) for r in metrics for k in r['IK'] if not k['reachable']],'max_contact_error_m':max(d['contact_error_m'] for r in metrics for d in r['feet'] if d['contact_error_m'] is not None),'min_rendered_sole_z_m':min(d['actual_sole_min_z_m'] for r in metrics for d in r['feet'])}))
# Small one-cycle proof only. Final render is a separate, coordinated operation.
S.render.resolution_x=240;S.render.resolution_y=360;D=P/'previews/proof';D.mkdir(exist_ok=True)
for f in range(1,33):S.frame_set(f);S.render.filepath=str(D/('%04d.png'%f));bpy.ops.render.render(write_still=True)
print('V024_PROOF_RENDERED')

