import json,subprocess,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg as F
P=Path(__file__).resolve().parents[1];ff=F.get_ffmpeg_exe();dest=P/'previews/WTSC_Rough_Construction_v031_Normal_Speed.mp4'
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',26);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
args=[ff,'-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s','1280x800','-r','30','-i','-','-an','-c:v','libx264','-threads','2','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
proc=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
for mode in ['CLOSE','SHOT']:
    for f in range(1,97):
        b=Image.new('RGB',(1280,800),(224,221,211));im=Image.open(P/f'previews/{mode}/{f:04d}.png').convert('RGB');b.paste(im,((1280-im.width)//2,45));d=ImageDraw.Draw(b)
        d.text((16,7),f'V031 | ROUGH CONSTRUCTION | {mode} | 30fps | F{f:02d}/96',font=font,fill=(24,24,22));d.text((16,775),'32 drawings x3 uninterrupted cycles | static world ruler | NOT APPROVED / NOT FINISHED',font=small,fill=(24,24,22));proc.stdin.write(b.tobytes())
proc.stdin.close();err=proc.stderr.read();code=proc.wait();assert code==0,err.decode(errors='replace')[-3000:]
reader=F.read_frames(str(dest),pix_fmt='rgb24');meta=next(reader);count=0;selected=[]
for n,raw in enumerate(reader):
    count+=1
    if n in [0,3,9,12,16,19,25,28,31,32,63,64,95,96,127,159,191]:
        destframe=P/f'previews/DECODED_{n:03d}.png';Image.frombytes('RGB',meta['size'],raw).save(destframe);selected.append(str(destframe.relative_to(P)))
assert count==192 and meta['fps']==30 and dest.stat().st_size<20_000_000
report={'file':str(dest.relative_to(P)),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'decoded_frames':count,'fps':meta['fps'],'size':meta['size'],'seconds':count/meta['fps'],'layout':'3.2s close, then3.2s shot; each three uninterrupted authored32-frame cycles; no slow motion, holds or optical interpolation','selected_actual_encoded_frames':selected,'observation_limit':'Decoded actual movie frames inspected. Continuous player playback was not observed through available tools; independent normal-speed review is required.','status':'CONSTRUCTION TEST, not approved/finished animation'}
(P/'evidence/ENCODE_AND_DECODE_CHECK.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
