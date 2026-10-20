"""Encode the actual 65-frame normal-speed render and matched v053 A/B."""
import hashlib,json,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg

P=Path(__file__).resolve().parents[1];E=P/'evidence';V=P/'previews'
candidate=V/'frames_v056';source=P.parent/'authored_walk_beats_v053'/'previews'/'frames_V053'
assert all((candidate/f'FRAME_{i:04d}.png').exists() and (source/f'FRAME_{i:04d}.png').exists() for i in range(1,66))
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
full=V/'WTSC_Girl_Yoke_v056_FullShot_NormalSpeed.mp4'
ab=V/'WTSC_v053_vs_v056_Girl_Yoke_Matched_AB_NormalSpeed.mp4'
def run(args):
    result=subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y',*args],capture_output=True,text=True)
    if result.returncode:raise RuntimeError(result.stderr)
run(['-framerate','30','-start_number','1','-i',str(candidate/'FRAME_%04d.png'),'-frames:v','65','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(full)])
run(['-framerate','30','-start_number','1','-i',str(source/'FRAME_%04d.png'),
     '-framerate','30','-start_number','1','-i',str(candidate/'FRAME_%04d.png'),
     '-filter_complex','[0:v][1:v]hstack=inputs=2[v]','-map','[v]','-frames:v','65',
     '-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',str(ab)])
assert full.stat().st_size<20_000_000 and ab.stat().st_size<20_000_000
font=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',22)
frames=[1,4,9,13,17,20,25,29,33,49,65]
board=Image.new('RGB',(4*640,3*420),'#222b2d');d=ImageDraw.Draw(board)
for j,f in enumerate(frames):
    im=Image.open(candidate/f'FRAME_{f:04d}.png').convert('RGB').resize((640,360),Image.Resampling.LANCZOS)
    x=(j%4)*640;y=(j//4)*420;board.paste(im,(x,y+30));d.text((x+12,y+4),f'v056 | F{f:03d}',font=font,fill='#f0eadf')
boardpath=V/'WTSC_v056_NormalSpeed_Contact_Board.jpg';board.save(boardpath,quality=93)
evidence={'frames':65,'fps':30,'duration_s':65/30,'source':'frozen v053 frame-for-frame match','a_b_left':'v053','a_b_right':'v056',
 'full':str(full),'full_size_bytes':full.stat().st_size,'full_sha256':hashlib.sha256(full.read_bytes()).hexdigest(),
 'a_b':str(ab),'a_b_size_bytes':ab.stat().st_size,'a_b_sha256':hashlib.sha256(ab.read_bytes()).hexdigest(),
 'contact_board':str(boardpath),'contact_board_sha256':hashlib.sha256(boardpath.read_bytes()).hexdigest()}
(E/'ENCODED_REVIEW.json').write_text(json.dumps(evidence,indent=2))
print('V056_MOVIES',full,full.stat().st_size,ab,ab.stat().st_size)
