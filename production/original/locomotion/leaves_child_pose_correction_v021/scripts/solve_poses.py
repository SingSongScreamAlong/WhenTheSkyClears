import numpy as np,json,math,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import pose_model as M
lo,hi=M.bounds();x=np.clip(M.initial(),lo,hi);lam=1e-2;history=[]
for it in range(230):
 r=M.residual(x);cost=float(r@r);J=np.empty((len(r),len(x)))
 for j in range(len(x)):
  h=2e-6;xp=x.copy();xm=x.copy();xp[j]+=h;xm[j]-=h;J[:,j]=(M.residual(xp)-M.residual(xm))/(2*h)
 H=J.T@J;g=J.T@r;step=np.linalg.solve(H+lam*np.diag(np.maximum(np.diag(H),1e-4)), -g);candidate=np.clip(x+step,lo,hi);nr=M.residual(candidate);nc=float(nr@nr)
 if nc<cost:
  x=candidate;lam=max(1e-8,lam/2.5)
  if abs(cost-nc)<1e-12 and np.linalg.norm(step)<1e-6:break
 else:lam=min(1e10,lam*5)
 if it%10==0:history.append({'iteration':it,'cost':cost,'lambda':lam})
poses=M.evaluate(x);steps,gains,Hs,sw,pitches=M.unpack(x);shift=-Hs[0,0];rows=[]
for i,(p,src) in enumerate(zip(poses,M.SOURCE)):
 feet={}
 for s,d in p['feet'].items():
  q=dict(d);q['ankle_xz']=[d['ankle_xz'][0]+shift,d['ankle_xz'][1]]
  if 'anchor_xz' in q:q['anchor_xz']=[q['anchor_xz'][0]+shift,q['anchor_xz'][1]];q['flat_x']+=shift
  feet[s]=q
 errors={s:[math.degrees(M.wrap(a-b)) for a,b in zip(p['angles'][s],src['angles'][s])] for s in M.SIDE}
 rows.append({**M.PHASES[i],'hip_world_xz':[p['hip'][0]+shift,p['hip'][1]],'root_travel_m':sum(steps)*(M.PHASES[i]['unwrapped_source_frame']-9.75)/31,'feet':feet,'native_leg_angle_rad':{s:p['angles'][s].tolist() for s in M.SIDE},'leg_direction_residual_deg':errors,'pelvis_rad':src['pelvis'],'source_foot_pitch_deg':{s:math.degrees(src['feet'][s]['angle_rad']) for s in M.SIDE}})
out={'model':'Coherent eight-pose support/pelvis/step retarget. Original native segment lengths and actual boot hulls; no post-fit hip projection.','method':'Bounded32variable sagittal least-squares bridge using numpy; native Blender IK remains final controller. Global alternating step distances, free per-pose pelvisX/Z, foot-rocker gains, and swing joint/pitch adaptation solved together.','variables':x.tolist(),'steps_m':steps.tolist(),'cycle_stride_m':float(sum(steps)),'heel_toe_roll_gains':gains.tolist(),'first_hip_x_origin_shift_m':float(shift),'max_leg_direction_error_deg':max(abs(e) for r in rows for a in r['leg_direction_residual_deg'].values() for e in a),'min_swing_clearance_m':min(d['clearance_m'] for r in rows for d in r['feet'].values() if d['mode']=='SWING'),'hip_heights_m':Hs[:,1].tolist(),'iterations':it+1,'cost':float(M.residual(x)@M.residual(x)),'history':history,'poses':rows,'limitation':'These are eight poses only; source reference angles and proportions differ, so residuals and foot-pitch adaptations are explicit. No continuous animation or artistic approval.'}
(P/'evidence/coherent_pose_solution.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['poses','variables','history']}));print('perPose',[(r['name'],r['hip_world_xz'],r['leg_direction_residual_deg'],[(s,round(d['clearance_m']*1000,2),round(math.degrees(d['angle_rad']),2)) for s,d in r['feet'].items()]) for r in rows])
