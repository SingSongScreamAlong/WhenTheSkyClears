from pathlib import Path
import json,re
P=Path(__file__).resolve().parents[1];A=json.loads((P/'evidence/BOTH_CHARACTERS_AND_WORLD_NATIVE.json').read_text());out={}
for c in ['boy_v041','pair_v007']:
 print(c)
 for g in A['cases'][c]['rigs']:
  B=g['rest_bones'];H=g['properties']['height_m'];row={'nominal_height_m':H,'rig_name':g['name'],'rest_segments_m':{n:B[n]['length'] for n in ['head','chest','upper_arm_near','forearm_near','upper_arm_far','forearm_far','hand_near','thigh_near','shin_near','thigh_far','shin_far','foot_near','foot_far']}}
  for limb,p,q in [('arm','upper_arm','forearm'),('leg','thigh','shin')]:
   near=B[p+'_near']['length']+B[q+'_near']['length'];far=B[p+'_far']['length']+B[q+'_far']['length'];row[limb]={'near_total_m':near,'far_total_m':far,'far_relative_to_near_percent':100*(far/near-1),'near_total_over_nominal_height':near/H}
  row['nominal_height_over_head_bone_length_NOT_anatomical_head_count']=H/B['head']['length'];out[c+'_'+g['name']]=row;print(json.dumps(row))
 for o in A['cases'][c]['object_inventory']:
  if re.search('head|braid|sole|floor',o['name'],re.I) and o['type'] in ['MESH','GREASEPENCIL']:print('PART',o['name'],o['type'],o['dimensions'],o['hide_render'])
(P/'evidence/CURRENT_SEGMENT_MEASUREMENTS.json').write_text(json.dumps(out,indent=2))
