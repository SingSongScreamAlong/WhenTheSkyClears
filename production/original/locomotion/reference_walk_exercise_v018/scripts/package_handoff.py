from pathlib import Path
import json,hashlib,csv,zipfile
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];E=P/'evidence';summary=json.loads((E/'validation_summary.json').read_text());append=json.loads((E/'fresh_append_validation.json').read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
start=json.loads((E/'source_hashes.json').read_text());preserved=[{'path':p,'before':h,'after':sha(Path(p)),'unchanged':sha(Path(p))==h} for p,h in start.items()]
originals={'shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend':'f4972ea64ceab1c8c88f1c77ed6875f373daac81c007492e4adddfb3660fb661','locomotion/supported_recovery_v007/native/WTSC_Supported_Recovery_v007.blend':'77f253b88300415ce13cf4710455174f9afc64366b6dd361416703362b8788de','shots/world/WTSC_Open_Battlefield_Art_Study_v045c.blend':'5dd333d28452e1427daf828711c3a6ac9abee5223d69090623e92e53e8583fb4'}
for name,h in originals.items():
 p=ROOT/name;actual=sha(p);preserved.append({'path':str(p),'previous_verified_sha256':h,'after':actual,'unchanged':actual==h})
(E/'source_preservation_final.json').write_text(json.dumps(preserved,indent=2))
receipts=[]
for name in ['library_movies_receipt.json','library_images_receipt.json']:receipts+=json.loads((E/name).read_text())['results']
(E/'private_library_receipts.json').write_text(json.dumps({'results':receipts,'metadata_note':'Current official helper was invoked on each original after upload. Windows Python lacks os.setxattr; local xattrs failed. Library creates succeeded, exact identities retained in these receipts.','prepared_path':'Current helper read-only discovery found prepare/finalize unavailable; no prepared session started. Direct small-file fallback used.'},indent=2))
with (P/'TRAVEL_CURVE_v018.csv').open('w',newline='') as out:
 w=csv.writer(out);w.writerow(['source_frame','seconds_from_frame_1','travel_x_m','speed_m_per_s'])
 for i in range(769):
  f=1+i/16;w.writerow([f,(f-1)/24,.44*(f-1)/24,.44])
technical='PASS' if summary['technical_status']=='PASS' and append['status']=='PASS' and all(x['unchanged'] for x in preserved) else 'FAIL'
assessment={'technical_status':technical,'artistic_status':'UNPASSED; INDEPENDENT REVIEW REQUIRED','review_method':'Actual PNG key renders and twelve decoded chronological samples of the final encoded movie, plus painted contact/shot-size crops. No normal-speed video playback observation claimed.','observed_gains':['Actual rigid boot vertices support heel, flat sole and successive forefoot rolling contacts without repainting.','Two-frame double support gives a visible transfer before lift-off. Alternating passing silhouettes and opposed arms are authored on the source-proportion child.','Boy head remains the original right profile; hair and face silhouette do not undergo a turnaround.'],'remaining_visual_failures_or_limits':['Near/far hands merge into the coat in the forward-swing half, weakening arm separation. This is not a solved crossing-arm test.','Knees and calf bands still read as articulated cutout strips; the passing shapes retain an angular or rubbery quality.','The original drawn near/far leg reach differs. The asymmetric bounded hip path avoids stretch but can read as an uneven or tentative walk. Independent cadence review is needed.','Coat response remains restrained, and the torso can still feel like a rigid card. This is not finished character acting.','V017 deep compression cloth and extreme folded far-arm defects remain explicit FAIL criteria. This low-amplitude walk does not exercise, repair or waive them.','The girl head turnaround remains unresolved and excluded from this boy-profile test. No rejected v008 patch or edge-on head card was used.'],'stop_condition':'Stop here for independent review. Do not extend actions, paint new art, replace production animation or claim the recovery-to-walk shot is solved.'}
(E/'ARTISTIC_ASSESSMENT_v018.json').write_text(json.dumps(assessment,indent=2))
reuse={'contract':'dcc-mcp-production-reuse/v1','guide_shape_check':'guide_available true; substantive production reuse gate read in prior v017 work and retained unchanged here. Shape checker alone is not acceptance.','reuse':'Project-owned v017 painted control asset, original v015 packed source painting and existing native Blender IK/Geometry Nodes/shape drivers. No downloaded rig or third-party animation.','actual_host':'Blender5.2.2LTS d13f752e3b9c at verified local executable; background native bpy fallback. Typed DCC tools/CLI unavailable in this session. No claim of a DCC-MCP acceptance call.','bounded_external_discovery':'Prior v017 official extension/docs search and limitations retained in that checkpoint. This exercise uses existing project assets and the two user-supplied written reference articles.','fresh_host_checks':['native fresh saved-file evaluation','fresh append into empty scene','all target references linked','zero externally linked content datablocks','packed paint image','whole-study placement translation'], 'libraries_note':'Blender retains an unused append source Library bookkeeping record; linked_datablocks is empty. This is not a live external dependency.','scripts':'Native playback has no frame handlers. Included scripts reproduce/check locally from project-relative v017 source.'}
(E/'production_reuse_and_host_check.json').write_text(json.dumps(reuse,indent=2))
guide='''V018 BOY TRAVELLING WALK - IMPORT AND TIMING CONTRACT

STATUS
Isolated rig capability exercise, not final animation or trailer integration.
Technical checks PASS; artistic acceptance UNPASSED. Stop for independent review.

EDITABLE ASSETS
native/WTSC_Boy_Travelling_Walk_v018.blend is the continuous native asset.
native/WTSC_Boy_Travelling_Walk_Blocking_v018.blend retains the stepped keys.
The boy uses the original fifteen bones and four two-bone IK chains. Stretch is
disabled. All original boy base vertices, UVs, materials, skin weights, shape-key
data, rest bones and packed painting match v017. There is no new head view.

APPEND AND PLACE
Append collection WTSC_BOY_TRAVELLING_WALK_v018, including its nested world-contact
collection. Do not append just the armature or discard the contact goals.
The continuous file includes fixed inspection and following matched-size cameras.
Use V018 | EXERCISE_PLACEMENT | move whole study to translate the entire exercise.
Translation was checked on a fresh append. Preserve scale1 and the existing XZ
plane; rotation/scale changes are outside this acceptance test.
V018 | WORLD_TRAVEL | +X metres is parent of the existing source rig. HIP is a
separate relative body control. Native foot mode constraints operate in world
space against the contact goals. Original native geometry/shape drivers remain.
Playback needs no Python frame handler and no external linked asset.

EXACT TIMING AND TRAVEL
24fps. Frame1 is time0. One full translating gait cycle is24frames /1second.
Frames1,25,49 are the same character-relative pose. Displacement is+0.44m/cycle.
D(s)=0.44*(s-1)/24 metres along+X in the unchanged scene metre scale.
The preview renders frames1..48; frame49 is the duplicate relative bookend at
time2s and world displacement0.88m. TRAVEL_CURVE_v018.csv supplies1/16frame values.
The MP4 is a two-cycle travelling study; replay resets world position and numbered
ground markers. It is not a seamless fixed-world screen-position loop.

Near contacts:1,25,49. Far contacts:13,37; previous far contact is-11.
For contact C, phase q=s-C modulo24. Each flat landing ankle reference is
L(C)=D(C)+0.11m. Same-foot landing references advance0.44m; alternate steps0.22m.
q0 contact; q3 down/load; q6 passing; q9 up; q14 lift-off; q24 next contact.
Stance lasts14frames; swing lasts10. Both feet support during the two-frame
interval after each new contact. Peak authored sole clearance is0.055m.
The down/passing/up schedule and amplitudes are our proposals, not source presets.

ACTUAL SOLE CONTRACT - NO FLOOR FITTING OR BOOT REPAINT
evidence/actual_sole_pivots.json contains the flat bone matrix, all boot vertices,
actual active vertex IDs, fixed ground anchors and exact switch phases.
Near rocker uses source vertices56,46,42; far uses61,46. The uneven source soles
require a small forefoot pivot transition. Each active ground anchor stays fixed
until its next support vertex takes over at the exact polygon-edge angle.
Heel pitch eases-4deg to0 over q0..3; sole holds q3..9; forefoot roll eases0 to8deg
over q9..14. Contact targets are native pivot empties with child bone-matrix goals.
Ankle COPY_TRANSFORMS constraints select one contact or swing goal with CONSTANT
mode keys. Their world matrices coincide at each mode change. Swing uses dense
native location/quaternion keys at1/16frame; independent tests sample1/32frame.
Arm/body overlap is restrained: chest1frame, head2frames, lower arm1.5frames.

PRODUCTION MATCH REQUIREMENT - NOT APPLIED
This asset's root moves+D while its planted goals remain on fixed ground.
The matched camera follows+D, yielding centered character and ground moving-D.
Any future production use must preserve that same relative0.44m/s travel. Do not
keep an unrelated existing world pass and layer this D on top. In a screen-centered
representation, subtract D from both character and world-contact positions, and
move the visible ground by-D. The supplied following camera already demonstrates
the equivalent view without changing native contact coordinates.
If mapping source frame s to production frame F0+(s-1), keep24fps. A later approved
retime must remap all body, goal, mode and travel keys together. No production
start frame, recovery restart or variable-speed world curve is supplied/approved
by this loop. The existing75-80s scene and trailer timing have not been edited.

REVIEW LIMITS
See V018_CHECKPOINT_REPORT.txt and evidence/ARTISTIC_ASSESSMENT_v018.json.
Deep cloth compression and extreme folded/crossing arms remain failed capability
areas inherited from v017; absence from this small walk is not a pass. Do not
extend performance actions or paint new art before independent review.
'''
(P/'V018_IMPORT_AND_TIMING_GUIDE.txt').write_text(guide)
report='V018 BOY TRAVELLING WALK CHECKPOINT\n\nTechnical: '+technical+'. Artistic: UNPASSED; independent review required.\n\nBuilt a boy-only original-profile two-cycle travelling walk, after stepped actual-art key review. Preserved painting/proportions and every original boy mesh/UV/weight/rest-bone datum. No girl head-turn patch, new drawings or production edits. Blender5.2.2LTS d13f752e3b9c verified; one small EEVEE job at a time with two threads.\n\nMEASURED TECHNICAL EVIDENCE\n'+str(summary['sample_count'])+' independent samples at1/32frame plus mode boundaries. All four IK chains reachable; minimum extension margin '+format(summary['minimum_reach_margin_m']*1000,'.3f')+'mm. Max IK endpoint error '+format(summary['max_IK_endpoint_error_m']*1000,'.4f')+'mm. Max active contact error '+format(summary['max_fixed_contact_error_m']*1000,'.6f')+'mm. Worst floor penetration is numerical '+format(-summary['minimum_sole_height_m']*1000,'.6f')+'mm. Max swing clearance interpolation error '+format(summary['max_swing_clearance_error_m']*1000,'.4f')+'mm. No IK branch switches/stretch. Relative loop error below0.001mm at+0.44m and+0.88m. Fresh append passes, original packed painting retained, no linked content datablocks, no frame handlers. Whole-study placement translation max error below0.001mm.\n\nThe first swing sampling test failed at0.88mm deviation; keys were tightened before rendering. The initial append test misclassified an unused Library bookkeeping record as an external dependency; checking actual linked datablocks confirms none. Both initial results are retained in evidence. Numerical/projected face-sign counts include near-degenerate source boot triangles and are not an artistic acceptance test.\n\nARTISTIC ASSESSMENT\n'+'\n'.join('- '+s for s in assessment['observed_gains']+assessment['remaining_visual_failures_or_limits'])+'\n\nREVIEW METHOD\n'+assessment['review_method']+'\n\nPREVIEWS\nReview MP4:1920x640,24fps,48frames,2seconds,264992bytes.\nMatched-size MP4:960x540,24fps,48frames,2seconds,73996bytes.\nBoth are below20MB. Original100mm lens/sensor/shift framing is retained at half1080p resolution over neutral ground; this is not a world/art composite.\n\nPRIVATE LIBRARY IDENTITIES\n'+'\n'.join(r['file_name']+' | '+r['library_file_id']+' | '+r['file_id']+' | version'+str(r['current_version_number']) for r in receipts)+'\nLibrary saves succeeded. Local extended metadata writeback failed because Windows Python lacks os.setxattr; exact receipts retained.\n\nSOURCE SAFETY\nAll three v017 source hashes and the previously verified v046/v007/v045c native hashes remain unchanged. Full-trailer duration, music, titles and specialist FX files were not touched.\n\nNEXT GATE\n'+assessment['stop_condition']+'\n'
(P/'V018_CHECKPOINT_REPORT.txt').write_text(report)
handoff={'checkpoint':'v018','scope':'Isolated one-child original-profile travelling walk; rig capability test only','technical_status':technical,'artistic_status':assessment['artistic_status'],'native':str((P/'native/WTSC_Boy_Travelling_Walk_v018.blend').resolve()),'stepped_native':str((P/'native/WTSC_Boy_Travelling_Walk_Blocking_v018.blend').resolve()),'timing_guide':str((P/'V018_IMPORT_AND_TIMING_GUIDE.txt').resolve()),'travel_curve':str((P/'TRAVEL_CURVE_v018.csv').resolve()),'summary':summary,'fresh_append_status':append['status'],'private_library_files':[{k:r[k] for k in ['file_name','library_file_id','file_id','current_version_number','file_size_bytes']} for r in receipts],'originals_unchanged':all(x['unchanged'] for x in preserved),'remaining_blockers':'No execution blocker. Artistic acceptance pending independent review; deep cloth/crossing capabilities remain failed and girl turnaround unresolved. Do not extend actions or integrate production.','stop_for_independent_review':True}
(E/'FINAL_HANDOFF_v018.json').write_text(json.dumps(handoff,indent=2))
files=[]
for folder in ['native','scripts','evidence']:
 for p in (P/folder).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.blend1') and p.name!='dcc_agent_workflows.md':files.append(p)
files.extend([P/'V018_CHECKPOINT_REPORT.txt',P/'V018_IMPORT_AND_TIMING_GUIDE.txt',P/'TRAVEL_CURVE_v018.csv',P/'reference/SOURCE_LINKED_MOTION_NOTES_v018.txt',P/'reference/WRITTEN_REFERENCE_STUDY_v018.json'])
files.extend(p for p in (P/'previews').iterdir() if p.is_file() and p.suffix in ['.mp4','.jpg'])
archive=P/'WTSC_Boy_Travelling_Walk_Capability_v018.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for p in sorted(set(files)):z.write(p,p.relative_to(P))
with zipfile.ZipFile(archive) as z:bad=z.testzip();count=len(z.namelist())
package={'path':str(archive.resolve()),'bytes':archive.stat().st_size,'sha256':sha(archive),'files':count,'zip_test_bad_file':bad,'excluded':'Raw render sequences, reference illustration/GIF copies, current Library helper runtime, pycache and blend backups; saved native playback requires none.'};(E/'PACKAGE_v018.json').write_text(json.dumps(package,indent=2));print(json.dumps({'technical':technical,'all_sources_unchanged':all(x['unchanged'] for x in preserved),'package':package}))
if technical!='PASS' or bad:raise RuntimeError('Package gate failed')
