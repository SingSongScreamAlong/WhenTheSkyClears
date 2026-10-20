"""Isolated native world-art branch. Original title/edit/character actions retained."""
import bpy,math,random,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(r'WTSC_LOCAL_WORKSPACE')
O=Path(r'WTSC_LOCAL_USER\Documents\Codex\2026-10-16\task\world_art_v048')
SRC=R/'shots/world/WTSC_Painted_World_Full_Trailer_Editable_v040.blend'
OUT=O/'WTSC_World_Art_Branch_v048.blend'
assert not OUT.exists(),'Choose a new checkpoint; do not overwrite.'
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False)
S=bpy.data.scenes['WTSC_WORLD_CORRECTED_v040'];bpy.context.window.scene=S
random.seed(48018);changed=[];created=[]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def actions():
 out={}
 for a in bpy.data.actions:
  rows=[]
  for l in a.layers:
   for st in l.strips:
    for bag in st.channelbags:
     for f in bag.fcurves:rows.append((f.data_path,f.array_index,[(tuple(k.co),k.interpolation) for k in f.keyframe_points]))
  out[a.name]=hashlib.sha256(repr(rows).encode()).hexdigest()
 return out
original_actions=actions()
original_timing={s.name:[s.frame_start,s.frame_end,s.render.fps,s.render.resolution_x,s.render.resolution_y] for s in bpy.data.scenes}
original_camera={}
for f in [1,241,841,1201,1609,1849,1921,2161,2400]:
 S.frame_set(f);bpy.context.view_layer.update();original_camera[str(f)]=[list(v) for v in S.camera.matrix_world]

C=bpy.data.collections.new('v048 | WORLD ART | fixed architecture and authored terrain');S.collection.children.link(C)
def material(name,c,variation=.08):
 m=bpy.data.materials.new('v048 | '+name);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');out=nt.nodes.new('ShaderNodeOutputMaterial')
 if variation:
  geo=nt.nodes.new('ShaderNodeTexCoord');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=7;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.65;nt.links.new(geo.outputs['Object'],noise.inputs['Vector']);r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=tuple(v*(1-variation) for v in c)+(1,);r.color_ramp.elements[1].color=tuple(v*(1+variation) for v in c)+(1,);nt.links.new(noise.outputs['Fac'],r.inputs[0]);nt.links.new(r.outputs[0],em.inputs[0])
 else:em.inputs[0].default_value=(*c,1)
 nt.links.new(em.outputs[0],out.inputs[0]);return m
M={
 'ink':material('dry charcoal contour',(.014,.019,.020),.12),
 'soil':material('earth umber',(.025,.028,.024),.30),
 'soil_light':material('broken ochre earth edge',(.070,.063,.044),.20),
 'soil_war':material('ash earth',(.026,.033,.035),.20),
 'root':material('exposed root fiber',(.072,.064,.047),.12),
 'stone':material('cool plaster face',(.102,.120,.125),.15),
 'stone_dark':material('slate fracture shadow',(.039,.053,.058),.18),
 'stone_light':material('chalk broken edge',(.180,.198,.190),.10),
 'warm':material('sunlit limestone',(.25,.186,.108),.13),
 'warm_dark':material('limestone crevice',(.065,.055,.035),.17),
 'wood':material('weathered beam face',(.039,.042,.036),.18),
 'wood_light':material('splinter highlight',(.105,.108,.082),.17),
 'glass':material('muted blue window shard',(.105,.143,.155),.08),
 'room':material('room darkness',(.012,.022,.027),.12),
}

def proj(f,u,v,y):
 S.frame_set(f);bpy.context.view_layer.update();cam=S.camera;d=y-cam.matrix_world.translation.y;w=d*cam.data.sensor_width/cam.data.lens;h=w*S.render.resolution_y/S.render.resolution_x
 return (cam.matrix_world.translation.x+(u-.5+cam.data.shift_x)*w,y,cam.matrix_world.translation.z+(v-.5)*h+cam.data.shift_y*w)
def poly(name,pts,mat):
 me=bpy.data.meshes.new('v048 '+name);me.from_pydata(pts,[],[tuple(range(len(pts)))]);me.update();o=bpy.data.objects.new('v048 | '+name,me);C.objects.link(o);o.data.materials.append(M[mat] if isinstance(mat,str) else mat);o['world_art_fixed']=True;created.append(o.name);return o
