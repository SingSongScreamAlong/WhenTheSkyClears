"""Isolated main-impact candidate. No rendering, source file or choreography edits.

Run with Blender 5.2.2 background, opening the v047g native source first.
Creates native editable X/Z contour meshes, hidden real GP contour guides,
individually authored chip trajectories and persistent displaced-earth marks.
All output is contained in effects/main_impact_v015.
"""
import bpy, math, json, hashlib, re, random
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

P = Path(__file__).resolve().parents[1]
PROJECT = P.parents[1]
SOURCE = PROJECT / 'shots/world/WTSC_Open_Battlefield_Refinement_v047g.blend'
assert Path(bpy.data.filepath).resolve() == SOURCE.resolve(), bpy.data.filepath
source_sha = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
for sub in ('native', 'evidence', 'previews'):
    (P/sub).mkdir(parents=True, exist_ok=True)
s = bpy.data.scenes['WTSC_OPEN_BATTLEFIELD_REFINEMENT_v047g']
bpy.context.window.scene = s
s.name = 'WTSC_MAIN_GROUND_IMPACT_CANDIDATE_v015'
old = bpy.data.objects['FXv003 | fixed ground origin and controls']
# In this separately saved context copy, disable only prior rendered geometry.
# The original point light and its established material receivers remain intact.
hidden_prior = []
for ob in [old, *old.children_recursive]:
    if ob.type in {'MESH', 'CURVE', 'GREASEPENCIL', 'VOLUME'}:
        ob.animation_data_clear()
        ob.hide_render = True
        ob.hide_viewport = True
        hidden_prior.append(ob.name)

c = bpy.data.collections.new('FXv015 | MAIN SOIL RUPTURE | separate contour exposures')
s.collection.children.link(c)
guides = bpy.data.collections.new('FXv015 | GP contour editing guides | hidden')
c.children.link(guides)
r = bpy.data.objects.new('FXv015 | fixed ground anchor and controls', None)
c.objects.link(r)
# Exact retained main-event origin and clock, rather than the unrelated compact FX.
r.location = old.location.copy()
r.empty_display_type = 'CIRCLE'
r.empty_display_size = .25
for k, v in {'start_frame':1824., 'speed':1., 'size':1., 'intensity':.94,
             'age':0., 'painted':1.}.items():
    r[k] = v

def drive(owner, path, expression, index=None):
    f = owner.driver_add(path) if index is None else owner.driver_add(path, index)
    f.driver.type = 'SCRIPTED'
    for var in list(f.driver.variables):
        f.driver.variables.remove(var)
    for name, key in [('t','age'),('start','start_frame'),('speed','speed'),
                      ('S','size'),('I','intensity'),('P','painted')]:
        if not re.search(r'\b'+name+r'\b', expression):
            continue
        var = f.driver.variables.new()
        var.name = name
        var.type = 'SINGLE_PROP'
        var.targets[0].id = r
        var.targets[0].data_path = '["'+key+'"]'
    f.driver.expression = expression

drive(r, '["age"]', '(frame-start)*speed')
for axis in range(3):
    drive(r, 'scale', 'max(.01,S)', axis)

# Convert the prior measured grass edge into world X/Z at this exact camera.
# The contact is intentionally placed just behind that occlusion edge.
s.frame_set(1824)
bpy.context.view_layer.update()
profile = json.loads((PROJECT/'effects/drawn_impact_v013/evidence/visible_terrain_profile.json').read_text())['profile']
def lerp_ground(px):
    if px <= profile[0][0]: return profile[0][1]
    if px >= profile[-1][0]: return profile[-1][1]
    i = next(i for i in range(len(profile)-1) if profile[i][0] <= px < profile[i+1][0])
    a,b = profile[i:i+2]
    return a[1]+(b[1]-a[1])*(px-a[0])/(b[0]-a[0])
