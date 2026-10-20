import bpy,json,hashlib,math,random
from pathlib import Path
O=Path(__file__).parent;SRC=Path(r'WTSC_LOCAL_WORKSPACE\work\world_facade_v057\WTSC_Continuous_Painterly_Facade_Proof_v057.blend')
OUT=O/'WTSC_Rooted_Foreground_Study_v058a.blend';assert not OUT.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC)=='87c897b5ccc178b1288f5d614eeaa34d642b8e8ac2c239bcd2ab50a79569361a'
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_CONTINUOUS_FACADE_SOURCE_LIGHTING_v057_TEST'];bpy.context.window.scene=s
def actions():
 d={}
 for a in bpy.data.actions:
  rows=[]
  for l in a.layers:
   for st in l.strips:
    for bag in st.channelbags:
     for f in bag.fcurves:rows.append((f.data_path,f.array_index,[(tuple(k.co),k.interpolation) for k in f.keyframe_points]))
  d[a.name]=hashlib.sha256(repr(rows).encode()).hexdigest()
 return d
before_actions=actions();before_timing={t.name:[t.frame_start,t.frame_end,t.render.fps,t.render.resolution_x,t.render.resolution_y] for t in bpy.data.scenes}
camera={}
for f in [1,241,601,961,1201,1537,1849,2161,2377,2400]:
 s.frame_set(f);bpy.context.view_layer.update();camera[str(f)]=[list(v) for v in s.camera.matrix_world]

o=s.objects['v020 | Walking path | continuous blended paint'];m=o.data.materials[0].copy();m.name='v058a | continuous earth | original light and path silhouette';o.data.materials[0]=m;nt=m.node_tree
def mathnode(op,a,b=None,name=None):
 n=nt.nodes.new('ShaderNodeMath');n.operation=op;n.name=name or 'v058a | '+op
 for i,v in enumerate([a,b]):
  if v is None:continue
  if isinstance(v,(int,float)):n.inputs[i].default_value=v
  else:nt.links.new(v,n.inputs[i])
 return n.outputs[0]
def ramp(src,a,b,c,d,name):
 n=nt.nodes.new('ShaderNodeMapRange');n.name='v058a | '+name;n.clamp=True;n.interpolation_type='SMOOTHERSTEP'
 for i,v in enumerate([a,b,c,d],1):n.inputs[i].default_value=v
 nt.links.new(src,n.inputs[0]);return n.outputs[0]
geo=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geo.outputs['Position'],sep.inputs[0]);x=sep.outputs['X'];z=sep.outputs['Z']
u=mathnode('MULTIPLY_ADD',x,.1176470588);u.node.inputs[2].default_value=.137
u=mathnode('FRACT',u)
u2=mathnode('FRACT',mathnode('ADD',u,.5))
v=ramp(z,-.75,.55,.035,.235,'earth-only source band excludes painted children')
image=bpy.data.images['Foreground_Bank_Paintover_v047.png'];image.pack()
def sample(ux):
 c=nt.nodes.new('ShaderNodeCombineXYZ');nt.links.new(ux,c.inputs[0]);nt.links.new(v,c.inputs[1]);t=nt.nodes.new('ShaderNodeTexImage');t.image=image;t.extension='EXTEND';nt.links.new(c.outputs[0],t.inputs[0]);return t.outputs[0]
a=sample(u);b=sample(u2)
phase=mathnode('COSINE',mathnode('MULTIPLY',u,2*math.pi));weight=mathnode('MULTIPLY_ADD',phase,.5);weight.node.inputs[2].default_value=.5
mix=nt.nodes.new('ShaderNodeMixRGB');mix.name='v058a | overlapping paint samples hide wrap without mirrors';nt.links.new(weight,mix.inputs[0]);nt.links.new(a,mix.inputs[1]);nt.links.new(b,mix.inputs[2])
warm=nt.nodes.new('ShaderNodeMixRGB');warm.blend_type='MULTIPLY';warm.name='v058a | warm village soil to cool ash';warm.inputs[2].default_value=(1.65,1.13,.64,1);nt.links.new(ramp(x,27,47,.6,0,'fixed geography warmth'),warm.inputs[0]);nt.links.new(mix.outputs[0],warm.inputs[1])
hs=nt.nodes['Hue/Saturation/Value'];old=hs.inputs['Color'].links[0].from_socket
replace=nt.nodes.new('ShaderNodeMixRGB');replace.name='v058a | replace mirrored lower leaf border only';nt.links.new(ramp(z,.32,.56,1,0,'foreground-only spatial mask'),replace.inputs[0]);nt.links.new(old,replace.inputs[1]);nt.links.new(warm.outputs[0],replace.inputs[2]);nt.links.new(replace.outputs[0],hs.inputs['Color'])
# Old three isolated soil patches are superseded by the continuous earth field.
disabled=[]
for n in nt.nodes:
 if n.name.startswith('v048b |') and 'earth-only spatial join' in n.name:
  for l in list(n.inputs[0].links):nt.links.remove(l)
  n.inputs[0].default_value=0;disabled.append(n.name)

