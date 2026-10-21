"""Focused native Font/compositor ending over clean cached world footage."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(r'WTSC_LOCAL_WORKSPACE')
OUT=R/'shots/world/WTSC_Knockout_Ending_Editable_v032.blend'
assert not OUT.exists(), 'Preserve all prior source versions'
world=bpy.data.scenes['WTSC_WORLD_EDIT_v031'];world.name='WTSC_WORLD_CENTERED_v032'
pair=next(o for o in world.objects if o.type=='GREASEPENCIL')
world.frame_set(1249)
# Native held GP geometry, rather than approximate screen eyeballing.
drawing=pair.data.layers[0].frames[0].drawing
positions=drawing.attributes['position'].data
points=[pair.matrix_world@p.vector for p in positions]
projected=[world_to_camera_view(world,world.camera,p) for p in points]
center=((min(p.x for p in projected)+max(p.x for p in projected))/2,
        (min(p.y for p in projected)+max(p.y for p in projected))/2)
local_center_x=(min(p.vector.x for p in positions)+max(p.vector.x for p in positions))/2
crop_scale=2.0
crop_x=(.5-center[0])*3840*crop_scale
crop_y=(.5-center[1])*2160*crop_scale
assert abs(crop_x)<=1920 and abs(crop_y)<=1080, 'Crop must stay inside picture'
# Separate camera copy; original scene/camera data and prior files preserved.
camera=world.camera.copy();camera.data=world.camera.data.copy();camera.name='v032 | Camera follows shared pair center'
world.collection.objects.link(camera)
if camera.animation_data and camera.animation_data.action:
 camera.animation_data.action=camera.animation_data.action.copy()
 for layer in camera.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in list(bag.fcurves):
     if fc.data_path=='location' and fc.array_index==0:bag.fcurves.remove(fc)
driver=camera.driver_add('location',0).driver;driver.type='SCRIPTED'
var=driver.variables.new();var.name='pair_world_x';var.type='TRANSFORMS';var.targets[0].id=pair;var.targets[0].transform_type='LOC_X';var.targets[0].transform_space='WORLD_SPACE'
driver.expression=f'pair_world_x+({local_center_x:.12f})';world.camera=camera
bpy.data.collections['v016 | 07 Monumental title terrain'].hide_render=True
world['v032_camera_scope']='Horizontal camera follows the pair shared root plus held drawing center. Local poses and translation curves unchanged; future gait must keep proper contacts.'
ending=bpy.data.scenes.new('WTSC_KNOCKOUT_ENDING_v032')
ending.render.engine='BLENDER_EEVEE';ending.eevee.taa_render_samples=1
ending.render.resolution_x=3840;ending.render.resolution_y=2160;ending.render.resolution_percentage=100
ending.render.fps=24;ending.frame_start=1;ending.frame_end=2472
ending.render.film_transparent=True;ending.render.use_sequencer=False;ending.render.dither_intensity=0
ending.view_settings.view_transform='Standard';ending.view_settings.look='None'
camdata=bpy.data.cameras.new('v032 | Flat title camera');camdata.type='ORTHO';camdata.ortho_scale=16
cam=bpy.data.objects.new('v032 | Flat title camera',camdata);ending.collection.objects.link(cam);cam.location=(0,0,10);ending.camera=cam
view=camdata.view_frame(scene=ending);W=max(v.x for v in view)-min(v.x for v in view);H=max(v.y for v in view)-min(v.y for v in view)
font=bpy.data.fonts.load(r'C:\Windows\Fonts\ariblk.ttf');font.pack()
mat=bpy.data.materials.new('v032 | True white glyph');mat.use_nodes=True
mat.node_tree.nodes.clear();em=mat.node_tree.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(1,1,1,1)
mo=mat.node_tree.nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(em.outputs[0],mo.inputs['Surface'])
def text(name,body):
 data=bpy.data.curves.new(name,'FONT');data.body=body;data.font=font;data.align_x='LEFT';data.align_y='BOTTOM_BASELINE';data.resolution_u=12;data.materials.append(mat)
 ob=bpy.data.objects.new(name,data);ending.collection.objects.link(ob);return ob
def bounds(ob):
 bpy.context.view_layer.update()
 return (min(p[0] for p in ob.bound_box),max(p[0] for p in ob.bound_box),min(p[1] for p in ob.bound_box),max(p[1] for p in ob.bound_box))
bpy.context.window.scene=ending
line=text('v032 | Moving knockout | WHEN THE SKY CLEARS','WHEN THE SKY CLEARS')
b=bounds(line);scale=.88*H/(b[3]-b[2]);line.scale=(scale,scale,scale)
line.location.y=-(b[2]+b[3])*scale/2
start_x=W/2-b[0]*scale;end_x=-W/2-b[1]*scale
for frame,x in [(1969,start_x),(2401,end_x)]:line.location.x=x;line.keyframe_insert('location',index=0,frame=frame)
for frame,hidden in [(1,False),(2400,False),(2401,True)]:line.hide_render=hidden;line.keyframe_insert('hide_render',frame=frame)
# Solid final card, geometric ink bounds centered and uniform scale per line.
card=[]
for name,body,targetw,cy in [('top','WHEN THE',.76*W,.195*H),('main','SKY CLEARS',.88*W,-.055*H),('year','2027',.245*W,-.315*H)]:
 ob=text('v032 | Final card | '+name,body);b=bounds(ob);sc=targetw/(b[1]-b[0]);ob.scale=(sc,sc,sc);ob.location.x=-(b[0]+b[1])*sc/2;ob.location.y=cy-(b[2]+b[3])*sc/2
 for frame,hidden in [(1,True),(2400,True),(2401,False)]:ob.hide_render=hidden;ob.keyframe_insert('hide_render',frame=frame)
 card.append(ob)
ending.use_nodes=True
nt=bpy.data.node_groups.new('v032 | REAL FONT ALPHA KNOCKOUT','CompositorNodeTree');ending.compositing_node_group=nt
nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
rl=nt.nodes.new('CompositorNodeRLayers');rl.name='Native animated glyph alpha';rl.location=(-650,200)
image=bpy.data.images.load(str(R/'renders/world_v016/WTSC_Painted_World_4K_v030.mp4'),check_existing=False)
movie=nt.nodes.new('CompositorNodeImage');movie.image=image;movie.frame_start=1;movie.frame_offset=-720;movie.frame_duration=2400;movie.use_auto_refresh=True;movie.use_cyclic=False;movie.name='CLEAN WORLD | source52–70 at global82–100';movie.location=(-850,-180)
crop=nt.nodes.new('CompositorNodeTransform');crop.inputs['X'].default_value=crop_x;crop.inputs['Y'].default_value=crop_y;crop.inputs['Scale'].default_value=2;crop.location=(-600,-180);crop.name='PAIR CENTER | uniform 2x finishing crop';nt.links.new(movie.outputs['Image'],crop.inputs['Image'])
def mix(name):
 n=nt.nodes.new('ShaderNodeMix');n.data_type='RGBA';n.blend_type='MIX';n.name=name;return n
fill=mix('World until100; pure white final card');fill.location=(-300,-50);nt.links.new(crop.outputs['Image'],fill.inputs[6]);fill.inputs[7].default_value=(1,1,1,1)
for f,v in [(1,0),(2400,0),(2401,1)]:fill.inputs[0].default_value=v;fill.inputs[0].keyframe_insert('default_value',frame=f)
mask=mix('BLACK OUTSIDE TRUE GLYPH ALPHA');mask.location=(0,120);mask.inputs[6].default_value=(0,0,0,1);nt.links.new(rl.outputs['Alpha'],mask.inputs[0]);nt.links.new(fill.outputs[2],mask.inputs[7])
output=nt.nodes.new('NodeGroupOutput');output.location=(250,120);nt.links.new(mask.outputs[2],output.inputs['Image'])
def interpolations(idblock):
 if not idblock.animation_data or not idblock.animation_data.action:return
 for layer in idblock.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR' if fc.data_path=='location' else 'CONSTANT'
for ob in [line]+card:interpolations(ob)
interpolations(nt)
master=bpy.data.scenes.new('WTSC_MASTER_4K_103S_v032');master.render.resolution_x=3840;master.render.resolution_y=2160;master.render.resolution_percentage=100
master.render.fps=24;master.frame_start=1;master.frame_end=2472;master.view_settings.view_transform='Standard';master.view_settings.look='None';master.render.dither_intensity=0
master.render.use_sequencer=True;master.render.use_compositing=False;master.render.image_settings.media_type='VIDEO';master.render.ffmpeg.format='MPEG4';master.render.ffmpeg.codec='H264';master.render.ffmpeg.constant_rate_factor='HIGH';master.render.ffmpeg.ffmpeg_preset='GOOD';master.render.ffmpeg.audio_codec='AAC';master.render.ffmpeg.audio_bitrate=320;master.render.ffmpeg.audio_mixrate=48000
master.render.filepath='//../../renders/world_v016/WTSC_Knockout_Full_Edit_v032.mp4'
seq=master.sequence_editor_create()
picture=seq.strips.new_scene('WORLD | shared pair centered | 0–82',world,channel=2,frame_start=1);picture.scene_input='CAMERA';picture.frame_final_duration=1968
endstrip=seq.strips.new_scene('ENDING | native font alpha | 82–103',ending,channel=2,frame_start=1);endstrip.scene_input='CAMERA';endstrip.frame_offset_start=1968
sound=seq.strips.new_sound('MUSIC | original start + original 90–100 fade',str(R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'),channel=1,frame_start=1);sound.sound.pack()
for f,v in [(1,1),(2161,1),(2400,0)]:sound.volume=v;sound.keyframe_insert('volume',frame=f)
if master.animation_data:
 for layer in master.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:k.interpolation='LINEAR'
for name,f in [('KNOCKOUT begins | 82s',1969),('Music fade | 90s',2161),('Last S clears / final card | 100s',2401),('Silent card ends | 103s',2473)]:master.timeline_markers.new(name,frame=f)
report={'source':str(OUT),'world_scene':world.name,'ending_scene':ending.name,'master_scene':master.name,'preview_global_seconds':[82,103],'preview_frames':[1969,2472],'clean_cached_picture_seconds':[52,70],'picture_mapping':'global frame minus720; no retime, no loop','music':'Original supplied WAV at global0–100. Original native volume keys1=1,2161=1,2400=0; silence100–103.','final_S_boundary_seconds':100,'last_knockout_frame_seconds':2399/24,'final_card_seconds':[100,103],'card_lines':['WHEN THE','SKY CLEARS','2027'],'projected_pair_center_source':[center[0],center[1]],'crop_uniform_scale':crop_scale,'crop_xy_pixels':[crop_x,crop_y],'cached_picture_effective_pixels':[1920,1080],'output':[3840,2160,24],'native_world_camera':'New shared-root horizontal follow; no child pose/animation changes','legacy_terrain_title_disabled':True,'preview_scope':'Only82–103 exported. Full103 native master editable, not full-film render. Cached ending crop has effective1080 detail within UHD output; no claim of new native4K paint.'}
ending['finishing_scope']=json.dumps(report)
note=bpy.data.texts.new('CURRENT v032 | Knockout ending + centered pair');note.write(json.dumps(report,indent=2))
bpy.context.window.scene=ending;ending.frame_set(2137);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(R/'notes/world_v016/knockout_build_v032.json').write_text(json.dumps(report,indent=2));print('KNOCKOUT_SAVED',str(OUT),flush=True)
# Inspection only. Save source at full4K first; no lowres settings persist.
ending.render.resolution_percentage=25;ending.render.image_settings.media_type='IMAGE';ending.render.image_settings.file_format='PNG'
for frame in [2033,2137,2257,2398,2401]:
 ending.frame_set(frame);ending.render.filepath=str(R/f'renders/world_v016/ending_inspection_v032/{frame}.png');bpy.ops.render.render(write_still=True,scene=ending.name)