q = world_to_camera_view(s,s.camera,r.location)
qx = world_to_camera_view(s,s.camera,r.location+Vector((1,0,0)))
qz = world_to_camera_view(s,s.camera,r.location+Vector((0,0,1)))
pxm = (qx.x-q.x)*1920
pym = (qz.y-q.y)*1080
screenx = q.x*1920
screeny = (1-q.y)*1080
def floor_z(x):
    return (screeny-lerp_ground(screenx+pxm*x))/pym
floor0 = floor_z(0)

# This source is joined to the reviewed v014 source/camera-preservation header.
atlas_path=P/'assets/Painted_Soil_Rupture_4Stages_v015b.png'
info=json.loads((P/'assets/painted_contours.json').read_text())
atlas=bpy.data.images.load(str(atlas_path),check_existing=True);atlas.pack()
atlas.name='FXv015 | original imagegen four painted soil stages | packed RGBA'
W,H=info['size']
def painted_material(name,value=.78,saturation=.22,opacity='I'):
    m=bpy.data.materials.new('FXv015 | '+name);m.use_nodes=True;m.surface_render_method='DITHERED'
    n=m.node_tree.nodes;n.clear();L=m.node_tree.links
    uv=n.new('ShaderNodeTexCoord');tex=n.new('ShaderNodeTexImage');tex.image=atlas
    tex.interpolation='Linear';L.new(uv.outputs['UV'],tex.inputs[0])
    hs=n.new('ShaderNodeHueSaturation');hs.inputs['Saturation'].default_value=saturation
    hs.inputs['Value'].default_value=value;L.new(tex.outputs['Color'],hs.inputs['Color'])
    em=n.new('ShaderNodeEmission');L.new(hs.outputs['Color'],em.inputs[0])
    alpha=n.new('ShaderNodeMath');alpha.operation='MULTIPLY';L.new(tex.outputs['Alpha'],alpha.inputs[0])
    drive(alpha.inputs[1],'default_value',opacity)
    tr=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader')
    L.new(alpha.outputs[0],mix.inputs[0]);L.new(tr.outputs[0],mix.inputs[1]);L.new(em.outputs[0],mix.inputs[2])
    out=n.new('ShaderNodeOutputMaterial');L.new(mix.outputs[0],out.inputs[0]);return m
paint=painted_material('original painted soil, native restrained cool grade')
collapsepaint=painted_material('falling painted soil with final thinning',opacity='I*max(0,min(1,(43-t)/16))')
scarpaint=painted_material('original lower soil paint persistent ground disturbance',value=.44,saturation=.10)
chipmat=painted_material('actual painted clod fragments',value=.58,saturation=.12)
drawings=[]
def mesh_from_pixels(name,contour,anchor,scale,material,y,lo,hi=None,guide=False,terrain=False):
    ax,ay=anchor
    points=[]
    for px,py in contour:
        x=(px-ax)*scale;z=(ay-py)*scale
        z+=floor_z(x) if terrain else floor0
        points.append((x,y,z))
    mesh=bpy.data.meshes.new('FXv015 | '+name);mesh.from_pydata(points,[],[tuple(range(len(points)))]);mesh.update()
    uv=mesh.uv_layers.new(name='Untouched original RGBA exact pixel coordinates')
    for loop in mesh.loops:
        px,py=contour[loop.vertex_index];uv.data[loop.index].uv=(px/W,1-py/H)
    mesh.materials.append(material)
    ob=bpy.data.objects.new(mesh.name,mesh);c.objects.link(ob);ob.parent=r
    expression=f't<{lo}' if hi is None else f'not ({lo}<=t<{hi})'
    drive(ob,'hide_render',expression);drive(ob,'hide_viewport',expression)
    ob['original_pixel_outline']=True;ob['visible_surface']='Original imagegen RGBA on alpha-traced native mesh'
    if guide:
        gp=bpy.data.grease_pencils.new('FXv015 | GP | '+name)
        go=bpy.data.objects.new(gp.name,gp);guides.objects.link(go);go.parent=r
        layer=gp.layers.new('Original alpha-traced editable contour',set_active=True)
        d=layer.frames.new(1).drawing;d.add_strokes([len(points)])
        stroke=d.strokes[0];stroke.cyclic=True
        for pt,co in zip(stroke.points,points):pt.position=co;pt.radius=.001;pt.opacity=1
        go.hide_render=True;go.hide_viewport=True
        go['purpose']='Editable true GP source contour guide. Native filled mesh carries rendered original paint.'
    return ob

