from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
P=Path(__file__).resolve().parents[1];old=P.parent/'four_pose_silhouette_rebuild_v029/previews';font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',25);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
if not (old/'CLOSE/0001.png').exists():old=P/'reference/V029_RENDERS'
poses=[(1,'CONTACT'),(4,'LOADED DOWN'),(11,'PASSING'),(13,'UP')]
board=Image.new('RGB',(1920,1560),'#eee9dd');d=ImageDraw.Draw(board)
for row,(folder,mode,label) in enumerate([(old,'CLOSE','V029 baseline'),(P/'previews','CLOSE','V030 revised volume')]):
    for i,(f,name) in enumerate(poses):
        x=i*480;y=row*780;board.paste(Image.open(folder/mode/f'{f:04d}.png').convert('RGB'),(x,y+60));d.text((x+12,y+8),f'{label}',font=font,fill='#292622');d.text((x+12,y+36),f'{name} | source phase F{f}',font=small,fill='#292622')
board.save(P/'previews/WTSC_v030_vs_v029_Four_Pose_Close_Board.png');board.save(P/'evidence/FOUR_POSE_CLOSE_COMPARISON.jpg',quality=95)
board=Image.new('RGB',(2560,800),'#eee9dd');d=ImageDraw.Draw(board)
for row,(folder,mode,label) in enumerate([(old,'SHOT','V029 baseline'),(P/'previews','SHOT','V030 revised volume')]):
    for i,(f,name) in enumerate(poses):
        x=i*640;y=row*400;board.paste(Image.open(folder/mode/f'{f:04d}.png').convert('RGB').resize((640,360)),(x,y+40));d.text((x+12,y+7),f'{label} | {name}',font=font,fill='#292622')
board.save(P/'previews/WTSC_v030_vs_v029_Four_Pose_Shot_Board.png');board.save(P/'evidence/FOUR_POSE_SHOT_COMPARISON.jpg',quality=95)
close=Image.open(P/'previews/WTSC_v030_vs_v029_Four_Pose_Close_Board.png').convert('RGB');shot=Image.open(P/'previews/WTSC_v030_vs_v029_Four_Pose_Shot_Board.png').convert('RGB').resize((1920,600))
review=Image.new('RGB',(1920,2220),'#eee9dd');review.paste(close,(0,0));review.paste(shot,(0,1620));ImageDraw.Draw(review).text((14,1572),'SAME SHOT CAMERA BELOW | Four poses only; no cycle or artistic pass claimed',font=font,fill='#292622');review.save(P/'previews/WTSC_v030_Four_Pose_Review_Board.png')
print('V030_COMPARISON_BOARDS_COMPLETE')
