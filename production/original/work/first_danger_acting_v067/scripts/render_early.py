import subprocess,json,concurrent.futures
from pathlib import Path
O=Path(__file__).resolve().parents[1];R=O.parents[1];EXE=r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe'
def work(job):
 a,b=job
 with (O/f'evidence/early_E_{a}_{b}.log').open('w') as log:
  p=subprocess.run([EXE,'--background','--factory-startup','--disable-autoexec','--threads','2','--python',str(O/'scripts/render_review.py'),'--','early',str(a),str(b)],cwd=R,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 d=json.loads((O/f'evidence/RENDER_early_C_{a}_{b}.json').read_text());assert p.returncode==0 and d['status']=='complete' and d['completed']==b-a+1
 print('STABLE_BEND_RANGE',a,b,'COMPLETE',flush=True);return {'range':[a,b],'native_sha256':d['native_sha256'],'passed':True}
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for f in concurrent.futures.as_completed([pool.submit(work,x) for x in [(913,936),(937,960),(961,983)]]):
  rows.append(f.result());(O/'evidence/EARLY_BATCHES_E.json').write_text(json.dumps(rows,indent=2))
print('V067E_EARLY_71_FRAMES_COMPLETE',flush=True)
