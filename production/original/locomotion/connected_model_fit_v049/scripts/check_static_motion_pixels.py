import json,hashlib
from pathlib import Path
from PIL import Image,ImageChops
import numpy as np
P=Path(__file__).resolve().parents[1];out=[]
for f in [1,5,9]:
 a=P/'previews'/('AFTER_WALK_F%02d.png'%f);b=P/'previews/frames_V049'/('FRAME_%04d.png'%f)
 ia=Image.open(a).convert('RGB');ib=Image.open(b).convert('RGB');ar=np.array(ia).astype(int);br=np.array(ib).astype(int);diff=np.abs(ar-br)
 out.append({'frame':f,'same_png_bytes':a.read_bytes()==b.read_bytes(),'size_a':list(ia.size),'size_b':list(ib.size),'pixels_identical':bool(np.all(diff==0)),'max_channel_delta':int(diff.max()),'mean_channel_delta':float(diff.mean()),'changed_pixels':int(np.any(diff>0,axis=2).sum()),'diff_bounds':ImageChops.difference(ia,ib).getbbox(),'static_info':ia.info,'motion_info':ib.info})
for r in out:
 for k in ['static_info','motion_info']:r[k]={n:v for n,v in r[k].items() if n in ['Date','Time','Frame','Camera','Scene','RenderTime']}
print(json.dumps(out,indent=2));(P/'evidence/STATIC_MOTION_PIXEL_COMPARISON.json').write_text(json.dumps(out,indent=2))
