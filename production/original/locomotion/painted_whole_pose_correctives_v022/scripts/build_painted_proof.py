"""Bounded v022: two whole painted poses, with editable replacement trouser drawings.
Native v021 support, skeleton, boots, arms, head and travel remain unchanged.
"""
import bpy,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api
BASE=P/'reference/BASE_COHERENT_SUPPORT_v021_COPY.blend'
bpy.ops.wm.open_mainfile(filepath=str(BASE),load_ui=False,use_scripts=False)
S=bpy.context.scene;rigs,controls=api.initialize_from_scene();rig=rigs['BOY'];travel=rig.parent;sol=json.loads((P/'reference/coherent_pose_solution_v021.json').read_text());chosen=[sol['poses'][5],sol['poses'][6]]
pack=bpy.data.collections['WTSC_CHILD_SUPPORT_POSES_v021'];pack.name='WTSC_PAINTED_WHOLE_POSE_CORRECTIVES_v022'
artcol=bpy.data.collections.new('V022 | editable pose replacement drawings');pack.children.link(artcol)
ctrl=bpy.data.objects.new('V022 | WHOLE POSE ART | two selected poses',None);artcol.objects.link(ctrl)
for prop in ['loading','passing']:
 ctrl[prop]=0.;ctrl.id_properties_ui(prop).update(min=0,max=1,description='One selected painted pose only; no accepted intermediate blend')
for p in sol['poses']+[dict(sol['poses'][0],study_frame_30fps=32)]:
 for prop,name in [('loading','L_LOADING'),('passing','L_PASSING')]:
  ctrl[prop]=float(p['name']==name);ctrl.keyframe_insert('["'+prop+'"]',frame=p['study_frame_30fps'])
for l in ctrl.animation_data.action.layers:
 for st in l.strips:
  for bag in st.channelbags:
   for fc in bag.fcurves:
    for k in fc.keyframe_points:k.interpolation='CONSTANT'
def scalar_driver(socket,prop):
 fc=socket.driver_add('default_value');v=fc.driver.variables.new();v.name='amount';v.targets[0].id=ctrl;v.targets[0].data_path='["'+prop+'"]';fc.driver.expression='max(0,min(1,amount))'
def visible_on(o,prop,inverse=False):
 for path in ['hide_render','hide_viewport']:
  fc=o.driver_add(path)
  for n in ['loading','passing']:
   v=fc.driver.variables.new();v.name=n;v.targets[0].id=ctrl;v.targets[0].data_path='["'+n+'"]'
  expression=prop if prop in ['loading','passing'] else 'loading+passing'
  fc.driver.expression=('('+expression+')>0.5') if inverse else ('('+expression+')<0.5')
