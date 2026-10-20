import bpy,json,hashlib,shutil
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\work\production_look_v061');native=O/'native/WTSC_Physical_Ink_Wash_Forest_v061.blend';A=O/'reference/pre_focus_correction';A.mkdir(exist_ok=True)
for p in [native,O/'evidence/PRODUCTION_LOOK_BUILD.json',O/'evidence/FLAT_STAGE_NATIVE_VALIDATION.json',O/'evidence/NATIVE_SEQUENCE_RENDER.json',O/'evidence/ENCODED_REVIEW_VALIDATION.json']:
 if p.exists():shutil.copy2(p,A/p.name)
P=O/'previews'
for p in list(P.glob('WTSC_Ink_Wash*'))+list(P.glob('Native_*'))+list(P.glob('Decoded_Review*'))+list(P.glob('Chronological_Review*'))+list(P.glob('physical_v061*'))+[P/'Lateral_Depth_Witness_v061.png']:
 if p.exists():shutil.copy2(p,A/p.name)
if (P/'frames').exists():shutil.move(str(P/'frames'),str(A/'frames'))
before=hashlib.sha256(native.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
s=bpy.data.scenes['WTSC_INK_WASH_DEPTH_v061'];bpy.context.window.scene=s;s.frame_set(981)
changed={};seen=set()
for ob in s.objects:
 for slot in ob.material_slots:
  m=slot.material
  if m and m.get('V061_actual_light_wash') and m.as_pointer() not in seen:
   seen.add(m.as_pointer());changed[m.name]={'old':m.surface_render_method,'new':'DITHERED'};m.surface_render_method='DITHERED';m['V061_depth_of_field_fix']='DITHERED supplies correct illustrated alpha depth; BLENDED rendered faces/hands out of focus.'
note=bpy.data.texts.get('START HERE | V061 | full production direction')
if note:note.clear();note.write((O/'START_HERE_v061.txt').read_text())
s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
r={'source_native_sha256':before,'fixed_native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'diagnosis':'EEVEE blended transparent illustration objects blur under native DOF; DITHERED restores correct alpha depth and sharpness. Verified with original DOF, noDOF and DITHERED+DOF4K renders.','changes':changed,'source_raster_UVs_geometry_actions_untouched':True,'original_data_materials_untouched':True,'camera_DOF_retained':s.camera.data.dof.use_dof,'camera_fstop':s.camera.data.dof.aperture_fstop,'archived_previous_delivery':str(A)}
(O/'evidence/TRANSPARENT_FOCUS_FIX.json').write_text(json.dumps(r,indent=2))
for g in [937,981,1056]:
 s.frame_set(g);s.render.resolution_x=1280;s.render.resolution_y=720;s.render.filepath=str(P/('physical_v061_%04d.png'%g));bpy.ops.render.render(write_still=True,scene=s.name)
print('V061_TRANSPARENT_FOCUS_FIXED',flush=True)
