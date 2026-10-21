from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg,json,hashlib
P=Path(__file__).resolve().parents[1];D=P/'previews';font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',25);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
slides=[]
for phase,src,f in [('L_LOADING',26,17.25),('L_PASSING',34,25.25)]:
 im=Image.new('RGB',(1920,1200),'#eee9dd');dr=ImageDraw.Draw(im);dr.text((20,8),f'V022 | {phase} | source f{src} / study f{f} | selected painted pose only',font=font,fill='#272522')
 for i,label in enumerate(['BEFORE','AFTER']):
  x=i*960;dr.text((x+20,52),label+' | whole pose / close',font=small,fill='#272522');im.paste(Image.open(D/f'{phase}/{label}_CLOSE.png').convert('RGB'),(x,80));dr.text((x+20,638),label+' | original v046 camera framing / neutral stage',font=small,fill='#272522');im.paste(Image.open(D/f'{phase}/{label}_SHOT.png').convert('RGB'),(x,670))
 dr.text((20,1160),'Same v021 skeleton, support and boots. Coat shape/folds and pose-specific trouser drawings. No in-betweens.',font=small,fill='#272522')
 # Bottom images end1210; crop only the empty lower stage, keeping exact character scale.
 im.save(D/f'WTSC_v022_{phase}_Before_After.jpg',quality=95);slides.append(im)
detail=Image.new('RGB',(1920,1200),'#eee9dd');dr=ImageDraw.Draw(detail);dr.text((20,8),'V022 | passing detail | original design / rolled cuffs and visible ankles retained',font=font,fill='#272522')
for i,label in enumerate(['BEFORE','AFTER']):
 x=i*960;source=Image.open(D/f'L_PASSING/{label}_CLOSE.png').convert('RGB');dr.text((x+20,55),label+' | coat compression',font=small,fill='#272522');crop=source.crop((420,205,565,390));crop.thumbnail((860,480));detail.paste(crop.resize((376,480)),(x+292,95));dr.text((x+20,625),label+' | knee, rolled cuff and ankle',font=small,fill='#272522');crop=source.crop((375,360,570,538));detail.paste(crop.resize((548,500)),(x+206,665))
dr.text((20,1170),'Detail crops enlarged for inspection. Coat remains a flat painted layer; temporal consistency is untested.',font=small,fill='#272522');detail.save(D/'WTSC_v022_Passing_Detail_Before_After.jpg',quality=95);slides.append(detail)
movie=D/'WTSC_v022_Whole_Painted_Pose_Comparison_8s.mp4';writer=imageio_ffmpeg.write_frames(str(movie),(1920,1200),fps=30,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',quality=8,ffmpeg_log_level='error',output_params=['-threads','2','-crf','18','-preset','medium','-movflags','+faststart']);writer.send(None)
for im,frames in zip(slides,[90,90,60]):
 for _ in range(frames):writer.send(im.tobytes())
writer.close()
reader=imageio_ffmpeg.read_frames(str(movie),pix_fmt='rgb24');meta=next(reader);decoded=[];count=0
for count,raw in enumerate(reader,1):
 if count in [30,120,210]:decoded.append(Image.frombytes('RGB',meta['size'],raw))
qa=Image.new('RGB',(1920,1200),'#eee9dd')
for i,im in enumerate(decoded):qa.paste(im.resize((960,600)),((i%2)*960,(i//2)*600))
qa.save(P/'evidence/ACTUAL_ENCODED_THREE_SLIDE_REVIEW.jpg',quality=95)
report={'movie':str(movie.resolve()),'bytes':movie.stat().st_size,'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'frames':count,'fps':30,'seconds':count/30,'dimensions':meta['size'],'all_unique_slides_decoded':len(decoded),'presentation':'Loading and passing comparisons held3s each, plus passing detail2s. Selected poses, not normal-speed motion.'}
(P/'evidence/preview_verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))

