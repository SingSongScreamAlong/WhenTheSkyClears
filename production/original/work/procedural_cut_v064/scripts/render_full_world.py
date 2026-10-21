import subprocess,json,time,hashlib,re
from pathlib import Path
R=Path(r'WTSC_LOCAL_WORKSPACE');O=R/'work/procedural_cut_v064'
B=r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe'
build=json.loads((O/'evidence/FULL_CUT_BUILD.json').read_text());native=Path(build['native']);assert hashlib.sha256(native.read_bytes()).hexdigest()==build['native_sha256']
assert not list((O/'previews/world_frames').glob('*.png')),'Render folder already has frames; investigate before a rerun'
jobs=[]
for start,end in [(1,600),(601,1200),(1201,1800),(1801,2400)]:
 log=O/f'evidence/world_{start:04d}_{end:04d}.log';stream=log.open('w',encoding='utf8')
 p=subprocess.Popen([B,'--background','--factory-startup','--disable-autoexec','--threads','3','--python',str(O/'scripts/render_world_worker.py'),'--',str(start),str(end)],cwd=R,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 jobs.append(dict(p=p,log=log,stream=stream,start=start,end=end,pid=p.pid))
print('V064_WORLD_RENDER_STARTED',[j['pid'] for j in jobs],flush=True)
while True:
 rows=[]
 for j in jobs:
  paths=(O/'previews/world_frames');n=sum(1 for f in range(j['start'],j['end']+1) if (paths/f'{f:04d}.png').is_file())
  code=j['p'].poll();rows.append(dict(pid=j['pid'],start=j['start'],end=j['end'],frames=n,exit=code))
 status=dict(phase='fresh native world rendering',done=sum(r['frames'] for r in rows),total=2400,workers=rows,max_parallel=4,threads_per_worker=3)
 (O/'evidence/RENDER_STATUS.json').write_text(json.dumps(status,indent=2))
 print('V064_RENDER_STATUS',json.dumps(status),flush=True)
 if all(j['p'].poll() is not None for j in jobs):break
 time.sleep(15)
for j in jobs:
 j['stream'].close();assert j['p'].returncode==0,(j['pid'],j['log']);assert 'V064_WORLD_WORKER_COMPLETE' in j['log'].read_text(errors='replace')
assert status['done']==2400
assert hashlib.sha256(native.read_bytes()).hexdigest()==build['native_sha256']
status['phase']='complete';(O/'evidence/RENDER_STATUS.json').write_text(json.dumps(status,indent=2))
print('V064_ALL_WORLD_FRAMES_READY',flush=True)
