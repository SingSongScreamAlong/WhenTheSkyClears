import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'work/first_danger_conform_v065';build=json.loads((O/'evidence/BUILD.json').read_text());S=Path(build['native']);H=hashlib.sha256(S.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False)
w=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v065'];m=bpy.data.scenes['WTSC_FIRST_DANGER_TITLE_v065'];oc=bpy.data.scenes.get(build.get('foreground_occlusion_scene',''));G=1069 if oc else 997;TAG='F' if oc else 'E'
for sc in [w,m]+([oc] if oc else []):
 sc.render.resolution_x=3840;sc.render.resolution_y=2160;sc.render.resolution_percentage=100;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.dither_intensity=0;sc.render.image_settings.media_type='IMAGE';sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB';sc.render.image_settings.color_depth='8';sc.render.image_settings.compression=15
 if hasattr(sc,'eevee'):sc.eevee.taa_render_samples=32
for node in w.compositing_node_group.nodes:
 if node.type=='OUTPUT_FILE':node.mute=True
bpy.context.window.scene=w;w.frame_set(G);m.frame_set(G)
if oc:oc.frame_set(G)
bpy.context.view_layer.update();w.render.filepath=str(O/f'evidence/LIVE_NATIVE_{TAG}_{G:04d}_4K.png');bpy.ops.render.render(write_still=True,scene=w.name)
ctrl=bpy.data.objects['V065 | both children | global full-cut color time'];u=((G-1)/24)/96;expected=3*u*u-2*u*u*u;assert abs(ctrl['charcoal_progress']-expected)<.000002
assert hashlib.sha256(S.read_bytes()).hexdigest()==H
(O/'evidence/LIVE_NATIVE_WITNESS.json').write_text(json.dumps({'native':str(S),'native_sha256':H,'native_unchanged':True,'frame':G,'resolution':[3840,2160],'actual_global_color_progress':ctrl['charcoal_progress'],'expected_global_color_progress':expected,'scope':'Fresh full live-native world plus title/drawing-reveal and foreground-occlusion composite. Independent comparison target for the cache composite.'},indent=2));print('LIVE_NATIVE_WITNESS_COMPLETE',flush=True)
