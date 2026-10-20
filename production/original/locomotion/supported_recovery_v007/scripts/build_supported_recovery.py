"""Localized authored2D pose drawings, not further rigid knee-cap rotations.
All changes are in specialist copies. Protected foot/root matrices are checked.
"""
import bpy,math,json,runpy,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import acting_v007
P=Path(__file__).resolve().parents[1];R=P.parents[1]
BASE=R/'locomotion/battlefield_proof_v005/native/WTSC_Battlefield_Weary_Stumble_5s_v005.blend'
base_hash=hashlib.sha256(BASE.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(BASE),load_ui=False);S=bpy.context.scene
root=next(o for o in S.objects if o.get('loco_pack')=='WTSC_BATTLEFIELD_WEARY_v005');oldconfig=runpy.run_path(str(R/'locomotion/battlefield_proof_v005/scripts/configure_battlefield.py'))['configure_battlefield'];oldconfig(start=1801,root_motion=False,root=root)
rigs={o['character']:o for o in root.children_recursive if o.type=='ARMATURE'};distance=next(o for o in root.children if o.get('loco_role')=='DISTANCE_CURVE')
travel=next(o for o in root.children if 'TRAVEL' in o.name);pair=root.users_collection[0];pair.name='WTSC_BATTLEFIELD_DRAWN_PAIR_v007';root['loco_pack']='WTSC_BATTLEFIELD_DRAWN_v007';root['motion_revision']='v007_drawn_pose_corrections';root['review_status']='Localized silhouette/hand corrections; inspect actual motion before cinematic acceptance.'
pair.asset_data.description='Five-second weary recovery with authored curved limb silhouettes, articulated hand drawings and living settle. Preserved v005 route/foot contract; native shape keys and Bezier pose guides.'
rest={w:{b.name:b.matrix_local.copy() for b in rig.data.bones} for w,rig in rigs.items()};baseline={w:{} for w in rigs};D=[]
for f in range(1,121):
    S.frame_set(1800+f);bpy.context.view_layer.update();D.append(distance.location.x)
    for who,rig in rigs.items():baseline[who][f]={p.name:p.matrix.copy() for p in rig.pose.bones}
source_materials={who:{'pants':next(o for o in rig.children if o.get('skin_region')=='leg_near').data.materials[0],
                        'skin':next(o for o in rig.children if ' | skin near' in o.name).data.materials[0],
                        'sleeve':next(o for o in rig.children if ' | sleeve near' in o.name and 'cuff' not in o.name).data.materials[0],
                        'cuff':next(o for o in rig.children if 'sleeve near | source gray cuff' in o.name).data.materials[0],
                        'hand':next(o for o in rig.children if 'original hand near' in o.name).data.materials[0]} for who,rig in rigs.items()}
im=next(i for i in bpy.data.images if i.name.startswith('Pair_Painterly_Near_Age'))
def opaque_copy(m,name):
    n=m.copy();n.name=name
    mix=next((x for x in n.node_tree.nodes if x.type=='MIX_SHADER'),None)
    if mix:
        value=n.node_tree.nodes.new('ShaderNodeValue');value.outputs[0].default_value=1;n.node_tree.links.new(value.outputs[0],mix.inputs[0])
    return n
mats={w:{k:opaque_copy(m,'V007 '+w+' drawn '+k) for k,m in mm.items()} for w,mm in source_materials.items()}
def smooth(a,b,t):
    u=max(0,min(1,(t-a)/(b-a)));return u*u*(3-2*u)
def curveval(keys,t):
    if t<=keys[0][0]:return keys[0][1]
    for (a,x),(b,y) in zip(keys,keys[1:]):
        if t<=b:return x+(y-x)*smooth(a,b,t)
    return keys[-1][1]
def around(p,angle):return Matrix.Translation(p)@Matrix.Rotation(angle,4,'Y')@Matrix.Translation(-p)
def linear(action):
    for l in action.layers:
        for st in l.strips:
            for bag in st.channelbags:
                for fc in bag.fcurves:
                    for k in fc.keyframe_points:k.interpolation='LINEAR'
