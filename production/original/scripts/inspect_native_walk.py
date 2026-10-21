import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(r'WTSC_LOCAL_WORKSPACE')
rig=bpy.data.objects['Girl_Walk_Rig'];scene=bpy.data.scenes['01_GIRL_WALK_CLEAN']
bpy.context.window.scene=scene
samples=json.loads((ROOT/'notes/walk_contact_samples.json').read_text())
errors=[];evaluated=[]
for rec in samples:
    scene.frame_set(rec['frame']);bpy.context.view_layer.update()
    row={'frame':rec['frame'],'feet':{}}
    for side in ['near','far']:
        p=rig.matrix_world@rig.pose.bones['shoe_'+side].head
        expected=rec['feet'][side]
        error=max(abs(p.x-expected['world_x']),abs(p.y-expected['ankle_y']))
        errors.append(error)
        row['feet'][side]={'x':p.x,'y':p.y,'stance':expected['stance']}
    evaluated.append(row)
max_drift=0
for previous,current in zip(evaluated,evaluated[1:]):
    for side in ['near','far']:
        a=previous['feet'][side];b=current['feet'][side]
        if a['stance'] and b['stance']:
            max_drift=max(max_drift,abs(a['x']-b['x']))
native_parts=[o for o in scene.objects if o.type=='GREASEPENCIL']
report={'blender':bpy.app.version_string,'filepath':bpy.data.filepath,
  'scenes':{s.name:{'frames':[s.frame_start,s.frame_end],'fps':s.render.fps,
    'resolution':[s.render.resolution_x,s.render.resolution_y],'percentage':s.render.resolution_percentage} for s in bpy.data.scenes},
  'native_grease_pencil_objects':len(native_parts),
  'native_drawing_layers':sum(len(o.data.layers) for o in native_parts),
  'native_bones':len(rig.data.bones),'max_foot_target_error_m':max(errors),
  'max_planted_ankle_frame_drift_m':max_drift,
  'source_images':[{ 'name':im.name,'packed':bool(im.packed_file),'size':list(im.size)} for im in bpy.data.images if im.name.startswith('Girl_')],
  'motion_status':'Authored kinematic walk, visual quality unapproved',
  'guide_in_clean_scene':any(o.name.startswith('Guide ') for o in scene.objects),
  'master_sound_frames':[s.frame_final_duration for s in bpy.data.scenes['00_TRAILER_MASTER_4K_100s'].sequence_editor.strips if s.type=='SOUND'],
  'evaluated_feet':evaluated}
assert max(errors)<1e-4,report
assert max_drift<1e-4,report
assert not report['guide_in_clean_scene']
assert report['master_sound_frames']==[2400]
scene.frame_set(1)
(ROOT/'notes/native_reopen_verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='evaluated_feet'}))
