"""Isolated native 2D performance study. Original face/body paint; clean vector overlaps.
No image edits, replacement models, add-ons, handlers, or production writes.
"""
import bpy,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.geometry import tessellate_polygon
P=Path(__file__).resolve().parents[1];R=P.parents[1]
source=R/'locomotion/first_pack_v001/native/WTSC_Locomotion_Library_v001.blend'
source_hash=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False)
S=bpy.context.scene;S.name='LOCO v002 | Skip performance study';S.frame_start=1;S.frame_end=120
SRC=json.loads((P/'art/native_overlap_sources.json').read_text());SC=SRC['scale'];BASE=SRC['base']
CTRL=next(o for o in S.objects if o.get('loco_pack'));CTRL['loco_pack']='WTSC_PERFORMANCE_v002'
CTRL['root_motion']=0.;CTRL['ground_speed_mps']=.60;CTRL['duration_frames']=120.;CTRL['pair_gap_m']=.80
TRAVEL=next(o for o in CTRL.children if 'TRAVEL' in o.name);TRAVEL['distance_offset_m']=0.
PAIR=CTRL.users_collection[0];PAIR.name='WTSC_PERFORMANCE_PAIR_v002';PAIR.asset_data.description='Current charcoal children; native planar overlap rigs, SKIP and STUMBLE_RECOVER performance studies. Inspect render before production use.'
DIST=bpy.data.objects.new('PERF | DISTANCE_CURVE',None);PAIR.objects.link(DIST);DIST.parent=CTRL;DIST.hide_render=True;DIST['loco_role']='DISTANCE_CURVE';CTRL['use_distance_curve']=0.
rigs={o['character']:o for o in S.objects if o.type=='ARMATURE' and o.get('character')}
oldactions=list(bpy.data.actions)
for rig in rigs.values():
    rig.animation_data_clear()
    for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
    for ob in list(rig.children):
        if ob.type=='MESH' and (str(ob.get('skin_region','')).startswith('rigid:') or 'arm_' in str(ob.get('skin_region','')) or ob.get('skin_region') in ['head','braid']):bpy.data.objects.remove(ob,do_unlink=True)
for a in oldactions:
    a.use_fake_user=False
    if a.users==0:bpy.data.actions.remove(a)
im=next(i for i in bpy.data.images if i.name.startswith('Pair_Painterly_Near_Age'))
paint=bpy.data.materials['LOCO | ORIGINAL v015 charcoal paint, packed']
def vpx(p,cx):return Vector(((p[0]-cx)*SC,0,(BASE-p[1])*SC))
def material(name):
    m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();t=nt.nodes.new('ShaderNodeTexImage');t.image=im
    gray=nt.nodes.new('ShaderNodeHueSaturation');gray.inputs['Saturation'].default_value=0;gray.inputs['Value'].default_value=.8;nt.links.new(t.outputs['Color'],gray.inputs['Color'])
    em=nt.nodes.new('ShaderNodeEmission');nt.links.new(gray.outputs[0],em.inputs[0]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],out.inputs[0]);return m
opaque=material('LOCO v002 | original paint sampled on native overlap geometry')
def mesh(rig,name,pts,faces,uvs,bn,mat,depth):
    me=bpy.data.meshes.new(name);me.from_pydata([(p.x,depth,p.z) for p in pts],[],faces);me.update();ob=bpy.data.objects.new(name,me);rig.users_collection[0].objects.link(ob);ob.parent=rig;me.materials.append(mat)
    uv=me.uv_layers.new(name='Original v015 paint source')
    for l in me.loops:uv.data[l.index].uv=uvs[l.vertex_index]
    g=ob.vertex_groups.new(name=bn);g.add(list(range(len(pts))),1,'REPLACE');mo=ob.modifiers.new('Native planar attachment','ARMATURE');mo.object=rig
    ob['art']='Native editable 2D overlap; original sampled paint, no bitmap repaint or 3D volume';return ob
def poly(rig,name,px,bn,cx,depth,offset=None):
    pts=[vpx(p,cx)+(offset or Vector()) for p in px];vs=[Vector((p.x,p.z,0)) for p in pts];ts=tessellate_polygon([vs]);mp={tuple(v):i for i,v in enumerate(vs)};fs=[tuple(t) if isinstance(t[0],int) else tuple(mp[tuple(v)] for v in t) for t in ts]
    uv=[(x/im.size[0],1-y/im.size[1]) for x,y in px];return mesh(rig,name,pts,fs,uv,bn,paint,depth)
