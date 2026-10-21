"""Isolated v027 loading and passive coat response. No production writes.
Run using verified Blender 5.2.2 LTS, background, threads 2.
"""
import bpy,sys,math,json,csv,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'))
import loading_model as M
import rig_pose_api as api
SOURCE=P/'reference/PRESERVED_BASELINE_v026.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
S=bpy.context.scene;rigs,C=api.initialize_from_scene();rig=rigs['BOY'];T=rig.parent
coat=bpy.data.objects['V025 | COAT drawings | editable GP'];layer=coat.data.layers[0]
names=['HIP','CHEST','HEAD_PROFILE','WRIST_near','WRIST_far','ARM_POLE_near','ARM_POLE_far','LEG_POLE_near','LEG_POLE_far']
pants={s:bpy.data.objects['V024 continuous '+s+' trouser drawing'] for s in ['near','far']}
boots={s:bpy.data.objects['V007_BOY | redrawn support boot '+s] for s in ['near','far']}
def frame(f):S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
def worldbone(n,end='head'):return rig.matrix_world@getattr(rig.pose.bones[n],end)
def meshpts(o):
    e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [e.matrix_world@v.co for v in e.data.vertices]
def curves(id):
    if not id.animation_data or not id.animation_data.action:return
    for l in id.animation_data.action.layers:
        for st in l.strips:
            for bag in st.channelbags:yield from bag.fcurves
def linear_repeat(o):
    for fc in curves(o):
        for k in fc.keyframe_points:k.interpolation='LINEAR'
        c=next((m for m in fc.modifiers if m.type=='CYCLES'),None) or fc.modifiers.new('CYCLES');c.mode_before=c.mode_after='REPEAT'

# Capture immutable source evaluations before detaching edited actions.
old={}
for i in range(125):
    f=1+i/4;frame(f);h=worldbone('pelvis');ch=worldbone('chest','tail')
    old[f]={'H':h.copy(),'Hlocal':rig.pose.bones['pelvis'].head.copy(),'a':math.atan2(ch.x-h.x,ch.z-h.z),'sternum_z':ch.z,'C':{n:C['BOY',n].matrix_world.copy() for n in names},
            'boot':{s:meshpts(o) for s,o in boots.items()},'K':{s:rig.pose.bones['shin_'+s].head.copy() for s in pants},
            'goal':{s:bpy.data.objects['V020 | '+s+' | SOLE_BONE_GOAL'].matrix_world.copy() for s in pants}}
oldverts={s:[[v.co.copy() for v in k.data] for k in o.data.shape_keys.key_blocks] for s,o in pants.items()}
frame(1);H=rig.pose.bones['pelvis'].head.copy();a=old[1.]['a'];R=Matrix.Rotation(-a,4,'Y')
template=next(fr for fr in layer.frames if fr.frame_number==1).drawing
styles=[];points=[];counts=[]
for st in template.strokes:
    styles.append({k:(tuple(st.fill_color) if k=='fill_color' else getattr(st,k)) for k in ['material_index','fill_id','cyclic','hide_stroke','softness','fill_opacity','fill_color']})
    counts.append(len(st.points));points.append([(R@(p.position-H),p.radius,p.opacity,tuple(p.vertex_color)) for p in st.points])
original_head_hash=hashlib.sha256(bytes(str([(tuple(v.co)) for v in bpy.data.objects['PERF_BOY | original head'].data.vertices]),'utf8')).hexdigest()
for n in names:
    ob=C['BOY',n]
    if ob.animation_data:
        ob.animation_data.action=None
        for track in list(ob.animation_data.nla_tracks):ob.animation_data.nla_tracks.remove(track)

