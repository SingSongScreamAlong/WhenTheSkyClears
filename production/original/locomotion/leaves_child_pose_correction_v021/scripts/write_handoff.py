"""Generate the bounded v021 handoff from actual saved-pose evidence."""
from pathlib import Path
import json,csv,hashlib,shutil
P=Path(__file__).resolve().parents[1]; ROOT=P.parents[1]
def read(n):return json.loads((P/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sol=read('evidence/coherent_pose_solution.json'); rows=read('evidence/authored_native_poses.json'); comp=read('evidence/v020_v021_angle_comparison.json'); art=read('evidence/art_variant_definition_and_check.json'); fresh=read('evidence/fresh_base_pose_check.json'); tests=read('evidence/final_native_variants_check.json'); old=read('reference/v020_eight_pose_matching.json'); S=sol['cycle_stride_m']
movie=read('evidence/library_movie_receipt.json'); images=read('evidence/library_images_receipt.json')
libs=[*movie['results'],*images['results']]
assert len(libs)==3 and all(r['status']=='succeeded' for r in libs)
protected=read('evidence/source_hashes_start.json')
protected.update({
 str(ROOT/'shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend'):'f4972ea64ceab1c8c88f1c77ed6875f373daac81c007492e4adddfb3660fb661',
 str(ROOT/'locomotion/supported_recovery_v007/native/WTSC_Supported_Recovery_v007.blend'):'77f253b88300415ce13cf4710455174f9afc64366b6dd361416703362b8788de',
 str(ROOT/'shots/world/WTSC_Open_Battlefield_Art_Study_v045c.blend'):'5dd333d28452e1427daf828711c3a6ac9abee5223d69090623e92e53e8583fb4'})
pres=[{'path':p,'expected_sha256':h,'actual_sha256':sha(Path(p)),'unchanged':sha(Path(p))==h} for p,h in protected.items()]
(P/'evidence/source_preservation_final.json').write_text(json.dumps(pres,indent=2))
assert all(r['unchanged'] for r in pres),'Protected-source hash changed; investigate rather than claiming preservation.'
assert sha(P/'reference/BASE_EIGHTPOSE_SOURCE_v020_COPY.blend')==list(protected.values())[0]
maxres=max(q['source_angle_residual_deg'] for r in rows[:8] for q in r['leg_residuals'])
minsw=min(q['actual_sole_min_z_m'] for r in rows[:8] for q in r['foot'] if q['mode']=='SWING')
maxcontact=max(q['active_contact_error_m'] for r in rows for q in r['foot'] if q['active_contact_error_m'] is not None)
with (P/'V021_PHASE_TRAVEL_AND_SUPPORT_KEYS.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['phase','source_frame_unwrapped_30fps','study_frame_30fps','seconds_from_contact','nominal_travel_x_m','hip_world_x_m','hip_world_z_m','hip_local_x_m','hip_local_z_m','near_mode','near_ankle_x_m','near_ankle_z_m','near_pitch_rad','near_active_vertex','near_anchor_x_m','near_anchor_z_m','far_mode','far_ankle_x_m','far_ankle_z_m','far_pitch_rad','far_active_vertex','far_anchor_x_m','far_anchor_z_m'])
 for p,r in zip(sol['poses'],rows[:8]):
  out=[p['name'],p['unwrapped_source_frame'],p['study_frame_30fps'],p['seconds_from_study_contact'],p['root_travel_m'],*p['hip_world_xz'],r['hip_local'][0],r['hip_local'][2]]
  for side in ['near','far']:
   d=p['feet'][side];out.extend([d['mode'],*d['ankle_xz'],d['angle_rad'],d.get('vertex',''),*d.get('anchor_xz',['',''])])
  w.writerow(out)
 # Bookend is represented fully in authored_native_poses.json, including actual feet.
with (P/'V021_REFERENCE_ANGLE_RESIDUALS.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['phase','v020_largest_leg_error_deg','v021_largest_leg_error_deg','near_thigh_deg','near_shin_deg','far_thigh_deg','far_shin_deg'])
 for r in comp:w.writerow([r['phase'],r['v020_max_leg_error_deg'],r['v021_max_leg_error_deg'],*[q['source_angle_residual_deg'] for q in r['v021_residuals']]])
table='\n'.join('%-12s %6.2f -> %5.2f degrees'%(r['phase'],r['v020_max_leg_error_deg'],r['v021_max_leg_error_deg']) for r in comp)
guide=f"""WTSC v021 IMPORT AND REVIEW GUIDE — BOUNDED POSE CHECKPOINT
Status: mechanics proof plus separate one-pose art study. Artistic acceptance remains OPEN.
This supersedes inherited v020 notes inside these copies. Do not integrate automatically.

FILES AND REVIEW
native/WTSC_Child_Coherent_Support_Eight_Poses_v021.blend
  Collection WTSC_CHILD_SUPPORT_POSES_v021.
native/WTSC_Child_Passing_Whole_Pose_Art_Study_v021.blend
  Collection WTSC_CHILD_PASSING_ART_VARIANT_v021.
These are independent alternatives. Do not append both into production as one rig.
Open with Blender 5.2.2 LTS. Packed original painting, native IK/constraints/drivers and editable geometry are retained. No frame handlers or external scripts are required for playback.
The source FBX 52-bone rig/action remains in the native file for inspection. Source/child skeleton preview collections are hidden for normal painted review. Toggle their viewport visibility and painted meshes deliberately when inspecting skeletons.

TIMING — EXACT SELECTED PHASES, NOT IN-BETWEENS
Study FPS30, frame1 right contact, frame32 duplicate contact one cycle later.
Source FPS30, original keys2..33, period31 frames=1.033333333s.
Study frame = source unwrapped frame -8.75.
"""
guide+='\n'.join(f"{p['name']:12s} source {p['unwrapped_source_frame']:6.2f} (wrapped {p['wrapped_source_frame']:5.2f}) -> study {p['study_frame_30fps']:5.2f}, +{p['seconds_from_study_contact']:.9f}s" for p in sol['poses'])
guide+=f"""

All child pose, support-mode and travel keys use CONSTANT interpolation. Exact fractional frames matter: use scene.frame_set(int(f), subframe=f-int(f)) for scripts. Integer-only timeline scrubbing omits some selected poses.
The MP4 holds each of these eight phases for0.5s, then the art comparison for1s. Its5s duration is a review presentation, not the gait timing. It does not show a continuous walk.

TRAVEL AND SUPPORT CONTRACT
Units metres; +X travel, +Z up, depthY. Native child near leg maps sourceR; far maps sourceL. Source -Y was mapped to child+X.
Alternating flat step distances: {sol['steps_m'][0]:.12f}m and {sol['steps_m'][1]:.12f}m.
Cycle stride S={S:.12f}m, versus v0201.021383492060m.
The nominal reference envelope is D(source_f)=S*(source_f-9.75)/31,
equivalently D(study_f)=S*(study_f-1)/31, nominal speed {S/(31/30):.12f}m/s.
The native V021 | CHILD_SUPPORT_TRAVEL has sampled CONSTANT keys on that envelope.
Do not interpret those held keys as a finished continuous root curve.

HIP is independently authored: hip_world = (D,0,0) + HIP_local.
Use the CSV for exact per-pose root, hip, ankle, boot pitch and active polygon contact anchor; full JSON contains rocker anchors and original hull coordinates.
Do not restore the adult stride, scale the child bones, clamp HIP onto the feet after posing, or move only the travel empty: boot goals and source/preview staging have independent world transforms.
The contact COPY_TRANSFORMS constraint uses V020 | side | SOLE_BONE_GOAL under ACTUAL_SOLE_PIVOT; the swing constraint uses SWING_BONE_GOAL. The V020 names are retained ABI names.
Native pivot active_vertex is inspection metadata; the keyed goal matrices are the controlling transforms.
For a future scene transfer, append the chosen whole collection into a disposable scene. Apply one common rigid placement transform to all its independent top-level roots/controls, including foot targets, without double-transforming descendants. Check the actual painted sole polygon against the destination ground at every selected phase.
This version supplies exact sampled placements and a nominal envelope only. Continuous heel/toe roll transitions, take-off/landing arcs, velocity, easing and world matching must be authored and reviewed before any production replacement.
No frame mapping into production75–80s is authorized by this checkpoint. Full-trailer duration/music/title/FX are untouched.

ONE-POSE ART VARIANT
L_PASSING: source34(wrapped3), study25.25.
V021 | PASSING ART CORRECTIVE | amount is1 only for that selected pose and0 at the other seven. Its held interval until the next key is a pose-study convenience, not a valid animation blend.
Two additive Geometry Nodes offsets on LOCO_BOY | PAINT body and V007_BOY | drawn leg near. Original base vertex coordinates, topology, UVs, weights, materials and painted image are unchanged. Hip/boot collar rows and head are untouched.
Mute the two V021 one-pose painted contour offset modifiers or set amount0 with the action disabled to compare the unchanged base.
The art file is a separate study; preserve the mechanics file as the clean baseline.

REBUILD / EVIDENCE
The editable blend files are self-contained. Rebuilding uses scripts/build_corrected.py then art_variant.py with the local reference/BASE_EIGHTPOSE_SOURCE_v020_COPY.blend and JSON inputs. The optional solve_poses.py uses existing numpy, no SciPy or installs.
build_corrected.py also renders48 small frames; do not run it during a heavy world/FX render. Use one Blender job, threads2. make_previews.py uses the included reference/V020_COMPARISON stills to rebuild the mechanics board; the final boards/movie and their current render inputs are included.
Evidence: coherent_pose_solution.json, authored_native_poses.json, fresh_base_pose_check.json, final_native_variants_check.json, art_variant_definition_and_check.json, source_preservation_final.json.
Read V021_RESOLVED_AND_REMAINING_REPORT.txt before interpreting any numeric PASS.
"""
(P/'V021_IMPORT_AND_REVIEW_GUIDE.txt').write_text(guide,encoding='utf-8')
report=f"""WTSC v021 RESOLVED AND REMAINING — 2026-10-18
Scope completed: a bounded correction of the existing eight child poses at unchanged source phases, followed by one small separate geometry art variant. STOPPED before continuous animation and world integration.

WHAT CHANGED
The v020 adult leg-mean scale produced a1.021383492m cycle and required a28.89mm3D pelvis accommodation at L_CONTACT. v021 solves alternating step placements, free pelvisX/Z, support geometry and swing pose together using the original asymmetric child segment lengths and actual rigid boot polygons. No after-fit pelvis projection or limb stretch.
Stride is now{S:.9f}m ({100*(1-S/old[0]['child_stride_m']):.2f}% shorter). This is reach-adapted reference blocking, not a declaration that this cadence/stride is right for the child's acting.
Second-landing hipZ rises from{old[4]['hip_fitted'][2]:.6f}m to{sol['poses'][4]['hip_world_xz'][1]:.6f}m. It remains{1000*(old[4]['hip_wanted'][2]-sol['poses'][4]['hip_world_xz'][1]):.2f}mm below the old unfitted source target rather than{1000*(old[4]['hip_wanted'][2]-old[4]['hip_fitted'][2]):.2f}mm. The former29mm3D accommodation is removed as an operation by changing the coherent target trajectory; it has not become a zero-error reproduction of the old target.
Second loading hipZ is{sol['poses'][5]['hip_world_xz'][1]:.6f}m versus v020{old[5]['hip_fitted'][2]:.6f}m.
The large near-shin source discrepancy at second landing/loading falls from about18.15/18.17deg to2.53/3.60deg.
Largest actual native thigh/shin direction residual per phase:
{table}
All sampled swing soles now clear ground by22.00–60.08mm; the previously grazing L_UP boot clears22.00mm. Boot pitch adapts to the child's original boot length: not a literal adult-foot copy.
Pelvis lowering/contact, support-leg reach and torso placement are coherent selected poses. The hip is not rigidly locked to either foot.

TECHNICAL TESTS — PASS WITH NARROW SCOPE
Fresh saved native files: all four child IK chains reachable; original rest bone lengths unchanged; max active painted-sole contact error{maxcontact:.3g}m.
Duplicate cycle-end painted mesh matches the first pose plus stride within{tests['duplicate_bookend_relative_mesh_error_m']:.3g}m.
Art variant skeleton matrices and boot vertices equal mechanics baseline exactly at all eight phases. Other seven poses have zero mesh effect. Original base vertices/UVs/weights/materials retained.
Actual MP4 decoded:150 frames,30fps,1920x960,5s,{read('evidence/preview_verification.json')['bytes']}bytes,9unique slides checked. All three private Library creates succeeded at version0.
Five protected source files retain their expected SHA256 values, including v020/v017 assets and v046/v007/v045c production sources.
These tests establish reproducible poses/contacts/proportions/export, not convincing animation.

ARTISTIC ASSESSMENT — STILL UNPASSED
The second landing no longer reads as the same compressed retarget failure; swing separation is clearer. The painted body still reads as a rigid cutout over articulated strips. Upper-body reference angles and arms are not a new acting pass.
The largest reference leg difference remains{maxres:.2f}deg at R_LOADING, and L_UP remains6.70deg. First UP pelvis is{1000*(sol['hip_heights_m'][3]-sol['hip_heights_m'][7]):.2f}mm higher than second UP; first loading drop5.15mm versus second0.66mm. These asymmetries need an artistic choice before an animation pass. They are not hidden by averaging.
The adult source period is still retained (about116steps/min). Contact onsets are inferred from ankle/toe behavior because the FBX has no heel or painted sole. Child character intent and timing remain unapproved.
No sampled test establishes center-of-mass dynamics, continuous non-slip support, convincing weight transfer at speed, in-between shape or recovery-to-walking performance.
The source, unchanged child skeleton and painting are presented at the same actual source phases and original camera size; source adult height is not normalized to imitate a proportion match.

SEPARATE WHOLE-POSE ART TEST
Worst exposed passing choice: L_PASSING/source34/study25.25. The torso/waist/hem and near knee/calf were adjusted together with two small additive geometry offsets; no skeleton, travel, foot, head or paint redesign.
Max evaluated body change{max(r['mesh_delta_m']['LOCO_BOY | PAINT body'] for r in art['poses'])*1000:.2f}mm; near-leg change{max(r['mesh_delta_m']['V007_BOY | drawn leg near'] for r in art['poses'])*1000:.2f}mm. The leg method includes a6mm outer-cap intent and4mm posterior-calf intent; actual net displacement is measured after the original shape blending.
The waist/hem softens modestly and the knee contour rounds slightly at close size. At shot size this is a limited gain. The baked calf band and rigid cloth drawing remain conspicuous. This is not an art pass or proof of deep cloth folds/folded-arm performance.
Boy profile/hair painting is preserved. No flat head card was turned edge-on, and rejected v008 was not reused. Girl, helping/clasp acting and original75–80s restart are outside this bounded checkpoint.

WORKFLOW / RESOURCES
Reused the user's exact Animation Base Locomotion v3 FBX through the existing v020 native source and the retained v017 painted control asset. FBX identity SHA2564e5d8bac507f1b9b43c5c20326a47f287c2e84d362a5613501add4eaccb9571b; no asset acquisition or external sharing.
Actual Blender5.2.2LTS(d13f752e3b9c), native bpy fallback; no typed DCC tool available. Do not claim MCP real-host acceptance. The substantive DCC production guide is retained with evidence.
One Blender job at a time, threads2, EEVEE32,640x360 mechanical views and960x540 art comparisons. No definite competing-render blocker observed. Production, world/art specialists' files, duration, music, title and explosion work were not modified.
No execution blocker remains. Artistic acceptance is pending review; no continuous animation/integration was attempted.
"""
(P/'V021_RESOLVED_AND_REMAINING_REPORT.txt').write_text(report,encoding='utf-8')
recipe={'workflow':'reuse existing source and painted native control asset; bounded child pose correction','runtime':'Blender5.2.2LTS native bpy fallback, no DCC real-host acceptance claimed','source_fbx_sha256':'4e5d8bac507f1b9b43c5c20326a47f287c2e84d362a5613501add4eaccb9571b','local_base_sha256':sha(P/'reference/BASE_EIGHTPOSE_SOURCE_v020_COPY.blend'),'stages':['solve_poses.py (optional existing numpy)','build_corrected.py','art_variant.py','final_native_check.py','make_previews.py','write_handoff.py','annotate_native.py'],'asset_policy':'Reuse user-selected source and original packed painting; no acquisition/install/upload of source FBX','review_status':'Technical selected-pose tests pass; artistic quality remains unapproved; no continuous gait or integration'}
(P/'evidence/reuse_recipe_and_host_evidence.json').write_text(json.dumps(recipe,indent=2))
handoff={'status':'BOUNDED_POSE_CORRECTION_COMPLETE_ART_UNPASSED','continuous_animation':'NOT_STARTED','production_integration':'NOT_STARTED','stride_m':S,'period_s':31/30,'max_native_leg_source_residual_deg':maxres,'minimum_sampled_swing_sole_clearance_m':minsw,'technical_checks':tests,'private_previews':[{'file':r['file_name'],'library_file_id':r['library_file_id'],'file_id':r['file_id'],'version':r['current_version_number']} for r in libs],'native_assets':['native/WTSC_Child_Coherent_Support_Eight_Poses_v021.blend','native/WTSC_Child_Passing_Whole_Pose_Art_Study_v021.blend'],'guide':'V021_IMPORT_AND_REVIEW_GUIDE.txt','assessment':'V021_RESOLVED_AND_REMAINING_REPORT.txt','remaining':['7.33deg worst source leg residual','11.48mm UP-height asymmetry','adult source cadence and child intention not accepted','rigid torso/cloth and calf paint band remain','continuous weight transfer/recovery transition not authored'],'execution_blockers':[]}
(P/'evidence/FINAL_HANDOFF_v021.json').write_text(json.dumps(handoff,indent=2))
print(json.dumps({'guide':'written','report':'written','private_preview_ids':[r['library_file_id'] for r in libs],'sources_unchanged':all(r['unchanged'] for r in pres),'max_angle_residual_deg':maxres,'min_swing_m':minsw}))

