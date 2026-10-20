"""Isolated main-impact candidate. No rendering, source file or choreography edits.

Run with Blender 5.2.2 background, opening the v047g native source first.
Creates native editable X/Z contour meshes, hidden real GP contour guides,
individually authored chip trajectories and persistent displaced-earth marks.
All output is contained in effects/main_impact_v014.
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
s.name = 'WTSC_MAIN_GROUND_IMPACT_CANDIDATE_v014'
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

c = bpy.data.collections.new('FXv014 | MAIN SOIL RUPTURE | separate contour exposures')
s.collection.children.link(c)
guides = bpy.data.collections.new('FXv014 | GP contour editing guides | hidden')
c.children.link(guides)
r = bpy.data.objects.new('FXv014 | fixed ground anchor and controls', None)
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

atlas_path = PROJECT/'effects/benchmark_v003/assets/Cold_Smoke_Atlas_4Forms_v003.png'
atlas = bpy.data.images.load(str(atlas_path),check_existing=True)
atlas.pack()
atlas.name = 'FXv014 | project original imagegen pigment | packed'

def material(name, color, opacity=1., grain=.65):
    m=bpy.data.materials.new('FXv014 | '+name)
    m.use_nodes=True
    m.surface_render_method='DITHERED'
    n=m.node_tree.nodes;n.clear();L=m.node_tree.links
    uv=n.new('ShaderNodeTexCoord')
    tex=n.new('ShaderNodeTexImage');tex.image=atlas
    L.new(uv.outputs['UV'],tex.inputs['Vector'])
    bw=n.new('ShaderNodeRGBToBW');L.new(tex.outputs['Color'],bw.inputs[0])
    tone=n.new('ShaderNodeMapRange');tone.clamp=True
    tone.inputs['From Min'].default_value=.025
    tone.inputs['From Max'].default_value=.42
    tone.inputs['To Min'].default_value=.38
    tone.inputs['To Max'].default_value=1.4
    L.new(bw.outputs[0],tone.inputs['Value'])
    tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY'
    tint.inputs[0].default_value=1.;tint.inputs[1].default_value=(*color,1)
    L.new(tone.outputs[0],tint.inputs[2])
    paint=n.new('ShaderNodeMixRGB');drive(paint.inputs[0],'default_value',f'{grain}*P')
    paint.inputs[1].default_value=(*color,1);L.new(tint.outputs[0],paint.inputs[2])
    em=n.new('ShaderNodeEmission');L.new(paint.outputs[0],em.inputs[0])
    edge=n.new('ShaderNodeAttribute');edge.attribute_name='FX_edge'
    alpha=n.new('ShaderNodeMath');alpha.operation='MULTIPLY'
    L.new(edge.outputs['Fac'],alpha.inputs[0]);drive(alpha.inputs[1],'default_value',f'{opacity}*I')
    tr=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader')
    L.new(alpha.outputs[0],mix.inputs[0]);L.new(tr.outputs[0],mix.inputs[1]);L.new(em.outputs[0],mix.inputs[2])
    out=n.new('ShaderNodeOutputMaterial');L.new(mix.outputs[0],out.inputs[0])
    return m

M={
 'soil':material('charcoal umber ejected earth',(.055,.049,.040),.98,.8),
 'dark':material('deep torn inner folds',(.012,.016,.017),.87,.65),
 'edge':material('cold brush ridges',(.155,.145,.123),.76,.8),
 'dust':material('low warm grey soil veil',(.19,.178,.15),.40,.8),
 'far':material('distant thin disturbed dust',(.27,.27,.25),.24,.7),
 'hot':material('brief dirty ochre impulse',(.65,.37,.13),.96,.35),
 'core':material('one frame pale fissure',(.97,.74,.38),1.,.25),
 'scar':material('persistent dark ripped ground',(.019,.024,.022),.90,.8),
 'lip':material('raised pale broken soil lip',(.32,.28,.21),.88,.65),
 'chip':material('opaque large soil fragments',(.036,.038,.031),1.,.7),
 'contact':material('short landing brush dust',(.31,.28,.22),.72,.7),
}
drawings=[]
def poly(name, points, key, lo, hi=None, y=0., feather=.965, ground=False, guide=False):
    points=[(x,z+(floor_z(x) if ground else floor0)) for x,z in points]
    cx=sum(p[0] for p in points)/len(points);cz=sum(p[1] for p in points)/len(points)
    inner=[(cx+(x-cx)*feather,cz+(z-cz)*feather) for x,z in points]
    n=len(points);verts=[(x,y,z) for x,z in inner+points]
    faces=[tuple(range(n))]+[(i,n+i,n+(i+1)%n,(i+1)%n) for i in range(n)]
    me=bpy.data.meshes.new('FXv014 | '+name);me.from_pydata(verts,[],faces);me.materials.append(M[key]);me.update()
    uv=me.uv_layers.new(name='World-fixed original pigment sampling')
    for loop in me.loops:
        x,yy,z=me.vertices[loop.vertex_index].co
        uv.data[loop.index].uv=(.10+.25*(x+1.8)/3.6,.55+.25*(z-floor0)/2.2)
    edge=me.attributes.new('FX_edge','FLOAT','POINT')
    for i,d in enumerate(edge.data):d.value=1. if i<n else 0.
    ob=bpy.data.objects.new(me.name,me);c.objects.link(ob);ob.parent=r
    expr=f't<{lo}' if hi is None else f'not ({lo}<=t<{hi})'
    drive(ob,'hide_render',expr);drive(ob,'hide_viewport',expr)
    ob['age_exposure_start']=float(lo)
    ob['age_exposure_end']=float(hi) if hi is not None else 100000.
    ob['construction']='Independent native contour drawing, binary exposure; no scaling a complete painting.'
    drawings.append({'name':ob.name,'age':[lo,hi],'role':key,'points':points,'depth_y':y})
    if guide:
        gp=bpy.data.grease_pencils.new('FXv014 | GP | '+name)
        go=bpy.data.objects.new(gp.name,gp);guides.objects.link(go);go.parent=r
        layer=gp.layers.new('Editable main contour',set_active=True)
        d=layer.frames.new(1).drawing;d.add_strokes([len(points)])
        stroke=d.strokes[0];stroke.cyclic=True
        for pt,(x,z) in zip(stroke.points,points):pt.position=(x,y,z);pt.radius=.001;pt.opacity=1
        go.hide_render=True;go.hide_viewport=True
        go['purpose']='Native GP source contour editing guide. Painted mesh supplies visible filled surface.'
    return ob

# Separate deliberately asymmetric silhouettes: a ground wedge tears into three
# upward diagonal tongues, which fragment and fall outward. No mushroom cap.
FORMS=[
 ('00 fissure',0,1,[(-.16,0),(-.10,.04),(-.06,.02),(-.025,.20),(.02,.12),(.08,.06),(.18,0)]),
 ('01 vertical impulse',1,2,[(-.35,0),(-.28,.09),(-.22,.06),(-.18,.36),(-.10,.27),(-.06,.62),(.0,.43),(.09,.50),(.14,.20),(.28,.24),(.35,.04),(.25,0)]),
 ('02 torn soil fan',2,4,[(-.59,0),(-.55,.12),(-.66,.28),(-.42,.24),(-.45,.65),(-.30,.52),(-.34,.91),(-.19,.70),(-.10,1.16),(.01,.84),(.15,1.02),(.26,.56),(.39,.72),(.44,.31),(.68,.39),(.59,.15),(.80,.02),(.44,0)]),
 ('04 three split tongues',4,6,[(-.78,0),(-.90,.18),(-.73,.27),(-.84,.70),(-.62,.58),(-.69,1.13),(-.46,.92),(-.49,1.43),(-.25,1.15),(-.15,1.62),(.00,1.24),(.19,1.44),(.29,1.02),(.45,1.19),(.53,.63),(.76,.90),(.74,.42),(1.01,.49),(.88,.17),(1.13,.04),(.52,0)]),
 ('06 outward tear',6,9,[(-1.02,0),(-1.13,.17),(-.91,.26),(-1.02,.66),(-.77,.57),(-.84,1.02),(-.62,.91),(-.72,1.39),(-.42,1.21),(-.38,1.75),(-.21,1.52),(-.08,1.79),(.07,1.35),(.31,1.58),(.36,1.16),(.60,1.32),(.65,.83),(.90,1.02),(.86,.57),(1.15,.65),(1.02,.25),(1.35,.12),(1.18,0)]),
 ('09 broken falling crown',9,13,[(-1.22,0),(-1.32,.20),(-1.10,.29),(-1.28,.69),(-1.01,.59),(-1.10,1.03),(-.79,.92),(-.82,1.35),(-.57,1.19),(-.49,1.65),(-.29,1.44),(-.13,1.73),(.02,1.31),(.26,1.45),(.36,1.02),(.65,1.20),(.71,.80),(1.02,.91),(.99,.51),(1.30,.52),(1.22,.25),(1.54,.09),(1.29,0)]),
 ('13 folded collapse',13,18,[(-1.35,0),(-1.44,.19),(-1.22,.28),(-1.38,.58),(-1.09,.52),(-1.13,.87),(-.84,.78),(-.85,1.17),(-.60,1.01),(-.47,1.42),(-.26,1.15),(-.10,1.41),(.06,1.09),(.37,1.27),(.41,.89),(.73,1.01),(.79,.64),(1.13,.71),(1.16,.38),(1.49,.38),(1.40,.13),(1.67,.03),(1.25,0)]),
 ('18 separated low wings',18,24,[(-1.49,0),(-1.55,.19),(-1.28,.26),(-1.39,.48),(-1.11,.44),(-1.08,.74),(-.78,.65),(-.66,.99),(-.49,.76),(-.22,.95),(-.06,.70),(.16,.86),(.31,.64),(.61,.79),(.72,.47),(1.03,.58),(1.16,.34),(1.46,.41),(1.53,.16),(1.78,.05),(1.28,0)]),
]
for name,lo,hi,points in FORMS:
    poly(name,points,'soil',lo,hi,y=.02,feather=.985,guide=True)

# Internal ripped brush shapes distinguish overlapping planes; they do not
# outline every edge uniformly or make a bright smoke ball.
for lo,hi,shift,height,width in [(2,4,-.10,.95,.38),(4,6,-.23,1.45,.50),(6,9,-.29,1.62,.62),(9,13,-.32,1.55,.72),(13,18,-.27,1.26,.84),(18,24,-.16,.86,.99)]:
    p=[(shift-width*.45,.03),(shift-width*.55,height*.26),(shift-width*.23,height*.40),(shift-width*.42,height*.63),(shift-width*.10,height*.55),(shift+.02,height),(shift+.14,height*.57),(shift+width*.31,height*.74),(shift+width*.26,height*.32),(shift+width*.58,height*.21),(shift+width*.43,.04)]
    poly(f'{lo:02d} dark inner broken fold',p,'dark',lo,hi,y=-.035,feather=.91)
    p2=[(x+.13,z*.94+.025) for x,z in p[2:-2]]
    poly(f'{lo:02d} dry brushed edge ridge',p2,'edge',lo,hi,y=-.045,feather=.82)

poly('00 pale fissure',[(-.025,0),(-.018,.08),(.005,.16),(.02,.06),(.04,0)],'core',0,1,y=-.10)
poly('01 dirty ochre split',[(-.19,0),(-.16,.17),(-.09,.11),(-.06,.44),(.0,.31),(.07,.36),(.12,.12),(.25,.05),(.13,0)],'hot',1,2,y=-.10)
poly('02 last torn heat',[(-.28,.02),(-.24,.19),(-.16,.15),(-.13,.36),(-.05,.21),(.04,.30),(.08,.09),(.22,.13),(.30,.03)],'hot',2,4,y=-.10,feather=.90)

# Separate near and far low dust veils spread along the ground. Each drawing is
# explicitly authored at its exposure; no continuously growing puff/card.
for lo,hi,w,h,mat in [(2,4,.55,.18,'far'),(4,7,.90,.29,'far'),(7,12,1.25,.39,'dust'),(12,18,1.55,.44,'dust'),(18,26,1.82,.41,'dust'),(26,36,2.05,.30,'dust'),(36,49,2.20,.20,'far'),(49,68,2.31,.12,'far')]:
    pts=[(-w,0),(-w*.91,h*.28),(-w*.80,h*.16),(-w*.72,h*.71),(-w*.54,h*.57),(-w*.41,h),(-w*.19,h*.66),(-w*.07,h*.84),(w*.16,h*.58),(w*.29,h*.90),(w*.45,h*.53),(w*.65,h*.66),(w*.74,h*.24),(w*.90,h*.33),(w,0),(w*.35,.012),(-w*.31,.009)]
    poly(f'{lo:02d} near ground-travelling torn dust',pts,mat,lo,hi,y=-.16,feather=.82,ground=True)
    poly(f'{lo:02d} far thin spreading veil',[(x*.91,z*.73) for x,z in pts],'far',lo+1,hi+2,y=.55,feather=.84,ground=True)

# Persistent scar: multiple non-collinear earth fractures and raised broken lips.
scar_specs=[(-.82,.41),(-.35,.57),(.19,.51),(.70,.38)]
for i,(x,w) in enumerate(scar_specs):
    pts=[(x-w/2,.018),(x-w*.32,.052),(x-w*.18,.039),(x+w*.05,.077),(x+w*.21,.049),(x+w*.38,.064),(x+w/2,.021),(x+w*.17,.006),(x-w*.19,.011)]
    poly(f'persistent ripped soil fracture {i}',pts,'scar',2+i//2,None,y=-.20,ground=True)
    pts=[(x-w*.45,.016),(x-w*.29,.043),(x-w*.11,.024),(x+w*.09,.050),(x+w*.29,.031),(x+w*.43,.045),(x+w*.49,.017),(x+w*.12,.019)]
    poly(f'raised broken earth lip {i}',pts,'lip',5+i,None,y=-.21,ground=True,feather=.94)

# Individually shaped, individually timed rigid fragments; 24fps ballistic flight,
# geometry-based support, two brief bounce/settle poses and permanent contact.
rng=random.Random(1401824)
specs=[(-3.7,5.0,15.,2,.075),(-2.5,5.8,16.,2,.055),(-1.2,6.2,17.,3,.083),(-.4,5.2,15.,2,.038),(.7,6.7,18.,3,.064),(1.4,5.8,15.,4,.091),(2.5,4.9,16.,3,.051),(3.7,5.2,17.,4,.072),(4.2,3.5,15.,5,.037),(-4.1,3.6,16.,5,.034)]
debris=[]
for i,(vx,vz,g,birth,rad) in enumerate(specs):
    n=7+i%4
    shape=[]
    for j in range(n):
        a=j*math.tau/n;rr=rad*rng.uniform(.72,1.15)
        shape.append((rr*math.cos(a)*rng.uniform(.8,1.25),rr*math.sin(a)*rng.uniform(.7,1.1)))
    ob=poly(f'flight fragment {i:02d}',shape,'chip',birth,None,y=-.25-.009*i,feather=.985)
    base=[v.co.copy() for v in ob.data.vertices]
    # poly adds the terrain base; center each fragment before authoring its flight.
    for v in base:v.z-=floor0
    theta0=rng.uniform(-1.,1.);spin=rng.uniform(4.,11.)*(-1 if i%2==0 else 1)
    angle_rest=rng.uniform(-.35,.35)
    flight=2*vz/g
    for _ in range(12):
        x=vx*flight*math.exp(-.16*flight);theta=theta0+spin*flight
        support=-min(-p.x*math.sin(theta)+p.z*math.cos(theta) for p in base)
        delta=floor0+.035-floor_z(x)-support
        flight=(vz+math.sqrt(max(0,vz*vz+2*g*delta)))/g
    land_age=birth+flight*24;landx=vx*flight*math.exp(-.16*flight)
    theta_land=theta0+spin*flight;slide=vx*rng.uniform(.012,.028)
    for age in range(121):
        u=max(0,age-birth)/24;after=max(0,u-flight)
        if u<flight:
            x=vx*u*math.exp(-.16*u);theta=theta0+spin*u
            z=floor0+.035+vz*u-.5*g*u*u
        else:
            x=landx+slide*(1-math.exp(-12*after))
            theta=angle_rest+(theta_land-angle_rest)*math.exp(-22*after)
            support=-min(-p.x*math.sin(theta)+p.z*math.cos(theta) for p in base)
            z=floor_z(x)+support+max(0,.70*after-.5*g*after*after)
        key=ob.shape_key_add(name=f'AGE_{age:03d}');key.interpolation='KEY_LINEAR'
        co=math.cos(theta);sn=math.sin(theta)
        for d,p in zip(key.data,base):d.co=(x+co*p.x+sn*p.z,p.y,z-sn*p.x+co*p.z)
    ob.data.shape_keys.use_relative=False
    drive(ob.data.shape_keys,'eval_time','10*max(0,min(120,t))')
    bottom=min(v.co.z for v in key.data)
    error=abs(bottom-floor_z(x));assert error<1e-5,error
    debris.append({'object':ob.name,'birth_age':birth,'apex_age':birth+vz/g*24,
                   'landing_age':land_age,'landing_x':landx,'final_bottom_error_m':error})
    if i in (0,2,4,5,7,8):
        for stage,lo,hi,w,h in [('A',0,1,.10,.052),('B',1,4,.19,.12),('C',4,7,.27,.065)]:
            puff=[(-w,0),(-w*.75,h*.40),(-w*.67,h*.27),(-w*.43,h*.91),(-w*.09,h*.71),(w*.13,h),(w*.39,h*.52),(w*.61,h*.63),(w,0),(w*.21,.005)]
            poly(f'landing {i:02d} {stage}',[(landx+xx,zz) for xx,zz in puff],'contact',land_age+lo,land_age+hi,y=-.38,ground=True,feather=.84)

r['construction']='Asymmetric soil fans exposed as separate native drawings; ten ballistic fragments and six staggered landing dust cues; persistent scar. No fluid volume or scaling of mature raster cloud.'
r['artistic_acceptance']=False
r['existing_context_light']='Retained original v043 point light and material receivers, exact old origin/start1824. No additional candidate light doubles this context.'
s.frame_start=1801;s.frame_end=1920
s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100
s.render.threads_mode='FIXED';s.render.threads=2
s.frame_set(1832);bpy.context.view_layer.update()
out=P/'native/WTSC_Main_Ground_Impact_Context_v014.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
asset=P/'native/WTSC_Main_Ground_Impact_Append_v014.blend'
bpy.data.libraries.write(str(asset),{c},fake_user=True,compress=True)
report={'native_context':str(out),'native_append':str(asset),'source':str(SOURCE),
 'source_sha256':source_sha,'source_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_sha,
 'blender':bpy.app.version_string,'scene':s.name,'collection':c.name,'root':r.name,
 'origin':list(r.location),'impact_start':1824,'size':1.,'intensity':.94,
 'native_resolution':[3840,2160],'fps':s.render.fps,'range':[1801,1920],
 'old_visual_geometry_disabled_only_in_context_copy':hidden_prior,
 'GP_guides_hidden':True,'visible_paint_surfaces':'native editable contour meshes',
 'source_pigment':str(atlas_path),'source_pigment_sha256':hashlib.sha256(atlas_path.read_bytes()).hexdigest(),
 'drawings':drawings,'debris':debris,'object_count':len(c.all_objects),
 'rendered':False,'artistic_acceptance':False,
 'limits':['Prepared isolated candidate. Native render review required before integration.',
           'Terrain profile is measured from prior shot alpha and approximates the occlusion edge.',
           'Append collection intentionally contains no light. Reuse the exact physical event light and rebind receivers when integrating.',
           'No body, camera, music, full-trailer propagation or production acceptance.']}
(P/'evidence/build_main_impact.json').write_text(json.dumps(report,indent=2))
print('MAIN_IMPACT_V014_BUILT',json.dumps({k:report[k] for k in ('native_context','native_append','source_unchanged','object_count')}),flush=True)
