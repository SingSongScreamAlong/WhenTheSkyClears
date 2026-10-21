"""Distinct compact onset drawings and terrain-seated authored chip contacts."""
import bpy,math,random,json,re,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv011 | compact brief impact low dust'];bpy.context.window.scene=s
oldroot=bpy.data.objects['FXv011 | fixed impact anchor and controls'];origin=oldroot.location.copy();profile=json.loads((P/'evidence/visible_terrain_profile.json').read_text())['profile']
for col in list(s.collection.children):s.collection.children.unlink(col)
for o in list(s.collection.objects):
    if o!=s.camera:s.collection.objects.unlink(o)
s.name='FXv013 | drawn expansion and seated contacts';s.frame_start=1;s.frame_end=72;s.render.fps=24;s.render.fps_base=1;s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=24;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.media_type='IMAGE'
c=bpy.data.collections.new('FXv013 | DRAWN COMPACT IMPACT | distinct onset and contacts');s.collection.children.link(c)
def interp(x):
    if x<=profile[0][0]:return profile[0][1]
    if x>=profile[-1][0]:return profile[-1][1]
    j=next(i for i in range(len(profile)-1) if profile[i][0]<=x<profile[i+1][0]);a,b=profile[j],profile[j+1];return a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0])
q=world_to_camera_view(s,s.camera,origin);qz=world_to_camera_view(s,s.camera,origin+Vector((0,0,1)));qx=world_to_camera_view(s,s.camera,origin+Vector((1,0,0)));px_per_m=(qx.x-q.x)*1920;py_per_m=(qz.y-q.y)*1080;screen_x=q.x*1920;old_y=(1-q.y)*1080;target_y=interp(screen_x);origin.z+=(old_y-target_y)/py_per_m
r=bpy.data.objects.new('FXv013 | terrain anchor and controls',None);c.objects.link(r);r.location=origin;r.empty_display_type='CIRCLE';r.empty_display_size=.25
for k,v in {'start_frame':7.,'speed':1.,'size':1.,'intensity':1.,'age':0.,'painted':0.}.items():r[k]=v
def drive(owner,path,expr,index=None):
    f=owner.driver_add(path) if index is None else owner.driver_add(path,index);f.driver.type='SCRIPTED'
    for v in list(f.driver.variables):f.driver.variables.remove(v)
    for name,key in [('t','age'),('start','start_frame'),('speed','speed'),('S','size'),('I','intensity'),('P','painted')]:
        if not re.search(r'\b'+name+r'\b',expr):continue
        v=f.driver.variables.new();v.name=name;v.type='SINGLE_PROP';v.targets[0].id=r;v.targets[0].data_path='["'+key+'"]'
    f.driver.expression=expr;return f