def shape(f,name,uv,y,mat):return poly(name,[proj(f,u,v,y) for u,v in uv],mat)
def stroke(f,name,uv,y,mat='ink',px=1.8):
 cr=bpy.data.curves.new('v048 '+name,'CURVE');cr.dimensions='3D';cr.resolution_u=1;cr.bevel_resolution=0;d=y-S.camera.matrix_world.translation.y;cr.bevel_depth=d*.36*px/7680
 sp=cr.splines.new('POLY');sp.points.add(len(uv)-1)
 for p,(u,v) in zip(sp.points,uv):p.co=(*proj(f,u,v,y),1)
 o=bpy.data.objects.new('v048 | '+name,cr);C.objects.link(o);cr.materials.append(M[mat]);o['world_art_fixed']=True;created.append(o.name);return o
def beam(f,name,a,b,width,y,mat='wood'):
 dx=b[0]-a[0];dy=b[1]-a[1];n=math.hypot(dx,dy);x=-dy/n*width/2;z=dx/n*width/2
 shape(f,name,[(a[0]+x,a[1]+z),(b[0]+x,b[1]+z),(b[0]-x,b[1]-z),(a[0]-x,a[1]-z)],y,mat)
 stroke(f,name+' lit splinter',[(a[0]+x*.8,a[1]+z*.8),(b[0]+x*.8,b[1]+z*.8)],y-.012,'wood_light',2)

def grade(ob,kind,frame,lift):
 old=ob.data.materials[0];m=old.copy();m.name='v048 | '+kind+' | '+ob.name;ob.data.materials[0]=m;nt=m.node_tree
 em=next(n for n in nt.nodes if n.type=='EMISSION');base=em.inputs[0].links[0].from_socket
 # Fixed oblique sky opening, not actor-following or camera-generated.
 g=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(g.outputs['Position'],sep.inputs[0]);S.frame_set(frame);cx=S.camera.matrix_world.translation.x-1.728
 x=nt.nodes.new('ShaderNodeMath');x.operation='SUBTRACT';x.inputs[1].default_value=cx;nt.links.new(sep.outputs['X'],x.inputs[0]);z=nt.nodes.new('ShaderNodeMath');z.operation='MULTIPLY_ADD';z.inputs[1].default_value=.65;z.inputs[2].default_value=-1.3;nt.links.new(sep.outputs['Z'],z.inputs[0]);a=nt.nodes.new('ShaderNodeMath');a.operation='ADD';nt.links.new(x.outputs[0],a.inputs[0]);nt.links.new(z.outputs[0],a.inputs[1]);ab=nt.nodes.new('ShaderNodeMath');ab.operation='ABSOLUTE';nt.links.new(a.outputs[0],ab.inputs[0]);rg=nt.nodes.new('ShaderNodeMapRange');rg.clamp=True;rg.interpolation_type='SMOOTHERSTEP';rg.inputs['From Min'].default_value=.3;rg.inputs['From Max'].default_value=7.5;rg.inputs['To Min'].default_value=lift;rg.inputs['To Max'].default_value=0;nt.links.new(ab.outputs[0],rg.inputs[0]);mix=nt.nodes.new('ShaderNodeMixRGB');mix.name='v048 | stationary sky opening on painted surface';mix.inputs[2].default_value=(.40,.43,.39,1) if kind=='warm morning' else (.28,.35,.40,1);nt.links.new(rg.outputs[0],mix.inputs[0]);nt.links.new(base,mix.inputs[1]);nt.links.new(mix.outputs[0],em.inputs[0]);changed.append({'object':ob.name,'material':m.name,'fixed_world_light_center':cx,'strength':lift})
grade(S.objects['v016 | Village continues | abandoned'],'warm morning',241,.08)
grade(S.objects['v016 | School | broken windows and plaster'],'overcast plaster',1201,.12)
grade(S.objects['v016 | Battlefield | broken village line'],'storm clearing',1849,.24)
grade(S.objects['v016 | Ruins | distant ash street'],'storm clearing',2161,.15)

# P1: restrained native detail on existing village masonry and the garden wall.
f=241;y=11.96
for j in range(7):
 v=.35+j*.058
 for i in range(6):
  u=.73+i*.046+(.023 if j%2 else 0)
  if .75<u<.91 and .35<v<.65:continue
  stroke(f,'village limestone joint %d %d'%(j,i),[(u,v),(u+.041,v+random.uniform(-.003,.003))],y,'warm_dark',1.2)
  if random.random()<.5:stroke(f,'village limestone riser %d %d'%(j,i),[(u,v),(u-.003,v+.046)],y,'warm_dark',1.1)
for k,(u,v) in enumerate([(.12,.49),(.22,.39),(.33,.40),(.67,.45),(.87,.72),(.95,.60)]):
 stroke(f,'village plaster hairline '+str(k),[(u,v+.08),(u-.006,v+.043),(u+.008,v+.02),(u-.008,v)],y-.01,'warm_dark',1.3)
for i in range(20):
 u=.02+i*.049;v=.345+random.uniform(-.006,.006)
 shape(f,'garden wall cap '+str(i),[(u,v),(u+.037,v+.005),(u+.040,v-.008),(u+.004,v-.012)],6,'warm')

