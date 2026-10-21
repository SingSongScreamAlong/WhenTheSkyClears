from pathlib import Path
import hashlib,shutil,json,datetime
S=Path(r'WTSC_LOCAL_WORKSPACE\locomotion\painted_outfit_restoration_v046\native\WTSC_Age10_Painted_Outfit_Restoration_v046.blend')
O=Path(r'WTSC_LOCAL_WORKSPACE\locomotion\garment_continuity_v047')/'current_v046_continuation'
for sub in ['native','evidence','previews','reference']: (O/sub).mkdir(parents=True,exist_ok=True)
D=O/'reference/PRESERVED_FINAL_v046_INPUT.blend'
assert not D.exists(),'Do not replace an existing preserved input.'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=h(S);st=S.stat();shutil.copy2(S,D);after=h(S);copied=h(D)
assert before==after==copied,'Concurrent source change; do not proceed.'
r={'original_path':str(S),'original_modified_utc':datetime.datetime.fromtimestamp(st.st_mtime,datetime.timezone.utc).isoformat(),'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':copied,'bytes':st.st_size,'copy_verified_against_source_before_and_after':True}
(O/'evidence/INPUT_SNAPSHOT.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r),flush=True)
