from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
def J(n):return json.loads((P/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
check=J('evidence/fresh_native_preservation_check.json');defs=J('evidence/corrective_definitions.json');preview=J('evidence/preview_verification.json');lib=J('evidence/private_library_receipt.json');base=J('evidence/reuse_scope_and_host_evidence.json')
assert check['status']=='PASS' and len(lib['results'])==1 and lib['results'][0]['status']=='succeeded'
protected={
 str(ROOT/'locomotion/leaves_child_pose_correction_v021/native/WTSC_Child_Coherent_Support_Eight_Poses_v021.blend'):base['v021_baseline']['sha256'],
 str(ROOT/'shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend'):'f4972ea64ceab1c8c88f1c77ed6875f373daac81c007492e4adddfb3660fb661',
 str(ROOT/'locomotion/supported_recovery_v007/native/WTSC_Supported_Recovery_v007.blend'):'77f253b88300415ce13cf4710455174f9afc64366b6dd361416703362b8788de',
 str(ROOT/'shots/world/WTSC_Open_Battlefield_Art_Study_v045c.blend'):'5dd333d28452e1427daf828711c3a6ac9abee5223d69090623e92e53e8583fb4'}
pres=[{'path':p,'expected_sha256':h,'actual_sha256':sha(Path(p)),'unchanged':sha(Path(p))==h} for p,h in protected.items()]
assert all(x['unchanged'] for x in pres);assert sha(P/'reference/BASE_COHERENT_SUPPORT_v021_COPY.blend')==base['v021_baseline']['sha256']
(P/'evidence/source_preservation_final.json').write_text(json.dumps(pres,indent=2))
guide="""WTSC v022 WHOLE PAINTED POSE CORRECTIVES — REVIEW / EDIT GUIDE
Status: bounded two-pose visual study; partial visual improvement, artistically UNAPPROVED.
No finished cycle or production integration.

START HERE
native/WTSC_Painted_Whole_Pose_Correctives_v022.blend
Collection WTSC_PAINTED_WHOLE_POSE_CORRECTIVES_v022
Subcollection V022 | editable pose replacement drawings
Controller V022 | WHOLE POSE ART | two selected poses
Use Blender5.2.2LTS. Packed original v015 painting and native drivers/IK are retained. No addon, handler or external image is needed to open and inspect this file.

SELECTED POSES
L_LOADING: source26.0, study17.25 at30fps.
L_PASSING: source34.0(wrapped3.0), study25.25 at30fps.
Use exact fractional frames: scene.frame_set(17,subframe=.25) or(25,subframe=.25).
Other six v021 selected poses and the frame32 duplicate bookend are retained. All art switches use CONSTANT keys; their intervening holds are a study convenience, not valid animation.
The8s movie holds loading3s, passing3s and enlarged passing detail2s. It contains no normal-speed motion or in-betweens.

ART EDITING
Two additive Geometry Nodes modifiers on LOCO_BOY | PAINT body:
V022 loading coat compression and hem
V022 passing coat compression and hem
Their V022_loading_delta and V022_passing_delta point attributes preserve the original base coordinates/UVs. One amount driver per modifier controls its pose.
Four new editable trouser meshes: loading/passing times near/far. These are static pose-specific replacement drawings, parented to V021 | CHILD_SUPPORT_TRAVEL. They are not a new general leg rig.
Each has97rows and7cross-section points, continuous curved fabric contours, an anatomically placed knee, bowed/flared original rolled cuffs and the original boot-collar endpoint. Original v015 pigment is remapped through editable UVs; no new raster painting is claimed.
A60mm hidden waist overlap closes the coat-to-trouser seam. It changes the drawing overlap, not the skeleton length.
Four small tapered ink/wash crease ribbon meshes use the original coat pigments and sit behind the near sleeve. Their contribution is subtle.
The original V007_BOY | drawn leg near/far meshes are retained intact and hidden by native visibility drivers only while either selected art amount is active. Pose drawings use inverse visibility drivers.
To compare live: temporarily detach/mute the controller action, set both loading and passing to0, update the view layer. Restore its action to return to the authored switches. Enabling both amounts simultaneously is unsupported.
The code in scripts/build_painted_proof.py reproduces this native study from the included byte-identical reference/BASE_COHERENT_SUPPORT_v021_COPY.blend. It also renders eight960x540stills; avoid launching it during world/FX rendering.

SUPPORT / IMPORT CONTRACT
The v021 support solve is unchanged: cycle stride0.952443738458m,31/30s reference period, original child bones and rigid boots.
Read reference/V021_IMPORT_AND_REVIEW_GUIDE.txt and V021_PHASE_TRAVEL_AND_SUPPORT_KEYS.csv for exact root, free pelvis, ankle and painted-sole anchor placements.
These two pose drawings are evaluated only at their selected frames. Keep all independent controls/foot targets under one common placement transform if testing transfer in a disposable scene; moving only the boy travel empty will invalidate world foot targets.
There is no mapping or replacement authorization into the production75–80s shot in this checkpoint.
Head, profile/hair, hands, arms, source52skeleton/action, camera timing and the world are retained. No rejected v008 head work is used.
Review camera V022 | whole painted pose close is orthographic2.9m. SHOT uses the retained actual v046100mm lens/shift, on a neutral stage. Stills are960x540; the film background is not rendered here.

QUALITY / LIMITS
Read V022_VISUAL_ASSESSMENT.txt. The trouser/cuff result is a useful local improvement; the coat remains a flat painted representation. Technical preservation checks do not establish animation quality, cloth dynamics, convincing weight transfer at speed or temporal consistency.
"""
(P/'V022_REVIEW_AND_EDIT_GUIDE.txt').write_text(guide,encoding='utf-8')
coat='\n'.join('%s: max authored coat displacement %.2fmm'%(d['phase'],d['coat_max_offset_m']*1000) for d in defs['poses'])
assessment=f"""WTSC v022 VISUAL ASSESSMENT — 2026-10-18
Completed scope: painted representation corrective study for L_LOADING and L_PASSING. This is a separate isolated branch from v021. No full walk cycle or production integration.

ACTUAL VISUAL GAINS
The stronger improvement is in the trousers. The original grey cuff artwork was being carried high along the articulated calf as a flat strip. Four pose-specific replacement mesh drawings now carry the original pigments over continuous curved thigh/knee/calf contours and bow/flare the rolled cuffs near the hem. Cropped trousers and visible dark ankles remain part of the boy's design.
At close size the passing knee turns more smoothly into the calf, and both loading legs read more like fabric around a limb. At the retained shot framing, the cuff/ankle separation is clearer and the legs appear less segmented. The cuff remains intentionally grey: this is placement/shape repair, not deletion of a design feature.
The coat has distinct loading compression and passing hem lift/tuck, with subtle tapered ink/wash folds. The front triangular hem is quieter; the waist/hip overlap is closed after an initial visible gap was found and corrected. Coat improvement is smaller than trouser improvement.
{coat}
These claims are based on the actual rendered before/after painted images and decoded final comparison movie. The image placement, camera and skeleton are identical within each before/after pair.

LIMITATIONS — ARTISTIC ACCEPTANCE REMAINS OPEN
The torso/coat still reads as a flat painted cutout. The new fold ribbons are subtle and do not create fully convincing cloth volume or replace the baked fold design. This does not resolve the general cloth problem.
The leg shapes can still look too smoothly tubular; reusing original pigment stretches some internal marks. They are pose-specific mesh drawings using existing paint, not newly hand-painted replacement animation.
The loading and passing samples are two local representations, not a temporal sequence. Their differently shaped cuffs/cloth could pop between poses. No blend, velocity, overlap timing or moving silhouette has been accepted.
The v021 source-angle residuals, asymmetric UP heights and adult reference cadence remain. v022 makes no new weight-transfer, restart-step, pair interaction or full-trailer performance claim.
More complete coat drawings would need pose-specific garment panels/folds with consistent cross-pose volumes, followed by a short temporal test. Do not promote this file as finished animation or integrate it automatically.

DESIGN / SUPPORT PRESERVATION — TECHNICAL EVIDENCE
Fresh saved native file versus v021:
- Boy bone world matrices: maximum delta0.
- All actual boot vertices: maximum delta0. Contact and swing clearance remain v021.
- Original head, arms and hands: maximum mesh delta0.
- Other six selected poses: maximum original-mesh delta0.
- Original base mesh coordinates/UVs and packed image bytes unchanged.
- All native limb IK chains reachable.
These are preservation checks only. They are separate from the partial visual assessment above.
The new mesh drawings preserve boot-collar endpoints and add a hidden60mm waist overlap; bone lengths and support trajectories are not changed.

PREVIEW / DELIVERY
Actual MP4:8s,240frames,30fps,1920x1200,{preview['bytes']}bytes. All3unique slides decoded and reviewed. Loading/passing holds3s each; detail2s. No gait playback.
The before/after close and shot views are included as JPEG boards and original960x540PNGs. Detail crops are enlarged for inspection.
The comparison is saved privately in Library, confirmed version0; exact receipt is evidence/private_library_receipt.json.
Editable blend, local source copy, rebuild code, timing data and technical evidence accompany the preview. No sourceFBX or native package was externally shared.

RESOURCE COORDINATION / BLOCKERS
Initial coordination notice to world task01a14565-35ea-72b8-8731-2181768cf013 succeeded. Local Blender CPU activity was checked before each render. One threads2job at a time; the final eight-still job completed in about3s. No render contention was observed.
The completion notice to that world task returned 'invalid turn/start params: AbsolutePathBuf deserialized without a base path'; delivery of that final notice is unconfirmed. No additional renders are queued.
The private preview save is confirmed; its identity and version receipt are retained with the evidence.
No asset-authoring or rendering blocker remains for this bounded study. Full artistic approval and temporal consistency are unresolved.
Protected v021, v046, v007 and v045c native source hashes are unchanged. Production, music, titles, duration, world/art and explosion files were untouched.
"""
(P/'V022_VISUAL_ASSESSMENT.txt').write_text(assessment,encoding='utf-8')
handoff={'status':'TWO_POSE_PAINTED_CORRECTIVE_COMPLETE_PARTIAL_VISUAL_GAIN','artistic_approval':'OPEN','scope':['L_LOADING source26/study17.25','L_PASSING source34/study25.25'],'native':'native/WTSC_Painted_Whole_Pose_Correctives_v022.blend','preview':'previews/WTSC_v022_Whole_Painted_Pose_Comparison_8s.mp4','preview_bytes':preview['bytes'],'private_library_result':lib['results'][0],'visual_gains':['Continuous curved trouser shapes with original pigment','Rolled cuffs at hem with flare/bow and visible ankles retained','Quieter coat hem and closed waist overlap'],'visual_limits':['Flat coat/torso representation remains','Smooth tubular leg tendency and reused paint distortion','Two pose drawings only; temporal popping/blending untested'],'support_preservation':check,'continuous_cycle':'NOT_STARTED','production_integration':'NOT_STARTED','render_blockers':[],'coordination_completion_notice':'failed path error; delivery unconfirmed; no render pending'}
(P/'evidence/FINAL_HANDOFF_v022.json').write_text(json.dumps(handoff,indent=2))
print(json.dumps({'guide':'written','assessment':'written','protected_source_hashes':'PASS','artistic_status':'partial gain / unapproved','private_preview':'confirmed'}))

