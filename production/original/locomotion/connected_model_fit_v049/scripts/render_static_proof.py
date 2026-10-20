import bpy,math,json,hashlib,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];sys.path.insert(0,str(P/'scripts'));import model_spec as M
old=ROOT/'locomotion/weight_loading_v048/native/WTSC_Connected_Weight_Loading_v048.blend';new=P/'native/WTSC_Connected_Model_Fit_v049.blend';hashes={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [old,new]};report={'source_hashes':hashes,'views':[]}
for tag,file,scene in [('BEFORE',old,'V048 | CONNECTED WEIGHT LOADING | ordinary walk'),('AFTER',new,'V049 | MODEL FIT AND GROUPED HANDS | v048 motion')]:
 bpy.ops.wm.open_mainfile(filepath=str(file),load_ui=False,use_scripts=False);S=bpy.data.scenes[scene];bpy.context.window.scene=S;C=bpy.data.collections['V046 | restored original painted wardrobe'];ART=bpy.data.collections['V044 | age10 editable profile anatomy'];R={w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']};S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.dither_intensity=0
 def render(view):
  S.render.filepath=str(P/'previews'/(tag+'_'+view+'.png'));bpy.ops.render.render(write_still=True,scene=S.name);report['views'].append({'version':tag,'view':view,'camera_width_m':S.camera.data.ortho_scale,'resolution':[1280,720]})
 for f in [1,5,9]:S.frame_set(f);render('WALK_F%02d'%f)
 root=bpy.data.objects['V048 | shared travel | steady .73125mps'];root.animation_data_clear();root.location.x=0;S.camera.animation_data_clear();S.camera.location=(0,-10,.8);S.camera.data.ortho_scale=3.25
 for r in R.values():
  r.animation_data_clear()
  for pb in r.pose.bones:pb.matrix_basis.identity()
 S.frame_set(1);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();gap=0
 for r in R.values():
  e=r.evaluated_get(dg)
  for n,b in e.pose.bones.items():gap=max(gap,(b.head-r.data.bones[n].head_local).length,(b.tail-r.data.bones[n].tail_local).length)
 assert gap<1e-6,gap
 for who,r in R.items():
  pose={n:{'head':b.head_local.copy(),'tail':b.tail_local.copy(),'matrix':b.matrix_local.copy()} for n,b in r.data.bones.items()}
  for side in ['near','far']:
   for kind in ['sleeve','leg']:
    o=next(o for o in C.objects if o.parent==r and o.get('wardrobe_role')==kind and o.name.endswith(side));verts=M.limb_vertices(r,pose,side,kind,tag=='AFTER');o.shape_key_clear();o.data.vertices.foreach_set('co',[c for p in verts for c in p]);o.data.update()
 render('NEUTRAL_SIDE')
 # Isolate actual sleeves, forearms and hands so the girl's charcoal hand does
 # not disappear against the dark dress. Same rest pose; hiding is only in RAM.
 keep=[o for o in C.objects if o.get('wardrobe_role') in ['sleeve','skin','hand']]
 for r in R.values():
  for o in S.objects:
   if o.parent==r and o.type=='MESH' and o not in keep:o.hide_render=True
 S.camera.data.ortho_scale=1.6;S.camera.location=(0,-10,.9);render('ARMS_WRISTS_HANDS_DETAIL')
for file,h in hashes.items():assert hashlib.sha256(Path(file).read_bytes()).hexdigest()==h
report.update({'sources_unchanged':True,'neutral_pose':'Actual rest bones, sleeve/leg cache regenerated to rest axes for each version; no anatomy rescale.','walk_pose':'Same v048 F5, same bone/root/camera Actions.','arm_detail':'Same neutral pose, bodies hidden only in RAM,1.6m camera width; no joint spreading or hand resizing for the review.','scope':'Static model construction proof, not additional motion polish or final model approval.'});(P/'evidence/STATIC_PROOF_RENDER.json').write_text(json.dumps(report,indent=2));print('V049_BEFORE_AFTER_STATIC_MODEL_PROOF_COMPLETE_SOURCES_UNCHANGED',flush=True)
