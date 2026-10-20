import bpy,json
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\work\production_review_v059')
bpy.ops.wm.open_mainfile(filepath=str(O/'WTSC_Production_Benchmark_v059.blend'),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_TITLE_VISIBILITY_REVIEW_v059'];bpy.context.window.scene=s
d={'objects':[],'samples':[],'master':{}}
for ob in s.objects:
 d['objects'].append({'name':ob.name,'type':ob.type,'action':ob.animation_data.action.name if ob.animation_data and ob.animation_data.action else None,'drivers':[{'path':f.data_path,'expression':f.driver.expression,'vars':[(v.name,[(t.id.name if t.id else None,t.data_path) for t in v.targets]) for v in f.driver.variables]} for f in ob.animation_data.drivers] if ob.animation_data else []})
for f in [1801,1844,1901,1918]:
 s.frame_set(f);bpy.context.view_layer.update();d['samples'].append({'f':f,'locations':{o.name:list(o.matrix_world.translation) for o in s.objects}})
world=bpy.data.scenes['WTSC_RECOVERY_WORLD_v059'];master=bpy.data.scenes['WTSC_5S_REVIEW_MASTER_v059']
d['master']={'view':master.view_settings.view_transform,'world_view':world.view_settings.view_transform,'look':master.view_settings.look,'world_look':world.view_settings.look,'strips':[{'name':x.name,'start':x.frame_start,'final_start':x.frame_final_start,'final_end':x.frame_final_end} for x in master.sequence_editor.strips]}
(O/'title_clock_inspection.json').write_text(json.dumps(d,indent=2))
print(json.dumps(d,indent=2),flush=True)
