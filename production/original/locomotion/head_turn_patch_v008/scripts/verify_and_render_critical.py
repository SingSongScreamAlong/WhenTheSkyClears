import bpy,json,runpy,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1];source=R/'shots/world/WTSC_Open_Battlefield_Supported_Trial_v046.blend';sha=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False);s=bpy.data.scenes['WTSC_OPEN_SUPPORTED_RECOVERY_TRIAL_v046'];bpy.context.window.scene=s;assert s.render.engine=='BLENDER_EEVEE';root=next(o for o in s.objects if o.get('motion_revision')=='v007_drawn_pose_corrections');rigs=[o for o in root.children_recursive if o.type=='ARMATURE'];before={};objects={o.name:(o.data.as_pointer() if o.data else None) for o in s.objects};frames=[1843,1844,1845,1846]
for f in range(1801,1921):
 s.frame_set(f);bpy.context.view_layer.update();before[f]={'bones':{r.name:{p.name:p.matrix.copy() for p in r.pose.bones} for r in rigs},'camera':s.camera.matrix_world.copy(),'travel':next(o for o in root.children if 'TRAVEL' in o.name).matrix_world.copy()}
settings={'engine':s.render.engine,'resolution':[s.render.resolution_x,s.render.resolution_y],'view':s.view_settings.view_transform,'look':s.view_settings.look}
s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.render.use_sequencer=False;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.use_border=True;s.render.use_crop_to_border=True;s.render.border_min_x=2000/3840;s.render.border_max_x=2600/3840;s.render.border_min_y=1-1200/2160;s.render.border_max_y=1-600/2160
def render(which):
 folder=P/'previews'/which;folder.mkdir(exist_ok=True)
 for f in frames:s.frame_set(f);s.render.filepath=str(folder/f'{f}.png');bpy.ops.render.render(write_still=True)
render('v046_before');apply=runpy.run_path(str(P/'scripts/apply_head_patch.py'))['apply_head_patch_v008'];patch=apply(root);errors={'all_rig_bone_matrices':0,'camera':0,'root_travel':0};visibility=[]
heads=[o for o in root.children_recursive if o.get('v007_head_exposure')]
for f in range(1801,1921):
 s.frame_set(f);bpy.context.view_layer.update();row=before[f]
 for r in rigs:
  for p in r.pose.bones:errors['all_rig_bone_matrices']=max(errors['all_rig_bone_matrices'],max(abs(p.matrix[i][j]-row['bones'][r.name][p.name][i][j]) for i in range(4) for j in range(4)))
 errors['camera']=max(errors['camera'],max(abs(s.camera.matrix_world[i][j]-row['camera'][i][j]) for i in range(4) for j in range(4)));travel=next(o for o in root.children if 'TRAVEL' in o.name).matrix_world;errors['root_travel']=max(errors['root_travel'],max(abs(travel[i][j]-row['travel'][i][j]) for i in range(4) for j in range(4)));visible=[o.name for o in heads if not o.hide_render];assert len(visible)==1,(f,visible)
 if f in frames:visibility.append({'frame':f,'visible_head':visible[0]})
assert max(errors.values())==0,errors
changed=[o.name for o in s.objects if o.name in objects and (o.data.as_pointer() if o.data else None)!=objects[o.name]];assert changed==[patch['target']],changed
render('v008_after');s.frame_set(1844);copy=P/'native/WTSC_Head_Patch_v008_Critical_Comparison_Copy.blend'
for scene in bpy.data.scenes:scene.render.filepath=str(P/'previews/OWNED_HEAD_CRITICAL_ONLY')
bpy.ops.wm.save_as_mainfile(filepath=str(copy),compress=True);assert hashlib.sha256(source.read_bytes()).hexdigest()==sha
report={'source':str(source),'source_sha256':sha,'source_preserved':True,'patch':patch,'engine':'BLENDER_EEVEE','original_settings':settings,'native4K_crop_pixels':[2000,600,2600,1200],'actual_rendered_frames':frames,'whole_movie_rerendered':False,'all120_frame_unchanged_errors':errors,'only_existing_object_with_changed_mesh_data':changed,'visibility':visibility,'comparison_copy':str(copy)};(P/'evidence/critical_verification.json').write_text(json.dumps(report,indent=2));print('V008_CRITICAL_NATIVE_HEAD_COMPARISON_READY',json.dumps(report),flush=True)
