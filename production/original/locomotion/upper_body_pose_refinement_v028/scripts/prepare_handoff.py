from pathlib import Path
import hashlib,json,csv,zipfile,sys,math
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];sys.path.insert(0,str(P/'scripts'));import upper_body_model as M
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=json.loads((P/'evidence/V027_UPPER_BODY_SOURCE.json').read_text());body={r['frame']:r for r in source['rows']}
with (P/'reference/V027_TRAVEL_AND_SUPPORT_QUARTER_FRAMES.csv').open(newline='') as infile:base=list(csv.DictReader(infile))
with (P/'V028_TRAVEL_AND_SUPPORT_QUARTER_FRAMES.csv').open('w',newline='') as out:
    fields=list(base[0])+[s+'_'+n+'_degrees' for s in ['near','far'] for n in ['upper_arm','forearm','hand']];w=csv.DictWriter(out,fieldnames=fields);w.writeheader()
    for row in base:
        f=float(row['native_frame_30fps']);q=f-1;phase=1+q%31;r=body[phase];a=M.trunk_delta(q);head=r['chest_head'];neck=r['chest_tail'];dx=head[0]-neck[0];dz=head[2]-neck[2]
        row['chest_degrees']=float(row['chest_degrees'])+math.degrees(a);row['upper_origin_x_m']=float(row['root_x_m'])+neck[0]+math.cos(a)*dx+math.sin(a)*dz;row['upper_origin_z_m']=neck[2]-math.sin(a)*dx+math.cos(a)*dz
        for s in ['near','far']:
            for n,value in zip(['upper_arm','forearm','hand'],M.arm(s,q)):row[s+'_'+n+'_degrees']=math.degrees(value)
        w.writerow(row)
targets={'v046':('shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend','f4972ea64ceab1c8c88f1c77ed6875f373daac81c007492e4adddfb3660fb661'),'v007':('locomotion/supported_recovery_v007/native/WTSC_Supported_Recovery_v007.blend','77f253b88300415ce13cf4710455174f9afc64366b6dd361416703362b8788de'),'v045c':('shots/world/WTSC_Open_Battlefield_Art_Study_v045c.blend','5dd333d28452e1427daf828711c3a6ac9abee5223d69090623e92e53e8583fb4')}
checks={}
for name,(path,expected) in targets.items():
    actual=sha(ROOT/path);checks[name]={'path':path,'sha256':actual,'unchanged':actual==expected};assert actual==expected
