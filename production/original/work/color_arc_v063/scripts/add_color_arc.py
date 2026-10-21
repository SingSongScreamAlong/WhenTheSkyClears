"""Shared full-color to charcoal arc on copied drawn-character materials only."""
import bpy

NAME = 'V063 | shared color to charcoal | both children'
PROP = 'charcoal_progress'
SCHEDULE = [(0, 0.), (18, .08), (35, .28), (50, .48), (67, .72),
            (80, .88), (90, .96), (96, 1.), (100, 1.)]
TONES = [(0., .006), (.06, .014), (.22, .032), (.5, .068), (1., .12)]

def _surface_nodes(tree):
    pending = [link.from_node for node in tree.nodes
               if node.type == 'OUTPUT_MATERIAL' and node.is_active_output
               for link in node.inputs['Surface'].links]
    seen = set()
    while pending:
        node = pending.pop()
        if node not in seen:
            seen.add(node)
            pending.extend(link.from_node for socket in node.inputs for link in socket.links)
    return seen

def _curves(action):
    try:
        return list(action.fcurves)
    except AttributeError:
        return [fc for layer in action.layers for strip in layer.strips
                for bag in getattr(strip, 'channelbags', ()) for fc in bag.fcurves]

def _feed(tree, value, target):
    if hasattr(value, 'is_output'):
        tree.links.new(value, target)
    else:
        target.default_value = value

def _node(tree, kind, label):
    node = tree.nodes.new(kind)
    node.name = 'V063 | ' + label
    node.label = label
    return node

def _controller(scene):
    assert bpy.data.objects.get(NAME) is None, 'Color arc controller already exists'
    ob = bpy.data.objects.new(NAME, None)
    scene.collection.objects.link(ob)
    ob.empty_display_type = 'PLAIN_AXES'
    ob.empty_display_size = .2
    ob[PROP] = 0.
    ob.id_properties_ui(PROP).update(min=0., max=1., soft_min=0., soft_max=1.,
        description='Shared full painted color (0) to neutral charcoal (1), both children')
    path = '["' + PROP + '"]'
    for seconds, value in SCHEDULE:
        ob[PROP] = value
        ob.keyframe_insert(data_path=path, frame=1 + 24 * seconds,
                          group='V063 | shared production color arc')
    curves = [fc for fc in _curves(ob.animation_data.action) if fc.data_path == path]
    assert len(curves) == 1, 'Expected exactly one shared progress F-curve'
    fc = curves[0]
    fc.extrapolation = 'CONSTANT'
    for key in fc.keyframe_points:
        key.interpolation = 'BEZIER'
        key.handle_left_type = 'AUTO_CLAMPED'
        key.handle_right_type = 'AUTO_CLAMPED'
    fc.update()
    values = [fc.evaluate(1 + 2400 * i / 1000) for i in range(1001)]
    diffs = [b-a for a, b in zip(values, values[1:])]
    assert min(values) >= -1e-7 and max(values) <= 1.0000001
    assert min(diffs) >= -1e-7, 'Shared progress curve is not monotonic'
    ob[PROP] = float(fc.evaluate(scene.frame_current + scene.frame_subframe))
    return ob, dict(samples=1001, minimum=min(values), maximum=max(values),
                    minimum_sample_step=min(diffs), monotonic=True,
                    interpolation='BEZIER / AUTO_CLAMPED', extrapolation='CONSTANT')

