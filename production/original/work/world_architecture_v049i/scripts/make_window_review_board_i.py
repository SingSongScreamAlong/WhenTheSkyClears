from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
O=Path(__file__).parent;W=2304;M=32;G=32;CW=1104;BG='#15191b';FG='#ebeee8';MUTED='#b5beb9';ACC='#cfb885'
font=lambda n,b=False:ImageFont.truetype('C:/Windows/Fonts/seguisb.ttf' if b else 'C:/Windows/Fonts/segoeui.ttf',n)
header=210;rowh=38+621+24;croph=52+860+24;H=header+3*rowh+2*croph+180
canvas=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(canvas)
d.text((M,24),'WHEN THE SKY CLEARS  /  v049i WINDOW DEPTH PROOF',font=font(37,True),fill=FG)
d.text((M,76),'Partial architecture experiment • original palette • actual Blender 3840 × 2160 source frames',font=font(28),fill=MUTED)
d.text((M,120),'High-resolution painted facade and wider ruin reconstruction remain OPEN.',font=font(28,True),fill=ACC)
d.text((M,169),'BEFORE  /  preserved v048d',font=font(27,True),fill=FG);d.text((M+CW+G,169),'AFTER  /  separate diagnostic v049i',font=font(27,True),fill=FG)
def frame(f,after):return Image.open(O/('native_4k_after' if after else 'native_4k_before')/(f'WTSC_v049i_School_{f}_4K.png' if after else f'WTSC_v048d_School_{f}_4K.png')).convert('RGB')
y=header
for f,label in [(1225,'51.000 s • selected window / full composition'),(1249,'52.000 s • adjacent camera / fixed world construction'),(1297,'54.000 s • later camera / original ruined wall restored')]:
 d.text((M,y),f'FRAME {f}  |  {label}',font=font(26),fill=MUTED);y+=38
 for col,after in enumerate([False,True]):canvas.paste(frame(f,after).resize((CW,621),Image.Resampling.LANCZOS),(M+col*(CW+G),y))
 y+=621+24
for f,box,label in [(1225,(1520,0,2624,860),'NATIVE 4K PIXELS • selected aperture / no crop rescaling'),(1297,(2640,40,3744,900),'NATIVE 4K PIXELS • ruined-wall painting restored / failed split removed')]:
 d.text((M,y),label,font=font(27,True),fill=ACC);y+=52
 for col,after in enumerate([False,True]):canvas.paste(frame(f,after).crop(box),(M+col*(CW+G),y))
 y+=884
d.text((M,y+8),'Kept: 35 cm window reveal, 62 cm backing, source-painted timber/glass thickness; clean ground sampling.',font=font(25),fill=FG)
d.text((M,y+49),'Rejected: masonry grid seams, added sill, broad wall return and rear split. Original facade remains 1672 × 941.',font=font(25),fill=MUTED)
d.text((M,y+90),'Cameras, children, actions and trailer timing preserved. Still review only; no production palette or rig integration.',font=font(25),fill=MUTED)
out=O/'WTSC_v049i_Window_Depth_Proof_Before_After_4K_Crops.jpg';canvas.save(out,quality=95,subsampling=0)
canvas.resize((1152,H//2)).save(O/'BOARD_LAYOUT_QA.jpg',quality=90)
for f in [1225,1297]:frame(f,True).resize((960,540)).save(O/f'Final_{f}_QA.png')
frame(1225,True).crop((1520,0,2624,860)).save(O/'FINAL_WINDOW_NATIVE_PIXELS.png')
frame(1297,True).crop((2640,40,3744,900)).save(O/'FINAL_RUIN_NATIVE_PIXELS.png')
q=json.loads((O/'ARCHITECTURE_VERIFICATION_v049i.json').read_text());q['review_board']=str(out);q['review_board_sha256']=hashlib.sha256(out.read_bytes()).hexdigest();q['review_board_dimensions']=[W,H]
q['visual_assessment']='PARTIAL: source-registered broken glass edges and timber/reveal depth survive adjacent still views; diagrammatic masonry and failed wall split removed. Original facade detail remains visibly soft at1:1, so high-resolution painted architecture gate is not met.'
(O/'ARCHITECTURE_VERIFICATION_v049i.json').write_text(json.dumps(q,indent=2));print(out.name,out.stat().st_size,[W,H])
