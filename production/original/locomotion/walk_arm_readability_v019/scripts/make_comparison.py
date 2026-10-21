from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import imageio_ffmpeg,subprocess,json,hashlib
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];B=ROOT/'locomotion/reference_walk_exercise_v018/previews';D=P/'previews';(D/'COMPARISON').mkdir(exist_ok=True)
F=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',24);SM=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
for f in range(1,49):
 im=Image.new('RGB',(1920,1160),'#eee9dd');d=ImageDraw.Draw(im)
 for x,label,path in [(0,'v018 BEFORE',B/'SMOOTH'),(960,'v019 WRISTS / ORDER ONLY',D/'AFTER')]:
  d.text((x+20,6),label+' | close whole-body view',font=F,fill='#282624');im.paste(Image.open(path/f'{f:04d}.png').convert('RGB'),(x,40))
 for x,label,path in [(0,'BEFORE',B/'MATCHED'),(960,'AFTER',D/'MATCHED_AFTER')]:
  d.text((x+20,585),label+' | original shot scale | frame '+str(f)+' | overall walk rejected',font=SM,fill='#282624');im.paste(Image.open(path/f'{f:04d}.png').convert('RGB'),(x,620))
 im.save(D/f'COMPARISON/{f:04d}.png')
ff=imageio_ffmpeg.get_ffmpeg_exe();movie=D/'WTSC_v019_Arm_Comparison_Whole_Body_and_Shot_Size_2s.mp4'
subprocess.run([ff,'-y','-hide_banner','-loglevel','error','-framerate','24','-i',str(D/'COMPARISON/%04d.png'),'-frames:v','48','-c:v','libx264','-threads','2','-crf','18','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],check=True)
# Critical window: actual painted crops alongside the unaltered matched framing.
board=Image.new('RGB',(1920,1080),'#eee9dd');draw=ImageDraw.Draw(board)
for j,f in enumerate([10,13,16]):
 x=j*640;draw.text((x+15,10),'Frame '+str(f)+' | BEFORE / AFTER',font=F,fill='#282624');cx=480+((.44*(f-1)/24)-.44)/3.25*960
 for k,path in enumerate([B/'SMOOTH',D/'AFTER']):
  a=Image.open(path/f'{f:04d}.png').convert('RGB');crop=a.crop((int(cx-125),135,int(cx+155),490));crop=crop.resize((320,406));board.paste(crop,(x+k*320,55))
 for k,path in enumerate([B/'MATCHED',D/'MATCHED_AFTER']):
  a=Image.open(path/f'{f:04d}.png').convert('RGB').resize((320,180));board.paste(a,(x+k*320,490));draw.text((x+k*320+10,677),'v018' if k==0 else 'v019',font=SM,fill='#282624')
draw.text((24,746),'Local result: the near hand clears the coat through the rejected10-16 window.',font=F,fill='#282624')
draw.text((24,790),'Whole walk remains artistically rejected: rigid torso, uneven loading and strip-like knees are unchanged.',font=F,fill='#282624')
draw.text((24,835),'The wider forward arm arc is a silhouette accommodation; it does not supply believable body weight.',font=F,fill='#282624')
draw.text((24,880),'Feet, travel, cadence, body and head are frozen from v018. No new painting, additional performances or production integration.',font=F,fill='#282624')
board.save(D/'WTSC_v019_Arm_Window_Before_After.jpg',quality=95)
# Decode actual encoded frames for an honest chronological visual review.
reader=imageio_ffmpeg.read_frames(str(movie),pix_fmt='rgb24');meta=next(reader);wanted=[1,7,8,10,13,16,19,20,22,25,37,48];sampled={}
for i,raw in enumerate(reader,1):
 if i in wanted:sampled[i]=Image.frombytes('RGB',meta['size'],raw)
contact=Image.new('RGB',(1920,1560),'#eee9dd')
for j,f in enumerate(wanted):
 a=sampled[f].resize((480,290));x=j%4*480;y=j//4*520;contact.paste(a,(x,y));ImageDraw.Draw(contact).text((x+16,y+305),'Decoded frame '+str(f),font=SM,fill='#282624')
contact.save(D/'WTSC_v019_Decoded_Comparison_Samples.jpg',quality=94)
out={'movie':str(movie.resolve()),'bytes':movie.stat().st_size,'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'fps':24,'frames':48,'duration_seconds':2,'dimensions':meta['size'],'decoded_review_frames':wanted,'observation_limit':'Decoded samples and crop boards only; no normal-speed playback observation claimed. Cadence judgement remains provisional.','screen_loop':'Two translating cycles; replay resets world travel and numbered markers.'};(P/'evidence/comparison_preview.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
