import bpy
def apply_high_crown(scene,root):
    im=bpy.data.images.load(str(root/'sets/world_v030/High_Crown_Oak.png'),check_existing=True);im.pack()
    m=bpy.data.materials.new('v030 | Purpose-painted high crown oak');m.use_nodes=True;m.surface_render_method='BLENDED';nt=m.node_tree;nt.nodes.clear()
    t=nt.nodes.new('ShaderNodeTexImage');t.image=im;t.extension='CLIP';hsv=nt.nodes.new('ShaderNodeHueSaturation');hsv.inputs['Saturation'].default_value=.45;hsv.inputs['Value'].default_value=.48;nt.links.new(t.outputs['Color'],hsv.inputs['Color']);clean=nt.nodes.new('ShaderNodeMapRange');clean.clamp=True;clean.inputs['From Min'].default_value=.05;clean.inputs['From Max'].default_value=.96;nt.links.new(t.outputs['Alpha'],clean.inputs[0])
    em=nt.nodes.new('ShaderNodeEmission');nt.links.new(hsv.outputs[0],em.inputs[0]);tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(clean.outputs[0],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],out.inputs[0])
    objects=[o for o in scene.objects if o.name.startswith('v025 | Whole rooted foreground oak ')]
    assert len(objects)==4
    h=8;w=h*im.size[0]/im.size[1]
    for i,o in enumerate(objects):
        nx,nz=32,48;d=bpy.data.meshes.new('v030 | Whole high crown oak native grid');d.from_pydata([((u/nx-.5)*w,0,v/nz*h) for v in range(nz+1) for u in range(nx+1)],[],[(v*(nx+1)+u,v*(nx+1)+u+1,(v+1)*(nx+1)+u+1,(v+1)*(nx+1)+u) for v in range(nz) for u in range(nx)]);d.update();uv=d.uv_layers.new(name='Whole undistorted oak UV')
        for loop in d.loops:j=loop.vertex_index;uv.data[loop.index].uv=(j%(nx+1)/nx,j//(nx+1)/nz)
        d.materials.append(m);o.data=d;o.scale=(1,1,1);o.name='v030 | High crown foreground oak '+str(i);o.shape_key_add(name='Basis');key=o.shape_key_add(name='Wind | rooted trunk, high canopy');key.slider_min=-1
        for p in key.data:p.co.x+=.07*max(0,(p.co.z/h-.10)/.9)**1.7
        f=key.driver_add('value');f.driver.expression=f'.65*sin(frame/47+{i})+.25*sin(frame/21+{i})+.1*sin(frame/117)'
        o['readability']='New purpose-painted high crown; bare lower trunk. Source aspect ratio preserved; no stretched painting.'
    return {'objects':[o.name for o in objects],'image_pixels':list(im.size),'physical_size':[w,h],'source':'sets/world_v030/High_Crown_Oak.png'}
