from pathlib import Path
import hashlib,json,zipfile
from PIL import Image
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];OLD=P.parent/'rough_breakdowns_construction_v031'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
prior=json.loads((OLD/'evidence/PROTECTED_SOURCE_HASHES.json').read_text());checks={}
for name,r in prior.items():
    path=ROOT/r['path'];actual=sha(path);checks[name]={'path':str(path),'sha256':actual,'unchanged':actual==r['sha256']};assert checks[name]['unchanged']
old=json.loads((OLD/'evidence/final_handoff.json').read_text());path=Path(old['native']);checks['v031']={'path':str(path),'sha256':sha(path),'unchanged':sha(path)==old['native_sha256']};assert checks['v031']['unchanged'] and sha(P/'reference/PRESERVED_BASELINE_v031.blend')==sha(path)
(P/'evidence/PROTECTED_SOURCE_HASHES.json').write_text(json.dumps(checks,indent=2))
native=P/'native/WTSC_Rough_Construction_v032.blend';movie=json.loads((P/'evidence/ENCODE_AND_DECODE_CHECK.json').read_text());cold=json.loads((P/'evidence/COLD_REOPEN_AND_RENDER_CHECK.json').read_text());visual=json.loads((P/'evidence/BREAKDOWN_VISUAL_REVIEW.json').read_text());spacing=json.loads((P/'evidence/ACTUAL_FRAME_SPACING_COMPARISON.json').read_text())
assert cold['max_actual_boot_change_from_saved_v031_m']==0 and cold['max_integer_frame_cuff_join_error_m']<1e-6
assert movie['decoded_frames']==576 and (P/movie['file']).stat().st_size==movie['bytes']<20_000_000 and sha(P/movie['file'])==movie['sha256']
receipts={}
for key in ['MOVIE','BOARD']:
    r=json.loads((P/f'evidence/LIBRARY_{key}_RECEIPT.json').read_text())['structuredContent'];assert r['status']=='succeeded';meta=json.loads((P/f'evidence/LIBRARY_{key}_RECEIPT_METADATA_VERIFIED.json').read_text());assert meta['readback']['user.library-file-id']==r['library_file_id'];receipts[key.lower()]=r
for board in (P/'previews').glob('WTSC*.png'):Image.open(board).verify()
handoff={'status':'V032_LANDING_AND_ARM_CORRECTION_DELIVERED_CONSTRUCTION_REVIEW_PENDING','artistic_acceptance':False,'paired_acting':'HELD pending construction review and user feedback','native':str(native),'native_bytes':native.stat().st_size,'native_sha256':sha(native),'preview':movie,'private_Library':receipts,'primary_comparison_board':str(P/'previews/WTSC_v032_Construction_Comparison_Board.png'),'consecutive_frame_boards':[str(p) for p in (P/'previews').glob('WTSC_v032_Landing_Consecutive*.png')],'arm_board':str(P/'previews/WTSC_v032_Arm_Overlap_Comparison.png'),'guide':str(P/'V032_IMPORT_TIMING_AND_CANDID_ASSESSMENT.txt'),'travel_CSV':str(P/'evidence/TRAVEL_SOLE_AND_BODY_QUARTER_FRAME.csv'),'travel_contract':{'unchanged_from':'v031','period_frames':32,'fps':30,'stride_m':.8146774020162355,'root':'D=.8146774020162355*(F-1)/32 metres+X, unwrapped linear','speed_mps':.7637600643902208,'production24fps':'Unified per-output-frame bake required; q=30*(N-N0)/24+q0. No production integration or changed trailer duration.'},'actual_render_spacing_comparison':spacing,'visual_review':visual,'cold_native_technical_safeguards':cold,'normal_speed_render':json.loads((P/'evidence/NORMAL_SPEED_RENDER_RECORD.json').read_text()),'source_preservation':checks,'observation_limit':'Actual successive frames, all32 drawings, selected shot frames and selected decoded encoded-movie frames inspected. Continuous playback not observed through available tools; performance/user-feedback gate remains open.','review_request':'Please route independent V032 review through parent, focusing on comparable absorption/push through both landings and legibility of both arms during F17–27. User feedback is pending; no artistic acceptance claimed.','remaining_issues':visual['remaining_visual_issues'],'coordination':'All Blender jobs used host no-process gates and two threads; all have exited. No production/other-specialist files edited. No direct world messaging.','execution_blockers':[]}
(P/'evidence/final_handoff.json').write_text(json.dumps(handoff,indent=2))
files=[]
for folder in ['native','reference','scripts','evidence']:
    files.extend(p for p in (P/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.blend1','.pyc'] and p.name not in ['PACKAGE_RESULT.json','PACKAGE_MANIFEST.json'])
files.extend(p for p in (P/'previews').iterdir() if p.is_file() and (p.name.startswith('WTSC') or p.name in ['DECODED_000.png','DECODED_019.png','DECODED_026.png','DECODED_288.png','DECODED_575.png']));files.extend(P.glob('*.txt'))
manifest=[{'path':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(set(files))];mf=P/'evidence/PACKAGE_MANIFEST.json';mf.write_text(json.dumps(manifest,indent=2));dest=P/'WTSC_Balanced_Load_Arms_v032.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for p in sorted(set(files+[mf])):archive.write(p,'balanced_load_and_arm_readability_v032/'+p.relative_to(P).as_posix())
with zipfile.ZipFile(dest) as archive:
    assert archive.testzip() is None
    for r in manifest:assert hashlib.sha256(archive.read('balanced_load_and_arm_readability_v032/'+r['path'])).hexdigest()==r['sha256']
result={'package':str(dest),'bytes':dest.stat().st_size,'sha256':sha(dest),'files':len(files)+1,'CRC_and_hashes':'PASS','Library_movie_id':receipts['movie']['library_file_id'],'Library_movie_version':receipts['movie']['current_version_number'],'Library_board_id':receipts['board']['library_file_id'],'Library_board_version':receipts['board']['current_version_number'],'status':handoff['status']};(P/'evidence/PACKAGE_RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