def stash(id,action,name):
    slot=id.animation_data.action_slot;id.animation_data.action=None;track=id.animation_data.nla_tracks.new();track.name=name;st=track.strips.new(action.name,1,action);st.action_slot=slot;st.action_frame_start=1;st.action_frame_end=120;st.frame_end=120;st.extrapolation='HOLD';action.use_fake_user=True;return st

# Bake exact120frame protected lower-body poses, with independent upper-body
# recovery/counterbalance. Native keys remain editable; no live handlers.
poses={w:{} for w in rigs};upper=['chest','head','upper_arm_near','upper_arm_far','forearm_near','forearm_far','hand_near','hand_far','braid']
oldactions=list(bpy.data.actions)
acting_v007.author(globals())
for t in list(distance.animation_data.nla_tracks):distance.animation_data.nla_tracks.remove(t)
distance.animation_data.action=None
for f,d in enumerate(D,1):distance.location.x=d;distance.keyframe_insert('location',index=0,frame=f)
distance.animation_data.action.name='V007_ROOT__PRESERVED_DISTANCE_120F';linear(distance.animation_data.action);stash(distance,distance.animation_data.action,'V007 preserved route')
for a in oldactions:
    a.use_fake_user=False
    if a.users==0:bpy.data.actions.remove(a)

GUIDES=bpy.data.collections.new('V007 | EDITABLE BEZIER CORRECTION POSES | hidden');pair.children.link(GUIDES);GUIDES.hide_render=True
KEYPOSES=[1,25,37,47,58,81,101,120]
def bezier_guide(name,points,rig):
    data=bpy.data.curves.new(name,'CURVE');data.dimensions='2D';data.resolution_u=8
    # Curves are actual editable native closed vectors inXY; object rotates toXZ.
    sp=data.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for bp,p in zip(sp.bezier_points,points):bp.co=(p.x,p.z,0);bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
    sp.use_cyclic_u=True;ob=bpy.data.objects.new(name,data);GUIDES.objects.link(ob);ob.parent=rig;ob.rotation_euler=(math.pi/2,0,0);ob.hide_render=True;ob.hide_viewport=True
def morph(name,verts_by_frame,faces,uvs,material,rig,bone=None,role='drawn'):
    me=bpy.data.meshes.new(name);me.from_pydata([tuple(p) for p in verts_by_frame[1]],[],faces);me.update();ob=bpy.data.objects.new(name,me);rig.users_collection[0].objects.link(ob);ob.parent=rig;me.materials.append(material)
    uv=me.uv_layers.new(name='Original painting, registered to replacement drawing')
    for lp in me.loops:uv.data[lp.index].uv=uvs[lp.vertex_index]
    ob['v007_role']=role;ob['method']='Authored curved2D replacement poses; native editable shape keys. No volume/extrusion or generated bitmap.'
    if bone:
        g=ob.vertex_groups.new(name=bone);g.add(list(range(len(me.vertices))),1,'REPLACE');mod=ob.modifiers.new('Source joint placement only','ARMATURE');mod.object=rig
    ob.shape_key_add(name='Basis')
    for f in range(1,121):
        key=ob.shape_key_add(name=f'POSE_{f:03d}');key.data.foreach_set('co',[c for p in verts_by_frame[f] for c in p])
        for frame,value in [(max(1,f-1),0),(f,1),(min(120,f+1),0)]:key.value=value;key.keyframe_insert('value',frame=frame)
    # Correct endpoint duplicate insertion; first/last key must actually hold1.
    for f in [1,120]:
        k=ob.data.shape_keys.key_blocks[f'POSE_{f:03d}'];k.value=1;k.keyframe_insert('value',frame=f)
    action=ob.data.shape_keys.animation_data.action;action.name=name+' | native drawings120F';linear(action);stash(ob.data.shape_keys,action,'V007 drawing clock')
    return ob
