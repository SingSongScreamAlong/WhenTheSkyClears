from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parents[1]
def font(n):return ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
def label(im,xy,text,n=20):ImageDraw.Draw(im).text(xy,text,fill=(24,24,22),font=font(n))
bg=(224,221,211)
for first in [1,17]:
    b=Image.new('RGB',(1920,850),bg);label(b,(18,10),f'V031 | ROUGH CONSTRUCTION | F{first:02d}–F{first+15:02d} | drawings on ones, 30fps | NOT APPROVED',26)
    for i,f in enumerate(range(first,first+16)):
        x=(i%8)*240;y=60+(i//8)*390;im=Image.open(P/f'previews/PROOF_CLOSE/{f:04d}.png').convert('RGB').resize((240,360),Image.Resampling.LANCZOS);b.paste(im,(x,y+24));label(b,(x+9,y),f'F{f:02d}',18)
    b.save(P/f'previews/WTSC_v031_Breakdowns_F{first:02d}_{first+15:02d}.png')
b=Image.new('RGB',(1920,1620),bg);label(b,(18,12),'V030 accepted construction poses → V031 rough action key poses',31);label(b,(18,52),'Matched camera | first passing retimed F11→F10 | softened chest/waist and deliberate up-pose hand gap',22)
for row,version,frames in [(0,'V030',[1,4,11,13]),(1,'V031',[1,4,10,13])]:
    for i,f in enumerate(frames):
        path=P.parent/'four_pose_volume_revision_v030'/f'previews/CLOSE/{f:04d}.png' if row==0 else P/f'previews/PROOF_CLOSE/{f:04d}.png'
        y=100+row*760;b.paste(Image.open(path).convert('RGB'),(480*i,y+30));label(b,(480*i+12,y),f'{version} F{f:02d} | '+['CONTACT','LOADED DOWN','PASSING','UP'][i],21)
b.save(P/'previews/WTSC_v031_Construction_Pose_Board.png')
b=Image.new('RGB',(2560,1280),bg);label(b,(18,10),'V031 | ROUGH CONSTRUCTION | actual shot-size frames on neutral stage | NOT INTEGRATED / NOT FINISHED',28)
for i,f in enumerate([1,4,10,13,17,20,26,29]):
    x=(i%2)*1280;y=60+(i//2)*300;im=Image.open(P/f'previews/PROOF_SHOT/{f:04d}.png').convert('RGB').resize((533,300),Image.Resampling.LANCZOS);b.paste(im,(x+360,y));label(b,(x+12,y+12),f'F{f:02d}',24)
b.save(P/'previews/WTSC_v031_Shot_Size_Key_Board.png')
print('V031_BOARDS_SAVED')
