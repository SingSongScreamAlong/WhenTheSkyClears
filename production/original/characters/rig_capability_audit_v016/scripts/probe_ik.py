import bpy,math,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(P/'native/WTSC_Painted_Rig_Capability_v016.blend'),load_ui=False,use_scripts=False)
S=bpy.context.scene;out=[]
for f in [1,21,161]:
 S.frame_set(f)
 for r in [o for o in S.objects if o.type=='ARMATURE']:
  for side in ['near','far']:
   for chain in ['shin','forearm']:
    b=r.pose.bones[chain+'_'+side];ik=next(c for c in b.constraints if c.type=='IK')
    for seed in [0.05,-0.05]:
     b.rotation_mode='XYZ';b.rotation_euler.z=seed
     for angle in [0,math.pi]:
      ik.pole_angle=angle;bpy.context.view_layer.update()
      goal=r.matrix_world.inverted()@ik.target.matrix_world.translation
      out.append({'seed':seed,'frame':f,'who':r['character'],'chain':b.name,'angle':angle,'error':(b.tail-goal).length,'joint_y':b.head.y,'parent_y':b.parent.head.y,'parent':list(b.parent.head),'joint':list(b.head),'tail':list(b.tail),'target':list(goal),'iklocks':[b.lock_ik_x,b.lock_ik_y,b.lock_ik_z], 'limits':[b.use_ik_limit_x,b.use_ik_limit_y,b.use_ik_limit_z], 'basis':[list(x) for x in b.matrix_basis], 'parent_basis':[list(x) for x in b.parent.matrix_basis], 'scales':list(b.scale), 'constraint':{'use_tail':ik.use_tail,'use_rotation':ik.use_rotation,'iterations':ik.iterations,'ik_type':ik.ik_type},'rest_head':list(b.bone.head_local),'rest_parent_tail':list(b.parent.bone.tail_local)})
(P/'evidence/ik_plane_probe.json').write_text(json.dumps(out,indent=2))
print('PROBE_COMPLETE')
