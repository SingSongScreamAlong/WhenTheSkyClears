import time,subprocess,sys,json
from pathlib import Path
O=Path(__file__).resolve().parents[1];began=time.monotonic();last=-1
required=[O/'evidence/FINAL_COMPOSITE_COMPLETE.json',O/'evidence/RENDER_RECOVERY.json']
def ready():
 return all(p.exists() for p in required) and json.loads(required[1].read_text()).get('all_remaining_frames_completed',False)
while not ready():
 assert time.monotonic()-began<2400,'Bounded source/composite completion wait expired'
 p=O/'evidence/FINAL_COMPOSITE_PROGRESS.json'
 if p.exists():
  try:
   n=json.loads(p.read_text())['completed']
   if n//12!=last//12:print('FINAL_RENDER_PROGRESS',n,168,flush=True);last=n
  except json.JSONDecodeError:pass
 time.sleep(1)
for name in ['assemble_render_record.py','package_review.py']:
 done=subprocess.run([sys.executable,str(O/'scripts'/name)],cwd=O.parents[1])
 assert done.returncode==0,(name,done.returncode)
print('V065_RENDERED_MOVIES_READY_FOR_VISUAL_REVIEW',flush=True)
