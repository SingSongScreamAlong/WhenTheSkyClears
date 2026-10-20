from pathlib import Path
import subprocess,json,hashlib
import imageio_ffmpeg
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];R=P.parents[1];ff=imageio_ffmpeg.get_ffmpeg_exe()
source=R/'renders/world_v016/integration_v046/WTSC_Supported_Recovery_v046_1080p_75_80.mp4'
outputs=[]
for mode,name in [('neutral','WTSC_v009_Neutral_Recovery_Walk_5s.mp4'),('matched','WTSC_v009_Matched_Recovery_Walk_75_80.mp4')]:
 files=list((P/f'previews/{mode}').glob('*.png'));assert len(files)==120,(mode,len(files))
 output=P/name;cmd=[ff,'-y','-v','error','-framerate','24','-i',str(P/f'previews/{mode}/%04d.png')]
 if mode=='matched':cmd+=['-i',str(source),'-map','0:v:0','-map','1:a:0?']
 cmd+=['-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-frames:v','120','-movflags','+faststart']
 if mode=='matched':cmd+=['-c:a','aac','-b:a','160k','-t','5']
 cmd+=[str(output)];subprocess.run(cmd,check=True,capture_output=True)
 outputs.append(output)
output=P/'WTSC_v046_vs_v009_Matched_Comparison_5s.mp4'
subprocess.run([ff,'-y','-v','error','-i',str(source),'-i',str(outputs[1]),'-filter_complex','[0:v]scale=960:540,setsar=1[a];[1:v]setsar=1[b];[a][b]hstack=inputs=2[v]','-map','[v]','-map','0:a:0?','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-frames:v','120','-t','5','-movflags','+faststart',str(output)],check=True,capture_output=True);outputs.append(output)
report=[]
for p in outputs:
 gen=imageio_ffmpeg.read_frames(str(p),pix_fmt='rgb24');meta=next(gen);count=sum(1 for _ in gen)
 row={'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'decoded_frames':count,'fps':meta['fps'],'size':meta['size'],'duration':meta['duration']};assert count==120 and meta['fps']==24 and p.stat().st_size<20_000_000,row;report.append(row)
(P/'evidence/preview_media_verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