drive(r,'["age"]','(frame-start)*speed')
for a in range(3):drive(r,'scale','max(.01,S)',a)
bpy.context.view_layer.update()
def ground_z(x):return (target_y-interp(screen_x+px_per_m*x))/py_per_m
atlas=bpy.data.images.get('FXv003 | ORIGINAL four cold forms | packed straight alpha')
if not atlas:atlas=bpy.data.images.load(str(P.parent/'benchmark_v003/assets/Cold_Smoke_Atlas_4Forms_v003.png'));atlas.pack()
def material(name,color,opacity=1,grain=.55):
    m=bpy.data.materials.new('FXv013 | '+name);m.use_nodes=True;m.surface_render_method='DITHERED';nt=m.node_tree;nt.nodes.clear();uv=nt.nodes.new('ShaderNodeTexCoord');scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(.34,.34,1);nt.links.new(uv.outputs['UV'],scale.inputs[0]);offset=nt.nodes.new('ShaderNodeVectorMath');offset.operation='ADD';offset.inputs[1].default_value=(.08,.58,0);nt.links.new(scale.outputs[0],offset.inputs[0]);tex=nt.nodes.new('ShaderNodeTexImage');tex.image=atlas;nt.links.new(offset.outputs[0],tex.inputs[0]);hs=nt.nodes.new('ShaderNodeHueSaturation');hs.inputs['Saturation'].default_value=.12;hs.inputs['Value'].default_value=.85;nt.links.new(tex.outputs[0],hs.inputs['Color']);tint=nt.nodes.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(*color,1);nt.links.new(hs.outputs[0],tint.inputs[1]);wash=nt.nodes.new('ShaderNodeMixRGB');wash.inputs[0].default_value=grain;wash.inputs[1].default_value=(*color,1);nt.links.new(tint.outputs[0],wash.inputs[2]);mode=nt.nodes.new('ShaderNodeMixRGB');drive(mode.inputs[0],'default_value','P');mode.inputs[1].default_value=(*color,1);nt.links.new(wash.outputs[0],mode.inputs[2]);em=nt.nodes.new('ShaderNodeEmission');nt.links.new(mode.outputs[0],em.inputs[0]);edge=nt.nodes.new('ShaderNodeAttribute');edge.attribute_name='FX_edge';alpha=nt.nodes.new('ShaderNodeMath');alpha.operation='MULTIPLY';nt.links.new(edge.outputs['Fac'],alpha.inputs[0]);drive(alpha.inputs[1],'default_value',f'{opacity}*I');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=105;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.7;nt.links.new(uv.outputs['UV'],noise.inputs['Vector']);rng=nt.nodes.new('ShaderNodeMapRange');rng.clamp=True;rng.inputs['From Min'].default_value=.27;rng.inputs['From Max'].default_value=.72;rng.inputs['To Min'].default_value=1 if any(term in name for term in ['chips','soil nicks','contact shadow']) else .50;rng.inputs['To Max'].default_value=1;nt.links.new(noise.outputs['Fac'],rng.inputs['Value']);grainmode=nt.nodes.new('ShaderNodeMixRGB');grainmode.inputs[1].default_value=(1,1,1,1);drive(grainmode.inputs[0],'default_value','P');nt.links.new(rng.outputs[0],grainmode.inputs[2]);pigmentalpha=nt.nodes.new('ShaderNodeMath');pigmentalpha.operation='MULTIPLY';nt.links.new(alpha.outputs[0],pigmentalpha.inputs[0]);nt.links.new(grainmode.outputs[0],pigmentalpha.inputs[1]);tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(pigmentalpha.outputs[0],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],out.inputs[0]);return m
M={'earth':material('rupture charcoal wash',(.060,.058,.049),.9,.72),'hot':material('muted ochre initial impulse',(.48,.26,.08),.95,.35),'cream':material('brief pale impulse accent',(.72,.55,.27),1,.25),'shade':material('drawn inner shadow',(.013,.018,.018),.65,.6),'dust':material('low breakup wash',(.14,.135,.115),.36,.75),'faint':material('last sparse soil strokes',(.13,.135,.125),.14,.75),'scar':material('irregular persistent soil nicks',(.023,.028,.026),.68,.7),'chip':material('small varied painted chips',(.038,.046,.042),1,.65),'contact':material('brief low contact dust',(.27,.25,.20),.68,.30),'contactlate':material('contact dust torn thin',(.18,.17,.14),.25,.40),'shadow':material('local contact shadow',(.012,.016,.015),.28,.4)}
drawings=[]
def poly(name,points,mat,lo=None,hi=None,y=-.10,terrain=False):
    soft=name.startswith('A') or name.startswith('landing')
    if soft:
        # Two corner-cut passes round the authored contours; every exposure
        # still has its own distinct mesh and outward shape change.
        for _ in range(2):
            smooth=[]
            for j,p in enumerate(points):
                q=points[(j+1)%len(points)]
                smooth += [(.78*p[0]+.22*q[0],.78*p[1]+.22*q[1]),(.22*p[0]+.78*q[0],.22*p[1]+.78*q[1])]
            points=smooth
    feather=.86 if name.startswith('landing') else (.90 if soft else .965)
    pts=[(x,z+(ground_z(x) if terrain else 0)) for x,z in points];cx=sum(x for x,z in pts)/len(pts);cz=sum(z for x,z in pts)/len(pts);inner=[(cx+(x-cx)*feather,cz+(z-cz)*feather) for x,z in pts];V=[(x,y,z) for x,z in inner+pts];n=len(pts);F=[tuple(range(n))]+[(i,n+i,n+(i+1)%n,(i+1)%n) for i in range(n)];me=bpy.data.meshes.new(name);me.from_pydata(V,[],F);me.materials.append(mat);me.update();uv=me.uv_layers.new(name='Fixed brush field per distinct drawing')
    for loop in me.loops:x,yy,z=me.vertices[loop.vertex_index].co;uv.data[loop.index].uv=((x+.85)/1.7,(z+.12)/.55)
    attr=me.attributes.new('FX_edge','FLOAT','POINT')
    for i,d in enumerate(attr.data):d.value=1 if i<n else 0
    o=bpy.data.objects.new('FXv013 | '+name,me);c.objects.link(o);o.parent=r
    if lo is not None:
        expr=f'not ({lo}<=t<{hi})' if hi is not None else f't<{lo}'
        drive(o,'hide_render',expr);drive(o,'hide_viewport',expr)
    if lo is not None and hi is not None:drawings.append({'object':o.name,'age_range':[lo,hi],'vertices':len(V),'bounds':[min(x for x,z in pts),min(z for x,z in pts),max(x for x,z in pts),max(z for x,z in pts)],'contour':pts})
    return o
