"""Native 4K key and movie review without resaving source."""
import bpy,json,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:];version=args[0];mode=args[1]
report=json.loads((R/f'notes/improvement_v048/build_{version}.json').read_text());p=Path(bpy.data.filepath);sha=hashlib.sha256(p.read_bytes()).hexdigest();assert sha==report['sha256']
s=bpy.data.scenes[report['world_scene']];m=bpy.data.scenes[report['master_scene']];bpy.context.window.scene=s
out=R/f'renders/refinement_{version}';out.mkdir(exist_ok=True)
if mode=='keys':
 s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.use_border=False;s.render.use_crop_to_border=False
 for f in [1801,1834,1840,1846,1881,1901,1918]:
  s.frame_set(f);pout=out/f'Full_{f}_4K.png';assert not pout.exists();s.render.filepath=str(pout);bpy.ops.render.render(write_still=True,scene=s.name);print('V048_KEY',f,flush=True)
elif mode=='movie':
 bpy.context.window.scene=m;m.render.image_settings.media_type='VIDEO';m.render.ffmpeg.format='MPEG4';m.render.ffmpeg.codec='H264';m.render.ffmpeg.constant_rate_factor='HIGH';m.render.ffmpeg.ffmpeg_preset='GOOD';m.render.ffmpeg.audio_codec='AAC';m.render.ffmpeg.audio_bitrate=192;m.render.ffmpeg.audio_mixrate=48000
 pout=out/f'WTSC_Refinement_{version}_75_80_4K.mp4';assert not pout.exists();m.render.filepath=str(pout);bpy.ops.render.render(animation=True,scene=m.name)
else:raise ValueError(mode)
assert hashlib.sha256(p.read_bytes()).hexdigest()==sha;print('V048_RENDER_COMPLETE',version,mode,flush=True)
