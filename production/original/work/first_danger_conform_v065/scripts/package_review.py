"""Encode only the completed native UHD sequence; decode and inspect its real output."""
import json,hashlib,subprocess,re,math,array,sys
from pathlib import Path
import imageio_ffmpeg
import numpy as np
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[3];O=R/'work/first_danger_conform_v065';P=O/'previews';F=imageio_ffmpeg.get_ffmpeg_exe();S=O/'renders/sequence4K';FG='--foreground' in sys.argv;V='v065f' if FG else 'v065';C=O/('renders/final_composite4K_F' if FG else 'renders/final_composite4K')
record=json.loads((O/('evidence/FINAL_COMPOSITE_F_COMPLETE.json' if FG else 'evidence/FINAL_COMPOSITE_COMPLETE.json')).read_text())
assert record['frames']==168 and record['resolution']==[3840,2160] and record['native_unchanged']
assert all((S/folder/f'{g:04d}.png').exists() for folder in ['final','world','inherited','matte','glyph'] for g in range(913,1081))
assert all((C/f'{g:04d}.png').exists() for g in range(913,1081))
MUSIC=R/'edit/When_The_Sky_Clears_Trailer_Music_100s.wav'
def run(args):
 p=subprocess.run([F,'-hide_banner','-nostdin',*args],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
 if p.returncode:raise RuntimeError(p.stderr[-5000:])
 return p
def decode(path,expected):
 p=run(['-v','error','-i',str(path),'-map','0:v:0','-progress','pipe:1','-f','null','NUL'])
 counts=re.findall(r'^frame=(\d+)',p.stdout,re.M);assert counts and int(counts[-1])==expected,(path,counts[-1:])
 return {'frames':int(counts[-1]),'all_frames_decoded':True}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
clips=[]
for folder,name in [('final',f'WTSC_First_Danger_Title_{V}_4K.mp4'),('world','WTSC_First_Danger_Unmasked_v065_4K.mp4')]:
 out=P/name
 reuse=FG and folder=='world' and out.exists()
 assert not out.exists() or reuse,'Do not silently replace a delivered movie'
 input_dir=C if folder=='final' else S/folder
 if not reuse:run(['-v','error','-framerate','24','-start_number','913','-i',str(input_dir/'%04d.png'),'-ss','38','-i',str(MUSIC),'-map','0:v:0','-map','1:a:0','-frames:v','168','-t','7','-vf','scale=out_color_matrix=bt709:out_range=tv,format=yuv420p','-c:v','libx264','-preset','fast','-crf','18','-threads','4','-pix_fmt','yuv420p','-r','24','-fps_mode','cfr','-video_track_timescale','24000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-c:a','aac','-b:a','192k','-movflags','+faststart',str(out)])
 clips.append({'path':str(out),'resolution':[3840,2160],'fps':24,'seconds':7,'bytes':out.stat().st_size,'sha256':sha(out),**decode(out,168)})
 print('V065_PACKAGED',name,flush=True)

# Viewing copy keeps both native results side by side with clear labels.
compare=O/('renders/comparison1080_F' if FG else 'renders/comparison1080');compare.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25)
for g in range(913,1081):
 canvas=Image.new('RGB',(1920,600),'#10161e');draw=ImageDraw.Draw(canvas)
 canvas.paste(Image.open(S/'world'/f'{g:04d}.png').convert('RGB').resize((960,540),Image.Resampling.LANCZOS),(0,60))
 canvas.paste(Image.open(C/f'{g:04d}.png').convert('RGB').resize((960,540),Image.Resampling.LANCZOS),(960,60))
 sec=(g-1)/24
 draw.text((20,16),f'v065 | layered world | global {sec:05.2f}s',font=font,fill='white')
 draw.text((980,16),'v065 | title with readable children',font=font,fill='white')
 canvas.save(compare/f'{g:04d}.png')
