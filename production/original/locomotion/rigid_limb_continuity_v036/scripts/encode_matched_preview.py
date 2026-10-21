import json,subprocess,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import numpy as np
import imageio_ffmpeg as FF
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];BASE=ROOT/'locomotion/preferred_walk_consistent_footwear_v033/previews';ff=FF.get_ffmpeg_exe();font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19);BG=(231,227,217);size=(1280,840);dest=P/'previews/WTSC_v036_vs_v033_Normal_Speed_9p3s.mp4';args=[ff,'-loglevel','error','-nostats','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','1280x840','-r','30','-i','-','-an','-c:v','libx264','-threads','2','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)];proc=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
for section in ['MATCHED_CLOSE','MATCHED_SHOT','NATIVE_CANDIDATE_SHOT']:
 for f in range(1,94):
  b=Image.new('RGB',size,BG);d=ImageDraw.Draw(b);view='CLOSE' if section=='MATCHED_CLOSE' else 'SHOT';new=Image.open(P/'previews'/view/f'{f:04d}.png').convert('RGB');d.text((16,5),f'v036 focused limb correction | 30fps | F{f:03d}/93 | preferred timing retained',font=font,fill='#18252b')
  if section.startswith('MATCHED'):
   old=Image.open(BASE/view/f'{f:04d}.png').convert('RGB');d.text((80,36),'v033 preferred movement / source art',font=small,fill='#18252b');d.text((720,36),'v036 same timing / focused limb art',font=small,fill='#18252b')
   if view=='CLOSE':b.paste(old,(80,65));b.paste(new,(720,65))
   else:b.paste(old.resize((640,360),Image.Resampling.LANCZOS),(0,240));b.paste(new.resize((640,360),Image.Resampling.LANCZOS),(640,240))
   d.text((16,792),'Same native frame/time/camera | three complete cycles | clean art, no guides or hand x-rays',font=small,fill='#18252b');d.text((16,816),'Close panels at native size' if view=='CLOSE' else 'Matched shot panels at50%; native1280x720 candidate shot follows',font=small,fill='#18252b')
  else:
   d.text((16,36),'v036 candidate | original shot camera | native1280x720 pixels',font=small,fill='#18252b');b.paste(new,(0,65));d.text((16,792),'Normal speed | art/motion review candidate | no production integration',font=small,fill='#18252b');d.text((16,816),'Looped walking study; paired recovery and richer acting remain unfinished',font=small,fill='#18252b')
  proc.stdin.write(b.tobytes())
proc.stdin.close();err=proc.stderr.read();assert proc.wait()==0,err.decode(errors='replace')[-2000:]
reader=FF.read_frames(str(dest),pix_fmt='rgb24');meta=next(reader);count=0;selected=[]
for n,raw in enumerate(reader):
 count+=1
 if n in [0,3,10,19,26,30,31,61,92,103,112,119,185,186,196,205,212,216,217,247,278]:
  p=P/'previews'/f'DECODED_{n:03d}.png';Image.frombytes('RGB',meta['size'],raw).save(p);selected.append(str(p.relative_to(P)))
assert count==279 and meta['fps']==30 and dest.stat().st_size<20_000_000
# Measure clean charcoal pixels using the earlier actual hand ID, at unchanged wrist path.
measure=[]
for f in [11,27]:
 a=np.array(Image.open(ROOT/f'locomotion/readability_working_view_v034/previews/ID_FULL_SHOT/{f:04d}.png').convert('RGB')).astype(float);m=(a[:,:,0]>a[:,:,1]+45)&(a[:,:,0]>a[:,:,2]+10)&(a[:,:,0]>110);r={'frame':f}
 for name,file in [('v033',BASE/'SHOT'/f'{f:04d}.png'),('v036',P/'previews/SHOT'/f'{f:04d}.png')]:
  im=np.array(Image.open(file).convert('RGB')).mean(2);r[name+'_near_hand_median_RGB_luma']=float(np.median(im[m]))
 measure.append(r)
overlap={}
for name in ['FULL','NO_NEAR_TROUSER']:
 a=np.array(Image.open(P/'previews/F20_OVERLAP'/(name+'.png')).convert('RGB')).astype(float);mask=(a[:,:,1]>a[:,:,0]+80)&(a[:,:,1]>a[:,:,2]+80)&(a[:,:,1]>160);overlap[name]=int(mask.sum())
report={'file':str(dest.relative_to(P)),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'decoded_frames':count,'fps':meta['fps'],'dimensions':meta['size'],'seconds':9.3,'sections':[{'seconds':[0,3.1],'layout':'Matched close v033/v036 at native480x720 each'},{'seconds':[3.1,6.2],'layout':'Matched shot v033/v036 at50percent each'},{'seconds':[6.2,9.3],'layout':'Candidate shot at native1280x720'}],'native_source_frames':'1..93 at30fps, three31-frame cycles; same camera/time as saved v033 renders. No time warping, holds, interpolation, phase alignment or invented frames. Layouts reuse the same three-cycle shot footage as clearly labelled.','hand_value_measurements':measure,'F20_far_hand_ID_pixels':overlap,'selected_actual_decoded_frames':selected,'observation_limit':'Actual native stills and decoded movie frames inspected. Continuous player playback not observed through available tools; no cinematic or studio-quality acceptance inferred.'};(P/'evidence/PREVIEW_ENCODE_DECODE_AND_READABILITY.json').write_text(json.dumps(report,indent=2));assert overlap['FULL']==0 and overlap['NO_NEAR_TROUSER']>250;print('V036_PREVIEW_READY',json.dumps({k:v for k,v in report.items() if k not in ['selected_actual_decoded_frames','native_source_frames','sections','observation_limit']}),flush=True)