original=P.parent/'body_loading_overlap_v027/native/WTSC_Body_Loading_Overlap_v027.blend';copy=P/'reference/PRESERVED_BASELINE_v027.blend';expected='f24114a894e777c7e1dcf2df87bb539e78eba2259c3a89098b94b8ccef98b139'
checks['v027_preserved_baseline']={'original_sha256':sha(original),'copy_sha256':sha(copy),'unchanged':sha(original)==sha(copy)==expected};assert checks['v027_preserved_baseline']['unchanged']
(P/'evidence/PROTECTED_SOURCE_HASHES.json').write_text(json.dumps(checks,indent=2))
preview=json.loads((P/'evidence/PREVIEW_VERIFICATION.json').read_text());native=P/'native/WTSC_Upper_Body_Pose_Refinement_v028.blend';technical=json.loads((P/'evidence/UPPER_BODY_AND_PRESERVATION_CHECKS.json').read_text());gate=json.loads((P/'evidence/POSE_REVIEW_GATE.json').read_text());receipt=json.loads((P/'evidence/LIBRARY_PREVIEW_RECEIPT.json').read_text())['structuredContent'];assert receipt['status']=='succeeded' and receipt['file_size_bytes']==preview['bytes']
assert preview['frames_decoded']==837 and preview['bytes']<20_000_000 and not preview['blue_fill_artifact_frames'] and not technical['unreachable_samples']
mesh_errors={name:max(r['preserved_mesh_errors_m'][name] for r in technical['quarter_frame_samples']) for name in technical['quarter_frame_samples'][0]['preserved_mesh_errors_m']}
handoff={'status':'FOCUSED_UPPER_BODY_COMPARISON_DELIVERED_ART_REVIEW_OPEN','native':str(native),'native_bytes':native.stat().st_size,'native_sha256':sha(native),'private_preview':receipt,'preview':preview,
    'changes':['Restrained trunk bend/release beneath preserved head, -1.6 to+.65degrees relative tov027','Individually authored near/far upper-arm and elbow-flex spacing','Forearm reversal delays1.5/1frames; hand delays.75/.5frames, relaxed wrist direction','Coat attachment/compression derived from changed body, <=5mm waist compression and small damped hem correction'],
    'pose_review_before_long_render':gate,'technical_safeguards_not_art_acceptance':{'first_cycle_samples':len(technical['quarter_frame_samples']),'later_contact_repeats':len(technical['late_cycles']),'max_preserved_mesh_errors_m':mesh_errors,'max_root_matrix_error':technical['max_root_matrix_error'],'max_head_world_control_matrix_error':technical['max_head_control_matrix_error'],'unreachable_samples':len(technical['unreachable_samples'])},
    'head_preservation':'HEAD_PROFILE is parented to CHEST. Its local keys compensate the changed parent so v027 world profile/head motion is preserved; actual deformed head checked in foreground view-layer depsgraph.',
    'actual_continuous_playback_observed':False,'visual_review':preview['visual_review_status'],'remaining_art':gate['observed_remaining_weaknesses']+gate['playback_uncertainties']+['This remains a repeated solo walk. Differentiated paired fatigue, support contact and recovery restart in75-80seconds are unfinished.'],
    'integration_contract':{'fps':30,'period_frames':31,'stride_m':.9524437384576381,'root':'D=.9524437384576381*(F-1)/31m +X, unwrapped','nominal_speed_mps':.9217197468944884,'near_contact_frame':1,'far_contact_frame':17,'foot_pelvis_root_trouser_curves_changed':False,'production_24fps_mapping':'F_native=1+phase_q+30*(F_film-F_film_start)/24; resample GP/drawing exposures, transform root AND separate world sole goals consistently'},
    'guide':'V028_VIEWING_AND_IMPORT_GUIDE.txt','travel_curve':'V028_TRAVEL_AND_SUPPORT_QUARTER_FRAMES.csv','source_preservation':checks,'render_coordination':'CPU-gated threads2, world task explicitly released slot. Small matched poses reviewed first. Long558frame render released immediately after Blender exit.','no_production_integration':True,
    'blockers':[{'action':'Observe continuous normal-speed playback for artistic acceptance','target':preview['filename'],'reason':'No observable running player is exposed in this task. All837frames decoded, actual encoded poses/joins inspected.','status':'PENDING_CONRAD_VIEWING_FEEDBACK','denied':False}]}
(P/'evidence/final_handoff.json').write_text(json.dumps(handoff,indent=2))
files=[p for folder in ['native','reference','scripts','evidence'] for p in (P/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ['.blend1','.pyc'] and p.name not in ['PACKAGE_RESULT.json','PACKAGE_MANIFEST.json']]
files.extend(p for p in P.iterdir() if p.is_file() and p.suffix in ['.txt','.csv']);files.extend(p for p in (P/'previews').iterdir() if p.is_file())
manifest=[{'path':p.relative_to(P).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(set(files))];mf=P/'evidence/PACKAGE_MANIFEST.json';mf.write_text(json.dumps(manifest,indent=2));z=P/'WTSC_Upper_Body_Pose_Refinement_v028.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
    for p in sorted(set(files+[mf])):archive.write(p,'upper_body_pose_refinement_v028/'+p.relative_to(P).as_posix())
with zipfile.ZipFile(z) as archive:
    assert archive.testzip() is None
    for r in manifest:assert hashlib.sha256(archive.read('upper_body_pose_refinement_v028/'+r['path'])).hexdigest()==r['sha256']
result={'package':str(z),'bytes':z.stat().st_size,'sha256':sha(z),'files':len(files)+1,'CRC_and_hashes':'PASS','raw_PNG_directories_included':False,'preview_bytes':preview['bytes'],'private_library_id':receipt['library_file_id'],'version':receipt['current_version_number']}
(P/'evidence/PACKAGE_RESULT.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
