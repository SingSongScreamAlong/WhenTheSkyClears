from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,subprocess,hashlib
import imageio_ffmpeg
P=Path(__file__).resolve().parents[1];BASE=P.parent/'character_design_finish_v040/previews';FONT='C:/Windows/Fonts/segoeui.ttf'
def label(d,p,s,n=24):d.text(p,s,font=ImageFont.truetype(FONT,n),fill='#e6e5dc')
board=Image.new('RGB',(1920,3900),'#202725');d=ImageDraw.Draw(board);label(d,(28,12),'WHEN THE SKY CLEARS  |  v041 NECK / COLLAR CONSTRUCTION',34);label(d,(28,59),'Same liked face, painting and walk. Local garment construction candidate; no new acting.',25)
for x,p,name in [(0,BASE/'HERO/0001.png','v040 | preserved source'),(960,P/'previews/CANDIDATE_HERO/0001.png','v041 | neck-attached collar')]:
 label(d,(x+28,105),name,27);board.paste(Image.open(p).convert('RGB'),(x,140))
for i,f in enumerate([1,11,20,27]):
 y=1660+i*535
 for x,mode,title in [(160,'BASELINE','v040'),(1120,'CANDIDATE','v041')]:
  label(d,(x,y-36),f'{title} | F{f:02d} | actual 640x480 detail camera',24);board.paste(Image.open(P/f'previews/{mode}_DETAIL/{f:04d}.png').convert('RGB'),(x,y))
label(d,(28,3810),'Actual native renders. Original yoke hidden intact; folded collar and upper coat meet on the original walking clock.',23);label(d,(28,3850),'This local connection does not finish the fixed expression, body/hand construction or paired recovery acting.',22);bp=P/'previews/WTSC_v041_Neck_Collar_Matched_Proof.png';board.save(bp)
out=P/'previews/WTSC_v041_vs_v040_Neck_Collar_Normal_Speed.mp4';size=(1280,840);cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-y','-v','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','1280x840','-r','30','-i','-','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)];proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
for section in ['MATCHED CLOSE','MATCHED SHOT AT 50%','CANDIDATE NATIVE SHOT']:
 for f in range(1,64):
  canvas=Image.new('RGB',size,'#202725');d=ImageDraw.Draw(canvas);label(d,(24,10),'WHEN THE SKY CLEARS  |  v041 NECK / COLLAR TEST',27);label(d,(24,47),f'{section}  |  unchanged walk  |  30 fps  |  F{f:02d}',21)
  if section=='MATCHED CLOSE':
   canvas.paste(Image.open(BASE/f'CLOSE/{f:04d}.png').convert('RGB'),(160,86));canvas.paste(Image.open(P/f'previews/CANDIDATE_CLOSE/{f:04d}.png').convert('RGB'),(640,86));label(d,(24,150),'v040',22);label(d,(1140,150),'v041',22)
  elif section=='MATCHED SHOT AT 50%':
   for x,p,name in [(0,BASE/f'SHOT/{f:04d}.png','v040'),(640,P/f'previews/CANDIDATE_SHOT/{f:04d}.png','v041')]:canvas.paste(Image.open(p).convert('RGB').resize((640,360),Image.Resampling.LANCZOS),(x,236));label(d,(x+24,194),name+' | 50% view',22)
   label(d,(24,650),'Comparison panels are reduced. The candidate follows at full native shot size.',21)
  else:canvas.paste(Image.open(P/f'previews/CANDIDATE_SHOT/{f:04d}.png').convert('RGB'),(0,86))
  label(d,(24,812),'CONSTRUCTION CANDIDATE | Two native cycles + closing pose. Original face and body timing retained.',18);proc.stdin.write(canvas.tobytes())
proc.stdin.close();err=proc.stderr.read().decode();assert proc.wait()==0,err
reader=imageio_ffmpeg.read_frames(str(out),pix_fmt='rgb24');meta=next(reader);count=0;decode=[]
for i,raw in enumerate(reader):
 if i in [0,3,10,19,26,31,61,62,63,73,82,89,125,126,136,145,152,157,187,188]:
  p=P/f'previews/DECODED/{i:04d}.png';p.parent.mkdir(exist_ok=True);Image.frombytes('RGB',size,raw).save(p);decode.append({'zero_based_movie_frame':i,'section':i//63,'source_frame':i%63+1,'file':str(p.relative_to(P))})
 count+=1
assert count==189 and meta['fps']==30 and out.stat().st_size<20_000_000
r={'file':str(out.relative_to(P)),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'dimensions':size,'fps':meta['fps'],'decoded_frames':count,'duration_seconds':count/30,'source_frames_per_section':[1,63],'cycles_per_section':2,'closing_pose_included':True,'sections':['Matched close at native480x720 per panel','Matched shot reduced to640x360 per panel','Candidate shot at full native1280x720'],'native_candidate_unique_motion_frames':126,'native_cycles_rendered_not_recycled':True,'same_original_body_actions':True,'new_AI_paint_or_AI_animation':False,'board':str(bp.relative_to(P)),'board_dimensions':board.size,'board_bytes':bp.stat().st_size,'decoded_inspection_frames':decode,'observation_limit':'Actual encoded movie decoded for frame/pixel inspection. No continuous video-player playback observation claimed.'};(P/'evidence/COMPARISON_ENCODING_AND_DECODE.json').write_text(json.dumps(r,indent=2));print('V041_COMPARISON_COMPLETE',json.dumps({k:v for k,v in r.items() if k!='decoded_inspection_frames'}))
