import subprocess,json,hashlib
from pathlib import Path
import imageio_ffmpeg
P=Path(__file__).resolve().parents[1];V9=P.parent/'recovery_walk_refinement_v009';ff=imageio_ffmpeg.get_ffmpeg_exe();outputs=[]
specs=[('matched',1,168,'WTSC_v010_Matched_5s_Polish_PLUS_Separate_2s_Continuation.mp4'),('matched',1,120,'WTSC_v010_Matched_Original_5s_Polish.mp4'),('matched',121,48,'WTSC_v010_Matched_Separate_80_82s_Continuation.mp4'),('neutral',1,168,'WTSC_v010_Neutral_Polish_Continuation_7s.mp4')]
for mode,start,count,name in specs:
 assert all((P/f'previews/{mode}/{f:04d}.png').is_file() for f in range(start,start+count))
 output=P/name;subprocess.run([ff,'-y','-v','error','-framerate','24','-start_number',str(start),'-i',str(P/f'previews/{mode}/%04d.png'),'-frames:v',str(count),'-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(output)],check=True,capture_output=True);outputs.append((output,count))
out=P/'WTSC_v009_vs_v010_Original_5s_Comparison.mp4'
subprocess.run([ff,'-y','-v','error','-i',str(V9/'WTSC_v009_Matched_Recovery_Walk_75_80.mp4'),'-i',str(P/'WTSC_v010_Matched_Original_5s_Polish.mp4'),'-filter_complex','[0:v]setsar=1[a];[1:v]setsar=1[b];[a][b]hstack=inputs=2[v]','-map','[v]','-c:v','libx264','-crf','19','-preset','medium','-pix_fmt','yuv420p','-an','-frames:v','120','-movflags','+faststart',str(out)],check=True,capture_output=True);outputs.append((out,120))
rows=[]
for p,count in outputs:
 reader=imageio_ffmpeg.read_frames(str(p),pix_fmt='rgb24');metadata=next(reader);actual=sum(1 for _ in reader);assert actual==count and metadata['fps']==24 and p.stat().st_size<20_000_000
 rows.append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'decoded_frames':actual,'fps':metadata['fps'],'seconds':metadata['duration'],'size':metadata['size'],'audio':'Silent review only; no production music edits.'})
(P/'evidence/media_verification.json').write_text(json.dumps(rows,indent=2));(P/'evidence/rendered_frame_hashes.json').write_text(json.dumps({mode:{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((P/f'previews/{mode}').glob('*.png'))} for mode in ['matched','neutral']},indent=2));print(json.dumps(rows,indent=2))
