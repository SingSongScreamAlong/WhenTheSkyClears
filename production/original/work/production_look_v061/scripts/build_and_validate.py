import subprocess
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\work\production_look_v061');B=r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe'
with (O/'evidence/build_production_look_third.log').open('w') as log:
 subprocess.run([B,'--background','--factory-startup','--disable-autoexec','--python',str(O/'scripts/build_production_look.py')],stdout=log,stderr=subprocess.STDOUT,check=True)
with (O/'evidence/final_native_validation.log').open('w') as log:
 subprocess.run([B,'--background','--factory-startup','--disable-autoexec','--python',str(O/'scripts/validate_flat_stage_v061.py'),'--','--reference',str(O/'reference/PRESERVED_v060.blend'),'--target',str(O/'native/WTSC_Physical_Ink_Wash_Forest_v061.blend'),'--scene','WTSC_INK_WASH_DEPTH_v061','--report',str(O/'evidence/FLAT_STAGE_NATIVE_VALIDATION.json')],stdout=log,stderr=subprocess.STDOUT,check=True)
print('V061_BUILD_AND_NATIVE_VALIDATION_COMPLETE',flush=True)
