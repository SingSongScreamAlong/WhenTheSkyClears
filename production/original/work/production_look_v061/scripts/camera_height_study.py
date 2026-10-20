import bpy
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\work\production_look_v061')
bpy.ops.wm.open_mainfile(filepath=str(O/'reference/first_physical_blocking/WTSC_Physical_Ink_Wash_Forest_v061.blend'),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_INK_WASH_DEPTH_v061'];bpy.context.window.scene=s;cam=s.camera
cam.data.shift_y+=1.3*cam.data.lens/(cam.data.sensor_width*15.64)
for l in cam.animation_data.action.layers:
 for st in l.strips:
  for bag in st.channelbags:
   for fc in bag.fcurves:
    if fc.data_path=='location' and fc.array_index==2:
     for k in fc.keyframe_points:
      k.co.y-=1.3;k.handle_left.y-=1.3;k.handle_right.y-=1.3
     fc.update()
s.frame_set(981);s.render.resolution_x=1280;s.render.resolution_y=720;s.render.filepath=str(O/'previews/camera_height_study.png');bpy.ops.render.render(write_still=True,scene=s.name)
print('CAMERA_STUDY_READY')
