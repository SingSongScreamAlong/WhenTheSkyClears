import bpy,json,hashlib,time,sys,math
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];B=ROOT/'locomotion/face_hand_finish_v050';old=B/'native/WTSC_Face_Hand_Finish_v050.blend';new=P/'native/WTSC_Controlled_Fluid_Coat_v051.blend';cold=json.loads((P/'evidence/COLD_COAT_VALIDATION.json').read_text());hashes=cold['source_hashes'];sys.path.insert(0,str(ROOT/'locomotion/connected_model_fit_v049/scripts'));import model_spec as M
for path,h in hashes.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h
prior=json.loads((B/'evidence/ACTUAL_V050_MOTION_RENDER.json').read_text());baseframes={r['frame']:r for r in prior['records'] if r['version']=='V050'};records=[];neutral=[];begin=time.time()
for f in range(1,258):
 r=baseframes[f];assert hashlib.sha256(Path(r['file']).read_bytes()).hexdigest()==r['sha256'];records.append(dict(r,view='FULL',method='frozen v050 actual native frame; verified read-only against original manifest'))
for tag,file,scene in [('V050',old,'V050 | FACE FINISH AND RELAXED HANDS | v049 gait'),('V051',new,'V051 | BOY COAT FLUIDITY | exact v050 gait')]:
 bpy.ops.wm.open_mainfile(filepath=str(file),load_ui=False,use_scripts=False);S=bpy.data.scenes[scene];bpy.context.window.scene=S;S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.dither_intensity=0;assert S.render.fps==30
 if tag=='V051':
  folder=P/'previews/frames_V051';folder.mkdir(exist_ok=True)
  for f in range(1,258):
   S.frame_set(f);target=folder/('FRAME_%04d.png'%f);S.render.filepath=str(target);bpy.ops.render.render(write_still=True,scene=S.name);records.append({'version':tag,'view':'FULL','frame':f,'file':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'method':'actual isolated v051 native timeline frame, exact v050 gait'})
 S.camera.animation_data_clear();S.camera.data.ortho_scale=1.25;root=bpy.data.objects['V048 | shared travel | steady .73125mps'];folder=P/'previews'/('detail_'+tag);folder.mkdir(exist_ok=True)
 for f in range(1,130):
  S.frame_set(f);S.camera.location=(root.location.x-.4,-10,.95);target=folder/('FRAME_%04d.png'%f);S.render.filepath=str(target);bpy.ops.render.render(write_still=True,scene=S.name);records.append({'version':tag,'view':'DETAIL','frame':f,'file':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'method':'actual native coat-camera frame, same pose/camera, no video crop or retiming'})
 # Actual rest-bone construction proof, with cache sleeves/legs regenerated to
 # those rest axes in RAM. New cloth keys are held at0 for neutral construction.
 root.animation_data_clear();root.location.x=0;C=bpy.data.collections['V046 | restored original painted wardrobe'];rigs={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']}
 for r in rigs.values():
  r.animation_data_clear()
  for pb in r.pose.bones:pb.matrix_basis.identity()
 for o in C.objects:
  if o.get('wardrobe_role')=='body' and o.data.shape_keys:
   o.data.shape_keys.animation_data_clear()
   for k in list(o.data.shape_keys.key_blocks)[1:]:k.value=0
 S.frame_set(1);bpy.context.view_layer.update()
 for who,r in rigs.items():
  pose={n:{'head':b.head_local.copy(),'tail':b.tail_local.copy(),'matrix':b.matrix_local.copy()} for n,b in r.data.bones.items()}
  for side in ['near','far']:
   for kind in ['sleeve','leg']:
    o=next(o for o in C.objects if o.parent==r and o.get('wardrobe_role')==kind and o.name.endswith(side));verts=M.limb_vertices(r,pose,side,kind)
    if tag=='V051' and who=='BOY' and kind=='sleeve':
     for i,p in enumerate(verts):
      row,col=divmod(i,9);t=row/48;s=col/8
      if row<=3 or row>=46:continue
      normal=(verts[row*9+8]-verts[row*9]).normalized();cap=.003*math.sin(math.pi*max(0,min(1,(t-.06)/.73)))**2 if t<.79 else 0;p-=normal*((s*2-1)*cap)
    o.shape_key_clear();o.data.vertices.foreach_set('co',[c for p in verts for c in p]);o.data.update()
 S.camera.location=(0,-10,.8);S.camera.data.ortho_scale=3.25;target=P/'previews'/(('AFTER' if tag=='V051' else 'BEFORE')+'_NEUTRAL_SIDE.png');S.render.filepath=str(target);bpy.ops.render.render(write_still=True,scene=S.name);neutral.append({'version':tag,'file':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
for path,h in hashes.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h
(P/'evidence/ACTUAL_V051_MOTION_RENDER.json').write_text(json.dumps({'source_hashes':hashes,'full_frame_range':[1,257],'detail_frame_range':[1,129],'fps':30,'native_resolution':[1280,720],'same_underlying_v050_gait':True,'body_timing_changed':False,'threads':2,'elapsed_seconds':time.time()-begin,'records':records},indent=2));(P/'evidence/NEUTRAL_MODEL_RENDER.json').write_text(json.dumps({'source_hashes':hashes,'same_actual_rest_bones':True,'cloth_inertia_keys_zeroed_only_in_RAM':True,'views':neutral},indent=2));print('V051_FULL_AND_COAT_DETAIL_ACTUAL_NORMAL_SPEED_RENDER_DONE_SOURCES_UNCHANGED')
