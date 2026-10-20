"""Original native 2.5D FX; writes only this effects pack. Blender 5.2.2."""
import bpy, math, json, random
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]; R=P.parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
random.seed(81017)
assets=[]; specs=[]
smoke_image=bpy.data.images.load(str(R/'sets/fx/Painted_Smoke_Wisp_v016.png'));smoke_image.name='WTSC original smoke ink | PACKED';smoke_image.alpha_mode='STRAIGHT';smoke_image.pack()

def driver(id,path,root,expr,index=None):
    f=id.driver_add(path) if index is None else id.driver_add(path,index)
    d=f.driver; d.type='SCRIPTED'; d.expression=expr
    for n,prop in [('t','age'),('I','intensity'),('W','wind'),('S','size'),('C','warmth')]:
        v=d.variables.new();v.name=n;v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["'+prop+'"]'
    return f

def root_for(name,kind,frames,seed):
    c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c)
    root=bpy.data.objects.new(name+' | CONTROLS',None);c.objects.link(root);root.empty_display_type='CIRCLE';root.empty_display_size=.3
    props={'start_frame':1.,'speed':1.,'intensity':1.,'size':1.,'wind':.32,'warmth':1.,'age':0.}
    for k,v in props.items():root[k]=v
    root['tint']=(1.,1.,1.);root.id_properties_ui('tint').update(min=0.,max=1.,subtype='COLOR',description='RGB multiplier for every painted effect material; default white preserves charcoal/amber palette')
    for k,mi,ma,desc in [('start_frame',-10000,10000,'First visible frame; offsets all child motion and material animation'),('speed',.1,4,'Playback speed multiplier'),('intensity',0,2,'Opacity, flash and light strength'),('size',.02,20,'Uniform local visual scale; anchored root remains fixed'),('wind',-2,2,'Horizontal billow drift; negative blows left'),('warmth',0,1,'0=charcoal/cool; 1=muted amber fire')]:
        root.id_properties_ui(k).update(min=mi,max=ma,description=desc)
    f=root.driver_add('["age"]'); f.driver.expression='(frame-a)*v'
    for n,k in [('a','start_frame'),('v','speed')]:
        z=f.driver.variables.new();z.name=n;z.type='SINGLE_PROP';z.targets[0].id=root;z.targets[0].data_path='["'+k+'"]'
    rig=bpy.data.objects.new(name+' | SCALE_RIG',None);c.objects.link(rig);rig.parent=root;rig.empty_display_size=.05
    for i in range(3):driver(rig,'scale',root,'S',i)
    root['usage']='Move/rotate CONTROLS for placement. X horizontal; Z up; camera at negativeY. Parent remains at emitter. No handlers or Python namespace required.'
    c['kind']=kind;c['fps']=24;c['frame_range']=f'1-{frames}';c['seed']=seed;c['orientation']='XZ paint plane; +Y depth; origin is fixed ground emitter'
    c.asset_mark();c.asset_data.description=kind+' | editable ink wash meshes, 24fps, XZ, fixed emitter. Root custom properties for offset/speed/size/intensity/wind/warmth.'
    for tag in ['WTSC','Ink wash','2.5D',kind]:c.asset_data.tags.new(tag)
    assets.append((c,root,rig));specs.append({'collection':name,'kind':kind,'frames':frames,'loop':kind.startswith('Loop'),'root':root.name,'seed':seed})
    return c,root,rig

def mesh(c,rig,name,verts,faces,uv=None,mat=None):
    d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update()
    o=bpy.data.objects.new(name,d);c.objects.link(o);o.parent=rig
    if uv:
        u=d.uv_layers.new(name='Paint coordinates')
        for l in d.loops:u.data[l.index].uv=uv[l.vertex_index]
    if mat:d.materials.append(mat)
    return o

