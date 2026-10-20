from pathlib import Path
import hashlib,json,csv,zipfile,sys,math
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];sys.path.insert(0,str(P/'scripts'));import loading_model as M
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with (P/'V027_TRAVEL_AND_SUPPORT_QUARTER_FRAMES.csv').open('w',newline='') as out:
    w=csv.writer(out);w.writerow(['native_frame_30fps','elapsed_seconds','cycle_zero_based','phase_q','root_x_m','centered_world_scroll_x_m','hip_world_x_m','hip_z_m','upper_origin_x_m','upper_origin_z_m','chest_degrees','near_ankle_world_x_m','near_ankle_world_z_m','near_sole_rotation_radians','near_mode','far_ankle_world_x_m','far_ankle_world_z_m','far_sole_rotation_radians','far_mode','frame_in_movie_range'])
    for i in range(1117):
        q=i/4;r=M.evaluate(q);feet=r['feet'];w.writerow([1+q,q/30,math.floor(q/31),q%31,r['D'],-r['D'],*r['H'],*r['upper_origin'],math.degrees(r['chest']),*[v for s in ['near','far'] for v in [*feet[s]['A'],feet[s]['angle'],feet[s]['mode']]],q<279])
targets={'v046':('shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend','f4972ea64ceab1c8c88f1c77ed6875f373daac81c007492e4adddfb3660fb661'),'v007':('locomotion/supported_recovery_v007/native/WTSC_Supported_Recovery_v007.blend','77f253b88300415ce13cf4710455174f9afc64366b6dd361416703362b8788de'),'v045c':('shots/world/WTSC_Open_Battlefield_Art_Study_v045c.blend','5dd333d28452e1427daf828711c3a6ac9abee5223d69090623e92e53e8583fb4')}
checks={}
for name,(path,expected) in targets.items():
    actual=sha(ROOT/path);checks[name]={'path':path,'sha256':actual,'unchanged':actual==expected};assert actual==expected