def _wrap(mat, controller):
    tree = mat.node_tree
    emissions = sorted((node for node in _surface_nodes(tree) if node.type == 'EMISSION'),
                       key=lambda node: node.name)
    for emission in emissions:
        color = emission.inputs['Color']
        source = color.links[0].from_socket if color.is_linked else tuple(color.default_value)
        luma = _node(tree, 'ShaderNodeRGBToBW', 'source painted luminance / ' + emission.name)
        _feed(tree, source, luma.inputs[0])
        ramp = _node(tree, 'ShaderNodeValToRGB', 'neutral charcoal painted values / ' + emission.name)
        ramp.color_ramp.interpolation = 'EASE'
        elements = ramp.color_ramp.elements
        elements[0].position = TONES[0][0]
        elements[0].color = (TONES[0][1],) * 3 + (1.,)
        elements[1].position = TONES[-1][0]
        elements[1].color = (TONES[-1][1],) * 3 + (1.,)
        for position, value in TONES[1:-1]:
            elements.new(position).color = (value, value, value, 1.)
        tree.links.new(luma.outputs[0], ramp.inputs['Fac'])
        mix = _node(tree, 'ShaderNodeMixRGB', 'shared color to charcoal / ' + emission.name)
        mix.blend_type = 'MIX'
        mix.use_clamp = False
        _feed(tree, source, mix.inputs[1])
        tree.links.new(ramp.outputs['Color'], mix.inputs[2])
        driver = mix.inputs[0].driver_add('default_value').driver
        variable = driver.variables.new()
        variable.name = 'progress'
        variable.type = 'SINGLE_PROP'
        variable.targets[0].id = controller
        variable.targets[0].data_path = '["' + PROP + '"]'
        driver.expression = 'progress'
        tree.links.new(mix.outputs[0], color)
    return [node.name for node in emissions]

def apply(scene, actors):
    """Caller supplies all hero/gesture meshes and owns opening, saving and rendering."""
    assert scene.render.fps / scene.render.fps_base == 24, 'Arc is specified at24fps'
    meshes = sorted({ob for ob in actors if ob.type == 'MESH'}, key=lambda ob: ob.name)
    assert meshes, 'No actor meshes supplied'
    for ob in meshes:
        for slot in ob.material_slots:
            assert not slot.material or not slot.material.get('V063_color_arc'), 'Arc already applied'
    controller, verification = _controller(scene)
    report = dict(controller=controller.name, property=PROP, fps=24,
        schedule=[dict(seconds=s, frame=1+24*s, progress=p) for s, p in SCHEDULE],
        curve_verification=verification, tonal_ramp=TONES, ramp_interpolation='EASE',
        objects=[], materials=[], skipped=[])
    cache = {}
    for ob in meshes:
        coverage = []
        for index, slot in enumerate(ob.material_slots):
            original = slot.material
            reason = ('empty material slot' if not original else
                      'material has no nodes' if not original.use_nodes else
                      'no reachable surface Emission' if not any(
                          n.type == 'EMISSION' for n in _surface_nodes(original.node_tree)) else None)
            if reason:
                report['skipped'].append(dict(object=ob.name, slot=index, reason=reason))
                continue
            identity = original.as_pointer()
            if identity not in cache:
                mat = original.copy()
                mat.surface_render_method = 'DITHERED'
                mat.name = 'V063 | shared color arc | ' + original.name
                channels = _wrap(mat, controller)
                mat['V063_color_arc'] = True
                cache[identity] = mat
                report['materials'].append(dict(source=original.name, copy=mat.name,
                    emission_channels=channels, surface_render_method=mat.surface_render_method))
            mat = cache[identity]
            slot.link = 'OBJECT'
            slot.material = mat
            coverage.append(dict(slot=index, source=original.name, copy=mat.name))
        report['objects'].append(dict(name=ob.name, currently_hidden=ob.hide_render,
                                      slots=coverage))
    report['object_count'] = len(report['objects'])
    report['material_count'] = len(report['materials'])
    report['limits'] = [
        'Only supplied actor meshes are eligible; caller must include every boot, limb and gesture mesh.',
        'Hidden supplied meshes are included for later visibility; world materials are not traversed.',
        'Full-color endpoint is the existing painted material: no outfit palette or source image changes.',
        'Neutral charcoal is a tonal treatment of the same paint, not newly drawn expressions or anatomy.',
        'Alpha paths, UVs, packed pixels, geometry, poses and original Emission Strength remain unchanged.',
        'DITHERED copies retain the diagnosed DOF fix; native sequence must be reviewed for dither stability.',
        'Surface Emission inside shader node groups is not rewritten; skipped slots require caller review.',
        'No native open, save or render is performed by this helper.',
    ]
    return report