for stage in info['stages']:
    lo,hi=stage['age_exposure']
    if stage['name']=='Collapse':hi=43
    rows=[]
    for i,island in enumerate(stage['islands']):
        ob=mesh_from_pixels(f"{stage['name']} original island {i:02d}",island['contour'],stage['anchor'],stage['metres_per_pixel'],collapsepaint if stage['name']=='Collapse' else paint,.02,lo,hi,guide=i==0)
        # Restrained native follow-through only, never grow a completed painting
        # from a seed by object scale. Main exposures remain four distinct drawings.
        if i==0:
            ob.shape_key_add(name='Original painted contour')
            key=ob.shape_key_add(name='Small directional settling of painted soil')
            height=stage['height_m']
            for d,base in zip(key.data,ob.data.vertices):
                weight=max(0,min(1,(base.co.z-floor0)/height))**1.4
                d.co.x+=.045*weight
                d.co.z+=(-.045 if stage['name']=='Collapse' else .025)*weight
            drive(key,'value',f'max(0,min(1,(t-{lo})/{max(1,hi-lo-1)}))')
        rows.append(ob.name)
    drawings.append({'stage':stage['name'],'age_exposure':[lo,hi],'objects':rows,'height_m':stage['height_m'],'scale_m_per_original_pixel':stage['metres_per_pixel']})

# The actual painted lower edge of the collapse drawing remains as disturbed
# ground. This is a native geometry/UV band, not a repainted or erased bitmap.
scar=info['scar']
for i,island in enumerate(scar['islands']):
    ob=mesh_from_pixels(f'persistent painted broken ground {i:02d}',island['contour'],scar['anchor'],scar['metres_per_pixel'],scarpaint,-.18,13,None,terrain=True)
    ob['native_UV_band']=str(scar['native_UV_band_only'])

