"""One compact low-smoke correction. No new simulation or large fracture blocks."""
import bpy,bmesh,math,random,json,re,shutil
from pathlib import Path
from mathutils import Vector
P=Path(__file__).resolve().parents[1];s=bpy.data.scenes['FXv010 | joined rupture and ground dust'];bpy.context.window.scene=s
oldroot=bpy.data.objects['FXv010 | fixed impact anchor and timing'];origin=oldroot.location.copy();oldvol=bpy.data.objects['FXv010 | retimeable finite dust VDB'];volmatrix=oldvol.matrix_world.copy();olddata=oldvol.data
oldlights=[o for o in s.objects if o.type=='LIGHT']
for c in list(s.collection.children):s.collection.children.unlink(c)
for o in list(s.collection.objects):
    if o!=s.camera:s.collection.objects.unlink(o)
s.name='FXv011 | compact brief impact low dust';s.view_layers[0].name='RUPTURE';s.frame_start=1;s.frame_end=72;s.render.fps=24;s.render.fps_base=1
s.render.engine='BLENDER_EEVEE';s.eevee.taa_render_samples=24;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.media_type='IMAGE'
asset=bpy.data.collections.new('FXv011 | COMPACT IMPACT | brief flash small debris low dust');s.collection.children.link(asset)
preview=bpy.data.collections.new('FXv011 | PREVIEW lights only');s.collection.children.link(preview)
for old in oldlights:o=old.copy();o.data=old.data.copy();preview.objects.link(o)
r=bpy.data.objects.new('FXv011 | fixed impact anchor and controls',None);asset.objects.link(r);r.location=origin;r.empty_display_type='CIRCLE';r.empty_display_size=.2
for k,v in {'start_frame':7.,'speed':1.,'size':1.,'age':0.,'dust_density':.04,'intensity':1.}.items():r[k]=v
def drive(owner,path,expr,index=None):
    f=owner.driver_add(path) if index is None else owner.driver_add(path,index);f.driver.type='SCRIPTED'
    for v in list(f.driver.variables):f.driver.variables.remove(v)
    for n,k in [('t','["age"]'),('start','["start_frame"]'),('speed','["speed"]'),('S','["size"]'),('D','["dust_density"]'),('I','["intensity"]'),('Z','location[2]')]:
        if not re.search(r'\b'+n+r'\b',expr):continue
        v=f.driver.variables.new();v.name=n;v.type='SINGLE_PROP';v.targets[0].id=r;v.targets[0].data_path=k
    f.driver.expression=expr;return f
drive(r,'["age"]','(frame-start)*speed')
for axis in range(3):drive(r,'scale','max(.01,S)',axis)
bpy.context.view_layer.update()
atlas=bpy.data.images.get('FXv003 | ORIGINAL four cold forms | packed straight alpha')
if not atlas:atlas=bpy.data.images.load(str(P.parent/'benchmark_v003/assets/Cold_Smoke_Atlas_4Forms_v003.png'));atlas.pack()
def material(name,color,alpha='1',paint=False,hot=False):
    m=bpy.data.materials.new('FXv011 | '+name);m.use_nodes=True;m.surface_render_method='DITHERED';nt=m.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(*color,1)
    if paint:
        tc=nt.nodes.new('ShaderNodeTexCoord');scale=nt.nodes.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(.34,.34,.34);nt.links.new(tc.outputs['Generated'],scale.inputs[0]);off=nt.nodes.new('ShaderNodeVectorMath');off.operation='ADD';off.inputs[1].default_value=(.08,.58,0);nt.links.new(scale.outputs[0],off.inputs[0]);tex=nt.nodes.new('ShaderNodeTexImage');tex.image=atlas;nt.links.new(off.outputs[0],tex.inputs[0]);hsv=nt.nodes.new('ShaderNodeHueSaturation');hsv.inputs['Saturation'].default_value=.15;hsv.inputs['Value'].default_value=.9;nt.links.new(tex.outputs[0],hsv.inputs['Color']);mix=nt.nodes.new('ShaderNodeMixRGB');mix.inputs[0].default_value=.55;mix.inputs[1].default_value=(*color,1);nt.links.new(hsv.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],em.inputs[0])
    if hot:em.inputs['Strength'].default_value=2.3
    tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');drive(mix.inputs[0],'default_value',alpha);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],out.inputs[0]);return m
