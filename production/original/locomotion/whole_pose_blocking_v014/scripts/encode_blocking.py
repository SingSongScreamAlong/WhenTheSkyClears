from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg,subprocess,json,hashlib
P=Path(__file__).resolve().parents[1];ff=imageio_ffmpeg.get_ffmpeg_exe();media=[];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15);folder=P/'evidence/decoded_review';folder.mkdir(exist_ok=True)
for mode in ['INSPECTION','SHOT_SIZE']:
 assert len(list((P/'previews'/mode).glob('*.png')))==72
 dest=P/('WTSC_v014_Whole_Pose_Blocking_3s.mp4' if mode=='INSPECTION' else 'WTSC_v014_Shot_Size_Blocking_3s.mp4')
 subprocess.run([ff,'-y','-v','error','-framerate','24','-i',str(P/f'previews/{mode}/%04d.png'),'-frames:v','72','-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(dest)],check=True)
 reader=imageio_ffmpeg.read_frames(str(dest),pix_fmt='rgb24');metadata=next(reader);count=0;pages=[]
 for i,pixels in enumerate(reader):
  if i%24==0:out=Image.new('RGB',(1600,6*345),(237,237,233));d=ImageDraw.Draw(out)
  im=Image.frombytes('RGB',metadata['size'],pixels).crop((230,100,730,500)).resize((400,320));x=i%4*400;y=i%24//4*345;out.paste(im,(x,y+25));d.text((x+7,y+4),f'{mode} decoded {i+1:02d} / {i/24:.3f}s',font=font,fill='black');count=i+1
  if i%24==23:
   path=folder/f'{mode}_{i-22:02d}_{i+1:02d}.jpg';out.save(path,quality=94);pages.append(str(path))
 assert count==72 and metadata['fps']==24 and dest.stat().st_size<20_000_000
 media.append({'path':str(dest),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'decoded_frames':count,'fps':24,'seconds':metadata['duration'],'size':metadata['size'],'interpolation':'Stepped whole-pose blocking; intentional held exposures, no curve polish.','decoded_review_pages':pages})
(P/'evidence/media_verification.json').write_text(json.dumps(media,indent=2));print(json.dumps(media,indent=2))
