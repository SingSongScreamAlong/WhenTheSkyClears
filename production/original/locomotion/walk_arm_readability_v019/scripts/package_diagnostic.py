from pathlib import Path
import hashlib,json,zipfile
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];E=P/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=json.loads((E/'source_hashes.json').read_text());preserved=[{'path':p,'before':h,'after':sha(Path(p)),'unchanged':sha(Path(p))==h} for p,h in source.items()];(E/'source_preservation_final.json').write_text(json.dumps(preserved,indent=2))
checks=json.loads((E/'frozen_gait_check.json').read_text());preview=json.loads((E/'comparison_preview.json').read_text());change=json.loads((E/'change_contract.json').read_text());library=[]
for file in ['library_movie_receipt.json','library_image_receipt.json']:library+=json.loads((E/file).read_text())['results']
(E/'private_library_receipts.json').write_text(json.dumps({'results':library,'local_metadata':'Library saves confirmed. Returned version xattr writeback on original local preview files failed: Windows Python has no os.setxattr. No upload is pending or uncertain.'},indent=2))
diagnosis={
 'overall_artistic_status':'REJECTED; latest user rating of v018 was2/10. V019 is an occlusion diagnostic, not an accepted walk.',
 'local_change':'Near hand now separates from the coat at all integer frames10..16 in the critical-frame crop board. The change is visible at original shot framing. Far arm ordering is deliberate; its rear hand still legitimately occludes behind the coat.',
 'what_did_not_change':'Every non-wrist animation channel, body/head pose, foot goal, travel curve and cadence is copied from v018 unchanged. Source proportions/painting/UV/geometry/materials/modifiers are retained.',
 'observations':[
  'The widened near arc provides a clean hand outline, but the hand can look held out or gestural during the forward half. This is a design accommodation for the long coat and short source arm, not proof of natural arm swing.',
  'Whole-body weight transfer still reads weak. A planted boot is clear, but the upper body remains an upright column rather than resolving and recovering the load.',
  'The torso and coat retain nearly the same long triangular shape across the poses; little independent chest or cloth settling is visible.',
  'At passing frames7/19, the knee contour and diagonal calf bands still resemble articulated strips. Their folded silhouettes remain a major visible defect.',
  'The far-foot loading sits10-12mm lower in the retained hip path. That asymmetry remains provisional and can suggest an unintended limp or uneven gait.',
  'At shot size, the local arm change is modest. It does not materially change the appeal or acting quality of the whole walk.'
 ],
 'cadence_and_stride':'Frozen proposal:120steps/min,0.22m per step,0.44m/s. These numbers have not been validated as the right rhythm for this child or emotional state. Normal-speed independent viewing is still required; no cadence acceptance is claimed.',
 'representation_can_do':[
  'Preserve the existing charcoal painting and profile design while placing readable limbs in a controlled side view.',
  'Maintain fixed boot contacts and unchanged child proportions; expose editable wrist arcs and intentional front/back ordering.',
  'Support further pose-specific deformation using the existing meshes and drawings, if that work is independently judged at shot size.'
 ],
 'representation_limits_as_currently_authored':[
  'The body has a single main chest segment and no separately authored lumbar/cloth articulation in this walk. Its motion largely inherits the hip translation; a small chest rotation phase offset does not supply convincing body mass.',
  'Generated knee/limb strips and the existing scalar compression corrections do not produce convincing painted folds through every passing/load pose.',
  'A wrist path or depth switch cannot supply absent torso compression, pelvis/chest counter-motion or well-designed knee silhouettes.',
  'One painted profile does not provide a registered turnaround. No new head view or rejected v008 patch was used.'
 ],
 'diagnostic_conclusion':'The current asset can produce a technically controlled profile walk and clearer hand silhouettes. As currently posed/deformed it cannot deliver the required natural, appealing finished performance. Further arm polishing or tighter contact tolerances will not address the dominant visible failures.',
 'next_gate_not_started':'A whole-body weight/pose and knee/cloth deformation decision is needed on this same isolated child before extending performance. Existing art and mesh correctives remain feasible material to investigate; no request for user-supplied drawings is a prerequisite. No new workstream or corrective phase was started here.',
 'review_method':'Viewed before/after actual-art close renders, every critical frame10..16, matched shot-size examples, and twelve chronological decoded samples of the final encoded movie. No normal-speed video observation claimed.',
 'stop':'Stop here for independent review. Preserve the working rig and all sources. No production integration, additional acting or new painting.'
}
(E/'WHOLE_WALK_DIAGNOSIS_v019.json').write_text(json.dumps(diagnosis,indent=2))
text='V019 BOUNDED ARM DIAGNOSTIC AND WHOLE-WALK DIAGNOSIS\n\n'+diagnosis['overall_artistic_status']+'\n\nLOCAL RESULT\n'+diagnosis['local_change']+'\n'+diagnosis['what_did_not_change']+'\n\nWHOLE-BODY ARTISTIC ASSESSMENT\n'+'\n'.join('- '+x for x in diagnosis['observations'])+'\n\nCADENCE / STRIDE\n'+diagnosis['cadence_and_stride']+'\n\nWHAT THE CURRENT REPRESENTATION CAN DO\n'+'\n'.join('- '+x for x in diagnosis['representation_can_do'])+'\n\nLIMITS OF THE CURRENT AUTHORING\n'+'\n'.join('- '+x for x in diagnosis['representation_limits_as_currently_authored'])+'\n\nCONCLUSION\n'+diagnosis['diagnostic_conclusion']+'\n\n'+diagnosis['next_gate_not_started']+'\n\nREVIEW METHOD\n'+diagnosis['review_method']+'\n\nBOUNDED REGRESSION\nOnly193quarter-frame samples were used to guard the frozen gait. Body/lower-bone matrices, boot vertices and travel have zero measured delta from v018; all non-wrist action channels are identical. Four nativeIKchains remain reachable. This regression prevents damage; it is not an animation quality pass.\n\nDELIVERED PROOF\n1920x1160 comparison movie,24fps,48frames,2seconds,512658bytes. Top row close whole-body view; bottom row original camera size. Reuses the exact v018 before frames and renders v019 after with the same camera/shading. Both show the same translating cycle, not a new performance. Critical-window board contains before/after frames10/13/16 and matched views; all10..16 are also retained in evidence.\n\nPRIVATE LIBRARY\n'+'\n'.join(r['file_name']+' | '+r['library_file_id']+' | '+r['file_id']+' | version'+str(r['current_version_number']) for r in library)+'\nBoth saves succeeded. Local returned version-xattr writeback failed on Windows because Python has no os.setxattr; this did not undo the Library saves.\n\nSOURCE SAFETY\nThe v018 native and v017 control asset hashes are unchanged. Only the isolated v019 folder was authored. No installs, external sharing, heavy renders or source/production changes.\n\nSTOP\n'+diagnosis['stop']+'\n'
(P/'V019_WHOLE_WALK_DIAGNOSIS.txt').write_text(text)
guide='''V019 NATIVE IMPORT / CHANGE CONTRACT

Purpose: bounded wrist/coat occlusion diagnostic following broad artistic rejection
of v018. This file is not approved animation and does not rescue the walk.

Open native/WTSC_Boy_Arm_Readability_v019.blend, or append the complete collection
WTSC_BOY_ARM_READABILITY_v019. Retain its nested world-contact goals and native
drivers. The original v018 internal controller/camera names remain intentionally
unchanged. Move the whole study with V018 | EXERCISE_PLACEMENT | move whole study.
Do not independently move the rig or planted goals. Playback needs no Python.

Only the two WRIST controls' location/quaternion channels and the far wrist
FrontLayer property change. All body, head, pole, rig, foot goal, travel and timing
channels are copied unchanged. The near FrontLayer remains0; its depth is already
in front of the torso. Far FrontLayer is1 during forward phase q0..7 andq18..24,
and0 behind the torso for rear phaseq7..18, with CONSTANT switch keys. The existing
v017 depth driver puts it behind the near arm when in front of the body.

Wrist proposal, not a tutorial preset: near upper-arm arc -28cos(theta)+12sin²(theta)
degrees, far24cos(theta). Native limb lengths remain unchanged. Forearm direction
uses the same arc delayed1.5frames plus30deg near /27deg far. Hand aim flexes8deg
toward vertical relative to the forearm. Source native poles and IK planes are
retained. The broader near forward arc is a silhouette accommodation and may read
as held out; its naturalness is unapproved.

Timing/travel remain exactly v018:24fps,24frames per gait cycle,0.44m per cycle,
D(s)=0.44*(s-1)/24m along+X. Frames1/25/49 are relative cycle bookends; render1..48.
Cadence120steps/min and0.22m per step remain provisional. All heel/sole/forefoot
goals and switch phases are frozen; the original integration contract is copied
under reference/V018_FROZEN_IMPORT_AND_TIMING_GUIDE.txt. No production mapping,
retime, recovery restart or integration has been authored or approved here.

Review the before/after movie at normal speed and actual shot size. The technical
regression only verifies preservation of the working gait. The whole walk remains
artistically rejected; knee/calf strips, stiff torso/coat, loading asymmetry and
cadence/stride fit remain unresolved. Deep cloth/folded arm failures are not waived.
Stop for independent review before another correction phase or additional acting.
'''
(P/'V019_IMPORT_AND_CHANGE_GUIDE.txt').write_text(guide)
(P/'reference/V018_FROZEN_IMPORT_AND_TIMING_GUIDE.txt').write_bytes((ROOT/'locomotion/reference_walk_exercise_v018/V018_IMPORT_AND_TIMING_GUIDE.txt').read_bytes())
(P/'reference/V018_FROZEN_TRAVEL_CURVE.csv').write_bytes((ROOT/'locomotion/reference_walk_exercise_v018/TRAVEL_CURVE_v018.csv').read_bytes())
hand={'checkpoint':'v019','scope':'Bounded wrists/order diagnostic on frozen rejected v018 gait','artistic_status':diagnosis['overall_artistic_status'],'local_result':diagnosis['local_change'],'whole_walk_conclusion':diagnosis['diagnostic_conclusion'],'regression':checks,'preview':preview,'native':str((P/'native/WTSC_Boy_Arm_Readability_v019.blend').resolve()),'report':str((P/'V019_WHOLE_WALK_DIAGNOSIS.txt').resolve()),'guide':str((P/'V019_IMPORT_AND_CHANGE_GUIDE.txt').resolve()),'source_unchanged':all(x['unchanged'] for x in preserved),'library_files':[{k:r[k] for k in ['file_name','library_file_id','file_id','current_version_number','file_size_bytes']} for r in library],'stop_for_independent_review':True,'blockers':'No execution blocker. Whole-walk artistic quality is rejected; independent normal-speed review remains necessary. Local metadata xattrs unavailable on Windows; Library preview saves succeeded.'}
(E/'FINAL_HANDOFF_v019.json').write_text(json.dumps(hand,indent=2))
files=[]
for folder in ['native','scripts','evidence','reference']:
 for p in (P/folder).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.blend1') and p.name!='PACKAGE_v019.json':files.append(p)
files+=[P/'V019_WHOLE_WALK_DIAGNOSIS.txt',P/'V019_IMPORT_AND_CHANGE_GUIDE.txt'];files.extend(p for p in (P/'previews').iterdir() if p.is_file() and p.suffix in ['.jpg','.mp4'] and not p.name.startswith('V019_First_'))
zip_path=P/'WTSC_Boy_Arm_Diagnostic_and_Walk_Diagnosis_v019.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for p in sorted(set(files)):z.write(p,p.relative_to(P))
with zipfile.ZipFile(zip_path) as z:bad=z.testzip();count=len(z.namelist())
pkg={'path':str(zip_path.resolve()),'bytes':zip_path.stat().st_size,'sha256':sha(zip_path),'files':count,'zip_bad_file':bad,'scope':'Editable diagnostic, comparison movie/boards, frozen travel contract and candid whole-walk assessment. Raw render sequences excluded.'};(E/'PACKAGE_v019.json').write_text(json.dumps(pkg,indent=2));print(json.dumps({'package':pkg,'source_unchanged':hand['source_unchanged'],'artistic_status':diagnosis['overall_artistic_status']}))
if bad or not hand['source_unchanged']:raise RuntimeError('Package/source preservation check failed')
