"""Helpers for a FUTURE verified snapshot; importing this file performs no mutation."""
import bpy,math

def bind_event_to_native_fx(scene,fx_root,physical_light):
    """Bind local paint to actual native FX position/energy, without a second light."""
    assert physical_light.type=='LIGHT'
    control=scene.objects['v041 | Live event binding | awaiting verified FX']
    for i,axis in enumerate(['LOC_X','LOC_Y','LOC_Z']):
        curve=control.driver_add('location',i);curve.driver.expression='p';v=curve.driver.variables.new();v.name='p';v.type='TRANSFORMS';v.targets[0].id=fx_root;v.targets[0].transform_type=axis;v.targets[0].transform_space='WORLD_SPACE'
    curve=control.driver_add('["power_watts"]');curve.driver.expression='P';v=curve.driver.variables.new();v.name='P';v.type='SINGLE_PROP';v.targets[0].id_type='LIGHT';v.targets[0].id=physical_light.data;v.targets[0].data_path='energy';control['bound_to_verified_fx']=1.
    return control

def bake_boot_contacts(scene,performance_root,first=1801,last=1920,floor_slope=None):
    """Own native soft contact planes follow evaluated boot soles, not old held art.

    Caller must first align accepted root travel/camera and disable old contacts.
    Metrics are geometry diagnostics, never an artistic contact pass.
    """
    if floor_slope is None:
        held=next(o for o in scene.objects if o.type=='GREASEPENCIL');p=[held.matrix_world@q.vector for q in held.data.layers[0].frames[0].drawing.attributes['position'].data];sole=min(p,key=lambda q:q.z);floor_slope=(scene.camera.location.z-sole.z)/(sole.y-scene.camera.location.y)
    boots=[o for o in performance_root.children_recursive if o.type=='MESH' and 'rigid original boot' in o.name];assert len(boots)==4,[o.name for o in boots]
    collection=bpy.data.collections.new('v041 OWNED | Animated evaluated sole contacts');scene.collection.children.link(collection);records=[]
    for boot in boots:
        mat=bpy.data.materials.new('v041 contact | '+boot.name);mat.use_nodes=True;mat.surface_render_method='BLENDED';nt=mat.node_tree;nt.nodes.clear();uv=nt.nodes.new('ShaderNodeTexCoord');dist=nt.nodes.new('ShaderNodeVectorMath');dist.operation='DISTANCE';dist.inputs[1].default_value=(.5,.5,0);nt.links.new(uv.outputs['UV'],dist.inputs[0]);fall=nt.nodes.new('ShaderNodeMapRange');fall.clamp=True;fall.interpolation_type='SMOOTHERSTEP';fall.inputs['From Min'].default_value=.05;fall.inputs['From Max'].default_value=.5;fall.inputs['To Min'].default_value=.55;fall.inputs['To Max'].default_value=0;nt.links.new(dist.outputs['Value'],fall.inputs[0]);weight=nt.nodes.new('ShaderNodeMath');weight.operation='MULTIPLY';nt.links.new(fall.outputs[0],weight.inputs[0]);weight.inputs[1].default_value=1
        transparent=nt.nodes.new('ShaderNodeBsdfTransparent');em=nt.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(.015,.012,.009,1);mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(weight.outputs[0],mix.inputs[0]);nt.links.new(transparent.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],out.inputs[0]);mesh=bpy.data.meshes.new('contact plane | '+boot.name);mesh.from_pydata([(-.5,0,-.5),(.5,0,-.5),(.5,0,.5),(-.5,0,.5)],[],[(0,1,2,3)]);mesh.materials.append(mat);layer=mesh.uv_layers.new(name='soft contact UV')
        for v,xy in zip(layer.data,[(0,0),(1,0),(1,1),(0,1)]):v.uv=xy
        plane=bpy.data.objects.new('v041 sole contact | '+boot.name,mesh);collection.objects.link(plane);samples=[]
        for frame in range(first,last+1):
            scene.frame_set(frame);bpy.context.view_layer.update();ev=boot.evaluated_get(bpy.context.evaluated_depsgraph_get());evaluated=ev.to_mesh();p=[ev.matrix_world@v.co for v in evaluated.vertices];ev.to_mesh_clear();assert p
            minimum=min(v.z for v in p);bottom=[v for v in p if v.z<=minimum+.004];x=sum(v.x for v in bottom)/len(bottom);y=sum(v.y for v in bottom)/len(bottom);floor=3-floor_slope*(y+16);height=minimum-floor;width=max(v.x for v in p)-min(v.x for v in p);shadow_y=y+.018;shadow_floor=3-floor_slope*(shadow_y+16)
            plane.location=(x,shadow_y,shadow_floor-.002);plane.scale=(max(.08,width*1.05),1,.035+.025*max(0,min(1,height/.15)));opacity=max(0,min(1,1-max(0,height)/.13))**2;weight.inputs[1].default_value=opacity;plane.keyframe_insert('location',frame=frame);plane.keyframe_insert('scale',frame=frame);weight.inputs[1].keyframe_insert('default_value',frame=frame);samples.append({'frame':frame,'evaluated_boot_min_height_above_floor':height,'contact_x':x,'opacity':opacity})
        for id in [plane,nt]:
            if id.animation_data and id.animation_data.action:
                for layer in id.animation_data.action.layers:
                    for strip in layer.strips:
                        for bag in strip.channelbags:
                            for curve in bag.fcurves:
                                for key in curve.keyframe_points:key.interpolation='LINEAR'
        records.append({'boot':boot.name,'contact':plane.name,'samples':samples})
    return records
