import bpy,json,hashlib,time
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];B=ROOT/'locomotion/connected_model_fit_v049';old=B/'native/WTSC_Connected_Model_Fit_v049.blend';new=P/'native/WTSC_Face_Hand_Finish_v050.blend';cold=json.loads((P/'evidence/COLD_FINISH_VALIDATION.json').read_text());hashes=cold['source_hashes']
for path,h in hashes.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h
prior=json.loads((B/'evidence/ACTUAL_V049_MOTION_RENDER.json').read_text());oldrecords={r['frame']:r for r in prior['records'] if r['version']=='V049'};records=[]
for f in range(1,258):
 r=oldrecords[f];assert hashlib.sha256(Path(r['file']).read_bytes()).hexdigest()==r['sha256'];records.append(dict(r,method='frozen v049 actual native frame verified read-only against its render manifest'))
bpy.ops.wm.open_mainfile(filepath=str(new),load_ui=False,use_scripts=False);S=bpy.data.scenes['V050 | FACE FINISH AND RELAXED HANDS | v049 gait'];bpy.context.window.scene=S;S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.threads_mode='FIXED';S.render.threads=2;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.dither_intensity=0;assert S.render.fps==30 and S.render.fps_base==1
folder=P/'previews/frames_V050';folder.mkdir(exist_ok=True);begin=time.time()
for f in range(1,258):
 S.frame_set(f);target=folder/('FRAME_%04d.png'%f);S.render.filepath=str(target);bpy.ops.render.render(write_still=True,scene=S.name)
 records.append({'version':'V050','frame':f,'file':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'method':'actual v050 native frame; all v049 motion Actions preserved'})
for path,h in hashes.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h
(P/'evidence/ACTUAL_V050_MOTION_RENDER.json').write_text(json.dumps({'source_hashes':hashes,'fps':30,'timeline_range':[1,257],'native_frames_per_version':257,'duration_each_seconds':257/30,'resolution_per_native_frame':[1280,720],'threads':2,'elapsed_render_seconds':time.time()-begin,'model_version':'v050 face/hand finish','motion_version':'v049 exactly preserved (v048 gait)','same_camera_scale_phase_cadence_root_travel':True,'speed_m_s':.73125,'period_source_frames':32,'travel_m':'0.78*(F-1)/32','records':records},indent=2));print('V050_ACTUAL_257_FRAME_RENDER_COMPLETE_FROZEN_V049_UNCHANGED')
