import bpy,sys,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];sys.path.insert(0,str(P/'scripts'));import source_match as M;import rig_pose_api as api
bpy.ops.wm.open_mainfile(filepath=str(P/'reference/BASE_CONTROL_ASSET_v017_COPY.blend'),load_ui=False,use_scripts=False);r,c=api.initialize_from_scene();rig=r['BOY'];out=[]
for mapping in [{'near':'R','far':'L'},{'near':'L','far':'R'}]:
 rows=[]
 for p in M.PHASES['phases']:
  v=M.parameters(p['unwrapped_source_frame'],rig,mapping);rows.append({'phase':p['name'],'hip_wanted':list(v['hip_wanted']),'hip_fitted':list(v['hip_fitted']),'hip_reach_correction_m':v['hip_correction_m'],'source_chest_degrees':v['chest_angle']*180/3.14159265,'source_pelvis_degrees':v['pelvis_angle']*180/3.14159265,'source_head_degrees':v['head_angle']*180/3.14159265})
 out.append({'mapping':mapping,'max_correction_m':max(x['hip_reach_correction_m'] for x in rows),'poses':rows,'scale':v['scale'],'stride_m':v['stride_m']})
(P/'evidence/proportion_mapping_comparison.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