new={};checks=[]
for i in range(125):
    f=1+i/4;q=f-1;frame(f);r=M.evaluate(q);src=old[f];newH=Vector((r['H'][0],src['H'].y,r['H'][1]));dH=newH-src['H']
    U=Matrix.Translation((r['upper_origin'][0],src['H'].y,r['upper_origin'][1]))@Matrix.Rotation(r['chest']-src['a'],4,'Y')@Matrix.Translation(-src['H'])
    C['BOY','HIP'].matrix_world=Matrix.Translation(dH)@src['C']['HIP'];bpy.context.view_layer.update()
    C['BOY','CHEST'].matrix_world=U@src['C']['CHEST'];bpy.context.view_layer.update()
    # Retain the original painted profile/gaze angle; translate with neck attachment.
    hm=src['C']['HEAD_PROFILE'].copy();hm.translation=U@hm.translation;C['BOY','HEAD_PROFILE'].matrix_world=hm
    for n in ['WRIST_near','WRIST_far','ARM_POLE_near','ARM_POLE_far']:C['BOY',n].matrix_world=U@src['C'][n]
    bpy.context.view_layer.update()
    for s in pants:
        hip=worldbone('thigh_'+s);A=C['BOY','ANKLE_'+s].matrix_world.translation;_,K,_=M.B.M.ik(M.np.array([hip.x,hip.z]),M.np.array([A.x,A.z]),s)
        knee=Vector((K[0],hip.y,K[1]));C['BOY','LEG_POLE_'+s].matrix_world=Matrix.Translation(knee+(knee-(hip+A)*.5)*4)
    bpy.context.view_layer.update()
    for n in names:
        ob=C['BOY',n];ob.rotation_mode='QUATERNION'
        for field in ['location','rotation_quaternion','scale']:ob.keyframe_insert(field,frame=f)
    h=worldbone('pelvis');ch=worldbone('chest','tail');new[f]={'H':h.copy(),'Hlocal':rig.pose.bones['pelvis'].head.copy(),'K':{s:rig.pose.bones['shin_'+s].head.copy() for s in pants},'chest':ch.copy(),'chest_head':worldbone('chest')}
    err=max((x-y).length for s,o in boots.items() for x,y in zip(src['boot'][s],meshpts(o)))
    goalerr=max(abs(src['goal'][s][i][j]-bpy.data.objects['V020 | '+s+' | SOLE_BONE_GOAL'].matrix_world[i][j]) for s in pants for i in range(4) for j in range(4))
    bad=[x for x in api.reach_report() if not x['reachable']]
    checks.append({'frame':f,'body_x_relative_root_m':h.x-T.location.x,'pelvis_z_m':h.z,'sternum_z_m':ch.z,'baseline_sternum_z_m':src['sternum_z'],'chest_degrees':math.degrees(r['chest']),'upper_origin_offset_m':r['upper_origin'][1]-r['H'][1],'max_boot_change_m':err,'max_goal_matrix_change':goalerr,'unreachable':bad})
for n in names:linear_repeat(C['BOY',n]);C['BOY',n].animation_data.action.name='V027 | authored loading | '+n

def hermite(A,B,mA,mB,t):return (2*t**3-3*t*t+1)*A+(t**3-2*t*t+t)*mA+(-2*t**3+3*t*t)*B+(t**3-t*t)*mB
def center(H,K,E,t):
    u=(K-H).normalized();v=(E-K).normalized();mid=(u+v).normalized();l1=(K-H).length;l2=(E-K).length
    return hermite(H,K,u*l1,mid*l1,t/.58) if t<=.58 else hermite(K,E,mid*l2,v*l2,(t-.58)/.42)
def tangent(H,K,E,t):return (center(H,K,E,min(1,t+.002))-center(H,K,E,max(0,t-.002))).normalized()
cuff_error=0.
for s,o in pants.items():
    for j,kb in enumerate(o.data.shape_keys.key_blocks):
        f=float(j+1);v=oldverts[s][j];H=(v[0]+v[6])*.5;E=(v[-7]+v[-1])*.5;K=old[f]['K'][s];K.y=H.y
        Hn=H+new[f]['Hlocal']-old[f]['Hlocal'];Kn=new[f]['K'][s].copy();Kn.y=H.y
        arr=[]
        for row in range(97):
            t=row/96;co=center(H,K,E,t);cn=center(Hn,Kn,E,t);to=tangent(H,K,E,t);tn=tangent(Hn,Kn,E,t);no=Vector((-to.z,0,to.x));nn=Vector((-tn.z,0,tn.x))
            for col in range(7):
                p=v[row*7+col];d=p-co;nv=cn+tn*d.dot(to)+nn*d.dot(no)+Vector((0,d.y,0))
                cuff=max(0,min(1,(1-t)/.08));cuff=cuff*cuff*(3-2*cuff);arr.append(p+(nv-p)*cuff)
        kb.data.foreach_set('co',[x for vtx in arr for x in vtx])
        if j==0:o.data.vertices.foreach_set('co',[x for vtx in arr for x in vtx])
        cuff_error=max(cuff_error,max((a-b).length for a,b in zip(arr[-7:],v[-7:])))
    o.data.update();o['V027_fit']='Same UVs, rolled-cuff cross-sections and fixed boot collar; centerline re-fitted to authored hip/knee, 31 cyclic pose samples'

