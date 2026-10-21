"""Read-only v043 world, specialist local comparison copy and CPU previews."""
import bpy,runpy,json,hashlib,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1]
source=R/'shots/world/WTSC_Open_Battlefield_Combined_Trial_v043.blend';before=hashlib.sha256(source.read_bytes()).hexdigest()
copy=P/'native/WTSC_v006_Integrated_Comparison_Copy.blend'
if not copy.exists():
 bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
 s=bpy.data.scenes['WTSC_OPEN_BATTLEFIELD_COMBINED_TRIAL_v043'];bpy.context.window.scene=s
 old=next(o for o in s.objects if o.get('loco_pack')=='WTSC_BATTLEFIELD_WEARY_v005');anchor=old.matrix_world.copy()
 old_visible=[o.name for o in old.children_recursive if not o.hide_render]
 for ob in old.children_recursive:
  ob.hide_render=True
  if ob.type in ['MESH','GREASEPENCIL','CURVE']:ob.hide_viewport=True
 with bpy.data.libraries.load(str(P/'native/WTSC_Battlefield_Drawn_Corrections_v006.blend'),link=False) as (available,loaded):loaded.collections=['WTSC_BATTLEFIELD_DRAWN_PAIR_v006']
 s.collection.children.link(loaded.collections[0]);root=next(o for o in loaded.collections[0].all_objects if o.get('motion_revision')=='v006_drawn_pose_corrections');root.matrix_world=anchor
 cfg=runpy.run_path(str(P/'scripts/configure_v006.py'))['configure_v006'];cfg(start=1801,root_motion=True,root=root)
 # Preserve the parent-owned physical light's same source, clock, falloff and
 # eye/dark-paint protection on the newly appended original-paint materials.
 light=s.objects['v043 OWNED | Brief eruption light'];rows=[]
 materials={m for ob in root.children_recursive if hasattr(ob.data,'materials') for m in ob.data.materials if m and m.node_tree}
 for mat in materials:
  nt=mat.node_tree;em=next((n for n in nt.nodes if n.type=='EMISSION'),None)
  if not em or not em.inputs[0].is_linked:continue
  base=em.inputs[0].links[0].from_socket;geo=nt.nodes.new('ShaderNodeNewGeometry');pos=nt.nodes.new('ShaderNodeCombineXYZ')
  for i,axis in enumerate(['LOC_X','LOC_Y','LOC_Z']):
   f=pos.inputs[i].driver_add('default_value');f.driver.expression='p';v=f.driver.variables.new();v.name='p';v.type='TRANSFORMS';v.targets[0].id=light;v.targets[0].transform_type=axis;v.targets[0].transform_space='WORLD_SPACE'
  def mathn(op,a,b):
   n=nt.nodes.new('ShaderNodeMath');n.operation=op
   for i,x in enumerate([a,b]):
    if isinstance(x,(int,float)):n.inputs[i].default_value=x
    else:nt.links.new(x,n.inputs[i])
   return n.outputs[0]
  def remap(x,a,b,c,d):
   n=nt.nodes.new('ShaderNodeMapRange');n.clamp=True;n.interpolation_type='SMOOTHERSTEP'
   for name,val in [('From Min',a),('From Max',b),('To Min',c),('To Max',d)]:n.inputs[name].default_value=val
   nt.links.new(x,n.inputs[0]);return n.outputs[0]
  dist=nt.nodes.new('ShaderNodeVectorMath');dist.operation='DISTANCE';nt.links.new(geo.outputs['Position'],dist.inputs[0]);nt.links.new(pos.outputs[0],dist.inputs[1]);fall=remap(dist.outputs['Value'],2,16,1,0)
  power=nt.nodes.new('ShaderNodeValue');f=power.outputs[0].driver_add('default_value');f.driver.expression='p/1800';v=f.driver.variables.new();v.name='p';v.type='SINGLE_PROP';v.targets[0].id_type='LIGHT';v.targets[0].id=light.data;v.targets[0].data_path='energy'
  lum=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(base,lum.inputs[0]);eye=remap(lum.outputs[0],.18,.65,1,0);protect=remap(lum.outputs[0],.01,.16,.2,1);fac=mathn('MULTIPLY',fall,fall);fac=mathn('MULTIPLY',fac,power.outputs[0]);fac=mathn('MULTIPLY',fac,mathn('MULTIPLY',eye,protect));fac=mathn('MULTIPLY',fac,.025)
  mix=nt.nodes.new('ShaderNodeMix');mix.data_type='RGBA';mix.blend_type='ADD';mix.name='v006 comparison | v043 physical reflected light';mix.inputs[7].default_value=(.85,.31,.065,1);nt.links.new(base,mix.inputs[6]);nt.links.new(fac,mix.inputs[0]);nt.links.new(mix.outputs[2],em.inputs[0]);rows.append(mat.name)
 samples=[];err=0
 for f in range(1801,1921):
  s.frame_set(f);bpy.context.view_layer.update()
  oldrigs={o['character']:o for o in old.children_recursive if o.type=='ARMATURE'};newrigs={o['character']:o for o in root.children_recursive if o.type=='ARMATURE'}
  for who in oldrigs:
   for bn in ['foot_near','foot_far']:
    a=oldrigs[who].matrix_world@oldrigs[who].pose.bones[bn].matrix;b=newrigs[who].matrix_world@newrigs[who].pose.bones[bn].matrix
    err=max(err,max(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4)))
  if f in [1801,1837,1847,1858,1881,1901,1920]:samples.append({'frame':f,'camera':list(s.camera.matrix_world.translation),'root':list(root.matrix_world.translation),'travel':list(next(o for o in root.children if 'TRAVEL' in o.name).matrix_world.translation)})
 assert err<.00003,err
 s.name='V006 | SPECIALIST integrated comparison';s.frame_start=1801;s.frame_end=1920;s.render.use_sequencer=False
 for scene in bpy.data.scenes:scene.render.filepath=str(P/'previews/integrated/OWNED_COMPARISON_ONLY')
 report={'source':str(source),'source_sha256':before,'source_preserved':hashlib.sha256(source.read_bytes()).hexdigest()==before,'comparison_copy':str(copy),'root_anchor':[list(v) for v in anchor],'new_foot_world_matrix_max_error_v043':err,'camera':'Original v043 camera and driver retained, following original hidden travel with identical route.','physical_light':'Original v043 point light, clock, gain .025 and protected-eye material response copied into local comparison only.','old_characters_hidden':old_visible,'materials':rows,'samples':samples,'render_difference':'CPU Cycles two-sample 960x540 proof; original was EEVEE4K. Native geometry/camera/FX clocks retained. Compare performance, not renderer appearance.'}
 (P/'evidence/integrated_comparison.json').write_text(json.dumps(report,indent=2))
 for scene in list(bpy.data.scenes):
  if scene!=s:bpy.data.scenes.remove(scene)
 s.frame_set(1801);bpy.ops.wm.save_as_mainfile(filepath=str(copy),compress=True)
else:
 bpy.ops.wm.open_mainfile(filepath=str(copy),load_ui=False);s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=2;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=960;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.use_sequencer=False;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG'
s.cycles.transparent_max_bounces=64
if hasattr(s.render,'compositor_device'):s.render.compositor_device='CPU'
folder=P/'previews/integrated';folder.mkdir(exist_ok=True)
frames=[1920] if '--probe-transparent' in sys.argv else (range(1801,1921) if '--all' in sys.argv else [1837,1847,1858,1881,1901,1920])
for f in frames:
 path=(P/'evidence/transparency64_probe120.png') if '--probe-transparent' in sys.argv else folder/f'{f-1800:04d}.png'
 if path.exists() and '--rerender' not in sys.argv:continue
 s.frame_set(f);s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
print('V006_ACTUAL_INTEGRATED_COMPARISON_RENDER_DONE',flush=True)
