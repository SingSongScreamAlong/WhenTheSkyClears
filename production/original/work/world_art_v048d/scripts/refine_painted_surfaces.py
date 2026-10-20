import bpy,json,hashlib,random,math
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
R=Path(r'WTSC_LOCAL_WORKSPACE');O=Path(r'WTSC_LOCAL_USER\Documents\Codex\2026-10-16\task\world_art_v048')
out=O/'WTSC_World_Art_Branch_v048b.blend';assert not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(O/'WTSC_World_Art_Branch_v048.blend'),load_ui=False,use_scripts=False);S=bpy.data.scenes['WTSC_WORLD_CORRECTED_v040'];bpy.context.window.scene=S
image=bpy.data.images.load(str(R/'sets/refinement_v047/Foreground_Bank_Paintover_v047.png'),check_existing=True);image.pack()
random.seed(4819);hidden=[]
for o in S.objects:
 if not o.name.startswith('v048 |'):continue
 if any(k in o.name for k in ['angular soil stone','stone upper plane','school plaster chip','surviving glass shard','broken masonry mass','fractured sky edge','ruin mortar','ruin vertical seam','left dark broken window','left window sill','collapsed timber','broken vertical','diagonal roof spar','timber dry grain','garden wall cap']):o.hide_render=True;hidden.append(o.name)
def ramp(nt,src,a,b,c,d):
 n=nt.nodes.new('ShaderNodeMapRange');n.clamp=True;n.interpolation_type='SMOOTHERSTEP'
 for key,v in [('From Min',a),('From Max',b),('To Min',c),('To Max',d)]:n.inputs[key].default_value=v
 nt.links.new(src,n.inputs[0]);return n.outputs[0]
def mul(nt,a,b):
 n=nt.nodes.new('ShaderNodeMath');n.operation='MULTIPLY';nt.links.new(a,n.inputs[0]);nt.links.new(b,n.inputs[1]);return n.outputs[0]
def uv_map(o,name,f):
 S.frame_set(f);bpy.context.view_layer.update();u=o.data.uv_layers.new(name=name)
 for loop in o.data.loops:
  p=world_to_camera_view(S,S.camera,o.matrix_world@o.data.vertices[loop.vertex_index].co);u.data[loop.index].uv=(p.x,p.y)
 return name
for label,f in [('peaceful',241),('transition',1201),('war_zone',1849)]:
 o=S.objects['v048 | '+label+' fixed foreground soil bank'];name=uv_map(o,'v048b fixed soil paint registration '+label,f)
 m=bpy.data.materials.new('v048b | '+label+' original painted earth');m.use_nodes=True;m.surface_render_method='DITHERED';nt=m.node_tree;nt.nodes.clear();uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map=name;t=nt.nodes.new('ShaderNodeTexImage');t.image=image;t.extension='EXTEND';nt.links.new(uv.outputs[0],t.inputs[0]);em=nt.nodes.new('ShaderNodeEmission');nt.links.new(t.outputs[0],em.inputs[0]);sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs[0],sep.inputs[0]);fac=mul(nt,ramp(nt,sep.outputs[0],-.24,-.08,0,1),ramp(nt,sep.outputs[0],1.08,1.24,1,0));tr=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(fac,mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);outn=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(mix.outputs[0],outn.inputs[0]);o.data.materials[0]=m
# Replace the repeating lower-path foliage RGB using earth-only pixels of the
# owned v047 painting. UV and spatial masks stay fixed to world geometry.
o=S.objects['v020 | Walking path | continuous blended paint'];m=o.data.materials[0].copy();m.name='v048b | continuous path | fixed earth-only paint joins';o.data.materials[0]=m;nt=m.node_tree;em=next(n for n in nt.nodes if n.type=='EMISSION');base=em.inputs[0].links[0].from_socket
for label,f in [('peaceful',241),('transition',1201),('war_zone',1849)]:
 name=uv_map(o,'v048b fixed path registration '+label,f);uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map=name;tex=nt.nodes.new('ShaderNodeTexImage');tex.image=image;tex.extension='EXTEND';nt.links.new(uv.outputs[0],tex.inputs[0]);sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs[0],sep.inputs[0]);fac=mul(nt,ramp(nt,sep.outputs[0],-.24,-.08,0,1),ramp(nt,sep.outputs[0],1.08,1.24,1,0));fac=mul(nt,fac,ramp(nt,sep.outputs[1],.14,.175,0,1));fac=mul(nt,fac,ramp(nt,sep.outputs[1],.240,.269,1,0));mix=nt.nodes.new('ShaderNodeMixRGB');mix.name='v048b | '+label+' earth-only spatial join';nt.links.new(fac,mix.inputs[0]);nt.links.new(base,mix.inputs[1]);nt.links.new(tex.outputs[0],mix.inputs[2]);base=mix.outputs[0]
nt.links.new(base,em.inputs[0])
# Reduce the too-broad first-pass lift while retaining a stationary cool sky opening.
for m in bpy.data.materials:
 if m.name.startswith('v048 | storm clearing'):
  for n in m.node_tree.nodes:
   if n.type=='MAP_RANGE' and abs(n.inputs['To Min'].default_value-.24)<.001:n.inputs['To Min'].default_value=.15
S['v048b_revision']='Rejected flat geometric banks, bold chips and flat ruin mass hidden; original painted soil reused, earth-only path RGB joins, native fine architectural lines retained.'
S.render.resolution_percentage=100;S.eevee.taa_render_samples=32;S.frame_set(1849);bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
(O/'revision_v048b.json').write_text(json.dumps({'native':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'hidden_failed_first_pass_objects':len(hidden),'reused_painting':str(R/'sets/refinement_v047/Foreground_Bank_Paintover_v047.png'),'paint_sampling_limit':'Only source texture v<0.269; original painted characters are above this band and are not sampled.','new_generated_masonry':'Inline candidate generated, not consumed; no local output file supplied by tool.','reason':'Native preview showed flat vector shapes out of keeping with painted source.','source_scope':'No source or character edits'},indent=2))
(O/'after_v048b').mkdir(exist_ok=True);S.render.resolution_percentage=25;S.eevee.taa_render_samples=16
for label,f in [('peaceful',241),('transition',1201),('war_zone',1849)]:
 S.frame_set(f);S.render.filepath=str(O/'after_v048b'/f'{label}_{f}_960.png');bpy.ops.render.render(write_still=True,scene=S.name);print('PAINTED_PREVIEW',label,flush=True)
