"""One isolated correction of smoke evolution; no production writes or bake."""
import bpy, math, random, json, hashlib, time
from pathlib import Path
P = Path(__file__).resolve().parents[1]
scene = bpy.data.scenes['FX_MOTION_v002 | real shot plate + animated native FX']
bpy.context.window.scene = scene
scene.name = 'FX_PROOF_v003 | 75-80s held shot evolution'
collection = bpy.data.collections['FXv002 | Detailed painterly ground eruption']
collection.name = 'FXv003 | Evolving anchored eruption | NO PRODUCTION LIGHTS'
root = bpy.data.objects['FXv002 | fixed ground origin and controls']
for ob in collection.all_objects:
    ob.name = ob.name.replace('FXv002', 'FXv003')
for mat in bpy.data.materials:
    if mat.name.startswith('FXv002'):
        mat.name = mat.name.replace('FXv002', 'FXv003')
root['start_frame'] = 1824.0
root['speed'] = 1.0
root['size'] = 1.0
root['smoke_density'] = .88
root['hot_frames'] = 14.0
root['wind'] = .18
root['smoke_color'] = [.72, .77, .83]
root['hot_envelope'] = 0.0
root['status'] = 'Candidate v003: compare actual motion before production integration.'
root['medium'] = 'Four distinct original cold-smoke forms, independent overlapping births/rise/roll/erosion/dissipation; short separate hot phase. 2.5D, no fluid simulation.'

def driver(owner, path, expression, index=None, extra=None):
    f = owner.driver_add(path) if index is None else owner.driver_add(path, index)
    f.driver.type = 'SCRIPTED'
    for variable in list(f.driver.variables):
        f.driver.variables.remove(variable)
    for name, key in [('t','age'),('I','intensity'),('W','wind'),('D','smoke_density'),('H','hot_frames'),('S','size')]:
        v = f.driver.variables.new(); v.name = name; v.type = 'SINGLE_PROP'
        v.targets[0].id = root; v.targets[0].data_path = '["'+key+'"]'
    for name, key in extra or []:
        v = f.driver.variables.new(); v.name = name; v.type = 'SINGLE_PROP'
        v.targets[0].id = root; v.targets[0].data_path = key
    f.driver.expression = expression
    return f

for axis in range(3):
    driver(root, 'scale', 'max(.01,S)', axis)
driver(root, '["hot_envelope"]', 'max(0,min(1,t))*exp(-(max(1,t)-1)/3)*max(0,min(1,(H-t)/3))')
# There are deliberately no lights in the handed-off collection. Production
# owns actual source-linked relighting. The held proof only reuses its old map.
removed_lights = []
for ob in list(collection.all_objects):
    if ob.type == 'LIGHT':
        removed_lights.append(ob.name); bpy.data.objects.remove(ob, do_unlink=True)

# The old full painted eruption is a short ignition jet only, never late smoke.
hot = bpy.data.materials['FXv003 | detailed soot internal light and cooling']
driver(hot.node_tree.nodes['Shot age opacity'].inputs[1], 'default_value',
       'I*max(0,min(1,t/2))*exp(-max(0,t-2)/4)*max(0,min(1,(H-t)/3))')
plume = bpy.data.objects['FXv003 | unique root-pinned eruption paint']
plume.name = 'FXv003 | short hot launch jet | gone after hot_frames'

flash = bpy.data.materials['FXv003 | fast pale-hot core flash']; nt = flash.node_tree
uv = next(n for n in nt.nodes if n.type == 'TEX_COORD')
sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(uv.outputs['UV'],sep.inputs[0])
cap = nt.nodes.new('ShaderNodeMapRange'); cap.name = 'Feathered ignition tip'; cap.clamp=True; cap.interpolation_type='SMOOTHERSTEP'
for key,value in [('From Min',.18),('From Max',.29),('To Min',1),('To Max',0)]: cap.inputs[key].default_value=value
nt.links.new(sep.outputs['Y'],cap.inputs[0])
out=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL'); mix=out.inputs[0].links[0].from_node; old=mix.inputs[0].links[0].from_socket
mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';nt.links.new(old,mul.inputs[0]);nt.links.new(cap.outputs[0],mul.inputs[1]);nt.links.new(mul.outputs[0],mix.inputs[0])

