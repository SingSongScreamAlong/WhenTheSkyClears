from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json
O=Path(__file__).parent;font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',16)
intervals=[('village',241),('camp',1537),('ruins',2161)];stats=[]
whole=Image.new('RGB',(1280,3*3*205),(15,15,15));dr=ImageDraw.Draw(whole)
band=Image.new('RGB',(1536,24*80),(15,15,15));db=ImageDraw.Draw(band)
for zone,(label,start) in enumerate(intervals):
 arr=[]
 for i in range(48):
  f=start+i;p=O/'motion'/'after'/label/f'{f:04d}.png';im=Image.open(p).convert('RGB');a=np.asarray(im);arr.append(a)
  # Whole composition at every fourth frame; all 48 foreground bands separately.
  if i%4==0:
   j=i//4;x=j%4*320;y=(zone*3+j//4)*205;whole.paste(im.resize((320,180)),(x,y+25));dr.text((x+3,y+4),f'{label} F{f}',font=font,fill='white')
  x=i%6*256;y=(zone*8+i//6)*80;band.paste(im.crop((0,500,1280,680)).resize((256,56)),(x,y+24));db.text((x+3,y+3),f'{label} F{f}',font=font,fill='white')
 dif=[]
 for a,b in zip(arr[:-1],arr[1:]):
  d=np.abs(a.astype(float)-b.astype(float));dif.append(float(d[510:590].mean()))
 stats.append({'zone':label,'all_48_frames_read':True,'adjacent_foreground_rgb_mean_abs_diff_min':min(dif),'adjacent_foreground_rgb_mean_abs_diff_max':max(dif),'adjacent_foreground_rgb_mean_abs_diff_median':float(np.median(dif)),'duplicate_raw_frames':48-len({__import__('hashlib').sha256(a.tobytes()).hexdigest() for a in arr})})
whole.save(O/'MOTION_COMPOSITIONS_36_FRAMES.jpg',quality=92);band.save(O/'FOREGROUND_ALL_144_FRAMES.jpg',quality=94)
(O/'MOTION_IMAGE_ANALYSIS.json').write_text(json.dumps({'frames_read':144,'rows':stats,'scope':'All-frame decode/image inspection support, no continuous-player artistic acceptance claim'},indent=2));print('MOTION_CONTACTS_READY')
