from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];V=P/'previews';fontpath='C:/Windows/Fonts/segoeui.ttf';boldpath='C:/Windows/Fonts/segoeuib.ttf'
def ft(n,b=False):return ImageFont.truetype(boldpath if b else fontpath,n)
out=Image.new('RGB',(2560,1600),'#202a2c');d=ImageDraw.Draw(out)
for row,view in enumerate(['NEUTRAL_SIDE','WALK_F05']):
 for col,tag in enumerate(['BEFORE','AFTER']):
  x=col*1280;y=row*800;d.text((x+22,y+12),('v048 before' if tag=='BEFORE' else 'v049 model fit')+' | '+('actual neutral side view' if not row else 'same F5 loading pose'),font=ft(27,True),fill='#f0eadf');d.text((x+22,y+48),'Same bones, face/hair, hand length and gait; garment fit and hand grouping only',font=ft(19),fill='#c1c9c6');out.paste(Image.open(V/(tag+'_'+view+'.png')).convert('RGB'),(x,y+80))
out.save(V/'WTSC_v048_v049_Model_Fit_Before_After.png')
out=Image.new('RGB',(2560,800),'#202a2c');d=ImageDraw.Draw(out)
for col,tag in enumerate(['BEFORE','AFTER']):
 x=col*1280;d.text((x+22,12),('v048 before' if tag=='BEFORE' else 'v049 grouped fingers and continuous wrist'),font=ft(27,True),fill='#f0eadf');d.text((x+22,48),'Actual neutral sleeves/forearms/hands; body hidden in RAM; identical 1.6m camera',font=ft(19),fill='#c1c9c6');out.paste(Image.open(V/(tag+'_ARMS_WRISTS_HANDS_DETAIL.png')).convert('RGB'),(x,80))
out.save(V/'WTSC_v048_v049_Wrist_Cuff_Hand_Comparison.png')
if all((V/('AFTER_WALK_F%02d.png'%f)).is_file() for f in [1,5,9]):
 out=Image.new('RGB',(2560,1600),'#202a2c');d=ImageDraw.Draw(out)
 for i,(view,title) in enumerate([('NEUTRAL_SIDE','Actual neutral standing side view'),('WALK_F01','F1 contact'),('WALK_F05','F5 loading'),('WALK_F09','F9 passing')]):
  x=(i%2)*1280;y=(i//2)*800;d.text((x+22,y+12),'v049 | '+title,font=ft(27,True),fill='#f0eadf');d.text((x+22,y+48),'Same framing, scale and preserved v048 gait; targeted static model-fit candidate',font=ft(19),fill='#c1c9c6');out.paste(Image.open(V/('AFTER_'+view+'.png')).convert('RGB'),(x,y+80))
 out.save(V/'WTSC_v049_Neutral_And_Three_Walk_Poses.png')
print('V049_STATIC_MODEL_COMPARISON_BOARDS_READY')
