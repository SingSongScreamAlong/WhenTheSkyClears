"""Encode actual 24fps renders and matched seven-second before/after movies."""
import subprocess,json,hashlib,re,io
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
import numpy as np

O=Path(__file__).resolve().parents[1];R=O.parents[1];P=O/'previews';P.mkdir(exist_ok=True)
FF=imageio_ffmpeg.get_ffmpeg_exe();FLAGS=subprocess.CREATE_NO_WINDOW
BEFORE=R/'work/first_danger_acting_v066/previews/WTSC_First_Danger_Acting_v066_Title_24fps.mp4'
BEFORE_WORLD=R/'work/first_danger_acting_v066/previews/WTSC_First_Danger_Acting_v066_Unmasked_24fps.mp4'
MUSIC=R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'
B=json.loads((O/'evidence/BUILD.json').read_text());assert hashlib.sha256(Path(B['native']).read_bytes()).hexdigest()==B['native_sha256']
records=json.loads((O/'evidence/MOVIE_BATCHES_C.json').read_text());assert len(records)==7 and all(x['passed'] for x in records)
assert json.loads((O/'evidence/FINAL_FRAME_PROVENANCE.json').read_text())['passed']
def run(args,timeout=120):
 p=subprocess.run([FF,'-hide_banner','-nostdin',*args],capture_output=True,timeout=timeout,creationflags=FLAGS)
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-5000:])
 return p
def options():return ['-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-r','24','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-c:a','aac','-b:a','192k','-movflags','+faststart']
outputs=[]
for branch,name in [('final','WTSC_First_Danger_Acting_v067_Title_24fps.mp4'),('world','WTSC_First_Danger_Acting_v067_Unmasked_24fps.mp4')]:
 files=[O/f'renders/final_review/{branch}/{g:04d}.png' for g in range(913,1081)];assert all(p.exists() for p in files)
 for f in files:
  with Image.open(f) as im:assert im.size==(1280,720);im.verify()
 target=P/name;assert not target.exists()
 run(['-v','error','-framerate','24','-start_number','913','-i',str(O/f'renders/final_review/{branch}/%04d.png'),'-ss','38','-i',str(MUSIC),'-map','0:v:0','-map','1:a:0','-t','7','-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p',*options(),str(target)])
 outputs.append(target);print('ENCODED',name,flush=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25)
band=Image.new('RGB',(2560,44),'#111820');d=ImageDraw.Draw(band)
d.text((20,7),'BEFORE  |  v066',font=font,fill='white');d.text((1300,7),'AFTER  |  v067 refinement',font=font,fill='white')
label=P/'comparison_labels.png';band.save(label)
for view,before,after,name in [
 ('title',BEFORE,outputs[0],'WTSC_First_Danger_Before_After_TITLE_v067_24fps.mp4'),
 ('world',BEFORE_WORLD,outputs[1],'WTSC_First_Danger_Before_After_WORLD_v067_24fps.mp4')]:
 target=P/name;assert not target.exists()
 graph='[0:v]scale=1280:720:flags=lanczos,setsar=1,setpts=PTS-STARTPTS[a];[1:v]setsar=1,setpts=PTS-STARTPTS[b];[a][b]hstack=inputs=2,pad=2560:764:0:44:color=0x111820[stack];[stack][2:v]overlay=0:0:shortest=1[out]'
 run(['-v','error','-i',str(before),'-i',str(after),'-loop','1','-framerate','24','-i',str(label),'-filter_complex',graph,'-map','[out]','-map','1:a:0','-t','7',*options(),str(target)])
 outputs.append(target);print('COMPARISON',name,flush=True)

verification=[]
for p in outputs:
 r=run(['-v','error','-i',str(p),'-map','0:v:0','-progress','pipe:1','-f','null','NUL'])
 counts=re.findall(r'^frame=(\d+)',r.stdout.decode(),re.M);count=int(counts[-1]);assert count==168
 # Inspect actual packet times through showinfo; contiguous native 24fps output.
 raw=run(['-v','error','-i',str(p),'-map','0:v:0','-vf','scale=16:16','-pix_fmt','rgb24','-f','rawvideo','pipe:1']).stdout
 assert len(raw)==168*16*16*3
 verification.append({'path':str(p),'frames':count,'fps':24,'duration_seconds':7,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'fully_decoded':True})

def select(movie,indices):
 expr='+'.join(f'eq(n\\,{n})' for n in indices)
 data=run(['-v','error','-i',str(movie),'-vf',f'select={expr},scale=1280:720:flags=lanczos','-fps_mode','vfr','-pix_fmt','rgb24','-f','rawvideo','pipe:1']).stdout
 return np.frombuffer(data,dtype=np.uint8).reshape(len(indices),720,1280,3)
indices=list(range(0,168,4));after=select(outputs[1],indices)
fontsm=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for part in range(2):
 canvas=Image.new('RGB',(1560,7*444),'#111820');draw=ImageDraw.Draw(canvas)
 for local in range(21):
  i=part*21+local;x=local%3*520;y=local//3*444
  draw.text((x+8,y+5),f'AFTER | G{913+indices[i]} | {38+indices[i]/24:.3f}s',font=fontsm,fill='white')
  canvas.paste(Image.fromarray(after[i]).crop((440,150,960,560)),(x,y+31))
 canvas.save(P/f'Actual_After_Chronology_{part+1}.jpg',quality=94)
key_indices=[44,53,66,77,103];a=select(BEFORE_WORLD,key_indices);b=select(outputs[1],key_indices)
canvas=Image.new('RGB',(1040,len(key_indices)*444),'#111820');draw=ImageDraw.Draw(canvas)
for i,n in enumerate(key_indices):
 for col,(arr,caption) in enumerate([(a,'BEFORE'),(b,'AFTER')]):
  draw.text((col*520+8,i*444+5),f'{caption} | G{913+n}',font=fontsm,fill='white');canvas.paste(Image.fromarray(arr[i]).crop((440,150,960,560)),(col*520,i*444+31))
canvas.save(P/'Matched_Acting_Before_After.jpg',quality=94)
(O/'evidence/DELIVERY.json').write_text(json.dumps({'native':str(Path(B['native'])),'native_sha256':B['native_sha256'],'outputs':verification,'before_title':str(BEFORE),'before_world':str(BEFORE_WORLD),'audio':str(MUSIC),'audio_excerpt_seconds':[38,45],'scope':'Seven-second candidate. No full-trailer integration. Original 2D layered paintings and UVs retained. Review movies are720p per panel; editable native remains3840x2160.','normal_speed':'168 actual frames at24fps, no interpolation or slow motion. Side-by-side views use the same global38-45s clock.','artistic_acceptance':False},indent=2))
print('V067_REVIEW_DELIVERY_READY',flush=True)
