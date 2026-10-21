import subprocess,sys
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\work\production_look_v061');B=r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe'
with (O/'evidence/fix_focus.log').open('w') as log:
 subprocess.run([B,'--background','--factory-startup','--disable-autoexec','--python',str(O/'scripts/fix_transparent_focus.py')],stdout=log,stderr=subprocess.STDOUT,check=True)
with (O/'evidence/final_native_validation.log').open('w') as log:
 subprocess.run([B,'--background','--factory-startup','--disable-autoexec','--python',str(O/'scripts/validate_flat_stage_v061.py'),'--','--reference',str(O/'reference/PRESERVED_v060.blend'),'--target',str(O/'native/WTSC_Physical_Ink_Wash_Forest_v061.blend'),'--scene','WTSC_INK_WASH_DEPTH_v061','--report',str(O/'evidence/FLAT_STAGE_NATIVE_VALIDATION.json')],stdout=log,stderr=subprocess.STDOUT,check=True)
subprocess.run([sys.executable,str(O/'scripts/render_and_package.py')],check=True)
print('V061_FOCUS_FIXED_REVALIDATED_AND_DELIVERED',flush=True)
