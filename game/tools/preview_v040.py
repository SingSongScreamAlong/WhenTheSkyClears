"""Encode genuine native gameplay frames; preserve unmodified PNG captures."""
from pathlib import Path
import json,subprocess,hashlib,shutil
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
P=Path(__file__).resolve().parents[1];E=P/'evidence/v040';C=E/'release_final/crossing-capture';F=C/'crossing_frames';O=E/'freight_preview';O.mkdir(exist_ok=True)
report=json.loads((C/'capture_report.json').read_text());frames=sorted(F.glob('*.jpg'))
assert len(frames)==report['frames'] and report['reached_gate'] and report['deaths']==0
size=Image.open(frames[0]).size;assert all(Image.open(p).size==size for p in frames)
ff=imageio_ffmpeg.get_ffmpeg_exe();full=O/'WTSC_v040_Freight_Crossing_Full_Gameplay.mp4'
def run(cmd):
 r=subprocess.run(cmd,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW);assert r.returncode==0,r.stderr[-2500:];return r
run([ff,'-y','-framerate','30','-i',str(F/'%05d.jpg'),'-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(full)])
gap=next(x['frame'] for x in report['phase_events'] if x['phase']=='gap')
start=max(0,gap-60);count=min(480,len(frames)-start)
short=O/'WTSC_v040_Motion_Preview.mp4'
run([ff,'-y','-ss',str(start/30),'-i',str(full),'-t',str(count/30),'-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(short)])
validation={}
for movie in [full,short]:
 r=run([ff,'-v','error','-i',str(movie),'-f','null','-','-progress','pipe:1','-nostats'])
 decoded=max(int(l.split('=')[1]) for l in r.stdout.splitlines() if l.startswith('frame='));assert decoded>0 and 'progress=end' in r.stdout
 validation[movie.name]={'bytes':movie.stat().st_size,'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'decoded_frames':decoded,'fps':30,'size':size,'seconds':decoded/30,'scope':'Uncut native automated gameplay after the rehearsal start; no actor repositioning. Short preview is a continuous excerpt. Silent.'}
shots=[('02_rest.png','Rest after finding bread'),('04_wall.png','Leaving the low beam'),('crossing_frames/00660.jpg','Jumping the broken crossing'),('09_done.png','The shared loading bar opens')]
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
board=Image.new('RGB',(1600,1030),(13,23,27));draw=ImageDraw.Draw(board)
draw.text((26,20),'WHEN THE SKY CLEARS / DEVELOPMENT 0.4.0',font=font,fill=(225,230,213))
for i,(name,label) in enumerate(shots):
 p=C/name
 assert p.exists(),name
 out=O/('WTSC_v040_Jump.jpg' if '/' in name else 'WTSC_v040_'+name);shutil.copy2(p,out)
 im=Image.open(p).convert('RGB');im.thumbnail((770,433));x=20+(i%2)*790;y=65+(i//2)*470
 board.paste(im,(x,y));draw.text((x+8,y+437),label,font=small,fill=(190,207,192))
draw.text((26,1002),'Genuine packaged gameplay captures. Automated input; no art approval or human balancing implied.',font=small,fill=(149,176,171))
board.save(O/'WTSC_v040_Gameplay_Review.jpg',quality=93)
validation['capture']={'renderer_log':str((C/'engine.log').relative_to(P)),'frames':len(frames),'report':report,'original_screenshots':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in C.glob('*.png')}}
(E/'preview_validation.json').write_text(json.dumps(validation,indent=2));print(json.dumps(validation,indent=2))
