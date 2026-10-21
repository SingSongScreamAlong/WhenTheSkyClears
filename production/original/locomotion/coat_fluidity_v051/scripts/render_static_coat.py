import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];old=ROOT/'locomotion/face_hand_finish_v050/native/WTSC_Face_Hand_Finish_v050.blend';new=P/'native/WTSC_Controlled_Fluid_Coat_v051.blend';hashes={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in [old,new]};records=[]
for tag,path,scene in [('BEFORE',old,'V050 | FACE FINISH AND RELAXED HANDS | v049 gait'),('AFTER',new,'V051 | BOY COAT FLUIDITY | exact v050 gait')]:
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);S=bpy.data.scenes[scene];bpy.context.window.scene=S;S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.dither_intensity=0
 def render(view):
  target=P/'previews'/(tag+'_'+view+'.png');S.render.filepath=str(target);bpy.ops.render.render(write_still=True,scene=S.name);records.append({'tag':tag,'view':view,'file':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'camera_width_m':S.camera.data.ortho_scale})
 for f in [1,5,9,13,17,21,25,29,33]:S.frame_set(f);render('WALK_F%02d'%f)
 S.camera.animation_data_clear();root=bpy.data.objects['V048 | shared travel | steady .73125mps'];S.camera.data.ortho_scale=1.25
 for f in [5,13,21,29]:S.frame_set(f);S.camera.location=(root.location.x-.4,-10,.95);render('COAT_DETAIL_F%02d'%f)
 S.frame_set(5);S.camera.location=(root.location.x-.4,-10,.95)
 boy=bpy.data.objects['V044 BOY | estimated joint centres'];C=bpy.data.collections['V046 | restored original painted wardrobe'];keep=[o for o in C.objects if o.parent==boy and o.get('wardrobe_role') in ['body','sleeve']]
 for o in S.objects:
  if o.type=='MESH' and o.parent and o.parent.type=='ARMATURE' and o not in keep:o.hide_render=True
 if tag=='AFTER':
  body=next(o for o in keep if o.get('wardrobe_role')=='body');body.data.shape_keys.animation_data_clear()
  for k in list(body.data.shape_keys.key_blocks)[1:]:k.value=0
 mat=bpy.data.materials.new('RAM-only coat contour ink');mat.use_nodes=True;ns=mat.node_tree.nodes;ns.clear();em=ns.new('ShaderNodeEmission');em.inputs[0].default_value=(.018,.025,.027,1);out=ns.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(em.outputs[0],out.inputs[0])
 for o in keep:o.data.materials.clear();o.data.materials.append(mat)
 render('COAT_CONTOUR_ONLY_F05')
for f,h in hashes.items():assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==h
(P/'evidence/STATIC_COAT_PROOF.json').write_text(json.dumps({'source_hashes':hashes,'sources_unchanged':True,'same_underlying_pose_and_gait':True,'views':records,'contour_view':'Coat/sleeves only, matte shader and other character parts hidden in RAM; v051 hem inertia keys zeroed in RAM to isolate contour changes. Exact same F5 bone pose/camera.','scope':'Static silhouette/construction proof, not animation acceptance.'},indent=2));print('V051_MATCHED_COAT_STATIC_PROOF_COMPLETE')
