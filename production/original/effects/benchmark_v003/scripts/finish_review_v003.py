import json,subprocess,re,hashlib
from pathlib import Path
from PIL import Image
import numpy as np
P=Path(__file__).resolve().parents[1]
F=Path(r'WTSC_LOCAL_USER\AppData\Local\Programs\Python\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe')
new=P/'previews/motion_frames';old=P.parent/'benchmark_v002/previews/motion_frames_gpu_v002'
for folder,count,first in [(new,120,1800),(old,96,1795)]:
    files=sorted(folder.glob('*.png'));assert len(files)==count,(folder,len(files))
    for i,file in enumerate(files):
        assert file.name==f'{first+i:04}.png'
        with Image.open(file) as im:im.load();assert im.size==(1920,1080)
def run(args,log):
    r=subprocess.run([str(F),'-hide_banner','-nostdin','-y',*args],capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
    (P/'evidence'/log).write_text(r.stderr);assert r.returncode==0,r.stderr
    return r
common=['-an','-c:v','libx264','-crf','17','-preset','fast','-threads','2','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart']
view=P/'WTSC_Evolving_Eruption_75-80s_v003.mp4'
compare=P/'WTSC_Compare_LEFT-v002a_RIGHT-v003_matched-ages.mp4'
run(['-framerate','24','-start_number','1800','-i',str(new/'%04d.png'),'-frames:v','120',*common,str(view)],'encode_v003.log')
# Legacy source1795..1890 has event ages-18..77. New1806..1901 has
# exactly those same ages after moving ignition1813 to1824. No padded,
# frozen or synthesized reference frames and no extra GPU render are used.
run(['-framerate','24','-start_number','1795','-i',str(old/'%04d.png'),'-framerate','24','-start_number','1806','-i',str(new/'%04d.png'),'-filter_complex','[0:v][1:v]hstack=inputs=2[v]','-map','[v]','-frames:v','96',*common,str(compare)],'encode_comparison_v003.log')
outputs=[]
for output,pixels,expected in [(view,[1920,1080],120),(compare,[3840,1080],96)]:
    assert output.stat().st_size<20_000_000
    r=run(['-v','error','-i',str(output),'-progress','pipe:1','-f','null','NUL'],output.stem+'_decode.log')
    count=re.findall(r'^frame=(\d+)',r.stdout,re.M);assert count and int(count[-1])==expected,count
    outputs.append({'path':output.name,'bytes':output.stat().st_size,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'frames':expected,'fps':24,'seconds':expected/24,'pixels':pixels,'full_decode_passed':True})
audit=P/'previews/decoded_audit';audit.mkdir(exist_ok=True)
frames=[1825,1830,1838,1842,1850,1860,1872,1890,1904,1919]
expression="select='"+'+'.join(f'eq(n,{frame-1800})' for frame in frames)+"'"
run(['-v','error','-i',str(view),'-vf',expression,'-fps_mode','passthrough',str(audit/'%02d.png')],'extract_decoded_audit.log')
(P/'evidence/decoded_audit_map.json').write_text(json.dumps([{'image':f'{i+1:02}.png','source_frame':frame,'age':frame-1824,'seconds_in_clip':(frame-1800)/24} for i,frame in enumerate(frames)],indent=2))
# Unscaled pair at late age66 is evidence of the exact matching framing.
run(['-i',str(old/'1879.png'),'-i',str(new/'1890.png'),'-filter_complex','[0:v][1:v]hstack=inputs=2[v]','-map','[v]','-frames:v','1',str(P/'previews/Compare_LEFT-v002a_RIGHT-v003_frame1890.png')],'comparison_still.log')
production=json.loads((P.parent/'benchmark_v002/evidence/benchmark_build.json').read_text())
unchanged=hashlib.sha256(Path(production['source']).read_bytes()).hexdigest()==production['source_sha256'];assert unchanged
report={'outputs':outputs,'all216_source_frames_decoded':True,'same_framing':True,'comparison_alignment':{'legacy_actual_frames':[1795,1890],'new_actual_frames':[1806,1901],'common_event_ages':[-18,77],'method':'Existing96 legacy PNGs reused without freezing or interpolation; compared with corresponding new age. No extra legacy render performed.'},'new_ignition':1824,'held_scene_source_frame':1825,'production_source_unchanged':unchanged,'artistic_status':'Evaluate actual decoded motion and changing billows. Technical pass is not cinematic acceptance.','limits':['Camera/characters held for controlled effects comparison','2.5D independent paint layers with native shader erosion and deformation, not fluid simulation','Collection contains no lights; production owns live relighting/occlusion/contact','No transparent animation sequence is claimed in this review build']}
(P/'evidence/media_validation_v003.json').write_text(json.dumps(report,indent=2));print('FX_REVIEW_MEDIA_COMPLETE',json.dumps(report),flush=True)
