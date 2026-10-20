from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parents[1]
A=json.loads((P/'evidence/NATIVE_SCALE_AUDIT.json').read_text())
M=json.loads((P/'evidence/RENDERED_SCALE_METRICS.json').read_text())
old=M['versions']['v039']['actual_diagnostic_head_hair_neck_only']
new=M['versions']['v041']['actual_diagnostic_head_hair_neck_only']
mass=(new['alpha_weighted_area_pixels']/old['alpha_weighted_area_pixels']-1)*100
matdiff={}
for v,a in A.items():
 matdiff[v]={}
 for f in ['1','20']:
  b=A['v028']['frames'][f];c=a['frames'][f]
  matdiff[v][f]={'root_world_max_difference_from_v028':max(abs(c['root_world'][i][j]-b['root_world'][i][j]) for i in range(4) for j in range(4)),
   'camera_world_max_difference_from_v028':{n:max(abs(c['camera_world'][n][i][j]-b['camera_world'][n][i][j]) for i in range(4) for j in range(4)) for n in c['camera_world']}}
hashes=json.loads((P/'evidence/SOURCE_HASHES_BEFORE_AFTER.json').read_text())
for r in hashes.values():
 now=hashlib.sha256(Path(r['source']).read_bytes()).hexdigest()
 assert now==r['before']==r['after']
 r['final_sha256']=now
