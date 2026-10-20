import bpy,json,hashlib
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');O=Path(r'WTSC_LOCAL_USER\Documents\Codex\2026-10-16\task\color_progression_study_v049');O.mkdir(exist_ok=True)
src=R/'work/world_art_v048d/WTSC_World_Art_Checkpoint_v048d.blend';out=O/'WTSC_Three_Still_Color_Test_v049.blend';assert not out.exists()
source_hash=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);s=bpy.data.scenes['WTSC_WORLD_ART_v048d_OPEN_DIAGNOSTIC'];bpy.context.window.scene=s
stages=[{'frame':241,'label':'peaceful','world_saturation':.95,'child_saturation':1.,'child_warmth':.75},{'frame':1201,'label':'transition','world_saturation':.22,'child_saturation':1.,'child_warmth':.75},{'frame':1849,'label':'war_zone','world_saturation':.08,'child_saturation':.06,'child_warmth':.04}]
def constant_keys(socket,field):
 for stage in stages:socket.default_value=stage[field];socket.keyframe_insert('default_value',frame=stage['frame'])
 a=socket.id_data.animation_data.action
 for l in a.layers:
  for st in l.strips:
   for bag in st.channelbags:
    for fc in bag.fcurves:
     if fc.data_path==socket.path_from_id():
      for key in fc.keyframe_points:key.interpolation='CONSTANT'
cache={};world_mats=[]
for o in s.objects:
 if o.type!='MESH' or not any(k in o.name for k in ['Village','village','Woods','School','Camp','Battlefield','Ruins','Countryside','Walking path','Foreground bank','fixed foreground soil bank','High crown','Rooted grass','path shoulder stone','Opening oak roots']):continue
 if any(k in o.name.lower() for k in ['smoke','flame','wisp','ember','fire','fx','dust']):continue
 for i,old in enumerate(list(o.data.materials)):
  if not old or not old.use_nodes:continue
  if old.name not in cache:
   m=old.copy();m.name='COLOR TEST v049 | WORLD | '+old.name;nt=m.node_tree
   for em in [n for n in list(nt.nodes) if n.type=='EMISSION' and n.inputs[0].is_linked]:
    old_socket=em.inputs[0].links[0].from_socket;h=nt.nodes.new('ShaderNodeHueSaturation');h.name='COLOR TEST ONLY | world loses saturation first';nt.links.new(old_socket,h.inputs['Color']);constant_keys(h.inputs['Saturation'],'world_saturation');nt.links.new(h.outputs[0],em.inputs[0])
   cache[old.name]=m;world_mats.append(m.name)
  o.data.materials[i]=cache[old.name]
actor=s.objects['v015 | Near-black painted fill | GP vector clipped'];old=actor.data.materials[0];m=old.copy();m.name='COLOR TEST v049 | CHILDREN | restrained umber to charcoal';actor.data.materials[0]=m;nt=m.node_tree;em=next(n for n in nt.nodes if n.type=='EMISSION');old_socket=em.inputs[0].links[0].from_socket
h=nt.nodes.new('ShaderNodeHueSaturation');h.name='COLOR TEST | drain children by war';nt.links.new(old_socket,h.inputs['Color']);constant_keys(h.inputs['Saturation'],'child_saturation')
bw=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(h.outputs[0],bw.inputs[0]);mask=nt.nodes.new('ShaderNodeMapRange');mask.clamp=True;mask.interpolation_type='SMOOTHERSTEP';mask.inputs['From Min'].default_value=.14;mask.inputs['From Max'].default_value=.42;mask.inputs['To Min'].default_value=1.;mask.inputs['To Max'].default_value=0.;nt.links.new(bw.outputs[0],mask.inputs[0]);amount=nt.nodes.new('ShaderNodeValue');constant_keys(amount.outputs[0],'child_warmth');fac=nt.nodes.new('ShaderNodeMath');fac.operation='MULTIPLY';nt.links.new(mask.outputs[0],fac.inputs[0]);nt.links.new(amount.outputs[0],fac.inputs[1]);mix=nt.nodes.new('ShaderNodeMixRGB');mix.name='COLOR TEST | preserve value and eye accents';mix.blend_type='MULTIPLY';mix.inputs[2].default_value=(1.55,1.03,.59,1);nt.links.new(fac.outputs[0],mix.inputs[0]);nt.links.new(h.outputs[0],mix.inputs[1]);nt.links.new(mix.outputs[0],em.inputs[0])
s.name='WTSC_THREE_STILL_COLOR_TEST_v049';s['color_test_scope']='Three approved still tests only; CONSTANT preset anchors are not an approved film color curve. No geometry/rig/contact/performance changes. No new hand contact or residual accent.'
for stage in stages:
 s.frame_set(stage['frame']);bpy.context.view_layer.update()
s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.threads_mode='FIXED';s.render.threads=2;s.eevee.taa_render_samples=32;s.frame_set(241)
note=bpy.data.texts.new('COLOR STUDY ONLY | presets and boundaries');note.write(json.dumps({'presets':stages,'warm_multiplier':[1.55,1.03,.59],'eye_protection':'Luma mask falls from1 at linear.14 to0 at.42; geometry and opacity untouched.','timing':'CONSTANT keys solely select the three still presets. Do not infer transition durations or propagate to production.'},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);(O/'previews').mkdir(exist_ok=True);s.render.resolution_percentage=25;s.eevee.taa_render_samples=16
for stage in stages:
 s.frame_set(stage['frame']);s.render.filepath=str(O/'previews'/f"Color_Test_{stage['label']}_{stage['frame']}_960.png");bpy.ops.render.render(write_still=True,scene=s.name);print('COLOR_PREVIEW',stage['label'],flush=True)
report={'native':str(out),'source':str(src),'source_sha256':source_hash,'source_unchanged':hashlib.sha256(src.read_bytes()).hexdigest()==source_hash,'stages':stages,'world_materials':world_mats,'child_material':m.name,'warmth_multiplier':[1.55,1.03,.59],'new_geometry':False,'alpha_changed':False,'new_hand_contact':False,'residual_accent':'None added; war preset tends to neutral charcoal.','status':'TEST ONLY; no full-film propagation or approved transition curve'};(O/'COLOR_TEST_REPORT_v049.json').write_text(json.dumps(report,indent=2));print('COLOR_STUDY_NATIVE',str(out),flush=True)
