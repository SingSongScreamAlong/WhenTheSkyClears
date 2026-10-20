from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
O=Path(r'WTSC_LOCAL_USER\Documents\Codex\2026-10-16\task\world_art_v048')
font=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',32);title=ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf',46)
rows=[('Peaceful village - frame241 /10.000s','peaceful',241),('Transition / damaged school - frame1201 /50.000s','transition',1201),('War zone - frame1849 /77.000s','war_zone',1849)]
board=Image.new('RGB',(3840,3560),(20,23,25));draw=ImageDraw.Draw(board);draw.text((32,12),'WTSC WORLD ART v048d - NATIVE BLENDER BEFORE / AFTER',(236,233,225),font=title);draw.text((32,72),'Open diagnostic views. Each panel downsampled from a separate3840x2160 native render. Partial art checkpoint; target remains open.',(198,199,196),font=font)
checks=[]
for j,(label,kind,f) in enumerate(rows):
 y=140+j*1140;draw.text((25,y),label+' | BEFORE v040',(218,217,210),font=font);draw.text((1945,y),label+' | AFTER v048d',(218,217,210),font=font)
 for i,(folder,version) in enumerate([('native_4k_before','v040'),('native_4k_after_d','v048d')]):
  p=O/folder/f'WTSC_{version}_{kind}_{f}_4K.png';im=Image.open(p);im.load();assert im.size==(3840,2160);board.paste(im.convert('RGB').resize((1920,1080),Image.Resampling.LANCZOS),(i*1920,y+48));checks.append({'path':str(p),'dimensions':im.size,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
board.save(O/'WTSC_World_Art_v048d_Before_After_Three_Regions.jpg',quality=94,subsampling=0)
# Native-pixel crops: no resizing of the art.
crop=Image.new('RGB',(2048,2160),(20,23,25));d=ImageDraw.Draw(crop)
for j,(kind,f,box) in enumerate([('peaceful',241,(0,1100,1024,2124)),('transition',1201,(250,100,1274,1124))]):
 for i,(folder,version) in enumerate([('native_4k_before','v040'),('native_4k_after_d','v048d')]):
  im=Image.open(O/folder/f'WTSC_{version}_{kind}_{f}_4K.png').convert('RGB');crop.paste(im.crop(box),(i*1024,j*1080+50));d.text((i*1024+16,j*1080+6),f'{kind} {version} - actual4K pixels',(220,220,215),font=font)
crop.save(O/'WTSC_World_Art_v048d_Actual_4K_Crops.jpg',quality=95,subsampling=0)
(O/'render_file_verification.json').write_text(json.dumps(checks,indent=2));print(json.dumps({'comparison_bytes':(O/'WTSC_World_Art_v048d_Before_After_Three_Regions.jpg').stat().st_size,'native_4k_files':checks},indent=2))
