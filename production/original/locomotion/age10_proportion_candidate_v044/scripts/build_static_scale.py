"""Stage 1: separate, editable age-ten static anatomy candidate. No animation retarget.
Original native files and original image pixels are read only.
"""
import bpy,math,json,hashlib,re
from pathlib import Path
from mathutils import Vector,Matrix
import numpy as np
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
for n in ['native','evidence','previews','reference']:(P/n).mkdir(exist_ok=True)
BOY=ROOT/'locomotion/neck_collar_connection_v041/native/WTSC_Neck_Collar_Connection_Candidate_v041.blend'
GIRL=ROOT/'locomotion/supported_recovery_v007/native/WTSC_Supported_Recovery_v007.blend'
HASH={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [BOY,GIRL]}
bpy.ops.wm.open_mainfile(filepath=str(BOY),load_ui=False,use_scripts=False);oldscene=bpy.context.scene
oldscene.name='REFERENCE | liked v041 boy and original source pair | preserved'
with bpy.data.libraries.load(str(GIRL),link=False) as (src,dst):dst.collections=['WTSC_BATTLEFIELD_DRAWN_PAIR_v007']
oldscene.collection.children.link(dst.collections[0]);oldscene.frame_set(1);bpy.context.view_layer.update()
originalBoy=bpy.data.objects['LOCO_BOY | RIG'];originalGirl=next(o for o in dst.collections[0].all_objects if o.type=='ARMATURE' and o.get('character')=='GIRL')
boynames=['V007_BOY | articulated drawn hand far','V007_BOY | articulated drawn hand near','V007_BOY | drawn skin far','V007_BOY | drawn skin near','V007_BOY | drawn sleeve far','V007_BOY | drawn sleeve near','V007_BOY | drawn source gray cuff far','V007_BOY | drawn source gray cuff near','V024 continuous far trouser drawing','V024 continuous near trouser drawing','V033 | far | canonical painted shoe','V033 | near | canonical painted shoe','V037 | coherent charcoal coat | five pose study','V040 | painted boy profile and neck','V041 | folded linen collar | neck attached']
girlnames=['LOCO_GIRL | PAINT body','PERF_GIRL | original head and attached braid']+[f'V007_GIRL | {n} {s}' for s in ['near','far'] for n in ['redrawn support boot','drawn leg','drawn sleeve','drawn source gray cuff','drawn skin','articulated drawn hand']]
fore=oldscene.view_layers['V025 | original foreground'];fore.update()
SNAP={};sourceRecords={};matCache={}
def clean_mesh(src):
 # Strip inherited deform-weight storage before rebinding to a different rig.
 # Retain actual topology, painted UVs, material slots and shader attributes.
 me=bpy.data.meshes.new('V044 clean copy | '+src.name);me.from_pydata([tuple(v.co) for v in src.vertices],[],[tuple(p.vertices) for p in src.polygons]);me.update()
 for a,b in zip(src.polygons,me.polygons):b.material_index=a.material_index;b.use_smooth=a.use_smooth
 for old in src.uv_layers:
  uv=me.uv_layers.new(name=old.name)
  for a,b in zip(old.data,uv.data):b.uv=a.uv
 for at in src.attributes:
  if at.name in me.attributes or at.name.startswith('.') or at.name=='position':continue
  field={'FLOAT':'value','INT':'value','BOOLEAN':'value','FLOAT_VECTOR':'vector','FLOAT_COLOR':'color','BYTE_COLOR':'color'}.get(at.data_type)
  if not field:continue
  try:
   dst=me.attributes.new(at.name,at.data_type,at.domain)
   for a,b in zip(at.data,dst.data):setattr(b,field,getattr(a,field))
  except (TypeError,RuntimeError):pass
 for m in src.materials:me.materials.append(m)
 return me
def freeze_mat(m):
 if not m:return None
 if m.name in matCache:return matCache[m.name]
 q=m.copy();q.name='V044 preserved paint | '+m.name
 q.surface_render_method='BLENDED'
 if q.node_tree and q.node_tree.animation_data:q.node_tree.animation_data_clear()
 if q.animation_data:q.animation_data_clear()
 matCache[m.name]=q;return q