def disc(c,rig,name,mat,r=1,seed=0):
    rnd=random.Random(seed);N=48
    vs=[(0,0,0)];uv=[(.5,.5)]
    for i in range(N):
        a=i*math.tau/N;rad=1+.06*math.sin(a*5+seed)+.035*math.sin(a*13+2)
        x=math.cos(a)*rad;z=math.sin(a)*rad
        vs.append((x*r,0,z*r));uv.append((x*.5+.5,z*.5+.5))
    return mesh(c,rig,name,vs,[(0,i+1,(i+1)%N+1) for i in range(N)],uv,mat)

def material(name,root,color,opacity_expr,noise_seed=0,mode='wash',image=None):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.surface_render_method='BLENDED'
    nt=m.node_tree;nt.nodes.clear()
    out=nt.nodes.new('ShaderNodeOutputMaterial');out.location=(940,0)
    mix=nt.nodes.new('ShaderNodeMixShader');mix.location=(720,0)
    tr=nt.nodes.new('ShaderNodeBsdfTransparent');tr.location=(500,-160)
    em=nt.nodes.new('ShaderNodeEmission');em.location=(500,80);em.inputs[0].default_value=(*color,1)
    alpha=nt.nodes.new('ShaderNodeMath');alpha.name='ANIMATED WASH OPACITY';alpha.operation='MULTIPLY';alpha.location=(500,240)
    driver(alpha.inputs[1],'default_value',root,opacity_expr)
    if mode=='warm':
        tint=nt.nodes.new('ShaderNodeMixRGB');tint.blend_type='MIX';tint.inputs[1].default_value=(.28,.28,.26,1);tint.inputs[2].default_value=(*color,1)
        driver(tint.inputs[0],'default_value',root,'C');nt.links.new(tint.outputs[0],em.inputs[0])
    if image:
        tex=nt.nodes.new('ShaderNodeTexImage');tex.image=image;tex.extension='CLIP';tex.location=(-300,300)
        mul=nt.nodes.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;mul.inputs[2].default_value=(*color,1);nt.links.new(tex.outputs['Color'],mul.inputs[1]);nt.links.new(mul.outputs[0],em.inputs[0])
        ramp=nt.nodes.new('ShaderNodeMapRange');ramp.clamp=True;ramp.inputs['From Min'].default_value=.06;ramp.inputs['From Max'].default_value=.90;nt.links.new(tex.outputs['Alpha'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],alpha.inputs[0])
    elif mode=='solid' or mode=='warm': alpha.inputs[0].default_value=1
    else:
        uv=nt.nodes.new('ShaderNodeTexCoord');uv.location=(-1100,0)
        shift=nt.nodes.new('ShaderNodeVectorMath');shift.operation='SUBTRACT';shift.inputs[1].default_value=(.5,.5,0);nt.links.new(uv.outputs['UV'],shift.inputs[0])
        length=nt.nodes.new('ShaderNodeVectorMath');length.operation='LENGTH';nt.links.new(shift.outputs[0],length.inputs[0])
        noise=nt.nodes.new('ShaderNodeTexNoise');noise.noise_dimensions='4D';noise.inputs['Scale'].default_value=8;noise.inputs['Detail'].default_value=4;noise.inputs['Roughness'].default_value=.78;noise.inputs['W'].default_value=noise_seed
        nt.links.new(uv.outputs['UV'],noise.inputs['Vector'])
        grain=nt.nodes.new('ShaderNodeMath');grain.operation='MULTIPLY_ADD';grain.inputs[1].default_value=.22;grain.inputs[2].default_value=-.11;nt.links.new(noise.outputs['Fac'],grain.inputs[0])
        edge=nt.nodes.new('ShaderNodeMath');edge.operation='ADD';nt.links.new(length.outputs['Value'],edge.inputs[0]);nt.links.new(grain.outputs[0],edge.inputs[1])
        ramp=nt.nodes.new('ShaderNodeMapRange');ramp.interpolation_type='SMOOTHSTEP';ramp.clamp=True;ramp.inputs['From Min'].default_value=.15;ramp.inputs['From Max'].default_value=.5;ramp.inputs['To Min'].default_value=.85;ramp.inputs['To Max'].default_value=0;nt.links.new(edge.outputs[0],ramp.inputs[0])
        detail=nt.nodes.new('ShaderNodeMath');detail.operation='MULTIPLY';nt.links.new(ramp.outputs[0],detail.inputs[0]);nt.links.new(noise.outputs['Fac'],detail.inputs[1]);nt.links.new(detail.outputs[0],alpha.inputs[0])
        shade=nt.nodes.new('ShaderNodeMixRGB');shade.inputs[1].default_value=(*[v*.57 for v in color],1);shade.inputs[2].default_value=(*[min(v*1.35+.005,1) for v in color],1);nt.links.new(noise.outputs['Fac'],shade.inputs[0]);nt.links.new(shade.outputs[0],em.inputs[0])
    tint=nt.nodes.new('ShaderNodeMixRGB');tint.name='ROOT RGB TINT';tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1
    if em.inputs[0].is_linked:nt.links.new(em.inputs[0].links[0].from_socket,tint.inputs[1])
    else:tint.inputs[1].default_value=em.inputs[0].default_value[:]
    for i in range(3):
        f=tint.inputs[2].driver_add('default_value',i);f.driver.expression='v';v=f.driver.variables.new();v.name='v';v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path=f'["tint"][{i}]'
    tint.inputs[2].default_value[3]=1;nt.links.new(tint.outputs[0],em.inputs[0])
    nt.links.new(alpha.outputs[0],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs[0])
    m.diffuse_color=(*color,.5);return m

