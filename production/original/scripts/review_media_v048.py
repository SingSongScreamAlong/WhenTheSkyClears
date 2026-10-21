"""Full-decode actual4K output and prepare review-only crops/sheets and small preview."""
import json,subprocess,re,hashlib,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
version=sys.argv[1] if len(sys.argv)>1 else 'v047f'
R=Path(__file__).resolve().parents[1];N=R/'notes/improvement_v048';D=R/f'renders/refinement_{version}';E=D/'review_evidence';E.mkdir(exist_ok=True)
F=r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
movie=D/f'WTSC_Refinement_{version}_75_80_4K.mp4';small=D/f'WTSC_Refinement_{version}_75_80_View_1080p.mp4'

def run(args):
 r=subprocess.run([F,'-hide_banner','-nostdin',*args],capture_output=True,text=True)
 assert r.returncode==0,r.stderr[-3000:]
 return r
decoded=run(['-v','info','-i',str(movie),'-progress','pipe:1','-f','null','NUL'])
counts=re.findall(r'^frame=(\d+)',decoded.stdout,re.M)
assert counts and int(counts[-1])==120,counts[-1:]
assert '3840x2160' in decoded.stderr and '24 fps' in decoded.stderr,decoded.stderr[:3000]
assert 'Audio:' in decoded.stderr and '48000 Hz' in decoded.stderr
run(['-v','error','-i',str(movie),'-vf','scale=1920:1080:flags=lanczos','-c:v','libx264','-crf','18','-preset','fast','-threads','4','-c:a','copy','-movflags','+faststart','-n',str(small)])
heads=D/'decoded_4K_head_turn';heads.mkdir(exist_ok=True)
run(['-v','error','-i',str(movie),'-vf',r'select=between(n\,38\,49),crop=750:750:1900:500','-fps_mode','vfr','-start_number','1839','-frames:v','12','-threads','2',str(heads/'%04d.png')])
dense=D/'decoded_4K_actor_chronology';dense.mkdir(exist_ok=True)
run(['-v','error','-i',str(movie),'-vf',r'select=not(mod(n\,3)),crop=1440:1200:1400:480,scale=720:600:flags=lanczos','-fps_mode','vfr','-start_number','0','-frames:v','40','-threads','2',str(dense/'%03d.png')])
whole=D/'decoded_4K_whole_keys';whole.mkdir(exist_ok=True);frames=[1801,1825,1841,1844,1848,1881,1901,1920]
select='+'.join(f'eq(n\\,{f-1801})' for f in frames)
run(['-v','error','-i',str(movie),'-vf','select='+select,'-fps_mode','vfr','-frames:v','8','-threads','2',str(whole/'%02d.png')])
font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf',24)
def canvas(size):return Image.new('RGB',size,(18,18,18))
def save(im,name):p=E/name;im.save(p,quality=96);return str(p)
head_sheets=[]
for group in range(2):
 im=canvas((2266,1576));draw=ImageDraw.Draw(im)
 for j,frame in enumerate(range(1839+group*6,1845+group*6)):
  x=8+j%3*754;y=8+j//3*780;draw.text((x,y),f'{frame} / {(frame-1)/24:.3f}s | actual4K pixels',font=font,fill='white')
  im.paste(Image.open(heads/f'{frame}.png').convert('RGB'),(x,y+30))
 head_sheets.append(save(im,f'Head_Turn_Actual4K_Consecutive_{group+1}.jpg'))
chronology=[]
for group in range(5):
 im=canvas((2920,1280));draw=ImageDraw.Draw(im)
 for j in range(8):
  index=group*8+j;frame=1801+index*3;x=8+j%4*728;y=8+j//4*636
  draw.text((x,y),f'{frame} / {(frame-1)/24:.3f}s | actual4K-derived crop',font=font,fill='white')
  im.paste(Image.open(dense/f'{index:03d}.png').convert('RGB'),(x,y+30))
 chronology.append(save(im,f'Actor_Chronology_{group+1}.jpg'))
before=R/'renders/world_v016/integration_v046/Native_v046_1844_4K.png'
im=canvas((1508,792));draw=ImageDraw.Draw(im);draw.text((8,4),'v046 BEFORE /1844 | native4K pixels',font=font,fill='white');draw.text((762,4),version+' AFTER /1844 | native4K pixels',font=font,fill='white')
im.paste(Image.open(before).convert('RGB').crop((1900,500,2650,1250)),(0,36));im.paste(Image.open(heads/'1844.png').convert('RGB'),(758,36))
head_before_after=save(im,'Head_Before_After_1844_Native4KPixels.jpg')
im=canvas((1920,1112));draw=ImageDraw.Draw(im)
for row,(label,path) in enumerate([('v046 BEFORE /1901',R/'renders/world_v016/integration_v046/Native_v046_1901_4K.png'),(version+' AFTER /1901',D/'Full_1901_4K.png')]):
 draw.text((8,row*556+4),label+' | actual4K image shown at50percent',font=font,fill='white');im.paste(Image.open(path).convert('RGB').resize((1920,1080),Image.Resampling.LANCZOS).crop((0,560,1920,1080)),(0,row*556+36))
ground_before_after=save(im,'Ground_Before_After_1901.jpg')
im=canvas((1936,2320));draw=ImageDraw.Draw(im)
for j,frame in enumerate(frames):
 x=8+j%2*968;y=8+j//2*580;draw.text((x,y),f'{frame} / {(frame-1)/24:.3f}s | decoded actual4K',font=font,fill='white');im.paste(Image.open(whole/f'{j+1:02d}.png').convert('RGB').resize((960,540),Image.Resampling.LANCZOS),(x,y+32))
whole_sheet=save(im,'Whole_Shot_Chronology_Actual4K.jpg')
def audio(path):
 r=subprocess.run([F,'-v','error','-i',str(path),'-map','0:a:0','-ar','48000','-ac','2','-f','s16le','-'],capture_output=True);assert r.returncode==0
 return np.frombuffer(r.stdout,dtype='<i2').astype(float).reshape(-1,2)[:240000]
original=R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'
r=subprocess.run([F,'-v','error','-ss','75','-t','5','-i',str(original),'-ar','48000','-ac','2','-f','s16le','-'],capture_output=True);assert r.returncode==0
a=np.frombuffer(r.stdout,dtype='<i2').astype(float).reshape(-1,2)[:240000];b=audio(movie);length=min(len(a),len(b));correlation=float(np.corrcoef(a[:length].flatten(),b[:length].flatten())[0,1]);assert correlation>.99,correlation
def item(path):return {'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
report=json.loads((N/f'build_{version}.json').read_text());assert hashlib.sha256(Path(report['native']).read_bytes()).hexdigest()==report['sha256']
result={'native':item(Path(report['native'])),'movie4K':item(movie),'view1080p':item(small),
 'actual_frames_decoded':120,'resolution':[3840,2160],'fps':24,'duration_seconds':5,
 'music75_80_original_correlation':correlation,'head_consecutive_frames':[1839,1850],'head_sheets':head_sheets,
 'actor_chronology_sheets':chronology,'whole_shot_chronology':whole_sheet,'before_after_head':head_before_after,'before_after_ground':ground_before_after,
 'method':'Actual native4K frames and decoded movie frames. Analysis-only crops/downsampled sheets; no synthetic motion or frame interpolation.',
 'visual_inspection_complete':False,'artistic_acceptance':False,'full_trailer_propagated':False}
(N/f'media_qa_{version}.json').write_text(json.dumps(result,indent=2));print('V047_MEDIA_REVIEW_READY',version,json.dumps(result),flush=True)
