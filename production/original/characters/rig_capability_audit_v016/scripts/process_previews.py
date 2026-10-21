import json,subprocess,hashlib,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter
import numpy as np
import imageio_ffmpeg
P=Path(__file__).resolve().parents[1];FF=imageio_ffmpeg.get_ffmpeg_exe()
FONT=Path(r'C:\Windows\Fonts\segoeui.ttf');BOLD=Path(r'C:\Windows\Fonts\segoeuib.ttf')
def font(n,b=False):return ImageFont.truetype(str(BOLD if b else FONT),n)
BG=(232,230,224);INK=(36,43,46);MUTED=(84,91,93)
def placed(canvas,path,box):
 im=Image.open(path).convert('RGB');im=ImageOps.contain(im,(box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS);canvas.paste(im,(box[0]+(box[2]-box[0]-im.width)//2,box[1]+(box[3]-box[1]-im.height)//2))
def cropped(canvas,path,crop,box):
 im=Image.open(path).convert('RGB').crop(crop);im=ImageOps.contain(im,(box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS);canvas.paste(im,(box[0]+(box[2]-box[0]-im.width)//2,box[1]+(box[3]-box[1]-im.height)//2))
labels=['Neutral identity','Planted squat','New off-cache intermediate','Reach / elbow bend','Heel contact','Flat support','Toe roll','Sole lift','Painted thigh brace','Profile tilt ONLY','Limb crossing','Pair gap0.8m / offer']
sheet=Image.new('RGB',(2560,1370),BG);d=ImageDraw.Draw(sheet);d.text((30,15),'v016  PAINTED RIG / NATIVE CONTROL STRESS TESTS',font=font(38,True),fill=INK);d.text((30,62),'Actual retained paint; original15/18-bone rigs. Technical linkage study; final-art readiness remains UNPASSED.',font=font(25),fill=MUTED)
for i,label in enumerate(labels):
 x=(i%4)*640;y=106+(i//4)*400;d.text((x+14,y),f'{i+1:02d}  {label}',font=font(23,True),fill=INK);placed(sheet,P/f'previews/pose_{i*20+1:03d}.png',(x+6,y+34,x+634,y+392))
d.text((30,1322),'Review gates: cuff and deep garment shapes; required girl head turn. These are rig tests, not approved story animation.',font=font(25),fill=INK)
sheet.save(P/'WTSC_v016_Painted_Pose_Stress_Tests.jpg',quality=92,subsampling=0)
def separation(part):
 masks=[];bounds=[]
 for who in ['BOY','GIRL']:
  im=Image.open(P/f'previews/clearance_{part}_{who}.png').convert('RGBA');a=np.asarray(im)[:,:,3]>.10*255
  er=np.asarray(Image.fromarray(a.astype('uint8')*255).filter(ImageFilter.MinFilter(3)))>0
  pts=np.argwhere(a&~er);bounds.append(pts);masks.append(a)
 best=1e20;pair=None
 for chunk in np.array_split(bounds[0],max(1,len(bounds[0])//200)):
  ds=((chunk[:,None,:].astype('float64')-bounds[1][None,:,:])**2).sum(2);i,j=np.unravel_index(ds.argmin(),ds.shape)
  if ds[i,j]<best:best=float(ds[i,j]);pair=[chunk[i].tolist(),bounds[1][j].tolist()]
 return {'alpha_threshold':.10,'pixel_gap_at1280px':math.sqrt(best),'approx_orthographic_gap_m':math.sqrt(best)*3/1280,'opaque_pixel_overlap':int((masks[0]&masks[1]).sum()),'closest_pixel_pair_yx':pair,'scope':'Only static v016 source-profile pair test221 at0.8m root gap; future approved turn drawings need a new clearance check.'}
clearance={name:separation(name) for name in ['head','offer_hand']}
(P/'evidence/painted_clearance_masks.json').write_text(json.dumps(clearance,indent=2))
detail=Image.new('RGB',(1920,1390),BG);d=ImageDraw.Draw(detail);d.text((25,15),'v016  CONTACTS, CONTROL RESPONSE AND HEAD LIMITS',font=font(34,True),fill=INK);d.text((25,60),'Original painting retained. Native contact measurements support only the tested range; artistic acceptance remains open.',font=font(22),fill=MUTED)
panels=[('Painted palm / thigh brace','Projected palm-edge gap0.5mm; native planar follower.'),('Original painted boots','Native soles and boot dimensions preserved; both sides tested.'),('New native HIP edit / feet fixed','All16 contours respond; no cached POSE_### clock.'),('Original profile / attached braid','In-plane tilt works. Looking back toward boy remains UNSOLVED.'),('Actual v046 movie:1843 /1844 /1845 /1846','Historical head disc at1844-45 is still a required-view defect.'),('Paired clearance /0.8m root gap','Original-profile heads clear; fingertips remain an offer, not a grasp.')]
for i,(title,caption) in enumerate(panels):
 x=(i%2)*960;y=108+(i//2)*410;d.text((x+15,y),title,font=font(24,True),fill=INK);d.text((x+15,y+34),caption,font=font(19),fill=MUTED)
 if i==0:cropped(detail,P/'previews/pose_161.png',(275,300,1080,650),(x+12,y+72,x+948,y+400))
 elif i==1:cropped(detail,P/'previews/pose_121.png',(255,500,1050,710),(x+12,y+72,x+948,y+400))
 elif i==2:
  for j,f in enumerate(['pose_041.png','pose_OFF_CACHE_CONTROL_EDIT.png']):cropped(detail,P/'previews'/f,(270,190,1100,705),(x+12+j*470,y+72,x+472+j*470,y+400))
 elif i==3:cropped(detail,P/'previews/pose_181.png',(280,70,1090,420),(x+12,y+72,x+948,y+400))
 elif i==4:
  for j in range(4):
   cropped(detail,P/f'reference/v046_actual_movie_frames/source_{j+1:02d}.png',(1070,325,1280,585),(x+12+j*235,y+72,x+237+j*235,y+365));d.text((x+35+j*235,y+365),str(1843+j),font=font(22,True),fill=INK)
 elif i==5:cropped(detail,P/'previews/pose_221.png',(340,130,970,560),(x+12,y+72,x+948,y+400))
d.text((25,1350),'Required new art: two registered girl quarter views preserving face, swept fringe, skull/jaw and braid origin. No rejected v008 patch reused.',font=font(21),fill=INK)
detail.save(P/'WTSC_v016_Contacts_And_Head_Limits.jpg',quality=93,subsampling=0)
sections=['Native HIP edit / planted original boots','Source-sole heel / flat / toe / lift','Actual painted palm / native thigh follow','Head pitch / original profile and braid ONLY']
videos=[]
for mode,name in [('INSPECTION','WTSC_v016_Painted_Rig_Diagnostic_4s.mp4'),('MATCHED_SHOT','WTSC_v016_Camera_Matched_Rig_Diagnostic_4s.mp4')]:
 folder=P/'previews'/('LABELED_'+mode);folder.mkdir(exist_ok=True)
 for f in range(1,97):
  im=Image.open(P/f'previews/{mode}/{f:04d}.png').convert('RGB');dr=ImageDraw.Draw(im);dr.rectangle((0,0,959,31),fill=(29,35,38));dr.text((13,5),sections[(f-1)//24],font=font(17,True),fill=(245,245,240));dr.rectangle((0,516,959,539),fill=(29,35,38));dr.text((12,518),f'v016 TECHNICAL RIG DIAGNOSTIC | art / head turn UNAPPROVED | {mode} | frame{f:03d}',font=font(14),fill=(245,245,240));im.save(folder/f'{f:04d}.png')
 out=P/name;cmd=[FF,'-v','error','-framerate','24','-i',str(folder/'%04d.png'),'-frames:v','96','-c:v','libx264','-threads','2','-preset','medium','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart','-an','-y',str(out)];subprocess.run(cmd,check=True)
 reader=imageio_ffmpeg.read_frames(str(out),pix_fmt='rgb24');meta=next(reader);count=0;decoded=[]
 for data in reader:
  count+=1
  if count in [1,13,25,37,49,61,73,85]:decoded.append((count,Image.frombytes('RGB',meta['size'],data)))
 board=Image.new('RGB',(1920,1160),BG);dr=ImageDraw.Draw(board);dr.text((20,10),name+' / decoded chronological frames',font=font(25,True),fill=INK)
 for i,(f,im) in enumerate(decoded):
  im=im.resize((480,270),Image.Resampling.LANCZOS);x=i%4*480;y=60+i//4*550;board.paste(im,(x,y));dr.text((x+12,y+280),f'Frame{f:03d} / {sections[(f-1)//24]}',font=font(15),fill=INK)
 board.save(P/f'evidence/DECODED_{mode}.jpg',quality=90)
 videos.append({'file':name,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'decoded_frames':count,'width':meta['size'][0],'height':meta['size'][1],'fps':meta['fps'],'duration_seconds':meta['duration'],'under20MB':out.stat().st_size<20_000_000,'review_method':'All frames decoded; chronological sample board inspected. No normal-speed playback claim.'})
(P/'evidence/preview_verification.json').write_text(json.dumps(videos,indent=2));print('PREVIEWS_READY',json.dumps(videos))