def window(a,b,fade=9):
    return f'max(0,min(1,(t-{a})/{fade},({b}-t)/{fade}))'

def explosion(name,variant):
    c,r,rig=root_for(name,'One shot ground explosion',144,100+variant);rnd=random.Random(100+variant)
    width=[1.5,2.1,1.05][variant];height=[2.1,1.3,1.55][variant]
    r['intensity']=.9 if variant==2 else 1
    # A torn, fleeting warm flash. No smooth spheres or glossy surfaces.
    m=material(name+' flash',r,(.85,.31,.065),f'I*1.6*{window(0,8,1)}',noise_seed=92)
    flash=disc(c,rig,'Flash | short ragged wash',m,seed=variant);flash.location=(0,-.12,.22)
    driver(flash,'scale',r,'.05+.8*min(1,max(0,t)/4)',0);driver(flash,'scale',r,'.05+.65*min(1,max(0,t)/4)',2)
    for j in range(7):
        fm=material(name+f' torn flash stroke {j}',r,(.75,.26,.05),f'I*{window(j%2,7+j%2,1)}',noise_seed=j+31)
        fob=disc(c,rig,f'Torn warm flash stroke {j}',fm,seed=j+91);fob.location=(math.sin(j*2.4)*.15,-.13-j*.003,.25)
        fob.rotation_euler.y=j*.72;fob.scale=(.09,1,.25+j%3*.07)
    # Rising lobes and later rolling sooty shoulders with nonuniform timings.
    for j in range(16):
        delay=(j%5)*2+2;life=132-j%4*6;a=f'max(0,t-{delay})';rise=(j/15)**.85
        col=(.019+rise*.014,.025+rise*.018,.029+rise*.020) if variant!=1 else (.044,.039,.030)
        m=material(f'{name} | ink billow {j:02}',r,col,f'I*1.3*{window(delay,life,8)}',j*1.7)
        ob=disc(c,rig,f'Ink billow {j:02}',m,seed=j*3+variant)
        bx=rnd.uniform(-.45,.45)*width;targetz=.15+rise*height
        ob.location.y=.06+j*.012
        driver(ob,'location',r,f'{bx:.5f}+W*.006*{a}+{.14*math.sin(j*2):.5f}*sin({a}*.035)',0)
        driver(ob,'location',r,f'.10+{targetz:.5f}*(1-exp(-{a}/22))+.0018*{a}',2)
        w=width*(.25+.30*rise);h=height*(.14+.17*rise)
        driver(ob,'scale',r,f'{w}*(.08+.92*(1-exp(-{a}/15)))',0)
        driver(ob,'scale',r,f'{h}*(.08+.92*(1-exp(-{a}/19)))',2)
    for j in range(2):
        m=material(name+f' | packed ink curl {j}',r,(.13,.15,.16),f'I*.84*{window(4+j*4,140,12)}',image=smoke_image)
        w=width*.72;h=height*1.08
        ob=mesh(c,rig,f'Painted granular ink curl {j}',[(-w/2,0,0),(w/2,0,0),(w/2,0,h),(-w/2,0,h)],[(0,1,2,3)],[(0,0),(1,0),(1,1),(0,1)],m);ob.location=((j-.5)*width*.23,-.035-j*.01,.06)
        driver(ob,'scale',r,'.12+.88*(1-exp(-max(0,t-4)/20))',2);driver(ob,'scale',r,'.1+.9*(1-exp(-max(0,t-4)/18))',0)
        ob.shape_key_add(name='Basis');key=ob.shape_key_add(name='Upper smoke lean | root pinned')
        for p in key.data:p.co.x+=(p.co.z/h)**2*width*.3
        driver(key,'value',r,'W*.6*sin(t/39)')
    for j in range(7):
        a=f'max(0,t-{j+3})';side=(-1 if j%2 else 1)
        m=material(f'{name} | floor dust {j}',r,(.33,.30,.24),f'I*.8*{window(j+3,100+j*3,8)}',j+60)
        ob=disc(c,rig,f'Floor rolling dust {j}',m,seed=200+j);ob.location.y=-.04-j*.01
        driver(ob,'location',r,f'{side}*.012*{a}+.10*sin({j})',0);driver(ob,'location',r,f'.035+.0015*{a}',2)
        driver(ob,'scale',r,f'.04+{width*.35}*(1-exp(-{a}/25))',0);driver(ob,'scale',r,f'.025+.12*(1-exp(-{a}/15))',2)
    for j in range(18):
        a=f'max(0,t-{3+j%4})';d=3+j%4;end=40+j%6*3
        m=material(f'{name} | charcoal fleck {j}',r,(.034,.032,.028),f'I*{window(d,end,3)}',mode='solid')
        ob=mesh(c,rig,f'Debris brush fleck {j}',[(-.018,0,0),(.017,0,.012),(.01,0,.045),(-.009,0,.034)],[(0,1,2,3)],mat=m);ob.location.y=-.16
        vx=rnd.uniform(-.045,.045)*width;vz=rnd.uniform(.07,.14)*height/2
        driver(ob,'location',r,f'{vx}*{a}',0);driver(ob,'location',r,f'max(0,.05+{vz}*{a}-.0018*{a}**2)',2);driver(ob,'rotation_euler',r,f'{j}+.12*{a}',1)
    ld=bpy.data.lights.new(name+' | flash light','POINT');ld.color=(1,.29,.07);ld.shadow_soft_size=.8;ld.energy=0
    lo=bpy.data.objects.new(ld.name,ld);c.objects.link(lo);lo.parent=rig;lo.location=(0,-.5,.4);driver(ld,'energy',r,f'80*I*C*{window(0,9,2)}')
    return c,r,rig

