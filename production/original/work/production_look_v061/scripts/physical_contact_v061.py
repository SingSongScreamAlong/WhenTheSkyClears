"""Evaluated-sole grounding marks on the real flat v061 floor.

apply(scene, boots, frames, floor_z) creates only new native XY contact marks.
It never hides/deletes old marks, changes a boot, opens/saves a file or renders.
The caller owns old-contact visibility and native render review.
"""
import bpy
import math
import hashlib

COLLECTION = 'V061 | physical floor XY contact marks | measured sole support'


def _smooth(a,b,x):
    t = max(0.0,min(1.0,(x-a)/(b-a)))
    return t*t*(3.0-2.0*t)


def _clamp(x,lo,hi):
    return max(lo,min(hi,x))


def _frame(scene,f):
    n = math.floor(f)
    scene.frame_set(n,subframe=f-n)
    bpy.context.view_layer.update()


def _points(ob):
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = ev.to_mesh()
    try:
        return [ev.matrix_world@v.co for v in mesh.vertices]
    finally:
        ev.to_mesh_clear()


def _curves(action):
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    yield curve


def _action_hash(ob):
    if not ob.animation_data or not ob.animation_data.action:
        return None
    rows = [(f.data_path,f.array_index,f.extrapolation,
             [(tuple(k.co),k.interpolation) for k in f.keyframe_points],
             [(m.type,getattr(m,'mode_before',None),getattr(m,'mode_after',None))
              for m in f.modifiers]) for f in _curves(ob.animation_data.action)]
    return hashlib.sha256(repr(rows).encode()).hexdigest()


def _linear(block):
    if block.animation_data and block.animation_data.action:
        for fc in _curves(block.animation_data.action):
            fc.extrapolation = 'CONSTANT'
            for k in fc.keyframe_points:
                k.interpolation = 'CONSTANT' if fc.data_path=='hide_render' else 'LINEAR'