def strip(rig,name,bn,a,b,width0,width1,patch,depth,cuff=False):
    d=(b-a).normalized();right=Vector((-d.z,0,d.x));N=10;pts=[];uv=[]
    for i in range(N+1):
        t=i/N;w=width0*(1-t)+width1*t;w*=1+.025*math.sin(i*2.8)
        if 'source gray cuff' not in name and i<2:w*=.22 if i==0 else .83
        for side in [-1,1]:
            p=a.lerp(b,t)+right*w*side;pts.append(p)
            u=(side+1)/2;px=patch[0]+u*(patch[2]-patch[0]);py=patch[1]+t*(patch[3]-patch[1]);uv.append((px/im.size[0],1-py/im.size[1]))
    fs=[(i*2,i*2+1,i*2+3,i*2+2) for i in range(N)];ob=mesh(rig,name,pts,fs,uv,bn,opaque,depth)
    if cuff:
        c0=b-d*.035;c1=b+d*.012
        strip(rig,name+' | source gray cuff',bn,c0,c1,width1*1.11,width1*1.1,(490,451,548,476) if rig['character']=='BOY' else (883,439,928,460),depth-.001)
    return ob

rest={};handdata={}
for who,rig in rigs.items():
    cx=636 if who=='BOY' else 1010
    bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    for side,px in ([('near',(502,527)),('far',(812,520))] if who=='BOY' else [('near',(855,523)),('far',(1137,553))]):
        eb=rig.data.edit_bones['forearm_'+side];eb.tail=vpx(px,cx)
        hb=rig.data.edit_bones.new('hand_'+side);hb.head=eb.tail;hb.tail=eb.tail+Vector((-.01,0,-.085));hb.align_roll(Vector((0,-1,0)))
    bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
    rest[who]={b.name:(b.head_local.copy(),b.tail_local.copy()) for b in rig.data.bones}
    for side in ['near','far']:
        dep=-.035 if side=='near' else .025;r=rest[who]
        a,b=r['upper_arm_'+side];d=(b-a).normalized()
        strip(rig,'PERF_'+who+' | sleeve '+side,'upper_arm_'+side,a-d*.018,b+d*.015,.048 if who=='BOY' else .044,.050 if who=='BOY' else .045,(586,330,642,428) if who=='BOY' else (1000,353,1040,409),dep,True)
        a,b=r['forearm_'+side];d=(b-a).normalized()
        strip(rig,'PERF_'+who+' | skin '+side,'forearm_'+side,a-d*.018,b+d*.018,.025,.021,(492,494,506,522) if who=='BOY' else (867,497,878,520),dep-.001)
        donor=SRC['hands'][who];off=r['hand_'+side][0]-vpx(donor['wrist'],cx)
        poly(rig,'PERF_'+who+' | original hand '+side,donor['outline'],'hand_'+side,cx,dep-.003,off)
    headpoly=[(530,24),(786,24),(786,247),(697,253),(674,268),(636,268),(604,252),(566,244),(535,210)] if who=='BOY' else [(865,85),(1115,85),(1115,297),(1050,297),(1045,311),(1006,311),(978,300),(950,307),(944,334),(931,363),(912,394),(881,394),(864,373),(875,337),(891,307),(911,283),(891,245)]
    poly(rig,'PERF_'+who+' | original head'+(' and attached braid' if who=='GIRL' else ''),headpoly,'head',cx,-.045)
    rig['performance_version']='v002';rig['review']='Authoring study. Original face/body paint; new flat sleeve/skin overlaps and original traced donor hands.'

