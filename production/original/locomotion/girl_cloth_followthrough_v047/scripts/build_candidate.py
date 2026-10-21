"""Existing painted girl wardrobe, restrained periodic dress and braid response."""
import bpy,json,hashlib,math
import numpy as np
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];SRC=ROOT/'locomotion/painted_outfit_restoration_v046/native/WTSC_Age10_Painted_Outfit_Restoration_v046.blend';BEFORE=hashlib.sha256(SRC.read_bytes()).hexdigest();assert BEFORE=='e993540280bc60ff5fcc1dafe316f7c8457c5c8750a1110b8f6e307a865d005d';bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False)
S=bpy.data.scenes['V046 | AGE10 BONES | restored painted clothing'];bpy.context.window.scene=S;S.name='V047 | GIRL PAINT AND RESTRAINED FOLLOW THROUGH';master=bpy.data.collections['V046 | AGE10 PAIR | restored painted outfits'];master.name='V047 | AGE10 PAIR | girl cloth and braid';C=bpy.data.collections['V046 | restored original painted wardrobe'];ART=bpy.data.collections['V044 | age10 editable profile anatomy'];DETAIL=bpy.data.collections.new('V047 | girl painted collar');master.children.link(DETAIL)
RIGS={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']};girl=RIGS['GIRL'];body=bpy.data.objects['V046 GIRL | tailored knee-length dress'];head=bpy.data.objects['V044 GIRL | head'];pair=next(i for i in bpy.data.images if 'Pair_Painterly_Near_Age_v015' in i.name and i.size[0]==1672)
def ah(a):return hashlib.sha256(repr([(f.data_path,f.array_index,[(tuple(k.co),k.interpolation) for k in f.keyframe_points]) for l in a.layers for s in l.strips for b in s.channelbags for f in b.fcurves]).encode()).hexdigest()
protected={w:{'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'length':b.length} for b in r.data.bones},'action_hash':ah(r.animation_data.action)} for w,r in RIGS.items()}
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def uv(px,py):return (px/1672,1-py/941)
def graded(m,color,kind='dress'):
 ns=m.node_tree.nodes;lk=m.node_tree.links;bw=ns.new('ShaderNodeRGBToBW');lk.new(color,bw.inputs[0]);ramp=ns.new('ShaderNodeValToRGB');ramp.name='V047 | restrained original-brushwork palette';cr=ramp.color_ramp;cr.interpolation='EASE'
 if kind=='linen':stops=[(0,(.045,.038,.027)),(.035,(.14,.12,.086)),(.12,(.36,.31,.22)),(.35,(.56,.50,.38)),(1,(.68,.63,.51))]
 elif kind=='stocking':stops=[(0,(.003,.004,.006)),(.05,(.009,.012,.018)),(.20,(.023,.028,.035)),(1,(.043,.047,.052))]
 else:stops=[(0,(.004,.006,.010)),(.035,(.023,.034,.052)),(.10,(.073,.097,.128)),(.25,(.18,.21,.235)),(1,(.34,.36,.36))]
 cr.elements.remove(cr.elements[1]);cr.elements[0].position=stops[0][0];cr.elements[0].color=(*stops[0][1],1)
 for pos,c in stops[1:]:e=cr.elements.new(pos);e.color=(*c,1)
 lk.new(bw.outputs[0],ramp.inputs[0]);return ramp.outputs[0]
def paint_mat(name,uvname,kind='dress'):
 m=bpy.data.materials.new(name);m.use_nodes=True;ns=m.node_tree.nodes;ns.clear();lk=m.node_tree.links;u=ns.new('ShaderNodeUVMap');u.uv_map=uvname;tx=ns.new('ShaderNodeTexImage');tx.image=pair;tx.interpolation='Linear';lk.new(u.outputs[0],tx.inputs[0]);color=graded(m,tx.outputs['Color'],kind);em=ns.new('ShaderNodeEmission');lk.new(color,em.inputs[0]);out=ns.new('ShaderNodeOutputMaterial');lk.new(em.outputs[0],out.inputs[0]);return m
# Existing skirt/bodice painting and its feathered registration are preserved.
m=body.data.materials[0].copy();m.name='V047 GIRL | coherent original painted indigo dress';body.data.materials.clear();body.data.materials.append(m);em=next(n for n in m.node_tree.nodes if n.type=='EMISSION');old=em.inputs[0].links[0].from_socket;color=graded(m,old);m.node_tree.links.new(color,em.inputs[0])
for side in ['near','far']:
 sleeve=bpy.data.objects['V046 GIRL | painted continuous rolled sleeve '+side];layer=sleeve.data.uv_layers.new(name='V047 | actual original girl sleeve painting')
 for lp in sleeve.data.loops:
  i,j=divmod(lp.vertex_index,9);t=i/48;s=j/8;px=979-80*t;py=326+119*t;nx=-119/math.hypot(80,119);ny=-80/math.hypot(80,119);width=29-3*t;layer.data[lp.index].uv=uv(px+nx*(1-2*s)*width,py+ny*(1-2*s)*width)
 sleeve.data.materials.clear();sleeve.data.materials.append(paint_mat('V047 GIRL | original girl painted sleeve '+side,layer.name));sleeve['V047_finish']='Actual original girl sleeve painting, common dress palette; unchanged v046 actual-bone shape cache.'
 # Only the last linen cuff rows use the original cuff pigment with a warm
 # grey grade. The same geometry is continuous with the sleeve above.
 linen=paint_mat('V047 GIRL | original painted rolled linen '+side,layer.name,'linen');sleeve.data.materials.append(linen)
 for poly in sleeve.data.polygons:poly.material_index=1 if min(poly.vertices)//9>=42 else 0
 stock=bpy.data.objects['V046 GIRL | original painted stockings '+side];stock.data.materials.clear();stock.data.materials.append(paint_mat('V047 GIRL | subdued original stocking '+side,'V046 | original pigment registration','stocking'))
# Restore a modest folded collar from the original girl's collar brushwork.
verts=[];uvs=[]
for row in [0,1]:
 for j in range(17):
  u=j/16
  if not row:x=-.030+.066*u;z=1.180-.006*u;px=986+46*u;py=301+14*u
  else:x=-.065+.150*u;z=1.153-.010*u-.006*math.sin(math.pi*u);px=968+76*u;py=321+18*u
  verts.append((x,0,z));uvs.append(uv(px,py))
me=bpy.data.meshes.new('V047 | original painted girl folded collar');me.from_pydata(verts,[],[(j,j+1,17+j+1,17+j) for j in range(16)]);layer=me.uv_layers.new(name='V047 | original girl collar')
for lp in me.loops:layer.data[lp.index].uv=uvs[lp.vertex_index]
me.materials.append(paint_mat('V047 GIRL | original collar linen',layer.name,'linen'));collar=bpy.data.objects.new(me.name,me);DETAIL.objects.link(collar);collar.parent=girl;collar.location.y=-.060;vg=collar.vertex_groups.new(name='chest');vg.add(list(range(len(verts))),1,'REPLACE');mod=collar.modifiers.new('Unchanged age-ten chest bone','ARMATURE');mod.object=girl
# Periodic spring response to ACTUAL rig-anchor horizontal acceleration.
# The shared root is linear, so it contributes no acceleration. We use rig-local
# coordinates to avoid a discontinuity when wrapping the 31-frame cycle.
N=248;DT=1/240;root_px=(946,246);scale=.193/143
def pp(px,py):return Vector(((px-1008)*scale,0,1.405-(py-137)*scale))
nodes=[pp(*v) for v in [(946,246),(922,280),(907,315),(892,349),(890,375)]];anchor=nodes[0];xhead=[];xhip=[];pitch=[]
for i in range(N):
 f=1+i/8;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();ev=girl.evaluated_get(bpy.context.evaluated_depsgraph_get());h=ev.pose.bones['head'];p=h.matrix@girl.data.bones['head'].matrix_local.inverted()@anchor;xhead.append(p.x);xhip.append(ev.pose.bones['pelvis'].head.x);d=(h.tail-h.head).normalized();pitch.append(math.atan2(d.x,d.z))
omega=2*math.pi*np.fft.rfftfreq(N,DT);low=(np.arange(len(omega))<=6);XH=np.fft.rfft(xhead);XP=np.fft.rfft(np.unwrap(pitch));XHIP=np.fft.rfft(xhip)
def response(X,L,zeta,extra=None):
 w0=math.sqrt(9.81/L);force=-omega**2*X/L
 if extra is not None:force+=omega**2*extra
 transfer=force/(w0*w0-omega**2+2j*zeta*w0*omega);transfer*=low;transfer[0]=0;return np.fft.irfft(transfer,n=N)
braid=response(XH,.16,.72,XP);dress=response(XHIP,.42,.80)
braid_gain=min(1,math.radians(4)/max(1e-8,float(np.max(abs(braid)))));braid*=braid_gain
dress_gain=min(1,math.radians(1.5)/max(1e-8,float(np.max(abs(dress)))));dress*=dress_gain
def sample(values,f,delay=0):q=((f-1-delay)*8)%N;k=int(q);return float(values[k]*(1-(q-k))+values[(k+1)%N]*(q-k))
def ry(v,a):c=math.cos(a);s=math.sin(a);return Vector((c*v.x+s*v.z,v.y,-s*v.x+c*v.z))
def chain(f,gain=1):
 out=[nodes[0].copy()]
 for j in range(4):a=sample(braid,f,j*.25)*(.25+.25*j)*gain;out.append(out[-1]+ry(nodes[j+1]-nodes[j],a))
 return out
raw_tip=max((chain(1+i/8)[-1]-nodes[-1]).length for i in range(N));tip_gain=min(1,.010/max(raw_tip,1e-8))
base_head=[v.co.copy() for v in head.data.vertices];head_uv={lp.vertex_index:head.data.uv_layers[0].data[lp.index].uv.copy() for lp in head.data.loops};base_body=[v.co.copy() for v in body.data.vertices];braid_vertices={};face_indices=[]
for i,p in enumerate(base_head):
 u=head_uv[i];px=u.x*1672;py=(1-u.y)*941;weight=smooth((py-240)/30)*(1-smooth((px-958)/28))
 if weight<1e-8:face_indices.append(i);continue
 options=[]
 for j in range(4):
  d=nodes[j+1]-nodes[j];t=max(0,min(1,(p-nodes[j]).dot(d)/d.length_squared));near=nodes[j]+d*t;options.append(((p-near).length_squared,j,t,p-near))
 _,j,t,res=min(options,key=lambda q:q[0]);braid_vertices[i]=(weight,j,t,res)
def head_pose(f):
 changed=chain(f,tip_gain);out=[p.copy() for p in base_head]
 for i,(w,j,t,res) in braid_vertices.items():
  angle=sample(braid,f,j*.25)*(.25+.25*j)*tip_gain;q=changed[j].lerp(changed[j+1],t)+ry(res,angle);q.y=base_head[i].y;out[i]=base_head[i].lerp(q,w)
 return out
def body_pose(f):
 theta=sample(dress,f);pivot=Vector((.008,0,.873));out=[]
 for p in base_body:
  w=smooth((.873-p.z)/.34);q=pivot+ry(p-pivot,theta*w);q.y=p.y;out.append(q)
 return out
def cache(o,func,label):
 assert not o.data.shape_keys,o.name;poses={1+i/4:func(1+i/4) for i in range(125)};o.data.vertices.foreach_set('co',[c for p in poses[1.] for c in p]);o.shape_key_add(name='Basis | '+label+' F1')
 for i in range(1,124):
  f=1+i/4;k=o.shape_key_add(name='V047 '+label+' F%05.2f'%f);k.data.foreach_set('co',[c for p in poses[f] for c in p])
  for at in [1.,max(1.,f-.25),f,min(32.,f+.25),32.]:k.value=float(at==f);k.keyframe_insert('value',frame=at)
 action=o.data.shape_keys.animation_data.action;action.name='V047 | '+label+' | actual-anchor periodic response'
 for l in action.layers:
  for s in l.strips:
   for b in s.channelbags:
    for fc in b.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR'
     cy=fc.modifiers.new('CYCLES');cy.mode_before=cy.mode_after='REPEAT'
 return poses
heads=cache(head,head_pose,'braid lag');bodies=cache(body,body_pose,'dress hem lag');head['V047_scope']='Only existing braid pixels/vertices below the nape bend; face, skull and main hair geometry remain exactly unchanged in local space. No head turnaround.';body['V047_scope']='Original painted dress, unchanged bodice above waist; hem responds to actual hip acceleration with <=1.5 degree restrained lag.'
face_error=max((poses[i]-base_head[i]).length for poses in heads.values() for i in face_indices);assert face_error==0
head_disp=max((p-base_head[i]).length for poses in heads.values() for i,p in enumerate(poses));body_disp=max((p-base_body[i]).length for poses in bodies.values() for i,p in enumerate(poses));assert head_disp<.015 and body_disp<.015,(head_disp,body_disp)
for who,r in RIGS.items():
 assert ah(r.animation_data.action)==protected[who]['action_hash']
 for b in r.data.bones:assert list(b.head_local)==protected[who]['bones'][b.name]['head'] and list(b.tail_local)==protected[who]['bones'][b.name]['tail']
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==BEFORE
S['V047_scope']='Girl original-painted outfit finish and restrained dress/braid follow-through. v046 bones, contacts, root and boy appearance preserved. Girl face remains original charcoal; no head turnaround, finger acting, clasp or recovery transition.';S.frame_set(1);bpy.context.view_layer.update();out=P/'native/WTSC_Girl_Painted_Cloth_FollowThrough_v047.blend'
report={'source':str(SRC),'source_sha256':BEFORE,'source_unchanged':True,'protected_rigs':protected,'bones_and_rig_actions_preserved':True,'new_raster_paint':False,'outfit_changes':'Original girl sleeve and collar painting, common subdued indigo cloth grade, warm-grey rolled linen, subdued stocking cuffs. Original dress painting and v046 soft bodice registration preserved.','secondary_model':'Periodic damped spring transfer from actual nape/hip horizontal acceleration, six-harmonic low-pass; local head angular inertia included for braid. Geometry chain preserves rest segment lengths. No cloth simulator or random wind.','spring_parameters':{'braid_effective_length_m':.16,'braid_damping_ratio':.72,'dress_effective_length_m':.42,'dress_damping_ratio':.80,'braid_angle_cap_degrees':4,'dress_angle_cap_degrees':1.5,'braid_response_gain':braid_gain,'braid_tip_limit_gain':tip_gain,'dress_response_gain':dress_gain},'max_braid_vertex_displacement_m':head_disp,'max_dress_vertex_displacement_m':body_disp,'max_non_braid_head_vertex_displacement_m':face_error,'non_braid_head_vertex_count':len(face_indices),'braid_weighted_vertex_count':len(braid_vertices),'original_head_and_body_vertices':{'head':[list(p) for p in base_head],'body':[list(p) for p in base_body]},'signals':[{'frame':1+i/8,'braid_angle_rad':float(braid[i])*tip_gain,'dress_angle_rad':float(dress[i])} for i in range(N)],'limitations':S['V047_scope']}
(P/'evidence/FOLLOWTHROUGH_BUILD.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);print('V047_NATIVE_SAVED',json.dumps({'head_mm':head_disp*1000,'hem_mm':body_disp*1000,'face_error_m':face_error}),flush=True)
