import json, subprocess, re, hashlib, zipfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
P=Path(__file__).resolve().parents[1];R=P.parents[1]
F=Path(r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe')
raw=P/'previews/motion_frames';reference=P.parent/'benchmark_v003/previews/motion_frames'
assert {int(f.stem) for f in raw.glob('*.png')}==set(range(1800,1920))
for folder in [raw,reference]:
    for f in folder.glob('*.png'):
        with Image.open(f) as im:im.load();assert im.size==(1920,1080)
def run(arguments,log):
    result=subprocess.run([str(F),'-hide_banner','-nostdin','-y',*arguments],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
    (P/'evidence'/log).write_text(result.stderr);assert result.returncode==0,result.stderr
    return result
codec=['-an','-c:v','libx264','-crf','17','-preset','fast','-threads','2','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart']
proof=P/'WTSC_Painted_Impulse_75-80s_v006.mp4';comparison=P/'WTSC_Compare_LEFT-v003_RIGHT-Painted-Impulse-v006.mp4';ignition=P/'WTSC_Ignition_24fps_LEFT-v003_RIGHT-v006.mp4'
run(['-framerate','24','-start_number','1800','-i',str(raw/'%04d.png'),'-frames:v','120',*codec,str(proof)],'encode_proof.log')
run(['-framerate','24','-start_number','1800','-i',str(reference/'%04d.png'),'-framerate','24','-start_number','1800','-i',str(raw/'%04d.png'),'-filter_complex','[0:v][1:v]hstack=inputs=2[v]','-map','[v]','-frames:v','120',*codec,str(comparison)],'encode_comparison.log')
run(['-framerate','24','-start_number','1818','-i',str(reference/'%04d.png'),'-framerate','24','-start_number','1818','-i',str(raw/'%04d.png'),'-filter_complex','[0:v]crop=800:480:1100:300[a];[1:v]crop=800:480:1100:300[b];[a][b]hstack=inputs=2[v]','-map','[v]','-frames:v','36',*codec,str(ignition)],'encode_ignition.log')
outputs=[]
for file,pixels,count in [(proof,[1920,1080],120),(comparison,[3840,1080],120),(ignition,[1600,480],36)]:
    assert file.stat().st_size<20_000_000
    result=run(['-v','error','-i',str(file),'-progress','pipe:1','-f','null','NUL'],file.stem+'_decode.log');counts=re.findall(r'^frame=(\d+)',result.stdout,re.M);assert int(counts[-1])==count
    outputs.append({'file':file.name,'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'pixels':pixels,'frames':count,'fps':24,'seconds':count/24,'full_decode':True})
audit=P/'previews/decoded_audit';audit.mkdir(exist_ok=True)
auditframes=[1808,1825,1826,1832,1848,1884,1919]
selector="select='"+'+'.join(f'eq(n,{frame-1800})' for frame in auditframes)+"'"
run(['-v','error','-i',str(proof),'-vf',selector,'-fps_mode','passthrough',str(audit/'%02d.png')],'extract_audit.log')
(P/'evidence/decoded_audit_map.json').write_text(json.dumps([{'image':f'{i+1:02d}.png','frame':frame} for i,frame in enumerate(auditframes)],indent=2))
font=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',24);small=ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf',18)
board=Image.new('RGB',(1600,650),(22,26,29));draw=ImageDraw.Draw(board)
draw.text((20,12),'LEFT: preferred v003    /    RIGHT: painted impulse v006',font=font,fill=(220,223,216))
for row,frame in enumerate([1832,1884]):
    for col,folder in enumerate([reference,raw]):board.paste(Image.open(folder/f'{frame}.png').resize((800,450),Image.Resampling.LANCZOS).crop((0,120,800,400)),(col*800,52+row*298))
    draw.text((12,52+row*298),f'Frame {frame}',font=small,fill=(238,228,204))
board.save(P/'previews/Compare_Painted_Impulse_v006.jpg',quality=94)
frames=list(range(1823,1833));strip=Image.new('RGB',(2000,500),(22,26,29));draw=ImageDraw.Draw(strip)
draw.text((12,6),'Consecutive native frames at 24 fps | v003 top, v006 bottom | identical crop',font=small,fill=(220,223,216))
for i,frame in enumerate(frames):
    for row,folder in enumerate([reference,raw]):
        crop=Image.open(folder/f'{frame}.png').crop((1240,550,1840,780)).resize((200,190),Image.Resampling.LANCZOS);strip.paste(crop,(i*200,42+row*220));draw.text((i*200+4,232+row*220),str(frame),font=small,fill=(222,225,219))
strip.save(P/'previews/Ignition_Consecutive_24fps_v006.jpg',quality=96)
fg=np.array(Image.open(P.parent/'benchmark_v002/assets/Native_Foreground_Alpha_1080_v002.png'))[:,:,3]
protected=fg>254;protected[:275]=False;protected[735:]=False;protected[:,:720]=False;protected[:,1205:]=False
base=np.array(Image.open(raw/'1800.png')).astype(int)[:,:,:3];child=[]
for frame in [1832,1848,1860,1884,1919]:
    delta=np.abs(np.array(Image.open(raw/f'{frame}.png')).astype(int)[:,:,:3]-base)
    child.append({'frame':frame,'protected_pixels':int(protected.sum()),'max_channel_delta_8bit':int(delta[protected].max()),'mean_absolute_channel_delta':float(delta[protected].mean())})
on=np.array(Image.open(raw/'1826.png')).astype(int)[:,:,:3];off=np.array(Image.open(P/'previews/no_bloom_1826.png')).astype(int)[:,:,:3];difference=np.maximum(0,on-off);changed=np.max(difference,axis=2)>0
native_alpha=np.array(Image.open(P/'sandbox/Append_Test_RGBA_1826.png').getchannel('A').resize((1920,1080),Image.Resampling.BILINEAR))
outside=(native_alpha==0)
bloom={'frame':1826,'changed_pixels':int(changed.sum()),'max_added_channel_8bit':int(difference.max()),'sum_added_channels':int(difference.sum()),'added_pixels_outside_raw_fx_alpha':int((changed&outside).sum()),'comparison':'Identical native scene/frame, only Bloom gain disabled for diagnostic. Outside-alpha support uses the matched factory Append RGBA render.'}
assert bloom['changed_pixels']>0,'Bloom ablation has no measured effect'
seq=json.loads((P/'evidence/transparent_sequence.json').read_text());seqfiles=sorted((P/seq['folder']).glob('*.png'));assert len(seqfiles)==120
amin=255;amax=0;outer=0;bounds=[]
for f in seqfiles:
    with Image.open(f) as im:im.load();assert im.mode=='RGBA' and im.size==(960,540);a=np.array(im)[:,:,3]
    amin=min(amin,int(a.min()));amax=max(amax,int(a.max()));outer=max(outer,int(a[0].max()),int(a[-1].max()),int(a[:,0].max()),int(a[:,-1].max()))
    if int(f.stem) in [1,3,9,25,72,120]:
        y,x=np.where(a>2);bounds.append({'frame':int(f.stem),'bounds':None if not len(x) else [int(x.min()),int(y.min()),int(x.max()),int(y.max())]})
assert amin==0 and amax>0 and outer==0,(amin,amax,outer)
seqcheck={'all120_decoded':True,'pixels':[960,540],'alpha_min':amin,'alpha_max':amax,'outer_edge_alpha_max':outer,'bounds':bounds,'convention':'Straight RGBA PNG, no bloom/scene mask/ground scar'}
source_hashes={
 'v003':('effects/benchmark_v003/native/WTSC_Evolving_Eruption_Collection_v003.blend','d089770cccee18b786692d76113b80fbf8514d8034bab4eaae17d6b5f9bd1868'),
 'production_v038':('shots/world/WTSC_Full_Knockout_Trailer_Editable_v038.blend','f08c0d6f004b85693b124a1c84aac10617ca7742475979e2d80ca3d6961778ed')}
unchanged={key:hashlib.sha256((R/file).read_bytes()).hexdigest()==expected for key,(file,expected) in source_hashes.items()};assert all(unchanged.values())
report={'outputs':outputs,'all120_new_proof_pngs_decoded':True,'same_camera_exposure_Standard_view_and_24fps_as_v003':True,'new_bake':False,'gas_used':False,'child_silhouette_checks':child,'bloom_ablation':bloom,'transparent_sequence':seqcheck,'source_hashes_unchanged':unchanged,'native_library_sha256':hashlib.sha256((P/'native/WTSC_Painted_Blast_Assets_v006.blend').read_bytes()).hexdigest(),'proof_native_sha256':hashlib.sha256((P/'native/WTSC_Painted_Blast_Proof_v006.blend').read_bytes()).hexdigest(),'status':'Authored refinement candidate; artistic acceptance and moving production shot integration pending.'}
(P/'evidence/media_validation.json').write_text(json.dumps(report,indent=2));print('PAINTED_REVIEW_MEDIA_VALIDATED',json.dumps(report),flush=True)
archive=P/'WTSC_Painted_Impulse_Assets_v006.zip'
included=[P/'IMPORT_GUIDE.md',P/'native/WTSC_Painted_Blast_Assets_v006.blend',P/'assets/Painted_Ground_Gouge_v006.png',P/'sandbox/WTSC_Fresh_Append_Sandbox_v006.blend',P/'sandbox/Append_Test_RGBA_1826.png']
included+=list((P/'scripts').glob('*.py'))+list((P/'evidence').glob('*.json'))+seqfiles
included+=[P/'previews/Compare_Painted_Impulse_v006.jpg',P/'previews/Ignition_Consecutive_24fps_v006.jpg',P/'previews/persistence_2064.png']
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for file in sorted(included):z.write(file,file.relative_to(P))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
(P/'evidence/package_validation.json').write_text(json.dumps({'file':archive.name,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'files':len(included),'zip_crc_passed':True,'contains_production_scene_or_background_plate':False,'contains_simulation_cache':False,'source_library_packed':True},indent=2))
print('PACKAGE_VALIDATED',archive.stat().st_size,flush=True)
