import json,hashlib,zipfile
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];E=P/'evidence';V=P/'previews'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
native=P/'native/WTSC_Age10_Painted_Outfit_Restoration_v046.blend';native_sha=sha(native)
for name in ['COLD_CONTACT_VALIDATION.json','COLD_GARMENT_VALIDATION.json','ACTUAL_BONE_RENDER_PROOF.json','MOTION_RENDER.json','ENCODED_REVIEW_VALIDATION.json']:
 assert json.loads((E/name).read_text())['native_sha256']==native_sha,name
build=json.loads((E/'OUTFIT_RESTORATION_BUILD.json').read_text());r45=json.loads((ROOT/'locomotion/age10_animation_retarget_v045/evidence/RETARGET_BUILD.json').read_text())
expected={
 'locomotion/neck_collar_connection_v041/native/WTSC_Neck_Collar_Connection_Candidate_v041.blend':'c9806d2d905168f9e1ff2adbc20842ac298e37def9f37223d228639f414b931c',
 'locomotion/character_design_finish_v040/native/WTSC_Painted_Character_Look_STUDY_v040.blend':'cfa9827e8caecdb66271eb46b63d6d5e9a998c0dbba69380f53f7f5d6f7cf503',
 'locomotion/supported_recovery_v007/native/WTSC_Supported_Recovery_v007.blend':'77f253b88300415ce13cf4710455174f9afc64366b6dd361416703362b8788de',
 'shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend':'f4972ea64ceab1c8c88f1c77ed6875f373daac81c007492e4adddfb3660fb661',
 'locomotion/character_design_finish_v040/textures/WTSC_Boy_Painted_Parts_Atlas_v040.png':'6b1bf80d09f1de01a4664a6d73a873e5237ab1c73c7ae781bca6908dddd79121',
 'locomotion/age10_proportion_candidate_v044/native/WTSC_Age10_Static_Proportion_Candidate_v044.blend':r45['static_source_sha256'],
 'locomotion/age10_animation_retarget_v045/native/WTSC_Age10_Walk_Retarget_Proof_v045.blend':build['source_sha256']}
sources=[]
for rel,old in expected.items():
 f=ROOT/rel;now=sha(f);sources.append({'path':rel,'expected_sha256':old,'actual_sha256':now,'unchanged':old==now});assert old==now,rel
(E/'SOURCE_INTEGRITY.json').write_text(json.dumps({'all_seven_sources_unchanged':True,'sources':sources,'current_native_sha256':native_sha},indent=2))
assessment={'status':'Unapproved standalone age-ten walking and painted-outfit checkpoint. Not final animation.','source_assumption':'Earlier liked look interpreted as v040/v041; exact older version was not named.','visual_review_method':'Inspected native full-size F1/F9/F17/F25, actual-bone board, all31 local-cycle integer poses in three contact sheets, and12 selected decoded preview frames. Agent did not observe continuous player playback.','fixed':['Transparent garment origins now sort coat over thighs and collar over coat without moving world geometry.','Native painted bodice registration is feathered; hard rectangular chest patches removed.','Original detached sleeve armhole covered with existing cloth painting so moving shoulder does not reveal a second empty cavity.','Girl stocking UV rows map knee-to-cuff on actual shin; old cuff pixels no longer run through entire leg.','Retained richer cloth, buttons, pockets, sleeve rolls and original painted hand silhouettes on corrected anatomy.'],'remaining_artistic_work':['Girl retains old charcoal face, white eye and rigid braid; visual finish differs from full-color boy.','Planar fixed profiles and rigid painted hands need expressive drawing changes and finger intentions.','Cloth needs authored secondary motion and settling.','Shot-specific fatigue, load-bearing clasp and recovery-to-walk restart are not authored here.','Actual production camera/world-light integration remains separate; technical contacts are not artistic approval.'],'next_priority':'Unify girl painting and secondary cloth/braid movement while preserving validated scale and contacts; then author shot-specific recovery and support acting.','technical_validation_separate':True,'preview_below_20_MB':True,'no_production_overwrite':True}
(E/'ARTISTIC_ASSESSMENT.json').write_text(json.dumps(assessment,indent=2))
files=[native,P/'IMPORT_TIMING_GUIDE_v046.txt']
files += [P/'scripts'/n for n in ['build_outfits.py','cold_validate.py','render_comparison.py','render_motion.py','encode_review.py','prepare_delivery.py']]
files += [E/n for n in ['OUTFIT_RESTORATION_BUILD.json','COLD_CONTACT_VALIDATION.json','COLD_GARMENT_VALIDATION.json','ACTUAL_BONE_RENDER_PROOF.json','MOTION_RENDER.json','ENCODED_REVIEW_VALIDATION.json','TRAVEL_CURVE_v046.csv','SOURCE_INTEGRITY.json','ARTISTIC_ASSESSMENT.json','LIBRARY_VERIFIED_LIBRARY_PREVIEW_CREATE_RESULT.json']]
files += [V/n for n in ['WTSC_Age10_Painted_Outfits_v046_NormalSpeed.mp4','WTSC_Painted_Outfits_Actual_Bones_v046.png','RESTORED_DRESSED_F1.png','RESTORED_DRESSED_F09.png','RESTORED_DRESSED_F17.png','RESTORED_DRESSED_F25.png','ACTUAL_CORRECTED_BONES_F1.png','RESTORED_WITH_ACTUAL_BONES_F1.png','ENCODED_MOTION_CONTACT_SHEET_v046.jpg']]
manifest=[{'path':str(f.relative_to(P)).replace('\\','/'),'bytes':f.stat().st_size,'sha256':sha(f)} for f in files];(E/'DELIVERY_MANIFEST.json').write_text(json.dumps(manifest,indent=2));files.append(E/'DELIVERY_MANIFEST.json')
archive=P/'WTSC_Age10_Painted_Outfit_Restoration_v046.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in files:z.write(f,str(f.relative_to(P)))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None;assert len(z.namelist())==len(files)
receipt={'native_file':str(native),'native_bytes':native.stat().st_size,'native_sha256':native_sha,'archive':str(archive),'archive_bytes':archive.stat().st_size,'archive_sha256':sha(archive),'archive_file_count':len(files),'all_archive_crcs_pass':True,'all_seven_source_hashes_unchanged':True,'library_preview':json.loads((E/'LIBRARY_VERIFIED_LIBRARY_PREVIEW_CREATE_RESULT.json').read_text()),'status':'Separate development checkpoint; actual preview delivered. Girl finish, secondary motion and recovery acting remain artistic work, not pending technical failures.'}
(E/'FINAL_HANDOFF.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
