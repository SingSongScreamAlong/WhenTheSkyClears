from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1];V=P/'previews';R=V/'model_review';fontpath='C:/Windows/Fonts/segoeui.ttf';boldpath='C:/Windows/Fonts/segoeuib.ttf'
def ft(n,b=False):return ImageFont.truetype(boldpath if b else fontpath,n)
def board(entries,path):
 out=Image.new('RGB',(2560,1600),'#202a2c');d=ImageDraw.Draw(out)
 for i,(f,title,sub) in enumerate(entries):x=(i%2)*1280;y=(i//2)*800;d.text((x+22,y+12),title,font=ft(26,True),fill='#f0eadf');d.text((x+22,y+48),sub,font=ft(18),fill='#c1c9c6');out.paste(Image.open(f).convert('RGB'),(x,y+80))
 out.save(path)
board([(R/'CURRENT_NEUTRAL_STANDING_SIDE.png','A | v048 actual neutral standing side view','Identity rest bones; sleeve/leg drawings rebuilt to rest axes in RAM'),(R/'CURRENT_WALK_CONTACT_F01.png','B | v048 F1 contact','Same 3.25m camera width and scale'),(R/'CURRENT_WALK_LOADING_F05.png','C | v048 F5 loading','Same camera, anatomy and painting'),(R/'CURRENT_WALK_PASSING_F09.png','D | v048 F9 passing','Three actual walk poses; no model rescale or paint-over')],R/'WTSC_v048_Neutral_And_Three_Walk_Poses.png')
out=Image.new('RGB',(1400,1400),'#202a2c');d=ImageDraw.Draw(out)
for x,n,t in [(0,'OLDER_V041_BOY_ACTUAL_F1_SAME_METRES.png','Older preferred v041 | actual F1'),(700,'CURRENT_BOY_ACTUAL_F1_SAME_METRES.png','v048 | actual F1, age-ten bones')]:d.text((x+15,12),t,font=ft(22,True),fill='#f0eadf');d.text((x+15,48),'Identical metre/pixel camera; pose/anatomy differ',font=ft(17),fill='#c1c9c6');out.paste(Image.open(R/n).convert('RGB').crop((300,70,650,720)).resize((700,1300),Image.Resampling.LANCZOS),(x,100))
out.save(R/'WTSC_Older_v041_Current_v048_Model_Comparison.png')
# Correct inherited contact-sheet labels without re-encoding unchanged movies.
for block in range(4):
 out=Image.new('RGB',(1920,1170),'#202a2c');d=ImageDraw.Draw(out)
 for j,f in enumerate(range(1+block*8,9+block*8)):
  x=(j%3)*640;y=(j//3)*390;out.paste(Image.open(V/'frames_V048'/('FRAME_%04d.png'%f)).convert('RGB').resize((640,360),Image.Resampling.LANCZOS),(x,y+30));d.text((x+10,y+4),'Actual v048 native F%02d'%f,font=ft(18),fill='#f0eadf')
 out.save(V/('LOCAL_CYCLE_REVIEW_%d.jpg'%(block+1)),quality=95)
print('V048_MODEL_REVIEW_BOARDS_READY')
