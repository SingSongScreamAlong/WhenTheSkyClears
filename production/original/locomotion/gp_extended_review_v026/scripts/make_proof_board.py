from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
P=Path(__file__).resolve().parents[1];D=P/'previews/PROOF';font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18);board=Image.new('RGB',(1920,1584),'#eee9dd');d=ImageDraw.Draw(board)
for i in range(32):
    x=(i%8)*240;y=(i//8)*396;board.paste(Image.open(D/f'{i+1:04d}.png').convert('RGB').resize((240,360)),(x,y+36));d.text((x+7,y+6),f'F{i+1}'+(' bookend' if i==31 else ''),font=font,fill='#292622')
board.save(P/'evidence/FULL_CYCLE_32_FRAME_JOIN_PROOF.jpg',quality=95)
