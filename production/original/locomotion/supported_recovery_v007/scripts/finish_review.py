import json,subprocess,re,hashlib,zipfile,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];R=P.parents[1]
F=Path(r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe')
def run(args):
 r=subprocess.run([str(F),'-hide_banner','-nostdin',*args],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
 assert r.returncode==0,r.stderr
 return r
font=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',24);small=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',18)
before=json.loads((P/'evidence/preservation_before.json').read_text());preservation={p:hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in before.items()};assert all(preservation.values())
old=P/'previews/original_v044';old.mkdir(exist_ok=True)
run(['-y','-threads','2','-i',str(R/'renders/world_v016/integration_v044/WTSC_Drawn_Open_75_80_View_v044.mp4'),'-vf','scale=960:540','-frames:v','120','-threads','2',str(old/'%04d.png')])
ab=P/'previews/ab';ab.mkdir(exist_ok=True)
for f in range(1,121):
 for folder in ['neutral','integrated']:assert (P/f'previews/{folder}/{f:04d}.png').exists()
 canvas=Image.new('RGB',(1920,592),(24,28,31));d=ImageDraw.Draw(canvas)
 canvas.paste(Image.open(old/f'{f:04d}.png').convert('RGB'),(0,52));canvas.paste(Image.open(P/f'previews/integrated/{f:04d}.png').convert('RGB'),(960,52))
 d.text((18,9),f'v044 BASELINE / EEVEE / {75+(f-1)/24:.3f}s',font=font,fill=(232,228,216));d.text((978,9),'v007 SUPPORT + LOOK BACK / EEVEE / MATCHED CAMERA',font=font,fill=(232,228,216));canvas.save(ab/f'{f:04d}.png')
videos=[]
for folder,name in [('neutral','WTSC_v007_Neutral_5s.mp4'),('integrated','WTSC_v007_Integrated_5s.mp4'),('ab','WTSC_v044_vs_v007_Matched_Framing.mp4')]:
 path=P/name;run(['-y','-framerate','24','-start_number','1','-i',str(P/f'previews/{folder}/%04d.png'),'-frames:v','120','-an','-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(path)])
 r=run(['-v','error','-threads','2','-i',str(path),'-progress','pipe:1','-f','null','NUL']);decoded=int(re.findall(r'^frame=(\d+)',r.stdout,re.M)[-1]);assert decoded==120 and path.stat().st_size<20_000_000
 videos.append({'path':name,'frames':120,'fps':24,'seconds':5,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
frames=[1,31,37,43,47,58,71,81,89,101,110,120]
for folder,name in [('neutral','WTSC_v007_Neutral_Contact_Sheet.jpg'),('integrated','WTSC_v007_Integrated_Contact_Sheet.jpg')]:
 sheet=Image.new('RGB',(1920,1604),(24,28,31));d=ImageDraw.Draw(sheet);d.text((20,16),'WHEN THE SKY CLEARS / v007 DRAWN CORRECTION REVIEW / '+folder.upper(),font=font,fill=(232,228,216))
 for i,f in enumerate(frames):
  x=10+(i%3)*640;y=62+(i//3)*381;im=Image.open(P/f'previews/{folder}/{f:04d}.png').convert('RGB')
  if folder=='neutral':im=im.crop((120,90,840,495))
  im=im.resize((620,349),Image.Resampling.LANCZOS);sheet.paste(im,(x,y));d.text((x+8,y+354),f'F{f:03d} / {75+(f-1)/24:.3f}s',font=small,fill=(218,217,208))
 sheet.save(P/name,quality=94)
# Full-size character crops from actual matched frames, with identical crop and
# scale on both versions; no character reconstruction or background replacement.
sheet=Image.new('RGB',(1920,6*395+52),(24,28,31));d=ImageDraw.Draw(sheet);d.text((20,10),'SAME FRAME / LEFT v044 / RIGHT v007 / CAMERA CROP / SAME EEVEE RENDERER',font=font,fill='white')
for i,f in enumerate([43,47,58,89,101,120]):
 y=52+i*395
 for col,folder in enumerate(['original_v044','integrated']):
  im=Image.open(P/f'previews/{folder}/{f:04d}.png').convert('RGB').crop((335,155,735,410)).resize((588,375),Image.Resampling.LANCZOS)
  x=col*960+180;sheet.paste(im,(x,y));d.text((col*960+12,y+10),f'F{f:03d}\n{75+(f-1)/24:.3f}s',font=font,fill='white')
sheet.save(P/'WTSC_v044_vs_v007_Pose_Comparison.jpg',quality=94)

# Existing original projection metadata is valid because the camera and boot
# sole trajectories are unchanged. Check actual rendered planted boot patches
# against actual traveling ground, excluding roll and airborne frames.
projection=json.loads((R/'locomotion/battlefield_proof_v005/evidence/projection_samples.json').read_text());lookup={r['frame']:r for r in projection}
def corr(a,b):
 a=a-a.mean();b=b-b.mean();return float((a*b).sum()/max(1e-9,np.sqrt((a*a).sum()*(b*b).sum())))
def shift(a,b,box):
 x0,y0,x1,y1=box;tpl=a[y0:y1,x0:x1]
 if tpl.size==0 or tpl.std()<1:return None
 return max((corr(tpl,b[y0:y1,x0+dx:x1+dx]),dx) for dx in range(-12,13) if x0+dx>=0 and x1+dx<b.shape[1])
prev=None;meta0=None;matches=[];settle=[];settle0=None
for f in range(1,121):
 a=np.array(Image.open(P/f'previews/neutral/{f:04d}.png').convert('L'),dtype=np.float32);m=lookup[f];floor=m['floor_row_pixels']
 if f==81:settle0=a[150:480,320:765]<90
 if f>=81:settle.append({'frame':f,'changed_silhouette_pixels_from81':int(np.count_nonzero((a[150:480,320:765]<90)!=settle0))})
 if prev is not None:
  gy=int(round(m['ground_row_pixels']));g=shift(prev,a,(100,gy-1,860,gy+2))
  for ft in m['feet']:
   b=next(q for q in meta0['feet'] if q['who']==ft['who'] and q['side']==ft['side'])
   if not(ft['contact'] and b['contact'] and abs(ft['pitch'])<1e-5 and abs(b['pitch'])<1e-5):continue
   x0,_,x1,_=b['bounds_pixels'];x0=max(15,int(math.floor(x0))+3);x1=min(944,int(math.ceil(x1))-3)
   if x1-x0<17:continue
   y1=int(math.floor(floor))-1;shoe=shift(prev,a,(x0,y1-19,x1,y1))
   if shoe and g and shoe[0]>.65 and g[0]>.45:matches.append({'frame':f,'who':ft['who'],'side':ft['side'],'error_px':shoe[1]-g[1]})
 prev=a;meta0=m
report={'videos':videos,'source_preservation':preservation,'rendered_planted_boot_vs_ground':{'method':'Independent normalized pixel correlation of actual flat planted boot patches versus visible ground ticks, roll/airborne frames excluded.','matches':len(matches),'max_abs_error_pixels':max(abs(m['error_px']) for m in matches),'samples':matches},'actual_post_stop_silhouette_changes':settle,'artistic_review':'Shot-size and critical-crop review: projected boot/shin paths separate during76.7..77.3; girl stabilizes, turns toward boy and offers her hand; boy braces his thigh, prepares weight forward after stop, reaches and rises visibly. Original sole/shoe/art basis retained. The fast2D head exposure and stylized fingertip clasp remain limited; no cinematic acceptance.','renderer_limit':'Same production EEVEE renderer and settings, camera/world/FX/light/route; v007 actual render960x540, v044 reference1920x1080 downsampled to960x540. No renderer switch or background replacement.'}
(P/'evidence/final_review.json').write_text(json.dumps(report,indent=2));print('V007_REELS_AND_REVIEW_COMPLETE',json.dumps(videos),flush=True)
