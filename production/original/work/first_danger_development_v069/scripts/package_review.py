"""Full seven-second normal-speed movies, with matched v067 before panels."""
import subprocess,json,hashlib,re
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
import imageio_ffmpeg
O=Path(__file__).resolve().parents[1];R=O.parents[1];P=O/'previews';FF=imageio_ffmpeg.get_ffmpeg_exe()
B=json.loads((O/'evidence/BUILD.json').read_text());assert hashlib.sha256(Path(B['native']).read_bytes()).hexdigest()==B['native_sha256']
assert json.loads((O/'evidence/COLD_VALIDATION.json').read_text())['passed']
tag=Path(B['native']).stem.split('_')[-1]
records=json.loads((O/f'evidence/MOVIE_BATCHES_{tag}.json').read_text());assert len(records)==7 and all(x['passed'] for x in records)
MUSIC=R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'
BEFORE={'world':R/'work/first_danger_rough_v068/previews/WTSC_First_Danger_Rough_v068e_24fps.mp4','final':R/'work/first_danger_rough_v068/previews/WTSC_First_Danger_Rough_v068e_Title_24fps.mp4'}
def run(args,timeout=120):
 p=subprocess.run([FF,'-hide_banner','-nostdin',*args],capture_output=True,timeout=timeout,creationflags=subprocess.CREATE_NO_WINDOW)
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-4000:])
 return p
def options():return ['-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-r','24','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-c:a','aac','-b:a','192k','-movflags','+faststart']
outputs=[];afters={}
for branch,name in [('world','WTSC_First_Danger_Rough_v069_24fps.mp4'),('final','WTSC_First_Danger_Rough_v069_Title_24fps.mp4')]:
 for g in range(913,1081):
  f=O/f'renders/movie_{tag}/{branch}/{g:04d}.png'
  with Image.open(f) as im:assert im.size==(1280,720);im.verify()
 target=P/name;assert not target.exists()
 run(['-v','error','-framerate','24','-start_number','913','-i',str(O/f'renders/movie_{tag}/{branch}/%04d.png'),'-ss','38','-i',str(MUSIC),'-map','0:v:0','-map','1:a:0','-t','7','-vf','scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p',*options(),str(target)])
 afters[branch]=target;outputs.append(target);print('ENCODED',name,flush=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25);band=Image.new('RGB',(2560,44),'#111820');dr=ImageDraw.Draw(band)
dr.text((20,7),'BEFORE | v068 rough',font=font,fill='white');dr.text((1300,7),'AFTER | v069 PAINTED DEVELOPMENT',font=font,fill='white');label=P/'comparison_labels.png';band.save(label)
for branch,name in [('world','WTSC_First_Danger_Before_After_ROUGH_v069_24fps.mp4'),('final','WTSC_First_Danger_Before_After_ROUGH_TITLE_v069_24fps.mp4')]:
 target=P/name;assert not target.exists()
 graph='[0:v]scale=1280:720:flags=lanczos,setsar=1,setpts=PTS-STARTPTS[a];[1:v]setsar=1,setpts=PTS-STARTPTS[b];[a][b]hstack=inputs=2,pad=2560:764:0:44:color=0x111820[stack];[stack][2:v]overlay=0:0:shortest=1[out]'
 run(['-v','error','-i',str(BEFORE[branch]),'-i',str(afters[branch]),'-loop','1','-framerate','24','-i',str(label),'-filter_complex',graph,'-map','[out]','-map','1:a:0','-t','7',*options(),str(target)])
 outputs.append(target);print('COMPARISON',name,flush=True)
