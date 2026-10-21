"""Owned native understory finish; no file, render, camera or hero operations."""
import bpy
import math
import random
from mathutils import Vector

def apply_environment_finish(scene, collection):
    assert collection.name.startswith('V061'), 'Only the owned production-look collection is supported'
    label = 'V061 | finish | understory paint masses'
    assert not any(c.name == label for c in collection.children), 'Understory finish already applied'
    root = scene.objects.get('V047 | shared travel | steady .73125mps')
    assert root, 'Current steady pair root is required for shot-space composition'
    # Read the existing evaluated hero position; never advance or alter its clock.
    start_x = root.matrix_world.translation.x - (scene.frame_current-937)*.73125/24
    end_x = start_x + 119*.73125/24
    rng = random.Random(61061)
    target = bpy.data.collections.new(label)
    collection.children.link(target)
    report = dict(hidden_stems=[], objects=[], clusters=[], hero_start_x=start_x,
                  hero_end_x=end_x, clear_walking_lane_y=[-1., 2.2])
    for ob in collection.all_objects:
        if ob.name.startswith('V061 | rooted understory stem '):
            ob.hide_render = True
            ob.hide_viewport = True
            report['hidden_stems'].append(ob.name)
    def height(x, y):
        z = .7713720202445984
        if y < -1.05:
            z -= .20*(-1.05-y) + .025*math.sin(x*.91+y)
        elif y > 2.2:
            z += .040*(y-2.2) + .07*math.sin(x*.39+y*.7)
        if y < -.9 or y > 2:
            z += .015*math.sin(x*3.7+y*2.1)*math.sin(y*3)
        return z
    def material(name, color):
        mat = bpy.data.materials.new('V061 | finish | ' + name)
        mat.use_nodes = True
        tree = mat.node_tree
        bsdf = tree.nodes.get('Principled BSDF')
        bsdf.inputs['Roughness'].default_value = .96
        bsdf.inputs['Specular IOR Level'].default_value = .08
        coords = tree.nodes.new('ShaderNodeTexCoord')
        noise = tree.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 3.1
        noise.inputs['Detail'].default_value = 1
        tree.links.new(coords.outputs['Object'], noise.inputs['Vector'])
        ramp = tree.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.interpolation = 'EASE'
        ramp.color_ramp.elements[0].position = .18
        ramp.color_ramp.elements[0].color = tuple(c*.78 for c in color) + (1,)
        ramp.color_ramp.elements[1].position = .82
        ramp.color_ramp.elements[1].color = tuple(c*1.13 for c in color) + (1,)
        tree.links.new(noise.outputs['Fac'], ramp.inputs[0])
        tree.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
        mat.diffuse_color = (*color, 1)
        return mat
    mats = [
        material('pooled olive underpainting', (.025, .043, .025)),
        material('deep brush leaves', (.042, .074, .035)),
        material('olive brush leaves', (.082, .126, .052)),
        material('sparse light brush leaves', (.15, .205, .085)),
    ]
    def mesh(name, vertices, faces, indices):
        me = bpy.data.meshes.new(name)
        me.from_pydata(vertices, [], faces)
        me.update()
        for mat in mats:
            me.materials.append(mat)
        ob = bpy.data.objects.new(name, me)
        target.objects.link(ob)
        ob['V061_owned_finish'] = True
        for polygon, index in zip(me.polygons, indices):
            polygon.material_index = index
        report['objects'].append(ob.name)
        return ob
    # No smooth core volumes: overlapping curved leaves carry the whole silhouette.
    # Uneven branch sprays create peaks, notches and low root-connected growth.
    specs = [
        (-7.3, 3.7, 1.4, .65, .48), (-5.4, 4.8, 1.45, .80, .76),
        (-3.2, 3.4, .95, .57, .38), (-1.5, 4.5, 1.70, .90, .54),
        (.9, 3.15, .95, .45, .28), (3.0, 4.4, 1.20, .74, .39),
        (4.9, 3.5, .90, .55, .32), (6.8, 4.9, 1.60, .85, .68),
        (8.9, 3.4, 1.30, .62, .48), (-5.8, 7.2, 1.80, 1., .95),
        (-2.2, 8.4, 1.65, .95, .55), (2.3, 7.4, 1.80, 1., .83),
        (6.9, 8.5, 1.80, 1., .72), (-4.4, -2.6, 1.20, .62, .32),
        (-6.3, -3.8, 1.50, .85, .44), (8.4, -2.9, 1.40, .70, .35),
        (10.5, -4.1, 1.60, .80, .38),
    ]
    weights = [rx*ry+.25 for _, _, rx, ry, _ in specs]
    total_weight = sum(weights)
    def twig(name, points, radius):
        curve = bpy.data.curves.new(name, 'CURVE')
        curve.dimensions = '3D'
        curve.bevel_depth = radius
        curve.bevel_resolution = 1
        spline = curve.splines.new('POLY')
        spline.points.add(len(points)-1)
        for i, (point, value) in enumerate(zip(spline.points, points)):
            point.co = (*value, 1)
            point.radius = 1.-.8*i/(len(points)-1)
        ob = bpy.data.objects.new(name, curve)
        target.objects.link(ob)
        curve.materials.append(mats[0])
        ob['V061_owned_finish'] = True
        report['objects'].append(ob.name)
    for index, (offset, y, rx, ry, high) in enumerate(specs):
        x = start_x+offset
        if y > 0 and start_x-1.1 < x < end_x+1.1 and y < 5.5:
            high = min(high, .43)
        base = height(x, y)
        sprays = []
        number = 7+index%4
        for j in range(number):
            u = -1+(j+.22+rng.random()*.5)*2/number
            sx = x+rx*u
            sy = y+ry*rng.uniform(-.70, .70)
            h = high*rng.uniform(.38, 1.06)
            if (j+index)%5 == 2:
                h *= .30
            sz = height(sx, sy)+h
            sprays.append((Vector((sx, sy, sz)), rng.uniform(.17, .34), ry*rng.uniform(.16, .27), h))
            if j%2 == 0:
                foot = Vector((x-rx*.18, y+.10*ry, height(x-rx*.18, y+.10*ry)-.015))
                end = Vector((sx+rx*.13*u, sy, sz+.10))
                bend = foot.lerp(end, .55)+Vector((-.05*u, -.015, .035))
                twig('V061 | finish | broken ink branchspray %02d %02d'%(index, j),
                     [foot, bend, end], rng.uniform(.0016, .0030))
        vertices, faces, indices = [], [], []
        count = int(48000*weights[index]/total_weight)
        for leaf in range(count):
            center_spray, spread_x, spread_y, h = sprays[leaf%len(sprays)]
            # Volumetric overlapping foliage, with a low layer joining the roots.
            if rng.random() < .14:
                px = x+rx*rng.uniform(-1.03, 1.03)
                py = y+ry*rng.uniform(-.80, .80)
                center = Vector((px, py, height(px, py)+rng.uniform(.025, .15)))
            else:
                angle = rng.uniform(0, math.tau)
                radial = math.sqrt(rng.random())
                center = center_spray+Vector((spread_x*radial*math.cos(angle),
                    spread_y*radial*math.sin(angle), rng.uniform(-.11, .10)*(h/.4+.35)))
                center.z = max(height(center.x, center.y)+.035, center.z)
            normal = Vector((rng.uniform(-.36, .36), -rng.uniform(.48, .95),
                             rng.uniform(.45, .95))).normalized()
            a = normal.cross(Vector((0, 0, 1))).normalized()
            b = normal.cross(a).normalized()
            turn = rng.uniform(-1.15, 1.15) if rng.random() < .8 else rng.uniform(0, math.tau)
            axis = (a*math.cos(turn)+b*math.sin(turn)).normalized()
            cross = normal.cross(axis).normalized()
            length = rng.uniform(.055, .105)*(1.08 if y < 0 else 1)
            width = length*rng.uniform(.44, .68)
            points = [center-axis*length, center-axis*length*.43+cross*width,
                center+axis*length*.38+cross*width*.88, center+axis*length,
                center+axis*length*.36-cross*width*.93, center-axis*length*.43-cross*width*.9,
                center+normal*rng.uniform(.006, .017)]
            assert all(p.y < -1 or p.y > 2.2 for p in points)
            first = len(vertices)
            vertices.extend(tuple(point) for point in points)
            mi = rng.choices([1, 2, 3], [.50, .43, .07])[0]
            for j in range(6):
                faces.append((first+j, first+6, first+(j+1)%6))
                indices.append(mi)
        foliage = mesh('V061 | finish | wild interlocking brush foliage %02d'%index, vertices, faces, indices)
        for polygon in foliage.data.polygons:
            polygon.use_smooth = True
        report['clusters'].append(dict(center=[x, y, base], radius=[rx, ry],
            maximum_spray_height=high, leaves=count, visible_smooth_core=False, branch_sprays=number))
    report['understory_leaf_count'] = sum(group['leaves'] for group in report['clusters'])
    # Frontal key direction is roughly (-.8,+1,-1): these offscreen boughs
    # throw broken leaf shadows onto the walking lane, leaving a central pool.
    trunks = [o for o in collection.all_objects if 'oak 05 | asymmetric solid trunk' in o.name]
    bark = trunks[0].data.materials[0] if trunks else mats[0]
    anchor = (55., -2.6, 4.18)
    report['overhangs'] = []
    for index, (cx, cy, cz, rx, ry) in enumerate([
            (start_x+2.4, -3.55, 4.50, 1.20, .62),
            (start_x+6.35, -3.75, 4.63, 1.30, .65)]):
        points = [Vector(anchor), Vector(((anchor[0]+cx)*.5, -3.2, 4.56)), Vector((cx, cy, cz))]
        vertices, faces, uvs = [], [], []
        for row, (point, radius) in enumerate(zip(points, (.065, .044, .014))):
            tangent = (points[min(row+1, 2)]-points[max(0, row-1)]).normalized()
            a = tangent.cross(Vector((0, 0, 1))).normalized()
            b = tangent.cross(a).normalized()
            for j in range(12):
                angle = math.tau*j/12
                vertices.append(tuple(point+radius*(a*math.cos(angle)+b*math.sin(angle))))
                uvs.append((j/11, row/2))
        for row in range(2):
            for j in range(12):
                a = row*12+j
                b = row*12+(j+1)%12
                faces.append((a, b, b+12, a+12))
        branch = mesh('V061 | finish | overhanging shadow bough %d'%index, vertices, faces, [0]*len(faces))
        branch.data.materials[0] = bark
        uv = branch.data.uv_layers.new(name='V061 full bark pigment UV')
        for loop in branch.data.loops:
            uv.data[loop.index].uv = uvs[loop.vertex_index]
        for polygon in branch.data.polygons:
            polygon.use_smooth = True
        vertices, faces, indices = [], [], []
        for leaf in range(270):
            angle = rng.uniform(0, math.tau)
            radial = math.sqrt(rng.random())
            center = Vector((cx+rx*radial*math.cos(angle), cy+ry*radial*math.sin(angle),
                             cz+.18*(1-radial)+rng.uniform(-.11, .09)))
            turn = rng.uniform(0, math.tau)
            length = rng.uniform(.055, .10)
            axis = Vector((math.cos(turn), math.sin(turn), rng.uniform(-.3, .25))).normalized()*length
            cross = Vector((-axis.y, axis.x, .18*length)).normalized()*length*.52
            first = len(vertices)
            points_leaf = [center-axis, center-axis*.42+cross, center+axis*.36+cross,
                           center+axis, center+axis*.36-cross, center-axis*.42-cross,
                           center+Vector((0, 0, .012))]
            vertices.extend(tuple(point) for point in points_leaf)
            mi = rng.choices([1, 2, 3], [.48, .45, .07])[0]
            for j in range(6):
                faces.append((first+j, first+6, first+(j+1)%6))
                indices.append(mi)
        foliage = mesh('V061 | finish | physical overhang shadow leaves %d'%index, vertices, faces, indices)
        origin = Vector((cx, cy, cz))
        for vertex in foliage.data.vertices:
            vertex.co -= origin
        foliage.location = origin
        curve = foliage.driver_add('rotation_euler', 1)
        curve.driver.expression = '.0014*sin((frame-937)/29+%s)'%(index*1.7)
        foliage['maximum_leaf_tip_sway_m'] = .003
        report['overhangs'].append(dict(leaves=foliage.name, bough=branch.name,
            center=list(origin), leaf_count=270, tip_sway_bound_m=.003))
    report['limits'] = [
        'No visible smooth cores: dense curved leaf volumes, irregular silhouettes and selective branchspray ink; no alpha vegetation cards.',
        'Only owned V061 stems hidden. Hero geometry/materials, floor, lights and camera untouched; native overhang leaves cast key shadows.',
        'Ground anchoring follows this branch physical terrain formula; revise if terrain changes.',
        'No new raster artwork or external assets. Actual keys and moving parallax require review.',
    ]
    return report
