import bpy,time,json,csv,subprocess,os
from pathlib import Path
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv012 | drawn expansion and seated contacts'];bpy.context.window.scene=s
# Standalone effect only. The painted scene and its grass/child holdout live in
# the compositor, which is bypassed for a reusable transparent plate.
s.compositing_node_group=None;s.render.film_transparent=True
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
s.render.threads_mode='FIXED';s.render.threads=2
folder=P/'rgba/Drawn_Compact_Impact_24fps';folder.mkdir(parents=True,exist_ok=True);records=[]
for fr in range(1,73):
    f=folder/f'{fr:04d}.png'
    if f.exists() and f.read_bytes()[-12:]==b'\x00\x00\x00\x00IEND\xaeB`\x82':continue
    rows=csv.reader(subprocess.check_output([r'C:\Windows\System32\tasklist.exe','/FI','IMAGENAME eq blender.exe','/FO','CSV','/NH'],text=True,creationflags=subprocess.CREATE_NO_WINDOW).splitlines())
    others=[int(x[1]) for x in rows if x and x[0].lower()=='blender.exe' and int(x[1]) not in [39896,os.getpid()]]
    if others:raise RuntimeError('Deferred before next frame for other Blender '+str(others))
    s.frame_set(fr);bpy.context.view_layer.update();s.render.filepath=str(f);t=time.perf_counter();bpy.ops.render.render(write_still=True,scene=s.name);records.append({'frame':fr,'seconds':time.perf_counter()-t})
(P/'evidence/render_rgba.json').write_text(json.dumps({'frames':[1,72],'fps':24,'pixels':[1920,1080],'alpha':'Straight/unassociated PNG; Blender internal premultiplication is converted on PNG output. Foreground/children holdouts are not baked.','records':records},indent=2));print('DRAWN_RGBA_DONE',flush=True)
