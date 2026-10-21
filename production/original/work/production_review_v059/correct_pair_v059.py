"""Bounded late-contact native drawing candidate; importing performs no mutation.

Call apply(scene, exact_v007_root). The caller owns saving/rendering the separate
benchmark. Source .blend files are never opened, saved or modified by this helper.
"""
import bpy
import math
from mathutils import Vector

FIRST, LAST = 1801, 1920


def _smooth(a, b, value):
    q = max(0.0, min(1.0, (value - a) / (b - a)))
    return q * q * (3.0 - 2.0 * q)


def _world_vertices(ob):
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = ev.to_mesh()
    try:
        return [ev.matrix_world @ v.co for v in mesh.vertices]
    finally:
        ev.to_mesh_clear()


def _linear(action):
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:
                        key.interpolation = 'LINEAR'


def _rotate_xz(p, pivot, angle):
    d = p - pivot
    c, s = math.cos(angle), math.sin(angle)
    return Vector((pivot.x + c*d.x + s*d.z, p.y,
                   pivot.z - s*d.x + c*d.z))


def _curl_existing_fingers(points, weight):
    """Source topology: palm8 + four 9-row ribbons + one 9-row thumb.

    Keep palm, all digit roots and ribbon widths. Add a small distal bend to
    the actual evaluated drawings, rather than replace fingers or hand design.
    The same world-Y bend curls opposing hands toward one another.
    """
    assert len(points) == 98
    out = [p.copy() for p in points]
    for digit in range(4):
        start = 8 + digit*18
        pivot = (points[start+8] + points[start+9]) * 0.5
        for row in range(5, 9):
            t = (row-4)/4.0
            angle = 0.38 * weight * t*t
            for side in range(2):
                i = start + 2*row + side
                out[i] = _rotate_xz(points[i], pivot, angle)
    # The original opposed thumb remains separate and wraps slightly inward.
    start = 80
    pivot = (points[start] + points[start+1]) * 0.5
    for row in range(2, 9):
        angle = -0.18 * weight * (row/8.0)**2
        for side in range(2):
            i = start+2*row+side
            out[i] = _rotate_xz(points[i], pivot, angle)
    return out


def _bounds(points):
    return {axis: [min(getattr(p, axis) for p in points),
                   max(getattr(p, axis) for p in points)]
            for axis in ('x', 'y', 'z')}


def _make_baked_mesh(collection, source, name, samples, root):
    faces = [tuple(p.vertices) for p in source.data.polygons]
    count = len(source.data.vertices)
    assert all(len(p) == count for p in samples.values())
    mesh = bpy.data.meshes.new(name + ' | editable source topology')
    root_inverse = root.matrix_world.inverted()
    local = {f: [root_inverse @ p for p in points]
             for f, points in samples.items()}
    mesh.from_pydata(local[FIRST], [], faces)
    mesh.update()
    for material in source.data.materials:
        mesh.materials.append(material)
    for p, original in zip(mesh.polygons, source.data.polygons):
        p.material_index = original.material_index
        p.use_smooth = original.use_smooth
    for original in source.data.uv_layers:
        layer = mesh.uv_layers.new(name=original.name)
        assert len(layer.data) == len(original.data)
        for a, b in zip(layer.data, original.data):
            a.uv = b.uv
    ob = bpy.data.objects.new(name, mesh)
    collection.objects.link(ob)
    ob.parent = root
    ob.matrix_parent_inverse.identity()
    ob.location = (0, 0, 0)
    ob.rotation_euler = (0, 0, 0)
    ob.scale = (1, 1, 1)
    ob.shape_key_add(name='Basis')
    keys = mesh.shape_keys
    keys.use_relative = True
    for f in range(FIRST, LAST+1):
        key = ob.shape_key_add(name='DRAW_%04d' % f)
        key.data.foreach_set('co', [v for p in local[f] for v in p])
        for time, value in [(max(FIRST, f-1), 0), (f, 1), (min(LAST, f+1), 0)]:
            key.value = value
            key.keyframe_insert('value', frame=time)
    for f in (FIRST, LAST):
        key = keys.key_blocks['DRAW_%04d' % f]
        key.value = 1
        key.keyframe_insert('value', frame=f)
    keys.animation_data.action.name = name + ' | triangular 120-frame drawing clock'
    _linear(keys.animation_data.action)
    ob['v059_role'] = 'late_contact_native_drawing'
    ob['v059_source'] = source.name
    ob['v059_scope'] = 'Evaluated source drawing baked in static-root coordinates; late wrist/hand correction only.'
    return ob


