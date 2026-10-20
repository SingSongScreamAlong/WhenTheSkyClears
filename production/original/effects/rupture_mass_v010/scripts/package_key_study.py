import json,hashlib,zipfile
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
P=Path(__file__).resolve().parents[1];frames=[6,8,10,16,24,40,56,120]
for phase,title in [('WTSC_Earth_Plain_Motion_v010h','Plain motion'),('WTSC_Earth_Rupture_VDB_v010h','Shadow and color')]:
    sheet=Image.new('RGB',(1920,2*306+44),(21,25,25));d=ImageDraw.Draw(sheet);d.text((14,12),title+' | v010h UNACCEPTED KEY STUDY | actual Blender frames |24fps',fill=(225,225,215))
    for i,fr in enumerate(frames):
        f=P/'previews'/phase/f'{fr:04d}.png';assert f.is_file();im=Image.open(f).convert('RGB').resize((480,270),Image.Resampling.LANCZOS);x=(i%4)*480;y=(i//4)*306+44;sheet.paste(im,(x,y));d.text((x+10,y+278),f'frame{fr:03d} / impact{fr-7:+d}',fill=(225,225,215))
    name='WTSC_Plain_Motion_Actual_Keys_v010h.jpg' if title=='Plain motion' else 'WTSC_Shadow_Color_Actual_Keys_v010h.jpg';sheet.save(P/'previews'/name,quality=95)
Image.open(P/'previews/WTSC_Earth_Rupture_VDB_v010h/0120.png').save(P/'previews/WTSC_Rupture_Aftermath_Key_v010h.png')
a=np.asarray(Image.open(P/'previews/retime_h/baseline.png')).astype(float);b=np.asarray(Image.open(P/'previews/retime_h/offset100.png')).astype(float);diff=abs(a-b);assert diff.max()==0
(P/'evidence/retime_pixel_equality_h.json').write_text(json.dumps({'max_channel_error':float(diff.max()),'mean_channel_error':float(diff.mean()),'bit_identical_pixels':True},indent=2))
project=P.parents[1];checks=[]
for path,expected in [
('shots/world/WTSC_Full_Knockout_Trailer_Editable_v038.blend','f08c0d6f004b85693b124a1c84aac10617ca7742475979e2d80ca3d6961778ed'),
('effects/ground_impact_v009/native/WTSC_Ground_Debris_Append_v009d.blend','a0d3859e4d4fa793d47195fc5540b25e3412a5dff0e413c3465426ecdae73d48'),
('effects/coherent_native_v008/native/WTSC_Coherent_Append_v008b.blend','c992fb8247a968299350cc8e2f9db4b4ee6f38ae2ede28742d11398036b7fa2e')]:
    h=hashlib.sha256((project/path).read_bytes()).hexdigest();assert h==expected;checks.append({'path':path,'sha256':h,'unchanged':True})
(P/'evidence/source_preservation_h.json').write_text(json.dumps(checks,indent=2))
files=[P/'REVIEW_IMPORT_v010h.txt']
files += [P/'native'/n for n in ['WTSC_Earth_Rupture_Append_v010h.blend','WTSC_Earth_Rupture_Append_Test_v010h.blend','WTSC_Earth_Rupture_VDB_v010h.blend']]
files+=sorted((P/'cache/dust64_flat/data').glob('*.vdb'));assert len(list((P/'cache/dust64_flat/data').glob('*.vdb')))==120
files+=sorted((P/'scripts').glob('*.py'))
files+=[P/'evidence'/n for n in ['visual_assessment_h.json','append_test_h.json','native_volume_retime_h.json','retime_pixel_equality_h.json','source_preservation_h.json','dust_bake_f.json','dust_config_f.json','contact_shadow_construction.json','native_volume_h.json','build_rupture_e.json']]
archive=P/'WTSC_Rupture_Key_Study_Source_v010h.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for f in files:assert f.is_file(),f;z.write(f,'WTSC_Rupture_Key_Study_v010h/'+f.relative_to(P).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
paths=[archive,P/'previews/WTSC_Plain_Motion_Actual_Keys_v010h.jpg',P/'previews/WTSC_Shadow_Color_Actual_Keys_v010h.jpg',P/'previews/WTSC_Rupture_Aftermath_Key_v010h.png']
manifest=[{'path':str(f.resolve()),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in paths]
(P/'evidence/delivery_manifest_h.json').write_text(json.dumps(manifest,indent=2));uploads=[{'local_path':str(f.resolve()),'purpose':'create_library_file','directory_id':'[PRIVATE_LIBRARY_REFERENCE_REMOVED]','library_artifact_type':'other' if i==0 else 'image'} for i,f in enumerate(paths)];(P/'evidence/library_upload_request_h.json').write_text(json.dumps({'uploads':uploads},indent=2));print(json.dumps({'status':'Unaccepted key study. No full v010 clip rendered.','files':len(files),'deliverables':manifest},indent=2))
