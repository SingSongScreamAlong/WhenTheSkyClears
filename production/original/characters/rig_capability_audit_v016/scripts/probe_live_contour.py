import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
m=bpy.data.meshes.new('probe');m.from_pydata([(0,0,0),(1,0,0),(0,0,1)],[],[(0,1,2)]);o=bpy.data.objects.new('probe',m);bpy.context.scene.collection.objects.link(o)
c=bpy.data.objects.new('control',None);bpy.context.scene.collection.objects.link(c);c['X']=.2
o.shape_key_add(name='Basis');k=o.shape_key_add(name='Live');k.value=1
fc=m.shape_keys.driver_add('key_blocks["Live"].data[0].co',0);d=fc.driver;v=d.variables.new();v.name='x';v.targets[0].id=c;v.targets[0].data_path='["X"]';d.expression='x+0.1'
bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();a=o.evaluated_get(dg).data.vertices[0].co.x
c['X']=.7;c.update_tag();bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();b=o.evaluated_get(dg).data.vertices[0].co.x
print('LIVE_POINT_PROBE',a,b,fc.driver.is_valid)
(P/'evidence/native_point_driver_probe.json').write_text(json.dumps({'before':a,'after':b,'valid':fc.driver.is_valid}))
