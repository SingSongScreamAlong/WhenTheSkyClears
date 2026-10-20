"""Native static-camera proof: precompute occlusion/light, render real FX motion."""
import bpy,math,random,json
from pathlib import Path
P=Path(__file__).resolve().parents[1]
p=bpy.data.scenes['FX_SHOT_PROOF_v002 | held real shot + native eruption'];bpy.context.window.scene=p;p.frame_set(1825)
fx=bpy.data.collections['FXv002 | Detailed painterly ground eruption'];root=bpy.data.objects['FXv002 | fixed ground origin and controls']
hold=bpy.data.collections['FXv002 proof | frozen native foreground occlusion'];light=bpy.data.collections['FXv002 proof | source-anchored paint relighting']
random.seed(220180)
# Replace the overly graphic black chips with smaller, irregular matte stone.
mat=bpy.data.materials['FXv002 | rough broken charcoal and plaster'];nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');tex=next(n for n in nt.nodes if n.type=='TEX_NOISE');ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.025,.023,.021,1);ramp.color_ramp.elements[1].color=(.16,.14,.115,1);nt.links.new(tex.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
for ob in [o for o in fx.objects if 'weighted debris' in o.name]:
 radius=random.uniform(.007,.018)
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=radius)
 temp=bpy.context.object;me=temp.data;me.name=ob.name+' | chipped stone geometry'
 axes=[random.uniform(.65,1.5) for _ in range(3)]
 for v in me.vertices:
  noise=random.uniform(.84,1.14)
  for j in range(3):v.co[j]*=axes[j]*noise
 ob.data=me;ob.data.materials.clear();ob.data.materials.append(mat);bpy.data.objects.remove(temp,do_unlink=True)

def ambient(s):
 s.world=bpy.data.worlds.new(s.name+' | cool diffuse fill for solid debris');s.world.use_nodes=True;b=s.world.node_tree.nodes.get('Background');b.inputs[0].default_value=(.13,.16,.20,1);b.inputs[1].default_value=.32
ambient(p)
if hasattr(p.render,'compositor_device'):p.render.compositor_device='CPU'
comp=p.compositing_node_group;p.compositing_node_group=None;p.render.resolution_percentage=50;p.cycles.samples=8;p.cycles.use_animated_seed=False;p.cycles.seed=22017;p.render.image_settings.color_mode='RGBA'
lc=p.view_layers[0].layer_collection
def exclude(c,v):lc.children[c.name].exclude=v
exclude(fx,True);exclude(light,False);exclude(hold,False);p.frame_set(1814)
p.render.filepath=str(P/'assets/Native_Local_Light_Peak_1080_v002.png');bpy.ops.render.render(write_still=True,scene=p.name)
reference=root['intensity']*(.72+2.4*math.exp(-1/3.5))*(.93+.07*math.sin(1.7))
# Original alpha networks retained; white replaces Holdout only during this bake.
swapped=[];cache={}
for ob in hold.objects:
 for i,m in enumerate(list(ob.data.materials)):
  if not m:continue
  swapped.append((ob,i,m))
  if m.name not in cache:
   mm=m.copy();mm.name='Static alpha bake | '+m.name;nn=mm.node_tree;em=nn.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(1,1,1,1)
   for n in [n for n in nn.nodes if n.type=='HOLDOUT']:
    for link in list(n.outputs[0].links):nn.links.new(em.outputs[0],link.to_socket)
   cache[m.name]=mm
  ob.data.materials[i]=cache[m.name]
exclude(light,True);p.frame_set(1825);p.render.filepath=str(P/'assets/Native_Foreground_Alpha_1080_v002.png');bpy.ops.render.render(write_still=True,scene=p.name)
for ob,i,m in swapped:ob.data.materials[i]=m
exclude(fx,False);exclude(light,False);exclude(hold,False);p.compositing_node_group=comp;p.render.resolution_percentage=100
scale=next(n for n in comp.nodes if n.type=='SCALE');scale.inputs['X'].default_value=1;scale.inputs['Y'].default_value=1
# Final4K still includes the refined debris and corrected local-light driver.
p.frame_set(1825);p.render.filepath=str(P/'previews/WTSC_Explosion_Benchmark_4K_v002.png');bpy.ops.render.render(write_still=True,scene=p.name)

