from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np,json
P=Path(__file__).resolve().parents[1];data=json.loads((P/'evidence/build_drawn.json').read_text());sx,sy=data['source_contact_pixel'];ppm=205.1
fg=np.asarray(Image.open(P.parent/'benchmark_v002/assets/Native_Foreground_Alpha_1080_v002.png').convert('RGBA'))[:,:,3]/255
di=Image.open(P.parent/'blast_refinement_v006/assets/Native_Depth_Alpha_Y10_v006.png').convert('RGBA');dep=np.asarray(di)[:,:,3]/255
combo=np.maximum(fg,dep);rows=[]
for v in data['debris']:
    if v['piece'] not in [0,2,4,5]:continue
    shape=next(q for q in data['drawings'] if f"landing{v['piece']} B split" in q['object']);x0,z0,x1,z1=shape['bounds'];x0,x1=round(sx+x0*ppm),round(sx+x1*ppm);y0,y1=round(sy-z1*ppm),round(sy-z0*ppm)
    rows.append({'piece':v['piece'],'pixel_bounds':[x0,y0,x1,y1],'foreground_mean_holdout':float(fg[y0:y1+1,x0:x1+1].mean()),'depth_mean_holdout':float(dep[y0:y1+1,x0:x1+1].mean()),'combined_open_fraction':float((combo[y0:y1+1,x0:x1+1]<.5).mean()),'depth_alpha_at_top_center':float(dep[y0,(x0+x1)//2])})
(P/'evidence/contact_mask_audit.json').write_text(json.dumps({'assumed_depth_channel':'Alpha; verify compositor actual node uses alpha','events':rows},indent=2));print(json.dumps(rows))
rgb=np.stack([fg,dep,combo],axis=2);im=Image.fromarray((rgb*255).astype('uint8'));im=im.crop((1230,650,1840,805)).resize((1220,310));d=ImageDraw.Draw(im);d.text((10,10),'Red foreground | Green depth | Blue combined',fill=(255,255,255));im.save(P/'evidence/Contact_Masks_Diagnostic.png')
