import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
P=Path(__file__).resolve().parents[1];V=P/'previews';E=P/'evidence';record=json.loads((E/'LONG_RENDER_RECORD.json').read_text());fontfile='C:/Windows/Fonts/segoeui.ttf';boldfile='C:/Windows/Fonts/segoeuib.ttf'
def font(n,b=False):return ImageFont.truetype(boldfile if b else fontfile,n)
def source(tag,f):return Image.open(V/('frames_'+tag)/('FRAME_%04d.png'%f)).convert('RGB')
def writer(path,size):
 w=imageio_ffmpeg.write_frames(str(path),size,fps=30,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',quality=8,macro_block_size=16,ffmpeg_log_level='error',output_params=['-threads','2','-movflags','+faststart']);w.send(None);return w
full=V/'WTSC_Steady_Walk_v047_NormalSpeed_8Cycles.mp4';comp=V/'WTSC_v046_vs_v047_Steady_Walk_NormalSpeed.mp4';a=writer(full,(1280,800));b=writer(comp,(1920,640))
for f in range(1,258):
 current=source('V047',f);old=source('V046',f);im=Image.new('RGB',(1280,800),'#202a2c');d=ImageDraw.Draw(im);d.text((24,9),'v047 | STEADY ORDINARY WALK | NORMAL SPEED',font=font(26,True),fill='#f0eadf');d.text((24,44),'Eight 32-frame cycles + endpoint | fixed ground ticks | no cloth/braid embellishment',font=font(18),fill='#c1c9c6');d.text((1170,46),'F%03d'%f,font=font(17),fill='#c1c9c6');im.paste(current,(0,80));a.send(im.tobytes())
 im=Image.new('RGB',(1920,640),'#202a2c');d=ImageDraw.Draw(im)
 for x,title,sub in [(0,'v046 | PREVIOUS WALK','31-frame cycle, 0.830 m/s | preserved reference'),(960,'v047 | STEADY ORDINARY BASELINE','32-frame cycle, 0.731 m/s | shorter stride and coordinated transfer')]:d.text((x+22,9),title,font=font(26,True),fill='#f0eadf');d.text((x+22,45),sub,font=font(18),fill='#c1c9c6')
 im.paste(old.resize((960,540),Image.Resampling.LANCZOS),(0,80));im.paste(current.resize((960,540),Image.Resampling.LANCZOS),(960,80));d=ImageDraw.Draw(im);d.line((960,80,960,640),fill='#202a2c',width=2);d.text((20,620),'Same camera and scale | same elapsed time at 30 fps | cadence and travel differ intentionally',font=font(14),fill='#c1c9c6');d.text((1810,620),'F%03d'%f,font=font(14),fill='#c1c9c6');b.send(im.tobytes())
a.close();b.close();results=[];chosen={}
for file,size in [(full,(1280,800)),(comp,(1920,640))]:
 assert file.stat().st_size<20_000_000;reader=imageio_ffmpeg.read_frames(str(file),pix_fmt='rgb24');meta=next(reader);count=0
 for i,data in enumerate(reader):
  count+=1
  if file==comp and i in [0,16,32,48,64,96,128,160,192,224,240,256]:chosen[i]=Image.frombytes('RGB',size,data)
 assert count==257 and meta['size']==size and abs(meta['fps']-30)<1e-6,(count,meta)
 results.append({'file_name':file.name,'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'decoded_frames':count,'fps':30,'duration_seconds':257/30,'resolution':list(size),'under_20_MB':True})
sheet=Image.new('RGB',(1920,2064),'#202a2c');d=ImageDraw.Draw(sheet)
for j,(i,im) in enumerate(chosen.items()):x=(j%2)*960;y=(j//2)*344;sheet.paste(im.resize((960,320),Image.Resampling.LANCZOS),(x,y));d.text((x+10,y+322),'Encoded comparison frame %03d | %.3f seconds'%(i+1,i/30),font=font(15),fill='#f0eadf')
sheet.save(V/'ENCODED_LONG_COMPARISON_CONTACT_SHEET_v047.jpg',quality=95)
# Inspect every integer pose of the new local cycle, separately from decoding.
for block in range(4):
 sheet=Image.new('RGB',(1920,1170),'#202a2c');d=ImageDraw.Draw(sheet)
 for j,f in enumerate(range(1+block*8,9+block*8)):
  x=(j%3)*640;y=(j//3)*390;sheet.paste(source('V047',f).resize((640,360),Image.Resampling.LANCZOS),(x,y+30));d.text((x+10,y+4),'Actual v047 native F%02d'%f,font=font(18),fill='#f0eadf')
 sheet.save(V/('LOCAL_CYCLE_REVIEW_%d.jpg'%(block+1)),quality=95)
# Same elapsed time comparison poses, labels outside the native pixels.
board=Image.new('RGB',(2560,3200),'#202a2c');d=ImageDraw.Draw(board)
for row,f in enumerate([1,9,17,25]):
 for col,tag in enumerate(['V046','V047']):
  x=col*1280;y=row*800;d.text((x+24,y+12),'%s | native F%02d | %.3f seconds'%(tag,f,(f-1)/30),font=font(28,True),fill='#f0eadf');d.text((x+24,y+48),'Same camera and scale; each version retains its own gait clock and travel',font=font(19),fill='#c1c9c6');board.paste(source(tag,f),(x,y+80))
board.save(V/'WTSC_v046_v047_Matched_Pose_Comparison.png')
(E/'ENCODED_COMPARISON_VALIDATION.json').write_text(json.dumps({'native_source_hashes':record['source_hashes'],'movies':results,'all_encoded_frames_decoded':True,'interpolated_video_frames':False,'visual_review_method':'Native pose inspection, all32 local-cycle integer poses on contact sheets, selected decoded long-comparison frames. Continuous player playback has not been observed by the agent.','artistic_limit':'A technical pass or quieter numerical curves is not approval of weight and intent. User normal-speed judgment remains essential.'},indent=2));print(json.dumps(results,indent=2))