dustmat = bpy.data.materials['FXv003 | granular low dust with neutral edge palette']
driver(dustmat.node_tree.nodes['Shot age opacity'].inputs[1], 'default_value', 'I*.65*max(0,min(1,(t-2)/7,(90-t)/24))')
dust = bpy.data.objects['FXv003 | broad low asymmetric dust sheets']
driver(dust,'scale','.3+.9*(1-exp(-max(0,t-2)/18))',0)
driver(dust,'scale','.7+.15*(1-exp(-max(0,t-2)/16))',2)

atlas = bpy.data.images.load(str(P/'assets/Cold_Smoke_Atlas_4Forms_v003.png'))
atlas.name = 'FXv003 | ORIGINAL four cold forms | packed straight alpha'; atlas.alpha_mode='STRAIGHT';atlas.pack()
random.seed(31076)

def mathnode(nt, op, a, b):
    n=nt.nodes.new('ShaderNodeMath');n.operation=op
    for i,socket in enumerate([a,b]):
        if isinstance(socket,(float,int)):n.inputs[i].default_value=socket
        else:nt.links.new(socket,n.inputs[i])
    return n.outputs[0]

def smoke_material(index, tile, birth, life, opacity):
    a=f'max(0,t-{birth})'
    m=bpy.data.materials.new(f'FXv003 | cold billow {index:02} | form {tile} birth {birth} life {life}')
    m.use_nodes=True;m.surface_render_method='BLENDED';nt=m.node_tree;nt.nodes.clear()
    uv=nt.nodes.new('ShaderNodeTexCoord')
    noise=nt.nodes.new('ShaderNodeTexNoise');noise.noise_dimensions='4D';noise.inputs['Scale'].default_value=5.7;noise.inputs['Detail'].default_value=3.2;noise.inputs['Roughness'].default_value=.7
    nt.links.new(uv.outputs['UV'],noise.inputs[0]);driver(noise.inputs['W'],'default_value',f'{index*3.718}+{a}/27')
    shift=nt.nodes.new('ShaderNodeVectorMath');shift.operation='SUBTRACT';shift.inputs[1].default_value=(.5,.5,.5);nt.links.new(noise.outputs['Color'],shift.inputs[0])
    amp=nt.nodes.new('ShaderNodeVectorMath');amp.operation='MULTIPLY';amp.inputs[1].default_value=(.05,.06,0);nt.links.new(shift.outputs[0],amp.inputs[0])
    flow=nt.nodes.new('ShaderNodeVectorMath');flow.operation='ADD';nt.links.new(uv.outputs['UV'],flow.inputs[0]);nt.links.new(amp.outputs[0],flow.inputs[1])
    scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(.5,.5,1);nt.links.new(flow.outputs[0],scale.inputs[0])
    offset=nt.nodes.new('ShaderNodeVectorMath');offset.operation='ADD';offset.inputs[1].default_value=((tile%2)*.5,(1-tile//2)*.5,0);nt.links.new(scale.outputs[0],offset.inputs[0])
    tex=nt.nodes.new('ShaderNodeTexImage');tex.image=atlas;tex.extension='CLIP';tex.interpolation='Linear';nt.links.new(offset.outputs[0],tex.inputs[0])
    # Local UV edge feather prevents any atlas quadrant boundary becoming a box.
    separate=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs['UV'],separate.inputs[0])
    x=separate.outputs['X'];y=separate.outputs['Y']
    edge=mathnode(nt,'MINIMUM',mathnode(nt,'MINIMUM',x,mathnode(nt,'SUBTRACT',1,x)),mathnode(nt,'MINIMUM',y,mathnode(nt,'SUBTRACT',1,y)))
    feather=nt.nodes.new('ShaderNodeMapRange');feather.clamp=True;feather.interpolation_type='SMOOTHERSTEP';feather.inputs['From Min'].default_value=.025;feather.inputs['From Max'].default_value=.115;nt.links.new(edge,feather.inputs[0])
    erosion=nt.nodes.new('ShaderNodeMapRange');erosion.name='Independent evolving density erosion';erosion.clamp=True;erosion.interpolation_type='SMOOTHERSTEP';nt.links.new(noise.outputs['Fac'],erosion.inputs[0])
    driver(erosion.inputs['From Min'],'default_value',f'.15+.24*min(1,{a}/{life})')
    driver(erosion.inputs['From Max'],'default_value',f'.39+.24*min(1,{a}/{life})')
    alpha=mathnode(nt,'MULTIPLY',mathnode(nt,'MULTIPLY',tex.outputs['Alpha'],feather.outputs[0]),erosion.outputs[0])
    age=nt.nodes.new('ShaderNodeMath');age.name='Birth rise and independent dissipating lifetime';age.operation='MULTIPLY';nt.links.new(alpha,age.inputs[0])
    driver(age.inputs[1],'default_value',f'I*D*{opacity}*max(0,min(1,(t-{birth})/4,({birth+life}-t)/22))')
    hsv=nt.nodes.new('ShaderNodeHueSaturation');hsv.inputs['Saturation'].default_value=.15;hsv.inputs['Value'].default_value=.90;nt.links.new(tex.outputs['Color'],hsv.inputs['Color'])
    tint=nt.nodes.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;nt.links.new(hsv.outputs[0],tint.inputs[1])
    for component in range(3): driver(tint.inputs[2],'default_value',f'C',component,extra=[('C',f'["smoke_color"][{component}]')])
    emission=nt.nodes.new('ShaderNodeEmission');emission.name='Cold paint values ONLY; no hot core';emission.inputs[1].default_value=1;nt.links.new(tint.outputs[0],emission.inputs[0])
    transparent=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(age.outputs[0],mix.inputs[0]);nt.links.new(transparent.outputs[0],mix.inputs[1]);nt.links.new(emission.outputs[0],mix.inputs[2]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],out.inputs[0])
    return m

