import bpy,sys,json,math
from pathlib import Path
from mathutils import Matrix,Vector
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import motion_model as M;import rig_pose_api as api
F=P/'native/WTSC_Continuous_Coat_Walk_v024.blend';bpy.ops.wm.open_mainfile(filepath=str(F),load_ui=False,use_scripts=False);S=bpy.context.scene;r,c=api.initialize_from_scene();rig=r['BOY'];rest=rig.data.bones;DATA=json.loads((P/'reference/fbx_source_inspection.json').read_text());SRC={d['frame']:d for d in DATA['samples']}
for i in range(373):
 q=i/4;f=1+q;S.frame_set(int(f),subframe=f-int(f));B=SRC[round(2+(9.75+q-2)%31,6)]['bones'];targets=[];saved=[]
 for side in ['near','far']:
  for key in ['WRIST_','ARM_POLE_']:
   ob=c['BOY',key+side];targets.append(ob)
   if ob.animation_data and ob.animation_data.action:saved.append((ob,ob.animation_data.action,ob.animation_data.action_slot));ob.animation_data.action=None
 bpy.context.view_layer.update()
 for side,ss in [('near','R'),('far','L')]:
  sh=rig.pose.bones['upper_arm_'+side].head;suvec=Vector((-(B['Elbow_'+ss]['head'][1]-B['Shoulder_'+ss]['head'][1]),0,B['Elbow_'+ss]['head'][2]-B['Shoulder_'+ss]['head'][2]));su=math.atan2(suvec.x,-suvec.z);leg_u=M.evaluate(q-1)['angles'][side][0];mean={'near':.1142809274577463,'far':.2344164084896745}[side];ua=-.60*(leg_u-mean)+.20*(su+.15);va=ua+.32+.06*math.sin(2*math.pi*(q-(0 if side=='near' else 16))/31);u=Vector((math.sin(ua),0,-math.cos(ua)));v=Vector((math.sin(va),0,-math.cos(va)));E=sh+u*rest['upper_arm_'+side].length;W=E+v*rest['forearm_'+side].length;hd=Vector((math.sin(va+.08),0,-math.cos(va+.08)));ang=math.atan2(hd.z,hd.x);hb=rest['hand_'+side];dd=hb.tail_local-hb.head_local;rot=math.atan2(math.cos(ang),math.sin(ang))-math.atan2(dd.x,dd.z);api.target('BOY','WRIST_'+side,Matrix.Translation(W)@Matrix.Rotation(rot,4,'Y')@hb.matrix_local.to_3x3().to_4x4());api.target('BOY','ARM_POLE_'+side,Matrix.Translation(E+(E-(sh+W)/2)*4))
 for ob,action,slot in saved:ob.animation_data.action=action;ob.animation_data.action_slot=slot
 for ob in targets:
  for path in ['location','rotation_quaternion','scale']:ob.keyframe_insert(path,frame=f)
for ob in targets:
 for layer in ob.animation_data.action.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for fc in bag.fcurves:
     for key in fc.keyframe_points:key.interpolation='LINEAR'
S['V024_loading']='Rdown15.3mm/2.25frames; Ldown11.6mm/2.25frames; upper-body settling lag1frame. Provisional visual study.';S['V024_arm_swing']='Centred against each leg mean with1frame lag; variable elbow flexion; no drawing-plane flip.'
S.frame_set(19,subframe=.25);bpy.ops.wm.save_as_mainfile(filepath=str(F),compress=True);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=240;S.render.resolution_y=360
for f in range(1,33):S.frame_set(f);S.render.filepath=str(P/f'previews/proof/{f:04d}.png');bpy.ops.render.render(write_still=True)
print('V024_CENTRED_COUNTER_SWING_READY')

