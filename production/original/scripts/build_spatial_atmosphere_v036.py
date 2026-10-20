import bpy,math,json,re,random,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(r'WTSC_LOCAL_WORKSPACE');target=R/'shots/world/WTSC_World_Atmosphere_v036.blend';assert not target.exists()
s=bpy.data.scenes['WTSC_WORLD_CENTERED_v035'];bpy.context.window.scene=s;s.frame_set(1);random.seed(360613)
def fcurves(id):
 if not id.animation_data or not id.animation_data.action:return []
 return [f for l in id.animation_data.action.layers for st in l.strips for b in st.channelbags for f in b.fcurves]
def drive(id,path,expr,index=None):
 f=id.driver_add(path) if index is None else id.driver_add(path,index);f.driver.type='SCRIPTED';f.driver.expression=expr;return f
def lerp(points,x):
 for (a,u),(b,v) in zip(points,points[1:]):
  if a<=x<=b:return u+(v-u)*(x-a)/(b-a)
 return points[0][1]+x-points[0][0] if x<points[0][0] else points[-1][1]+x-points[-1][0]
spatial=[(0,0),(19,22.5),(29,43),(42,65),(53,87),(65,115),(77,156),(90,168)]
moves={
 'v016 | Village continues | abandoned':(22.5,12.06),
 'v016 | Woods | near rooted oaks':(43,6),
 'v016 | Woods | far silver canopy':(43,18),
 'v025 | Far woods continuation left':(25,18.015),
 'v025 | Far woods continuation right':(61,18.015),
 'v016 | School | broken windows and plaster':(65,10),
 'v016 | Camp | pinned canvas and ropes':(87,10.06),
 'v016 | Battlefield | broken village line':(115,12),
 'v016 | Ruins | distant ash street':(156,28)}
placement=[]
for name,(x,y) in moves.items():
 o=s.objects[name];old=list(o.location);o.location.x=x;o.location.y=y;placement.append({'object':name,'old':old,'new':list(o.location),'whole_painting_dimensions_preserved':True})
# Physical occlusion supplies the transition; no set opacity curves or switches.
for i,x in enumerate([34,54.5,76.5,99]):
 o=s.objects['v030 | High crown foreground oak '+str(i)];o.location.x=x
for o in s.objects:
 if o.name.startswith('v016 | Rooted grass '):o.location.x=lerp(spatial,o.location.x)
 if o.name.startswith(('v016 | Windborne leaf ','v016 | Paper or ash ','v016 | Slow ground mist ')):
  if o.animation_data:
   for f in o.animation_data.drivers:
    if f.data_path=='location' and f.array_index==0:
     expression=f.driver.expression;match=re.match(r'^([-+]?\d+(?:\.\d+)?)',expression)
     if match:f.driver.expression=f'{lerp(spatial,float(match[1])):.8f}'+expression[match.end():]
 if o.name.startswith('v016 | Distant light bloom '):o.location.x=lerp(spatial,o.location.x)
for name in ['v020 | Walking path | continuous blended paint','v020 | Foreground bank | continuous blended paint']:
 o=s.objects[name]
 for v in o.data.vertices:
  if v.co.x>120:v.co.x=220
 o['coverage_v036']='Continuous geometry extended toX220; world-space paint mapping unchanged, no bitmap stretching.'
smoke_offsets={'Bakery chimney':(0,0),'Far chimney':(3.5,.06),'Camp smoke':(34,.06),'Battlefield smoke':(50,0),'Far battlefield smoke':(79,0)}
for o in s.objects:
 for label,(dx,dy) in smoke_offsets.items():
  if o.name.startswith('v016 | '+label+' | wisp '):o.location.x+=dx;o.location.y+=dy;o['attachment_v036']='Emitter moved with its whole physical set; base remains fixed, only upward billow/scale.'
