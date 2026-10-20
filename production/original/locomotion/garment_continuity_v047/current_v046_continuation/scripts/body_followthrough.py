"""Measured periodic lower-garment follow-through for an isolated v047 candidate.

Importing performs no scene work. apply(scene) changes only the two body meshes'
native shape drawings. It never opens, saves or renders any file.
"""
import math
import hashlib
import bpy

PERIOD = 31.0
STEP = 0.25
COUNT = 124
PINNED_LAST_ROW = 28
SPECS = {
    'BOY': {'body': 'V046 BOY | tailored coat',
            'tau_frames': 2.0, 'lever_m': 0.28, 'gain': 1.35,
            'limit_x_m': 0.012, 'limit_z_m': 0.003, 'vertical_gain': 0.25},
    'GIRL': {'body': 'V046 GIRL | tailored knee-length dress',
             'tau_frames': 2.75, 'lever_m': 0.38, 'gain': 1.45,
             'limit_x_m': 0.018, 'limit_z_m': 0.003, 'vertical_gain': 0.30},
}


def _set_frame(scene, f):
    whole = math.floor(f)
    scene.frame_set(whole, subframe=f-whole)
    bpy.context.view_layer.update()


def _world_vertices(ob):
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = ev.to_mesh()
    try:
        return [ev.matrix_world @ v.co for v in mesh.vertices]
    finally:
        ev.to_mesh_clear()


def _action_hash(ob):
    if not ob.animation_data or not ob.animation_data.action:
        return None
    a = ob.animation_data.action
    rows = []
    for layer in a.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    rows.append((fc.data_path, fc.array_index,
                        [(tuple(k.co), k.interpolation) for k in fc.keyframe_points],
                        [(m.type, getattr(m, 'mode_before', None),
                          getattr(m, 'mode_after', None)) for m in fc.modifiers]))
    return hashlib.sha256(repr(rows).encode()).hexdigest()


def _periodic_lag(values, tau_frames):
    # Exact periodic causal exponential convolution. The wrapping comes from
    # the measured cycle, with no invented oscillation or separate time clock.
    weights = [math.exp(-k*STEP/tau_frames) for k in range(COUNT)]
    total = sum(weights)
    return [sum(weights[k]*values[(i-k) % COUNT] for k in range(COUNT))/total
            for i in range(COUNT)]


def _summary(values):
    return {'min': min(values), 'max': max(values),
            'peak_to_peak': max(values)-min(values),
            'rms': math.sqrt(sum(v*v for v in values)/len(values))}


def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t*t*(3-2*t)


def _pulse_keys(ob, rest, offsets):
    # Four samples per source frame. Triangular exposure weights blend adjacent
    # native drawings. F32 returns to F1 exactly and CYCLES repeats 31 frames.
    ob.shape_key_add(name='Basis | preserved v046 garment rest coordinates')
    keys = ob.data.shape_keys
    for i, (dx, dz) in enumerate(offsets):
        f = 1+i*STEP
        key = ob.shape_key_add(name='V047 measured cloth lag F%05.2f' % f)
        coords = []
        for index, p in enumerate(rest):
            row = index//17
            weight = _smooth((row-PINNED_LAST_ROW)/(64-PINNED_LAST_ROW))
            coords.extend((p.x+dx*weight, p.y, p.z+dz*weight))
        key.data.foreach_set('co', coords)
        # Insert in time order; endpoint duplicates are explicitly repaired.
        for at, value in [(1.0, 0.0), (max(1.0, f-STEP), 0.0),
                          (f, 1.0), (min(32.0, f+STEP), 0.0), (32.0, 0.0)]:
            key.value = value
            key.keyframe_insert('value', frame=at)
        if i == 0:
            for at in (1.0, 32.0):
                key.value = 1.0
                key.keyframe_insert('value', frame=at)
    action = keys.animation_data.action
    action.name = ob.name+' | V047 measured 31-frame lower-garment lag'
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for k in fc.keyframe_points:
                        k.interpolation = 'LINEAR'
                    cycle = fc.modifiers.new('CYCLES')
                    cycle.mode_before = cycle.mode_after = 'REPEAT'
    return action


