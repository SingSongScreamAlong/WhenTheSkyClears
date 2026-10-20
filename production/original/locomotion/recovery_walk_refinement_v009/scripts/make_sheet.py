from pathlib import Path
from PIL import Image,ImageDraw
import sys,math
P=Path(__file__).resolve().parents[1];mode=sys.argv[1] if len(sys.argv)>1 else 'neutral';files=sorted((P/f'previews/{mode}').glob('*.png'))
if len(files)>18:files=[files[i-1] for i in [1,37,44,45,73,81,86,94,99,102,108,112,116,120]]
width=480;height=270;rows=math.ceil(len(files)/3);out=Image.new('RGB',(width*3,rows*(height+25)),(236,232,221));draw=ImageDraw.Draw(out)
for i,p in enumerate(files):
 im=Image.open(p).convert('RGB');im.thumbnail((width,height));x=(i%3)*width;y=(i//3)*(height+25);out.paste(im,(x,y+25));draw.text((x+8,y+7),f'{mode} / {1800+int(p.stem)} / {75+(int(p.stem)-1)/24:.3f}s',fill=(25,25,25))
out.save(P/f'evidence/v009_{mode}_contact_sheet.jpg',quality=94);print('SHEET',len(files),str(P/f'evidence/v009_{mode}_contact_sheet.jpg'))
