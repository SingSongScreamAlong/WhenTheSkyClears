"""Inspect whole coordinated support paths before materializing a candidate."""
import json,math
from pathlib import Path
import numpy as np
import motion_spec as M
P=Path(__file__).resolve().parents[1];data=json.loads((P/'evidence/SUPPORT_GEOMETRY.json').read_text());M.configure(data['characters']);rows={w:[] for w in M.CHAR};summary={}
for who in M.CHAR:
 l1=M.CHAR[who]['thigh_m'];l2=M.CHAR[who]['shin_m'];margin=99
 for i in range(257):
  f=1+i/8;g=f+M.PHASE[who];H=M.hip(g,who);row={'frame':f,'hip':H.tolist(),'posture':M.posture(g,who),'feet':{}}
  for side in ['near','far']:
   A,beta,meta=M.foot(g,who,side);reach=l1+l2-float(np.linalg.norm(A-H));margin=min(margin,reach);row['feet'][side]={'ankle':A.tolist(),'knee_flex_deg':M.knee_angle(H,A,who),'beta_deg':math.degrees(beta),'reach_margin_m':reach,**meta}
  rows[who].append(row)
 summary[who]={'min_reach_margin_m':margin,'hip_z_range_m':float(np.ptp([r['hip'][2] for r in rows[who]])),'legs':{}}
 for side in ['near','far']:
  vals=np.array([r['feet'][side]['knee_flex_deg'] for r in rows[who]]);rate=np.diff(vals)*8;early=[r for r in rows[who] if r['feet'][side]['stance'] and r['feet'][side]['phase_frame']<=4.5];swing=[r for r in rows[who] if not r['feet'][side]['stance'] and r['feet'][side]['swing_u']<=.4]
  summary[who]['legs'][side]={'max_knee_rate_deg_per_source_frame':float(np.max(abs(rate))),'loading_knee_min_max_deg':[min(r['feet'][side]['knee_flex_deg'] for r in early),max(r['feet'][side]['knee_flex_deg'] for r in early)],'early_swing_knee_min_max_deg':[min(r['feet'][side]['knee_flex_deg'] for r in swing),max(r['feet'][side]['knee_flex_deg'] for r in swing)]}
report={'summary':summary,'rows':rows,'scope':'Construction feasibility and actual support-geometry planning. Not a physical COM simulation or artistic acceptance.'};(P/'evidence/LOADING_PATH_PLAN.json').write_text(json.dumps(report,indent=2));print(json.dumps(summary,indent=2));assert all(v['min_reach_margin_m']>.0001 for v in summary.values()),'Authored path exceeds leg reach; revise the path, not frame-dependent pelvis caps.'