detail=P/'WTSC_First_Danger_Before_After_ACTING_DETAIL_v069_24fps.mp4';assert not detail.exists()
band2=Image.new('RGB',(1440,40),'#111820');d2=ImageDraw.Draw(band2);f2=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21)
d2.text((14,7),'BEFORE | v068 rough',font=f2,fill='white');d2.text((734,7),'AFTER | v069 DEVELOPMENT',font=f2,fill='white');label2=P/'acting_detail_labels.png';band2.save(label2)
graph='[0:v]crop=720:420:280:150,setsar=1,setpts=PTS-STARTPTS[a];[1:v]crop=720:420:280:150,setsar=1,setpts=PTS-STARTPTS[b];[a][b]hstack=inputs=2,pad=1440:460:0:40:color=0x111820[stack];[stack][2:v]overlay=0:0:shortest=1[out]'
run(['-v','error','-i',str(BEFORE['world']),'-i',str(afters['world']),'-loop','1','-framerate','24','-i',str(label2),'-filter_complex',graph,'-map','[out]','-map','1:a:0','-t','7',*options(),str(detail)])
outputs.append(detail);print('ACTING_DETAIL_READY',flush=True)
checks=[]
for f in outputs:
 p=run(['-v','error','-i',str(f),'-map','0:v:0','-progress','pipe:1','-f','null','NUL']);count=int(re.findall(r'^frame=(\d+)',p.stdout.decode(),re.M)[-1]);assert count==168
 info=run(['-v','info','-i',str(f),'-map','0:v:0','-vf','showinfo','-an','-f','null','NUL']).stderr.decode(errors='replace')
 stamps=[float(x) for x in re.findall(r'\bn:\s*\d+\s+pts:\s*\d+\s+pts_time:([\d.]+)',info)]
 assert len(stamps)==168 and max(abs(v-i/24) for i,v in enumerate(stamps))<.00001
 checks.append({'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'frames':count,'fps':24,'duration_seconds':7,'fully_decoded':True,'contiguous_timestamps':True})
def rgbframes(movie,ns,size=(1280,720)):
 expr='+'.join(f'eq(n\\,{n})' for n in ns);raw=run(['-v','error','-i',str(movie),'-vf',f'select={expr},scale={size[0]}:{size[1]}:flags=lanczos','-fps_mode','vfr','-pix_fmt','rgb24','-f','rawvideo','pipe:1']).stdout
 return np.frombuffer(raw,dtype=np.uint8).reshape(len(ns),size[1],size[0],3)
ns=[0,38,48,60,72,78,90,108,144,167];before=rgbframes(BEFORE['world'],ns);after=rgbframes(afters['world'],ns)
fontsm=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
# Match complete camera compositions; do not chase each new pose with a crop.
board=Image.new('RGB',(1280,10*388),'#111820');bd=ImageDraw.Draw(board)
for i,n in enumerate(ns):
 for col,(arr,cap) in enumerate([(before,'BEFORE v068'),(after,'AFTER v069 DEVELOPMENT')]):
  x=col*640;y=i*388;bd.text((x+10,y+5),f'{cap} | G{913+n} | {38+n/24:.3f}s',font=fontsm,fill='white');im=Image.fromarray(arr[i]);im.thumbnail((640,360),Image.Resampling.LANCZOS);board.paste(im,(x,y+28))
board.save(P/'Full_Frame_Before_After_Chronology.jpg',quality=94)
# Every sixth production frame, in chronological order, for motion inspection.
ns2=list(range(0,168,6));motion=rgbframes(afters['world'],ns2,size=(640,360));sheet=Image.new('RGB',(640*4,388*7),'#111820');sd=ImageDraw.Draw(sheet)
for i,(n,a) in enumerate(zip(ns2,motion)):
 x=i%4*640;y=i//4*388;sd.text((x+10,y+5),f'ROUGH | G{913+n} | {38+n/24:.3f}s',font=fontsm,fill='white');sheet.paste(Image.fromarray(a),(x,y+28))
sheet.save(P/'Actual_Rough_Chronology.jpg',quality=94)
color=[]
for n,arr in zip(ns,after):
 src=np.array(Image.open(O/f'renders/movie_{tag}/world/{913+n:04d}.png').convert('RGB'));err=float(np.abs(src.astype(float)-arr.astype(float)).mean());color.append({'frame':913+n,'mean_abs_rgb_codes':err});assert err<3
raw_src=run(['-v','error','-ss','38','-t','7','-i',str(MUSIC),'-ac','1','-ar','16000','-f','f32le','pipe:1']).stdout
raw_out=run(['-v','error','-i',str(afters['world']),'-map','0:a:0','-t','7','-ac','1','-ar','16000','-f','f32le','pipe:1']).stdout
a=np.frombuffer(raw_src,dtype='<f4');b=np.frombuffer(raw_out,dtype='<f4');N=min(len(a),len(b));corr=float(np.corrcoef(a[:N],b[:N])[0,1]);assert corr>.995
assert hashlib.sha256(Path(B['source']).read_bytes()).hexdigest()==B['source_sha256']
(O/'evidence/DELIVERY.json').write_text(json.dumps({'native':B['native'],'native_sha256':B['native_sha256'],'outputs':checks,'before':{k:str(v) for k,v in BEFORE.items()},'audio':str(MUSIC),'audio_excerpt_seconds':[38,45],'source_audio_correlation':corr,'decoded_color_checks':color,'review_resolution_per_panel':[1280,720],'native_resolution':[3840,2160],'normal_speed':'168 production frames at24fps.168 native drawing exposures per child, one per production frame. Same global38-45s camera/audio; no slow motion, optical-flow interpolation or speed remapping.','scope':'Rough seven-second candidate only; no full-trailer integration. Painted head-angle studies and retained original pigments on developed contours. Likeness and animation remain provisional pending review.','artistic_acceptance':False},indent=2))
print('V069_REVIEW_READY',flush=True)
