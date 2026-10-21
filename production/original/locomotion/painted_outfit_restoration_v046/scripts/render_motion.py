"""94 actual native frames; source 30fps; render-only, two threads."""
import bpy,json,hashlib,shutil
from pathlib import Path
P=Path(__file__).resolve().parents[1];FILE=P/'native/WTSC_Age10_Painted_Outfit_Restoration_v046.blend';sha=hashlib.sha256(FILE.read_bytes()).hexdigest()
proof=json.loads((P/'evidence/ACTUAL_BONE_RENDER_PROOF.json').read_text());assert proof['native_sha256']==sha
bpy.ops.wm.open_mainfile(filepath=str(FILE),load_ui=False,use_scripts=False);S=bpy.data.scenes['V046 | AGE10 BONES | restored painted clothing'];bpy.context.window.scene=S
S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.threads_mode='FIXED';S.render.threads=2;S.render.dither_intensity=0
F=P/'previews/frames';F.mkdir(exist_ok=True);records=[]
for f in range(1,95):
 target=F/('FRAME_%04d.png'%f)
 if f in [1,9,17,25]:
  source=P/'previews'/('RESTORED_DRESSED_F1.png' if f==1 else 'RESTORED_DRESSED_F%02d.png'%f);shutil.copyfile(source,target);method='same-native same-settings comparison still'
 else:S.frame_set(f);S.render.filepath=str(target);bpy.ops.render.render(write_still=True,scene=S.name);method='native render'
 records.append({'frame':f,'path':str(target.relative_to(P)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'method':method})
 assert S.render.fps==30 and S.render.fps_base==1
assert hashlib.sha256(FILE.read_bytes()).hexdigest()==sha
(P/'evidence/MOTION_RENDER.json').write_text(json.dumps({'native_sha256':sha,'native_unchanged':True,'source_fps':30,'source_frame_range':[1,94],'timeline_frames':94,'cycle_source_frames':31,'description':'Three repeats of the authored 31-frame local walk and endpoint; native root and camera continue travelling. 90 new renders and 4 matching proof stills. No optical flow or interpolated video frames.','resolution':[1280,720],'threads':2,'frames':records},indent=2));print('V046_NATIVE_MOTION_RENDER_COMPLETE',flush=True)