pair=next(o for o in s.objects if o.type=='GREASEPENCIL')
for fc in list(fcurves(pair)):
 if fc.data_path=='location' and fc.array_index==0:
  for l in pair.animation_data.action.layers:
   for st in l.strips:
    for bag in st.channelbags:
     if fc in list(bag.fcurves):bag.fcurves.remove(fc)
route=[(0,0),(18,25.5),(35,45.4),(50,67.8),(67,89.8),(80,118),(90,142),(100,160.75)]
for t,x in route:pair.location.x=x-1.6891200542449951;pair.keyframe_insert('location',index=0,frame=min(2400,t*24+1))
for fc in fcurves(pair):
 if fc.data_path=='location' and fc.array_index==0:
  for k in fc.keyframe_points:k.interpolation='LINEAR'
fx=bpy.data.collections.new('v036 | Anchored flames smoke embers and responsive light');s.collection.children.link(fx)
def mesh(name,w,h,nx,nz,mat,location):
 d=bpy.data.meshes.new(name);d.from_pydata([((u/nx-.5)*w,0,v/nz*h) for v in range(nz+1) for u in range(nx+1)],[],[(v*(nx+1)+u,v*(nx+1)+u+1,(v+1)*(nx+1)+u+1,(v+1)*(nx+1)+u) for v in range(nz) for u in range(nx)]);d.materials.append(mat);d.update();uv=d.uv_layers.new(name='Whole painted layer')
 for loop in d.loops:i=loop.vertex_index;uv.data[loop.index].uv=(i%(nx+1)/nx,i//(nx+1)/nz)
 o=bpy.data.objects.new(name,d);fx.objects.link(o);o.location=location;return o
def painted(name,path,tint,opacity,strength=1):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.surface_render_method='BLENDED';nt=m.node_tree;nt.nodes.clear();t=nt.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(path),check_existing=True);t.image.pack();t.extension='CLIP'
 mult=nt.nodes.new('ShaderNodeMix');mult.data_type='RGBA';mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1;mult.inputs[7].default_value=(*tint,1);nt.links.new(t.outputs['Color'],mult.inputs[6])
 em=nt.nodes.new('ShaderNodeEmission');em.inputs[1].default_value=strength;nt.links.new(mult.outputs[2],em.inputs[0]);r=nt.nodes.new('ShaderNodeMapRange');r.clamp=True;r.inputs['From Min'].default_value=.055;r.inputs['From Max'].default_value=.90;nt.links.new(t.outputs['Alpha'],r.inputs[0]);a=nt.nodes.new('ShaderNodeMath');a.operation='MULTIPLY';a.inputs[1].default_value=opacity;nt.links.new(r.outputs[0],a.inputs[0]);tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(a.outputs[0],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],out.inputs[0]);return m,em,a
def flicker(phase):return f'(.82+.12*sin(frame*.77+{phase})+.065*sin(frame*1.93+{phase+1})+.045*sin(frame*.313+{phase+2}))'
def pinned(o,h,amp,phase,slow=False):
 o.shape_key_add(name='Basis')
 for i,name in enumerate(['Root pinned | billow','Root pinned | tip curl']):
  k=o.shape_key_add(name=name);k.slider_min=-1
  for p in k.data:
   v=max(0,min(1,p.co.z/h));p.co.x+=amp*v**1.6*(.7+.3*math.sin(v*9+i*2+p.co.x*8));p.co.z+=amp*.25*v**2*math.sin(p.co.x*5+i)
  drive(k,'value',f'.66*sin(frame/{39 if slow else 5.1}+{phase+i*2})+.34*sin(frame/{17 if slow else 2.7}+{phase+1})')
 o['motion']='Native subdivided whole paint; base pins at emitter, local upper mesh deformation only.'
