from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];im=Image.new('RGB',(1920,1160),'#ece6d8');d=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',25)
for j,name in enumerate(['LOADING','PASSING']):
 for i,(label,file) in enumerate([('V022 painted pose',ROOT/f'locomotion/painted_whole_pose_correctives_v022/previews/L_{name}/AFTER_CLOSE.png'),('V023 continuous coat',P/f'previews/V023_COAT_{name}_MATCHED_CLOSE.png')]):
  x=i*960;y=j*580;d.text((x+15,y+8),name+' | '+label,font=font,fill='#272522');im.paste(Image.open(file).convert('RGB'),(x,y+40))
im.save(P/'previews/WTSC_v023_Coat_Comparison.jpg',quality=95)