def impact(name):
    c,r,rig=root_for(name,'One shot impact puff',72,400)
    for j in range(8):
        a=f'max(0,t-{j%3})';m=material(name+f' wash {j}',r,(.34,.32,.27),f'I*{window(j%3,65-j,7)}',j+85)
        ob=disc(c,rig,f'Impact dry brush {j}',m,seed=j);ob.location.y=j*.014
        driver(ob,'location',r,f'{(j-3.5)*.04}+{(j-3.5)*.003}*{a}+W*.001*{a}',0);driver(ob,'location',r,f'.03+{.12+j%3*.04}*(1-exp(-{a}/8))+.001*{a}',2)
        driver(ob,'scale',r,f'.02+.34*(1-exp(-{a}/12))',0);driver(ob,'scale',r,f'.02+.19*(1-exp(-{a}/12))',2)
    return c,r,rig

def streak(name,direction=1):
    c,r,rig=root_for(name,'One shot incoming streak + impact',72,500+direction)
    # Ends at anchor; path originates above/outside it. A cinematic mark, no ballistics model.
    for j in range(3):
        m=material(name+f' tapered trail {j}',r,(.58,.29,.09) if j<2 else (.9,.72,.40),f'I*{window(j,10+j,1)}',mode='warm')
        length=1.1-j*.17;thick=.018-j*.005
        vs=[(-length*direction,0,0),(-.65*length*direction,0,thick),(-.2*length*direction,0,thick*.7),(0,0,0),(-.4*length*direction,0,-thick*.6)]
        ob=mesh(c,rig,f'Incoming broken brush trail {j}',vs,[(0,1,2,3,4)],mat=m);ob.location.y=-.06-j*.01;ob.rotation_euler.y=direction*.27
        driver(ob,'location',r,f'{direction}*(-2.8+min(1,max(0,t)/8)*2.8)',0);driver(ob,'location',r,'.76*(1-min(1,max(0,t)/8))+.12',2)
    for j in range(6):
        a='max(0,t-8)';m=material(name+f' attached puff {j}',r,(.28,.26,.22),f'I*.9*{window(8,64,6)}',j+43)
        ob=disc(c,rig,f'Impact pinned at streak endpoint {j}',m,seed=j+200);ob.location.y=.02+j*.015
        driver(ob,'location',r,f'{(j-2.5)*.02}+{(j-2.5)*.003}*{a}',0);driver(ob,'location',r,f'.03+{.10+j%2*.06}*(1-exp(-{a}/10))',2)
        driver(ob,'scale',r,f'.01+.26*(1-exp(-{a}/13))',0);driver(ob,'scale',r,f'.01+.18*(1-exp(-{a}/13))',2)
    return c,r,rig