scar=material('small persistent ragged soil mark',(.014,.018,.018),'I*.72 if t>=1 else 0',True)
chip=material('small painted charcoal debris',(.026,.031,.030),'I',True)
flash=material('brief muted ochre impact',(.58,.235,.045),'I*max(0,min(1,(3-t)/1.5)) if t>=0 else 0',False,True)
core=material('brief pale wash core',(.86,.68,.35),'I*max(0,min(1,(1.8-t))) if t>=0 else 0',False,True)
def polygon(name,points,mat,y=0):
    me=bpy.data.meshes.new(name);me.from_pydata([(x,y,z) for x,z in points],[],[tuple(range(len(points)))]);me.materials.append(mat);me.update();o=bpy.data.objects.new('FXv011 | '+name,me);asset.objects.link(o);o.parent=r;return o
# A restrained broken stain, not the previous raised ring/crater model.
polygon('persistent charcoal ground nick',[(-.39,.004),(-.31,.018),(-.22,.009),(-.13,.027),(-.04,.018),(.06,.026),(.13,.013),(.26,.021),(.32,.009),(.40,.003),(.30,-.006),(.17,-.003),(.04,-.010),(-.12,-.006),(-.28,-.009)],scar,y=-.10)
# Two/three-frame compact drawn flash; no large or sustained smoke core.
outline=[(-.17,.0),(-.18,.04),(-.13,.09),(-.16,.12),(-.10,.15),(-.08,.24),(-.03,.20),(.02,.32),(.065,.18),(.115,.21),(.10,.11),(.17,.07),(.12,.03),(.15,.0)]
fl=polygon('compact2to3frame flash',outline,flash,y=-.11)
for axis in range(3):drive(fl,'scale','max(.0001,1-.16*max(0,t)) if 0<=t<3 else .0001',axis)
co=polygon('small pale core',[(-.085,0),(-.095,.06),(-.035,.10),(.005,.19),(.05,.08),(.09,.035),(.07,0)],core,y=-.13)
for axis in range(3):drive(co,'scale','1 if 0<=t<2 else .0001',axis)
# Nine small irregular coherent chips, on the shot's X/Z motion plane.
# Authored gravity arcs + one small rebound; no large masonry blocks or grit swarm.
rng=random.Random(11219);records=[]
for i,(vx,vz) in enumerate([(-1.35,3.9),(-.85,3.25),(-.35,4.5),(.40,3.8),(.95,4.1),(1.5,3.35),(-1.7,2.8),(1.15,2.7),(.15,3.15)]):
    radius=rng.uniform(.025,.043);birth=i%2;me=bpy.data.meshes.new('FXv011 | small irregular chip');bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=2,radius=radius)
    for v in bm.verts:v.co*=rng.uniform(.78,1.20);v.co.y*=.48
    bm.to_mesh(me);bm.free();me.materials.append(chip);o=bpy.data.objects.new(f'FXv011 | small falling debris {i:02d}',me);asset.objects.link(o);o.parent=r;o.location.y=-.06+.01*(i%3)
    u=f'max(0,t-{birth})/24';flight=2*vz/12;after=f'max(0,({u})-{flight})';land=vx*flight*math.exp(-.15*flight)
    drive(o,'location',f'{vx}*min({flight},({u}))*exp(-.15*min({flight},({u})))+{vx*.08}*(1-exp(-8*({after})))',0)
    drive(o,'location',f'{radius*.72}+max(0,{vz}*({u})-6*({u})**2)+max(0,.45*({after})-6*({after})**2)',2)
    for axis in range(3):drive(o,'rotation_euler',f'{rng.uniform(-2,2)}+{rng.uniform(-11,11)}*min({flight+.10},({u}))',axis);drive(o,'scale',f'1 if t>={birth} else .0001',axis)
    shadow=material(f'tiny contact shadow{i}',(.012,.014,.014),f'.16*I*max(0,min(1,(t-{birth})/2))*exp(-max(0,{vz}*({u})-6*({u})**2)/.12) if t>={birth} else 0')
    pts=[(land+radius*1.35*math.cos(j*math.pi/8),.003+.005*math.sin(j*math.pi/8)) for j in range(16)];sh=polygon(f'ground contact shadow{i:02d}',pts,shadow,y=-.105)
    # Shadows are understated and only become visible close to landing.
    drive(sh,'location',f'{vx}*min({flight},({u}))*exp(-.15*min({flight},({u})))-({land})+{vx*.08}*(1-exp(-8*({after})))',0)
    records.append({'name':o.name,'radius':radius,'birth_age':birth,'apex_age':birth+vz/12*24,'landing_age':birth+flight*24,'final_x':land+vx*.08})
