import json,hashlib,zipfile,shutil
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];E=P/'evidence';V=P/'previews';W=ROOT/'locomotion/weight_loading_v048'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
render=json.loads((E/'ACTUAL_V049_MOTION_RENDER.json').read_text());encoded=json.loads((E/'ACTUAL_V049_ENCODE_VALIDATION.json').read_text())
for path,h in render['source_hashes'].items():assert sha(Path(path))==h
for r in encoded['movies']:assert sha(V/r['file_name'])==r['sha256'] and r['under_20_MB']
prior=json.loads((E/'SOURCE_INTEGRITY.json').read_text());checks=[]
for r in prior['sources']:
 actual=sha(ROOT/r['path']);assert actual==r['expected_sha256'];checks.append({'path':r['path'],'sha256':actual,'unchanged':True})
static_match=[]
for f in [1,5,9]:
 a=V/('AFTER_WALK_F%02d.png'%f);b=V/'frames_V049'/('FRAME_%04d.png'%f);equal=Image.open(a).convert('RGB').tobytes()==Image.open(b).convert('RGB').tobytes();assert equal
 static_match.append({'frame':f,'static_and_motion_render_pixels_identical':equal,'png_bytes_identical':sha(a)==sha(b),'note':'PNG metadata records different render dates/times; RGB pixels are identical.','sha256':sha(b)})
