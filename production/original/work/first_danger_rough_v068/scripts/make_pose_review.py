from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).resolve().parents[1];frames=[(973,'TURN BACK / SEARCH'),(991,'RECEIVE / SETTLE'),(1003,'LOOK AHEAD / MOVE')]
out=Image.new('RGB',(2160,3*900),'#111820');d=ImageDraw.Draw(out);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',32)
for i,(g,name) in enumerate(frames):
 im=Image.open(O/f'renders/uhd_E/world/{g:04d}.png').convert('RGB').crop((840,450,3000,1710));im.thumbnail((1440,840),Image.Resampling.LANCZOS)
 y=i*900;d.text((20,y+12),f'v068 ROUGH | {name} | G{g}',font=font,fill='white');out.paste(im,(360,y+58))
out.save(O/'previews/Rough_Acting_Native_Poses_v068e.jpg',quality=94)
print('NATIVE_POSE_REVIEW_READY')
