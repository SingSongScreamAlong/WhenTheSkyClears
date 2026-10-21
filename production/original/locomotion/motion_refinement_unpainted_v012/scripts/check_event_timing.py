"""Measure the actual authored/evaluated route, not just desired pose keys."""
import csv,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((P/'evidence/world_motion_samples.csv').open()))
r={(x['character'],int(x['frame'])):x for x in rows}
targets=json.loads((P/'evidence/joint_targets.json').read_text());out={}
keys=[24,26,29,33,36,40,44,53,62,66,69,70,74,78,83,94,139,144]
for who in ['BOY','GIRL']:
 out[who]={'actual_event_min':min(((f,float(r[who,f]['hip_z'])) for f in range(24,45)),key=lambda x:x[1]),'samples':{f:{k:float(r[who,f][k]) for k in ['root_x','hip_z','desired_hip_z']} for f in keys}}
out['boy_preload_upward_pairs']=[f for f in range(24,40) if float(r['BOY',f+1]['hip_z'])>float(r['BOY',f]['hip_z'])+1e-5]
out['boy_blocked_toe_x_span_m']=max(targets['BOY'][str(f)]['feet']['far']['toe'][0] for f in range(24,31))-min(targets['BOY'][str(f)]['feet']['far']['toe'][0] for f in range(24,31))
out['boy_heel_z_at26_m']=targets['BOY']['26']['feet']['far']['heel'][2]
out['boy_forward_travel_during_toe_block_m']=float(r['BOY',30]['root_x'])-float(r['BOY',24]['root_x'])
out['girl_restart_max_reach_limit_lowering_m']=max(float(r['GIRL',f]['desired_hip_z'])-float(r['GIRL',f]['hip_z']) for f in range(62,84))
out['girl_restart_min_actual_hip_m']=min(float(r['GIRL',f]['hip_z']) for f in range(62,84))
out['scope']='Technical timing/support evidence only. Actual hip-Z includes leg-reach limiting. No naturalism, force/dynamics, collision-solve or repaint approval claim.'
assert out['BOY']['actual_event_min'][0]==40 and out['GIRL']['actual_event_min'][0]==29
assert not out['boy_preload_upward_pairs']
assert out['boy_blocked_toe_x_span_m']<1e-6 and out['boy_heel_z_at26_m']>.18
assert out['boy_forward_travel_during_toe_block_m']>.15
# Desired extension is allowed to exceed the support arc; do not certify that
# arbitrary target as physically necessary. Guard the actual deep sag instead.
assert out['girl_restart_min_actual_hip_m']>.60
assert all(float(r[w,144]['hip_z'])>.60 for w in ['BOY','GIRL'])
(P/'evidence/event_timing_check.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k not in ['BOY','GIRL']},indent=2))
