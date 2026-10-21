import json,hashlib,subprocess
from pathlib import Path
import numpy as np
import imageio_ffmpeg
O=Path(__file__).resolve().parents[1];B=json.loads((O/'evidence/BUILD.json').read_text());D=json.loads((O/'evidence/DELIVERY.json').read_text());tag=Path(B['native']).stem.split('_')[-1];P=O/'previews';FF=imageio_ffmpeg.get_ffmpeg_exe()
assert D['native_sha256']==B['native_sha256']==hashlib.sha256(Path(B['native']).read_bytes()).hexdigest()
for r in D['outputs']:assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256']
seen=[]
for r in json.loads((O/f'evidence/MOVIE_BATCHES_{tag}.json').read_text()):
 data=json.loads(Path(r['record']).read_text());assert data['native_sha256']==B['native_sha256'] and data['status']=='complete'
 for q in data['rows']:
  g=q['frame'];seen.append(g)
  for branch,key in [('world','world_sha256'),('final','sha256')]:assert hashlib.sha256((O/f'renders/movie_{tag}/{branch}/{g:04d}.png').read_bytes()).hexdigest()==q[key]
assert sorted(seen)==list(range(913,1081))
ns=[0,78,167]
def read(p,w,h):
 expr='+'.join(f'eq(n\\,{n})' for n in ns);r=subprocess.run([FF,'-hide_banner','-v','error','-i',str(p),'-vf',f'select={expr}','-fps_mode','vfr','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],capture_output=True,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 return np.frombuffer(r.stdout,np.uint8).reshape(3,h,w,3)
a=read(D['before']['world'],1280,720);b=read(P/'WTSC_First_Danger_Rough_v069_24fps.mp4',1280,720);c=read(P/'WTSC_First_Danger_Before_After_ROUGH_v069_24fps.mp4',2560,764);d=read(P/'WTSC_First_Danger_Before_After_ACTING_DETAIL_v069_24fps.mp4',1440,460);checks=[]
for i,n in enumerate(ns):
 for name,x,y in [('full left',c[i,44:,:1280],a[i]),('full right',c[i,44:,1280:],b[i]),('detail left',d[i,40:,:720],a[i,150:570,280:1000]),('detail right',d[i,40:,720:],b[i,150:570,280:1000])]:
  err=float(np.abs(x.astype(float)-y.astype(float)).mean());assert err<2.5;checks.append({'frame':913+n,'panel':name,'mean_abs_rgb_codes':err})
assert hashlib.sha256(Path(B['source']).read_bytes()).hexdigest()==B['source_sha256']
(O/'evidence/REVIEW_QA.json').write_text(json.dumps({'passed':True,'native_sha256':B['native_sha256'],'all168_fresh_final_frames_verified':True,'all_movie_hashes_verified':True,'comparison_panel_checks':checks,'fixed_crop_source_pixels':[280,150,720,420],'source_unchanged':True,'artistic_acceptance':False},indent=2));print('V069_MEDIA_READBACK_PASSED',flush=True)
