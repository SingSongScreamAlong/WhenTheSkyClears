"""Authored support acting on original independent planar bones and drawings."""
import math,json
import bpy
from mathutils import Vector,Matrix

def author(g):
 rigs,rest,baseline=g['rigs'],g['rest'],g['baseline'];smooth=g['smooth'];cv=g['curveval'];around=g['around'];poses=g['poses']
 def bone(w,n,A,B):
  r=rest[w][n];v=rigs[w].data.bones[n].tail_local-r.translation;d=B-A
  angle=math.atan2(d.x,d.z)-math.atan2(v.x,v.z)
  return Matrix.Translation(A)@Matrix.Rotation(angle,4,'Y')@Matrix.Translation(-r.translation)@r
 def arm(w,p,side,W,direction):
  S=p['upper_arm_'+side].translation;L1=rigs[w].data.bones['upper_arm_'+side].length;L2=rigs[w].data.bones['forearm_'+side].length;d=W-S;d.y=0;D=min(max(d.length,abs(L1-L2)+.001),(L1+L2)*.994);u=d.normalized();W=S+u*D;W.y=-.037
  a=(L1*L1-L2*L2+D*D)/(2*D);h=math.sqrt(max(0,L1*L1-a*a));n=Vector((-u.z,0,u.x));E1=S+u*a+n*h;E2=S+u*a-n*h
  # Elbow below the shoulder and clear of the face; no stretch.
  E=min([E1,E2],key=lambda E:E.z+(.12*abs(E.x-S.x)));E.y=0
  p['upper_arm_'+side]=bone(w,'upper_arm_'+side,S,E);p['forearm_'+side]=bone(w,'forearm_'+side,E,W);p['hand_'+side]=bone(w,'hand_'+side,W,W+direction.normalized()*.06)
  return W
 events=[]
 for who,rig in rigs.items():
  for t in list(rig.animation_data.nla_tracks):rig.animation_data.nla_tracks.remove(t)
  rig.animation_data.action=None;action=bpy.data.actions.new('V007_'+who+'__SUPPORTED_RECOVERY_120F');rig.animation_data.action=action
  for f in range(1,121):
   src=baseline[who][f];p={n:m.copy() for n,m in src.items()}
   if who=='BOY':
    ox=cv([(1,0),(28,0),(42,.025),(52,.065),(68,.045),(80,.055),(89,.085),(102,.075),(120,.025)],f)
    oz=cv([(1,0),(30,0),(43,.025),(55,.015),(70,-.045),(81,-.085),(89,-.100),(99,-.075),(112,-.025),(120,0)],f)
    tilt=cv([(1,0),(30,0),(46,.06),(58,.10),(72,.10),(86,.18),(94,.15),(108,.035),(120,-.025)],f)
   else:
    ox=cv([(1,0),(28,0),(40,-.020),(52,-.025),(70,-.035),(85,-.040),(103,.015),(120,.025)],f)
    oz=cv([(1,0),(28,0),(39,.045),(48,.075),(58,.040),(73,0),(92,-.015),(110,0),(120,0)],f)
    tilt=cv([(1,0),(26,0),(38,-.24),(48,-.30),(65,-.18),(83,-.13),(103,-.16),(120,-.12)],f)
   offset=Vector((ox,0,oz));hip=src['pelvis'].translation+offset
   for n in p:
    if not n.startswith('foot_'):p[n]=Matrix.Translation(offset)@src[n]
   delta=around(hip,tilt)
   for n in ['chest','head','upper_arm_near','upper_arm_far','forearm_near','forearm_far','hand_near','hand_far','braid']:
    if n in p:p[n]=delta@p[n]
   nod=cv([(1,0),(44,-.03),(64,-.06),(81,-.02),(96,-.12),(120,-.06)],f) if who=='BOY' else cv([(1,0),(39,-.02),(46,.05),(57,-.07),(90,-.04),(120,-.025)],f)
   hd=around(p['head'].translation,nod);p['head']=hd@p['head']
   if 'braid' in p:p['braid']=hd@p['braid']
   if who=='GIRL' and f>=44:
    r=rest[who]['head'];current=math.atan2(p['head'].col[1].x,p['head'].col[1].z)-math.atan2(r.col[1].x,r.col[1].z);desired=cv([(44,-.27),(70,-.22),(90,-.14),(120,-.055)],f)
    turn=around(p['head'].translation,(desired-current)*smooth(43,48,f));p['head']=turn@p['head']
    if 'braid' in p:p['braid']=turn@p['braid']
   for side in ['near','far']:
    H=src['thigh_'+side].translation+offset;A=src['foot_'+side].translation;K=src['shin_'+side].translation+offset*.45
    active=smooth(27,35,f)*(1-smooth(63,72,f))
    if who=='BOY':
     if side=='near':drawK=Vector((H.x-.070,0,max(A.z+.085,H.z-.180)))
     else:drawK=Vector((H.x*.35+A.x*.65+.025,0,(H.z+A.z)*.5+.015))
    else:drawK=H.lerp(A,.52)+Vector((.025,0,.008))
    K=K.lerp(drawK,active)
    # New hips settle over the same boots after stop; skeleton and drawing agree.
    late=smooth(72,81,f);K=K.lerp(H.lerp(A,.52)+Vector((.045 if who=='BOY' else .022,0,0)),late)
    p['thigh_'+side]=bone(who,'thigh_'+side,H,K);p['shin_'+side]=bone(who,'shin_'+side,K,A)
   if who=='BOY':
    brace=smooth(37,49,f)*(1-smooth(101,115,f));W=p['hand_near'].translation;target=hip.lerp(p['shin_far'].translation,.45)+Vector((.030,0,.028));W=W.lerp(target,brace);arm(who,p,'near',W,Vector((.25,0,-1)))
    help=smooth(80,101,f);W=p['hand_far'].translation;z=cv([(1,.81),(86,.79),(101,.82),(120,.87)],f);target=Vector((.416,-.037,z));actual=arm(who,p,'far',W.lerp(target,help),Vector((1,0,0)))
   else:
    checking=smooth(35,56,f);W=p['hand_far'].translation;target=Vector((.20,0,.71));arm(who,p,'far',W.lerp(target,checking),Vector((.35,0,-1)))
    offer=smooth(43,78,f);W=p['hand_near'].translation;z=cv([(1,.81),(86,.79),(101,.82),(120,.87)],f);target=Vector((-.256,-.037,z));actual=arm(who,p,'near',W.lerp(target,offer),Vector((-1,0,0)))
   poses[who][f]=p
   for name,m in p.items():
    pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';pb.matrix=m
    for field in ['location','rotation_quaternion','scale']:pb.keyframe_insert(field,frame=f,group=name)
   if f in [37,43,48,58,81,89,101,110,120]:events.append({'who':who,'frame':f,'hip':list(hip),'hands':{side:list(p['hand_'+side].translation) for side in ['near','far']}})
  g['linear'](action);g['stash'](rig,action,'V007 distinct support acting')
 (g['P']/'evidence/acting_samples.json').write_text(json.dumps(events,indent=2))

