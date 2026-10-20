from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
P=Path(__file__).resolve().parents[1];V=P/'previews'
def font(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
def board(name,rows):
 im=Image.new('RGB',(2560,800*len(rows)),'#202a2c');d=ImageDraw.Draw(im)
 for j,(view,subtitle) in enumerate(rows):
  for col,tag in enumerate(['BEFORE','AFTER']):
   x=col*1280;y=j*800;d.text((x+22,y+10),('v049 | RECEIVED BASELINE' if col==0 else 'v050 | FACE AND RELAXED HAND FINISH'),font=font(28,True),fill='#f0eadf');d.text((x+22,y+49),subtitle,font=font(19),fill='#c1c9c6');im.paste(Image.open(V/(tag+'_'+view+'.png')).convert('RGB'),(x,y+80))
 im.save(V/name)
board('WTSC_v049_v050_Face_And_Hands_Before_After.png',[('FACE_DETAIL_F01','Same F1 pose/camera | original head outline, hair/braid and gait retained'),('HANDS_DETAIL_NEUTRAL','Actual rest pose; bodies hidden only in RAM | same scale; developed hand length retained')])
board('WTSC_v049_v050_Finish_Neutral_And_Walk.png',[('NEUTRAL_SIDE','Same actual neutral bones and camera | outfit and proportions retained'),('WALK_F05','Same F5 walk pose, motion, phase and root travel')])
sheet=Image.new('RGB',(2560,1600),'#202a2c');d=ImageDraw.Draw(sheet)
for j,f in enumerate([1,9,17,25]):
 x=(j%2)*1280;y=(j//2)*800;d.text((x+20,y+12),'v050 actual existing walk F%02d'%f,font=font(28,True),fill='#f0eadf');d.text((x+20,y+48),'Face/hand finish only | frozen v049 gait',font=font(19),fill='#c1c9c6');sheet.paste(Image.open(V/('AFTER_WALK_F%02d.png'%f)),(x,y+80))
sheet.save(V/'WTSC_v050_Existing_Walk_Pose_Proof.png')
print('V050_STATIC_BOARDS_COMPLETE')
