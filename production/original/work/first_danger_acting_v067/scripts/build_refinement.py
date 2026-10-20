"""Continue v066 with contact settling, receiving response, blinks and braid lag."""
import bpy,bmesh,json,math,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parents[1];R=O.parents[1]
SRC=R/'work/first_danger_acting_v066/native/WTSC_First_Danger_Acting_v066.blend';N=O/'native/WTSC_First_Danger_Acting_v067.blend'
BASE=json.loads((R/'work/first_danger_acting_v066/evidence/BUILD.json').read_text());SOURCE_SHA=hashlib.sha256(SRC.read_bytes()).hexdigest();assert SOURCE_SHA==BASE['native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False)
S=bpy.data.scenes[BASE['world_scene']];bpy.context.window.scene=S;S.name='WTSC_FIRST_DANGER_ACTING_WORLD_v067'
RIGS={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']};FRAMES=[913+i*.5 for i in range(335)]
def curves(o):
 ad=getattr(o,'animation_data',None)
 return [f for l in ad.action.layers for st in l.strips for bag in st.channelbags for f in bag.fcurves] if ad and ad.action else []
def clamp(x,a=0.,b=1.):return max(a,min(b,x))
def ease(x):x=clamp(x);return x*x*(3-2*x)
def interp(t,ks):
 if t<=ks[0][0]:return ks[0][1]
 if t>=ks[-1][0]:return ks[-1][1]
 for (a,x),(b,y) in zip(ks,ks[1:]):
  if a<=t<=b:return x+(y-x)*ease((t-a)/(b-a))
def frame(g):S.frame_set(math.floor(g),subframe=g-math.floor(g));bpy.context.view_layer.update()
def axis(a,up=False):a=math.radians(a);return Vector((math.sin(a),0,math.cos(a) if up else -math.cos(a)))
def angle(v,up=True):return math.degrees(math.atan2(v.x,v.z if up else -v.z))
def matrix(r,n,a,b):
 rb=r.data.bones[n];q=(rb.tail_local-rb.head_local).normalized().rotation_difference((b-a).normalized())
 return Matrix.Translation(a)@q.to_matrix().to_4x4()@rb.matrix_local.to_3x3().to_4x4()
def mixdir(a,b,t):
 a0=angle(a,False);a1=angle(b,False);delta=(a1-a0+180)%360-180
 return axis(a0+t*delta)
def ik(H,A,l1,l2):
 d=A-H;L=d.length;assert L<l1+l2-.000001,(L,l1+l2);U=d/max(L,1e-8);x=(l1*l1-l2*l2+L*L)/(2*L);h=math.sqrt(max(0,l1*l1-x*x));p=Vector((-U.z,0,U.x));a=H+U*x+p*h;b=H+U*x-p*h
 return a if a.z<b.z else b
def art():return {i.name:hashlib.sha256(i.packed_file.data).hexdigest() for i in bpy.data.images if i.packed_file}
ART=art();source={}
for g in FRAMES:
 frame(g);dg=bpy.context.evaluated_depsgraph_get();source[g]={}
 for w,r in RIGS.items():
  e=r.evaluated_get(dg);source[g][w]={'world':e.matrix_world.copy(),'bones':{b.name:{'head':b.head.copy(),'tail':b.tail.copy(),'matrix':b.matrix.copy()} for b in e.pose.bones}}
for w,r in RIGS.items():
 r.animation_data.action=r.animation_data.action.copy();r.animation_data.action.name='V067 '+w+' | receive settle and cautious continuation'
 # Preserve the original legs, pelvis and per-child travel exactly.
 for fc in list(curves(r)):
  if any(fc.data_path.startswith('pose.bones["'+n+'"].') for n in ['chest','head','upper_arm_near','forearm_near','hand_near','upper_arm_far','forearm_far','hand_far']):
   for l in r.animation_data.action.layers:
    for st in l.strips:
     for bag in st.channelbags:
      if fc in list(bag.fcurves):bag.fcurves.remove(fc)
LAST={};CACHE={w:{} for w in RIGS};ROWS=[]
for row in BASE['rows']:
 g=row['frame'];frame(g);P={};meta={w:dict(row['children'][w]) for w in RIGS}
 for w,r in RIGS.items():
  old=source[g][w]['bones'];p={n:(b['head'].copy(),b['tail'].copy()) for n,b in old.items()}
  delta=interp(g,[(913,0),(982 if w=='GIRL' else 986,0),(992 if w=='GIRL' else 998,3.5 if w=='GIRL' else 4),(1004 if w=='GIRL' else 1011,-1.8 if w=='GIRL' else -1.2),(1020,0),(1080,0)])
  waist=old['chest']['head'];ca=angle(old['chest']['tail']-waist)+delta;shoulder=waist+axis(ca,True)*r.data.bones['chest'].length
  p['chest']=(waist,shoulder)
  neckgap=(old['head']['head']-old['chest']['tail']).length;hb=shoulder+axis(ca,True)*neckgap
  look=interp(g,[(913,0),(972,0),(980,4 if w=='BOY' else 1),(990,2),(1003,-5 if w=='BOY' else -3),(1014,0),(1080,0)])
  ha=angle(old['head']['tail']-old['head']['head'])+look
  p['head']=(hb,hb+axis(ha,True)*r.data.bones['head'].length)
  # A bent, close guard replaces the stiff forward free hand during the threat.
  guard=interp(g,[(913,0),(960 if w=='GIRL' else 966,0),(977 if w=='GIRL' else 982,1),(995,.8),(1013,.18),(1030,0),(1080,0)])
  up0=(old['upper_arm_far']['tail']-old['upper_arm_far']['head']).normalized();fore0=(old['forearm_far']['tail']-old['forearm_far']['head']).normalized()
  U=mixdir(up0,axis(-16 if w=='GIRL' else -23),guard);F=mixdir(fore0,axis(48 if w=='GIRL' else 66),guard)
  E=shoulder+U*r.data.bones['upper_arm_far'].length;W=E+F*r.data.bones['forearm_far'].length
  p['upper_arm_far']=(shoulder,E);p['forearm_far']=(E,W)
  handold=(old['hand_far']['tail']-old['hand_far']['head']).normalized();handdir=mixdir(handold,axis(38 if w=='GIRL' else 51),guard)
  p['hand_far']=(W,W+handdir*r.data.bones['hand_far'].length)
  P[w]=p;meta[w]['chest_deg']=ca;meta[w]['head_deg']=ha;meta[w]['guard']=guard
 # Both hands share a settled contact centre; the response travels to the boy later.
 oldwrists={w:source[g][w]['world']@source[g][w]['bones']['hand_near']['head'] for w in RIGS}
 center=(oldwrists['BOY']+oldwrists['GIRL'])/2
 settle=interp(g,[(913,0),(981,0),(989,.018),(997,-.010),(1005,.005),(1017,0),(1080,0)])
 center+=Vector((interp(g,[(913,0),(983,0),(992,-.015),(1001,.006),(1015,0),(1080,0)]),0,settle))
 contact=ease((g-978)/14)
 for w,r in RIGS.items():
  old=source[g][w]['bones'];p=P[w];sign=1 if w=='BOY' else -1;world=source[g][w]['world'];H=p['chest'][1]
  goal=center+Vector((-sign*.053,0,-sign*.010));goal.y=oldwrists[w].y
  wrist=world.inverted()@oldwrists[w].lerp(goal,contact)
  # Carry the source offer along with the new shoulder before the grasp settles.
  wrist+=(1-contact)*(H-old['upper_arm_near']['head'])
  l1=r.data.bones['upper_arm_near'].length;l2=r.data.bones['forearm_near'].length
  if (wrist-H).length>l1+l2-.003:wrist=H+(wrist-H).normalized()*(l1+l2-.003)
  E=ik(H,wrist,l1,l2);p['upper_arm_near']=(H,E);p['forearm_near']=(E,wrist)
  d0=(old['hand_near']['tail']-old['hand_near']['head']).normalized();d=mixdir(d0,Vector((sign,0,sign*.16)).normalized(),contact)
  p['hand_near']=(wrist,wrist+d*r.data.bones['hand_near'].length)
  cache={}
  for n,(a,b) in p.items():
   if n in ['pelvis','thigh_near','shin_near','foot_near','thigh_far','shin_far','foot_far']:
    cache[n]={'head':a.copy(),'tail':b.copy(),'matrix':old[n]['matrix'].copy()};continue
   mat=matrix(r,n,a,b);pb=r.pose.bones[n];pb.rotation_mode='QUATERNION';pb.matrix=mat
   k=(w,n)
   if k in LAST and pb.rotation_quaternion.dot(LAST[k])<0:pb.rotation_quaternion.negate()
   LAST[k]=pb.rotation_quaternion.copy()
   for prop in ['location','rotation_quaternion','scale']:pb.keyframe_insert(prop,frame=g)
   cache[n]={'head':a.copy(),'tail':b.copy(),'matrix':mat}
  CACHE[w][g]=cache;meta[w]['hand_wrist_world']=list(world@wrist);meta[w]['grip_settle']=contact
 ROWS.append({'frame':g,'children':meta})
for r in RIGS.values():
 for f in curves(r):
  for k in f.keyframe_points:k.interpolation='LINEAR'

# Refit only the changed sleeve drawings. Native leg drawings remain exactly v066.
sp=importlib.util.spec_from_file_location('model_spec',R/'locomotion/connected_model_fit_v049/scripts/model_spec.py');M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
DRAWINGS=[]
for o in list(S.objects):
 if o.type!='MESH' or o.hide_render or o.parent not in RIGS.values() or o.get('wardrobe_role')!='sleeve':continue
 w='BOY' if 'BOY' in o.name else 'GIRL';side='near' if o.name.endswith('near') else 'far';ys=[v.co.y for v in o.data.vertices];o.shape_key_clear();basis=o.shape_key_add(name='Basis | original painting | G913')
 for g in FRAMES:
  verts=M.limb_vertices(RIGS[w],CACHE[w][g],side,'sleeve',True)
  for i,v in enumerate(verts):v.y=ys[i]
  if g==913:basis.data.foreach_set('co',[c for p in verts for c in p]);o.data.vertices.foreach_set('co',[c for p in verts for c in p])
  key=o.shape_key_add(name='V067 actual sleeve G%06.1f'%g);key.data.foreach_set('co',[c for p in verts for c in p])
  for at in sorted(set([913,max(913,g-.5),g,min(1080,g+.5),1080])):key.value=float(at==g);key.keyframe_insert('value',frame=at)
 for f in curves(o.data.shape_keys):
  for k in f.keyframe_points:k.interpolation='LINEAR'
 DRAWINGS.append(o.name)

# Open hands receive the offer, then close with a softer cupped distal silhouette.
for w,r in RIGS.items():
 o=bpy.data.objects['V060 '+w+' | retained paint hand fold near'];keys=o.data.shape_keys;keys.animation_data_clear()
 cup=o.shape_key_add(name='V067 | cupped palm and grouped fingertips')
 wristz=r.data.bones['hand_near'].head_local.z
 for i,v in enumerate(o.data.vertices):
  p=v.co.copy();d=wristz-p.z;t=ease((d-.028)/.08);p.x*=1-.18*t;p.z+=.006*t*clamp((d-.06)/.04);cup.data[i].co=p
 for g in FRAMES:
  for key in list(keys.key_blocks)[1:]:
   if 'finger fold' in key.name:v=interp(g,[(913,0),(981 if w=='GIRL' else 987,0),(993 if w=='GIRL' else 997,1),(1080,1)])
   elif 'opposed thumb' in key.name:v=interp(g,[(913,0),(965,0),(983,1),(1080,1)])
   elif 'pronation depth' in key.name:v=math.sin(math.pi*interp(g,[(913,0),(965,0),(983,1),(1080,1)]))
   elif key==cup:v=interp(g,[(913,0),(982,0),(996,1),(1080,1)])
   else:v=0
   key.value=v;key.keyframe_insert('value',frame=g)
 for fc in curves(keys):
  for k in fc.keyframe_points:k.interpolation='LINEAR'

# Add resolution to the original flat head meshes for editable local eyelid
# compression. All original pigment/alpha images and interpolated UVs remain.
HEAD_REPORT=[]
for w,r in RIGS.items():
 o=next(o for o in S.objects if o.parent==r and o.get('proportion_role')=='head' and not o.hide_render)
 eye_uv=(335/1254,1-261/1254) if w=='BOY' else (1058/1672,1-216/941)
 o.data.calc_loop_triangles();uv=o.data.uv_layers.active;eye=None
 for tri in o.data.loop_triangles:
  ids=list(tri.vertices);coords=[uv.data[i].uv.copy() for i in tri.loops];a,b,c=coords;v0=b-a;v1=c-a;v2=Vector(eye_uv)-a;den=v0.x*v1.y-v1.x*v0.y
  if abs(den)<1e-12:continue
  t=(v2.x*v1.y-v1.x*v2.y)/den;u=(v0.x*v2.y-v2.x*v0.y)/den
  if t>=-1e-5 and u>=-1e-5 and t+u<=1.00001:eye=o.data.vertices[ids[0]].co*(1-t-u)+o.data.vertices[ids[1]].co*t+o.data.vertices[ids[2]].co*u;break
 assert eye is not None,('Eye registration outside source head',w)
 original=len(o.data.vertices);bm=bmesh.new();bm.from_mesh(o.data)
 if w=='BOY':bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=80,use_grid_fill=True)
 else:
  bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=2,use_grid_fill=True)
 bm.to_mesh(o.data);bm.free();o.data.update()
 o.vertex_groups.clear();group=o.vertex_groups.new(name='head');group.add(list(range(len(o.data.vertices))),1,'REPLACE')
 o.shape_key_add(name='Basis | original painting and silhouette')
 blink=o.shape_key_add(name='V067 | local eyelid close | original paint')
 rx=.017 if w=='BOY' else .014;rz=.013 if w=='BOY' else .012
 for i,v in enumerate(o.data.vertices):
  p=v.co.copy();dx=(p.x-eye.x)/rx;dz=(p.z-eye.z)/rz;influence=math.exp(-(dx**4+dz**4)) if abs(dx)<3 and abs(dz)<3 else 0
  p.z=eye.z+(p.z-eye.z)*(1-.91*influence);blink.data[i].co=p
 schedule=[(913,0),(955,0),(957,1),(959,1),(962,0),(1003,0),(1005,1),(1006,1),(1009,0),(1080,0)] if w=='GIRL' else [(913,0),(964,0),(966,1),(967,1),(970,0),(997,0),(999,1),(1000,1),(1003,0),(1080,0)]
 for g in FRAMES:blink.value=interp(g,schedule);blink.keyframe_insert('value',frame=g)
 if w=='GIRL':
  lag=o.shape_key_add(name='V067 | attached braid follow through');lag.slider_min=-1
  pivot=Vector((-.075,0,1.35))
  for i,v in enumerate(o.data.vertices):
   p=v.co.copy();weight=ease((1.35-p.z)/.17)*ease((-.045-p.x)/.10);q=p-pivot;q=Matrix.Rotation(math.radians(10),3,'Y')@q;lag.data[i].co=p.lerp(pivot+q,weight)
  for g in FRAMES:
   prev=max(913,g-2);before=source[prev]['GIRL']['bones']['head'];now=source[g]['GIRL']['bones']['head'];diff=angle(before['tail']-before['head'])-angle(now['tail']-now['head'])
   lag.value=clamp(diff/10,-1,1);lag.keyframe_insert('value',frame=g)
 for f in curves(o.data.shape_keys):
  for k in f.keyframe_points:k.interpolation='LINEAR'
 o['V067_head_change']='Original painting with local eyelid compression; source UV interpolation retained. No face redesign or card turnaround.'
 HEAD_REPORT.append({'who':w,'source_vertices':original,'candidate_vertices':len(o.data.vertices),'eye_rest_coordinate':list(eye),'blink_schedule':schedule})