# Small, individually shaped leaves with fixed roots; no identical grass cards.
c=bpy.data.collections.new('v058a | irregular rooted path-edge plants');s.collection.children.link(c)
hidden=[]
for old in s.objects:
 if old.name.startswith('v016 | Rooted grass'):
  old.hide_render=True;hidden.append(old.name)
leaf_mats=[]
for i,col in enumerate([(.018,.025,.019),(.035,.043,.027),(.055,.060,.037),(.024,.032,.032)]):
 ma=bpy.data.materials.new('v058a | plant ink '+str(i));ma.use_nodes=True;n=ma.node_tree.nodes;n.clear();em=n.new('ShaderNodeEmission');em.inputs[0].default_value=(*col,1);out=n.new('ShaderNodeOutputMaterial');ma.node_tree.links.new(em.outputs[0],out.inputs[0]);leaf_mats.append(ma)
rng=random.Random(581026);plants=[];xx=-8
while xx<165:
 xx+=rng.uniform(.62,2.35)
 if rng.random()<.18:continue
 verts=[];faces=[];matids=[];rootz=rng.uniform(.11,.23);yy=1.97-rng.uniform(.01,.10);war=xx>95
 for blade in range(rng.randint(3,7) if not war else rng.randint(2,4)):
  bx=xx+rng.uniform(-.07,.07);bz=rootz+rng.uniform(-.035,.01);h=rng.uniform(.09,.24)*( .7 if war else 1);lean=rng.uniform(-.20,.20);w=rng.uniform(.012,.027);start=len(verts)
  for k in range(11):
   t=k/10;cx=bx+lean*t*t+.018*math.sin(t*math.pi);cz=bz+h*t;half=w*(math.sin(math.pi*t)**.8)*(.7+.3*math.sin(t*math.pi*1.8))
   verts.extend([(cx-half,yy-.012*math.sin(t*math.pi),cz),(cx+half,yy,cz)])
  for k in range(10):faces.append((start+k*2,start+k*2+1,start+k*2+3,start+k*2+2));matids.append(rng.choices([0,1,2,3],[5,3,1,2] if war else [2,4,2,1])[0])
 me=bpy.data.meshes.new('v058a rooted leaves');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new('v058a | rooted plant %03d'%len(plants),me);c.objects.link(ob)
 for ma in leaf_mats:me.materials.append(ma)
 for p,mi in zip(me.polygons,matids):p.material_index=mi
 ob['root_world']=[xx,yy,rootz];ob['role']='fixed path shoulder vegetation, below walking contact lane';plants.append(ob.name)
s.name='WTSC_ROOTED_FOREGROUND_v058a_WORLD_STUDY';s['v058a_scope']='Route-wide lower path foliage repetition correction. Existing source drawings, school proof, timing, title, audio and character performance preserved.'
s['v058a_artistic_status']='Development proof; whole-film minimum not yet attained.'
assert actions()==before_actions
after_camera={}
for f in map(int,camera):s.frame_set(f);bpy.context.view_layer.update();after_camera[str(f)]=[list(v) for v in s.camera.matrix_world]
assert after_camera==camera
s.render.threads_mode='FIXED';s.render.threads=2;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.frame_set(1537)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'BUILD_v058a.json').write_text(json.dumps({'native':str(OUT),'sha256':sha(OUT),'source':str(SRC),'source_unchanged':sha(SRC)=='87c897b5ccc178b1288f5d614eeaa34d642b8e8ac2c239bcd2ab50a79569361a','original_actions_identical':actions()==before_actions,'camera_samples_identical':camera==after_camera,'original_timing':before_timing,'disabled_local_rgb_patches':disabled,'replaced_needle_grass_objects':len(hidden),'new_unique_plant_meshes':len(plants),'original_path_alpha_graph':'unchanged','scope':'lower path RGB only plus separately rooted foreground plant meshes','limitations':['Native plants are a static study and need art review','No character-motion integration or minimum-standard claim']},indent=2))
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100;s.eevee.taa_render_samples=32;s.render.use_sequencer=False;s.render.dither_intensity=0
for f in [241,601,961,1201,1537,1849,2161,2377]:
 s.frame_set(f);s.render.filepath=str(O/f'AFTER_A_{f:04d}.png');bpy.ops.render.render(write_still=True,scene=s.name);print('V058A_FRAME',f,flush=True)
print('V058A_READY',flush=True)