# Native UV masks remove source pants/arm fragments from the original held torso
# crop. Original bitmap bytes, face and body brushwork remain unchanged.
for who,rig in rigs.items():
    ob=next(o for o in rig.children if o.get('skin_region')==('body' if who=='BOY' else 'dress'))
    m=paint.copy();m.name='PERF_'+who+' | original body paint, clean native boundary';ob.data.materials[0]=m;nt=m.node_tree
    uv=nt.nodes.new('ShaderNodeTexCoord');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs['UV'],sep.inputs[0])
    def mathnode(op,a,b):
        n=nt.nodes.new('ShaderNodeMath');n.operation=op
        for i,v in enumerate([a,b]):
            if isinstance(v,(float,int)):n.inputs[i].default_value=v
            else:nt.links.new(v,n.inputs[i])
        return n.outputs[0]
    y=sep.outputs['Y'];x=sep.outputs['X']
    if who=='BOY':mask=mathnode('GREATER_THAN',y,1-553/941)
    else:
        active=mathnode('MULTIPLY',mathnode('GREATER_THAN',y,1-600/941),mathnode('LESS_THAN',y,1-450/941))
        inside=mathnode('LESS_THAN',mathnode('ADD',mathnode('MULTIPLY',x,1672),mathnode('MULTIPLY',y,235.25)),1212.75)
        mask=mathnode('MAXIMUM',mathnode('SUBTRACT',1,active),inside)
    mix=next(n for n in nt.nodes if n.type=='MIX_SHADER');old=mix.inputs[0].links[0].from_socket
    nt.links.new(mathnode('MULTIPLY',old,mask),mix.inputs[0])

def driv(obj,path,idx,expr,vars):
    try:obj.driver_remove(path,idx)
    except:pass
    fc=obj.driver_add(path,idx);fc.driver.expression=expr
    for n,(target,key) in vars.items():
        v=fc.driver.variables.new();v.name=n
        if key=='TRANSFORM_X':v.type='TRANSFORMS';v.targets[0].id=target;v.targets[0].transform_type='LOC_X';v.targets[0].transform_space='LOCAL_SPACE'
        else:v.type='SINGLE_PROP';v.targets[0].id=target;v.targets[0].data_path='["'+key+'"]'
driv(TRAVEL,'location',0,'M*(V*min(max(frame-S,0),N)/24+O)',{'M':(CTRL,'root_motion'),'V':(CTRL,'ground_speed_mps'),'S':(CTRL,'start_frame'),'N':(CTRL,'duration_frames'),'O':(TRAVEL,'distance_offset_m')})
floor=S.objects['LOCO | traveling ground preview']
driv(floor,'location',0,'-(1-M)*(V*min(max(frame-S,0),N)/24+O)',{'M':(CTRL,'root_motion'),'V':(CTRL,'ground_speed_mps'),'S':(CTRL,'start_frame'),'N':(CTRL,'duration_frames'),'O':(TRAVEL,'distance_offset_m')})

def smooth(knots,t):
    if t<=knots[0][0]:return knots[0][1]
    for (a,x),(b,y) in zip(knots,knots[1:]):
        if t<=b:
            u=(t-a)/(b-a);u=u*u*(3-2*u);return x+(y-x)*u
    return knots[-1][1]
def pose(rig,n,a,b,f):
    a=Vector(a);b=Vector(b);old=rest[rig['character']][n][1]-rest[rig['character']][n][0];d=b-a
    angle=math.atan2(d.x,d.z)-math.atan2(old.x,old.z);m=Matrix.Translation(a)@Matrix.Rotation(angle,4,'Y')@rig.data.bones[n].matrix_local.to_3x3().to_4x4()
    sc=Matrix.Identity(4);sc[1][1]=d.length/old.length;pb=rig.pose.bones[n];pb.rotation_mode='QUATERNION';pb.matrix=m@sc
    for path in ['location','rotation_quaternion','scale']:pb.keyframe_insert(path,frame=f,group=n)
def knee(a,b,l1,l2):
    u=(b-a).normalized();dist=(b-a).length;h=(l1*l1-l2*l2+dist*dist)/(2*dist)
    return a+u*h+Vector((-u.z,0,u.x))*math.sqrt(max(0,l1*l1-h*h))
def foot(who,side,base_x,lift,pitch):
    r=rest[who];data=SRC['feet'][who+'_'+side];an=r['foot_'+side][0];theta=data['flatten_angle'];pivot=data['toe'] if pitch>=0 else data['heel'];piv=Vector((pivot[0]-an.x,0,pivot[1]-an.z))
    rot=Matrix.Rotation(theta+pitch,3,'Y');flat=Matrix.Rotation(theta,3,'Y');allp=[rot@Vector((x-an.x,0,z-an.z)) for x,z in data['lower_hull']]
    z=-min(p.z for p in allp);ankle=Vector((base_x+(flat@piv).x-(rot@piv).x,0,z+lift));return ankle,rot@(r['foot_'+side][1]-an),ankle+rot@piv
