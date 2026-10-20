from pathlib import Path
from PIL import Image
import hashlib,json,zipfile
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
prior=json.loads((P.parent/'four_pose_silhouette_rebuild_v029/evidence/PROTECTED_SOURCE_HASHES.json').read_text());checks={}
for name,r in prior.items():
    actual=sha(ROOT/r['path']);checks[name]={'path':r['path'],'sha256':actual,'unchanged':actual==r['sha256']};assert checks[name]['unchanged']
previous=json.loads((P.parent/'four_pose_silhouette_rebuild_v029/evidence/final_handoff.json').read_text());v29=Path(previous['native']);actual=sha(v29);checks['v029']={'path':str(v29),'sha256':actual,'unchanged':actual==previous['native_sha256']};assert checks['v029']['unchanged'] and sha(P/'reference/PRESERVED_BASELINE_v029.blend')==actual
(P/'evidence/PROTECTED_SOURCE_HASHES.json').write_text(json.dumps(checks,indent=2))
board=P/'previews/WTSC_v030_Four_Pose_Review_Board.png';Image.open(board).verify();receipt=json.loads((P/'evidence/LIBRARY_BOARD_RECEIPT.json').read_text())['structuredContent'];assert receipt['status']=='succeeded' and receipt['file_size_bytes']==board.stat().st_size
native=P/'native/WTSC_Four_Pose_Volume_Revision_v030.blend';review=json.loads((P/'evidence/ACTUAL_RENDER_REVIEW.json').read_text())
handoff={'status':'REVISED_FOUR_POSE_BOARD_DELIVERED_ART_REVIEW_PENDING_NO_CYCLE','native':str(native),'native_bytes':native.stat().st_size,'native_sha256':sha(native),'primary_board':{'path':str(board),'bytes':board.stat().st_size,'sha256':sha(board),'dimensions':[1920,2220],'content':'Actual Blender-rendered v029/v030 contact,loaded-down,passing,up close and shot-camera comparisons'},'private_preview':receipt,'actual_Blender_renders':json.loads((P/'evidence/RENDER_RECORD.json').read_text()),'review':review,
    'not_an_art_pass':'The volume/projection corrections are visible, but the broad graphic coat, pelvis value bridge and hand staging still need independent review. Stronger load/rise could become crouched/bouncy if generically interpolated.','full_cycle_or_inbetweens_generated':False,'motion_playback_or_animation_pass_claimed':False,'production_integration':False,'travel_contract':'None authored. Root/stage frozen. Frames1,4,11,13 select independent poses; timing/intermediate playback undefined.',
    'head_choice':'Original painted profile/head/hair UVs and design retained, translated with the revised whole-body mass positions; no turnaround or v008 patch.','critique_and_native_guide':'V030_POSE_GUIDE_AND_CANDID_CRITIQUE.txt','source_preservation':checks,'coordination':'All short threads2 Blender jobs used immediate host no-Blender-process gates and exited. No heavy/full-cycle render. Per user instruction, review requests go through parent; no direct world message attempted.','remaining_review_request':'Please independently review the v030 board before any full-cycle work, focusing on body/head proportion, loaded body mass, the boot/ankle gap and UP support construction.','execution_blockers':[]}
(P/'evidence/final_handoff.json').write_text(json.dumps(handoff,indent=2))
files=[p for folder in ['native','reference','scripts','evidence','previews'] for p in (P/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.blend1','.pyc'] and p.name not in ['PACKAGE_RESULT.json','PACKAGE_MANIFEST.json']];files.extend(p for p in P.iterdir() if p.is_file() and p.suffix=='.txt')
manifest=[{'path':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(set(files))];mf=P/'evidence/PACKAGE_MANIFEST.json';mf.write_text(json.dumps(manifest,indent=2));z=P/'WTSC_Four_Pose_Volume_Revision_v030.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for p in sorted(set(files+[mf])):archive.write(p,'four_pose_volume_revision_v030/'+p.relative_to(P).as_posix())
with zipfile.ZipFile(z) as archive:
    assert archive.testzip() is None
    for r in manifest:assert hashlib.sha256(archive.read('four_pose_volume_revision_v030/'+r['path'])).hexdigest()==r['sha256']
result={'package':str(z),'bytes':z.stat().st_size,'sha256':sha(z),'files':len(files)+1,'CRC_and_hashes':'PASS','private_library_id':receipt['library_file_id'],'version':receipt['current_version_number'],'artistic_status':'Independent four-pose review pending; no cycle generated'};(P/'evidence/PACKAGE_RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
