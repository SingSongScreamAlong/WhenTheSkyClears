"""One isolated, shot-resolution painterly FX benchmark. No production writes."""
import bpy,math,random,json,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1]
SOURCE=Path(bpy.data.filepath);source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
s=bpy.data.scenes['WTSC_WORLD_CORRECTED_v037'];bpy.context.window.scene=s;s.frame_set(1825)
s.name='FX_BENCHMARK_v002 | real battlefield copy'
START=1813;HERO=1825;FIRST=1795;LAST=1890
random.seed(22017)
fx=bpy.data.collections.new('FXv002 | Detailed painterly ground eruption');s.collection.children.link(fx)
root=bpy.data.objects.new('FXv002 | fixed ground origin and controls',None);fx.objects.link(root);root.empty_display_type='CIRCLE';root.empty_display_size=.25
pair=next(o for o in s.objects if o.type=='GREASEPENCIL');pts=pair.data.layers[0].frames[0].drawing.attributes['position'].data
sole=min((pair.matrix_world@p.vector).z for p in pts);sole_y=min((pair.matrix_world@p.vector).y for p in pts)
slope=(3-sole)/(16+sole_y);root.location=(109.10,10,3-slope*26)
for k,v in {'start_frame':float(START),'speed':1.,'intensity':.94,'wind':.16,'size':1.,'age':0.}.items():root[k]=v
root['status']='Artistic benchmark in a separate scene copy. v001 is a rejected technical prototype.'
root['medium']='Original GPT imagegen paint, root-pinned native mesh flow, unique dust layer, 3D debris and localized receiver color response. No fluid simulation.'
f=root.driver_add('["age"]');f.driver.expression='(frame-a)*v'
for name,key in [('a','start_frame'),('v','speed')]:
 var=f.driver.variables.new();var.name=name;var.type='SINGLE_PROP';var.targets[0].id=root;var.targets[0].data_path='["'+key+'"]'

def drive(owner,path,expr,index=None,extras=None):
 f=owner.driver_add(path) if index is None else owner.driver_add(path,index);f.driver.type='SCRIPTED';f.driver.expression=expr
 for name,key in [('t','age'),('I','intensity'),('W','wind')]:
  var=f.driver.variables.new();var.name=name;var.type='SINGLE_PROP';var.targets[0].id=root;var.targets[0].data_path='["'+key+'"]'
 if extras:
  for name,id,path in extras:
   var=f.driver.variables.new();var.name=name;var.type='SINGLE_PROP';var.targets[0].id=id;var.targets[0].data_path=path
 return f

def gate(start,end,fade=1):return f'max(0,min(1,(t-{start})/{fade},({end}-t)/{fade}))'

# Remove competing old FX in THIS COPY, including the independent old warm tint.
hidden=[]
for o in s.objects:
 if (o.name.startswith('v036 | ') and any(k in o.name for k in ['School debris','Camp hearth','Battlefield burn','Distant ruin burn','ember'])) or (o.name.startswith('v016 | ') and any(k in o.name for k in ['Battlefield smoke','Far battlefield smoke','Distant light bloom'])):
  o.hide_render=True;hidden.append(o.name)
muted_old_light_nodes=[]
for m in bpy.data.materials:
 if not m.node_tree or not m.node_tree.animation_data:continue
 for f in list(m.node_tree.animation_data.drivers):
  if '.19*' in f.driver.expression and 'sin' in f.driver.expression:
   try:
    target=m.node_tree.path_resolve(f.data_path.rsplit('.',1)[0]);target.driver_remove('default_value');target.default_value=0;muted_old_light_nodes.append(m.name)
   except Exception:pass

