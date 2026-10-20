"""Preserve the promisingv025 half-step and complete its opposite half for long review.
Nine31frame cycles, unwrapped travel; original v024 body/support, no v025b experiments.
"""
import bpy,json,math,hashlib,sys
import numpy as np
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];sys.path.insert(0,str(P/'scripts'));import rig_pose_api as api
SOURCE=P/'reference/PRESERVED_PROMISING_GP_v025.blend';bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False);S=bpy.context.scene;rigs,controls=api.initialize_from_scene();rig=rigs['BOY'];T=rig.parent;coat=bpy.data.objects['V025 | COAT drawings | editable GP'];layer=coat.data.layers[0];STRIDE=.9524437384576381
def pose(f):
    S.frame_set(int(f),subframe=f-int(f));bpy.context.view_layer.update();H=rig.pose.bones['pelvis'].head.copy();C=rig.pose.bones['chest'].tail;return H,math.atan2(C.x-H.x,C.z-H.z)
def curves(action):
    for l in action.layers:
        for s in l.strips:
            for bag in s.channelbags:yield from bag.fcurves
def style(s):return {k:getattr(s,k) for k in ['material_index','fill_id','cyclic','hide_stroke','softness','fill_opacity','fill_color']}
templates={};oldraw={};styles=None;counts=None;radius=None
for fr in layer.frames:
    f=fr.frame_number;H,a=pose(f);c=math.cos(a);s=math.sin(a);coords=[];opacity=[];radii=[];raw=[]
    if styles is None:styles=[style(st) for st in fr.drawing.strokes];counts=[len(st.points) for st in fr.drawing.strokes]
    for st in fr.drawing.strokes:
        for point in st.points:
            v=point.position;dx=v.x-H.x;dz=v.z-H.z;coords.append((c*dx-s*dz,v.y,s*dx+c*dz));opacity.append(point.opacity);radii.append(point.radius);raw.append(list(v))
    templates[f]=(np.asarray(coords),np.asarray(opacity));oldraw[f]=raw;radius=radii
# New first-half cloth extremes are offset from body keys. ExistingF17..32 remain untouched.
keys=[1.,4.25,6.,9.4,11.3,14.,17.];sourcekeys=[32,20,22,25,27,29,17]
def value(f,component):
    A=[templates[i][component] for i in sourcekeys];i=min(len(keys)-2,next((j for j in range(len(keys)-1) if f<=keys[j+1]),len(keys)-2));a=keys[i];b=keys[i+1];t=(f-a)/(b-a)
    m0=(A[i+1]-A[max(0,i-1)])/(keys[i+1]-keys[max(0,i-1)]) if i else (A[1]-A[0])/(keys[1]-keys[0])
    m1=(A[min(len(A)-1,i+2)]-A[i])/(keys[min(len(A)-1,i+2)]-keys[i])
    return (2*t**3-3*t*t+1)*A[i]+(t**3-2*t*t+t)*(b-a)*m0+(-2*t**3+3*t*t)*A[i+1]+(t**3-t*t)*(b-a)*m1
for f in range(1,17):
    H,a=pose(f);V=value(f,0);op=np.clip(value(f,1),0,1);c=math.cos(a);s=math.sin(a);d=layer.frames.new(f).drawing;d.add_strokes(counts);j=0
    for st,attrs in zip(d.strokes,styles):
        for k,v in attrs.items():setattr(st,k,v)
        for point in st.points:
            x,y,z=V[j];point.position=(H.x+c*x+s*z,y,H.z-s*x+c*z);point.opacity=float(op[j]);point.radius=radius[j];j+=1
    d.tag_positions_changed()
# Reuse drawings as native instances. Frame32 is the preservedRcontact bookend, not an extra output sample.
for f in range(33,281):layer.frames.copy(1+(f-1)%31,f,instance_drawing=True)
offset_names={T.name,'V020 | near | SOLE_BONE_GOAL','V020 | far | SOLE_BONE_GOAL'};modified=[];seen=set()
for o in S.objects:
    if not o.animation_data or not o.animation_data.action:continue
    action=o.animation_data.action
    for fc in curves(action):
        ident=fc.as_pointer()
        if ident in seen:continue
        seen.add(ident)
        if not fc.keyframe_points:continue
        cycle=next((m for m in fc.modifiers if m.type=='CYCLES'),None) or fc.modifiers.new('CYCLES')
        offset=o.name in offset_names and fc.data_path=='location' and fc.array_index==0
        cycle.mode_before=cycle.mode_after='REPEAT_OFFSET' if offset else 'REPEAT'
    modified.append({'object':o.name,'action':action.name,'travel_offset_x':o.name in offset_names})
