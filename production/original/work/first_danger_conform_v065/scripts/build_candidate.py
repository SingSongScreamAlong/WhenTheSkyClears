"""Separate v065: route conform, matched color pipeline, depth-respecting actor reveal."""
import bpy, json, math, hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'work/first_danger_conform_v065'
for d in ['native','previews','evidence','renders/keys','renders/world','renders/inherited','renders/matte','renders/glyph','renders/final']:(O/d).mkdir(parents=True,exist_ok=True)
SOURCE=R/'work/color_arc_v063/native/WTSC_Shared_Color_To_Charcoal_v063.blend'
SOURCE_SHA=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
assert SOURCE_SHA=='d1d4393c3afc77bf71fb8989bd001da56866baaa7f682216a5f05e54e9523687'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
w=bpy.data.scenes['WTSC_SHARED_COLOR_TO_CHARCOAL_v063'];m=bpy.data.scenes['WTSC_FIRST_DANGER_TITLE_CHECK_v060'];edit=bpy.data.scenes['WTSC_FIRST_DANGER_EDIT_v060']
bpy.context.window.scene=w
START=913;CORE0=937;CORE1=1056;END=1080;V=.73125/24
root=bpy.data.objects['V047 | shared travel | steady .73125mps']
actors=[o for o in root.children_recursive if o.type=='MESH' and not o.hide_render]
boots=[o for o in actors if o.get('proportion_role')=='boot']
def curves(a):return [f for l in a.layers for st in l.strips for b in st.channelbags for f in b.fcurves] if a else []
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest()
def art_signature():
 return digest({o.name:{'verts':[list(v.co) for v in o.data.vertices],'polys':[list(p.vertices) for p in o.data.polygons],'uv':[[list(v.uv) for v in uv.data] for uv in o.data.uv_layers]} for o in w.objects if o.type=='MESH' and not any(c.name.startswith('V060 | evaluated boot contact paint') for c in o.users_collection)})
def image_signature():return {i.name:hashlib.sha256(i.packed_file.data).hexdigest() for i in bpy.data.images if i.packed_file}
def action_signature(exclude=()):
 return {a.name:digest([{'p':f.data_path,'i':f.array_index,'x':f.extrapolation,'mods':[x.type for x in f.modifiers],'keys':[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation] for k in f.keyframe_points]} for f in curves(a)]) for a in bpy.data.actions if a.name not in exclude}
def setframe(g):
 w.frame_set(math.floor(g),subframe=g-math.floor(g));bpy.context.view_layer.update()
before_art=art_signature();before_images=image_signature()
oldcam=next(o for o in w.objects if o.type=='CAMERA' and o.name.startswith('v032 | Camera follows shared pair center'))
oldpair=oldcam.animation_data.drivers[0].driver.variables[0].targets[0].id
assert oldpair.parent is None
oldx=next(f for f in curves(oldpair.animation_data.action) if f.data_path=='location' and f.array_index==0)
setframe(981);oldoffset=float(oldcam.matrix_world.translation.x-oldpair.matrix_world.translation.x)
old_camera_samples=[float(oldx.evaluate(g)+oldoffset) for g in range(0,2402)]
for g in [1,913,937,981,1056,1080,2400]:
 setframe(g);assert abs(oldcam.matrix_world.translation.x-old_camera_samples[g])<.00002,(g,oldcam.matrix_world.translation.x,old_camera_samples[g])
print('V065_OLD_ROUTE_VERIFIED',flush=True)
def cold(g):
 i=max(0,min(2400,int(math.floor(g))));return old_camera_samples[i]+(g-i)*(old_camera_samples[i+1]-old_camera_samples[i])
