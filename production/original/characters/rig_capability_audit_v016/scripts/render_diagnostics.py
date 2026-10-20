import bpy,json,math
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Painted_Rig_Capability_v016.blend'),load_ui=False,use_scripts=False)
S=bpy.context.scene;S.render.resolution_x=1280;S.render.resolution_y=720
report=[]
for f in range(1,222,20):
    S.frame_set(f);bpy.context.view_layer.update()
    for r in [o for o in S.objects if o.type=='ARMATURE' and o.get('character')]:
        for side in ['near','far']:
            for bone,ctrl in [('shin','ANKLE_'),('forearm','WRIST_')]:
                b=r.pose.bones[bone+'_'+side];t=bpy.data.objects[r['character']+' | '+ctrl+side]
                goal=r.matrix_world.inverted()@t.matrix_world.translation
                report.append({'frame':f,'who':r['character'],'chain':bone+'_'+side,'endpoint_error_m':(b.tail-goal).length,'joint_y_m':b.head.y,'length_m':b.length})
    S.render.filepath=str(P/f'previews/pose_{f:03d}.png');bpy.ops.render.render(write_still=True)
(P/'evidence/native_ik_initial.json').write_text(json.dumps(report,indent=2))
print('V016_DIAGNOSTIC_RENDERS_COMPLETE',len(report),'MAX_IK',max(x['endpoint_error_m'] for x in report))
