from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math
P=Path(__file__).resolve().parents[1];poses=json.loads((P/'evidence/authored_story_poses.json').read_text());font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
frames=[1,10,13,16,19,22,27,34,38,43,49,56,64]
short={1:'TRY TO KEEP UP',10:'TOE STOPS / BODY CONTINUES',13:'LOSE BALANCE / ARMS SPLIT',16:'URGENT CATCH FOOT',19:'HEEL ARRIVES / CHEST CONTINUES',22:'DEEP LOAD / HAND BRACES',27:'GIRL: BOTH HEELS DOWN',34:'ATTEND / GATHER FEET',38:'GATHER EFFORT',43:'LEG PUSH / CHEST LAGS',49:'HIP UP / RELEASE BRACE',56:'SHOULDER AND HEAD SETTLE',64:'SUPPORTED PAUSE / ATTEND'}
for mode in ['INSPECTION','SHOT_SIZE']:
 # Sheet crops retain actual pixel scale: no enlarging shot-size silhouettes.
 panel=(500,430);out=Image.new('RGB',(1500,math.ceil(len(frames)/3)*430+60),(237,237,232));d=ImageDraw.Draw(out);d.text((12,10),f'V014 WHOLE-POSE STEPPED BLOCKING / {mode} / 3s / NO CURVE POLISH',font=font,fill='black')
 for i,f in enumerate(frames):
  im=Image.open(P/f'previews/{mode}/{f:04d}.png').convert('RGB').crop((220,70,720,460));x=i%3*500;y=60+i//3*430;out.paste(im,(x,y+40));d.text((x+8,y+3),f'{f:02d} / {(f-1)/24:.3f}s / {short[f]}',font=font,fill='black')
 out.save(P/f'WTSC_v014_{mode}_Key_Poses.jpg',quality=95)
