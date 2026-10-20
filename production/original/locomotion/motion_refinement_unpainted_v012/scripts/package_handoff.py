from pathlib import Path
import json,hashlib,zipfile
P=Path(__file__).resolve().parents[1];R=P.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return json.loads((P/'evidence'/name).read_text())
protected=read('protected_inputs.json');assert all(sha(R/n)==h for n,h in protected.items())
native=P/'native/WTSC_Unpainted_Motion_Rebuild_v012.blend';media=read('media_verification.json');art=read('artistic_assessment.json');lib=read('library_preview_receipt.json');technical=read('native_validation.json');append=read('append_validation.json');events=read('event_timing_check.json')
for m in media:assert sha(Path(m['path']))==m['sha256'] and m['decoded_frames']==144 and m['bytes']<20_000_000
assert lib['status']=='succeeded' and lib['file_size_bytes']==media[0]['bytes']
handoff={
 'status':art['status'],
 'native':{'path':str(native),'bytes':native.stat().st_size,'sha256':sha(native),'collection':'WTSC_UNPAINTED_MOTION_REBUILD_v012','frames':[1,144],'fps':24,'seconds':6,'armatures':2,'objects':44,'external_images':0},
 'previews':media,'private_library':lib,'guide':'REFINEMENT_AND_TIMING_GUIDE_v012.txt',
 'fundamental_changes':art['fundamental_changes'],'artistic_assessment':art,
 'technical_integrity':{'cold_reopened':technical['cold_reopened'],'binding_joint_target_error_m':technical['evaluated_joint_target_error_m'],'bound_mesh_center_error_m':technical['bound_proxy_mesh_center_error_m'],'fixed_segment_length_error_m':technical['native_segment_length_error_m'],'flat_sole_vertex_drift_m':technical['adjacent_flat_stance_vertex_drift_m'],'floor_min_z_m':technical['floor_min_z_m'],'fresh_append':append,'event_timing_check':events,'note':'Technical integrity only. Naturalism/repaint gate remains unpassed.'},
 'clock_and_integration':{'local_frames':[1,144],'fps':24,'frame1_seconds':0,'frame144_seconds':143/24,'boundary145_seconds':6,'boy_catch_heel':36,'boy_load_minimum':40,'girl_brake_heel':26,'girl_load_minimum':29,'boy_restart_heel':78,'girl_restart_heel':83,'travel':'Independent native Object root routes plus per-frame world_motion_samples.csv and full joint_targets.json. Camera averages child routes.','production_mapping':None,'instruction':'Append only into an empty test scene. Do not combine with old DISTANCE_CURVE, alter full-trailer length or silently retime144 frames into120. Accept movement/timing first, then match world/camera/contact routes together.'},
 'sources_preserved':{n:True for n in protected},'remaining_limitations':art['limitations'],
 'blocked_or_uncertain_actions':[],
 'ancillary_delivery_issue':{'action':'Persist local Library identity metadata','target':media[0]['path'],'reason':'Current Windows Python has no os.setxattr; current official helper invoked and returned AttributeError.','state':'Unavailable, not denied or pending; no local metadata written. Upload confirmed succeeded, exact identity/version receipt saved. No uncertain upload.'}
}
(P/'evidence/final_handoff.json').write_text(json.dumps(handoff,indent=2))
files=[native,P/'REFINEMENT_AND_TIMING_GUIDE_v012.txt']+[Path(m['path']) for m in media]
files+=[p for p in (P/'scripts').glob('*.py') if p.name!='derive_sources.py']
evidence=['final_handoff.json','build_report.json','native_validation.json','append_validation.json','event_timing_check.json','media_verification.json','artistic_assessment.json','protected_inputs.json','reuse_and_reference_record.json','prior_v011_independent_artistic_review.json','world_motion_samples.csv','joint_targets.json','contact_samples.json','library_preview_receipt.json','local_library_metadata_status.json','INSPECTION_pose_review.jpg','SHOT_SIZE_pose_review.jpg','dense_catch_progression.jpg']
files += [P/'evidence'/n for n in evidence]
files += sorted((P/'evidence/decoded_sequence_review').glob('*.jpg'))
out=P/'WTSC_Unpainted_Motion_Refinement_v012.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,p.relative_to(P))
with zipfile.ZipFile(out) as z:assert z.testzip() is None;entries=len(z.infolist())
receipt={'path':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'entries':entries,'source_hashes_preserved':True,'production_assets_included':False,'superseded_first_pass_excluded':True,'current_decoded_review_sheets_included':12}
(P/'evidence/package_receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