def smoke_loop(name):
    c,r,rig=root_for(name,'Loop rolling smoke 192f',192,610)
    for j in range(12):
        a=f'((t+{j*16})%192)/192'
        m=material(name+f' drifting ink {j}',r,(.045,.055,.065),f'I*.8*sin(pi*({a}))**2',j+19)
        ob=disc(c,rig,f'Loop smoke curl {j}',m,seed=j+81);ob.location.y=j*.018
        driver(ob,'location',r,f'{(j%3-1)*.24}+W*1.1*({a})+.1*sin(2*pi*({a})+{j})',0)
        driver(ob,'location',r,f'.08+1.95*({a})',2);driver(ob,'scale',r,f'.18+.6*({a})',0);driver(ob,'scale',r,f'.18+.45*({a})',2)
    return c,r,rig

def particles(name):
    c,r,rig=root_for(name,'Loop drifting ash and embers 192f',192,710);rnd=random.Random(710)
    for j in range(48):
        a=f'((t+{j*17})%192)/192';ember=j%4==0
        m=material(name+f' particle {j}',r,(.7,.19,.035) if ember else (.38,.37,.33),f'I*{.9 if ember else .65}*sin(pi*({a}))**2',mode='warm' if ember else 'solid')
        w=rnd.uniform(.004,.012);ob=mesh(c,rig,f'{"Ember" if ember else "Ash"} scraped fleck {j}',[(-w,0,0),(w,0,.008),(w*.4,0,w*2),(-w*.4,0,w)],[(0,1,2,3)],mat=m)
        ob.location.y=rnd.uniform(-.1,.1);x=rnd.uniform(-1.5,1.5);z=rnd.uniform(.1,.6)
        driver(ob,'location',r,f'{x}+W*1.4*({a})+.14*sin(2*pi*({a})+{j})',0)
        driver(ob,'location',r,f'{z}+{2.2 if ember else 1.8}*({a})',2);driver(ob,'rotation_euler',r,f'{j}+2*pi*({a})',1)
    return c,r,rig

