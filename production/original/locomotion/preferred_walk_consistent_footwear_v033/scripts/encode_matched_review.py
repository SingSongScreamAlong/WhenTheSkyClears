import json,subprocess,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg as F
P=Path(__file__).resolve().parents[1];OLD=P.parent/'upper_body_pose_refinement_v028';ff=F.get_ffmpeg_exe();font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19);BG=(224,221,211);reports={}
for kind,name,size in [('MATCHED','WTSC_v033_vs_v028_Preferred_Movement_18p6s.mp4',(1280,840)),('CANDIDATE','WTSC_v033_Consistent_Shoes_Normal_Speed_18p6s.mp4',(1280,800))]:
    dest=P/'previews'/name;args=[ff,'-loglevel','error','-nostats','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{size[0]}x{size[1]}','-r','30','-i','-','-an','-c:v','libx264','-threads','2','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(dest)];proc=subprocess.Popen(args,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    for mode in ['CLOSE','SHOT']:
        for f in range(1,280):
            b=Image.new('RGB',size,BG);d=ImageDraw.Draw(b);new=Image.open(P/f'previews/{mode}/{f:04d}.png').convert('RGB')
            if kind=='MATCHED':
                old=Image.open(OLD/f'previews/{mode}/{f:04d}.png').convert('RGB');d.text((16,5),f'Preferred V028 movement retained | {mode} | F{f:03d}/279 | 30fps',font=font,fill=(24,24,22));d.text((80,35),'V028 | preferred movement',font=small,fill=(24,24,22));d.text((720,35),'V033 | same movement / consistent shoes',font=small,fill=(24,24,22))
                if mode=='CLOSE':b.paste(old,(80,60));b.paste(new,(720,60))
                else:b.paste(old.resize((640,360),Image.Resampling.LANCZOS),(0,240));b.paste(new.resize((640,360),Image.Resampling.LANCZOS),(640,240))
                d.text((16,790),'Same native frame, time and camera | 31-frame cycle | shot panels shown at50% each',font=small,fill=(24,24,22));d.text((16,815),'Footwear correction only | user review pending | no production integration',font=small,fill=(24,24,22))
            else:
                b.paste(new,((1280-new.width)//2,45));d.text((16,6),f'V033 | preferred V028 movement / consistent shoes | {mode} | F{f:03d}/279',font=font,fill=(24,24,22));d.text((16,775),'30fps | nine cycles per view | one painted shoe asset | far97% perspective | review candidate',font=small,fill=(24,24,22))
            proc.stdin.write(b.tobytes())
    proc.stdin.close();err=proc.stderr.read();assert proc.wait()==0,err.decode(errors='replace')[-2000:]
    reader=F.read_frames(str(dest),pix_fmt='rgb24');meta=next(reader);count=0;selected=[];indices=[0,3,10,16,19,26,30,31,61,92,185,278,279,309,557] if kind=='MATCHED' else [0,16,26,278,279,557]
    for n,raw in enumerate(reader):
        count+=1
        if n in indices:
            p=P/f'previews/DECODED_{kind}_{n:03d}.png';Image.frombytes('RGB',meta['size'],raw).save(p);selected.append(str(p.relative_to(P)))
    assert count==558 and meta['fps']==30 and dest.stat().st_size<20_000_000
    reports[kind]={'file':str(dest.relative_to(P)),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'decoded_frames':count,'fps':meta['fps'],'size':meta['size'],'seconds':18.6,'layout':'9.3s close then9.3s shot; nine31-frame cycles per view','baseline':'Actual unchanged V028 source renders matched to V033 native frames1..279; no retiming, holds, phase alignment, interpolation or frame recycling','selected_actual_encoded_frames':selected,'observation_limit':'Decoded actual movie frames inspected; continuous player playback not observed through available tools. New footwear/user review remains pending.'}
(P/'evidence/MATCHED_ENCODE_AND_DECODE_CHECK.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports,indent=2))
