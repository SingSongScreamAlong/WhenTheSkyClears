import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
P=Path(__file__).resolve().parents[1];OLD=P.parent/'preferred_walk_consistent_footwear_v033';DIAG=P.parent/'readability_working_view_v034';out={'scope':'Raster overlap and charcoal values; not an artistic rating','far_F20_masks':{},'near_hand_values':[]}
for variant in ['SOURCE','ALL']:
 r={}
 for name in ['FULL','NO_FAR_TROUSER','NO_NEAR_TROUSER','NO_COAT','NO_COAT_OR_NEAR_TROUSER','ISOLATED']:
  a=np.array(Image.open(P/'previews'/('OVERLAP_'+variant)/(name+'.png')).convert('RGB')).astype(float);mask=(a[:,:,1]>a[:,:,0]+80)&(a[:,:,1]>a[:,:,2]+80)&(a[:,:,1]>160);r[name]=int(mask.sum())
 out['far_F20_masks'][variant]=r
for view in ['CLOSE','SHOT']:
 for f in [11,20,27]:
  a=np.array(Image.open(DIAG/'previews'/('ID_FULL_'+view)/f'{f:04d}.png').convert('RGB')).astype(float);m=(a[:,:,0]>a[:,:,1]+45)&(a[:,:,0]>a[:,:,2]+10)&(a[:,:,0]>110);ring=np.array(Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.MaxFilter(5)))>0;ring &=~m;r={'view':view,'frame':f}
  for name,file in [('SOURCE',OLD/'previews'/view/f'{f:04d}.png'),('ALL',P/'previews'/('ALL_'+view)/f'{f:04d}.png')]:
   im=np.array(Image.open(file).convert('RGB')).mean(2);cloth=ring&(im<130);r[name]={'hand_median_RGB_luma':float(np.median(im[m])),'adjacent_garment_median_RGB_luma':float(np.median(im[cloth])),'garment_ring_fraction':float(cloth.sum()/max(1,ring.sum()))}
  out['near_hand_values'].append(r)
out['far_hand_interpretation']='Compare each ablation against isolated count. Removing far trousers alone can still leave other independent occluders. Near-side coat/leg overlap is intentionally retained; no global front-layer hand override.'
(P/'evidence/STILL_READABILITY_MEASUREMENTS.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
