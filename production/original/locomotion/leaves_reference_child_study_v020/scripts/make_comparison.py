from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,csv,subprocess,hashlib
import imageio_ffmpeg
P=Path(__file__).resolve().parents[1];D=P/'previews';ph=json.loads((P/'reference/SOURCE_PHASE_TIMING_v020.json').read_text())['phases'];(D/'SLIDES').mkdir(exist_ok=True)
F=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',28);SM=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
slides=[]
for p in ph:
 im=Image.new('RGB',(1920,960),'#eee9dd');d=ImageDraw.Draw(im);d.text((20,8),'V020 | eight matched poses | adult reference only | no finished walk',font=F,fill='#282624');d.text((20,47),p['name']+' | source f%.2f (wrapped %.2f) | source t%.3fs | study +%.3fs'%(p['unwrapped_source_frame'],p['wrapped_source_frame'],p['source_seconds_from_first_key'],p['seconds_from_study_contact']),font=SM,fill='#282624')
 for i,(mode,title) in enumerate([('SOURCE','Source skeleton (native adult metres)'),('CHILD_SKELETON','Child native skeleton (original proportions)'),('PAINTED','Painted child (same native pose)')]):
  d.text((i*640+14,84),title+' / CLOSE',font=SM,fill='#282624');im.paste(Image.open(D/f'{mode}_CLOSE/{p["index"]:02d}.png').convert('RGB'),(i*640,112));d.text((i*640+14,500),'Original v046 camera size / '+title.split(' (')[0],font=SM,fill='#282624');im.paste(Image.open(D/f'{mode}_SHOT/{p["index"]:02d}.png').convert('RGB'),(i*640,532))
 d.text((20,914),'Equal 0.5s display holds. Actual source times are above; this is a pose comparison, not gait playback.',font=SM,fill='#282624');file=D/f'SLIDES/{p["index"]:02d}.png';im.save(file);slides.append(im)
ff=imageio_ffmpeg.get_ffmpeg_exe();movie=D/'WTSC_v020_Leaves_Source_Child_Eight_Pose_Comparison_4s.mp4';writer=imageio_ffmpeg.write_frames(str(movie),(1920,960),fps=30,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',quality=8,ffmpeg_log_level='error',output_params=['-threads','2','-crf','18','-preset','medium','-movflags','+faststart']);writer.send(None)
for im in slides:
 for _ in range(15):writer.send(im.tobytes())
writer.close()
board=Image.new('RGB',(1440,2640),'#eee9dd');dr=ImageDraw.Draw(board)
for j,p in enumerate(ph):
 y=j*330;dr.text((14,y+5),'%s | src f%.2f / %.3fs | study +%.3fs'%(p['name'],p['unwrapped_source_frame'],p['source_seconds_from_first_key'],p['seconds_from_study_contact']),font=SM,fill='#282624')
 for i,mode in enumerate(['SOURCE','CHILD_SKELETON','PAINTED']):
  dr.text((i*480+12,y+29),mode,font=SM,fill='#282624');a=Image.open(D/f'{mode}_CLOSE/{p["index"]:02d}.png').convert('RGB').resize((480,270));board.paste(a,(i*480,y+55))
board.save(D/'WTSC_v020_All_Eight_Source_Child_Poses.jpg',quality=95)
# Actual shot-size three-way contact sheet, retained separately for review.
shot=Image.new('RGB',(1440,2520),'#eee9dd');dr=ImageDraw.Draw(shot)
for j,p in enumerate(ph):
 y=j*315;dr.text((14,y+5),p['name']+' | SOURCE / CHILD SKELETON / PAINTED CHILD | original camera size',font=SM,fill='#282624')
 for i,mode in enumerate(['SOURCE','CHILD_SKELETON','PAINTED']):shot.paste(Image.open(D/f'{mode}_SHOT/{p["index"]:02d}.png').convert('RGB').resize((480,270)),(i*480,y+45))
shot.save(D/'WTSC_v020_All_Eight_At_Shot_Size.jpg',quality=95)
reader=imageio_ffmpeg.read_frames(str(movie),pix_fmt='rgb24');meta=next(reader);wanted=[1+15*i for i in range(8)];decoded=[]
for i,raw in enumerate(reader,1):
 if i in wanted:decoded.append(Image.frombytes('RGB',meta['size'],raw))
qa=Image.new('RGB',(1920,1920),'#eee9dd')
for i,im in enumerate(decoded):qa.paste(im.resize((960,480)),((i%2)*960,(i//2)*480))
qa.save(P/'evidence/ENCODED_EIGHT_SLIDE_SAMPLES.jpg',quality=94)
verification={'path':str(movie.resolve()),'bytes':movie.stat().st_size,'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'dimensions':meta['size'],'fps':30,'frames':120,'duration_seconds':4,'unique_pose_slides':8,'actual_encoded_slides_decoded':len(decoded),'presentation':'Equal0.5second holds per pose for comparison. Native study keys retain nonuniform actual source phase times. This is not normal-speed gait playback.','inspection':'Decoded each unique encoded slide and inspected pose/render sheets.'};(P/'evidence/preview_verification.json').write_text(json.dumps(verification,indent=2))
with (P/'reference/SOURCE_TO_STUDY_PHASES_v020.csv').open('w',newline='') as out:
 w=csv.writer(out);w.writerow(['index','phase','unwrapped_source_frame_30fps','wrapped_source_frame','source_seconds_from_first_key','study_seconds','study_frame_30fps'])
 for p in ph:w.writerow([p['index'],p['name'],p['unwrapped_source_frame'],p['wrapped_source_frame'],p['source_seconds_from_first_key'],p['seconds_from_study_contact'],p['study_frame_30fps']])
print(json.dumps(verification))