def points(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [e.matrix_world@v.co for v in e.data.vertices]
def frame(f):S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
def eulerstep(x):x=max(0,min(1,x));return x*x*(3-2*x)
body=next(o for o in rig.children if o.type=='MESH' and o.get('skin_region')=='body')
legs={side:bpy.data.objects['V007_BOY | drawn leg '+side] for side in ['near','far']}
original_meshes=[o for o in rig.children if o.type=='MESH'];base_pose={}
for p in sol['poses']:
 frame(p['study_frame_30fps']);base_pose[p['name']]={o.name:points(o) for o in original_meshes}
def offset_modifier(o,prop,delta):
 attr=o.data.attributes.new('V022_'+prop+'_delta','FLOAT_VECTOR','POINT');attr.data.foreach_set('vector',[x for v in delta for x in v])
 g=bpy.data.node_groups.new('V022 whole painted pose | '+prop,'GeometryNodeTree');g.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');g.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
 n=g.nodes;L=g.links;inp=n.new('NodeGroupInput');out=n.new('NodeGroupOutput');a=n.new('GeometryNodeInputNamedAttribute');a.data_type='FLOAT_VECTOR';a.inputs['Name'].default_value=attr.name;amount=n.new('ShaderNodeValue');scalar_driver(amount.outputs[0],prop);scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';L.new(a.outputs['Attribute'],scale.inputs[0]);L.new(amount.outputs[0],scale.inputs[3]);pos=n.new('GeometryNodeSetPosition');L.new(inp.outputs['Geometry'],pos.inputs['Geometry']);L.new(scale.outputs['Vector'],pos.inputs['Offset']);L.new(pos.outputs['Geometry'],out.inputs['Geometry']);mod=o.modifiers.new('V022 '+prop+' coat compression and hem','NODES');mod.node_group=g
def cloth_delta(v,H,ch,prop):
 z=v.z-H.z;t=z/max(.01,ch.z-H.z);cx=H.x+t*(ch.x-H.x);x=v.x-cx;front=.5+.5*math.tanh(x/.045);back=1-front;waist=math.exp(-((z-.17)/.12)**2);low=math.exp(-((z-.035)/.115)**2);fix=eulerstep((.385-z)/.14)
 if prop=='passing':
  dx=(.012*waist-.018*math.tanh(x/.055)*waist-.028*front*low-.014*back*low)*fix
  dz=(-.011*front*waist+.027*back*low+.012*front*low)*fix
 else:
  dx=(.010*waist-.018*front*waist-.024*front*low-.011*back*low)*fix
  dz=(-.015*waist-.009*back*low+.008*front*low)*fix
 return Vector((dx,0,dz))
def interp(a,knots):
 for (x,v),(y,w) in zip(knots,knots[1:]):
  if a<=y:return v+(w-v)*(a-x)/(y-x)
 return knots[-1][1]
def hermite(A,B,mA,mB,t):
 return (2*t**3-3*t*t+1)*A+(t**3-2*t*t+t)*mA+(-2*t**3+3*t*t)*B+(t**3-t*t)*mB
def center_curve(H,K,E,t,tk):
 u=(K-H).normalized();v=(E-K).normalized();mid=(u+v).normalized();L1=(K-H).length;L2=(E-K).length
 if t<=tk:return hermite(H,K,u*L1,mid*L1,t/tk)
 return hermite(K,E,mid*L2,v*L2,(t-tk)/(1-tk))
def material_edges(original,name):
 m=original.copy();m.name=name;n=m.node_tree.nodes;L=m.node_tree.links;mix=next(x for x in n if x.type=='MIX_SHADER');tex=next(x for x in n if x.type=='TEX_IMAGE');a=n.new('ShaderNodeVertexColor');a.layer_name='V022_EdgeAlpha';mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';L.new(a.outputs['Alpha'],mul.inputs[0]);L.new(tex.outputs['Alpha'],mul.inputs[1])
 for l in list(mix.inputs[0].links):L.remove(l)
 L.new(mul.outputs[0],mix.inputs[0]);return m
pantsmat=material_edges(legs['near'].data.materials[0],'V022 | original trouser pigments | relocated rolled cuff')
def make_mesh(name,verts,faces,uvs,alphas,mat,prop):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);artcol.objects.link(o);o.parent=travel;o.data.materials.append(mat);uv=me.uv_layers.new(name='Original_v015_paint_UV')
 for l in me.loops:uv.data[l.index].uv=uvs[l.vertex_index]
 ca=me.color_attributes.new(name='V022_EdgeAlpha',type='FLOAT_COLOR',domain='POINT')
 for i,a in enumerate(alphas):ca.data[i].color=(1,1,1,a)
 o['V022_pose']=prop;o['V022_asset_role']='Pose-specific replacement drawing; original source pigments; editable mesh and UVs';visible_on(o,prop);return o
inkmat=material_edges(legs['near'].data.materials[0],'V022 | original coat pigment | compression crease')
washmat=material_edges(legs['near'].data.materials[0],'V022 | original coat pigment | fold edge')
for mat,gain in [(inkmat,.38),(washmat,1.45)]:
 for n in mat.node_tree.nodes:
  if n.type=='HUE_SAT':n.inputs['Value'].default_value*=gain
