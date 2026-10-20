from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
P=Path(__file__).resolve().parents[1];OLD=P.parent/'coherent_garment_four_pose_v037/previews';BG='#e9e5dc';font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',27);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22);title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',38)
def text(d,xy,t,f=font):d.text(xy,t,font=f,fill='#1d2c32')
def im(mode,f):return Image.open(P/'previews'/mode/f'{f:04d}.png').convert('RGB')
def old(view,f):return Image.open(OLD/('PAINTED_'+view)/f'{f:04d}.png').convert('RGB')
H=6840;b=Image.new('RGB',(2560,H),BG);d=ImageDraw.Draw(b)
text(d,(35,20),'WHEN THE SKY CLEARS / BOY / FULL-COLOR CHARACTER STUDY v038',title)
text(d,(35,78),'Natural skin and hands, brown hair, slate fabric, linen collar/cuffs, olive trousers and matching leather shoes.')
text(d,(35,120),'Separate readable color version. Original dark treatment retained. Same head/profile, preferred poses and foot paths.',small)
text(d,(80,178),'FULL COLOR / F1 / actual 960 x 1440',font);text(d,(1420,178),'v037 DARK REFERENCE / same pose / actual 960 x 1440',font)
b.paste(im('HERO_COLOR',1),(80,220));b.paste(im('HERO_DARK_REFERENCE',1),(1420,220))
text(d,(35,1692),'Restrained painterly palette / original brush detail and image alpha retained',font)
palette=json.loads((P/'evidence/FULL_COLOR_BUILD.json').read_text())['palette']
for i,(role,label) in enumerate([('skin','Skin / hands'),('hair','Hair'),('coat','Coat / sleeves'),('linen','Collar / cuffs'),('trousers','Trousers'),('shoes','Matching shoes')]):
 x=40+i*420;text(d,(x,1740),label,small)
 for j,(_,c) in enumerate(palette[role]['stops']):d.rectangle((x+j*80,1780,x+j*80+74,1824),fill='#'+c)
text(d,(35,1872),'The original eye opening is retained, with a small shaded iris for this color version. No head turn or profile geometry change.',small)
text(d,(35,1920),'FULL-COLOR KEY POSES / actual 480 x 720 / clean art, no guides or x-rays',title)
for i,(f,label) in enumerate([(1,'CONTACT'),(4,'LOADED DOWN'),(11,'PASSING'),(20,'LOADED RECOVERY')]):
 x=80+i*620;text(d,(x,1974),f'F{f:02d} / {label}',font);b.paste(im('COLOR_CLOSE',f),(x,2020))
y=2800
for f in [1,11,20]:
 text(d,(30,y),f'F{f:02d} / ORIGINAL SHOT CAMERA / native 1280 x 720 per panel',font);text(d,(30,y+40),'v037 dark source',small);text(d,(1310,y+40),'v038 full color + local root repair',small);b.paste(old('SHOT',f),(0,y+76));b.paste(im('COLOR_SHOT',f),(1280,y+76));y+=820
# Five-pose garment study includes this extra overlap check, not an invented new gesture.
text(d,(30,5276),'F27 / HAND–HEM READABILITY CHECK / hand pose and garment length preserved',title)
b.paste(im('COLOR_CLOSE',27),(60,5340));b.paste(im('COLOR_SHOT',27),(1280,5340));detail=im('COLOR_CLOSE',27).crop((218,380,282,455)).resize((256,300),Image.Resampling.NEAREST);b.paste(detail,(740,5500));text(d,(650,5410),'Hand / hem, 4x actual pixels',small);text(d,(650,5450),'No overlay or lighting effect',small)
text(d,(30,6100),'LOCAL TROUSER-ROOT REPAIR / actual dark before–after confirms the contour change',title)
for group,f in enumerate([11,20]):
 x=group*1280+25;text(d,(x,6160),f'F{f:02d} / 3x actual-pixel hip details',font)
 for j,(label,a) in enumerate([('v037 before',old('CLOSE',f)),('v038 repair, dark',im('ROOT_REPAIR_DARK_CLOSE',f)),('v038 full color',im('COLOR_CLOSE',f))]):
  xx=x+j*410;text(d,(xx,6215),label,small);b.paste(a.crop((175,380,305,490)).resize((390,330),Image.Resampling.NEAREST),(xx,6255))
text(d,(30,6630),'Only upper trouser contour is rounded/tucked; original joints, drawing centerlines, lower legs, shoes and travel stay fixed.',small)
text(d,(30,6680),'Five static garment samples. Cloth inbetweens, moving color registration and paired acting remain unfinished. No production integration.',small)
text(d,(30,6730),'This is a full-color character candidate for artistic review; the final film silhouette treatment has not been replaced.',small)
dest=P/'previews/WTSC_v038_Full_Color_Boy_Reveal_and_Poses.png';b.save(dest)
# A compact actual-key-pose sheet for detailed local inspection.
c=Image.new('RGB',(1920,780),BG);dd=ImageDraw.Draw(c)
for i,f in enumerate([1,4,11,20]):text(dd,(i*480+10,12),f'v038 / F{f:02d}',font);c.paste(im('COLOR_CLOSE',f),(i*480,55))
c.save(P/'previews/WTSC_v038_Full_Color_Key_Poses.png')
r={'board':str(dest.relative_to(P)),'dimensions':b.size,'bytes':dest.stat().st_size,'hero_actual_size':[960,1440],'native_shot_pixels':[1280,720],'frames':[1,4,11,20,27],'composition':'Actual native renders pasted at original dimensions. Explicit3x/4x nearest-neighbor crops only for labelled overlap details. No retouching or generated replacement artwork.','full_color_not_diagnostic':'Coherent natural material palette, shared across matching skin/fabric/shoes; no joint colors or x-ray overlays.'};(P/'evidence/BOARD_RECORD.json').write_text(json.dumps(r,indent=2));assert dest.stat().st_size<20_000_000;print('V038_COLOR_BOARD_READY',json.dumps(r),flush=True)
