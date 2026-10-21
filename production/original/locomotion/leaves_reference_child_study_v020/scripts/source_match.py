import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
DATA=json.loads((P/'evidence/fbx_source_inspection.json').read_text());ROWS={round(r['frame'],6):r for r in DATA['samples']};PHASES=json.loads((P/'reference/SOURCE_PHASE_TIMING_v020.json').read_text());BOOTS=json.loads((P/'reference/ORIGINAL_BOY_BOOT_PIVOTS_v018.json').read_text())
PERIOD=31.;FIRST=9.75;ROOT_START=-ROWS[FIRST]['bones']['Root']['head'][1]
def sample(f):
 loop=math.floor((f-2)/PERIOD);w=2+(f-2)%PERIOD;a=math.floor(w*4)/4;b=min(33,a+.25);u=(w-a)/.25
 return {n:{end:Vector(ROWS[a]['bones'][n][end]).lerp(Vector(ROWS[b]['bones'][n][end]),u)+Vector((0,-loop*1.5,0)) for end in ['head','tail']} for n in DATA['bones']}
def point(B,n,end='head'):
 v=B[n][end];return Vector((-v.y,0,v.z))
def angle(a,b):d=b-a;return math.atan2(d.x,d.z)
def foot_angle(B,side):
 a=point(B,'Ankle_'+side);t=point(B,'Toes_'+side);flat=sample(12 if side=='R' else 28);fa=point(flat,'Ankle_'+side);ft=point(flat,'Toes_'+side)
 return -(math.atan2(t.z-a.z,t.x-a.x)-math.atan2(ft.z-fa.z,ft.x-fa.x))
def rolling(side,theta,flat_x):
 d=BOOTS[side];V=[Vector(v) for v in d['vertices']];flat=Matrix(d['flat_bone']);direction=1 if theta>=0 else -1;eps=direction*1e-6
 def active(a):R=Matrix.Rotation(a,4,'Y');return min(range(len(V)),key=lambda i:(R@V[i]).z)
 idx=active(eps);pivot=V[idx];anchor=Vector((flat_x+pivot.x,pivot.y,0));last=idx;switch=[]
 for k in range(1,1001):
  a=theta*k/1000;i=active(a)
  if i!=last:
   dv=V[i]-V[last];edge=math.atan2(dv.z,dv.x)
   while edge>math.pi/2:edge-=math.pi
   while edge<-math.pi/2:edge+=math.pi
   anchor+=Matrix.Rotation(edge,4,'Y')@dv;anchor.z=0;switch.append({'angle':edge,'from':last,'to':i});last=i
 pivot=V[last];M=Matrix.Translation(anchor)@Matrix.Rotation(theta,4,'Y')@Matrix.Translation(-pivot)@flat
 return M,{'active_vertex':last,'pivot_flat':list(pivot),'anchor':list(anchor),'angle_rad':theta,'flat_ankle_reference_x_m':flat_x,'successive_polygon_edges':switch}
def foot_goal(f,src_side,native_side,k):
 B=sample(f);C=(9.75 if src_side=='R' else 25.75)+math.floor((f-(9.75 if src_side=='R' else 25.75))/PERIOD+1e-8)*PERIOD
 flatf=(12 if src_side=='R' else 28)+(C-(9.75 if src_side=='R' else 25.75));off=(28.25 if src_side=='R' else 45.)+(C-(9.75 if src_side=='R' else 25.75))
 # Left contact25.75 lifts at45 (=wrapped14+31); right at28.25.
 flat_x=(point(sample(flatf),'Ankle_'+src_side).x-ROOT_START)*k;theta=foot_angle(B,src_side)
 if f<=off+1e-8:
  M,meta=rolling(native_side,theta,flat_x);meta.update({'mode':'CONTACT_POLYGON_PIVOT','source_contact':C,'source_toeoff':off,'source_side':src_side});return M,meta
 d=BOOTS[native_side];flat=Matrix(d['flat_bone']);V=[Vector(v) for v in d['vertices']];rot=Matrix.Rotation(theta,4,'Y');clearance=max(0,min(point(B,'Ball_'+src_side).z,point(B,'Toes_'+src_side).z)+.003)*k
 rel=[rot@(v-flat.translation) for v in V];M=rot@flat.to_3x3().to_4x4();M.translation=Vector(((point(B,'Ankle_'+src_side).x-ROOT_START)*k,0,clearance-min(v.z for v in rel)))
 return M,{'mode':'SWING','source_contact':C,'source_toeoff':off,'source_side':src_side,'angle_rad':theta,'clearance_m':clearance}
def fit_hip(H,ankles,offsets,lengths):
 # Closest point in the intersection of the two fixed-length reach discs.
 x=H.copy();corr=[Vector((0,0,0)),Vector((0,0,0))]
 for it in range(300):
  old=x.copy()
  for i,s in enumerate(['near','far']):
   y=x+corr[i];center=ankles[s]-offsets[s];D=y-center;limit=lengths[s]-.003;z=center+D*(min(1,limit/max(1e-8,D.length)));corr[i]=y-z;x=z
  if (x-old).length<1e-8:break
 return x
def parameters(f,rig,mapping):
 B=sample(f);native_mean=sum(rig.data.bones['thigh_'+s].length+rig.data.bones['shin_'+s].length for s in ['near','far'])/2
 source_mean=sum(DATA['bones']['UpperLeg_'+s]['length']*.01+DATA['bones']['LowerLeg_'+s]['length']*.01 for s in ['R','L'])/2;k=native_mean/source_mean
 pel=angle(point(B,'Hips'),point(B,'Spine_01'));rot=Matrix.Rotation(pel,4,'Y');rest=rig.data.bones;off={s:rot@(rest['thigh_'+s].head_local-rest['pelvis'].head_local) for s in ['near','far']};srcH=(point(B,'UpperLeg_L')+point(B,'UpperLeg_R'))/2
 flat_source_z=(point(sample(12),'Ankle_R').z+point(sample(28),'Ankle_L').z)/2;flat_native_z=sum(Matrix(BOOTS[s]['flat_bone']).translation.z for s in ['near','far'])/2;zero=flat_native_z-flat_source_z*k
 meanoff=(off['near']+off['far'])/2;wanted=Vector(((srcH.x-ROOT_START)*k,0,srcH.z*k+zero))-meanoff
 foot={s:foot_goal(f,mapping[s],s,k) for s in ['near','far']};ankle={s:foot[s][0].translation for s in foot};lengths={s:rest['thigh_'+s].length+rest['shin_'+s].length for s in foot};H=fit_hip(wanted,ankle,off,lengths)
 chest=angle(point(B,'Spine_01'),point(B,'Neck'));head=angle(point(B,'Head'),point(B,'Head','tail'))
 return {'source':B,'scale':k,'stride_m':1.5*k,'root_travel_m':(point(B,'Root').x-ROOT_START)*k,'hip_wanted':wanted,'hip_fitted':H,'hip_correction_m':(H-wanted).length,'pelvis_angle':pel,'chest_angle':chest,'head_angle':head,'foot':foot,'offsets':off}