# P2: window thickness, broken panes, chipped plaster and rain tracks.
f=1201;y=9.96
for idx,(u0,u1) in enumerate([(.056,.218),(.318,.440),(.580,.727)]):
 for u in [u0,u1]:stroke(f,'school masonry jamb %s %.3f'%(idx,u),[(u,.59),(u,.98)],y,'stone_dark',3)
 stroke(f,'school worn sill '+str(idx),[(u0-.015,.588),(u1+.014,.588),(u1+.014,.575),(u0-.012,.575)],y-.014,'stone_light',3.2)
 for j in range(4):
  v=.65+j*.082;stroke(f,'school window frame %s %s'%(idx,j),[(u0+.005,v),(u1-.004,v+.001)],y-.012,'wood_light',1.8)
 for u in [u0+(u1-u0)/3,u0+2*(u1-u0)/3]:stroke(f,'school window mullion %s %.3f'%(idx,u),[(u,.60),(u,.99)],y-.014,'stone_dark',2.1)
for k,(u,v) in enumerate([(.25,.78),(.47,.83),(.77,.72),(.86,.90),(.265,.43),(.82,.38)]):
 shape(f,'school plaster chip '+str(k),[(u-.012,v+.014),(u+.017,v+.009),(u+.021,v-.013),(u+.006,v-.031),(u-.010,v-.02)],y-.02,'stone_dark')
 stroke(f,'school fracture '+str(k),[(u,v+.065),(u-.007,v+.035),(u+.006,v+.015),(u,v-.045),(u+.012,v-.07)],y-.025,'stone_dark',1.7)
 stroke(f,'school rain run '+str(k),[(u+.014,v-.022),(u+.016,v-.08)],y-.023,'stone',2.2)
for k,uv in enumerate([[(.602,.81),(.620,.835),(.614,.785)],[(.697,.72),(.711,.755),(.716,.721)],[(.680,.92),(.69,.94),(.693,.898)]]):shape(f,'school surviving glass shard '+str(k),uv,y-.03,'glass')

# P3: new fixed ruined wall fragments and timber form a near-midground frame.
f=1849;y=7.8
left=[(-.08,.29),(-.08,1.08),(.05,1.08),(.056,.95),(.080,.958),(.082,.91),(.12,.92),(.117,.83),(.157,.85),(.15,.75),(.185,.77),(.18,.31)]
right=[(.87,.30),(.87,.62),(.896,.62),(.89,.72),(.917,.73),(.912,.83),(.945,.82),(.95,.97),(1.08,1.02),(1.08,.30)]
shape(f,'left broken masonry mass',left,y,'stone_dark');shape(f,'right broken masonry mass',right,y+.5,'stone_dark')
stroke(f,'left fractured sky edge',left[1:-1],y-.02,'stone_light',2.6);stroke(f,'right fractured sky edge',right[1:-1],y+.48,'stone_light',2.2)
for side,lo,hi in [('left',-.04,.15),('right',.92,1.06)]:
 for row in range(13):
  v=.34+row*.047
  for col in range(4):
   u=lo+col*.048+(.024 if row%2 else 0)
   if u>hi or (side=='left' and v>.77 and u>.09):continue
   stroke(f,'ruin mortar %s %s %s'%(side,row,col),[(u,v),(min(hi,u+.043),v+.001)],y-.025,'ink',1.9)
   if random.random()<.7:stroke(f,'ruin vertical seam %s %s %s'%(side,row,col),[(u,v),(u+.002,v+.040)],y-.026,'ink',1.4)
shape(f,'left dark broken window',[(.005,.62),(.075,.62),(.071,.77),(.045,.80),(.01,.77)],y-.03,'room')
stroke(f,'left window sill',[(.0,.62),(.077,.62),(.076,.608),(.0,.608)],y-.04,'stone_light',2)
beam(f,'collapsed timber left',(-.03,.365),(.258,.57),.025,6.1)
beam(f,'broken vertical left',(.101,.34),(.092,.65),.025,6.0)
beam(f,'right diagonal roof spar',(.83,.42),(1.02,.70),.020,6.7)
for k in range(5):
 u=.025+k*.018;stroke(f,'left timber dry grain '+str(k),[(u,.405+k*.012),(u+.13,.498+k*.012)],6.07,'wood_light',.9)

