"""Stage a bounded first-danger development shot from preserved current inputs."""
import bpy,json,hashlib,runpy,math
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(r'WTSC_LOCAL_WORKSPACE\work\trailer_development_v060')
G0=937;G1=1056
ACT=O/'native/WTSC_Steady_Paired_Reach_v060.blend'
WORLD=O/'reference/PRESERVED_WORLD_v058.blend'
bpy.ops.wm.open_mainfile(filepath=str(ACT),load_ui=False,use_scripts=False)
src=bpy.data.scenes['V060 | STEADY PAIR | first hand contact'];bpy.context.window.scene=src
master=bpy.data.collections['V047 | AGE10 PAIR | steady ordinary walk']
gesture=bpy.data.collections['V060 | paired offer into light | arm rehearsal']
root=bpy.data.objects['V047 | shared travel | steady .73125mps']
boots=[o for o in master.all_objects if o.type=='MESH' and o.get('proportion_role')=='boot' and not o.hide_render]
actors=[o for o in list(master.all_objects)+list(gesture.all_objects) if o.type=='MESH' and not o.hide_render]
source_actions=list(bpy.data.actions)
def frame(scene,f):
 scene.frame_set(math.floor(f),subframe=f-math.floor(f));bpy.context.view_layer.update()
# Keep an independent evaluated source record before any staging or retime.
before={}
for g in range(G0,G1+1):
 f=1+(g-G0)*30/24;frame(src,f);dg=bpy.context.evaluated_depsgraph_get()
 before[g]={b.name:[b.evaluated_get(dg).matrix_world@v.co for v in b.evaluated_get(dg).data.vertices] for b in boots}
for a in source_actions:
 for l in a.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     for k in fc.keyframe_points:
      for p in [k.co,k.handle_left,k.handle_right]:p.x=G0+(p.x-1)*24/30
     fc.update()
with bpy.data.libraries.load(str(WORLD),link=False) as (a,b):
 b.scenes=['WTSC_WORLD_FOREGROUND_v058d','WTSC_FULL_FILM_KNOCKOUT_v040']
s,mask=b.scenes;s.name='WTSC_FIRST_DANGER_WORLD_v060';mask.name='WTSC_FIRST_DANGER_TITLE_CHECK_v060'
bpy.context.window.scene=s;frame(s,G0)
held=next(o for o in s.objects if o.name.startswith('v016 | CHILDREN | held painterly'))
x0=held.matrix_world.translation.x;z0=held.matrix_world.translation.z;y0=-.36
slope=(3-z0)/(16+y0)
hidden=[]
for ob in [held]+list(held.children_recursive):
 ob.hide_render=True;ob.hide_viewport=True;hidden.append(ob.name)
s.collection.children.link(master);s.collection.children.link(gesture)
stage=bpy.data.objects.new('V060 | current age-ten pair | fixed world registration',None);s.collection.objects.link(stage)
M=Matrix.Translation((x0,y0,z0))@Matrix(((1,0,0,0),(0,1,0,0),(0,-slope,1,0),(0,0,0,1)))
stage.matrix_world=Matrix.Translation((x0,y0,z0))
root.parent=stage;root.matrix_parent_inverse=Matrix(((1,0,0,0),(0,1,0,0),(0,-slope,1,0),(0,0,0,1)))
stage['purpose']='Fixed world registration, same unit scale, small painted-floor depth shear; travel remains on original source root.'
stage['source_distance']='D(F)=.78*(F-1)/32 at30fps; F=1+(G-937)*30/24.'
stage['source_lead']='Girl+2 source frames already baked; not reapplied.'
oldcam=s.camera;cam=bpy.data.objects.new('V060 | camera follows actual steady root',oldcam.data.copy());s.collection.objects.link(cam);cam.rotation_euler=oldcam.rotation_euler;cam.location=oldcam.location;camx=oldcam.location.x;s.camera=cam
cam.data.dof.use_dof=True;cam.data.dof.focus_distance=16+y0;cam.data.dof.aperture_fstop=6.3;cam.data.dof.aperture_blades=7
maxerr=0.0
for g in range(G0,G1+1):
 frame(s,g);cam.location.x=camx+(root.matrix_world.translation.x-x0);cam.keyframe_insert('location',frame=g)
 dg=bpy.context.evaluated_depsgraph_get()
 for boot in boots:
  ev=boot.evaluated_get(dg);now=[ev.matrix_world@v.co for v in ev.data.vertices]
  maxerr=max(maxerr,max((p-M@q).length for p,q in zip(now,before[g][boot.name])))
assert maxerr<.00002,('Retime/stage changes feet',maxerr)
for l in cam.animation_data.action.layers:
 for st in l.strips:
  for bag in st.channelbags:
   for fc in bag.fcurves:
    for k in fc.keyframe_points:k.interpolation='LINEAR'
event=bpy.data.objects.new('V060 | one offscreen distant flash | painted response',None);s.collection.objects.link(event);event.location=(x0+3,6,4)
for f,pulse in [(937,0),(955,0),(956,.15),(957,1),(958,.8),(960,.23),(965,0),(1056,0)]:
 event['pulse']=float(pulse);event.keyframe_insert(data_path='["pulse"]',frame=f)
for f,v in [(937,0),(968,0),(1000,1),(1056,1)]:
 event['settle']=float(v);event.keyframe_insert(data_path='["settle"]',frame=f)
