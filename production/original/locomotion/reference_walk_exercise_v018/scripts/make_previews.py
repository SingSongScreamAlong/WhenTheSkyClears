from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,subprocess,hashlib,sys
import imageio_ffmpeg
P=Path(__file__).resolve().parents[1];D=P/'previews';(D/'PAIRED').mkdir(exist_ok=True)
def font(n):
 try:return ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',n)
 except:return ImageFont.load_default()
F=font(24);small=font(18);title=font(30)
def label(im,txt,xy=(16,10),f=small):ImageDraw.Draw(im).text(xy,txt,font=f,fill='#292724')
for f in range(1,49):
 a=Image.open(D/f'SMOOTH/{f:04d}.png').convert('RGB');b=Image.open(D/f'MATCHED/{f:04d}.png').convert('RGB');im=Image.new('RGB',(1920,640),'#eee9dd');im.paste(a,(0,50));im.paste(b,(960,50))
 label(im,'V018  |  travelling boy / fixed ground',f=F);label(im,'Original v046 camera scale / follows travel',(976,10),F)
 label(im,f'Frame {f:02d}   |   D = {(.44*(f-1)/24):.3f} m   |   24 fps   |   near contact: teal / far: ochre',(20,596))
 label(im,'Rig capability study - artistic approval pending',(1115,596));im.save(D/f'PAIRED/{f:04d}.png')
ff=imageio_ffmpeg.get_ffmpeg_exe();files=[]
for folder,name in [('PAIRED','WTSC_Boy_Travelling_Walk_v018_Review_2s.mp4'),('MATCHED','WTSC_Boy_Travelling_Walk_v018_Matched_Size_2s.mp4')]:
 path=D/name;subprocess.run([ff,'-y','-hide_banner','-loglevel','error','-threads','2','-framerate','24','-start_number','1','-i',str(D/folder/'%04d.png'),'-frames:v','48','-c:v','libx264','-threads','2','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(path)],check=True);files.append(path)
# Inspect the actual encoded review file via decoded chronological samples.
reader=imageio_ffmpeg.read_frames(str(files[0]),pix_fmt='rgb24');meta=next(reader);chosen=[0,3,6,9,12,15,18,21,24,30,36,47];frames={}
for i,data in enumerate(reader):
 if i in chosen:frames[i]=Image.frombytes('RGB',meta['size'],data)
board=Image.new('RGB',(1920,1280),'#eee9dd')
for j,i in enumerate(chosen):
 a=frames[i];a=a.crop((0,0,960,640)).resize((480,320));board.paste(a,((j%4)*480,(j//4)*426));label(board,'Decoded movie frame '+str(i+1),((j%4)*480+14,(j//4)*426+328))
board.save(D/'WTSC_v018_Decoded_Loop_Contact_Board.jpg',quality=94)
# Rebuild final stepped board after the key-pose refinements.
board=Image.new('RGB',(1440,1080),'#eee9dd');labels=['NEAR contact','DOWN / load near','FAR passing','UP / near stance','FAR contact','DOWN / load far','NEAR passing','UP / far stance','CYCLE +0.44m']
for i,f in enumerate([1,4,7,10,13,16,19,22,25]):
 a=Image.open(D/f'BLOCKING/{f:04d}.png').convert('RGB').resize((480,270));x=i%3*480;y=i//3*360;board.paste(a,(x,y+40));label(board,str(f)+'  '+labels[i],(x+14,y+8))
board.save(D/'WTSC_v018_Stepped_Key_Poses.jpg',quality=94)
# Contact and crossing detail at the actual rendered art, crop only.
board=Image.new('RGB',(1600,1110),'#eee9dd');label(board,'V018 actual painted walk - feet and silhouette review',(20,12),title)
for i,f in enumerate([1,4,7,10,13,16,19,22]):
 a=Image.open(D/f'SMOOTH/{f:04d}.png').convert('RGB');cx=480+((.44*(f-1)/24)-.44)/3.25*960;crop=a.crop((int(cx-125),210,int(cx+125),510));crop=crop.resize((250,300));x=i%4*400;y=70+(i//4)*520;board.paste(crop,(x+75,y+35));label(board,f'Frame {f:02d}',(x+20,y));b=Image.open(D/f'MATCHED/{f:04d}.png').convert('RGB').resize((400,225));board.paste(b,(x,y+300))
board.save(D/'WTSC_v018_Painted_Contact_and_Shot_Size_Board.jpg',quality=94)
out={'movies':[{ 'path':str(x.resolve()),'bytes':x.stat().st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest(),'frames':48,'fps':24,'duration_seconds':2} for x in files],'actual_decode':{'review_dimensions':meta['size'],'decoded_sample_frames':[i+1 for i in chosen],'method':'imageio-ffmpeg decoded RGB samples; no normal-speed playback observation claimed'},'loop_note':'Translating gait repeats every24frames with+0.44m. MP4 shows two cycles; replay resets world position and numbered ground markers.'}
(P/'evidence/movie_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
