import json,time,hashlib
from pathlib import Path
O=Path(r'WTSC_LOCAL_WORKSPACE\work\procedural_cut_v064')
b=json.loads((O/'evidence/FULL_CUT_BUILD.json').read_text());ranges=[(1,600),(601,1200),(1201,1800),(1801,2400)]
while True:
 rows=[]
 for start,end in ranges:
  proof=O/f'evidence/world_worker_{start:04d}_{end:04d}.json'
  count=sum((O/f'previews/world_frames/{f:04d}.png').exists() for f in range(start,end+1))
  complete=proof.exists()
  if complete:
   data=json.loads(proof.read_text());assert data['native_sha256']==b['native_sha256'];assert len(data['frames'])==600
  rows.append(dict(start=start,end=end,frames=count,proof_complete=complete))
 status=dict(phase='fresh native world rendering with verified resume',native_sha256=b['native_sha256'],done=sum(r['frames'] for r in rows),total=2400,workers=rows,numeric_precision_policy='Native RNA tolerance1.1e-4 measured in FLOAT_DRIVER_PRECISION.json; valid same-native frames retained')
 (O/'evidence/RENDER_STATUS.json').write_text(json.dumps(status,indent=2));print('V064_RENDER_STATUS',json.dumps(status),flush=True)
 if all(r['proof_complete'] for r in rows):break
 time.sleep(15)
assert status['done']==2400;assert hashlib.sha256(Path(b['native']).read_bytes()).hexdigest()==b['native_sha256']
status['phase']='complete';(O/'evidence/RENDER_STATUS.json').write_text(json.dumps(status,indent=2))
print('V064_ALL_WORLD_FRAMES_READY',flush=True)
