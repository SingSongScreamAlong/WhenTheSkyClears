"""Localized native paint response. Caller owns scene staging, timing and saves."""
from mathutils import Vector
def apply(scene, actor_objects, event, prefix='V060'):
    assert event.type == 'EMPTY' and all(k in event for k in ('pulse', 'settle'))
    actors = {o for o in actor_objects if o.type == 'MESH' and not o.hide_render}
    report = {'objects': [], 'materials': [], 'skipped': []}
    cache = {}
    marker = prefix + ' | painted light'
    ex = (event.matrix_world.translation if event.parent else event.location).x
    world_names = {
        'v020 | Walking path | continuous blended paint',
        'v020 | Foreground bank | continuous blended paint',
        'v016 | Woods | near rooted oaks',
        'v048 | peaceful fixed foreground soil bank',
        'v048 | transition fixed foreground soil bank',
    }
    world = []
    for ob in scene.objects:
        if ob in actors or ob.type != 'MESH' or ob.hide_render:
            continue
        if ob.name not in world_names and not ob.name.startswith('v030 | High crown foreground oak '):
            continue
        corners = [ob.matrix_world @ Vector(p) for p in ob.bound_box]
        if min(p.x for p in corners) <= ex+14 and max(p.x for p in corners) >= ex-14 and min(p.y for p in corners) < 12 and max(p.y for p in corners) > -8:
            world.append(ob)
    def who(ob):
        lineage = []
        while ob:
            lineage.append(ob.name.upper())
            ob = ob.parent
        text = ' '.join(lineage)
        return 'girl' if 'GIRL' in text else 'boy' if 'BOY' in text else 'actor'
    def reachable_emissions(nt):
        pending = [l.from_node for n in nt.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output for l in n.inputs['Surface'].links]
        seen = set()
        while pending:
            node = pending.pop()
            if node in seen:
                continue
            seen.add(node)
            pending.extend(l.from_node for s in node.inputs for l in s.links)
        return [n for n in seen if n.type == 'EMISSION']
    def patch(original, kind):
        key = (original.as_pointer(), kind)
        if key in cache:
            return cache[key]
        if not original.use_nodes or not original.node_tree:
            return None
        if any(n.name == marker for n in original.node_tree.nodes):
            raise RuntimeError('Paint response already applied: ' + original.name)
        if not reachable_emissions(original.node_tree):
            report['skipped'].append(original.name + ': no surface Emission')
            return None
        mat = original.copy()
        mat.name = prefix + ' | ' + kind + ' light | ' + original.name
        nt = mat.node_tree
        def node(node_type, label):
            n = nt.nodes.new(node_type)
            n.name = marker if label == 'position' else prefix + ' | ' + label
            return n
        def wire(socket, value):
            if hasattr(value, 'is_output'):
                nt.links.new(value, socket)
            else:
                socket.default_value = value
        def calc(operation, a, b):
            n = node('ShaderNodeMath', operation)
            n.operation = operation
            wire(n.inputs[0], a)
            wire(n.inputs[1], b)
            return n.outputs[0]
        def ramp(source, lo, hi, a, b):
            n = node('ShaderNodeMapRange', 'bounded local falloff')
            n.clamp = True
            n.interpolation_type = 'SMOOTHERSTEP'
            for name, value in [('From Min', lo), ('From Max', hi), ('To Min', a), ('To Max', b)]:
                n.inputs[name].default_value = value
            wire(n.inputs[0], source)
            return n.outputs[0]
        def control(prop):
            n = node('ShaderNodeValue', prop)
            f = n.outputs[0].driver_add('default_value')
            f.driver.expression = 'min(1,max(0,v))'
            v = f.driver.variables.new()
            v.name = 'v'
            v.type = 'SINGLE_PROP'
            v.targets[0].id = event
            v.targets[0].data_path = '["' + prop + '"]'
            return n.outputs[0]
        position = node('ShaderNodeNewGeometry', 'position').outputs['Position']
        source = node('ShaderNodeCombineXYZ', 'fixed source world position')
        for i, axis in enumerate(('LOC_X', 'LOC_Y', 'LOC_Z')):
            f = source.inputs[i].driver_add('default_value')
            f.driver.expression = 'p'
            v = f.driver.variables.new()
            v.name = 'p'
            v.type = 'TRANSFORMS'
            v.targets[0].id = event
            v.targets[0].transform_type = axis
            v.targets[0].transform_space = 'WORLD_SPACE'
        distance = node('ShaderNodeVectorMath', 'distance to fixed event')
        distance.operation = 'DISTANCE'
        wire(distance.inputs[0], position)
        wire(distance.inputs[1], source.outputs[0])
        weight = ramp(distance.outputs['Value'], 2, 14, 1, 0)
        if kind == 'world':
            point_z = node('ShaderNodeSeparateXYZ', 'receiver height')
            light_z = node('ShaderNodeSeparateXYZ', 'source height')
            wire(point_z.inputs[0], position)
            wire(light_z.inputs[0], source.outputs[0])
            delta_z = calc('SUBTRACT', point_z.outputs['Z'], light_z.outputs['Z'])
            weight = calc('MULTIPLY', weight, ramp(delta_z, -1, .5, 1, 0))
        pulse = calc('MULTIPLY', control('pulse'), weight)
        settle = calc('MULTIPLY', control('settle'), weight)
        saturation = calc('SUBTRACT', 1, calc('MULTIPLY', settle, .04))
        value = calc('MULTIPLY', .90 if kind == 'boy' else 1., calc('SUBTRACT', 1, calc('MULTIPLY', settle, 1-2**(-.1))))
        gain = node('ShaderNodeCombineXYZ', 'restrained warm-white multiplicative gain')
        amplitude = 2**(.12 if kind == 'world' else .20)-1
        for i, tint in enumerate((1., .985, .95)):
            wire(gain.inputs[i], calc('ADD', 1, calc('MULTIPLY', pulse, amplitude*tint)))
        emissions = reachable_emissions(nt)
        for em in emissions:
            color = em.inputs['Color']
            old = color.links[0].from_socket if color.is_linked else tuple(color.default_value)
            hsv = node('ShaderNodeHueSaturation', 'preserved pigment / local settle')
            wire(hsv.inputs['Color'], old)
            wire(hsv.inputs['Saturation'], saturation)
            wire(hsv.inputs['Value'], value)
            mix = node('ShaderNodeMixRGB', 'local flash on original paint')
            mix.blend_type = 'MULTIPLY'
            mix.inputs[0].default_value = 1
            wire(mix.inputs[1], hsv.outputs['Color'])
            wire(mix.inputs[2], gain.outputs[0])
            wire(color, mix.outputs[0])
        report['materials'].append(dict(source=original.name, copy=mat.name, kind=kind, emissions=[n.name for n in emissions]))
        cache[key] = mat
        return mat
    for ob in sorted(actors | set(world), key=lambda o: o.name):
        kind = who(ob) if ob in actors else 'world'
        assignments = [(i, m) for i, s in enumerate(ob.material_slots) if s.material and (m := patch(s.material, kind))]
        if not assignments:
            continue
        for i, mat in assignments:
            ob.material_slots[i].link = 'OBJECT'
            ob.material_slots[i].material = mat
        report['objects'].append({'name': ob.name, 'kind': kind})
    report['limits'] = ['Paint response only; original UV/alpha/pixels/Strength/geometry/timing preserved. No occlusion, rim or new shadows.',
        'Named near receivers only; 14m falloff and world-height mask exclude sky.',
        'Pre-attenuation flash: actors .20EV/world .12EV; settle 4% saturation/.10EV value.']
    return report
