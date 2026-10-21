"""Create the exact five-second v053 boy-only baseline without Blender work."""
import csv,hashlib,json,subprocess
from pathlib import Path
from PIL import Image
import imageio_ffmpeg

P=Path(__file__).resolve().parents[1];ROOT=P.parents[1]
V=P/'previews';F=V/'frames_A_v053';E=P/'evidence';F.mkdir(exist_ok=True,parents=True);E.mkdir(exist_ok=True,parents=True)
src=ROOT/'locomotion/authored_walk_beats_v053/previews/frames_V053'
native=ROOT/'locomotion/authored_walk_beats_v053/native/WTSC_Authored_Walk_Beats_v053.blend'
native_sha='23fc2578b499d6d2fded4f1d16a5466d93bea59b8bb7caa9eee26e7004a8a29b'
assert hashlib.sha256(native.read_bytes()).hexdigest()==native_sha
rows=[]
for k in range(120):
    exact=1+1.25*k;f=round(exact)
    source=src/f'FRAME_{f:04d}.png';assert source.exists()
    im=Image.open(source).convert('RGB');assert im.size==(1280,720)
    crop=im.crop((0,0,660,720))
    dest=F/f'FRAME_{k+1:04d}.png';crop.save(dest)
    rows.append({'output_frame':k+1,'output_time_s':k/24,'source_exact_frame':exact,'source_render_frame':f,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
with (E/'A_TIME_MAPPING.csv').open('w',newline='') as h:
    w=csv.DictWriter(h,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe();movie=V/'A_v053_Current_Walk_5s_24fps.mp4'
cmd=[ffmpeg,'-hide_banner','-loglevel','error','-y','-framerate','24','-start_number','1','-i',str(F/'FRAME_%04d.png'),'-frames:v','120','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)]
r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,r.stderr
assert movie.stat().st_size<20_000_000
data={'lane':'A','source_native':str(native),'source_native_sha256':native_sha,'source_render':'v053 257 native frames at30fps',
 'output_frames':120,'output_fps':24,'duration_s':5.,'crop_px':[0,0,660,720],'time_mapping':'source F=1+1.25k, nearest native rendered frame',
 'movie':str(movie),'movie_size_bytes':movie.stat().st_size,'movie_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),
 'all_output_frames_unique':len(set(x['source_render_frame'] for x in rows))==120}
(E/'A_BASELINE.json').write_text(json.dumps(data,indent=2))
print('V057_A_BASELINE',movie,movie.stat().st_size,rows[0]['source_render_frame'],rows[-1]['source_render_frame'])
