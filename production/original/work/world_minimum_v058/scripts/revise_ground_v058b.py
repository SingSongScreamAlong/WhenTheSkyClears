import bpy,json,hashlib,math
from pathlib import Path
O=Path(__file__).parent;SRC=O/'WTSC_Rooted_Foreground_Study_v058a.blend';OUT=O/'WTSC_Continuous_Painted_Path_v058b.blend';assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);s=bpy.data.scenes['WTSC_ROOTED_FOREGROUND_v058a_WORLD_STUDY'];bpy.context.window.scene=s
o=s.objects['v020 | Walking path | continuous blended paint'];m=o.data.materials[0];m.name='v058b | non-mirrored painted path';nt=m.node_tree
hs=nt.nodes['Hue/Saturation/Value'];old=nt.nodes['v058a | replace mirrored lower leaf border only'].inputs[1].links[0].from_socket;nt.links.new(old,hs.inputs['Color'])
# Retain original paint vertically and keep original alpha branch exactly intact.
base=nt.nodes['Image Texture.001'];v=nt.nodes['Separate XYZ.001'].outputs['Y'];x=nt.nodes['Separate XYZ'].outputs['X']
def calc(op,a,b=None,c=None):
 n=nt.nodes.new('ShaderNodeMath');n.operation=op;n.name='v058b | '+op
 for i,sv in enumerate([a,b,c]):
  if sv is None:continue
  if isinstance(sv,(int,float)):n.inputs[i].default_value=sv
  else:nt.links.new(sv,n.inputs[i])
 return n.outputs[0]
u=calc('FRACT',calc('MULTIPLY_ADD',x,1/8.8,.137));u2=calc('FRACT',calc('ADD',u,.5));cols=[]
for uu in [u,u2]:
 comb=nt.nodes.new('ShaderNodeCombineXYZ');nt.links.new(uu,comb.inputs[0]);nt.links.new(v,comb.inputs[1]);tex=nt.nodes.new('ShaderNodeTexImage');tex.image=base.image;tex.extension='EXTEND';nt.links.new(comb.outputs[0],tex.inputs[0]);cols.append(tex.outputs['Color'])
weight=calc('MULTIPLY_ADD',calc('COSINE',calc('MULTIPLY',u,2*math.pi)),.5,.5)
blend=nt.nodes.new('ShaderNodeMixRGB');blend.name='v058b | world-fixed overlapping brush panels';nt.links.new(weight,blend.inputs[0]);nt.links.new(cols[0],blend.inputs[1]);nt.links.new(cols[1],blend.inputs[2])
consumers=[link.to_socket for link in base.outputs['Color'].links]
mask=nt.nodes.new('ShaderNodeMapRange');mask.name='v058b | preserve upper path alpha color registration';mask.clamp=True;mask.interpolation_type='SMOOTHERSTEP'
for i,sv in enumerate([.50,.66,1,0],1):mask.inputs[i].default_value=sv
nt.links.new(nt.nodes['Separate XYZ'].outputs['Z'],mask.inputs[0])
lower=nt.nodes.new('ShaderNodeMixRGB');lower.name='v058b | foreground color only';nt.links.new(mask.outputs[0],lower.inputs[0]);nt.links.new(base.outputs['Color'],lower.inputs[1]);nt.links.new(blend.outputs[0],lower.inputs[2])
for dest in consumers:nt.links.new(lower.outputs[0],dest)
# Restore the previous isolated earth-only joins; their source paint stays intact.
for n in nt.nodes:
 if n.name.startswith('v048b |') and 'earth-only spatial join' in n.name:
  # They are bypassed only in this study so the route-wide test stays continuous.
  n.inputs[0].default_value=0
for ob in s.objects:
 if ob.name.startswith('v058a | rooted plant'):ob.hide_render=True
 # Keep failed old needle grass hidden as well; painted rooted foliage is retained.
s.name='WTSC_CONTINUOUS_PAINTED_PATH_v058b_STUDY';s['v058b_review']='Rejected v058a white fringe and flat plant meshes. Preserve original paint registration vertically; replace only mirrored horizontal color sampling. Original alpha branch, firelight and Hue/Saturation animation retained.'
s.frame_set(1537);s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'BUILD_v058b.json').write_text(json.dumps({'native':str(OUT),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'source':str(SRC),'revision':'Reject flat native plants and compressed pale earth band. Original path paint vertical scale restored; nonmirrored overlapping horizontal source panels. Only Color consumers changed, original texture Alpha remains connected.','new_raster_files':0,'new_rendered_native_plants':0},indent=2))
s.render.resolution_x=1280;s.render.resolution_y=720;s.eevee.taa_render_samples=32;s.render.dither_intensity=0;s.render.use_sequencer=False;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG'
for f in [241,601,961,1201,1537,1849,2161,2377]:
 s.frame_set(f);s.render.filepath=str(O/f'AFTER_B_{f:04d}.png');bpy.ops.render.render(write_still=True,scene=s.name);print('V058B_FRAME',f,flush=True)
print('V058B_READY',flush=True)
