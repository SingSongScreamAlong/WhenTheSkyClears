"""Label actual renders, encode normal-speed review and verify every decoded frame."""
import json,hashlib,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
P=Path(__file__).resolve().parents[1];V=P/'previews';E=P/'evidence';raw=V/'frames';fps=30
fontfile=Path('C:/Windows/Fonts/segoeui.ttf');fontbold=Path('C:/Windows/Fonts/segoeuib.ttf')
def font(n,bold=False):return ImageFont.truetype(str(fontbold if bold else fontfile),n)
record=json.loads((E/'MOTION_RENDER.json').read_text());native=P/'native/WTSC_Age10_Painted_Outfit_Restoration_v046.blend';assert record['native_sha256']==hashlib.sha256(native.read_bytes()).hexdigest()
out=V/'WTSC_Age10_Painted_Outfits_v046_NormalSpeed.mp4';writer=imageio_ffmpeg.write_frames(str(out),(1280,800),fps=fps,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',quality=8,macro_block_size=16,ffmpeg_log_level='error',output_params=['-movflags','+faststart','-threads','2']);writer.send(None)
for section in range(2):
 for f in range(1,95):
  im=Image.open(raw/('FRAME_%04d.png'%f)).convert('RGB');frame=Image.new('RGB',(1280,800),'#202a2c');d=ImageDraw.Draw(frame)
  if not section:
   title='AGE TEN | ORIGINAL PAINTED OUTFITS ON CORRECTED BONES';sub='30 fps native walk | 3 repeats of the 31-frame cycle | separate development proof';content=im
  else:
   title='CONTACT DETAIL | SAME NATIVE FRAMES AT NORMAL SPEED';sub='2x crop for feet and garment overlap | technical proof is separate from artistic approval';content=im.crop((300,360,940,720)).resize((1280,720),Image.Resampling.LANCZOS)
  d.text((25,9),title,font=font(25,True),fill='#f0eadf');d.text((25,43),sub,font=font(18),fill='#c1c9c6');d.text((1170,46),'F%03d'%f,font=font(17),fill='#c1c9c6');frame.paste(content,(0,80));writer.send(frame.tobytes())
writer.close();assert out.stat().st_size<20_000_000
# Independent ffmpeg decode: actually consume all encoded frames.
reader=imageio_ffmpeg.read_frames(str(out),pix_fmt='rgb24');metadata=next(reader);count=0;selected={}
for idx,data in enumerate(reader):
 count+=1
 if idx in [0,8,16,24,31,62,93,94,110,140,171,187]:selected[idx]=Image.frombytes('RGB',(1280,800),data)
assert count==188,count
assert metadata['size']==(1280,800),metadata
assert abs(metadata['fps']-30)<1e-6
sheet=Image.new('RGB',(1920,1696),'#202a2c');d=ImageDraw.Draw(sheet)
for i,(idx,im) in enumerate(selected.items()):
 x=(i%3)*640;y=(i//3)*424;sheet.paste(im.resize((640,400),Image.Resampling.LANCZOS),(x,y));d.text((x+8,y+402),'Encoded frame %03d / native F%03d'%(idx+1,idx%94+1),font=font(14),fill='#f0eadf')
sheet.save(V/'ENCODED_MOTION_CONTACT_SHEET_v046.jpg',quality=94)
# Actual matching native rigs, clothing, overlay and second pose. No fabricated bones.
panels=[('RESTORED_DRESSED_F1.png','A | Restored painting on age-ten bodies, native F1'),('ACTUAL_CORRECTED_BONES_F1.png','B | Actual evaluated armature bones, same camera and frame'),('RESTORED_WITH_ACTUAL_BONES_F1.png','C | Actual bones over clothing, same camera and frame'),('RESTORED_DRESSED_F17.png','D | Opposite stride, native F17; preserved contact timing')]
board=Image.new('RGB',(2560,1600),'#202a2c');d=ImageDraw.Draw(board)
for i,(name,title) in enumerate(panels):
 x=(i%2)*1280;y=(i//2)*800;d.text((x+22,y+14),title,font=font(27,True),fill='#f0eadf');d.text((x+22,y+49),'Original painting retained | boy 1.390 m / girl 1.380 m barefoot skull stature',font=font(19),fill='#c1c9c6');board.paste(Image.open(V/name).convert('RGB'),(x,y+80))
board.save(V/'WTSC_Painted_Outfits_Actual_Bones_v046.png')
(E/'ENCODED_REVIEW_VALIDATION.json').write_text(json.dumps({'file':str(out),'file_size_bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'native_sha256':record['native_sha256'],'source_timeline_frames':94,'encoded_frames':count,'fps':metadata['fps'],'duration_seconds':count/fps,'resolution':list(metadata['size']),'sections':['Full pair, 94 source timeline frames, 30fps','Same 94 native frames in a 2x crop, 30fps'],'decoded_all_frames':True,'review_method':'Native still review, encoded-frame sheet review, and independent full video decode. Continuous playback has not been observed by the agent.','file_under_20_MB':True},indent=2));print(json.dumps({'movie':str(out),'bytes':out.stat().st_size,'decoded_frames':count,'duration':count/fps}))
