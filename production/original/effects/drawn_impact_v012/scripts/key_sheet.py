from pathlib import Path
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1]
frames=list(range(6,16))+[18,22,26,30,36,72]
sheet=Image.new('RGB',(1600,760),(24,26,27));d=ImageDraw.Draw(sheet)
for i,f in enumerate(frames):
    im=Image.open(P/f'previews/painted_keys/{f:04d}.png').convert('RGB')
    crop=im.crop((1260,580,1810,790));crop.thumbnail((390,150))
    x=(i%4)*400;y=(i//4)*190
    sheet.paste(crop,(x,y+25));d.text((x+8,y+6),f'Frame {f} | age {f-7}',fill=(220,220,220))
sheet.save(P/'previews/WTSC_Drawn_Impact_Actual_Keys_v012.jpg',quality=94)
