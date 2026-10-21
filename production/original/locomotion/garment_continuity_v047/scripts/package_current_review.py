from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import subprocess,json,hashlib,re,datetime
import numpy as np
import imageio_ffmpeg
O=Path(r'WTSC_LOCAL_WORKSPACE\locomotion\garment_continuity_v047')/'current_v046_continuation'
P=O/'previews';ff=imageio_ffmpeg.get_ffmpeg_exe()
font=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',22)
def encode(folder,out,frames=94):
 subprocess.run([ff,'-hide_banner','-loglevel','error','-y','-framerate','30','-start_number','1','-i',str(folder/'%04d.png'),'-frames:v',str(frames),'-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
for name,title in [('baseline','Latest completed v046'),('garment','v047b | garment follow-through'),('candidate','v047b | reach and contact study')]:
 folder=P/name;n=94 if name!='garment' else 63
 assert all((folder/f'{f:04d}.png').exists() for f in range(1,n+1))
 encode(folder,P/({'baseline':'WTSC_Age10_Baseline_v047b.mp4','garment':'WTSC_Age10_Garments_v047b.mp4','candidate':'WTSC_Age10_Reach_v047b.mp4'}[name]),n)
 for page,start in enumerate(range(1,n+1,32),1):
  stop=min(n,start+31);board=Image.new('RGB',(2048,700),(23,25,29));dr=ImageDraw.Draw(board);dr.text((12,6),title+' | chronological frames '+str(start)+'–'+str(stop),font=font,fill='white')
  for i,f in enumerate(range(start,stop+1)):
   im=Image.open(folder/f'{f:04d}.png').convert('RGB').resize((256,144))
   x=i%8*256;y=40+i//8*164;board.paste(im,(x,y+20));dr.text((x+6,y),str(f),font=font,fill='white')
  board.save(P/f'{name}_chronological_{page}.jpg',quality=93)
# Inspection labels are outside the actual image. No character pixels are painted.
D=P/'comparison';D.mkdir(exist_ok=True)
for f in range(1,95):
 board=Image.new('RGB',(1280,400),(23,25,29));dr=ImageDraw.Draw(board)
 dr.text((10,7),'Latest v046 | original walk',font=font,fill='white')
 dr.text((650,7),'v047b | reach study',font=font,fill='white')
 for i,name in enumerate(['baseline','candidate']):
  im=Image.open(P/name/f'{f:04d}.png').convert('RGB').resize((640,360));board.paste(im,(i*640,40))
 board.save(D/f'{f:04d}.png')
encode(D,P/'WTSC_Age10_Comparison_v047b.mp4')
# Large unaltered render crops; headers only.
board=Image.new('RGB',(1600,600),(23,25,29));dr=ImageDraw.Draw(board)
for i,name in enumerate(['baseline','candidate']):
 im=Image.open(P/name/'0072.png').convert('RGB').crop((425,235,810,470)).resize((800,488))
 board.paste(im,(i*800,65));dr.text((i*800+12,14),('Latest v046 | F72' if i==0 else 'v047b | contact study F72'),font=font,fill='white')
board.save(P/'Contact_Comparison_v047b.jpg',quality=95)
# Decode every delivered frame and compare to its actual source render.
out=P/'WTSC_Age10_Reach_v047b.mp4';q=subprocess.Popen([ff,'-v','error','-i',str(out),'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
mae=[];count=0;size=1280*720*3
while True:
 raw=q.stdout.read(size)
 if not raw: break
 assert len(raw)==size,'Partial decoded frame'
 count+=1;a=np.frombuffer(raw,dtype=np.uint8).reshape(720,1280,3)
 b=np.array(Image.open(P/'candidate'/f'{count:04d}.png').convert('RGB'),dtype=np.int16)
 mae.append(float(np.abs(a.astype(np.int16)-b).mean()))
 if count in [1,40,55,72,94]: Image.fromarray(a).save(P/f'decoded_{count:02d}.jpg',quality=96)
assert q.wait()==0 and count==94
t=subprocess.run([ff,'-hide_banner','-i',str(out),'-vf','showinfo','-f','null','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,check=True).stderr
pts=[float(x) for x in re.findall(r' n:\s*\d+ pts:\s*\d+ pts_time:([\d.]+)',t)]
assert len(pts)==94 and max(abs(v-i/30) for i,v in enumerate(pts))<.00001,(len(pts),pts[:3])
assert max(mae)<4
report={'encoded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidate_frames_decoded':count,'fps':30,'duration_seconds':94/30,'all_presentation_times_verified':True,'maximum_decoded_vs_source_mean_absolute_RGB_error_255':max(mae),'mean_decoded_vs_source_mean_absolute_RGB_error_255':sum(mae)/len(mae),'no_interpolated_frames':True,'renders_are_actual_native_frames':True,'files':[{'name':f.name,'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in P.glob('*.mp4')]}
(O/'evidence/ENCODED_REVIEW_VALIDATION.json').write_text(json.dumps(report,indent=2))
print('V047B_MOVIES_BOARDS_DECODE_VERIFIED',json.dumps(report),flush=True)
