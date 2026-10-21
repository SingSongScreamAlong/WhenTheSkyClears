"""Native EEVEE ink/wash surface materials; caller owns staging, saves and renders."""
import bpy

def _node(tree, kind, label):
    node = tree.nodes.new(kind)
    node.name = 'V061 | ' + label
    node.label = label
    return node

def _wire(tree, socket, value):
    if hasattr(value, 'is_output'):
        tree.links.new(value, socket)
    else:
        socket.default_value = value

def _math(tree, operation, a, b, label=None):
    node = _node(tree, 'ShaderNodeMath', label or operation)
    node.operation = operation
    _wire(tree, node.inputs[0], a)
    _wire(tree, node.inputs[1], b)
    return node.outputs[0]

def _ramp(tree, source, stops, label):
    node = _node(tree, 'ShaderNodeValToRGB', label)
    node.color_ramp.interpolation = 'EASE'
    ramp = node.color_ramp
    while len(ramp.elements) > 2:
        ramp.elements.remove(ramp.elements[-1])
    ramp.elements[0].position, ramp.elements[0].color = stops[0]
    ramp.elements[1].position, ramp.elements[1].color = stops[-1]
    for position, color in stops[1:-1]:
        ramp.elements.new(position).color = color
    _wire(tree, node.inputs['Fac'], source)
    return node.outputs['Color']

def _multiply(tree, a, b, label):
    node = _node(tree, 'ShaderNodeMixRGB', label)
    node.blend_type = 'MULTIPLY'
    node.inputs[0].default_value = 1
    _wire(tree, node.inputs[1], a)
    _wire(tree, node.inputs[2], b)
    return node.outputs[0]

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

def _identity(ob):
    names = []
    while ob:
        names.append(ob.name.upper())
        ob = ob.parent
    text = ' '.join(names)
    return 'girl' if 'GIRL' in text else 'boy' if 'BOY' in text else 'actor'

def _pigment(tree, scale, low, high, label):
    coords = _node(tree, 'ShaderNodeTexCoord', label + ' object coordinates')
    noise = _node(tree, 'ShaderNodeTexNoise', label + ' fixed pigment grain')
    noise.inputs['Scale'].default_value = scale
    noise.inputs['Detail'].default_value = 1.2
    noise.inputs['Roughness'].default_value = .55
    tree.links.new(coords.outputs['Object'], noise.inputs['Vector'])
    gain = _math(tree, 'ADD', low,
                 _math(tree, 'MULTIPLY', noise.outputs['Fac'], high-low), label + ' grain gain')
    return gain, noise.outputs['Fac'], coords.outputs['Object']

