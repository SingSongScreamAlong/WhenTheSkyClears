"""One fixed-anchor cel blast from genuinely different new painted drawings.
Read v006 proof only for the held camera, background and occlusion fixture.
"""
import bpy,bmesh,math,random,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parents[1];R=P.parents[1]
measure=json.loads((P/'evidence/atlas_measurements.json').read_text())
s=bpy.data.scenes['FX_PROOF_v006 | painted impulse depth tracers and ground'];bpy.context.window.scene=s
background=next(n.image for n in s.compositing_node_group.nodes if n.type=='IMAGE' and n.image.size[0]==3840)
fg=next(n.image for n in s.compositing_node_group.nodes if n.type=='IMAGE' and 'Native_Foreground_Alpha' in n.image.name)
depth=next(n.image for n in s.compositing_node_group.nodes if n.type=='IMAGE' and 'Native_Depth_Alpha_Y10_' in n.image.name)
helper=bpy.data.node_groups['FXv006 | HDR FX bloom over | append helper'].copy();helper.name='FXv007 | FX-only bloom and holdout'
crater=bpy.data.images.get('Painted_Ground_Gouge_v006.png')
assert crater
for col in list(s.collection.children):s.collection.children.unlink(col)
for ob in list(s.collection.objects):
    if ob!=s.camera:s.collection.objects.unlink(ob)
for layer in list(s.view_layers)[1:]:s.view_layers.remove(layer)
s.view_layers[0].name='ONE_BLAST'
s.name='FX_PROOF_v007 | distinct painted poses | one blast'
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=32;s.render.threads_mode='FIXED';s.render.threads=2
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1818;s.frame_end=1913
s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.media_type='IMAGE'
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1
if hasattr(s.render,'compositor_device'):s.render.compositor_device='GPU'
asset=bpy.data.collections.new('FXv007 | ONE DRAWN BLAST | editable cels and contact');s.collection.children.link(asset)
blast=bpy.data.collections.new('FXv007 | Twelve genuinely drawn blast poses');dust=bpy.data.collections.new('FXv007 | Six connected settling dust poses');ground=bpy.data.collections.new('FXv007 | Persistent visible ground and landing chips')
for col in [blast,dust,ground]:asset.children.link(col)
def point_for_screen(u,v,depth_y):
    origin=s.camera.matrix_world.translation;basis=world_to_camera_view(s,s.camera,Vector((origin.x,depth_y,origin.z)));px=world_to_camera_view(s,s.camera,Vector((origin.x+1,depth_y,origin.z)));pz=world_to_camera_view(s,s.camera,Vector((origin.x,depth_y,origin.z+1)))
    return Vector((origin.x+(u-basis.x)/(px.x-basis.x),depth_y,origin.z+(v-basis.y)/(pz.y-basis.y)))
root=bpy.data.objects.new('FXv007 | fixed visible impact and timing',None);asset.objects.link(root);root.location=point_for_screen(.79,.323,10);root.empty_display_type='CIRCLE';root.empty_display_size=.15
for key,value in {'start_frame':1824.,'speed':1.,'size':1.,'intensity':1.,'age':0.,'light_envelope':0.,'bloom_gain':.20}.items():root[key]=value
root['animation_method']='12 distinct new blast drawings +6 new dust drawings, registered at one contact. No animated scale/rotation/location on any cel.'
def driver(owner,path,expression,index=None,extra=()):
    f=owner.driver_add(path) if index is None else owner.driver_add(path,index);f.driver.type='SCRIPTED'
    for v in list(f.driver.variables):f.driver.variables.remove(v)
    for name,key in [('t','age'),('I','intensity'),('S','size')]+list(extra):
        v=f.driver.variables.new();v.name=name;v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["'+key+'"]'
    f.driver.expression=expression;return f
f=root.driver_add('["age"]');f.driver.expression='(frame-start)*speed'
for name,key in [('start','start_frame'),('speed','speed')]:
    v=f.driver.variables.new();v.name=name;v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["'+key+'"]'
