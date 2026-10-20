"""Brief native neck-pitch response on the retimed v060 world shot.

apply(scene, rigs, event, G0=937, G1=1056) works in memory only. It copies
the two rig actions and changes only the head transform channels. No
new face, eye drawing, head turn, root, limb or camera motion is authored.
"""
import bpy
import math
import json
import hashlib
from mathutils import Matrix

_HEAD_PROPS = frozenset(('location','rotation_quaternion','rotation_euler',
                         'rotation_axis_angle','scale'))


def _selected(path):
    prefix = 'pose.bones["head"].'
    return path.startswith(prefix) and path[len(prefix):] in _HEAD_PROPS


def _curves(action):
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    yield bag, curve


def _nonhead_hash(action):
    rows = []
    for _, fc in _curves(action):
        if _selected(fc.data_path):
            continue
        rows.append((fc.data_path, fc.array_index, fc.extrapolation,
            [(tuple(k.co),k.interpolation) for k in fc.keyframe_points],
            [(m.type,getattr(m,'mode_before',None),getattr(m,'mode_after',None))
             for m in fc.modifiers]))
    return hashlib.sha256(repr(rows).encode()).hexdigest()


def _frame(scene, frame):
    scene.frame_set(int(frame),subframe=frame-int(frame))
    bpy.context.view_layer.update()


def _ease(u):
    u = max(0.0,min(1.0,float(u)))
    return u*u*u*(u*(u*6.0-15.0)+10.0)


def _pitch(frame, peak_degrees, zero, peak_start, peak_end, release):
    if frame <= zero or frame >= release:
        return 0.0
    if frame < peak_start:
        return peak_degrees*_ease((frame-zero)/(peak_start-zero))
    if frame <= peak_end:
        return peak_degrees
    return peak_degrees*(1.0-_ease((frame-peak_end)/(release-peak_end)))


def _mat_error(a,b):
    return max(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4))


