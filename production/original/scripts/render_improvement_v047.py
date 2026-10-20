"""Cold-open native key review or bounded actual 4K movie, no source resave."""
import bpy,json,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:]
version=args[0];mode=args[1]
report=json.loads((R/f'notes/improvement_v047/build_{version}.json').read_text())
native=Path(bpy.data.filepath);assert hashlib.sha256(native.read_bytes()).hexdigest()==report['sha256']
s=bpy.data.scenes[report['world_scene']];m=bpy.data.scenes[report['master_scene']]
bpy.context.window.scene=s
folder=R/f'renders/refinement_{version}';folder.mkdir(exist_ok=True)
for scene in [s,m]:
    assert (scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage,scene.render.fps)==(3840,2160,100,24)
    assert scene.render.engine=='BLENDER_EEVEE'
    scene.render.image_settings.media_type='IMAGE';scene.render.image_settings.file_format='PNG'
if mode=='keys':
    for f in ([1842,1844,1846,1847,1848,1849] if version=='v047g' else [1842,1844,1846]):
        s.frame_set(f)
        s.render.use_border=True;s.render.use_crop_to_border=True
        s.render.border_min_x=1900/3840;s.render.border_max_x=2650/3840
        s.render.border_min_y=(2160-1250)/2160;s.render.border_max_y=(2160-500)/2160
        out=folder/f'Head_{f}_Native4KPixels.png';assert not out.exists();s.render.filepath=str(out)
        print('V047_HEAD_KEY_START',f,flush=True);bpy.ops.render.render(write_still=True,scene=s.name)
    s.render.use_border=False;s.render.use_crop_to_border=False;s.frame_set(1901)
    out=folder/'Full_1901_4K.png';assert not out.exists();s.render.filepath=str(out)
    bpy.ops.render.render(write_still=True,scene=s.name)
elif mode in ['movie','tail']:
    bpy.context.window.scene=m
    m.render.image_settings.media_type='VIDEO';m.render.ffmpeg.format='MPEG4';m.render.ffmpeg.codec='H264'
    m.render.ffmpeg.constant_rate_factor='HIGH';m.render.ffmpeg.ffmpeg_preset='GOOD';m.render.ffmpeg.audio_codec='AAC'
    m.render.ffmpeg.audio_bitrate=192;m.render.ffmpeg.audio_mixrate=48000
    if mode=='tail':
        m.frame_start=1848;m.frame_end=1920
        out=folder/f'WTSC_Refinement_{version}_Tail_1848_1920_4K.mp4'
    else:out=folder/f'WTSC_Refinement_{version}_75_80_4K.mp4'
    assert not out.exists();m.render.filepath=str(out)
    bpy.ops.render.render(animation=True,scene=m.name)
else:raise ValueError(mode)
assert hashlib.sha256(native.read_bytes()).hexdigest()==report['sha256']
print('V047_RENDER_COMPLETED',version,mode,flush=True)
