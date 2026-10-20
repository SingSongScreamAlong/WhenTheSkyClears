from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,subprocess,hashlib
import imageio_ffmpeg
P=Path(__file__).resolve().parents[1];BASE=P.parent/'full_color_coat_continuity_v039/previews';FONT='C:/Windows/Fonts/segoeui.ttf'
def label(d,p,s,n=24):d.text(p,s,font=ImageFont.truetype(FONT,n),fill='#e6e5dc')
board=Image.new('RGB',(1920,2460),'#202725');d=ImageDraw.Draw(board);label(d,(28,12),'WHEN THE SKY CLEARS  |  v040 PAINTED LOOK STUDY',34);label(d,(28,58),'Same body motion. New painted profile, hair and material treatment. Design direction remains under review.',24)
for x,src,name in [(0,P/'previews/BASELINE_HERO/0001.png','v039 | earlier look'),(960,P/'previews/HERO/0001.png','v040 | painted native study')]:
 label(d,(x+28,104),name,28);board.paste(Image.open(src).convert('RGB'),(x,150))
for i,(f,view) in enumerate([(11,'before'),(11,'after'),(20,'before'),(20,'after')]):
 x=i*480;label(d,(x+16,1620),f'F{f} | '+('v039' if view=='before' else 'v040'),25);src=(BASE if view=='before' else P/'previews')/f'CLOSE/{f:04d}.png';board.paste(Image.open(src).convert('RGB'),(x,1660))
label(d,(28,2397),'Actual native renders. Head is a fixed-profile painted mesh; body/hand contours and paired acting still need work.',22);bp=P/'previews/WTSC_v040_Native_Character_Look_Comparison.png';board.save(bp)
out=P/'previews/WTSC_v040_vs_v039_Same_Movement_Look_Study.mp4';ff=imageio_ffmpeg.get_ffmpeg_exe();size=(1280,840);cmd=[ff,'-y','-v','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','1280x840','-r','30','-i','-','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)];proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
for section in ['MATCHED CLOSE','MATCHED SHOT AT 50%','CANDIDATE NATIVE SHOT']:
 for f in range(1,95):
  canvas=Image.new('RGB',size,'#202725');d=ImageDraw.Draw(canvas);label(d,(24,10),'WHEN THE SKY CLEARS  |  v040 PAINTED LOOK STUDY',27);label(d,(24,47),f'{section}  |  same body motion  |  30 fps  |  F{f:02d}',21)
  if section=='MATCHED CLOSE':
   for x,root in [(160,BASE),(640,P/'previews')]:canvas.paste(Image.open(root/f'CLOSE/{f:04d}.png').convert('RGB'),(x,86))
   label(d,(24,150),'v039',22);label(d,(1140,150),'v040',22)
  elif section=='MATCHED SHOT AT 50%':
   for x,root in [(0,BASE),(640,P/'previews')]:canvas.paste(Image.open(root/f'SHOT/{f:04d}.png').convert('RGB').resize((640,360),Image.Resampling.LANCZOS),(x,236))
   label(d,(24,194),'v039 | 50% view',22);label(d,(664,194),'v040 | 50% view',22);label(d,(24,650),'These comparison panels are reduced. The full native-size candidate shot follows.',21)
  else:canvas.paste(Image.open(P/f'previews/SHOT/{f:04d}.png').convert('RGB'),(0,86))
  label(d,(24,812),'ROUGH DESIGN TEST | Fixed-profile painted head. No new acting or production integration.',18);proc.stdin.write(canvas.tobytes())
proc.stdin.close();err=proc.stderr.read().decode();rc=proc.wait();assert rc==0,err
reader=imageio_ffmpeg.read_frames(str(out),pix_fmt='rgb24');meta=next(reader);count=0;selected=[]
for i,raw in enumerate(reader):
 if i in [0,3,10,19,26,31,62,93,94,104,113,120,187,188,198,207,214,219,250,281]:
  folder=P/'previews/DECODED';folder.mkdir(exist_ok=True);p=folder/f'{i:04d}.png';Image.frombytes('RGB',size,raw).save(p);selected.append({'zero_based_movie_frame':i,'section':i//94,'source_frame':i%94+1,'image':str(p.relative_to(P))})
 count+=1
assert count==282 and meta['fps']==30 and out.stat().st_size<20_000_000
report={'file':str(out.relative_to(P)),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'dimensions':size,'fps':meta['fps'],'decoded_frames':count,'duration_seconds':count/30,'source_frames_per_section':[1,94],'sections':['Matched close at native480x720 per panel','Matched shot at50percent640x360 per panel','Candidate shot at full native1280x720'],'old_new_walk_actions_identical':True,'new_candidate_source_images_per_camera':94,'cycles_per_section':3,'closing_pose_included':True,'actual_native_cycles_rendered_not_one_cycle_recycled':True,'AI_generated_movie':False,'new_paint_origin':'Unedited generated parts atlas, registered to editable native meshes; new fixed-profile head paint mesh bound to original head bone.','board':str(bp.relative_to(P)),'board_dimensions':board.size,'board_bytes':bp.stat().st_size,'decoded_inspection_frames':selected,'observation_limit':'Actual encoded movie decoded and selected frames inspected. No continuous video-player observation claimed.'};(P/'evidence/COMPARISON_ENCODING_AND_DECODE.json').write_text(json.dumps(report,indent=2));print('V040_COMPARISON_COMPLETE',json.dumps({k:v for k,v in report.items() if k!='decoded_inspection_frames'}))
