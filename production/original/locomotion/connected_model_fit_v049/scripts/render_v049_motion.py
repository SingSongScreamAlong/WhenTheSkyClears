"""Actual frozen v049 model at every frame of preserved v048 motion."""
import bpy,hashlib,json,time
from pathlib import Path
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
before=ROOT/'locomotion/weight_loading_v048/native/WTSC_Connected_Weight_Loading_v048.blend'
native=P/'native/WTSC_Connected_Model_Fit_v049.blend'
expected={str(before):'eeefa9ea2059a613d796277d6dfebfabe84a89b1c31470b585e5475fcb35001b',str(native):'2f78c5cd86b96d437d97a165b8b61473bcd6c9d1ab284015c229bfb11c6f9a94'}
for path,h in expected.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h,path
prior=json.loads((ROOT/'locomotion/weight_loading_v048/evidence/LONG_RENDER_RECORD.json').read_text())
oldrecords={r['frame']:r for r in prior['records'] if r['version']=='V048'}
records=[]
for f in range(1,258):
 r=oldrecords[f];assert hashlib.sha256(Path(r['file']).read_bytes()).hexdigest()==r['sha256']
 records.append(dict(r,method='read-only frozen v048 reference, verified against original render manifest'))
bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
S=bpy.data.scenes['V049 | MODEL FIT AND GROUPED HANDS | v048 motion'];bpy.context.window.scene=S
S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100
S.render.threads_mode='FIXED';S.render.threads=2;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.dither_intensity=0
assert S.render.fps==30 and S.render.fps_base==1
folder=P/'previews/frames_V049';folder.mkdir(exist_ok=True);begin=time.time()
for f in range(1,258):
 S.frame_set(f);target=folder/('FRAME_%04d.png'%f);S.render.filepath=str(target)
 bpy.ops.render.render(write_still=True,scene=S.name)
 records.append({'version':'V049','frame':f,'file':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'method':'actual frozen v049 native timeline render; no looped PNGs or video interpolation'})
for path,h in expected.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h,path
(P/'evidence/ACTUAL_V049_MOTION_RENDER.json').write_text(json.dumps({'source_hashes':expected,'fps':30,'timeline_range':[1,257],'native_frames_per_version':257,'duration_each_seconds':257/30,'resolution_per_native_frame':[1280,720],'threads':2,'elapsed_render_seconds':time.time()-begin,'model_version':'v049','motion_version':'v048 unchanged','same_camera_scale_phase_cadence_root_travel':True,'speed_m_s':.73125,'period_source_frames':32,'travel_m':'0.78*(F-1)/32','records':records},indent=2))
print('ACTUAL_V049_257_FRAME_RENDER_COMPLETE_FROZEN_SOURCES_UNCHANGED',flush=True)
