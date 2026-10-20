import bpy,json,hashlib,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'work/first_danger_conform_v065';build=json.loads((O/'evidence/BUILD.json').read_text());S=Path(build['native']);H=hashlib.sha256(S.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False)
oc=bpy.data.scenes[build['foreground_occlusion_scene']];w=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v065'];bpy.context.window.scene=oc;Q=O/'renders/foreground_alpha4K';Q.mkdir(exist_ok=True)
oc.render.use_compositing=True;oc.render.image_settings.media_type='IMAGE';oc.render.image_settings.file_format='PNG';oc.render.image_settings.color_mode='RGB';oc.render.image_settings.color_depth='8';oc.render.image_settings.compression=15
rows=[]
for g in range(913,1081):
 w.frame_set(g);oc.frame_set(g);bpy.context.view_layer.update();oc.render.filepath=str(Q/f'{g:04d}.png');bpy.ops.render.render(write_still=True,scene=oc.name)
 rows.append({'frame':g,'sha256':hashlib.sha256((Q/f'{g:04d}.png').read_bytes()).hexdigest()})
 if g%12==0:print('NATIVE_FOREGROUND_ALPHA',g,len(rows),168,flush=True)
assert hashlib.sha256(S.read_bytes()).hexdigest()==H
(O/'evidence/FOREGROUND_ALPHA_COMPLETE.json').write_text(json.dumps({'native':str(S),'native_sha256':H,'native_unchanged':True,'resolution':[3840,2160],'frames':168,'rows':rows},indent=2));print('NATIVE_FOREGROUND_ALPHA_COMPLETE',flush=True)