# All contours below are separate authored vector drawings. No scaling/morphing
# a mature raster; binary exposures, different silhouettes/topology and breakup.
poly('A0 seed tear',[(-.07,0),(-.08,.025),(-.035,.045),(-.015,.105),(.025,.078),(.05,.085),(.033,.03),(.075,.012),(.04,0)],M['hot'],0,1)
poly('A0 cream nick',[(-.032,0),(-.026,.028),(.005,.067),(.025,.02),(.032,0)],M['cream'],0,1,y=-.12)
poly('A1 outward rupture',[(-.22,0),(-.20,.045),(-.28,.09),(-.17,.105),(-.145,.18),(-.07,.145),(-.025,.225),(.035,.18),(.10,.205),(.125,.125),(.235,.115),(.175,.06),(.25,.02),(.16,0),(.04,.02),(-.09,0)],M['earth'],1,2)
poly('A1 ochre fork',[(-.17,.012),(-.16,.06),(-.08,.065),(-.09,.12),(-.025,.10),(.015,.155),(.045,.08),(.13,.08),(.10,.028),(.18,.01),(.035,.005)],M['hot'],1,2,y=-.115)
poly('A1 cream core',[(-.07,.004),(-.06,.035),(-.025,.045),(.005,.09),(.03,.045),(.07,.022),(.055,.004)],M['cream'],1,2,y=-.13)
poly('A2 split crown',[(-.36,0),(-.29,.045),(-.37,.11),(-.24,.10),(-.26,.18),(-.14,.16),(-.13,.265),(-.05,.22),(.03,.29),(.09,.22),(.20,.245),(.19,.155),(.34,.16),(.29,.08),(.39,.04),(.30,.005),(.14,.025),(0,.012),(-.16,.025)],M['earth'],2,3)
poly('A2 ochre opening',[(-.22,.012),(-.16,.065),(-.11,.055),(-.09,.13),(-.02,.105),(.015,.16),(.07,.08),(.16,.10),(.12,.035),(.24,.025),(.08,.005)],M['hot'],2,3,y=-.12)
poly('A2 drawn underfold',[(-.30,.01),(-.19,.06),(-.09,.045),(-.055,.09),(.02,.06),(.07,.012),(-.07,.022),(-.18,.008)],M['shade'],2,3,y=-.14)
L=[(-.47,0),(-.46,.035),(-.52,.08),(-.40,.08),(-.36,.13),(-.29,.10),(-.26,.18),(-.18,.14),(-.19,.085),(-.10,.045),(-.16,.008)]
R=[(.12,.01),(.15,.055),(.22,.065),(.25,.13),(.31,.09),(.37,.155),(.40,.09),(.52,.07),(.47,.025),(.55,.005),(.34,.012)]
poly('A3 tear outward LEFT',L,M['earth'],3,4);poly('A3 tear outward RIGHT',R,M['earth'],3,4)
poly('A3 broken center',[(-.08,.012),(-.10,.07),(-.05,.115),(.0,.08),(.055,.105),(.07,.035),(.12,.014)],M['dust'],3,4,y=-.12)
poly('A3 small heat fragment',[(-.09,.01),(-.045,.055),(-.018,.024),(.028,.04),(.08,.006)],M['hot'],3,4,y=-.13)
poly('A4 departing left',[(-.64,.004),(-.58,.025),(-.62,.06),(-.54,.06),(-.49,.095),(-.42,.065),(-.36,.075),(-.38,.026),(-.29,.008),(-.47,.004)],M['dust'],4,5)
poly('A4 departing right',[(.30,.01),(.36,.04),(.40,.035),(.44,.085),(.49,.05),(.58,.065),(.55,.025),(.67,.004),(.49,.008)],M['dust'],4,5)
poly('A5 low left stroke',[(-.77,.002),(-.67,.02),(-.68,.04),(-.61,.03),(-.55,.05),(-.52,.023),(-.40,.007),(-.61,.003)],M['faint'],5,7)
poly('A5 low right stroke',[(.40,.004),(.48,.03),(.53,.026),(.57,.045),(.60,.02),(.75,.005),(.59,.002)],M['faint'],5,7)
poly('A7 last left nick',[(-.83,.002),(-.76,.018),(-.70,.03),(-.66,.015),(-.57,.004)],M['faint'],7,9)
poly('A7 last right nick',[(.56,.004),(.64,.023),(.69,.02),(.76,.008),(.84,.002)],M['faint'],7,9)
# Several short patches follow the measured terrain; no straight level streak.
poly('persistent broken mark left',[(-.33,.010),(-.28,.027),(-.23,.018),(-.18,.032),(-.10,.015),(-.14,.006),(-.24,.010)],M['scar'],1,None,terrain=True)
poly('persistent broken mark center',[(-.12,.009),(-.07,.024),(-.025,.019),(.025,.031),(.07,.014),(.14,.024),(.12,.006),(.025,.011),(-.06,.005)],M['scar'],1,None,terrain=True)
poly('persistent broken mark right',[(.14,.011),(.20,.028),(.25,.016),(.32,.025),(.37,.013),(.29,.006),(.23,.011)],M['scar'],2,None,terrain=True)
# Distinct chip sizes/shapes and contact times. All geometry keys are rigid
# transforms; floor support is computed from each actual rotated contour.
rng=random.Random(12219);specs=[(-2.1,3.4,15,0,.050),(-1.3,4.2,15,1,.035),(-.45,4.8,15,0,.064),(.70,2.8,15,2,.026),(1.25,4.8,12,3,.048),(2.30,2.4,15,0,.038),(1.3,3.8,15,1,.030)];debris=[]
for i,(vx,vz,g,birth,rad) in enumerate(specs):
    n=9+i%3;shape=[]
    for j in range(n):a=j*2*math.pi/n;rr=rad*rng.uniform(.75,1.20);shape.append((rr*math.cos(a)*rng.uniform(.8,1.3),rr*math.sin(a)*rng.uniform(.6,1.1)))
    shape=[(.125*shape[(j-1)%n][0]+.75*p[0]+.125*shape[(j+1)%n][0],.125*shape[(j-1)%n][1]+.75*p[1]+.125*shape[(j+1)%n][1]) for j,p in enumerate(shape)]
    o=poly(f'varied coherent chip{i:02d}',shape,M['chip'],birth,None,y=-.055-.007*i);base=[v.co.copy() for v in o.data.vertices];theta0=rng.uniform(-1,1);spin=rng.uniform(7,12)*(1 if i%2 else -1);rest=rng.uniform(-.45,.45)
    flight=2*vz/g
    for it in range(8):
        lx=vx*flight*math.exp(-.13*flight);theta=theta0+spin*flight;support=-min(-p.x*math.sin(theta)+p.z*math.cos(theta) for p in base);floor=ground_z(lx);flight=(vz+math.sqrt(max(0,vz*vz+2*g*(.035-floor-support))))/g
    lx=vx*flight*math.exp(-.13*flight);land_age=birth+flight*24;bounce=rng.uniform(.45,.78);slide=vx*rng.uniform(.015,.035);end_angle=theta0+spin*flight;centers=[]
    for age in range(73):
        u=max(0,age-birth)/24;after=max(0,u-flight)
        if u<flight:x=vx*u*math.exp(-.13*u);theta=theta0+spin*u;z=.035+vz*u-.5*g*u*u
        else:
            x=lx+slide*(1-math.exp(-13*after));theta=rest+(end_angle-rest)*math.exp(-24*after);support=-min(-p.x*math.sin(theta)+p.z*math.cos(theta) for p in base);z=ground_z(x)+support+max(0,bounce*after-.5*g*after*after)
        key=o.shape_key_add(name=f'AGE_{age:03d}');key.interpolation='KEY_LINEAR';co=math.cos(theta);sn=math.sin(theta)
        for d,p in zip(key.data,base):d.co=(x+co*p.x+sn*p.z,p.y,z-sn*p.x+co*p.z)
        centers.append([x,z])
    o.data.shape_keys.use_relative=False;drive(o.data.shape_keys,'eval_time','10*max(0,min(72,t))')
    finalkey=o.data.shape_keys.key_blocks[-1];finalx=centers[-1][0];bottom=min(v.co.z for v in finalkey.data);error=abs(bottom-ground_z(finalx));assert error<1e-5,error
    shpts=[(finalx+rad*1.35*math.cos(j*math.pi/8),ground_z(finalx)+.012+.007*math.sin(j*math.pi/8)) for j in range(16)];sh=poly(f'contact shadow seated{i:02d}',shpts,M['shadow'],land_age-.5,None,y=-.15)
    debris.append({'piece':i,'radius':rad,'birth_age':birth,'apex_age':birth+vz/g*24,'landing_age':land_age,'landing_x':lx,'final_x':finalx,'terrain_contact_pixel_y':interp(screen_x+px_per_m*finalx),'final_bottom_error_metres':error})
    if i in [0,2,4,5]:
        floor=ground_z(lx)
        def puffs(name,points,mat,lo,hi):
            if 'B split' in name or 'C torn' in name:points=[(x*1.15,z*1.65) for x,z in points]
            poly(name,[(lx+x,floor+z) for x,z in points],mat,lo,hi,y=-.16)
        puffs(f'landing{i} A compression',[(-.07,.012),(-.04,.038),(-.01,.028),(.025,.04),(.075,.012),(.04,.003),(-.04,.003)],M['shade'],land_age,land_age+1)
        puffs(f'landing{i} B split low puff',[(-.14,.006),(-.12,.025),(-.14,.043),(-.08,.038),(-.055,.07),(-.01,.05),(.035,.066),(.055,.035),(.105,.044),(.14,.012),(.07,.006),(.015,.014),(-.06,.006)],M['contact'],land_age+1,land_age+4)
        puffs(f'landing{i} C torn trail',[(-.19,.003),(-.15,.022),(-.12,.018),(-.08,.037),(-.04,.019),(.0,.012),(.07,.029),(.10,.019),(.18,.005),(.08,.003),(-.02,.006),(-.11,.003)],M['contactlate'],land_age+4,land_age+6)
