from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];D=P/'previews/proof';im=Image.new('RGB',(1920,1440),'#ece6d8');dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
for i,f in enumerate(sorted(D.glob('*.png'))):
 x=(i%8)*240;y=(i//8)*360;im.paste(Image.open(f).convert('RGB'),(x,y));dr.text((x+8,y+8),'F'+f.stem.lstrip('0'),font=font,fill='#37342c')
im.save(P/'evidence/ALL_32_PROOF_FRAMES.jpg',quality=95)

