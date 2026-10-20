from pathlib import Path
from PIL import Image,ImageDraw
import sys,json
P=Path(__file__).resolve().parents[1];folder=P/'previews'/('motion' if '--motion' in sys.argv else 'keys')
frames=[6,7,8,9,10,11,12,13,14,15,16,17,19,21,24,28,32]
sheet=Image.new('RGB',(1600,1250),(24,26,27));d=ImageDraw.Draw(sheet)
for i,f in enumerate(frames):
    im=Image.open(folder/f'{f:04d}.png').convert('RGB').crop((1220,455,1850,805));im.thumbnail((395,220));x=(i%4)*400;y=(i//4)*250;sheet.paste(im,(x,y+28));d.text((x+8,y+7),f'Actual frame {f} | age {f-7}',fill=(225,225,225))
sheet.save(P/'previews/WTSC_Connected_Wedge_ROUGH_Keys_v014.jpg',quality=94)
shot=Image.new('RGB',(1920,1120),(24,26,27));d=ImageDraw.Draw(shot)
for i,f in enumerate([6,9,13,16,21,28]):
    im=Image.open(folder/f'{f:04d}.png').convert('RGB');im.thumbnail((960,348));x=(i%2)*960;y=(i//2)*373;shot.paste(im,(x,y+25));d.text((x+8,y+6),f'Actual full-shot frame {f}',fill=(225,225,225))
shot.save(P/'previews/WTSC_Connected_Wedge_ROUGH_Shot_Size_v014.jpg',quality=93)
print('ROUGH_KEY_SEQUENCE_SAVED')
