from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,zipfile,subprocess
import imageio_ffmpeg
P=Path(__file__).resolve().parents[1];F='C:/Windows/Fonts/segoeui.ttf'
def text(im,xy,s,n=25):ImageDraw.Draw(im).text(xy,s,font=ImageFont.truetype(F,n),fill='#e7e8e0')
board=Image.new('RGB',(3600,1300),'#23302c');text(board,(22,12),'BEFORE / AFTER | same native pixels, same metric camera | before sourceF1 poses; after static anatomy',30)
for x,name,lab in [(0,'BEFORE_EXISTING_F1_SAME_SCALE.png','BEFORE: earlier source poses / whole-silhouette height labels'),(1800,'AGE10_AFTER_NEUTRAL_PROFILE.png','AFTER: age10 candidate / barefoot skull stature139 /138cm')]:
 text(board,(x+20,57),lab,25);im=Image.open(P/'previews'/name).convert('RGB');assert im.size==(1800,1200);board.paste(im,(x,100))
board.save(P/'previews/WTSC_Age10_Before_After_Common_Scale_v044.png')
wb=Image.new('RGB',(2560,1560),'#23302c')
for j,f in enumerate([241,1201]):
 y=j*780
 for x,stem,lab in [(0,'WORLD_BEFORE','BEFORE held source pair'),(1280,'WORLD_AGE10_STATIC','AFTER neutral age10 scale witness')]:
  text(wb,(x+18,y+10),f'{lab} | F{f} | same-depth2m calibrator',23);im=Image.open(P/'previews'/f'{stem}_{f:04d}_1280.png').convert('RGB');assert im.size==(1280,720);wb.paste(im,(x,y+60))
wb.save(P/'previews/WTSC_Age10_World_Scale_Witness_v044.png')
# Actual under20MB review: clearly labelled static holds, not animation proof.
movie=P/'previews/WTSC_Age10_STATIC_Scale_Review_v044.mp4';ff=imageio_ffmpeg.get_ffmpeg_exe();fps=12;w,h=1280,920;proc=subprocess.Popen([ff,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(fps),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],stdin=subprocess.PIPE)
sections=[('BEFORE_EXISTING_F1_SAME_SCALE.png','STATIC BEFORE | existing sourceF1 poses'),('AGE10_AFTER_NEUTRAL_PROFILE.png','STATIC SCALE FIRST | age10 candidate; no retarget animation'),('AGE10_FRONT_CONSTRUCTION_GUIDE.png','CONSTRUCTION ONLY | estimated joints; no front artwork'),('WORLD_AGE10_STATIC_0241_1280.png','STATIC WORLD SCALE | original camera; not a motion or lighting integration'),('WORLD_AGE10_STATIC_1201_1280.png','STATIC WORLD SCALE | same-depth2m calibrator')]
for name,lab in sections:
 frame=Image.new('RGB',(w,h),'#23302c');text(frame,(18,12),lab,24);im=Image.open(P/'previews'/name).convert('RGB');im.thumbnail((w,h-60));frame.paste(im,((w-im.width)//2,60+(h-60-im.height)//2));b=frame.tobytes()
 for _ in range(2*fps):proc.stdin.write(b)
proc.stdin.close();assert proc.wait()==0
reader=imageio_ffmpeg.read_frames(str(movie),pix_fmt='rgb24');meta=next(reader);count=sum(1 for _ in reader);assert count==120;assert movie.stat().st_size<20000000
build=json.loads((P/'evidence/STATIC_SCALE_BUILD.json').read_text());native=P/'native/WTSC_Age10_Static_Proportion_Candidate_v044.blend'
handoff={'status':'STAGE1 static scale candidate completed; age10 for both. Animation retarget has not been performed in this checkpoint.','girl_source_found':True,'no_remaining_permission_or_missing_asset_block':True,'native':{'file':str(native.relative_to(P)),'bytes':native.stat().st_size,'sha256':hashlib.sha256(native.read_bytes()).hexdigest()},'candidate_measurements':build['candidate_measurements'],'guide':'STATIC_SCALE_GUIDE_v044.txt','preview':{'file':str(movie.relative_to(P)),'bytes':movie.stat().st_size,'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'fps':12,'decoded_frames':count,'seconds':10,'static_holds_NOT_animation':True},'boards':['previews/WTSC_Age10_Before_After_Common_Scale_v044.png','previews/WTSC_Age10_World_Scale_Witness_v044.png','previews/AGE10_FRONT_CONSTRUCTION_GUIDE.png'],'artistic_status':'Coherent age10 scale construction with estimated hidden cranial landmarks; cloth remains flat and girl retains older charcoal painting. Not final character design or animation quality.','sources_unchanged':build['sources_unchanged'],'world_saved_or_rescaled':False,'next_stage':'Separate animation retarget with stance/stride/pelvis correction. Do not claim old travel already validated.'}
(P/'evidence/STATIC_STAGE_HANDOFF.json').write_text(json.dumps(handoff,indent=2))
files=[native,P/'STATIC_SCALE_GUIDE_v044.txt',movie,*[P/p for p in handoff['boards']],*list((P/'scripts').glob('*.py')),*list((P/'evidence').glob('*.json'))]
z=P/'WTSC_Age10_Static_Proportion_Candidate_v044.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,6) as Z:
 for p in files:Z.write(p,p.relative_to(P))
with zipfile.ZipFile(z) as Z:assert Z.testzip() is None
print(json.dumps({'native_bytes':native.stat().st_size,'preview_bytes':movie.stat().st_size,'preview_frames':count,'zip_bytes':z.stat().st_size,'zip_files':len(files),'source_preservation':all(build['sources_unchanged'].values())}))