def fire(name):
    c,r,rig=root_for(name,'Loop burning debris and warm light 192f',192,810)
    im=bpy.data.images.load(str(R/'sets/fx/v036/Painterly_Flame.png'));im.name='WTSC original flame paint | PACKED';im.alpha_mode='STRAIGHT';im.pack()
    # Root-pinned subdivided texture cards with smoothly periodic shape keys.
    for j in range(3):
        m=material(name+f' painted flame {j}',r,(.72,.51,.32),f'I*(.71+.13*sin(2*pi*t/24+{j})+.08*sin(2*pi*t/8+{j}))',image=im)
        # allow cool/warm control for texture tint as well
        mul=next(n for n in m.node_tree.nodes if n.type=='MIX_RGB');driver(mul.inputs[2],'default_value',r,'.26+.46*C',0);driver(mul.inputs[2],'default_value',r,'.28+.23*C',1);driver(mul.inputs[2],'default_value',r,'.30+.02*C',2)
        nx=10;nz=22;w=.5-j*.1;h=.95-j*.17
        vs=[((u/nx-.5)*w,0,v/nz*h) for v in range(nz+1) for u in range(nx+1)];uv=[(u/nx,v/nz) for v in range(nz+1) for u in range(nx+1)]
        fs=[(v*(nx+1)+u,v*(nx+1)+u+1,(v+1)*(nx+1)+u+1,(v+1)*(nx+1)+u) for v in range(nz) for u in range(nx)]
        ob=mesh(c,rig,f'Flame {j} | root pinned editable paint mesh',vs,fs,uv,m);ob.location=(j*.07-.07,-.06-j*.015,.03)
        ob.shape_key_add(name='Basis')
        for k in range(2):
            key=ob.shape_key_add(name=f'Pinned billow {k}');key.slider_min=-1
            for p in key.data:
                v=p.co.z/h;p.co.x+=.10*v**1.8*math.sin(v*7+k*2+j);p.co.z+=.035*v**2*math.sin(p.co.x*20+k)
            driver(key,'value',r,f'.7*sin(2*pi*t/{24 if k==0 else 32}+{j+k})')
    for j in range(5):
        m=material(name+f' charred ink fragment {j}',r,(.035,.027,.021),'1',mode='solid')
        ob=mesh(c,rig,f'Charred debris {j}',[(-.18,0,0),(.17,0,.02),(.11,0,.10),(-.09,0,.09)],[(0,1,2,3)],mat=m);ob.location=((j-2)*.12,-.13,.01);ob.rotation_euler.y=(j-2)*.3
    for j in range(5):
        a=f'((t+{j*38})%192)/192';m=material(name+f' attached soot {j}',r,(.13,.14,.15),f'I*.58*sin(pi*({a}))**2',j+200)
        ob=disc(c,rig,f'Anchored soot plume {j}',m,seed=j);ob.location.y=.04+j*.015
        driver(ob,'location',r,f'W*.5*({a})+.06*sin(2*pi*({a})+{j})',0);driver(ob,'location',r,f'.48+1.65*({a})',2)
        driver(ob,'scale',r,f'.12+.36*({a})',0);driver(ob,'scale',r,f'.18+.40*({a})',2)
    ld=bpy.data.lights.new(name+' | physical flicker','POINT');ld.color=(1,.28,.055);ld.shadow_soft_size=.4;lo=bpy.data.objects.new(ld.name,ld);c.objects.link(lo);lo.parent=rig;lo.location=(0,-.24,.27)
    driver(ld,'energy',r,'38*I*C*(.8+.14*sin(2*pi*t/24)+.06*sin(2*pi*t/8))')
    m=material(name+' | painted warm pool',r,(.42,.17,.038),'I*C*(.28+.055*sin(2*pi*t/24)+.02*sin(2*pi*t/8))',42)
    ob=disc(c,rig,'Warm paint pool | optional emission-scenery response',m,seed=54);ob.location=(0,.12,.1);ob.scale=(.82,1,.36)
    r['firelight_note']='Point light affects lit materials. Existing world uses emission paint: use the optional warm pool or integrate localized tint manually. No global overlay.'
    return c,r,rig

