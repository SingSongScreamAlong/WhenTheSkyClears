"""Native isolated v028: trunk bend beneath preserved head; authored arm succession.
One coherent pose pass, retaining v027 root/feet/pelvis/trousers/head actions.
"""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import upper_body_model as M;import rig_pose_api as api
SOURCE=P/'reference/PRESERVED_BASELINE_v027.blend';bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
S=bpy.context.scene;rigs,C=api.initialize_from_scene();rig=rigs['BOY'];T=rig.parent;rest=rig.data.bones
coat=bpy.data.objects['V025 | COAT drawings | editable GP'];layer=coat.data.layers[0];edit=['CHEST','HEAD_PROFILE','WRIST_near','WRIST_far','ARM_POLE_near','ARM_POLE_far']
preserved=[bpy.data.objects[n] for n in ['PERF_BOY | original head','V007_BOY | redrawn support boot near','V007_BOY | redrawn support boot far','V024 continuous near trouser drawing','V024 continuous far trouser drawing']]
def frame(f):S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update()
def pts(o):
    view=S.view_layers['V025 | original foreground'] if o.name=='PERF_BOY | original head' else bpy.context.view_layer
    view.update();e=o.evaluated_get(view.depsgraph);return [e.matrix_world@v.co for v in e.data.vertices]
def curves(o):
    if o.animation_data and o.animation_data.action:
        for l in o.animation_data.action.layers:
            for st in l.strips:
                for bag in st.channelbags:yield from bag.fcurves
def repeat(o):
    for fc in curves(o):
        for k in fc.keyframe_points:k.interpolation='LINEAR'
        c=next((m for m in fc.modifiers if m.type=='CYCLES'),None) or fc.modifiers.new('CYCLES');c.mode_before=c.mode_after='REPEAT'
old={};drawings={};styles=None;counts=None
for i in range(125):
    f=1+i/4;frame(f);old[f]={'controls':{n:C['BOY',n].matrix_world.copy() for n in edit},'neck':rig.matrix_world@rig.pose.bones['chest'].tail,'H':rig.matrix_world@rig.pose.bones['pelvis'].head,'root':T.matrix_world.copy(),'head_control':C['BOY','HEAD_PROFILE'].matrix_world.copy(),'meshes':{o.name:pts(o) for o in preserved}}
    if f==int(f) and f<=31:
        d=next(fr for fr in layer.frames if fr.frame_number==f).drawing
        if styles is None:
            styles=[{k:(tuple(st.fill_color) if k=='fill_color' else getattr(st,k)) for k in ['material_index','fill_id','cyclic','hide_stroke','softness','fill_opacity','fill_color']} for st in d.strokes];counts=[len(st.points) for st in d.strokes]
        drawings[int(f)]=[[(p.position.copy(),p.radius,p.opacity,tuple(p.vertex_color)) for p in st.points] for st in d.strokes]
for n in edit:
    o=C['BOY',n]
    if o.animation_data:
        o.animation_data.action=None
        for tr in list(o.animation_data.nla_tracks):o.animation_data.nla_tracks.remove(tr)
rows=[]
for i in range(125):
    f=1+i/4;q=f-1;frame(f);src=old[f];a=M.trunk_delta(q);U=Matrix.Translation(src['neck'])@Matrix.Rotation(a,4,'Y')@Matrix.Translation(-src['neck'])
    C['BOY','CHEST'].matrix_world=U@src['controls']['CHEST'];bpy.context.view_layer.update()
    # HEAD_PROFILE is parented to CHEST. Compensate its local keys so its world
    # motion remains the baseline's, rather than inheriting the trunk correction.
    C['BOY','HEAD_PROFILE'].matrix_world=src['head_control'];bpy.context.view_layer.update();armrow={}
    for side in ['near','far']:
        shoulder=rig.matrix_world@rig.pose.bones['upper_arm_'+side].head;upper,lower,hand=M.arm(side,q);u=Vector((math.sin(upper),0,-math.cos(upper)));v=Vector((math.sin(lower),0,-math.cos(lower)));E=shoulder+u*rest['upper_arm_'+side].length;W=E+v*rest['forearm_'+side].length
        hd=Vector((math.sin(hand),0,-math.cos(hand)));rd=rest['hand_'+side].tail_local-rest['hand_'+side].head_local;rot=math.atan2(hd.x,hd.z)-math.atan2(rd.x,rd.z)
        C['BOY','WRIST_'+side].matrix_world=Matrix.Translation(W)@Matrix.Rotation(rot,4,'Y')@rest['hand_'+side].matrix_local.to_3x3().to_4x4()
        C['BOY','ARM_POLE_'+side].matrix_world=Matrix.Translation(E+(E-(shoulder+W)*.5)*4)
        armrow[side]={'upper_degrees':math.degrees(upper),'forearm_degrees':math.degrees(lower),'hand_degrees':math.degrees(hand),'wrist_world':list(W),'elbow_world':list(E)}
    bpy.context.view_layer.update()
    for n in edit:
        ob=C['BOY',n];ob.rotation_mode='QUATERNION'
        for p in ['location','rotation_quaternion','scale']:ob.keyframe_insert(p,frame=f)
    errors={o.name:max((v-w).length for v,w in zip(src['meshes'][o.name],pts(o))) for o in preserved}
    rooterr=max(abs(src['root'][a][b]-T.matrix_world[a][b]) for a in range(4) for b in range(4));headerr=max(abs(src['head_control'][a][b]-C['BOY','HEAD_PROFILE'].matrix_world[a][b]) for a in range(4) for b in range(4));bad=[r for r in api.reach_report() if not r['reachable']]
    rows.append({'frame':f,'trunk_delta_degrees':math.degrees(a),'arms':armrow,'preserved_mesh_errors_m':errors,'root_matrix_error':rooterr,'head_control_matrix_error':headerr,'unreachable':bad})
