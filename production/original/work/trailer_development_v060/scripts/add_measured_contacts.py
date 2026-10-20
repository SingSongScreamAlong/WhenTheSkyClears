"""Geometry-driven painted contact marks for an owned v060 world-shot candidate.

Import has no effects. apply(scene, boots, frames, floor_fn) creates eight new
native XZ quads; it never opens/saves a .blend, renders, or edits a foot.
"""
import bpy
import math
from mathutils import Vector

COLLECTION = 'V060 | evaluated boot contact paint | no physical shadow claim'


def _smooth(a, b, x):
    t = max(0.0, min(1.0, (x-a)/(b-a)))
    return t*t*(3.0-2.0*t)


def _clamp(x, low, high):
    return max(low, min(high, x))


def _set_frame(scene, f):
    n = math.floor(f)
    scene.frame_set(n, subframe=f-n)
    bpy.context.view_layer.update()


def _points(ob):
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = ev.to_mesh()
    try:
        return [ev.matrix_world @ v.co for v in mesh.vertices]
    finally:
        ev.to_mesh_clear()


def _linear(id_block):
    if not id_block.animation_data or not id_block.animation_data.action:
        return
    for layer in id_block.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for k in fc.keyframe_points:
                        k.interpolation = 'CONSTANT' if fc.data_path == 'hide_render' else 'LINEAR'


def _material(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.surface_render_method = 'BLENDED'
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    uv = nodes.new('ShaderNodeTexCoord')
    radius = nodes.new('ShaderNodeVectorMath')
    radius.operation = 'DISTANCE'
    radius.inputs[1].default_value = (.5, .5, 0)
    links.new(uv.outputs['UV'], radius.inputs[0])
    gradient = nodes.new('ShaderNodeMapRange')
    gradient.name = 'V060 | soft UV oval alpha'
    gradient.clamp = True
    gradient.interpolation_type = 'SMOOTHERSTEP'
    gradient.inputs['From Min'].default_value = 0.0
    gradient.inputs['From Max'].default_value = .5
    gradient.inputs['To Min'].default_value = 1.0
    gradient.inputs['To Max'].default_value = 0.0
    links.new(radius.outputs['Value'], gradient.inputs[0])
    opacity = nodes.new('ShaderNodeValue')
    opacity.name = 'V060 | actual evaluated sole clearance opacity'
    opacity.outputs[0].default_value = 0.0
    alpha = nodes.new('ShaderNodeMath')
    alpha.operation = 'MULTIPLY'
    links.new(gradient.outputs[0], alpha.inputs[0])
    links.new(opacity.outputs[0], alpha.inputs[1])
    clear = nodes.new('ShaderNodeBsdfTransparent')
    ink = nodes.new('ShaderNodeEmission')
    ink.inputs[0].default_value = (.010, .008, .006, 1)
    mix = nodes.new('ShaderNodeMixShader')
    links.new(alpha.outputs[0], mix.inputs[0])
    links.new(clear.outputs[0], mix.inputs[1])
    links.new(ink.outputs[0], mix.inputs[2])
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(mix.outputs[0], output.inputs[0])
    return mat, opacity.outputs[0]


def _quad(collection, boot, kind):
    name = 'V060 contact '+kind+' | '+boot.name
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(-.5, 0, -.5), (.5, 0, -.5),
                     (.5, 0, .5), (-.5, 0, .5)], [], [(0, 1, 2, 3)])
    mesh.update()
    layer = mesh.uv_layers.new(name='V060 soft contact oval UV')
    for d, uv in zip(layer.data, [(0, 0), (1, 0), (1, 1), (0, 1)]):
        d.uv = uv
    material, opacity = _material(name)
    mesh.materials.append(material)
    ob = bpy.data.objects.new(name, mesh)
    collection.objects.link(ob)
    ob['v060_contact_boot'] = boot.name
    ob['v060_contact_kind'] = kind
    ob['v060_contact_method'] = 'Painted camera-facing geometry derived from actual evaluated support points, not a physical light shadow.'
    return ob, material.node_tree, opacity


def _measure(points, floor_fn):
    heights = [p.z-float(floor_fn(p.y)) for p in points]
    clearance = min(heights)
    # A smooth six-millimetre lower envelope avoids switching abruptly between
    # single contour vertices as a sole rolls. No synthetic gait phase is used.
    weights = [(1-_smooth(0, .006, h-clearance))**2 for h in heights]
    total = sum(weights)
    assert total > 0
    x = sum(p.x*w for p, w in zip(points, weights))/total
    y = sum(p.y*w for p, w in zip(points, weights))/total
    variance = sum(w*(p.x-x)**2 for p, w in zip(points, weights))/total
    effective_span = 2.8*math.sqrt(max(0, variance))
    support = [p for p, h in zip(points, heights) if h <= clearance+.003]
    return {'clearance_m': clearance, 'support_x': x, 'support_y': y,
            'effective_support_span_m': effective_span,
            'lower_support_span_m': max(p.x for p in support)-min(p.x for p in support),
            'lower_support_count': len(support)}


def _ranges(rows, name):
    values = [r[name] for r in rows]
    return {'minimum': min(values), 'maximum': max(values)}


