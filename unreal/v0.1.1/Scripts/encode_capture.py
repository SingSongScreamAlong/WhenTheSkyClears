"""Encode genuine viewport samples with their measured wall-clock durations.

No invented intermediate frames, fixed-step playback or duplicate-frame smoothing.
Uses the FFmpeg executable already present with imageio_ffmpeg.
"""
from pathlib import Path
import argparse, csv, hashlib, json, subprocess
from PIL import Image
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('--capture-root', type=Path, required=True)
args = ap.parse_args()
src = args.capture_root.resolve()
receipt = json.loads((src/'GameplayReplay.json').read_text(encoding='utf-8-sig'))
frames = receipt['capture_frames']
assert len(frames) == receipt['recorded_frames'] and len(frames) > 100
assert all(b['engine_frame'] > a['engine_frame'] and b['wall_seconds'] > a['wall_seconds'] for a,b in zip(frames,frames[1:]))
outdir = ROOT/'Evidence'
concat = outdir/'ActualCapture.ffconcat'
lines = ['ffconcat version 1.0']
inventory = []
for i, f in enumerate(frames):
    p = src/'Frames'/f"Frame{f['index']:05d}.jpg"
    with Image.open(p) as im:
        assert im.format == 'JPEG' and im.size == (f['width'], f['height'])
        im.verify()
    duration = frames[i+1]['wall_seconds']-f['wall_seconds'] if i+1<len(frames) else 1/30
    lines += ["file '" + p.as_posix().replace("'", "'\\''") + "'", 'option framerate 1000', f'duration {duration:.9f}']
    inventory.append({**f,'duration':duration,'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
concat.write_text('\n'.join(lines)+'\n',encoding='utf8')
with (outdir/'ActualCaptureFrames.csv').open('w',newline='',encoding='utf8') as fp:
    w=csv.DictWriter(fp,fieldnames=list(inventory[0]));w.writeheader();w.writerows(inventory)
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
movie=outdir/'WTSC_v0_1_1_Actual_Gameplay.mp4'
cmd=[ffmpeg,'-hide_banner','-y','-f','concat','-safe','0','-i',str(concat),'-fps_mode','vfr','-enc_time_base','1:1000','-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',str(movie)]
run=subprocess.run(cmd,capture_output=True,text=True)
(outdir/'ActualVideoEncode.log').write_text(run.stdout+'\n'+run.stderr,encoding='utf8')
assert run.returncode==0,run.stderr[-2000:]
decoded_count,decoded_seconds=imageio_ffmpeg.count_frames_and_secs(str(movie))
assert decoded_count==len(frames),(decoded_count,len(frames))
with (outdir/'ActualVideoDecode.log').open('w',encoding='utf8') as log:
    decoded=subprocess.run([ffmpeg,'-hide_banner','-i',str(movie),'-f','null','-'],stdout=log,stderr=log)
assert decoded.returncode==0
result={'movie':str(movie),'bytes':movie.stat().st_size,'sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'width':frames[0]['width'],'height':frames[0]['height'],'source_jpeg_count':len(frames),'decoded_video_frames':decoded_count,'decoded_seconds':decoded_seconds,'actual_capture_fps':receipt['actual_capture_fps'],'actual_runtime_fps_including_capture':receipt['actual_runtime_fps_including_capture'],'timing':'Variable-rate playback from real wall-clock frame timestamps, no generated or duplicate smoothing frames','is_24fps_or_better':receipt['actual_capture_fps']>=24,'full_decode_passed':True,'source_inventory':'ActualCaptureFrames.csv','engine_replay_passed':receipt['passed'],'engine_regression_events':len(receipt['events'])}
(outdir/'ActualVideoReceipt.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,indent=2))
