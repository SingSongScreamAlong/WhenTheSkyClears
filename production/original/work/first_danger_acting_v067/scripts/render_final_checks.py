import subprocess,json
from pathlib import Path
O=Path(__file__).resolve().parents[1];R=O.parents[1];EXE=r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe'
for mode,lo,hi in [('witness',990,1016),('uhd',957,1016)]:
 with (O/f'evidence/render_{mode}_E.log').open('w') as log:
  p=subprocess.run([EXE,'--background','--factory-startup','--disable-autoexec','--threads','2','--python',str(O/'scripts/render_review.py'),'--',mode],cwd=R,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 d=json.loads((O/f'evidence/RENDER_{mode}_C_{lo}_{hi}.json').read_text());assert p.returncode==0 and d['status']=='complete'
 print('FINAL_CHECK',mode,'COMPLETE',flush=True)
