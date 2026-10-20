"""Project-owned source paint -> editable planar skin meshes and native Actions.
No production .blend is opened for writing. No handlers, add-ons or downloads.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.geometry import tessellate_polygon

P=Path(__file__).resolve().parents[1]; R=P.parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene; S.name='LOCO | Pair neutral walk proof'
S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=1;S.cycles.use_denoising=False
S.render.threads_mode='FIXED';S.render.threads=2
S.render.resolution_x=960;S.render.resolution_y=540;S.render.resolution_percentage=100
S.render.fps=24;S.render.fps_base=1;S.frame_start=1;S.frame_end=96
S.unit_settings.system='METRIC';S.unit_settings.scale_length=1
S.view_settings.view_transform='Standard';S.view_settings.look='None'
S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGBA'
S.world=bpy.data.worlds.new('LOCO | neutral paper');S.world.use_nodes=True
S.world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.70,.64,1)
S.world.node_tree.nodes['Background'].inputs[1].default_value=1

def col(name,parent=None):
    c=bpy.data.collections.new(name);(parent or S.collection).children.link(c);return c
PAIR=col('WTSC_LOCO_PAIR_v001');PAIR.asset_mark()
PAIR.asset_data.description='Native editable 2D painted cutout rigs. Near-age original v015 paint. 24fps XZ/metres. Walk, trudge, crouch, care reach.'
CTRL=bpy.data.objects.new('LOCO_PAIR | CONTROLS',None);PAIR.objects.link(CTRL)
CTRL.empty_display_type='CIRCLE';CTRL.empty_display_size=.2
CTRL['loco_pack']='WTSC_LOCO_v001'
for k,v in {'root_motion':0.,'ground_speed_mps':.40,'start_frame':1.,'pair_gap_m':.66}.items():CTRL[k]=v
CTRL['guide']='Root motion 0=in-place, 1=travel +X. Set ground_speed_mps to selected Action speed divided by NLA retime scale. pair_gap controls hip spacing, average stays centred.'
CTRL['orientation']='XZ drawings; metres; +X forward; +Z up; +Y back. Origins on floor.'
TRAVEL=bpy.data.objects.new('LOCO_PAIR | TRAVEL',None);PAIR.objects.link(TRAVEL);TRAVEL.parent=CTRL
def driver(obj,path,index,expression,props):
    fc=obj.driver_add(path,index);d=fc.driver;d.expression=expression
    for name,key in props.items():
        v=d.variables.new();v.name=name;v.type='SINGLE_PROP';v.targets[0].id=CTRL;v.targets[0].data_path='["'+key+'"]'
driver(TRAVEL,'location',0,'M*V*(frame-S)/24',{'M':'root_motion','V':'ground_speed_mps','S':'start_frame'})

im=bpy.data.images.load(str(R/'characters/Pair_Painterly_Near_Age_v015.png'));im.pack()
mat=bpy.data.materials.new('LOCO | ORIGINAL v015 charcoal paint, packed');mat.use_nodes=True
nt=mat.node_tree;nt.nodes.clear();tex=nt.nodes.new('ShaderNodeTexImage');tex.image=im;tex.extension='CLIP'
gray=nt.nodes.new('ShaderNodeHueSaturation');gray.inputs['Saturation'].default_value=0;gray.inputs['Value'].default_value=.8
nt.links.new(tex.outputs['Color'],gray.inputs['Color'])
em=nt.nodes.new('ShaderNodeEmission');nt.links.new(gray.outputs[0],em.inputs[0]);tr=nt.nodes.new('ShaderNodeBsdfTransparent')
mix=nt.nodes.new('ShaderNodeMixShader');out=nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(tex.outputs['Alpha'],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs[0])
mat.diffuse_color=(.025,.025,.025,1);mat.surface_render_method='DITHERED'

recipe=json.loads((R/'characters/Pair_Painterly_Near_Age_Vector_v015.json').read_text())
SCALE=1.45/(recipe['bounds_pixels'][3]-recipe['bounds_pixels'][1]);BASE=recipe['bounds_pixels'][3]
def v2(p,cx):return Vector(((p[0]-cx)*SCALE,0,(BASE-p[1])*SCALE))

# Every polygon samples the unchanged, packed source drawing. Dense mesh skinning
# permits elbow/knee bends while preserving original face, clothes and brushwork.
# Seams sit inside overlapping painted sleeves, trousers and dress.
SPEC={
 'BOY':{'cx':636,'height':1.45,'hipz':.578,'head':[(650,270),(651,125)],'neck':(650,267),
 'legs':{'near':[(636,553),(711,705),(751,845),(810,871)],'far':[(608,553),(556,680),(493,836),(534,872)]},
 'arms':{'near':[(602,306),(520,455),(491,550)],'far':[(674,321),(756,465),(822,538)]},
 'parts':[
 ('far_leg',[(575,530),(660,540),(650,608),(607,668),(563,739),(531,799),(511,843),(520,858),(569,866),(587,892),(566,910),(522,906),(475,888),(430,864),(450,824),(477,806),(502,753),(534,685),(548,637)],'leg_far',.022),
 ('near_leg',[(617,533),(693,538),(710,600),(737,668),(762,735),(787,798),(780,836),(791,852),(823,856),(849,870),(868,882),(848,898),(805,910),(715,911),(711,888),(719,859),(717,832),(687,793),(658,734),(630,686),(603,632),(588,584)],'leg_near',-.012),
 ('far_arm',[(646,294),(682,299),(704,353),(741,405),(798,456),(786,487),(815,512),(848,530),(861,545),(850,567),(827,577),(803,563),(789,541),(760,521),(728,494),(695,467),(675,419)],'arm_far',.015),
 ('body',[(608,244),(648,250),(682,279),(696,335),(700,405),(714,478),(735,545),(695,559),(648,563),(602,555),(535,551),(549,499),(568,423),(581,356),(590,296)],'body',0),
 ('near_arm',[(602,281),(645,315),(619,365),(589,412),(563,462),(550,491),(527,485),(522,513),(510,541),(506,568),(487,584),(471,579),(459,559),(462,536),(475,511),(489,471),(486,454),(511,414),(546,359),(568,322)],'arm_near',-.025),
 ('head',[(530,24),(786,24),(786,255),(696,268),(675,292),(633,291),(604,270),(566,244),(535,210)],'head',-.03)]},
 'GIRL':{'cx':1010,'height':recipe['girl_height_m'],'hipz':.565,'head':[(1009,315),(1000,174)],'neck':(1009,315),
 'legs':{'near':[(1037,573),(1099,727),(1147,846),(1204,878)],'far':[(978,553),(948,723),(915,843),(951,879)]},
 'arms':{'near':[(1002,347),(929,447),(847,542)],'far':[(1060,382),(1114,474),(1144,568)]},
 'parts':[
 ('far_leg',[(930,652),(1011,663),(995,715),(968,777),(949,823),(944,851),(970,865),(999,883),(1009,905),(965,913),(910,906),(863,887),(868,862),(884,831),(896,788),(908,725)],'leg_far',.023),
 ('near_leg',[(1015,650),(1080,638),(1114,707),(1139,766),(1160,821),(1169,846),(1206,854),(1231,856),(1257,870),(1255,893),(1232,903),(1192,909),(1126,913),(1117,890),(1117,857),(1102,819),(1081,774),(1057,725)],'leg_near',-.012),
 ('far_arm',[(1072,421),(1097,454),(1123,479),(1148,526),(1165,557),(1169,583),(1157,600),(1137,595),(1125,572),(1118,541),(1097,504),(1071,480),(1056,448)],'arm_far',.018),
 ('body',[(1000,294),(1045,312),(1068,356),(1080,406),(1094,456),(1112,530),(1145,614),(1161,696),(1117,718),(1061,725),(996,717),(935,701),(878,685),(835,676),(867,636),(910,574),(944,514),(970,461),(983,406),(982,362),(970,322)],'dress',0),
 ('near_arm',[(991,332),(1020,360),(997,392),(977,414),(950,448),(932,480),(912,471),(890,502),(872,527),(861,544),(850,560),(831,575),(814,569),(798,550),(802,531),(817,521),(836,520),(855,502),(878,474),(877,452),(898,419),(939,378),(978,343)],'arm_near',-.026),
 ('braid',[(947,272),(977,281),(964,302),(945,330),(931,363),(910,389),(887,389),(870,369),(879,340),(894,310),(918,291)],'braid',-.035),
 ('head',[(878,86),(1112,86),(1112,287),(1053,310),(1041,334),(1006,327),(979,311),(955,297),(922,279),(892,242)],'head',-.04)]}}

def bone_rows(spec):
    b={'pelvis':[(spec['cx'],553),(spec['cx'],493)],'chest':[(spec['cx'],553),spec['neck']], 'head':spec['head']}
    for side,pts in spec['legs'].items():
        for name,a,z in zip(['thigh_','shin_','foot_'],pts,pts[1:]):b[name+side]=[a,z]
    for side,pts in spec['arms'].items():
        b['upper_arm_'+side]=pts[:2];b['forearm_'+side]=pts[1:]
    if spec['cx']==1010:
        b['braid']=[(947,282),(904,373)];b['skirt_front']=[(1020,450),(1125,690)];b['skirt_back']=[(1020,450),(880,665)]
    return b

def segment_distance(p,a,b):
    d=b-a;t=max(0,min(1,(p-a).dot(d)/d.length_squared));return (p-(a+t*d)).length

def weights(part,p,rest,spec):
    if part.startswith('rigid:'):return {part.split(':',1)[1]:1}
    if part=='head':return {'head':1}
    if part=='braid':return {'braid':1}
    if part=='body':
        z=p.z;t=max(0,min(1,(z-.62)/.25));return {'pelvis':1-t,'chest':t}
    if part=='dress':
        if p.z>.79:return {'chest':1}
        w=max(0,min(.82,(.79-p.z)/.42));x=(p.x+.21)/.42;x=max(0,min(1,x))
        return {'pelvis':1-w,'skirt_front':w*x,'skirt_back':w*(1-x)}
    typ,side=part.split('_');bn=['thigh_'+side,'shin_'+side,'foot_'+side] if typ=='leg' else ['upper_arm_'+side,'forearm_'+side]
    if typ=='leg' and p.z<rest['foot_'+side][0].z-.008:return {'foot_'+side:1}
    ds=[segment_distance(p,*rest[n]) for n in bn]
    # Soft zones at anatomical joints; elsewhere almost rigid painted shapes.
    vals=[1/max(.010,d)**5 for d in ds];total=sum(vals)
    return {n:w/total for n,w in zip(bn,vals)}

rigs={};metadata=[]
def clip_halfplane(poly,origin,direction,limit,keep_less):
    out=[]
    def value(p):return (p[0]-origin[0])*direction[0]+(p[1]-origin[1])*direction[1]-limit
    for a,b in zip(poly,poly[1:]+poly[:1]):
        va=value(a);vb=value(b);ina=(va<=0) if keep_less else (va>=0);inb=(vb<=0) if keep_less else (vb>=0)
        if ina:out.append(a)
        if ina!=inb:
            t=va/(va-vb);out.append((a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])))
    return out
for who,spec in SPEC.items():
    C=col('LOCO_'+who+' | painted 2D rig',PAIR)
    data=bpy.data.armatures.new('LOCO_'+who+' | native planar skeleton');rig=bpy.data.objects.new('LOCO_'+who+' | RIG',data);C.objects.link(rig);rig.parent=TRAVEL
    rig.show_in_front=True;rig.hide_render=True;rig['character']=who;rig['height_m']=spec['height'];rig['source']='Unchanged Pair_Painterly_Near_Age_v015.png; provisional existing design'
    rig['motion_status']='First locomotion blocking / contact validated; artistic approval pending'
    driver(rig,'location',0,('-0.5*G' if who=='BOY' else '0.5*G'),{'G':'pair_gap_m'})
    bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    rest={n:[v2(p,spec['cx']) for p in pts] for n,pts in bone_rows(spec).items()}
    for n,(a,b) in rest.items():
        eb=data.edit_bones.new(n);eb.head=a;eb.tail=b;eb.align_roll(Vector((0,-1,0)))
    bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
    parts=[]
    for name,poly,part,depth in spec['parts']:
        if part.startswith('arm_'):
            side=part.split('_')[1];elbow=spec['arms'][side][1];wrist=spec['arms'][side][2]
            dx=wrist[0]-elbow[0];dy=wrist[1]-elbow[1];ll=math.hypot(dx,dy);d=(dx/ll,dy/ll)
            parts.append((name+'_upper',clip_halfplane(poly,elbow,d,15,True),'rigid:upper_arm_'+side,depth+.001))
            parts.append((name+'_lower',clip_halfplane(poly,elbow,d,-15,False),'rigid:forearm_'+side,depth-.001))
        else:parts.append((name,poly,part,depth))
    for name,poly,part,depth in parts:
        # Triangulate then subdivide each source triangle four times for smooth skinning.
        verts=[v2(p,spec['cx']) for p in poly];flat=[Vector((v.x,v.z,0)) for v in verts]
        tris=tessellate_polygon([flat]);lookup={tuple(v):i for i,v in enumerate(flat)}
        faces=[tuple(tri) if isinstance(tri[0],int) else tuple(lookup[tuple(v)] for v in tri) for tri in tris]
        for _ in range(3):
            edges={};fs=[]
            def mid(a,b):
                e=tuple(sorted([a,b]))
                if e not in edges:edges[e]=len(verts);verts.append((verts[a]+verts[b])*.5)
                return edges[e]
            for a,b,c in faces:
                ab=mid(a,b);bc=mid(b,c);ca=mid(c,a);fs.extend([(a,ab,ca),(ab,b,bc),(ca,bc,c),(ab,bc,ca)])
            faces=fs
        me=bpy.data.meshes.new('LOCO_'+who+' | '+name+' | 2D skin');me.from_pydata([(v.x,depth,v.z) for v in verts],[],faces);me.update()
        ob=bpy.data.objects.new('LOCO_'+who+' | PAINT '+name,me);C.objects.link(ob);ob.parent=rig
        uv=me.uv_layers.new(name='UNCHANGED original paint registration')
        for l in me.loops:
            v=verts[l.vertex_index];uv.data[l.index].uv=((v.x/SCALE+spec['cx'])/im.size[0],1-(BASE-v.z/SCALE)/im.size[1])
        me.materials.append(mat)
        groups={n:ob.vertex_groups.new(name=n) for n in rest}
        for i,p in enumerate(verts):
            for n,w in weights(part,p,rest,spec).items():
                if w>1e-6:groups[n].add([i],w,'REPLACE')
        mod=ob.modifiers.new('Native planar armature deformation','ARMATURE');mod.object=rig
        ob['visible_geometry']='Flat editable 2D painted cutout. No modeled child or generative redesign.'
        ob['source_region']=json.dumps(poly);ob['skin_region']=part
    rigs[who]=(rig,rest,spec)
    metadata.append({'character':who,'height_m':spec['height'],'rig':rig.name,'native_bones':len(rest),'cutout_parts':len(parts)})

def pose_bone(rig,rest,n,a,b,f):
    a=Vector(a);b=Vector(b);old=rest[n][1]-rest[n][0];d=b-a
    ang=math.atan2(d.x,d.z)-math.atan2(old.x,old.z)
    m=Matrix.Translation(a)@Matrix.Rotation(ang,4,'Y')@rig.data.bones[n].matrix_local.to_3x3().to_4x4()
    scale=Matrix.Identity(4);scale[1][1]=d.length/old.length
    pb=rig.pose.bones[n];pb.rotation_mode='QUATERNION';pb.matrix=m@scale
    pb.keyframe_insert('location',frame=f,group=n);pb.keyframe_insert('rotation_quaternion',frame=f,group=n);pb.keyframe_insert('scale',frame=f,group=n)

def ik(a,b,l1,l2):
    d=(b-a).length;d=min(d,l1+l2-.0001)
    u=(b-a).normalized();h=(l1*l1-l2*l2+d*d)/(2*d);v=Vector((-u.z,0,u.x))
    return a+u*h+v*math.sqrt(max(0,l1*l1-h*h))

def footphase(p,speed,period,lift,stance=.62):
    p=p%1;stride=speed*period/24;span=stride*stance
    if p<stance:return Vector((span*.5-stride*p,0,.083)),True
    u=(p-stance)/(1-stance)
    # Smooth cubic swing; velocity matches ground at both ends, avoiding a pop.
    x=(2*u**3-3*u*u+1)*(-span*.5)+(u**3-2*u*u+u)*(-stride*(1-stance))+(-2*u**3+3*u*u)*(span*.5)+(u**3-u*u)*(-stride*(1-stance))
    return Vector((x,0,.083+lift*math.sin(math.pi*u)**1.3)),False

CLIPS=[{'id':'WALK','frames':32,'speed':.40,'lift':.08,'stance':.62,'kind':'loop','note':'Neutral walk, restrained counter-swing and double support.'},
       {'id':'TRUDGE','frames':44,'speed':.24,'lift':.045,'stance':.70,'kind':'loop','note':'Weary small steps, delayed head and dropped shoulders.'},
       {'id':'CAUTION_CROUCH','frames':48,'speed':0,'kind':'transition','note':'Stand, lower defensively, hold, return. Feet remain planted.'},
       {'id':'CARE_REACH','frames':64,'speed':0,'kind':'transition','note':'Pair turns attention toward each other, reaching hands meet, then release.'}]
contact_report=[]

def make_action(who,clip):
    rig,rest,spec=rigs[who];N=clip['frames'];rig.animation_data_create();rig.animation_data.action=None
    basehip=Vector((0,0,spec['hipz']));chestlen=(rest['chest'][1]-rest['chest'][0]).length
    headlen=(rest['head'][1]-rest['head'][0]).length
    logs=[]
    for f in range(1,N+2):
        phase=(f-1)/N;S.frame_set(f);angle=0;lower=0;bob=0;progress=0
        if clip['kind']=='loop':
            bob=.012*math.cos(4*math.pi*phase) if clip['id']=='WALK' else .008*math.cos(4*math.pi*phase)
            angle=.035 if clip['id']=='WALK' else .14
        elif clip['id']=='CAUTION_CROUCH':
            u=min(1,max(0,(f-5)/14)) if f<=28 else 1-min(1,max(0,(f-32)/16))
            progress=u*u*(3-2*u);lower=.19*progress;angle=.23*progress
        else:
            u=min(1,max(0,(f-5)/19)) if f<=40 else 1-min(1,max(0,(f-42)/22))
            progress=u*u*(3-2*u);lower=.055*progress;angle=(.09 if who=='BOY' else -.09)*progress
        hip=basehip+Vector((-.025*progress if clip['id']=='CAUTION_CROUCH' else 0,0,bob-lower))
        neck=hip+Vector((math.sin(angle)*chestlen,0,math.cos(angle)*chestlen))
        pose_bone(rig,rest,'pelvis',hip,hip+Vector((0,0,.1)),f)
        pose_bone(rig,rest,'chest',hip,neck,f)
        headang=angle*(.45 if clip['id']=='TRUDGE' else .8)
        pose_bone(rig,rest,'head',neck,neck+Vector((math.sin(headang)*headlen,0,math.cos(headang)*headlen)),f)
        rec={'character':who,'clip':clip['id'],'frame':f,'hip_z':hip.z,'feet':{}}
        for side,offset in [('near',0),('far',.5)]:
            if clip['kind']=='loop':ankle,contact=footphase(phase+offset,clip['speed'],N,clip['lift'],clip['stance'])
            else:ankle=Vector((.12 if side=='near' else -.14,0,.083));contact=True
            # Preserve the source shoe's planted angle and its observed sole line.
            sole_px={('BOY','near'):906,('BOY','far'):904,('GIRL','near'):906,('GIRL','far'):907}[(who,side)]
            ankle.z+=rest['foot_'+side][0].z-(BASE-sole_px)*SCALE-.083
            l1=(rest['thigh_'+side][1]-rest['thigh_'+side][0]).length;l2=(rest['shin_'+side][1]-rest['shin_'+side][0]).length
            h=hip+Vector((.012 if side=='near' else -.012,0,0));kn=ik(h,ankle,l1,l2)
            pose_bone(rig,rest,'thigh_'+side,h,kn,f);pose_bone(rig,rest,'shin_'+side,kn,ankle,f)
            fl=(rest['foot_'+side][1]-rest['foot_'+side][0]).length
            fa=0 if contact else .16*math.sin(math.pi*((phase+offset)%1-clip['stance'])/(1-clip['stance']))
            source_delta=rest['foot_'+side][1]-rest['foot_'+side][0]
            pose_bone(rig,rest,'foot_'+side,ankle,ankle+Matrix.Rotation(fa,3,'Y')@source_delta,f)
            rec['feet'][side]={'local_x':ankle.x,'ankle_z':ankle.z,'contact':contact,'travel_x':ankle.x+clip['speed']*(f-1)/24}
            arm=spec['arms'][side];shoulder=neck+(v2(arm[0],spec['cx'])-rest['chest'][1])
            ua=(rest['upper_arm_'+side][1]-rest['upper_arm_'+side][0]).length;la=(rest['forearm_'+side][1]-rest['forearm_'+side][0]).length
            swing=-.28*math.cos(2*math.pi*(phase+offset)) if clip['kind']=='loop' else .06
            if clip['id']=='TRUDGE':swing*=.43
            elbow=shoulder+Vector((ua*math.sin(swing),0,-ua*math.cos(swing)))
            wrist=elbow+Vector((la*math.sin(swing+.10),0,-la*math.cos(swing+.10)))
            if clip['id']=='CAUTION_CROUCH':
                goal=neck+Vector((.16,0,-.17));wrist=wrist.lerp(goal,progress);elbow=ik(shoulder,wrist,ua,la)
            if clip['id']=='CARE_REACH' and side==('far' if who=='BOY' else 'near'):
                # Equal opposite local reach keeps the pair's mean location fixed.
                goal=Vector((.33 if who=='BOY' else -.33,0,.77));wrist=wrist.lerp(goal,progress);elbow=ik(shoulder,wrist,ua,la)
            pose_bone(rig,rest,'upper_arm_'+side,shoulder,elbow,f);pose_bone(rig,rest,'forearm_'+side,elbow,wrist,f)
        if who=='GIRL':
            hd=rest['head'][1]-rest['head'][0];headrot=headang-math.atan2(hd.x,hd.z)
            a=neck+Matrix.Rotation(headrot,3,'Y')@(rest['braid'][0]-rest['head'][0])
            sway=.045*math.sin(2*math.pi*phase-.7) if clip['kind']=='loop' else 0
            pose_bone(rig,rest,'braid',a,a+Matrix.Rotation(headrot+sway,3,'Y')@(rest['braid'][1]-rest['braid'][0]),f)
            for n in ['skirt_front','skirt_back']:
                a=hip+Vector((.015,0,.17));old=rest[n][1]-rest[n][0];rot=.045*math.sin(2*math.pi*phase-.4) if clip['kind']=='loop' else .12*progress
                pose_bone(rig,rest,n,a,a+Matrix.Rotation(rot,3,'Y')@old,f)
        logs.append(rec)
    act=rig.animation_data.action;act.name='LOCO_'+who+'__'+clip['id']+'__v001';act.use_fake_user=True;act['fps']=24;act['speed_mps']=clip['speed'];act['period_frames']=N;act['loop']=clip['kind']=='loop';act.asset_mark();act.asset_data.description=clip['note']+f' {N}fr /24fps, {clip["speed"]}m/s.'
    for layer in act.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for k in fc.keyframe_points:k.interpolation='LINEAR'
    slot=rig.animation_data.action_slot
    contact_report.extend(logs)
    return act,slot

actions={}
for who in rigs:
    for clip in CLIPS:actions[(who,clip['id'])]=make_action(who,clip)

def use(who,clip,repeat=1):
    rig=rigs[who][0];act,slot=actions[who,clip];rig.animation_data.action=None
    track=rig.animation_data.nla_tracks.new();track.name='ACTIVE | '+clip
    strip=track.strips.new(act.name,1,act);strip.action_slot=slot;strip.action_frame_start=1;strip.action_frame_end=act['period_frames']+1;strip.repeat=repeat;strip.extrapolation='NOTHING'
    return strip
for who in rigs:
    use(who,'WALK',3)
    for clip in ['TRUDGE','CAUTION_CROUCH','CARE_REACH']:
        use(who,clip);rigs[who][0].animation_data.nla_tracks[-1].mute=True

# Preserve an exact native GP source boundary as a hidden editable reference.
REF=col('LOCO | SOURCE GP boundary and original paint | hidden')
with bpy.data.libraries.load(str(R/'shots/world/WTSC_Full_Knockout_Trailer_Editable_v038.blend'),link=False) as (src,dst):
    dst.objects=[n for n in src.objects if n=='v016 | CHILDREN | held painterly near-age pair']
for o in dst.objects:
    REF.objects.link(o);o.name='LOCO_SOURCE | exact current GP outline';o.animation_data_clear();o.location=(0,0,0);o.hide_render=True;o.hide_viewport=True
REF.hide_render=True;REF.hide_viewport=True

def solid(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs[0].default_value=(*color,1);o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],o.inputs[0]);return m
PAPER=solid('LOCO | paper',(.64,.62,.56));GROUND=solid('LOCO | ground',(.29,.29,.26));INK=solid('LOCO | labels',(.09,.11,.12));TICK=solid('LOCO | ground ticks',(.18,.20,.18))
STAGE=col('LOCO | removable preview stage')
def rect(name,x0,x1,z0,z1,y,m,parent=None):
    me=bpy.data.meshes.new(name);me.from_pydata([(x0,y,z0),(x1,y,z0),(x1,y,z1),(x0,y,z1)],[],[(0,1,2,3)]);me.materials.append(m);o=bpy.data.objects.new(name,me);STAGE.objects.link(o);o.parent=parent;return o
rect('LOCO | paper',-20,20,-10,10,2,PAPER)
rect('LOCO | ground',-30,30,-1,-.005,1,GROUND)
floor=bpy.data.objects.new('LOCO | traveling ground preview',None);STAGE.objects.link(floor)
driver(floor,'location',0,'-(1-M)*V*(frame-S)/24',{'M':'root_motion','V':'ground_speed_mps','S':'start_frame'})
for i in range(-80,90):rect('LOCO | 0.2m ground tick %d'%i,i*.2,i*.2+.003,-.04,-.006,.98,TICK,floor)
def text(name,body,x,z,size):
    d=bpy.data.curves.new(name,'FONT');d.body=body;d.size=size;d.materials.append(INK);o=bpy.data.objects.new(name,d);STAGE.objects.link(o);o.location=(x,-.6,z);o.rotation_euler=(math.pi/2,0,0);return o
text('LOCO | title','WHEN THE SKY CLEARS / LOCOMOTION 01',-1.51,1.71,.077)
LABEL=text('LOCO | clip label','NEUTRAL WALK / 24fps / 0.40m per sec / 32fr cycle',-1.51,1.61,.057)
text('LOCO | provisional','ORIGINAL v015 PAINT  |  EDITABLE 2D RIGS  |  FIRST MOTION STUDY',-1.51,-.16,.048)
cd=bpy.data.cameras.new('LOCO | XZ camera');cd.type='ORTHO';cd.ortho_scale=3.6
cam=bpy.data.objects.new(cd.name,cd);STAGE.objects.link(cam);cam.location=(0,-12,.81);cam.rotation_euler=(math.pi/2,0,0);S.camera=cam
cam.parent=TRAVEL
S.frame_set(1)
S['proof']='Native flat painted mesh rigs, unchanged source paint; GP source outline retained hidden. Not a generic 3D replacement.'
S['preview_resource_limit']='Cycles CPU only, two threads, one sequential process. No shared UI or GPU.'
readme=bpy.data.texts.new('READ ME | locomotion first pack')
readme.write('Append collection WTSC_LOCO_PAIR_v001. Select LOCO_PAIR | CONTROLS.\nXZ /metres /24fps. root_motion 0=in-place,1=travel; ground_speed_mps matches Action.\nOriginal charcoal paint is packed and unchanged. Visible children are native flat skinned 2D meshes, with an exact hidden GP source boundary.\nNLA walk active. Other Actions retained as assets: WALK, TRUDGE, CAUTION_CROUCH, CARE_REACH.\nPose bones are independent planar controls, baked every frame, native editable keys. No Python handlers required.\nSource is one held drawing; hidden surfaces are not yet redraw-checked. First motion study, not production acceptance.\nSee accompanying IMPORT_GUIDE.txt and evidence for contacts, speed, append test and limitations.\n')
helper=bpy.data.texts.new('configure_clip.py');helper.write((P/'scripts/configure_clip.py').read_text())
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
S.render.filepath=str(P/'previews/walk/frame_')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Locomotion_Library_v001.blend'),compress=True)
(P/'evidence/contact_samples.json').write_text(json.dumps(contact_report,indent=2))
(P/'evidence/asset_manifest.json').write_text(json.dumps({'blender':bpy.app.version_string,'fps':24,'units':'metres','plane':'XZ','source':im.name,'packed':bool(im.packed_file),'characters':metadata,'clips':CLIPS,'actions':[a.name for a,_ in actions.values()],'render':'Cycles CPU,2threads,1sample','bounded_pack':'walk,trudge,caution crouch,care reach; remaining motions planned'},indent=2))
print('LOCOMOTION_LIBRARY_BUILT',flush=True)
import sys
if '--proof' in sys.argv:
    for frame in [1,9,17,25]:
        S.frame_set(frame);S.render.filepath=str(P/f'previews/proof_{frame:03d}.png');bpy.ops.render.render(write_still=True)
