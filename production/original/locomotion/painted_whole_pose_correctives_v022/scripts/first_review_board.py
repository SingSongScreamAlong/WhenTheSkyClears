from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];f=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',25)
for scale in ['CLOSE','SHOT']:
 im=Image.new('RGB',(1920,1160),'#eee9dc');d=ImageDraw.Draw(im)
 for j,phase in enumerate(['L_LOADING','L_PASSING']):
  for i,label in enumerate(['BEFORE','AFTER']):
   x=i*960;y=j*580;d.text((x+20,y+8),phase+' | '+label+' | '+scale,font=f,fill='#272622');im.paste(Image.open(P/f'previews/{phase}/{label}_{scale}.png').convert('RGB'),(x,y+40))
 im.save(P/f'evidence/FIRST_{scale}_PAINTED_REVIEW.jpg',quality=95)

