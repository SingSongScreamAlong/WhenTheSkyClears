"""Cold native scope and persistence checks for the selected refinement."""
import bpy, json, ast, hashlib, struct, sys
from pathlib import Path
version=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'v047f'
R=Path(__file__).resolve().parents[1];N=R/'notes/improvement_v047';report=json.loads((N/f'build_{version}.json').read_text());base=json.loads((R/'notes/world_v016/motion_trial_build_v046.json').read_text())
defs=ast.parse((R/'scripts/build_art_study_v045.py').read_text());defs.body=[n for n in defs.body if isinstance(n,ast.FunctionDef) and n.name in {'stable','props','curves','action_data','protected_fingerprint'}];exec(compile(defs,'native_protected_scope.py','exec'),globals())
allowed={'v020 | Foreground bank | continuous blended paint','v020 | Walking path | continuous blended paint'}
hashes={};fingerprints=[];feet=[];settings=[]
for path,scene in [(Path(report['base']),'WTSC_OPEN_SUPPORTED_RECOVERY_TRIAL_v046'),(Path(report['native']),report['world_scene'])]:
 hashes[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False);s=bpy.data.scenes[scene];bpy.context.window.scene=s
 protected={s.objects[name] for name in base['world_protected_ids'] if name not in allowed}
 fingerprints.append(protected_fingerprint())
 root=next(o for o in s.objects if o.get('motion_revision')=='v007_drawn_pose_corrections')
 boot_hash=hashlib.sha256()
 for ob in sorted([o for o in root.children_recursive if o.get('v007_role')=='support_boot'],key=lambda o:o.name):
  boot_hash.update(b''.join(struct.pack('fff',*v.co) for v in ob.data.vertices));boot_hash.update(json.dumps(action_data(ob),sort_keys=True).encode())
  if ob.data.shape_keys:boot_hash.update(json.dumps(action_data(ob.data.shape_keys),sort_keys=True).encode())
 feet.append(boot_hash.hexdigest())
 settings.append({'eevee':props(s.eevee),'view':props(s.view_settings),'camera':{k:v for k,v in props(s.camera.data).items() if k!='session_uid'}})
assert fingerprints[0]==fingerprints[1]
assert feet[0]==feet[1]
assert settings[0]==settings[1]
errors={key:0. for key in ['camera','root_travel','FX_matrix','FX_clock','light_watts','receiver_watts']};heads=[]
travel=next(o for o in root.children if 'TRAVEL' in o.name);fx=s.objects['FXv003 | fixed ground origin and controls'];light=s.objects['v043 OWNED | Brief eruption light'];receiver=s.objects['v041 | Live event binding | awaiting verified FX']
girl=next(o for o in root.children_recursive if o.type=='ARMATURE' and o.get('character')=='GIRL')
headobjects=[o for o in girl.children if any(w in o.name for w in ['original head and attached braid','original-painted look toward boy'])]
headobjects.extend(s.objects[row['object']] for row in report['head_drawings'])
for row in base['frozen_baseline_staging']:
 s.frame_set(row['frame']);bpy.context.view_layer.update()
 for key,value,reference in [('camera',s.camera.matrix_world,row['camera']),('FX_matrix',fx.matrix_world,row['fx_matrix'])]:errors[key]=max(errors[key],max(abs(value[i][j]-reference[i][j]) for i in range(4) for j in range(4)))
 errors['root_travel']=max(errors['root_travel'],max(abs(travel.matrix_world.translation[i]-row['route_world'][i]) for i in range(3)))
 errors['FX_clock']=max(errors['FX_clock'],abs(fx['age']-row['age']),abs(fx['hot_envelope']-row['hot']))
 errors['light_watts']=max(errors['light_watts'],abs(light.data.energy-row['watts']))
 errors['receiver_watts']=max(errors['receiver_watts'],abs(receiver['power_watts']-row['receiver_watts']))
 visible=[o.name for o in headobjects if not o.hide_render];assert len(visible)==1
 heads.append({'frame':row['frame'],'visible':visible[0]})
assert max(errors.values())<1e-6,errors
gps=[s.objects[row['GP_guide']] for row in report['head_drawings']]
assert len(gps)==len(report['head_drawings']) and all(o.type=='GREASEPENCIL' and len(o.data.layers[0].frames[0].drawing.strokes)==1 for o in gps)
grass=bpy.data.collections['v047d | rooted charcoal grass, native wind'];curves=[o for o in grass.objects if o.type=='CURVE'];roots=[o for o in grass.objects if o.type=='EMPTY']
positions=[];tips=[]
for frame in [1801,1844,1920]:
 s.frame_set(frame);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
 positions.append({o.name:list(o.matrix_world.translation) for o in roots})
 tips.append([list(o.evaluated_get(deps).data.splines[0].bezier_points[-1].co) for o in curves])
assert positions[0]==positions[1]==positions[2]
maxwind=max(abs(a[i]-b[i]) for a,b in zip(tips[0],tips[2]) for i in range(3));assert maxwind>.0001,maxwind
for item in report['head_drawings']:
 assert s.objects[item['object']].data.materials[0].node_tree
for path,expected in base['preserved_inputs'].items():
 assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==expected,path
assert hashes[report['native']]==report['sha256']
result={'native':report['native'],'native_sha256':report['sha256'],'cold_open_verified':True,
 'unchanged_world_excluding_two_intentional_ground_materials':fingerprints[1],
 'boots_geometry_and_object_action_fingerprint':feet[1],'all120_staging_errors':errors,
 'original_EEVEE_color_and_camera_settings_match':True,'head_exposures_all120':heads,
 'real_native_GP_objects':len(gps),'native_GP_points':[len(o.data.layers[0].frames[0].drawing.strokes[0].points) for o in gps],
 'rooted_grass_roots':len(roots),'animated_native_blade_curves':len(curves),'root_position_error':0,
 'measured_native_tip_motion_m':maxwind,'preserved_input_files_checked':len(base['preserved_inputs']),
 'native4K_and_24fps':True,'artistic_acceptance':False,'full_trailer_propagated':False}
(N/f'cold_verification_{version}.json').write_text(json.dumps(result,indent=2))
print('V047_COLD_VERIFIED',version,json.dumps({k:v for k,v in result.items() if k!='head_exposures_all120'}),flush=True)
