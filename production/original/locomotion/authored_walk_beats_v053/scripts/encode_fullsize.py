import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
P=Path(__file__).resolve().parents[1];E=P/'evidence';V=P/'previews';data=json.loads((E/'ACTUAL_MOTION_RENDER.json').read_text());records={r['frame']:r for r in data['records'] if r['version']=='V053'};assert len(records)==257
font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',25);sub=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
out=V/'WTSC_Authored_Walk_Beats_v053_Full_Size_NormalSpeed.mp4';w=imageio_ffmpeg.write_frames(str(out),(1280,800),fps=30,codec='libx264',pix_fmt_in='rgb24',pix_fmt_out='yuv420p',quality=8,macro_block_size=16,ffmpeg_log_level='error',output_params=['-threads','2','-movflags','+faststart']);w.send(None)
for f in range(1,258):
 r=records[f];path=Path(r['file']);assert hashlib.sha256(path.read_bytes()).hexdigest()==r['sha256'];im=Image.new('RGB',(1280,800),'#202a2c');d=ImageDraw.Draw(im)
 d.text((20,9),'v053 | AUTHORED ORDINARY WALK BEATS | ACTUAL NATIVE',font=font,fill='#f0eadf')
 d.text((20,45),'Contact / loading / passing / push-off | grounded v051 foot path | eight cycles',font=sub,fill='#c1c9c6');d.text((1180,45),f'F{f:03d}',font=sub,fill='#c1c9c6')
 im.paste(Image.open(path).convert('RGB'),(0,80));w.send(im.tobytes())
w.close();assert out.stat().st_size<20_000_000
reader=imageio_ffmpeg.read_frames(str(out),pix_fmt='rgb24');meta=next(reader);count=sum(1 for _ in reader)
assert count==257 and meta['size']==(1280,800) and abs(meta['fps']-30)<1e-6
report={'file_name':out.name,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'decoded_frames':count,'fps':30,'duration_seconds':count/30,'resolution':[1280,800],'under_20_MB':True,'actual_native_frames':True,'continuous_player_observed_by_agent':False}
(E/'FULLSIZE_ENCODED_VALIDATION.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
