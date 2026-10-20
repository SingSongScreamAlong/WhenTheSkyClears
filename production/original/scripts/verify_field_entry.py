import bpy,json
from bpy_extras.object_utils import world_to_camera_view
from pathlib import Path
root=Path(r'WTSC_LOCAL_WORKSPACE')
world=bpy.data.scenes['WTSC_WORLD_FIRST_4K'];bpy.context.window.scene=world
objects=[o for o in world.objects if o.type=='MESH' and o.data.materials and any(m.surface_render_method=='BLENDED' for m in o.data.materials if m)]
entries={}
for obj in objects:
    if 'Battlefield' not in obj.name and 'Far ruined' not in obj.name:continue
    for frame in range(1,1201):
        world.frame_set(frame)
        points=[world_to_camera_view(world,world.camera,obj.matrix_world@v.co) for v in obj.data.vertices]
        xs=[p.x for p in points];ys=[p.y for p in points]
        if max(xs)>=0 and min(xs)<=1 and max(ys)>=0 and min(ys)<=1:
            entries[obj.name]={'first_possible_frame':frame,'seconds':(frame-1)/24};break
world.frame_set(1)
assert len(entries)==2 and all(e['first_possible_frame']>1080 for e in entries.values()),entries
(root/'notes/world_field_entry.json').write_text(json.dumps(entries,indent=2))
print(json.dumps(entries))
