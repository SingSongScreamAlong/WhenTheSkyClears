"""Restore existing rich painting onto actual age-ten bones. Sources stay read-only."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
import numpy as np
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
for n in ['native','previews','evidence']:(P/n).mkdir(exist_ok=True)
SRC=ROOT/'locomotion/age10_animation_retarget_v045/native/WTSC_Age10_Walk_Retarget_Proof_v045.blend';SRC_HASH=hashlib.sha256(SRC.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);S=bpy.data.scenes['V045 | AGE TEN | RETARGET AFTER STATIC SCALE'];bpy.context.window.scene=S;S.name='V046 | AGE10 BONES | restored painted clothing';RIGS={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']};ART=bpy.data.collections['V044 | age10 editable profile anatomy'];master=bpy.data.collections['V045 | AGE TEN WALKING PAIR | retarget proof'];master.name='V046 | AGE10 PAIR | restored painted outfits';C=bpy.data.collections.new('V046 | restored original painted wardrobe');master.children.link(C)
def actionhash(a):
 return hashlib.sha256(repr([(fc.data_path,fc.array_index,[(tuple(k.co),k.interpolation) for k in fc.keyframe_points]) for l in a.layers for st in l.strips for bag in st.channelbags for fc in bag.fcurves]).encode()).hexdigest()
protected={w:{'bones':{b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'length':b.length} for b in r.data.bones},'action_hash':actionhash(r.animation_data.action)} for w,r in RIGS.items()}
atlas=next(i for i in bpy.data.images if 'Parts_Atlas_v040' in i.name and i.size[0]==1254);pair=next(i for i in bpy.data.images if 'Pair_Painterly_Near_Age_v015' in i.name and i.size[0]==1672)
def pixels(im):
 W,H=im.size;raw=np.empty(W*H*4,dtype=np.float32);im.pixels.foreach_get(raw);return raw.reshape(H,W,4)[::-1]
ALPHA={atlas.name:pixels(atlas)[:,:,3],pair.name:pixels(pair)[:,:,3]}
def run(im,py,lo,hi,goal):
 a=ALPHA[im.name];row=a[max(0,min(a.shape[0]-1,int(round(py))))];good=np.flatnonzero(row[lo:hi]>.75)+lo
 if not len(good):return lo+2,hi-2
 k=int(good[np.argmin(abs(good-goal))]);l=k;h=k
 while l>lo and row[l-1]>.75:l-=1
 while h<hi-1 and row[h+1]>.75:h+=1
 return l+.6,h-.6
UVNAME='V046 | original pigment registration'
def material(name,im,charcoal=False,skin=False,opaque=False):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.surface_render_method='BLENDED';ns=m.node_tree.nodes;ns.clear();lk=m.node_tree.links;uv=ns.new('ShaderNodeUVMap');uv.uv_map=UVNAME;tx=ns.new('ShaderNodeTexImage');tx.image=im;tx.interpolation='Linear';lk.new(uv.outputs[0],tx.inputs['Vector']);color=tx.outputs['Color']
 if charcoal:
  bw=ns.new('ShaderNodeRGBToBW');lk.new(color,bw.inputs[0]);mul=ns.new('ShaderNodeMath');mul.operation='MULTIPLY_ADD';mul.inputs[1].default_value=.035 if skin else .12;mul.inputs[2].default_value=.002 if skin else .001;lk.new(bw.outputs[0],mul.inputs[0]);color=mul.outputs[0]
 em=ns.new('ShaderNodeEmission');lk.new(color,em.inputs[0]);out=ns.new('ShaderNodeOutputMaterial')
 if opaque:lk.new(em.outputs[0],out.inputs[0])
 else:
  tr=ns.new('ShaderNodeBsdfTransparent');mix=ns.new('ShaderNodeMixShader');lk.new(tx.outputs['Alpha'],mix.inputs[0]);lk.new(tr.outputs[0],mix.inputs[1]);lk.new(em.outputs[0],mix.inputs[2]);lk.new(mix.outputs[0],out.inputs[0])
 return m
M={}
for who in RIGS:
 for kind in ['coat','sleeve','skin','hand','pants']:
  M[who,kind]=material('V046 '+who+' | original atlas '+kind,atlas,charcoal=who=='GIRL',skin=kind in ['skin','hand'])
 M[who,'dress']=material('V046 '+who+' | retained original dress painting',pair,opaque=True)
 M[who,'stocking']=material('V046 '+who+' | retained original stocking painting',pair,opaque=True)
for o in list(ART.objects):
 if o.type=='MESH' and o.get('proportion_role') in ['coat','dress','leg','upper','cuff','forearm','hand','boot shaft overlap','wrist paint overlap']:o.hide_render=True;o.hide_viewport=True;o['V046_status']='Preserved earlier study geometry; superseded by original-paint wardrobe fitted to actual bones.'
def objmesh(name,V,F,UV,mat,r):
 me=bpy.data.meshes.new(name);me.from_pydata(V,[],F);me.update();uv=me.uv_layers.new(name=UVNAME)
 for lp in me.loops:uv.data[lp.index].uv=UV[lp.vertex_index]
 me.materials.append(mat);o=bpy.data.objects.new(name,me);C.objects.link(o);o.parent=r;return o
def grid(rows,cols,fn):
 V=[];UV=[]
 for i in range(rows):
  for j in range(cols):p,uv=fn(i/(rows-1),j/(cols-1));V.append(p);UV.append(uv)
 F=[(i*cols+j,i*cols+j+1,(i+1)*cols+j+1,(i+1)*cols+j) for i in range(rows-1) for j in range(cols-1)];return V,F,UV
def uv(im,px,py):return (px/im.size[0],1-py/im.size[1])
def interp(t,keys):
 if t<=keys[0][0]:return float(keys[0][1])
 if t>=keys[-1][0]:return float(keys[-1][1])
 i=next(i for i in range(len(keys)-1) if keys[i][0]<=t<=keys[i+1][0]);x0,y0=keys[i];x1,y1=keys[i+1];dt=x1-x0;u=(t-x0)/dt
 m0=(y1-y0)/dt if i==0 else (keys[i+1][1]-keys[i-1][1])/(keys[i+1][0]-keys[i-1][0]);m1=(y1-y0)/dt if i==len(keys)-2 else (keys[i+2][1]-keys[i][1])/(keys[i+2][0]-keys[i][0]);return float(y0*(2*u**3-3*u*u+1)+m0*dt*(u**3-2*u*u+u)+y1*(-2*u**3+3*u*u)+m1*dt*(u**3-u*u))
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
BODY={}
def restore_bodice_pigment(o,who):
 # Blend two registrations of the SAME original painting. A point attribute
 # gives a soft textile transition instead of a rectangular UV discontinuity.
 # No source pixels are generated, retouched, or repainted.
 me=o.data;quiet=me.uv_layers.new(name='V046 | quiet upper cloth');weight=me.attributes.new('V046 upper textile blend','FLOAT','POINT');im=atlas if who=='BOY' else pair
 for lp in me.loops:
  i,j=divmod(lp.vertex_index,17);t=i/64;s=j/16
  quiet.data[lp.index].uv=uv(im,705+25*s,185+70*min(1,t/.36)) if who=='BOY' else uv(im,1004+38*s,465+75*min(1,t/.47))
 main_uv={lp.vertex_index:me.uv_layers[UVNAME].data[lp.index].uv.copy() for lp in me.loops}
 for i in range(65):
  t=i/64;w=1-smooth((t-(.12 if who=='BOY' else .22))/(.24 if who=='BOY' else .25))
  for j in range(17):
   value=w
   if who=='BOY':
    u=main_uv[i*17+j];px=u.x*im.size[0];py=(1-u.y)*im.size[1];rho=math.hypot((px-623)/66,(py-172)/90)
    # The atlas includes a painted empty armhole for a detached sleeve. Its
    # dark cavity must not stay on the back when the attached sleeve swings.
    value=max(value,1-smooth((rho-.78)/.42))
   weight.data[i*17+j].value=value
 m=bpy.data.materials.new('V046 '+who+' | seamless original painted bodice');m.use_nodes=True;ns=m.node_tree.nodes;ns.clear();lk=m.node_tree.links
 tx=[]
 for uvname in [UVNAME,quiet.name]:
  u=ns.new('ShaderNodeUVMap');u.uv_map=uvname;q=ns.new('ShaderNodeTexImage');q.image=im;q.interpolation='Linear';lk.new(u.outputs[0],q.inputs[0]);tx.append(q)
 a=ns.new('ShaderNodeAttribute');a.attribute_name=weight.name;mix=ns.new('ShaderNodeMixRGB');mix.blend_type='MIX';lk.new(a.outputs['Fac'],mix.inputs[0]);lk.new(tx[0].outputs['Color'],mix.inputs[1]);lk.new(tx[1].outputs['Color'],mix.inputs[2]);em=ns.new('ShaderNodeEmission');lk.new(mix.outputs[0],em.inputs[0]);out=ns.new('ShaderNodeOutputMaterial');lk.new(em.outputs[0],out.inputs[0]);me.materials.clear();me.materials.append(m);o['pigment_registration']='Original body painting with a feathered upper textile registration; no hard rectangular patch boundary. Opaque native silhouette owns the garment edge.'
for who,r in RIGS.items():
 def body(t,s):
  if who=='BOY':
   bk=interp(t,[(0,-.033),(.12,-.085),(.28,-.106),(.55,-.086),(.8,-.113),(1,-.127)]);fr=interp(t,[(0,.050),(.12,.100),(.28,.127),(.55,.108),(.8,.125),(1,.112)]);z=interp(t,[(0,1.178),(.12,1.145),(.28,1.065),(.55,.920),(.8,.780),(1,.691)])
   if t<.12:
    collar=next(o for o in ART.objects if o.parent==r and o.get('proportion_role')=='collar');bottom=[p.co for p in collar.data.vertices][22:33];u=s*10;k=min(9,int(u));p=bottom[k].lerp(bottom[k+1],u-k);q=smooth(t/.12);x=p.x*(1-q)+(bk+(fr-bk)*s)*q;z=p.z*(1-q)+z*q
   else:x=bk+(fr-bk)*s
   py=20+555*t;lo,hi=run(atlas,py,520,840,740)
   pu=lo+(hi-lo)*s;pv=py
   pigment=uv(atlas,pu,pv)
  else:
   bk=interp(t,[(0,-.030),(.12,-.077),(.27,-.093),(.50,-.071),(.72,-.12),(1,-.195)]);fr=interp(t,[(0,.035),(.12,.096),(.27,.120),(.5,.092),(.72,.14),(1,.205)]);x=bk+(fr-bk)*s;z=interp(t,[(0,1.175),(.12,1.137),(.27,1.047),(.5,.873),(.72,.680),(1,.440)]);z+=(.008-.015*s)*(1-smooth(t/.15));py=300+414*t;lo,hi=run(pair,py,835,1160,1020)
   if py<460:lo=max(lo,interp(py,[(300,982),(345,990),(460,982)]));hi=min(hi,interp(py,[(300,1044),(345,1070),(460,1070)]))
   pigment=uv(pair,lo+(hi-lo)*s,py)
  return (x,-.019-.003*math.sin(math.pi*s),z),pigment
 V,F,UV=grid(65,17,body);o=objmesh('V046 '+who+' | tailored '+('coat' if who=='BOY' else 'knee-length dress'),V,F,UV,M[who,'coat' if who=='BOY' else 'dress'],r);o['wardrobe_role']='body';BODY[who]=o
 restore_bodice_pigment(o,who)
 for n in ['pelvis','chest']:o.vertex_groups.new(name=n)
 for i,p in enumerate(V):w=smooth((p[2]-(r.data.bones['pelvis'].head_local.z+.02))/.17);o.vertex_groups['chest'].add([i],w,'REPLACE');o.vertex_groups['pelvis'].add([i],1-w,'REPLACE')
 mod=o.modifiers.new('Actual age10 torso and pelvis','ARMATURE');mod.object=r
 # Forearms taper to the painted wrist; hands use the existing fully painted
 # atlas hand silhouette, rather than enlarged generic finger polygons.
 for side in ['near','far']:
  elbow=r.data.bones['forearm_'+side].head_local.z;wrist=r.data.bones['hand_'+side].head_local.z;depth=-.045 if side=='near' else .035
  def skin(t,s):
   z=elbow+.012-t*(elbow-wrist+.022);rad=.0275*(1-t)+.0215*t;py=650+300*t;lo,hi=run(atlas,py,140,330,220);return ((s*2-1)*rad,depth,z),uv(atlas,lo+(hi-lo)*s,py)
  V,F,UV=grid(33,9,skin);o=objmesh('V046 '+who+' | painted forearm '+side,V,F,UV,M[who,'skin'],r);vg=o.vertex_groups.new(name='forearm_'+side);vg.add(list(range(len(V))),1,'REPLACE');mod=o.modifiers.new('Actual forearm bone','ARMATURE');mod.object=r;o['wardrobe_role']='skin'
  ar=ALPHA[atlas.name];yy,xx=np.nonzero(ar[950:1205,145:335]>.8);tip=950+int(yy.max())+1;wristpy=950.;hs=(.145 if who=='BOY' else .144)/(tip-wristpy)
  def hand(t,s):px=150+180*s;py=940+(tip-940)*t;return ((px-220)*hs,depth-.002,wrist-(py-wristpy)*hs),uv(atlas,px,py)
  V,F,UV=grid(49,17,hand);o=objmesh('V046 '+who+' | original painted hand '+side,V,F,UV,M[who,'hand'],r);vg=o.vertex_groups.new(name='hand_'+side);vg.add(list(range(len(V))),1,'REPLACE');mod=o.modifiers.new('Actual hand control','ARMATURE');mod.object=r;o['wardrobe_role']='hand';o['wrist_crease_source_row_estimate']=wristpy;o['actual_painted_fingertip_source_row']=tip;o['painted_vertical_hand_span_m']=.145 if who=='BOY' else .144
print('V046_STATIC_WARDROBE_READY',flush=True)
# Capture actual evaluated bone poses before adding drawing-cache Actions.
CACHE={w:{} for w in RIGS}
for i in range(125):
 f=1+i/4;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 for who,r in RIGS.items():
  e=r.evaluated_get(dg);CACHE[who][f]={n:{'head':b.head.copy(),'tail':b.tail.copy(),'matrix':b.matrix.copy()} for n,b in e.pose.bones.items()}
def rounded(H,K,A,l1,d,radius):
 U=(K-H).normalized();V=(A-K).normalized()
 if d<l1-radius:return H+U*d,U
 if d>l1+radius:return K+V*(d-l1),V
 u=(d-l1+radius)/(2*radius);p=K-U*radius;q=K+V*radius;m=U*2*radius;n=V*2*radius;pos=p*(2*u**3-3*u*u+1)+m*(u**3-2*u*u+u)+q*(-2*u**3+3*u*u)+n*(u**3-u*u);der=p*(6*u*u-6*u)+m*(3*u*u-4*u+1)+q*(-6*u*u+6*u)+n*(3*u*u-2*u);return pos,der.normalized()
def add_pose_cache(o,poses):
 first=poses[1.];o.data.vertices.foreach_set('co',[c for p in first for c in p]);o.shape_key_add(name='Basis | F1 exact actual-bone drawing')
 for i in range(1,124):
  f=1+i/4;k=o.shape_key_add(name='V046 actual bones F%05.2f'%f);k.data.foreach_set('co',[c for p in poses[f] for c in p])
  for at in [1.,max(1.,f-.25),f,min(32.,f+.25),32.]:k.value=float(at==f);k.keyframe_insert('value',frame=at)
 action=o.data.shape_keys.animation_data.action;action.name=o.name+' | original31frameclock'
 for l in action.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR'
     cy=fc.modifiers.new('CYCLES');cy.mode_before=cy.mode_after='REPEAT'
for who,r in RIGS.items():
 for side in ['near','far']:
  for kind in ['sleeve','leg']:
   if kind=='sleeve':n1='upper_arm_'+side;n2='forearm_'+side;start=-.008;end=r.data.bones[n1].length+.027;rounding=.018;rows=49;depth=-.052 if side=='near' else .028
   else:n1='thigh_'+side;n2='shin_'+side;start=-.025;end=r.data.bones[n1].length+r.data.bones[n2].length-.030;rounding=.022;rows=65;depth=.005 if side=='near' else .042
   l1=r.data.bones[n1].length;total=r.data.bones[n1].length+r.data.bones[n2].length
   def radius(t):
    if kind=='sleeve':return interp(t,[(0,.038),(.12,.049),(.5,.045),(.85,.034),(1,.041)])
    if who=='BOY':return interp(t,[(0,.060),(.13,.063),(.4,.052),(.56,.043),(.77,.044),(.92,.034),(1,.040)])
    return interp(t,[(0,.043),(.45,.036),(.56,.031),(.78,.033),(1,.024)])
   UV=[]
   for i in range(rows):
    t=i/(rows-1)
    if kind=='sleeve':py=40+525*t;lo,hi=run(atlas,py,935,1205,1070);im=atlas
    elif who=='BOY':py=615+608*t;lo,hi=run(atlas,py,510,705,610);im=atlas
    else:d=start+(end-start)*t;q=max(0,min(1,(d-l1)/(end-l1)));py=714+110*q;lo,hi=run(pair,py,875 if side=='near' else 1030,1020 if side=='near' else 1170,950 if side=='near' else 1100);im=pair
    for j in range(9):UV.append(uv(im,lo+(hi-lo)*j/8,py))
   F=[(i*9+j,i*9+j+1,(i+1)*9+j+1,(i+1)*9+j) for i in range(rows-1) for j in range(8)];poses={}
   for f,pose in CACHE[who].items():
    H=pose[n1]['head'];K=pose[n1]['tail'];A=pose[n2]['tail'];verts=[]
    for i in range(rows):
     t=i/(rows-1);d=start+(end-start)*t;center,tangent=rounded(H,K,A,l1,d,rounding);normal=Vector((-tangent.z,0,tangent.x))
     for j in range(9):
      s=j/8;p=center+normal*((s*2-1)*radius(t));p.y=depth
      if kind=='leg':
       # Draw the final cloth rows into the actual moving boot shaft, retaining
       # the rigid shin above the last6.5cm and removing the old floating cuff.
       w=smooth((d-(total-.095))/.065);rest=Vector(((s*2-1)*radius(t),depth,r.data.bones[n1].head_local.z-d));bound=pose['foot_'+side]['matrix']@r.data.bones['foot_'+side].matrix_local.inverted()@rest;p=p.lerp(bound,w);p.y=depth
      verts.append(p)
    poses[f]=verts
   mat=M[who,'sleeve' if kind=='sleeve' else 'pants' if who=='BOY' else 'stocking'];o=objmesh('V046 '+who+' | '+('painted continuous rolled sleeve' if kind=='sleeve' else 'painted rigid-axis trousers' if who=='BOY' else 'original painted stockings')+' '+side,poses[1.],F,UV,mat,r);o['wardrobe_role']=kind;o['conformity']='Regenerated directly from actual evaluated age10 bone heads/tails at quarter frames. Straight rigid axes outside18/22mm elbow/knee rounding; lower cloth rows fit the moving boot.';add_pose_cache(o,poses);print('V046_ACTUAL_BONE_CLOTH',who,side,kind,flush=True)
# Give alpha-blended painted pieces real depth origins. Eevee sorts blended
# objects by their origins; leaving every origin on the rig reverses wardrobe
# occlusion even when the vertices themselves have the intended depth.
visible=[o for c in [ART,C] for o in c.objects if o.type=='MESH' and not o.hide_render]
def world_snapshot(frame):
 S.frame_set(frame);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();return {o.name:[o.evaluated_get(dg).matrix_world@v.co for v in o.evaluated_get(dg).data.vertices] for o in visible}
geometry_before={f:world_snapshot(f) for f in [1,9,17]}
origin_changes=[]
for o in visible:
 old=[v.co.copy() for v in o.data.vertices];depth=sum(p.y for p in old)/len(old)
 if abs(depth)<1e-9:continue
 if o.data.shape_keys:
  key_y={k.name:[p.co.y for p in k.data] for k in o.data.shape_keys.key_blocks}
  for k in o.data.shape_keys.key_blocks:
   for p,y in zip(k.data,key_y[k.name]):p.co.y=y-depth
 for p,original in zip(o.data.vertices,old):p.co.y=original.y-depth
 o.location.y+=depth;o.data.update();origin_changes.append({'object':o.name,'origin_depth_y_m':depth})
origin_error=0.
for f in [1,9,17]:
 after=world_snapshot(f)
 for n,V in after.items():origin_error=max(origin_error,max((a-b).length for a,b in zip(V,geometry_before[f][n])))
assert origin_error<.000002,origin_error
# Source/rig integrity assertions: appearance changes must not undo structure.
for who,r in RIGS.items():
 assert protected[who]['action_hash']==actionhash(r.animation_data.action)
 for b in r.data.bones:assert list(b.head_local)==protected[who]['bones'][b.name]['head'] and list(b.tail_local)==protected[who]['bones'][b.name]['tail']
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SRC_HASH
S['V046_status']='Age10 skeleton and validated root/contact actions preserved. Rich existing v040/v041 painting refitted to continuous garments and actual bone-driven limb drawings. New user rejected crude v044 outfit treatment; this is a separate restoration candidate.';S['V046_girl_limit']='Original charcoal girl head/braid/dress painting retained and refitted; it is not equivalent to an approved new full-color girl face/turnaround. Source hand/sleeve pigments are charcoal graded to retain her earlier palette.';S['V046_source_assumption']='Older polished look interpreted as v040/v041, the last positively received painted boy versions. No exact older version was named.';S.frame_set(1);bpy.context.view_layer.update();report={'source':str(SRC),'source_sha256':SRC_HASH,'source_unchanged':True,'bones_and_rig_actions_exactly_preserved':True,'protected_rigs':protected,'girl_finishing_caveat':S['V046_girl_limit'],'source_assumption':S['V046_source_assumption'],'new_paint_generated':False,'original_image_pixels_edited':False,'native_shape_drawing_sample_count':125,'clothing_rounding_m':{'elbow':.018,'knee':.022},'depth_origin_changes':origin_changes,'depth_origin_world_geometry_error_m':origin_error,'outfit_objects':[o.name for o in C.objects]};(P/'evidence/OUTFIT_RESTORATION_BUILD.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Age10_Painted_Outfit_Restoration_v046.blend'),compress=True);print('V046_OUTFIT_RESTORATION_NATIVE_SAVED',flush=True)
