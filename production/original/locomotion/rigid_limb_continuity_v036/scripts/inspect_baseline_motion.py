from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json
P=Path(__file__).resolve().parents[1];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22);F=[1,5,9,11,15,17,20,24,27,31];b=Image.new('RGB',(2400,1540),'#e8e4db');d=ImageDraw.Draw(b)
for i,f in enumerate(F):
 p=P/'previews/BASE_CLOSE'/f'{f:04d}.png'
 if not p.exists():continue
 x=(i%5)*480;y=(i//5)*770;b.paste(Image.open(p).convert('RGB'),(x,y+40));d.text((x+10,y+8),f'v035 F{f:02d}',font=font,fill='#19242a')
b.save(P/'previews/V035_CYCLE_SHAPES.png')
print('BASELINE_CONTACT_SHEET_READY')