for who,rig,names in [('BOY',originalBoy,boynames),('GIRL',originalGirl,girlnames)]:
 dg=oldscene.view_layers[0].depsgraph;rigOrigin=rig.matrix_world.translation.copy();bones={n:{'head':rig.matrix_world@b.head,'tail':rig.matrix_world@b.tail} for n,b in rig.pose.bones.items()};parts={}
 for name in names:
  if who=='GIRL':o=next(o for o in dst.collections[0].all_objects if o.name.split('.00')[0]==name)
  else:o=bpy.data.objects[name]
  vldg=fore.depsgraph if who=='BOY' and (o.name.startswith('V040 |') or o.name.startswith('V041 |')) else dg
  e=o.evaluated_get(vldg);temp=e.to_mesh(preserve_all_data_layers=True,depsgraph=vldg);me=temp.copy();e.to_mesh_clear();world=[e.matrix_world@v.co for v in me.vertices]
  me.materials.clear()
  for slot in o.material_slots:me.materials.append(freeze_mat(slot.material))
  # Geometry is a snapshot only; shader UV/paint and vertex attributes remain.
  parts[name]={'mesh':me,'world':world,'object':o,'world_matrix':e.matrix_world.copy()}
 SNAP[who]={'parts':parts,'bones':bones,'origin':rigOrigin,'rig':rig}
 sourceRecords[who]={'rig':rig.name,'height_basis_m':rig['height_m'],'parts':list(parts),'bones_F1':{n:{k:list(v) for k,v in b.items()} for n,b in bones.items()}}
S=bpy.data.scenes.new('V044 | AGE TEN | STATIC SCALE FIRST');bpy.context.window.scene=S
S.render.engine='BLENDER_EEVEE';S.eevee.taa_render_samples=32;S.render.fps=30;S.frame_start=0;S.frame_end=0;S.render.resolution_x=1800;S.render.resolution_y=1200;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGBA';S.render.threads_mode='FIXED';S.render.threads=2;S.render.film_transparent=False;S.view_settings.view_transform='Standard';S.view_settings.look='None';S.unit_settings.system='METRIC';S.unit_settings.scale_length=1.
S.world=bpy.data.worlds.new('V044 neutral paper');S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.68,.69,.65,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=1
def collection(n):c=bpy.data.collections.new(n);S.collection.children.link(c);return c
ART=collection('V044 | age10 editable profile anatomy');BEFORE=collection('V044 | before F1 source painting snapshots');GUIDE=collection('V044 | dimension grid and surface landmarks');FRONT=collection('V044 | front CONSTRUCTION ONLY | no front art available')
def emission(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;ns=m.node_tree.nodes;ns.clear();e=ns.new('ShaderNodeEmission');e.inputs[0].default_value=(*c,1);o=ns.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],o.inputs[0]);return m
ink=emission('V044 guide ink',(.10,.16,.17));gridmat=emission('V044 quiet metric grid',(.45,.48,.45));blue=emission('V044 estimated internal joints',(.06,.32,.43));bonewhite=emission('V044 construction silhouette',(.78,.79,.74));red=emission('V044 surface landmark',(.49,.16,.08))
def mesh(n,verts,faces,c,mat=None):
 me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(n,me);c.objects.link(ob)
 if mat:me.materials.append(mat)
 return ob
def line(n,a,b,mat=gridmat,width=.001,c=GUIDE):
 a=Vector(a);b=Vector(b);d=(b-a).normalized();side=Vector((-d.z,0,d.x))*width/2
 return mesh(n,[a-side,b-side,b+side,a+side],[(0,1,2,3)],c,mat)
def text(n,body,x,z,size=.024,mat=ink,c=GUIDE):
 cu=bpy.data.curves.new(n,'FONT');cu.body=body;cu.size=size;cu.align_x='LEFT';o=bpy.data.objects.new(n,cu);c.objects.link(o);o.location=(x,-.25,z);o.rotation_euler=(math.pi/2,0,0);cu.materials.append(mat);return o
