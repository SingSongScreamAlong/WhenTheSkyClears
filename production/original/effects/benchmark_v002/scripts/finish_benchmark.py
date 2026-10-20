import json,subprocess,re,hashlib,zipfile
from pathlib import Path
from PIL import Image
import numpy as np
P=Path(__file__).resolve().parents[1]
F=Path(r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe')
folder=P/'previews/motion_frames_gpu_v002';frames=sorted(folder.glob('*.png'));assert len(frames)==96,len(frames)
for i,p in enumerate(frames):
 assert p.name==f'{1795+i:04}.png'
 with Image.open(p) as im:im.load();assert im.size==(1920,1080),(p,im.size)
out=P/'WTSC_Explosion_Motion_Proof_1080_v002a.mp4'
r=subprocess.run([str(F),'-hide_banner','-nostdin','-y','-framerate','24','-start_number','1795','-i',str(folder/'%04d.png'),'-frames:v','96','-an','-c:v','libx264','-crf','17','-preset','fast','-threads','2','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',str(out)],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
(P/'evidence/encode.log').write_text(r.stderr);assert r.returncode==0,r.stderr;assert out.stat().st_size<20_000_000
r=subprocess.run([str(F),'-v','error','-nostdin','-i',str(out),'-progress','pipe:1','-f','null','NUL'],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW);ns=re.findall(r'^frame=(\d+)',r.stdout,re.M);assert r.returncode==0 and int(ns[-1])==96
audit=P/'previews/decoded_audit_v002a';audit.mkdir(exist_ok=True)
selected=[19,22,30,50,80,95];expr="select='"+'+'.join(f'eq(n,{n})' for n in selected)+"'"
r=subprocess.run([str(F),'-v','error','-nostdin','-y','-i',str(out),'-vf',expr,'-fps_mode','passthrough',str(audit/'%02d.png')],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW);assert r.returncode==0,r.stderr
(P/'evidence/decoded_audit_map_v002a.json').write_text(json.dumps([{'file':f'{i+1:02}.png','video_frame':n,'source_frame':1795+n,'seconds':n/24} for i,n in enumerate(selected)],indent=2))
image=P/'previews/WTSC_Explosion_Benchmark_4K_v002.png';im=Image.open(image);assert im.size==(3840,2160);im.crop((2460,380,3660,1580)).save(P/'previews/WTSC_Explosion_Benchmark_4K_1to1_Detail_v002.png')
build=json.loads((P/'evidence/benchmark_build.json').read_text());unchanged=hashlib.sha256(Path(build['source']).read_bytes()).hexdigest()==build['source_sha256'];assert unchanged
motion=[]
for a,b in [(1813,1814),(1814,1817),(1817,1825),(1825,1840),(1840,1870)]:
 aa=np.array(Image.open(folder/f'{a:04}.png').convert('RGB'),dtype=np.int16);bb=np.array(Image.open(folder/f'{b:04}.png').convert('RGB'),dtype=np.int16);motion.append({'frames':[a,b],'whole_shot_mean_abs_difference':float(np.abs(aa-bb).mean()),'fx_region_mean_abs_difference':float(np.abs(aa[180:760,1220:1800]-bb[180:760,1220:1800]).mean())})
report={'still_pixels':[3840,2160],'clip_pixels':[1920,1080],'fps':24,'clip_frames':96,'clip_seconds':4,'clip_bytes':out.stat().st_size,'renderer':'Eevee32samples, one bounded GPU process with2CPUthreads; compositorGPU','full_mp4_decode':True,'all96_pngs_decoded':True,'source_unchanged':unchanged,'frame_differences':motion,'artistic_status':'Unaccepted benchmark. Technical checks and detailed still are not artistic acceptance. Actual motion and stylistic fit require review.','limitations':['Held actual project camera/characters/scene context, not locomotion or full moving trailer integration','2.5D original paint with native surface flow and3D debris; no volumetric smoke simulation','Motion proof uses held native occlusion/receiver maps; they must be re-evaluated for moving camera','Hero image1254px square and dust2172x724, inspected in a4K shot; no DLSS/upscaling claim']}
(P/'evidence/media_validation.json').write_text(json.dumps(report,indent=2))
print('FX_BENCHMARK_MEDIA_COMPLETE',json.dumps({'video':str(out),'bytes':out.stat().st_size,'pixels':[1920,1080],'frames':96,'seconds':4,'source_unchanged':unchanged}),flush=True)