explosion('FX01_Explosion_Tall_Charcoal',0)
explosion('FX02_Explosion_Low_Rolling_Dust',1)
explosion('FX03_Explosion_Distant_Muted',2)
streak('FX04_Incoming_Left_To_Right',1)
streak('FX05_Incoming_Right_To_Left',-1)
impact('FX06_Impact_Dry_Dust')
smoke_loop('FX07_Smoke_Roll_Loop')
particles('FX08_Ash_Embers_Loop')
fire('FX09_Burning_Debris_Loop')

def configure(s,w=640,h=360):
    s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=24;s.cycles.use_denoising=True
    s.cycles.max_bounces=1;s.cycles.transparent_max_bounces=32;s.render.threads_mode='FIXED';s.render.threads=2
    s.render.resolution_x=w;s.render.resolution_y=h;s.render.resolution_percentage=100;s.render.fps=24
    s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
    s.render.film_transparent=True;s.view_settings.view_transform='Standard';s.view_settings.look='None'
    s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.frame_start=1;s.frame_end=192
    s.world=bpy.data.worlds.new(s.name+' | black world');s.world.color=(0,0,0)

def camera(s,name,location,ortho):
    d=bpy.data.cameras.new(name);d.type='ORTHO';d.ortho_scale=ortho;ob=bpy.data.objects.new(name,d);s.collection.objects.link(ob);ob.location=location;ob.rotation_euler=(math.pi/2,0,0);s.camera=ob
    return ob

s=bpy.context.scene;s.name='FX_LIBRARY | append collections only';configure(s)
camera(s,'FX Library camera',(0,-20,1.35),7)
# Library contains every collection at origin so each can be independently appended.
readme=bpy.data.texts.new('START HERE | WTSC FX v001')
readme.write('Append one FX01..FX09 collection into the WORLD scene, not the flat knockout/title compositor. XZ plane, camera looks+Y, 24fps,1unit/metre. Move its CONTROLS empty to the emitter. Change start_frame,size,speed,intensity,wind,warmth under Custom Properties. No simulation, handler, script execution or unpack needed. Native materials/meshes and packed original flame texture. Single shots:1-144 or1-72; loops:1-192 repeat at193. See IMPORT_GUIDE.txt alongside this blend for instance independence and floor alignment.\n')
for c,_,_ in assets: c.use_fake_user=True
# Opening the master shows one effect, while all nine collections remain appendable.
for c,_,_ in assets[1:]:
    s.collection.children.unlink(c)
    ps=bpy.data.scenes.new('Preview | '+c.name);configure(ps);ps.collection.children.link(c);camera(ps,c.name+' | preview camera',(0,-20,1.5),6)
s.frame_set(32)
s.name='Preview | FX01 Explosion Tall Charcoal';bpy.context.window.scene=s
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Ink_Wash_FX_Library_v001.blend'),compress=True)
# Each standalone native file carries one collection and its actual dependencies.
for c,_,_ in assets:
    bpy.data.libraries.write(str(P/'native'/f'{c.name}_v001.blend'),{c},fake_user=True,compress=True)
manifest={'blender':bpy.app.version_string,'fps':24,'units':'metres, 1unit/metre','orientation':'+X right, +Z up, camera on-Y looking+Y','assets':specs,'simulation_cache_bytes':0,'packed_images':[im.name for im in bpy.data.images if im.packed_file],'source':'Original native procedural wash meshes; existing project GPT imagegen flame packed unchanged.'}
(P/'evidence/asset_manifest.json').write_text(json.dumps(manifest,indent=2))
print('FX_PACK_NATIVE_SAVED',json.dumps(manifest),flush=True)