# Authored irregular terrain islands replace the mechanically repeated bottom leaf edge.
for region,f in [('peaceful',241),('transition',1201),('war_zone',1849)]:
 y=-5.05;top=[]
 for i in range(49):
  u=-.24+i*1.48/48;v=.188+.010*math.sin(i*.47)+.008*math.sin(i*1.31+f)
  top.append((u,v))
 shape(f,region+' fixed foreground soil bank',[(-.24,-.15),(1.24,-.15)]+list(reversed(top)),y,'soil' if region=='peaceful' else 'soil_war')
 # interrupted roots and strata; no repeated foliage strip or uniform rows
 for k in range(28):
  u=random.uniform(-.15,1.1);v=random.uniform(.015,.155);w=random.uniform(.012,.075)
  stroke(f,region+' dry soil stratum '+str(k),[(u,v),(u+w*.4,v+.005),(u+w,v-.004)],y-.02,'soil_light',random.uniform(.8,1.7))
 for k in range(8):
  u=random.uniform(-.1,1.05);v=random.uniform(.04,.18);length=random.uniform(.018,.065)
  stroke(f,region+' rooted fiber '+str(k),[(u,v),(u+.008,v-length*.3),(u+.002,v-length),(u+.014,v-length*1.2)],y-.025,'root',1.3)
 for k in range(52):
  u=random.uniform(-.15,1.1);v=random.uniform(.015,.173);w=random.uniform(.004,.017);h=w*random.uniform(.35,.8)
  shape(f,region+' angular soil stone '+str(k),[(u-w,v),(u-w*.5,v+h),(u+w*.6,v+h*.8),(u+w,v-h*.4),(u,v-h)],y-.03,'stone_dark')
  stroke(f,region+' stone upper plane '+str(k),[(u-w*.5,v+h),(u+w*.6,v+h*.8)],y-.035,'soil_light',1)
 # Midground scattered rubble/fieldstone anchored behind the walking surface.
 for k in range(18):
  u=random.choice([random.uniform(-.05,.30),random.uniform(.72,1.05)]);v=random.uniform(.294,.324);w=random.uniform(.004,.02);h=w*.6
  shape(f,region+' path shoulder stone '+str(k),[(u-w,v),(u-w*.6,v+h),(u+w*.5,v+h*.8),(u+w,v-.004)],3.1,'warm_dark' if region=='peaceful' else 'stone_dark')

# Every added object is a fixed world landmark: no location, alpha or visibility keys.
assert all(o.animation_data is None for o in C.objects)
assert actions()==original_actions,'Original action changed'
after_camera={}
for f in map(int,original_camera):
 S.frame_set(f);bpy.context.view_layer.update();after_camera[str(f)]=[list(v) for v in S.camera.matrix_world]
assert after_camera==original_camera
for snd in bpy.data.sounds:snd.filepath=bpy.path.abspath(snd.filepath)
S['v048_scope']='WORLD ART ONLY. Open diagnostic views. Characters, title treatment, full trailer timing, music and FX retained from v040. Native world-fixed additions; no dissolving architecture.'
S['v048_artistic_acceptance']='PARTIAL WORLD STUDY; Arcane-level target NOT CLAIMED.'
S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_percentage=100;S.render.image_settings.media_type='IMAGE';S.render.image_settings.file_format='PNG';S.eevee.taa_render_samples=32
S.frame_set(1849)
for image in bpy.data.images:
 if image.source=='FILE' and not image.packed_file:
  try:image.pack()
  except Exception:pass
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
report={'native':str(OUT),'source':str(SRC),'source_sha256':sha(SRC),'native_sha256':sha(OUT),'world_scene':S.name,'created_native_objects':len(created),'modified_environment_materials':changed,'original_actions_identical':actions()==original_actions,'camera_samples_identical':after_camera==original_camera,'original_timing':original_timing,'new_objects_have_no_actions':True,'frames':{'peaceful':241,'transition':1201,'war_zone':1849},'changes':['World-fixed oblique sky openings painted into existing architecture materials','Existing village/school masonry, plaster chips, window thickness, glass and rain-run details','Fixed ruined masonry, fractured edges and weathered timber frame battlefield','Irregular foreground banks, strata, roots and stones replace repeated lower foliage at three study areas'],'limits':['Three representative regions; woods/camp and all intervening continuity require further art passes','No changed character rig/motion, FX, title or edit timing','Sub-4K original paintings retained; native curve/mesh detail is resolution-independent','Still-image study; no continuous motion artistic acceptance']}
(O/'build_manifest.json').write_text(json.dumps(report,indent=2));(O/'after_preview').mkdir(exist_ok=True)
S.render.resolution_percentage=25;S.eevee.taa_render_samples=16
for name,f in report['frames'].items():
 S.frame_set(f);S.render.filepath=str(O/'after_preview'/f'{name}_{f}_960.png');bpy.ops.render.render(write_still=True,scene=S.name);print('AFTER_PREVIEW',name,flush=True)
print('WORLD_ART_BUILT',len(created),'objects',str(OUT),flush=True)