VIN=(cold(START+1)-cold(START-1))/2;VOUT=(cold(END+1)-cold(END-1))/2
L0=CORE0-START;L1=END-CORE1
X0=cold(START);XCORE=X0+.5*(VIN+V)*L0;XCORE1=XCORE+V*(CORE1-CORE0);XEND=XCORE1+.5*(V+VOUT)*L1;OFFSET=XEND-cold(END)
def ramp(x,v0,v1,L,t):
 u=max(0.,min(1.,t/L));return x+v0*t+(v1-v0)*L*(u**3-.5*u**4)
def route(g):
 if g<=START:return cold(g)
 if g<CORE0:return ramp(X0,VIN,V,L0,g-START)
 if g<=CORE1:return XCORE+V*(g-CORE0)
 if g<END:return ramp(XCORE1,V,VOUT,L1,g-CORE1)
 return cold(g)+OFFSET
old_camera_action=w.camera.animation_data.action.name
old_color_action=bpy.data.objects['V063 | shared color to charcoal | both children'].animation_data.action.name
protected_actions=action_signature(exclude=(old_camera_action,old_color_action))
print('V065_SOURCE_SIGNATURES_READY',flush=True)
original_camera=w.camera
cam=original_camera.copy();cam.data=original_camera.data.copy();cam.name='V065 | full-route continuous camera | slow danger passage'
cam.animation_data_clear();w.collection.objects.link(cam);w.camera=cam
# Quarter-frame keys around the speed ramps; original full route outside this interval.
points=sorted(set([float(g) for g in range(1,2401)]+[START+i/4 for i in range((END-START)*4+1)]))
for g in points:
 cam.location.x=route(g);cam.keyframe_insert('location',index=0,frame=g)
for f in curves(cam.animation_data.action):
 f.extrapolation='LINEAR'
 for k in f.keyframe_points:k.interpolation='LINEAR'
cam['route_contract']='Old route before G913; smooth speed match over G913-937; actual .73125m/s tracking G937-1056; smooth exit G1056-1080; old route plus persistent offset thereafter. Do not splice unchanged old downstream frames.'
cam['downstream_offset_m']=OFFSET
cam['source_clock']='F=1+(G-937)*30/24; root travel is already applied once.'

# Keep the current full-cut global color time, with the original reviewed paint ramp.
ctrl=bpy.data.objects['V063 | shared color to charcoal | both children']
ctrl.animation_data_clear();ctrl.name='V065 | both children | global full-cut color time'
ctrl['fade_start_seconds']=0.;ctrl['fade_finish_seconds']=96.
driver=ctrl.driver_add('["charcoal_progress"]').driver
for name,key in [('start','fade_start_seconds'),('end','fade_finish_seconds')]:
 var=driver.variables.new();var.name=name;var.type='SINGLE_PROP';var.targets[0].id=ctrl;var.targets[0].data_path='["'+key+'"]'
u='min(max(((frame-1)/24-start)/max(end-start,0.001),0),1)'
driver.expression='3*('+u+')**2-2*('+u+')**3'
ctrl['scope']='Same global smoothstep clock as the current v064 full cut; inherited v063 paint and neutral charcoal tones. No shot reset.'

# Extend the existing evaluated sole-contact marks into the neighboring handles.
# The actor gait/root/gesture actions themselves are not edited.
contact=bpy.data.collections.get('V060 | evaluated boot contact paint | no physical shadow claim')
if contact:
 contact_objects=list(contact.all_objects)
else:contact_objects=[]
# Contact actions were baked only for the old five-second shot; holding them in the
# new handles would leave floating old marks. Rebuild those eight marks from the
# evaluated unchanged boot geometry, using the existing project helper.
contact_action_names=set(o.animation_data.action.name for o in contact_objects if o.animation_data and o.animation_data.action)
contact_materials=[s.material for o in contact_objects for s in o.material_slots if s.material]
contact_action_names.update(mat.node_tree.animation_data.action.name for mat in contact_materials if mat.node_tree and mat.node_tree.animation_data and mat.node_tree.animation_data.action)
if contact:
 for ob in contact_objects:bpy.data.objects.remove(ob,do_unlink=True)
 bpy.data.collections.remove(contact)
