"""Use the visible matte to reveal original world pixels without alpha-over brightening."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'work/first_danger_conform_v065';build=json.loads((O/'evidence/BUILD.json').read_text());S=Path(build['native']);N=O/'native/WTSC_First_Danger_Conformed_v065e.blend';assert not N.exists()
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False)
w=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v065'];nt=w.compositing_node_group
base=nt.nodes['V065 | inherited title window | background world'];world_image=base.inputs[7].links[0].from_socket;crypto=nt.nodes['V065 | existing children | visible drawing matte']
reveal=nt.nodes.new('ShaderNodeMix');reveal.name='V065 | color-exact drawing reveal';reveal.data_type='RGBA';reveal.blend_type='MIX';reveal.clamp_factor=True;reveal.clamp_result=False
nt.links.new(crypto.outputs['Matte'],reveal.inputs[0]);nt.links.new(base.outputs[2],reveal.inputs[6]);nt.links.new(world_image,reveal.inputs[7])
output=next(n for n in nt.nodes if n.type=='GROUP_OUTPUT');nt.links.new(reveal.outputs[2],output.inputs[0])
reveal.label='Original painted pixels; matte union with title, no double alpha-over'
bpy.context.window.scene=w;w.frame_set(981);bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(N),compress=True)
build['world_render_native']=str(S);build['world_render_native_sha256']=hashlib.sha256(S.read_bytes()).hexdigest();build['native']=str(N);build['native_sha256']=hashlib.sha256(N.read_bytes()).hexdigest()
build['drawing_reveal_refinement']='Mix inherited masked world to the same unmasked world using the visible actor matte. This preserves the original RGB instead of double-compositing translucent paint.'
build['cache_contract']='The in-flight v065d world/matte/glyph renders are unchanged inputs. v065e changes only the final drawing-reveal composite; final compositing may reuse those freshly rendered native pixels, with direct native e agreement checked.'
(O/'evidence/BUILD.json').write_text(json.dumps(build,indent=2));print('V065E_COLOR_EXACT_REVEAL_SAVED',flush=True)
Q=O/'evidence/color_exact_probe';Q.mkdir(exist_ok=True)
for sc in [w,bpy.data.scenes['WTSC_FIRST_DANGER_TITLE_v065']]:sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100;sc.render.threads_mode='FIXED';sc.render.threads=2
for n in nt.nodes:
 if n.type=='OUTPUT_FILE':
  n.mute=n.name not in ['V065 | world export','V065 | visible actor matte']
  if not n.mute:n.directory=str(Q);n.file_name=('world_' if n.name=='V065 | world export' else 'matte_')+'####'
w.frame_set(913);bpy.data.scenes['WTSC_FIRST_DANGER_TITLE_v065'].frame_set(913);bpy.context.view_layer.update();w.render.filepath=str(Q/'final.png');bpy.ops.render.render(write_still=True,scene=w.name)
print('V065E_COLOR_EXACT_PROBE_COMPLETE',flush=True)
