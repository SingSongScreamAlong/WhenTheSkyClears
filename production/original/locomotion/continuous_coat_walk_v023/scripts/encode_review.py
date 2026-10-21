from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg,json,hashlib
P=Path(__file__).resolve().parents[1];D=P/'previews';font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
movie=D/'WTSC_v023_Normal_Speed_Walk_Close_and_Shot_3p1s.mp4';writer=imageio_ffmpeg.write_frames(str(movie),(1328,608),fps=30,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',quality=8,ffmpeg_log_level='error',output_params=['-threads','2','-crf','18','-preset','medium','-movflags','+faststart']);writer.send(None)
for f in range(1,94):
 im=Image.new('RGB',(1328,608),'#eee9dd');d=ImageDraw.Draw(im);im.paste(Image.open(D/f'CLOSE/{f:04d}.png').convert('RGB'),(0,36));im.paste(Image.open(D/f'SHOT/{f:04d}.png').convert('RGB'),(360,36));d.text((10,5),'V023 | close',font=font,fill='#292622');d.text((380,5),f'Original camera framing | NORMAL SPEED /30fps | {(f-1)/30:.2f}s',font=font,fill='#292622');d.text((10,578),'Three walking cycles. Continuous cloth drawings; isolated neutral-stage proof. Artistic approval OPEN.',font=small,fill='#292622');writer.send(im.tobytes())
writer.close()
r=imageio_ffmpeg.read_frames(str(movie),pix_fmt='rgb24');meta=next(r);allframes=[]
for raw in r:allframes.append(Image.frombytes('RGB',meta['size'],raw))
board=Image.new('RGB',(1920,1440),'#eee9dd');d=ImageDraw.Draw(board)
for i in range(31):
 f=allframes[i];x=(i%8)*240;y=(i//8)*360;board.paste(f.crop((0,36,360,576)).resize((240,360)),(x,y));d.text((x+7,y+7),str(i+1),font=small,fill='#292622')
board.save(P/'evidence/ACTUAL_ENCODED_FIRST_CYCLE_ALL_FRAMES.jpg',quality=95)
chosen=[28,29,30,31,32,33,34,35,59,60,61,62,63,64,65,66,88,89,90,91,92,93]
board=Image.new('RGB',(1920,1080),'#eee9dd');d=ImageDraw.Draw(board)
for i,n in enumerate(chosen):
 x=(i%8)*240;y=(i//8)*360;board.paste(allframes[n-1].crop((0,36,360,576)).resize((240,360)),(x,y));d.text((x+7,y+7),'F'+str(n),font=small,fill='#292622')
board.save(P/'evidence/ACTUAL_ENCODED_LOOP_BOUNDARY_FRAMES.jpg',quality=95)
board=Image.new('RGB',(1920,1080),'#eee9dd')
for i,n in enumerate([1,5,9,13,17,21,25,29,32]):
 x=(i%3)*640;y=(i//3)*360;board.paste(allframes[n-1].crop((360,36,1320,576)).resize((640,360)),(x,y))
board.save(P/'evidence/ACTUAL_ENCODED_SHOT_FRAMES.jpg',quality=95)
report={'movie':str(movie.resolve()),'bytes':movie.stat().st_size,'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'fps':meta['fps'],'frames_decoded':len(allframes),'duration_seconds':len(allframes)/meta['fps'],'dimensions':meta['size'],'normal_speed':True,'holds_or_retiming':False,'source_period_frames':31,'cycles':3,'visual_inspection':'First-cycle31decoded frames plus loop boundary and shot-size boards. This is frame inspection, not observed real-time playback.'}
assert len(allframes)==93 and meta['fps']==30 and movie.stat().st_size<20_000_000
(P/'evidence/preview_verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))