def skip_foot(t):
    q=t%40
    if q<=5:return .18-.60*q/24,0.,smooth([(0,-.06),(1,0),(3,0),(4,.06),(5,.17)],q),True,'step'
    if q<10:return smooth([(5,.055),(10,.10)],q),.065*math.sin(math.pi*(q-5)/5),smooth([(5,.17),(8,-.03),(10,-.05)],q),False,'short flight'
    if q<=13:return .10-.60*(q-10)/24,0.,smooth([(10,-.05),(11,0),(12,0),(13,.20)],q),True,'same foot hop'
    return smooth([(13,.025),(20,-.22),(25,-.16),(31,.08),(36,.23),(40,.18)],q),smooth([(13,0),(20,.18),(27,.24),(34,.17),(40,0)],q),smooth([(13,.20),(22,-.15),(31,-.25),(40,-.06)],q),False,'recovery swing'
def weary_foot(t):
    p=(t/44+.61)%1;stance=.70;stride=.28*44/24
    if p<stance:return stride*stance*.5-stride*p,0,0,True
    u=(p-stance)/(1-stance);return -stride*stance*.5+stride*stance*(u*u*(3-2*u)),.055*math.sin(math.pi*u),-.05*math.sin(math.pi*u),False
def dist(t):
    t=max(0,t);total=0
    for a,b,v in [(0,17,.28),(17,29,.45),(29,47,.14),(47,63,.05),(63,200,0)]:total+=max(0,min(t,b)-a)*v/24
    return total
def stumble_foot(t,side):
    dt=dist(t)
    if t<17:
        x,z,p,c=weary_foot(t+(22 if side=='far' else 0));return x,z,p,c,'weary approach'
    if side=='near':
        catch=dist(17)+.18;settle=dist(48)+.06
        if t<=31:return catch-dt,0,smooth([(17,-.04),(20,.12),(25,.18),(31,.2)],t),True,'toe catch'
        if t<48:return smooth([(31,catch),(48,settle)],t)-dt,.13*math.sin(math.pi*(t-31)/17),-.08,False,'recover near'
        return settle-dt,0,0,True,'settled near'
    rear=dist(17)+weary_foot(17+22)[0];land=dist(33)+.25
    if t<=19:return rear-dt,0,.13,True,'rear release'
    if t<33:return smooth([(19,rear),(33,land)],t)-dt,.17*math.sin(math.pi*(t-19)/14),smooth([(19,.13),(26,-.15),(33,-.10)],t),False,'rescue step'
    return land-dt,0,smooth([(33,-.10),(36,0),(60,0)],t),True,'braking support'

