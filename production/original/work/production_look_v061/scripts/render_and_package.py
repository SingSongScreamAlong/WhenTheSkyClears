import subprocess,sys
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\work\production_look_v061');B=r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe'
with (O/'evidence/render_sequence.log').open('w') as log:
 subprocess.run([B,'--background','--factory-startup','--disable-autoexec','--python',str(O/'scripts/render_production_sequence.py')],stdout=log,stderr=subprocess.STDOUT,check=True)
with (O/'evidence/package_review.log').open('w') as log:
 subprocess.run([sys.executable,str(O/'scripts/package_production_review.py')],stdout=log,stderr=subprocess.STDOUT,check=True)
print('V061_RENDER_AND_PACKAGE_COMPLETE',flush=True)
