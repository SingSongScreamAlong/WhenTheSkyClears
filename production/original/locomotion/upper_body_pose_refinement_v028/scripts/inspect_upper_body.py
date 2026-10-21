import bpy,json,math
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'reference/PRESERVED_BASELINE_v027.blend'),load_ui=False,use_scripts=False)
S=bpy.context.scene;rig=bpy.data.objects['LOCO_BOY | RIG'];rows=[]
for name in ['BOY | HEAD_PROFILE','PERF_BOY | original head']:
    o=bpy.data.objects[name];print('HEAD_LINKAGE',name,'parent',o.parent.name if o.parent else None,'parent_type',o.parent_type,'parent_bone',o.parent_bone,'constraints',[(c.type,c.name,getattr(c,'subtarget',None),getattr(getattr(c,'target',None),'name',None)) for c in o.constraints],'modifiers',[(m.type,m.name,getattr(getattr(m,'object',None),'name',None)) for m in o.modifiers],flush=True)
print('HEAD_BONE_CONSTRAINTS',[(c.type,c.name,getattr(c,'subtarget',None),getattr(getattr(c,'target',None),'name',None)) for c in rig.pose.bones['head'].constraints],flush=True)
for i in range(125):
    f=1+i/4;S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();row={'frame':f,'arms':{}}
    for s in ['near','far']:
        b={n:rig.pose.bones[n+'_'+s] for n in ['upper_arm','forearm','hand']}
        row['arms'][s]={n:{'head':list(v.head),'tail':list(v.tail),'angle_degrees_from_down':math.degrees(math.atan2(v.tail.x-v.head.x,-(v.tail.z-v.head.z)))} for n,v in b.items()}
    row['chest_head']=list(rig.pose.bones['chest'].head);row['chest_tail']=list(rig.pose.bones['chest'].tail);row['hip']=list(rig.pose.bones['pelvis'].head);rows.append(row)
result={'version':bpy.app.version_string,'rest_lengths':{n:rig.data.bones[n].length for n in ['upper_arm_near','forearm_near','hand_near','upper_arm_far','forearm_far','hand_far']},'rows':rows}
(P/'evidence/V027_UPPER_BODY_SOURCE.json').write_text(json.dumps(result,indent=2))
print('SOURCE_ARM_SAMPLES',json.dumps([{'frame':r['frame'],'arms':{s:[round(r['arms'][s][n]['angle_degrees_from_down'],2) for n in ['upper_arm','forearm','hand']] for s in ['near','far']}} for r in rows if r['frame'] in [1,4,6,9,11,13,17,20,22,25,27,29,32]]),flush=True)
