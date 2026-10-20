"""Full timeline procedural palette; full-cut drawings and route remain unchanged."""
import bpy,json,hashlib,runpy,math
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');O=R/'work/procedural_cut_v064'
S=R/'work/world_minimum_v058/WTSC_World_Development_v058_Packed.blend'
assert hashlib.sha256(S.read_bytes()).hexdigest()=='13c2aee075315131eac6f85d9d726b766051a84edffa961f4ec38ecf7029a890'
# The preserved manifest is checked again below; tolerate no silently changed source.
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False)
w=bpy.data.scenes['WTSC_WORLD_FOREGROUND_v058d'];e=bpy.data.scenes['WTSC_FULL_FILM_KNOCKOUT_v040'];m=bpy.data.scenes['WTSC_MASTER_4K_106S_v040']
bpy.context.window.scene=w;w.frame_set(1)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,default=str).encode()).hexdigest()
def actions(id):
 a=getattr(id,'animation_data',None)
 if not a or not a.action:return []
 return [dict(path=f.data_path,index=f.array_index,extrap=f.extrapolation,mod=[x.type for x in f.modifiers],keys=[[list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation] for k in f.keyframe_points]) for l in a.action.layers for st in l.strips for b in st.channelbags for f in b.fcurves]
def geometry(scene):
 rows=[]
 for o in sorted(scene.objects,key=lambda x:x.name):
  row=dict(name=o.name,type=o.type,parent=getattr(o.parent,'name',None),matrix=[list(v) for v in o.matrix_basis],inverse=[list(v) for v in o.matrix_parent_inverse],hide=o.hide_render,action=actions(o))
  if o.type=='MESH':row.update(vertices=[list(v.co) for v in o.data.vertices],poly=[list(p.vertices) for p in o.data.polygons],uv=[[list(v.uv) for v in uv.data] for uv in o.data.uv_layers])
  elif o.type=='GREASEPENCIL':row['drawing']=[[list(v.vector) for v in f.drawing.attributes['position'].data] for l in o.data.layers for f in l.frames]
  if o.type=='CAMERA':row['camera']={k:getattr(o.data,k) for k in ['type','lens','ortho_scale','shift_x','shift_y']}
  rows.append(row)
 return digest(rows)
def glyphs(scene):
 scene.frame_set(1)
 rows=[]
 for ob in sorted(scene.objects,key=lambda x:x.name):
  row=dict(name=ob.name,type=ob.type,local=[list(r) for r in ob.matrix_local],hide=ob.hide_render,action=actions(ob))
  if ob.type=='FONT':
   row['font']={k:getattr(ob.data,k) for k in ['body','size','align_x','align_y','space_character','space_word','space_line','offset','extrude','bevel_depth','resolution_u','fill_mode','shear']}
   row['font']['packed_sha256']=hashlib.sha256(ob.data.font.packed_file.data).hexdigest();row['data_action']=actions(ob.data)
  if ob.type=='CAMERA':row['camera']={k:getattr(ob.data,k) for k in ['type','ortho_scale','lens','shift_x','shift_y','clip_start','clip_end']}
  rows.append(row)
 return digest(dict(objects=rows,res=[scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage,scene.render.fps],transparent=scene.render.film_transparent,frames=[scene.frame_start,scene.frame_end]))