def grid(name,w,h,mat,nx=48,nz=64,y=0,offset=(0,0)):
 vs=[((u/nx-.5)*w+offset[0],y,v/nz*h+offset[1]) for v in range(nz+1) for u in range(nx+1)]
 faces=[(j*(nx+1)+i,j*(nx+1)+i+1,(j+1)*(nx+1)+i+1,(j+1)*(nx+1)+i) for j in range(nz) for i in range(nx)]
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],faces);me.update();uv=me.uv_layers.new(name='Original paint UV')
 for l in me.loops:i=l.vertex_index;uv.data[l.index].uv=(i%(nx+1)/nx,i//(nx+1)/nz)
 me.materials.append(mat);ob=bpy.data.objects.new(name,me);fx.objects.link(ob);ob.parent=root;return ob

def paint(name,image,opacity,brightness='1',dust=False):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.surface_render_method='BLENDED';nt=m.node_tree;nt.nodes.clear()
 uv=nt.nodes.new('ShaderNodeTexCoord');tex=nt.nodes.new('ShaderNodeTexImage');tex.image=image;tex.extension='CLIP';tex.interpolation='Linear'
 # Very small advected UV deformation; preserves major painted vortex structures.
 no=nt.nodes.new('ShaderNodeTexNoise');no.noise_dimensions='4D';no.inputs['Scale'].default_value=4.5;no.inputs['Detail'].default_value=2.5;drive(no.inputs['W'],'default_value','max(0,t)/42')
 nt.links.new(uv.outputs['UV'],no.inputs[0]);sub=nt.nodes.new('ShaderNodeVectorMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=(.5,.5,.5);nt.links.new(no.outputs['Color'],sub.inputs[0])
 mul=nt.nodes.new('ShaderNodeVectorMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=(.012,.006,0);nt.links.new(sub.outputs[0],mul.inputs[0]);add=nt.nodes.new('ShaderNodeVectorMath');add.operation='ADD';nt.links.new(uv.outputs['UV'],add.inputs[0]);nt.links.new(mul.outputs[0],add.inputs[1]);nt.links.new(add.outputs[0],tex.inputs['Vector'])
 hsv=nt.nodes.new('ShaderNodeHueSaturation');nt.links.new(tex.outputs['Color'],hsv.inputs['Color'])
 if dust:
  # Native desaturation/palette mapping removes saturated generation-edge colors.
  hsv.inputs['Saturation'].default_value=0;hsv.inputs['Value'].default_value=.78
 else:drive(hsv.inputs['Saturation'],'default_value','.18+.47*exp(-max(0,t-18)/55)')
 tone=nt.nodes.new('ShaderNodeMixRGB');tone.blend_type='MULTIPLY';tone.inputs[0].default_value=1;tone.inputs[2].default_value=(.61,.57,.49,1) if dust else (.78,.84,.88,1);nt.links.new(hsv.outputs[0],tone.inputs[1])
 em=nt.nodes.new('ShaderNodeEmission');nt.links.new(tone.outputs[0],em.inputs[0]);drive(em.inputs[1],'default_value',brightness)
 clean=nt.nodes.new('ShaderNodeMapRange');clean.clamp=True;clean.interpolation_type='SMOOTHERSTEP';clean.inputs['From Min'].default_value=.025;clean.inputs['From Max'].default_value=.97;nt.links.new(tex.outputs['Alpha'],clean.inputs[0])
 alpha=nt.nodes.new('ShaderNodeMath');alpha.operation='MULTIPLY';alpha.name='Shot age opacity';nt.links.new(clean.outputs[0],alpha.inputs[0]);drive(alpha.inputs[1],'default_value',opacity)
 tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(alpha.outputs[0],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],out.inputs[0]);return m,nt,tex,em

hero=bpy.data.images.load(str(P/'assets/Hero_Explosion_Paint_v002.png'));hero.name='FXv002 original detailed eruption | packed';hero.alpha_mode='STRAIGHT';hero.pack()
dust=bpy.data.images.load(str(P/'assets/Ground_Dust_Paint_v002.png'));dust.name='FXv002 original granular ground surge | packed';dust.alpha_mode='STRAIGHT';dust.pack()

mat,nt,tex,em=paint('FXv002 | detailed soot internal light and cooling',hero,f'I*{gate(0,145,2)}','.84+.50*exp(-max(0,t)/18)')
plume=grid('FXv002 | unique root-pinned eruption paint',3.1,3.1,mat)
plume.shape_key_add(name='Basis')
impulse=plume.shape_key_add(name='Fast nonuniform impulse | pinned origin')
curl=plume.shape_key_add(name='Upper crown rollover');shear=plume.shape_key_add(name='Asymmetric wake shear');breath=plume.shape_key_add(name='Small billow displacement')
for i,p in enumerate(plume.data.vertices):
 x,z=p.co.x,p.co.z;v=z/3.1;u=(x/3.1+.5)
 impulse.data[i].co.x=x*(.035+.23*v+.06*math.sin(u*11+v*5));impulse.data[i].co.z=z*(.02+.08*v)
 curl.data[i].co.x+=.21*v**2*math.sin(v*5.2+u*3);curl.data[i].co.z+=.14*v**2*math.sin(u*5+v*7)
 shear.data[i].co.x+=.32*v**1.7;shear.data[i].co.z+=.08*math.sin(u*8+v*6)*v**2
 breath.data[i].co.x+=.07*math.sin(u*12+v*15)*v**1.3;breath.data[i].co.z+=.045*math.cos(u*13-v*12)*v**1.6
drive(impulse,'value','exp(-max(0,t)/7)');drive(curl,'value','.8*(1-exp(-max(0,t)/18))*sin(max(0,t)/32)');drive(shear,'value','W*max(0,t)/42');drive(breath,'value','.45*(1-exp(-max(0,t)/16))*sin(t/13)')
plume.location.y=.01

mat,_,_,_=paint('FXv002 | granular low dust with neutral edge palette',dust,f'I*.78*{gate(2,115,9)}','.92',True)
surge=grid('FXv002 | broad low asymmetric dust sheets',4.6,.87,mat,nx=64,nz=18,y=-.09,offset=(0,-.035));surge.shape_key_add(name='Basis');k=surge.shape_key_add(name='Low radial acceleration and drag')
for i,p in enumerate(surge.data.vertices):
 u=p.co.x/4.6+.5;v=max(0,p.co.z/.87);k.data[i].co.x=p.co.x*(.04+.12*v);k.data[i].co.z=p.co.z*(.12+.14*abs(u-.5))
drive(k,'value','exp(-max(0,t-2)/8)')
k=surge.shape_key_add(name='Fine low rolling dust shear')
for i,p in enumerate(surge.data.vertices):k.data[i].co.x+=.09*math.sin(p.co.x*3+p.co.z*8)*max(0,p.co.z/.87);k.data[i].co.z+=.05*math.sin(p.co.x*6)*max(0,p.co.z/.87)
drive(k,'value','.6*sin(t/17)*(1-exp(-max(0,t)/15))')

# A short irregular flash uses the detailed lower painted core, not a disk.
mat,nt,tex,em=paint('FXv002 | fast pale-hot core flash',hero,f'I*1.5*{gate(0,5,1)}','3.6')
flash=grid('FXv002 | brief torn ignition core',1.25,.78,mat,nx=28,nz=24,y=-.12)
for uv in flash.data.uv_layers[0].data:uv.uv.y*=.29

# Individually varied rough solid debris with gravity and rotation; no sprite shower.
coal=bpy.data.materials.new('FXv002 | rough broken charcoal and plaster');coal.use_nodes=True;bs=coal.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.028,.025,.021,1);bs.inputs['Roughness'].default_value=.94
noise=coal.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=18;noise.inputs['Detail'].default_value=3;bump=coal.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.55;bump.inputs['Distance'].default_value=.018;coal.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);coal.node_tree.links.new(bump.outputs[0],bs.inputs['Normal'])
for i in range(38):
 size=random.uniform(.009,.038);vs=[(-1,-.4,-.2),(.9,-.5,-.3),(1,.3,0),(.3,.5,.6),(-.7,.4,.4),(-.9,-.2,.8)];vs=[tuple(c*size*random.uniform(.75,1.3) for c in p) for p in vs]
 me=bpy.data.meshes.new('FXv002 chip');me.from_pydata(vs,[],[(0,1,2),(0,2,4),(2,3,4),(0,4,5),(0,5,1),(1,5,3),(1,3,2),(3,5,4)]);me.materials.append(coal)
 ob=bpy.data.objects.new(f'FXv002 | weighted debris {i:02}',me);fx.objects.link(ob);ob.parent=root
 delay=random.randint(0,3);age=f'max(0,t-{delay})/24';vx=random.uniform(-1.8,1.8);vz=random.uniform(2.5,6.4);dy=random.uniform(-.65,.65)
 drive(ob,'location',f'{vx}*({age})*exp(-.28*({age}))',0);ob.location.y=dy
 drive(ob,'location',f'max({.02-slope*dy},{.05-slope*dy}+{vz}*({age})-4.9*({age})**2)',2)
 for j in range(3):drive(ob,'rotation_euler',f'{random.uniform(-3,3)}+{random.uniform(-11,11)}*min(1.4,({age}))',j)
 # Keep visibility after landing, then gently remove only this benchmark debris.
 drive(ob,'scale',f'{gate(delay,110,1)}',0);drive(ob,'scale',f'{gate(delay,110,1)}',1);drive(ob,'scale',f'{gate(delay,110,1)}',2)