for node in s.compositing_node_group.nodes:
    if node.type=='R_LAYERS':node.scene=s;node.layer='RUPTURE'
r['construction']='Distinct manually authored vector onset drawings with binary exposures; geometry changes outward and tears into separate strokes. Seven varied rigid chip paths seated to measured terrain, four brief contact cues. No mature painting scale/crossfade, no global smoke volume.'
s.frame_set(9);r.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update();native=P/'native/WTSC_Drawn_Impact_Plain_v013.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
report={'blender':bpy.app.version_string,'fps':24,'frames':[1,72],'impact_frame':7,'root':list(r.location),'source_contact_pixel':[screen_x,target_y],'source_old_contact_y':old_y,'root_dropped_pixels':target_y-old_y,'drawings':drawings,'debris':debris,'global_smoke_volume':False,'new_simulation':False,'crossfade_of_paintings':False,'animated_scaling_of_onset':False,'onset_method':'Separate native vector drawings; each contour explicitly authored, exposed on an age interval; no pose crossfade. Pigment finish modulates color and local opacity grain; separate native contours define the silhouettes.','refinement':'Rounded distinct contours, softened pigment edges, less saturated initial heat, higher contrast brief landing cues; no additional smoke volume.','status':'Plain keys require actual shot-size review before painterly finish or full proof.'}
(P/'evidence/build_drawn.json').write_text(json.dumps(report,indent=2));print('DRAWN_IMPACT_BUILT',json.dumps({k:v for k,v in report.items() if k not in ['drawings','debris']}),flush=True)