def meshpts(name):
    o=bpy.data.objects[name];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());return [e.matrix_world@v.co for v in e.data.vertices]
boots={'near':'V007_BOY | redrawn support boot near','far':'V007_BOY | redrawn support boot far'};cache={};maxrepeat=0;minsole=1;maxroot=0;bad=[]
for i in range(124):
    f=1+i/4;pose(f);cache[round(f,4)]={s:meshpts(n) for s,n in boots.items()}
testframes=sorted(set([1+i/4 for i in range(124)]+[249+i/4 for i in range(124)]+[1+31*n+p for n in range(9) for p in [0,2.25,8,16,18.25,24.25,30]]+[280]))
for f in testframes:
    pose(f);q=f-1;n=math.floor(q/31);phase=round(1+q%31,4);maxroot=max(maxroot,abs(T.location.x-STRIDE*q/31))
    for side,name in boots.items():
        V=meshpts(name);minsole=min(minsole,min(v.z for v in V));maxrepeat=max(maxrepeat,max((a+Vector((n*STRIDE,0,0))-b).length for a,b in zip(cache[phase][side],V)))
    if f==int(f) or q%31 in [0,2.25,18.25]:bad.extend({'frame':f,**r} for r in api.reach_report() if not r['reachable'])
preserved=True
for f,raw in oldraw.items():
    fr=next(x for x in layer.frames if x.frame_number==f);now=[list(p.position) for st in fr.drawing.strokes for p in st.points];preserved=preserved and raw==now
f1=next(x for x in layer.frames if x.frame_number==1);f32=next(x for x in layer.frames if x.frame_number==32);gpjoin=max((a.position-b.position).length for sa,sb in zip(f1.drawing.strokes,f32.drawing.strokes) for a,b in zip(sa.points,sb.points))
report={'period_frames':31,'fps':30,'cycles':9,'frames_per_view':279,'seconds_per_view':9.3,'frames_encoded_per_cycle':31,'duplicate_boundary_frame_inserted':False,'preserved_v025_frames_17_32_exact':preserved,'newly_authored_opposite_half_frames':[1,16],'opposite_half_shape_keys':keys,'opposite_half_reference_drawings':sourcekeys,'GP_frames':len(layer.frames),'unique_GP_drawings':len({fr.drawing.as_pointer() for fr in layer.frames}),'GP_Rcontact_bookend_error_m':gpjoin,'sampled_native_frames':len(testframes),'max_root_curve_error_m':maxroot,'max_sole_repeat_translation_error_m':maxrepeat,'minimum_sole_z_m':minsole,'unreachable_chains':bad,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'action_extensions':modified,'upper_loading_and_pigment_experiments_included':False,'scope':'Technical continuity and source preservation only; artistic acceptance requires normal-speed review'}
assert preserved and gpjoin<.00001 and maxroot<.00002 and maxrepeat<.00002 and minsole>-.0001 and not bad
S.frame_start=1;S.frame_end=279;S.render.fps=30;S['V026_status']='Extended viewing proof requested byConrad; originalv025 preserved.9repeated31frame cycles. ART OPEN';S['V026_travel']='D=.9524437384576381*(F-1)/31m; unwrapped; root and sole goals repeat with offset';S['V026_GP_scope']='OriginalF17-32exact; opposite halfF1-16authored/re-registered; native drawing instances; no additional pose inserted at boundaries';S.frame_set(1);S.camera=bpy.data.objects['V024 | CLOSE portrait'];S.render.resolution_x=360;S.render.resolution_y=540
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_GP_Extended_Review_v026.blend'),compress=True);(P/'evidence/FULL_CYCLE_AND_TRAVEL_CHECK.json').write_text(json.dumps(report,indent=2));print('V026_NATIVE_CHECK',json.dumps({k:v for k,v in report.items() if k not in ['action_extensions','unreachable_chains']}),flush=True)
D=P/'previews/PROOF';D.mkdir(exist_ok=True)
for f in range(1,33):S.frame_set(f);S.render.filepath=str(D/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
print('V026_ONE_CYCLE_JOIN_PROOF_COMPLETE',flush=True)