def image_hashes():return {i.name:hashlib.sha256(i.packed_file.data).hexdigest() for i in bpy.data.images if i.packed_file}
before_geom=geometry(w);before_glyph=glyphs(e);before_imgs=image_hashes()
all_actions={a.name:actions(o) for o in bpy.data.objects if (a:=getattr(getattr(o,'animation_data',None),'action',None))}
fill=next(o for o in w.objects if 'Near-black painted fill' in o.name)
old_materials=[s.material for s in fill.material_slots]
color=runpy.run_path(str(O/'scripts/color_original_pair_v064.py'))['apply'](w,fill)
ctrl=bpy.data.objects.new('V064 | global procedural color loss | BOTH children',None);w.collection.objects.link(ctrl)
ctrl['charcoal_progress']=0.;ctrl.id_properties_ui('charcoal_progress').update(min=0.,max=1.,description='Global procedural transition for BOTH original children')
mat=fill.material_slots[0].material;mat.surface_render_method='DITHERED';mix=mat.node_tree.nodes[color['mix_node']]
# A blend toward very dark ink alone retains chroma too long. Remove saturation
# continuously as well, while resolving to the exact original charcoal endpoint.
nt=mat.node_tree;full_color=mix.inputs[1].links[0].from_socket
desat=nt.nodes.new('ShaderNodeHueSaturation');desat.name='V064 | continuous pigment saturation loss'
desat.inputs['Hue'].default_value=.5;desat.inputs['Value'].default_value=1.;desat.inputs['Fac'].default_value=1.
nt.links.new(full_color,desat.inputs['Color']);nt.links.new(desat.outputs['Color'],mix.inputs[1])
sd=desat.inputs['Saturation'].driver_add('default_value').driver
sv=sd.variables.new();sv.name='progress';sv.type='SINGLE_PROP';sv.targets[0].id=ctrl;sv.targets[0].data_path='["charcoal_progress"]';sd.expression='1-progress'
color['procedural_saturation_node']=desat.name;color['saturation_method']='1 minus shared global progress, with detail-preserving charcoal values'
gray=nt.nodes.new('ShaderNodeRGBToBW');gray.name='V064 | full painted detail luminance';nt.links.new(full_color,gray.inputs[0])
tones=[(0.,.006),(.06,.014),(.22,.032),(.5,.068),(1.,.12)]
ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.name='V064 | reviewed v063 neutral charcoal values';ramp.color_ramp.interpolation='EASE'
els=ramp.color_ramp.elements;els[0].position=tones[0][0];els[0].color=(tones[0][1],)*3+(1.,);els[1].position=tones[-1][0];els[1].color=(tones[-1][1],)*3+(1.,)
for pos,value in tones[1:-1]:els.new(pos).color=(value,)*3+(1.,)
nt.links.new(gray.outputs[0],ramp.inputs['Fac']);nt.links.new(ramp.outputs['Color'],mix.inputs[2])
mix.name='V064 | full color to charcoal | shared time';color['mix_node']=mix.name
color['factor_meaning']='0 full painted color; 1 reviewed v063 neutral charcoal values retaining facial and cloth detail'
color['charcoal_tones']=tones;color['root_refinement']='Original oldLit branch retained internally; final endpoint refined to reviewed v063 neutral charcoal, so natural painted facial features remain visible.'
color['limits']=[x for x in color['limits'] if not x.startswith('Factor1 restores')]
color['limits'].append('Final native uses the reviewed v063 neutral charcoal ramp, not the helper original oldLit endpoint; painted facial detail is preserved.')
fd=mix.inputs[0].driver_add('default_value').driver;v=fd.variables.new();v.name='progress';v.type='SINGLE_PROP';v.targets[0].id=ctrl;v.targets[0].data_path='["charcoal_progress"]';fd.expression='progress'
arc=dict(controller=ctrl.name,property='charcoal_progress',object_count=1,material_count=1,children=2,endpoint='Reviewed v063 neutral charcoal values retaining painted facial and cloth detail',skipped=[])
ctrl['fade_start_seconds']=0.;ctrl['fade_finish_seconds']=96.
ctrl.id_properties_ui('fade_start_seconds').update(min=0.,max=99.,description='Global trailer seconds: full painted color before this time')
ctrl.id_properties_ui('fade_finish_seconds').update(min=1.,max=100.,description='Global trailer seconds: both children reach charcoal by this time')
prop=arc['property'];fc=ctrl.driver_add('["'+prop+'"]');dr=fc.driver
for name,path in [('start','fade_start_seconds'),('end','fade_finish_seconds')]:
 v=dr.variables.new();v.name=name;v.type='SINGLE_PROP';v.targets[0].id=ctrl;v.targets[0].data_path='["'+path+'"]'
u='min(max(((frame-1)/24-start)/max(end-start,0.001),0),1)'
dr.expression='3*('+u+')**2-2*('+u+')**3'
ctrl['V064_method']='Smoothstep of global elapsed seconds. Driver uses absolute frame, never local shot or walk clocks. No palette keyframes.'
# Exact camera and geometry checks are made at matching source frame1.
bpy.context.window.scene=w;w.frame_set(1);bpy.context.view_layer.update()
# Controller is the only new world object, so omit it for preservation comparison.
w.collection.objects.unlink(ctrl)
checks=dict(world_geometry_uvs_transforms_visibility_actions_camera_exact=geometry(w)==before_geom,mask_and_credits_exact=glyphs(e)==before_glyph,original_packed_pixels_unchanged=all(image_hashes().get(k)==v for k,v in before_imgs.items()),original_pair_materials_retained=all(x in bpy.data.materials[:] for x in old_materials))
w.collection.objects.link(ctrl)
checks['original_action_curves_exact']=all(actions(o)==all_actions[a.name] for o in bpy.data.objects if (a:=getattr(getattr(o,'animation_data',None),'action',None)) and a.name in all_actions)
assert all(checks.values()),checks
world_node=next(n for n in e.compositing_node_group.nodes if n.type=='R_LAYERS' and n.scene!=e)
inherited_world=world_node.scene.name;world_node.scene=w
picture=next(x for x in m.sequence_editor.strips if x.type=='SCENE')
sound=next(x for x in m.sequence_editor.strips if x.type=='SOUND')
assert picture.scene==e and picture.frame_start==1 and picture.frame_final_duration==2544
assert sound.frame_start==1 and sound.frame_final_duration==2400
assert m.frame_end==e.frame_end==2544 and w.frame_end==2400
assert all(s.render.fps==24 and s.view_settings.view_transform=='Standard' for s in [w,e,m])
samples=[];values=[]
bpy.context.window.scene=w
for f in [1,433,841,937,1056,1057,1201,1609,1921,2161,2305,2400,2401]:
 w.frame_set(f);bpy.context.view_layer.update();p=ctrl[prop];t=(f-1)/24;u=min(1,max(0,t/96));expect=u*u*(3-2*u)
 assert abs(p-expect)<2e-6,(f,p,expect)
 values.append(p)
 if f in [1,433,841,937,1056,1057,1201,1609,1921,2161,2305,2400,2401]:
  mix=fill.material_slots[0].material.node_tree.nodes[color['mix_node']]
  assert abs(mix.inputs[0].default_value-p)<2e-6
  assert abs(desat.inputs['Saturation'].default_value-(1-p))<2e-6
  samples.append(dict(frame=f,seconds=t,progress=p,camera=list(w.camera.location)))
