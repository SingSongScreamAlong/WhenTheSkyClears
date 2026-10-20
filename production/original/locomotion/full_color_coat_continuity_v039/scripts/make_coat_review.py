from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,subprocess,sys
import numpy as np
import imageio_ffmpeg
P=Path(__file__).resolve().parents[1];fontpath=Path('C:/Windows/Fonts/segoeui.ttf')
def font(n):return ImageFont.truetype(str(fontpath),n)
def label(d,p,s,n=24,fill='#e8e7dd'):d.text(p,s,font=font(n),fill=fill)
F=[1,4,8,11,13,17,20,24,27,31,32];board=Image.new('RGB',(1920,1240),'#202725');d=ImageDraw.Draw(board);label(d,(28,14),'v039  |  ROUGH COAT CONTINUITY  |  actual native frames',30);label(d,(28,59),'One 31-frame cycle + closing pose. Preferred body motion and full-color palette retained.',22)
for i,f in enumerate(F):
 x=(i%6)*320;y=112+(i//6)*552;im=Image.open(P/f'previews/CLOSE/{f:04d}.png').convert('RGB');im.thumbnail((320,480),Image.Resampling.LANCZOS);board.paste(im,(x,y));label(d,(x+12,y+487),f'F{f:02d}'+(' / closing pose' if f==32 else ''),22)
label(d,(1616,720),'CHECKS',23);label(d,(1616,760),'Compression',21);label(d,(1616,795),'Hem response',21);label(d,(1616,830),'Hand overlap',21);label(d,(1616,865),'Paint registration',21);label(d,(28,1200),'Fitted/flat coat volume and crowded passing feet remain. This is not final animation.',22);bp=P/'previews/WTSC_v039_Coat_Cycle_Proof.png';board.save(bp)
if '--proof' in sys.argv:print('PROOF_BOARD',str(bp));raise SystemExit(0)
out=P/'previews/WTSC_v039_Full_Color_Coat_Normal_Speed_Rough.mp4';ff=imageio_ffmpeg.get_ffmpeg_exe();size=(1280,840);cmd=[ff,'-y','-v','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{size[0]}x{size[1]}','-r','30','-i','-','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)];proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
for view in ['CLOSE','SHOT']:
 for f in range(1,95):
  canvas=Image.new('RGB',size,'#202725');d=ImageDraw.Draw(canvas);label(d,(24,12),'WHEN THE SKY CLEARS  |  v039  |  ROUGH CONTINUITY TEST',25);label(d,(24,49),f'{view}  /  normal speed 30 fps  /  three native cycles + closing pose  /  F{f:02d}',20);im=Image.open(P/f'previews/{view}/{f:04d}.png').convert('RGB');canvas.paste(im,((1280-im.width)//2,86));label(d,(24,811),'Body motion unchanged. Coat: one 31-frame authored cycle. No final artistic acceptance.',18);proc.stdin.write(canvas.tobytes())
proc.stdin.close();err=proc.stderr.read().decode();rc=proc.wait();assert rc==0,err
reader=imageio_ffmpeg.read_frames(str(out),pix_fmt='rgb24');meta=next(reader);count=0;decoded=[]
for i,raw in enumerate(reader):
 if i in [0,3,10,19,26,30,31,61,62,92,93,94,104,113,120,125,156,187]:
  img=Image.frombytes('RGB',size,raw);dest=P/f'previews/DECODED/{i:04d}.png';dest.parent.mkdir(exist_ok=True);img.save(dest);decoded.append({'movie_frame_zero_based':i,'section':'CLOSE' if i<94 else 'SHOT','source_frame':i%94+1,'image':str(dest.relative_to(P))})
 count+=1
assert count==188 and abs(meta['fps']-30)<1e-6 and out.stat().st_size<20_000_000
report={'preview':str(out.relative_to(P)),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'dimensions':size,'fps':meta['fps'],'decoded_frames':count,'duration_seconds':count/30,'sections':[{'view':'CLOSE','movie_frames_zero_based':[0,93],'source_native_frames':[1,94],'scaling':'Original480x720 centered; no enlargement.'},{'view':'SHOT','movie_frames_zero_based':[94,187],'source_native_frames':[1,94],'scaling':'Original1280x720 at native pixels.'}],'unique_native_frames_per_camera':94,'native_render_total_images':188,'recycled_native_cycle_frames':False,'authored_coat_cycle':[1,32],'cycles_repeated_natively':3,'body_root_unwrapped':True,'closing_pose_included':True,'audio':False,'decoded_inspection_images':decoded,'observation_limit':'Actual movie decoded for pixel/frame checks. No continuous video-player playback observation claimed.','proof_board':str(bp.relative_to(P))};(P/'evidence/PREVIEW_ENCODING_AND_DECODE.json').write_text(json.dumps(report,indent=2));print('V039_PREVIEW_ENCODED',json.dumps({k:v for k,v in report.items() if k!='decoded_inspection_images'}))