def apply(scene, boots, frames, floor_fn):
    """Sample the supplied interval at quarter frames and return measurements.

    floor_fn accepts a WORLD Y and returns world floor Z. All boot dimensions
    and transforms, including the caller's affine Y-to-Z shear, are evaluated.
    The caller owns prior-contact visibility, native saving and render review.
    """
    boots = list(boots)
    requested = sorted(set(float(f) for f in frames))
    assert len(boots) == 4 and len({b.name for b in boots}) == 4
    assert requested and callable(floor_fn)
    assert all(b.type == 'MESH' and b.name in scene.objects and not b.hide_render for b in boots)
    assert not bpy.data.collections.get(COLLECTION), 'Contacts already exist; use a fresh world-shot candidate.'
    first, last = requested[0], requested[-1]
    count = int(math.ceil((last-first)*4))
    times = sorted(set(requested+[min(last, first+i*.25) for i in range(count+1)]))
    bpy.context.window.scene = scene
    original_frame = scene.frame_current+scene.frame_subframe
    collection = bpy.data.collections.new(COLLECTION)
    scene.collection.children.link(collection)
    marks = {b.name: {kind: _quad(collection, b, kind)
                     for kind in ('core', 'penumbra')} for b in boots}
    records = {b.name: [] for b in boots}
    before_checks = {}
    for f in times:
        _set_frame(scene, f)
        for boot in boots:
            points = _points(boot)
            assert points and all(math.isfinite(v) for p in points for v in p)
            measure = _measure(points, floor_fn)
            h = max(0, measure['clearance_m'])
            span = measure['effective_support_span_m']
            core = .36*(1-_smooth(.0005, .003, h))**2
            penumbra = .15*(1-_smooth(.002, .045, h))**2
            core_width = _clamp(span*.95, .022, .245)
            soft_width = _clamp(span*1.12+.030+.025*_smooth(0, .045, h), .065, .30)
            for kind, width, height, alpha, depth in [
                ('core', core_width, .006, core, .010),
                ('penumbra', soft_width, .018, penumbra, .014)]:
                ob, tree, opacity = marks[boot.name][kind]
                shadow_y = measure['support_y']+depth
                floor_z = float(floor_fn(shadow_y))
                ob.location = (measure['support_x'], shadow_y, floor_z-.001)
                ob.scale = (width, 1, height)
                ob.keyframe_insert('location', frame=f)
                ob.keyframe_insert('scale', frame=f)
                opacity.default_value = alpha
                opacity.keyframe_insert('default_value', frame=f)
            records[boot.name].append({'frame': f, **measure,
                'core_opacity': core, 'penumbra_opacity': penumbra,
                'core_width_m': core_width, 'penumbra_width_m': soft_width})
            if f in (first, last):
                before_checks[f, boot.name] = points
    # Explicit visibility bounds stop a held contact mark leaking into other
    # sections if this bounded shot is later linked into a longer edit.
    for objects in marks.values():
        for ob, tree, opacity in objects.values():
            for f, hidden in [(first-1, True), (first, False),
                              (last, False), (last+1, True)]:
                ob.hide_render = hidden
                ob.keyframe_insert('hide_render', frame=f)
            _linear(ob)
            _linear(tree)
    maximum_boot_change = 0.0
    for (f, name), original in before_checks.items():
        _set_frame(scene, f)
        now = _points(scene.objects[name])
        assert len(now) == len(original)
        maximum_boot_change = max(maximum_boot_change,
            max((a-b).length for a, b in zip(now, original)))
    assert maximum_boot_change < 1e-7
    per_boot = {}
    for name, rows in records.items():
        stance = [r for r in rows if r['clearance_m'] <= .0005]
        visible_swing = [r for r in rows if r['clearance_m'] >= .003]
        assert all(r['core_opacity'] == 0 for r in visible_swing)
        indices = sorted(set([0, len(rows)-1]+
            [i for i, r in enumerate(rows) if abs((r['frame']-first) % 12) < 1e-8]))
        per_boot[name] = {'sample_count': len(rows),
            'sole_clearance_m': _ranges(rows, 'clearance_m'),
            'core_opacity': _ranges(rows, 'core_opacity'),
            'penumbra_opacity': _ranges(rows, 'penumbra_opacity'),
            'core_width_m': _ranges(rows, 'core_width_m'),
            'penumbra_width_m': _ranges(rows, 'penumbra_width_m'),
            'geometric_stance_samples_below_half_mm': len(stance),
            'maximum_stance_floor_error_m': max(abs(r['clearance_m']) for r in stance) if stance else None,
            'visible_swing_samples_at_or_above_3mm': len(visible_swing),
            'visible_swing_core_opacity_is_zero': True,
            'key_samples': [rows[i] for i in indices]}
    _set_frame(scene, original_frame)
    return {'method': 'Evaluated-geometry-driven native painted contact core and penumbra; no physical-shadow claim.',
        'collection': collection.name,
        'objects': [ob.name for objects in marks.values() for ob, tree, opacity in objects.values()],
        'range': [first, last], 'quarter_production_samples_per_boot': len(times),
        'core_height_m': .006, 'penumbra_height_m': .018,
        'opacity_clearance_thresholds_m': {'core_full_below': .0005, 'core_zero_at': .003,
                                         'penumbra_full_below': .002, 'penumbra_zero_at': .045},
        'support_measurement': 'Smooth weighted six-millimetre lower envelope; world floor clearance includes each evaluated vertex Y.',
        'foot_geometry_or_animation_edited': False,
        'endpoint_evaluated_boot_vertex_change_m': maximum_boot_change,
        'object_origins': 'At each animated world contact centre for transparent sorting; quads stay in camera-facing XZ.',
        'per_boot': per_boot,
        'limits': 'These are painted grounding cues, not physically simulated shadows. A geometric contact threshold is not a gait-phase label. Inspect actual full-shot and native-pixel foot crops for darkness, intersection and sorting.'}
