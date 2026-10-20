import json,hashlib,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).parent;FF=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',24);small=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',20)
frames=[241,601,961,1201,1537,1849,2161,2377];names=['Village warmth','Abandoned village','Woods','School','Camp','Battlefield','Ruins','Ruins exit']
board=Image.new('RGB',(1280,8*390+40),(18,18,18));draw=ImageDraw.Draw(board);draw.text((12,8),'SOURCE v057',font=small,fill='white');draw.text((652,8),'DEVELOPMENT v058d',font=small,fill='white');pixel=[]
for i,(f,name) in enumerate(zip(frames,names)):
 before=Image.open(O/f'AUDIT_{f:04d}.png').convert('RGB');after=Image.open(O/f'AFTER_D_{f:04d}.png').convert('RGB')
 for col,im in enumerate([before,after]):board.paste(im.resize((640,360),Image.Resampling.LANCZOS),(col*640,40+i*390))
 draw.text((12,40+i*390+362),f'{name} | frame {f} | {(f-1)/24:.2f}s',font=small,fill='white')
 delta=np.abs(np.asarray(before).astype(int)-np.asarray(after).astype(int));mask=np.any(delta>0,axis=2);ys,xs=np.where(mask)
 pixel.append({'frame':f,'top_500_rows_exactly_identical':bool(np.all(delta[:500]==0)),'changed_bbox':[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())] if len(xs) else None,'max_abs_diff_top_500':int(delta[:500].max())})
board.save(O/'WTSC_v058d_All_Regions_Before_After.jpg',quality=92)
(O/'STILL_PIXEL_PRESERVATION.json').write_text(json.dumps(pixel,indent=2))
import sys
if '--board-only' in sys.argv:print('BOARD_READY');raise SystemExit(0)
intervals=[('village',241),('camp',1537),('ruins',2161)]
def encode(path,comparison=False):
 h=1520 if comparison else 800
 cmd=[FF,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'1280x{h}','-framerate','24','-i','-','-an','-c:v','libx264','-threads','2','-preset','medium','-crf','17','-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-movflags','+faststart',str(path)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 for label,start in intervals:
  for f in range(start,start+48):
   after=Image.open(O/'motion'/'after'/label/f'{f:04d}.png').convert('RGB');canvas=Image.new('RGB',(1280,h),(12,12,12));d=ImageDraw.Draw(canvas)
   if comparison:
    canvas.paste(Image.open(O/'motion'/'before'/label/f'{f:04d}.png').convert('RGB'),(0,40));canvas.paste(after,(0,800));d.text((12,7),'SOURCE v057 | same frame / camera',font=font,fill='white');d.text((12,767),'DEVELOPMENT v058d | corrected foreground',font=font,fill='white')
   else:
    canvas.paste(after,(0,0));d.text((14,729),f'v058d WORLD DEVELOPMENT | {label.upper()} | source frame {f} | 24 fps',font=font,fill='white');d.text((14,762),'Environment review only; existing held characters remain unchanged.',font=small,fill=(200,200,200))
   proc.stdin.write(canvas.tobytes())
 proc.stdin.close();assert proc.wait()==0
 result=subprocess.run([FF,'-v','error','-i',str(path),'-map','0:v:0','-f','framemd5','-'],capture_output=True,text=True,check=True)
 rows=[r for r in result.stdout.splitlines() if r and not r.startswith('#')];assert len(rows)==144
 assert [int(r.split(',')[2]) for r in rows]==list(range(144))
 (O/(path.stem+'_DECODED_FRAME_HASHES.txt')).write_text(result.stdout)
 return {'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,'decoded_frames':len(rows),'pts_contiguous':True,'fps':24,'duration':6,'dimensions':[1280,h],'unique_decoded_frames':len(set(r.split(',')[-1] for r in rows))}
videos=[encode(O/'WTSC_v058d_World_Foreground_6s_24fps.mp4'),encode(O/'WTSC_v058d_Before_After_6s_24fps.mp4',True)]
(O/'DELIVERY_REVIEW_v058d.json').write_text(json.dumps({'videos':videos,'all_region_pixel_preservation':pixel,'review_scope':'All eight route stills and three two-second normal-speed traversals; same old held characters, no new character proof','continuous_player_playback_observed':False,'source_foot_image_exclusion':'source v<=0.245, hard clamped below all source character pixels','minimum_standard_attained':False,'remaining_gates':['Paired drawn character performance and story beats','World/character registration and occlusion after integration','Broader native architectural depth','Full film artistic review after integration']},indent=2))
print('VIDEOS_AND_BOARD_READY')