def apply(scene, root):
    """Return a JSON-serializable correction report; do not save or render."""
    assert root.get('motion_revision') == 'v007_drawn_pose_corrections'
    assert root.name in scene.objects
    assert not any(o.get('v059_role') == 'late_contact_native_drawing'
                   for o in scene.objects), 'Already applied: use a fresh integration candidate.'
    bpy.context.window.scene = scene
    original_frame = scene.frame_current
    scene.frame_set(FIRST)
    bpy.context.view_layer.update()
    root_matrix = root.matrix_world.copy()
    assert abs(root.scale.x-1) < 1e-6 and abs(root.scale.y-1) < 1e-6 and abs(root.scale.z-1) < 1e-6
    rigs = {o['character']: o for o in root.children_recursive
            if o.type == 'ARMATURE' and 'character' in o}
    assert set(rigs) == {'BOY', 'GIRL'}
    spec = [('BOY', 'far'), ('GIRL', 'near')]
    sources = {}
    for who, side in spec:
        rig = rigs[who]
        hands = [o for o in rig.children if o.get('v007_role') == 'drawn_hand'
                 and o.name.split(' | ')[-1] == 'articulated drawn hand '+side]
        skins = [o for o in rig.children if o.name.split(' | ')[-1] == 'drawn skin '+side]
        assert len(hands) == len(skins) == 1, (who, hands, skins)
        assert len(hands[0].data.vertices) == 98
        assert len(skins[0].data.vertices) == 38
        sources[(who, 'hand')] = hands[0]
        sources[(who, 'skin')] = skins[0]
    boots = [o for o in root.children_recursive if o.get('v007_role') == 'support_boot']
    assert len(boots) == 4
    base, corrected = {k: {} for k in sources}, {k: {} for k in sources}
    boot_before = {}
    measurements = []
    for f in range(FIRST, LAST+1):
        scene.frame_set(f)
        bpy.context.view_layer.update()
        assert max(abs(root.matrix_world[i][j]-root_matrix[i][j])
                   for i in range(4) for j in range(4)) < 1e-7, 'Root must be static anchor; TRAVEL owns motion.'
        for key, source in sources.items():
            base[key][f] = _world_vertices(source)
            assert len(base[key][f]) == len(source.data.vertices), 'Topology-changing modifier not supported.'
        if f in (1801, 1897, 1901, 1918, 1920):
            boot_before[f] = {o.name: _world_vertices(o) for o in boots}
        # Skin ribbon final row is the existing visible wrist attachment.
        wrists = {who: (base[(who, 'skin')][f][-2] +
                        base[(who, 'skin')][f][-1])*0.5
                  for who, side in spec}
        a, b = wrists['BOY'], wrists['GIRL']
        axis = b-a
        axis.y = 0
        gap = axis.length
        assert gap > 0.05
        axis.normalize()
        weight = _smooth(1890, 1901, f)
        # At final 132mm wrist spacing this gives 29mm each: palm overlap
        # replaces almost-touching tips. Guard against excessive reach edits.
        inward = min(0.030, max(0, (gap-0.074)*0.5)) * weight
        shifts = {'BOY': axis*inward, 'GIRL': -axis*inward}
        for who, side in spec:
            delta = shifts[who]
            original_skin = base[(who, 'skin')][f]
            skin = []
            for i, p in enumerate(original_skin):
                row = i//2
                t = row/18.0
                blend = t*t*(3-2*t)
                skin.append(p + delta*blend)
            hand = _curl_existing_fingers(base[(who, 'hand')][f], weight)
            hand = [p+delta for p in hand]
            corrected[(who, 'skin')][f] = skin
            corrected[(who, 'hand')][f] = hand
            assert (skin[0]-original_skin[0]).length == 0
            assert (skin[1]-original_skin[1]).length == 0
        if f in (1889, 1890, 1897, 1901, 1910, 1918, 1920):
            measurements.append({'frame': f, 'ramp': weight,
                'each_wrist_shift_m': inward, 'original_wrist_gap_xz_m': gap,
                'corrected_wrist_gap_xz_m': gap-2*inward,
                'hands_before': {w: _bounds(base[(w, 'hand')][f]) for w, s in spec},
                'hands_after': {w: _bounds(corrected[(w, 'hand')][f]) for w, s in spec}})
    collection = bpy.data.collections.new('v059 | Authored late palm contact | separate candidate')
    scene.collection.children.link(collection)
    made = []
    for key, source in sources.items():
        who, part = key
        made.append(_make_baked_mesh(collection, source,
                    'v059 %s | coherent late-contact %s' % (who, part),
                    corrected[key], root))
    for source in sources.values():
        source.hide_render = True
        source.hide_viewport = True
    foot_error = 0
    for f, original in boot_before.items():
        scene.frame_set(f)
        bpy.context.view_layer.update()
        for boot in boots:
            now = _world_vertices(boot)
            foot_error = max(foot_error, max((a-b).length
                for a, b in zip(now, original[boot.name])))
    assert foot_error < 1e-7
    scene.frame_set(original_frame)
    bpy.context.view_layer.update()
    return {'scope': 'Native late-contact drawing candidate; no load-bearing or finished acting claim.',
        'new_editable_objects': [o.name for o in made],
        'original_drawings_hidden': [o.name for o in sources.values()],
        'native_drawing_keys_per_object': 120,
        'clock_global': [FIRST, LAST], 'correction_ramp': [1890, 1901],
        'max_wrist_shift_m': 0.030, 'target_wrist_gap_xz_m': 0.074,
        'fixed_elbow': True, 'original_rig_actions_and_feet_edited': False,
        'checked_boot_world_vertex_error_m': foot_error,
        'measurements': measurements,
        'review_required': 'Inspect actual 1897/1901/1918 native crops, then continuous-speed five-second movie. Reject tangled fingers or a detached palm. This is a firmer hand contact candidate; torso and planted feet still bear the body weight.'}