out=P/f'WTSC_First_Danger_World_and_Title_{V}_Review.mp4'
run(['-v','error','-framerate','24','-start_number','913','-i',str(compare/'%04d.png'),'-ss','38','-i',str(MUSIC),'-frames:v','168','-t','7','-vf','scale=out_color_matrix=bt709:out_range=tv,format=yuv420p','-c:v','libx264','-preset','fast','-crf','20','-threads','4','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)])
clips.append({'path':str(out),'resolution':[1920,600],'fps':24,'seconds':7,'bytes':out.stat().st_size,'sha256':sha(out),**decode(out,168)})
view=P/f'WTSC_First_Danger_Title_{V}_View.mp4'
run(['-v','error','-i',str(P/f'WTSC_First_Danger_Title_{V}_4K.mp4'),'-vf','scale=1280:720:flags=lanczos','-c:v','libx264','-preset','fast','-crf','21','-threads','4','-c:a','aac','-b:a','128k','-movflags','+faststart',str(view)])
clips.append({'path':str(view),'resolution':[1280,720],'fps':24,'seconds':7,'bytes':view.stat().st_size,'sha256':sha(view),**decode(view,168)})

coverage=[]
for g in range(913,1081):
 matte=np.asarray(Image.open(S/'matte'/f'{g:04d}.png').convert('RGB'))[:,:,0]/255.
 glyph=np.asarray(Image.open(S/'glyph'/f'{g:04d}.png').convert('RGB'))[:,:,0]/255.
 mask=matte>.995
 if FG:
  tree=np.asarray(Image.open(O/f'renders/foreground_alpha4K/{g:04d}.png').convert('RGB'))[:,:,0]
  mask=mask&(tree==0)
 world=np.asarray(Image.open(S/'world'/f'{g:04d}.png').convert('RGB')).astype(np.int16)
 final=np.asarray(Image.open(C/f'{g:04d}.png').convert('RGB')).astype(np.int16)
 old=np.asarray(Image.open(S/'inherited'/f'{g:04d}.png').convert('RGB')).astype(np.int16)
 assert np.count_nonzero(mask)>1000,(g,int(np.count_nonzero(mask)))
 after=np.abs(final-world)[mask];before=np.abs(old-world)[mask]
 coverage.append({'frame':g,'opaque_visible_actor_pixels':int(mask.sum()),'old_title_mask_retains_fraction':float((glyph[mask]>.995).mean()),'new_title_actor_mean_rgb_error_to_world':float(after.mean()),'new_title_actor_max_rgb_error':int(after.max()),'old_title_actor_mean_rgb_error_to_world':float(before.mean())})
assert max(r['new_title_actor_max_rgb_error'] for r in coverage)<=1

# Chronological actual UHD keys, plus an inherited-mask/current-mask comparison.
def sheet(name,entries,columns=2):
 cw,ch=960,582;canvas=Image.new('RGB',(columns*cw,math.ceil(len(entries)/columns)*ch),'#111923');draw=ImageDraw.Draw(canvas)
 for i,(label,path) in enumerate(entries):
  x,y=(i%columns)*cw,(i//columns)*ch
  canvas.paste(Image.open(path).convert('RGB').resize((960,540),Image.Resampling.LANCZOS),(x,y+42));draw.text((x+12,y+8),label,font=font,fill='white')
 canvas.save(P/name,quality=94)
sheet('First_Danger_v065_Rendered_Keys.jpg',[(f'v065 actual UHD | G{g} | {(g-1)/24:.2f}s',C/f'{g:04d}.png') for g in [913,937,957,981,1033,1056,1057,1080]])
sheet('Title_Visibility_Before_After_v065.jpg',[(f'{label} | G{g}',(C if folder=='final' else S/folder)/f'{g:04d}.png') for g in [937,981,1056] for label,folder in [('Inherited letter mask','inherited'),('v065 readable foreground drawings','final')]])
Image.open(C/'0981.png').save(P/'First_Danger_v065_0981_4K.png')

# Check real encoded timestamps and soundtrack against the exact original excerpt.
log=run(['-i',str(view),'-vf','showinfo','-an','-f','null','NUL']).stderr
pts=[float(x) for x in re.findall(r' n:\s*\d+ pts:\s*\d+ pts_time:([\d.]+)',log)]
assert len(pts)==168 and max(abs(x-i/24) for i,x in enumerate(pts))<.00002
def pcm(args):
 q=subprocess.run([F,'-v','error',*args,'-ac','1','-ar','48000','-f','f32le','pipe:1'],capture_output=True,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 return np.frombuffer(q.stdout,dtype='<f4')
a=pcm(['-i',str(view),'-map','0:a:0','-t','7']);b=pcm(['-ss','38','-i',str(MUSIC),'-t','7']);n=min(len(a),len(b));corr=float(np.corrcoef(a[:n],b[:n])[0,1]);assert corr>.98,corr
assert sha(Path(record['native']))==record['native_sha256']
report={'native':record['native'],'native_sha256':record['native_sha256'],'world_render_native':record['world_render_native'],'world_render_native_sha256':record['world_render_native_sha256'],'render_method':record['method'],'foreground_occlusion':FG,'global_range':[913,1080],'seconds':[38,45],'frames':168,'fps':24,'clips':clips,'all_movies_fully_decoded':True,'video_timestamps_contiguous':True,'audio':{'source':str(MUSIC),'source_excerpt_seconds':[38,45],'correlation_to_original':corr,'mixing_scope':'Original supplied music only; no new SFX'},'title_visibility':{'method':'Native drawing matte minus exact foreground-oak rendered alpha reveals original painted pixels. The girl naturally passes behind the near tree at the outgoing end.','minimum_original_mask_actor_fraction':min(x['old_title_mask_retains_fraction'] for x in coverage),'maximum_revealed_opaque_actor_rgb_error':max(x['new_title_actor_max_rgb_error'] for x in coverage),'every_rendered_frame_checked':True,'rows':coverage},'scope':'Actual 7-second UHD first-danger pass with one-second neighboring handles. New full camera route provided; unchanged old downstream movies are not a conform.','artistic_acceptance':False}
(O/'evidence/DELIVERY.json').write_text(json.dumps(report,indent=2));print('V065_DELIVERY_ENCODE_AND_READBACK_COMPLETE',flush=True)
