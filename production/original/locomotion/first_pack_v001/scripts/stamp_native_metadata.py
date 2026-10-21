import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]
rows=[]
for name in ['WTSC_Locomotion_Library_v001.blend','WTSC_Neutral_Walk_Proof_v001.blend','WTSC_Locomotion_Append_Test_v001.blend']:
    p=P/'native'/name;bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False)
    for a in bpy.data.actions:
        blocking=any(x in a.name for x in ['CAUTION_CROUCH','CARE_REACH'])
        a['readiness']='BLOCKING_NOT_PRODUCTION' if blocking else 'CONTACT_RETIME_TESTED_FIRST_PASS'
        if a.asset_data and blocking:a.asset_data.description='BLOCKING ONLY / hidden sleeve redraws and joint cleanup required. '+a.asset_data.description
    for n in ['IMPORT_GUIDE.txt','MOTION_STATUS.txt']:
        t=bpy.data.texts.get(n) or bpy.data.texts.new(n);t.clear();t.write((P/n).read_text())
    bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True)
    rows.append({'file':name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'actions':[{ 'name':a.name,'readiness':a['readiness']} for a in bpy.data.actions],'packed_images':[i.name for i in bpy.data.images if i.packed_file]})
(P/'evidence/final_native_files.json').write_text(json.dumps(rows,indent=2))
print('NATIVE_METADATA_FINALIZED',flush=True)