for n in edit:repeat(C['BOY',n]);C['BOY',n].animation_data.action.name='V028 | upper-body succession | '+n

# Deform the existing v027 drawings, preserving their materials/marks and base response.
# Upper attachment follows the new chest; waist compression derives from its bend.
for fr in list(layer.frames):layer.frames.remove(fr.frame_number)
coatrows=[]
for f in range(1,32):
    frame(f);q=f-1;src=old[float(f)];a=M.trunk_delta(q);U=Matrix.Translation(src['neck'])@Matrix.Rotation(a,4,'Y')@Matrix.Translation(-src['neck']);lag=M.extra_hem_lag(q);compress=max(0,-a/math.radians(1.6));H=src['H'];W=coat.matrix_world.copy();inv=W.inverted();d=layer.frames.new(f).drawing;d.add_strokes(counts)
    for st,attrs,ps in zip(d.strokes,styles,drawings[f]):
        for k,v in attrs.items():setattr(st,k,v)
        for point,(v,radius,opacity,color) in zip(st.points,ps):
            p=W@v;z=p.z-H.z;t=max(0,min(1,(z-.04)/.38));attach=t*t*(3-2*t);p+=(U@p-p)*attach
            waist=math.exp(-((z-.18)/.105)**2);p.x+=.004*compress*waist;p.z-=.005*compress*waist
            free=max(0,min(1,(.29-z)/.25));free=free*free*(3-2*free);pivot=H+Vector((0,0,.23));p=pivot+Matrix.Rotation(lag*free*.8,4,'Y')@(p-pivot)
            point.position=inv@p;point.radius=radius;point.opacity=opacity;point.vertex_color=color
    d.tag_positions_changed();coatrows.append({'frame':f,'compression_from_trunk_bend':compress,'extra_passive_hem_lag_degrees':math.degrees(lag)*.8})
layer.frames.copy(1,32,instance_drawing=True)
for f in range(33,281):layer.frames.copy(1+(f-1)%31,f,instance_drawing=True)
coat['V028_response']='Preserved v027 design/materials; upper attachment follows restrained trunk bend, waist compresses <=5mm from that bend, extra damped hem response only. No independently timed flare or texture pass.'
late=[]
for f in [32.,63.,94.,125.,156.,187.,218.,249.,280.]:
    frame(f);late.append({'frame':f,'unreachable':[r for r in api.reach_report() if not r['reachable']]})
report={'scope':'Technical safeguards, not artistic acceptance','native_version':bpy.app.version_string,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'changed_control_names':edit,'head_choice':'v027 head control, mesh and world motion preserved exactly; trunk pivots beneath neck','root_feet_pelvis_trousers_actions_changed':False,'quarter_frame_samples':rows,'late_cycles':late,'coat_derivation':coatrows,'max_preserved_mesh_error_m':max(v for r in rows for v in r['preserved_mesh_errors_m'].values()),'max_root_matrix_error':max(r['root_matrix_error'] for r in rows),'max_head_control_matrix_error':max(r['head_control_matrix_error'] for r in rows),'unreachable_samples':[r for r in rows if r['unreachable']]}
(P/'evidence/UPPER_BODY_AND_PRESERVATION_CHECKS.json').write_text(json.dumps(report,indent=2))
assert report['max_preserved_mesh_error_m']<.00002 and report['max_root_matrix_error']<.00002 and report['max_head_control_matrix_error']<.00002 and not report['unreachable_samples'] and all(not r['unreachable'] for r in late)
S['V028_status']='Focused trunk/arm pose refinement. Isolated comparison; ART REVIEW OPEN. v027 root/feet/pelvis/head preserved.';S['V028_arms']='Individually authored near/far upper-arm directions and flex; forearm reversal delays1.5/1frames, hand delays.75/.5frames. Fixed-length native IK, original painted hands retained.'
S.frame_start=1;S.frame_end=279;S.render.fps=30;frame(5);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=360;S.render.resolution_y=540;S.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Upper_Body_Pose_Refinement_v028.blend'),compress=True)
print('V028_NATIVE_BUILT',json.dumps({k:v for k,v in report.items() if k not in ['quarter_frame_samples','coat_derivation','unreachable_samples','late_cycles']}),flush=True)
