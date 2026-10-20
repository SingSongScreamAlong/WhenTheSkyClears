import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];FILE=ROOT/'locomotion/steady_walk_baseline_v047/native/WTSC_Steady_Ordinary_Walk_v047.blend';before=hashlib.sha256(FILE.read_bytes()).hexdigest();assert before=='29a4d9f794187602af43f7349f2b01c1019f39cba9f1d1278b966b78d1770103';bpy.ops.wm.open_mainfile(filepath=str(FILE),load_ui=False,use_scripts=False);ART=bpy.data.collections['V044 | age10 editable profile anatomy'];out={'source':str(FILE),'source_sha256':before,'characters':{}}
for who in ['BOY','GIRL']:
 r=bpy.data.objects['V044 '+who+' | estimated joint centres'];b=next(o for o in ART.objects if o.parent==r and o.get('proportion_role')=='boot' and o.name.endswith('near'));ankle=r.data.bones['foot_near'].head_local.z;out['characters'][who]={'thigh_m':r.data.bones['thigh_near'].length,'shin_m':r.data.bones['shin_near'].length,'hip_rest_z_m':r.data.bones['pelvis'].head_local.z,'boot_offsets':[[v.co.x,0,v.co.z-ankle] for v in b.data.vertices]}
assert hashlib.sha256(FILE.read_bytes()).hexdigest()==before;(P/'evidence/SUPPORT_GEOMETRY.json').write_text(json.dumps(out,indent=2));print('V048_READ_ONLY_SUPPORT_GEOMETRY_EXPORTED')
