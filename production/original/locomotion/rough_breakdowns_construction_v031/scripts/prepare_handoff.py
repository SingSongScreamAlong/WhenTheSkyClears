from pathlib import Path
import hashlib,json,zipfile
from PIL import Image
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
previous=P.parent/'four_pose_volume_revision_v030';prior=json.loads((previous/'evidence/PROTECTED_SOURCE_HASHES.json').read_text());checks={}
for name,r in prior.items():
    path=ROOT/r['path'];actual=sha(path);checks[name]={'path':str(path),'sha256':actual,'unchanged':actual==r['sha256']};assert checks[name]['unchanged']
old=json.loads((previous/'evidence/final_handoff.json').read_text());oldnative=Path(old['native']);checks['v030']={'path':str(oldnative),'sha256':sha(oldnative),'unchanged':sha(oldnative)==old['native_sha256']};assert checks['v030']['unchanged'] and sha(P/'reference/PRESERVED_BASELINE_v030.blend')==sha(oldnative)
(P/'evidence/PROTECTED_SOURCE_HASHES.json').write_text(json.dumps(checks,indent=2))
native=P/'native/WTSC_Rough_Construction_v031.blend';movie=json.loads((P/'evidence/ENCODE_AND_DECODE_CHECK.json').read_text());cold=json.loads((P/'evidence/COLD_REOPEN_AND_RENDER_CHECK.json').read_text());visual=json.loads((P/'evidence/BREAKDOWN_VISUAL_REVIEW.json').read_text())
assert cold['sample_count']==2049 and cold['max_boot_vertex_error_against_analytic_m']<.0003
assert (P/movie['file']).stat().st_size==movie['bytes']<20_000_000 and sha(P/movie['file'])==movie['sha256']
receipts={}
for key in ['MOVIE','BOARD']:
    r=json.loads((P/f'evidence/LIBRARY_{key}_RECEIPT.json').read_text())['structuredContent'];assert r['status']=='succeeded';meta=json.loads((P/f'evidence/LIBRARY_{key}_RECEIPT_METADATA_VERIFIED.json').read_text());assert meta['readback']['user.library-file-id']==r['library_file_id'];receipts[key.lower()]=r
for board in (P/'previews').glob('WTSC*.png'):Image.open(board).verify()
handoff={'status':'V031_ROUGH_CONSTRUCTION_ACTION_DELIVERED_INDEPENDENT_NORMAL_SPEED_REVIEW_PENDING','artistic_acceptance':False,'native':str(native),'native_bytes':native.stat().st_size,'native_sha256':sha(native),'preview':movie,'private_Library':receipts,'pose_board':str(P/'previews/WTSC_v031_Construction_Pose_Board.png'),'complete_breakdown_boards':[str(p) for p in (P/'previews').glob('WTSC_v031_Breakdowns*.png')],'guide':str(P/'V031_IMPORT_TIMING_AND_CANDID_ASSESSMENT.txt'),'travel_CSV':str(P/'evidence/TRAVEL_SOLE_AND_BODY_QUARTER_FRAME.csv'),'travel_contract':{'period_frames':32,'fps':30,'stride_m':.8146774020162355,'root':'D=.8146774020162355*(F-1)/32 metres+X, unwrapped linear','speed_mps':.7637600643902208,'production24fps':'Bake all body drawings and head/boot transforms together from q=30*(N-N0)/24+q0; do not independently retime held GP and continuous boot curves. No production integration claimed.'},'visual_review':visual,'cold_native_technical_safeguards':cold,'normal_speed_render':json.loads((P/'evidence/NORMAL_SPEED_RENDER_RECORD.json').read_text()),'source_preservation':checks,'observation_limit':'All32 actual close drawings, selected shot frames and decoded actual movie frames inspected. Continuous normal-speed playback not observed through available tools; independent/human review remains the artistic gate.','parent_review_request':'Please route an independent normal-speed construction review of v031 through the parent task. Focus on both load transfers, body volume stability, arm arcs and overlaps, F13 hand/hem gap, heel/toe projection and loop continuity. This is not a finished/approved cycle.','outstanding_scope':['Boy-only construction: no authored girl performance or paired supported recovery/stumble/restart transition in this checkpoint.','Rough clean body fills remain unlike final ink-and-wash painting.','Restrained arms and near-hand/coat merging around passing need playback judgment.','Asymmetric load heights may read unevenly; review before further production work.'],'coordination':'All Blender jobs used immediate host no-process gates and two threads. All own Blender jobs have exited. No other specialist or production files edited. Review requests through parent; no direct world message.','execution_blockers':[]}
(P/'evidence/final_handoff.json').write_text(json.dumps(handoff,indent=2))
# Keep every raw PNG in the workspace; package the usable native, evaluator,
# guides, evidence and compact review artifacts rather than192 intermediate frames.
files=[]
for folder in ['native','reference','scripts','evidence']:
    files.extend(p for p in (P/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.blend1','.pyc'] and p.name not in ['PACKAGE_RESULT.json','PACKAGE_MANIFEST.json'])
files.extend(p for p in (P/'previews').iterdir() if p.is_file());files.extend(P.glob('*.txt'))
manifest=[{'path':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(set(files))];mf=P/'evidence/PACKAGE_MANIFEST.json';mf.write_text(json.dumps(manifest,indent=2));dest=P/'WTSC_Rough_Construction_v031.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for p in sorted(set(files+[mf])):archive.write(p,'rough_breakdowns_construction_v031/'+p.relative_to(P).as_posix())
with zipfile.ZipFile(dest) as archive:
    assert archive.testzip() is None
    for r in manifest:assert hashlib.sha256(archive.read('rough_breakdowns_construction_v031/'+r['path'])).hexdigest()==r['sha256']
result={'package':str(dest),'bytes':dest.stat().st_size,'sha256':sha(dest),'files':len(files)+1,'CRC_and_hashes':'PASS','Library_movie_id':receipts['movie']['library_file_id'],'Library_movie_version':receipts['movie']['current_version_number'],'Library_board_id':receipts['board']['library_file_id'],'Library_board_version':receipts['board']['current_version_number'],'status':handoff['status']};(P/'evidence/PACKAGE_RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
