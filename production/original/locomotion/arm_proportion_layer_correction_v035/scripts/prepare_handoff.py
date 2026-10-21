from pathlib import Path
import json,hashlib,zipfile,re
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
guide=P/'V035_VIEWING_IMPORT_AND_CANDID_ASSESSMENT.txt'
s=guide.read_text(encoding='utf-8-sig')
for a,b in [('V 024/V 027','V024/V027'),("meshes'31","meshes' 31"),('frameF','frame F'),('contactF1','contact F1'),('contactF17','contact F17'),('frameG','frame G'),('sourceF:','source F:'),('(F-1)mod 31','(F-1) mod 31'),('json:125','json: 125'),('json:30','json: 30'),('native 3 D','native 3D'),('buildd 13 f 752 e 3 b 9 c','build d13f752e3b9c')]:s=s.replace(a,b)
guide.write_text(s,encoding='utf-8')
previous=json.loads((P.parent/'preferred_walk_consistent_footwear_v033/evidence/PROTECTED_SOURCE_HASHES.json').read_text());protected={}
for name,row in previous.items():
 path=Path(row['path']);h=sha(path);protected[name]={'path':str(path),'sha256':h,'expected_sha256':row['sha256'],'unchanged':h==row['sha256']}
for name,path in [('v033',P.parent/'preferred_walk_consistent_footwear_v033/native/WTSC_Preferred_Walk_Consistent_Shoes_v033.blend'),('v034',P.parent/'readability_working_view_v034/native/WTSC_Readability_Working_View_v034.blend')]:protected[name]={'path':str(path),'sha256':sha(path),'unchanged':True,'basis':'v033 matches retained source; v034 file not opened for writing by any v035 script'}
assert protected['v033']['sha256']=='e949e76b90397357f3f7378d02669caf276b2aec864a1c82e8594fe166ebd9b4';assert all(r['unchanged'] for r in protected.values())
(P/'evidence/PROTECTED_SOURCE_HASHES.json').write_text(json.dumps(protected,indent=2))
board=P/'previews/WTSC_v035_Matched_Arm_and_Leg_Structure_Comparison.png';receipt=json.loads((P/'evidence/LIBRARY_COMPARISON_RECEIPT.json').read_text())['structuredContent'];build=json.loads((P/'evidence/STRUCTURAL_BUILD_AND_PRESERVATION.json').read_text());cold=json.loads((P/'evidence/COLD_STRUCTURE_AND_OVERLAP_CHECK.json').read_text());metadata=json.loads((P/'evidence/FINAL_NATIVE_METADATA.json').read_text());assert board.stat().st_size<20_000_000;assert all(i['packed'] for i in metadata['ALL']['images'])
manifest={'status':'Isolated static structure candidate; user/parent artistic judgment pending. No full cycle render, no production integration.','preferred_movement':'v028 via retained v033; rejected v031/v032 movement not used','cause_of_curved_legs':build['leg_cause'],'native_files':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted((P/'native').glob('*.blend'))},'guide':guide.name,'private_preview':{'file':str(board.relative_to(P)),'bytes':board.stat().st_size,'sha256':sha(board),'library_file_id':receipt['library_file_id'],'version':receipt['current_version_number'],'confirmed_status':receipt['status'],'download_url':'https://chatgpt.com/api/library/files/'+receipt['library_file_id']+'/download','metadata_EA_readback_confirmed':(P/'evidence/LIBRARY_COMPARISON_RECEIPT_METADATA_VERIFIED.json').exists()},'technical_preservation':{'samples':125,'original_actions_changed':build['original_actions_changed'],'errors':build['preservation_errors'],'cold_leg_joint_change_m':cold['max_actual_leg_joint_change_m'],'cold_cuff_ring_change_m':cold['max_exact_cuff_ring_change_m'],'all_original_images_packed':True,'protected_sources_unchanged':True},'actual_render_scope':'30 matched static native renders at F11,F20,F27 +12 bounded F20 occlusion masks. No unrelated full render.','visual_assessment':['Straighter thigh/shin structure and more localized knee bend in inspected static renders.','Elbow/cuff split is higher; total reach, hand gesture and wrist path retained.','Near hand separation improves modestly but remains small and dark at shot size.','F20 far hand correctly remains behind near trouser; no forced foreground hand.','Knee volume remains broad in passing poses; overlapping leg/shoe silhouettes remain crowded; sleeve/shoulder contours remain graphic.','No continuous playback was observed; no claim of improved normal-speed animation or final acceptance.'],'remaining_work':['Review this matched static comparison before any full-cycle render.','Normal-speed structural continuity after visual direction is accepted.','Paired recovery, girl acting, credible support/clasp and recovery-to-walking remain unfinished.'],'integration_contract':{'fps':30,'period_frames':31,'stride_m':.9524437384576381,'D_F':'0.9524437384576381*(F-1)/31 metres +X','production24fps_map':'F=1+(G-G0)*30/24; bake character/cloth/shoes/world against one clock','production_integration_done':False},'blockers':[],'shared_render_status':'All v035 Blender jobs exited; no further rendering planned before static review.'}
(P/'evidence/final_handoff.json').write_text(json.dumps(manifest,indent=2))
files=[]
for p in sorted(P.rglob('*')):
 if not p.is_file() or p.suffix in ['.zip','.blend1','.pyc','.log'] or '__pycache__' in p.parts:continue
 if p.name.startswith('INSPECTION_') or p.name=='PACKAGE_RESULT.json':continue
 files.append(p)
out=P/'WTSC_Arm_and_Leg_Structure_v035.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,p.relative_to(P).as_posix())
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for p in files:assert hashlib.sha256(z.read(p.relative_to(P).as_posix())).hexdigest()==sha(p)
result={'zip':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'file_count':len(files),'CRC_and_all_file_hashes_pass':True,'preview_bytes':board.stat().st_size,'library_file_id':receipt['library_file_id'],'all_protected_sources_unchanged':True};(P/'evidence/PACKAGE_RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
