from pathlib import Path
import subprocess,json,hashlib,re,datetime
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
O=Path(r'WTSC_LOCAL_WORKSPACE\work\trailer_development_v060');P=O/'previews';F=imageio_ffmpeg.get_ffmpeg_exe()
r=json.loads((O/'evidence/DUAL_SEQUENCE_RENDER.json').read_text())
assert r['actual_rendered_frames']==120 and r['synchronized_world_and_glyph_clocks']
assert hashlib.sha256((O/'native/WTSC_First_Danger_Trailer_Development_v060.blend').read_bytes()).hexdigest()==r['native_sha256']
assert all(x['frame']==x['world_clock']==x['glyph_clock'] for x in r['rows'])
music=O.parents[1]/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'
jobs=[('frames_world','WTSC_First_Danger_v060_HD.mp4',1280,720,20),('frames_world','WTSC_First_Danger_v060_Preview.mp4',960,540,23),('frames_title','WTSC_First_Danger_Title_v060_Preview.mp4',960,540,21)]
records=[]
for folder,name,W,H,crf in jobs:
 assert all((P/folder/f'{g:04d}.png').exists() for g in range(937,1057))
 out=P/name
 cmd=[F,'-hide_banner','-loglevel','error','-y','-framerate','24','-start_number','937','-i',str(P/folder/'%04d.png'),'-ss','39','-i',str(music),'-map','0:v:0','-map','1:a:0','-vf',f'scale={W}:{H}:flags=lanczos','-frames:v','120','-t','5','-c:v','libx264','-preset','slow','-crf',str(crf),'-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(out)]
 subprocess.run(cmd,check=True)
 # Decode every encoded frame and compare with the exact same resize filter.
 dec=subprocess.Popen([F,'-v','error','-i',str(out),'-map','0:v:0','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
 ref=subprocess.Popen([F,'-v','error','-framerate','24','-start_number','937','-i',str(P/folder/'%04d.png'),'-vf',f'scale={W}:{H}:flags=lanczos','-frames:v','120','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
 count=0;mae=[];sz=W*H*3
 while True:
  a=dec.stdout.read(sz);b=ref.stdout.read(sz)
  if not a and not b:break
  assert len(a)==len(b)==sz
  count+=1;aa=np.frombuffer(a,dtype=np.uint8).reshape(H,W,3);bb=np.frombuffer(b,dtype=np.uint8).reshape(H,W,3)
  mae.append(float(np.abs(aa.astype(np.int16)-bb.astype(np.int16)).mean()))
  if count in [1,21,45,97,120] and name.endswith('_Preview.mp4'):
   Image.fromarray(aa).save(P/(name.replace('.mp4','')+f'_decoded_{count:03d}.jpg'),quality=95)
 assert dec.wait()==ref.wait()==0 and count==120
 log=subprocess.run([F,'-hide_banner','-i',str(out),'-vf','showinfo','-an','-f','null','-'],capture_output=True,text=True,check=True).stderr
 pts=[float(x) for x in re.findall(r' n:\s*\d+ pts:\s*\d+ pts_time:([\d.]+)',log)]
 assert len(pts)==120 and max(abs(t-i/24) for i,t in enumerate(pts))<.00001
 assert max(mae)<8,(name,max(mae))
 records.append({'name':name,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'decoded_frames':count,'fps':24,'seconds':5,'resolution':[W,H],'pts_verified':True,'max_mean_absolute_RGB_error_255':max(mae),'mean_RGB_error_255':sum(mae)/len(mae)})
def pcm(args):
 q=subprocess.run([F,'-v','error',*args,'-ac','2','-ar','48000','-f','f32le','-'],capture_output=True,check=True)
 return np.frombuffer(q.stdout,dtype=np.float32)
a=pcm(['-ss','39','-i',str(music),'-t','5']);b=pcm(['-i',str(P/'WTSC_First_Danger_v060_Preview.mp4'),'-vn'])
n=min(len(a),len(b));corr=float(np.corrcoef(a[:n],b[:n])[0,1]);assert corr>.98,corr
font=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',20)
for folder,label in [('frames_world','Current v060 world'),('frames_title','Actual inherited title view')]:
 for page,first in enumerate(range(937,1057,32),1):
  board=Image.new('RGB',(2048,700),(22,23,26));dr=ImageDraw.Draw(board);dr.text((10,5),label+' | chronological native frames',font=font,fill='white')
  for i,g in enumerate(range(first,min(first+32,1057))):
   im=Image.open(P/folder/f'{g:04d}.png').convert('RGB').resize((256,144));x=i%8*256;y=40+i//8*164;board.paste(im,(x,y+20));dr.text((x+5,y),str(g),font=font,fill='white')
  board.save(P/f'{folder}_chronological_{page}.jpg',quality=93)
board=Image.new('RGB',(1920,580),(22,23,26));dr=ImageDraw.Draw(board)
for i,(folder,label) in enumerate([('frames_world','Current world | contact at41 seconds'),('frames_title','Existing title | faces obscured')]):
 im=Image.open(P/folder/'0981.png').convert('RGB').resize((960,540));board.paste(im,(i*960,40));dr.text((i*960+12,8),label,font=font,fill='white')
board.save(P/'World_and_Title_Readability_v060.jpg',quality=95)
im=Image.open(P/'native4K/world_0981Image.png').convert('RGB')
im.resize((1920,1080)).save(P/'WTSC_First_Danger_v060_Poster.jpg',quality=94)
im.crop((1490,530,2380,1070)).save(P/'Native_Head_Hands_4K_Crop_v060.jpg',quality=98)
im.crop((1460,1390,2410,1630)).save(P/'Native_Feet_4K_Crop_v060.jpg',quality=98)
report={'packaged_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native_sha256':r['native_sha256'],'actual_native_frames':120,'world_range':[937,1056],'source_music_excerpt_seconds':[39,44],'audio_zero_lag_correlation_to_original_excerpt':corr,'source_music_sha256':hashlib.sha256(music.read_bytes()).hexdigest(),'movies':records,'no_interpolated_or_recycled_frames':True,'native_world_and_title_same_clock':True}
(O/'evidence/ENCODED_DELIVERY_VALIDATION.json').write_text(json.dumps(report,indent=2))
print('V060_ENCODE_AND_DECODE_VERIFIED',json.dumps(report),flush=True)
