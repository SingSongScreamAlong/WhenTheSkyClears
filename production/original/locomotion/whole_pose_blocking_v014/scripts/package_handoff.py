from pathlib import Path
import json,hashlib,zipfile
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return json.loads((P/'evidence'/name).read_text())
protected=read('protected_inputs.json');assert all(sha(Path(p))==h for p,h in protected.items())
native=P/'native/WTSC_Whole_Pose_Blocking_v014.blend';media=read('media_verification.json');art=read('artistic_assessment.json');comparison=read('focused_comparison.json');technical=read('native_validation.json');append=read('append_validation.json');receipts=read('library_key_sheets_receipt.json')
for m in media:assert sha(Path(m['path']))==m['sha256'] and m['decoded_frames']==72 and m['bytes']<20_000_000
sheets=[P/f'WTSC_v014_{mode}_Key_Poses.jpg' for mode in ['INSPECTION','SHOT_SIZE']]
assert len(receipts['results'])==2
for sheet,receipt in zip(sheets,receipts['results']):assert receipt['status']=='succeeded' and receipt['file_name']==sheet.name and receipt['file_size_bytes']==sheet.stat().st_size
handoff={'status':art['status'],'stage':'Requested arm/brace keys corrected, rendered and frame-reviewed. Stops for focused blocking review before polish.','native':{'path':str(native),'bytes':native.stat().st_size,'sha256':sha(native),'collection':'WTSC_WHOLE_POSE_BLOCKING_v014','frames':[1,72],'fps':24,'seconds':3,'armatures':2,'objects':44,'interpolation':'CONSTANT','boy_key_count':15,'girl_key_count':11},'previews':media,'key_pose_sheets':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sheets],'private_library_key_sheets':receipts,'guide':str(P/'FOCUSED_CORRECTION_GUIDE_v014.txt'),'artistic_assessment':art,'focused_preservation_and_contact':comparison,'technical_integrity':technical,'fresh_append':append,'sources_preserved':{p:True for p in protected},'local_clock':'Unchanged1..72 at24fps, boundary73=3s. Standalone stepped blocking; no production75..80s mapping.','remaining_limits':art['remaining_limits'],'blocked_or_uncertain_actions':[],'delivery_recovery':'Prepared helper failed during tool discovery before any write; ordered direct image creates succeeded. No uncertain upload or duplicate prepared file.','ancillary_metadata_limit':read('local_library_metadata_status.json')}
(P/'evidence/final_handoff.json').write_text(json.dumps(handoff,indent=2))
files=[native,P/'FOCUSED_CORRECTION_GUIDE_v014.txt']+[Path(m['path']) for m in media]+sheets+list((P/'scripts').glob('*.py'))
files += [P/'evidence'/name for name in ['final_handoff.json','artistic_assessment.json','authored_story_poses.json','build_report.json','native_validation.json','append_validation.json','focused_comparison.json','media_verification.json','protected_inputs.json','contact_samples.json','world_motion_samples.csv','prior_v013_independent_artistic_review.json','reuse_and_scope_record.json','library_key_sheets_receipt.json','library_preflight_failure.json','local_library_metadata_status.json']]
files+=sorted((P/'evidence/decoded_review').glob('*.jpg'))
dest=P/'WTSC_Focused_Blocking_Correction_v014.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,p.relative_to(P))
with zipfile.ZipFile(dest) as z:assert z.testzip() is None;entries=len(z.infolist())
receipt={'path':str(dest),'bytes':dest.stat().st_size,'sha256':sha(dest),'entries':entries,'stop_for_focused_blocking_review':True,'source_hashes_preserved':True,'outside_scope_native_matrix_difference':0,'private_library_sheets_confirmed':2,'painted_or_production_assets_included':False};(P/'evidence/package_receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
