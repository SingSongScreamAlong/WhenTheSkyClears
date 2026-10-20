from pathlib import Path
import json
P=Path(__file__).resolve().parents[1]
A=json.loads((P/'evidence/NATIVE_SCALE_AUDIT.json').read_text())
M=json.loads((P/'evidence/RENDERED_SCALE_METRICS.json').read_text())
out={}
for v,a in A.items():
 r={k:a[k] for k in ['fps','unit_system','unit_scale_length','rig_scale','root_scale','rig_world_scale']}
 r['bone_lengths']={k:x['rest_length'] for k,x in a['bones'].items()}
 r['camera_matrix_diff_F1']={c:M['camera_comparison'][c]['matrix_max_difference_at_F1'][v] for c in a['camera_data']}
 r['relevant_parts']={}
 for n,b in a['frames']['1']['parts'].items():
  if any(w in n for w in ['painted boy profile','PAINT body','folded linen','coherent charcoal','articulated drawn hand']):
   r['relevant_parts'][n]={'bbox_scene':b['world_geometry_bbox_including_transparent_canvas'],'bbox_close_pixels':b['close_projected_geometry_pixels']}
 r['hands']=M['versions'][v]['hands'];r['boots']=M['versions'][v]['boots'];out[v]=r
(P/'evidence/COMPACT_NATIVE_PROPORTIONS.json').write_text(json.dumps(out,indent=2))
for v,r in out.items():
 print(v, json.dumps(r))
