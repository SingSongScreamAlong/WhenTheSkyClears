from pathlib import Path
import json,numpy as np
from PIL import Image,ImageFilter
O=Path(__file__).resolve().parents[1];S=O/'renders/sequence4K';rows=[]
for g in [913,997]:
 a=np.asarray(Image.open(S/'final'/f'{g:04d}.png').convert('RGB')).astype(np.int16)
 b=np.asarray(Image.open(S/'world'/f'{g:04d}.png').convert('RGB')).astype(np.int16)
 mi=Image.open(S/'matte'/f'{g:04d}.png').convert('L');m=np.asarray(mi)==255
 interior=np.asarray(mi.filter(ImageFilter.MinFilter(7)))==255
 delta=np.abs(a-b);distance=delta.max(axis=2);restricted=np.where(m,distance,0)
 y,x=np.unravel_index(restricted.argmax(),restricted.shape)
 row={'frame':g,'all_opaque_percentiles':np.percentile(delta[m],[50,90,95,99,99.9,100]).tolist(),
      'interior_percentiles':np.percentile(delta[interior],[50,90,95,99,99.9,100]).tolist(),
      'interior_mean_error':float(delta[interior].mean()),'interior_fraction_over2':float((distance[interior]>2).mean()),
      'max_error_location':[int(x),int(y)],'max_pixel_final':a[y,x].tolist(),'max_pixel_world':b[y,x].tolist(),
      'all_opaque_mean_error':float(delta[m].mean())}
 rows.append(row)
 box=(max(0,x-120),max(0,y-120),min(a.shape[1],x+120),min(a.shape[0],y+120))
 canvas=Image.new('RGB',(720,240),'#171c23')
 for k,name in enumerate(['world','final','matte']):
  im=Image.open(S/name/f'{g:04d}.png').convert('RGB').crop(box).resize((240,240));canvas.paste(im,(k*240,0))
 canvas.save(O/f'evidence/visibility_edge_{g}.png')
(O/'evidence/VISIBILITY_EDGE_DIAGNOSIS.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
