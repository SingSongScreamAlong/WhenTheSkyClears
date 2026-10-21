"""One passing-pose geometry corrective. Original painting/topology/rig retained."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api
BASE=P/'native/WTSC_Child_Coherent_Support_Eight_Poses_v021.blend';bpy.ops.wm.open_mainfile(filepath=str(BASE),load_ui=False,use_scripts=False);S=bpy.context.scene;rigs,c=api.initialize_from_scene();rig=rigs['BOY'];sol=json.loads((P/'evidence/coherent_pose_solution.json').read_text());phases=sol['poses'];boots=json.loads((P/'reference/ORIGINAL_BOY_BOOT_PIVOTS_v018.json').read_text());chosen=phases[6];F=chosen['study_frame_30fps']
def points(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [e.matrix_world@v.co for v in e.data.vertices]
def digest(x):return hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest()
def art_identity():
 return {o.name:{'vertices':digest([list(v.co) for v in o.data.vertices]),'UV':digest([[list(v.uv) for v in l.data] for l in o.data.uv_layers]),'weights':digest([[(g.group,g.weight) for g in v.groups] for v in o.data.vertices]),'materials':[m.name for m in o.data.materials]} for o in rig.children if o.type=='MESH'}
base_identity=art_identity();base_pose={};fresh=[]
for p in phases:
 f=p['study_frame_30fps'];S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();base_pose[p['index']]={o.name:points(o) for o in rig.children if o.type=='MESH'};ff=[]
 for side in ['near','far']:
  d=p['feet'][side];V=points(bpy.data.objects[boots[side]['object']]);expected=Vector((d['anchor_xz'][0],boots[side]['vertices'][d['vertex']][1],d['anchor_xz'][1])) if 'anchor_xz' in d else None;ff.append({'side':side,'mode':d['mode'],'minimum_actual_sole_z_m':min(v.z for v in V),'contact_error_m':(V[d['vertex']]-expected).length if expected is not None else None})
 fresh.append({'phase':p['name'],'study_frame':f,'IK':api.reach_report(),'feet':ff,'hip_world':list(c['BOY','HIP'].matrix_world.translation)})
(P/'evidence/fresh_base_pose_check.json').write_text(json.dumps(fresh,indent=2));bad=[(p['phase'],r) for p in fresh for r in p['IK'] if not r['reachable']]
if bad:raise RuntimeError('Fresh corrected pose unreachable: '+repr(bad))
S.frame_set(int(F),subframe=F-int(F));bpy.context.view_layer.update();pack=bpy.data.collections['WTSC_CHILD_SUPPORT_POSES_v021'];pack.name='WTSC_CHILD_PASSING_ART_VARIANT_v021';ctrl=bpy.data.objects.new('V021 | PASSING ART CORRECTIVE | amount',None);pack.objects.link(ctrl);ctrl['amount']=1.;ctrl.id_properties_ui('amount').update(min=0,max=1,description='Pose-specific torso/hem and near swing knee shape study.1only at L_PASSING; no interpolation acceptance.')
for p in phases+[dict(phases[0],study_frame_30fps=32,index=9)]:ctrl['amount']=float(p['index']==chosen['index']);ctrl.keyframe_insert('["amount"]',frame=p['study_frame_30fps'])
for l in ctrl.animation_data.action.layers:
 for st in l.strips:
  for bag in st.channelbags:
   for fc in bag.fcurves:
    for k in fc.keyframe_points:k.interpolation='CONSTANT'
def add_offset(o,delta):
 name='V021_pose_delta';attr=o.data.attributes.get(name) or o.data.attributes.new(name,'FLOAT_VECTOR','POINT');attr.data.foreach_set('vector',[x for v in delta for x in v]);g=bpy.data.node_groups.new('V021 pose offset | '+o.name,'GeometryNodeTree');g.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');g.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry');n=g.nodes;L=g.links;inp=n.new('NodeGroupInput');out=n.new('NodeGroupOutput');a=n.new('GeometryNodeInputNamedAttribute');a.data_type='FLOAT_VECTOR';a.inputs['Name'].default_value=name;amount=n.new('ShaderNodeValue');amount.outputs[0].default_value=1;fc=amount.outputs[0].driver_add('default_value');v=fc.driver.variables.new();v.name='amount';v.targets[0].id=ctrl;v.targets[0].data_path='["amount"]';fc.driver.expression='max(0,min(1,amount))';scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';L.new(a.outputs['Attribute'],scale.inputs[0]);L.new(amount.outputs[0],scale.inputs[3]);setpos=n.new('GeometryNodeSetPosition');L.new(inp.outputs['Geometry'],setpos.inputs['Geometry']);L.new(scale.outputs['Vector'],setpos.inputs['Offset']);L.new(setpos.outputs['Geometry'],out.inputs['Geometry']);mod=o.modifiers.new('V021 one-pose painted contour offset','NODES');mod.node_group=g
S.frame_set(int(F),subframe=F-int(F));bpy.context.view_layer.update();body=next(o for o in rig.children if o.type=='MESH' and o.get('skin_region')=='body');leg=next(o for o in rig.children if o.get('v007_role')=='drawn_leg' and o.name.endswith('near'));H=rig.matrix_world@rig.pose.bones['pelvis'].head;ch=rig.matrix_world@rig.pose.bones['chest'].tail;V=points(body);inv=body.matrix_world.inverted().to_3x3();delta=[]
if len(V)!=len(body.data.vertices):raise RuntimeError('Body topology not1:1; do not apply index corrective')
for v in V:
 z=v.z-H.z;t=z/max(.01,ch.z-H.z);center=H.x+t*(ch.x-H.x);x=v.x-center;front=.5+.5*math.tanh(x/.05);back=1-front;side=math.tanh(x/.07);waist=math.exp(-((z-.15)/.085)**2);mid=math.exp(-((z-.24)/.11)**2);hem=math.exp(-((z-.015)/.075)**2);top=max(0,min(1,(.37-z)/.10));d=Vector(((-.009*side*waist-.004*mid+.008*back*hem)*top,0,(-.006*front*waist+.002*back*waist+.016*back*hem-.004*front*hem)*top))
 if d.length>.020:d*=.020/d.length
 delta.append(inv@d)
add_offset(body,delta);V=points(leg);count=len(V)//2
if len(V)!=len(leg.data.vertices) or count!=33:raise RuntimeError('Expected original33row painted leg')
C=[(V[2*i]+V[2*i+1])/2 for i in range(count)];K=rig.matrix_world@rig.pose.bones['shin_near'].head;K.y=C[16].y;new=[v.copy() for v in C]
for i in range(11,22):
 q=(i-11)/10;curve=(1-q)**2*C[11]+2*(1-q)*q*K+q*q*C[21];env=math.sin(math.pi*q)**2;new[i]=C[i].lerp(curve,env*.8)
inv=leg.matrix_world.inverted().to_3x3();delta=[Vector((0,0,0)) for _ in V]
for i in range(11,22):
 q=(i-11)/10;env=math.sin(math.pi*q)**2;T=new[min(32,i+1)]-new[max(0,i-1)];T.y=0;T.normalize();N=Vector((-T.z,0,T.x));W=(V[2*i+1]-V[2*i])/2
 if N.dot(W)<0:N=-N
 widths=[((V[2*j+1]-V[2*j])/2).length for j in range(max(0,i-2),min(33,i+3))];w=W.length*.70+sum(widths)/len(widths)*.30
 for side in [0,1]:
  sign=-1 if side==0 else 1;target=new[i]+N*(sign*w);outer=(N*sign).x>0
  if outer:target+=N*(sign*.006*env)
  d=(target-V[2*i+side])*env
  if d.length>.014:d*=.014/d.length
  delta[2*i+side]=inv@d
for i in range(22,30):
 q=(i-22)/7;env=math.sin(math.pi*q)**2;T=C[min(32,i+1)]-C[max(0,i-1)];T.y=0;T.normalize();N=Vector((-T.z,0,T.x));W=(V[2*i+1]-V[2*i])/2
 if N.dot(W)<0:N=-N
 for side in [0,1]:
  sign=-1 if side==0 else 1
  if (N*sign).x<0:delta[2*i+side]+=inv@(N*(sign*.004*env))
add_offset(leg,delta);S.frame_set(int(F),subframe=F-int(F));bpy.context.view_layer.update();variant_check=[]
for p in phases:
 f=p['study_frame_30fps'];S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();diff={o.name:max((a-b).length for a,b in zip(base_pose[p['index']][o.name],points(o))) for o in rig.children if o.type=='MESH'};variant_check.append({'phase':p['name'],'amount':ctrl['amount'],'mesh_delta_m':diff})
identity=art_identity();report={'selected_phase':chosen['name'],'source_frame':chosen['unwrapped_source_frame'],'study_frame':F,'selection_reason':'The near swing knee/calf is exposed under the rigid coat at L_PASSING; chosen as the harder visible near-leg passing silhouette.','changed_meshes':[body.name,leg.name],'native_method':'Two additive post-deformation Geometry Nodes offsets, driven by one pose amount. Original mesh vertices,UVs,weights,materials and rig remain. No new paint or topology.','body_intent':'Local waist/side compression up to9mm, modest torso countercurve4mm, rear hem lift16mm/tuck8mm, quieter front hem. No head/shoulder redesign.','knee_intent':'Round rows11..21 around the existing joint with a blended quadratic center and6mm outer cap; add4mm posterior calf fullness on rows22..29. Hip/boot collar rows and depth plane remain unchanged.','base_art_identity_retained':base_identity==identity,'poses':variant_check,'scope':'Only one passing pose is authored. Other selected poses amount0; no claim of valid intermediate blends or finished cloth.'};(P/'evidence/art_variant_definition_and_check.json').write_text(json.dumps(report,indent=2))
if base_identity!=identity:raise RuntimeError('Original art data changed unexpectedly')
S.frame_set(int(F),subframe=F-int(F));bpy.context.view_layer.update();stage=bpy.data.collections['V020 | study stage and sole controls'];close=bpy.data.objects.new('V021 | ART WHOLE POSE CLOSE',bpy.data.cameras.new('V021 art close'));stage.objects.link(close);close.parent=rig.parent;close.location=(0,-7,.79);close.rotation_euler=(math.pi/2,0,0);close.data.type='ORTHO';close.data.ortho_scale=3.0;S.render.resolution_x=960;S.render.resolution_y=540
for col in ['V020 | source skeleton render','V020 | child native skeleton render']:bpy.data.collections[col].hide_render=True
S['V021_art_variant']='One L_PASSING pose only; two additive geometry corrections, no rig/foot/motion or paint change. Artistic approval unpassed.';S.camera=close;bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Child_Passing_Whole_Pose_Art_Study_v021.blend'),compress=True)
saved=ctrl.animation_data.action;slot=ctrl.animation_data.action_slot;ctrl.animation_data.action=None
for amount,label in [(0,'BEFORE'),(1,'AFTER')]:
 ctrl['amount']=amount;ctrl.update_tag();bpy.context.view_layer.update()
 for scale,cam in [('CLOSE',close),('SHOT',bpy.data.objects['V020 | CHILD | SHOT'])]:
  S.camera=cam;S.render.filepath=str(P/f'previews/ART_VARIANT/{label}_{scale}.png');bpy.ops.render.render(write_still=True)
ctrl.animation_data.action=saved;ctrl.animation_data.action_slot=slot
print('V021_ART_VARIANT_READY',json.dumps({'phase':chosen['name'],'identity':base_identity==identity,'pose_deltas':[{'phase':r['phase'],'max_m':max(r['mesh_delta_m'].values())} for r in variant_check]}))