def qbez(a,b,c,t):return (1-t)**2*a+2*(1-t)*t*b+t*t*c
def cbez(a,b,c,d,t):return (1-t)**3*a+3*(1-t)**2*t*b+3*(1-t)*t*t*c+t**3*d
def normal(v):
    n=Vector((-v.z,0,v.x));return n.normalized() if n.length>.00001 else Vector((1,0,0))
def pxuv(p,cx):return ((p.x/(1.45/851)+cx)/1672,1-(907-p.z/(1.45/851))/941)

src=json.loads((R/'locomotion/performance_v003/art/native_overlap_sources.json').read_text());boot_openings={};boot_report=[]
# Local boot-collar pose corrections. Soles and all vertices below the ankle
# stay exactly where the sealed source puts them.
boot_report,boot_openings=acting_v007.boots(globals())

N=32;faces=[(i*2,i*2+1,i*2+3,i*2+2) for i in range(N)]
leg_report=[]
for who,rig in rigs.items():
    cx=636 if who=='BOY' else 1010
    for side in ['near','far']:
        byframe={};uvs=[];restH=rig.data.bones['thigh_'+side].head_local;restK=rig.data.bones['shin_'+side].head_local;restE=sum(boot_openings[who,side]['rest'],Vector())*.5
        for f in range(1,121):
            pp=poses[who][f];H=pp['thigh_'+side].translation;K=pp['shin_'+side].translation.copy();U,V=boot_openings[who,side][f];E=(U+V)*.5;openaxis=(V-U).normalized();enddir=normal(openaxis)
            # Draw compressed cloth/flesh inside the actual silhouette, rather
            # than following the deeply folded skeleton into a hollow loop.
            # Girl knees remain mostly concealed beneath the long source skirt.
            max_knee_x=max(H.x,E.x)+(.075 if who=='BOY' else .025)
            K.x=min(K.x,max_knee_x)
            if enddir.dot(E-K)<0:enddir=-enddir
            t1=(K-H).normalized();t2=(E-K).normalized();angle=t1.angle(t2);rounding=curveval([(1,.035),(25,.05),(37,.09),(48,.105),(60,.095),(76,.045),(120,.035)],f)
            rounding=min(rounding,(K-H).length*.35,(E-K).length*.35);B=K-t1*rounding;C=K+t2*rounding;outer=(K-(H+E)*.5).normalized()
            centers=[]
            for i in range(N+1):
                t=i/N
                if t<.35:p=H.lerp(B,t/.35)
                elif t<.65:p=qbez(B,K,C,(t-.35)/.30)+outer*(.008 if who=='BOY' else .003)*math.sin(math.pi*(t-.35)/.30)**2
                else:p=cbez(C,C+t2*(E-C).length*.35,E-enddir*.032,E,(t-.65)/.35)
                centers.append(p)
            verts=[]
            for i,p in enumerate(centers):
                t=i/N;v=centers[min(N,i+1)]-centers[max(0,i-1)];n=normal(v)
                if i==N:
                    if n.dot(openaxis)<0:openaxis=-openaxis
                    n=openaxis
                width=curveval([(0,.059 if who=='BOY' else .039),(.40,.053 if who=='BOY' else .033),(.67,.047 if who=='BOY' else .030),(1,(V-U).length*.5)],t)
                width*=1-(.20 if who=='BOY' and side=='near' else .10)*smooth(28,36,f)*(1-smooth(64,72,f))
                crease=max(0,min(1,(angle-.65)/1.7))*math.sin(math.pi*max(0,min(1,(t-.25)/.5)))**2
                for sign in [-1,1]:
                    w=width*(1-.10*crease) if (n*sign).dot(outer)<0 else width
                    point=p+n*w*sign;point.y=(-.013 if side=='near' else .023) if who=='BOY' else (.016 if side=='near' else .026);verts.append(point)
                    if f==1:
                        rr=restH.lerp(restK,t*2) if t<.5 else restK.lerp(restE,(t-.5)*2);axis=restK-restH if t<.5 else restE-restK;rp=rr+normal(axis)*width*sign
                        if who=='BOY':uvs.append(pxuv(rp,cx))
                        else:uvs.append(((913+(sign+1)*9)/1672,1-(738+t*40)/941))
            byframe[f]=verts
            if f in KEYPOSES:bezier_guide(f'POSE{1800+f} | {who} {side} rounded knee',[verts[i*2] for i in range(N+1)]+[verts[i*2+1] for i in range(N,-1,-1)],rig)
        ob=morph('V007_'+who+' | drawn leg '+side,byframe,faces,uvs,mats[who]['pants' if who=='BOY' else 'skin'],rig,role='drawn_leg');leg_report.append({'who':who,'side':side,'method':'Authored rounded knee contours and curved ankle entry; original paint UV;120native pose drawings, no armature hinge deformation'})
        for old in rig.children:
            if old==ob:continue
            if old.get('skin_region')=='leg_'+side or 'hidden thigh overlap '+side in old.name:old.hide_render=True;old.hide_viewport=True;old['superseded_by_v007']=ob.name

