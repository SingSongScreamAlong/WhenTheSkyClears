import hashlib,json,shutil,datetime
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');O=R/'locomotion/garment_continuity_v047';D=O/'reference';D.mkdir(exist_ok=True)
S=R/'locomotion/painted_outfit_restoration_v046/native/WTSC_Age10_Painted_Outfit_Restoration_v046.blend';P=D/'PRESERVED_v046_INPUT.blend';assert not P.exists()
a=S.read_bytes();h=hashlib.sha256(a).hexdigest();P.write_bytes(a);h2=hashlib.sha256(S.read_bytes()).hexdigest();assert h==h2,'Source changed during read; do not use snapshot.'
meta={'snapshot_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'original_source':str(S),'original_modified_utc':datetime.datetime.fromtimestamp(S.stat().st_mtime,datetime.timezone.utc).isoformat(),'snapshot':str(P),'sha256':h,'input_unchanged_during_capture':True,'policy':'Source remains actively authored elsewhere; all continuation uses this owned immutable snapshot. Do not overwrite the external v046 branch.'}
(O/'evidence/INPUT_SNAPSHOT.json').write_text(json.dumps(meta,indent=2))
old=O/'evidence/NATIVE_SOURCE_INSPECTION.json';shutil.copy2(old,O/'evidence/INITIAL_SOURCE_INSPECTION_SUPERSEDED.json')
script=O/'scripts/inspect_source.py';t=script.read_text();t=t.replace("P=R/'locomotion/painted_outfit_restoration_v046/native/WTSC_Age10_Painted_Outfit_Restoration_v046.blend'","P=O/'reference/PRESERVED_v046_INPUT.blend'");assert "P=O/'reference/PRESERVED_v046_INPUT.blend'" in t;script.write_text(t)
print('IMMUTABLE_INPUT_CAPTURED',json.dumps(meta),flush=True)
