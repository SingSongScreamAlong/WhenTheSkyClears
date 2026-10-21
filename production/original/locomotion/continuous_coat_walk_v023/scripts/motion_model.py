"""Continuous bridge of v021 support poses: same step placements, smooth root/hip,
rigid polygon rocker contacts, endpoint-matched swing arcs. No external packages."""
from pathlib import Path
import math,json,numpy as np
import v021_model as M
P=Path(__file__).resolve().parents[1];SOL=json.loads((P/'reference/coherent_pose_solution_v021.json').read_text());POSES=SOL['poses'];PER=31.;STRIDE=SOL['cycle_stride_m'];Q=[p['study_frame_30fps']-1 for p in POSES]
def pchip(xs,ys,x,end_slopes=None):
 n=len(xs);h=[xs[i+1]-xs[i] for i in range(n-1)];d=[(ys[i+1]-ys[i])/h[i] for i in range(n-1)];m=[0.]*n
 for i in range(1,n-1):
  if d[i-1]*d[i]>0:
   w1=2*h[i]+h[i-1];w2=h[i]+2*h[i-1];m[i]=(w1+w2)/(w1/d[i-1]+w2/d[i])
 m[0]=d[0];m[-1]=d[-1]
 if end_slopes:m[0],m[-1]=end_slopes
 i=max(0,min(n-2,next((i for i in range(n-1) if x<=xs[i+1]),n-2)));t=(x-xs[i])/h[i];t=max(0,min(1,t))
 return (2*t**3-3*t*t+1)*ys[i]+(t**3-2*t*t+t)*h[i]*m[i]+(-2*t**3+3*t*t)*ys[i+1]+(t**3-t*t)*h[i]*m[i+1]
def cyclic(vals,q):
 q=q%PER;xs=[x-PER for x in Q]+Q+[x+PER for x in Q];return pchip(xs,vals*3,q)
HIPX=[p['hip_world_xz'][0]-p['root_travel_m'] for p in POSES];HIPZ=[p['hip_world_xz'][1] for p in POSES];PELV=[p['pelvis_rad'] for p in POSES]
OLD=json.loads((P/'reference/v020_eight_pose_matching.json').read_text())
CHEST=[math.radians(p['chest_degrees']) for p in OLD[:8]];HEAD=[math.radians(p['head_degrees']) for p in OLD[:8]]
def stance_angle(s,t):
 if s=='near':xs=[0,2.25,8,9.25,16,16.25,18.5];ys=[POSES[i]['feet'][s]['angle_rad'] for i in [0,1,2,3,4,5]]+[.64]
 else:xs=[0,.25,2.8,15,17.25,19.25];ys=[POSES[4]['feet'][s]['angle_rad'],POSES[5]['feet'][s]['angle_rad'],0,POSES[0]['feet'][s]['angle_rad'],POSES[1]['feet'][s]['angle_rad'],.65]
 return pchip(xs,ys,t)
def stance(s,t,flat):a=stance_angle(s,t);A,meta=M.rolling(s,a,flat);return A,a,meta
def foot(s,q):
 onset=0 if s=='near' else 16.;t=(q-onset)%PER;loop=math.floor((q-onset)/PER);flat=POSES[0 if s=='near' else 4]['feet'][s]['flat_x']+loop*STRIDE;toe=18.5 if s=='near' else 19.25
 if t<=toe:
  A,a,meta=stance(s,t,flat);return {'mode':'CONTACT','A':A,'angle':a,'meta':meta,'clearance':M.sole_clear(s,A,a)}
 # Two original v021 swing poses, relative to this foot's own contact cycle.
 inds=[6,7] if s=='near' else [2,3];times=[24.25,26.25] if s=='near' else [23.,24.25]
 A0,a0,_=stance(s,toe,flat);A1,a1,_=stance(s,0,flat+STRIDE);epsilon=.001
 V0=(stance(s,toe,flat)[0]-stance(s,toe-epsilon,flat)[0])/epsilon;V1=(stance(s,epsilon,flat+STRIDE)[0]-A1)/epsilon
 xs=[toe,*times,PER];As=[A0,*[np.array(POSES[i]['feet'][s]['ankle_xz'])+np.array([loop*STRIDE+(STRIDE if s=='far' else 0),0]) for i in inds],A1]
 A=np.array([pchip(xs,[v[k] for v in As],t,(V0[k],V1[k])) for k in [0,1]])
 pitchxs=[toe,*times,29.75,PER];pitchys=[a0,*[POSES[i]['feet'][s]['angle_rad'] for i in inds],a1-.12,a1]
 av0=(stance_angle(s,toe)-stance_angle(s,toe-epsilon))/epsilon;av1=(stance_angle(s,epsilon)-stance_angle(s,0))/epsilon
 a=pchip(pitchxs,pitchys,t,(av0,av1));u=(t-toe)/(PER-toe);floor=.024*math.sin(math.pi*u)**1.5;clear=M.sole_clear(s,A,a);gap=floor-clear
 # Smooth lower bound, zero at takeoff/landing. Keeps original positive clearances.
 eps=.0008*math.sin(math.pi*u)**2;lift=.5*(gap+math.sqrt(gap*gap+eps*eps));A[1]+=lift
 return {'mode':'SWING','A':A,'angle':a,'meta':{},'clearance':M.sole_clear(s,A,a)}
def evaluate(q):
 D=STRIDE*q/PER;H=np.array([D+cyclic(HIPX,q),cyclic(HIPZ,q)]);pel=cyclic(PELV,q);feet={};angles={};knees={};margins={}
 for s in ['near','far']:
  f=foot(s,q);off=M.rotate(M.v2(M.REST['thigh_'+s]['head'])-M.v2(M.REST['pelvis']['head']),pel);a,K,dist=M.ik(H+off,f['A'],s);feet[s]=f;angles[s]=a;knees[s]=K;margins[s]=sum(M.LENS[s])-dist
 return {'q':q,'D':D,'H':H,'pelvis':pel,'chest':cyclic(CHEST,q),'head':cyclic(HEAD,q),'feet':feet,'angles':angles,'knees':knees,'margins':margins}
if __name__=='__main__':
 rows=[evaluate(i/4) for i in range(249)];bad=[(r['q'],s,v) for r in rows for s,v in r['margins'].items() if v<.0008]
 report={'period_frames_30fps':31,'stride_m':STRIDE,'sample_rate_per_frame':4,'minimum_reach_margin_m':min(v for r in rows for v in r['margins'].values()),'bad_reach_samples':bad,'maximum_clearance_m':max(d['clearance'] for r in rows for d in r['feet'].values()),'minimum_swing_clearance_m':min(d['clearance'] for r in rows for d in r['feet'].values() if d['mode']=='SWING')}
 (P/'evidence/initial_motion_model_check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))

