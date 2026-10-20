from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);frames=[11,27]
b=Image.new('RGB',(1440,1540),'#e8e4db');d=ImageDraw.Draw(b)
for row,f in enumerate(frames):
 for col,(label,file) in enumerate([('Preferred v033',ROOT/f'locomotion/preferred_walk_consistent_footwear_v033/previews/CLOSE/{f:04d}.png'),('v035 structure',P/f'previews/BASE_CLOSE/{f:04d}.png'),('v036 focused correction',P/f'previews/PROOF_CLOSE/{f:04d}.png')]):
  x=col*480;y=row*770;d.text((x+9,y+8),f'{label} / F{f:02d}',font=font,fill='#18252c');b.paste(Image.open(file).convert('RGB'),(x,y+42))
b.save(P/'previews/WTSC_v036_F11_F27_Art_Comparison.png')
for f in [1,4,11,20,27]:
 b=Image.new('RGB',(2560,1560),'#e8e4db');d=ImageDraw.Draw(b);d.text((20,12),f'v036 focused limb correction / F{f:02d} / same preferred v033 timing and camera / no guides',font=font,fill='#18252c');
 for x,file,label in [(0,ROOT/f'locomotion/preferred_walk_consistent_footwear_v033/previews/SHOT/{f:04d}.png','Preferred v033 / actual 1280x720'),(1280,P/f'previews/PROOF_SHOT/{f:04d}.png','v036 / actual 1280x720')]:
  d.text((x+20,52),label,font=font,fill='#18252c');b.paste(Image.open(file).convert('RGB'),(x,88))
 old=Image.open(ROOT/f'locomotion/preferred_walk_consistent_footwear_v033/previews/CLOSE/{f:04d}.png').convert('RGB');new=Image.open(P/f'previews/PROOF_CLOSE/{f:04d}.png').convert('RGB');b.paste(old,(400,824));b.paste(new,(1680,824));b.save(P/f'previews/WTSC_v036_Matched_F{f:02d}_Shot_and_Close.png')
print('V036_PROOF_BOARDS_READY')