for axis in range(3):driver(root,'scale','max(.01,S)',axis)
driver(root,'["light_envelope"]','max(0,min(1,t/1.5))*exp(-max(0,t-1.5)/2.2)*max(0,min(1,(8-t)/3))')
def quad(name,col,width,height,baseline,material,uvrect=(0,0,1,1),y=0):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata([(-width/2,y,-baseline*height),(width/2,y,-baseline*height),(width/2,y,(1-baseline)*height),(-width/2,y,(1-baseline)*height)],[],[(0,1,2,3)]);mesh.materials.append(material);mesh.update();uv=mesh.uv_layers.new(name='Registered original atlas UV')
    u0,v0,u1,v1=uvrect
    for loop in mesh.loops:uv.data[loop.index].uv=[(u0,v0),(u1,v0),(u1,v1),(u0,v1)][loop.vertex_index]
    ob=bpy.data.objects.new(name,mesh);col.objects.link(ob);ob.parent=root;return ob
def flat_material(name,color):
    m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(*color,1);o=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],o.inputs[0]);return m
def paint_material(name,image,opacity,warm=False,persistent=False):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.surface_render_method='BLENDED';nt=m.node_tree;nt.nodes.clear();tex=nt.nodes.new('ShaderNodeTexImage');tex.image=image;tex.extension='CLIP';tex.interpolation='Linear'
    bw=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(tex.outputs['Color'],bw.inputs[0]);hsv=nt.nodes.new('ShaderNodeHueSaturation');hsv.name='Preferred v003 saturation and value';hsv.inputs['Saturation'].default_value=.15;hsv.inputs['Value'].default_value=.90;nt.links.new(tex.outputs['Color'],hsv.inputs['Color']);tint=nt.nodes.new('ShaderNodeMixRGB');tint.name='Preferred v003 charcoal palette';tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(.72,.77,.83,1);nt.links.new(hsv.outputs[0],tint.inputs[1]);color=tint.outputs[0]
    if warm:
        hot=nt.nodes.new('ShaderNodeMapRange');hot.clamp=True;hot.inputs['From Min'].default_value=.40;hot.inputs['From Max'].default_value=.85;nt.links.new(bw.outputs[0],hot.inputs['Value'])
        mixed=nt.nodes.new('ShaderNodeMixRGB');mixed.inputs[2].default_value=(1,.58,.24,1);nt.links.new(color,mixed.inputs[1]);nt.links.new(hot.outputs[0],mixed.inputs[0]);color=mixed.outputs[0]
    e=nt.nodes.new('ShaderNodeEmission');e.inputs['Strength'].default_value=1.;nt.links.new(color,e.inputs['Color'])
    if warm:
        hot_strength=nt.nodes.new('ShaderNodeMath');hot_strength.operation='MULTIPLY_ADD';hot_strength.inputs[1].default_value=2.4;hot_strength.inputs[2].default_value=1;nt.links.new(hot.outputs[0],hot_strength.inputs[0]);nt.links.new(hot_strength.outputs[0],e.inputs['Strength'])
    alpha=nt.nodes.new('ShaderNodeMath');alpha.name='Authored cel exposure, not growth';alpha.operation='MULTIPLY';nt.links.new(tex.outputs['Alpha'],alpha.inputs[0]);driver(alpha.inputs[1],'default_value',opacity)
    transparent=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(alpha.outputs[0],mix.inputs[0]);nt.links.new(transparent.outputs[0],mix.inputs[1]);nt.links.new(e.outputs[0],mix.inputs[2]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],out.inputs[0]);return m
def exposure(keys,index):
    key=keys[index];previous=keys[index-1] if index else -0.1;following=keys[index+1] if index<len(keys)-1 else key+20
    if index==0:return f'max(0,min(1,(t+.1)/.1,({following}-t)/{following-key}))'
    return f'max(0,min(1,(t-{previous})/{key-previous},({following}-t)/{following-key}))'
pose_records=[]
for filename,keys,densities,col,width,height,y,prefix in [
    ('Blast_Drawn_Poses_v007.png',[0,1.5,3,5,7.5,10,13.5,18,24,32,44,60],[.8,1,1,1,.95,.9,.85,.76,.68,.50,.24,.08],blast,3.0,2.6,.08,'Blast'),
    ('Dust_Drawn_Poses_v007.png',[2,5,10,18,31,50],[.8,.85,.82,.70,.45,.16],dust,3.8,.55,-.20,'Dust')]:
    im=bpy.data.images.load(str(P/'assets'/filename));im.alpha_mode='STRAIGHT';im.pack();spec=measure[filename];cols,rows=spec['grid']
    for i,key in enumerate(keys):
        column=i%cols;row=i//cols;uv=((column+.001)/cols,(rows-row-1+.001)/rows,(column+.999)/cols,(rows-row-.001)/rows)
        opacity=f'I*{densities[i]}*({exposure(keys,i)})';mat=paint_material(f'FXv007 | {prefix} cel{i+1:02d} exposure',im,opacity,warm=prefix=='Blast' and i<3)
        ob=quad(f'FXv007 | {prefix} DRAWING {i+1:02d} | age{key:g}',col,width,height,spec['cells'][i]['baseline_v'],mat,uv,y=y+i*.001)
        ob['source_pose_index']=i;ob['key_age']=key;ob['role']='genuine distinct painted pose';ob['fixed_canvas_m']=[width,height];ob['registration']='Original cell alpha baseline48 registered to fixed ground; no animation of this canvas transform.'
        pose_records.append({'kind':prefix,'drawing':i+1,'key_age':key,'object':ob.name,'cell':spec['cells'][i]['cell'],'density':densities[i]})
