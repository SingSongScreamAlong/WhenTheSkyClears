import bpy,json,sys
from pathlib import Path
from mathutils import Matrix
P=Path(__file__).resolve().parents[1];source=bpy.data.scenes['FXv012 | drawn expansion and seated contacts'];bpy.context.window.scene=source
camera=source.camera
cam={k:getattr(camera.data,k) for k in ['type','lens','sensor_width','sensor_height','sensor_fit','shift_x','shift_y','clip_start','clip_end']}
matrix=[list(row) for row in camera.matrix_world]
view={k:getattr(source.view_settings,k) for k in ['view_transform','look','exposure','gamma']}
display=source.display_settings.display_device;dither=source.render.dither_intensity
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.name='FXv012 | actual independent append RGBA render';s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=24;s.render.threads_mode='FIXED';s.render.threads=2;s.render.fps=24;s.frame_end=72
with bpy.data.libraries.load(str(P/'native/WTSC_Drawn_Impact_Append_v012.blend'),link=False) as (src,dst):dst.collections=['FXv012 | DRAWN COMPACT IMPACT | distinct onset and contacts']
s.collection.children.link(dst.collections[0]);data=bpy.data.cameras.new('Validation camera only');o=bpy.data.objects.new('Validation camera only',data);s.collection.objects.link(o);s.camera=o;o.matrix_world=Matrix(matrix)
for k,v in cam.items():setattr(data,k,v)
s.display_settings.display_device=display
for k,v in view.items():setattr(s.view_settings,k,v)
s.render.dither_intensity=dither;s.render.film_transparent=True;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
baseline='--baseline' in sys.argv;offset=0 if baseline else 100;label='Baseline' if baseline else 'Offset100'
r=bpy.data.objects['FXv012 | terrain anchor and controls'];r['start_frame']=7.+offset;s.frame_set(9+offset);r.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update()
s.render.filepath=str(P/f'evidence/Append_{label}_Actual_RGBA_Frame9.png');bpy.ops.render.render(write_still=True)
if not baseline:bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Drawn_Impact_Render_Test_v012.blend'),compress=True)
(P/f'evidence/append_render_{label.lower()}.json').write_text(json.dumps({'appended':True,'empty_scene_before_append':True,'source_age':2,'test_frame':9+offset,'test_start_frame':7+offset,'packed_images':len(bpy.data.images),'camera':cam,'matrix':matrix,'view':view},indent=2));print('DRAWN_APPEND_RENDER_DONE',label,flush=True)
