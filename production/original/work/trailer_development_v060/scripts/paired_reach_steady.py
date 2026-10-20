"""Owned v060 paired reaching on the frozen steady 32-frame age-ten walk.

apply(scene) edits only in-memory copies of the two selected near-arm actions,
and copies the selected sleeve/hand drawings. It never opens, saves or renders.
The source walking feet, root travel, camera, painting and other arm remain.
Fresh reach only: no earlier31-frame caches, extra gait phase, cloth or braid lag.
"""
import bpy
import math
import hashlib
import numpy as np
from mathutils import Vector, Matrix

_ARM = ('upper_arm_near', 'forearm_near', 'hand_near')
PROOF_END = 151
_FRAMES = tuple(1.0 + i / 4.0 for i in range((PROOF_END - 1)*4 + 1))
_EPS = 0.00002


def _frame(scene, f):
    scene.frame_set(int(f), subframe=f - int(f))
    bpy.context.view_layer.update()


def _curves(action):
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    yield bag, fc


def _is_selected(path):
    return any(path.startswith('pose.bones["' + n + '"].') for n in _ARM)


def _action_hash(action, selected=False):
    rows = []
    for _, fc in _curves(action):
        if _is_selected(fc.data_path) != selected:
            continue
        rows.append((fc.data_path, fc.array_index, fc.extrapolation,
                     [(tuple(k.co), k.interpolation) for k in fc.keyframe_points],
                     [(m.type, getattr(m, 'mode_before', None),
                       getattr(m, 'mode_after', None)) for m in fc.modifiers]))
    return hashlib.sha256(repr(rows).encode()).hexdigest()


def _smooth(u):
    u = max(0.0, min(1.0, float(u)))
    return u * u * u * (u * (u * 6.0 - 15.0) + 10.0)


def _interp(t, keys):
    if t <= keys[0][0]:
        return float(keys[0][1])
    if t >= keys[-1][0]:
        return float(keys[-1][1])
    i = next(i for i in range(len(keys) - 1)
             if keys[i][0] <= t <= keys[i + 1][0])
    x0, y0 = keys[i]
    x1, y1 = keys[i + 1]
    dt = x1 - x0
    u = (t - x0) / dt
    m0 = ((y1 - y0) / dt if i == 0 else
          (keys[i + 1][1] - keys[i - 1][1]) /
          (keys[i + 1][0] - keys[i - 1][0]))
    m1 = ((y1 - y0) / dt if i == len(keys) - 2 else
          (keys[i + 2][1] - keys[i][1]) /
          (keys[i + 2][0] - keys[i][0]))
    return (y0 * (2 * u**3 - 3 * u*u + 1) +
            m0 * dt * (u**3 - 2 * u*u + u) +
            y1 * (-2 * u**3 + 3 * u*u) +
            m1 * dt * (u**3 - u*u))


def _rounded(H, K, A, l1, d, radius):
    U = (K - H).normalized()
    V = (A - K).normalized()
    if d < l1 - radius:
        return H + U * d, U
    if d > l1 + radius:
        return K + V * (d - l1), V
    u = (d - l1 + radius) / (2 * radius)
    p, q = K - U * radius, K + V * radius
    m, n = U * 2 * radius, V * 2 * radius
    pos = (p * (2*u**3 - 3*u*u + 1) + m * (u**3 - 2*u*u + u) +
           q * (-2*u**3 + 3*u*u) + n * (u**3 - u*u))
    der = (p * (6*u*u - 6*u) + m * (3*u*u - 4*u + 1) +
           q * (-6*u*u + 6*u) + n * (3*u*u - 2*u))
    return pos, der.normalized()


def _ik(H, A, l1, l2, branch):
    delta = Vector((A.x - H.x, 0.0, A.z - H.z))
    d = delta.length
    if not abs(l1 - l2) + 0.00001 < d < l1 + l2 - 0.00001:
        raise RuntimeError('Paired wrist target is outside native arm reach: ' +
                           repr((d, l1, l2)))
    U = delta / d
    x = (l1*l1 - l2*l2 + d*d) / (2*d)
    h = math.sqrt(max(0.0, l1*l1 - x*x))
    perp = Vector((-U.z, 0.0, U.x))
    return H + U * x + perp * h * branch