original=P.parent/'gp_extended_review_v026/native/WTSC_GP_Extended_Review_v026.blend';copied=P/'reference/PRESERVED_BASELINE_v026.blend'
checks['v026_preserved_baseline']={'original_sha256':sha(original),'copy_sha256':sha(copied),'unchanged':sha(original)==sha(copied)};assert checks['v026_preserved_baseline']['unchanged']
(P/'evidence/PROTECTED_SOURCE_HASHES.json').write_text(json.dumps(checks,indent=2))
preview=json.loads((P/'evidence/PREVIEW_VERIFICATION.json').read_text());native=P/'native/WTSC_Body_Loading_Overlap_v027.blend';technical=json.loads((P/'evidence/LOADING_AND_CONTACT_CHECKS.json').read_text());receipt=json.loads((P/'evidence/LIBRARY_PREVIEW_RECEIPT.json').read_text())['structuredContent'];assert receipt['status']=='succeeded' and receipt['file_size_bytes']==preview['bytes']
assert preview['frames_decoded']==837 and preview['bytes']<20_000_000 and not preview['blue_fill_artifact_frames'] and not technical['unreachable_samples']
late_old=float(M.B.evaluate(26.25)['H'][0]-M.B.evaluate(24.25)['H'][0]-2*M.STRIDE/31);late_new=float(M.hip(26.25)[0]-M.hip(24.25)[0]-2*M.STRIDE/31)
handoff={'status':'FOCUSED_LOADING_COMPARISON_DELIVERED_ART_REVIEW_OPEN','baseline_human_assessment':'v026 directional improvement, about3/10; preserved, not approved final','native':str(native),'native_bytes':native.stat().st_size,'native_sha256':sha(native),'private_preview':receipt,'preview':preview,
    'two_visible_causes':technical['two_visible_causes'],'coherent_changes':technical['changes'],'spacing_example_F25p25_to_F27p25':{'v026_centered_hip_delta_m':late_old,'v027_centered_hip_delta_m':late_new},
    'technical_only':{'sample_count':len(technical['body_samples']),'late_contact_checks':len(technical['late_cycle_checks']),'max_actual_boot_change_m':technical['maximum_boot_change_m'],'max_world_sole_goal_matrix_change':technical['maximum_goal_matrix_change'],'max_final_cuff_row_change_m':technical['maximum_cuff_row_change_m'],'unreachable_samples':len(technical['unreachable_samples']),'head_mesh_unchanged':technical['original_head_mesh_unchanged'],'pelvis_low_frames':[3.75,19.75],'upper_mass_low_frames':[4.75,20.75]},
    'actual_continuous_playback_observed':False,'visual_review':preview['visual_review_status'],'artistic_assessment':'Clearer load/recovery separation and more consistent coat design are visible in matched poses. Naturalness/cadence over time is unapproved; repeated forward settle may still read as a nod. Requires Conrad playback feedback.',
    'remaining_art':['Same footfall schedule; this is changed body spacing, not a new temporal cadence.','Arm timing retained; shoulders/wrists may still require a focused pass.','Passive hem is simplified; no cloth/thigh collision simulation or individual collision drawings.','Painted surface/fold finish deferred until motion is accepted.','Paired fatigue/support, girl intention and recovery restart in the75-80second shot remain unfinished.'],
    'head_choice':'Preserve original painted profile and sagittal gaze orientation; translate through neck attachment, no turnaround or v008 patch.',
    'integration_contract':technical['integration'],'timing_guide':'V027_VIEWING_AND_IMPORT_GUIDE.txt','travel_curve':'V027_TRAVEL_AND_SUPPORT_QUARTER_FRAMES.csv','preservation':checks,
    'render_coordination':'World specialist explicitly released slot before558smallframes/threads2,174.5s. Blender exited and slot released immediately. No additional character render active/planned.',
    'initial_proof_correction':'Copied GP fill_color was an invalid view after source drawings were removed. Converted it to an owned tuple, rebuilt from immutable baseline, re-rendered/reviewed all32proof frames. Initial bad proof retained outside package.',
    'no_production_integration':True,'blockers':[{'action':'Observe continuous normal-speed playback for artistic acceptance','target':preview['filename'],'reason':'No observable running player is exposed through the available task tools. All837frames decoded and selected actual encoded frames/boards inspected.','status':'PENDING_HUMAN_VIEWING_FEEDBACK','denied':False}]}
(P/'evidence/final_handoff.json').write_text(json.dumps(handoff,indent=2))
files=[p for folder in ['native','reference','scripts','evidence'] for p in (P/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.blend1','.pyc'] and p.name not in ['PACKAGE_RESULT.json','PACKAGE_MANIFEST.json']]
files.extend(p for p in P.iterdir() if p.is_file() and p.suffix in ['.txt','.csv']);files.extend(p for p in (P/'previews').iterdir() if p.is_file())
manifest=[{'path':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(set(files))];mf=P/'evidence/PACKAGE_MANIFEST.json';mf.write_text(json.dumps(manifest,indent=2));z=P/'WTSC_Body_Loading_Overlap_v027.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for p in sorted(set(files+[mf])):archive.write(p,'body_loading_overlap_v027/'+p.relative_to(P).as_posix())
with zipfile.ZipFile(z) as archive:
    assert archive.testzip() is None
    for r in manifest:assert hashlib.sha256(archive.read('body_loading_overlap_v027/'+r['path'])).hexdigest()==r['sha256']
result={'package':str(z),'bytes':z.stat().st_size,'sha256':sha(z),'files':len(files)+1,'CRC_and_hashes':'PASS','raw_PNG_directories_included':False,'preview_bytes':preview['bytes'],'private_library_id':receipt['library_file_id'],'version':receipt['current_version_number']}
(P/'evidence/PACKAGE_RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
