import bpy,math
from pathlib import Path
ROOT=Path(r'WTSC_LOCAL_WORKSPACE')
scene=bpy.context.scene
C=scene.collection.children
scene.use_nodes=True;nt=bpy.data.node_groups.new('WTSC final picture fade','CompositorNodeTree');scene.compositing_node_group=nt
nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
rl=nt.nodes.new('CompositorNodeRLayers');comp=nt.nodes.new('NodeGroupOutput')
fade=nt.nodes.new('CompositorNodeExposure');nt.links.new(rl.outputs['Image'],fade.inputs['Image']);nt.links.new(fade.outputs['Image'],comp.inputs['Image'])
fade.inputs['Exposure'].default_value=0;fade.inputs['Exposure'].keyframe_insert('default_value',frame=1)
for f in range(2353,2402):
    fade.inputs['Exposure'].default_value=math.log2(max(2**-24,(2400-f)/47));fade.inputs['Exposure'].keyframe_insert('default_value',frame=f)
for label,seconds in [('VILLAGE',0),('VILLAGE EMPTIES / WOODS',18),('WOODS',28),('SCHOOL',39),('CAMP',47),('BATTLEFIELD / CRATER',54),('RUINS AND ASH',67),('TITLE TERRAIN',80),('AUDIO FADE',90),('CAMERA HOLD',96),('PICTURE FADE',98),('100 SECOND END boundary',100)]:scene.timeline_markers.new(label,frame=int(seconds*24)+1)

note=bpy.data.texts.new('READ ME | WORLD FIRST')
note.write('When the Sky Clears — WORLD FIRST\n\n3840 x 2160 UHD, 24 fps, frames 1–2400 = 100 seconds.\n\nThis pass reviews the continuous world, atmosphere, palette, region changes and title scale.\nThe children are one held editable Grease Pencil vector drawing, translated intact through the route. There is no limb, bone, walk or facial animation in this file.\n\nDistinct sets: village (intact and abandoned), woods at two depths, school, camp, battlefield/crater, ruins/ash, physical title terrain.\nPaint layers are genuine built-in GPT imagegen outputs, packed and copied into sets/painted_layers. Native source rasters are 1672 x 941 approximately; the render master is native UHD.\n\nMusic is the user-supplied 100-second WAV, referenced relatively. Its fade starts at 90 seconds. Picture fades during the final two seconds.\n\nThe earlier segmented mannequin motion was rejected. When animation resumes, align a verified animated 3D source behind the vector silhouette and adapt its gait. Do not reuse the rejected procedural gait.\n\nThis is a provisional world and mood pass, not a finished trailer or approved art package.\n')
scene.frame_set(1)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
scene.render.filepath='//../../renders/world/frames_4k/frame_'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'shots/world/WTSC_World_First_v001.blend'))
print('WORLD_FIRST_SAVED',len(scene.objects),'objects,',len(C),'depth/set collections,100seconds,3840x2160')
