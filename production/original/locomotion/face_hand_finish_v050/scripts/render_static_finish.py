import bpy,json,hashlib,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];sys.path.insert(0,str(ROOT/'locomotion/connected_model_fit_v049/scripts'));import model_spec as M
old=ROOT/'locomotion/connected_model_fit_v049/native/WTSC_Connected_Model_Fit_v049.blend';new=P/'native/WTSC_Face_Hand_Finish_v050.blend';hashes={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [old,new]};records=[]
for tag,path,scene in [('BEFORE',old,'V049 | MODEL FIT AND GROUPED HANDS | v048 motion'),('AFTER',new,'V050 | FACE FINISH AND RELAXED HANDS | v049 gait')]:
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);S=bpy.data.scenes[scene];bpy.context.window.scene=S;S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.dither_intensity=0
 def render(view):
  target=P/'previews'/(tag+'_'+view+'.png');S.render.filepath=str(target);bpy.ops.render.render(write_still=True,scene=S.name);records.append({'version':tag,'view':view,'file':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'camera_width_m':S.camera.data.ortho_scale})
 for f in ([1,5,9,13,17,21,25,29,33] if tag=='AFTER' else [1,5,9,17]):S.frame_set(f);render('WALK_F%02d'%f)
 S.frame_set(1);S.camera.animation_data_clear();S.camera.location=(0,-10,1.27);S.camera.data.ortho_scale=1.75;render('FACE_DETAIL_F01')
 S.camera.location=(0,-10,.70);S.camera.data.ortho_scale=1.25
 C=bpy.data.collections['V046 | restored original painted wardrobe'];art=bpy.data.collections['V044 | age10 editable profile anatomy'];R={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']}
 keep=[o for o in C.objects if o.get('wardrobe_role') in ['sleeve','skin','hand']]
 for o in S.objects:
  if o.type=='MESH' and o.parent in R.values() and o not in keep:o.hide_render=True
 S.frame_set(5);root=bpy.data.objects['V048 | shared travel | steady .73125mps'];S.camera.location.x=root.location.x;render('HANDS_DETAIL_F05')
 # Neutral model proof: original rest bones and v049 garment generation in RAM.
 root.animation_data_clear();root.location.x=0
 for r in R.values():
  r.animation_data_clear()
  for pb in r.pose.bones:pb.matrix_basis.identity()
 S.frame_set(1);bpy.context.view_layer.update()
 for r in R.values():
  pose={n:{'head':b.head_local.copy(),'tail':b.tail_local.copy(),'matrix':b.matrix_local.copy()} for n,b in r.data.bones.items()}
  for side in ['near','far']:
   for kind in ['sleeve','leg']:
    o=next(o for o in C.objects if o.parent==r and o.get('wardrobe_role')==kind and o.name.endswith(side));verts=M.limb_vertices(r,pose,side,kind);o.shape_key_clear();o.data.vertices.foreach_set('co',[c for p in verts for c in p]);o.data.update()
 S.camera.location=(0,-10,.70);render('HANDS_DETAIL_NEUTRAL')
 # Reopen to avoid changing original visibility when rendering full neutral.
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);S=bpy.data.scenes[scene];bpy.context.window.scene=S;S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.dither_intensity=0;S.camera.animation_data_clear();S.camera.location=(0,-10,.8);S.camera.data.ortho_scale=3.25;root=bpy.data.objects['V048 | shared travel | steady .73125mps'];root.animation_data_clear();root.location.x=0;C=bpy.data.collections['V046 | restored original painted wardrobe'];R={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']}
 for r in R.values():
  r.animation_data_clear()
  for pb in r.pose.bones:pb.matrix_basis.identity()
 S.frame_set(1);bpy.context.view_layer.update()
 for r in R.values():
  pose={n:{'head':b.head_local.copy(),'tail':b.tail_local.copy(),'matrix':b.matrix_local.copy()} for n,b in r.data.bones.items()}
  for side in ['near','far']:
   for kind in ['sleeve','leg']:
    o=next(o for o in C.objects if o.parent==r and o.get('wardrobe_role')==kind and o.name.endswith(side));verts=M.limb_vertices(r,pose,side,kind);o.shape_key_clear();o.data.vertices.foreach_set('co',[c for p in verts for c in p]);o.data.update()
 render('NEUTRAL_SIDE')
for path,h in hashes.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h
(P/'evidence/STATIC_FINISH_RENDER.json').write_text(json.dumps({'source_hashes':hashes,'sources_unchanged':True,'views':records,'neutral':'Actual rest bones, existing v049 garment caches regenerated in RAM only.','hands_detail':'Bodies hidden in RAM only; same camera, pose and scale before/after.','scope':'Before/after model finish proof and existing walk poses, not new animation.'},indent=2));print('V050_STATIC_PROOF_DONE_SOURCES_UNCHANGED')