for i in range(-16,17):line('10cm vertical grid '+str(i),(i*.1,.2,0),(i*.1,.2,2.02),width=.00035)
for i in range(21):line('10cm horizontal grid '+str(i),(-1.6,.2,i*.1),(1.6,.2,i*.1),width=.00035)
line('GROUND | shoe outer sole',( -1.6,-.18,0),(1.6,-.18,0),ink,.002)
for i in range(11):text('ruler '+str(i),f'{i*20} cm',-1.56,i*.2+.008,.017)
line('2.00m calibration frame', (1.27,.1,0),(1.27,.1,2.0),ink,.003)
line('calibration frame top',(1.27,.1,2.0),(1.50,.1,2.0),ink,.003);line('calibration frame base',(1.27,.1,0),(1.50,.1,0),ink,.003)
text('calibration label','2.00 m\ncalibration\nframe',1.29,1.68,.022)
text('static title','AGE TEN | STATIC PROPORTION CANDIDATE | original paintings retained',-1.36,2.05,.028)
CAM=bpy.data.cameras.new('V044 orthographic metric camera');camera=bpy.data.objects.new(CAM.name,CAM);S.collection.objects.link(camera);camera.location=(0,-10,1.0);camera.rotation_euler=(math.pi/2,0,0);CAM.type='ORTHO';CAM.ortho_scale=3.25;S.camera=camera
TARGET={
 'BOY':{'stature_barefoot_m':1.390,'vertical_head_m':.194,'shoe_lift_m':.025,'surface_shoulder_breadth_m':.300,'estimated_hip_joint_z_m':.752,'estimated_knee_joint_z_m':.417,'estimated_ankle_joint_z_m':.095,'estimated_shoulder_joint_z_m':1.145,'upper_arm_joint_length_m':.235,'forearm_joint_length_m':.200,'drawn_hand_length_m':.145,'bare_foot_length_m':.202,'shoe_outer_length_m':.223,'skull_crown_source_px':[225,95],'chin_source_px':[328,403],'neck_source_x_px':178.,'head_image_size':[1254,1254],'x':-.66},
 'GIRL':{'stature_barefoot_m':1.380,'vertical_head_m':.193,'shoe_lift_m':.025,'surface_shoulder_breadth_m':.298,'estimated_hip_joint_z_m':.746,'estimated_knee_joint_z_m':.413,'estimated_ankle_joint_z_m':.095,'estimated_shoulder_joint_z_m':1.137,'upper_arm_joint_length_m':.233,'forearm_joint_length_m':.199,'drawn_hand_length_m':.144,'bare_foot_length_m':.200,'shoe_outer_length_m':.221,'skull_crown_source_px':[985,137],'chin_source_px':[1064,280],'neck_source_x_px':1008.,'head_image_size':[1672,941],'x':.36}}
RESULT={}
def profile_point(who,px,py):
 t=TARGET[who];scale=t['vertical_head_m']/(t['chin_source_px'][1]-t['skull_crown_source_px'][1]);return Vector(((px-t['neck_source_x_px'])*scale, -.065,t['stature_barefoot_m']+t['shoe_lift_m']-(py-t['skull_crown_source_px'][1])*scale))
def uv_per_vertex(me,name=None):
 layer=me.uv_layers.get(name) if name else me.uv_layers[0];r={}
 for lp in me.loops:r[lp.vertex_index]=Vector(layer.data[lp.index].uv)
 return r
