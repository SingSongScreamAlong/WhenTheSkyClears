import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).parent;SRC=O/'WTSC_Painted_Foreground_Continuity_v058c.blend';OUT=O/'WTSC_World_Foreground_Development_v058d.blend';assert not OUT.exists()
bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False);s=bpy.data.scenes['WTSC_PAINTED_FOREGROUND_v058c_DEVELOPMENT'];bpy.context.window.scene=s
m=s.objects['v020 | Walking path | continuous blended paint'].data.materials[0];m.name='v058d | continuous painterly soil | earth-only source';nt=m.node_tree
linear=nt.nodes['v058c | MULTIPLY_ADD'];linear.inputs[2].default_value=.10
limit=nt.nodes.new('ShaderNodeMath');limit.name='v058d | hard source exclusion of all painted people';limit.operation='MINIMUM';limit.inputs[1].default_value=.245;nt.links.new(linear.outputs[0],limit.inputs[0])
targets=[]
for n in nt.nodes:
 if n.type=='TEX_IMAGE' and n.image and n.image.name=='Foreground_Bank_Paintover_v047.png' and n.inputs[0].is_linked:
  co=n.inputs[0].links[0].from_node
  if co.type=='COMBXYZ' and any(l.from_node.name.startswith('v058a') for l in co.inputs[0].links):nt.links.new(limit.outputs[0],co.inputs[1]);targets.append(n.name)
assert len(targets)==2
# Keep original graph nodes plus reachable additions; discard failed study wiring.
old=json.loads((O/'FOREGROUND_INSPECTION.json').read_text())[0]['materials'][0]['nodes'];original_names={n['name'] for n in old}
seen=set()
def walk(n):
 if n.name in seen:return
 seen.add(n.name)
 for sock in n.inputs:
  for l in sock.links:walk(l.from_node)
for n in nt.nodes:
 if n.type=='OUTPUT_MATERIAL':walk(n)
removed=[]
for n in list(nt.nodes):
 if n.name not in original_names and n.name not in seen:removed.append(n.name);nt.nodes.remove(n)
for co in list(bpy.data.collections):
 if co.name.startswith('v058a | irregular rooted'):bpy.data.collections.remove(co)
for me in list(bpy.data.meshes):
 if me.name.startswith('v058a rooted leaves') and me.users==0:bpy.data.meshes.remove(me)
for ma in list(bpy.data.materials):
 if ma.name.startswith('v058a | plant ink') and ma.users==0:bpy.data.materials.remove(ma)
s.name='WTSC_WORLD_FOREGROUND_v058d';s['v058d_scope']='WORLD DEVELOPMENT. Continuous painted foreground soil replacing mirrored decorative leaf border. Original art reused through fixed world coordinates; original path silhouette/contact lane, source lighting, v057 school, cameras, title, audio and held character data retained.'
s['v058d_limits']='Not whole-film minimum acceptance: held full-film children and incomplete paired acting remain; architecture remains largely layered paintings.'
s.frame_set(1537);s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2;s.eevee.taa_render_samples=32;s.render.dither_intensity=0;s.render.use_sequencer=False;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT),compress=True)
(O/'BUILD_v058d.json').write_text(json.dumps({'native':str(OUT),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'source_paint':'Foreground_Bank_Paintover_v047.png','image_dimensions':list(bpy.data.images['Foreground_Bank_Paintover_v047.png'].size),'source_v_max':.245,'all_characters_in_source_excluded_by_texture_coordinate_limit':True,'new_failed_meshes_removed':True,'unused_study_nodes_removed':removed,'mapping':'fixed world geometry position; overlapping UV samples with zero weight at each discontinuity; no mirrored U','new_raster_files':0,'source_file_changes':0},indent=2))
s.render.resolution_x=1280;s.render.resolution_y=720
for f in [241,601,961,1201,1537,1849,2161,2377]:
 s.frame_set(f);s.render.filepath=str(O/f'AFTER_D_{f:04d}.png');bpy.ops.render.render(write_still=True,scene=s.name);print('V058D_FRAME',f,flush=True)
print('V058D_READY',flush=True)
