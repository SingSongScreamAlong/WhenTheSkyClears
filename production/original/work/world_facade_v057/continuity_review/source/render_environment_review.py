import bpy,json,hashlib,time,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
O=Path(__file__).parent;F=O/'frames';F.mkdir(exist_ok=True)
SRC=Path(r'WTSC_LOCAL_WORKSPACE\work\world_facade_v057\WTSC_Continuous_Painterly_Facade_Proof_v057.blend')
EXPECTED='87c897b5ccc178b1288f5d614eeaa34d642b8e8ac2c239bcd2ab50a79569361a'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()==EXPECTED
# Reuse the existing source/object/action preservation functions, without their
# authoring or render code. This review changes only in-memory render settings.
definitions=(O.parent/'facade_candidate_v053/test_registered_candidate.py').read_text()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
definitions=definitions[definitions.index('def val(v):'):definitions.index('bpy.ops.wm.open_mainfile')]
exec(compile(definitions,'existing preservation functions','exec'))
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_CONTINUOUS_FACADE_SOURCE_LIGHTING_v057_TEST'];bpy.context.window.scene=s
s.frame_set(1);baseline=snapshot(s);assert s.render.fps==24 and s.render.fps_base==1
school=s.objects['v016 | School | broken windows and plaster'];mat=school.data.materials[0]
window=sorted([o for o in s.objects if o.name.startswith('v049')],key=lambda o:o.name)
assert len(window)==32,len(window)
anchors=[('plaster_shadow',1045.,535.,64),('exposed_stone',1045.,580.,56),('porch_tiles',1155.,513.,48),('door_surround',1167.,570.,48),('left_join',837.,560.,48)]
def point(px,py):return Vector((65+(px/1672-.5)*22,10,3.29222369194+(.5-py/941)*12.3815793991))
def project(px,py):
 v=world_to_camera_view(s,s.camera,point(px,py));return [v.x*1280,(1-v.y)*720]
def fixed_layer_signature():
 q=[]
 for o in [school,*window]:
  q.append([o.name,[list(x) for x in o.matrix_world],o.hide_render,[(m.name,material(m)) for m in getattr(o.data,'materials',[]) if m]])
  if o.type=='LIGHT':q[-1].append([o.data.energy,list(o.data.color)])
 q.append(['paintUV',[(list(x.uv)) for x in school.data.uv_layers['Paint UV'].data]])
 return sha_text(repr(q))
s.render.engine='BLENDER_EEVEE';s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.render.use_sequencer=False;s.eevee.taa_render_samples=32;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.dither_intensity=0
start=time.monotonic();rows=[]
metadata_only='--metadata-only' in sys.argv
initial_details=None;altered_details={}
def detailed_state():
 data={};mats={}
 for o in [school,*window]:
  data['matrix/'+o.name]=[round(float(v),7) for line in o.matrix_world for v in line];data['hide_render/'+o.name]=o.hide_render
  if o.type=='LIGHT':data['light/'+o.name]=[o.data.energy,*o.data.color]
  for m in getattr(o.data,'materials',[]):
   if m:mats[m.name]=m
 for m in mats.values():
  if m.node_tree:
   for n in m.node_tree.nodes:
    for direction,sockets in [('input',n.inputs),('output',n.outputs)]:
     for i,ss in enumerate(sockets):
      if hasattr(ss,'default_value'):data['node/'+m.name+'/'+n.name+'/'+direction+str(i)+'/'+ss.name]=val(ss.default_value)
 return data
for f in range(1201,1250):
 s.frame_set(f);bpy.context.view_layer.update();assert len(bpy.app.handlers.frame_change_pre)==0 and len(bpy.app.handlers.frame_change_post)==0
 row={'frame':f,'source_seconds':(f-1)/24,'camera_matrix':[list(x) for x in s.camera.matrix_world],'camera_lens':s.camera.data.lens,'camera_shifts':[s.camera.data.shift_x,s.camera.data.shift_y],'fixed_facade_and_window_signature':fixed_layer_signature(),'anchors':{name:{'projected_center':project(x,y),'patch_size':size,'source_pixel':[x,y]} for name,x,y,size in anchors}}
 row['window_review_box']=[*project(866,475),*project(1007,654)]
 if metadata_only:
  details=detailed_state()
  if initial_details is None:initial_details=details
  for k,v in details.items():
   if v!=initial_details[k] and k not in altered_details:altered_details[k]={'first_changed_frame':f,'at1201':initial_details[k],'changed_value':v}
 s.render.filepath=str(F/f'Environment_Continuity_{f:04d}.png')
 if not metadata_only:bpy.ops.render.render(write_still=True,scene=s.name)
 row['file']=str(F/f'Environment_Continuity_{f:04d}.png');rows.append(row)
 if f%8==1:print('ENVIRONMENT_REVIEW_FRAME',f,'OF1249',flush=True)
s.frame_set(1);assert snapshot(s)==baseline;assert hashlib.sha256(SRC.read_bytes()).hexdigest()==EXPECTED
state_count=len(set(x['fixed_facade_and_window_signature'] for x in rows))
assert len(list(F.glob('Environment_Continuity_*.png')))==49
q={'status':'RENDERED; temporal visual acceptance pending','purpose':'Environment continuity review only; existing character animation unchanged.','source_native':str(SRC),'source_sha256':EXPECTED,'source_unchanged':True,'source_scene':s.name,'frame_start':1201,'frame_end':1249,'frame_count':49,'source_fps':24,'source_fps_base':1,'duration_seconds':49/24,'camera_traversal_seconds':48/24,'render_dimensions':[1280,720],'samples':32,'threads':2,'render_elapsed_seconds':None if metadata_only else time.monotonic()-start,'metadata_only_recovery':metadata_only,'source_objects_actions_children_timing_preserved':snapshot(s)==baseline,'object_count':len(baseline['objects']),'action_count':len(baseline['actions']),'child_material_sets':len(baseline['children']),'fixed_facade_and_window_signature_unchanged_all49frames':state_count==1,'facade_window_distinct_exact_state_count':state_count,'fixed_window_object_count':len(window),'fixed_window_objects':[o.name for o in window],'new_character_motion_authored':False,'native_saved_or_modified':False,'rows':rows}
q['state_variation_diagnostics']=altered_details
(O/'ENVIRONMENT_RENDER_VERIFICATION.json').write_text(json.dumps(q,indent=2));print('ENVIRONMENT_REVIEW_RENDER_COMPLETE',json.dumps({k:v for k,v in q.items() if k not in ['rows','fixed_window_objects']}),flush=True)