# Continuous drawn sleeves/forearms remove the exposed elbow hinge. Gray cuff
# band remains the original design; its outline follows the drawn curve.
for who,rig in rigs.items():
    for side in ['near','far']:
        for part in ['sleeve','skin']:
            byframe={};uvs=[];M=18;ff=[(i*2,i*2+1,i*2+3,i*2+2) for i in range(M)]
            for f in range(1,121):
                pp=poses[who][f];A=pp['upper_arm_'+side].translation if part=='sleeve' else pp['forearm_'+side].translation;B=pp['forearm_'+side].translation if part=='sleeve' else pp['hand_'+side].translation;v=B-A;n=normal(v)
                sag=(.007 if part=='sleeve' else .004)*math.sin((f-27)/17);C1=A+v*.33+n*sag;C2=A+v*.72-n*sag*.5;pts=[]
                for i in range(M+1):
                    t=i/M;p=cbez(A,C1,C2,B,t);tangent=3*(1-t)**2*(C1-A)+6*(1-t)*t*(C2-C1)+3*t*t*(B-C2);norm=normal(tangent)
                    width=curveval([(0,.041 if part=='sleeve' else .023),(.25,.048 if part=='sleeve' else .022),(1,.047 if part=='sleeve' else .018)],t)
                    for sign in [-1,1]:
                        q=p+norm*sign*width;q.y=-.037 if side=='near' else .025;pts.append(q)
                        if f==1:
                            patch=(586,330,642,428) if who=='BOY' else (1000,353,1040,409)
                            if part=='skin':patch=(492,494,506,522) if who=='BOY' else (867,497,878,520)
                            u=(sign+1)/2;uvs.append(((patch[0]+u*(patch[2]-patch[0]))/1672,1-(patch[1]+t*(patch[3]-patch[1]))/941))
                byframe[f]=pts
                if f in KEYPOSES:bezier_guide(f'POSE{1800+f} | {who} {side} {part}',[pts[i*2] for i in range(M+1)]+[pts[i*2+1] for i in range(M,-1,-1)],rig)
            ob=morph('V007_'+who+' | drawn '+part+' '+side,byframe,ff,uvs,mats[who][part],rig,role='drawn_arm')
            if part=='sleeve':
                cuffposes={f:[Vector((q.x,q.y-.001,q.z)) for q in pts[-8:]] for f,pts in byframe.items()}
                patch=(490,451,548,476) if who=='BOY' else (883,439,928,460)
                cuffuv=[((patch[0]+s*(patch[2]-patch[0]))/1672,1-(patch[1]+i/3*(patch[3]-patch[1]))/941) for i in range(4) for s in [0,1]]
                morph('V007_'+who+' | drawn source gray cuff '+side,cuffposes,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(3)],cuffuv,mats[who]['cuff'],rig,role='drawn_cuff')
            for old in rig.children:
                if old==ob:continue
                if ' | '+part+' '+side in old.name and not old.name.startswith('V007_'):old.hide_render=True;old.hide_viewport=True;old['superseded_by_v007']=ob.name

