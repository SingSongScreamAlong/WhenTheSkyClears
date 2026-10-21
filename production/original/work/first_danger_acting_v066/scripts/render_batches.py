import subprocess,json,concurrent.futures,time
from pathlib import Path
O=Path(__file__).resolve().parents[1];R=O.parents[1]
BLENDER=Path(r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe')
jobs=[(a,min(a+23,1080)) for a in range(913,1081,24)]
def work(job):
 a,b=job;log=O/f'evidence/movie_{a}_{b}.log'
 with log.open('w',encoding='utf-8') as f:
  p=subprocess.run([str(BLENDER),'--background','--factory-startup','--disable-autoexec','--threads','2','--python',str(O/'scripts/render_review.py'),'--','movie',str(a),str(b)],cwd=R,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 record=O/f'evidence/RENDER_movie_{a}_{b}.json'
 data=json.loads(record.read_text()) if record.exists() else {}
 ok=p.returncode==0 and data.get('status')=='complete' and data.get('completed')==b-a+1
 print('BATCH',a,b,'COMPLETE' if ok else 'FAILED',flush=True)
 return {'range':[a,b],'returncode':p.returncode,'passed':ok,'record':str(record),'log':str(log)}
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for f in concurrent.futures.as_completed([pool.submit(work,j) for j in jobs]):
  rows.append(f.result());(O/'evidence/MOVIE_BATCHES.json').write_text(json.dumps(rows,indent=2))
assert len(rows)==7 and all(r['passed'] for r in rows),'Inspect failed ranges before recovery'
print('V066_ALL_168_MOVIE_FRAMES_COMPLETE',flush=True)
