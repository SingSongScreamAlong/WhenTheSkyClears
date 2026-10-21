"""Explicit final-art pose interface. Native targets/IK work after this call.
Coordinates are rig-local metres in XZ; +X travel; camera from -Y.
No frame handler, proxy retarget or old POSE_### clock is involved.
Run initialize_from_scene() after opening the saved editable native.
"""
import bpy,math,json
from mathutils import Matrix,Vector
RIGS={};CONTROLS={};FEET={}
def initialize(rigs,controls,feet):
    global RIGS,CONTROLS,FEET
    RIGS=rigs;CONTROLS=controls;FEET=feet
    for w,r in rigs.items():r['v016_foot_recipe']=json.dumps({s:feet[w+'_'+s] for s in ['near','far']})
def initialize_from_scene():
    rigs={o['character']:o for o in bpy.context.scene.objects if o.type=='ARMATURE' and o.get('rig_revision')=='v016 painted linkage audit'}
    controls={(o.parent['character'] if o.parent and o.parent.type=='ARMATURE' else o.name.split(' | ')[0],o['v016_control']):o for o in bpy.context.scene.objects if o.get('v016_control')}
    feet={w+'_'+side:d for w,r in rigs.items() for side,d in json.loads(r['v016_foot_recipe']).items()}
    initialize(rigs,controls,feet);return rigs,controls
def target(w,name,M):
    o=CONTROLS[w,name];bpy.context.view_layer.update();o.matrix_world=RIGS[w].matrix_world@M;bpy.context.view_layer.update();return o
def set_world_foot_matrix(w,side,world_matrix):
    """Maintain a fixed world-space foot-bone goal while WORLD_TRAVEL moves.
    Does not move hips or silently stretch a leg. Check reach after placement.
    """
    ob=CONTROLS[w,'ANKLE_'+side];ob.matrix_world=world_matrix.copy();bpy.context.view_layer.update();return ob
def reach_report(tolerance=.0001):
    """Eight chains total: four legs and four arms. No silent validity claim."""
    bpy.context.view_layer.update();rows=[]
    for who,rig in RIGS.items():
        for side in ['near','far']:
            for upper,lower,ctrl in [('thigh','shin','ANKLE_'),('upper_arm','forearm','WRIST_')]:
                b=rig.pose.bones[lower+'_'+side];root=b.parent.head;goal=rig.matrix_world.inverted()@CONTROLS[who,ctrl+side].matrix_world.translation
                l1=rig.data.bones[upper+'_'+side].length;l2=rig.data.bones[lower+'_'+side].length;D=(goal-root).length;error=(goal-b.tail).length
                rows.append({'who':who,'chain':lower+'_'+side,'distance_m':D,'min_reach_m':abs(l1-l2),'max_reach_m':l1+l2,'endpoint_error_m':error,'reachable':abs(l1-l2)-tolerance<=D<=l1+l2+tolerance and error<=tolerance})
    return rows
def require_reachable(tolerance=.0001):
    rows=reach_report(tolerance);bad=[r for r in rows if not r['reachable']]
    if bad:raise ValueError('Native pose exceeds fixed-length rig reach: '+repr(bad))
    return rows
def set_foot(w,side,x,roll=0,lift=0):
    """Rigid original painted boot: source sole-aware heel/flat/toe roll.
    x is flat ankle X. roll in degrees. lift is actual sole clearance.
    We reuse the existing foot solver and report true hull contact.
    """
    r=RIGS[w];b=r.data.bones['foot_'+side];data=FEET[w+'_'+side];A=b.head_local
    theta=data['flatten_angle'];p=math.radians(roll);pv=data['toe'] if p>=0 else data['heel'];v=Vector((pv[0]-A.x,0,pv[1]-A.z))
    rot=Matrix.Rotation(theta+p,4,'Y');flat=Matrix.Rotation(theta,4,'Y')
    hull=[rot@(Vector(v)-A) for v in data.get('actual_native_vertices',[(a,0,c) for a,c in data['lower_hull']])]
    ankle=Vector((x+(flat@v).x-(rot@v).x,0,-min(q.z for q in hull)+lift))
    M=Matrix.Translation(ankle)@rot@Matrix.Translation(-A)@b.matrix_local
    ob=target(w,'ANKLE_'+side,M);ob['flat_ankle_x']=x;ob['sole_lift_m']=lift;ob['roll_degrees']=roll
    ob['contact_mode']='SOLE_FIT '+('toe' if roll>0 else 'heel' if roll<0 else 'flat')
    return M
