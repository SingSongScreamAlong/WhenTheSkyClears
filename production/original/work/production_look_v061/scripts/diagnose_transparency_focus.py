import bpy,json
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\work\production_look_v061')
bpy.ops.wm.open_mainfile(filepath=str(O/'native/WTSC_Physical_Ink_Wash_Forest_v061.blend'),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_INK_WASH_DEPTH_v061'];bpy.context.window.scene=s;s.frame_set(981);changed={}
for ob in s.objects:
 for slot in ob.material_slots:
  mat=slot.material
  if mat and mat.get('V061_actual_light_wash'):
   changed[mat.name]=mat.surface_render_method;mat.surface_render_method='DITHERED'
s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.filepath=str(O/'previews/DIAGNOSTIC_Dithered_DOF_4K.png');bpy.ops.render.render(write_still=True,scene=s.name)
(O/'evidence/TRANSPARENCY_FOCUS_DIAGNOSTIC.json').write_text(json.dumps({'original_methods':changed,'test':'Copied actor overrides DITHERED, original DOF true/f5.6, all else unchanged; no native save'},indent=2));print('DITHERED_DOF_DIAGNOSTIC_READY',flush=True)
