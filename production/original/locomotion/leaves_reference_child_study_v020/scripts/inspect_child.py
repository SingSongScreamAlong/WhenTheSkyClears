import bpy,json,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api
bpy.ops.wm.open_mainfile(filepath=str(P/'reference/BASE_CONTROL_ASSET_v017_COPY.blend'),load_ui=False,use_scripts=False);r,c=api.initialize_from_scene();rig=r['BOY'];d={b.name:{'head':list(b.head_local),'tail':list(b.tail_local),'length':b.length,'matrix':[list(row) for row in b.matrix_local]} for b in rig.data.bones};(P/'evidence/child_rest_bones.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