# Reuse only the first30 existing cache frames; substantially reduce and clip dust.
# No new bake and no animated scaling of a mature cloud.
src=P.parent/'rupture_mass_v010/cache/dust64_flat/data'
for fr in range(1,31):shutil.copy2(src/f'fluid_data_{fr:04d}.vdb',P/f'cache/data/fluid_data_{fr:04d}.vdb')
v=olddata.copy();v.name='FXv011 |30frame modest residual dust';v.animation_data_clear();v.filepath='//../cache/data/fluid_data_0001.vdb';v.frame_duration=30;v.sequence_mode='CLIP';v.materials.clear();drive(v,'frame_offset','t+7-frame');vo=bpy.data.objects.new('FXv011 | faint low residual dust only',v);asset.objects.link(vo);vo.matrix_world=volmatrix;vo.parent=r;vo.matrix_parent_inverse=r.matrix_world.inverted()
m=bpy.data.materials.new('FXv011 | faint dust height and duration limited');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();info=nt.nodes.new('ShaderNodeVolumeInfo');gain=nt.nodes.new('ShaderNodeMath');gain.operation='MULTIPLY';nt.links.new(info.outputs['Density'],gain.inputs[0]);drive(gain.inputs[1],'default_value','19*D*I*exp(-max(0,t-3)/5)*max(0,min(1,(22-t)/5)) if t>=0 else 0')
geom=nt.nodes.new('ShaderNodeNewGeometry');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(geom.outputs['Position'],sep.inputs[0]);height=nt.nodes.new('ShaderNodeMath');height.operation='SUBTRACT';nt.links.new(sep.outputs['Z'],height.inputs[0]);drive(height.inputs[1],'default_value','Z');mask=nt.nodes.new('ShaderNodeMapRange');mask.clamp=True;mask.inputs['From Min'].default_value=.10;mask.inputs['From Max'].default_value=.30;mask.inputs['To Min'].default_value=1;mask.inputs['To Max'].default_value=0;nt.links.new(height.outputs[0],mask.inputs[0]);mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';nt.links.new(gain.outputs[0],mul.inputs[0]);nt.links.new(mask.outputs[0],mul.inputs[1]);vol=nt.nodes.new('ShaderNodeVolumePrincipled');vol.inputs['Color'].default_value=(.16,.18,.17,1);vol.inputs['Density Attribute'].default_value='';vol.inputs['Color Attribute'].default_value='';vol.inputs['Temperature Attribute'].default_value='';vol.inputs['Emission Strength'].default_value=0;vol.inputs['Blackbody Intensity'].default_value=0;nt.links.new(mul.outputs[0],vol.inputs['Density']);out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(vol.outputs['Volume'],out.inputs['Volume']);v.materials.append(m)
# Retain the existing held-shot review composite and exact child/foreground masks.
for n in s.compositing_node_group.nodes:
    if n.type=='R_LAYERS':n.scene=s;n.layer='RUPTURE'
r['construction']='One compact event:2-3frame flash,9 small authored falling chips,4percent old dust gain with low height mask and rapid decay,small persistent ground nick. No towering/sustained plume, no raised ring, no large blocks.'
s.frame_set(8);r.update_tag(refresh={'OBJECT'});bpy.context.view_layer.update();native=P/'native/WTSC_Compact_Impact_Proof_v011.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
report={'blender':bpy.app.version_string,'fps':24,'frames':[1,72],'impact_frame':7,'flash_age_range':[0,3],'small_debris':records,'dust_gain_fraction_of_v010':.04,'dust_full_strength_below_metres':.10,'dust_zero_above_metres':.30,'dust_zero_after_age':22,'dust_cache_frames':30,'dust_cache_bytes':sum(f.stat().st_size for f in (P/'cache/data').glob('*.vdb')),'new_simulation':False,'root':list(r.location),'changes':'Simplified visible event once in direct response to the amount-of-smoke correction. Large block fractures and raised crater ring are removed.','pending':'Actual shot-size key review.'}
(P/'evidence/build_compact.json').write_text(json.dumps(report,indent=2));print('COMPACT_IMPACT_BUILT',json.dumps({k:v for k,v in report.items() if k!='small_debris'}),flush=True)
