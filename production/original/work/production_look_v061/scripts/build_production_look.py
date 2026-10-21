"""Native physical ink/wash forest candidate; preserves drawn cast."""
import bpy,math,json,random,runpy,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(r'WTSC_LOCAL_WORKSPACE\work\production_look_v061');R=O.parents[1];random.seed(61018)
bpy.ops.wm.open_mainfile(filepath=str(O/'reference/PRESERVED_v060.blend'),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v060'];s.name='WTSC_INK_WASH_DEPTH_v061';bpy.context.window.scene=s;s.frame_set(981)
C=bpy.data.collections.new('V061 | physical ink wash forest');s.collection.children.link(C)
report={'basis':'Preserved v060 current age-ten pair, owned production look branch','range':[937,1056],'preserved_input_sha256':hashlib.sha256((O/'reference/PRESERVED_v060.blend').read_bytes()).hexdigest()}
def mesh(name,vs,fs,mat=None,uvs=None):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new(name,me);C.objects.link(ob)
 if mat:me.materials.append(mat)
 if uvs:
  uv=me.uv_layers.new(name='V061 surface pigment registration')
  for p in me.polygons:
   for li in p.loop_indices:uv.data[li].uv=uvs[me.loops[li].vertex_index]
 return ob
def paint(name,palette,image=None,bark=False):
 m=bpy.data.materials.new('V061 | '+name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();N=nt.nodes;L=nt.links
 out=N.new('ShaderNodeOutputMaterial');bs=N.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=.92;bs.inputs['Specular IOR Level'].default_value=.14;L.new(bs.outputs[0],out.inputs['Surface'])
 tc=N.new('ShaderNodeTexCoord');noise=N.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=2.3 if bark else 1.4;noise.inputs['Detail'].default_value=2.2;noise.inputs['Roughness'].default_value=.62;L.new(tc.outputs['Object'],noise.inputs['Vector'])
 ramp=N.new('ShaderNodeValToRGB');ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
 for i,(pos,col) in enumerate(palette):
  e=ramp.color_ramp.elements[0] if i==0 else ramp.color_ramp.elements.new(pos);e.position=pos;e.color=(*col,1)
 ramp.color_ramp.interpolation='EASE';L.new(noise.outputs['Fac'],ramp.inputs[0]);col=ramp.outputs[0]
 if image:
  tex=N.new('ShaderNodeTexImage');tex.image=image;tex.interpolation='Linear';L.new(tc.outputs['UV'],tex.inputs[0]);mix=N.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.72;L.new(tex.outputs['Color'],mix.inputs[1]);L.new(col,mix.inputs[2]);col=mix.outputs[0]
 if name.startswith('bank'):
  shade=N.new('ShaderNodeMixRGB');shade.blend_type='MULTIPLY';shade.inputs[0].default_value=1;shade.inputs[2].default_value=(.48,.57,.54,1);L.new(col,shade.inputs[1]);col=shade.outputs[0]
 L.new(col,bs.inputs['Base Color'])
 fine=N.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=72 if bark else 48;fine.inputs['Detail'].default_value=1.5;L.new(tc.outputs['Object'],fine.inputs[0])
 bump=N.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.09;bump.inputs['Distance'].default_value=.004 if bark else .003;L.new(fine.outputs['Fac'],bump.inputs['Height']);L.new(bump.outputs[0],bs.inputs['Normal'])
 return m
earthasset=O/'reference/Ink_Wash_Earth_v061.png'
groundimg=bpy.data.images.load(str(earthasset if earthasset.exists() else R/'sets/painted_layers/Ground_Painted_v001.png'),check_existing=True)
barkasset=O/'reference/Ink_Wash_Bark_v061.png'
oakimg=bpy.data.images.load(str(barkasset if barkasset.exists() else R/'sets/world_v030/High_Crown_Oak.png'),check_existing=True)
earth=paint('ochre earth wash',[(.23,(.35,.29,.20)),(.48,(.61,.52,.37)),(.76,(.80,.71,.52))],groundimg)
bankmat=paint('bank umber pooled pigment',[(.18,(.12,.14,.105)),(.49,(.31,.29,.21)),(.80,(.55,.49,.33))],groundimg)
bark=paint('bark original pigment on solid volume',[(.16,(.19,.21,.14)),(.48,(.51,.47,.32)),(.78,(.82,.74,.48))],oakimg,True)
leaves=[]
for k,p in enumerate([[(.2,(.035,.056,.037)),(.5,(.095,.125,.061)),(.8,(.22,.25,.12))],[(.2,(.08,.10,.045)),(.5,(.21,.25,.10)),(.8,(.40,.42,.20))],[(.2,(.11,.13,.065)),(.5,(.30,.32,.14)),(.8,(.52,.49,.25))]]):leaves.append(paint('canopy wash '+str(k),p))
ink=paint('selective olive black ink',[(.1,(.018,.027,.018)),(.9,(.035,.044,.025))])
# Physically horizontal walking corridor. Front bank slopes below it.
floor=.7713720202445984
root=bpy.data.objects['V047 | shared travel | steady .73125mps'];root.matrix_parent_inverse=Matrix.Identity(4)
stage=root.parent;stage['purpose']='V061 physical world registration; no projected floor shear.'
hidden=[]
for ob in list(s.objects):
 if ob.name in ['v020 | Walking path | continuous blended paint','v020 | Foreground bank | continuous blended paint','v016 | Woods | near rooted oaks','v030 | High crown foreground oak 1'] or 'fixed foreground soil bank' in ob.name or ob.name.startswith('V060 contact '):
  ob.hide_render=True;hidden.append(ob.name)
disabled=bpy.data.collections.new('V061 | replaced flat scenery | render disabled');s.collection.children.link(disabled);disabled.hide_render=True
for name in hidden:
 ob=bpy.data.objects[name]
 for col in list(ob.users_collection):col.objects.unlink(ob)
 disabled.objects.link(ob)
report['replaced_flat_objects']=hidden
vs=[];uv=[];fs=[];nx=113;ny=45
for j in range(ny):
 y=-8+j*20/(ny-1)
 for i in range(nx):
  x=35+i*40/(nx-1)
  z=floor
  if y < -1.05:z-=.20*(-1.05-y)+.025*math.sin(x*.91+y)
  elif y>2.2:z+=.040*(y-2.2)+.07*math.sin(x*.39+y*.7)
  if y<-.9 or y>2:z+=.015*math.sin(x*3.7+y*2.1)*math.sin(y*3)
  vs.append((x,y,z));uv.append(((x-35)/5,(y+8)/4.6))
for j in range(ny-1):
 for i in range(nx-1):
  a=j*nx+i;fs.append((a,a+1,a+1+nx,a+nx))
ground=mesh('V061 | physical path and bank | actual shadow receiver',vs,fs,earth,uv);ground.data.materials.append(bankmat)
for p in ground.data.polygons:
 if not -1.05<=sum(ground.data.vertices[v].co.y for v in p.vertices)/len(p.vertices)<=1.8:p.material_index=1
 p.use_smooth=True
# Fixed world brush/ink curves. Never screen-space outlines.
def stroke(name,points,radius=.003,material=ink):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=2;cu.bevel_depth=radius;cu.bevel_resolution=2
 sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for i,(p,v) in enumerate(zip(sp.points,points)):
  p.co=(*v,1);p.radius=.35+.65*math.sin(math.pi*(i+.3)/(len(points)-.4))**.7
 ob=bpy.data.objects.new(name,cu);C.objects.link(ob);cu.materials.append(material);return ob
def tube(name,points,rads,material=bark,N=28):
 vs=[];uv=[];fs=[]
 for j,(p,r) in enumerate(zip(points,rads)):
  p=Vector(p);t=(Vector(points[min(j+1,len(points)-1)])-Vector(points[max(j-1,0)])).normalized();a=t.cross(Vector((0,1,0)))
  if a.length<.001:a=t.cross(Vector((1,0,0)))
  a.normalize();b=t.cross(a).normalized()
  for k in range(N):
   th=2*math.pi*k/N;rr=r*(1+.055*math.sin(k*2.7+j*.31)+.030*math.sin(k*5.1-j*.73))
   v=p+(a*math.cos(th)+b*math.sin(th))*rr;vs.append(tuple(v));uv.append((k/(N-1),j/(len(points)-1)*2.3) if barkasset.exists() else (.442+.103*k/(N-1),.13+.37*j/(len(points)-1)))
 for j in range(len(points)-1):
  for k in range(N):a=j*N+k;b=j*N+(k+1)%N;fs.append((a,b,b+N,a+N))
 fs.append(tuple(reversed(range(N))));fs.append(tuple((len(points)-1)*N+k for k in range(N)))
 ob=mesh(name,vs,fs,material,uv)
 if barkasset.exists():
  layer=ob.data.uv_layers.active
  for j in range(len(points)-1):
   for k in range(N):
    p=ob.data.polygons[j*N+k]
    for li,co in zip(p.loop_indices,[(k/N,j/(len(points)-1)*2.3),((k+1)/N,j/(len(points)-1)*2.3),((k+1)/N,(j+1)/(len(points)-1)*2.3),(k/N,(j+1)/(len(points)-1)*2.3)]):layer.data[li].uv=co
 for p in ob.data.polygons:p.use_smooth=True
 return ob
def tree(idx,x,y,r,h):
 z=floor+(.04*(y-2.2) if y>2.2 else -.2*max(0,-1.05-y))
 pts=[];rs=[]
 for j in range(19):
  t=j/18;pts.append((x+.17*math.sin(t*2.8+idx)*t,y+.09*math.sin(t*3+idx),z+h*t));rs.append(r*(1-.52*t)*(1+.28*math.exp(-t*17)))
 tube('V061 | oak %02d | asymmetric solid trunk'%idx,pts,rs)
 for a in range(5):
  th=a*math.tau/5+.31*idx;end=(x+math.cos(th)*r*2.7,y+math.sin(th)*r*2.7,z-.035)
  tube('V061 | oak %02d buttress %d'%(idx,a),[pts[1],(x+math.cos(th)*r*.9,y+math.sin(th)*r*.9,z+.14),end],[r*.40,r*.29,.015],N=16)
  if a%2==0:
   q=[(pts[1][0]+.02,pts[1][1]-.02,pts[1][2]),(x+math.cos(th)*r*.8,y+math.sin(th)*r*.8-.015,z+.21),(end[0],end[1]-.012,end[2]+.025)]
   stroke('V061 | root ink %02d %d'%(idx,a),q,.005)
 for a in range(4):
  j=5+a*2;p=pts[j];th=a*2.1+idx*.7;L=h*(.25+.035*a);end=(p[0]+math.cos(th)*L,p[1]+math.sin(th)*L,p[2]+L*.8)
  mid=tuple(p[k]*.47+end[k]*.53 for k in range(3));tube('V061 | oak %02d bough %d'%(idx,a),[p,mid,end],[rs[j]*.63,rs[j]*.30,.025],N=16)
 # Broken ink clefts in the camera facing half; varied pressure, not full outline.
 for k in range(12):
  th=math.pi*random.uniform(1.05,1.95);start=random.uniform(.05,.72);length=random.uniform(.07,.21);q=[]
  for l in range(8):
   t=start+length*l/7;j=min(17,int(t*18));rr=rs[j]*1.025;pp=pts[j]
   q.append((pp[0]+rr*math.cos(th+.02*math.sin(l)),pp[1]+rr*math.sin(th+.02*math.sin(l)),z+h*t))
  stroke('V061 | broken bark ink %02d %d'%(idx,k),q,.0035 if y<0 else .002)
 # Selected branch scar / irregular ink pool, authored on the solid bark.
 if idx in (1,3,5):
  zz=z+h*.20;xx=x+.04;yy=y-r*1.03
  tube('V061 | oak %02d branch scar volume'%idx,[(xx,yy+.045,zz),(xx+.025,yy-.045,zz+.025),(xx+.04,yy-.065,zz+.04)],[.066,.046,.020],N=18)
  stroke('V061 | oak %02d broken knot ink'%idx,[(xx+.075*math.cos(t*.30),yy-.007-.008*math.sin(t*.30),zz+.12*math.sin(t*.30)) for t in range(18)],.004)
 # Native leaf facets in clustered masses around elevated crown / branch tips.
 lvs=[];lfs=[];mids=[]
 for a in range(950 if y<0 else 470):
  th=random.uniform(0,math.tau);rr=random.random()**.5*h*.37
  cx=x+rr*math.cos(th);cy=y+rr*math.sin(th);cz=z+h*(.70+.34*random.random())-.12*rr
  sz=random.uniform(.045,.11)*(1.3 if y<0 else 1)
  direction=random.uniform(0,math.tau);u=Vector((math.cos(direction)*sz,math.sin(direction)*sz,random.uniform(-.2,.3)*sz));v=Vector((-math.sin(direction)*sz*.42,math.cos(direction)*sz*.42,sz*.35));c=Vector((cx,cy,cz));a0=len(lvs)
  lvs.extend([tuple(c-u),tuple(c+v),tuple(c+u),tuple(c-v)]);lfs.append((a0,a0+1,a0+2,a0+3));mids.append(random.randrange(3))
 lo=mesh('V061 | oak %02d | dimensional canopy brush leaves'%idx,lvs,lfs)
 for m in leaves:lo.data.materials.append(m)
 for p,mi in zip(lo.data.polygons,mids):p.material_index=mi
for args in [(0,47.0,4.0,.39,6.2),(1,48.6,7.3,.48,7.0),(2,54.1,5.4,.40,6.5),(3,57.7,8.8,.52,7.9),(4,45.4,10.5,.34,7.1),(5,55.0,-2.6,.27,7.2),(6,43.1,3.8,.37,6.6),(7,60.8,4.2,.49,7.8)]:tree(*args)
# Sparse native understory and pebbles grouped in depth, leaving hands/head gap quiet.
for q in range(38):
 x=random.uniform(42,63);y=random.choice([random.uniform(2.8,5.2),random.uniform(-3.7,-1.5)]);z=floor+.04*max(0,y-2.2)-.2*max(0,-1.05-y)
 for a in range(random.randint(3,6)):
  h=random.uniform(.12,.39);dx=random.uniform(-.14,.14);dy=random.uniform(-.12,.12)
  stroke('V061 | rooted understory stem %d %d'%(q,a),[(x,y,z),(x+dx*.4,y+dy*.4,z+h*.65),(x+dx,y+dy,z+h)],.003,leaves[a%3])
# Ink at chosen bank cracks, broken segments.
for j in range(21):
 x=43+j*.72;y=-1.12-.05*math.sin(x);stroke('V061 | selected bank lip ink %02d'%j,[(x+t*.15,y-.02*math.sin(t),floor-.009-.01*math.sin(t)) for t in range(4)],.0025)
# Keep only far matte canopy; all new near geometry reacts to real lights.
w=bpy.data.worlds.new('V061 | cool forest ambient');w.use_nodes=True;w.node_tree.nodes.get('Background').inputs[0].default_value=(.39,.46,.52,1);w.node_tree.nodes.get('Background').inputs[1].default_value=.34;s.world=w
for ob in list(s.objects):
 if ob.type=='LIGHT':ob.hide_render=True
def light(name,typ,loc,energy,color,target=None,size=1):
 data=bpy.data.lights.new(name,typ);data.energy=energy;data.color=color
 if typ=='AREA':data.shape='DISK';data.size=size
 ob=bpy.data.objects.new(name,data);C.objects.link(ob);ob.location=loc
 if target:ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
 return ob
sun=light('V061 | broken canopy late afternoon key','SUN',(57,-7,10),2.2,(1,.89,.69),(49,3,0));sun.data.angle=math.radians(5)
fill=light('V061 | broad cool sky fill','AREA',(51,-7,6),850,(.65,.77,1),(52,0,1.5),8)
rim=light('V061 | leaf gap warm bounce','AREA',(54,3,5),550,(1,.87,.66),(52,0,1.4),3)
event=bpy.data.objects['V060 | one offscreen distant flash | painted response']
flash=light('V061 | offscreen distant flash real receivers','AREA',(57,5,5),0,(1,.79,.52),(52,0,.9),5)
fc=flash.data.driver_add('energy');fc.driver.expression='pulse*3600';v=fc.driver.variables.new();v.name='pulse';v.type='SINGLE_PROP';v.targets[0].id=event;v.targets[0].data_path='["pulse"]'
# Volume is behind the cast; the foreground/face path stays clear.
bpy.ops.mesh.primitive_cube_add(size=1,location=(52,8,4.6));vol=bpy.context.object;vol.name='V061 | bounded canopy atmosphere | behind cast'
for col in list(vol.users_collection):col.objects.unlink(vol)
C.objects.link(vol);vol.dimensions=(32,16,9)
vm=bpy.data.materials.new('V061 | restrained physical atmosphere');vm.use_nodes=True;nt=vm.node_tree;nt.nodes.clear();p=nt.nodes.new('ShaderNodeVolumePrincipled');p.inputs['Density'].default_value=.009;p.inputs['Color'].default_value=(.73,.78,.70,1);p.inputs['Anisotropy'].default_value=.28;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(p.outputs['Volume'],out.inputs['Volume']);vol.data.materials.append(vm)
# Contact marks and light response are authored helpers, applied only to owned copies.
actors=[o for o in s.objects if o.type=='MESH' and not o.hide_render and (o.name.startswith('V044 ') or o.name.startswith('V046 ') or o.name.startswith('V060 ') and 'contact' not in o.name)]
boots=[o for o in actors if o.get('proportion_role')=='boot']
report['flat_floor_z']=floor;report['physical_objects']=len(C.objects);report['ground_topology']=[len(ground.data.vertices),len(ground.data.polygons)];report['tree_positions']=[list(a) for a in [(47,4),(50.1,7.3),(53.1,5.4),(57.7,8.8),(55,-2.6)]]
hp=O/'scripts/ink_wash_materials.py'
if hp.exists():report['paint_response']=runpy.run_path(str(hp))['apply'](s,actors,event)
hp=O/'scripts/physical_contact_v061.py'
if hp.exists():report['contacts']=runpy.run_path(str(hp))['apply'](s,boots,[937+i/4 for i in range(477)],floor)
# Lower the camera to children's shoulder height; preserve their exact screen placement.
cam=s.camera;dz=1.30;cam.data.shift_y+=dz*cam.data.lens/(cam.data.sensor_width*15.64)
for layer in cam.animation_data.action.layers:
 for strip in layer.strips:
  for bag in strip.channelbags:
   for fc in bag.fcurves:
    if fc.data_path=='location' and fc.array_index==2:
     for k in fc.keyframe_points:
      k.co.y-=dz;k.handle_left.y-=dz;k.handle_right.y-=dz
     fc.update()
hp=O/'scripts/environment_finish_v061.py'
if hp.exists():report['environment_finish']=runpy.run_path(str(hp))['apply_environment_finish'](s,C)
s.camera.data.dof.aperture_fstop=5.6
s['V061_scope']='Physical-depth and native ink/wash production-look candidate, not finished full trailer.'
s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=4
if hasattr(s,'eevee'):s.eevee.taa_render_samples=64
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
s.frame_set(981);bpy.context.window.scene=s
note=bpy.data.texts.new('START HERE | V061 | full production direction');note.write((O/'START_HERE_v061.txt').read_text())
report['painted_albedo']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [barkasset,earthasset] if p.exists()}
report['camera_plan']={'z_m':s.camera.location.z,'shift_y':s.camera.data.shift_y,'lens_mm':s.camera.data.lens,'aperture':s.camera.data.dof.aperture_fstop}
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(O/'native/WTSC_Physical_Ink_Wash_Forest_v061.blend'),compress=True)
(O/'evidence/PRODUCTION_LOOK_BUILD.json').write_text(json.dumps(report,indent=2,default=str))
for g in [937,981,1056]:
 s.frame_set(g);s.render.resolution_x=1280;s.render.resolution_y=720;s.render.filepath=str(O/('previews/physical_v061_%04d.png'%g));bpy.ops.render.render(write_still=True,scene=s.name)
print('V061_PHYSICAL_LOOK_KEYS_READY',flush=True)
