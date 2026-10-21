import bpy,json
master=bpy.data.scenes['WTSC_MASTER_4K_100S']
sound=next(s for s in master.sequence_editor.strips if s.type=='SOUND')
original=bpy.context.window.scene
report={'active_scene':original.name,'packed':bool(sound.sound.packed_file),'contexts':{}}
for scene in [original,master]:
    bpy.context.window.scene=scene
    values={}
    for frame in [1,2161,2281,2401]:
        master.frame_set(frame)
        bpy.context.view_layer.update()
        values[str(frame)]=sound.volume
    report['contexts'][scene.name]=values
if master.animation_data and master.animation_data.action:
    action=master.animation_data.action
    report['action']=action.name
    report['slot']=str(master.animation_data.action_slot)
    report['curves']=[{'path':f.data_path,'keys':[[p.co.x,p.co.y,p.interpolation] for p in f.keyframe_points]} for l in action.layers for s in l.strips for b in s.channelbags for f in b.fcurves]
master.frame_set(1)
bpy.context.window.scene=original
print(json.dumps(report))