for l in event.animation_data.action.layers:
 for st in l.strips:
  for bag in st.channelbags:
   for fc in bag.fcurves:
    for k in fc.keyframe_points:k.interpolation='LINEAR'
event['purpose']='One restrained offscreen first-danger cue; no fire or explosion raster substitute.'
reports={'retimed_actor_actions':len(source_actions),'source_clock':'30fps input to24fps world by exact key/handle time transform; cycle25.6 production frames','range':[G0,G1],'source_range_evaluated':[1,149.75],'floor_depth_slope':slope,'world_registration_matrix':[list(v) for v in M],'original_held_hidden':hidden,'actual_all_four_boot_retime_stage_max_error_m':maxerr,'new_camera':'Moves with actual .73125m/s root. No second travel layer.'}
reports['head_response']=runpy.run_path(str(O/'scripts/add_head_response.py'))['apply'](s,{w:bpy.data.objects['V044 '+w+' | estimated joint centres'] for w in ['BOY','GIRL']},{'controller':event.name,'flash_peak_output_frame':957})
light_path=O/'scripts/add_painted_light.py'
if light_path.exists():reports['painted_light']=runpy.run_path(str(light_path))['apply'](s,actors,event)
reports['girl_head_edge']=runpy.run_path(str(O/'scripts/add_girl_edge.py'))['apply'](s,event)
contacts_path=O/'scripts/add_measured_contacts.py'
if contacts_path.exists():reports['contacts']=runpy.run_path(str(contacts_path))['apply'](s,boots,[G0+i/4 for i in range((G1-G0)*4+1)],lambda y:3-slope*(y+16))
s.frame_start=G0;s.frame_end=G1;s.render.fps=24;s.render.use_sequencer=False
s['V060_scope']='Five-second first-danger development shot. Current steady age-ten pair and fresh hand gesture. Not a completed full-trailer conform.'
s['V060_source_clock']='32 source frames, .78m stride,30fps; native world24fps. Original source phase retained.'
# Actual inherited glyph geometry; point its world input at the revised shot.
for n in mask.compositing_node_group.nodes:
 if n.type=='R_LAYERS' and n.scene and n.scene!=mask:n.scene=s
mask.frame_start=G0;mask.frame_end=G1
# Native shot edit uses the original supplied music at its actual trailer time.
edit=bpy.data.scenes.new('WTSC_FIRST_DANGER_EDIT_v060');edit.render.engine=s.render.engine;edit.render.fps=24;edit.frame_start=G0;edit.frame_end=G1
edit.render.resolution_x=3840;edit.render.resolution_y=2160;edit.render.resolution_percentage=100
edit.render.use_sequencer=True
edit.sequence_editor_create();strip=edit.sequence_editor.strips.new_scene('V060 | first danger | current drawn children',s,channel=2,frame_start=G0);strip.scene_input='CAMERA'
music=O.parents[1]/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'
if music.exists():edit.sequence_editor.strips.new_sound('Original supplied trailer music | unchanged time',str(music),channel=1,frame_start=1)
reports['shot_edit']={'scene':edit.name,'picture_strip_start':strip.frame_final_start,'picture_strip_duration':strip.frame_final_duration,'music':str(music),'music_exists':music.exists(),'timeline_seconds':[39,44]}
for sc in [s,mask,edit]:
 sc.render.resolution_x=3840;sc.render.resolution_y=2160;sc.render.resolution_percentage=100;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.render.image_settings.file_format='PNG';sc.render.filepath='//renders_v060/'
 if hasattr(sc,'eevee'):sc.eevee.taa_render_samples=32
# Export the unmasked compositor branch in the same native render as the glyph view.
nt=mask.compositing_node_group
matte=next(n for n in nt.nodes if n.name=='EXACT BLACK OUTSIDE NATIVE LETTERS')
assert matte.inputs[7].is_linked
world_image=matte.inputs[7].links[0].from_socket
fo=nt.nodes.new('CompositorNodeOutputFile');fo.name='V060 | actual native unmasked world export'
fo.directory='//../previews/frames_world';fo.file_name='world_####';fo.format.media_type='IMAGE';fo.format.file_format='PNG';fo.format.color_mode='RGB';fo.format.color_depth='8';fo.save_as_render=True
fo.file_output_items.new('RGBA','Image')
nt.links.new(world_image,fo.inputs['Image'])
reports['native_dual_output']='Actual compositor world branch and inherited glyph view rendered together; no synthetic title overlay.'
bpy.context.window.scene=s;frame(s,981)
note=bpy.data.texts.new('START HERE | V060 | first danger development');note.write(json.dumps(reports,indent=2,default=str))
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(O/'native/WTSC_First_Danger_Trailer_Development_v060.blend'),compress=True)
(O/'evidence/WORLD_BUILD.json').write_text(json.dumps(reports,indent=2,default=str))
for f in [937,957,969,981,1001,1033,1056]:
 s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;frame(s,f);s.render.filepath=str(O/f'previews/world_v060_{f}.png');bpy.ops.render.render(write_still=True,scene=s.name)
for f in [957,981,1033]:
 mask.render.resolution_x=1280;mask.render.resolution_y=720;frame(s,f);frame(mask,f);mask.render.filepath=str(O/f'previews/title_check_v060_{f}.png');bpy.ops.render.render(write_still=True,scene=mask.name)
print('V060_WORLD_SHOT_NATIVE_AND_KEYS_READY',flush=True)
