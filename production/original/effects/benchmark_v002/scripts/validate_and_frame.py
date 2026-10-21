import bpy,json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1]
s=bpy.data.scenes['FX_SHOT_PROOF_v002 | held real shot + native eruption'];bpy.context.window.scene=s
fixed=[]
for m in bpy.data.materials:
 if not m.node_tree or not m.node_tree.animation_data:continue
 if not m.name.startswith(('FXv002','Proof overlay')):continue
 for f in m.node_tree.animation_data.drivers:
  for v in f.driver.variables:
   if v.targets[0].data_path=='location.x':v.targets[0].data_path='location[0]';f.driver.expression=f.driver.expression;fixed.append(m.name)
s.frame_set(1826);s.frame_set(1825);bpy.context.view_layer.update()
root=bpy.data.objects['FXv002 | fixed ground origin and controls'];states=[]
for f in [1795,1814,1825,1840,1870,1890]:
 s.frame_set(f);bpy.context.view_layer.update();states.append({'frame':f,'age':root['age'],'root':list(root.matrix_world.translation)})
assert max(max(abs(x-y) for x,y in zip(a['root'],states[0]['root'])) for a in states)<1e-6
bad=[]
ids=[o for o in bpy.data.objects if o.name.startswith('FXv002')]
ids += [m.node_tree for m in bpy.data.materials if m.node_tree and m.name.startswith(('FXv002','Proof overlay'))]
ids += [k for k in bpy.data.shape_keys if any(o.data.shape_keys==k for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('FXv002'))]
for id in ids:
 if id.animation_data:
  bad += [{'id':id.name,'path':f.data_path,'expression':f.driver.expression} for f in id.animation_data.drivers if not f.driver.is_valid]
assert not bad,bad
report={'fixed_camera_component_paths':fixed,'invalid_own_drivers':bad,'fixed_root_samples':states,'source_unchanged':hashlib.sha256(Path(json.loads((P/'evidence/benchmark_build.json').read_text())['source']).read_bytes()).hexdigest()==json.loads((P/'evidence/benchmark_build.json').read_text())['source_sha256'],'alpha_pipeline':'Native premultiplied compositor render over captured original real-scene plate; original source images use Straight alpha.','artistic_status':'Not accepted. Still and actual motion must be judged separately from these technical checks.'}
assert report['source_unchanged'];(P/'evidence/benchmark_native_validation.json').write_text(json.dumps(report,indent=2))
s.frame_set(1825);s.render.resolution_percentage=100;s.cycles.samples=8
if hasattr(s.render,'compositor_device'):s.render.compositor_device='CPU'
scale=next(n for n in s.compositing_node_group.nodes if n.type=='SCALE');scale.inputs['X'].default_value=1;scale.inputs['Y'].default_value=1
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath,compress=True)
s.render.filepath=str(P/'previews/WTSC_Explosion_Benchmark_4K_v002.png');bpy.ops.render.render(write_still=True,scene=s.name)
print('FX_VALIDATED_AND_4K_FRAME_SAVED',json.dumps(report),flush=True)
