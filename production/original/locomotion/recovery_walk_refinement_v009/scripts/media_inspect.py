import subprocess,json
from pathlib import Path
from PIL import Image,ImageDraw
import imageio_ffmpeg
P=Path(__file__).resolve().parents[1];R=P.parents[1];ff=imageio_ffmpeg.get_ffmpeg_exe()
source=R/'renders/world_v016/integration_v046/WTSC_Supported_Recovery_v046_1080p_75_80.mp4'
frames=[1,25,37,44,45,61,81,89,101,110,115,120]
(P/'evidence').mkdir(exist_ok=True)
sheet=Image.new('RGB',(960,4*205),(240,237,228));draw=ImageDraw.Draw(sheet)
for i,f in enumerate(frames):
 data=subprocess.run([ff,'-v','error','-ss',str((f-1)/24),'-i',str(source),'-frames:v','1','-vf','scale=320:180','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True,check=True).stdout
 im=Image.frombytes('RGB',(320,180),data);sheet.paste(im,((i%3)*320,(i//3)*205+25));draw.text(((i%3)*320+8,(i//3)*205+6),f'v046 frame {1800+f} / {75+(f-1)/24:.3f}s',fill=(25,25,25))
sheet.save(P/'evidence/v046_actual_shot_contact_sheet.jpg',quality=94)
print('MEDIA_SHEET_SAVED')