# Reuse genuine small painted clods from the original atlas. Their native mesh
# silhouettes and UVs carry painted thickness; no flat dark proxy polygons.
samples=[v for v in info['stages'][2]['islands'][1:] if v['pixel_area']>50][:10]
assert len(samples)>=7
specs=[(-3.0,4.8,15.,3,.048),(-2.1,5.8,16.,3,.038),(-1.0,6.1,17.,4,.061),(-.25,5.1,15.,3,.031),(.85,6.3,18.,4,.047),(1.55,5.5,15.,5,.067),(2.7,4.9,16.,4,.042),(3.6,4.9,17.,5,.052)]
debris=[]
for i,(vx,vz,g,birth,rad) in enumerate(specs):
    island=samples[i%len(samples)];p=island['contour']
    minx=min(x for x,y in p);maxx=max(x for x,y in p);miny=min(y for x,y in p);maxy=max(y for x,y in p)
    anchor=[(minx+maxx)/2,(miny+maxy)/2];scale=rad*2/max(maxx-minx,maxy-miny)
    ob=mesh_from_pixels(f'painted airborne clod {i:02d}',p,anchor,scale,chipmat,-.10-.012*i,birth,None)
    base=[v.co.copy() for v in ob.data.vertices]
    for v in base:v.z-=floor0
    theta0=.22*i;spin=(4.2+.6*i)*(-1 if i%2 else 1);rest=.10*(-1 if i%2 else 1)
    flight=2*vz/g
    for _ in range(12):
        x=vx*flight*math.exp(-.14*flight);theta=theta0+spin*flight
        support=-min(-p.x*math.sin(theta)+p.z*math.cos(theta) for p in base)
        delta=floor0+.025-floor_z(x)-support
        flight=(vz+math.sqrt(max(0,vz*vz+2*g*delta)))/g
    landage=birth+flight*24;landx=vx*flight*math.exp(-.14*flight);landangle=theta0+spin*flight
    for age in range(121):
        u=max(0,age-birth)/24;after=max(0,u-flight)
        if u<flight:
            x=vx*u*math.exp(-.14*u);theta=theta0+spin*u;z=floor0+.025+vz*u-.5*g*u*u
        else:
            x=landx+vx*.017*(1-math.exp(-12*after));theta=rest+(landangle-rest)*math.exp(-22*after)
            support=-min(-p.x*math.sin(theta)+p.z*math.cos(theta) for p in base)
            z=floor_z(x)+support+max(0,.6*after-.5*g*after*after)
        key=ob.shape_key_add(name=f'AGE_{age:03d}');key.interpolation='KEY_LINEAR'
        co=math.cos(theta);sn=math.sin(theta)
        for d,p0 in zip(key.data,base):d.co=(x+co*p0.x+sn*p0.z,p0.y,z-sn*p0.x+co*p0.z)
    ob.data.shape_keys.use_relative=False;drive(ob.data.shape_keys,'eval_time','10*max(0,min(120,t))')
    bottom=min(v.co.z for v in key.data);error=abs(bottom-floor_z(x));assert error<1e-5,error
    debris.append({'name':ob.name,'birth_age':birth,'landing_age':landage,'landing_x':landx,'final_floor_error_m':error,'original_painted_fragment_pixel_bounds':[minx,miny,maxx,maxy]})

r['construction']='Four original built-in imagegen RGBA stages on alpha-traced editable native contour meshes; four hidden real GP outline guides; eight native painted clod arcs; native lower-edge painted ground scar. No new choreography, camera or light.'
r['artistic_acceptance']=False
r['original_light_preserved']='v043 original physical point light, exact origin and first14-frame envelope; no additional light.'
s.frame_start=1801;s.frame_end=1920;s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100
s.render.threads_mode='FIXED';s.render.threads=2
s.frame_set(1833);bpy.context.view_layer.update()
native=P/'native/WTSC_Painted_Main_Impact_Context_v015.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
asset=P/'native/WTSC_Painted_Main_Impact_Append_v015.blend'
bpy.data.libraries.write(str(asset),{c},fake_user=True,compress=True)
report={'native_context':str(native),'native_append':str(asset),'source':str(SOURCE),'source_sha256':source_sha,
 'source_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_sha,
 'blender':bpy.app.version_string,'scene':s.name,'collection':c.name,'root':r.name,'origin':list(r.location),
 'impact_start':1824,'native_resolution':[3840,2160],'fps':24,'range':[1801,1920],
 'original_image_RGBA_preserved':True,'texture_pixels':[W,H],'texture_claim':'Original2172x724atlas; native output is3840x2160, no texture4Kclaim.',
 'texture_sha256':hashlib.sha256(atlas_path.read_bytes()).hexdigest(),'texture_source':str(atlas_path),
 'drawings':drawings,'debris':debris,'object_count':len(c.all_objects),'original_light_unchanged':True,
 'old_geometry_disabled_only_in_context_copy':hidden_prior,'rendered':False,'artistic_acceptance':False,
 'limits':['Four replacement drawings may exhibit visible phase jumps; consecutive native frame review required.',
 'Scar is layered painted disturbance; it does not excavate physical terrain.',
 'Native fragment contacts approximate the prior measured alpha terrain edge.',
 'No body/character/camera/music edits, no full-trailer integration.']}
(P/'evidence/build_main_impact.json').write_text(json.dumps(report,indent=2))
print('PAINTED_MAIN_IMPACT_V015_BUILT',json.dumps({k:report[k] for k in ('native_context','native_append','source_unchanged','object_count')}),flush=True)