# Replace phase-authored flares with a settled follower of the actual trunk.
# Retain one accepted design template, all materials, marks and point styles.
for fr in list(layer.frames):layer.frames.remove(fr.frame_number)
cloth=[]
for f in range(1,32):
    frame(f);q=f-1;r=M.evaluate(q);H=new[float(f)]['Hlocal'];a=r['chest'];lag=M.cloth_response(q);delta=r['upper_origin'][1]-r['H'][1];d=layer.frames.new(f).drawing;d.add_strokes(counts)
    for st,attrs,pts in zip(d.strokes,styles,points):
        for k,v in attrs.items():setattr(st,k,v)
        for pt,(v,radius,opacity,color) in zip(st.points,pts):
            t=max(0,min(1,v.z/.49));attach=t*t*(3-2*t);free=max(0,min(1,(.32-v.z)/.28));free=free*free*(3-2*free)
            pivot=Vector((0,0,.23));vv=pivot+Matrix.Rotation(lag*free,4,'Y')@(v-pivot)
            # Compression is inherited from the torso's measured attachment lag.
            p=H+Matrix.Rotation(a,4,'Y')@vv;p.z+=delta*attach
            pt.position=p;pt.radius=radius;pt.opacity=opacity;pt.vertex_color=color
    d.tag_positions_changed();cloth.append({'frame':f,'body_degrees':math.degrees(a),'passive_hem_lag_degrees':math.degrees(lag),'upper_attachment_offset_m':delta})
layer.frames.copy(1,32,instance_drawing=True)
for f in range(33,281):layer.frames.copy(1+(f-1)%31,f,instance_drawing=True)
coat['V027_response']='Single preserved coat design; lower hem is a damped follower driven solely by actual torso angle. Upper points follow actual trunk compression. No separately keyed flap or new texture.'
coat['V027_follower']='240Hz; omega15rad/s; damping.84; twelve cycles of warmup; per-output-frame drawings on ones'

# Source captures remain the evidence for unchanged contacts; sample the saved cyclic result too.
cyclic=[]
for f in [32.,63.,94.,125.,156.,187.,218.,249.,280.]:
    frame(f);cyclic.append({'frame':f,'hip_x_relative_root_m':worldbone('pelvis').x-T.location.x,'hip_z_m':worldbone('pelvis').z,'unreachable':[x for x in api.reach_report() if not x['reachable']]})
report={'scope':'Technical support verification only. Not an artistic pass.','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'two_visible_causes':['Upper body stays columnar while centered hip resets backward late in the cycle','Coat flare/tuck keyed by phase rather than responding to trunk loading'],
        'changes':['Authored smooth asymmetric hip X spacing and compressed rise/recovery, without changing sole goals or root','Forward trunk loading and delayed upper mass; original gaze orientation retained','Painted trouser centerlines refitted with fixed cuffs and UVs','Passive damped coat hem driven by trunk, retaining a single accepted design template'],
        'native_version':bpy.app.version_string,'body_samples':checks,'late_cycle_checks':cyclic,'cloth_response':cloth,'maximum_boot_change_m':max(x['max_boot_change_m'] for x in checks),'maximum_goal_matrix_change':max(x['max_goal_matrix_change'] for x in checks),'maximum_cuff_row_change_m':cuff_error,
        'unreachable_samples':[x for x in checks if x['unreachable']],'original_head_mesh_unchanged':original_head_hash==hashlib.sha256(bytes(str([tuple(v.co) for v in bpy.data.objects['PERF_BOY | original head'].data.vertices]),'utf8')).hexdigest(),
        'integration':{'period_frames':31,'fps':30,'stride_m':M.STRIDE,'root':'D=.9524437384576381*(F-1)/31 metres +X; native unwrapped travel','footfall_timing_changed':False,'root_or_sole_trajectory_changed':False,'near_contact_frame':1,'far_contact_frame':17,'not_complete_paired_recovery_scene':True}}
(P/'evidence/LOADING_AND_CONTACT_CHECKS.json').write_text(json.dumps(report,indent=2))
assert report['maximum_boot_change_m']<.00002 and report['maximum_goal_matrix_change']<.00002 and cuff_error<.00002 and not report['unreachable_samples'] and all(not x['unreachable'] for x in cyclic)
assert report['original_head_mesh_unchanged']
with (P/'evidence/BODY_SPACING_AND_RESPONSE.csv').open('w',newline='') as out:
    fields=[k for k in checks[0] if k!='unreachable'];w=csv.DictWriter(out,fieldnames=fields);w.writeheader();w.writerows({k:r[k] for k in fields} for r in checks)
S.frame_start=1;S.frame_end=279;S.render.fps=30;S['V027_status']='Focused whole-body loading and passive coat proof. ART REVIEW OPEN. v026 preserved.'
S['V027_travel_contract']='Same v026 root/sole curves;31frames30fps;.9524437384576381m +X per cycle. New body pose and trouser drawings must be imported together.'
S['V027_head_choice']='Original painted side profile/gaze orientation maintained; head translates through neck attachment. No turnaround/card rotation or v008 reuse.'
frame(4);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=360;S.render.resolution_y=540;S.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Body_Loading_Overlap_v027.blend'),compress=True)
print('V027_NATIVE_BUILT',json.dumps({k:v for k,v in report.items() if k not in ['body_samples','late_cycle_checks','cloth_response','unreachable_samples']}),flush=True)
