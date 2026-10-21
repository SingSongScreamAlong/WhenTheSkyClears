import json,hashlib,shutil
from pathlib import Path
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parents[1];B=json.loads((O/'evidence/BUILD.json').read_text());early=json.loads((O/'evidence/EARLY_BATCHES_E.json').read_text());old=json.loads((O/'evidence/MOVIE_BATCHES_C.json').read_text());witness=json.loads((O/'evidence/RENDER_witness_C_990_1016.json').read_text())
assert len(early)==3 and all(r['passed'] and r['native_sha256']==B['native_sha256'] for r in early)
assert len(old)==7 and all(r['passed'] for r in old)
for rec in old:
 data=json.loads(Path(rec['record']).read_text());assert data['native_sha256']==B['bend_source_sha256']
assert witness['status']=='complete' and witness['native_sha256']==B['native_sha256']
assert B['late_near_arm_endpoint_max_difference_m']<2e-6
pixel=[]
for branch in ['world','final']:
 for g in [990,1016]:
  a=np.array(Image.open(O/f'renders/movie_C/{branch}/{g:04d}.png')).astype(float);b=np.array(Image.open(O/f'renders/witness_C/{branch}/{g:04d}.png')).astype(float);delta=abs(a-b);mae=float(delta.mean());assert mae<.02,(branch,g,mae)
  pixel.append({'branch':branch,'frame':g,'RGB_mean_absolute_difference':mae,'max_RGB_difference':float(delta.max())})
rows=[]
for branch in ['world','final']:
 dest=O/f'renders/final_review/{branch}';dest.mkdir(parents=True,exist_ok=True)
 for g in range(913,1081):
  src=O/f'renders/{"early_C" if g<984 else "movie_C"}/{branch}/{g:04d}.png';target=dest/f'{g:04d}.png';assert src.exists() and not target.exists()
  with Image.open(src) as im:assert im.size==(1280,720);im.verify()
  shutil.copyfile(src,target);rows.append({'branch':branch,'frame':g,'source':str(src),'native_sha256':B['native_sha256'] if g<984 else B['bend_source_sha256'],'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
(O/'evidence/FINAL_FRAME_PROVENANCE.json').write_text(json.dumps({'fresh_stable_bend_range':[913,983],'unchanged_cached_range':[984,1080],'late_endpoint_max_difference_m':B['late_near_arm_endpoint_max_difference_m'],'fresh_native_pixel_witness':pixel,'rows':rows,'passed':True,'explanation':'Only the early elbow path changed in final native e. Later poses agree within the measured endpoint tolerance; fresh native e images at990/1016 match the cached native d world/title images. Original native pixel caches are retained with hashes rather than rerendered.'},indent=2));print('FINAL_168_FRAMES_ASSEMBLED_WITH_PROVENANCE',flush=True)
