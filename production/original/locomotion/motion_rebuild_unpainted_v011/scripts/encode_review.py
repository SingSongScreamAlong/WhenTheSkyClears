from pathlib import Path
import subprocess,hashlib,json
from PIL import Image,ImageDraw
import imageio_ffmpeg
P=Path(__file__).resolve().parents[1];ff=imageio_ffmpeg.get_ffmpeg_exe();outputs=[]
for mode in ['INSPECTION','SHOT_SIZE']:
 assert len(list((P/'previews'/mode).glob('*.png')))==144
 name='WTSC_v011_Unpainted_Stumble_Recovery_Walk_6s.mp4' if mode=='INSPECTION' else 'WTSC_v011_Unpainted_Shot_Size_6s.mp4';out=P/name
 subprocess.run([ff,'-y','-v','error','-framerate','24','-i',str(P/f'previews/{mode}/%04d.png'),'-frames:v','144','-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(out)],capture_output=True,check=True)
 reader=imageio_ffmpeg.read_frames(str(out),pix_fmt='rgb24');meta=next(reader);count=sum(1 for _ in reader);assert count==144 and meta['fps']==24 and out.stat().st_size<20_000_000
 outputs.append({'path':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'decoded_frames':count,'fps':meta['fps'],'seconds':meta['duration'],'size':meta['size'],'sound':'Silent motion test; no soundtrack edits.'})
 frames=[13,23,24,27,30,35,40,44,48,56,64,66,72,78,82,94,109,124,139,144];sheet=Image.new('RGB',(1440,7*295),(237,237,233));draw=ImageDraw.Draw(sheet)
 for i,f in enumerate(frames):
  im=Image.open(P/f'previews/{mode}/{f:04d}.png').convert('RGB').resize((480,270));x=(i%3)*480;y=(i//3)*295;sheet.paste(im,(x,y+25));draw.text((x+8,y+7),f'{mode} / {f} / {(f-1)/24:.3f}s',fill='black')
 sheet.save(P/f'evidence/{mode}_pose_review.jpg',quality=94)
# Dense actual-frame progression of the catch/load event, not isolated hero poses.
frames=list(range(22,51,2));out=Image.new('RGB',(1440,5*295),(237,237,233));dr=ImageDraw.Draw(out)
for i,f in enumerate(frames):
 im=Image.open(P/f'previews/INSPECTION/{f:04d}.png').convert('RGB').resize((480,270));x=(i%3)*480;y=(i//3)*295;out.paste(im,(x,y+25));dr.text((x+8,y+7),f'Catch progression {f} / {(f-1)/24:.3f}s',fill='black')
out.save(P/'evidence/dense_catch_progression.jpg',quality=94)
(P/'evidence/media_verification.json').write_text(json.dumps(outputs,indent=2));print(json.dumps(outputs,indent=2))
