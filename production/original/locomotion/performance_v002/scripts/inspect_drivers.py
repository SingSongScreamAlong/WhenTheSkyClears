import bpy,json,runpy
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene
with bpy.data.libraries.load(str(P/'native/WTSC_Performance_Library_v002.blend'),link=False) as (a,b):b.collections=['WTSC_PERFORMANCE_PAIR_v002']
s.collection.children.link(b.collections[0]);root=next(o for o in s.objects if o.get('loco_pack')=='WTSC_PERFORMANCE_v002')
runpy.run_path(str(P/'scripts/configure_performance.py'))['configure']('PLAYFUL_SKIP',repeat=1,root_motion=True)
rows=[]
for frame in [1,2,3,1]:
    s.frame_set(frame);bpy.context.view_layer.update()
    for o in s.objects:
        if o.type=='ARMATURE' or 'TRAVEL' in o.name:
            row={'f':frame,'name':o.name,'location':list(o.location),'world':list(o.matrix_world.translation),'root_props':dict(root.items()),'drivers':[]}
            if o.animation_data:
                for fc in o.animation_data.drivers:row['drivers'].append({'expression':fc.driver.expression,'valid':fc.driver.is_valid,'variables':[{'name':v.name,'target':v.targets[0].id.name if v.targets[0].id else None,'same':v.targets[0].id==root,'path':v.targets[0].data_path,'value':str(v.targets[0].id.get('pair_gap_m')) if v.targets[0].id else None} for v in fc.driver.variables]})
            rows.append(row)
(P/'evidence/driver_inspection.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
