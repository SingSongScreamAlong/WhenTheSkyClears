from pathlib import Path
import subprocess,json,hashlib,re
from PIL import Image
O=Path(__file__).parent;F=O/'frames';FF=Path(r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe')
render_report=O/'ENVIRONMENT_RENDER_VERIFICATION.json'
q=json.loads(render_report.read_text()) if render_report.exists() else {'frame_count':len(list(F.glob('Environment_Continuity_*.png')))}
assert q['frame_count']==49
assert all((F/f'Environment_Continuity_{f:04d}.png').exists() for f in range(1201,1250))
out=O/'WTSC_v057_ENVIRONMENT_Continuity_24fps_1201-1249.mp4';assert not out.exists()
font=r"C\:/Windows/Fonts/segoeui.ttf"
vf="pad=iw:ih+80:0:0:color=0x192124,drawtext=fontfile='"+font+"':text='ENVIRONMENT CONTINUITY REVIEW  |  v057  |  Original 24 fps':fontsize=23:fontcolor=white:x=18:y=734,drawtext=fontfile='"+font+"':text='Source frames 1201-1249  |  Existing character animation unchanged  |  2.04 s':fontsize=20:fontcolor=0xc1cec5:x=18:y=766,scale=iw:ih:out_color_matrix=bt709:out_range=tv"
args=[str(FF),'-hide_banner','-loglevel','warning','-threads','2','-framerate','24','-start_number','1201','-i',str(F/'Environment_Continuity_%04d.png'),'-vf',vf,'-frames:v','49','-an','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-threads','2','-filter_threads','1','-movflags','+faststart','-fps_mode','passthrough',str(out)]
r=subprocess.run(args,capture_output=True,text=True);(O/'ENCODE_LOG.txt').write_text(r.stderr)
if r.returncode:raise RuntimeError(r.stderr)
decode=subprocess.run([str(FF),'-hide_banner','-loglevel','error','-threads','2','-i',str(out),'-map','0:v:0','-f','framemd5','-'],capture_output=True,text=True,check=True)
(O/'DECODED_FRAME_HASHES.txt').write_text(decode.stdout)
tb=re.search(r'#tb 0:\s*(\d+)/(\d+)',decode.stdout);assert tb and tuple(map(int,tb.groups()))==(1,24)
data=[x for x in decode.stdout.splitlines() if x and not x.startswith('#')];assert len(data)==49,len(data)
parsed=[[z.strip() for z in x.split(',')] for x in data];assert [int(x[2]) for x in parsed]==list(range(49));assert all(int(x[3])==1 for x in parsed)
assert len(set(x[-1] for x in parsed))==49
poster=O/'ENVIRONMENT_REVIEW_POSTER.png'
subprocess.run([str(FF),'-hide_banner','-loglevel','error','-threads','2','-i',str(out),'-vf','select=eq(n\\,24)','-frames:v','1','-update','1',str(poster)],capture_output=True,text=True,check=True)
im=Image.open(poster);assert im.size==(1280,800)
result={'status':'ENCODED AND DECODE-VERIFIED','path':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'video_dimensions':[1280,800],'picture_dimensions':[1280,720],'label_position':'80pixel review bar below original picture; no visual content covered.','codec':'H.264','pixel_format':'yuv420p','fps':24,'decoded_timebase':[1,24],'decoded_frame_count':49,'decoded_pts_sequence':list(range(49)),'decoded_frame_duration_ticks':1,'distinct_decoded_frames':49,'duration_seconds':49/24,'source_frame_interval':[1201,1249],'audio':False,'new_character_motion_authored':False,'source_native_modified':False,'poster':str(poster)}
(O/'ENVIRONMENT_VIDEO_VERIFICATION.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