def bone_line(snapshot,name):return snapshot['bones'][name]['head'],snapshot['bones'][name]['tail']
def transplant(who,part,kind,side=None):
 snap=SNAP[who];t=TARGET[who];me=clean_mesh(part['mesh']);V=[];groups=[];src=part['world'];origin=snap['origin'];y=-.045 if side=='near' else .035
 def pair(name):a,b=bone_line(snap,name);d=(b-a).normalized();return a,b,d,Vector((-d.z,0,d.x)),(b-a).length
 if kind=='head':
  uv=uv_per_vertex(me);W,H=t['head_image_size']
  for i in range(len(src)):u=uv[i];V.append(profile_point(who,u.x*W,(1-u.y)*H));groups.append({'head':1})
 elif kind=='collar':
  h=snap['parts']['V040 | painted boy profile and neck'];u=uv_per_vertex(h['mesh']);X=[];B=[]
  for i,p in enumerate(h['world']):X.append([p.x,p.z,1]);B.append([u[i].x*1254,(1-u[i].y)*1254])
  affine=np.linalg.lstsq(np.array(X),np.array(B),rcond=None)[0]
  for p in src:q=np.array([p.x,p.z,1])@affine;v=profile_point(who,*q);v.y=-.067;V.append(v);groups.append({'chest':1})
 elif kind=='coat':
  collar_src=snap['parts']['V040 | painted boy profile and neck'];u=uv_per_vertex(collar_src['mesh']);aa=np.array([[p.x,p.z,1] for p in collar_src['world']]);bb=np.array([[u[i].x*1254,(1-u[i].y)*1254] for i in range(len(aa))]);affine=np.linalg.lstsq(aa,bb,rcond=None)[0]
  for i,p in enumerate(src):
   row=i//17;z=float(np.interp(p.z,[.58,.85,1.11],[.69,.94,1.176]));v=Vector(((p.x-origin.x)*.92,-.018,z))
   if row<7:
    q=np.array([p.x,p.z,1])@affine;top=profile_point(who,*q);w=max(0,1-row/6);v.x=v.x*(1-w)+top.x*w;v.z=v.z*(1-w)+top.z*w
   V.append(v);groups.append({'chest':min(1,max(0,(v.z-.77)/.13)),'pelvis':1-min(1,max(0,(v.z-.77)/.13))})
  # Monotonic upper rows prevent the old fitted neckline from folding into a
  # small spike when the whole neck is fitted to a smaller anatomical head.
  for row in range(1,6):
   q=row/6;q=q*q*(3-2*q)
   for col in range(17):V[row*17+col]=V[col].lerp(V[6*17+col],q)
 elif kind=='dress':
  uv=uv_per_vertex(me);W,H=1672,941
  for i,p in enumerate(src):
   px=uv[i].x*W;py=(1-uv[i].y)*H;cx=float(np.interp(py,[289,460,714],[1008,1004,1003]));xs=float(np.interp(py,[289,460,714],[.00134965,.00135,.00123]));z=float(np.interp(py,[289,345,460,714],[1.20,1.13,.87,.535]));v=Vector(((px-cx)*xs,-.017,z))
   if py<345:
    hp=profile_point(who,px,py);v.x=hp.x;v.z=hp.z
   V.append(v);w=min(1,max(0,(v.z-.77)/.12));groups.append({'chest':w,'pelvis':1-w})
 elif kind=='boot':
  # Use the liked boy's canonical source shoe for both. This is a shared footwear
  # construction choice, not a bare-foot measurement. Original meshes untouched.
  raw=[v.co.copy() for v in part['object'].data.vertices];xmin=min(p.x for p in raw);xmax=max(p.x for p in raw);zmin=min(p.z for p in raw);zmax=max(p.z for p in raw);V=[];me=clean_mesh(part['object'].data);me.materials.clear()
  for m in part['mesh'].materials:me.materials.append(m)
  for p in raw:V.append(Vector((-.070+(p.x-xmin)/(xmax-xmin)*t['shoe_outer_length_m'],y,(p.z-zmin)/(zmax-zmin)*.132)));groups.append({'foot_'+side:1})
 elif kind in ['upper','cuff','forearm','hand']:
  bn=('upper_arm_' if kind in ['upper','cuff'] else 'forearm_' if kind=='forearm' else 'hand_')+side;a,b,d,perp,L=pair(bn);nb=REST[who][bn];na,nt=nb;nd=(nt-na).normalized();npv=Vector((-nd.z,0,nd.x));along=[(p-a).dot(d) for p in src];scale=(nt-na).length/L
  lo=min(along);hi=max(along)
  if kind=='hand':start,end=-.004,t['drawn_hand_length_m']-.004
  elif kind=='forearm':start,end=-.004,t['forearm_joint_length_m']+.010
  elif kind=='upper':start,end=-.012,t['upper_arm_joint_length_m']+.008
  else:start,end=t['upper_arm_joint_length_m']-.025,t['upper_arm_joint_length_m']+.016
  across=[(p-a).dot(perp) for p in src];norm=[(u-lo)/(hi-lo) for u in along];c0=float(np.median([c for c,n in zip(across,norm) if n<.20]));c1=float(np.median([c for c,n in zip(across,norm) if n>.80]));residual=[c-(c0+(c1-c0)*n) for c,n in zip(across,norm)];span=max(residual)-min(residual)
  for i,p in enumerate(src):
   u=along[i];cross=across[i]-(c0+(c1-c0)*norm[i])
   u=start+(u-lo)/(hi-lo)*(end-start)
   if kind=='hand':cross*=1.10
   elif kind=='cuff':cross*=.075/span
   elif kind=='upper':cross*=(.10-.035*norm[i])/span
   v=na+nd*u+npv*cross;v.y=y;V.append(v);groups.append({bn:1})
 elif kind=='leg':
  a,k,d,pv,L=pair('thigh_'+side);b,f,dd,pp,LL=pair('shin_'+side)
  for p in src:
   options=[]
   for bn,h,tail,D,perp,l in [('thigh_'+side,a,k,d,pv,L),('shin_'+side,b,f,dd,pp,LL)]:
    u=max(0,min(1,(p-h).dot(D)/l));center=h+D*u*l;options.append(((p-center).length,bn,u,(p-center).dot(perp)))
   _,bn,u,cross=min(options,key=lambda x:x[0]);na,nt=REST[who][bn];D=(nt-na).normalized();perp=Vector((-D.z,0,D.x));v=na.lerp(nt,u)+perp*cross*.94;v.y=y+.007;V.append(v)
   kneeZ=REST[who]['shin_'+side][0].z;w=max(0,min(1,(v.z-kneeZ+.022)/.044));groups.append({'thigh_'+side:w,'shin_'+side:1-w})
  lo=min(v.z for v in V)
  if lo>.118:
   for v in V:
    if v.z<.20:v.z=.118+(v.z-lo)/(.20-lo)*(.20-.118)
 else:raise ValueError(kind)
 assert len(V)==len(me.vertices),(kind,len(V),len(me.vertices))
 for p,v in zip(me.vertices,V):p.co=v
 me.update();return me,groups