def apply(scene):
    assert scene.render.fps == 30, 'Apply to the source 30fps scene before a production retime.'
    bpy.context.window.scene = scene
    old_frame = scene.frame_current+scene.frame_subframe
    bodies = {who: scene.objects[spec['body']] for who, spec in SPECS.items()}
    rigs = {who: scene.objects['V044 '+who+' | estimated joint centres']
            for who in SPECS}
    for who, ob in bodies.items():
        assert ob.get('wardrobe_role') == 'body', ob.name
        assert len(ob.data.vertices) == 65*17
        assert not ob.data.shape_keys, 'Use a fresh preserved v046 input; body already has shape keys.'
        assert not ob.get('v047_measured_lower_garment_lag')
        assert any(m.type == 'ARMATURE' and m.object == rigs[who] for m in ob.modifiers)
    original_actions = {who: _action_hash(rig) for who, rig in rigs.items()}
    rest = {who: [v.co.copy() for v in ob.data.vertices] for who, ob in bodies.items()}
    inputs = {who: {'angle': [], 'pelvis_x': [], 'pelvis_z': []} for who in SPECS}
    baseline = {who: [] for who in SPECS}
    for i in range(COUNT+1):
        _set_frame(scene, 1+i*STEP)
        for who, rig in rigs.items():
            ev = rig.evaluated_get(bpy.context.evaluated_depsgraph_get())
            pelvis, chest = ev.pose.bones['pelvis'], ev.pose.bones['chest']
            pv, cv = pelvis.tail-pelvis.head, chest.tail-chest.head
            angle = 0.65*math.atan2(pv.x, pv.z)+0.35*math.atan2(cv.x, cv.z)
            if i < COUNT:
                inputs[who]['angle'].append(angle)
                inputs[who]['pelvis_x'].append(pelvis.head.x)
                inputs[who]['pelvis_z'].append(pelvis.head.z)
            baseline[who].append(_world_vertices(bodies[who]))
    results, offsets_by_who = {}, {}
    for who, spec in SPECS.items():
        values = inputs[who]
        # The source stays near upright; refuse an angle-wrap discontinuity.
        assert max(abs(values['angle'][i]-values['angle'][(i-1) % COUNT])
                   for i in range(COUNT)) < 0.5
        lag = {k: _periodic_lag(v, spec['tau_frames']) for k, v in values.items()}
        raw_x, raw_z, offsets = [], [], []
        for i in range(COUNT):
            turn = spec['lever_m']*(math.sin(lag['angle'][i])-math.sin(values['angle'][i]))
            sway = lag['pelvis_x'][i]-values['pelvis_x'][i]
            x = spec['gain']*(turn+sway)
            z = spec['vertical_gain']*(lag['pelvis_z'][i]-values['pelvis_z'][i])
            z += spec['lever_m']*0.2*(math.cos(lag['angle'][i])-math.cos(values['angle'][i]))
            raw_x.append(x)
            raw_z.append(z)
            # Smooth saturation retains changing response through the limits;
            # no hard clipping plateau is introduced.
            offsets.append((spec['limit_x_m']*math.tanh(x/spec['limit_x_m']),
                            spec['limit_z_m']*math.tanh(z/spec['limit_z_m'])))
        offsets_by_who[who] = offsets
        ob = bodies[who]
        if ob.data.users > 1:
            ob.data = ob.data.copy()
        action = _pulse_keys(ob, rest[who], offsets)
        ob['v047_measured_lower_garment_lag'] = True
        ob['v047_pinned_rows'] = '0 through 28 inclusive, all 17 columns'
        ob['v047_motion_source'] = 'Periodic causal lag of actual pelvis/chest angle and pelvis sway; no independent oscillator.'
        results[who] = {
            'object': ob.name, 'action': action.name,
            'input_angle_rad': _summary(values['angle']),
            'input_pelvis_x_m': _summary(values['pelvis_x']),
            'input_pelvis_z_m': _summary(values['pelvis_z']),
            'periodic_filter_tau_source_frames': spec['tau_frames'],
            'raw_response_x_m': _summary(raw_x), 'raw_response_z_m': _summary(raw_z),
            'hem_response_x_m': _summary([x for x, z in offsets]),
            'hem_response_z_m': _summary([z for x, z in offsets]),
            'maximum_authored_rest_displacement_m': max(math.hypot(x, z) for x, z in offsets),
            'pinned_rows_inclusive': [0, PINNED_LAST_ROW],
            'pinned_vertices': (PINNED_LAST_ROW+1)*17,
            'new_drawing_samples': COUNT,
            'armature_modifier_retained': True}
    maximum_world = {who: 0.0 for who in SPECS}
    upper_world = {who: 0.0 for who in SPECS}
    first_world = {}
    for i in range(COUNT+1):
        _set_frame(scene, 1+i*STEP)
        for who, ob in bodies.items():
            now = _world_vertices(ob)
            if i == 0:
                inv = rigs[who].matrix_world.inverted()
                first_world[who] = [inv @ p for p in now]
            before = baseline[who][i]
            maximum_world[who] = max(maximum_world[who],
                max((a-b).length for a, b in zip(now, before)))
            upper_world[who] = max(upper_world[who],
                max((now[j]-before[j]).length for j in range((PINNED_LAST_ROW+1)*17)))
            if i == COUNT:
                inv = rigs[who].matrix_world.inverted()
                results[who]['local_evaluated_closing_bookend_error_m'] = max(
                    ((inv @ a)-b).length for a, b in zip(now, first_world[who]))
    for who, rig in rigs.items():
        assert _action_hash(rig) == original_actions[who]
        results[who]['maximum_evaluated_world_change_m'] = maximum_world[who]
        results[who]['maximum_pinned_upper_world_change_m'] = upper_world[who]
        assert upper_world[who] < 2e-6
        # Local comparison removes the rig object's unwrapped travel only;
        # the evaluated garment and all body-pose deformation remain included.
        assert results[who]['local_evaluated_closing_bookend_error_m'] < 2e-6
        results[who]['local_evaluated_closing_bookend_within_2um'] = True
    _set_frame(scene, old_frame)
    return {'scope': 'Lower-garment follow-through candidate; existing body/arm/foot acting is unchanged.',
            'source_period_frames': PERIOD, 'source_fps': 30,
            'quarter_frame_samples': COUNT, 'cycle_bookend': [1, 32],
            'body_topology_uv_material_image_edits': False,
            'rig_action_hashes_unchanged': True,
            'bones_feet_root_camera_edited': False,
            'characters': results,
            'limits': 'Small rest-space deformation over the original armature, not cloth simulation or a new acting performance. Quarter-frame linear drawing blends are position-continuous, not a claim of continuous velocity. Inspect waist volume, projected hem continuity and actual playback before retention.'}
