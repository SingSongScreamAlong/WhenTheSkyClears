import bpy,math,json,hashlib,ast,shutil,time
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];new=P/'native/WTSC_Steady_Ordinary_Walk_v047.blend';old=ROOT/'locomotion/painted_outfit_restoration_v046/native/WTSC_Age10_Painted_Outfit_Restoration_v046.blend';hashes={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [old,new]};assert hashes[str(old)]=='e993540280bc60ff5fcc1dafe316f7c8457c5c8750a1110b8f6e307a865d005d';assert json.loads((P/'evidence/COLD_CONTACT_VALIDATION.json').read_text())['native_sha256']==hashes[str(new)]
records=[];begin=time.time()
for tag,file,scene in [('V047',new,'V047 | STEADY ORDINARY WALK | no stumble baseline'),('V046',old,'V046 | AGE10 BONES | restored painted clothing')]:
 bpy.ops.wm.open_mainfile(filepath=str(file),load_ui=False,use_scripts=False);S=bpy.data.scenes[scene];bpy.context.window.scene=S
 if tag=='V046':
  for o in bpy.data.collections['V045 | review-only fixed metric ground'].objects:o.hide_render=True
  review=bpy.data.collections.new('RAM ONLY matched fixed ground');S.collection.children.link(review);tree=ast.parse((P/'scripts/build_steady_walk.py').read_text());tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='line'];exec(compile(tree,'same_review_ground_drawer','exec'),globals())
  for i in range(-20,121):line('matched fixed10cm X'+str(i),(i*.1,.2,-.1),(i*.1,.2,1.75),.00035,bpy.data.materials['V044 quiet metric grid'])
  for i in range(18):line('matched height Z'+str(i),(-2,.2,i*.1),(12,.2,i*.1),.00035,bpy.data.materials['V044 quiet metric grid'])
  line('matched fixed ground',(-2,-.18,0),(12,-.18,0),.003,bpy.data.materials['V044 guide ink'])
  for i in range(-5,31):line('matched40cm tick'+str(i),(i*.4,-.17,-.025),(i*.4,-.17,.028),.0015,bpy.data.materials['V044 guide ink'])
 S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.threads_mode='FIXED';S.render.threads=2;S.render.dither_intensity=0;folder=P/'previews'/('frames_'+tag);folder.mkdir(exist_ok=True)
 for f in range(1,258):
  target=folder/('FRAME_%04d.png'%f)
  if tag=='V047' and f in [1,5,9,13,17,21,25,29]:shutil.copyfile(P/'previews'/('STEADY_%04d.png'%f),target);method='same-final-native matched proof still'
  else:S.frame_set(f);S.render.filepath=str(target);bpy.ops.render.render(write_still=True,scene=S.name);method='actual native timeline render'
  records.append({'version':tag,'frame':f,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'method':method})
 for path,digest in hashes.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest
 print('LONG_NATIVE_SEQUENCE_COMPLETE',tag,round(time.time()-begin,1),flush=True)
(P/'evidence/LONG_RENDER_RECORD.json').write_text(json.dumps({'source_hashes':hashes,'resolution_per_native_frame':[1280,720],'fps':30,'timeline_range':[1,257],'duration_each_seconds':257/30,'native_frames_per_version':257,'actual_timeline_frames_total':514,'threads':2,'ground_reference':'Same fixed10cm grid, stronger sole baseline and40cm ticks in both renders. Added in RAM to v046; no source save.','camera':'Same1280x720, ortho width3.25m, local Z.80m and X follow each version distance. Different gait speeds/cycle lengths are intended and labelled.','elapsed_seconds':time.time()-begin,'records':records},indent=2));print('V047_LONG_MATCHED_COMPARISON_RENDER_COMPLETE',flush=True)
