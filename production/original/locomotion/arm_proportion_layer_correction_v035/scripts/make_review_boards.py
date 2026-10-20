from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json
P=Path(__file__).resolve().parents[1];ROOT=P.parents[1];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20);title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',32)
data=json.loads((P/'evidence/STILL_RENDER_RECORD.json').read_text())
def img(mode,f):return Image.open(P/'previews'/mode/f'{f:04d}.png').convert('RGB')
def source(view,f):return Image.open(ROOT/'locomotion/preferred_walk_consistent_footwear_v033/previews'/view/f'{f:04d}.png').convert('RGB')
def label(d,xy,t,font=small):d.text(xy,t,font=font,fill='#18252c')
def guided(variant,f):
 im=img(variant+'_GUIDES_CLOSE',f);d=ImageDraw.Draw(im);r=data['joint_projections'][variant]['CLOSE'][str(f)]
 for side in ['near','far']:
  for key,t in [('Hip','H'),('Knee','K'),('Ankle','A')]:
   x,y=r[side][key];dx,dy=(9,3) if side=='near' else (-22,-22);c='#b23b1d' if side=='near' else '#126db3';d.text((x+dx,y+dy),t,font=small,fill=c,stroke_width=1,stroke_fill='#eeece5')
 return im
panels=[]
for f in [11,20,27]:
 b=Image.new('RGB',(2560,1700),'#eeeae1');d=ImageDraw.Draw(b);label(d,(25,14),f'v035 / F{f:02d}  |  preferred v028/v033 motion retained',title)
 for x,name,im in [(30,'A  Preferred v033',source('CLOSE',f)),(535,'B  Arm refit + local values',img('ARMS_CLOSE',f)),(1040,'C  Arms + straight-axis trousers',img('ALL_CLOSE',f)),(1545,'D  Source / actual bone axes',guided('SOURCE',f)),(2050,'E  v035 / actual bone axes',guided('ALL',f))]:
  label(d,(x,66),name);b.paste(im,(x,102))
 label(d,(30,834),'A-C: native charcoal renders. D-E: light working materials; orange near / blue far. H hip, K knee, A ankle. No hand x-rays.')
 b.paste(source('SHOT',f),(0,898));b.paste(img('ALL_SHOT',f),(1280,898));label(d,(25,865),'A  Preferred source / actual 1280 x 720 shot');label(d,(1305,865),'C  v035 combined / actual 1280 x 720 shot')
 label(d,(25,1630),'Static shape review only. Timing, root, foot contacts and hand paths retained. No full-cycle render or animation acceptance.')
 out=P/'previews'/f'WTSC_v035_F{f:02d}_Matched_Structure_Review.png';b.save(out);panels.append(out)
# One consolidated private deliverable; three 1700px frame panels retain exact shot size.
combined=Image.new('RGB',(2560,1700*3+220),'#eeeae1');d=ImageDraw.Draw(combined)
label(d,(25,20),'v035  |  Arm proportions and leg structure: matched still review',title)
label(d,(25,70),'Leg cause: straight rigid bones underneath continuously bowed trouser drawings. Candidate localizes the bend at the knee.')
label(d,(25,105),'Arm test: same shoulder/wrist paths and total reach; shorter upper arm, longer forearm; original painted hands and widths.')
label(d,(25,140),'Far hand remains behind near-side body/coat where the pose overlaps. Light guides show actual skeleton; no hand is projected forward.')
label(d,(25,175),'F11, F20, F27 only. Full-cycle motion and final art approval remain open.')
for i,p in enumerate(panels):combined.paste(Image.open(p),(0,220+i*1700))
combined.save(P/'previews/WTSC_v035_Matched_Arm_and_Leg_Structure_Comparison.png')
# Compact lossless contact sheet for quick visual inspection (explicitly scaled).
for f in [11,20,27]:
 b=Image.new('RGB',(1920,800),'#eeeae1');d=ImageDraw.Draw(b)
 for i,(name,im) in enumerate([('Source',source('CLOSE',f)),('Arms',img('ARMS_CLOSE',f)),('Combined',img('ALL_CLOSE',f)),('Source axes',img('SOURCE_GUIDES_CLOSE',f))]):label(d,(i*480+8,12),name);b.paste(im,(i*480,55))
 b.save(P/'previews'/f'INSPECTION_F{f:02d}.png')
print('V035_BOARDS_READY')