def ribbon(points,radii,depth):
    out=[]
    for i,p in enumerate(points):
        d=points[min(len(points)-1,i+1)]-points[max(0,i-1)];n=Vector((-d.y,d.x)).normalized()
        for sign in [-1,1]:out.append(Vector((p.x+n.x*radii[i]*sign,p.y+n.y*radii[i]*sign,depth)))
    return out,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(points)-1)]
def hand_drawing(curl,spread,phase):
    vertices=[];faces=[]
    palm=[(-.012,-.004),(.012,-.004),(.018,.014),(.016,.032),(.009,.038),(-.010,.036),(-.020,.025),(-.019,.010)]
    vertices.extend(Vector((x,y,0)) for x,y in palm);faces.append(tuple(range(len(palm))))
    for finger,(bx,L) in enumerate([(-.011,.030),(-.0035,.036),(.004,.033),(.0115,.025)]):
        opening=(finger-1.5)*(.045+.16*spread);delay=.03*math.sin(phase-finger*.45);c=max(0,min(1,curl+delay));ang=c*1.6
        A=Vector((bx,.030));v=Vector((math.sin(opening),math.cos(opening)));K=A+v*L*.52;tip=K+Vector((math.sin(opening+ang),math.cos(opening+ang)))*L*.48
        points=[qbez(A,K,tip,t/8) for t in range(9)];r=.0042 if finger<3 else .0036;rr=[r*(1-.60*(t/8)**5) for t in range(9)];vs,fs=ribbon(points,rr,-finger*.00015);base=len(vertices);vertices.extend(vs);faces.extend(tuple(base+i for i in face) for face in fs);faces.append((base+16,base+17,base+15,base+14))
    A=Vector((-.014,.012));K=Vector((-.027,.020));tip=Vector((-.031+.012*curl,.033-.006*curl));vs,fs=ribbon([qbez(A,K,tip,t/8) for t in range(9)],[.005*(1-.55*(t/8)**4) for t in range(9)],-.0008);base=len(vertices);vertices.extend(vs);faces.extend(tuple(base+i for i in face) for face in fs)
    return vertices,faces
hand_report=[]
for who,rig in rigs.items():
    for side in ['near','far']:
        byframe={};uvs=[];hf=None;BM=rest[who]['hand_'+side]
        for f in range(1,121):
            t=f-(2 if side=='far' else 0)-(1 if who=='GIRL' else 0);opening=curveval([(1,.12),(22,.15),(31,.75),(44,.95),(55,.55),(70,.22),(83,.10),(103,.22),(120,.13)],t)
            curl=curveval([(1,.46),(22,.42),(32,.10),(44,.16),(57,.58),(73,.50),(88,.40),(108,.28),(120,.38)],t)
            if who=='BOY' and side=='near':
                brace=smooth(38,49,f)*(1-smooth(101,115,f));curl=curl*(1-brace)+.12*brace;opening=max(opening,.55*brace)
            if (who=='BOY' and side=='far') or (who=='GIRL' and side=='near'):
                help=smooth(79 if who=='BOY' else 51,101 if who=='BOY' else 78,f);curl=curl*(1-help)+.35*help;opening=opening*(1-help)+.18*help
            points,hf=hand_drawing(curl,opening,f/11);byframe[f]=[BM@p for p in points]
            if f==1:
                patch=(479,542,503,576) if who=='BOY' else (1134,560,1157,592)
                for p in points:uvs.append(((patch[0]+max(0,min(1,(p.x+.04)/.08))*(patch[2]-patch[0]))/1672,1-(patch[1]+max(0,min(1,p.y/.08))*(patch[3]-patch[1]))/941))
        ob=morph('V007_'+who+' | articulated drawn hand '+side,byframe,hf,uvs,mats[who]['hand'],rig,'hand_'+side,'drawn_hand')
        for old in rig.children:
            if old!=ob and 'original hand '+side in old.name:old.hide_render=True;old.hide_viewport=True;old['superseded_by_v007']=ob.name
        hand_report.append({'who':who,'side':side,'method':'Native palm+four curved fingers+opposed thumb; guarded/open/curl/relax silhouette poses with staggered digits; original skin paint'})

