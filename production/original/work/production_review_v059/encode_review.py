from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,json,re,hashlib
import imageio_ffmpeg
R=Path(r'WTSC_LOCAL_WORKSPACE');O=R/'work/production_review_v059';F=imageio_ffmpeg.get_ffmpeg_exe()
assert (O/'renders_complete.json').exists()
font=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',23)
def run(args):
 p=subprocess.run([F,'-hide_banner','-y']+args,capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stderr[-4000:])
 return p
view=O/'WTSC_Recovery_Benchmark_v059_720p.mp4'
run(['-framerate','24','-start_number','1801','-i',str(O/'frames_world/%04d.png'),'-ss','75','-i',str(R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'),'-map','0:v:0','-map','1:a:0','-frames:v','120','-t','5','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(view)])
head=Image.new('RGB',(1920,40),(16,18,23));d=ImageDraw.Draw(head);d.text((18,4),'SOURCE v048a | earlier terrain, smoke and offered fingertips',font=font,fill=(235,235,235));d.text((978,4),'BENCHMARK v059 | latest world, painted impact, palm contact',font=font,fill=(237,204,140));head.save(O/'comparison_header.png')
old=R/'renders/refinement_v048a/WTSC_Refinement_v048a_75_80_View_1080p.mp4'
comp=O/'WTSC_Before_After_v048a_v059.mp4'
run(['-i',str(old),'-i',str(view),'-loop','1','-i',str(O/'comparison_header.png'),'-filter_complex','[0:v]scale=960:540,pad=960:580:0:40:black[a];[1:v]scale=960:540,pad=960:580:0:40:black[b];[a][b]hstack=inputs=2[c];[c][2:v]overlay=0:0[v]','-map','[v]','-map','1:a:0','-frames:v','120','-t','5','-r','24','-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(comp)])
review=O/'WTSC_Recovery_Benchmark_v059_Review.mp4'
run(['-i',str(view),'-vf','scale=960:540','-c:v','libx264','-preset','medium','-crf','25','-c:a','aac','-b:a','128k','-movflags','+faststart',str(review)])
# Chronological inspection boards: actual native renders, no generated frames.
for j in range(4):
 out=Image.new('RGB',(1920,1030),(17,18,22));draw=ImageDraw.Draw(out)
 for n in range(30):
  f=1801+j*30+n;im=Image.open(O/f'frames_world/{f:04d}.png').convert('RGB').resize((320,180))
  x=(n%6)*320;y=(n//6)*206;out.paste(im,(x,y+26));draw.text((x+5,y+1),str(f),font=font,fill='white')
 out.save(O/f'chronology_{j+1}.jpg',quality=90)
# Contact before/after at exact matched frame, no artistic image modification.
out=Image.new('RGB',(1600,600),(18,19,24));draw=ImageDraw.Draw(out)
for j,name in enumerate(['candidate_1901.png','corrected_1901.png']):
 im=Image.open(O/name).convert('RGB').crop((420,215,800,475));im=im.resize((800,547));out.paste(im,(j*800,45))
 draw.text((j*800+15,10),['BEFORE | fingertip gap','v059 | continuous palm contact'][j],font=font,fill='white')
out.save(O/'Hand_Contact_Before_After_v059.jpg',quality=94)
out=Image.new('RGB',(1280,1158),(18,19,24));draw=ImageDraw.Draw(out)
for j,f in enumerate([1844,1901,1918]):
 for k,p in enumerate([O/f'frames_world/{f}.png',O/f'title_visibility_{f}.png']):
  out.paste(Image.open(p).convert('RGB').resize((640,360)),(k*640,j*386+26))
  draw.text((k*640+10,j*386+2),str(f)+(' | unmasked' if k==0 else ' | inherited title composition'),font=font,fill='white')
out.save(O/'Title_Visibility_Review_v059.jpg',quality=92)
records={}
for p in [view,comp,review]:
 q=run(['-i',str(p),'-map','0:v:0','-f','framehash','-'])
 rows=[x for x in q.stdout.splitlines() if re.match(r'^\s*0,',x)]
 pts=[int(x.split(',')[2]) for x in rows]
 assert len(rows)==120 and pts==list(range(120)),(p, len(rows),pts[:4])
 records[p.name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'decoded_frames':len(rows),'contiguous_video_pts':True,'duration_seconds':5,'fps':24}
(O/'media_verification.json').write_text(json.dumps(records,indent=2))
print('REVIEW_MEDIA_READY',json.dumps(records),flush=True)