def coat_fold(H,ch,prop,D,light=False):
 z=.105 if prop=='loading' else .165
 A=H+Vector((-.070,-.002,z+.037));B=H+Vector((-.006,-.002,z-.024));C=H+Vector((.064,-.002,z+.004))
 if light:
  for v in [A,B,C]:v.z+=.003
 verts=[];uvs=[];alpha=[];faces=[];cols=[0,.13,.5,.87,1];rows=31
 for i in range(rows):
  t=i/(rows-1);center=(1-t)**2*A+2*(1-t)*t*B+t*t*C;T=(2*(1-t)*(B-A)+2*t*(C-B)).normalized();N=Vector((-T.z,0,T.x));width=(.0018 if light else .0023)*math.sin(math.pi*t)**.65
  for j,q in enumerate(cols):
   v=center+N*(width*(q*2-1));v+=cloth_delta(v,H,ch,prop);v.x-=D;verts.append(v);uvs.append(((595+65*t)/1672,1-(420+6*math.sin(t*math.pi)+q*3)/941));alpha.append(0 if j in [0,4] else .78)
 for i in range(rows-1):
  for j in range(4):a=i*5+j;faces.append((a,a+1,a+6,a+5))
 return make_mesh('V022 | '+prop+' | '+('wash fold edge' if light else 'waist compression ink crease'),verts,faces,uvs,alpha,washmat if light else inkmat,prop)
definitions=[]
for p in chosen:
 prop='loading' if p['name']=='L_LOADING' else 'passing';frame(p['study_frame_30fps']);H=rig.matrix_world@rig.pose.bones['pelvis'].head;ch=rig.matrix_world@rig.pose.bones['chest'].tail;V=points(body);inv=body.matrix_world.inverted().to_3x3();delta=[inv@cloth_delta(v,H,ch,prop) for v in V];offset_modifier(body,prop,delta)
 row={'phase':p['name'],'study_frame':p['study_frame_30fps'],'coat_max_offset_m':max(d.length for d in delta),'trousers':[]}
 for side,old in legs.items():
  V=points(old);C=[(V[2*i]+V[2*i+1])/2 for i in range(33)];h=C[0]+Vector((0,0,.060));k=rig.matrix_world@rig.pose.bones['shin_'+side].head;k.y=h.y;e=C[32];tk=(k-h).length/((k-h).length+(e-k).length)
  uv_by_v={l.vertex_index:old.data.uv_layers.active.data[l.index].uv.copy() for l in old.data.loops}
  widths=[((V[2*i+1]-V[2*i])/2).length for i in range(33)]
  verts=[];uvs=[];alphas=[];faces=[];Nrows=97;cols=[0,.035,.27,.5,.73,.965,1]
  for i in range(Nrows):
   t=i/(Nrows-1);c=center_curve(h,k,e,t,tk);tangent=(center_curve(h,k,e,min(1,t+.002),tk)-center_curve(h,k,e,max(0,t-.002),tk)).normalized();n=Vector((-tangent.z,0,tangent.x))
   # Main fabric now reaches the hem; source cuff rows24–27 are placed there.
   src=interp(t,[(0,0),(tk,.50),(.790,23.0/32),(.825,24.0/32),(.910,27.0/32),(1,1)])
   j=min(31,int(src*32));q=src*32-j;u0=uv_by_v[2*j].lerp(uv_by_v[2*(j+1)],q);u1=uv_by_v[2*j+1].lerp(uv_by_v[2*(j+1)+1],q)
   hipw=widths[0];cw=widths[-1]
   w=interp(t,[(0,hipw),(.22,hipw*.91),(max(.23,tk-.10),.047),(tk,.044),(.73,.045),(.790,.042),(.825,.0465),(.900,.0465),(.927,.0315),(1,cw)])
   # Rounded kneecap and a soft inner compression pocket instead of a joint hinge.
   bend=(k-h).normalized().angle((e-k).normalized());knee=math.exp(-((t-tk)/.095)**2);outer_sign=1 if ((k-h).cross(e-k)).y>=0 else -1
   for jcol,s in enumerate(cols):
    xx=2*s-1;out=c+n*(xx*w)
    out+=n*(outer_sign*.0055*knee*(max(0,xx*outer_sign))**2*min(1,bend/.8))
    # A small irregular rolled edge; no change at the boot collar endpoint.
    roll=math.exp(-((t-.865)/.038)**2);out+=tangent*(roll*(.003*(s-.5)+.007*(1-xx*xx)))
    out-=Vector((p['root_travel_m'],0,0));verts.append(out);uvs.append(u0.lerp(u1,s*.98+.01));alphas.append(0 if jcol in [0,len(cols)-1] else 1)
  W=len(cols)
  for i in range(Nrows-1):
   for j in range(W-1):a=i*W+j;faces.append((a,a+1,a+W+1,a+W))
  ob=make_mesh('V022 | '+p['name']+' | '+side+' painted trouser replacement',verts,faces,uvs,alphas,pantsmat,prop)
  row['trousers'].append({'side':side,'knee_parameter':tk,'source_cuff_rows':[24,27],'new_cuff_parameter':[.825,.910],'vertices':len(verts),'original_boot_collar_center_world':list(e),'design_retention':'Rolled cuff flare and visible ankle retained; cuff surface bows across its width instead of a flat band.'})
 for light in [False,True]:coat_fold(H,ch,prop,p['root_travel_m'],light)
 row['waist_overlap_extension_m']=.060;row['cloth_drawing']='Two tapered original-pigment crease ribbons, one ink and one wash edge, following the coat compression.';definitions.append(row)