CLIPS=[{'id':'PLAYFUL_SKIP','frames':40,'speed':.60,'loop':True,'reel_frames':120},{'id':'WEARY_STUMBLE_RECOVER','frames':96,'speed':.28,'loop':False,'reel_frames':96}]
records=[];actions={};travel_actions={}
for clip in CLIPS:
    N=clip['frames'];DIST.animation_data_clear();DIST.location.x=0
    if not clip['loop']:
        for f in range(1,N+1):DIST.location.x=dist(f-1);DIST.keyframe_insert('location',index=0,frame=f)
        ta=DIST.animation_data.action;ta.name='PERF_ROOT__'+clip['id'];ta.use_fake_user=True;travel_actions[clip['id']]=(ta,DIST.animation_data.action_slot)
    for who,rig in rigs.items():
        rig.animation_data_clear();r=rest[who];chlen=(r['chest'][1]-r['chest'][0]).length;headlen=(r['head'][1]-r['head'][0]).length
        for f in range(1,N+2 if clip['loop'] else N+1):
            t=f-1;phase=(t+(4 if who=='GIRL' else 0))%40
            if clip['loop']:
                u=phase%20;hz=smooth([(0,.54),(3,.50),(6,.588),(8,.616),(10,.54),(11,.505),(13,.589),(16,.68),(17,.675),(20,.54)],u)
                ang=.035+.07*math.sin(math.tau*(phase-2)/40);headang=.035+.045*math.sin(math.tau*(phase-4)/40);emph=0
            else:
                u=max(0,min(95,t+(2 if who=='GIRL' else 0)));emph=smooth([(0,0),(17,0),(29,1),(38,.8),(55,.18),(72,0),(95,0)],u)
                hz=smooth([(0,.55),(17,.55),(28,.47),(34,.405),(44,.44),(56,.50),(72,.54),(95,.535)],u)
                ang=smooth([(0,.14),(17,.14),(29,.60),(38,.48),(53,.26),(72,.12),(95,.14)],u);headang=smooth([(0,.14),(19,.14),(31,.72),(41,.40),(57,.28),(77,.12),(95,.17)],u)
            hz-=.012 if who=='GIRL' else 0;hipx=(.012 if who=='BOY' else -.012)*math.sin(math.tau*t/40) if clip['loop'] else .085*emph
            feet={}
            for side,off in [('near',0),('far',20)]:
                x,z,pitch,contact,label=skip_foot(phase+off) if clip['loop'] else stumble_foot(u,side)
                if not clip['loop']:x+=dist(u)-dist(t)
                an,fd,piv=foot(who,side,x,z,pitch);feet[side]=(an,fd,piv,contact,label,pitch)
                if contact:
                    l1=(r['thigh_'+side][1]-r['thigh_'+side][0]).length;l2=(r['shin_'+side][1]-r['shin_'+side][0]).length
                    dx=an.x-hipx-(.012 if side=='near' else -.012);hz=min(hz,an.z+math.sqrt(max(.01,(l1+l2-.003)**2-dx*dx)))
            hip=Vector((hipx,0,hz));neck=hip+Vector((math.sin(ang)*chlen,0,math.cos(ang)*chlen));pose(rig,'pelvis',hip,hip+Vector((0,0,(r['pelvis'][1]-r['pelvis'][0]).length)),f);pose(rig,'chest',hip,neck,f)
            pose(rig,'head',neck,neck+Vector((math.sin(headang)*headlen,0,math.cos(headang)*headlen)),f)
            row={'clip':clip['id'],'who':who,'frame':f,'root_distance_m':clip['speed']*t/24 if clip['loop'] else dist(t),'hip_x':hip.x,'hip_z':hip.z,'trunk_angle_rad':ang,'feet':{}}
            for side,off in [('near',0),('far',20)]:
                an,fd,piv,contact,label,pitch=feet[side];h=hip+Vector((.012 if side=='near' else -.012,0,0));l1=(r['thigh_'+side][1]-r['thigh_'+side][0]).length;l2=(r['shin_'+side][1]-r['shin_'+side][0]).length
                if not contact and (an-h).length>l1+l2-.002:an=h+(an-h).normalized()*(l1+l2-.002);piv=an+(piv-feet[side][0])
                k=knee(h,an,l1,l2);pose(rig,'thigh_'+side,h,k,f);pose(rig,'shin_'+side,k,an,f);pose(rig,'foot_'+side,an,an+fd,f)
                row['feet'][side]={'contact':contact,'phase':label,'ankle':list(an),'support_pivot':list(piv),'pitch':pitch}
                shoulder=neck+(r['upper_arm_'+side][0]-r['chest'][1]);ua=(r['upper_arm_'+side][1]-r['upper_arm_'+side][0]).length;la=(r['forearm_'+side][1]-r['forearm_'+side][0]).length
                if clip['loop']:
                    a=-.50*math.cos(math.tau*(phase+off-1)/40)+.10;flex=.35+.18*math.sin(math.tau*(phase+off-3)/40)
                else:a=.12+.12*math.cos(t/6+off)+.93*emph;flex=.18+.32*emph
                el=shoulder+Vector((ua*math.sin(a),0,-ua*math.cos(a)));wr=el+Vector((la*math.sin(a+flex),0,-la*math.cos(a+flex)));pose(rig,'upper_arm_'+side,shoulder,el,f);pose(rig,'forearm_'+side,el,wr,f)
                hd=r['hand_'+side][1]-r['hand_'+side][0];ha=a+flex+.10*math.sin(math.tau*(phase+off)/40-.3) if clip['loop'] else a+flex+.10*math.sin(t/4+off);pose(rig,'hand_'+side,wr,wr+Vector((hd.length*math.sin(ha),0,-hd.length*math.cos(ha))),f)
            if who=='GIRL':
                for n in ['skirt_front','skirt_back']:
                    a=hip+Vector((.015,0,.17));dv=r[n][1]-r[n][0];sway=.07*math.sin(math.tau*(phase-3)/40) if clip['loop'] else .17*emph
                    pose(rig,n,a,a+Matrix.Rotation(sway+ang*.14,3,'Y')@dv,f)
                pose(rig,'braid',r['braid'][0],r['braid'][1],f)
            records.append(row)
        act=rig.animation_data.action;act.name='PERF_'+who+'__'+clip['id'];act.use_fake_user=True;act['period_frames']=N;act['loop']=clip['loop'];act['speed_mps']=clip['speed'];act['review']='Performance study; inspect actual rendered sequence';act.asset_mark();actions[(who,clip['id'])]=(act,rig.animation_data.action_slot)

