import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
m=bpy.data.meshes.new('owned probe');m.from_pydata([(0,0,0),(1,0,0),(0,0,1)],[],[(0,1,2)])
o=bpy.data.objects.new('owned probe',m);bpy.context.scene.collection.objects.link(o)
base=o.shape_key_add(name='age0');o.data.shape_keys.use_relative=False
for i in range(1,133):o.shape_key_add(name=f'age{i}')
o.data.shape_keys.use_relative=False
for key in o.data.shape_keys.key_blocks:key.interpolation='KEY_LINEAR'
report={'blender':bpy.app.version_string,'absolute_frames':[key.frame for key in o.data.shape_keys.key_blocks],'eval_time_writable':not o.data.shape_keys.bl_rna.properties['eval_time'].is_readonly,'key_frame_writable':not base.bl_rna.properties['frame'].is_readonly,'no_render':True}
assert max(abs(value-i*10) for i,value in enumerate(report['absolute_frames']))<.01 and report['eval_time_writable'],report
(P/'evidence/absolute_shape_key_probe.json').write_text(json.dumps(report,indent=2));print('ABSOLUTE_GEOMETRY_PROBE',json.dumps(report))
