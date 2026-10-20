import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(P/'reference/PREFERRED_v033.blend'),load_ui=False,use_scripts=False);r=bpy.data.objects['LOCO_BOY | RIG'];out={'bones':{},'meshes':{}}
for s in ['near','far']:
    for kind in ['upper_arm','forearm','hand']:
        n=kind+'_'+s;b=r.data.bones[n];pb=r.pose.bones[n];out['bones'][n]={'head':list(b.head_local),'tail':list(b.tail_local),'matrix':[list(v) for v in b.matrix_local],'length':b.length,'parent':b.parent.name if b.parent else None,'connected':b.use_connect,'constraints':[{'type':c.type,'name':c.name,'target':c.target.name if hasattr(c,'target') and c.target else None,'pole_target':c.pole_target.name if c.type=='IK' and c.pole_target else None,'pole_angle':c.pole_angle if c.type=='IK' else None,'chain_count':c.chain_count if c.type=='IK' else None,'use_stretch':c.use_stretch if c.type=='IK' else None} for c in pb.constraints]}
    for part in ['drawn sleeve','drawn skin','drawn source gray cuff','articulated drawn hand']:
        o=bpy.data.objects['V007_BOY | '+part+' '+s];out['meshes'][o.name]={'matrix_relative_rig':[list(v) for v in r.matrix_world.inverted()@o.matrix_world],'location':list(o.location),'materials':[m.name for m in o.data.materials],'bone_groups':[g.name for g in o.vertex_groups]}
(P/'evidence/ARM_BINDING_INSPECTION.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2),flush=True)