# Body volume/tail breathing is drawn in the garment as well as keyed in the
# upper skeleton. The pelvis, legs and boot sole trajectories remain untouched.
for who,rig in rigs.items():
    body=next(o for o in rig.children if o.get('skin_region') in ['body','dress']);body.shape_key_add(name='Basis');breathe=body.shape_key_add(name='Living chest and cloth');tail=body.shape_key_add(name='Settling hem')
    for i,v in enumerate(body.data.vertices):
        weight=max(0,1-abs(v.co.z-.90)/.20);breathe.data[i].co.x+=v.co.x*.026*weight;breathe.data[i].co.z+=.0025*weight
        hem=max(0,min(1,(.77-v.co.z)/.20));tail.data[i].co.x+=.004*hem
    for f in range(1,121):
        env=smooth(110,120,f);breathe.value=env*.5*(1+math.sin((f-86)*math.tau/84));tail.value=env*math.sin((f-80)/12)*.65
        breathe.keyframe_insert('value',frame=f);tail.keyframe_insert('value',frame=f)
    action=body.data.shape_keys.animation_data.action;action.name='V007_'+who+' | drawn breathing and hem120F';linear(action);stash(body.data.shape_keys,action,'V007 breathing clock')

configure=runpy.run_path(str(P/'scripts/configure_v007.py'))['configure_v007'];configure(start=1801,root_motion=False,root=root)
protected_error=0;distance_error=0;settle_displacement=[]
for f in range(1,121):
    S.frame_set(1800+f);bpy.context.view_layer.update();distance_error=max(distance_error,abs(distance.location.x-D[f-1]))
    for who,rig in rigs.items():
        for name in ['foot_near','foot_far']:
            protected_error=max(protected_error,max(abs(rig.pose.bones[name].matrix[i][j]-baseline[who][f][name][i][j]) for i in range(4) for j in range(4)))
        if f>=81:settle_displacement.append((rig.pose.bones['head'].head-baseline[who][f]['head'].translation).length)
assert protected_error<.00001 and distance_error<.00001,(protected_error,distance_error)
configure(start=1,root_motion=False,root=root);S.name='V007 | supported recovery and distinct acting';S.frame_start=1;S.frame_end=120
S.objects['LOCO | title'].data.body='WHEN THE SKY CLEARS / SPECIALIST CORRECTIONS v007';S.objects['LOCO | clip label'].data.body='STAGGERED SUPPORT / GIRL CHECKS BOY / SUPPORTED RISE /75-80s /24FPS'
for t in list(bpy.data.texts):bpy.data.texts.remove(t)
t=bpy.data.texts.new('configure_v007.py');t.write((P/'scripts/configure_v007.py').read_text())
glance_report=acting_v007.glance(globals())
(P/'evidence/glance_method.json').write_text(json.dumps(glance_report,indent=2))
S.render.engine='BLENDER_EEVEE'
S.frame_set(1);out=P/'native/WTSC_Supported_Recovery_v007.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
report={'source':str(BASE),'source_sha256':base_hash,'source_preserved':hashlib.sha256(BASE.read_bytes()).hexdigest()==base_hash,'native':str(out),'native_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'frames':120,'fps':24,'root_distance_m':D[-1],'protected_foot_matrix_max_error':protected_error,'root_distance_max_error':distance_error,'settle_head_delta_range_m':[min(settle_displacement),max(settle_displacement)],'leg_drawings':leg_report,'hand_drawings':hand_report,'boot_collars':boot_report,'native_actions':len(bpy.data.actions),'guides':len(GUIDES.objects),'method':'Localized authored2D silhouette replacement poses, native mesh shape keys and editable closed Bezier guides. Original face/body/paint retained; no bitmap generation, no volumetric character model.','limits':'Artist review required. New limb/finger edge artwork must be judged in actual integrated framing; no cinematic acceptance from protected-contact checks.'}
(P/'evidence/build_validation.json').write_text(json.dumps(report,indent=2));print('V007_DRAWN_CORRECTIONS_BUILT',json.dumps(report),flush=True)
