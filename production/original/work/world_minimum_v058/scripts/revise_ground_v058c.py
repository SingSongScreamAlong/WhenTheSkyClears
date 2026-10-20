import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).parent;SRC=O/'WTSC_Continuous_Painted_Path_v058b.blend';OUT=O/'WTSC_Painted_Foreground_Continuity_v058c.blend';assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);s=bpy.data.scenes['WTSC_CONTINUOUS_PAINTED_PATH_v058b_STUDY'];bpy.context.window.scene=s
m=s.objects['v020 | Walking path | continuous blended paint'].data.materials[0];m.name='v058c | correctly proportioned original painted soil';nt=m.node_tree
def calc(op,a,b,c=0):
 n=nt.nodes.new('ShaderNodeMath');n.operation=op;n.name='v058c | '+op
 for i,sv in enumerate([a,b,c]):
  if isinstance(sv,(int,float)):n.inputs[i].default_value=sv
  else:nt.links.new(sv,n.inputs[i])
 return n.outputs[0]
# Correct physical aspect: full owned 1672x941 paint spans 6.5016m by 3.659m.
linv=calc('MULTIPLY_ADD',nt.nodes['Separate XYZ'].outputs['Z'],1/3.65715,.1542)
nt.links.new(linv,nt.nodes['v058a | MULTIPLY_ADD'].outputs[0].links[0].to_socket) if False else None
for n in nt.nodes:
 if n.type=='TEX_IMAGE' and n.image and n.image.name=='Foreground_Bank_Paintover_v047.png' and n.inputs[0].is_linked:
  co=n.inputs[0].links[0].from_node
  if co.type=='COMBXYZ' and any(l.from_node.name.startswith('v058a') for l in co.inputs[0].links):nt.links.new(linv,co.inputs[1])
nt.nodes['v058a | MULTIPLY_ADD'].inputs[1].default_value=1/6.5016
nt.nodes['v058a | foreground-only spatial mask'].inputs[1].default_value=.38
nt.nodes['v058a | foreground-only spatial mask'].inputs[2].default_value=.56
hs=nt.nodes['Hue/Saturation/Value'];nt.links.new(nt.nodes['v058a | replace mirrored lower leaf border only'].outputs[0],hs.inputs['Color'])
# Restore original upper source input, bypassing the failed horizontally stretched B study.
nt.links.new(nt.nodes['Image Texture.001'].outputs['Color'],nt.nodes['Mix (Legacy).001'].inputs[2])
for ob in list(bpy.data.objects):
 if ob.name.startswith('v058a | rooted plant'):bpy.data.objects.remove(ob,do_unlink=True)
s.name='WTSC_PAINTED_FOREGROUND_v058c_DEVELOPMENT';s['v058c_revision']='Reject A compressed white soil edge and B stretched leaves. Source-v047 painted foreground sampled at original physical aspect, linear vertical registration and overlapping fixed world UV panels. No new raster edits. Original upper path, contact lane, alpha, lighting and character data retained.'
s.frame_set(1537);s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'BUILD_v058c.json').write_text(json.dumps({'native':str(OUT),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'source_paint':'Foreground_Bank_Paintover_v047.png','mapping':{'u_world_scale':1/6.5016,'v_world_scale':1/3.65715,'v_bias':.1542,'mask_full_below_world_z':.38,'mask_zero_above_world_z':.56},'failed_added_plant_meshes_removed':True,'new_raster_files':0},indent=2))
s.render.resolution_x=1280;s.render.resolution_y=720;s.eevee.taa_render_samples=32;s.render.dither_intensity=0;s.render.use_sequencer=False;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG'
for f in [241,1537,2161]:
 s.frame_set(f);s.render.filepath=str(O/f'AFTER_C_{f:04d}.png');bpy.ops.render.render(write_still=True,scene=s.name);print('V058C_FRAME',f,flush=True)
print('V058C_READY',flush=True)
