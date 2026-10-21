import json,hashlib,subprocess
from pathlib import Path
import numpy as np
import imageio_ffmpeg
O=Path(__file__).resolve().parents[1];D=json.loads((O/'evidence/DELIVERY_E.json').read_text());B=json.loads((O/'evidence/BUILD.json').read_text());F=imageio_ffmpeg.get_ffmpeg_exe();P=O/'previews'
assert D['native_sha256']==B['native_sha256'] and hashlib.sha256(Path(B['native']).read_bytes()).hexdigest()==B['native_sha256']
for q in D['outputs']:assert hashlib.sha256(Path(q['path']).read_bytes()).hexdigest()==q['sha256']
records=json.loads((O/'evidence/MOVIE_BATCHES_E.json').read_text());seen=[]
for r in records:
 data=json.loads(Path(r['record']).read_text());assert data['native_sha256']==B['native_sha256'] and data['status']=='complete'
 for row in data['rows']:
  g=row['frame'];seen.append(g)
  assert hashlib.sha256((O/f'renders/movie_E/world/{g:04d}.png').read_bytes()).hexdigest()==row['world_sha256']
  assert hashlib.sha256((O/f'renders/movie_E/final/{g:04d}.png').read_bytes()).hexdigest()==row['sha256']
assert sorted(seen)==list(range(913,1081))
ns=[0,78,167]
def read(path,width,height):
 expr='+'.join(f'eq(n\\,{n})' for n in ns)
 p=subprocess.run([F,'-hide_banner','-v','error','-i',str(path),'-vf',f'select={expr}','-fps_mode','vfr','-pix_fmt','rgb24','-f','rawvideo','pipe:1'],capture_output=True,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 return np.frombuffer(p.stdout,np.uint8).reshape(len(ns),height,width,3)
a=read(D['before']['world'],1280,720);b=read(P/'WTSC_First_Danger_Rough_v068e_24fps.mp4',1280,720)
c=read(P/'WTSC_First_Danger_Before_After_ROUGH_v068e_24fps.mp4',2560,764)
e=read(P/'WTSC_First_Danger_Before_After_ACTING_DETAIL_v068e_24fps.mp4',1440,460)
checks=[]
for i,n in enumerate(ns):
 for name,x,y in [('full left',c[i,44:,:1280],a[i]),('full right',c[i,44:,1280:],b[i]),('detail left',e[i,40:,:720],a[i,150:570,280:1000]),('detail right',e[i,40:,720:],b[i,150:570,280:1000])]:
  err=float(np.abs(x.astype(float)-y.astype(float)).mean());assert err<2.5
  checks.append({'production_frame':913+n,'panel':name,'mean_abs_rgb_codes':err})
assert hashlib.sha256(Path(B['source']).read_bytes()).hexdigest()==B['source_sha256']
(O/'evidence/REVIEW_QA_E.json').write_text(json.dumps({'passed':True,'native_sha256':B['native_sha256'],'fresh_final_e_frames':168,'all_render_hashes_verified':True,'video_hashes_verified':True,'comparison_panel_readback':checks,'detail_crop_source_pixels':[280,150,720,420],'detail_crop_same_for_both_panels_and_all_frames':True,'scope':'Seven-second rough review only. No artistic acceptance or full-film integration.'},indent=2))
print('V068_E_MEDIA_READBACK_PASSED',flush=True)