def set_wrist(w,side,x,z,angle=-90,shape='Relax',fit_reach=False):
    b=RIGS[w].data.bones['hand_'+side];d=b.tail_local-b.head_local
    desired=Vector((math.cos(math.radians(angle)),0,math.sin(math.radians(angle))))
    a=math.atan2(desired.x,desired.z)-math.atan2(d.x,d.z)
    r=RIGS[w];S=r.pose.bones['upper_arm_'+side].head;W=Vector((x,0,z));D=W-S
    l1=r.data.bones['upper_arm_'+side].length;l2=r.data.bones['forearm_'+side].length
    allowed=min(max(D.length,abs(l1-l2)+.003),l1+l2-.003)
    request=list(W)
    if abs(allowed-D.length)>.00001:
        if not fit_reach:raise ValueError((w,side,'wrist outside fixed-length arm range',D.length,abs(l1-l2)+.003,l1+l2-.003))
        W=S+D.normalized()*allowed
    M=Matrix.Translation(W)@Matrix.Rotation(a,4,'Y')@b.matrix_local.to_3x3().to_4x4()
    ob=CONTROLS[w,'WRIST_'+side]
    if 'TorsoFollow' in ob:ob['TorsoFollow']=0.;ob.update_tag();bpy.context.view_layer.update()
    if 'BraceFollow' in ob:ob['BraceFollow']=0.;ob.update_tag();bpy.context.view_layer.update()
    ob=target(w,'WRIST_'+side,M);ob['Reach']=float(shape=='Reach');ob['Brace']=float(shape=='Brace');ob.update_tag()
    ob['requested_position']=request;ob['reach_fit_adjustment_m']=(W-Vector(request)).length
    return M
def apply_pose(w,spec):
    r=RIGS[w];H=Vector((spec.get('hip',(0,.55))[0],0,spec.get('hip',(0,.55))[1]));rest=r.data.bones
    pel=rest['pelvis'].matrix_local;hipM=Matrix.Translation(H)@Matrix.Rotation(math.radians(spec.get('pelvis',0)),4,'Y')@Matrix.Translation(-pel.translation)@pel
    target(w,'HIP',hipM)
    chest=rest['chest'].matrix_local;cd=Matrix.Translation(H)@Matrix.Rotation(math.radians(spec.get('chest',0)),4,'Y')@Matrix.Translation(-pel.translation)
    target(w,'CHEST',cd@chest)
    hr=rest['head'].matrix_local;h0=cd@hr;ha=math.radians(spec.get('head',0)-spec.get('chest',0))
    target(w,'HEAD_PROFILE',Matrix.Translation(h0.translation)@Matrix.Rotation(ha,4,'Y')@Matrix.Translation(-h0.translation)@h0)
    for side in ['near','far']:
        ft=spec.get(side+'_foot',(-.10 if side=='near' else .13,0,0));set_foot(w,side,*ft)
        foot=CONTROLS[w,'ANKLE_'+side].matrix_local.translation
        polex=H.x+spec.get('knee_pole_'+side,1)*1.0
        target(w,'LEG_POLE_'+side,Matrix.Translation((polex,0,(H.z+foot.z)*.5)))
    bpy.context.view_layer.update()
    for side in ['near','far']:
        hb=rest['hand_'+side];hw=cd@hb.head_local;hv=cd.to_3x3()@(hb.tail_local-hb.head_local)
        default=(hw.x,hw.z,math.degrees(math.atan2(hv.z,hv.x)),'Relax')
        hand=spec.get(side+'_hand',default)
        set_wrist(w,side,*hand,fit_reach=True)
        if side+'_hand' not in spec:CONTROLS[w,'WRIST_'+side]['TorsoFollow']=1.;CONTROLS[w,'WRIST_'+side].update_tag();bpy.context.view_layer.update()
        shoulder=r.pose.bones['upper_arm_'+side].head
        pole=spec.get('elbow_pole_'+side,-1)
        target(w,'ARM_POLE_'+side,Matrix.Translation((shoulder.x+pole*.25,0,shoulder.z-.8)))
    bpy.context.view_layer.update()
    choose_planes(w,spec)
def choose_planes(w,spec):
    # Source bone rolls differ. Select the in-plane branch against an authored
    # pole, rather than assuming the same pole_angle suits both children.
    r=RIGS[w]
    for side in ['near','far']:
        for chain,prefix in [('shin','LEG_'),('forearm','ARM_')]:
            b=r.pose.bones[chain+'_'+side];ik=next(c for c in b.constraints if c.type=='IK')
            pole=r.matrix_world.inverted()@CONTROLS[w,prefix+'POLE_'+side].matrix_world.translation
            opts=[]
            for angle in [0,math.pi]:
                ik.pole_angle=angle;bpy.context.view_layer.update();opts.append(((b.head-pole).length,angle))
            ik.pole_angle=min(opts)[1];bpy.context.view_layer.update()
def key_controls(frame):
    for o in CONTROLS.values():
        o.rotation_mode='QUATERNION'
        for field in ['location','rotation_quaternion','scale']:o.keyframe_insert(field,frame=frame)
        for key in ['Reach','Brace','BraceFollow','TorsoFollow','FrontLayer']:
            if key in o:o.keyframe_insert(data_path='["'+key+'"]',frame=frame)
    for r in RIGS.values():
        for b in r.pose.bones:
            for c in b.constraints:
                if c.type=='IK':c.keyframe_insert('pole_angle',frame=frame)
def constant_keys():
    for o in [*CONTROLS.values(),*RIGS.values()]:
        if not o.animation_data or not o.animation_data.action:continue
        a=o.animation_data.action;a.name='V016_DIAGNOSTIC | '+o.name
        for layer in a.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for k in fc.keyframe_points:k.interpolation='CONSTANT'
