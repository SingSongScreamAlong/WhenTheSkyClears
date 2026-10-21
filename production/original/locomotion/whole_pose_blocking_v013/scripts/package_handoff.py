from pathlib import Path
import hashlib,json,zipfile
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((P/'evidence'/n).read_text())
protected=read('protected_inputs.json');assert all(sha(Path(p))==h for p,h in protected.items())
native=P/'native/WTSC_Whole_Pose_Blocking_v013.blend';media=read('media_verification.json');art=read('artistic_assessment.json');technical=read('native_validation.json');append=read('append_validation.json');lib=read('library_preview_receipt.json')
for m in media:assert sha(Path(m['path']))==m['sha256'] and m['decoded_frames']==72 and m['bytes']<20_000_000
assert lib['status']=='succeeded' and lib['file_size_bytes']==media[0]['bytes']
references=[]
for name,expected in [('Muybridge_Plate272_Trip_Over_Bed_V0048664.jpg','7153731180a65365105b6c93d2a02c9b4ce1505e'),('Muybridge_Lifting_Trunk_V0048693.jpg','90f3130586d806e0bdabb6bf3f288795df103ab5')]:
 p=P/'reference'/name;actual=hashlib.sha1(p.read_bytes()).hexdigest();assert actual==expected,(name,actual)
 references.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'sha1_matches_Commons_original':True})
sheets=[P/f'WTSC_v013_{mode}_Key_Poses.jpg' for mode in ['INSPECTION','SHOT_SIZE']]
handoff={'status':art['status'],'stage':'Authored, rendered and reviewed as blocking. Stopped for pose review; no curve polish authorized by this handoff.','native':{'path':str(native),'bytes':native.stat().st_size,'sha256':sha(native),'collection':'WTSC_WHOLE_POSE_BLOCKING_v013','frames':[1,72],'fps':24,'duration_s':3,'armatures':2,'objects':44,'external_images':0,'interpolation':'CONSTANT','boy_key_count':15,'girl_key_count':11},'previews':media,'key_pose_sheets':[{'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sheets],'guide':str(P/'READ_ME_BLOCKING_REVIEW_v013.txt'),'private_library':lib,'artistic_assessment':art,'technical_integrity':technical,'fresh_append':append,'reference_sources':references,'reference_notes':str(P/'reference/REFERENCE_OBSERVATIONS.txt'),'sources_preserved':{p:True for p in protected},'local_clock':'1..72 at24fps, boundary73=3s. Standalone stepped routes; no75..80s mapping. Do not integrate or mix with old DISTANCE_CURVE.','next_step':'Independent whole-pose blocking review. No spline polish, new walking, repaint or production integration before that review.','blocked_or_uncertain_actions':[],'review_limit':{'action':'Continuous/full-speed artistic verification','target':[m['path'] for m in media],'state':'Unavailable to agent/reviewer, not denied or pending tool execution. All72decodedframes per view inspected; pacing remains provisional.'},'ancillary_delivery_issue':{'action':'Persist local Library identity metadata','target':media[0]['path'],'state':'Unavailable; Windows Python has no os.setxattr. Official helper invoked and failed; private upload succeeded and exact Library/file/version receipt is retained. No uncertain upload.'}}
(P/'evidence/final_handoff.json').write_text(json.dumps(handoff,indent=2))
files=[native,P/'READ_ME_BLOCKING_REVIEW_v013.txt']+[Path(m['path']) for m in media]+sheets+list((P/'scripts').glob('*.py'))+list((P/'reference').glob('*'))
files += [P/'evidence'/name for name in ['final_handoff.json','artistic_assessment.json','authored_story_poses.json','native_validation.json','append_validation.json','build_report.json','media_verification.json','contact_samples.json','protected_inputs.json','prior_v012_independent_artistic_review.json','reuse_and_reference_record.json','world_motion_samples.csv','library_preview_receipt.json','local_library_metadata_status.json']]
files+=sorted((P/'evidence/decoded_review').glob('*.jpg'))
dest=P/'WTSC_Whole_Pose_Blocking_v013.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,p.relative_to(P))
with zipfile.ZipFile(dest) as z:assert z.testzip() is None;entries=len(z.infolist())
receipt={'path':str(dest),'bytes':dest.stat().st_size,'sha256':sha(dest),'entries':entries,'stop_for_blocking_review':True,'source_hashes_preserved':True,'painted_or_production_assets_included':False,'unmodified_reference_images_credited':True}
(P/'evidence/package_receipt.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
