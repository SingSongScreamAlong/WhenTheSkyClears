"""Capture one real-scene plate; animate native FX/occlusion/local light over it."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
world=bpy.data.scenes['FX_BENCHMARK_v002 | real battlefield copy'];bpy.context.window.scene=world;world.frame_set(1825)
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();fx=bpy.data.collections['FXv002 | Detailed painterly ground eruption'];root=bpy.data.objects['FXv002 | fixed ground origin and controls']
for i in range(3):
 f=root.driver_add('scale',i);f.driver.expression='S';v=f.driver.variables.new();v.name='S';v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["size"]'
proof=bpy.data.scenes.new('FX_SHOT_PROOF_v002 | held real shot + native eruption');proof.collection.children.link(fx)
holdouts=bpy.data.collections.new('FXv002 proof | frozen native foreground occlusion');proof.collection.children.link(holdouts)
lightcol=bpy.data.collections.new('FXv002 proof | source-anchored paint relighting');proof.collection.children.link(lightcol)
cam=world.camera.copy();cam.data=world.camera.data.copy();cam.animation_data_clear();cam.parent=None;cam.matrix_world=world.camera.matrix_world.copy();proof.collection.objects.link(cam);proof.camera=cam

def clone_frozen(ob,col,name):
 eo=ob.evaluated_get(dg);me=bpy.data.meshes.new_from_object(eo,preserve_all_data_layers=True,depsgraph=dg)
 n=bpy.data.objects.new(name,me);col.objects.link(n);n.matrix_world=ob.matrix_world.copy();return n

matcache={};occluders=[]
for ob in world.objects:
 if ob.type!='MESH' or ob.hide_render or ob.name.startswith('FXv002'):continue
 p=[ob.matrix_world@Vector(c) for c in ob.bound_box]
 if not p:continue
 if min(q.y for q in p)>=9.95 or max(q.x for q in p)<103 or min(q.x for q in p)>115 or max(ob.dimensions.x,ob.dimensions.z)<.15:continue
 n=clone_frozen(ob,holdouts,'HOLDOUT | '+ob.name)
 for i,m in enumerate(list(n.data.materials)):
  if not m or not m.node_tree:continue
  if m.name not in matcache:
   hm=m.copy();hm.name='Holdout alpha | '+m.name;nt=hm.node_tree;nt.animation_data_clear();h=nt.nodes.new('ShaderNodeHoldout');h.name='Native foreground holdout | original paint alpha retained'
   for em in [x for x in nt.nodes if x.type in {'EMISSION','BSDF_PRINCIPLED','BSDF_DIFFUSE'}]:
    for link in list(em.outputs[0].links):nt.links.new(h.outputs[0],link.to_socket)
   matcache[m.name]=hm
  n.data.materials[i]=matcache[m.name]
 occluders.append(n.name)

receivers=[]
for ob in world.objects:
 if ob.type!='MESH' or not ob.data.materials or not ob.data.materials[0] or not ob.data.materials[0].name.startswith('FXv002 receiver'):continue
 n=clone_frozen(ob,lightcol,'LIGHT RESPONSE | '+ob.name);m=ob.data.materials[0].copy();m.name='Proof overlay | '+ob.name;n.data.materials.clear();n.data.materials.append(m);nt=m.node_tree
 tint=nt.nodes.get('FXv002 | only local warm paint response');out=next(x for x in nt.nodes if x.type=='OUTPUT_MATERIAL');terminal=out.inputs[0].links[0].from_node
 assert tint and terminal.type=='MIX_SHADER',(ob.name,terminal.type)
 weight=tint.inputs[0].links[0].from_socket;old_alpha=terminal.inputs[0].links[0].from_socket
 nt.links.remove(tint.inputs[0].links[0]);tint.inputs[0].default_value=1
 alpha=nt.nodes.new('ShaderNodeMath');alpha.operation='MULTIPLY';nt.links.new(weight,alpha.inputs[0]);nt.links.new(old_alpha,alpha.inputs[1]);nt.links.new(alpha.outputs[0],terminal.inputs[0])
 if nt.animation_data:
  for f in nt.animation_data.drivers:
   for v in f.driver.variables:
    if v.targets[0].id==world.camera:v.targets[0].id=cam
 n.location.y-=.003;receivers.append(n.name)

proof.render.engine='CYCLES';proof.cycles.device='CPU';proof.cycles.samples=8;proof.cycles.use_denoising=True;proof.cycles.max_bounces=2;proof.cycles.transparent_max_bounces=40
proof.render.threads_mode='FIXED';proof.render.threads=2;proof.render.fps=24;proof.render.resolution_x=3840;proof.render.resolution_y=2160;proof.render.resolution_percentage=100
proof.render.film_transparent=True;proof.view_settings.view_transform='Standard';proof.view_settings.look='None';proof.render.image_settings.media_type='IMAGE';proof.render.image_settings.file_format='PNG';proof.render.image_settings.color_mode='RGBA';proof.world=bpy.data.worlds.new('FX proof black world');proof.world.color=(0,0,0);proof.frame_start=1795;proof.frame_end=1890
proof.use_nodes=True;nt=bpy.data.node_groups.new('FXv002 | real scene plate + native occluded relit eruption','CompositorNodeTree');proof.compositing_node_group=nt;nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
bg=nt.nodes.new('CompositorNodeImage');bg.name='Real world captured at frame1825 | camera and children held'
scale=nt.nodes.new('CompositorNodeScale');scale.name='Base plate resize | X=Y=render percentage divided100';scale.inputs['Type'].default_value='Relative';scale.inputs['X'].default_value=1;scale.inputs['Y'].default_value=1;nt.links.new(bg.outputs['Image'],scale.inputs['Image'])
rl=nt.nodes.new('CompositorNodeRLayers');rl.scene=proof
glow=nt.nodes.new('CompositorNodeGlare');glow.inputs['Type'].default_value='Fog Glow';glow.inputs['Quality'].default_value='High';glow.inputs['Threshold'].default_value=1.7;glow.inputs['Strength'].default_value=.07;glow.inputs['Size'].default_value=.08;nt.links.new(rl.outputs['Image'],glow.inputs['Image'])
over=nt.nodes.new('CompositorNodeAlphaOver');over.inputs['Factor'].default_value=1;nt.links.new(scale.outputs['Image'],over.inputs['Background']);nt.links.new(glow.outputs['Image'],over.inputs['Foreground']);out=nt.nodes.new('NodeGroupOutput');nt.links.new(over.outputs['Image'],out.inputs['Image'])

# One4K capture of the real scene, with new effects and their receiver response off.
fx.hide_render=True
for ob in world.objects:
 if ob.type=='MESH':
  for m in ob.data.materials:
   if m and m.node_tree and m.name.startswith('FXv002 receiver'):
    v=m.node_tree.nodes.get('FXv002 source-synchronous local light')
    if v:v.outputs[0].driver_remove('default_value');v.outputs[0].default_value=0
bpy.context.window.scene=world;world.frame_set(1825);world.render.resolution_percentage=100;world.cycles.samples=6;world.render.filepath=str(P/'assets/Real_Scene_Base_Plate_4K_v002.png')
print('FX_PROOF_BASE_PLATE_START',len(occluders),'holdouts',flush=True);bpy.ops.render.render(write_still=True,scene=world.name)
fx.hide_render=False
im=bpy.data.images.load(world.render.filepath);im.name='FXv002 | captured original world at frame1825';im.alpha_mode='STRAIGHT';im.pack();bg.image=im
bpy.context.window.scene=proof;proof.frame_set(1825);proof.render.filepath=str(P/'previews/WTSC_Explosion_Benchmark_4K_v002.png')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_FX_Shot_Proof_v002.blend'),compress=True)
bpy.data.libraries.write(str(P/'native/WTSC_Hero_Eruption_Collection_v002.blend'),{fx},fake_user=True,compress=True)
bpy.ops.render.render(write_still=True,scene=proof.name)
report={'proof_scene':proof.name,'native_file':str(P/'native/WTSC_FX_Shot_Proof_v002.blend'),'base_plate_pixels':[3840,2160],'base_plate_source_frame':1825,'camera_and_children':'Held for FX evaluation; this is not a moving trailer/locomotion test. Foreground geometry is evaluated from the actual scene at the same frame and rendered as alpha-preserving holdouts.','native_occluders':occluders,'native_light_receivers':receivers,'medium':'Original detailed paint with native root-pinned flow, dust, solid debris and local relighting. This is2.5D, not a volumetric fluid simulation.','first4K_frame':str(P/'previews/WTSC_Explosion_Benchmark_4K_v002.png'),'resource':'One sequential two-thread CPU process; no GPU job or shared UI.'}
(P/'evidence/shot_proof_setup.json').write_text(json.dumps(report,indent=2));print('FX_4K_SHOT_PROOF_FRAME_COMPLETE',json.dumps({k:v for k,v in report.items() if k not in ['native_occluders']}),flush=True)
