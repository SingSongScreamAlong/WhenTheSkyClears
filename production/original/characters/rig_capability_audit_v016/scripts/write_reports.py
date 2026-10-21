import json,hashlib,csv,datetime
from pathlib import Path
P=Path(__file__).resolve().parents[1]
t=json.loads((P/'evidence/technical_validation.json').read_text());v=json.loads((P/'evidence/delivery_native_verification.json').read_text());movies=json.loads((P/'evidence/preview_verification.json').read_text());m=json.loads((P/'NATIVE_CONTROL_MAP_v016.json').read_text());c=json.loads((P/'evidence/painted_clearance_masks.json').read_text())
rows=v['fresh_saved_live_all96_frames'];maxik=max(x['max_IK_error_m'] for x in rows)*1000;gaps=[n*1000 for x in rows if x['brace_projected_gap_m'] for n in x['brace_projected_gap_m'].values()]
report=f'''v016 - PAINTED CHARACTER RIG CAPABILITY STUDY
Status: technical linkage demonstrated within tested ranges; FINAL-ART READINESS UNPASSED.

The concrete repair is on the actual painted children, not the v014 proxy. Sixteen limb/cuff surfaces previously ran on 120 cached drawings without following individual bones. They now use native pose-driven curved contours. The original 33 rest bones (boy 15/girl 18),28 painted meshes, UVs, topology, packed painting, body weights, boots and existing finger drawings are retained. No source or production file was overwritten.

Tested capabilities
- Native HIP/CHEST/HEAD controls, fixed-length leg/arm IK, independent wrist targets, relaxed-hand torso follow, near-thigh brace follow and independent Reach/Brace hand shapes. Blends normalize safely when both hand shapes are selected.
- Twelve actual-art tests: neutral, planted squat, off-cache intermediate, reach/deep elbow, heel/flat/toe/lift, thigh brace, opposed chest/head tilt, profile attention limit, crossed limbs and pair clearance at0.8m.
- All 16 contours respond to a new native HIP edit without the old drawing clock. Boot drift remains below0.001mm in that plant test. All four boots remain rigid and sole-fitted across the tested-15 to35 degree rolls.
- Both delivered natives were reopened with scripts disabled. The unkeyed asset has zero Actions and retains its control drivers. All 96 saved diagnostic frames pass: maximum IK endpoint error{maxik:.3f}mm; brace projected palm gap{min(gaps):.3f} to{max(gaps):.3f}mm; no plant drift. This measures planar drawing contact, not forces or a3D grasp.
- Original profile head/braid moves coherently under a 12 degree in-plane head edit. Separate braid and skirt controls were tested at +/-5 degrees: stable non-braid head vertices and no dress triangle inversions.
- Fresh native collection append passes. Original UVs, topology, body weights and rest-bone positions compare exactly. Known v007/v046/v045c source hashes remain unchanged.

Candid visual assessment / remaining defects
The linkage gap is repaired. The children are still not ready to call final animation assets. Cuffs remain boxy, crossed/deep elbows reveal construction, and knees/garment compression can read as bent strips rather than authored cloth volume. Fixed near/far layering is usable in the shown tests but needs pose-specific occlusion choices for extreme crossings. The tiny fingers are controllable drawings; they are not an arbitrary finger rig or an approved load-bearing clasp. The0.8m static offer keeps about{c['offer_hand']['approx_orthographic_gap_m']*1000:.1f}mm of visible fingertip separation.

The girl's required look back toward the boy is UNSOLVED. The delivered rig deliberately retains the original right profile, with in-plane pitch; it does not turn a flat card edge-on, substitute the v014 proxy, use a negative-scale snap or reuse rejected v008. There is no independent eye-gaze drawing control. The original v046 1844-45 disc defect is shown openly in the contact/head sheet. Keeping one profile avoids reproducing that defect in this rig test; it does not fulfil the story's attention turn.

Precise remaining art requirement: two matching registered girl quarter views between the original right profile, front passage and toward-boy left profile. Preserve the swept fringe, skull/cheek/jaw, eye/nose identity and anatomical braid origin. Use the original 1672x941 atlas registration or supply crop offsets. Source neck registration is approximately{[round(x,1) for x in m['characters']['GIRL']['neck_registration_source_px']]}; source braid root approximately{[round(x,1) for x in m['characters']['GIRL']['braid_root_source_px']]}. Tag the braid root deliberately in each new view; it need not stay at the same screen coordinate during a turn. These are concrete authoring requirements, not a request for user-supplied drawings before other rig work. New views still need design review and a fresh paired-clearance test.

Review method: native perturbation/append tests, actual painted renders, full movie decoding and chronological decoded-frame review. Normal-speed playback was not available to this agent. Technical passes are not artistic acceptance. Performance development and v015 inbetweens remain paused. No Mixamo/Synty motion was imported, no adapter was built, and setting/FX/music/title/duration/production integration were untouched.
'''
(P/'RIG_CAPABILITIES_AND_DEFECTS_v016.txt').write_text(report,encoding='utf-8')
guide='''v016 - IMPORT / POSING / TIMING GUIDE

Start with native/WTSC_Painted_Rig_Control_Asset_v016.blend. It is the editable unkeyed asset: no Actions, no runtime handler, no external plugin or image dependency. Blender 5.2.2 LTS was verified at WTSC_LOCAL_USER\\AppData\\Local\\Programs\\Blender\\blender-5.2.2-windows-x64\\blender.exe (build d13f752e3b9c).

Append exactly collection WTSC_PAINTED_RIG_CAPABILITY_v016, including all of its control/contour-anchor children. Keep both original armatures, their packed paint, Geometry Nodes groups, drivers and internal targets together. Append to a scratch scene first; no production replacement is authorized by this delivery. Do not copy v014's17-bone proxy Actions onto these original 15/18-bone rigs.

Native files and timing
- Control_Asset: one unkeyed neutral frame; primary posing asset.
- Capability: twelve stepped stress poses at 1,21,41,61,81,101,121,141,161,181,201,221; scene 1..240 at 24fps. This is a capability board, not a ten-second story sequence.
- Live_Diagnostic: frames 1..96 at 24fps (4s).1..24 native hip/foot plant,25..48 sole-aware roll,49..72 painted brace follow,73..96 profile head/braid pitch. These are separate test sections, not performance transitions.
- Inspection preview uses a simple orthographic 3m camera and 1.24m pair gap. Camera-matched preview uses the actual v046 frame 1844 lens 100mm, 36mm horizontal sensor, original lens shifts and camera relative to the pair root, plus the original 0.8m pair gap. It matches framing/scale, not the world lighting, atmosphere or setting.
- No timing in these files replaces 75..80 seconds of the trailer. There is no new recovery step or production travel curve in this rig-only phase. diagnostic_world_travel.csv explicitly records zero diagnostic travel.

Coordinates and controls
Metres, +X travel, +Z up, camera from-Y. In-plane card rotation is about worldY. WORLD_TRAVEL is separate from the children's HIP controls and is zero in all diagnostics. Rig roots are independently spaced; do not change character proportions to fit an imported skeleton.
For each BOY/GIRL, edit HIP, CHEST, HEAD_PROFILE, ANKLE_near/far, WRIST_near/far and LEG/ARM_POLE_near/far. Internal anchors/row attributes are construction dependencies. HIP moves the pelvis; CHEST and HEAD_PROFILE can counter-tilt independently. The original rig has no separate lumbar or neck bone. Braid and skirt_front/skirt_back remain original girl pose bones, with bounded5-degree tests supplied.
Native IK preserves original child-specific projected bone lengths. Poles must remain in the XZ drawing plane. Do not rotate the head card in yaw or roll it edge-on. Source near/far lengths are not assumed to be identical.

Hands
WRIST properties Reach/Brace select reused v007 finger drawings; zero/zero is Relax. Their effective weights normalize if their sum exceeds one. TorsoFollow 1 carries a relaxed hand with the chest; set 0 for an explicit wrist target. The calibrated BraceFollow control is implemented on the NEAR wrist only, and overrides it with the planar thigh anchor. BraceFollow on a far wrist has no follower implementation; far Brace is only a hand-shape choice.
BraceFollow is validated around the saved deep brace pose: boy HIP(.015,.435), girl HIP(.015,.415), chest 50 degrees, head 7 degrees, near flat ankleX.13/far-.10, with small combined hip changes. It is not a reach planner. Enabling it in an upright pose can exceed arm reach. No hand-to-hand helping load is claimed.

Foot placement / documented pose API
ANKLE targets are native and remain editable with the IK rig. For an exact source-sole heel/flat/toe placement, use embedded rig_pose_api.py. In Blender's Python Console:
  ns={}; exec(bpy.data.texts['rig_pose_api.py'].as_string(),ns)
  ns['initialize_from_scene']()
  ns['set_foot']('BOY','near',.13,20,0)
set_foot arguments are child, side, flat-ankle-X, roll degrees, actual sole lift. It uses the original source heel/toe reference and the actual native boot vertices for floor fitting. The boot is rigid; contact may roll over its curved sole. No deforming toe or exact physical force solver is implied.
set_wrist accepts child,side,X,Z,in-plane hand direction in degrees,shape. It rejects out-of-range arm targets by default. apply_pose is the diagnostic convenience authoring function; requested wrist positions can be fitted into the arm range and that adjustment is recorded. Use native IK endpoint checks before treating a pose as valid. See diagnostic_pose_manifest.json for actual fitted requests and NATIVE_CONTROL_MAP_v016.json for all source lengths/control names.

World travel contract for any later integration
For a rest-space painted vertex p, a single-bone part evaluates as:
  p_world = M_rig_world @ M_pose_bone @ inverse(M_rest_bone) @ p
M_rig_world includes WORLD_TRAVEL and that child's root spacing. The new contours read the same final skeleton/boot targets; they do not read a separate frame clock. If WORLD_TRAVEL moves while a foot is planted, set ANKLE.matrix_world to the desired fixed world foot-bone matrix each frame (equivalently local target=inverse(M_rig_world)@world_target). Merely moving WORLD_TRAVEL carries its child targets and will slide a nominally planted foot. A future motion/world adapter must supply that compensation and an exact travel curve; none is claimed built here.

Design limits and future source motion
The original right-profile art is the supported head view. Full turn and independent eye gaze remain unpassed; see the report and historical v046 defect witness. Extreme cuffs, deep garment compression and crossing occlusion require further local drawing/corrective review. New quarter views require design approval before a performance turn.
Potential future3D inputs may supply root/pelvis/spine/limb reference, but must be projected and re-solved to each child's lengths. Original lumbar/neck independence cannot be invented by renaming proxy bones. Keep head/profile, fingers, support contacts, braid, skirt and draw order as authored overrides. Existing Leaves/Synty sampling code was read as a reference only; no automatic2D retargeting compatibility or asset entitlement was established here.

Reproduction and preservation
scripts/build_rig_audit.py derives only this isolated folder from immutable v007. make_live_diagnostic.py writes the unkeyed/live assets; verify_delivery.py reopens them with scripts disabled and checks every diagnostic frame. Clear Actions with animation_data.action=None; do not call animation_data_clear on the control objects because that deletes their native follower drivers too. The exporter now preserves and verifies those drivers. Original v007, v046 and retained v045c hashes are verified in evidence/source_integrity.json.
'''
(P/'IMPORT_AND_POSING_GUIDE_v016.txt').write_text(guide,encoding='utf-8')
with (P/'evidence/diagnostic_world_travel.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['diagnostic_frame','seconds','world_travel_x_m','world_travel_z_m','scope']);w.writerows((i,(i-1)/24,0,0,'rig diagnostic only; no production replacement') for i in range(1,97))
assessment={'status':'FINAL_ART_READINESS_UNPASSED','technical_linkage':'PROVEN_WITHIN_TESTED_RANGES','actual_art_not_proxy':True,'visually_working':['Original character paint and profile identity retained','Contacts and planted source boots visible','New posed contours follow controls without cache','Head and attached braid in-plane continuity'],'visually_open_or_failed':['Boxy cuffs and constructed crossed/deep elbows','Tubular knee/cloth compression and stretched garment paint need authored correction','Fixed source near/far draw order needs per-pose extreme crossing review','Girl required look back is not supplied by retained profile','No independent eye-gaze drawing or arbitrary finger/grasp rig'],'normal_speed_review':False,'performance_approval':False,'production_integration':False,'historical_failed_head_visible_in_evidence':True}
(P/'evidence/artistic_assessment.json').write_text(json.dumps(assessment,indent=2))
handoff={'status':'RIG_AUDIT_AND_TARGETED_LINKAGE_FIX_DELIVERED; ART_READINESS_UNPASSED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Latest user direction: kids and rig first; performance paused','primary_asset':str((P/'native/WTSC_Painted_Rig_Control_Asset_v016.blend').resolve()),'report':str((P/'RIG_CAPABILITIES_AND_DEFECTS_v016.txt').resolve()),'guide':str((P/'IMPORT_AND_POSING_GUIDE_v016.txt').resolve()),'technical_gates':t['technical_gates'],'fresh_native_delivery_pass':v['technical_only_pass'],'max_live_IK_error_mm':maxik,'brace_gap_mm_range':[min(gaps),max(gaps)],'preview_verification':movies,'artistic_assessment':assessment,'library_uploads':'pending','blockers':[{'action':'Approve final girl look-back/turn capability','target':'Actual painted girl head/profile art','reason':'Two registered matching quarter views missing; original profile cannot express the required turn. Rejectedv008 not reused.','state':'unresolved art/design requirement, not an execution denial'}]}
(P/'evidence/final_handoff.json').write_text(json.dumps(handoff,indent=2))
(P/'evidence/CURRENT_REPAIR_CHECKPOINT.json').write_text(json.dumps(handoff,indent=2))
print('REPORTS_WRITTEN')