def boots(g):
 src,rigs,rest,baseline,poses=g['src'],g['rigs'],g['rest'],g['baseline'],g['poses'];openings={};report=[]
 for who,rig in rigs.items():
  for side in ['near','far']:
   old=next(o for o in rig.children if 'rigid original boot '+side in o.name);data=src['feet'][who+'_'+side];allposes={};newopens={};sole_error=0
   original=[v.co.copy() for v in old.data.vertices];layer=old.data.uv_layers.active;vuv={lp.vertex_index:layer.data[lp.index].uv.copy() for lp in old.data.loops};uvs=[tuple(vuv[i]) for i in range(len(original))];yy={i:(1-vuv[i].y)*941 for i in range(len(original))};top=min(yy.values());ids=[i for i,y in yy.items() if y<top+1.6];left=min(ids,key=lambda i:original[i].x);right=max(ids,key=lambda i:original[i].x)
   protected={i for i,p in enumerate(original) if min((p.x-x)**2+(p.z-z)**2 for x,z in data['lower_hull'])<1e-9 or yy[i]>top+43}
   # The original support mesh resampled a few source contour coordinates.
   # Protect actual native edge vertices, not just exact source-pixel matches.
   protected.update(min(range(len(original)),key=lambda i:(original[i].x-x)**2+(original[i].z-z)**2) for x,z in data['lower_hull'])
   for f in range(1,121):
    M=baseline[who][f]['foot_'+side]@rest[who]['foot_'+side].inverted();inv=M.inverted();A=baseline[who][f]['foot_'+side].translation;K=poses[who][f]['shin_'+side].translation;shin=(K-A).normalized();O=A+shin*.027;axis=g['normal'](shin);L,Q=sorted([O-axis*(.043 if who=='BOY' else .032),O+axis*(.043 if who=='BOY' else .032)],key=lambda p:p.x)
    strength=g['smooth'](28,35,f)*(1-g['smooth'](63,72,f));out=[]
    for i,p in enumerate(original):
     w=0 if i in protected else (1-g['smooth'](top+3,top+43,yy[i]))*strength;u=(p.x-original[left].x)/max(.001,original[right].x-original[left].x);target=L.lerp(Q,max(0,min(1,u)));source_top=(M@original[left]).lerp(M@original[right],u);out.append(inv@(M@p+(target-source_top)*w))
    allposes[f]=out;newopens[f]=(M@out[left],M@out[right])
   faces=[tuple(poly.vertices) for poly in old.data.polygons];material=old.data.materials[0]
   ob=g['morph']('V007_'+who+' | redrawn support boot '+side,allposes,faces,uvs,material,rig,'foot_'+side,role='support_boot');old.hide_render=True;old.hide_viewport=True;old['superseded_by_v007']=ob.name
   newopens['rest']=(original[left],original[right]);openings[who,side]=newopens
   report.append({'who':who,'side':side,'sole_curve_points':len(data['lower_hull']),'sole_vertices_unchanged':all((allposes[f][i]-original[i]).length<1e-7 for f in allposes for i in protected),'sole_curve_max_error_m':sole_error,'method':'Original shoe and UVs retained; source sole and heel/toe points protected exactly; localized native upper-boot drawings align toward new shin only in catch/recovery28..72. No rounded caps.'})
 return report,openings