def _direction_mix(a, b, amount):
    """Shortest 2D angular interpolation, with native segment lengths kept."""
    a0 = math.atan2(a.x, -a.z)
    a1 = math.atan2(b.x, -b.z)
    delta = (a1-a0+math.pi) % (2.0*math.pi) - math.pi
    theta = a0 + amount*delta
    return Vector((math.sin(theta),0.0,-math.cos(theta)))


def _matrix_for(rig, name, a, b):
    rb = rig.data.bones[name]
    old = rb.tail_local - rb.head_local
    old.y = 0.0
    old.normalize()
    new = b - a
    new.y = 0.0
    new.normalize()
    q = old.rotation_difference(new)
    return (Matrix.Translation(a) @ q.to_matrix().to_4x4() @
            rb.matrix_local.to_3x3().to_4x4())


def _put_pose(rig, name, matrix, f, last_q):
    pb = rig.pose.bones[name]
    pb.rotation_mode = 'QUATERNION'
    pb.matrix = matrix
    bpy.context.view_layer.update()
    key = (rig.name, name)
    if key in last_q and pb.rotation_quaternion.dot(last_q[key]) < 0.0:
        pb.rotation_quaternion.negate()
    last_q[key] = pb.rotation_quaternion.copy()
    for prop in ('location', 'rotation_quaternion', 'scale'):
        pb.keyframe_insert(prop, frame=f)


def _world_vertices(ob, depsgraph):
    e = ob.evaluated_get(depsgraph)
    return [e.matrix_world @ v.co for v in e.data.vertices]


def _mat_error(a, b):
    return max(abs(a[i][j] - b[i][j]) for i in range(4) for j in range(4))


def _copy_drawing(source, collection, new_name):
    ob = source.copy()
    ob.data = source.data.copy()
    ob.name = new_name
    collection.objects.link(ob)
    if ob.data.shape_keys:
        ob.shape_key_clear()
    ob.animation_data_clear()
    ob.hide_render = False
    ob.hide_viewport = False
    source.hide_render = True
    source.hide_viewport = True
    source['V060_reach_status'] = 'Preserved original drawing; hidden by owned near-arm rehearsal copy.'
    return ob


def _drawing_cache(ob, poses):
    ob.data.vertices.foreach_set('co', [v for p in poses[1.0] for v in p])
    ob.shape_key_add(name='Basis | retained F1 paint and pose')
    for f in _FRAMES[1:]:
        key = ob.shape_key_add(name='V060 actual arm F%05.2f' % f)
        key.data.foreach_set('co', [v for p in poses[f] for v in p])
        ats = sorted(set((1.0, max(1.0, f - 0.25), f,
                          min(float(PROOF_END), f + 0.25), float(PROOF_END))))
        for at in ats:
            key.value = float(at == f)
            key.keyframe_insert('value', frame=at)
    action = ob.data.shape_keys.animation_data.action
    action.name = ob.name + ' | 151 frame quarter drawings'
    for _, fc in _curves(action):
        fc.extrapolation = 'CONSTANT'
        for key in fc.keyframe_points:
            key.interpolation = 'LINEAR'
    ob['V060_quarter_drawings'] = len(_FRAMES)
    ob['V060_original_topology_UV_materials_retained'] = True


def _mesh_signature(ob):
    return {
        'vertices': len(ob.data.vertices),
        'faces': [tuple(p.vertices) for p in ob.data.polygons],
        'uv': [(u.name, [(float(v.uv.x), float(v.uv.y)) for v in u.data])
               for u in ob.data.uv_layers],
        'materials': [m.name for m in ob.data.materials]
    }


def _hand_mask(ob):
    layer = ob.data.uv_layers.active
    image = next(n.image for m in ob.data.materials if m and m.use_nodes
                 for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image)
    W, H = image.size
    pix = np.empty(W*H*4, dtype=np.float32)
    image.pixels.foreach_get(pix)
    alpha = pix.reshape(H, W, 4)[:, :, 3]
    uvs = {}
    for loop in ob.data.loops:
        if loop.vertex_index not in uvs:
            uvs[loop.vertex_index] = layer.data[loop.index].uv.copy()
    ids = [i for i, uv in uvs.items()
           if alpha[min(H-1, max(0, int(uv.y*H))),
                    min(W-1, max(0, int(uv.x*W)))] > 0.8]
    return ids, image.name