fast=bpy.data.scenes.new('FX_MOTION_v002 | real shot plate + animated native FX');fast.collection.children.link(fx)
cam=p.camera.copy();cam.data=p.camera.data.copy();fast.collection.objects.link(cam);fast.camera=cam;ambient(fast)
fast.render.engine='CYCLES';fast.cycles.device='CPU';fast.cycles.samples=8;fast.cycles.use_denoising=True;fast.cycles.max_bounces=2;fast.cycles.transparent_max_bounces=16;fast.cycles.use_animated_seed=False;fast.cycles.seed=22017
fast.render.threads_mode='FIXED';fast.render.threads=2;fast.render.resolution_x=1920;fast.render.resolution_y=1080;fast.render.resolution_percentage=100;fast.render.fps=24;fast.render.film_transparent=True;fast.frame_start=1795;fast.frame_end=1890
fast.render.image_settings.media_type='IMAGE';fast.render.image_settings.file_format='PNG';fast.render.image_settings.color_mode='RGB';fast.view_settings.view_transform='Standard';fast.view_settings.look='None'
if hasattr(fast.render,'compositor_device'):fast.render.compositor_device='CPU'
fast.use_nodes=True;nt=bpy.data.node_groups.new('FXv002 | source plate + native relighting + occluded real motion','CompositorNodeTree');fast.compositing_node_group=nt;nt.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
def image_node(path,name):
 im=bpy.data.images.load(str(path),check_existing=True);im.alpha_mode='STRAIGHT';im.pack();n=nt.nodes.new('CompositorNodeImage');n.image=im;n.name=name;return n
bg=image_node(P/'assets/Real_Scene_Base_Plate_4K_v002.png','Held real project shot at frame1825');bgs=nt.nodes.new('CompositorNodeScale');bgs.inputs['X'].default_value=.5;bgs.inputs['Y'].default_value=.5;nt.links.new(bg.outputs['Image'],bgs.inputs['Image'])
li=image_node(P/'assets/Native_Local_Light_Peak_1080_v002.png','Baked native spatial receiver response, animated source strength')
ma=image_node(P/'assets/Native_Foreground_Alpha_1080_v002.png','Actual native foreground alpha at held shot position')
lit=nt.nodes.new('CompositorNodeAlphaOver');nt.links.new(bgs.outputs['Image'],lit.inputs['Background']);nt.links.new(li.outputs['Image'],lit.inputs['Foreground'])
f=lit.inputs['Factor'].driver_add('default_value');f.driver.type='SCRIPTED';f.driver.expression=f'min(1,max(0,I*(.72+2.4*exp(-max(0,t)/3.5))*(.93+.07*sin(t*1.7))*max(0,min(1,t,128-t))/{reference}))'
for name,key in [('t','age'),('I','intensity')]:
 v=f.driver.variables.new();v.name=name;v.type='SINGLE_PROP';v.targets[0].id=root;v.targets[0].data_path='["'+key+'"]'
rl=nt.nodes.new('CompositorNodeRLayers');rl.scene=fast
inv=nt.nodes.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1;nt.links.new(ma.outputs['Alpha'],inv.inputs[1])
masked=nt.nodes.new('CompositorNodeAlphaOver');masked.inputs['Background'].default_value=(0,0,0,0);nt.links.new(inv.outputs[0],masked.inputs['Factor']);nt.links.new(rl.outputs['Image'],masked.inputs['Foreground'])
over=nt.nodes.new('CompositorNodeAlphaOver');nt.links.new(lit.outputs['Image'],over.inputs['Background']);nt.links.new(masked.outputs['Image'],over.inputs['Foreground']);out=nt.nodes.new('NodeGroupOutput');nt.links.new(over.outputs['Image'],out.inputs['Image'])
bpy.context.window.scene=fast;fast.frame_set(1825)
bpy.ops.wm.save_as_mainfile(filepath=str(P/'native/WTSC_FX_Shot_Proof_v002.blend'),compress=True)
bpy.data.libraries.write(str(P/'native/WTSC_Hero_Eruption_Collection_v002.blend'),{fx},fake_user=True,compress=True)
report={'motion_scene':fast.name,'frames':[1795,1890],'fps':24,'pixels':[1920,1080],'background':'Real project camera, scenery and characters held at1825 for FX evaluation. Not a locomotion or full-trailer integration test.','occlusion':'Original native foreground alpha captured once for this fixed camera; real animated FX masked by it.','light':'Native spatial receiver response captured at peak, modulated with the same source time/flicker expression; not a global overlay.','debris':'Refined smaller rough3D stone with actual weighted trajectories and cool diffuse fill.','smoke':'Detailed original paint, subdivided native pinned flow, UV advection and shader cooling;2.5D rather than fluid simulation.','source_editing':'No production file modified.'}
(P/'evidence/fast_motion_setup.json').write_text(json.dumps(report,indent=2));print('FX_FAST_MOTION_PREPARED',json.dumps(report),flush=True)