def linear(act):
    for layer in act.layers:
        for st in layer.strips:
            for bag in st.channelbags:
                for fc in bag.fcurves:
                    for k in fc.keyframe_points:k.interpolation='LINEAR'
for a,_ in list(actions.values())+list(travel_actions.values()):linear(a)
for who,rig in rigs.items():
    rig.animation_data.action=None
    for clip in CLIPS:
        a,slot=actions[who,clip['id']];track=rig.animation_data.nla_tracks.new();track.name=clip['id'];track.mute=not clip['loop'];st=track.strips.new(a.name,1,a);st.action_slot=slot;st.action_frame_start=1;st.action_frame_end=clip['frames']+1 if clip['loop'] else clip['frames'];st.repeat=3 if clip['loop'] else 1;st.extrapolation='HOLD_FORWARD'
DIST.animation_data_clear();DIST.location.x=0
for cid,(a,slot) in travel_actions.items():
    DIST.animation_data_create();tr=DIST.animation_data.nla_tracks.new();tr.name=cid;tr.mute=True;st=tr.strips.new(a.name,1,a);st.action_slot=slot;st.extrapolation='HOLD_FORWARD'
# animation_data_clear used during Action authoring also clears drivers. Rebuild
# the three placement/travel drivers only after all Action tracks are stashed.
for who,rig in rigs.items():driv(rig,'location',0,('-0.5*G' if who=='BOY' else '0.5*G'),{'G':(CTRL,'pair_gap_m')})
vrs={'M':(CTRL,'root_motion'),'V':(CTRL,'ground_speed_mps'),'S':(CTRL,'start_frame'),'N':(CTRL,'duration_frames'),'C':(CTRL,'use_distance_curve'),'D':(DIST,'TRANSFORM_X')}
driv(TRAVEL,'location',0,'M*((1-C)*V*min(max(frame-S,0),N)/24+C*D)',vrs)
driv(floor,'location',0,'-(1-M)*((1-C)*V*min(max(frame-S,0),N)/24+C*D)',vrs)
CTRL.update_tag(refresh={'OBJECT'});TRAVEL.update_tag(refresh={'OBJECT'})
for ob in [CTRL,*CTRL.children_recursive,floor]:
    ob.update_tag(refresh={'OBJECT'})
    if ob.animation_data:
        for fc in ob.animation_data.drivers:fc.driver.expression=str(fc.driver.expression)
bpy.context.view_layer.update()
S.objects['LOCO | clip label'].data.body='PLAYFUL SKIP / step-hop / 24fps / performance study v002'
S.objects['LOCO | title'].data.body='WHEN THE SKY CLEARS / LOCOMOTION 02'
S.objects['LOCO | provisional'].data.body='ORIGINAL FACE + BODY PAINT / NATIVE FLAT OVERLAPS / ARTISTIC REVIEW OPEN'
S.camera.data.ortho_scale=3.9;S.camera.location.z=.88
S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=2;S.cycles.use_denoising=False;S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100
helper=bpy.data.texts.get('configure_performance.py') or bpy.data.texts.new('configure_performance.py');helper.clear();helper.write((P/'scripts/configure_performance.py').read_text())
S.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Performance_Library_v002.blend'),compress=True)
(P/'evidence/performance_samples.json').write_text(json.dumps(records,indent=2))
(P/'evidence/build_manifest.json').write_text(json.dumps({'blender':bpy.app.version_string,'source_library':str(source),'source_sha256':source_hash,'clips':CLIPS,'actions':[a.name for a,_ in actions.values()],'new_art':'Native flat sleeve, cuff and skin overlap vectors sample original paint; hands traced from original source; original heads recontoured to include attached braid; no generated bitmap or visible 3D model','height_source_m':[1.45,1.3699177],'fps':24,'units':'metres','plane':'XZ','source_preserved':hashlib.sha256(source.read_bytes()).hexdigest()==source_hash},indent=2))
print('PERFORMANCE_NATIVE_BUILD_COMPLETE',flush=True)
if '--proof' in sys.argv:
    for f in [1,4,7,9,12,14,17,21,25,29,34,39]:
        S.frame_set(f);S.render.filepath=str(P/f'previews/skip_proof_{f:03d}.png');bpy.ops.render.render(write_still=True)
