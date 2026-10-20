"""Capability board only, deliberately no performance or walk cycle."""
import bpy,json,math,copy
from pathlib import Path
import rig_pose_api as api
TESTS=[
 ('01_NEUTRAL','Neutral source identity',{}),
 ('02_SQUAT','Planted squat / fixed sole targets',{'hip':(.02,.43),'chest':10,'head':-4}),
 ('03_OFF_CACHE','New off-cache intermediate / opposed torso-head',{'hip':(.035,.472),'pelvis':-4,'chest':18,'head':-9,'near_hand':(.285,.735,-25,'Reach')}),
 ('04_REACH','Deep elbow and shoulder / reaching hand',{'hip':(0,.54),'chest':-8,'head':6,'near_hand':(.37,.94,12,'Reach'),'far_hand':(-.17,.76,-30,'Relax')}),
 ('05_HEEL','Painted boot heel contact',{'near_foot':(-.1,-12,0),'near_hand':(.13,.62,-85,'Relax')}),
 ('06_FLAT','Painted boot flat contact',{}),
 ('07_TOE','Painted boot toe roll',{'near_foot':(-.1,30,0),'hip':(.05,.52)}),
 ('08_LIFT','Painted boot lift / reverse roll range',{'near_foot':(-.1,12,.055),'hip':(.04,.50)}),
 ('09_BRACE','Actual painted palm / thigh contact',{'hip':(.015,.435),'chest':50,'head':7}),
 ('10_ATTENTION','Supported profile attention tilt; yaw UNSOLVED',{'hip':(.005,.53),'chest':-9,'head':-15,'near_hand':(-.19,.72,170,'Reach')}),
 ('11_CROSSING','Near/far painted limb crossing and braid attachment',{'hip':(.0,.465),'chest':12,'head':-12,'near_hand':(-.15,.89,155,'Reach'),'far_hand':(.20,.77,-15,'Relax')}),
 ('12_CLEARANCE','Pair clearance / offer is a cue, not a grasp',{'hip':(0,.52),'chest':8,'head':-8})
]
def neutral(w):
    # Different original limb lengths and shoulder heights are retained.
    return {'hip':(0,.60323),'pelvis':0,'chest':0,'head':0,
      'near_foot':(.13,0,0),'far_foot':(-.10,0,0)}
def brace(w):
    from mathutils import Vector,Matrix
    r=api.RIGS[w];b=r.pose.bones['thigh_near'];dg=bpy.context.evaluated_depsgraph_get()
    leg=next(o for o in r.children if o.get('v007_role')=='drawn_leg' and o.name.endswith('near'))
    hand=next(o for o in r.children if o.get('v007_role')=='drawn_hand' and o.name.endswith('near'))
    ev=leg.evaluated_get(dg);pts=[r.matrix_world.inverted()@ev.matrix_world@v.co for v in ev.data.vertices]
    station=8;t=((pts[20]+pts[21])-(pts[12]+pts[13])).normalized();t.y=0;t.normalize();n=Vector((-t.z,0,t.x));surface=pts[station*2+1].copy();surface.y=0
    W=surface+n*.021-t*.019;angle=math.degrees(math.atan2(t.z,t.x))
    for _ in range(3):
        api.set_wrist(w,'near',W.x,W.z,angle,'Brace',fit_reach=False);api.choose_planes(w,{})
        bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();he=hand.evaluated_get(dg)
        palm=[r.matrix_world.inverted()@he.matrix_world@v.co for v in he.data.vertices[:8]]
        gap=min((p-surface).dot(n) for p in palm);W+=n*(.0005-gap)
    # A native thigh parent preserves this calibrated projected palm contact
    # when hips are edited. No Python handler is needed after authoring.
    wrist=api.CONTROLS[w,'WRIST_near'];collection=wrist.users_collection[0]
    # The painted contour projects joints into XZ. Copying the complete3D bone
    # frame drifted during combined hip edits, so use the same planar tangent
    # and normal algebra for the contact target itself.
    anchors=[]
    for name,tail in [('H',0.),('K',1.)]:
        ob=bpy.data.objects.new(w+' | BRACE_THIGH_'+name,None);collection.objects.link(ob);ob.empty_display_size=.012
        c=ob.constraints.new('COPY_LOCATION');c.target=r;c.subtarget='thigh_near';c.head_tail=tail;anchors.append(ob)
    bpy.context.view_layer.update()
    anchor=bpy.data.objects.new(w+' | PAINTED_PALM_BRACE_ANCHOR',None);collection.objects.link(anchor);anchor.empty_display_size=.02
    mid=(b.head+b.tail)*.5;ww=r.matrix_world.inverted()@wrist.matrix_world.translation;along=(ww-mid).dot(t);outside=(ww-mid).dot(n)
    def driver(path,index,expression):
        fc=anchor.driver_add(path,index);d=fc.driver
        for key,ob,axis in [('hx',anchors[0],'LOC_X'),('hz',anchors[0],'LOC_Z'),('kx',anchors[1],'LOC_X'),('kz',anchors[1],'LOC_Z'),('hy',anchors[0],'LOC_Y'),('ky',anchors[1],'LOC_Y')]:
            v=d.variables.new();v.name=key;v.type='TRANSFORMS';v.targets[0].id=ob;v.targets[0].transform_type=axis;v.targets[0].transform_space='WORLD_SPACE'
        d.expression=expression
    length='sqrt((kx-hx)**2+(kz-hz)**2)'
    driver('location',0,f'(hx+kx)*0.5+((kx-hx)*({along!r})-(kz-hz)*({outside!r}))/{length}')
    driver('location',1,'(hy+ky)*0.5')
    driver('location',2,f'(hz+kz)*0.5+((kz-hz)*({along!r})+(kx-hx)*({outside!r}))/{length}')
    anchor.rotation_mode='XYZ';sign=r.data.bones['hand_near'].matrix_local.col[2].y
    anchor.rotation_euler.x=math.pi/2 if sign<0 else -math.pi/2
    driver('rotation_euler',1,'atan2(kx-hx,kz-hz)' if sign<0 else 'atan2(hx-kx,hz-kz)')
    follow=wrist.constraints.new('COPY_TRANSFORMS');follow.name='V016 calibrated painted thigh brace';follow.target=anchor
    wrist['BraceFollow']=1.;fc=follow.driver_add('influence');v=fc.driver.variables.new();v.name='follow';v.targets[0].id=wrist;v.targets[0].data_path='["BraceFollow"]';fc.driver.expression='follow'
    wrist['brace_scope']='Projected palm edge to actual native thigh contour; calibrated0.5mm gap; native planar thigh-follow. Validate before other poses.'
    wrist.update_tag();bpy.context.view_layer.update()
