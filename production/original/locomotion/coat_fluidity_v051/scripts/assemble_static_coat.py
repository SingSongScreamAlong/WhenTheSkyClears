from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
P=Path(__file__).resolve().parents[1];V=P/'previews'
def font(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if b else 'segoeui.ttf'),n)
def board(name,rows):
 im=Image.new('RGB',(2560,800*len(rows)),'#202a2c');d=ImageDraw.Draw(im)
 for row,(view,sub) in enumerate(rows):
  for col,tag in enumerate(['BEFORE','AFTER']):
   x=col*1280;y=row*800;d.text((x+22,y+10),'v050 | FROZEN COAT' if col==0 else 'v051 | CONTROLLED FLUID COAT',font=font(28,True),fill='#f0eadf');d.text((x+22,y+49),sub,font=font(19),fill='#c1c9c6');im.paste(Image.open(V/(tag+'_'+view+'.png')).convert('RGB'),(x,y+80))
 im.save(V/name)
board('WTSC_v050_v051_Same_Pose_Coat_And_Silhouette.png',[('COAT_DETAIL_F05','Same F5 bones, camera and painting | changed coat shape/response only'),('COAT_CONTOUR_ONLY_F05','Same F5 pose; coat only in RAM | hem inertia held at zero to isolate contour')])
rows=[('WALK_F01','Same F1 gait/phase/travel | face, hands, proportions and foot contacts retained'),('WALK_F17','Same F17 gait/phase/travel | no body timing changes')]
if (V/'AFTER_NEUTRAL_SIDE.png').exists():rows.insert(0,('NEUTRAL_SIDE','Same actual rest bones | hem inertia zeroed in RAM; clothing caches regenerated to rest'))
board('WTSC_v050_v051_Same_Gait_Full_Pose_Proof.png',rows)
board('WTSC_v050_v051_Fabric_Phases.png',[('COAT_DETAIL_F05','Actual native coat F5 | same underlying body motion'),('COAT_DETAIL_F13','Actual native coat F13 | same underlying body motion'),('COAT_DETAIL_F21','Actual native coat F21 | same underlying body motion'),('COAT_DETAIL_F29','Actual native coat F29 | same underlying body motion')])
print('V051_STATIC_COAT_BOARDS_COMPLETE')