fires=[('School debris',61.5,9.92,.35,.65,.95,620),('Camp hearth',85,9.92,.35,.90,1.55,1050),('Battlefield burn',112,11.85,.30,1.30,2.25,1650),('Distant ruin burn',151,24,.10,1.6,3.0,1800)]
coal=bpy.data.materials.new('v036 | Charred rough logs and stones');coal.use_nodes=True;bs=coal.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.025,.018,.012,1);bs.inputs['Roughness'].default_value=.94
noise=coal.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=17;noise.inputs['Detail'].default_value=4;bump=coal.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.45;bump.inputs['Distance'].default_value=.035;coal.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);coal.node_tree.links.new(bump.outputs[0],bs.inputs['Normal'])
anchors=[]
for i,(label,x,y,z,w,h,energy) in enumerate(fires):
 phase=i*2.13;root=bpy.data.objects.new('v036 | '+label+' | fixed emitter',None);fx.objects.link(root);root.location=(x,y,z)
 for j in range(2):
  m,em,a=painted('v036 | '+label+' | flame paint '+str(j),R/'sets/fx/v036/Painterly_Flame.png',(1,.83 if j else 1,.63 if j else 1),.80 if j else .96,2.1)
  ob=mesh('v036 | '+label+' | painted flame '+str(j),w*(1 if j==0 else .56),h*(1 if j==0 else .77),20,40,m,(0,-j*.025,0));ob.parent=root;pinned(ob,h*(1 if j==0 else .77),w*.21,phase+j)
  drive(ob,'scale',f'1+.065*sin(frame*.48+{phase+j})+.035*sin(frame*.91)',2);drive(em.inputs[1],'default_value',f'2.15*{flicker(phase+j)}')
 for j in range(4):
  mat,em,a=painted('v036 | '+label+' | soot billow '+str(j),R/'sets/fx/Painted_Smoke_Wisp_v016.png',(.42,.44,.46) if i>1 else (.66,.64,.60),.24 if i>1 else .17)
  sh=h*3.7;ob=mesh('v036 | '+label+' | rooted smoke '+str(j),w*2.6,sh,12,26,mat,(0,.055+j*.02,h*.55));ob.parent=root;pinned(ob,sh,w*.58,phase+j*1.8,True)
  age=f'((frame+{j*71+i*23})%340)/340';drive(ob,'scale',f'.75+.32*({age})',0);drive(ob,'scale',f'.83+.30*({age})',2);drive(a.inputs[1],'default_value',f'{.24 if i>1 else .17}*(.18+.82*sin(pi*({age}))**2)')
 ld=bpy.data.lights.new('v036 | '+label+' | physical firelight','POINT');ld.color=(1,.30,.055);ld.shadow_soft_size=w*.65;ld.energy=energy;lo=bpy.data.objects.new(ld.name,ld);fx.objects.link(lo);lo.parent=root;lo.location=(0,-.32,h*.36);drive(ld,'energy',f'{energy}*{flicker(phase)}')
 for j in range(5):
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=w*.12,location=(x+math.cos(j*2.2)*w*.4,y+math.sin(j*2.2)*w*.16,z+.025));ob=bpy.context.object;ob.name='v036 | '+label+' | charred hearth stone '+str(j);ob.scale=(1.3,.7,.5);ob.data.materials.append(coal)
  for c in list(ob.users_collection):c.objects.unlink(ob)
  fx.objects.link(ob)
 for j in range(10):
  mat=bpy.data.materials.new(f'v036 | ember {i}-{j}');mat.use_nodes=True;mat.node_tree.nodes.clear();em=mat.node_tree.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(1,.11,.009,1);em.inputs[1].default_value=3;out=mat.node_tree.nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(em.outputs[0],out.inputs[0]);ob=mesh(f'v036 | {label} | ember {j}',.009+w*.005,.02+h*.006,1,1,mat,(0,0,0));ob.parent=root
  age=f'((frame+{j*17+i*31})%137)/137';drive(ob,'location',f'{w*.22}*sin(frame/19+{j})+{w*.25}*({age})**2',0);drive(ob,'location',f'{h}*({age})*1.4',2);ob.location.y=-.12;drive(em.inputs[1],'default_value',f'3.2*sin(pi*({age}))**2')
 anchors.append({'name':label,'fixed_root':[x,y,z],'flame_height':h,'physical_point_light_energy':energy,'phase':phase,'flame_parts':2,'smoke_parts':4,'embers':10})