def apply(scene):
    if scene.frame_start != 1 or scene.frame_end < PROOF_END or scene.render.fps != 30:
        raise RuntimeError('Expected the frozen steady source at 30fps covering at least1..151.')
    source_scene_range = [scene.frame_start, scene.frame_end]
    rigs = {w: bpy.data.objects['V044 ' + w + ' | estimated joint centres']
            for w in ('BOY', 'GIRL')}
    if any(bpy.data.objects.get('V060 ' + w + ' | reach sleeve near')
           for w in rigs):
        raise RuntimeError('Paired reach has already been applied to this file.')
    sleeves = {w: bpy.data.objects['V046 ' + w +
               ' | painted continuous rolled sleeve near'] for w in rigs}
    hands = {w: bpy.data.objects['V046 ' + w +
             ' | original painted hand near'] for w in rigs}
    for w in rigs:
        if len(sleeves[w].data.vertices) != 441 or len(hands[w].data.vertices) != 833:
            raise RuntimeError('Unexpected original sleeve/hand grid topology.')
    boots = [o for o in bpy.data.objects
             if o.parent in rigs.values() and o.type == 'MESH' and
             o.get('proportion_role') == 'boot' and not o.hide_render]
    if len(boots) != 4:
        raise RuntimeError('Could not identify all four original painted boots.')
    collection = bpy.data.collections.new('V060 | paired offer into light | arm rehearsal')
    scene.collection.children.link(collection)
    baseline = {}
    nonarm_action_hash = {w: _action_hash(r.animation_data.action)
                          for w, r in rigs.items()}
    protected_bones = {w: {b.name: (list(b.head_local), list(b.tail_local))
                           for b in r.data.bones} for w, r in rigs.items()}
    original_drawings = {w: {'sleeve': _mesh_signature(sleeves[w]),
                              'hand': _mesh_signature(hands[w])}
                         for w in rigs}
    old_frame = scene.frame_current + scene.frame_subframe
    for f in _FRAMES:
        _frame(scene, f)
        dg = bpy.context.evaluated_depsgraph_get()
        row = {'rigs': {}, 'boots': {o.name: _world_vertices(o, dg) for o in boots},
               'camera': scene.camera.matrix_world.copy()}
        for w, r in rigs.items():
            e = r.evaluated_get(dg)
            row['rigs'][w] = {
                'world': e.matrix_world.copy(),
                'bones': {b.name: {'matrix': b.matrix.copy(), 'head': b.head.copy(),
                                  'tail': b.tail.copy()} for b in e.pose.bones}}
        baseline[f] = row
    for w, r in rigs.items():
        copied = r.animation_data.action.copy()
        copied.name = 'V060 ' + w + ' | near arm offer and reassuring hold'
        r.animation_data.action = copied
        for bag, fc in list(_curves(copied)):
            if _is_selected(fc.data_path):
                bag.fcurves.remove(fc)
    source_clock = {}
    for w, r in rigs.items():
        root = r.parent
        source_clock[w] = {k: root.get(k) for k in
            ('stride_m', 'period_frames', 'fps', 'phase_girl_frames',
             'source_distance_formula', 'source_clock')}
        if abs(float(root.get('period_frames', 0.0)) - 32.0) > 0.000001:
            raise RuntimeError('This gesture requires the frozen native32-frame steady gait.')
    ik_branch = {}
    source_arm_intent = {}
    for w, r in rigs.items():
        pose = baseline[25.0]['rigs'][w]['bones']
        H = pose['upper_arm_near']['head']
        K = pose['upper_arm_near']['tail']
        A = pose['forearm_near']['tail']
        U = (A-H).normalized()
        side = (K-H).dot(Vector((-U.z,0.0,U.x)))
        if abs(side) < 0.000001:
            raise RuntimeError('Source F25 elbow is too straight to select a stable IK branch.')
        ik_branch[w] = 1.0 if side > 0.0 else -1.0
        source_arm_intent[w] = {'source_f25_wrist_x_minus_shoulder_x_m': A.x-H.x,
            'source_f25_signed_elbow_side_m': side, 'source_ik_branch': ik_branch[w]}
    last_q = {}
    reference_shoulders = baseline[55.0]['rigs']
    reference_mean_shoulder_z = sum((reference_shoulders[w]['world'] @
        reference_shoulders[w]['bones']['upper_arm_near']['head']).z for w in rigs) / 2.0
    targets = {}
    max_target_error = 0.0
    min_reach_margin = 10.0
    max_girl_wrist_departure_from_linear_m = 0.0
    authored_path_samples = []
    for f in _FRAMES:
        _frame(scene, f)
        base = baseline[f]['rigs']
        shoulders = {w: base[w]['world'] @ base[w]['bones'][_ARM[0]]['head']
                     for w in rigs}
        middle_x = (shoulders['BOY'].x + shoulders['GIRL'].x) / 2.0
        mean_shoulder_z = (shoulders['BOY'].z + shoulders['GIRL'].z) / 2.0
        shared_z = 0.880 + 0.5 * (mean_shoulder_z - reference_mean_shoulder_z)
        targets[f] = {}
        for w, r in rigs.items():
            offer = _smooth((f - (29.0 if w == 'BOY' else 25.0)) /
                            (26.0 if w == 'BOY' else 26.0))
            poses = base[w]['bones']
            world = base[w]['world']
            source_wrist = world @ poses['hand_near']['head']
            sign = 1.0 if w == 'BOY' else -1.0
            goal = Vector((middle_x - sign*0.065, 0.0, shared_z - sign*0.005))
            wrist_world = source_wrist.lerp(goal, offer)
            H = poses['upper_arm_near']['head'].copy()
            A = world.inverted() @ wrist_world
            if offer <= 0.0:
                matrices = {n: poses[n]['matrix'] for n in _ARM}
            else:
                l1 = r.data.bones['upper_arm_near'].length
                l2 = r.data.bones['forearm_near'].length
                if w == 'GIRL':
                    # Reach the low-elbow backward offer without an IK pole pop.
                    # The native source uses the other bend branch; unfold then
                    # refold by blending fixed-length FK directions in 2D.
                    # Only the final goal is an IK target during approach.
                    goal_A = world.inverted() @ goal
                    goal_K = _ik(H, goal_A, l1, l2, 1.0)
                    source_U = (poses['upper_arm_near']['tail']-
                                poses['upper_arm_near']['head']).normalized()
                    source_V = (poses['forearm_near']['tail']-
                                poses['forearm_near']['head']).normalized()
                    U = _direction_mix(source_U,(goal_K-H).normalized(),offer)
                    V = _direction_mix(source_V,(goal_A-goal_K).normalized(),offer)
                    K = H+U*l1
                    A = K+V*l2
                    actual_fk_wrist = world @ A
                    max_girl_wrist_departure_from_linear_m = max(
                        max_girl_wrist_departure_from_linear_m,
                        (actual_fk_wrist-wrist_world).length)
                    wrist_world = actual_fk_wrist
                    # A straight elbow can occur in this continuous FK path;
                    # no IK reach guard is applied to its intermediate wrist.
                else:
                    K = _ik(H, A, l1, l2, ik_branch[w])
                min_reach_margin = min(min_reach_margin, l1 + l2 - (A - H).length)
                h0 = (poses['hand_near']['tail'] -
                      poses['hand_near']['head']).normalized()
                h1 = Vector((sign, 0.0, 0.075*sign)).normalized()
                hdir = h0.lerp(h1, offer).normalized()
                matrices = {
                    'upper_arm_near': _matrix_for(r, 'upper_arm_near', H, K),
                    'forearm_near': _matrix_for(r, 'forearm_near', K, A),
                    'hand_near': _matrix_for(r, 'hand_near', A,
                                            A + hdir*r.data.bones['hand_near'].length)}
            for n in _ARM:
                _put_pose(r, n, matrices[n], f, last_q)
            targets[f][w] = {'wrist_world': wrist_world, 'offer': offer,
                             'contact_goal_world': goal}
            if w == 'GIRL' and f in (1.0,25.0,29.0,33.0,40.0,45.0,51.0,55.0,94.0,150.0,151.0):
                authored_path_samples.append({'frame':f,'offer':offer,
                    'authored_fk_wrist_world':list(wrist_world),
                    'terminal_goal_wrist_world':list(goal),
                    'distance_to_terminal_goal_m':(wrist_world-goal).length})
        bpy.context.view_layer.update()
    for r in rigs.values():
        for _, fc in _curves(r.animation_data.action):
            if _is_selected(fc.data_path):
                fc.extrapolation = 'CONSTANT'
                for key in fc.keyframe_points:
                    key.interpolation = 'LINEAR'
                for mod in list(fc.modifiers):
                    fc.modifiers.remove(mod)
    # Rebuild the selected sleeve drawings from their actual new bone positions.
    sleeve_poses = {w: {} for w in rigs}
    new_sleeves = {}
    new_hands = {}
    hand_masks = {}
    hand_spans = {}
    for w, r in rigs.items():
        o = _copy_drawing(sleeves[w], collection, 'V060 ' + w + ' | reach sleeve near')
        new_sleeves[w] = o
        # Same source vertex order, polygons, UV registration, material and origin.
        local_from_rig = (r.matrix_world.inverted() @ o.matrix_world).inverted()
        o['V060_local_from_rig'] = [v for row in local_from_rig for v in row]
        h = _copy_drawing(hands[w], collection, 'V060 ' + w + ' | retained paint hand fold near')
        new_hands[w] = h
        ids, im = _hand_mask(h)
        hand_masks[w] = ids
        hand_spans[w] = {'source_painted_span_m': float(h.get('painted_vertical_hand_span_m')),
                          'source_fingertip_row': int(h.get('actual_painted_fingertip_source_row')),
                          'opaque_grid_samples': len(ids), 'original_atlas': im}
        # Native vertex-grid finger fold. Wrist and first 52 mm keep original
        # longitudinal registration. The finger fold projects about 90 mm.
        # The original single atlas hand chirality is opposed for GIRL below.
        to_rig = r.matrix_world.inverted() @ h.matrix_world
        from_rig = to_rig.inverted()
        rest_wrist = r.data.bones['hand_near'].head_local.z
        source = [v.co.copy() for v in h.data.vertices]
        h.shape_key_add(name='Basis | untouched original painted hand')
        key = h.shape_key_add(name='V060 native grid finger fold | retained atlas')
        for i, co in enumerate(source):
            p = to_rig @ co
            d = rest_wrist - p.z
            if d > 0.052:
                u = max(0.0, min(1.0, (d - 0.052) / (0.145 - 0.052)))
                p.z = rest_wrist - (0.052 + 0.042 * math.sin(u*math.pi*0.65))
                p.x += (1.0 if w == 'BOY' else -1.0) * 0.014 * (1.0 - math.cos(u*math.pi*0.80))
            # Two millimetres of separation sets the retained girl paint in front.
            if w == 'GIRL':
                p.y -= 0.002
            key.data[i].co = from_rig @ p
        for f in _FRAMES:
            key.value = _smooth((f - 36.0) / 19.0)
            key.keyframe_insert('value', frame=f)
        if w == 'GIRL':
            # One source hand chirality cannot oppose thumbs by bone rotation
            # alone: its +localX thumb becomes world-down on a -X hand bone.
            # Rotate its native painted grid 180 degrees about the long axis.
            # Two keys give cos(theta)/sin(theta), preserving cross-section
            # width through the pronation instead of flattening scalar x.
            mirror = h.shape_key_add(name='V060 opposed thumb | native lateral pronation')
            turn_depth = h.shape_key_add(name='V060 wrist pronation depth | native grid')
            opaque_rows = {}
            for i in ids:
                opaque_rows.setdefault(i//17, []).append((to_rig @ source[i]).x)
            for i, co in enumerate(source):
                p = to_rig @ co
                d = rest_wrist - p.z
                row = opaque_rows.get(i//17, [])
                center = ((min(row)+max(row))/2.0 if row else 0.0)
                axis_x = center * (1.0 - _smooth(max(0.0,d)/0.020))
                q = p.copy()
                q.x = 2.0*axis_x - p.x
                mirror.data[i].co = from_rig @ q
                q = p.copy()
                q.y += p.x-axis_x
                turn_depth.data[i].co = from_rig @ q
            for f in _FRAMES:
                theta = math.pi*_smooth((f-25.0)/26.0)
                mirror.value = 0.5*(1.0-math.cos(theta))
                turn_depth.value = math.sin(theta)
                mirror.keyframe_insert('value',frame=f)
                turn_depth.keyframe_insert('value',frame=f)
            hand_spans[w]['chirality'] = 'Native 180 degree grid pronation during offer; original opaque wrist envelope fitted over first20mm, distal thumb opposed.'
        for _, fc in _curves(h.data.shape_keys.animation_data.action):
            fc.extrapolation = 'CONSTANT'
            for k in fc.keyframe_points:
                k.interpolation = 'LINEAR'
        h['V060_hand_limit'] = 'Native existing 833-vertex atlas grid fold, with wrist rows retained; profile contact rehearsal, not approved finished grip anatomy.'
    max_nonarm_error = max_root_error = max_camera_error = max_boot_error = 0.0
    max_joint_error = 0.0
    contact = []
    for f in _FRAMES:
        _frame(scene, f)
        dg = bpy.context.evaluated_depsgraph_get()
        base = baseline[f]
        max_camera_error = max(max_camera_error,
                               _mat_error(scene.camera.matrix_world, base['camera']))
        for boot in boots:
            V = _world_vertices(boot, dg)
            max_boot_error = max(max_boot_error,
                                max((a-b).length for a, b in zip(V, base['boots'][boot.name])))
        for w, r in rigs.items():
            e = r.evaluated_get(dg)
            max_root_error = max(max_root_error,
                                 _mat_error(e.matrix_world, base['rigs'][w]['world']))
            for b in e.pose.bones:
                if b.name not in _ARM:
                    max_nonarm_error = max(max_nonarm_error,
                        _mat_error(b.matrix, base['rigs'][w]['bones'][b.name]['matrix']))
            arm = e.pose.bones
            max_joint_error = max(max_joint_error,
                (arm['upper_arm_near'].tail-arm['forearm_near'].head).length,
                (arm['forearm_near'].tail-arm['hand_near'].head).length)
            actual_wrist = e.matrix_world @ arm['hand_near'].head
            max_target_error = max(max_target_error,
                (actual_wrist-targets[f][w]['wrist_world']).length)
            H = arm['upper_arm_near'].head
            K = arm['upper_arm_near'].tail
            A = arm['forearm_near'].tail
            l1 = r.data.bones['upper_arm_near'].length
            end = l1 + 0.027
            local_from_rig = Matrix([new_sleeves[w]['V060_local_from_rig'][i*4:i*4+4]
                                    for i in range(4)])
            verts = []
            for i in range(49):
                t = i / 48.0
                d = -0.008 + (end + 0.008)*t
                center, tangent = _rounded(H, K, A, l1, d, 0.018)
                normal = Vector((-tangent.z, 0.0, tangent.x))
                rad = _interp(t, [(0,.038),(.12,.049),(.5,.045),(.85,.034),(1,.041)])
                for j in range(9):
                    p = center + normal*((j/8.0*2.0-1.0)*rad)
                    p.y = -0.052
                    verts.append(local_from_rig @ p)
            sleeve_poses[w][f] = verts
        if f >= 55.0:
            paint = {}
            for w, h in new_hands.items():
                ev = h.evaluated_get(dg)
                paint[w] = np.array([list(ev.matrix_world @ ev.data.vertices[i].co)
                                     for i in hand_masks[w]])
            d = paint['BOY'][:, None, :] - paint['GIRL'][None, :, :]
            nearest = float(np.sqrt(np.min(np.sum(d*d, axis=2))))
            boy_wrist = rigs['BOY'].matrix_world @ rigs['BOY'].pose.bones['hand_near'].head
            girl_wrist = rigs['GIRL'].matrix_world @ rigs['GIRL'].pose.bones['hand_near'].head
            contact.append({'frame': f, 'wrist_gap_m': (boy_wrist-girl_wrist).length,
                            'closest_opaque_paint_grid_distance_m': nearest,
                            'contact_center': list((boy_wrist+girl_wrist)/2.0)})
    for w in rigs:
        _drawing_cache(new_sleeves[w], sleeve_poses[w])
        for kind, ob in [('sleeve', new_sleeves[w]), ('hand', new_hands[w])]:
            if _mesh_signature(ob) != original_drawings[w][kind]:
                raise RuntimeError('Original drawing topology/UV/material registration changed.')
        if _action_hash(rigs[w].animation_data.action) != nonarm_action_hash[w]:
            raise RuntimeError('A protected non-arm action channel changed.')
        for b in rigs[w].data.bones:
            if (list(b.head_local), list(b.tail_local)) != protected_bones[w][b.name]:
                raise RuntimeError('The age-ten rest anatomy changed.')
    errors = {'protected_nonselected_bone_matrix_max_abs_error': max_nonarm_error,
              'root_world_matrix_max_abs_error': max_root_error,
              'camera_world_matrix_max_abs_error': max_camera_error,
              'actual_four_boot_world_vertex_max_error_m': max_boot_error,
              'selected_elbow_wrist_joint_max_gap_m': max_joint_error,
              'selected_wrist_target_max_error_m': max_target_error}
    if max(errors.values()) > _EPS:
        raise RuntimeError('Native paired reach preservation/attachment check failed: ' + repr(errors))
    _frame(scene, old_frame)
    result = {
        'status': 'OWNED V060 REFINED IN-MEMORY PROFILE REACH REHEARSAL; render review required',
        'selected_arms': {'BOY': 'near; forward response toward girl',
                          'GIRL': 'near; fresh backward offer toward boy'},
        'source_f25_arm_geometry': source_arm_intent,
        'girl_terminal_goal_ik_branch': 1.0,
        'girl_approach_path': 'F25..51 shortest-angle2D FK blend of native upper/forearm directions toward branch+1 IK goal. Segment lengths fixed; wrist arcs freely, reaches goal exactly at51. No upper-arm depth or3D rotation trick.',
        'girl_max_wrist_departure_from_linear_interpolation_m': max_girl_wrist_departure_from_linear_m,
        'girl_authored_wrist_path_key_samples': authored_path_samples,
        'valid_authored_range': [1, PROOF_END], 'fps': 30, 'source_walk_period_frames': 32,
        'source_scene_range_retained': source_scene_range,
        'source_clock_retained': source_clock,
        'girl_source_phase_already_baked_frames': 2,
        'output_clock': 'F=1+(G-G0)*30/24; outputG0..G0+119 evaluatesF1..149.75',
        'quarter_samples': len(_FRAMES),
        'timing': {'girl_offer': [25,51], 'boy_response': [29,55], 'paired_hold': [55,PROOF_END]},
        'wrist_horizontal_gap_m': .130, 'vertical_wrist_stagger_m': .010,
        'contact_center_height_at_f55_m': .880, 'source_mean_shoulder_bob_gain': .5,
        'hand_pitch_z_over_x': .075, 'fold_projected_paint_length_approx_m': .090,
        'minimum_elbow_reach_margin_m': min_reach_margin,
        'hand_paint': hand_spans, 'checks': errors,
        'protected_nonarm_actions_identical': True,
        'age10_rest_bones_exact': True,
        'selected_sleeve_hand_topology_UV_materials_exact': True,
        'new_raster_paint_generated': False,
        'other_arm_unchanged': True,
        'selected_sleeve_drawing_count_each': len(_FRAMES),
        'paint_contact_samples': contact,
        'paint_contact_max_nearest_grid_distance_m': max(r['closest_opaque_paint_grid_distance_m'] for r in contact),
        'limits': ['Fixed profile heads and original age-ten painting retained; no body/head turn.',
                   'Walking reassurance only: no load-bearing support or recovery acting claimed.',
                   'Hand fold retains the source paint and is a profile grip rehearsal; visual review must approve silhouette and finger overlap.',
                   'Quarter-frame sleeve drawings and selected arm gesture cover only native1..151; source scene range is retained but no gesture attachment is approved after151.']
    }
    scene['V060_paired_reach_status'] = result['status']
    scene['V060_paired_reach_limit'] = 'Reassuring walking hand contact rehearsal; no load-bearing support, head turn, or full-trailer approval.'
    print('V060_REFINED_PAIRED_REACH_IN_MEMORY_READY', errors, flush=True)
    return result