assert all(b>=a-1e-7 for a,b in zip(values,values[1:]))
w.name='WTSC_PROCEDURAL_COLOR_WORLD_v064';e.name='WTSC_PROCEDURAL_FULL_CUT_v064';m.name='WTSC_PROCEDURAL_MASTER_106S_v064'
for scene,label in [(w,'World'),(e,'Knockout'),(m,'Master')]:scene.render.filepath='//../renders/WTSC_Procedural_'+label+'_4K_v064.mp4'
note='Full106-second cut with procedural color loss for BOTH ORIGINAL full-cut children. Preserved full-cut held drawings, route, layered painted sets, title and credits. Palette only; v063 first-danger acting remains a separate preserved branch, not stretched into a full gait.'
w['V064_scope']=note;w['V064_controller']=ctrl.name
text=bpy.data.texts.new('START HERE | V064 | procedural full cut');text.write(note+'\n'+json.dumps(dict(controller=ctrl.name,property=prop,expression=dr.expression,color=color,checks=checks),indent=2,default=str))
for p in ['native','previews','evidence','previews/world_frames','renders']:(O/p).mkdir(parents=True,exist_ok=True)
bpy.ops.file.pack_all();bpy.context.window.scene=m;m.frame_set(1)
native=O/'native/WTSC_Procedural_Full_Trailer_v064.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
report=dict(source=str(S),source_sha256=hashlib.sha256(S.read_bytes()).hexdigest(),native=str(native),native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),world_scene=w.name,picture_scene=e.name,master_scene=m.name,checks=checks,all_checks_pass=all(checks.values()),unchanged_mask_and_credits_signature=True,mask_signature=before_glyph,controller=ctrl.name,property=prop,driver_expression=dr.expression,start_seconds=0,finish_seconds=96,palette_keyframes=0,global_palette_samples=samples,monotonic_samples=len(values),color_material=color,arc=arc,scope=note,inherited_world_reference=inherited_world)
(O/'evidence/FULL_CUT_BUILD.json').write_text(json.dumps(report,indent=2,default=str))
print('V064_NATIVE_FULL_PROCEDURAL_CUT_SAVED',flush=True)
# Native actual-global-time pilots. Lower output settings are never saved.
for scene,frames,prefix in [(w,[1,841,1609,2305],'world'),(e,[841,1609,2305,2401],'cut')]:
 bpy.context.window.scene=scene;scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
 if hasattr(scene,'eevee'):scene.eevee.taa_render_samples=32
 for f in frames:
  scene.frame_set(f);scene.render.image_settings.media_type='IMAGE';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(O/f'previews/{prefix}_{f:04d}.png');bpy.ops.render.render(write_still=True,scene=scene.name)
assert hashlib.sha256(native.read_bytes()).hexdigest()==report['native_sha256']
bpy.context.window.scene=w;w.frame_set(1);w.render.resolution_x=3840;w.render.resolution_y=2160;w.render.filepath=str(O/'previews/Native_Opening_4K_v064.png');bpy.ops.render.render(write_still=True,scene=w.name)
# Prove the inherited native glyph/card objects still match the preserved full-cut source.
reference=R/'shots/world/WTSC_Painted_World_Full_Trailer_Editable_v040.blend'
assert hashlib.sha256(reference.read_bytes()).hexdigest()=='c3ed3c15055ae5cd242a68964d6980bb8bda3ff6f7f4882d69fa4198e937819f'
bpy.ops.wm.open_mainfile(filepath=str(reference),load_ui=False,use_scripts=False)
assert glyphs(bpy.data.scenes['WTSC_FULL_FILM_KNOCKOUT_v040'])==before_glyph,'Glyph/card differs from v040: cached alpha not reusable'
report['mask_reference_v040_verified']=True;report['mask_reference_source_sha256']=hashlib.sha256(reference.read_bytes()).hexdigest()
(O/'evidence/FULL_CUT_BUILD.json').write_text(json.dumps(report,indent=2,default=str))
print('V064_FULL_CUT_PILOTS_COMPLETE',flush=True)
