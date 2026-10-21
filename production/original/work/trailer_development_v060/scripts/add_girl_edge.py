def apply(scene, event):
    def girl(ob):
        while ob:
            if 'GIRL' in ob.name.upper():
                return True
            ob = ob.parent
        return False
    heads = [o for o in scene.objects if o.type == 'MESH' and not o.hide_render
             and o.get('proportion_role') == 'head' and girl(o)]
    assert len(heads) == 1, 'Expected one active girl head: ' + str([o.name for o in heads])
    ob = heads[0]
    report = {'object': ob.name, 'materials': []}
    def reachable(nt):
        pending = [l.from_node for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'
                   and n.is_active_output for l in n.inputs['Surface'].links]
        seen = set()
        while pending:
            n = pending.pop()
            if n not in seen:
                seen.add(n)
                pending.extend(l.from_node for s in n.inputs for l in s.links)
        return seen
    for index, slot in enumerate(ob.material_slots):
        original = slot.material
        if not original or not original.use_nodes:
            continue
        assert not original.get('V060_girl_edge'), 'Head edge already applied'
        mat = original.copy()
        mat.name = 'V060 | subtle head edge | ' + original.name
        nt = mat.node_tree
        nodes = reachable(nt)
        textures = [n for n in nodes if n.type == 'TEX_IMAGE' and n.image
                    and 'Pair_Painterly_Near_Age' in n.image.name]
        assert textures, 'Original pair image not found in active girl head material'
        tex = max(textures, key=lambda n: len(n.outputs['Alpha'].links))
        assert tex.projection == 'FLAT', 'Atlas offsets require FLAT projection'
        width, height = tex.image.size
        assert width > 0 and height > 0
        def new(kind, label):
            n = nt.nodes.new(kind)
            n.name = 'V060 head edge | ' + label
            return n
        def mathn(operation, a, b):
            n = new('ShaderNodeMath', operation)
            n.operation = operation
            for i, value in enumerate((a, b)):
                if hasattr(value, 'is_output'):
                    nt.links.new(value, n.inputs[i])
                else:
                    n.inputs[i].default_value = value
            return n.outputs[0]
        if tex.inputs['Vector'].is_linked:
            uv = tex.inputs['Vector'].links[0].from_socket
            mapping = 'Preserved original incoming Vector chain'
        else:
            assert ob.data.uv_layers.active, 'Girl head has no active UV layer'
            uv_node = new('ShaderNodeUVMap', 'original active UV')
            uv_node.uv_map = ob.data.uv_layers.active.name
            uv = uv_node.outputs['UV']
            mapping = 'Original active UV: ' + uv_node.uv_map
        edges = []
        for label, offset in [('right', (1.2/width, 0, 0)), ('top', (0, 1.2/height, 0))]:
            shift = new('ShaderNodeVectorMath', label + ' 1.2 source texels')
            shift.operation = 'ADD'
            nt.links.new(uv, shift.inputs[0])
            shift.inputs[1].default_value = offset
            sample = new('ShaderNodeTexImage', label + ' original atlas alpha')
            sample.image = tex.image
            sample.interpolation = tex.interpolation
            sample.extension = tex.extension
            sample.projection = tex.projection
            nt.links.new(shift.outputs['Vector'], sample.inputs['Vector'])
            edges.append(mathn('MAXIMUM', mathn('SUBTRACT', tex.outputs['Alpha'], sample.outputs['Alpha']), 0))
        pulse = new('ShaderNodeValue', 'source pulse')
        f = pulse.outputs[0].driver_add('default_value')
        f.driver.expression = 'min(1,max(0,p))'
        v = f.driver.variables.new()
        v.name = 'p'
        v.type = 'SINGLE_PROP'
        v.targets[0].id = event
        v.targets[0].data_path = '["pulse"]'
        gain = mathn('ADD', .026, mathn('MULTIPLY', pulse.outputs[0], .010))
        factor = mathn('MULTIPLY', mathn('MAXIMUM', edges[0], edges[1]), gain)
        for em in [n for n in nodes if n.type == 'EMISSION']:
            color = em.inputs['Color']
            assert color.is_linked, 'Expected original lit color chain'
            add = new('ShaderNodeMixRGB', 'interior warm-gray separation')
            add.blend_type = 'ADD'
            nt.links.new(factor, add.inputs[0])
            nt.links.new(color.links[0].from_socket, add.inputs[1])
            add.inputs[2].default_value = (.80, .78, .72, 1)
            nt.links.new(add.outputs[0], color)
        mat['V060_girl_edge'] = True
        slot.link = 'OBJECT'
        slot.material = mat
        report['materials'].append(dict(source=original.name, copy=mat.name, image=tex.image.name,
            pixels=[width, height], uv_mapping=mapping, texel_offset=1.2, max_linear_add=.0288))
    report['limits'] = 'Head only; original alpha/UV/pixels/Strength untouched. No body rim or normals/occlusion. Actual renders require review.'
    return report