# A small low contact-light receiver preview, driven only after visible ignition.
lightmat=bpy.data.materials.new('FXv007 | LOCAL contact light wash | ages0-8');lightmat.use_nodes=True;lightmat.surface_render_method='BLENDED';nt=lightmat.node_tree;nt.nodes.clear();coord=nt.nodes.new('ShaderNodeTexCoord');subtract=nt.nodes.new('ShaderNodeVectorMath');subtract.operation='SUBTRACT';subtract.inputs[1].default_value=(.5,0,.45);nt.links.new(coord.outputs['Generated'],subtract.inputs[0]);distance=nt.nodes.new('ShaderNodeVectorMath');distance.operation='LENGTH';nt.links.new(subtract.outputs['Vector'],distance.inputs[0]);fade=nt.nodes.new('ShaderNodeMapRange');fade.clamp=True;fade.inputs['From Min'].default_value=.08;fade.inputs['From Max'].default_value=.58;fade.inputs['To Min'].default_value=1;fade.inputs['To Max'].default_value=0;nt.links.new(distance.outputs['Value'],fade.inputs['Value']);alpha=nt.nodes.new('ShaderNodeMath');alpha.operation='MULTIPLY';nt.links.new(fade.outputs[0],alpha.inputs[0]);driver(alpha.inputs[1],'default_value','.28*L',extra=[('L','light_envelope')]);e=nt.nodes.new('ShaderNodeEmission');e.inputs['Color'].default_value=(.75,.32,.07,1);e.inputs['Strength'].default_value=1;tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(alpha.outputs[0],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(e.outputs[0],mix.inputs[2]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],out.inputs[0]);quad('FXv007 | Local receiver wash | source-synced',blast,2.4,.58,.45,lightmat,y=.24)
# Ground damage is shallow and separated from dynamic dust, not a floating slab.
scar_mat=paint_material('FXv007 | low persistent gouge',crater,'I*.82*max(0,min(1,(t-4)/8))')
scar=quad('FXv007 | shallow fixed ground consequence',ground,1.8,.16,.5,scar_mat,y=-.50);scar['role']='persistent_ground_scar'
chip_dark=flat_material('FXv007 | charcoal chip',(.035,.032,.028));chip_light=flat_material('FXv007 | dusty plaster chip',(.20,.18,.145));rng=random.Random(704)
trajectories=[]
for i,(vx,vz,delay) in enumerate([(-2.5,3.8,0),(-1.8,4.1,1),(-.8,3.3,2),(.6,4.2,0),(1.7,3.6,2),(2.6,3.9,1),(2.1,2.9,3)]):
    vx*=.75
    mesh=bpy.data.meshes.new(f'FXv007 chip{i}');bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=1,radius=rng.uniform(.025,.042))
    for v in bm.verts:v.co.x*=rng.uniform(.7,1.4);v.co.y*=.35;v.co.z*=rng.uniform(.6,1.25)
    bm.to_mesh(mesh);bm.free();mesh.materials.append(chip_light if i in [1,4] else chip_dark);ob=bpy.data.objects.new(f'FXv007 | visible landing chip{i}',mesh);ground.objects.link(ob);ob.parent=root;ob.location.y=-.55
    flight=2*vz/8;seconds=f'max(0,t-{delay})/24';limited=f'min({flight},{seconds})';land_x=vx*flight*math.exp(-.10*flight);landing=delay+flight*24
    driver(ob,'location',f'{vx}*{limited}*exp(-.1*{limited})',0);driver(ob,'location',f'.028+max(0,{vz}*({seconds})-4*({seconds})**2)',2)
    for axis in range(3):driver(ob,'scale',f'max(0,min(1,(t-{delay}+.1)/1.2))',axis);driver(ob,'rotation_euler',f'{rng.uniform(-2,2)}+{rng.uniform(-7,7)}*{limited}',axis)
    if i in [0,2,4,5]:
        image=bpy.data.images['Dust_Drawn_Poses_v007.png'];spec=measure['Dust_Drawn_Poses_v007.png'];mat=paint_material(f'FXv007 | landing puff{i}',image,f'.62*max(0,min(1,(t-{landing})/1.5,({landing+8}-t)/6))');puff=quad(f'FXv007 | readable landing puff{i}',ground,.48,.13,spec['cells'][0]['baseline_v'],mat,(.001,.667,.499,.999),y=-.60);puff.location.x=land_x
    trajectories.append({'chip':i,'birth_age':delay,'apex_age':delay+vz/8*24,'landing_age':landing,'landing_x':land_x,'landing_world':list(root.location+Vector((land_x,-.55,.028)))})
