"""V018 boy-only travelling capability exercise. No frame handler or external rig.
The original rigid boots roll on their measured lower polygon vertices.
"""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api
STEP=.22;PERIOD=24.;END=49;RATE=24
def ease(x):return x*x*(3-2*x)
def curve(q,keys):
 for (a,x),(b,y) in zip(keys,keys[1:]):
  if a<=q<=b:return x+(y-x)*ease((q-a)/(b-a))
 return keys[0][1] if q<keys[0][0] else keys[-1][1]
def periodic_hips(f):
 # Fixed source limbs have unequal drawn lengths. A modest asymmetric hip
 # path stays inside both reach envelopes; no scaling/stretch compensation.
 z=[.602,.590,.610,.613,.590,.580,.602,.608];q=(f-1)%24;i=int(q//3);u=(q-i*3)/3;j=(i+1)%8
 m0=(z[j]-z[(i-1)%8])/6;m1=(z[(i+2)%8]-z[i])/6
 Z=(2*u**3-3*u*u+1)*z[i]+(u**3-2*u*u+u)*3*m0+(-2*u**3+3*u*u)*z[j]+(u**3-u*u)*3*m1
 return Vector((.018+.007*math.sin(2*math.pi*(f-1)/12-.3),0,Z))
def travel(f):return (f-1)*2*STEP/PERIOD
def contact_frame(f,side):
 offset=1 if side=='near' else 13
 return offset+math.floor((f-offset)/PERIOD+1e-9)*PERIOD
def pitch(q):return math.radians(curve(q,[(0,-4),(3,0),(9,0),(14,8)]))
def inv_pitch(p):
 lo,hi=(0.,3.) if p<0 else (9.,14.)
 for i in range(55):
  mid=(lo+hi)/2
  if pitch(mid)<p:lo=mid
  else:hi=mid
 return (lo+hi)/2
def foot_recipe(rig,side):
 ob=next(o for o in rig.children if o.get('v007_role')=='support_boot' and o.name.endswith(side));b=rig.data.bones['foot_'+side];d=api.FEET['BOY_'+side]
 A=b.head_local;rot=Matrix.Rotation(d['flatten_angle'],4,'Y');v=[ob.matrix_local@x.co for x in ob.data.vertices];h=[rot@(x-A) for x in v];low=min(x.z for x in h)
 flat=Matrix.Translation((0,0,-low))@rot@Matrix.Translation(-A)@b.matrix_local;v=[flat@b.matrix_local.inverted()@x for x in v]
 # Determine the actual support polygon at the deliberately bounded rocker
 # range. Solve each transition exactly from its edge slope.
 indices=[]
 for i in range(2401):
  a=math.radians(-4+i*.005);j=min(range(len(v)),key=lambda j:-math.sin(a)*v[j].x+math.cos(a)*v[j].z)
  if not indices or indices[-1]!=j:indices.append(j)
 contacts=[];anchor=None
 for i,j in enumerate(indices):
  pv=v[j]
  if i==0:ang=math.radians(-4);anchor=Vector((pv.x,pv.y,0));q=0
  else:
   prev=v[indices[i-1]];ang=math.atan2(pv.z-prev.z,pv.x-prev.x);q=inv_pitch(ang) if abs(ang)>1e-6 else 9.
   anchor=anchor+Matrix.Rotation(ang,4,'Y')@(pv-prev);anchor.z=0
  contacts.append({'vertex':j,'point':list(pv),'anchor':list(anchor),'from_pitch':ang,'from_phase':q})
 return {'object':ob.name,'flat_bone':[list(x) for x in flat],'vertices':[list(x) for x in v],'contacts':contacts}
def state(f,side,recipes):
 C=contact_frame(f,side);q=f-C;land=travel(C)+STEP/2;d=recipes[side];flat=Matrix(d['flat_bone']);V=[Vector(v) for v in d['vertices']]
 if q<=14+1e-9:
  a=pitch(q);active=0
  for i,k in enumerate(d['contacts']):
   if q>=k['from_phase']-1e-8:active=i
  c=d['contacts'][active];pv=Vector(c['point']);anchor=Vector(c['anchor'])+Vector((land,0,0));M=Matrix.Translation(anchor)@Matrix.Rotation(a,4,'Y')@Matrix.Translation(-pv)@flat
  mode='HEEL' if q<3 else ('SOLE' if q<9 else 'FOREFOOT')
  return M,{'contact_frame':C,'phase':q,'mode':mode,'vertex':c['vertex'],'anchor':list(anchor),'pitch':a,'land_ankle_x':land,'clearance_target':0.}
 a=math.radians(curve(q,[(14,8),(16,10),(18,2),(21,-4),(24,-4)]));lift=curve(q,[(14,0),(15,.025),(17,.055),(19,.052),(22,.018),(24,0)])
 last=d['contacts'][-1];start=Matrix.Translation(Vector(last['anchor'])+Vector((land,0,0)))@Matrix.Rotation(math.radians(8),4,'Y')@Matrix.Translation(-Vector(last['point']))@flat
 first=d['contacts'][0];end=Matrix.Translation(Vector(first['anchor'])+Vector((land+2*STEP,0,0)))@Matrix.Rotation(math.radians(-4),4,'Y')@Matrix.Translation(-Vector(first['point']))@flat
 u=(q-14)/10;x=start.translation.x+(end.translation.x-start.translation.x)*ease(u)
 rot=Matrix.Rotation(a,4,'Y');bone_rot=rot@flat.to_3x3().to_4x4();rel=[rot@(v-flat.translation) for v in V];z=lift-min(v.z for v in rel)
 M=bone_rot;M.translation=Vector((x,0,z))
 return M,{'contact_frame':C,'phase':q,'mode':'SWING','vertex':None,'anchor':None,'pitch':a,'land_ankle_x':land,'clearance_target':lift}
def empty(name,collection,parent=None):
 o=bpy.data.objects.new(name,None);collection.objects.link(o);o.parent=parent;o.empty_display_size=.03;return o
def ensure_placement():
 pack=bpy.data.collections['WTSC_BOY_TRAVELLING_WALK_v018'];name='V018 | EXERCISE_PLACEMENT | move whole study'
 if name in bpy.data.objects:return bpy.data.objects[name]
 placement=empty(name,pack);placement['contract']='Parent of travel and world-contact goals. Move/rotate this object to place the entire study; do not independently shift locked goals.'
 for o in list(pack.all_objects):
  if o!=placement and o.parent is None:o.parent=placement
 return placement
def iter_fc(o):
 if o.animation_data and o.animation_data.action:
  for l in o.animation_data.action.layers:
   for st in l.strips:
    for bag in st.channelbags:
     for fc in bag.fcurves:yield fc
def interpolation(o,kind='LINEAR'):
 for fc in iter_fc(o):
  for k in fc.keyframe_points:k.interpolation='CONSTANT' if 'pole_angle' in fc.data_path or fc.data_path.startswith('["') else kind
def material(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;n=m.node_tree.nodes;n.clear();e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*color,1);out=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],out.inputs['Surface']);return m
def line(name,pts,mat,col,r=.002):
 cr=bpy.data.curves.new(name,'CURVE');cr.dimensions='3D';cr.bevel_depth=r;cr.bevel_resolution=0;sp=cr.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,v in zip(sp.points,pts):p.co=(*v,1)
 o=bpy.data.objects.new(name,cr);col.objects.link(o);o.data.materials.append(mat);return o
