import json,subprocess,re,hashlib,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
P=Path(__file__).resolve().parents[1];R=P.parents[1]
F=Path(r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe')
folder=P/'previews/motion_frames';files=sorted(folder.glob('*.png'));assert {int(f.stem) for f in files}==set(range(1818,1914))
for f in files:
    with Image.open(f) as im:im.load();assert im.size==(1920,1080)
def run(args,name):
    r=subprocess.run([str(F),'-hide_banner','-nostdin','-y',*args],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW);(P/'evidence'/name).write_text(r.stderr);assert r.returncode==0,r.stderr;return r
video=P/'WTSC_Single_Drawn_Blast_v007b_MUTED.mp4'
run(['-framerate','24','-start_number','1818','-i',str(folder/'%04d.png'),'-frames:v','96','-an','-c:v','libx264','-preset','fast','-crf','17','-threads','2','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],'encode_review.log')
r=run(['-v','error','-i',str(video),'-progress','pipe:1','-f','null','NUL'],'decode_review.log');assert int(re.findall(r'^frame=(\d+)',r.stdout,re.M)[-1])==96;assert video.stat().st_size<20_000_000
font=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',19);small=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',16)
build=json.loads((P/'evidence/build_single_pose.json').read_text());poses=[row for row in build['poses'] if row['kind']=='Blast']
strip=Image.new('RGB',(1440,1636),(23,27,29));draw=ImageDraw.Draw(strip);draw.text((15,10),'ONE BLAST / actual native pose keys /24fps / no cel scale animation',font=font,fill=(224,220,204))
for i,row in enumerate(poses):
    x=(i%3)*480;y=52+(i//3)*396;im=Image.open(P/f'previews/final_pose_{i+1:02d}.png').crop((1160,180,1920,755)).resize((480,363),Image.Resampling.LANCZOS);strip.paste(im,(x,y+27));draw.text((x+8,y+4),f'Drawing{i+1:02d} | age{row["key_age"]:g}f',font=small,fill=(224,220,204))
strip.save(P/'WTSC_Drawn_Pose_Strip_v007b.jpg',quality=94)
times=[1824,1825,1826,1827,1829,1834,1844,1846,1848,1850,1854,1913]
board=Image.new('RGB',(1440,1332),(23,27,29));draw=ImageDraw.Draw(board);draw.text((14,10),'Actual24fps impulse, landings and settled consequence / silent source frames',font=font,fill=(224,220,204))
for i,frame in enumerate(times):
    x=(i%3)*480;y=48+(i//3)*320;im=Image.open(folder/f'{frame}.png').crop((1120,330,1920,810)).resize((480,288),Image.Resampling.LANCZOS);board.paste(im,(x,y+27));draw.text((x+8,y+4),f'frame{frame} | age{frame-1824}f',font=small,fill=(224,220,204))
board.save(P/'WTSC_Impact_and_Landings_v007b.jpg',quality=95)
audit=P/'previews/decoded_audit';audit.mkdir(exist_ok=True)
frames=[1825,1827,1834,1846,1848,1850,1868,1913];selector="select='"+'+'.join(f'eq(n,{f-1818})' for f in frames)+"'"
run(['-i',str(video),'-vf',selector,'-fps_mode','passthrough',str(audit/'%02d.png')],'extract_decode_audit.log')
protected=np.array(Image.open(P.parent/'benchmark_v002/assets/Native_Foreground_Alpha_1080_v002.png'))[:,:,3]>254;protected[:275]=False;protected[735:]=False;protected[:,:720]=False;protected[:,1205:]=False
base=np.array(Image.open(folder/'1818.png')).astype(int);child=[]
for frame in [1825,1827,1834,1848,1913]:
    delta=np.abs(np.array(Image.open(folder/f'{frame}.png')).astype(int)-base);child.append({'frame':frame,'opaque_child_pixels':int(protected.sum()),'max_channel_delta':int(delta[protected].max())})
sources=[('v006_native',P.parent/'blast_refinement_v006/native/WTSC_Painted_Blast_Proof_v006.blend','c6501238e0d1dd9769bc6b607401d604b02ce5d108192f9f4326b9dc109beedb'),('v003_assets',P.parent/'benchmark_v003/native/WTSC_Evolving_Eruption_Collection_v003.blend','d089770cccee18b786692d76113b80fbf8514d8034bab4eaae17d6b5f9bd1868'),('production_v038',R/'shots/world/WTSC_Full_Knockout_Trailer_Editable_v038.blend','f08c0d6f004b85693b124a1c84aac10617ca7742475979e2d80ca3d6961778ed')]
unchanged={name:hashlib.sha256(path.read_bytes()).hexdigest()==expected for name,path,expected in sources};assert all(unchanged.values()),unchanged
native=P/'native/WTSC_Single_Drawn_Blast_Assets_v007b.blend'
report={'video':{'file':video.name,'bytes':video.stat().st_size,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'fps':24,'pixels':[1920,1080],'frames':96,'seconds':4,'audio':False,'full_decode_passed':True,'all96_actual_pngs_decoded':True},'pose_strip':{'file':'WTSC_Drawn_Pose_Strip_v007b.jpg','actual_native_keys':12,'not_just_raw_generated_atlas':True},'impact_strip':{'file':'WTSC_Impact_and_Landings_v007b.jpg','actual_frames':times},'decoded_audit_frames':frames,'opaque_child_mask':child,'protected_sources_unchanged':unchanged,'native_asset':{'file':native.name,'bytes':native.stat().st_size,'sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'new_packed_art_atlases':2,'cel_scale_rotation_position_animation':False},'no_audio_camera_shake_variants_or_tracers':True,'review_status':'Review candidate; distinct shapes are visible but impact/rolling weight and drawing continuity require honest visual evaluation, not build-only acceptance.'}
(P/'evidence/media_validation.json').write_text(json.dumps(report,indent=2));print('SINGLE_PROOF_VALIDATED',json.dumps(report),flush=True)
included=[native,P/'assets/Blast_Drawn_Poses_v007.png',P/'assets/Dust_Drawn_Poses_v007.png',P/'REVIEW_AND_IMPORT.txt']+list((P/'scripts').glob('*.py'))+list((P/'evidence').glob('*.json'))+list((P/'evidence').glob('*prompt.txt'))
archive=P/'WTSC_Single_Blast_Review_Source_v007b.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for f in included:z.write(f,f.relative_to(P))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
(P/'evidence/package_validation.json').write_text(json.dumps({'file':archive.name,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':len(included),'crc_passed':True,'background_or_production_scene_included':False,'simulation_cache':False},indent=2));print('SINGLE_SOURCE_PACKAGE_VALIDATED',archive.stat().st_size)