nt=bpy.data.node_groups.new('FXv007 | one-blast held-shot proof','CompositorNodeTree');nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');s.compositing_node_group=nt
bg=nt.nodes.new('CompositorNodeImage');bg.image=background;scale=nt.nodes.new('CompositorNodeScale');scale.inputs['X'].default_value=.5;scale.inputs['Y'].default_value=.5;nt.links.new(bg.outputs['Image'],scale.inputs['Image']);layer=nt.nodes.new('CompositorNodeRLayers');layer.scene=s;layer.layer='ONE_BLAST';a=nt.nodes.new('CompositorNodeImage');a.image=fg;b=nt.nodes.new('CompositorNodeImage');b.image=depth;maximum=nt.nodes.new('ShaderNodeMath');maximum.operation='MAXIMUM';nt.links.new(a.outputs['Alpha'],maximum.inputs[0]);nt.links.new(b.outputs['Alpha'],maximum.inputs[1]);over=nt.nodes.new('CompositorNodeGroup');over.node_tree=helper;nt.links.new(layer.outputs['Image'],over.inputs['Foreground']);nt.links.new(scale.outputs[0],over.inputs['Background']);nt.links.new(maximum.outputs[0],over.inputs['Occluder']);driver(over.inputs['Bloom gain'],'default_value','B',extra=[('B','bloom_gain')]);out=nt.nodes.new('NodeGroupOutput');nt.links.new(over.outputs[0],out.inputs['Image'])
s.frame_set(1828);bpy.context.view_layer.update();invalid=[]
for ob in asset.all_objects:
    assert ob.type not in {'CAMERA','LIGHT'}
    if ob.get('role')=='genuine distinct painted pose':assert not ob.animation_data,'Cel transform is animated'
    owners=[ob]+([m.node_tree for m in ob.data.materials if m and m.node_tree] if ob.type=='MESH' else [])
    for owner in owners:
        if owner.animation_data:
            invalid += [[owner.name,f.data_path] for f in owner.animation_data.drivers if not f.driver.is_valid]
assert not invalid,invalid
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Single_Drawn_Blast_Proof_v007b.blend'),compress=True)
bpy.data.libraries.write(str(P/'native/WTSC_Single_Drawn_Blast_Assets_v007b.blend'),{asset,helper},fake_user=True,compress=True)
report={'blender':bpy.app.version_string,'scene':s.name,'fps':24,'frames':[1818,1913],'pixels':[1920,1080],'start_frame':1824,'root':list(root.location),'anchor_screen':list(world_to_camera_view(s,s.camera,root.location)),'poses':pose_records,'trajectories':trajectories,'objects':len(asset.all_objects),'invalid_drivers':invalid,'pose_transform_animation':False,'background':'Existing held actual-project frame1825; no source scene edited','local_light':'Small native preview wash, zero atage0, peak after visible ignition, zero byage8. No inherited whole-background warm map.','no_variants_or_tracers':True,'no_simulation_or_bake':True,'new_art':'Two new original painted atlases; original returnedPNG bytes packed. Atlas edit improved heat timing, but modeled wash quality remains subject to shot review.','proof_status':'Await actual rendered review; do not claim fixed from build alone.'}
(P/'evidence/build_single_pose.json').write_text(json.dumps(report,indent=2));print('SINGLE_DRAWN_BLAST_BUILT',json.dumps({k:v for k,v in report.items() if k not in ['poses','trajectories']}),flush=True)
