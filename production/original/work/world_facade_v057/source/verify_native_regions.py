from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,math
O=Path(__file__).parent;R=Path(r'WTSC_LOCAL_WORKSPACE\work\world_architecture_v049i\native_4k_after');S=453.441/84
q=[]
for f,xb in [(1201,2830.17),(1225,2299.25),(1249,1768.33)]:
 a=np.asarray(Image.open(R/f'WTSC_v049i_School_{f}_4K.png').convert('RGB'),dtype=np.int16);b=np.asarray(Image.open(O/'native_4k_after'/f'WTSC_ContinuousFacade_v057_{f}_4K.png').convert('RGB'),dtype=np.int16);d=np.abs(b-a)
 def projection(x,y):return (xb+(x-1004)*S,-41.09+(y-475)*S)
 def rect(box):
  xa,ya=projection(box[0],box[1]);xx,yy=projection(box[2],box[3]);x0=max(0,math.ceil(xa));x1=min(3840,math.floor(xx));y0=max(0,math.ceil(ya));y1=min(2160,math.floor(yy))
  if x1<=x0 or y1<=y0:return None
  v=d[y0:y1,x0:x1];return {'native_box':[x0,y0,x1,y1],'max_channel_delta':int(v.max()),'changed_pixels':int((v.max(2)>0).sum())}
 lo=projection(824,324);hi=projection(1448,740);envelope=np.zeros((2160,3840),bool);envelope[max(0,math.floor(lo[1])-2):min(2160,math.ceil(hi[1])+2),max(0,math.floor(lo[0])-2):min(3840,math.ceil(hi[0])+2)]=True
 outside=d[~envelope];cx,cy=projection(1044.0833,497.9167);pit=d[int(cy)-20:int(cy)+21,int(cx)-20:int(cx)+21]
 row={'frame':f,'outside_projected_edit_envelope_max_delta':int(outside.max()),'outside_projected_edit_envelope_changed_pixels':int((outside.max(1)>0).sum()),'protected_window_interior':rect((874,414,1001,654)),'protected_lower_left_foliage':rect((842,636,1102,722)),'protected_lower_right_foliage':rect((1338,598,1430,722)),'pit_core_41x41_max_delta':int(pit.max()),'pit_core_41x41_changed_pixels':int((pit.max(2)>0).sum())}
 assert row['outside_projected_edit_envelope_max_delta']==0 and row['pit_core_41x41_max_delta']==0
 for k in ['protected_window_interior','protected_lower_left_foliage','protected_lower_right_foliage']:
  if row[k]:assert row[k]['max_channel_delta']==0,(k,row[k])
 q.append(row)
(O/'NATIVE_PRESERVATION_REGIONS.json').write_text(json.dumps(q,indent=2));print(json.dumps(q))
# Native join crop, used only for review; no pixel resizing.
A=Image.open(R/'WTSC_v049i_School_1225_4K.png').convert('RGB');B=Image.open(O/'native_4k_after/WTSC_ContinuousFacade_v057_1225_4K.png').convert('RGB');font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
im=Image.new('RGB',(900,1450),'#192124');dr=ImageDraw.Draw(im)
for col,(img,t) in enumerate([(A,'v049i / original'),(B,'v057 / left join')]):im.paste(img.crop((1190,0,1640,1400)),(col*450,50));dr.text((col*450+10,12),t,fill='white',font=font)
im.save(O/'QA_LEFT_JOIN_1_TO_1.jpg',quality=96,subsampling=0)
im=Image.new('RGB',(2160,300),'#192124');dr=ImageDraw.Draw(im)
for col,(img,t) in enumerate([(A,'v049i / original lower edge'),(B,'v057 / lower join')]):im.paste(img.crop((1650,1230,2730,1480)),(col*1080,50));dr.text((col*1080+10,12),t,fill='white',font=font)
im.save(O/'QA_LOWER_JOIN_1_TO_1.jpg',quality=96,subsampling=0)
