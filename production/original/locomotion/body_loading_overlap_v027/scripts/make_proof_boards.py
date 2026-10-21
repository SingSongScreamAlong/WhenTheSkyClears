from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
P=Path(__file__).resolve().parents[1];font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',21)
old=P.parent/'gp_extended_review_v026/previews/PROOF';new=P/'previews/PROOF'
board=Image.new('RGB',(1920,1600),'#eee9dd');d=ImageDraw.Draw(board)
frames=[1,4,6,9,12,17,20,27]
for r,(folder,label) in enumerate([(old,'V026 baseline'),(new,'V027 loading + passive hem')]):
    for i,f in enumerate(frames):
        x=i*240;y=r*400;im=Image.open(folder/f'{f:04d}.png').convert('RGB').resize((240,360));board.paste(im,(x,y+40));d.text((x+5,y+6),f'{"V026" if r==0 else "V027"} | F{f}',font=font,fill='#292622')
for r,(folder,label) in enumerate([(old,'V026'),(new,'V027')]):
    for i,f in enumerate([24,25,26,27,28,29,30,31]):
        x=i*240;y=800+r*400;board.paste(Image.open(folder/f'{f:04d}.png').convert('RGB').resize((240,360)),(x,y+40));d.text((x+5,y+6),f'{label} late spacing | F{f}',font=font,fill='#292622')
board.save(P/'evidence/MATCHED_LOADING_AND_LATE_SPACING.jpg',quality=95)
board=Image.new('RGB',(1920,1600),'#eee9dd');d=ImageDraw.Draw(board)
for i,f in enumerate(range(1,33)):
    x=(i%8)*240;y=(i//8)*400;board.paste(Image.open(new/f'{f:04d}.png').convert('RGB').resize((240,360)),(x,y+40));d.text((x+8,y+6),f'V027 | F{f}',font=font,fill='#292622')
board.save(P/'evidence/V027_ALL_32_PROOF_FRAMES.jpg',quality=95)
print('MATCHED_PROOF_BOARDS_COMPLETE')
