"""Cold-open exact protection check and only six native4K PNGs. No movie."""
import bpy,json,hashlib,ast,struct
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(r'WTSC_LOCAL_WORKSPACE');report=json.loads((R/'notes/world_v016/art_study_build_v045a.json').read_text());p=Path(bpy.data.filepath);assert hashlib.sha256(p.read_bytes()).hexdigest()==report['source_sha256'];s=bpy.data.scenes[report['world_scene']];m=bpy.data.scenes[report['master_scene']];bpy.context.window.scene=s
root=next(o for o in s.objects if o.get('motion_revision')=='v006_drawn_pose_corrections');fx=s.objects['FXv003 | fixed ground origin and controls'];light=s.objects['v043 OWNED | Brief eruption light'];travel=next(o for o in root.children if 'TRAVEL' in o.name);protected={s.objects[n] for n in report['protected_ids']}
definitions=ast.parse((R/'scripts/build_art_study_v045a.py').read_text());definitions.body=[node for node in definitions.body if isinstance(node,ast.FunctionDef) and node.name in {'stable','props','render_settings','curves','action_data','protected_fingerprint'}];exec(compile(definitions,'owned_v045a_readonly_fingerprint','exec'),globals());fingerprint=protected_fingerprint();assert fingerprint==report['unchanged_protected_fingerprint'],(fingerprint,report['unchanged_protected_fingerprint'])
settings=render_settings();prior=report['unchanged_render_settings'];assert {k:v for k,v in settings['render'].items() if k!='filepath'}=={k:v for k,v in prior['render'].items() if k!='filepath'}
for key in ['eevee','view','camera','world']:assert settings[key]==prior[key],key
errors={key:0. for key in report['evaluated_120frame_errors']};coverage=[];pano=s.objects['v026 | Countryside panorama | stationary at true depth']
for row in report['baseline_staging']:
 s.frame_set(row['frame']);bpy.context.view_layer.update()
 for key,mat in [('camera',s.camera.matrix_world),('root',root.matrix_world),('fx',fx.matrix_world)]:errors[key]=max(errors[key],max(abs(mat[i][j]-row[key][i][j]) for i in range(4) for j in range(4)))
 errors['travel']=max(errors['travel'],max(abs(travel.matrix_world.translation[i]-row['travel'][i]) for i in range(3)))
 for key,value in [('age',fx['age']),('hot',fx['hot_envelope']),('watts',light.data.energy)]:errors[key]=max(errors[key],abs(value-row[key]))
 box=[world_to_camera_view(s,s.camera,pano.matrix_world@Vector(v)) for v in pano.bound_box];bounds=[min(v.x for v in box),max(v.x for v in box),min(v.y for v in box),max(v.y for v in box)];assert bounds[0]<0 and bounds[1]>1 and bounds[2]<0 and bounds[3]>1
 coverage.append({'frame':row['frame'],'opaque_panorama_bounds':bounds})
assert max(errors.values())==0
for item in report['changed_materials']:
 nt=bpy.data.materials[item['art_material']].node_tree
 assert not any(f.data_path.startswith('nodes["v045a') for f in nt.animation_data.drivers) if nt.animation_data else True
first={'source':str(p),'source_sha256':report['source_sha256'],'cold_reopen':True,'protected_fingerprint':fingerprint,'protected_geometry_actions_materials_unchanged':True,'render_camera_eevee_settings_match_v044':True,'all120frame_errors':errors,'opaque_backing_coverage_all120frames':coverage,'paint_alpha_and_card_geometry':'Unchanged; only native RGB routing changed. Opaque backing covers entire frame over all120samples.','actual_card_seams_visual_check':'Pending sixactualrenders; geometry/alpha unchanged does not by itself approve art continuity.','frames':report['frame_first'],'movie_render_started':False}
(R/'notes/world_v016/art_fresh_open_v045a.json').write_text(json.dumps(first,indent=2));print('V045_COLD_OPEN_FIXED_PERFORMANCE_FX_VERIFIED',fingerprint,flush=True)
folder=R/'renders/world_v016/art_v045a';folder.mkdir(parents=True,exist_ok=True);bpy.context.window.scene=m;m.render.image_settings.media_type='IMAGE';m.render.image_settings.file_format='PNG';m.render.resolution_percentage=100
for frame in report['frame_first']:
 out=folder/f'Art_v045a_{frame}_4K.png';assert not out.exists();m.frame_set(frame);m.render.filepath=str(out);print('V045_FRAME_STARTED',frame,flush=True);bpy.ops.render.render(write_still=True,scene=m.name);print('V045_FRAME_COMPLETED',frame,str(out),flush=True)
assert hashlib.sha256(p.read_bytes()).hexdigest()==report['source_sha256']
for name,sha in report['preserved_inputs'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==sha
first['six_actual_4K_pngs_complete']=True;first['movie_render_started']=False;first['actual_card_seams_visual_check']='SixactualPNGsready; human/sampleinspectionpending.';(R/'notes/world_v016/art_fresh_open_v045a.json').write_text(json.dumps(first,indent=2));print('V045_FRAME_FIRST_SIX_PNGS_COMPLETED_NO_MOVIE',flush=True)
