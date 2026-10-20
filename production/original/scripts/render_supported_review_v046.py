"""Cold-open native verification; bounded4Kkeys or matched1080p120frame preview."""
import bpy,json,hashlib,ast,struct,sys
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');report=json.loads((R/'notes/world_v016/motion_trial_build_v046.json').read_text());args=sys.argv[sys.argv.index('--')+1:];mode=args[args.index('--job')+1];assert mode in ['candidate_keys','baseline_preview','candidate_preview'];isbase=mode=='baseline_preview';p=Path(bpy.data.filepath);sha=report['base_sha256'] if isbase else report['source_sha256'];assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
s=bpy.data.scenes['WTSC_OPEN_BATTLEFIELD_ART_STUDY_v045c' if isbase else report['world_scene']];m=bpy.data.scenes['WTSC_OPEN_5S_ART_MASTER_v045c' if isbase else report['master_scene']];bpy.context.window.scene=s;protected={s.objects[n] for n in report['world_protected_ids']}
defs=ast.parse((R/'scripts/build_art_study_v045.py').read_text());defs.body=[n for n in defs.body if isinstance(n,ast.FunctionDef) and n.name in {'stable','props','render_settings','curves','action_data','protected_fingerprint'}];exec(compile(defs,'owned_cold_world_fingerprint_v046','exec'),globals());worldsha=protected_fingerprint();assert worldsha==report['world_protected_fingerprint'];settings=render_settings();expected=report['original_4K_render_settings']
for key in ['eevee','camera','view','world']:
 aa={k:v for k,v in settings[key].items() if k!='session_uid'} if isinstance(settings[key],dict) else settings[key]
 bb={k:v for k,v in expected[key].items() if k!='session_uid'} if isinstance(expected[key],dict) else expected[key]
 if aa!=bb:print('SETTINGS_DIFFERENCE',key,flush=True)
 assert aa==bb,key # Camera.session_uid is a per-process ID counter, not a camera setting.
assert {k:v for k,v in settings['render'].items() if k!='filepath'}=={k:v for k,v in expected['render'].items() if k!='filepath'}
assert s.render.engine=='BLENDER_EEVEE'
for scene in [s,m]:assert (scene.frame_start,scene.frame_end,scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage,scene.render.fps)==(1801,1920,3840,2160,100,24)
root=next(o for o in s.objects if o.get('motion_revision')==('v006_drawn_pose_corrections' if isbase else 'v007_drawn_pose_corrections'));travel=next(o for o in root.children if 'TRAVEL' in o.name);fx=s.objects['FXv003 | fixed ground origin and controls'];light=s.objects['v043 OWNED | Brief eruption light'];event=s.objects['v041 | Live event binding | awaiting verified FX'];heads=[o for o in root.children_recursive if o.get('v007_head_exposure')];headrows=[];error=0
for row in report['frozen_baseline_staging']:
 s.frame_set(row['frame']);bpy.context.view_layer.update();error=max(error,max(abs(s.camera.matrix_world[i][j]-row['camera'][i][j]) for i in range(4) for j in range(4)),max(abs(travel.matrix_world.translation[i]-row['route_world'][i]) for i in range(3)),abs(fx['age']-row['age']),abs(fx['hot_envelope']-row['hot']),abs(light.data.energy-row['watts']),abs(event['power_watts']-row['receiver_watts']))
 if not isbase:
  visible=[o.name for o in heads if not o.hide_render];assert len(visible)==1;headrows.append({'frame':row['frame'],'visible_girl_head':visible[0]})
assert error<1e-6,error
oldroots=[o for o in s.objects if o.get('motion_revision')=='v006_drawn_pose_corrections'] if not isbase else []
for old in oldroots:assert all(o.hide_render for o in old.children_recursive)
picture=next(st for st in m.sequence_editor.strips if st.type=='SCENE');sound=next(st for st in m.sequence_editor.strips if st.type=='SOUND');assert picture.scene==s and picture.frame_final_duration==120 and sound.frame_final_start==1801 and sound.frame_final_end==1921 and sound.sound.packed_file
folder=R/'renders/world_v016/integration_v046';receipt={'mode':mode,'source':str(p),'source_sha256':sha,'cold_open_verified':True,'world_fingerprint':worldsha,'all120_frozen_stage_error':error,'saved_native_resolution':[3840,2160],'review_effective_resolution':[1920,1080] if mode!='candidate_keys' else [3840,2160],'fps':24,'AA_samples':s.eevee.taa_render_samples,'engine':s.render.engine,'view_settings':props(s.view_settings),'master_view_settings':props(m.view_settings),'head_exposures':headrows,'audio':'Same native originalpacked75-80s segment','native_not_resaved':True,'output_status':'launching'}
print('V046_COLD_OPEN_VERIFIED',mode,sha,flush=True);(R/f'notes/world_v016/v046_cold_{mode}.json').write_text(json.dumps(receipt,indent=2));bpy.context.window.scene=m
def still(frame,prefix):
 output=folder/f'{prefix}_{frame}_4K.png';assert not output.exists();m.frame_set(frame);m.render.filepath=str(output);print('V046_4K_FRAME_STARTED',prefix,frame,flush=True);bpy.ops.render.render(write_still=True,scene=m.name);print('V046_4K_FRAME_DONE',prefix,frame,flush=True)
if mode=='candidate_keys':
 m.render.image_settings.media_type='IMAGE';m.render.image_settings.file_format='PNG'
 for f in report['critical_4K_frames']:still(f,'Native_v046')
else:
 for scene in [s,m]:scene.render.resolution_percentage=50
 output=folder/('Baseline_v006_on_v045c_1080p_75_80.mp4' if isbase else 'WTSC_Supported_Recovery_v046_1080p_75_80.mp4');assert not output.exists();m.render.filepath=str(output);m.render.image_settings.media_type='VIDEO';m.render.ffmpeg.format='MPEG4';m.render.ffmpeg.codec='H264';m.render.ffmpeg.constant_rate_factor='HIGH';m.render.ffmpeg.ffmpeg_preset='GOOD';m.render.ffmpeg.audio_codec='AAC';m.render.ffmpeg.audio_bitrate=192;m.render.ffmpeg.audio_mixrate=48000
 print('V046_MATCHED_1080P_120F_STARTED',mode,str(output),flush=True);bpy.ops.render.render(animation=True,scene=m.name);print('V046_MATCHED_1080P_120F_DONE',mode,str(output),flush=True)
 if isbase:
  for scene in [s,m]:scene.render.resolution_percentage=100
  m.render.image_settings.media_type='IMAGE';m.render.image_settings.file_format='PNG'
  for f in [1844,1845,1846,1889]:still(f,'Baseline_v006')
assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
for name,expectedsha in report['preserved_inputs'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==expectedsha,name
receipt['output_status']='completed';(R/f'notes/world_v016/v046_cold_{mode}.json').write_text(json.dumps(receipt,indent=2));print('V046_BOUNDED_JOB_COMPLETED',mode,flush=True)
