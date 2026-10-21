import bpy,json
from pathlib import Path
root=Path(r'WTSC_LOCAL_WORKSPACE')
assert bpy.data.filepath.endswith('WTSC_World_First_v006.blend'),bpy.data.filepath
world=bpy.data.scenes['WTSC_WORLD_FIRST_4K'];bpy.context.window.scene=world
assert not bpy.data.collections.get('20 | LIVING WORLD dimensional sets')
keep={'Painted sky | warm left to cold right','Painted distant wooded hills','Far ruined street dissolves into ash'}
for obj in world.objects:
    if obj.type=='MESH' and obj.name not in keep and not obj.name.startswith('Title broken base'):
        obj.hide_render=True;obj.hide_viewport=True
        obj['living_world_status']='Preserved concept guide; replaced by dimensional set geometry'
parent=bpy.data.collections.new('20 | LIVING WORLD dimensional sets');world.collection.children.link(parent)
for region in ['Terrain','Village','Departure','Woods','School','Camp','Battlefield','Ash','Atmosphere']:
    col=bpy.data.collections.new('LW | '+region);parent.children.link(col)
world['production_stage']='DIMENSIONAL WORLD REBUILD: original set meshes, painted surfaces, animated environmental detail'
world['character_scope']='Held GP silhouette preserved while the dimensional world is developed; real 3D gait reference remains the next character method.'
world.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'shots/world/WTSC_Living_World_PREBUILD_v008.blend'))
print(json.dumps({'saved':bpy.data.filepath,'preserved':'v006 source and all concept objects retained','target_scene':world.name}))
