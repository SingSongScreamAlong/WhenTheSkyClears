import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
O=Path(__file__).resolve().parents[1];B=json.loads((O/'evidence/BUILD.json').read_text());bpy.ops.wm.open_mainfile(filepath=B['native'],load_ui=False,use_scripts=False);s=bpy.data.scenes[B['world_scene']];bpy.context.window.scene=s;s.frame_set(957);bpy.context.view_layer.update()
for head in B['head_changes']:
 w=head['who'];r=bpy.data.objects['V044 '+w+' | estimated joint centres'];o=next(o for o in s.objects if o.parent==r and o.get('proportion_role')=='head' and not o.hide_render);eye=Vector(head['eye_rest_coordinate']);to_rig=r.matrix_world.inverted()@o.matrix_world;world=r.matrix_world@r.pose.bones['head'].matrix@r.data.bones['head'].matrix_local.inverted()@to_rig@eye;p=world_to_camera_view(s,s.camera,world)
 print(w,'EYE_PIXEL_720',[p.x*1280,(1-p.y)*720],'REST',list(eye),flush=True)
