"""Cold reopen and render two normal-speed cycles for candid v056 review."""
import bpy,hashlib,json,math
from pathlib import Path
P=Path(__file__).resolve().parents[1];E=P/'evidence';V=P/'previews'/'frames_v056';V.mkdir(exist_ok=True,parents=True)
build=json.loads((E/'NATIVE_BUILD.json').read_text());native=Path(build['native'])
assert hashlib.sha256(native.read_bytes()).hexdigest()==build['native_sha256']
bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
S=bpy.data.scenes['V056 | ORIGINAL-PAINT SHOULDER DRAPE | v053 grounded walk'];bpy.context.window.scene=S
assert S.frame_end==257
rig=bpy.data.objects['V044 GIRL | estimated joint centres']
yoke=bpy.data.objects['V056 GIRL | pose-specific original painted shoulder yoke']
body=bpy.data.objects['V046 GIRL | tailored knee-length dress']
assert yoke.parent==body.parent==rig
assert len(yoke.data.vertices)==187 and len(yoke.data.shape_keys.key_blocks)==7 and len(body.data.shape_keys.key_blocks)==7
assert len(yoke.data.uv_layers)==1 and len(body.data.uv_layers)==2
def values(o):return {k.name:round(k.value,6) for k in list(o.data.shape_keys.key_blocks)[1:]}
S.frame_set(1);one=values(yoke);S.frame_set(33);repeat=values(yoke)
assert one==repeat,(one,repeat)
S.frame_set(4);peak=values(yoke)
assert max(peak.values())>.99
scene_state={'frame_end':S.frame_end,'yoke_shape_values_f1_f33_exact':one==repeat,'yoke_peak_f4':peak,
 'source_sha256':hashlib.sha256(Path(build['source']).read_bytes()).hexdigest(),
 'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest()}
assert scene_state['source_sha256']==build['source_sha256']
S.render.resolution_x=1280;S.render.resolution_y=720;S.render.resolution_percentage=100
S.render.threads_mode='FIXED';S.render.threads=1;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.render.dither_intensity=0
files=[]
for f in range(1,66):
    S.frame_set(f);S.render.filepath=str(V/f'FRAME_{f:04d}.png')
    bpy.ops.render.render(write_still=True,scene=S.name)
    files.append(V/f'FRAME_{f:04d}.png')
assert len(files)==65 and all(x.exists() for x in files)
result={'cold_reopen':True,'native_sha256':build['native_sha256'],'source_unchanged':True,
 'scene_state':scene_state,'review_frames':[1,65],'frame_count':65,'resolution':[1280,720],
 'fps':30,'first_frame_sha256':hashlib.sha256(files[0].read_bytes()).hexdigest(),
 'last_frame_sha256':hashlib.sha256(files[-1].read_bytes()).hexdigest(),
 'no_scene_duration_change':True}
(E/'COLD_RENDER_REVIEW.json').write_text(json.dumps(result,indent=2))
print('V056_COLD_REVIEW_RENDERED',len(files),flush=True)
