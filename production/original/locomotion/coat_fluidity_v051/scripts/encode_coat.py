import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
P=Path(__file__).resolve().parents[1];V=P/'previews';E=P/'evidence';record=json.loads((E/'ACTUAL_V051_MOTION_RENDER.json').read_text());lookup={(r['version'],r['view'],r['frame']):r for r in record['records']}
def font(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
def source(tag,view,f):
 r=lookup[(tag,view,f)];p=Path(r['file']);assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'];return Image.open(p).convert('RGB')
def writer(path,size):
 w=imageio_ffmpeg.write_frames(str(path),size,fps=30,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',quality=8,macro_block_size=16,ffmpeg_log_level='error',output_params=['-threads','2','-movflags','+faststart']);w.send(None);return w
def pair(view,f):
 im=Image.new('RGB',(1920,640),'#202a2c');d=ImageDraw.Draw(im)
 for x,tag,title,sub in [(0,'V050','v050 | FROZEN COAT / GAIT','Original rigid lower coat and level hem'),(960,'V051','v051 | CLOTH ONLY | SAME GAIT','Soft contour, damped hem response and restrained sleeve compression')]:
  d.text((x+22,9),title,font=font(25,True),fill='#f0eadf');d.text((x+22,45),sub,font=font(17),fill='#c1c9c6');im.paste(source(tag,view,f).resize((960,540),Image.Resampling.LANCZOS),(x,80))
 d.line((960,80,960,620),fill='#202a2c',width=2);d.text((20,620),'Actual native frames at 30 fps | identical body motion, scale, phase and travel | '+view.lower()+' camera',font=font(14),fill='#c1c9c6');d.text((1810,620),'F%03d'%f,font=font(14),fill='#c1c9c6');return im
full=V/'WTSC_Controlled_Fluid_Coat_v051_Actual_NormalSpeed.mp4';comp=V/'WTSC_v050_vs_v051_Cloth_Only_Same_Gait.mp4';detail=V/'WTSC_v050_vs_v051_Coat_Detail_NormalSpeed.mp4';a=writer(full,(1280,800));b=writer(comp,(1920,640));c=writer(detail,(1920,640))
for f in range(1,258):
 im=Image.new('RGB',(1280,800),'#202a2c');d=ImageDraw.Draw(im);d.text((22,9),'v051 CONTROLLED FLUID COAT | ACTUAL NATIVE | NORMAL SPEED',font=font(25,True),fill='#f0eadf');d.text((22,44),'Exact v050 gait / face / hands / scale | eight cycles + endpoint | cloth changes only',font=font(18),fill='#c1c9c6');d.text((1170,44),'F%03d'%f,font=font(17),fill='#c1c9c6');im.paste(source('V051','FULL',f),(0,80));a.send(im.tobytes());b.send(pair('FULL',f).tobytes())
 if f<=129:c.send(pair('DETAIL',f).tobytes())
a.close();b.close();c.close();results=[];cycle={};comparisons={};details={}
for file,size,expected in [(full,(1280,800),257),(comp,(1920,640),257),(detail,(1920,640),129)]:
 assert file.stat().st_size<20_000_000;reader=imageio_ffmpeg.read_frames(str(file),pix_fmt='rgb24');meta=next(reader);count=0
 for i,data in enumerate(reader):
  count+=1
  if file==full and i<32:cycle[i+1]=Image.frombytes('RGB',size,data)
  if file==comp and i in [0,4,8,12,16,20,24,28,32,64,128,256]:comparisons[i+1]=Image.frombytes('RGB',size,data)
  if file==detail and i in [0,4,8,12,16,20,24,28,32,64,96,128]:details[i+1]=Image.frombytes('RGB',size,data)
 assert count==expected and meta['size']==size and abs(meta['fps']-30)<1e-6
 results.append({'file_name':file.name,'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'decoded_frames':count,'fps':30,'duration_seconds':count/30,'resolution':list(size),'under_20_MB':True,'same_v050_gait':True})
for block in range(4):
 sheet=Image.new('RGB',(1920,1272),'#202a2c');d=ImageDraw.Draw(sheet)
 for j,f in enumerate(range(1+block*8,9+block*8)):
  x=(j%3)*640;y=(j//3)*424;sheet.paste(cycle[f].resize((640,400),Image.Resampling.LANCZOS),(x,y+24));d.text((x+8,y+2),'DECODED v051 F%02d | unchanged v050 gait'%f,font=font(16),fill='#f0eadf')
 sheet.save(V/('DECODED_V051_CYCLE_%d.jpg'%(block+1)),quality=96)
for name,frames in [('DECODED_FULL_COMPARISON.jpg',comparisons),('DECODED_COAT_DETAIL_COMPARISON.jpg',details)]:
 sheet=Image.new('RGB',(1920,2064),'#202a2c');d=ImageDraw.Draw(sheet)
 for j,(f,im) in enumerate(frames.items()):
  x=(j%2)*960;y=(j//2)*344;sheet.paste(im.resize((960,320),Image.Resampling.LANCZOS),(x,y));d.text((x+10,y+322),'Decoded A/B F%03d | %.3f seconds'%(f,(f-1)/30),font=font(15),fill='#f0eadf')
 sheet.save(V/name,quality=96)
(E/'ENCODED_COAT_VALIDATION.json').write_text(json.dumps({'native_source_hashes':record['source_hashes'],'movies':results,'all_encoded_frames_decoded':True,'video_interpolation':False,'looped_pngs_instead_of_native_timeline_render':False,'body_timing_changed':False,'visual_review_material':'All32 decoded first-cycle integer poses,12 full A/B frames over8cycles and12 native coat-camera A/B frames over4cycles. Continuous player playback not observed.','artistic_scope':'Cloth contribution isolated. Numerical contacts and successful decoding do not establish natural performance or artistic approval.'},indent=2));print(json.dumps(results,indent=2))
