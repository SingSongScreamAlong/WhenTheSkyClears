import bpy
from pathlib import Path
ROOT=Path(r'WTSC_LOCAL_WORKSPACE')
for camera in ['Clean side camera','Comparison side camera']:
    obj=bpy.data.objects[camera]
    for layer in obj.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:key.interpolation='LINEAR'
clean=bpy.data.scenes['01_GIRL_WALK_CLEAN']
compare=bpy.data.scenes['02_GUIDE_COMPARISON']
clean.render.filepath='//../renders/girl_walk_clean_4k_v002/frame_'
compare.render.filepath='//../renders/girl_walk_comparison_4k_v002/frame_'
for s in bpy.data.scenes:s.frame_set(1)
bpy.context.window.scene=clean
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'shots/WTSC_Girl_Walk_Proof_v002.blend'))
print('Saved v002: linear lateral cameras and verified reference Action Slot')
