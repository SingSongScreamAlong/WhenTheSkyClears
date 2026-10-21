"""Decode existing movies and make chronological animation evidence boards."""
import hashlib, io, json, re, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
FF=imageio_ffmpeg.get_ffmpeg_exe()
FLAGS=subprocess.CREATE_NO_WINDOW
SOURCES={
 'full_v040':('renders/world_v016/WTSC_Full_Knockout_Trailer_View_v040.mp4',2544),
 'walk_v053':('locomotion/authored_walk_beats_v053/previews/WTSC_Authored_Walk_Beats_v053_Full_Size_NormalSpeed.mp4',257),
 'girl_v056':('locomotion/girl_yoke_drape_v056/previews/WTSC_Girl_Yoke_v056_FullShot_NormalSpeed.mp4',65),
 'danger_v065f':('work/first_danger_conform_v065/previews/WTSC_First_Danger_Title_v065f_View.mp4',168),
 'recovery_v059':('work/production_review_v059/WTSC_Recovery_Benchmark_v059_720p.mp4',120),
}
def run(args):
 return subprocess.run([FF,'-hide_banner','-nostdin',*args],capture_output=True,timeout=90,creationflags=FLAGS)
report=json.loads((OUT/'media_readback.json').read_text()) if '--boards-only' in sys.argv else {}
for label,(rel,expected) in SOURCES.items():
 if '--boards-only' in sys.argv: continue
 p=ROOT/rel;before=hashlib.sha256(p.read_bytes()).hexdigest()
 result=run(['-v','error','-i',str(p),'-map','0:v:0','-progress','pipe:1','-f','null','NUL'])
 counts=re.findall(r'^frame=(\d+)',result.stdout.decode(),re.M)
 report[label]={'path':rel,'sha256':before,'expected_frames':expected,
  'decoded_frames':int(counts[-1]) if counts else None,'returncode':result.returncode,
  'stderr':result.stderr.decode(errors='replace')[-600:]}
 report[label]['passed']=result.returncode==0 and report[label]['decoded_frames']==expected
 print('DECODE',label,report[label]['decoded_frames'],flush=True)

font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
def frame(label,index):
 p=ROOT/SOURCES[label][0]
 r=run(['-v','error','-i',str(p),'-vf',f'select=eq(n\\,{index}),scale=960:540',
        '-frames:v','1','-fps_mode','vfr','-f','image2pipe','-vcodec','png','pipe:1'])
 if r.returncode or not r.stdout: raise RuntimeError(r.stderr.decode(errors='replace'))
 return Image.open(io.BytesIO(r.stdout)).convert('RGB')

def board(name,entries,crop=None):
 cells=[]
 for label,index,caption in entries:
  im=frame(label,index)
  if crop: im=im.crop(crop)
  im.thumbnail((560,350))
  cells.append((im,caption))
 cols=3;cw=570;ch=385
 canvas=Image.new('RGB',(cols*cw,((len(cells)+cols-1)//cols)*ch),'#171c23')
 draw=ImageDraw.Draw(canvas)
 for n,(im,caption) in enumerate(cells):
  x=n%cols*cw;y=n//cols*ch
  draw.text((x+10,y+8),caption,font=font,fill='white')
  canvas.paste(im,(x+(cw-im.width)//2,y+36))
 canvas.save(OUT/name,quality=94)

board('walk_one_cycle.jpg',[('walk_v053',i,f'v053 | source frame {i+1} | {i/30:.3f}s') for i in range(0,33,3)],crop=(260,65,700,540))
board('danger_action.jpg',[('danger_v065f',i,f'v065f | G{913+i} | {38+i/24:.3f}s') for i in [0,24,44,56,64,72,88,104,120,136,148,164]],crop=(290,85,675,440))
board('recovery_action.jpg',[('recovery_v059',i,f'v059 | {75+i/24:.3f}s') for i in [0,12,24,36,48,60,72,84,96,108,119]],crop=(240,100,670,440))
report['v064_delivery']={'documented_movies':{rel:(ROOT/rel).exists() for rel in [
 'work/procedural_cut_v064/previews/WTSC_Procedural_Full_Knockout_v064.mp4',
 'work/procedural_cut_v064/previews/WTSC_Procedural_Unmasked_World_v064.mp4']},
 'render_status':json.loads((ROOT/'work/procedural_cut_v064/evidence/RENDER_STATUS.json').read_text())}
(OUT/'media_readback.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('ANIMATION_MEDIA_AUDIT_COMPLETE',flush=True)