def setup():
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/'characters/rig_correctives_v017/native/WTSC_Painted_Rig_Control_Asset_v017.blend'),load_ui=False,use_scripts=False);S=bpy.context.scene
 for o in list(bpy.data.objects):
  if 'GIRL' in o.name:bpy.data.objects.remove(o,do_unlink=True)
 r,c=api.initialize_from_scene();rig=r['BOY'];T=rig.parent;T.matrix_world=Matrix.Identity(4);T.name='V018 | WORLD_TRAVEL | +X metres';rig.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update()
 pack=bpy.data.collections['WTSC_PAINTED_RIG_CORRECTIVES_v017'];pack.name='WTSC_BOY_TRAVELLING_WALK_v018';col=bpy.data.collections.new('V018 | WORLD_CONTACTS_AND_MARKERS');pack.children.link(col)
 for o in bpy.data.objects:
  if o.animation_data:
   o.animation_data.action=None
   for tr in list(o.animation_data.nla_tracks):o.animation_data.nla_tracks.remove(tr)
 for a in list(bpy.data.actions):bpy.data.actions.remove(a)
 recipes={s:foot_recipe(rig,s) for s in ['near','far']};(P/'evidence/actual_sole_pivots.json').write_text(json.dumps(recipes,indent=2))
 floor=material('V018 | warm graphite ground',(.35,.34,.30));tick=material('V018 | ground markers',(.60,.59,.55));line('Fixed ground', [(-1,-.09,0),(2,-.09,0)],floor,col)
 for i in range(-3,9):
  x=i*STEP;line('GROUND %.2fm'%x,[(x,-.09,-.008),(x,-.09,-.045)],tick,col,.0014)
  cr=bpy.data.curves.new('World distance','FONT');cr.body='%.2f'%x;cr.size=.027;cr.align_x='CENTER';ob=bpy.data.objects.new('LABEL %.2f'%x,cr);col.objects.link(ob);ob.rotation_euler=(math.pi/2,0,0);ob.location=(x,-.10,-.084);cr.materials.append(floor)
 cam=bpy.data.objects.new('V018 | INSPECTION fixed ground camera',bpy.data.cameras.new('V018 inspection'));col.objects.link(cam);cam.location=(.44,-7,.745);cam.rotation_euler=(Vector((.44,0,.745))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.25;S.camera=cam
 S.world.color=(.75,.73,.68);S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.88,.85,.78,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.8
 S.render.engine='BLENDER_EEVEE'
 if hasattr(S.eevee,'taa_render_samples'):S.eevee.taa_render_samples=32
 S.view_settings.view_transform='Standard';S.view_settings.look='None';S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100;S.render.film_transparent=False;S.render.image_settings.file_format='PNG';S.render.fps=RATE;S.frame_start=1;S.frame_end=48
 rig['exercise_status']='V018 capability test; artistic approval NOT PASSED; no production integration';S['V018_scope']='Boy original profile; original v017 paint/geometry/lengths. World-ground walk capability test only.'
 return S,rig,T,col,recipes
def body_pose(f,rig,T,recipes,overlap=False,direct_feet=True):
 T.location=(travel(f),0,0);bpy.context.view_layer.update();q=(f-1)%12
 H=periodic_hips(f)
 pelvic=math.radians(1.2*math.sin(2*math.pi*(f-1)/24));rest=rig.data.bones;pel=rest['pelvis'].matrix_local
 api.target('BOY','HIP',Matrix.Translation(H)@Matrix.Rotation(pelvic,4,'Y')@Matrix.Translation(-pel.translation)@pel)
 lag=1 if overlap else 0;chest=math.radians(3+1.2*math.sin(2*math.pi*(f-1-lag)/12));cd=Matrix.Translation(H)@Matrix.Rotation(chest,4,'Y')@Matrix.Translation(-pel.translation)
 api.target('BOY','CHEST',cd@rest['chest'].matrix_local);hd=math.radians(.6+.7*math.sin(2*math.pi*(f-1-(2 if overlap else 0))/12));h0=cd@rest['head'].matrix_local
 api.target('BOY','HEAD_PROFILE',Matrix.Translation(h0.translation)@Matrix.Rotation(hd-chest,4,'Y')@Matrix.Translation(-h0.translation)@h0)
 for side in ['near','far']:
  M,info=state(f,side,recipes)
  if direct_feet:api.set_world_foot_matrix('BOY',side,M)
  A=rig.matrix_world.inverted()@M.translation;api.target('BOY','LEG_POLE_'+side,Matrix.Translation((H.x+1,0,(H.z+A.z)/2)))
 bpy.context.view_layer.update()
 for side,sign,amp in [('near',-1,18),('far',1,16)]:
  S=rig.pose.bones['upper_arm_'+side].head;upper=math.radians(sign*amp*math.cos(2*math.pi*(f-1)/24));fore=math.radians(sign*amp*math.cos(2*math.pi*(f-1-(1.5 if overlap else 0))/24)+25)
  Lu=rest['upper_arm_'+side].length;Ll=rest['forearm_'+side].length;E=S+Vector((Lu*math.sin(upper),0,-Lu*math.cos(upper)));W=E+Vector((Ll*math.sin(fore),0,-Ll*math.cos(fore)))
  api.set_wrist('BOY',side,W.x,W.z,math.degrees(fore)-90,'Relax',fit_reach=False);api.CONTROLS['BOY','WRIST_'+side]['FrontLayer']=0.
  pole=E+(E-(S+W)/2)*4;api.target('BOY','ARM_POLE_'+side,Matrix.Translation(pole))
 api.choose_planes('BOY',{});bpy.context.view_layer.update()
def evaluated_points(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [e.matrix_world@v.co for v in e.data.vertices]
def validate(f,rig,recipes):
 row={'frame':f,'travel_m':travel(f),'reach':api.reach_report(),'feet':{}}
 for side in ['near','far']:
  ob=bpy.data.objects[recipes[side]['object']];V=evaluated_points(ob);M,info=state(f,side,recipes);info['minimum_sole_z_m']=min(v.z for v in V);info['ankle_goal_error_m']=(api.CONTROLS['BOY','ANKLE_'+side].matrix_world.translation-M.translation).length
  if info['vertex'] is not None:info['active_contact_error_m']=(V[info['vertex']]-Vector(info['anchor'])).length
  info['clearance_error_m']=abs(info['minimum_sole_z_m']-info['clearance_target']);row['feet'][side]=info
 row['finite_meshes']=all(math.isfinite(c) for o in rig.children if o.type=='MESH' for v in evaluated_points(o) for c in v)
 return row
