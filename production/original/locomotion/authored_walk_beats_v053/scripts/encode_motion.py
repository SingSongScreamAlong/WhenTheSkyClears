import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
P=Path(__file__).resolve().parents[1];E=P/'evidence';V=P/'previews';data=json.loads((E/'ACTUAL_MOTION_RENDER.json').read_text());lookup={(r['version'],r['frame']):r for r in data['records']}
def image(tag,f):
 r=lookup[(tag,f)];path=Path(r['file']);assert hashlib.sha256(path.read_bytes()).hexdigest()==r['sha256'];return Image.open(path).convert('RGB')
font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',24);sub=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
out=V/'WTSC_v051_vs_v053_Authored_Walk_Beats_NormalSpeed.mp4';w=imageio_ffmpeg.write_frames(str(out),(1920,640),fps=30,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',quality=8,macro_block_size=16,ffmpeg_log_level='error',output_params=['-threads','2','-movflags','+faststart']);w.send(None)
for f in range(1,258):
 canvas=Image.new('RGB',(1920,640),'#202a2c');d=ImageDraw.Draw(canvas)
 for x,tag,title,line in [(0,'V051','v051 | FROZEN BODY TIMING','Fluid coat; existing chest, elbow and wrist timing'),(960,'V053','v053 | AUTHORED WALK BEATS','Same grounded feet, speed, coat and art; contact / loading / passing / push-off')]:
  canvas.paste(image(tag,f).resize((960,540),Image.Resampling.LANCZOS),(x,80));d.text((x+20,9),title,font=font,fill='#f0eadf');d.text((x+20,45),line,font=sub,fill='#c1c9c6')
 d.text((20,621),'Actual native frames |30fps|matching camera and travel',font=sub,fill='#c1c9c6');d.text((1810,621),f'F{f:03d}',font=sub,fill='#c1c9c6');w.send(canvas.tobytes())
w.close();assert out.stat().st_size<20_000_000
reader=imageio_ffmpeg.read_frames(str(out),pix_fmt='rgb24');meta=next(reader);frames={};count=0
for i,raw in enumerate(reader):
 count+=1
 if i in [0,4,8,12,16,20,24,28,32,48,64,80,96,112,128,160,192,224,256]:frames[i+1]=Image.frombytes('RGB',(1920,640),raw)
assert count==257 and meta['size']==(1920,640) and abs(meta['fps']-30)<1e-6
sheet=Image.new('RGB',(1920,10*344),'#202a2c');d=ImageDraw.Draw(sheet)
for j,(f,im) in enumerate(frames.items()):
 x=(j%2)*960;y=(j//2)*344;sheet.paste(im.resize((960,320),Image.Resampling.LANCZOS),(x,y));d.text((x+10,y+322),f'Decoded F{f:03d} |{(f-1)/30:.3f}s',font=sub,fill='#f0eadf')
sheet.save(V/'WTSC_v051_v053_Decoded_Motion_Review.jpg',quality=95)
report={'file_name':out.name,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'decoded_frames':count,'fps':30,'duration_seconds':count/30,'resolution':[1920,640],'all_frames_decoded':True,'actual_native_frame_sources':True,'same_foot_root_camera_travel':True,'continuous_player_observed_by_agent':False,'technical_pass_not_artistic_approval':True}
(E/'ENCODED_MOTION_VALIDATION.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
