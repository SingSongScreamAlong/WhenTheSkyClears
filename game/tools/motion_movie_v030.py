from pathlib import Path
import subprocess,json
import imageio_ffmpeg
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1]; E=P/'evidence/v030'; F=E/'final_native_verified/motion/motion_frames'
frames=sorted(F.glob('*.jpg'));assert len(frames)==360
size=Image.open(frames[0]).size
assert all(Image.open(p).size==size for p in frames)
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe();movie=E/'WTSC_Movement_Study_v030.mp4'
r=subprocess.run([ffmpeg,'-y','-framerate','30','-i',str(F/'%04d.jpg'),'-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
assert r.returncode==0,r.stderr
r=subprocess.run([ffmpeg,'-v','error','-i',str(movie),'-f','null','-','-progress','pipe:1','-nostats'],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
count=max(int(line.split('=')[1]) for line in r.stdout.splitlines() if line.startswith('frame='));assert r.returncode==0 and count==360 and 'progress=end' in r.stdout
info={'build':'0.3.0','file':str(movie.relative_to(P)),'decoded_frames':count,'fps':30,'size':list(size),'bytes':movie.stat().st_size,'audio':'silent','scope':'Isolated flat movement study rendered by the actual Windows executable. Not a campaign playthrough.'}
(E/'motion_movie_validation.json').write_text(json.dumps(info,indent=2))
board=Image.new('RGB',(1600,960),(12,20,23));d=ImageDraw.Draw(board)
for i,n in enumerate([60,105,165,222,262,315]):
    image=Image.open(F/f'{n:04}.jpg').convert('RGB').resize((800,450))
    image.thumbnail((528,297));board.paste(image,((i%3)*536,(i//3)*320))
d.text((20,720),'WHEN THE SKY CLEARS / 0.3.0 / NATIVE LOCOMOTION STUDY',fill=(216,224,207))
d.text((20,756),'Walk, stop, crouch, run, jump/land and low cover. Isolated study; campaign navigation tested separately.',fill=(159,180,172))
board.save(E/'MOVEMENT_CONTACT_REVIEW_v030.jpg',quality=93)
print(json.dumps(info))