def apply(scene, actors, event):
    """Multiply original illustrated pigments by actual native light and shadows."""
    assert scene.render.engine == 'BLENDER_EEVEE', 'ShaderToRGB requires native EEVEE'
    report = dict(objects=[], materials=[], skipped=[], engine=scene.render.engine,
                  event=event.name if event else None, normal_world=[0, -1, 0])
    cache = {}
    visible = sorted({ob for ob in actors if ob.type == 'MESH' and not ob.hide_render}, key=lambda ob: ob.name)
    for ob in visible:
        kind = _identity(ob)
        replacements = []
        for index, slot in enumerate(ob.material_slots):
            original = slot.material
            if not original or not original.use_nodes:
                continue
            key = (original.as_pointer(), kind)
            if key not in cache:
                assert not original.get('V061_actual_light_wash'), 'Wash already applied: ' + original.name
                if not any(node.type == 'EMISSION' for node in _surface_nodes(original.node_tree)):
                    report['skipped'].append(original.name + ': no surface Emission')
                    continue
                mat = original.copy()
                mat.surface_render_method = 'DITHERED'
                mat.name = 'V061 | actual-light ' + kind + ' wash | ' + original.name
                tree = mat.node_tree
                emissions = [node for node in _surface_nodes(tree) if node.type == 'EMISSION']
                diffuse = _node(tree, 'ShaderNodeBsdfDiffuse', 'actual light receiver / illustration normal')
                diffuse.inputs['Color'].default_value = (1, 1, 1, 1)
                diffuse.inputs['Roughness'].default_value = 1
                diffuse.inputs['Normal'].default_value = (0, -1, 0)
                light = _node(tree, 'ShaderNodeShaderToRGB', 'actual EEVEE irradiance and shadows')
                tree.links.new(diffuse.outputs[0], light.inputs['Shader'])
                luma = _node(tree, 'ShaderNodeRGBToBW', 'light intensity preserves source hue')
                tree.links.new(light.outputs['Color'], luma.inputs[0])
                intensity = _math(tree, 'MULTIPLY', luma.outputs[0], 1., 'irradiance calibration / tune after actual keys')
                levels = (.86, .98, 1.07) if kind == 'girl' else (.72, .91, 1.07)
                stops = [(position, (value, value, value, 1))
                         for position, value in zip((.08, .40, .90), levels)]
                wash = _ramp(tree, intensity, stops, 'three broad soft light / wash values')
                pigment, _, _ = _pigment(tree, 85., .985, 1.015, 'illustrated surface')
                gain = _multiply(tree, wash, pigment, 'actual light with subtle local pigment')
                for emission in emissions:
                    color = emission.inputs['Color']
                    old_color = color.links[0].from_socket if color.is_linked else tuple(color.default_value)
                    tree.links.new(_multiply(tree, old_color, gain, 'original pigment times light'), color)
                mat['V061_actual_light_wash'] = True
                cache[key] = mat
                report['materials'].append(dict(source=original.name, copy=mat.name, identity=kind,
                    wash_levels=list(levels), irradiance_stops=[.08, .40, .90],
                    surface_render_method=mat.surface_render_method,
                    render_method_reason='4K DOF diagnosis: BLENDED softened faces/hands; DITHERED retains focus at f/5.6.',
                    emission_channels=[node.name for node in emissions],
                    retained_v060_response=any(node.name.startswith('V060') for node in tree.nodes)))
            replacements.append((index, cache[key]))
        for index, mat in replacements:
            ob.material_slots[index].link = 'OBJECT'
            ob.material_slots[index].material = mat
        if replacements:
            report['objects'].append(dict(name=ob.name, identity=kind))
    report['limits'] = [
        'Actual native EEVEE lighting/shadows; not supported as the same look in Cycles.',
        'Constant camera-facing world normal suits drawn planes; no invented 3D facial anatomy.',
        'Original pigment chains, alpha, UVs, image pixels and Emission Strength remain intact.',
        'No outlines or screen filter. Fine Object-space grain can move within strongly deforming art.',
        'Existing V060 pulse/edge chains remain; inspect against physical flash to avoid double emphasis.',
        'Light ramp needs actual-key calibration; finite shadow floors deliberately preserve palette.',
    ]
    return report

def matte_material(name, palette, roughness=.9):
    """Opaque environment paint. Palette is three linear RGB(A) colors or one RGB."""
    values = list(palette)
    if len(values) == 3 and all(isinstance(value, (int, float)) for value in values):
        colors = [tuple(max(0, component*gain) for component in values) + (1,)
                  for gain in (.66, .90, 1.04)]
    else:
        assert len(values) == 3, 'Provide dark/mid/light paint colors'
        colors = [tuple(value[:3]) + (1,) for value in values]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.diffuse_color = colors[1]
    tree = mat.node_tree
    tree.nodes.clear()
    output = _node(tree, 'ShaderNodeOutputMaterial', 'opaque painted surface')
    bsdf = _node(tree, 'ShaderNodeBsdfPrincipled', 'matte pigment / actual environmental light')
    bsdf.inputs['Roughness'].default_value = max(.75, min(1., roughness))
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = .15
    grain, grain_fac, coordinates = _pigment(tree, 70., .965, 1.015, 'environment')
    masses = _node(tree, 'ShaderNodeTexNoise', 'broad object-anchored wash masses')
    masses.inputs['Scale'].default_value = 2.3
    masses.inputs['Detail'].default_value = 1
    tree.links.new(coordinates, masses.inputs['Vector'])
    color = _ramp(tree, masses.outputs['Fac'], list(zip((.18, .50, .82), colors)), 'selected paint palette')
    ao = _node(tree, 'ShaderNodeAmbientOcclusion', 'local pigment pools in actual creases')
    ao.inputs['Distance'].default_value = .14
    if hasattr(ao, 'samples'):
        ao.samples = 16
    pooling = _math(tree, 'ADD', .86, _math(tree, 'MULTIPLY', ao.outputs['AO'], .14))
    tree.links.new(_multiply(tree, color, _math(tree, 'MULTIPLY', grain, pooling),
                            'pigment variation and local pooling'), bsdf.inputs['Base Color'])
    bump = _node(tree, 'ShaderNodeBump', 'restrained physical paint tooth')
    bump.inputs['Strength'].default_value = .08
    bump.inputs['Distance'].default_value = .004
    tree.links.new(grain_fac, bump.inputs['Height'])
    tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    mat['V061_surface_kind'] = 'Opaque actual-light rough paint; local object-space wash/pigment and crease pooling'
    return mat
