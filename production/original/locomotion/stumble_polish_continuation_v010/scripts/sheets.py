from pathlib import Path
from PIL import Image,ImageDraw
import sys,math
P=Path(__file__).resolve().parents[1];V9=P.parent/'recovery_walk_refinement_v009';mode=sys.argv[1] if len(sys.argv)>1 else 'neutral'
if mode=='early':
 frames=[25,33,37,41,45,53,69];out=Image.new('RGB',(960,len(frames)*235),(236,232,221));dr=ImageDraw.Draw(out)
 for i,f in enumerate(frames):
  for j,base in enumerate([V9,P]):
   im=Image.open(base/f'previews/neutral/{f:04d}.png').crop((275,130,700,490));im.thumbnail((480,210));out.paste(im,(j*480,i*235+25));dr.text((j*480+8,i*235+7),f'{"v009" if j==0 else "v010"} / local{f}',fill='black')
else:
 frames=[81,102,116,119,120,121,124,128,134,142,148,152,160,166,168];out=Image.new('RGB',(1440,math.ceil(len(frames)/3)*295),(236,232,221));dr=ImageDraw.Draw(out)
 for i,f in enumerate(frames):
  im=Image.open(P/f'previews/{mode}/{f:04d}.png').convert('RGB');im.thumbnail((480,270));x=(i%3)*480;y=(i//3)*295;out.paste(im,(x,y+25));dr.text((x+8,y+7),f'{mode} / global{f+1800} / {75+(f-1)/24:.3f}s',fill='black')
out.save(P/f'evidence/{mode}_review_sheet.jpg',quality=94);print('SHEET',mode)
