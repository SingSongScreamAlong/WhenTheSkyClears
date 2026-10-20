import bpy,json
from pathlib import Path
root=Path(r'WTSC_LOCAL_WORKSPACE')
world=bpy.data.scenes['WTSC_WORLD_FIRST_4K']
master=bpy.data.scenes['WTSC_MASTER_4K_100S']
bpy.context.window.scene=world
changed=[]
for mat in bpy.data.materials:
    if mat.use_nodes and any(n.type=='TEX_IMAGE' and n.image and n.image.name.startswith('Battlefield_v001.png') for n in mat.node_tree.nodes):
        mat.surface_render_method='BLENDED'
        changed.append(mat.name)
assert len(changed)==2,changed
world.render.resolution_percentage=100
world.render.filepath='//../../renders/world/frames_4k/frame_'
world.frame_set(1);master.frame_set(1)
world['battlefield_alpha_repair']='BLENDED transparent material on the two battlefield planes removes black DITHERED overlap artifacts. Source paintings unchanged.'
bpy.data.texts['READ ME | WORLD FIRST'].write('\nWorld source v006 corrects the two battlefield alpha materials to BLENDED after exported-frame review. The original imagegen paintings, geography, camera and held vector pair are unchanged. Review movie v006 supersedes the v004 movie.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'shots/world/WTSC_World_First_v006.blend'))
(root/'notes/battlefield_alpha_repair.json').write_text(json.dumps({'source':'shots/world/WTSC_World_First_v006.blend','changed_materials':changed,'repair':'DITHERED to BLENDED','verification_images':['renders/world/test_no_gp.png','renders/world/test_blended.png'],'source_images_unchanged':True},indent=2))
print(json.dumps({'saved':bpy.data.filepath,'changed_materials':changed}))
