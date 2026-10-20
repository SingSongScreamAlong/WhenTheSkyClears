from pathlib import Path
import hashlib,json,csv,zipfile
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];S=.9524437384576381
with (P/'V026_TRAVEL_TIMING.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['native_frame','elapsed_seconds','cycle_one_based','phase_one_based','root_x_m','centred_world_scroll_x_m','included_in_each_video_segment'])
    for frame in range(1,281):q=frame-1;w.writerow([frame,q/30,q//31+1,q%31+1,S*q/31,-S*q/31,frame<=279])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
targets={'v046':('shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend','f4972ea64ceab1c8c88f1c77ed6875f373daac81c007492e4adddfb3660fb661'),'v007':('locomotion/supported_recovery_v007/native/WTSC_Supported_Recovery_v007.blend','77f253b88300415ce13cf4710455174f9afc64366b6dd361416703362b8788de'),'v045c':('shots/world/WTSC_Open_Battlefield_Art_Study_v045c.blend','5dd333d28452e1427daf828711c3a6ac9abee5223d69090623e92e53e8583fb4')}
checks={}
for name,(path,expected) in targets.items():actual=sha(ROOT/path);checks[name]={'path':path,'sha256':actual,'unchanged':actual==expected};assert actual==expected
original=P.parent/'gp_coat_transition_v025/reference/PRESERVED_GP_FIRST_ROUGH_v025.blend';copied=P/'reference/PRESERVED_PROMISING_GP_v025.blend';checks['v025_promising_source']={'original_sha256':sha(original),'copy_sha256':sha(copied),'unchanged':sha(original)==sha(copied)};assert checks['v025_promising_source']['unchanged']
(P/'evidence/PROTECTED_SOURCE_HASHES.json').write_text(json.dumps(checks,indent=2))
preview=json.loads((P/'evidence/PREVIEW_VERIFICATION.json').read_text());native=P/'native/WTSC_GP_Extended_Review_v026.blend'
handoff={'status':'REQUESTED_LONGER_REVIEW_COMPLETE_ART_OPEN','native':str(native),'native_bytes':native.stat().st_size,'native_sha256':sha(native),'preview':preview,'technical':json.loads((P/'evidence/FULL_CYCLE_AND_TRAVEL_CHECK.json').read_text()),'actual_continuous_playback_observed':False,'visual_review':'Full32frame native proof; decoded firstcycle/join, latecyclejoin and shot boards. Frame inspection, not real-time playback acceptance.','remaining_art':['Coat is a rough cleaner value study; painterly surface and final fold quality remain open.','Cadence/whole-body loading requires the requested uninterrupted viewing assessment.','Opposing half is newly completed for this review; originalv025half is exact.','This is a solo walk proof; paired recovery-to-walk integration remains separate.'],'experiments_excluded':['v025b upper-loading delay','v025b pigment/fill-carrier study'],'preservation':checks,'coordination':'CPU-gated threads2. Last world message reported no further world render planned. Local thread messaging subsequently returned Transport closed; no concurrent Blender render was detected before launch.'}
receipt=P/'evidence/LIBRARY_PREVIEW_RECEIPT.json'
if receipt.exists():handoff['private_preview']=json.loads(receipt.read_text()).get('structuredContent')
(P/'evidence/final_handoff.json').write_text(json.dumps(handoff,indent=2))
files=[p for folder in ['native','reference','scripts','evidence'] for p in (P/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.blend1','.pyc'] and p.name not in ['PACKAGE_RESULT.json','PACKAGE_MANIFEST.json']]
files.extend(p for p in P.iterdir() if p.is_file() and p.suffix in ['.txt','.csv']);files.extend(p for p in (P/'previews').iterdir() if p.is_file())
manifest=[{'path':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(set(files))];mf=P/'evidence/PACKAGE_MANIFEST.json';mf.write_text(json.dumps(manifest,indent=2));z=P/'WTSC_GP_Extended_Review_v026.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for p in sorted(set(files+[mf])):archive.write(p,'gp_extended_review_v026/'+p.relative_to(P).as_posix())
with zipfile.ZipFile(z) as archive:
    assert archive.testzip() is None
    for r in manifest:assert hashlib.sha256(archive.read('gp_extended_review_v026/'+r['path'])).hexdigest()==r['sha256']
result={'package':str(z),'bytes':z.stat().st_size,'sha256':sha(z),'files':len(files)+1,'CRC_and_hashes':'PASS','raw_render_directories_included':False};(P/'evidence/PACKAGE_RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