ld=bpy.data.lights.new('FXv002 | hot core physical illumination','POINT');ld.color=(1,.39,.12);ld.shadow_soft_size=.4;lo=bpy.data.objects.new(ld.name,ld);fx.objects.link(lo);lo.parent=root;lo.location=(0,-.14,.38)
drive(ld,'energy',f'I*(85+1100*exp(-max(0,t)/3.5))*{gate(0,130,1)}')

def mathnode(nt,op,a,b):
 n=nt.nodes.new('ShaderNodeMath');n.operation=op
 for j,q in enumerate([a,b]):
  if isinstance(q,(int,float)):n.inputs[j].default_value=q
  else:nt.links.new(q,n.inputs[j])
 return n.outputs[0]

receivers=[]
for name in ['v016 | Battlefield | broken village line','v020 | Walking path | continuous blended paint','v015 | Near-black painted fill | GP vector clipped']:
 ob=s.objects.get(name)
 if not ob or not ob.data.materials:continue
 old=ob.data.materials[0];m=old.copy();m.name='FXv002 receiver | '+name;ob.data.materials[0]=m;nt=m.node_tree;em=next((n for n in nt.nodes if n.type=='EMISSION'),None)
 if not em:continue
 src=em.inputs[0].links[0].from_socket if em.inputs[0].links else None
 if not src:continue
 geo=nt.nodes.new('ShaderNodeNewGeometry');dist=nt.nodes.new('ShaderNodeVectorMath');dist.operation='DISTANCE';nt.links.new(geo.outputs['Position'],dist.inputs[0])
 ground='Walking path' in name;child='painted fill' in name
 if ground:
  # Project a fixed 3D emitter onto the flat painted ground receiver, so its
  # light/contact does not slide with depth parallax as the camera tracks.
  ratio=(ob.location.y+16)/(root.location.y+16)
  dist.inputs[1].default_value=(root.location.x,ob.location.y,3+(root.location.z-3)*ratio)
  drive(dist.inputs[1],'default_value',f'cx+({root.location.x}-cx)*{ratio}',0,extras=[('cx',s.camera,'location[0]')]);radius=1.65*ratio;strength=.11
 else:dist.inputs[1].default_value=tuple(root.location+Vector((0,-.1,.5)));radius=7.5 if not child else 12;strength=.10 if not child else .021
 fall=nt.nodes.new('ShaderNodeMapRange');fall.clamp=True;fall.interpolation_type='SMOOTHERSTEP';fall.inputs['From Min'].default_value=.1;fall.inputs['From Max'].default_value=radius;fall.inputs['To Min'].default_value=1;fall.inputs['To Max'].default_value=0;nt.links.new(dist.outputs['Value'],fall.inputs[0])
 temporal=nt.nodes.new('ShaderNodeValue');temporal.name='FXv002 source-synchronous local light';drive(temporal.outputs[0],'default_value',f'I*({strength})*(.72+2.4*exp(-max(0,t)/3.5))*(.93+.07*sin(t*1.7))*{gate(0,128,1)}')
 weight=mathnode(nt,'MULTIPLY',fall.outputs[0],temporal.outputs[0])
 # Preserve the charcoal linework instead of filling black strokes with orange.
 lum=nt.nodes.new('ShaderNodeRGBToBW');nt.links.new(src,lum.inputs[0]);protect=nt.nodes.new('ShaderNodeMapRange');protect.clamp=True;protect.inputs['From Min'].default_value=.008;protect.inputs['From Max'].default_value=.13;nt.links.new(lum.outputs[0],protect.inputs[0]);weight=mathnode(nt,'MULTIPLY',weight,protect.outputs[0])
 tint=nt.nodes.new('ShaderNodeMixRGB');tint.name='FXv002 | only local warm paint response';tint.blend_type='ADD';tint.inputs[2].default_value=(.9,.32,.065,1);nt.links.new(weight,tint.inputs[0]);nt.links.new(src,tint.inputs[1]);nt.links.new(tint.outputs[0],em.inputs[0]);receivers.append({'object':name,'material':m.name,'radius':radius,'strength':strength,'projected_ground_receiver':ground})

