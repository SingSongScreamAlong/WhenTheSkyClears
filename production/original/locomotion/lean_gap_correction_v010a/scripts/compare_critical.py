import json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
P=Path(__file__).resolve().parents[1];meta=json.loads((P/'evidence/projected_head_meshes.json').read_text());frames=[1841,1842,1843,1844,1845,1846,1847]
coords=[q for mode in meta.values() for f in frames for head in mode[str(f)].values() for q in head['pixels']]
rect=(math.floor(min(q[0] for q in coords))-14,math.floor(min(q[1] for q in coords))-14,math.ceil(max(q[0] for q in coords))+14,math.ceil(max(q[1] for q in coords))+55);ww=rect[2]-rect[0];hh=rect[3]-rect[1]
scale=2;tilew=ww*scale;tileh=hh*scale;out=Image.new('RGB',(tilew*2,len(frames)*(tileh+25)),(235,231,222));draw=ImageDraw.Draw(out);metrics={}
def mask(head):
 im=Image.new('L',(ww*4,hh*4),0);dr=ImageDraw.Draw(im);pts=[((q[0]-rect[0])*4,(q[1]-rect[1])*4) for q in head['pixels']]
 for face in head['faces']:dr.polygon([pts[i] for i in face],fill=255)
 return im
def mesh_gap(B,G):
 ba=np.array(B)>0;ga=np.array(G)>0;overlap=int(np.count_nonzero(ba&ga))
 if overlap:return 0.,overlap
 b=ba&~(np.array(B.filter(ImageFilter.MinFilter(3)))>0);g=ga&~(np.array(G.filter(ImageFilter.MinFilter(3)))>0);by,bx=np.nonzero(b);gy,gx=np.nonzero(g);best=1e20
 for i in range(0,len(bx),128):best=min(best,float(np.min((bx[i:i+128,None]-gx[None,:])**2+(by[i:i+128,None]-gy[None,:])**2)))
 return math.sqrt(best)/4,0
for i,f in enumerate(frames):
 metrics[str(f)]={}
 for j,mode in enumerate(['v010','v010a']):
  im=Image.open(P/f'previews/{mode}/{f}.png').convert('RGB').crop(rect).resize((tilew,tileh));x=j*tilew;y=i*(tileh+25);out.paste(im,(x,y+25));draw.text((x+8,y+7),f'{mode} / global{f} / same camera and1080p render',fill='black')
  gap,overlap=mesh_gap(mask(meta[mode][str(f)]['BOY']),mask(meta[mode][str(f)]['GIRL']));metrics[str(f)][mode]={'projected_mesh_gap_pixels_at1080p':gap,'overlap_quarter_pixel_samples':overlap}
out.save(P/'evidence/v010_vs_v010a_critical_head_braid.png')
shotframes=[1842,1844,1846];sheet=Image.new('RGB',(1280,len(shotframes)*385),(235,231,222));dr=ImageDraw.Draw(sheet)
for i,f in enumerate(shotframes):
 for j,mode in enumerate(['v010','v010a']):
  im=Image.open(P/f'previews/{mode}/{f}.png').convert('RGB').resize((640,360));sheet.paste(im,(j*640,i*385+25));dr.text((j*640+8,i*385+7),f'{mode} / actual shot frame{f}',fill='black')
sheet.save(P/'evidence/v010_vs_v010a_shot_size.jpg',quality=94)
controls={}
for f in [1837,1849]:
 a=np.array(Image.open(P/f'previews/v010/{f}.png').convert('RGB'),dtype=np.int16);b=np.array(Image.open(P/f'previews/v010a/{f}.png').convert('RGB'),dtype=np.int16);diff=np.abs(a-b);controls[str(f)]={'max_channel_difference':int(diff.max()),'changed_pixels':int(np.count_nonzero(np.any(diff,axis=2)))}
(P/'evidence/critical_visual_diagnostics.json').write_text(json.dumps({'crop_rectangle_1080p':rect,'gap_proxy':'Rasterized evaluated native mesh silhouettes at4x. Diagnostic proxy only; actual painterly pixels in comparison are the artistic evidence.','frames':metrics,'outside_window_render_controls':controls},indent=2));print('CRITICAL_COMPARISONS_READY',json.dumps(metrics),json.dumps(controls))