def glance(g):
 who='GIRL';rig=g['rigs'][who];old=next(o for o in rig.children if 'original head and attached braid' in o.name);axis=g['rest'][who]['head'].translation.x
 mirror=old.copy();mirror.data=old.data.copy();mirror.name='V007_GIRL | original-painted look toward boy';rig.users_collection[0].objects.link(mirror);mirror.parent=rig
 for v in mirror.data.vertices:v.co.x=2*axis-v.co.x
 mirror.vertex_groups.clear();group=mirror.vertex_groups.new(name='head');group.add(list(range(len(mirror.data.vertices))),1,'REPLACE')
 mirror['v007_role']='look_back_original_paint';mirror['method']='Native reflected source profile plus hand-authored back-of-head passing drawing. Local2D pose variant, no new bitmap or3D head.'
 mirror.shape_key_add(name='Basis');lag=mirror.shape_key_add(name='Braid lag on turned head')
 for i,v in enumerate(mirror.data.vertices):
  w=max(0,min(1,(1.08-v.co.z)/.20));lag.data[i].co.x+=.018*w;lag.data[i].co.z+=.006*w
 for f in range(1,121):lag.value=math.exp(-max(0,f-49)/25)*math.sin((f-49)/5) if f>=48 else 0;lag.keyframe_insert('value',frame=f)
 action=mirror.data.shape_keys.animation_data.action;action.name='V007_GIRL | braid turn followthrough';g['linear'](action);g['stash'](mirror.data.shape_keys,action,'V007 turned braid')
 # Two-frame drawn back-of-head passing pose, with original charcoal hair RGB.
 pts=[];uv=[];N=40;cx=axis-.012;cz=1.215
 for i in range(N):
  a=i*math.tau/N;rx=.177*(1+.070*math.sin(i*2.7));rz=.192*(1+.055*math.sin(i*3.1));pts.append(Vector((cx+rx*math.cos(a),-.042,cz+rz*math.sin(a))));uv.append(((975+30*math.cos(a))/1672,1-(168+35*math.sin(a))/941))
 me=bpy.data.meshes.new('V007 girl passing back-view drawing');me.from_pydata(pts,[],[tuple(range(N))]);me.update();back=bpy.data.objects.new(me.name,me);rig.users_collection[0].objects.link(back);back.parent=rig;me.materials.append(g['mats']['GIRL']['sleeve']);layer=me.uv_layers.new()
 for lp in me.loops:layer.data[lp.index].uv=uv[lp.vertex_index]
 vg=back.vertex_groups.new(name='head');vg.add(list(range(N)),1,'REPLACE');mod=back.modifiers.new('Original head anchor','ARMATURE');mod.object=rig
 for ob,visible in [(old,lambda f:f<=43),(back,lambda f:44<=f<=45),(mirror,lambda f:f>=46)]:
  for f in range(1,121):ob.hide_render=not visible(f);ob.keyframe_insert('hide_render',frame=f)
  action=ob.animation_data.action;action.name=ob.name+' | head turn drawing exposure';g['stash'](ob,action,'V007 head drawing exposure')
  ob['v007_head_exposure']='source profile1..43; drawn back44..45; original-painted reflected profile46..120'
 return {'method':'Localized native2D head pose exposure: source profile1..43,two-frame charcoal back passing drawing44..45,mirrored original profile46..120 with braid lag. Girl looks down toward boy and offered hand during helping reach.','limit':'Reflected profile is a stylized look-back, not a newly authored three-quarter facial design. The quick turn and neck/shoulder articulation need artistic review at shot size.'}
