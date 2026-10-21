from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,math,hashlib,imageio_ffmpeg
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];D=P/'previews';OLD=P/'reference/V020_COMPARISON';SOL=json.loads((P/'evidence/coherent_pose_solution.json').read_text());ph=SOL['poses'];res={r['phase']:r for r in json.loads((P/'evidence/v020_v021_angle_comparison.json').read_text())};F=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',28);SM=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20);(D/'SLIDES').mkdir(exist_ok=True)
slides=[]
for p in ph:
 im=Image.new('RGB',(1920,960),'#eee9dd');d=ImageDraw.Draw(im);r=res[p['name']];d.text((20,8),'V021 | coherent child support poses | source reference only | no finished walk',font=F,fill='#282624');d.text((20,47),'%s | source f%.2f | largest leg residual %.1f -> %.1f deg | stride1.021 -> %.3fm'%(p['name'],p['unwrapped_source_frame'],r['v020_max_leg_error_deg'],r['v021_max_leg_error_deg'],SOL['cycle_stride_m']),font=SM,fill='#282624')
 for i,(mode,label) in enumerate([('SOURCE','Source skeleton / adult reference'),('CHILD_SKELETON','Corrected native child skeleton'),('PAINTED','Same corrected pose / original paint')]):
  d.text((i*640+14,84),label+' / CLOSE',font=SM,fill='#282624');im.paste(Image.open(D/f'{mode}_CLOSE/{p["index"]:02d}.png').convert('RGB'),(i*640,112));d.text((i*640+14,500),'Original v046 camera size',font=SM,fill='#282624');im.paste(Image.open(D/f'{mode}_SHOT/{p["index"]:02d}.png').convert('RGB'),(i*640,532))
 d.text((20,914),'Equal0.5s display holds; same actual source phases. No child in-betweens, cadence or performance approval.',font=SM,fill='#282624');im.save(D/f'SLIDES/{p["index"]:02d}.png');slides.append(im)
# Separate whole-pose variant, with exactly the same skeleton and foot goals.
art=Image.new('RGB',(1920,1440),'#eee9dd');d=ImageDraw.Draw(art)
for i,label in enumerate(['BEFORE','AFTER']):
 x=i*960;d.text((x+20,8),label+' | L_PASSING | same skeleton and feet',font=F,fill='#282624');a=Image.open(D/f'ART_VARIANT/{label}_CLOSE.png').convert('RGB');art.paste(a,(x,45));d.text((x+20,598),'Original camera size',font=SM,fill='#282624');art.paste(Image.open(D/f'ART_VARIANT/{label}_SHOT.png').convert('RGB').resize((640,360)),(x+160,630));d.text((x+160,1000),'Knee/calf detail',font=SM,fill='#282624');d.text((x+500,1000),'Waist/cloth detail',font=SM,fill='#282624');art.paste(a.crop((390,345,575,525)).resize((320,311)),(x+140,1035));art.paste(a.crop((390,205,600,365)).resize((320,244)),(x+500,1035))
d.text((20,1385),'Minimal geometry-only study: modest contour change; painted band and rigid cloth drawing remain unpassed.',font=SM,fill='#282624');art.save(D/'WTSC_v021_Passing_Whole_Pose_Corrective_Before_After.jpg',quality=95)
last=Image.new('RGB',(1920,960),'#eee9dd');ld=ImageDraw.Draw(last);ld.text((20,8),'Separate one-pose art study | source L_PASSING | same skeleton / feet / painting',font=F,fill='#282624')
for i,label in enumerate(['BEFORE','AFTER']):
 x=i*960;ld.text((x+30,52),label+' / whole pose',font=SM,fill='#282624');last.paste(Image.open(D/f'ART_VARIANT/{label}_CLOSE.png').convert('RGB').resize((800,450)),(x+80,85));ld.text((x+30,555),'Original camera size',font=SM,fill='#282624');last.paste(Image.open(D/f'ART_VARIANT/{label}_SHOT.png').convert('RGB').resize((480,270)),(x+240,590))
ld.text((20,915),'Waist/hem and knee/calf offsets only. This modest study does not resolve the painted strip or approve the walk.',font=SM,fill='#282624');last.save(D/'SLIDES/09.png');slides.append(last)
movie=D/'WTSC_v021_Support_Pose_Correction_and_Art_Study_5s.mp4';writer=imageio_ffmpeg.write_frames(str(movie),(1920,960),fps=30,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',quality=8,ffmpeg_log_level='error',output_params=['-threads','2','-crf','18','-preset','medium','-movflags','+faststart']);writer.send(None)
for i,im in enumerate(slides):
 for _ in range(15 if i<8 else 30):writer.send(im.tobytes())
writer.close()
board=Image.new('RGB',(1920,1620),'#eee9dd');dr=ImageDraw.Draw(board)
for j,(index,text) in enumerate([(5,'Second landing: pelvis/legs solved together'),(6,'Second loading: no post-fit pelvis projection'),(8,'Swing boot: actual sole clearance restored')]):
 y=j*540;dr.text((20,y+8),text,font=F,fill='#282624');dr.text((20,y+47),'v020 BEFORE',font=SM,fill='#282624');dr.text((980,y+47),'v021 CORRECTED',font=SM,fill='#282624')
 for i,path in enumerate([OLD/f'PAINTED_CLOSE/{index:02d}.png',D/f'PAINTED_CLOSE/{index:02d}.png']):board.paste(Image.open(path).convert('RGB').resize((800,450)),(i*960+80,y+70))
board.save(D/'WTSC_v021_Matching_Correction_Before_After.jpg',quality=95)
# Every unique slide is decoded from the actual movie, not just its inputs.
reader=imageio_ffmpeg.read_frames(str(movie),pix_fmt='rgb24');meta=next(reader);wanted=[1+15*i for i in range(8)]+[121];decoded=[]
for i,raw in enumerate(reader,1):
 if i in wanted:decoded.append(Image.frombytes('RGB',meta['size'],raw))
qa=Image.new('RGB',(1920,1440),'#eee9dd')
for i,im in enumerate(decoded):qa.paste(im.resize((640,320)),((i%3)*640,(i//3)*480))
qa.save(P/'evidence/ENCODED_UNIQUE_SLIDE_REVIEW.jpg',quality=94)
v={'movie':str(movie.resolve()),'bytes':movie.stat().st_size,'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'frames':150,'fps':30,'duration_seconds':5,'dimensions':meta['size'],'unique_slides':9,'all_unique_slides_decoded':len(decoded),'presentation':'Eight source-phase pose slides held0.5s each, plus separate same-pose art before/after held1s. No child motion interpolation or normal-speed gait observation.'};(P/'evidence/preview_verification.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