REST={};RIGS={}
for who,t in TARGET.items():
 print('V044_BUILD_CHARACTER',who,flush=True)
 hip=t['estimated_hip_joint_z_m'];shoulder=t['estimated_shoulder_joint_z_m'];ank=t['estimated_ankle_joint_z_m'];knee=t['estimated_knee_joint_z_m'];crown=t['stature_barefoot_m']+t['shoe_lift_m'];chin=crown-t['vertical_head_m'];r={'pelvis':(Vector((0,0,hip)),Vector((0,0,hip+.10))),'chest':(Vector((0,0,hip+.10)),Vector((0,0,shoulder))),'head':(Vector((0,0,chin)),Vector((0,0,crown)))}
 for side in ['near','far']:
  r['upper_arm_'+side]=(Vector((0,0,shoulder)),Vector((0,0,shoulder-t['upper_arm_joint_length_m'])))
  r['forearm_'+side]=(r['upper_arm_'+side][1],r['upper_arm_'+side][1]-Vector((0,0,t['forearm_joint_length_m'])))
  r['hand_'+side]=(r['forearm_'+side][1],r['forearm_'+side][1]-Vector((0,0,.13)))
  r['thigh_'+side]=(Vector((0,0,hip)),Vector((0,0,knee)))
  r['shin_'+side]=(Vector((0,0,knee)),Vector((0,0,ank)))
  r['foot_'+side]=(Vector((0,0,ank)),Vector((.105,0,.025)))
 REST[who]=r;arm=bpy.data.armatures.new('V044 '+who+' | estimated joint centres');rig=bpy.data.objects.new(arm.name,arm);ART.objects.link(rig);rig.location.x=t['x'];bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 for n,(a,b) in r.items():bo=arm.edit_bones.new(n);bo.head=a;bo.tail=b
 bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False);rig['age_years']=10;rig['anatomy_stage']='Static scale candidate first. Joint placements are estimates; surface anthropometry is not bone length.';rig['stature_barefoot_m']=t['stature_barefoot_m'];rig['source_identity']='Liked v041 boy painting; retained v015 girl with original attached braid. No flat card head turn.';RIGS[who]=rig
 # Original painting snapshots at exact source F1, displayed at the same unit scale.
 for name,part in SNAP[who]['parts'].items():
  print('V044_BUILD_PART',who,name,flush=True)
  me=part['mesh'].copy()
  for v,p in zip(me.vertices,part['world']):v.co=p-SNAP[who]['origin']
  ob=bpy.data.objects.new('BEFORE '+who+' | '+name,me);BEFORE.objects.link(ob);ob.location.x=t['x']
 for name,part in SNAP[who]['parts'].items():
  side='near' if re.search(r'\bnear\b',name) else 'far' if re.search(r'\bfar\b',name) else None
  if 'profile and neck' in name or 'original head and attached braid' in name:kind='head'
  elif 'folded linen collar' in name:kind='collar'
  elif 'coherent charcoal coat' in name:kind='coat'
  elif name=='LOCO_GIRL | PAINT body':kind='dress'
  elif 'shoe' in name or 'support boot' in name:kind='boot'
  elif 'trouser drawing' in name or 'drawn leg' in name:kind='leg'
  elif 'articulated drawn hand' in name:kind='hand'
  elif 'gray cuff' in name:kind='cuff'
  elif 'drawn skin' in name:kind='forearm'
  elif 'drawn sleeve' in name:kind='upper'
  else:raise ValueError(name)
  if kind=='boot':part=SNAP['BOY']['parts']['V033 | near | canonical painted shoe']
  me,weights=transplant(who,part,kind,side);ob=bpy.data.objects.new('V044 '+who+' | '+kind+(' '+side if side else ''),me);ART.objects.link(ob);ob.parent=rig;ob['preserved_source_part']=name;ob['proportion_role']=kind
  for bn in set(n for w in weights for n in w):vg=ob.vertex_groups.new(name=bn)
  for i,w in enumerate(weights):
   for bn,val in w.items():
    if val>0:ob.vertex_groups[bn].add([i],val,'REPLACE')
  mod=ob.modifiers.new('V044 editable anatomical rig','ARMATURE');mod.object=rig
 # Front view is an explicit construction guide, not invented finished artwork.
 x=t['x'];zShoulder=shoulder;crown=t['stature_barefoot_m']+.025;chin=crown-t['vertical_head_m'];bw=t['surface_shoulder_breadth_m']
 outline=[(x-.11,-.06,.75),(x-.105,-.06,.89),(x-bw/2,-.06,shoulder),(x+bw/2,-.06,shoulder),(x+.105,-.06,.89),(x+.11,-.06,.75)]
 mesh('V044 '+who+' front torso | construction only',outline,[tuple(range(6))],FRONT,bonewhite)
 verts=[(x+.073*math.cos(i*math.tau/64),-.06,(chin+crown)/2+t['vertical_head_m']/2*math.sin(i*math.tau/64)) for i in range(64)];mesh('V044 '+who+' front head | estimated unpainted construction',verts,[tuple(range(64))],FRONT,bonewhite)
 for side,sign in [('near',-1),('far',1)]:
  pts=[(x+sign*bw/2,-.08,shoulder),(x+sign*.16,-.08,shoulder-t['upper_arm_joint_length_m']),(x+sign*.17,-.08,shoulder-t['upper_arm_joint_length_m']-t['forearm_joint_length_m']),(x+sign*.17,-.08,shoulder-t['upper_arm_joint_length_m']-t['forearm_joint_length_m']-t['drawn_hand_length_m'])]
  for j in range(3):line(who+' front arm '+side+str(j),pts[j],pts[j+1],blue,.009,FRONT)
  for a,b in [((x+sign*.075,-.08,hip),(x+sign*.077,-.08,knee)),((x+sign*.077,-.08,knee),(x+sign*.080,-.08,ank)),((x+sign*.080,-.08,ank),(x+sign*.080,-.08,.025))]:line(who+' front leg '+side,a,b,blue,.012,FRONT)
 line(who+' shoulder surface span',(x-bw/2,-.10,shoulder+.045),(x+bw/2,-.10,shoulder+.045),red,.0015,FRONT)
 text(who+' front breadth',f'{bw*100:.1f} cm surface shoulder span',x-.24,shoulder+.065,.019,c=FRONT)
 for label,z in [('skull crown',crown),('chin',chin),('shoe sole',0)]:
  line(who+' '+label+' marker',(x-.29,-.13,z),(x+.30,-.13,z),red,.0008)
 text(who+' height',f'{who} | 10 years\n{t["stature_barefoot_m"]:.2f} m barefoot skull crown\n+2.5 cm shoe lift; hair above crown',x-.28,1.72,.023)
 if who=='GIRL':
  neckmat=emission('V044 girl | quiet original charcoal neck bridge',(.012,.013,.015));o=mesh('V044 GIRL | neck overlap drawn bridge',[(-.028,.0,1.226),(.026,.0,1.226),(.013,.0,1.185),(.019,.0,1.153),(-.028,.0,1.153),(-.020,.0,1.193)],[tuple(range(6))],ART,neckmat);o.parent=rig;vg=o.vertex_groups.new(name='head');vg.add(list(range(6)),1,'REPLACE');mod=o.modifiers.new('V044 neck head attachment','ARMATURE');mod.object=rig;o['proportion_role']='neck bridge'
  # This visibility pose keeps the larger hands clear of the dark dress. It is
  # a static model-sheet pose; it is not an authored walk or new acting choice.
  for side,ang in [('near',math.radians(24)),('far',math.radians(-18))]:
   shoulderPt=r['upper_arm_'+side][0];D=Vector((math.sin(ang),0,-math.cos(ang)));elbow=shoulderPt+D*t['upper_arm_joint_length_m'];wrist=elbow+D*t['forearm_joint_length_m']
   for bn,a,b in [('upper_arm_'+side,shoulderPt,elbow),('forearm_'+side,elbow,wrist),('hand_'+side,wrist,wrist+D*.13)]:
    rb=rig.data.bones[bn];oldD=(rb.tail_local-rb.head_local).normalized();newD=(b-a).normalized();Q=oldD.rotation_difference(newD);rig.pose.bones[bn].matrix=Matrix.Translation(a)@Q.to_matrix().to_4x4()@rb.matrix_local.to_3x3().to_4x4()
 line(who+' front neck',(x,-.065,chin),(x,-.065,shoulder),bonewhite,.065,FRONT)
 for name,v in [('skull vertex | ESTIMATED under hair',profile_point(who,*t['skull_crown_source_px'])),('menton | painted chin',profile_point(who,*t['chin_source_px'])),('bare heel support | inside shoe',Vector((-.060,0,.025))),('bare longest toe | inside shoe',Vector((-.060+t['bare_foot_length_m'],0,.025)))]:
  marker=bpy.data.objects.new('V044 '+who+' | '+name,None);ART.objects.link(marker);marker.parent=rig;marker.location=v;marker.empty_display_type='SPHERE';marker.empty_display_size=.004;marker['landmark_type']='Authored surface landmark estimate, not a rig joint centre';marker['candidate_age']=10
 RESULT[who]={**t,'estimated_rest_bone_lengths_m':{n:(b-a).length for n,(a,b) in r.items()},'head_mapping_scene_units_per_source_pixel':t['vertical_head_m']/(t['chin_source_px'][1]-t['skull_crown_source_px'][1]),'uniform_head_mapping':True,'standing_skull_crown_world_z_m':crown,'chin_world_z_m':chin,'foot_measure_is_inside_shoe':True,'static_visibility_pose_girl_arms_degrees':[24,-18] if who=='GIRL' else [0,0]}
