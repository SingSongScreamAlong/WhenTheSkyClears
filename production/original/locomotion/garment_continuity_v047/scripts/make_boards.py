from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
O=Path(r'WTSC_LOCAL_WORKSPACE\locomotion\garment_continuity_v047')
font=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',18)
for name in ['baseline','candidate']:
 folder=O/'previews'/name
 if not (folder/'0032.png').exists():continue
 board=Image.new('RGB',(2048,656),(20,21,24));d=ImageDraw.Draw(board)
 for i in range(32):
  im=Image.open(folder/f'{i+1:04d}.png').convert('RGB').resize((256,144));x=i%8*256;y=i//8*164;board.paste(im,(x,y+20));d.text((x+6,y+1),str(i+1),font=font,fill='white')
 board.save(O/'previews'/f'{name}_cycle_all32.jpg',quality=92)
 board=Image.new('RGB',(1600,1040),(20,21,24));d=ImageDraw.Draw(board)
 for i,f in enumerate([1,5,9,13,17,21,25,29]):
  im=Image.open(folder/f'{f:04d}.png').convert('RGB').crop((335,250,945,710)).resize((400,302));x=i%4*400;y=i//4*520;board.paste(im,(x,y+25));d.text((x+8,y+2),f'{name} F{f}',font=font,fill='white')
 board=board.crop((0,0,1600,847));board.save(O/'previews'/f'{name}_garment_keys.jpg',quality=94)
print('BOARDS_READY',flush=True)