for old in legs.values():visible_on(old,'sum',inverse=True)
# Keep the original profile, hands and support artwork. No head turn or wrist changes.
S['V022_scope']='Two whole painted poses only: L_LOADING and L_PASSING. Coat deformation plus editable pose-specific trouser drawings using original v015 pigments. Support animation untouched.'
S['V022_artist_acceptance']='UNREVIEWED_NATIVE_TEST';S['V022_continuous_cycle']='NOT_AUTHORED'
# Native camera at a close but whole-body comparison scale, plus original v046 lens.
stage=bpy.data.collections['V020 | study stage and sole controls'];cam=bpy.data.objects.new('V022 | whole painted pose close',bpy.data.cameras.new('V022 close'));stage.objects.link(cam);cam.parent=travel;cam.location=(0,-7,.79);cam.rotation_euler=(math.pi/2,0,0);cam.data.type='ORTHO';cam.data.ortho_scale=2.9
S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100
for col in ['V020 | source skeleton render','V020 | child native skeleton render']:bpy.data.collections[col].hide_render=True
frame(chosen[-1]['study_frame_30fps']);S.camera=cam
out=P/'native/WTSC_Painted_Whole_Pose_Correctives_v022.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(P/'evidence/corrective_definitions.json').write_text(json.dumps({'method':'Original-coat additive native geometry fields; four static pose-specific curved-trouser mesh drawings using the original image/UV pigments and relocated original rolled cuffs. No new raster generation.','poses':definitions,'baseline_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'blender':bpy.app.version_string},indent=2))
saved=ctrl.animation_data.action;slot=ctrl.animation_data.action_slot;ctrl.animation_data.action=None
for p in chosen:
 frame(p['study_frame_30fps']);prop='loading' if p['name']=='L_LOADING' else 'passing'
 for label,amount in [('BEFORE',0),('AFTER',1)]:
  ctrl['loading']=float(amount if prop=='loading' else 0);ctrl['passing']=float(amount if prop=='passing' else 0);ctrl.update_tag();bpy.context.view_layer.update()
  for scale,camera in [('CLOSE',cam),('SHOT',bpy.data.objects['V020 | CHILD | SHOT'])]:
   S.camera=camera;D=P/'previews'/p['name'];D.mkdir(exist_ok=True);S.render.filepath=str(D/(label+'_'+scale+'.png'));bpy.ops.render.render(write_still=True)
ctrl.animation_data.action=saved;ctrl.animation_data.action_slot=slot
print('V022_FIRST_PAINTED_PROOF_READY')

