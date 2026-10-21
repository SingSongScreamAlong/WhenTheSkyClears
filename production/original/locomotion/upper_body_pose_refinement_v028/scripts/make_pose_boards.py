from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
P=Path(__file__).resolve().parents[1];O=P.parent/'body_loading_overlap_v027/previews';N=P/'previews';font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',21)
frames=[1,4,6,9,11,13,17,20,22,25,27,29]
board=Image.new('RGB',(1920,1584),'#eee9dd');d=ImageDraw.Draw(board)
for i,f in enumerate(frames):
    x=(i%6)*320;y=(i//6)*792
    for row,(folder,mode,label) in enumerate([(O,'CLOSE','V027'),(N,'PROOF_CLOSE','V028')]):
        im=Image.open(folder/mode/f'{f:04d}.png').convert('RGB');board.paste(im.resize((240,360)),(x+40,y+row*396+36));d.text((x+45,y+row*396+5),f'{label} | F{f}',font=font,fill='#292622')
board.save(P/'evidence/MATCHED_KEY_AND_BREAKDOWN_POSES.jpg',quality=95)
board=Image.new('RGB',(1920,1584),'#eee9dd');d=ImageDraw.Draw(board)
for i,f in enumerate(range(1,33)):
    x=(i%8)*240;y=(i//8)*396;board.paste(Image.open(N/'PROOF_CLOSE'/f'{f:04d}.png').convert('RGB').resize((240,360)),(x,y+36));d.text((x+6,y+5),f'V028 | F{f}',font=font,fill='#292622')
board.save(P/'evidence/V028_ALL32_NATIVE_POSES.jpg',quality=95)
# Preserve full shot scale for selected matched poses; crops supplement it.
frames=[4,11,20,27];board=Image.new('RGB',(1280,1600),'#eee9dd');d=ImageDraw.Draw(board)
for i,f in enumerate(frames):
    for row,(folder,mode,label) in enumerate([(O,'SHOT','V027'),(N,'PROOF_SHOT','V028')]):
        x=(i%2)*640;y=(i//2)*800+row*400;im=Image.open(folder/mode/f'{f:04d}.png').convert('RGB');board.paste(im.resize((640,360)),(x,y+40));d.text((x+8,y+6),f'{label} | original shot | F{f}',font=font,fill='#292622')
board.save(P/'evidence/MATCHED_SHOT_POSES.jpg',quality=95)
print('V028_POSE_BOARDS_COMPLETE')