def author(rigs,controls):
    records=[]
    for i,(name,label,delta) in enumerate(TESTS):
        f=i*20+1
        bpy.context.scene.frame_set(f)
        # Pose edits are made without the previous diagnostic Actions fighting
        # them during dependency-graph updates. Restore Actions before keying.
        saved=[]
        for ob in [*controls.values(),*rigs.values()]:
            ad=ob.animation_data
            if ad and ad.action:
                saved.append((ob,ad.action,ad.action_slot));ad.action=None
        for w,rig in rigs.items():
            gap=.8 if name=='12_CLEARANCE' else 1.24
            rig.location=(-gap*.5 if w=='BOY' else gap*.5,0,0)
            spec=neutral(w);spec.update(copy.deepcopy(delta))
            # Explicit capability tests use each child's original dimensions.
            if w=='GIRL' and 'hip' in delta:spec['hip']=(delta['hip'][0],delta['hip'][1]-.02)
            if name=='04_REACH' and w=='GIRL':spec['near_hand']=(.31,.84,8,'Reach')
            if name=='12_CLEARANCE':
                if w=='BOY':spec.update(chest=12,head=4,far_hand=(.37,.77,10,'Reach'))
                else:spec.update(chest=-10,head=-15,near_hand=(-.29,.76,170,'Reach'))
            api.apply_pose(w,spec)
            if name=='09_BRACE':brace(w)
            records.append({'frame':f,'test':name,'who':w,'label':label,'spec':spec,
              'actual_wrists':{s:{'position':list(rig.matrix_world.inverted()@api.CONTROLS[w,'WRIST_'+s].matrix_world.translation),'reach_fit_adjustment_m':api.CONTROLS[w,'WRIST_'+s].get('reach_fit_adjustment_m',0),'Reach':api.CONTROLS[w,'WRIST_'+s]['Reach'],'Brace':api.CONTROLS[w,'WRIST_'+s]['Brace'],'BraceFollow':api.CONTROLS[w,'WRIST_'+s]['BraceFollow']} for s in ['near','far']}})
        for ob,act,slot in saved:ob.animation_data.action=act;ob.animation_data.action_slot=slot
        for rig in rigs.values():rig.keyframe_insert('location',frame=f)
        api.key_controls(f)
        bpy.context.scene.timeline_markers.new(name,frame=f)
    api.constant_keys()
    for r in rigs.values():
        for l in r.animation_data.action.layers:
            for s in l.strips:
                for b in s.channelbags:
                    for fc in b.fcurves:
                        for k in fc.keyframe_points:k.interpolation='CONSTANT'
    p=Path(__file__).resolve().parents[1]
    (p/'evidence/diagnostic_pose_manifest.json').write_text(json.dumps(records,indent=2))