def _material(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.surface_render_method = 'BLENDED'
    nodes,links = mat.node_tree.nodes,mat.node_tree.links
    nodes.clear()
    uv = nodes.new('ShaderNodeTexCoord')
    radius = nodes.new('ShaderNodeVectorMath')
    radius.operation = 'DISTANCE'
    radius.inputs[1].default_value = (.5,.5,0.0)
    links.new(uv.outputs['UV'],radius.inputs[0])
    falloff = nodes.new('ShaderNodeMapRange')
    falloff.name = 'V061 | soft floor oval alpha'
    falloff.clamp = True
    falloff.interpolation_type = 'SMOOTHERSTEP'
    falloff.inputs['From Min'].default_value = 0.0
    falloff.inputs['From Max'].default_value = .5
    falloff.inputs['To Min'].default_value = 1.0
    falloff.inputs['To Max'].default_value = 0.0
    links.new(radius.outputs['Value'],falloff.inputs[0])
    opacity = nodes.new('ShaderNodeValue')
    opacity.name = 'V061 | evaluated sole clearance opacity'
    opacity.outputs[0].default_value = 0.0
    alpha = nodes.new('ShaderNodeMath')
    alpha.operation = 'MULTIPLY'
    links.new(falloff.outputs[0],alpha.inputs[0])
    links.new(opacity.outputs[0],alpha.inputs[1])
    clear = nodes.new('ShaderNodeBsdfTransparent')
    ink = nodes.new('ShaderNodeEmission')
    ink.inputs[0].default_value = (.010,.008,.006,1.0)
    mix = nodes.new('ShaderNodeMixShader')
    links.new(alpha.outputs[0],mix.inputs[0])
    links.new(clear.outputs[0],mix.inputs[1])
    links.new(ink.outputs[0],mix.inputs[2])
    out = nodes.new('ShaderNodeOutputMaterial')
    links.new(mix.outputs[0],out.inputs[0])
    return mat,opacity.outputs[0]


def _quad(collection,boot,kind):
    name = 'V061 floor contact '+kind+' | '+boot.name
    me = bpy.data.meshes.new(name)
    # Real horizontal world XY surface, positive-Z normal. No camera-facing card.
    me.from_pydata([(-.5,-.5,0.0),(.5,-.5,0.0),
                   (.5,.5,0.0),(-.5,.5,0.0)],[],[(0,1,2,3)])
    me.update()
    uv = me.uv_layers.new(name='V061 horizontal floor oval UV')
    for item,coord in zip(uv.data,[(0,0),(1,0),(1,1),(0,1)]):
        item.uv = coord
    mat,opacity = _material(name)
    me.materials.append(mat)
    ob = bpy.data.objects.new(name,me)
    collection.objects.link(ob)
    ob['V061_contact_boot'] = boot.name
    ob['V061_contact_kind'] = kind
    ob['V061_contact_plane'] = 'WORLD XY; z=real flat floor+1mm'
    ob['V061_contact_limit'] = 'Grounding paint driven by evaluated sole geometry; no physical-light shadow simulation claim.'
    return ob,mat.node_tree,opacity


def _measure(points,floor_z):
    heights = [p.z-floor_z for p in points]
    clearance = min(heights)
    weights = [(1.0-_smooth(0.0,.006,h-clearance))**2 for h in heights]
    total = sum(weights)
    if total <= 0:
        raise RuntimeError('Could not identify an evaluated sole lower envelope.')
    x = sum(p.x*w for p,w in zip(points,weights))/total
    y = sum(p.y*w for p,w in zip(points,weights))/total
    variance_x = sum(w*(p.x-x)**2 for p,w in zip(points,weights))/total
    lower = [p for p,h in zip(points,heights) if h<=clearance+.003]
    return {'clearance_m':clearance,'support_x':x,'support_y':y,
            'effective_support_span_x_m':2.8*math.sqrt(max(0.0,variance_x)),
            'lower_support_span_x_m':max(p.x for p in lower)-min(p.x for p in lower),
            'lower_support_count':len(lower),
            'evaluated_boot_x_span_m':max(p.x for p in points)-min(p.x for p in points),
            'evaluated_boot_y_span_m':max(p.y for p in points)-min(p.y for p in points)}


def _range(rows,key):
    values = [r[key] for r in rows]
    return {'minimum':min(values),'maximum':max(values)}


def apply(scene,boots,frames,floor_z):
    boots = list(boots)
    requested = sorted(set(float(f) for f in frames))
    floor_z = float(floor_z)
    if len(boots)!=4 or len({b.name for b in boots})!=4:
        raise RuntimeError('Expected four distinct evaluated original boots.')
    if not requested or not math.isfinite(floor_z):
        raise RuntimeError('Need a bounded frame interval and real flat floor Z.')
    if any(b.type!='MESH' or b.name not in scene.objects or b.hide_render for b in boots):
        raise RuntimeError('All four supplied boots must be visible meshes in the target scene.')
    if bpy.data.collections.get(COLLECTION):
        raise RuntimeError('Owned V061 contact collection exists; use a fresh staging copy.')
    first,last = requested[0],requested[-1]
    if first<937 or last>1056:
        raise RuntimeError('V061 contact pass is bounded to output frames937..1056.')
    count = int(math.ceil((last-first)*4))
    times = sorted(set(requested+[min(last,first+i*.25) for i in range(count+1)]))
    old_frame = scene.frame_current+scene.frame_subframe
    old_scene = bpy.context.window.scene
    bpy.context.window.scene = scene
    protected = set(boots)
    for b in boots:
        for mod in b.modifiers:
            if mod.type=='ARMATURE' and mod.object:
                protected.add(mod.object)
        p = b.parent
        while p is not None:
            protected.add(p)
            p = p.parent
    actions = {o.name:_action_hash(o) for o in protected}
    source_meshes = {b.name:hashlib.sha256(repr(
        [(tuple(v.co)) for v in b.data.vertices]).encode()).hexdigest() for b in boots}
    collection = bpy.data.collections.new(COLLECTION)
    scene.collection.children.link(collection)
    marks = {b.name:{kind:_quad(collection,b,kind) for kind in ('core','penumbra')}
             for b in boots}
    source_vertices = {}
    records = {b.name:[] for b in boots}
    for f in times:
        _frame(scene,f)
        for boot in boots:
            points = _points(boot)
            if not points or not all(math.isfinite(q) for p in points for q in p):
                raise RuntimeError('Invalid evaluated original boot coordinates.')
            source_vertices[f,boot.name] = points
            m = _measure(points,floor_z)
            h = max(0.0,m['clearance_m'])
            span = m['effective_support_span_x_m']
            core_alpha = .36*(1.0-_smooth(.0005,.003,h))**2
            soft_alpha = .15*(1.0-_smooth(.002,.045,h))**2
            core_x = _clamp(span*.95,.022,.245)
            soft_x = _clamp(span*1.12+.030+.025*_smooth(0,.045,h),.065,.30)
            # Source boots are planar drawings, not solid footwear. Their Y
            # span cannot provide a measured sole breadth. Declare this small
            # transverse floor footprint as an estimate from their X-length.
            core_y = _clamp(m['evaluated_boot_x_span_m']*.28,.035,.075)
            soft_y = core_y+.040+.020*_smooth(0,.045,h)
            for kind,width_x,width_y,alpha in (
                    ('core',core_x,core_y,core_alpha),
                    ('penumbra',soft_x,soft_y,soft_alpha)):
                ob,tree,opacity = marks[boot.name][kind]
                ob.location = (m['support_x'],m['support_y'],floor_z+.001)
                ob.scale = (width_x,width_y,1.0)
                ob.keyframe_insert('location',frame=f)
                ob.keyframe_insert('scale',frame=f)
                opacity.default_value = alpha
                opacity.keyframe_insert('default_value',frame=f)
            records[boot.name].append({'frame':f,**m,'core_opacity':core_alpha,
                'penumbra_opacity':soft_alpha,'core_width_x_m':core_x,
                'penumbra_width_x_m':soft_x,'core_depth_y_m':core_y,
                'penumbra_depth_y_m':soft_y})
    for objects in marks.values():
        for ob,tree,opacity in objects.values():
            for f,hidden in ((first-1,True),(first,False),(last,False),(last+1,True)):
                ob.hide_render = hidden
                ob.keyframe_insert('hide_render',frame=f)
            _linear(ob)
            _linear(tree)
    max_boot_error = 0.0
    for f in times:
        _frame(scene,f)
        for boot in boots:
            actual = _points(boot)
            original = source_vertices[f,boot.name]
            if len(actual)!=len(original):
                raise RuntimeError('Evaluated boot vertex count changed.')
            max_boot_error = max(max_boot_error,
                max((a-b).length for a,b in zip(actual,original)))
    if max_boot_error > 0.0000001:
        raise RuntimeError('Original boot geometry changed during floor contact creation.')
    for ob in protected:
        if _action_hash(ob)!=actions[ob.name]:
            raise RuntimeError('Protected boot/rig/root action changed: '+ob.name)
    for boot in boots:
        now = hashlib.sha256(repr([tuple(v.co) for v in boot.data.vertices]).encode()).hexdigest()
        if now!=source_meshes[boot.name]:
            raise RuntimeError('Original boot rest mesh changed: '+boot.name)
    per_boot = {}
    for name,rows in records.items():
        swinging = [r for r in rows if r['clearance_m']>=.003]
        if not all(r['core_opacity']==0.0 for r in swinging):
            raise RuntimeError('A lifted boot retained a hard contact mark.')
        keys = sorted(set([0,len(rows)-1]+
            [i for i,r in enumerate(rows) if abs((r['frame']-first)%12)<1e-8]))
        per_boot[name] = {'sample_count':len(rows),
            'sole_clearance_m':_range(rows,'clearance_m'),
            'core_opacity':_range(rows,'core_opacity'),
            'penumbra_opacity':_range(rows,'penumbra_opacity'),
            'core_width_x_m':_range(rows,'core_width_x_m'),
            'core_depth_y_m':_range(rows,'core_depth_y_m'),
            'source_boot_y_span_m':_range(rows,'evaluated_boot_y_span_m'),
            'samples_penetrating_flat_floor_over3mm':sum(r['clearance_m']<-.003 for r in rows),
            'lifted_samples_at_or_above3mm':len(swinging),
            'lifted_core_opacity_exactly_zero':True,
            'key_samples':[rows[i] for i in keys]}
    _frame(scene,old_frame)
    if old_scene!=scene:
        bpy.context.window.scene = old_scene
    return {'method':'Geometry-driven grounding marks on real horizontal world XY floor.',
        'collection':collection.name,
        'objects':[o.name for group in marks.values() for o,t,a in group.values()],
        'range':[first,last],'quarter_samples_per_boot':len(times),
        'floor_z':floor_z,'mark_z':floor_z+.001,'mark_plane':'WORLD XY; normal+Z',
        'material_surface_method':'BLENDED; same method as original v060 contact helper',
        'core_full_below_m':.0005,'core_zero_at_m':.003,
        'penumbra_full_below_m':.002,'penumbra_zero_at_m':.045,
        'all_checked_evaluated_boot_vertex_max_error_m':max_boot_error,
        'protected_boot_rig_root_actions_hash_exact':True,
        'boot_rest_meshes_hash_exact':True,
        'old_objects_hidden_deleted_or_modified':False,
        'transverse_width_method':'Explicit estimate: coreY=clamp(evaluated bootXspan*.28,.035,.075); planar source art has no physical sole breadth.',
        'per_boot':per_boot,
        'limits':['Grounding paint, not a physically simulated light shadow.',
                  'Marks lie on the real floor and may appear thin at a low camera angle; no camera-facing geometry is substituted.',
                  'Exact stance clearance is measured; a geometric threshold is not a gait-phase label.',
                  'Inspect native floor/foot crops for darkness, intersections and blended transparency sorting.']}
