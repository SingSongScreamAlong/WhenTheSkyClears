"""Clearly versioned, native-clock model-fit review; no motion changes."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];V=P/'previews';E=P/'evidence'
record=json.loads((E/'ACTUAL_V049_MOTION_RENDER.json').read_text())
lookup={(r['version'],r['frame']):r for r in record['records']}
def font(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
def source(tag,f):
 r=lookup[(tag,f)];p=Path(r['file']);assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'];return Image.open(p).convert('RGB')
def writer(path,size):
 w=imageio_ffmpeg.write_frames(str(path),size,fps=30,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',quality=8,macro_block_size=16,ffmpeg_log_level='error',output_params=['-threads','2','-movflags','+faststart']);w.send(None);return w
full=V/'WTSC_Model_Fit_v049_Actual_NormalSpeed.mp4';comp=V/'WTSC_v048_vs_v049_Model_Fit_SameMotion.mp4'
a=writer(full,(1280,800));b=writer(comp,(1920,640))
for f in range(1,258):
 current=source('V049',f);old=source('V048',f)
 im=Image.new('RGB',(1280,800),'#202a2c');d=ImageDraw.Draw(im)
 d.text((24,8),'v049 MODEL FIT | ACTUAL NATIVE MOTION | NORMAL SPEED',font=font(25,True),fill='#f0eadf')
 d.text((24,44),'Preserved v048 gait | 30 fps | eight 32-frame cycles + endpoint | no video interpolation',font=font(18),fill='#c1c9c6')
 d.text((1170,44),'F%03d'%f,font=font(17),fill='#c1c9c6');im.paste(current,(0,80));a.send(im.tobytes())
 im=Image.new('RGB',(1920,640),'#202a2c');d=ImageDraw.Draw(im)
 for x,title,sub in [(0,'v048 | BEFORE MODEL FIT','Original garment fit, sleeve crown and painted hand grouping'),(960,'v049 | FITTED MODEL IN MOTION','Refined garment contour, sleeves, forearms and hand grouping')]:
  d.text((x+22,9),title,font=font(26,True),fill='#f0eadf');d.text((x+22,45),sub,font=font(18),fill='#c1c9c6')
 im.paste(old.resize((960,540),Image.Resampling.LANCZOS),(0,80));im.paste(current.resize((960,540),Image.Resampling.LANCZOS),(960,80));d=ImageDraw.Draw(im)
 d.line((960,80,960,620),fill='#202a2c',width=2)
 d.text((20,620),'Same v048 motion, camera, scale, phase and travel in both panels | actual native frames at 30 fps',font=font(14),fill='#c1c9c6')
 d.text((1810,620),'F%03d'%f,font=font(14),fill='#c1c9c6');b.send(im.tobytes())
a.close();b.close();results=[];chosen={};cycle={}
for file,size in [(full,(1280,800)),(comp,(1920,640))]:
 assert file.stat().st_size<20_000_000;reader=imageio_ffmpeg.read_frames(str(file),pix_fmt='rgb24');meta=next(reader);count=0
 for i,data in enumerate(reader):
  count+=1
  if file==full and i<32:cycle[i+1]=Image.frombytes('RGB',size,data)
  if file==comp and i in [0,4,8,12,16,20,24,28,32,64,128,256]:chosen[i+1]=Image.frombytes('RGB',size,data)
 assert count==257 and meta['size']==size and abs(meta['fps']-30)<1e-6,(count,meta)
 results.append({'file_name':file.name,'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'decoded_frames':count,'fps':30,'duration_seconds':257/30,'resolution':list(size),'under_20_MB':True,'model_version':'v049' if file==full else 'v048 left, v049 right','motion_version':'v048 unchanged'})
for block in range(4):
 sheet=Image.new('RGB',(1920,1272),'#202a2c');d=ImageDraw.Draw(sheet)
 for j,f in enumerate(range(1+block*8,9+block*8)):
  x=(j%3)*640;y=(j//3)*424;sheet.paste(cycle[f].resize((640,400),Image.Resampling.LANCZOS),(x,y+24));d.text((x+8,y+2),'DECODED v049 F%02d | preserved v048 gait'%f,font=font(16),fill='#f0eadf')
 sheet.save(V/('DECODED_V049_CYCLE_%d.jpg'%(block+1)),quality=96)
sheet=Image.new('RGB',(1920,2064),'#202a2c');d=ImageDraw.Draw(sheet)
for j,(f,im) in enumerate(chosen.items()):
 x=(j%2)*960;y=(j//2)*344;sheet.paste(im.resize((960,320),Image.Resampling.LANCZOS),(x,y));d.text((x+10,y+322),'Decoded comparison F%03d | %.3f seconds'%(f,(f-1)/30),font=font(15),fill='#f0eadf')
sheet.save(V/'DECODED_V048_V049_COMPARISON.jpg',quality=96)
# Decoded model detail at eight phases; no invented intermediate poses.
sheet=Image.new('RGB',(1920,680),'#202a2c');d=ImageDraw.Draw(sheet)
for j,f in enumerate([1,5,9,13,17,21,25,29]):
 x=(j%4)*480;y=(j//4)*340;im=cycle[f].crop((410,275,880,570));im=im.resize((480,301),Image.Resampling.LANCZOS);sheet.paste(im,(x,y+30));d.text((x+10,y+4),'DECODED v049 | F%02d'%f,font=font(19),fill='#f0eadf')
sheet.save(V/'DECODED_V049_UPPER_BODY_PHASES.jpg',quality=96)
(E/'ACTUAL_V049_ENCODE_VALIDATION.json').write_text(json.dumps({'native_source_hashes':record['source_hashes'],'movies':results,'all_encoded_frames_decoded':True,'interpolated_video_frames':False,'rendered_frames_repeated_instead_of_actual_timeline':False,'visual_review_material':'Decoded all32 integer cycle poses, selected decoded comparison frames across8cycles, decoded upper-body phase details. Continuous player playback has not been observed by the agent.','scope':'Model coherence review. Gait intentionally unchanged from v048. Technical checks do not establish artistic acceptance.'},indent=2));print(json.dumps(results,indent=2))