records=[]
births=[0,1,3,5,8,12,16,20,25,30,36,42,48]
for index,birth in enumerate(births):
    tile=[2,0,1,2,0,3,1,2,0,1,3,0,3][index]
    life=random.randint(62,88) if birth<30 else random.randint(59,78)
    width=random.uniform(1.35,1.85) if birth<30 else random.uniform(1.1,1.6)
    height=width*random.uniform(.85,1.12)
    rise=random.uniform(1.85,2.65) if birth<30 else random.uniform(1.65,2.2)
    x0=random.uniform(-.20,.20); spread=random.uniform(-.46,.46); phase=random.uniform(0,6.28); roll=random.uniform(-.48,.48)
    m=smoke_material(index,tile,birth,life,random.uniform(.78,1.0))
    count=22;vertices=[((u/count-.5),0,(v/count-.5)) for v in range(count+1) for u in range(count+1)]
    faces=[(v*(count+1)+u,v*(count+1)+u+1,(v+1)*(count+1)+u+1,(v+1)*(count+1)+u) for v in range(count) for u in range(count)]
    mesh=bpy.data.meshes.new(m.name+' | subdivided paint');mesh.from_pydata(vertices,[],faces);mesh.materials.append(m);mesh.update();uv=mesh.uv_layers.new(name='Local cell UV')
    for loop in mesh.loops:uv.data[loop.index].uv=(loop.vertex_index%(count+1)/count,loop.vertex_index//(count+1)/count)
    ob=bpy.data.objects.new(f'FXv003 | rolling smoke {index:02} | born {birth:02}',mesh);collection.objects.link(ob);ob.parent=root
    ob.shape_key_add(name='Basis');curl=ob.shape_key_add(name='Independent unequal vortex curl');tear=ob.shape_key_add(name='Differential billow shear')
    for j,v in enumerate(mesh.vertices):
        x,z=v.co.x,v.co.z
        curl.data[j].co.x += .08*math.sin(z*9+x*5+phase)*(1-abs(x))
        curl.data[j].co.z += .065*math.cos(x*8-z*7+phase)*(1-abs(z))
        tear.data[j].co.x += .09*z*z*math.sin(x*13+phase)+.06*z
        tear.data[j].co.z += .07*math.sin(x*11-z*4+phase)*z
    a=f'max(0,t-{birth})'
    driver(curl,'value',f'.7*sin({phase}+{a}/16)')
    driver(tear,'value',f'.6*sin({phase}+{a}/23)')
    driver(ob,'scale',f'{width}*(.06+.94*(1-exp(-{a}/7.5)))*(1+.0028*{a})',0)
    driver(ob,'scale',f'{height}*(.06+.94*(1-exp(-{a}/9)))*(1+.0018*{a})',2)
    ob.location.y=.12+index*.026
    driver(ob,'location',f'{x0}+{spread}*(1-exp(-{a}/15))+W*{a}/27+.15*sin({phase}+{a}/15)*min(1,{a}/16)',0)
    driver(ob,'location',f'.09+{rise}*(1-exp(-{a}/21))',2)
    driver(ob,'rotation_euler',f'{roll}+{roll}*{a}/45+.08*sin({phase}+{a}/19)',1)
    records.append({'object':ob.name,'tile':tile,'birth':birth,'life':life,'rise':rise,'size':[width,height],'roll':roll})

# Replace only the benchmark's held receiver intensity. No new production
# receiver materials or lighting pass are created in this revision.
comp=scene.compositing_node_group
lit=next(n for n in comp.nodes if n.type=='ALPHAOVER' and n.inputs['Foreground'].is_linked and n.inputs['Foreground'].links[0].from_node.type=='IMAGE')
driver(lit.inputs['Factor'],'default_value','min(1,max(0,I/.94*E))',extra=[('E','["hot_envelope"]')])
collection['timing']='75-80s proof, ignition1824 at24fps, source-anchored, hot phase ends14frames later.'
collection['ownership']='Effect geometry/material evolution only. No native lights. Production owns live lighting/contact/occlusion.'
scene.render.engine='BLENDER_EEVEE';scene.eevee.taa_render_samples=32;scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100;scene.render.fps=24
scene.render.image_settings.media_type='IMAGE';scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.frame_start=1800;scene.frame_end=1919
if hasattr(scene.render,'compositor_device'):scene.render.compositor_device='GPU'
ld=bpy.data.lights.new('PREVIEW ONLY | cool fragment soft fill','AREA');ld.energy=20;ld.color=(.44,.55,.70);ld.shape='DISK';ld.size=4
lo=bpy.data.objects.new(ld.name,ld);scene.collection.objects.link(lo);lo.location=root.location+__import__('mathutils').Vector((-2,-4,5));lo.rotation_euler=(root.location+__import__('mathutils').Vector((0,0,.7))-lo.location).to_track_quat('-Z','Y').to_euler()
states=[]
for frame in [1800,1825,1830,1838,1842,1860,1890,1919]:
    scene.frame_set(frame);bpy.context.view_layer.update()
    states.append({'frame':frame,'age':root['age'],'hot_envelope':root['hot_envelope'],'root':list(root.matrix_world.translation),'hot_alpha':hot.node_tree.nodes['Shot age opacity'].inputs[1].default_value,'held_receiver_factor':lit.inputs['Factor'].default_value})
    if frame>=1838:assert root['hot_envelope']==0 and hot.node_tree.nodes['Shot age opacity'].inputs[1].default_value==0 and lit.inputs['Factor'].default_value==0
bad=[]
ids=list(collection.all_objects)+list(bpy.data.shape_keys)+[m.node_tree for m in bpy.data.materials if m.node_tree]+[comp]
for owner in ids:
    if owner.animation_data:
        bad += [{'id':owner.name,'path':f.data_path,'expression':f.driver.expression} for f in owner.animation_data.drivers if not f.driver.is_valid]
assert not bad,bad
scene.frame_set(1842)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Evolution_Proof_v003.blend'),compress=True)
bpy.data.libraries.write(str(P/'native/WTSC_Evolving_Eruption_Collection_v003.blend'),{collection},fake_user=True,compress=True)
report={'blender':bpy.app.version_string,'scene':scene.name,'native_collection':collection.name,'objects':len(collection.all_objects),'atlas_pixels':list(atlas.size),'births':records,'hot_phase_frames':14,'ignition':1824,'fps':24,'range':[1800,1919],'render_pixels':[1920,1080],'no_lights_in_collection':not any(o.type=='LIGHT' for o in collection.all_objects),'states':states,'invalid_drivers':bad,'source':'v002 isolated minimal preview, not production blend','artistic_status':'Candidate pending matched-frame motion review.'}
(P/'evidence/evolution_build_v003.json').write_text(json.dumps(report,indent=2))
print('FX_EVOLUTION_BUILD_COMPLETE',json.dumps(report),flush=True)
