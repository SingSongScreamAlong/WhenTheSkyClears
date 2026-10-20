from pathlib import Path
import json,hashlib,datetime,shutil
O=Path(r'WTSC_LOCAL_WORKSPACE\locomotion\garment_continuity_v047\current_v046_continuation');B=Path(r'WTSC_LOCAL_WORKSPACE\locomotion\garment_continuity_v047')
S=Path(r'WTSC_LOCAL_WORKSPACE\locomotion\painted_outfit_restoration_v046\native\WTSC_Age10_Painted_Outfit_Restoration_v046.blend')
H='e993540280bc60ff5fcc1dafe316f7c8457c5c8750a1110b8f6e307a865d005d'
assert hashlib.sha256(S.read_bytes()).hexdigest()==H
D=O/'scripts';D.mkdir(exist_ok=True)
for name in ['body_followthrough.py','paired_reach_refined.py','build_current_garment.py','build_current_reach.py','render_current_sequences.py','validate_current_native.py','package_current_review.py']:
 shutil.copy2(B/'scripts'/name,D/name)
r=json.loads((O/'evidence/COLD_NATIVE_VALIDATION.json').read_text());e=json.loads((O/'evidence/ENCODED_REVIEW_VALIDATION.json').read_text())
assert r['all_checks_pass'] and e['candidate_frames_decoded']==94
files=[O/'native/WTSC_Age10_Garment_Continuity_v047b.blend',O/'native/WTSC_Age10_Paired_Reach_v047b.blend',O/'previews/WTSC_Age10_Reach_v047b.mp4',O/'previews/WTSC_Age10_Comparison_v047b.mp4',O/'previews/Contact_Comparison_v047b.jpg',O/'README_v047b.txt']
m={'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_still_matches_final_v046':True,'source_sha256':H,'cold_native_all_checks_pass':True,'encoded_frames_decoded':94,'range':[1,94],'fps':30,'files':[{'path':str(f.relative_to(O)),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files],'artistic_status':'Improved garment and hand-contact study; facial performance, finger articulation and shot lighting remain.'}
(O/'evidence/DELIVERY_MANIFEST.json').write_text(json.dumps(m,indent=2))
print(json.dumps(m,indent=2),flush=True)