# Paint receives the same spatially anchored warm response as the physical light;
# this changes color only, never architecture alpha. No global red overlay.
responsive=[]
for name in ['v016 | School | broken windows and plaster','v016 | Camp | pinned canvas and ropes','v016 | Battlefield | broken village line','v016 | Ruins | distant ash street','v020 | Walking path | continuous blended paint','v020 | Foreground bank | continuous blended paint']:
 ob=s.objects[name];nt=ob.data.materials[0].node_tree;em=next(n for n in nt.nodes if n.type=='EMISSION');src=em.inputs[0].links[0].from_socket;geo=nt.nodes.new('ShaderNodeNewGeometry')
 for i,(_,x,y,z,w,h,energy) in enumerate(fires):
  if abs(ob.location.x-x)>45 and 'continuous' not in name:continue
  d=nt.nodes.new('ShaderNodeVectorMath');d.operation='DISTANCE';d.inputs[1].default_value=(x,y,z+h*.3);nt.links.new(geo.outputs['Position'],d.inputs[0]);r=nt.nodes.new('ShaderNodeMapRange');r.clamp=True;r.inputs['From Min'].default_value=.3;r.inputs['From Max'].default_value=7;r.inputs['To Min'].default_value=1;r.inputs['To Max'].default_value=0;nt.links.new(d.outputs['Value'],r.inputs[0]);fac=nt.nodes.new('ShaderNodeMath');fac.operation='MULTIPLY';nt.links.new(r.outputs[0],fac.inputs[0]);drive(fac.inputs[1],'default_value',f'.19*{flicker(i*2.13)}');mix=nt.nodes.new('ShaderNodeMix');mix.data_type='RGBA';mix.blend_type='ADD';mix.inputs[7].default_value=(.8,.20,.025,1);nt.links.new(fac.outputs[0],mix.inputs[0]);nt.links.new(src,mix.inputs[6]);src=mix.outputs[2]
 nt.links.new(src,em.inputs[0]);responsive.append(name)
s.name='WTSC_WORLD_CORRECTED_v036';s.frame_start=1;s.frame_end=2400;s['duration_status']='Confirmed100s moving world; final mask/master will add6s exact credit card,106total.';s['spatial_v036']='Whole sets spaced physically, slight depth separation at overlaps; no set fades. Continuous ground extendsX220. Frame route adjusted to preserve village/woods/school/camp/battlefield progression.'
report={'source':str(target),'scene':s.name,'set_placements':placement,'camera_route_seconds_x':route,'ground_extent_x':[-24,220],'new_fire_anchors':anchors,'new_smoke_layers':16,'responsive_painted_objects':responsive,'fire_asset':'sets/fx/v036/Painterly_Flame.png','fire_asset_pixels':[1024,1536],'fire_asset_provenance':'Builtin GPTimagegen; originalalpha preserved; mapped to root-pinned native meshes','children':'Same held near-age GP drawing and parented painted fill; only whole-pair routetranslation changed','correction_scope':'Necessary physical layout/overlap and attachedFX corrections. No environment opacity dissolves, no character gait.','final_timing':'100 moving world +6silentcredits =106s; mask/master created next.'}
note=bpy.data.texts.new('CURRENT v036 | Spatial world and anchored fire');note.write(json.dumps(report,indent=2));s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True)
(R/'notes/world_v016/atmosphere_build_v036.json').write_text(json.dumps(report,indent=2));print('ATMOSPHERE_WORLD_SAVED',str(target),flush=True)
s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.resolution_percentage=50
for f in [193,481,841,1201,1609,1801,2161,2377]:
 s.frame_set(f);s.render.filepath=str(R/f'renders/world_v016/atmosphere_checks_v036/{f}.png');bpy.ops.render.render(write_still=True,scene=s.name)
