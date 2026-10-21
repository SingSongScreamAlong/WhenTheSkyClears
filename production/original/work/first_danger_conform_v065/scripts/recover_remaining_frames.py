import subprocess,json,hashlib,concurrent.futures
from pathlib import Path
from PIL import Image
O=Path(__file__).resolve().parents[1];R=O.parents[1];B=Path(r'WTSC_LOCAL_USER\AppData\Local\Programs\Blender\blender-5.2.2-windows-x64\blender.exe');build=json.loads((O/'evidence/BUILD.json').read_text());source=Path(build['world_render_native']);assert hashlib.sha256(source.read_bytes()).hexdigest()==build['world_render_native_sha256']
prior=[]
for start,end in [(913,996),(997,1080)]:
 p=json.loads((O/f'evidence/RENDER_MOVIE_{start}_{end}_PROGRESS.json').read_text())
 for row in p['rows']:
  g=row['frame'];assert hashlib.sha256((O/f'renders/sequence4K/final/{g:04d}.png').read_bytes()).hexdigest()==row['sha256']
  for folder in ['world','inherited','matte','glyph','final']:
   with Image.open(O/f'renders/sequence4K/{folder}/{g:04d}.png') as image:assert image.size==(3840,2160);image.verify()
  prior.append(g)
assert sorted(prior)==list(range(913,957))+list(range(997,1040)),prior
chunks=[(957,972),(1040,1055),(973,988),(1056,1071),(989,996),(1072,1080)]
for a,b in chunks:assert not any((O/f'renders/sequence4K/final/{g:04d}.png').exists() for g in range(a,b+1)),(a,b,'Inspect uncertain frame before any replay')
record={'world_native':str(source),'world_native_sha256':build['world_render_native_sha256'],'original_worker_returncodes':[1,1],'native_failure':'EXCEPTION_ACCESS_VIOLATION in GPU_texture_extend_mode / VolumeModule / DRW_render_gpencil','verified_completed_frames':sorted(prior),'fresh_nonoverlapping_chunks':chunks,'maximum_frames_per_fresh_process':16,'completed_chunks':[]}
(O/'evidence/RENDER_RECOVERY.json').write_text(json.dumps(record,indent=2));print('VERIFIED_COMPLETED_UHD_FRAMES',len(prior),flush=True)
def job(pair):
 a,b=pair;log=O/f'evidence/recovery_{a}_{b}.log'
 with log.open('w',encoding='utf8') as stream:
  done=subprocess.run([str(B),'--background','--factory-startup','--disable-autoexec','--python-exit-code','1','--threads','2','--python',str(O/'scripts/render_candidate.py'),'--','movie',str(a),str(b),'--world-source'],cwd=R,stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
 assert done.returncode==0,(a,b,done.returncode,str(log))
 result=json.loads((O/f'evidence/RENDER_MOVIE_{a}_{b}_COMPLETE.json').read_text());assert result['native_sha256']==build['world_render_native_sha256'] and result['frames']==b-a+1
 print('FRESH_UHD_BATCH_COMPLETE',a,b,flush=True);return pair
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
 for pair in executor.map(job,chunks):
  record['completed_chunks'].append(pair);(O/'evidence/RENDER_RECOVERY.json').write_text(json.dumps(record,indent=2))
record['all_remaining_frames_completed']=True;(O/'evidence/RENDER_RECOVERY.json').write_text(json.dumps(record,indent=2));print('UHD_RECOVERY_COMPLETE',flush=True)
