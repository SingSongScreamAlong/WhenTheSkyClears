import bpy,json
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE')
s=bpy.context.scene
rear=s.objects['v015 | Rear countryside']
for t,v in [(0,1),(80,1),(90,1.7),(96,2.4),(100,2.4)]:
    rear.scale=(v,v,v);rear.keyframe_insert('scale',frame=min(2400,int(t*24)+1))
out=R/'renders/world_v016/inspection';out.mkdir(exist_ok=True)
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.compression=15
for name,f in [('01_village',1),('02_woods',721),('03_school',1057),('04_camp',1417),('05_battlefield',1777),('06_title',2305)]:
    s.frame_set(f);s.render.filepath=str(out/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    print('REVIEW_FRAME_COMPLETE',name,f,flush=True)
s.render.image_settings.media_type='VIDEO';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.filepath=str(R/'renders/world_v016/WTSC_Painted_World_4K_v016.mp4');s.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'shots/world/WTSC_Painted_World_Trailer_v016.blend'),compress=True)