unchanged={'older_sources':checks,'motion_native_sources':render['source_hashes'],'actual_v049_matches_static_render':static_match,'old_static_archive_sha256':sha(P/'WTSC_Model_Fit_v049_and_Loading_v048.zip')}
assert unchanged['old_static_archive_sha256']=='a116f21b26ab3c14c977ba496b06291359af4363504b688e8ed91c04cf84ac81'
(E/'ACTUAL_MOTION_SOURCE_INTEGRITY.json').write_text(json.dumps(unchanged,indent=2))
shutil.copyfile(W/'evidence/TRAVEL_CURVE_v048.csv',P/'TRAVEL_CURVE_v049.csv')
clarification={'library_file_id':'[PRIVATE_LIBRARY_REFERENCE_REMOVED]','file_name':'WTSC_v047_vs_v048_Weight_Loading_NormalSpeed.mp4','left_label':'v047 | QUIET BASELINE','left_subtitle':'32-frame cycle, 0.731 m/s | preserved reference','right_label':'v048 | CONNECTED STEP LOADING','right_subtitle':'Same pace and phase | knee absorption, drawn-sole rollover and counterbalance','footer':'Same camera and scale | same elapsed time at 30 fps | same cadence, phase and travel','contains_v049_model_fit':False}
(E/'OLDER_MOVIE_EXACT_VERSION_CLARIFICATION.json').write_text(json.dumps(clarification,indent=2))
assessment={'status':'Actual frozen v049 model in preserved v048 motion. Model coherence review, not artistic acceptance.','reviewed':'Decoded all32 integer cycle poses,8 upper-body phases,12 matched comparison frames spanning8cycles. Continuous player playback not observed.','visible_improvements':['Reduced bodice projection and softer waist remain consistent across reviewed phases.','Softer sleeve crown and forearm/wrist taper show no new visible open gaps or return of the corrected wrist ledge.','Grouped original fingers read less splayed while hand lengths and painting remain unchanged.'],'remaining_visible_limits':['Girl charcoal face/white eye remains a different finish from the painted boy.','Hands retain a single rigid painted pose.','Planar narrow clothing, static dress hem and braid, and neck/shoulder-to-torso construction still read assembled.','The preserved v048 body motion is restrained and cyclic; this pass adds no performance or recovery/clasp transition.'],'technical_tests':'Frozen native hashes, earlier exact bone/Action/UV/pixel/cache checks, actual257frame render, full movie decode and identical static/motion proof frames. These are not art acceptance.','technical_blockers':[],'render_finished':True,'production_changed':False}
(E/'ACTUAL_MOTION_ARTISTIC_ASSESSMENT.json').write_text(json.dumps(assessment,indent=2))
statics=json.loads((E/'LIBRARY_VERIFIED_LIBRARY_STATIC_CREATE_RESULT.json').read_text());movies=json.loads((E/'LIBRARY_VERIFIED_LIBRARY_ACTUAL_V049_MOTION_CREATE_RESULT.json').read_text());assert len(statics)==2 and len(movies)==2 and all(r['metadata_verified'] for r in statics+movies)
items=[P/'native/WTSC_Connected_Model_Fit_v049.blend',W/'native/WTSC_Connected_Weight_Loading_v048.blend',P/'ACTUAL_MOTION_REVIEW_v049.txt',P/'TRAVEL_CURVE_v049.csv']
items += [P/'scripts'/n for n in ['model_spec.py','build_model_fit.py','render_static_proof.py','cold_validate.py','assemble_static_boards.py','render_v049_motion.py','encode_v049_motion.py']]
items += [E/n for n in ['COLD_MODEL_VALIDATION.json','MODEL_FIT_BUILD.json','STATIC_PROOF_RENDER.json','STATIC_MOTION_PIXEL_COMPARISON.json','ACTUAL_V049_MOTION_RENDER.json','ACTUAL_V049_ENCODE_VALIDATION.json','ACTUAL_MOTION_SOURCE_INTEGRITY.json','OLDER_MOVIE_EXACT_VERSION_CLARIFICATION.json','ACTUAL_MOTION_ARTISTIC_ASSESSMENT.json','LIBRARY_VERIFIED_LIBRARY_STATIC_CREATE_RESULT.json','LIBRARY_VERIFIED_LIBRARY_ACTUAL_V049_MOTION_CREATE_RESULT.json']]
items += [V/n for n in ['WTSC_v048_v049_Model_Fit_Before_After.png','WTSC_v048_v049_Wrist_Cuff_Hand_Comparison.png','WTSC_v049_Neutral_And_Three_Walk_Poses.png','DECODED_V049_UPPER_BODY_PHASES.jpg','DECODED_V048_V049_COMPARISON.jpg']]
items += [V/('DECODED_V049_CYCLE_%d.jpg'%i) for i in range(1,5)]+[V/r['file_name'] for r in encoded['movies']]
manifest=[{'archive_path':str(f.relative_to(ROOT)).replace('\\','/'),'bytes':f.stat().st_size,'sha256':sha(f)} for f in items]
(E/'ACTUAL_MOTION_DELIVERY_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
archive=P/'WTSC_v049_Actual_Model_Motion_Review.zip';assert not archive.exists(),'Do not overwrite the motion review archive'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f,r in zip(items,manifest):z.write(f,r['archive_path'])
 z.write(E/'ACTUAL_MOTION_DELIVERY_MANIFEST.json','DELIVERY_MANIFEST.json')
with zipfile.ZipFile(archive) as z:assert z.testzip() is None;assert len(z.namelist())==len(items)+1
handoff={'model_version':'v049','motion_version':'v048 exactly preserved','static_library_files':statics,'actual_motion_library_files':movies,'older_movie_clarification':clarification,'movies':encoded['movies'],'native':str(P/'native/WTSC_Connected_Model_Fit_v049.blend'),'native_sha256':sha(P/'native/WTSC_Connected_Model_Fit_v049.blend'),'import_timing_guide':str(P/'ACTUAL_MOTION_REVIEW_v049.txt'),'travel_curve':str(P/'TRAVEL_CURVE_v049.csv'),'archive':str(archive),'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'archive_files':len(items)+1,'all_archive_crcs_pass':True,'older_sources_and_static_archive_unchanged':True,'remaining_visible_defects':assessment['remaining_visible_limits'],'technical_blockers':[],'artistic_acceptance':False}
(E/'ACTUAL_MOTION_FINAL_HANDOFF.json').write_text(json.dumps(handoff,indent=2));print(json.dumps(handoff,indent=2))