S['V067_scope']='Continuation of v066; contact settling, individual upper body and free arms, native blinks and attached braid lag. No full-trailer integration.'
for sc in bpy.data.scenes:
 if sc==S or 'v065' in sc.name or 'V065' in sc.name:sc.render.resolution_x=3840;sc.render.resolution_y=2160;sc.render.resolution_percentage=100
S.timeline_markers.new('RECEIVE | palm closes after contact',frame=994)
assert art()==ART,'Original packed artwork changed'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SOURCE_SHA
frame(994)
out={k:v for k,v in BASE.items() if k not in ['native','native_sha256','source','source_sha256','rows','world_scene']}
out.update({'source':str(SRC),'source_sha256':SOURCE_SHA,'native':str(N),'world_scene':S.name,'rows':ROWS,'drawing_caches':DRAWINGS,'head_changes':HEAD_REPORT,'packed_art_unchanged':True,'original_UVs_unchanged':'Unchanged except interpolated subdivisions of the existing two head meshes; same UV mappings and paintings.','changes':'Coupled contact settle, distinct receiving response, bent close free-arm guard, cupped finger silhouettes, local native blink shapes and attached braid follow-through.','status':'Separate seven-second refinement, user artistic review pending; not integrated.'})
bpy.context.window.scene=S;bpy.ops.wm.save_as_mainfile(filepath=str(N),compress=True);out['native_sha256']=hashlib.sha256(N.read_bytes()).hexdigest()
(O/'evidence/BUILD.json').write_text(json.dumps(out,indent=2,default=str));print('V067_REFINEMENT_SAVED',str(N),flush=True)