s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=12;s.cycles.use_denoising=True;s.cycles.max_bounces=2;s.cycles.transparent_max_bounces=48;s.render.threads_mode='FIXED';s.render.threads=2
s.render.fps=24;s.frame_start=FIRST;s.frame_end=LAST;s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100;s.render.film_transparent=False
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.view_settings.view_transform='Standard';s.view_settings.look='None';s.frame_set(HERO)
note=bpy.data.texts.new('FXv002 BENCHMARK | read me');note.write('Separate real world scene copy. Source files were not saved or altered. This is an artistic benchmark, not accepted final FX. Original paint textures are packed; root-pinned native mesh flow and unique dust; actual rough solid debris; localized painted receiver light response. Frame range1795-1890 at24fps, ignition1813, hero1825. Native working resolution3840x2160. No simulation cache. CPU two-thread defaults.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_Real_World_FX_Benchmark_v002.blend'),compress=True)
bpy.data.libraries.write(str(P/'native/WTSC_Hero_Eruption_Collection_v002.blend'),{fx},fake_user=True,compress=True)
report={'source':str(SOURCE),'source_sha256':source_hash,'source_unchanged':hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash,'scene':s.name,'emitter':list(root.location),'ignition':START,'hero_frame':HERO,'range':[FIRST,LAST],'fps':24,'intended_pixels':[3840,2160],'asset_pixels':{'hero':list(hero.size),'dust':list(dust.size)},'medium':'Original built-in GPT imagegen paint; native subdivided root-pinned flow and temporal shader cooling; distinct dust; individually weighted3D debris; physical point light plus localized emission-paint receiver response. No fluid simulation.','old_fx_hidden_in_copy':hidden,'old_light_materials_neutralized':muted_old_light_nodes,'receivers':receivers,'artistic_status':'Unaccepted benchmark; inspect shot pixels and actual motion. Import success alone is not an artistic pass.','resource':'One CPU preview process, two threads; no GPU or shared UI.'}
(P/'evidence/benchmark_build.json').write_text(json.dumps(report,indent=2));print('FX_BENCHMARK_BUILT',json.dumps({k:v for k,v in report.items() if k not in ['old_fx_hidden_in_copy']}),flush=True)
# First test is a full-shot1080p frame, not a small isolated icon.
s.render.resolution_percentage=50;s.cycles.samples=8;s.render.filepath=str(P/'previews/WTSC_Explosion_Benchmark_First_Frame_1080_v002.png');bpy.ops.render.render(write_still=True,scene=s.name)
print('FX_BENCHMARK_FIRST_FRAME_SAVED',flush=True)
