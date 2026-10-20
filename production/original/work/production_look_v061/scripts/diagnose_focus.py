import bpy
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\work\production_look_v061')
bpy.ops.wm.open_mainfile(filepath=str(O/'native/WTSC_Physical_Ink_Wash_Forest_v061.blend'),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_INK_WASH_DEPTH_v061'];bpy.context.window.scene=s;s.frame_set(981)
s.camera.data.dof.use_dof=False;s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100;s.render.filepath=str(O/'previews/DIAGNOSTIC_No_DOF_4K.png');bpy.ops.render.render(write_still=True,scene=s.name)
print('NO_DOF_DIAGNOSTIC_READY',flush=True)