import runpy
stage=root.parent;z0=stage.matrix_world.translation.z;y0=stage.matrix_world.translation.y;slope=(3-z0)/(16+y0)
contacts_report=runpy.run_path(str(R/'work/trailer_development_v060/scripts/add_measured_contacts.py'))['apply'](w,boots,[START+i/4 for i in range((END-START)*4+1)],lambda y:3-slope*(y+16))
print('V065_CONTACT_HANDLES_READY',flush=True)
contact=bpy.data.collections.get('V060 | evaluated boot contact paint | no physical shadow claim')
contact_objects=list(contact.all_objects) if contact else []

w.name='WTSC_FIRST_DANGER_WORLD_v065';m.name='WTSC_FIRST_DANGER_TITLE_v065';edit.name='WTSC_FIRST_DANGER_UNMASKED_EDIT_v065'
for scene in [w,m,edit]:
 scene.frame_start=START;scene.frame_end=END;scene.render.fps=24
 scene.render.resolution_x=3840;scene.render.resolution_y=2160;scene.render.resolution_percentage=100
 scene.render.threads_mode='FIXED';scene.render.threads=2
 scene.render.image_settings.media_type='IMAGE';scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
 scene.render.dither_intensity=0;scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0.;scene.view_settings.gamma=1.
 scene.render.filepath='//../renders/final/'
 if hasattr(scene,'eevee'):scene.eevee.taa_render_samples=32
for st in list(edit.sequence_editor.strips):
 if st.type=='SCENE':edit.sequence_editor.strips.remove(st)
picture=edit.sequence_editor.strips.new_scene('V065 | unmasked native shot | neighboring handles',w,channel=2,frame_start=START);picture.scene_input='CAMERA'

# Cryptomatte uses the *visible* actor contribution from the real world render.
# Foreground illustrated trees still occlude them; no duplicate isolated render
# can incorrectly draw the children over a nearer tree.
vl=w.view_layers[0];vl.use_pass_cryptomatte_object=True;vl.pass_cryptomatte_depth=6;vl.use_pass_cryptomatte_accurate=True
nt=m.compositing_node_group
for node in nt.nodes:
 if node.type=='OUTPUT_FILE':node.mute=True
base=nt.nodes['EXACT BLACK OUTSIDE NATIVE LETTERS'];base.name='V065 | inherited title window | background world'
world_image=base.inputs[7].links[0].from_socket
crypto=nt.nodes.new('CompositorNodeCryptomatteV2');crypto.name='V065 | existing children | visible drawing matte';crypto.scene=w;crypto.layer_name=vl.name+'.CryptoObject'
selected=sorted(actors+contact_objects,key=lambda o:o.name)
crypto.matte_id=','.join(o.name for o in selected)
nt.links.new(world_image,crypto.inputs['Image'])
over=nt.nodes.new('CompositorNodeAlphaOver');over.name='V065 | readable children in foreground of title';over.inputs['Factor'].default_value=1.
nt.links.new(base.outputs[2],over.inputs['Background']);nt.links.new(crypto.outputs['Image'],over.inputs['Foreground'])
output=next(n for n in nt.nodes if n.type=='GROUP_OUTPUT');nt.links.new(over.outputs[0],output.inputs[0])
def fileout(name,folder,socket,rgba=False):
 n=nt.nodes.new('CompositorNodeOutputFile');n.name='V065 | '+name;n.directory=str(O/f'renders/{folder}');n.file_name='frame_####';n.format.media_type='IMAGE';n.format.file_format='PNG';n.format.color_mode='RGBA' if rgba else 'RGB';n.format.color_depth='8';n.save_as_render=True;n.file_output_items.new('RGBA','Image');nt.links.new(socket,n.inputs['Image']);return n
