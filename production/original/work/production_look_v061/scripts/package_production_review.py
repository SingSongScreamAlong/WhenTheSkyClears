from pathlib import Path
import subprocess,json,hashlib,re,datetime
import imageio_ffmpeg,numpy as np
from PIL import Image,ImageDraw,ImageFont
O=Path(r'WTSC_LOCAL_WORKSPACE\work\production_look_v061');P=O/'previews';F=imageio_ffmpeg.get_ffmpeg_exe();r=json.loads((O/'evidence/NATIVE_SEQUENCE_RENDER.json').read_text());native=O/'native/WTSC_Physical_Ink_Wash_Forest_v061.blend'
assert r['frames']==120 and r['native_sha256']==hashlib.sha256(native.read_bytes()).hexdigest()
assert all(row['sha256']==hashlib.sha256((P/'frames'/('%04d.png'%row['frame'])).read_bytes()).hexdigest() for row in r['rows'])
music=O.parents[1]/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav';rows=[]
for name,W,H,crf in [('WTSC_Ink_Wash_Depth_v061_HD.mp4',1280,720,19),('WTSC_Ink_Wash_Depth_v061_Preview.mp4',960,540,22)]:
 out=P/name
 subprocess.run([F,'-v','error','-y','-framerate','24','-start_number','937','-i',str(P/'frames/%04d.png'),'-ss','39','-i',str(music),'-map','0:v:0','-map','1:a:0','-vf',f'scale={W}:{H}:flags=lanczos','-frames:v','120','-t','5','-c:v','libx264','-preset','slow','-crf',str(crf),'-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(out)],check=True)
 dec=subprocess.Popen([F,'-v','error','-i',str(out),'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
 ref=subprocess.Popen([F,'-v','error','-framerate','24','-start_number','937','-i',str(P/'frames/%04d.png'),'-vf',f'scale={W}:{H}:flags=lanczos','-frames:v','120','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
 count=0;errs=[];sz=W*H*3
 while True:
  a=dec.stdout.read(sz);b=ref.stdout.read(sz)
  if not a and not b:break
  assert len(a)==len(b)==sz;count+=1
  aa=np.frombuffer(a,dtype=np.uint8).reshape(H,W,3);bb=np.frombuffer(b,dtype=np.uint8).reshape(H,W,3)
  errs.append(float(np.abs(aa.astype(np.int16)-bb.astype(np.int16)).mean()))
  if W==960 and count in [1,21,45,73,97,120]:Image.fromarray(aa).save(P/f'Decoded_Review_{count:03d}.jpg',quality=95)
 assert dec.wait()==ref.wait()==0 and count==120 and max(errs)<8
 log=subprocess.run([F,'-hide_banner','-i',str(out),'-vf','showinfo','-an','-f','null','-'],capture_output=True,text=True,check=True).stderr
 pts=[float(x) for x in re.findall(r' n:\s*\d+ pts:\s*\d+ pts_time:([\d.]+)',log)]
 assert len(pts)==120 and max(abs(t-i/24) for i,t in enumerate(pts))<.00001
 rows.append({'name':name,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'decoded_frames':count,'fps':24,'duration_s':5,'resolution':[W,H],'max_mean_RGB_error_255':max(errs),'frame_pts_verified':True})
def pcm(args):
 q=subprocess.run([F,'-v','error',*args,'-ac','2','-ar','48000','-f','f32le','-'],capture_output=True,check=True);return np.frombuffer(q.stdout,dtype=np.float32)
a=pcm(['-ss','39','-i',str(music),'-t','5']);b=pcm(['-i',str(P/'WTSC_Ink_Wash_Depth_v061_Preview.mp4'),'-vn']);n=min(len(a),len(b));corr=float(np.corrcoef(a[:n],b[:n])[0,1]);assert corr>.98
font=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',20)
for page,first in enumerate(range(937,1057,30),1):
 board=Image.new('RGB',(1920,1050),(22,23,26));dr=ImageDraw.Draw(board);dr.text((10,4),'v061 | native ink/wash depth development | chronological frames',font=font,fill='white')
 for i,g in enumerate(range(first,min(first+30,1057))):
  im=Image.open(P/'frames'/f'{g:04d}.png').convert('RGB').resize((320,180));x=i%6*320;y=35+i//6*200
  board.paste(im,(x,y+20));dr.text((x+6,y),str(g),font=font,fill='white')
 board.save(P/f'Chronological_Review_{page}.jpg',quality=94)
im=Image.open(P/'Native_Contact_4K_v061.png').convert('RGB');im.resize((1920,1080)).save(P/'WTSC_Ink_Wash_Depth_v061.jpg',quality=95)
im.crop((1480,540,2380,1100)).save(P/'Native_Head_Hands_4K_Crop_v061.jpg',quality=98)
im.crop((1450,1390,2420,1630)).save(P/'Native_Feet_4K_Crop_v061.jpg',quality=98)
before=O/'reference/pre_focus_correction/Native_Head_Hands_4K_Crop_v061.jpg'
if before.exists():
 board=Image.new('RGB',(1800,610),(22,23,26));dr=ImageDraw.Draw(board);board.paste(Image.open(before).convert('RGB'),(0,45));board.paste(Image.open(P/'Native_Head_Hands_4K_Crop_v061.jpg').convert('RGB'),(900,45));dr.text((12,10),'Before | BLENDED transparency with DOF',font=font,fill='white');dr.text((912,10),'Corrected | DITHERED alpha depth | same artwork',font=font,fill='white');board.save(P/'Focus_Depth_Correction_v061.jpg',quality=96)
report={'packaged_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native_sha256':r['native_sha256'],'all120_native_frames_checked':True,'movies':rows,'source_music_excerpt_s':[39,44],'audio_zero_lag_correlation':corr,'artistic_scope':'Production-look development candidate; not final character acting or full trailer.'}
(O/'evidence/ENCODED_REVIEW_VALIDATION.json').write_text(json.dumps(report,indent=2));print('V061_MOVIES_ENCODE_DECODE_VERIFIED',json.dumps(report),flush=True)
