import json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1]
build=json.loads((O/'evidence/BUILD.json').read_text());recovery=json.loads((O/'evidence/RENDER_RECOVERY.json').read_text());assert recovery['all_remaining_frames_completed']
parts=[json.loads((O/f'evidence/RENDER_MOVIE_{start}_{end}_COMPLETE.json').read_text()) for start,end in recovery['fresh_nonoverlapping_chunks']]
old=[json.loads((O/f'evidence/RENDER_MOVIE_{start}_{end}_PROGRESS.json').read_text()) for start,end in [(913,996),(997,1080)]]
rows=sorted([r for p in old+parts for r in p['rows']],key=lambda r:r['frame'])
assert [r['frame'] for r in rows]==list(range(913,1081))
assert len({p['native_sha256'] for p in parts})==1 and all(p['resolution']==[3840,2160] and p['native_unchanged'] for p in parts)
assert all('charcoal_progress' in r and r['world_clock']==r['title_clock']==r['frame'] for r in rows)
native=Path(parts[0]['native']);assert hashlib.sha256(native.read_bytes()).hexdigest()==parts[0]['native_sha256']==build['world_render_native_sha256']
for r in rows:
 assert hashlib.sha256((O/f'renders/sequence4K/final/{r["frame"]:04d}.png').read_bytes()).hexdigest()==r['sha256']
report={'native':str(native),'native_sha256':parts[0]['native_sha256'],'native_unchanged':True,'frames':168,'resolution':[3840,2160],'global_range':[913,1080],'world_clock_and_title_clock_synchronized':True,'recovery':'87 completed native frames independently verified after the two long worker failures; remaining81 rendered in six fresh nonoverlapping batches of at most16frames.','rows':rows}
(O/'evidence/RENDER_MOVIE_COMPLETE.json').write_text(json.dumps(report,indent=2));print('NATIVE_UHD_SEQUENCE_VERIFIED',len(rows),flush=True)