fileout('world export','world',world_image)
fileout('inherited title export','inherited',base.outputs[2])
fileout('visible actor matte','matte',crypto.outputs['Matte'])
glyph=next(n for n in nt.nodes if n.type=='R_LAYERS' and n.scene==m)
fileout('original glyph alpha','glyph',glyph.outputs['Alpha'])

master=bpy.data.scenes.new('WTSC_FIRST_DANGER_REVIEW_MASTER_v065')
master.render.engine='BLENDER_EEVEE';master.render.fps=24;master.frame_start=START;master.frame_end=END
master.render.resolution_x=3840;master.render.resolution_y=2160;master.render.resolution_percentage=100;master.render.use_sequencer=True
master.view_settings.view_transform='Standard';master.view_settings.look='None';master.view_settings.exposure=0.;master.view_settings.gamma=1.;master.render.dither_intensity=0
master.sequence_editor_create();strip=master.sequence_editor.strips.new_scene('V065 | title and readable drawing layers',m,channel=2,frame_start=START);strip.scene_input='CAMERA'
master.sequence_editor.strips.new_sound('Original supplied music | global 38-45 seconds',str(R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'),channel=1,frame_start=1)
master.render.filepath='//../previews/WTSC_First_Danger_v065_4K.mp4'

setframe(981);m.frame_set(981);master.frame_set(981)
after_actions=action_signature()
checks={'world_and_actor_meshes_uvs_unchanged_except_regenerated_contact_quads':art_signature()==before_art,'packed_original_pixels_unchanged':image_signature()==before_images,
        'existing_non_camera_non_palette_non_contact_actions_unchanged':all(after_actions.get(k)==v for k,v in protected_actions.items() if k not in contact_action_names),
        'source_native_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA,
        'matched_world_title_edit_master_view':all(sc.view_settings.view_transform=='Standard' for sc in [w,m,edit,master])}
assert all(checks.values()),checks
report={'source':str(SOURCE),'source_sha256':SOURCE_SHA,'scope':'38-45 seconds, with developed first-danger core39-44. New camera route is provided for full timeline; old downstream exports require rerender. No full-trailer assembly or new story acting is claimed.',
 'range':[START,END],'core_range':[CORE0,CORE1],'seconds':[38,45],'fps':24,'frames':END-START+1,
 'world_scene':w.name,'title_scene':m.name,'unmasked_edit':edit.name,'review_master':master.name,
 'camera_route':{'start_frame':START,'core_start_frame':CORE0,'core_end_frame':CORE1,'end_frame':END,'core_speed_mps':V*24,'entrance_speed_mps':VIN*24,'exit_speed_mps':VOUT*24,'downstream_offset_m':OFFSET,'new_route_samples':[[g,route(g)] for g in [912,913,936,937,981,1056,1057,1080,1081,2400]],'old_route_samples':[[g,cold(g)] for g in [912,913,936,937,981,1056,1057,1080,1081,2400]]},
 'title_method':'Original font geometry/wording/scroll unchanged. Native visible-object Cryptomatte reveals existing children above the letter mask, retaining actual foreground illustration occlusions. No new raster artwork or 3D set replacement.',
 'matte_objects':[o.name for o in selected], 'global_color':'Same absolute-time smoothstep0-96s as v064 full cut, inherited reviewed v063 charcoal values; original alpha/UVs retained.',
 'contacts':contacts_report,'checks':checks,'artistic_acceptance':False}
note=bpy.data.texts.new('START HERE | V065 | first danger conform');note.write(json.dumps(report,indent=2,default=str))
bpy.context.window.scene=master
bpy.ops.file.pack_all();target=O/'native/WTSC_First_Danger_Conformed_v065.blend'
assert not target.exists(),'Preserve prior candidates; choose a fresh version before rebuilding.'
bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
report['native']=str(target);report['native_sha256']=hashlib.sha256(target.read_bytes()).hexdigest()
(O/'evidence/BUILD.json').write_text(json.dumps(report,indent=2,default=str));print('V065_BUILD_COMPLETE',flush=True)
