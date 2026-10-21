"""Cold-open verification of combined character/impact source and preserved stage."""
import bpy,json,hashlib,ast
from pathlib import Path
R=Path(__file__).resolve().parents[1];N=R/'notes/improvement_v048';report=json.loads((N/'build_v048b.json').read_text())
p=Path(bpy.data.filepath);assert str(p)==report['native'];assert hashlib.sha256(p.read_bytes()).hexdigest()==report['sha256']
s=bpy.data.scenes[report['world_scene']];bpy.context.window.scene=s
defs=ast.parse((R/'scripts/build_art_study_v045.py').read_text());defs.body=[n for n in defs.body if isinstance(n,ast.FunctionDef) and n.name in {'stable','props','curves','action_data','protected_fingerprint'}];exec(compile(defs,'cold_preserved_native.py','exec'),globals())
protected={s.objects[name] for name in report['protected_original_ids']};fingerprint=protected_fingerprint();assert fingerprint==report['protected_original_fingerprint']
root=next(o for o in s.objects if o.get('motion_revision')=='v007_drawn_pose_corrections');rigs=[o for o in root.children_recursive if o.type=='ARMATURE'];old=s.objects['FXv003 | fixed ground origin and controls'];light=s.objects['v043 OWNED | Brief eruption light'];new=s.objects[report['painted_impact_root']]
assert (s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.fps)==(3840,2160,100,24)
errors={'camera':0.,'root':0.,'old_FX_controller':0.,'light_matrix':0.,'light_watts':0.,'all_pose_bones':0.,'new_FX_clock':0.}
for row in report['original_staging_all120']:
 s.frame_set(row['frame']);bpy.context.view_layer.update()
 for key,mat,ref in [('camera',s.camera.matrix_world,'camera'),('root',root.matrix_world,'root'),('old_FX_controller',old.matrix_world,'FX'),('light_matrix',light.matrix_world,'light')]:errors[key]=max(errors[key],max(abs(mat[i][j]-row[ref][i][j]) for i in range(4) for j in range(4)))
 errors['light_watts']=max(errors['light_watts'],abs(light.data.energy-row['watts']));errors['new_FX_clock']=max(errors['new_FX_clock'],abs(new['age']-(row['frame']-1824)))
 for rig in rigs:
  for pbone in rig.pose.bones:errors['all_pose_bones']=max(errors['all_pose_bones'],max(abs(pbone.matrix[i][j]-row['bones'][rig.name][pbone.name][i][j]) for i in range(4) for j in range(4)))
assert max(errors.values())==0,errors
for name in report['disabled_old_FX_visuals']:assert s.objects[name].hide_render
gps=[o for o in s.objects if o.type=='GREASEPENCIL'];assert len(gps)>=8
base=json.loads((R/'notes/world_v016/motion_trial_build_v046.json').read_text())
for path,sha in base['preserved_inputs'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha,path
assert hashlib.sha256(Path(report['parent_native']).read_bytes()).hexdigest()==report['parent_sha256']
assert hashlib.sha256(Path(report['painted_impact_append']).read_bytes()).hexdigest()==report['painted_impact_sha256']
result={'native':report['native'],'native_sha256':report['sha256'],'cold_open_verified':True,'original_world_characters_and_light_except_superseded_FX_fingerprint':fingerprint,'all120_staging_errors':errors,'native_resolution':[3840,2160],'fps':24,'native_real_GP_objects':len(gps),'preserved_source_files_checked':len(base['preserved_inputs']),'original_imagegen_atlas_packed':any(im.packed_file and 'FXv015' in im.name for im in bpy.data.images),'artistic_acceptance':False,'full_trailer_propagated':False}
assert result['original_imagegen_atlas_packed'];(N/'cold_verification_v048b.json').write_text(json.dumps(result,indent=2));print('V048B_COLD_VERIFIED',json.dumps(result),flush=True)