for o in BEFORE.objects:o.hide_render=True;o.hide_viewport=True
for o in FRONT.objects:o.hide_render=True;o.hide_viewport=True
S['stage']='STAGE1 STATIC ANATOMY AND GLOBAL SCALE CANDIDATE. No animation retarget performed.';S['age_target']='Conrad explicitly specified ten years for BOTH children.';S['measurement_limit']='Barefoot stature excludes shoes/hair. Chin-to-skull-vertex head landmarks under hair are estimated in existing paintings. Internal joints are estimated and are not asserted as surface anthropometry. No official orthographic front artwork exists; front view is a construction diagram only.';S['movement_reference']='Preferred v028/v041 31-frame cycle remains in separate retained reference scene. Do not claim its foot contacts/travel are already validated on this static candidate.'
txt=bpy.data.texts.new('READ FIRST v044 | SCALE BEFORE ANIMATION');txt.write(S['stage']+'\n'+S['measurement_limit']+'\n'+S['movement_reference'])
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:
  try:im.pack()
  except RuntimeError:pass
report={'stage':S['stage'],'blender':bpy.app.version_string,'build_hash':bpy.app.build_hash.decode(),'sources':HASH,'girl_source_available':True,'retained_girl_braid':True,'original_pixel_images_edited':False,'candidate_measurements':RESULT,'source_snapshot':sourceRecords,'caveats':[S['measurement_limit'],S['movement_reference']],'sources_unchanged':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in HASH.items()}}
assert all(report['sources_unchanged'].values());(P/'evidence/STATIC_SCALE_BUILD.json').write_text(json.dumps(report,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Age10_Static_Proportion_Candidate_v044.blend'),compress=True);print('V044_STATIC_BUILT_NO_RETARGET',flush=True)
