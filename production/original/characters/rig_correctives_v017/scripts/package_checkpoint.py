import json,math,hashlib,subprocess,zipfile,datetime
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import imageio_ffmpeg
P=Path(__file__).resolve().parents[1];R=P.parents[1]
BG=(232,230,224);INK=(33,40,43)
def font(n,b=False):return ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf' if b else r'C:\Windows\Fonts\segoeui.ttf',n)
def put(canvas,path,box,crop=None):
 im=Image.open(path).convert('RGB')
 if crop:im=im.crop(crop)
 im=ImageOps.contain(im,(box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS);canvas.paste(im,(box[0]+(box[2]-box[0]-im.width)//2,box[1]+(box[3]-box[1]-im.height)//2))
focused=Image.new('RGB',(1920,1870),BG);d=ImageDraw.Draw(focused);d.text((22,12),'V016 BEFORE / V017 AFTER - PAINTED RIG CORRECTIVE CHECKPOINT',font=font(31,True),fill=INK);d.text((22,57),'Same skeletal poses and source paint. Targeted contour/cloth/layer changes; visual acceptance remains OPEN.',font=font(23),fill=INK)
for row,(f,label,crop) in enumerate([(61,'Reach: softer shoulder / elbow / cuff / wrist',(275,215,1100,545)),(161,'Brace: rounded elbow path and quieter wrist join',(275,290,1100,650)),(201,'Crossing: layer override; folded far arm still needs review',(260,255,1110,590)),(21,'Compression: inner knee fold and hem over the knee',(280,420,1100,710))]):
 y=110+row*425;d.text((22,y),label,font=font(26,True),fill=INK)
 for col,mode in enumerate(['BEFORE','AFTER']):
  put(focused,P/f'previews/{mode}/{f:04d}.png',(col*960+12,y+39,col*960+948,y+365),crop);d.text((col*960+20,y+375),mode+' / retained original painting and UVs',font=font(22),fill=INK)
d.text((22,1820),'Rig study only. Knee/cloth volume, folded crossings and required girl attention turn remain unresolved artistic gates.',font=font(22),fill=INK)
focused.save(P/'WTSC_v017_Before_After_Focused_Stress_Board.jpg',quality=93,subsampling=0)
labels=['Neutral','Planted squat','Off-cache intermediate','Reach / deep elbow','Heel contact','Flat support','Toe roll','Lift','Painted brace','Profile tilt ONLY','Crossing / layer override','Pair clearance0.8m']
sheet=Image.new('RGB',(3200,1080),BG);d=ImageDraw.Draw(sheet);d.text((25,14),'v017 - TWELVE ACTUAL-ART BEFORE / AFTER STRESS POSES',font=font(43,True),fill=INK);d.text((25,70),'Eight IK chains total (four arms, four legs). Twelve is the number of poses, not chains. No performance or head-turn approval.',font=font(28),fill=INK)
for i,label in enumerate(labels):
 x=(i%4)*800;y=120+(i//4)*300;d.text((x+12,y),f'{i+1:02d}  {label}',font=font(25,True),fill=INK)
 for j,mode in enumerate(['BEFORE','AFTER']):
  put(sheet,P/f'previews/{mode}/{i*20+1:04d}.png',(x+j*400+5,y+33,x+j*400+395,y+254));d.text((x+j*400+15,y+258),mode,font=font(20),fill=INK)
d.text((25,1035),'Checkpoint: rounded painted joints are improved; compressed cloth and extreme folded-arm silhouettes remain studies. Source v016 and production preserved.',font=font(25),fill=INK)
sheet.save(P/'WTSC_v017_All_Stress_Poses_Before_After.jpg',quality=92,subsampling=0)
folder=P/'previews/COMPARISON';folder.mkdir(exist_ok=True)
for f in range(1,49):
 im=Image.new('RGB',(1920,540),BG)
 for j,mode in enumerate(['BEFORE','AFTER']):im.paste(Image.open(P/f'previews/LIVE_{mode}/{f:04d}.png').convert('RGB'),(j*960,0))
 dr=ImageDraw.Draw(im)
 for j,name in enumerate(['V016 baseline','V017 corrective checkpoint']):dr.rectangle((j*960,0,j*960+959,31),fill=INK);dr.text((j*960+14,5),name,font=font(19,True),fill=BG)
 phase='Bounded cuff / reach / compression fixture' if f<=24 else 'Bounded painted-palm / thigh-brace fixture'
 dr.rectangle((0,516,1919,539),fill=INK);dr.text((12,517),phase+' | two-second rig diagnostic; hard cut at frame25 | not a walk / performance / tutorial emulation',font=font(16),fill=BG);im.save(folder/f'{f:04d}.png')
movie=P/'WTSC_v017_Before_After_Rig_Diagnostic_2s.mp4';ff=imageio_ffmpeg.get_ffmpeg_exe();subprocess.run([ff,'-v','error','-framerate','24','-i',str(folder/'%04d.png'),'-frames:v','48','-c:v','libx264','-threads','2','-preset','medium','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart','-an','-y',str(movie)],check=True)
reader=imageio_ffmpeg.read_frames(str(movie),pix_fmt='rgb24');meta=next(reader);decoded=[];count=0
for data in reader:
 count+=1
 if count in [1,7,13,19,25,31,37,43]:decoded.append((count,Image.frombytes('RGB',meta['size'],data)))
qa=Image.new('RGB',(1920,1190),BG);d=ImageDraw.Draw(qa);d.text((20,12),'v017 - ACTUAL DECODED COMPARISON FRAMES / CHRONOLOGICAL REVIEW',font=font(28,True),fill=INK)
for i,(f,im) in enumerate(decoded):
 x=i%2*960;y=60+i//2*280;qa.paste(im.resize((960,270),Image.Resampling.LANCZOS),(x,y));d.text((x+12,y+246),str(f),font=font(17),fill=BG)
qa.save(P/'evidence/decoded_comparison_review.jpg',quality=92)
core=json.loads((P/'evidence/core_validation.json').read_text());samples=json.loads((P/'evidence/interpolated_diagnostic_validation.json').read_text());root=json.loads((P/'evidence/root_foot_compensation.json').read_text());app=json.loads((P/'evidence/fresh_append_validation.json').read_text());limits=json.loads((P/'evidence/brace_reach_limits.json').read_text());reg=json.loads((R/'characters/rig_capability_audit_v016/NATIVE_CONTROL_MAP_v016.json').read_text())['characters']['GIRL']
maxik=max(x['endpoint_error_m'] for a in samples for x in a['IK'])*1000;gaps=[x*1000 for a in samples if a['palm_gap_m'] for x in a['palm_gap_m'].values()]
pv={'file':movie.name,'bytes':movie.stat().st_size,'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'width':meta['size'][0],'height':meta['size'][1],'fps':meta['fps'],'duration_seconds':meta['duration'],'decoded_frames':count,'under20MB':movie.stat().st_size<20_000_000,'review':'All frames decoded; chronological board used for review. No continuous video playback observation claimed.'};(P/'evidence/preview_verification.json').write_text(json.dumps(pv,indent=2))
report=f'''V017 SAFE CORRECTIVE CHECKPOINT - ACTUAL PAINTED CHILDREN
Status: bounded technical tests pass; VISUAL READINESS STILL UNPASSED.

Changed from immutable v016
The sleeve and cuff now share a rounded elbow path. A tapered, gently bowed forearm and native corner subdivision remove many flat end corners. Original images, base UVs, materials, source skeleton, body weights, hand drawings and contact controls remain. The evaluated arm surface interpolates the original UVs; it is still a planar painted surface.
The trouser knee gains a bend-driven inner compression notch and restrained outer cap. The girl's front hem stays over the bent knee, while rear slack is tucked slightly inward. These are pose-driven correctives, not frame-clock drawings. The thigh support station and boot-entry anchors are unchanged.
A FrontLayer override on each FAR wrist changes the sleeve/cuff/forearm/hand ordering for the crossing study; forearm is in front of its sleeve. This is a deliberate drawing-layer choice, not proof that every folded pose is visually solved.

Observed gain and limits
Cuff corners, shoulder transitions and reaching/brace elbow joins are softer and more continuous in the before/after renders. Compression is only a partial gain: trousers still read as bent painted strips in some deep poses, and skirt/jacket mass still needs authored cloth judgement. The tight folded far arm remains puffy/ambiguous even with the explicit layer override. Hand shapes and the helping offer are unchanged; no load-bearing clasp is approved. These defects remain visible on the stress boards. No final-art or natural-performance acceptance is implied.

Technical evidence
There are EIGHT actual two-bone IK chains: four arms and four legs. Twelve refers to stress poses, not chains.
All twelve baseline skeletal poses match v016; boot geometry, base UVs, original materials, base topology and body weights are retained. No additional signed polygon inversions were found in those static leg/garment tests. Fresh off-cache HIP and wrist edits respond. Native unkeyed append passes with internal dependencies and drivers retained.
The saved two-second fixture was reopened with scripts disabled and tested at94 integer/half-frame samples (the deliberate section cut excluded). Maximum IK error is{maxik:.3f}mm, boot drift is zero, and projected palm gap is{min(gaps):.3f}..{max(gaps):.3f}mm. Those are planar drawing-contact measurements, not3D force validation.
Root travel of25mm drifts boots by25mm without compensation. Reapplying fixed world foot-bone goals reduces measured drift to{root['with_world_goal_compensation_boot_drift_m']*1000:.6f}mm, with all eight chains reachable. Deliberate500mm excess travel is rejected by the reach guard. The brace chest-angle scan rejects sampled0/10/20degree cases; sampled25..65degree cases are reachable at that fixed hip/foot setup. This is not a general visual approval or an exact continuous limit.

Girl attention view remains UNSOLVED
The original right-profile head and braid are retained unchanged. No v008 patch, edge-on card turn, proxy head or invented approval was used. Required art remains two matching registered quarter views bridging right profile, front passage and toward-boy left profile, preserving fringe, skull/cheek/jaw, eye/nose and anatomical braid origin.
Source atlas:1672x941. Retained girl neck registration approximately{[round(x,1) for x in reg['neck_registration_source_px']]}; braid root approximately{[round(x,1) for x in reg['braid_root_source_px']]}. New views need explicit crop offsets/neck registration and a tagged braid root for deliberate interpolation, followed by design and pair-clearance review. Existing profile/reflection is not a completed attention turn.

Safe pause
This checkpoint ends the current unguided corrective pass. No walk cycle, new performance, tutorial emulation, FX or production edit was started. The next separate exercise awaits the parent's verified written guidance/diagrams. Web documentation/extension fetch attempts in this task were unavailable and are not claimed as studied tutorial evidence. Production and v016 source hashes remain unchanged. Actual comparison movie:2seconds,48frames at24fps, under20MB.
'''
(P/'V017_CHECKPOINT_REPORT.txt').write_text(report,encoding='utf-8')
guide='''V017 EDITABLE CHECKPOINT / IMPORT CONTRACT

Primary: native/WTSC_Painted_Rig_Control_Asset_v017.blend (unkeyed). Append collection WTSC_PAINTED_RIG_CORRECTIVES_v017 with all child targets, drivers, shape keys and node groups. Fresh append was tested. The original v016 control ABI/tag and foot recipe are deliberately retained for compatibility; corrective_revision identifies v017. Eight IK chains total,33 original bones,28 painted meshes. Do not treat this study as production-approved art.

native/WTSC_Painted_Rig_Corrective_Board_v017.blend holds the same twelve stepped tests at1,21,..221. native/WTSC_Painted_Rig_Arm_Correctives_v017.blend is the earlier arm-only checkpoint. native/WTSC_Painted_Rig_Diagnostic_v017.blend is a48frame/24fps control fixture:1..24 cuff/reach/compression and25..48 brace follow, with a deliberate section cut. It has no trailer placement or walking timing contract.

New correctives live in corrective_geometry.py: source-width/UV arm ribbons use a shared shoulder-elbow-wrist curve and native subdivision. Body shape keys and trouser-width fields respond to joint/foot distances. No runtime Python handler or frame-specific contour clock is required. Source body weights and original image pixels remain.

FAR WRIST FrontLayer:0 uses source rear depth;1 brings that arm forward of the torso, keeping the skin forward of sleeve/cuff and the hand forward of skin. Key this as CONSTANT for deliberate2D occlusion changes. Primary neutral value is0. It does not repair every folded silhouette. Reach/Brace/TorsoFollow and calibrated NEAR BraceFollow remain the v016 controls; hand-shape weights still normalize. Preserve drivers when clearing animation: set animation_data.action=None; do not use animation_data_clear.

World-space foot locks while moving WORLD_TRAVEL
Load embedded rig_pose_api.py into a namespace, call initialize_from_scene(), capture each ANKLE's matrix_world as the desired foot-bone goal. After changing WORLD_TRAVEL, call set_world_foot_matrix(child,side,goal) for all planted feet, then require_reachable(). Equivalently, target_local=inverse(rig.matrix_world)@desired_world_foot_bone_matrix. Moving travel without resetting the world goal moves its child ankle targets and slides boots. The helper does not stretch legs or plan a step; out-of-range poses must be rejected/re-authored. The supplied root-compensation test proves a25mm case and rejects500mm excess. No new production travel curve was authored.

Coordinates: metres; +X travel, +Z up; camera from-Y. Use in-plane head pitch only. Original right-profile eyes/hair are not a turnaround or eye-gaze rig. Keep proportions, near/far identity and the retained braid/skirt bones. The source near/far projected lengths are intentionally not assumed equal. See V017_CHECKPOINT_REPORT.txt for exact missing head-view registration and candid remaining cloth/crossing defects.

Actual Blender5.2.2 LTS (build d13f752e3b9c) was verified. Native source files are self-contained with packed original paint. Source v016 files and production remain immutable. This checkpoint is paused for a separate verified-written-reference exercise; it is not a tutorial match or an approved walk.
'''
(P/'V017_IMPORT_AND_CONTROL_GUIDE.txt').write_text(guide,encoding='utf-8')
status={'status':'SAFE_CHECKPOINT_PAUSED_FOR_VERIFIED_WRITTEN_REFERENCE_EXERCISE','technical_status':'PASS_WITHIN_TESTED_RANGES','visual_status':'PARTIAL_IMPROVEMENT_FINAL_ART_UNPASSED','IK_chains':8,'static_poses':12,'fresh_fractional_samples':len(samples),'max_IK_error_mm':maxik,'palm_gap_mm_range':[min(gaps),max(gaps)],'root_compensation':root,'core_gates':core['gates'],'fresh_append':app,'preview':pv,'head_view':'Required girl attention quarter views unresolved; original profile retained openly.','next_work':'No new walk/performance in this task. Separate small exercise after verified written guidance arrives.','production_modified':False,'v016_sources_unchanged':core['v016_sources_unchanged'],'library_previews':'pending'}
(P/'evidence/CHECKPOINT_HANDOFF_v017.json').write_text(json.dumps(status,indent=2))
print('V017_PREVIEW_READY',json.dumps(pv))
