import bpy,json
from pathlib import Path
scene=bpy.context.scene
arm=bpy.data.objects['Armature']
action=arm.animation_data.action
out={'scene_fps':scene.render.fps,'action':action.name,'range':list(action.frame_range),
     'location':list(arm.location),'scale':list(arm.scale),'rotation':list(arm.rotation_euler),
     'bone_names':[b.name for b in arm.data.bones],'samples':[]}
for frame in [action.frame_range[0],(action.frame_range[0]+action.frame_range[1])/2,action.frame_range[1]]:
    scene.frame_set(int(frame),subframe=frame-int(frame));bpy.context.view_layer.update()
    poses={b.name:[round(float(v),5) for v in arm.matrix_world@b.head] for b in arm.pose.bones if any(s in b.name.lower() for s in ['root','hip','pelvis','thigh','calf','foot','toe','head','upperarm','lowerarm','hand','neck','spine'])}
    out['samples'].append({'frame':frame,'bones':poses})
Path(r'WTSC_LOCAL_WORKSPACE\notes\synty_reference_inspection.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))