def apply(scene, rigs, event, G0=937, G1=1056):
    if G1 <= G0:
        raise RuntimeError('Head response requires an increasing output-frame range.')
    if abs(scene.render.fps/scene.render.fps_base-24.0) > 0.000001:
        raise RuntimeError('Head response is defined on the already-retimed24fps output shot.')
    R = {who:rigs[who] for who in ('BOY','GIRL')}
    for who, rig in R.items():
        if rig.type != 'ARMATURE' or 'head' not in rig.pose.bones:
            raise RuntimeError('Missing native age-ten head bone for '+who)
        if not rig.animation_data or not rig.animation_data.action:
            raise RuntimeError('Retimed source rig action missing for '+who)
    frames = tuple(float(G0)+i/4.0 for i in range(int(round((G1-G0)*4))+1))
    schedule = {'GIRL':{'peak_degrees':-2.5,'zero':955.0,'peak_start':958.0,
                        'peak_end':960.0,'release':970.0},
                'BOY':{'peak_degrees':-1.4,'zero':958.0,'peak_start':961.0,
                       'peak_end':963.0,'release':973.0}}
    if G0 > 955 or G1 < 973:
        raise RuntimeError('The authored output-frame range must include G955..973.')
    try:
        event_metadata = json.loads(json.dumps(event))
    except (TypeError,ValueError):
        event_metadata = str(event)
    source_range = [scene.frame_start,scene.frame_end]
    old_frame = scene.frame_current+scene.frame_subframe
    before_hash = {w:_nonhead_hash(r.animation_data.action) for w,r in R.items()}
    rest = {w:{b.name:(list(b.head_local),list(b.tail_local))
               for b in r.data.bones} for w,r in R.items()}
    baseline = {}
    for frame in frames:
        _frame(scene,frame)
        dg = bpy.context.evaluated_depsgraph_get()
        row = {'rigs':{},'camera':scene.camera.matrix_world.copy() if scene.camera else None}
        for who,rig in R.items():
            e = rig.evaluated_get(dg)
            row['rigs'][who] = {'world':e.matrix_world.copy(),
                'bones':{b.name:b.matrix.copy() for b in e.pose.bones},
                'head_base':e.pose.bones['head'].head.copy(),
                'head_length':(e.pose.bones['head'].tail-e.pose.bones['head'].head).length}
        baseline[frame] = row
    last_quaternion = {}
    authored = {}
    for who,rig in R.items():
        action = rig.animation_data.action.copy()
        action.name = 'V060 '+who+' | brief neck-pitch response | output24fps'
        rig.animation_data.action = action
        for bag,fc in list(_curves(action)):
            if _selected(fc.data_path):
                bag.fcurves.remove(fc)
    for frame in frames:
        _frame(scene,frame)
        authored[frame] = {}
        for who,rig in R.items():
            source = baseline[frame]['rigs'][who]
            degrees = _pitch(frame,**schedule[who])
            H = source['head_base']
            base = source['bones']['head']
            matrix = (Matrix.Translation(H) @
                      Matrix.Rotation(math.radians(degrees),4,'Y') @
                      Matrix.Translation(-H) @ base)
            pb = rig.pose.bones['head']
            pb.rotation_mode = 'QUATERNION'
            pb.matrix = matrix
            bpy.context.view_layer.update()
            if who in last_quaternion and pb.rotation_quaternion.dot(last_quaternion[who]) < 0.0:
                pb.rotation_quaternion.negate()
            last_quaternion[who] = pb.rotation_quaternion.copy()
            for prop in ('location','rotation_quaternion','scale'):
                pb.keyframe_insert(prop,frame=frame)
            authored[frame][who] = {'degrees':degrees,'matrix':matrix}
    for rig in R.values():
        for _,fc in _curves(rig.animation_data.action):
            if _selected(fc.data_path):
                fc.extrapolation = 'CONSTANT'
                for key in fc.keyframe_points:
                    key.interpolation = 'LINEAR'
                for mod in list(fc.modifiers):
                    fc.modifiers.remove(mod)
    errors = {'protected_nonhead_bone_matrix_max_abs_error':0.0,
              'root_world_matrix_max_abs_error':0.0,
              'camera_world_matrix_max_abs_error':0.0,
              'head_base_max_position_error_m':0.0,
              'head_segment_length_max_error_m':0.0,
              'authored_head_matrix_max_abs_error':0.0,
              'head_matrix_outside_response_max_abs_error':0.0}
    samples = []
    for frame in frames:
        _frame(scene,frame)
        dg = bpy.context.evaluated_depsgraph_get()
        row = baseline[frame]
        if scene.camera:
            errors['camera_world_matrix_max_abs_error'] = max(
                errors['camera_world_matrix_max_abs_error'],
                _mat_error(scene.camera.matrix_world,row['camera']))
        for who,rig in R.items():
            e = rig.evaluated_get(dg)
            source = row['rigs'][who]
            errors['root_world_matrix_max_abs_error'] = max(
                errors['root_world_matrix_max_abs_error'],
                _mat_error(e.matrix_world,source['world']))
            for bone in e.pose.bones:
                if bone.name != 'head':
                    errors['protected_nonhead_bone_matrix_max_abs_error'] = max(
                        errors['protected_nonhead_bone_matrix_max_abs_error'],
                        _mat_error(bone.matrix,source['bones'][bone.name]))
            head = e.pose.bones['head']
            errors['head_base_max_position_error_m'] = max(
                errors['head_base_max_position_error_m'],
                (head.head-source['head_base']).length)
            errors['head_segment_length_max_error_m'] = max(
                errors['head_segment_length_max_error_m'],
                abs((head.tail-head.head).length-source['head_length']))
            errors['authored_head_matrix_max_abs_error'] = max(
                errors['authored_head_matrix_max_abs_error'],
                _mat_error(head.matrix,authored[frame][who]['matrix']))
            if authored[frame][who]['degrees'] == 0.0:
                errors['head_matrix_outside_response_max_abs_error'] = max(
                    errors['head_matrix_outside_response_max_abs_error'],
                    _mat_error(head.matrix,source['bones']['head']))
        if frame.is_integer() and 954 <= frame <= 974:
            samples.append({'output_frame':frame,
                'girl_pitch_delta_degrees':authored[frame]['GIRL']['degrees'],
                'boy_pitch_delta_degrees':authored[frame]['BOY']['degrees']})
    for who,rig in R.items():
        if _nonhead_hash(rig.animation_data.action) != before_hash[who]:
            raise RuntimeError('Protected non-head action channel changed for '+who)
        for bone in rig.data.bones:
            if (list(bone.head_local),list(bone.tail_local)) != rest[who][bone.name]:
                raise RuntimeError('Rest anatomy changed for '+who)
    if max(errors.values()) > 0.00002:
        raise RuntimeError('Head-response preservation/pivot check failed: '+repr(errors))
    if [scene.frame_start,scene.frame_end] != source_range:
        raise RuntimeError('Source scene frame range changed unexpectedly.')
    _frame(scene,old_frame)
    report = {'status':'V060 brief native neck-pitch response; render review required',
        'event_metadata':event_metadata,
        'event_timing_interpretation':'Metadata only; explicit absolute output-frame schedule below.',
        'selected_scope':'Only head transform channels on two copied rig actions.',
        'output_fps':24,'checked_range':[G0,G1],'quarter_samples':len(frames),
        'schedule_output_frames':schedule,'integer_frame_pitch_samples':samples,
        'nonhead_action_channels_hash_exact':True,'all_rest_bones_exact':True,
        'checks':errors,
        'method':'Head.matrix = T(native head base) @ RY(pitch) @ T(-native head base) @ baseline head.matrix. Quintic nonoscillating rise/hold/release.',
        'limits':['Brief neck pitch only; original fixed-profile face painting retained.',
                  'No eye movement, facial expression, head-turn drawing or physical impact response claimed.',
                  'Selected head channels authored only within the checked output shot range.']}
    print('V060_HEAD_RESPONSE_READY',errors,flush=True)
    return report
