"""Exact isolated alpha of the existing near oak suppresses the drawing reveal."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'work/first_danger_conform_v065';build=json.loads((O/'evidence/BUILD.json').read_text());S=Path(build['native']);N=O/'native/WTSC_First_Danger_Conformed_v065f.blend';assert not N.exists()
bpy.ops.wm.open_mainfile(filepath=str(S),load_ui=False,use_scripts=False)
w=bpy.data.scenes['WTSC_FIRST_DANGER_WORLD_v065'];tree=bpy.data.objects['v030 | High crown foreground oak 1']
oc=bpy.data.scenes.new('V065 | actual foreground oak alpha');oc.collection.objects.link(tree);oc.collection.objects.link(w.camera);oc.camera=w.camera;oc.world=w.world;oc.render.engine='BLENDER_EEVEE';oc.render.film_transparent=True;oc.render.resolution_x=3840;oc.render.resolution_y=2160;oc.render.resolution_percentage=100;oc.render.fps=24;oc.frame_start=913;oc.frame_end=1080;oc.render.threads_mode='FIXED';oc.render.threads=2;oc.eevee.taa_render_samples=32;oc.view_settings.view_transform='Standard';oc.view_settings.look='None';oc.render.dither_intensity=0
ont=bpy.data.node_groups.new('V065 | native near-oak alpha export','CompositorNodeTree');ont.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor');oc.compositing_node_group=ont;rl=ont.nodes.new('CompositorNodeRLayers');rl.scene=oc;out=ont.nodes.new('NodeGroupOutput');ont.links.new(rl.outputs['Alpha'],out.inputs[0])
nt=w.compositing_node_group;reveal=nt.nodes['V065 | color-exact drawing reveal'];actor=reveal.inputs[0].links[0].from_socket
fore=nt.nodes.new('CompositorNodeRLayers');fore.name='V065 | actual nearer oak alpha';fore.scene=oc
inverse=nt.nodes.new('ShaderNodeMath');inverse.name='V065 | unoccluded by near illustration';inverse.operation='SUBTRACT';inverse.inputs[0].default_value=1.;nt.links.new(fore.outputs['Alpha'],inverse.inputs[1])
visible=nt.nodes.new('ShaderNodeMath');visible.name='V065 | visible children only | preserve foreground occlusion';visible.operation='MULTIPLY';visible.use_clamp=True;nt.links.new(actor,visible.inputs[0]);nt.links.new(inverse.outputs[0],visible.inputs[1]);nt.links.new(visible.outputs[0],reveal.inputs[0])
w['V065_foreground_fix']='The existing foreground oak is rendered as an isolated alpha pass and subtracts from the actor reveal. This prevents world-tree pixels being revealed in the shape of an occluded child.'
bpy.context.window.scene=w;w.frame_set(981);oc.frame_set(981);bpy.ops.wm.save_as_mainfile(filepath=str(N),compress=True)
build['previous_reveal_native']=str(S);build['native']=str(N);build['native_sha256']=hashlib.sha256(N.read_bytes()).hexdigest();build['foreground_occlusion_scene']=oc.name;build['foreground_object']=tree.name;build['foreground_occlusion_correction']='Exact existing near-oak rendered alpha multiplies down the visible-child reveal. No tree or character artwork changed.'
(O/'evidence/BUILD.json').write_text(json.dumps(build,indent=2));print('V065F_FOREGROUND_OCCLUSION_SAVED',flush=True)
