import json,subprocess,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
O=Path(__file__).resolve().parents[1];P=O/'previews';F=imageio_ffmpeg.get_ffmpeg_exe();movie=P/'WTSC_First_Danger_Title_v065f_4K.mp4'
def raw(args):return subprocess.run([F,'-v','error',*args],capture_output=True,check=True,creationflags=subprocess.CREATE_NO_WINDOW).stdout
keys=[937,981,1056];indices=[g-913 for g in keys]
select='+'.join(f'eq(n\\,{n})' for n in indices)
data=raw(['-i',str(movie),'-vf',f'select={select},scale=1280:720:flags=lanczos','-fps_mode','vfr','-pix_fmt','rgb24','-f','rawvideo','pipe:1'])
decoded=np.frombuffer(data,dtype=np.uint8).reshape(len(keys),720,1280,3);rows=[]
for i,g in enumerate(keys):
 reference=raw(['-i',str(O/f'renders/final_composite4K_F/{g:04d}.png'),'-vf','scale=1280:720:flags=lanczos','-frames:v','1','-pix_fmt','rgb24','-f','rawvideo','pipe:1'])
 ref=np.frombuffer(reference,dtype=np.uint8).reshape(720,1280,3);delta=decoded[i].astype(np.int16)-ref.astype(np.int16)
 rows.append({'frame':g,'mean_absolute_RGB_error':float(np.abs(delta).mean()),'signed_mean_RGB_error':delta.mean((0,1)).tolist()})
 Image.fromarray(decoded[i]).save(P/f'Actual_Movie_Decoded_{g:04d}.jpg',quality=96)
report={'movie':str(movie),'comparison_resolution':[1280,720],'source':'The actual final native UHD pixel sequence, resized using the same FFmpeg Lanczos filter','encoder_matrix':'Explicit BT.709 limited-range YUV conversion; decoded RGB compared to source','rows':rows}
assert max(r['mean_absolute_RGB_error'] for r in rows)<3,rows
assert max(abs(v) for r in rows for v in r['signed_mean_RGB_error'])<1.5,rows
(O/'evidence/ENCODED_COLOR_CHECK.json').write_text(json.dumps(report,indent=2))

# Actual decoded samples every fourth frame, covering the full seven seconds.
data=raw(['-i',str(movie),'-vf','select=not(mod(n\\,4)),scale=640:360:flags=lanczos','-fps_mode','vfr','-pix_fmt','rgb24','-f','rawvideo','pipe:1'])
frames=np.frombuffer(data,dtype=np.uint8).reshape(-1,360,640,3);assert len(frames)==42
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for part in range(2):
 canvas=Image.new('RGB',(1920,2730),'#141a22');draw=ImageDraw.Draw(canvas)
 for local in range(21):
  i=part*21+local;g=913+4*i;x=(local%3)*640;y=(local//3)*390
  canvas.paste(Image.fromarray(frames[i]),(x,y+30));draw.text((x+8,y+4),f'Actual movie | G{g} | {(g-1)/24:.3f}s',font=font,fill='white')
 canvas.save(P/f'Decoded_Chronology_{part+1}.jpg',quality=94)
(O/'evidence/DECODED_REVIEW_SAMPLES.json').write_text(json.dumps({'movie':str(movie),'sample_count':42,'selection':'Every fourth encoded frame, original24fps; no interpolation','global_frames':[913+4*i for i in range(42)],'boards':['Decoded_Chronology_1.jpg','Decoded_Chronology_2.jpg'],'limits':'Chronological sample inspection and complete decoding; not an assertion of continuous native-player artistic playback.'},indent=2))
print('ACTUAL_MOVIE_COLOR_AND_CHRONOLOGY_READY',json.dumps(rows),flush=True)
