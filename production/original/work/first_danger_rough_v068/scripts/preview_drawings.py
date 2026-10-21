from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import pose_spec as M
O=Path(__file__).resolve().parents[1]
frames=[951,961,973,985,991,1003]
W,H=1000,880;S=500
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
canvas=Image.new('RGB',(W*3,H*2),'#e7e4d9');cd=ImageDraw.Draw(canvas)
for i,g in enumerate(frames):
 im=Image.new('RGB',(W,H),'#e7e4d9');dr=ImageDraw.Draw(im);pp=M.paired(g);centre=sum(p['hip'][0]+p['offset'] for p in pp.values())/2
 def screen(p):return ((p[0]-centre)*S+W*.5,H-80-p[1]*S)
 dr.line([(0,H-80),(W,H-80)],fill='#a4a295',width=2)
 for w in ['BOY','GIRL']:
  d,p=M.draw_actor(w,g,pp)
  for q in d.paths:
   pts=[screen(v) for v in q['points']]
   if q['fill']:dr.polygon(pts,fill=M.PALETTE[q['fill']])
   if q['stroke']:dr.line(pts+([pts[0]] if q['closed'] else []),fill=M.PALETTE[q['stroke']],width=max(1,round(q['width']*S)),joint='curve')
 dr.text((20,20),f'ROUGH REPLACEMENT DRAWINGS | G{g}',font=font,fill='#252925')
 im.save(O/'previews'/f'Pose_{g}.png');canvas.paste(im,(i%3*W,i//3*H))
canvas.save(O/'previews/Rough_Pose_Board_A.jpg',quality=95)
print('POSE_BOARD_READY')