(P/'evidence/SOURCE_HASHES_BEFORE_AFTER.json').write_text(json.dumps(hashes,indent=2))
report=f'''WTSC v042 — READ-ONLY SCALE AUDIT
Status: Complete diagnosis and matched evidence. No candidate asset saved, edited or rescaled. Cosmetic development remains paused pending the user's clarification of "scaling feels very off".

Finding: the current review-camera evidence points more strongly to an inconsistent design/proportion read than to a recent uniform enlargement or camera zoom. That remains a visual diagnosis, not confirmation of the user's intended meaning. Unchanged transform tests do not validate anatomy or perceived scale.

SAME CAMERA / SAME PIXELS
Five native sources: v028, v036, v039, v040 and v041. At F1 the actual rendered character alpha height is 628/628/628/629/629 px in a 480x720 close view, and 319 px in every 1280x720 shot view (alpha >=0.5). The old/new hair+head+neck masks are 158/157 px high; v041 has {mass:.2f}% less alpha-weighted painted area than v039, with its mass centroid about 4.56 px higher. This mask includes hair and neck: it is not an anatomical crown-to-chin head count. Alpha thresholds0.1 and0.9 are retained in the evidence.

Both review cameras' data are identical across all five files. Their world matrices and the travel root world matrices match v028 at sampled F1/F20. All native files use metric scale1, unit rig/root scale and 30 fps. v028's saved render default is360x540; later saved close defaults are480x720. The audit uses the same480x720 for every close source, so that default does not contaminate the comparison.

SPECIFIC DESIGN / REGISTRATION PROBLEM
The v040 head+neck painting was independently generated, then fitted to the old occupied X/Z box. The mapping is 0.000863882 scene units/source pixel horizontally versus0.000786976 vertically: horizontal relative stretch9.7723%. This is distortion relative to the generated painting, not proof of a9.8% enlargement over the earlier rendered head. Fitting the whole hair/head/neck box did not separately constrain crown, chin, neck length, eye size or facial mass. A more literal face now reads against the inherited stylized torso, limbs and tiny hands. The matched native pixels show that design mismatch even though total head occupancy did not grow.

HANDS / ARMS / BOOTS
The near drawn hand spans0.067076m along its hand-bone axis; the canonical near boot's rest drawing is0.241518m long: ratio3.60066. These are drawing measurements, not anatomical norms or a claim that the entire boot is the bare foot. The new leather/face painting makes that inherited small-hand/large-footwear contrast conspicuous. v036 through v041 keep those hand/boot sizes. Their new painting alone is not evidence of correct proportions.
v028 to v036 had a real arm redistribution: near upper/forearm lengths0.289785/0.126455m became0.218000/0.198239m, while total reach stayed0.416239m. v036/v039/v040/v041 have identical rest-bone lengths. New face painting should not be taken to validate that body proportion choice. The side-profile torso and shoulder silhouette need a unified design review; profile depth is not frontal shoulder breadth.

NECK / COLLAR / SHOULDERS
v041 deliberately changed upper garment construction. It is not correct to say all geometry was unchanged. The old visible yoke was hidden intact; a new36-vertex collar and adjusted upper six coat rows were added. Maximum upper-coat movement across the cycle is0.043310m; lower rows6..32 remained exact. At F1 the collar's projected mesh envelope is46.71x33.74px (profile X/Z extents0.107037x0.077330m). The old yoke envelope is76.57x53.81px (0.175481x0.123310m); those are different garment pieces and cannot be treated as anatomical neck widths. Shoulder/arm bone anchors did not scale; visible neckline/upper coat and exposed neck read did change. v040 and v041 share the exact same painted head.

FRAMING / ENVIRONMENT LIMIT
The close view fills about87.3% of720px height; the shot view44.3%. In the existing comparison movie, the paired shot panels are explicitly reduced to50%, so the character is about159.5px tall there versus629px in the native close section, roughly a3.94x on-screen size change. That layout may contribute if the feedback concerns the review presentation. The audit's PNGs use no rescaling, alignment or size normalization.
v040/v041 have not been integrated into the v046 production environment. These neutral review-camera measurements cannot establish environmental scale. Do not rescale the world or the whole character from this audit. The pending answer about body/head proportions versus size in scene still matters.

VISUAL ASSESSMENT / NEXT CONCRETE STEP
The more detailed face, tiny hands, strong boot mass and fitted narrow coat do not yet read as one coherently designed child. A registration correction alone will not make the animation or character Arcane-level. After the clarification, the appropriate proportion pass is a single same-camera design pose with crown/chin/neck/shoulder/wrist/heel/toe anchors, uniform head-paint scaling, and an explicit hand/footwear choice, then a matched movement review. No such correction has been performed during this audit. Preserve the liked face/painting and preferred movement as references; do not infer approval for a new proportion from preservation tests.

EVIDENCE
images/MATCHED_CLOSE_UNSCALED.png: original480x720 panels F1/F20, five versions, no resizing.
images/HEAD_PAINT_MASS_UNSCALED.png: identical240x240 native-pixel crops of transparent native head renders; paper background is diagnostic only.
images/MATCHED_SHOT_UNSCALED.png: original1280x720 panels v039/v041 F1, no resizing.
evidence/RENDERED_SCALE_METRICS.json: alpha bboxes/areas, camera data, drawing measurements and registration calculation.
evidence/NATIVE_SCALE_AUDIT.json: native camera/root/rig/bone/mesh measurements F1/F20.
evidence/SOURCE_HASHES_BEFORE_AFTER.json: all five source hashes unchanged, rechecked at delivery.

METHOD / QUALITY LIMIT
Blender5.2.2 LTS(d13f752e3b9c), verified installed executable. One bounded2-thread job emitted15 small diagnostic PNGs, then exited. Changes to visibility/compositor were in RAM only; no blend save was called. Matching existing rendered F1/F20 images were also inspected. This is a static scale/design audit, not an animation-quality pass, continuous playback observation, new production integration or accepted final design. No source, production, world-specialist, music, title or trailer duration file was changed.
'''
(P/'READ_ONLY_SCALE_DIAGNOSIS_v042.txt').write_text(report,encoding='utf-8')
handoff={'status':'Completed read-only scale audit; no rescaling or further cosmetic development performed. User clarification pending.',
 'diagnosis':'Uniform review-camera enlargement was not found. Main evidence points to mismatched design proportions and a nonuniform head-paint registration; environmental scale remains unestablished.',
 'source_files_preserved':all(r['unchanged'] for r in hashes.values()),'source_native_files_saved':False,'head_source_mapping_horizontal_relative_stretch_percent':9.772310900248904,
 'actual_head_hair_neck_painted_area_change_v039_to_v041_percent':mass,'camera_and_root_sample_comparison':matdiff,
 'preview_mixed_panel_character_height_pixels':[629,159.5,319],
 'report':'READ_ONLY_SCALE_DIAGNOSIS_v042.txt','boards':['images/MATCHED_CLOSE_UNSCALED.png','images/HEAD_PAINT_MASS_UNSCALED.png','images/MATCHED_SHOT_UNSCALED.png'],
 'pending':'Which perceived scaling problem the user means: head/body proportions or character size in the environment. No dependent rescaling performed.',
 'technical_success_is_not_visual_approval':True,'blender_job_exited':True,'no_remaining_technical_block':True}
(P/'evidence/final_handoff.json').write_text(json.dumps(handoff,indent=2))
print(json.dumps({'sources_unchanged':True,'head_painted_area_change_percent':mass,'camera_root_max_error':max(x for r in matdiff.values() for f in r.values() for x in [f['root_world_max_difference_from_v028'],*f['camera_world_max_difference_from_v028'].values()]),'report_bytes':(P/'READ_ONLY_SCALE_DIAGNOSIS_v042.txt').stat().st_size}))
